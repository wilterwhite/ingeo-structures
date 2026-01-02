# app/domain/chapter18/__init__.py
"""
Requisitos sísmicos para muros estructurales especiales según ACI 318-25 Capítulo 18.

Estructura modular:
- results.py: Todas las dataclasses y enums
- amplification/: Amplificación de cortante sísmico (§18.10.3.3)
- boundary_elements/: Elementos de borde (§18.10.6)
- piers/: Pilares de muro (§18.10.8)
- coupling_beams/: Vigas de acoplamiento (§18.10.7)

Re-exportados desde domain/chapter11/ para compatibilidad:
- limits: Límites de diseño de muros (§11.3, §11.7)
- design_methods: Métodos de diseño (§11.5.3, §11.8)
"""
# Servicios desde subdirectorios
from .amplification import ShearAmplificationService
from .boundary_elements import BoundaryElementService
from .piers import WallPierService
from .coupling_beams import CouplingBeamService

# Dataclasses y enums desde results.py
from .results import (
    # Amplification
    ShearAmplificationResult,
    ShearAmplificationFactors,
    SpecialWallRequirements,
    # Boundary Elements
    BoundaryElementMethod,
    BoundaryElementResult,
    StressCheckResult,
    DisplacementCheckResult,
    BoundaryElementDimensions,
    BoundaryTransverseReinforcement,
    # Piers
    DesignMethod as WallPierDesignMethod,
    WallPierCategory,
    WallPierClassification,
    WallPierShearDesign,
    WallPierTransverseReinforcement,
    WallPierBoundaryCheck,
    WallPierDesignResult,
    # Coupling Beams
    CouplingBeamType,
    CouplingBeamClassification,
    DiagonalShearResult,
    DiagonalConfinementResult,
    CouplingBeamDesignResult,
    ReinforcementType,
    ConfinementOption,
)
# Re-export from domain/chapter11/ for backward compatibility
from ..chapter11 import (
    WallLimitsService,
    WallLimitsResult,
    WallType,
    WallCastType,
    ThicknessCheckResult,
    SpacingCheckResult,
    DoubleCurtainCheckResult,
    WallDesignMethodsService,
    SimplifiedMethodResult,
    SlenderWallResult,
    BoundaryCondition,
)

__all__ = [
    # amplification
    'ShearAmplificationService',
    'ShearAmplificationResult',
    'ShearAmplificationFactors',
    'SpecialWallRequirements',
    # boundary_elements
    'BoundaryElementService',
    'BoundaryElementMethod',
    'BoundaryElementResult',
    'StressCheckResult',
    'DisplacementCheckResult',
    'BoundaryElementDimensions',
    'BoundaryTransverseReinforcement',
    # piers
    'WallPierService',
    'WallPierDesignResult',
    'WallPierDesignMethod',
    'WallPierCategory',
    'WallPierClassification',
    'WallPierShearDesign',
    'WallPierTransverseReinforcement',
    'WallPierBoundaryCheck',
    # coupling_beams
    'CouplingBeamService',
    'CouplingBeamDesignResult',
    'CouplingBeamType',
    'CouplingBeamClassification',
    'DiagonalShearResult',
    'DiagonalConfinementResult',
    'ReinforcementType',
    'ConfinementOption',
    # limits
    'WallLimitsService',
    'WallLimitsResult',
    'WallType',
    'WallCastType',
    'ThicknessCheckResult',
    'SpacingCheckResult',
    'DoubleCurtainCheckResult',
    # design_methods
    'WallDesignMethodsService',
    'SimplifiedMethodResult',
    'SlenderWallResult',
    'BoundaryCondition',
]
