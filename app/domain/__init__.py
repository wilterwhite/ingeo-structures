# app/domain/__init__.py
"""
Capa de dominio del modulo estructural.
Contiene entidades y logica de calculo estructural segun ACI 318-25.

Estructura de subcarpetas:
- entities/: Entidades de datos (VerticalElement, HorizontalElement, etc.)
- calculations/: Calculos auxiliares
- constants/: Constantes ACI (shear, reinforcement)
- flexure/: Verificacion de capacidad a flexion
- shear/: Verificacion de capacidad al corte
- chapter11/: Requisitos generales (Cap. 11)
- chapter18/: Requisitos sismicos (Cap. 18)
"""
from .entities import VerticalElement, HorizontalElement, LoadCombination, ElementForces, ElementForceType

# Re-export desde subcarpetas - Verificación de capacidad
from .flexure import (
    InteractionDiagramService,
    SlendernessService,
    FlexureChecker,
)

from .shear import (
    ShearVerificationService,
    WallClassificationService,
    ShearResult,
    WallClassification,
    ElementType,
)

# Re-export desde subcarpetas - Requisitos de código
from .chapter11 import (
    WallLimitsService,
    ReinforcementLimitsService,
)

from .chapter18 import (
    ShearAmplificationService,
    ShearAmplificationResult,
    BoundaryElementService,
    BoundaryElementMethod,
    BoundaryElementResult,
)

from .constants import SeismicDesignCategory

__all__ = [
    # Entities
    'VerticalElement',
    'HorizontalElement',
    'LoadCombination',
    'ElementForces',
    'ElementForceType',
    # Flexure (capacity verification)
    'InteractionDiagramService',
    'SlendernessService',
    'FlexureChecker',
    # Shear (capacity verification)
    'ShearVerificationService',
    'WallClassificationService',
    'ShearResult',
    'WallClassification',
    'ElementType',
    # Chapter 11 (general requirements)
    'WallLimitsService',
    'ReinforcementLimitsService',
    # Chapter 18 (seismic requirements)
    'ShearAmplificationService',
    'ShearAmplificationResult',
    'BoundaryElementService',
    'BoundaryElementMethod',
    'BoundaryElementResult',
    # Constants
    'SeismicDesignCategory',
]
