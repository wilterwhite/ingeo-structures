# app/structural/domain/detailing/__init__.py
"""
Requisitos de detallado según ACI 318-25 Capítulo 18.

Módulos:
- boundary_elements: Elementos de borde (§18.10.6)
- piers: Pilares de muro (§18.10.8)
- coupling_beams: Vigas de acoplamiento (§18.10.7)
- limits: Límites de diseño de muros (§11.3, §11.7)
- design_methods: Métodos de diseño (§11.5.3, §11.8)
"""
from ..constants.materials import SteelGrade
from .boundary_elements import (
    BoundaryElementService,
    BoundaryElementMethod,
    BoundaryElementResult,
    StressCheckResult,
    DisplacementCheckResult,
    BoundaryElementDimensions,
    BoundaryTransverseReinforcement,
)
from .piers import (
    WallPierService,
    WallPierDesignResult,
    DesignMethod as WallPierDesignMethod,
    WallPierCategory,
    WallPierClassification,
    WallPierShearDesign,
    WallPierTransverseReinforcement,
    WallPierBoundaryCheck,
)
from .coupling_beams import (
    CouplingBeamService,
    CouplingBeamDesignResult,
    CouplingBeamType,
    CouplingBeamClassification,
    DiagonalShearResult,
    DiagonalConfinementResult,
    ReinforcementType,
    ConfinementOption,
)
from .limits import (
    WallLimitsService,
    WallLimitsResult,
    WallType,
    WallCastType,
    ThicknessCheckResult,
    SpacingCheckResult,
    DoubleCurtainCheckResult,
)
from .design_methods import (
    WallDesignMethodsService,
    SimplifiedMethodResult,
    SlenderWallResult,
    BoundaryCondition,
)

__all__ = [
    # boundary_elements
    'BoundaryElementService',
    'BoundaryElementMethod',
    'BoundaryElementResult',
    'StressCheckResult',
    'DisplacementCheckResult',
    'BoundaryElementDimensions',
    'BoundaryTransverseReinforcement',
    'SteelGrade',
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
