# app/services/analysis/__init__.py
"""
Servicios de análisis estructural.

ElementOrchestrator es el punto de entrada principal para verificación
de todos los elementos estructurales (Pier, Column, Beam, DropBeam).
"""
from .flexocompression_service import FlexocompressionService
from .shear_service import ShearService
from .proposal_service import ProposalService
from .element_orchestrator import ElementOrchestrator, OrchestrationResult
from .element_classifier import ElementClassifier, ElementType
from .design_behavior import DesignBehavior
from .design_behavior_resolver import DesignBehaviorResolver
from .force_extractor import ForceExtractor, ForceEnvelope
from .geometry_normalizer import GeometryNormalizer, ColumnGeometry, BeamGeometry, WallGeometry
from .verification_config import VerificationConfig, get_config

__all__ = [
    # Servicios principales
    'FlexocompressionService',
    'ShearService',
    'ProposalService',
    'ElementOrchestrator',
    'OrchestrationResult',
    # Clasificación y comportamiento de diseño
    'ElementClassifier',
    'ElementType',
    'DesignBehavior',
    'DesignBehaviorResolver',
    # Extracción de fuerzas
    'ForceExtractor',
    'ForceEnvelope',
    # Normalización de geometría
    'GeometryNormalizer',
    'ColumnGeometry',
    'BeamGeometry',
    'WallGeometry',
    # Configuración
    'VerificationConfig',
    'get_config',
]
