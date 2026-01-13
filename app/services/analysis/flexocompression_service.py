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
import math

from ...domain.entities import Pier, Column, Beam, PierForces, ColumnForces
from ...domain.entities.protocols import FlexuralElement
from ...domain.constants.materials import get_bar_area
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
from ...domain.constants.units import N_TO_TONF, NMM_TO_TONFM


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

        # Verificar - llamar directamente a FlexureChecker (evita nivel intermedio)
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
            'sf': sf,
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
            'phi_Pt_min': round(phi_Pt_min, 2)
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
        beam: Beam,
        alpha: float = ALPHA_OVERSTRENGTH
    ) -> Tuple[float, float]:
        """
        Calcula Mpr en ambos extremos de una viga segun ACI 318-25 §18.6.5.1.

        El momento probable Mpr se usa para calcular el cortante de diseno Ve
        en vigas de porticos especiales resistentes a momento.

        Mpr = As * (alpha * fy) * (d - a/2)

        donde:
        - alpha = ALPHA_OVERSTRENGTH (1.25, considera sobreresistencia del acero)
        - a = As * (alpha * fy) / (0.85 * f'c * b)

        Args:
            beam: Viga a analizar
            alpha: Factor de amplificacion del acero (default ALPHA_OVERSTRENGTH)

        Returns:
            Tuple (Mpr_negative, Mpr_positive) en tonf-m
            - Mpr_negative: momento con refuerzo superior (momento negativo)
            - Mpr_positive: momento con refuerzo inferior (momento positivo)
        """
        fc = beam.fc  # MPa
        fy = beam.fy  # MPa
        b = beam.width  # mm
        d = beam.d  # mm (peralte efectivo)

        # Area de acero superior e inferior
        As_top = beam.As_top  # mm2
        As_bottom = beam.As_bottom  # mm2

        # Calcular Mpr para momento negativo (refuerzo superior en tension)
        fy_amp = alpha * fy
        a_neg = (As_top * fy_amp) / (WHITNEY_STRESS_FACTOR * fc * b)
        Mpr_neg = As_top * fy_amp * (d - a_neg / 2)  # N-mm

        # Calcular Mpr para momento positivo (refuerzo inferior en tension)
        a_pos = (As_bottom * fy_amp) / (WHITNEY_STRESS_FACTOR * fc * b)
        Mpr_pos = As_bottom * fy_amp * (d - a_pos / 2)  # N-mm

        # Convertir N-mm a tonf-m
        Mpr_neg_tonf = Mpr_neg / NMM_TO_TONFM
        Mpr_pos_tonf = Mpr_pos / NMM_TO_TONFM

        return (round(Mpr_neg_tonf, 2), round(Mpr_pos_tonf, 2))

    def calculate_Ve_beam(
        self,
        beam: Beam,
        wu: float = 0.0
    ) -> Tuple[float, float, float]:
        """
        Calcula el cortante de diseno Ve para vigas sismicas segun §18.6.5.1.

        Ve = (Mpr_left + Mpr_right) / ln ± wu*ln/2

        El cortante sismico se calcula asumiendo que en ambos extremos
        se desarrollan los momentos probables Mpr con curvatura opuesta.

        Args:
            beam: Viga a analizar
            wu: Carga distribuida factorizada (tonf/m) para gravedad
                Segun §18.6.5.1: wu no debe incluir E

        Returns:
            Tuple (Ve_left, Ve_right, Ve_seismic) en tonf
            - Ve_left: Cortante en extremo izquierdo
            - Ve_right: Cortante en extremo derecho
            - Ve_seismic: Componente sismica (Mpr_left + Mpr_right) / ln
        """
        # Obtener o calcular Mpr
        if beam.Mpr_left is not None and beam.Mpr_right is not None:
            Mpr_neg = beam.Mpr_left
            Mpr_pos = beam.Mpr_right
        else:
            Mpr_neg, Mpr_pos = self.calculate_Mpr(beam)

        # Luz libre en metros (mínimo 1mm para evitar división por cero)
        ln_m = max(beam.ln_calculated, 1) / 1000

        # Cortante sismico (ambos extremos desarrollan Mpr)
        Ve_seismic = (abs(Mpr_neg) + abs(Mpr_pos)) / ln_m

        # Cortante por gravedad
        Vg = wu * ln_m / 2 if wu > 0 else 0

        # Cortante total en cada extremo
        Ve_left = Ve_seismic + Vg
        Ve_right = Ve_seismic + Vg  # Igual para carga uniforme

        return (round(Ve_left, 2), round(Ve_right, 2), round(Ve_seismic, 2))

    def calculate_Mn_column_at_Pu(
        self,
        column: Column,
        Pu: float,
        direction: str = 'primary'
    ) -> float:
        """
        Calcula Mn de una columna para un Pu dado.

        Usado para verificacion columna fuerte-viga debil §18.7.3.2.
        Debe usarse el Pu que resulte en el menor Mn.

        Args:
            column: Columna a analizar
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
