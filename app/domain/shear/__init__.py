# app/structural/domain/shear/__init__.py
"""
Verificación de cortante según ACI 318-25.

Módulos:
- verification: Verificación de resistencia al corte (§11.5, §18.10.4)
- amplification: Amplificación de cortante sísmico (§18.10.3.3)
- classification: Clasificación de muros y wall piers (§18.10.8)
- results: Dataclasses para resultados de verificación
"""
from .verification import ShearVerificationService
from .amplification import (
    ShearAmplificationService,
    ShearAmplificationResult,
    ShearAmplificationFactors,
    DesignShearResult,
    SpecialWallRequirements,
)
from .classification import WallClassificationService, WallClassification, ElementType
from .results import ShearResult, CombinedShearResult, WallGroupShearResult

__all__ = [
    # verification
    'ShearVerificationService',
    # results
    'ShearResult',
    'CombinedShearResult',
    'WallGroupShearResult',
    # amplification
    'ShearAmplificationService',
    'ShearAmplificationResult',
    'ShearAmplificationFactors',
    'DesignShearResult',
    'SpecialWallRequirements',
    # classification
    'WallClassificationService',
    'WallClassification',
    'ElementType',
]
