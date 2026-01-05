# app/domain/entities/__init__.py
"""
Entidades de dominio para el analisis estructural.

Soporta:
- Piers (muros de hormigon armado)
- Columnas de hormigon armado
- Vigas de hormigon armado (frame y spandrels)
- Losas de hormigon armado (1-Way y 2-Way)
"""
from .pier import Pier
from .load_combination import LoadCombination
from .pier_forces import PierForces
from .column import Column
from .column_forces import ColumnForces
from .beam import Beam, BeamSource
from .beam_forces import BeamForces
from .slab import Slab, SlabType, SupportCondition
from .slab_forces import SlabForces, SlabSectionCut
from .verification_result import VerificationResult
from .parsed_data import ParsedData
from .design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
)
from .coupling_beam import CouplingBeamConfig, PierCouplingConfig

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
    'BeamForces',
    # Losas
    'Slab',
    'SlabType',
    'SupportCondition',
    'SlabForces',
    'SlabSectionCut',
    # Comunes
    'LoadCombination',
    'VerificationResult',
    'ParsedData',
    'DesignProposal',
    'ReinforcementConfig',
    'FailureMode',
    'ProposalType',
    'CouplingBeamConfig',
    'PierCouplingConfig',
]
