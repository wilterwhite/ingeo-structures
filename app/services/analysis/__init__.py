# app/services/analysis/__init__.py
"""
Servicios de análisis estructural.
"""
from .flexocompression_service import FlexocompressionService
from .shear import ShearService
from .statistics_service import StatisticsService
from .proposal_service import ProposalService
from .element_verification_service import ElementService
from .element_classifier import ElementClassifier, ElementType
from .verification_config import VerificationConfig, get_config
from .verification_result import (
    ElementVerificationResult,
    FlexureResult,
    BidirectionalShearResult,
    ShearResult,  # Alias de BidirectionalShearResult para compatibilidad
    SlendernessResult,
    WallChecks,
    WallClassification,
    BoundaryResult,
    EndZonesResult,
    MinReinforcementResult,
)

__all__ = [
    # Servicios principales
    'FlexocompressionService',
    'ShearService',
    'StatisticsService',
    'ProposalService',
    'ElementService',
    # Clasificacion
    'ElementClassifier',
    'ElementType',
    # Configuracion
    'VerificationConfig',
    'get_config',
    # Resultados
    'ElementVerificationResult',
    'FlexureResult',
    'BidirectionalShearResult',
    'ShearResult',  # Alias
    'SlendernessResult',
    'WallChecks',
    'WallClassification',
    'BoundaryResult',
    'EndZonesResult',
    'MinReinforcementResult',
]
