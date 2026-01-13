# app/domain/entities/__init__.py
"""
Entidades de dominio para el analisis estructural.

Soporta:
- Piers (muros de hormigon armado)
- Columnas de hormigon armado
- Vigas de hormigon armado (frame y spandrels)
- Vigas capitel (drop beams)
"""
from .pier import Pier
from .load_combination import LoadCombination
from .pier_forces import PierForces
from .column import Column
from .column_forces import ColumnForces
from .beam import Beam, BeamSource, BeamShape
from .beam_forces import BeamForces
from .drop_beam import DropBeam
from .drop_beam_forces import DropBeamForces
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
    # Piers
    'Pier',
    'PierForces',
    # Columnas
    'Column',
    'ColumnForces',
    # Vigas
    'Beam',
    'BeamSource',
    'BeamShape',
    'BeamForces',
    # Vigas Capitel
    'DropBeam',
    'DropBeamForces',
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
