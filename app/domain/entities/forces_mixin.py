# app/domain/entities/forces_mixin.py
"""
Mixin con métodos comunes para colecciones de fuerzas.

Elimina duplicación entre PierForces, ColumnForces y DropBeamForces.
"""
import math
from typing import List, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .load_combination import LoadCombination


class ForcesCollectionMixin:
    """
    Mixin que provee métodos comunes para colecciones de LoadCombination.

    Las clases que usen este mixin deben tener:
    - combinations: List[LoadCombination]
    """

    combinations: List['LoadCombination']

    def get_envelope(self) -> Dict[str, float]:
        """
        Obtiene la envolvente de todas las combinaciones.
        Retorna los valores máximos absolutos.
        """
        if not self.combinations:
            return {}

        return {
            'P_max': max(c.P for c in self.combinations),
            'P_min': min(c.P for c in self.combinations),
            'V2_max': max(abs(c.V2) for c in self.combinations),
            'V3_max': max(abs(c.V3) for c in self.combinations),
            'M2_max': max(abs(c.M2) for c in self.combinations),
            'M3_max': max(abs(c.M3) for c in self.combinations),
        }

    def get_critical_pm_points(
        self,
        moment_axis: str = 'M3',
        angle_deg: float = 0
    ) -> List[Tuple[float, float, str]]:
        """
        Obtiene todos los puntos (P, M) para graficar en diagrama de interacción.

        Args:
            moment_axis: 'M2', 'M3', 'combined' o 'SRSS' para momento combinado
            angle_deg: Ángulo en grados para vista combinada (0=M3, 90=M2)

        Returns:
            Lista de (P, M, combo_name) en tonf y tonf-m.
            P con convención positivo = compresión.
        """
        points = []

        for combo in self.combinations:
            P = -combo.P  # Convertir a convención positivo = compresión

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
                M = abs(combo.M3)  # Default

            points.append((P, M, f"{combo.name} ({combo.location})"))

        return points

    def get_combinations_with_angles(self) -> List[dict]:
        """
        Obtiene todas las combinaciones con información de ángulo.
        Ordenadas por momento resultante (más críticas primero).

        Returns:
            Lista de diccionarios con info de cada combinación.
        """
        combos_info = []
        for i, combo in enumerate(self.combinations):
            combos_info.append({
                'index': i,
                'name': combo.name,
                'location': combo.location,
                'step_type': combo.step_type,
                'P': -combo.P,  # Positivo = compresión
                'M2': combo.M2,
                'M3': combo.M3,
                'M_resultant': combo.moment_resultant,
                'angle_deg': combo.moment_angle_deg,
                'full_name': f"{combo.name} ({combo.location})"
            })

        combos_info.sort(key=lambda x: x['M_resultant'], reverse=True)
        return combos_info

    def get_max_shear(self) -> Dict[str, float]:
        """
        Obtiene los cortantes máximos en cada dirección.
        """
        if not self.combinations:
            return {'V2_max': 0, 'V3_max': 0}

        return {
            'V2_max': max(abs(c.V2) for c in self.combinations),
            'V3_max': max(abs(c.V3) for c in self.combinations),
        }
