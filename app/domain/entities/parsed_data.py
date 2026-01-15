# app/domain/entities/parsed_data.py
"""
Estructura de datos parseados de archivos Excel de ETABS.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .vertical_element import VerticalElement
    from .horizontal_element import HorizontalElement
    from .element_forces import ElementForces
    from .coupling_beam import CouplingBeamConfig, PierCouplingConfig
    from ..calculations.wall_continuity import WallContinuityInfo, BuildingInfo


@dataclass
class ParsedData:
    """
    Datos parseados del Excel de ETABS.

    Contiene:
    - vertical_elements: Diccionario de elementos verticales (columnas/piers)
    - horizontal_elements: Diccionario de elementos horizontales (vigas)
    - vertical_forces: Fuerzas de elementos verticales (piers y columnas)
    - horizontal_forces: Fuerzas de elementos horizontales (vigas y drop_beams)
    - materials: Mapeo de nombres de materiales a f'c
    - stories: Lista de pisos ordenados
    - raw_data: DataFrames originales para debugging
    """
    # Elementos unificados
    vertical_elements: Dict[str, 'VerticalElement'] = field(default_factory=dict)
    horizontal_elements: Dict[str, 'HorizontalElement'] = field(default_factory=dict)

    # Fuerzas unificadas
    vertical_forces: Dict[str, 'ElementForces'] = field(default_factory=dict)
    horizontal_forces: Dict[str, 'ElementForces'] = field(default_factory=dict)

    # Metadatos
    materials: Dict[str, float] = field(default_factory=dict)
    stories: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    # Datos calculados
    continuity_info: Optional[Dict[str, 'WallContinuityInfo']] = field(default=None)
    building_info: Optional['BuildingInfo'] = field(default=None)
    default_coupling_beam: Optional['CouplingBeamConfig'] = field(default=None)
    pier_coupling_configs: Dict[str, 'PierCouplingConfig'] = field(default_factory=dict)

    # Cache de resultados de analisis
    analysis_cache: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @property
    def has_vertical_elements(self) -> bool:
        """True si hay elementos verticales cargados."""
        return len(self.vertical_elements) > 0

    @property
    def has_horizontal_elements(self) -> bool:
        """True si hay elementos horizontales cargados."""
        return len(self.horizontal_elements) > 0

    @property
    def has_piers(self) -> bool:
        """True si hay piers cargados."""
        from .vertical_element import VerticalElementSource
        return any(
            e.source == VerticalElementSource.PIER
            for e in self.vertical_elements.values()
        )

    @property
    def has_columns(self) -> bool:
        """True si hay columnas cargadas."""
        from .vertical_element import VerticalElementSource
        return any(
            e.source == VerticalElementSource.FRAME
            for e in self.vertical_elements.values()
        )

    @property
    def has_beams(self) -> bool:
        """True si hay vigas cargadas (FRAME o SPANDREL)."""
        return any(
            not e.is_drop_beam
            for e in self.horizontal_elements.values()
        )

    @property
    def has_drop_beams(self) -> bool:
        """True si hay vigas capitel cargadas."""
        return any(
            e.is_drop_beam
            for e in self.horizontal_elements.values()
        )

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
        if self.has_drop_beams:
            types.append('drop_beams')
        return types

    # Metodos de acceso por tipo
    def get_piers(self) -> Dict[str, 'VerticalElement']:
        """Retorna solo los elementos tipo PIER."""
        from .vertical_element import VerticalElementSource
        return {
            k: v for k, v in self.vertical_elements.items()
            if v.source == VerticalElementSource.PIER
        }

    def get_columns(self) -> Dict[str, 'VerticalElement']:
        """Retorna solo los elementos tipo FRAME (columnas)."""
        from .vertical_element import VerticalElementSource
        return {
            k: v for k, v in self.vertical_elements.items()
            if v.source == VerticalElementSource.FRAME
        }

    def get_beams(self) -> Dict[str, 'HorizontalElement']:
        """Retorna solo las vigas (no drop_beams)."""
        return {
            k: v for k, v in self.horizontal_elements.items()
            if not v.is_drop_beam
        }

    def get_drop_beams(self) -> Dict[str, 'HorizontalElement']:
        """Retorna solo las vigas capitel."""
        return {
            k: v for k, v in self.horizontal_elements.items()
            if v.is_drop_beam
        }
