# app/domain/calculations/__init__.py
"""
Módulo de cálculos del dominio.
Contiene calculadores puros sin dependencias de servicios.

Módulos:
- steel_layer_calculator: Capas de acero para diagramas P-M
- wall_continuity: Continuidad de muros y cálculo de hwcs
- confinement: Cálculos de confinamiento Ash/(s*bc) y rho_s
- minimum_reinforcement: Cálculo de armadura mínima para muros
- wall_boundary_zone: Zona de borde 0.15×lw para muros
- coupling_beam_capacity: Capacidad Mn/Mpr de vigas de acople
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
from .minimum_reinforcement import (
    MinimumReinforcementCalculator,
    MinimumReinforcementConfig,
)
from .wall_boundary_zone import WallBoundaryZoneService
from .coupling_beam_capacity import CouplingBeamCapacityService

__all__ = [
    'SteelLayer',
    'SteelLayerCalculator',
    'WallContinuityService',
    'WallContinuityInfo',
    'BuildingInfo',
    'calculate_ash_sbc',
    'calculate_rho_s',
    'calculate_confinement_requirements',
    'MinimumReinforcementCalculator',
    'MinimumReinforcementConfig',
    'WallBoundaryZoneService',
    'CouplingBeamCapacityService',
]
