# app/domain/chapter18/__init__.py
"""
Reglas ACI 318-25 Capítulo 18: Estructuras Resistentes a Sismos.

Este módulo es la ÚNICA FUENTE DE VERDAD para las reglas del Capítulo 18.
Los servicios de aplicación (app/services/) usan estas funciones
a través de ElementVerificationService.

Estructura:
-----------
common/             - Infraestructura común (SeismicCategory)
results.py          - Dataclasses y enums para resultados
reinforcement/      - Refuerzo mínimo distribuido (§18.10.2)
design_forces/      - Fuerzas de diseño, amplificación cortante (§18.10.3)
boundary_elements/  - Elementos de borde (§18.10.6)
coupling_beams/     - Vigas de acoplamiento (§18.10.7)
wall_piers/         - Pilares de muro (§18.10.8)
coupled_walls/      - Muros acoplados dúctiles (§18.10.9)
columns/            - Columnas sísmicas (§18.3.3, §18.4.3, §18.7)
beams/              - Vigas sísmicas (§18.3.2, §18.4.2, §18.6)
non_sfrs/           - Elementos no parte del SFRS (§18.14)

Integración con Servicios de Aplicación:
---------------------------------------
Todos los servicios de dominio están COMPLETAMENTE integrados en:
  app/services/analysis/element_verification_service.py

ElementVerificationService usa:
- SeismicBeamService      → verify() para vigas con is_seismic=True
- SeismicColumnService    → verify() para columnas con is_seismic=True
- NonSfrsService          → verify_non_sfrs() para elementos fuera del SFRS
- DuctileCoupledWallService → verify_coupled_wall_system() para muros acoplados

Funciones de Cálculo Directo:
----------------------------
calculate_design_shear(Vu, lu, Mpr_total, ...)
    Calcula Ve para diseño por capacidad según §18.7.6.1 y §18.10.8.1(a).
    Ve = min(Mpr_total/lu, Omega_o*Vu)

classify_wall_pier(lw, tw, hw)
    Clasifica elemento según Tabla R18.10.1.
    Determina si es columna, wall pier, o muro.

check_boundary_zone_reinforcement(...)
    Verifica refuerzo de zonas de borde en wall piers.

Uso desde ElementVerificationService:
------------------------------------
    from app.services.analysis import ElementVerificationService

    service = ElementVerificationService()

    # Vigas sísmicas (automático si beam.is_seismic=True)
    result = service.verify(beam, forces)
    seismic = result.seismic_beam  # SeismicBeamChecks

    # Columnas sísmicas (automático si column.is_seismic=True)
    result = service.verify(column, forces)
    seismic = result.seismic_column  # SeismicColumnChecks

    # Elementos no-SFRS (§18.14)
    result = service.verify_non_sfrs(element, delta_u=0.02, hsx=3000)

    # Muros acoplados dúctiles (§18.10.9)
    result = service.verify_coupled_wall_system(walls, coupling_beams)

Re-exports desde chapter11:
- WallLimitsService: Límites de espesor (§11.3, §11.7)
- WallDesignMethodsService: Métodos simplificado/esbelto (§11.5.3, §11.8)
"""
# Infraestructura común
from .common import SeismicCategory

# Servicios desde subdirectorios
from .design_forces import ShearAmplificationService
from .boundary_elements import BoundaryElementService
from .wall_piers import WallPierService
from .coupling_beams import CouplingBeamService
from .reinforcement import SeismicReinforcementService, SeismicReinforcementResult
from .columns import (
    # Servicios
    SeismicColumnService,
    SeismicColumnShearService,
    # Resultados
    SeismicColumnResult,
    SeismicColumnShearResult,
    ColumnShearCapacity,
    DimensionalLimitsResult,
    StrongColumnResult,
    LongitudinalReinforcementResult,
    TransverseReinforcementResult,
)
from .beams import (
    SeismicBeamService,
    SeismicBeamResult,
    BeamDimensionalLimitsResult,
    BeamLongitudinalResult,
    BeamTransverseResult,
    BeamShearResult,
)
from .non_sfrs import (
    NonSfrsService,
    NonSfrsResult,
    DriftCompatibilityResult,
    SlabColumnShearResult,
    DriftCheckType,
)
from .coupled_walls import (
    DuctileCoupledWallService,
    DuctileCoupledWallResult,
    WallGeometryCheck,
    CouplingBeamGeometryCheck,
    LevelComplianceResult,
)

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
    # Infraestructura común
    'SeismicCategory',
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
    # columns (§18.3.3, §18.4.3, §18.7)
    'SeismicColumnService',
    'SeismicColumnShearService',
    'SeismicColumnResult',
    'SeismicColumnShearResult',
    'ColumnShearCapacity',
    'DimensionalLimitsResult',
    'StrongColumnResult',
    'LongitudinalReinforcementResult',
    'TransverseReinforcementResult',
    # beams (§18.3.2, §18.4.2, §18.6)
    'SeismicBeamService',
    'SeismicBeamResult',
    'BeamDimensionalLimitsResult',
    'BeamLongitudinalResult',
    'BeamTransverseResult',
    'BeamShearResult',
    # non_sfrs (§18.14)
    'NonSfrsService',
    'NonSfrsResult',
    'DriftCompatibilityResult',
    'SlabColumnShearResult',
    'DriftCheckType',
    # coupling_beams (§18.10.7)
    'CouplingBeamService',
    'CouplingBeamDesignResult',
    'CouplingBeamType',
    'CouplingBeamClassification',
    'DiagonalShearResult',
    'DiagonalConfinementResult',
    'ReinforcementType',
    'ConfinementOption',
    # coupled_walls (§18.10.9)
    'DuctileCoupledWallService',
    'DuctileCoupledWallResult',
    'WallGeometryCheck',
    'CouplingBeamGeometryCheck',
    'LevelComplianceResult',
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
