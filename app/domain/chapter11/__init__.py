# app/domain/chapter11/__init__.py
"""
Requisitos generales de diseño según ACI 318-25 Capítulo 11.

Este módulo contiene verificaciones generales que aplican a elementos
estructurales sin requisitos sísmicos especiales.

Módulos:
- limits: Límites de diseño para muros (§11.3 espesor, §11.7 espaciamiento)
- design_methods: Método alternativo para muros esbeltos (§11.8)
- reinforcement: Cuantías mínimas de refuerzo (§11.6)

NOTA SOBRE MÉTODO SIMPLIFICADO (§11.5.3):
=========================================
El método simplificado (Ec. 11.5.3.1: Pn = 0.55*f'c*Ag*[1-(k*lc/32h)^2])
NO SE IMPLEMENTA porque solo aplica cuando e <= h/6 (carga casi centrada).

Esta aplicación usa diagramas de interacción P-M para muros sísmicos con
momentos significativos, donde el método correcto es la magnificación de
momentos según ACI 318-25 §6.6.4: Mc = δns × Mu

Ver domain/flexure/slenderness.py para la implementación de δns.

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
    SlenderWallService,
    SlenderWallResult,
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
    # design_methods (§11.8 muros esbeltos)
    'SlenderWallService',
    'SlenderWallResult',
    # reinforcement
    'ReinforcementLimitsService',
    'MinReinforcementResult',
    'ShearReinforcementResult',
    'BarSize',
]
