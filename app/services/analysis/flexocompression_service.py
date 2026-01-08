# app/services/analysis/flexocompression_service.py
"""
Servicio unificado de flexocompresion para elementos estructurales.

Funciona con cualquier elemento que implemente el Protocol FlexuralElement:
- Pier (muros)
- Column (columnas)

Centraliza la generacion de curvas de interaccion P-M y verificacion
de flexocompresion segun ACI 318-25 Capitulo 22.
"""
from typing import Dict, List, Any, Optional, Tuple, Union

from ...domain.entities import Pier, Column, PierForces, ColumnForces
from ...domain.entities.protocols import FlexuralElement
from ...domain.flexure import (
    InteractionDiagramService,
    SlendernessService,
    SteelLayer,
    InteractionPoint,
    FlexureChecker,
)
from ...domain.constants.phi_chapter21 import PHI_COMPRESSION
from ...domain.constants.units import N_TO_TONF


class FlexocompressionService:
    """
    Servicio unificado de flexocompresion para Pier, Column, etc.

    Responsabilidades:
    - Generar curvas de interaccion P-M
    - Verificar capacidad de flexocompresion
    - Calcular capacidades puras
    - Manejar efectos de esbeltez
    - Interpolar valores en la curva

    Uso tipico:
        service = FlexocompressionService()
        result = service.check_flexure(pier, forces)
        # o
        result = service.check_flexure(column, forces, k=1.0)
    """

    def __init__(self):
        self._interaction_service = InteractionDiagramService()
        self._slenderness_service = SlendernessService()

    # =========================================================================
    # Curva de Interaccion
    # =========================================================================

    def generate_interaction_curve(
        self,
        element: FlexuralElement,
        direction: str = 'primary',
        apply_slenderness: bool = True,
        k: float = 0.8,
        braced: bool = True
    ) -> Tuple[List[InteractionPoint], Dict[str, Any]]:
        """
        Genera la curva de interaccion P-M para cualquier elemento.

        Args:
            element: Pier, Column, o cualquier FlexuralElement
            direction: 'primary' para eje fuerte, 'secondary' para eje debil
            apply_slenderness: Si aplicar reduccion por esbeltez
            k: Factor de longitud efectiva (0.8 para muros, 1.0 para columnas)
            braced: Si el elemento esta arriostrado

        Returns:
            Tuple (interaction_points, slenderness_data)
        """
        # Analizar esbeltez
        slenderness = self._slenderness_service.analyze(element, k=k, braced=braced)
        slenderness_data = {
            'lambda': round(slenderness.lambda_ratio, 1),
            'is_slender': slenderness.is_slender,
            'reduction': round(slenderness.buckling_factor, 3) if slenderness.is_slender else 1.0
        }

        # Obtener dimensiones y capas de acero
        width, thickness = element.get_section_dimensions(direction)
        steel_layers = element.get_steel_layers(direction)

        # Generar curva de interaccion
        interaction_points = self._interaction_service.generate_interaction_curve(
            width=width,
            thickness=thickness,
            fc=element.fc,
            fy=element.fy,
            As_total=element.As_flexure_total,
            cover=element.cover,
            steel_layers=steel_layers
        )

        # Aplicar reduccion por esbeltez si corresponde
        if apply_slenderness and slenderness.is_slender:
            reduction = slenderness.buckling_factor
            for point in interaction_points:
                point.phi_Pn *= reduction
                point.Pn *= reduction

        return interaction_points, slenderness_data

    # =========================================================================
    # Verificacion de Flexocompresion
    # =========================================================================

    def check_flexure(
        self,
        element: FlexuralElement,
        forces: Optional[Union[PierForces, ColumnForces]],
        moment_axis: str = 'M3',
        direction: str = 'primary',
        angle_deg: float = 0,
        k: float = 0.8,
        braced: bool = True
    ) -> Dict[str, Any]:
        """
        Verifica flexocompresion de cualquier elemento.

        Args:
            element: Pier, Column, o cualquier FlexuralElement
            forces: Fuerzas del elemento (PierForces o ColumnForces)
            moment_axis: Eje del momento ('M2' o 'M3')
            direction: 'primary' o 'secondary'
            angle_deg: Angulo del momento resultante
            k: Factor de longitud efectiva
            braced: Si el elemento esta arriostrado

        Returns:
            Dict con resultados de la verificacion
        """
        # Generar curva con esbeltez
        interaction_points, slenderness_data = self.generate_interaction_curve(
            element, direction, apply_slenderness=True, k=k, braced=braced
        )
        design_curve = self._interaction_service.get_design_curve(interaction_points)

        # Obtener puntos de demanda
        demand_points = []
        if forces and hasattr(forces, 'combinations') and forces.combinations:
            demand_points = forces.get_critical_pm_points(
                moment_axis=moment_axis,
                angle_deg=angle_deg
            )

        # Verificar
        if demand_points:
            (sf, status, critical, phi_Mn_0, phi_Mn_at_Pu,
             critical_Pu, critical_Mu, exceeds_axial, phi_Pn_max,
             has_tension, tension_combos) = \
                self._interaction_service.check_flexure(interaction_points, demand_points)
        else:
            sf, status, critical = float('inf'), "OK", "N/A"
            phi_Mn_0, phi_Mn_at_Pu, critical_Pu, critical_Mu = 0.0, 0.0, 0.0, 0.0
            exceeds_axial, phi_Pn_max = False, 0.0
            has_tension, tension_combos = False, 0

        return {
            'sf': sf,
            'status': status,
            'critical_combo': critical,
            'phi_Mn_0': phi_Mn_0,           # Capacidad a P=0 (flexion pura)
            'phi_Mn_at_Pu': phi_Mn_at_Pu,   # Capacidad a Pu critico
            'Pu': critical_Pu,
            'Mu': critical_Mu,
            'design_curve': design_curve,
            'demand_points': demand_points,
            'slenderness': slenderness_data,
            'exceeds_axial_capacity': exceeds_axial,
            'phi_Pn_max': phi_Pn_max,
            'has_tension': has_tension,
            'tension_combos': tension_combos
        }

    # =========================================================================
    # Capacidades Puras
    # =========================================================================

    def get_capacities(
        self,
        element: FlexuralElement,
        pn_max_factor: float = 0.80,
        k: float = 0.8,
        braced: bool = True
    ) -> Dict[str, Any]:
        """
        Calcula las capacidades puras del elemento (sin demanda).

        Args:
            element: Pier, Column, o cualquier FlexuralElement
            pn_max_factor: Factor para Pn,max (0.80 estribos, 0.85 espirales)
            k: Factor de longitud efectiva
            braced: Si el elemento esta arriostrado

        Returns:
            Dict con capacidades de compresion y momentos
        """
        # Esbeltez
        slenderness = self._slenderness_service.analyze(element, k=k, braced=braced)

        # 1. Compresion pura (ACI 318-25 §22.4.2.1)
        Ag = element.Ag
        As_total = element.As_flexure_total
        Pn_max = pn_max_factor * (0.85 * element.fc * (Ag - As_total) + element.fy * As_total)
        phi_Pn_max = PHI_COMPRESSION * Pn_max / N_TO_TONF

        # 2. Momento eje fuerte (primary)
        interaction_primary, _ = self.generate_interaction_curve(
            element, direction='primary', apply_slenderness=False, k=k
        )
        phi_Mn_primary = FlexureChecker.get_phi_Mn_at_P0(interaction_primary)

        # 3. Momento eje debil (secondary)
        interaction_secondary, _ = self.generate_interaction_curve(
            element, direction='secondary', apply_slenderness=False, k=k
        )
        phi_Mn_secondary = FlexureChecker.get_phi_Mn_at_P0(interaction_secondary)

        return {
            'phi_Pn_max': round(phi_Pn_max, 1),
            'phi_Mn_primary': round(phi_Mn_primary, 2),
            'phi_Mn_secondary': round(phi_Mn_secondary, 2),
            # Aliases para compatibilidad
            'phi_Mn3': round(phi_Mn_primary, 2),
            'phi_Mn2': round(phi_Mn_secondary, 2),
            'slenderness': {
                'lambda': round(slenderness.lambda_ratio, 1),
                'is_slender': slenderness.is_slender,
                'reduction': round(slenderness.buckling_factor, 3) if slenderness.is_slender else 1.0
            }
        }

    # =========================================================================
    # Interpolacion en Curva
    # =========================================================================

    def get_phi_Mn_at_Pu(
        self,
        interaction_points: List[InteractionPoint],
        Pu: float
    ) -> float:
        """
        Interpola phi_Mn en la curva de interaccion para un Pu dado.

        Args:
            interaction_points: Lista de puntos de interaccion
            Pu: Carga axial (tonf)

        Returns:
            Capacidad phi_Mn interpolada (tonf-m)
        """
        if not interaction_points:
            return 0.0

        points_sorted = sorted(interaction_points, key=lambda p: p.phi_Pn, reverse=True)

        for i in range(len(points_sorted) - 1):
            p1, p2 = points_sorted[i], points_sorted[i + 1]
            if p1.phi_Pn >= Pu >= p2.phi_Pn:
                if abs(p1.phi_Pn - p2.phi_Pn) < 0.001:
                    return p1.phi_Mn
                ratio = (p1.phi_Pn - Pu) / (p1.phi_Pn - p2.phi_Pn)
                return p1.phi_Mn + ratio * (p2.phi_Mn - p1.phi_Mn)

        if Pu > points_sorted[0].phi_Pn:
            return points_sorted[0].phi_Mn
        return points_sorted[-1].phi_Mn

    def get_c_at_point(
        self,
        interaction_points: List[InteractionPoint],
        Pu: float,
        Mu: float
    ) -> Optional[float]:
        """
        Encuentra la profundidad del eje neutro para un punto de demanda.

        Busca el punto en la curva de interaccion mas cercano y extrae c.

        Args:
            interaction_points: Lista de puntos de interaccion
            Pu: Carga axial (tonf)
            Mu: Momento (tonf-m)

        Returns:
            Profundidad c en mm, o None si no se puede calcular
        """
        if not interaction_points:
            return None

        min_distance = float('inf')
        closest_c = None

        for point in interaction_points:
            # Normalizar para comparar (evitar diferencias de escala)
            dP = (point.phi_Pn - Pu) / max(abs(point.phi_Pn), 1)
            dM = (point.phi_Mn - abs(Mu)) / max(abs(point.phi_Mn), 1)
            distance = (dP ** 2 + dM ** 2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                closest_c = point.c

        return closest_c if closest_c and closest_c < float('inf') else None
