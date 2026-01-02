# app/domain/entities/parsed_data.py
"""
Estructura de datos parseados de archivos Excel de ETABS.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .pier import Pier
    from .pier_forces import PierForces
    from .column import Column
    from .column_forces import ColumnForces
    from .beam import Beam
    from .beam_forces import BeamForces
    from .coupling_beam import CouplingBeamConfig, PierCouplingConfig
    from ..calculations.wall_continuity import WallContinuityInfo, BuildingInfo


@dataclass
class ParsedData:
    """
    Datos parseados del Excel de ETABS.

    Contiene:
    - piers: Diccionario de piers indexados por "Story_Label"
    - pier_forces: Fuerzas por combinacion de carga
    - columns: Diccionario de columnas indexadas por "Story_Label"
    - column_forces: Fuerzas de columnas
    - beams: Diccionario de vigas indexadas por "Story_Label"
    - beam_forces: Fuerzas de vigas
    - materials: Mapeo de nombres de materiales a f'c
    - stories: Lista de pisos ordenados
    - raw_data: DataFrames originales para debugging
    - continuity_info: Informacion de continuidad de muros (calculada)
    - building_info: Informacion global del edificio (calculada)
    - default_coupling_beam: Viga de acople generica por defecto
    - pier_coupling_configs: Configuraciones de vigas por pier
    """
    piers: Dict[str, 'Pier']
    pier_forces: Dict[str, 'PierForces']
    materials: Dict[str, float]
    stories: List[str]
    raw_data: Dict[str, Any]  # pd.DataFrame, Any para evitar dependencia de tipos

    # Columnas (nuevo)
    columns: Dict[str, 'Column'] = field(default_factory=dict)
    column_forces: Dict[str, 'ColumnForces'] = field(default_factory=dict)

    # Vigas (nuevo)
    beams: Dict[str, 'Beam'] = field(default_factory=dict)
    beam_forces: Dict[str, 'BeamForces'] = field(default_factory=dict)

    # Datos calculados
    continuity_info: Optional[Dict[str, 'WallContinuityInfo']] = field(default=None)
    building_info: Optional['BuildingInfo'] = field(default=None)
    default_coupling_beam: Optional['CouplingBeamConfig'] = field(default=None)
    pier_coupling_configs: Dict[str, 'PierCouplingConfig'] = field(default_factory=dict)

    @property
    def has_piers(self) -> bool:
        """True si hay piers cargados."""
        return len(self.piers) > 0

    @property
    def has_columns(self) -> bool:
        """True si hay columnas cargadas."""
        return len(self.columns) > 0

    @property
    def has_beams(self) -> bool:
        """True si hay vigas cargadas."""
        return len(self.beams) > 0

    @property
    def element_types_loaded(self) -> List[str]:
        """Lista de tipos de elementos cargados."""
        types = []
        if self.has_piers:
            types.append('piers')
        if self.has_columns:
            types.append('columns')
        if self.has_beams:
            types.append('beams')
        return types
