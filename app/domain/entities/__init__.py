# app/domain/entities/__init__.py
"""
Entidades de dominio para el análisis estructural de muros.
"""
from .pier import Pier
from .load_combination import LoadCombination
from .pier_forces import PierForces
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
    'Pier',
    'LoadCombination',
    'PierForces',
    'VerificationResult',
    'ParsedData',
    'DesignProposal',
    'ReinforcementConfig',
    'FailureMode',
    'ProposalType',
    'CouplingBeamConfig',
    'PierCouplingConfig',
]
