# app/domain/entities/drop_beam_forces.py
"""
Entidad DropBeamForces: colección de combinaciones de carga para vigas capitel.

Las vigas capitel provienen de Section Cut Forces - Analysis de ETABS y se
analizan como elementos a flexocompresión (similar a piers).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .load_combination import LoadCombination
from .section_cut import SectionCutInfo
from .forces_mixin import ForcesCollectionMixin


@dataclass
class DropBeamForces(ForcesCollectionMixin):
    """
    Colección de combinaciones de carga para una viga capitel.

    Hereda métodos comunes de ForcesCollectionMixin:
    - get_envelope()
    - get_critical_pm_points()
    - get_biaxial_pm_points()
    - get_combinations_with_angles()
    - get_max_shear()

    Combina la información de Section Cut con los métodos de análisis P-M.
    """
    drop_beam_label: str
    story: str
    section_cut: SectionCutInfo
    combinations: List[LoadCombination] = field(default_factory=list)

    def get_max_shear(self) -> Dict[str, float]:
        """
        Obtiene los cortantes máximos.
        Para vigas capitel, el cortante principal es V2 o V3 según orientación.
        """
        if not self.combinations:
            return {'V_max': 0, 'V2_max': 0, 'V3_max': 0}

        V2_max = max(abs(c.V2) for c in self.combinations)
        V3_max = max(abs(c.V3) for c in self.combinations)

        return {
            'V_max': max(V2_max, V3_max),
            'V2_max': V2_max,
            'V3_max': V3_max
        }

    def get_critical_shear_combo(self) -> Optional[LoadCombination]:
        """
        Obtiene la combinación con el cortante máximo.
        """
        if not self.combinations:
            return None

        return max(self.combinations, key=lambda c: max(abs(c.V2), abs(c.V3)))

    def get_critical_flexure_combo(self) -> Optional[LoadCombination]:
        """
        Obtiene la combinación crítica para flexocompresión.
        Busca el punto más alejado del origen en el espacio P-M.
        """
        if not self.combinations:
            return None

        # Buscar la combinación con mayor momento (cualquier dirección)
        return max(self.combinations, key=lambda c: max(abs(c.M2), abs(c.M3)))
