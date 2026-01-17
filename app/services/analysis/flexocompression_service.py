# app/services/analysis/flexocompression_service.py
"""
Servicio unificado de flexocompresion para elementos estructurales.

Funciona con cualquier elemento que implemente el Protocol FlexuralElement:
- Pier (muros)
- Column (columnas)

Centraliza la generacion de curvas de interaccion P-M y verificacion
de flexocompresion segun ACI 318-25 Capitulo 22.

OPTIMIZACIÓN DE RENDIMIENTO:
Las curvas P-M se pre-generan y almacenan en ParsedData.interaction_curves
antes del análisis paralelo. Esto evita recálculos costosos durante la
verificación de múltiples combinaciones de carga.
"""
from typing import Dict, List, Any, Optional, Tuple, Union
import math

from ...domain.entities import VerticalElement, HorizontalElement, ElementForces
from ...domain.entities.protocols import FlexuralElement
from ...domain.flexure import (
    InteractionDiagramService,
    SlendernessService,
    SteelLayer,
    InteractionPoint,
    FlexureChecker,
)
from ...domain.constants.phi_chapter21 import (
    PHI_COMPRESSION,
    PN_MAX_FACTOR_TIED,
    ALPHA_OVERSTRENGTH,
    WHITNEY_STRESS_FACTOR,
)
from ...domain.constants.units import N_TO_TONF
from ..presentation.formatters import format_safety_factor
from ...domain.chapter18.beams.service import (
    calculate_Mpr as _calculate_Mpr,
    calculate_Ve_beam as _calculate_Ve_beam,
)


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
        braced: bool = True,
        use_cache: bool = True  # Mantenido por compatibilidad, ignorado
    ) -> Tuple[List[InteractionPoint], Dict[str, Any]]:
        """
        Genera la curva de interaccion P-M para cualquier elemento.

        NOTA: El cache ahora se maneja externamente en ParsedData.interaction_curves.
        Las curvas se pre-generan en structural_analysis.py antes del análisis
        paralelo para optimizar rendimiento.

        Args:
            element: Pier, Column, o cualquier FlexuralElement
            direction: 'primary' para eje fuerte, 'secondary' para eje debil
            apply_slenderness: Si aplicar reduccion por esbeltez
            k: Factor de longitud efectiva (0.8 para muros, 1.0 para columnas)
            braced: Si el elemento esta arriostrado
            use_cache: Ignorado (mantenido por compatibilidad)

        Returns:
            Tuple (interaction_points, slenderness_data)
        """
        # Analizar esbeltez
        slenderness = self._slenderness_service.analyze(element, k=k, braced=braced)
        slenderness_data = {
            'lambda': round(slenderness.lambda_ratio, 1),
            'is_slender': slenderness.is_slender,
            'delta_ns': round(slenderness.delta_ns, 3) if slenderness.is_slender else 1.0,
            'magnification_pct': round(slenderness.magnification_pct, 1) if slenderness.is_slender else 0.0
        }

        # Obtener dimensiones y capas de acero
        width, thickness = element.get_section_dimensions(direction)
        steel_layers = element.get_steel_layers(direction)

        # Generar curva de interaccion
        # NOTA: No se reduce la curva P-M. El efecto de esbeltez se aplica
        # magnificando Mu segun ACI 318-25 §6.6.4: Mc = δns × Mu
        interaction_points = self._interaction_service.generate_interaction_curve(
            width=width,
            thickness=thickness,
            fc=element.fc,
            fy=element.fy,
            As_total=element.As_flexure_total,
            cover=element.cover,
            steel_layers=steel_layers
        )

        return interaction_points, slenderness_data

    # =========================================================================
    # Verificacion de Flexocompresion
    # =========================================================================

    def check_flexure(
        self,
        element: FlexuralElement,
        forces: Optional[ElementForces],
        moment_axis: str = 'M3',
        direction: str = 'primary',
        angle_deg: float = 0,
        k: float = 0.8,
        braced: bool = True,
        interaction_points: Optional[List[InteractionPoint]] = None
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
            interaction_points: Curva P-M pre-calculada (optimización de rendimiento)

        Returns:
            Dict con resultados de la verificacion
        """
        # Usar curva pre-calculada si se proporciona, sino generar
        if interaction_points is not None:
            # Analizar esbeltez para slenderness_data
            slenderness = self._slenderness_service.analyze(element, k=k, braced=braced)
            slenderness_data = {
                'lambda': round(slenderness.lambda_ratio, 1),
                'is_slender': slenderness.is_slender,
                'delta_ns': round(slenderness.delta_ns, 3) if slenderness.is_slender else 1.0,
                'magnification_pct': round(slenderness.magnification_pct, 1) if slenderness.is_slender else 0.0
            }
        else:
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

        # Verificar - llamar directamente a FlexureChecker (evita nivel intermedio)
        combo_results_list = []
        if demand_points:
            result = FlexureChecker.check_flexure(interaction_points, demand_points)
            sf = result.safety_factor
            status = result.status
            critical = result.critical_combo
            phi_Mn_0 = result.phi_Mn_0
            phi_Mn_at_Pu = result.phi_Mn_at_Pu
            critical_Pu = result.critical_Pu
            critical_Mu = result.critical_Mu
            exceeds_axial = result.exceeds_axial_capacity
            phi_Pn_max = result.phi_Pn_max
            has_tension = result.has_tension
            tension_combos = result.tension_combos
            exceeds_tension = result.exceeds_tension_capacity
            phi_Pt_min = result.phi_Pt_min
            # Propagar resultados de TODAS las combinaciones
            combo_results_list = [
                {
                    'name': c.combo_name,
                    'location': c.combo_location,
                    'Pu': round(c.Pu, 2),
                    'Mu': round(c.Mu, 2),
                    'sf': format_safety_factor(c.sf, as_string=False),
                    'dcr': round(c.dcr, 3) if not math.isinf(c.dcr) else 0,
                    'phi_Mn_at_Pu': round(c.phi_Mn_at_Pu, 2),
                    'is_tension': c.is_tension,
                    'status': 'OK' if c.sf >= 1.0 else 'NO OK'
                }
                for c in result.combo_results
            ]
        else:
            sf, status, critical = float('inf'), "OK", "N/A"
            phi_Mn_0, phi_Mn_at_Pu, critical_Pu, critical_Mu = 0.0, 0.0, 0.0, 0.0
            exceeds_axial, phi_Pn_max = False, 0.0
            has_tension, tension_combos = False, 0
            exceeds_tension, phi_Pt_min = False, 0.0

        # DCR centralizado: se calcula UNA VEZ aquí
        # DCR = 1/SF = Mu/φMn (demand/capacity)
        dcr = 1 / sf if sf > 0 and sf < float('inf') else 0

        return {
            'sf': format_safety_factor(sf, as_string=False),
            'dcr': round(dcr, 3),            # DCR centralizado (Mu/φMn)
            'status': status,
            'critical_combo': critical,
            'phi_Mn_0': phi_Mn_0,           # Capacidad a P=0 (flexion pura)
            'phi_Mn_at_Pu': phi_Mn_at_Pu,   # Capacidad a Pu critico (via ray-casting)
            'Pu': critical_Pu,
            'Mu': critical_Mu,
            'design_curve': design_curve,
            'demand_points': demand_points,
            'slenderness': slenderness_data,
            'exceeds_axial_capacity': exceeds_axial,
            'phi_Pn_max': phi_Pn_max,
            'has_tension': has_tension,
            'tension_combos': tension_combos,
            'exceeds_tension': exceeds_tension,
            'phi_Pt_min': round(phi_Pt_min, 2),
            'combo_results': combo_results_list  # Resultados de TODAS las combinaciones
        }

    # =========================================================================
    # Capacidades Puras
    # =========================================================================

    def get_capacities(
        self,
        element: FlexuralElement,
        pn_max_factor: float = PN_MAX_FACTOR_TIED,
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
        Pn_max = pn_max_factor * (WHITNEY_STRESS_FACTOR * element.fc * (Ag - As_total) + element.fy * As_total)
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
                'delta_ns': round(slenderness.delta_ns, 3) if slenderness.is_slender else 1.0,
                'magnification_pct': round(slenderness.magnification_pct, 1) if slenderness.is_slender else 0.0
            }
        }

    # =========================================================================
    # Interpolacion en Curva
    # =========================================================================

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

    # =========================================================================
    # Momento Probable (Mpr) para Vigas Sismicas §18.6.5.1
    # =========================================================================

    def calculate_Mpr(
        self,
        beam: 'HorizontalElement',
        alpha: float = ALPHA_OVERSTRENGTH
    ) -> Tuple[float, float]:
        """
        Calcula Mpr en ambos extremos de una viga según ACI 318-25 §18.6.5.1.

        Delega a domain/chapter18/beams/service.calculate_Mpr().

        Args:
            beam: Viga a analizar
            alpha: Factor de amplificación del acero (default ALPHA_OVERSTRENGTH)

        Returns:
            Tuple (Mpr_negative, Mpr_positive) en tonf-m
        """
        return _calculate_Mpr(
            As_top=beam.As_top,
            As_bottom=beam.As_bottom,
            fc=beam.fc,
            fy=beam.fy,
            b=beam.width,
            d=beam.d,
            alpha=alpha
        )

    def calculate_Ve_beam(
        self,
        beam: 'HorizontalElement',
        wu: float = 0.0
    ) -> Tuple[float, float, float]:
        """
        Calcula el cortante de diseño Ve para vigas sísmicas según §18.6.5.1.

        Delega a domain/chapter18/beams/service.calculate_Ve_beam().

        Args:
            beam: Viga a analizar
            wu: Carga distribuida factorizada (tonf/m) para gravedad

        Returns:
            Tuple (Ve_left, Ve_right, Ve_seismic) en tonf
        """
        # Obtener o calcular Mpr
        if beam.Mpr_left is not None and beam.Mpr_right is not None:
            Mpr_neg = beam.Mpr_left
            Mpr_pos = beam.Mpr_right
        else:
            Mpr_neg, Mpr_pos = self.calculate_Mpr(beam)

        return _calculate_Ve_beam(
            Mpr_neg=Mpr_neg,
            Mpr_pos=Mpr_pos,
            ln_mm=beam.ln_calculated,
            wu=wu
        )

    def calculate_Mn_column_at_Pu(
        self,
        column: 'VerticalElement',
        Pu: float,
        direction: str = 'primary'
    ) -> float:
        """
        Calcula Mn de una columna para un Pu dado.

        Usado para verificacion columna fuerte-viga debil §18.7.3.2.
        Debe usarse el Pu que resulte en el menor Mn.

        Args:
            column: VerticalElement a analizar
            Pu: Carga axial (tonf)
            direction: 'primary' o 'secondary'

        Returns:
            Mn nominal (tonf-m) - sin factor phi
        """
        # Generar curva de interaccion sin phi (Mn nominal)
        interaction_points, _ = self.generate_interaction_curve(
            column,
            direction=direction,
            apply_slenderness=False
        )

        # Interpolar Mn en la curva
        if not interaction_points:
            return 0.0

        # Ordenar por Pn (de mayor a menor)
        points_sorted = sorted(interaction_points, key=lambda p: p.Pn, reverse=True)

        # Buscar el rango donde cae Pu
        for i in range(len(points_sorted) - 1):
            p1, p2 = points_sorted[i], points_sorted[i + 1]
            # Convertir Pn a tonf (si no lo esta)
            Pn1 = p1.Pn if p1.Pn < 1e6 else p1.Pn / (1000 * 9.80665)
            Pn2 = p2.Pn if p2.Pn < 1e6 else p2.Pn / (1000 * 9.80665)

            if Pn1 >= Pu >= Pn2:
                if abs(Pn1 - Pn2) < 0.001:
                    return p1.Mn
                ratio = (Pn1 - Pu) / (Pn1 - Pn2)
                Mn = p1.Mn + ratio * (p2.Mn - p1.Mn)
                return round(Mn, 2)

        # Si Pu esta fuera del rango, usar extremo
        if Pu > points_sorted[0].Pn:
            return points_sorted[0].Mn
        return points_sorted[-1].Mn
