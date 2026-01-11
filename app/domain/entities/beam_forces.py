# app/domain/entities/beam_forces.py
"""
Entidad BeamForces: coleccion de combinaciones de carga para una viga.

Hereda de ForcesCollectionMixin para métodos compartidos con PierForces,
ColumnForces y DropBeamForces.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .load_combination import LoadCombination
from .forces_mixin import ForcesCollectionMixin


@dataclass
class BeamForces(ForcesCollectionMixin):
    """
    Coleccion de todas las combinaciones de carga para una viga.

    Las vigas tienen fuerzas en multiples "stations" (puntos a lo largo
    de la luz). Se guardan todas las combinaciones en cada station
    para poder calcular envolventes de cortante y momento.

    Hereda de ForcesCollectionMixin:
    - get_envelope(): Envolvente de fuerzas (P, V, M)
    - get_max_shear(): Cortantes máximos V2, V3
    - get_critical_pm_points(): Puntos para diagrama P-M
    - get_biaxial_pm_points(): Puntos para análisis biaxial (§18.6.4.6)
    - get_combinations_with_angles(): Info detallada por combinación
    """
    beam_label: str
    story: str
    combinations: List[LoadCombination] = field(default_factory=list)

    # Longitud calculada desde las stations
    length: float = 0.0  # mm

    def get_max_moment(self) -> Dict[str, float]:
        """
        Obtiene el momento maximo (tipicamente M3 para vigas).
        """
        if not self.combinations:
            return {'M2_max': 0, 'M3_max': 0}

        return {
            'M2_max': max(abs(c.M2) for c in self.combinations),
            'M3_max': max(abs(c.M3) for c in self.combinations)
        }

    def get_critical_shear_combo(self) -> Optional[LoadCombination]:
        """
        Obtiene la combinacion con el cortante V2 maximo.
        """
        if not self.combinations:
            return None

        return max(self.combinations, key=lambda c: abs(c.V2))

    def get_critical_moment_combo(self) -> Optional[LoadCombination]:
        """
        Obtiene la combinacion con el momento M3 maximo.
        """
        if not self.combinations:
            return None

        return max(self.combinations, key=lambda c: abs(c.M3))
