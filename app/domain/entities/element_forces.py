# app/domain/entities/element_forces.py
"""
Entidad unificada para fuerzas de cualquier elemento estructural.

OPTIMIZADO: Almacena combinaciones como DataFrame en lugar de lista de objetos
para evitar crear 240k+ objetos Python durante el parsing.
"""
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, TYPE_CHECKING, Any
import numpy as np

if TYPE_CHECKING:
    from .load_combination import LoadCombination
    from .section_cut import SectionCutInfo

# Importar pandas solo cuando se necesite
import pandas as pd


class ElementForceType(Enum):
    """Tipo de elemento para las fuerzas."""
    PIER = "pier"
    COLUMN = "column"
    BEAM = "beam"
    DROP_BEAM = "drop_beam"


# Columnas estándar para el DataFrame de combinaciones
COMBO_COLUMNS = ['name', 'location', 'step_type', 'P', 'V2', 'V3', 'T', 'M2', 'M3']


@dataclass
class ElementForces:
    """
    Colección de combinaciones de carga para cualquier elemento estructural.

    OPTIMIZADO: Usa DataFrame interno para almacenar combinaciones en lugar
    de lista de objetos LoadCombination. Esto elimina la creación de 240k+
    objetos Python y permite operaciones vectorizadas.

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

    # Campos opcionales según tipo
    height: float = 0.0  # mm - Columnas
    length: float = 0.0  # mm - Vigas
    section_cut: Optional['SectionCutInfo'] = None  # Drop beams

    # DataFrame interno para combinaciones (OPTIMIZADO)
    _combinations_df: Optional[pd.DataFrame] = field(default=None, repr=False)

    # Cache para lista de objetos (lazy loading)
    _combinations_list: Optional[List['LoadCombination']] = field(default=None, repr=False)

    def __post_init__(self):
        """Inicializa DataFrame vacío si no se proporciona."""
        if self._combinations_df is None:
            self._combinations_df = pd.DataFrame(columns=COMBO_COLUMNS)

    # =========================================================================
    # Propiedades para acceso a combinaciones
    # =========================================================================

    @property
    def combinations(self) -> List['LoadCombination']:
        """
        Retorna lista de LoadCombination (lazy loading).
        Solo crea objetos cuando se accede a esta propiedad.
        """
        if self._combinations_list is not None:
            return self._combinations_list

        # Crear lista desde DataFrame solo si se necesita
        if self._combinations_df is None or len(self._combinations_df) == 0:
            return []

        from .load_combination import LoadCombination
        # Convertir tipos numpy a Python nativos para evitar errores de serialización JSON
        self._combinations_list = [
            LoadCombination(
                name=str(row['name']) if row['name'] is not None else '',
                location=str(row['location']) if row['location'] is not None else '',
                step_type=str(row['step_type']) if row['step_type'] is not None else '',
                P=float(row['P']),
                V2=float(row['V2']),
                V3=float(row['V3']),
                T=float(row['T']),
                M2=float(row['M2']),
                M3=float(row['M3'])
            )
            for row in self._combinations_df.to_dict('records')
        ]
        return self._combinations_list

    @combinations.setter
    def combinations(self, value: List['LoadCombination']):
        """Permite asignar lista de combinaciones (compatibilidad)."""
        if not value:
            self._combinations_df = pd.DataFrame(columns=COMBO_COLUMNS)
            self._combinations_list = []
            return

        # Convertir lista a DataFrame
        self._combinations_df = pd.DataFrame([
            {
                'name': c.name,
                'location': c.location,
                'step_type': c.step_type,
                'P': c.P,
                'V2': c.V2,
                'V3': c.V3,
                'T': c.T,
                'M2': c.M2,
                'M3': c.M3
            }
            for c in value
        ])
        self._combinations_list = value

    def set_combinations_from_df(self, df: pd.DataFrame):
        """
        Asigna combinaciones directamente desde DataFrame (RÁPIDO).
        Evita crear objetos LoadCombination.
        """
        self._combinations_df = df[COMBO_COLUMNS].copy() if len(df) > 0 else pd.DataFrame(columns=COMBO_COLUMNS)
        self._combinations_list = None  # Invalidar cache

    @property
    def combinations_df(self) -> pd.DataFrame:
        """Acceso directo al DataFrame de combinaciones."""
        return self._combinations_df

    @property
    def n_combinations(self) -> int:
        """Número de combinaciones (sin crear objetos)."""
        return len(self._combinations_df) if self._combinations_df is not None else 0

    # =========================================================================
    # Métodos VECTORIZADOS (no crean objetos LoadCombination)
    # =========================================================================

    def get_envelope(self) -> Dict[str, float]:
        """
        Obtiene la envolvente de todas las combinaciones.
        VECTORIZADO: Opera sobre DataFrame directamente.
        """
        df = self._combinations_df
        if df is None or len(df) == 0:
            return {}

        return {
            'P_max': float(df['P'].max()),
            'P_min': float(df['P'].min()),
            'V2_max': float(df['V2'].abs().max()),
            'V3_max': float(df['V3'].abs().max()),
            'M2_max': float(df['M2'].abs().max()),
            'M3_max': float(df['M3'].abs().max()),
        }

    def get_critical_pm_points(
        self,
        moment_axis: str = 'M3',
        angle_deg: float = 0
    ) -> List[tuple]:
        """
        Obtiene todos los puntos (P, M) para graficar en diagrama de interacción.
        VECTORIZADO: Opera sobre DataFrame.
        """
        df = self._combinations_df
        if df is None or len(df) == 0:
            return []

        # P con convención positivo = compresión
        P = -df['P'].values

        # Calcular momento según eje
        if moment_axis == 'M2':
            M = np.abs(df['M2'].values)
        elif moment_axis == 'M3':
            M = np.abs(df['M3'].values)
        elif moment_axis == 'combined':
            rad = math.radians(angle_deg)
            M = np.abs(df['M3'].values * math.cos(rad) + df['M2'].values * math.sin(rad))
        elif moment_axis == 'SRSS':
            M = np.sqrt(df['M2'].values**2 + df['M3'].values**2)
        else:
            M = np.abs(df['M3'].values)

        # Crear nombres de combinación y convertir a tipos Python nativos
        names = df['name'].values + ' (' + df['location'].values + ')'

        return [(float(p), float(m), str(n)) for p, m, n in zip(P, M, names)]

    def get_combinations_with_angles(self) -> List[dict]:
        """
        Obtiene todas las combinaciones con información de ángulo.
        VECTORIZADO: Opera sobre DataFrame.
        """
        df = self._combinations_df
        if df is None or len(df) == 0:
            return []

        # Calcular valores vectorizados
        M2 = df['M2'].values
        M3 = df['M3'].values
        P_compression = -df['P'].values

        M_resultant = np.sqrt(M2**2 + M3**2)

        # Ángulo (evitar division por cero)
        with np.errstate(divide='ignore', invalid='ignore'):
            angle_deg = np.degrees(np.arctan2(np.abs(M2), np.abs(M3)))
            angle_deg = np.nan_to_num(angle_deg, nan=0.0)

        # Crear lista de dicts (convertir tipos numpy a Python nativos)
        combos_info = []
        for i in range(len(df)):
            combos_info.append({
                'index': int(i),
                'name': str(df['name'].iloc[i]),
                'location': str(df['location'].iloc[i]),
                'step_type': str(df['step_type'].iloc[i]),
                'P': float(P_compression[i]),
                'M2': float(M2[i]),
                'M3': float(M3[i]),
                'M_resultant': float(M_resultant[i]),
                'angle_deg': float(angle_deg[i]),
                'full_name': f"{df['name'].iloc[i]} ({df['location'].iloc[i]})"
            })

        # Ordenar por momento resultante
        combos_info.sort(key=lambda x: x['M_resultant'], reverse=True)
        return combos_info

    def get_max_shear(self) -> Dict[str, float]:
        """
        Obtiene los cortantes máximos en cada dirección.
        VECTORIZADO.
        """
        df = self._combinations_df
        if df is None or len(df) == 0:
            if self.element_type == ElementForceType.DROP_BEAM:
                return {'V_max': 0, 'V2_max': 0, 'V3_max': 0}
            return {'V2_max': 0, 'V3_max': 0}

        V2_max = float(df['V2'].abs().max())
        V3_max = float(df['V3'].abs().max())

        result = {
            'V2_max': V2_max,
            'V3_max': V3_max,
        }

        if self.element_type == ElementForceType.DROP_BEAM:
            result['V_max'] = max(V2_max, V3_max)

        return result

    def get_max_moment(self) -> Dict[str, float]:
        """
        Obtiene el momento máximo. VECTORIZADO.
        """
        df = self._combinations_df
        if df is None or len(df) == 0:
            return {'M2_max': 0, 'M3_max': 0}

        return {
            'M2_max': float(df['M2'].abs().max()),
            'M3_max': float(df['M3'].abs().max())
        }

    # =========================================================================
    # Métodos que retornan LoadCombination (lazy loading)
    # =========================================================================

    def get_critical_combination(self) -> Optional['LoadCombination']:
        """
        Obtiene la combinación con máxima demanda (P + M combinado).
        """
        df = self._combinations_df
        if df is None or len(df) == 0:
            return None

        # Calcular demanda vectorizada
        demand = df['P'].abs() + np.sqrt(df['M2']**2 + df['M3']**2)
        idx = demand.idxmax()

        # Crear solo el objeto necesario
        from .load_combination import LoadCombination
        row = df.loc[idx]
        return LoadCombination(
            name=row['name'],
            location=row['location'],
            step_type=row['step_type'],
            P=row['P'],
            V2=row['V2'],
            V3=row['V3'],
            T=row['T'],
            M2=row['M2'],
            M3=row['M3']
        )

    def get_critical_shear_combo(self) -> Optional['LoadCombination']:
        """
        Obtiene la combinación con el cortante máximo.
        """
        df = self._combinations_df
        if df is None or len(df) == 0:
            return None

        if self.element_type == ElementForceType.DROP_BEAM:
            shear = np.maximum(df['V2'].abs(), df['V3'].abs())
        else:
            shear = df['V2'].abs()

        idx = shear.idxmax()

        from .load_combination import LoadCombination
        row = df.loc[idx]
        return LoadCombination(
            name=row['name'],
            location=row['location'],
            step_type=row['step_type'],
            P=row['P'],
            V2=row['V2'],
            V3=row['V3'],
            T=row['T'],
            M2=row['M2'],
            M3=row['M3']
        )

    def get_critical_moment_combo(self) -> Optional['LoadCombination']:
        """
        Obtiene la combinación con el momento M3 máximo.
        """
        df = self._combinations_df
        if df is None or len(df) == 0:
            return None

        idx = df['M3'].abs().idxmax()

        from .load_combination import LoadCombination
        row = df.loc[idx]
        return LoadCombination(
            name=row['name'],
            location=row['location'],
            step_type=row['step_type'],
            P=row['P'],
            V2=row['V2'],
            V3=row['V3'],
            T=row['T'],
            M2=row['M2'],
            M3=row['M3']
        )

    def get_critical_flexure_combo(self) -> Optional['LoadCombination']:
        """
        Obtiene la combinación crítica para flexocompresión.
        """
        df = self._combinations_df
        if df is None or len(df) == 0:
            return None

        M_max = np.maximum(df['M2'].abs(), df['M3'].abs())
        idx = M_max.idxmax()

        from .load_combination import LoadCombination
        row = df.loc[idx]
        return LoadCombination(
            name=row['name'],
            location=row['location'],
            step_type=row['step_type'],
            P=row['P'],
            V2=row['V2'],
            V3=row['V3'],
            T=row['T'],
            M2=row['M2'],
            M3=row['M3']
        )

    # =========================================================================
    # Métodos específicos de PierForces
    # =========================================================================

    def get_unique_angles(self) -> List[dict]:
        """
        Obtiene los ángulos únicos de las solicitaciones.
        """
        combos = self.get_combinations_with_angles()
        angle_groups: Dict[int, dict] = {}

        for combo in combos:
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

        angles_list = list(angle_groups.values())
        angles_list.sort(key=lambda x: x['max_M_resultant'], reverse=True)
        return angles_list
