# app/structural/domain/__init__.py
"""
Capa de dominio del módulo estructural.
Contiene entidades y lógica de cálculo estructural según ACI 318-25.

Estructura de subcarpetas:
- entities/: Entidades de datos (Pier, PierForces, etc.)
- calculations/: Cálculos auxiliares
- constants/: Constantes ACI (shear, reinforcement)
- flexure/: Verificación de flexión
- shear/: Verificación de cortante
- detailing/: Requisitos de detallado (Cap. 18)
"""
from .entities import Pier, LoadCombination, VerificationResult, PierForces

# Re-export desde subcarpetas
from .flexure import (
    InteractionDiagramService,
    SlendernessService,
    FlexureChecker,
)

from .shear import (
    ShearVerificationService,
    ShearAmplificationService,
    WallClassificationService,
    ShearResult,
    ShearAmplificationResult,
    WallClassification,
    WallType,
)

from .detailing import (
    BoundaryElementService,
    BoundaryElementMethod,
    BoundaryElementResult,
)

from .constants import (
    SeismicDesignCategory,
    WallCategory,
)

__all__ = [
    # Entities
    'Pier',
    'LoadCombination',
    'VerificationResult',
    'PierForces',
    # Flexure
    'InteractionDiagramService',
    'SlendernessService',
    'FlexureChecker',
    # Shear
    'ShearVerificationService',
    'ShearAmplificationService',
    'WallClassificationService',
    'ShearResult',
    'ShearAmplificationResult',
    'WallClassification',
    'WallType',
    # Detailing
    'BoundaryElementService',
    'BoundaryElementMethod',
    'BoundaryElementResult',
    # Constants
    'SeismicDesignCategory',
    'WallCategory',
]
