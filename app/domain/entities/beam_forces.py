# app/domain/entities/beam_forces.py
"""
Entidad BeamForces: coleccion de combinaciones de carga para una viga.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

from .load_combination import LoadCombination


@dataclass
class BeamForces:
    """
    Coleccion de todas las combinaciones de carga para una viga.

    Las vigas tienen fuerzas en multiples "stations" (puntos a lo largo
    de la luz). Se guardan todas las combinaciones en cada station
    para poder calcular envolventes de cortante y momento.
    """
    beam_label: str
    story: str
    combinations: List[LoadCombination] = field(default_factory=list)

    # Longitud calculada desde las stations
    length: float = 0.0  # mm

    def get_envelope(self) -> dict:
        """
        Obtiene la envolvente de todas las combinaciones.
        Retorna los valores maximos absolutos.
        """
        if not self.combinations:
            return {}

        # Para vigas, V2 es el cortante principal (vertical)
        # M3 es el momento flector principal
        V2_max = max(abs(c.V2) for c in self.combinations)
        V3_max = max(abs(c.V3) for c in self.combinations)
        M2_max = max(abs(c.M2) for c in self.combinations)
        M3_max = max(abs(c.M3) for c in self.combinations)
        P_max = max(c.P for c in self.combinations)
        P_min = min(c.P for c in self.combinations)

        return {
            'P_max': P_max,
            'P_min': P_min,
            'V2_max': V2_max,
            'V3_max': V3_max,
            'M2_max': M2_max,
            'M3_max': M3_max
        }

    def get_max_shear(self) -> Dict[str, float]:
        """
        Obtiene el cortante maximo (tipicamente V2 para vigas).
        """
        if not self.combinations:
            return {'V2_max': 0, 'V3_max': 0}

        return {
            'V2_max': max(abs(c.V2) for c in self.combinations),
            'V3_max': max(abs(c.V3) for c in self.combinations)
        }

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

    def get_critical_shear_combo(self) -> LoadCombination:
        """
        Obtiene la combinacion con el cortante V2 maximo.
        """
        if not self.combinations:
            return None

        return max(self.combinations, key=lambda c: abs(c.V2))

    def get_critical_moment_combo(self) -> LoadCombination:
        """
        Obtiene la combinacion con el momento M3 maximo.
        """
        if not self.combinations:
            return None

        return max(self.combinations, key=lambda c: abs(c.M3))

    def get_critical_pm_points(
        self,
        moment_axis: str = 'M3',
        angle_deg: float = 0
    ) -> List[Tuple[float, float, str]]:
        """
        Retorna puntos (P, M, combo_name) para verificacion de flexocompresion.

        Compatible con FlexocompressionService.check_flexure().
        Convencion: P positivo = compresion.

        Args:
            moment_axis: Eje de momento ('M2' o 'M3'), default 'M3'
            angle_deg: Angulo para vista combinada (no usado en vigas)

        Returns:
            Lista de tuplas (P, M, combo_name) para cada combinacion
        """
        if not self.combinations:
            return []

        points = []
        for combo in self.combinations:
            # Convertir P: ETABS usa negativo=compresion, nosotros positivo=compresion
            P = -combo.P
            M = abs(combo.M3) if moment_axis == 'M3' else abs(combo.M2)
            points.append((P, M, combo.name))

        return points
