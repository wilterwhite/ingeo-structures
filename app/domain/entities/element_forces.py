# app/domain/entities/element_forces.py
"""
Entidad unificada para fuerzas de cualquier elemento estructural.

Reemplaza las clases PierForces, ColumnForces, BeamForces y DropBeamForces
con una sola entidad que maneja todos los tipos de elementos.
"""
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .load_combination import LoadCombination
    from .section_cut import SectionCutInfo


class ElementForceType(Enum):
    """Tipo de elemento para las fuerzas."""
    PIER = "pier"
    COLUMN = "column"
    BEAM = "beam"
    DROP_BEAM = "drop_beam"


@dataclass
class ElementForces:
    """
    Colección de combinaciones de carga para cualquier elemento estructural.

    Unifica PierForces, ColumnForces, BeamForces y DropBeamForces en una
    sola clase con todos los métodos necesarios.

    Campos obligatorios:
        label: Identificador del elemento
        story: Piso del elemento
        element_type: Tipo de elemento (PIER, COLUMN, BEAM, DROP_BEAM)

    Campos opcionales según tipo:
        height: Altura del elemento (columnas, mm)
        length: Longitud del elemento (vigas, mm)
        section_cut: Info de section cut (drop beams)
    """
    # Campos obligatorios
    label: str
    story: str
    element_type: ElementForceType
    combinations: List['LoadCombination'] = field(default_factory=list)

    # Campos opcionales según tipo
    height: float = 0.0  # mm - Columnas
    length: float = 0.0  # mm - Vigas
    section_cut: Optional['SectionCutInfo'] = None  # Drop beams

    # =========================================================================
    # Métodos heredados de ForcesCollectionMixin (usados por todos los tipos)
    # =========================================================================

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
    ) -> List[tuple]:
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

        Para drop beams, también incluye V_max (el mayor entre V2 y V3).
        """
        if not self.combinations:
            if self.element_type == ElementForceType.DROP_BEAM:
                return {'V_max': 0, 'V2_max': 0, 'V3_max': 0}
            return {'V2_max': 0, 'V3_max': 0}

        V2_max = max(abs(c.V2) for c in self.combinations)
        V3_max = max(abs(c.V3) for c in self.combinations)

        result = {
            'V2_max': V2_max,
            'V3_max': V3_max,
        }

        # Drop beams incluyen V_max adicional
        if self.element_type == ElementForceType.DROP_BEAM:
            result['V_max'] = max(V2_max, V3_max)

        return result

    # =========================================================================
    # Métodos específicos de PierForces
    # =========================================================================

    def get_unique_angles(self) -> List[dict]:
        """
        Obtiene los ángulos únicos de las solicitaciones (agrupados por ~1°).
        Útil para mostrar los planos disponibles.

        Returns:
            Lista de ángulos únicos con conteo de combinaciones
        """
        combos = self.get_combinations_with_angles()
        angle_groups: Dict[int, dict] = {}

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

    # =========================================================================
    # Métodos específicos de ColumnForces
    # =========================================================================

    def get_critical_combination(self) -> Optional['LoadCombination']:
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

    # =========================================================================
    # Métodos específicos de BeamForces
    # =========================================================================

    def get_max_moment(self) -> Dict[str, float]:
        """
        Obtiene el momento máximo (típicamente M3 para vigas).
        """
        if not self.combinations:
            return {'M2_max': 0, 'M3_max': 0}

        return {
            'M2_max': max(abs(c.M2) for c in self.combinations),
            'M3_max': max(abs(c.M3) for c in self.combinations)
        }

    def get_critical_shear_combo(self) -> Optional['LoadCombination']:
        """
        Obtiene la combinación con el cortante máximo.

        Para vigas normales usa V2.
        Para drop beams usa max(V2, V3).
        """
        if not self.combinations:
            return None

        if self.element_type == ElementForceType.DROP_BEAM:
            return max(self.combinations, key=lambda c: max(abs(c.V2), abs(c.V3)))

        return max(self.combinations, key=lambda c: abs(c.V2))

    def get_critical_moment_combo(self) -> Optional['LoadCombination']:
        """
        Obtiene la combinación con el momento M3 máximo.
        """
        if not self.combinations:
            return None

        return max(self.combinations, key=lambda c: abs(c.M3))

    # =========================================================================
    # Métodos específicos de DropBeamForces
    # =========================================================================

    def get_critical_flexure_combo(self) -> Optional['LoadCombination']:
        """
        Obtiene la combinación crítica para flexocompresión.
        Busca el punto más alejado del origen en el espacio P-M.
        """
        if not self.combinations:
            return None

        # Buscar la combinación con mayor momento (cualquier dirección)
        return max(self.combinations, key=lambda c: max(abs(c.M2), abs(c.M3)))

