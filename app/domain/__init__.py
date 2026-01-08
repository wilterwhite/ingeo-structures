# app/domain/__init__.py
"""
Capa de dominio del módulo estructural.
Contiene entidades y lógica de cálculo estructural según ACI 318-25.

Estructura de subcarpetas:
- entities/: Entidades de datos (Pier, PierForces, etc.)
- calculations/: Cálculos auxiliares
- constants/: Constantes ACI (shear, reinforcement)
- flexure/: Verificación de capacidad a flexión
- shear/: Verificación de capacidad al corte
- chapter11/: Requisitos generales (Cap. 11)
- chapter18/: Requisitos sísmicos (Cap. 18)
"""
from .entities import Pier, LoadCombination, PierForces

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

from .constants import (
    SeismicDesignCategory,
    WallCategory,
)

__all__ = [
    # Entities
    'Pier',
    'LoadCombination',
    'PierForces',
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
    'WallCategory',
]
