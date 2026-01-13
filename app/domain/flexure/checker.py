# app/domain/flexure/checker.py
"""
Verificador de flexocompresión para secciones de hormigón armado.
Extrae la lógica de verificación que antes estaba en interaction_diagram.py.
"""
import math
from dataclasses import dataclass
from typing import List, Tuple, TYPE_CHECKING

from ..constants.tolerances import (
    ZERO_TOLERANCE,
    PARALLEL_TOLERANCE,
    SEGMENT_PARAM_TOLERANCE,
    INSIDE_SF_THRESHOLD,
    AXIAL_CAPACITY_TOLERANCE,
)

if TYPE_CHECKING:
    from .interaction_diagram import InteractionPoint


@dataclass
class FlexureCheckResult:
    """
    Resultado de verificación de flexocompresión.

    NOMENCLATURA DE φMn:
    - phi_Mn_0: Capacidad a P=0 (flexión pura). Usado para referencia/comparación.
    - phi_Mn_at_Pu: Capacidad de momento interpolada en la curva P-M al nivel de Pu crítico.
      Se obtiene via get_phi_Mn_at_P(points, critical_Pu), NO es Mu × SF.

    SAFETY FACTOR (SF):
    - Calculado via ray-casting desde origen hacia punto de demanda (Pu, Mu).
    - SF = distancia_hasta_curva / distancia_demanda

    DCR (Demand/Capacity Ratio):
    - DCR = 1/SF (inverso del factor de seguridad)
    - status = "OK" si SF >= 1.0, "NO OK" si SF < 1.0
    """
    safety_factor: float      # Factor de seguridad mínimo (via ray-casting)
    status: str               # "OK" o "NO OK"
    critical_combo: str       # Combinación crítica
    phi_Mn_0: float          # Capacidad de momento a P=0 (tonf-m) - flexión pura
    phi_Mn_at_Pu: float      # Capacidad de momento al Pu crítico (tonf-m) - interpolada
    critical_Pu: float       # Carga axial crítica (tonf)
    critical_Mu: float       # Momento crítico (tonf-m)
    exceeds_axial_capacity: bool = False  # Si Pu > φPn,max
    phi_Pn_max: float = 0.0  # Capacidad axial máxima (tonf)
    has_tension: bool = False  # Si alguna combinación tiene Pu < 0 (tracción)
    tension_combos: int = 0    # Número de combinaciones con tracción
    exceeds_tension_capacity: bool = False  # Si Pu < φPt,min (más tracción que capacidad)
    phi_Pt_min: float = 0.0  # Capacidad de tracción mínima (tonf, negativo)


class FlexureChecker:
    """
    Verifica la capacidad de flexocompresión contra demandas.

    Responsabilidades:
    - Calcular factor de seguridad para un punto de demanda
    - Verificar múltiples puntos de demanda
    - Interpolar capacidad de momento a P=0
    """

    @staticmethod
    def calculate_safety_factor(
        points: List['InteractionPoint'],
        Pu: float,
        Mu: float
    ) -> Tuple[float, bool]:
        """
        Calcula el factor de seguridad para un punto de demanda.

        Metodo: Ray-casting desde el origen pasando por el punto de demanda.
        Se busca la interseccion con cada segmento de la curva P-M.
        SF = distancia_capacidad / distancia_demanda

        Args:
            points: Puntos del diagrama de interaccion
            Pu: Carga axial de demanda (tonf), positivo = compresion
            Mu: Momento de demanda (tonf-m), siempre positivo

        Returns:
            Tuple (factor_seguridad, is_inside)
        """
        Mu = abs(Mu)

        # Distancia del origen al punto de demanda
        d_demand = math.sqrt(Pu**2 + Mu**2)

        if d_demand < ZERO_TOLERANCE:
            return float('inf'), True

        # Obtener la curva de capacidad como lista de puntos (Mn, Pn)
        curve_points = [(p.phi_Mn, p.phi_Pn) for p in points]

        # Direccion normalizada desde origen hacia punto de demanda
        dir_M = Mu / d_demand
        dir_P = Pu / d_demand

        # Buscar interseccion del rayo con cada segmento de la curva
        best_t = None

        n = len(curve_points)
        for i in range(n - 1):
            M1, P1 = curve_points[i]
            M2, P2 = curve_points[i + 1]

            dM = M2 - M1
            dP = P2 - P1

            det = dir_M * (-dP) - dir_P * (-dM)

            if abs(det) < PARALLEL_TOLERANCE:
                continue

            t = (M1 * (-dP) - P1 * (-dM)) / det
            s = (dir_M * P1 - dir_P * M1) / det

            if t > 0 and -SEGMENT_PARAM_TOLERANCE <= s <= 1 + SEGMENT_PARAM_TOLERANCE:
                if best_t is None or t < best_t:
                    best_t = t

        if best_t is not None:
            d_capacity = best_t
            sf = d_capacity / d_demand
            is_inside = sf >= INSIDE_SF_THRESHOLD
            return sf, is_inside

        # Si no se encontro interseccion, usar point-in-polygon como verificacion
        # y calcular SF basado en el punto de capacidad mas cercano
        is_inside = FlexureChecker._point_in_polygon(Mu, Pu, curve_points)

        # Encontrar el punto de capacidad mas cercano al rayo de demanda
        min_dist_to_ray = float('inf')
        closest_capacity_dist = 0.0

        for M_cap, P_cap in curve_points:
            # Distancia del punto de capacidad al rayo desde origen
            # Proyeccion del punto sobre el rayo
            proj = (M_cap * dir_M + P_cap * dir_P)
            if proj > 0:
                # Punto proyectado sobre el rayo
                proj_M = proj * dir_M
                proj_P = proj * dir_P
                # Distancia perpendicular al rayo
                dist_to_ray = math.sqrt((M_cap - proj_M)**2 + (P_cap - proj_P)**2)
                if dist_to_ray < min_dist_to_ray:
                    min_dist_to_ray = dist_to_ray
                    closest_capacity_dist = math.sqrt(M_cap**2 + P_cap**2)

        if closest_capacity_dist > 0:
            sf = closest_capacity_dist / d_demand
            return sf, is_inside

        # Caso extremo: no se pudo calcular - conservador
        return 0.5, False

    @staticmethod
    def _point_in_polygon(
        x: float,
        y: float,
        polygon: List[Tuple[float, float]]
    ) -> bool:
        """Verifica si un punto está dentro de un polígono usando ray casting."""
        n = len(polygon)
        inside = False

        j = n - 1
        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[j]

            if ((yi > y) != (yj > y)) and \
               (x < (xj - xi) * (y - yi) / (yj - yi + PARALLEL_TOLERANCE) + xi):
                inside = not inside
            j = i

        return inside

    @staticmethod
    def get_phi_Mn_at_P0(points: List['InteractionPoint']) -> float:
        """
        Obtiene la capacidad de momento φMn a P=0 (flexión pura).
        Delegado a get_phi_Mn_at_P(points, 0).

        Args:
            points: Puntos del diagrama de interacción

        Returns:
            φMn en tonf-m a P=0
        """
        return FlexureChecker.get_phi_Mn_at_P(points, 0.0)

    @staticmethod
    def get_phi_Mn_at_P(points: List['InteractionPoint'], Pu: float) -> float:
        """
        Obtiene la capacidad de momento φMn a un P dado, interpolando en la curva.

        Args:
            points: Puntos del diagrama de interacción
            Pu: Carga axial (tonf), positivo = compresión

        Returns:
            φMn en tonf-m al nivel de P dado
        """
        # Buscar los dos puntos que encierran el P dado
        curve_points = [(p.phi_Mn, p.phi_Pn) for p in points]

        # Separar por zona (compresión vs tracción)
        above_points = [(M, P) for M, P in curve_points if P >= Pu]
        below_points = [(M, P) for M, P in curve_points if P <= Pu]

        if not above_points or not below_points:
            # P está fuera del rango - buscar el más cercano
            closest = min(curve_points, key=lambda mp: abs(mp[1] - Pu))
            return closest[0]

        # Encontrar el punto más cercano por arriba y por abajo
        point_above = min(above_points, key=lambda mp: mp[1])  # Menor P >= Pu
        point_below = max(below_points, key=lambda mp: mp[1])  # Mayor P <= Pu

        M1, P1 = point_below
        M2, P2 = point_above

        if abs(P2 - P1) < ZERO_TOLERANCE:
            return M1

        # Interpolar linealmente
        phi_Mn = M1 + (M2 - M1) * (Pu - P1) / (P2 - P1)
        return max(0.0, phi_Mn)

    @staticmethod
    def check_flexure(
        points: List['InteractionPoint'],
        demand_points: List[Tuple[float, float, str]]
    ) -> FlexureCheckResult:
        """
        Verifica flexocompresión para múltiples puntos de demanda.

        Args:
            points: Puntos del diagrama de interacción
            demand_points: Lista de (Pu, Mu, combo_name)

        Returns:
            FlexureCheckResult con el resultado de la verificación
        """
        min_sf = float('inf')
        critical_combo = ""
        critical_Pu = 0.0
        critical_Mu = 0.0
        tension_count = 0

        for Pu, Mu, combo_name in demand_points:
            # Contar combinaciones con tracción (Pu < 0)
            if Pu < 0:
                tension_count += 1

            sf, _ = FlexureChecker.calculate_safety_factor(points, Pu, Mu)
            if sf < min_sf:
                min_sf = sf
                critical_combo = combo_name
                critical_Pu = Pu
                critical_Mu = abs(Mu)

        status = "OK" if min_sf >= 1.0 else "NO OK"
        phi_Mn_0 = FlexureChecker.get_phi_Mn_at_P0(points)

        # φMn_at_Pu es la capacidad de momento en la curva P-M al nivel Pu critico.
        # Siempre usar interpolacion horizontal para obtener la capacidad real,
        # NO calcular como Mu × SF (eso da un valor escalado incorrecto).
        phi_Mn_at_Pu = FlexureChecker.get_phi_Mn_at_P(points, critical_Pu)

        # Detectar si Pu excede la capacidad axial máxima (compresión)
        phi_Pn_max = max(p.phi_Pn for p in points) if points else 0.0
        exceeds_axial = critical_Pu > phi_Pn_max * AXIAL_CAPACITY_TOLERANCE

        # Detectar si Pu excede la capacidad de tracción mínima
        phi_Pt_min = min(p.phi_Pn for p in points) if points else 0.0
        exceeds_tension = critical_Pu < phi_Pt_min * AXIAL_CAPACITY_TOLERANCE

        return FlexureCheckResult(
            safety_factor=min_sf,
            status=status,
            critical_combo=critical_combo,
            phi_Mn_0=phi_Mn_0,
            phi_Mn_at_Pu=phi_Mn_at_Pu,
            critical_Pu=critical_Pu,
            critical_Mu=critical_Mu,
            exceeds_axial_capacity=exceeds_axial,
            phi_Pn_max=phi_Pn_max,
            has_tension=tension_count > 0,
            tension_combos=tension_count,
            exceeds_tension_capacity=exceeds_tension,
            phi_Pt_min=phi_Pt_min
        )
