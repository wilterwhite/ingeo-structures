# app/domain/entities/drop_beam_forces.py
"""
Entidad DropBeamForces: colección de combinaciones de carga para vigas capitel.

Las vigas capitel provienen de Section Cut Forces - Analysis de ETABS y se
analizan como elementos a flexocompresión (similar a piers).
"""
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

from .load_combination import LoadCombination
from .slab_forces import SlabSectionCut


@dataclass
class DropBeamForces:
    """
    Colección de combinaciones de carga para una viga capitel.

    Combina la información de Section Cut (de SlabForces) con los métodos
    de análisis P-M (de PierForces).
    """
    drop_beam_label: str
    story: str
    section_cut: SlabSectionCut
    combinations: List[LoadCombination] = field(default_factory=list)

    def get_envelope(self) -> Dict[str, float]:
        """
        Obtiene la envolvente de todas las combinaciones.
        Retorna los valores máximos absolutos.
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
        Obtiene todos los puntos (P, M) para graficar en diagrama de interacción.
        Retorna lista de tuplas (P_tonf, M_tonf_m, combo_name).

        Args:
            moment_axis: 'M2', 'M3', o 'combined' para momento combinado
            angle_deg: Ángulo en grados para vista combinada (0=M3, 90=M2)

        Returns:
            Lista de (P, M, combo_name) en tonf y tonf-m
        """
        points = []

        for combo in self.combinations:
            # Usar P con signo invertido (positivo = compresión)
            P = -combo.P  # Convertir a convención positivo = compresión

            if moment_axis == 'M2':
                M = abs(combo.M2)
            elif moment_axis == 'M3':
                M = abs(combo.M3)
            elif moment_axis == 'combined':
                # Momento resultante en el plano definido por el ángulo
                rad = math.radians(angle_deg)
                M = abs(combo.M3 * math.cos(rad) + combo.M2 * math.sin(rad))
            elif moment_axis == 'SRSS':
                # Raíz cuadrada de la suma de cuadrados (envolvente)
                M = math.sqrt(combo.M2**2 + combo.M3**2)
            else:
                M = abs(combo.M3)  # Default

            points.append((P, M, f"{combo.name} ({combo.location})"))

        return points

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

    def get_combinations_with_angles(self) -> List[dict]:
        """
        Obtiene todas las combinaciones con su información de ángulo.
        Ordenadas por momento resultante (más críticas primero).
        """
        combos_info = []
        for i, combo in enumerate(self.combinations):
            P = -combo.P  # Positivo = compresión
            M_resultant = combo.moment_resultant
            angle_deg = combo.moment_angle_deg

            combos_info.append({
                'index': i,
                'name': combo.name,
                'location': combo.location,
                'step_type': combo.step_type,
                'P': P,
                'M2': combo.M2,
                'M3': combo.M3,
                'M_resultant': M_resultant,
                'angle_deg': angle_deg,
                'full_name': f"{combo.name} ({combo.location})"
            })

        combos_info.sort(key=lambda x: x['M_resultant'], reverse=True)
        return combos_info
