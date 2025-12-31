# app/domain/entities/parsed_data.py
"""
Estructura de datos parseados de archivos Excel de ETABS.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .pier import Pier
    from .pier_forces import PierForces
    from .coupling_beam import CouplingBeamConfig, PierCouplingConfig
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
    - default_coupling_beam: Viga de acople generica por defecto
    - pier_coupling_configs: Configuraciones de vigas por pier
    """
    piers: Dict[str, 'Pier']
    pier_forces: Dict[str, 'PierForces']
    materials: Dict[str, float]
    stories: List[str]
    raw_data: Dict[str, Any]  # pd.DataFrame, Any para evitar dependencia de tipos
    continuity_info: Optional[Dict[str, 'WallContinuityInfo']] = field(default=None)
    building_info: Optional['BuildingInfo'] = field(default=None)
    default_coupling_beam: Optional['CouplingBeamConfig'] = field(default=None)
    pier_coupling_configs: Dict[str, 'PierCouplingConfig'] = field(default_factory=dict)
