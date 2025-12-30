# app/structural/domain/entities/parsed_data.py
"""
Estructura de datos parseados de archivos Excel de ETABS.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    from .pier import Pier
    from .pier_forces import PierForces
    from ..calculations.wall_continuity import WallContinuityInfo, BuildingInfo


@dataclass
class ParsedData:
    """
    Datos parseados del Excel de ETABS.

    Contiene:
    - piers: Diccionario de piers indexados por "Story_Label"
    - pier_forces: Fuerzas por combinación de carga
    - materials: Mapeo de nombres de materiales a f'c
    - stories: Lista de pisos ordenados
    - raw_data: DataFrames originales para debugging
    - continuity_info: Información de continuidad de muros (calculada)
    - building_info: Información global del edificio (calculada)
    """
    piers: Dict[str, 'Pier']
    pier_forces: Dict[str, 'PierForces']
    materials: Dict[str, float]
    stories: List[str]
    raw_data: Dict[str, 'pd.DataFrame']
    continuity_info: Optional[Dict[str, 'WallContinuityInfo']] = field(default=None)
    building_info: Optional['BuildingInfo'] = field(default=None)
