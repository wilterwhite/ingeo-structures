# app/structural/domain/entities/pier_forces.py
"""
Entidad PierForces: colección de combinaciones de carga para un pier.
"""
import math
from dataclasses import dataclass, field
from typing import List, Tuple

from .load_combination import LoadCombination


@dataclass
class PierForces:
    """
    Colección de todas las combinaciones de carga para un pier.
    """
    pier_label: str
    story: str
    combinations: List[LoadCombination] = field(default_factory=list)

    def get_envelope(self) -> dict:
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
                # angle=0 -> M3, angle=90 -> M2
                rad = math.radians(angle_deg)
                M = abs(combo.M3 * math.cos(rad) + combo.M2 * math.sin(rad))
            elif moment_axis == 'SRSS':
                # Raíz cuadrada de la suma de cuadrados (envolvente)
                M = math.sqrt(combo.M2**2 + combo.M3**2)
            else:
                M = abs(combo.M3)  # Default

            points.append((P, M, f"{combo.name} ({combo.location})"))

        return points

    def get_biaxial_pm_points(self) -> List[Tuple[float, float, float, str]]:
        """
        Obtiene puntos (P, M2, M3) para análisis biaxial completo.
        Retorna lista de tuplas (P_tonf, M2_tonf_m, M3_tonf_m, combo_name).
        """
        points = []
        for combo in self.combinations:
            P = -combo.P  # Positivo = compresión
            M2 = combo.M2
            M3 = combo.M3
            points.append((P, M2, M3, f"{combo.name} ({combo.location})"))
        return points

    def get_combinations_with_angles(self) -> List[dict]:
        """
        Obtiene todas las combinaciones con su información de ángulo.
        Ordenadas por momento resultante (más críticas primero).

        Returns:
            Lista de diccionarios con info de cada combinación
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

        # Ordenar por momento resultante (más crítico primero)
        combos_info.sort(key=lambda x: x['M_resultant'], reverse=True)
        return combos_info

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
