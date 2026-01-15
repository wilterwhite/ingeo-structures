# app/domain/entities/__init__.py
"""
Entidades de dominio para el analisis estructural.

Soporta:
- VerticalElement: columnas y piers unificados
- HorizontalElement: vigas frame, spandrel y drop_beam unificadas
"""
from .reinforcement import (
    MeshReinforcement,
    DiscreteReinforcement,
    BeamReinforcement,
)
from .vertical_element import (
    VerticalElement,
    VerticalElementSource,
    ReinforcementLayout,
)
from .horizontal_element import (
    HorizontalElement,
    HorizontalElementSource,
    HorizontalElementShape,
    HorizontalMeshReinforcement,
    HorizontalDiscreteReinforcement,
)
from .load_combination import LoadCombination
from .element_forces import ElementForces, ElementForceType
from .parsed_data import ParsedData
from .design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
)
from .coupling_beam import CouplingBeamConfig, PierCouplingConfig
from .protocols import FlexuralElement
from .value_objects import (
    MeshReinforcementConfig,
    EdgeBarConfig,
    StirrupConfig,
    BoundaryZoneDefinition,
)

__all__ = [
    # Armadura (unificada)
    'MeshReinforcement',
    'DiscreteReinforcement',
    'BeamReinforcement',
    # Elementos Verticales
    'VerticalElement',
    'VerticalElementSource',
    'ReinforcementLayout',
    # Elementos Horizontales
    'HorizontalElement',
    'HorizontalElementSource',
    'HorizontalElementShape',
    'HorizontalMeshReinforcement',  # Alias de MeshReinforcement
    'HorizontalDiscreteReinforcement',  # Alias de BeamReinforcement
    # Fuerzas
    'ElementForces',
    'ElementForceType',
    # Comunes
    'LoadCombination',
    'ParsedData',
    'DesignProposal',
    'ReinforcementConfig',
    'FailureMode',
    'ProposalType',
    'CouplingBeamConfig',
    'PierCouplingConfig',
    # Protocols
    'FlexuralElement',
    # Value Objects
    'MeshReinforcementConfig',
    'EdgeBarConfig',
    'StirrupConfig',
    'BoundaryZoneDefinition',
]
