# app/domain/entities/column_forces.py
"""
Entidad ColumnForces: colección de combinaciones de carga para una columna.
"""
import math
from dataclasses import dataclass, field
from typing import List

from .load_combination import LoadCombination
from .forces_mixin import ForcesCollectionMixin


@dataclass
class ColumnForces(ForcesCollectionMixin):
    """
    Colección de todas las combinaciones de carga para una columna.

    Hereda métodos comunes de ForcesCollectionMixin:
    - get_envelope()
    - get_critical_pm_points()
    - get_biaxial_pm_points()
    - get_combinations_with_angles()
    - get_max_shear()

    A diferencia de PierForces, las columnas tienen fuerzas en múltiples
    "stations" (puntos a lo largo de la altura). Se guardan las fuerzas
    críticas (Top y Bottom) similar a los piers.
    """
    column_label: str
    story: str
    combinations: List[LoadCombination] = field(default_factory=list)

    # Altura calculada desde las stations
    height: float = 0.0  # mm

    def get_critical_combination(self) -> 'LoadCombination | None':
        """
        Obtiene la combinación con máxima demanda (P + M combinado).

        Usa la suma de carga axial absoluta más el momento resultante SRSS
        como criterio de criticidad.

        Returns:
            LoadCombination más crítica, o None si no hay combinaciones.
        """
        if not self.combinations:
            return None
        return max(
            self.combinations,
            key=lambda c: abs(c.P) + math.sqrt(c.M2**2 + c.M3**2)
        )
