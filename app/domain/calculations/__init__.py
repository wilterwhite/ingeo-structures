# app/domain/calculations/__init__.py
"""
Módulo de cálculos del dominio.
Contiene calculadores puros sin dependencias de servicios.

Módulos:
- steel_layer_calculator: Capas de acero para diagramas P-M
- wall_continuity: Continuidad de muros y cálculo de hwcs
"""
from .steel_layer_calculator import SteelLayer, SteelLayerCalculator
from .wall_continuity import (
    WallContinuityService,
    WallContinuityInfo,
    BuildingInfo,
)

__all__ = [
    'SteelLayer',
    'SteelLayerCalculator',
    'WallContinuityService',
    'WallContinuityInfo',
    'BuildingInfo',
]
