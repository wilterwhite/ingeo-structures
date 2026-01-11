# app/domain/entities/pier_forces.py
"""
Entidad PierForces: colección de combinaciones de carga para un pier.
"""
from dataclasses import dataclass, field
from typing import List

from .load_combination import LoadCombination
from .forces_mixin import ForcesCollectionMixin


@dataclass
class PierForces(ForcesCollectionMixin):
    """
    Colección de todas las combinaciones de carga para un pier.

    Hereda métodos comunes de ForcesCollectionMixin:
    - get_envelope()
    - get_critical_pm_points()
    - get_biaxial_pm_points()
    - get_combinations_with_angles()
    - get_max_shear()
    """
    pier_label: str
    story: str
    combinations: List[LoadCombination] = field(default_factory=list)

    def get_unique_angles(self) -> List[dict]:
        """
        Obtiene los ángulos únicos de las solicitaciones (agrupados por ~1°).
        Útil para mostrar los planos disponibles.

        Returns:
            Lista de ángulos únicos con conteo de combinaciones
        """
        combos = self.get_combinations_with_angles()
        angle_groups = {}

        for combo in combos:
            # Redondear a 1 grado para agrupar
            angle_rounded = round(combo['angle_deg'])
            if angle_rounded not in angle_groups:
                angle_groups[angle_rounded] = {
                    'angle_deg': angle_rounded,
                    'count': 0,
                    'max_M_resultant': 0,
                    'combinations': []
                }
            angle_groups[angle_rounded]['count'] += 1
            angle_groups[angle_rounded]['combinations'].append(combo)
            if combo['M_resultant'] > angle_groups[angle_rounded]['max_M_resultant']:
                angle_groups[angle_rounded]['max_M_resultant'] = combo['M_resultant']

        # Convertir a lista y ordenar por max momento
        angles_list = list(angle_groups.values())
        angles_list.sort(key=lambda x: x['max_M_resultant'], reverse=True)
        return angles_list
