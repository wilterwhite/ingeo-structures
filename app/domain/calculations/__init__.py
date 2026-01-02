# app/domain/calculations/__init__.py
"""
Módulo de cálculos del dominio.
Contiene calculadores puros sin dependencias de servicios.

Módulos:
- steel_layer_calculator: Capas de acero para diagramas P-M
- wall_continuity: Continuidad de muros y cálculo de hwcs
- confinement: Cálculos de confinamiento Ash/(s*bc) y rho_s
"""
from .steel_layer_calculator import SteelLayer, SteelLayerCalculator
from .wall_continuity import (
    WallContinuityService,
    WallContinuityInfo,
    BuildingInfo,
)
from .confinement import (
    calculate_ash_sbc,
    calculate_rho_s,
    calculate_confinement_requirements,
)

__all__ = [
    'SteelLayer',
    'SteelLayerCalculator',
    'WallContinuityService',
    'WallContinuityInfo',
    'BuildingInfo',
    'calculate_ash_sbc',
    'calculate_rho_s',
    'calculate_confinement_requirements',
]
