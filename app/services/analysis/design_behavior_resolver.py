# app/services/analysis/design_behavior_resolver.py
"""
Resuelve el comportamiento de diseno para elementos estructurales.

Este servicio determina que verificaciones aplicar a un elemento basandose en:
1. Su clasificacion (ElementType)
2. Sus fuerzas actuantes (carga axial significativa)
3. Su flag sismico

IMPORTANTE: Corrige el gap arquitectonico donde las verificaciones se aplicaban
por `isinstance()` en lugar de por clasificacion. Ahora:
- Un Pier clasificado como WALL_PIER_COLUMN recibe verificaciones §18.7
- Una Beam con carga axial significativa recibe verificaciones de flexocompresion
"""
from typing import Optional, Union, TYPE_CHECKING

from .design_behavior import DesignBehavior
from .element_classifier import ElementType
from ...domain.chapter18.design_forces.service import has_significant_axial

if TYPE_CHECKING:
    from ...domain.entities import HorizontalElement, VerticalElement
    from ...domain.entities import ElementForces


class DesignBehaviorResolver:
    """
    Resuelve el comportamiento de diseno para cualquier elemento estructural.

    Uso:
        resolver = DesignBehaviorResolver()
        behavior = resolver.resolve(element_type, element, forces, is_seismic=True)

        if behavior.requires_column_checks:
            # Aplicar verificaciones §18.7
            ...
    """

    # Mapeo primario: ElementType → DesignBehavior (para casos sin logica especial)
    _TYPE_TO_BEHAVIOR = {
        ElementType.COLUMN_SEISMIC: DesignBehavior.SEISMIC_COLUMN,
        ElementType.COLUMN_NONSEISMIC: DesignBehavior.FLEXURE_COMPRESSION,
        ElementType.WALL: DesignBehavior.SEISMIC_WALL,
        ElementType.WALL_SQUAT: DesignBehavior.SEISMIC_WALL,
        ElementType.WALL_PIER_ALTERNATE: DesignBehavior.SEISMIC_WALL_PIER_ALT,
        ElementType.DROP_BEAM: DesignBehavior.DROP_BEAM,
    }

    def resolve(
        self,
        element_type: ElementType,
        element: Union['HorizontalElement', 'VerticalElement'],
        forces: Optional['ElementForces'] = None,
        is_seismic: bool = True,
    ) -> DesignBehavior:
        """
        Resuelve el comportamiento de diseno para un elemento.

        Args:
            element_type: Tipo de elemento (de ElementClassifier)
            element: Entidad del elemento (para calculos de umbral)
            forces: Fuerzas actuantes (para verificar axial significativo)
            is_seismic: Si el elemento es parte del SFRS

        Returns:
            DesignBehavior que determina las verificaciones a aplicar

        Casos especiales:
            - WALL_PIER_COLUMN → SEISMIC_COLUMN (recibe verificaciones §18.7)
            - BEAM con axial significativo → FLEXURE_COMPRESSION
            - BEAM sismico → SEISMIC_BEAM
            - BEAM no-sismico → FLEXURE_ONLY
        """
        # Caso especial 1: Wall Pier tipo columna
        # ACI 318-25 §18.10.8: cuando lw/tw <= 2.5 y hw/lw < 2.0,
        # el pier debe disenarse como columna sismica segun §18.7
        if element_type == ElementType.WALL_PIER_COLUMN:
            return DesignBehavior.SEISMIC_COLUMN

        # Caso especial 2: Vigas
        if element_type == ElementType.BEAM:
            return self._resolve_beam_behavior(element, forces, is_seismic)

        # Casos directos del mapeo
        if element_type in self._TYPE_TO_BEHAVIOR:
            return self._TYPE_TO_BEHAVIOR[element_type]

        # Fallback para tipos no mapeados
        return DesignBehavior.FLEXURE_ONLY

    def _resolve_beam_behavior(
        self,
        element: 'HorizontalElement',
        forces: Optional['ElementForces'],
        is_seismic: bool,
    ) -> DesignBehavior:
        """
        Resuelve el comportamiento para vigas.

        Segun ACI 318-25 §18.6.4.6:
        - Si Pu > Ag*f'c/10: verificar confinamiento como columna (§18.7.5)
        - Si no: disenar como viga (§18.6)

        Args:
            element: Viga
            forces: Fuerzas de la viga
            is_seismic: Si es viga sismica

        Returns:
            DesignBehavior apropiado
        """
        # Verificar si tiene carga axial significativa
        # §18.6.4.6: Si Pu > Ag*f'c/10, usar hoops segun §18.7.5.2-18.7.5.4
        if is_seismic and self._has_significant_axial(element, forces):
            return DesignBehavior.SEISMIC_BEAM_COLUMN

        # No sismica con axial significativo: flexocompresion §22.4
        if self._has_significant_axial(element, forces):
            return DesignBehavior.FLEXURE_COMPRESSION

        # Vigas sismicas: verificaciones §18.6
        if is_seismic:
            return DesignBehavior.SEISMIC_BEAM

        # Vigas no-sismicas: flexion pura
        return DesignBehavior.FLEXURE_ONLY

    def _has_significant_axial(
        self,
        element: Union['HorizontalElement', 'VerticalElement'],
        forces: Optional['ElementForces'],
        divisor: float = 10.0,
    ) -> bool:
        """
        Verifica si Pu >= Ag*f'c/divisor.

        Delega a domain/chapter18/design_forces/service.has_significant_axial().

        ACI 318-25 §18.6.4.6: cuando la carga axial factorizada excede
        Ag*f'c/10, se requieren verificaciones adicionales de confinamiento.

        Args:
            element: Elemento a verificar
            forces: Fuerzas del elemento
            divisor: Divisor del umbral (default 10.0 para §18.6.4.6)

        Returns:
            True si la carga axial es significativa
        """
        if not forces:
            return False

        Ag = getattr(element, 'Ag', 0)  # mm2
        fc = getattr(element, 'fc', 0)  # MPa
        Pu_max = self._get_max_axial(forces)

        return has_significant_axial(Ag, fc, Pu_max, divisor)

    def _get_max_axial(
        self,
        forces: 'ElementForces',
    ) -> float:
        """
        Obtiene la carga axial maxima de las fuerzas.

        Args:
            forces: Fuerzas del elemento

        Returns:
            Pu maximo en tonf (valor absoluto)
        """
        Pu_max = 0.0

        # Usar envelope si disponible
        if hasattr(forces, 'get_envelope'):
            envelope = forces.get_envelope()
            P_max = abs(envelope.get('P_max', 0))
            P_min = abs(envelope.get('P_min', 0))
            Pu_max = max(P_max, P_min)

        # Fallback: iterar combinaciones
        elif hasattr(forces, 'combinations') and forces.combinations:
            for combo in forces.combinations:
                P = abs(getattr(combo, 'P', 0))
                if P > Pu_max:
                    Pu_max = P

        return Pu_max
