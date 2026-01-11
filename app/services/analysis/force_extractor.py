# app/services/analysis/force_extractor.py
"""
Extractor unificado de fuerzas para elementos estructurales.

Centraliza la lógica de extracción de fuerzas críticas de cualquier
tipo de objeto Forces (BeamForces, ColumnForces, PierForces, DropBeamForces).

Usado por ElementOrchestrator para normalizar fuerzas de cualquier elemento.
"""
from typing import Dict, Optional, Tuple, Union, TYPE_CHECKING
from dataclasses import dataclass

from ...domain.constants.units import TONF_TO_N

if TYPE_CHECKING:
    from ...domain.entities import BeamForces, ColumnForces, PierForces, DropBeamForces


@dataclass
class ForceEnvelope:
    """Envolvente de fuerzas críticas."""
    V2_max: float = 0.0
    V3_max: float = 0.0
    M2_max: float = 0.0
    M3_max: float = 0.0
    P_max: float = 0.0  # Compresión máxima (positivo)
    P_min: float = 0.0  # Tracción máxima (negativo)

    def to_dict(self) -> Dict[str, float]:
        """Convierte a diccionario."""
        return {
            'V2_max': self.V2_max,
            'V3_max': self.V3_max,
            'M2_max': self.M2_max,
            'M3_max': self.M3_max,
            'P_max': self.P_max,
            'P_min': self.P_min,
        }


class ForceExtractor:
    """
    Extrae fuerzas críticas de cualquier tipo de Forces.

    Soporta múltiples patrones de acceso:
    - get_envelope() method (preferido)
    - combinations iteration
    - Atributos directos

    Uso:
        envelope = ForceExtractor.extract_envelope(forces)
        Vu = ForceExtractor.extract_critical_shear(forces, axis='V2')
        P_max, P_min = ForceExtractor.extract_critical_axial(forces)
    """

    @staticmethod
    def extract_envelope(
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces']]
    ) -> ForceEnvelope:
        """
        Extrae la envolvente de fuerzas críticas.

        Args:
            forces: Objeto de fuerzas (cualquier tipo)

        Returns:
            ForceEnvelope con valores máximos de V2, V3, M2, M3, P
        """
        if forces is None:
            return ForceEnvelope()

        # Patrón 1: Usar get_envelope() si está disponible (preferido)
        if hasattr(forces, 'get_envelope'):
            envelope = forces.get_envelope()
            return ForceEnvelope(
                V2_max=abs(envelope.get('V2_max', 0)),
                V3_max=abs(envelope.get('V3_max', 0)),
                M2_max=abs(envelope.get('M2_max', 0)),
                M3_max=abs(envelope.get('M3_max', 0)),
                P_max=envelope.get('P_max', 0),
                P_min=envelope.get('P_min', 0),
            )

        # Patrón 2: Iterar sobre combinaciones
        if hasattr(forces, 'combinations') and forces.combinations:
            return ForceExtractor._extract_from_combinations(forces.combinations)

        # Patrón 3: Atributos directos
        return ForceExtractor._extract_from_attributes(forces)

    @staticmethod
    def _extract_from_combinations(combinations) -> ForceEnvelope:
        """Extrae envolvente iterando sobre combinaciones."""
        V2_max = 0.0
        V3_max = 0.0
        M2_max = 0.0
        M3_max = 0.0
        P_max = 0.0
        P_min = 0.0

        for combo in combinations:
            # Cortante
            V2 = abs(getattr(combo, 'V2', 0))
            V3 = abs(getattr(combo, 'V3', 0))
            if V2 > V2_max:
                V2_max = V2
            if V3 > V3_max:
                V3_max = V3

            # Momento
            M2 = abs(getattr(combo, 'M2', 0))
            M3 = abs(getattr(combo, 'M3', 0))
            if M2 > M2_max:
                M2_max = M2
            if M3 > M3_max:
                M3_max = M3

            # Axial (track max compression y max tension)
            P = getattr(combo, 'P', 0)
            if P > P_max:
                P_max = P
            if P < P_min:
                P_min = P

        return ForceEnvelope(
            V2_max=V2_max,
            V3_max=V3_max,
            M2_max=M2_max,
            M3_max=M3_max,
            P_max=P_max,
            P_min=P_min,
        )

    @staticmethod
    def _extract_from_attributes(forces) -> ForceEnvelope:
        """Extrae envolvente de atributos directos."""
        return ForceEnvelope(
            V2_max=abs(getattr(forces, 'V2', 0)),
            V3_max=abs(getattr(forces, 'V3', 0)),
            M2_max=abs(getattr(forces, 'M2', 0)),
            M3_max=abs(getattr(forces, 'M3', 0)),
            P_max=getattr(forces, 'P', 0),
            P_min=getattr(forces, 'P', 0),
        )

    @staticmethod
    def extract_critical_shear(
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces']],
        axis: str = 'V2'
    ) -> float:
        """
        Extrae cortante crítico en eje especificado.

        Args:
            forces: Objeto de fuerzas
            axis: 'V2' o 'V3'

        Returns:
            Valor absoluto del cortante máximo
        """
        envelope = ForceExtractor.extract_envelope(forces)
        if axis == 'V3':
            return envelope.V3_max
        return envelope.V2_max

    @staticmethod
    def extract_critical_moment(
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces']],
        axis: str = 'M3'
    ) -> float:
        """
        Extrae momento crítico en eje especificado.

        Args:
            forces: Objeto de fuerzas
            axis: 'M2' o 'M3'

        Returns:
            Valor absoluto del momento máximo
        """
        envelope = ForceExtractor.extract_envelope(forces)
        if axis == 'M2':
            return envelope.M2_max
        return envelope.M3_max

    @staticmethod
    def extract_critical_axial(
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces']]
    ) -> Tuple[float, float]:
        """
        Extrae carga axial crítica (compresión y tracción).

        Args:
            forces: Objeto de fuerzas

        Returns:
            Tupla (P_max_compression, P_min_tension)
            P_max es positivo (compresión), P_min es negativo (tracción)
        """
        envelope = ForceExtractor.extract_envelope(forces)
        return envelope.P_max, envelope.P_min

    @staticmethod
    def extract_combined_shear(
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces']]
    ) -> float:
        """
        Extrae cortante combinado SRSS (V2² + V3²)^0.5.

        Args:
            forces: Objeto de fuerzas

        Returns:
            Cortante combinado SRSS
        """
        import math
        envelope = ForceExtractor.extract_envelope(forces)
        return math.sqrt(envelope.V2_max**2 + envelope.V3_max**2)

    @staticmethod
    def has_significant_axial(
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces']],
        Ag: float,
        fc: float,
        divisor: float = 10.0
    ) -> bool:
        """
        Verifica si la carga axial es significativa según ACI 318-25 §18.6.4.6.

        Args:
            forces: Objeto de fuerzas
            Ag: Área bruta de la sección (mm²)
            fc: Resistencia del concreto (MPa)
            divisor: Divisor del umbral (default 10.0 para Ag*f'c/10)

        Returns:
            True si |Pu| >= Ag*f'c/divisor
        """
        if Ag <= 0 or fc <= 0:
            return False

        P_max, P_min = ForceExtractor.extract_critical_axial(forces)
        Pu_max = max(abs(P_max), abs(P_min))

        # Umbral: Ag * f'c / divisor, convertido a tonf
        # (mm² × MPa) = N → / TONF_TO_N → tonf
        threshold_N = Ag * fc / divisor
        threshold_tonf = threshold_N / TONF_TO_N

        return Pu_max >= threshold_tonf
