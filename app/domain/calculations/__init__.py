# app/structural/domain/calculations/__init__.py
"""
Módulo de cálculos del dominio.
Contiene calculadores puros sin dependencias de servicios.
"""
from .steel_layer_calculator import SteelLayer, SteelLayerCalculator
from .reinforcement_calculator import (
    ReinforcementCalculator,
    ReinforcementProperties,
    BAR_AREAS
)
from .flexure_checker import FlexureChecker, FlexureCheckResult

__all__ = [
    'SteelLayer',
    'SteelLayerCalculator',
    'ReinforcementCalculator',
    'ReinforcementProperties',
    'BAR_AREAS',
    'FlexureChecker',
    'FlexureCheckResult'
]
