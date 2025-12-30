# app/structural/domain/calculations/flexure_checker.py
"""
Verificador de flexocompresión para secciones de hormigón armado.
Extrae la lógica de verificación que antes estaba en interaction_diagram.py.
"""
import math
from dataclasses import dataclass
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..interaction_diagram import InteractionPoint


@dataclass
class FlexureCheckResult:
    """Resultado de verificación de flexocompresión."""
    safety_factor: float      # Factor de seguridad mínimo
    status: str               # "OK" o "NO OK"
    critical_combo: str       # Combinación crítica
    phi_Mn_0: float          # Capacidad de momento a P=0 (tonf-m)
    phi_Mn_at_Pu: float      # Capacidad de momento a Pu crítico (tonf-m)
    critical_Pu: float       # Carga axial crítica (tonf)
    critical_Mu: float       # Momento crítico (tonf-m)
    is_inside: bool          # Si el punto crítico está dentro de la curva


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

        Método: Trazar una línea desde el origen pasando por el punto de demanda
        y encontrar donde intersecta la curva de capacidad.
        SF = distancia_capacidad / distancia_demanda

        Args:
            points: Puntos del diagrama de interacción
            Pu: Carga axial de demanda (tonf), positivo = compresión
            Mu: Momento de demanda (tonf-m), siempre positivo

        Returns:
            Tuple (factor_seguridad, is_inside)
        """
        Mu = abs(Mu)

        # Distancia del origen al punto de demanda
        d_demand = math.sqrt(Pu**2 + Mu**2)

        if d_demand < 1e-6:
            return float('inf'), True

        # Obtener la curva de capacidad como lista de puntos (Mn, Pn)
        curve_points = [(p.phi_Mn, p.phi_Pn) for p in points]

        # Dirección normalizada desde origen hacia punto de demanda
        dir_M = Mu / d_demand
        dir_P = Pu / d_demand

        # Buscar intersección del rayo con cada segmento de la curva
        best_t = None

        n = len(curve_points)
        for i in range(n - 1):
            M1, P1 = curve_points[i]
            M2, P2 = curve_points[i + 1]

            dM = M2 - M1
            dP = P2 - P1

            det = dir_M * (-dP) - dir_P * (-dM)

            if abs(det) < 1e-10:
                continue

            t = (M1 * (-dP) - P1 * (-dM)) / det
            s = (dir_M * P1 - dir_P * M1) / det

            if t > 0 and -0.001 <= s <= 1.001:
                if best_t is None or t < best_t:
                    best_t = t

        if best_t is not None:
            d_capacity = best_t
            sf = d_capacity / d_demand
            is_inside = sf >= 0.999
            return sf, is_inside

        # Fallback: buscar el punto más cercano en la misma dirección angular
        best_dist = None
        angle_demand = math.atan2(Pu, Mu)

        for M_cap, P_cap in curve_points:
            angle_cap = math.atan2(P_cap, M_cap)
            diff = abs(angle_cap - angle_demand)
            if diff > math.pi:
                diff = 2 * math.pi - diff

            if diff < 0.26:  # ~15 grados
                d_cap = math.sqrt(M_cap**2 + P_cap**2)
                if best_dist is None or d_cap < best_dist:
                    best_dist = d_cap

        if best_dist is not None:
            sf = best_dist / d_demand
            is_inside = sf >= 0.999
            return sf, is_inside

        # Último fallback
        is_inside = FlexureChecker._point_in_polygon(Mu, Pu, curve_points)
        if is_inside:
            return 10.0, True
        else:
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
               (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi):
                inside = not inside
            j = i

        return inside

    @staticmethod
    def get_phi_Mn_at_P0(points: List['InteractionPoint']) -> float:
        """
        Obtiene la capacidad de momento φMn a P=0 (flexión pura).

        Args:
            points: Puntos del diagrama de interacción

        Returns:
            φMn en tonf-m a P≈0
        """
        # Buscar el punto con φPn más cercano a 0
        best_point = None
        min_abs_P = float('inf')

        for p in points:
            abs_P = abs(p.phi_Pn)
            if abs_P < min_abs_P:
                min_abs_P = abs_P
                best_point = p

        if best_point is not None and min_abs_P < 5.0:
            return best_point.phi_Mn

        # Interpolar entre los dos puntos más cercanos a P=0
        pos_point = None
        neg_point = None

        for p in points:
            if p.phi_Pn >= 0:
                if pos_point is None or p.phi_Pn < pos_point.phi_Pn:
                    pos_point = p
            else:
                if neg_point is None or p.phi_Pn > neg_point.phi_Pn:
                    neg_point = p

        if pos_point is not None and neg_point is not None:
            P1, M1 = neg_point.phi_Pn, neg_point.phi_Mn
            P2, M2 = pos_point.phi_Pn, pos_point.phi_Mn
            if abs(P2 - P1) > 1e-6:
                phi_Mn_0 = M1 + (M2 - M1) * (0 - P1) / (P2 - P1)
                return phi_Mn_0

        return best_point.phi_Mn if best_point else 0.0

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

        if abs(P2 - P1) < 1e-6:
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
        critical_is_inside = True

        for Pu, Mu, combo_name in demand_points:
            sf, is_inside = FlexureChecker.calculate_safety_factor(points, Pu, Mu)
            if sf < min_sf:
                min_sf = sf
                critical_combo = combo_name
                critical_Pu = Pu
                critical_Mu = abs(Mu)
                critical_is_inside = is_inside

        status = "OK" if min_sf >= 1.0 else "NO OK"
        phi_Mn_0 = FlexureChecker.get_phi_Mn_at_P0(points)
        phi_Mn_at_Pu = FlexureChecker.get_phi_Mn_at_P(points, critical_Pu)

        return FlexureCheckResult(
            safety_factor=min_sf,
            status=status,
            critical_combo=critical_combo,
            phi_Mn_0=phi_Mn_0,
            phi_Mn_at_Pu=phi_Mn_at_Pu,
            critical_Pu=critical_Pu,
            critical_Mu=critical_Mu,
            is_inside=critical_is_inside
        )
