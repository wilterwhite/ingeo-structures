# app/domain/chapter11/__init__.py
"""
Requisitos generales de diseño según ACI 318-25 Capítulo 11.

Este módulo contiene verificaciones generales que aplican a elementos
estructurales sin requisitos sísmicos especiales.

Módulos:
- limits: Límites de diseño para muros (§11.3 espesor, §11.7 espaciamiento)
- design_methods: Métodos de diseño (§11.5.3 simplificado, §11.8 esbeltos)
- reinforcement: Cuantías mínimas de refuerzo (§11.6)

Nota: Los requisitos sísmicos especiales están en domain/chapter18/.
"""
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
from .reinforcement import (
    ReinforcementLimitsService,
    MinReinforcementResult,
    ShearReinforcementResult,
    BarSize,
)

__all__ = [
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
    # reinforcement
    'ReinforcementLimitsService',
    'MinReinforcementResult',
    'ShearReinforcementResult',
    'BarSize',
]
