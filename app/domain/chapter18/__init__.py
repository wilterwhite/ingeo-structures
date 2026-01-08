# app/domain/chapter18/__init__.py
"""
Reglas ACI 318-25 Capítulo 18: Estructuras Resistentes a Sismos.

Este módulo es la ÚNICA FUENTE DE VERDAD para las reglas del Capítulo 18.
Los servicios de aplicación (app/services/) deben usar estas funciones
en lugar de reimplementar la lógica.

Estructura:
-----------
results.py          - Dataclasses y enums para resultados
reinforcement/      - Refuerzo mínimo distribuido (§18.10.2)
design_forces/      - Fuerzas de diseño, amplificación cortante (§18.10.3)
boundary_elements/  - Elementos de borde (§18.10.6)
coupling_beams/     - Vigas de acoplamiento (§18.10.7)
wall_piers/         - Pilares de muro y columnas (§18.10.8, §18.7.6)

Funciones Clave:
---------------
calculate_design_shear(Vu, lu, Mpr_total, ...)
    Calcula Ve para diseño por capacidad según §18.7.6.1 y §18.10.8.1(a).
    Aplica a columnas especiales y wall piers con vigas de acople.
    Ve = min(Mpr_total/lu, Omega_o*Vu)

classify_wall_pier(lw, tw, hw)
    Clasifica elemento según Tabla R18.10.1.
    Determina si es columna, wall pier, o muro.

Uso típico:
----------
    from app.domain.chapter18 import calculate_design_shear

    # Calcular Ve para diseño por capacidad
    design = calculate_design_shear(
        Vu=50,           # tonf del análisis
        lu=3000,         # mm altura libre
        Mpr_total=200,   # tonf-m de vigas de acople
    )
    Ve = design.Ve  # Cortante de diseño

Re-exports desde chapter11:
- WallLimitsService: Límites de espesor (§11.3, §11.7)
- WallDesignMethodsService: Métodos simplificado/esbelto (§11.5.3, §11.8)
"""
# Servicios desde subdirectorios
from .design_forces import ShearAmplificationService
from .boundary_elements import BoundaryElementService
from .wall_piers import WallPierService
from .coupling_beams import CouplingBeamService
from .reinforcement import SeismicReinforcementService, SeismicReinforcementResult

# Funciones de cálculo directo (para usar desde servicios)
from .wall_piers.shear_design import calculate_design_shear
from .wall_piers.classification import classify_wall_pier
from .wall_piers.boundary_zones import check_boundary_zone_reinforcement

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
    BoundaryZoneCheck,
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
    # Funciones de cálculo directo (usar desde servicios)
    'calculate_design_shear',
    'classify_wall_pier',
    'check_boundary_zone_reinforcement',
    # reinforcement (§18.10.2.1)
    'SeismicReinforcementService',
    'SeismicReinforcementResult',
    # design_forces (§18.10.3)
    'ShearAmplificationService',
    'ShearAmplificationResult',
    'ShearAmplificationFactors',
    'SpecialWallRequirements',
    # boundary_elements (§18.10.6)
    'BoundaryElementService',
    'BoundaryElementMethod',
    'BoundaryElementResult',
    'StressCheckResult',
    'DisplacementCheckResult',
    'BoundaryElementDimensions',
    'BoundaryTransverseReinforcement',
    # wall_piers (§18.10.8, §18.10.2.4)
    'WallPierService',
    'WallPierDesignResult',
    'WallPierDesignMethod',
    'WallPierCategory',
    'WallPierClassification',
    'WallPierShearDesign',
    'WallPierTransverseReinforcement',
    'WallPierBoundaryCheck',
    'BoundaryZoneCheck',
    # coupling_beams (§18.10.7)
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
