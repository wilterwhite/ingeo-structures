# app/domain/entities/column_forces.py
"""
Entidad ColumnForces: coleccion de combinaciones de carga para una columna.
"""
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

from .load_combination import LoadCombination


@dataclass
class ColumnForces:
    """
    Coleccion de todas las combinaciones de carga para una columna.

    A diferencia de PierForces, las columnas tienen fuerzas en multiples
    "stations" (puntos a lo largo de la altura). Se guardan las fuerzas
    criticas (Top y Bottom) similar a los piers.
    """
    column_label: str
    story: str
    combinations: List[LoadCombination] = field(default_factory=list)

    # Altura calculada desde las stations
    height: float = 0.0  # mm

    def get_envelope(self) -> dict:
        """
        Obtiene la envolvente de todas las combinaciones.
        Retorna los valores maximos absolutos.
        """
        if not self.combinations:
            return {}

        P_max = max(c.P for c in self.combinations)
        P_min = min(c.P for c in self.combinations)
        V2_max = max(abs(c.V2) for c in self.combinations)
        V3_max = max(abs(c.V3) for c in self.combinations)
        M2_max = max(abs(c.M2) for c in self.combinations)
        M3_max = max(abs(c.M3) for c in self.combinations)

        return {
            'P_max': P_max,
            'P_min': P_min,
            'V2_max': V2_max,
            'V3_max': V3_max,
            'M2_max': M2_max,
            'M3_max': M3_max
        }

    def get_critical_pm_points(
        self,
        moment_axis: str = 'M3',
        angle_deg: float = 0
    ) -> List[Tuple[float, float, str]]:
        """
        Obtiene todos los puntos (P, M) para graficar en diagrama de interaccion.
        Retorna lista de tuplas (P_tonf, M_tonf_m, combo_name).

        Args:
            moment_axis: 'M2', 'M3', o 'combined' para momento combinado
            angle_deg: Angulo en grados para vista combinada (0=M3, 90=M2)

        Returns:
            Lista de (P, M, combo_name) en tonf y tonf-m
        """
        points = []

        for combo in self.combinations:
            P = -combo.P  # Convertir a convencion positivo = compresion

            if moment_axis == 'M2':
                M = abs(combo.M2)
            elif moment_axis == 'M3':
                M = abs(combo.M3)
            elif moment_axis == 'combined':
                rad = math.radians(angle_deg)
                M = abs(combo.M3 * math.cos(rad) + combo.M2 * math.sin(rad))
            elif moment_axis == 'SRSS':
                M = math.sqrt(combo.M2**2 + combo.M3**2)
            else:
                M = abs(combo.M3)

            points.append((P, M, f"{combo.name} ({combo.location})"))

        return points

    def get_biaxial_pm_points(self) -> List[Tuple[float, float, float, str]]:
        """
        Obtiene puntos (P, M2, M3) para analisis biaxial completo.
        """
        points = []
        for combo in self.combinations:
            P = -combo.P
            M2 = combo.M2
            M3 = combo.M3
            points.append((P, M2, M3, f"{combo.name} ({combo.location})"))
        return points

    def get_max_shear(self) -> Dict[str, float]:
        """
        Obtiene los cortantes maximos en cada direccion.
        """
        if not self.combinations:
            return {'V2_max': 0, 'V3_max': 0}

        return {
            'V2_max': max(abs(c.V2) for c in self.combinations),
            'V3_max': max(abs(c.V3) for c in self.combinations)
        }
