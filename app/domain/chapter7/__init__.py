# app/domain/chapter7/__init__.py
"""
Capitulo 7 ACI 318-25: Losas en Una Direccion (One-Way Slabs).

Este modulo implementa los requisitos de diseno para losas
que tienen una relacion de luces largo/corto > 2.

Secciones principales:
- 7.3: Limites de diseno (espesor minimo)
- 7.6: Limites de refuerzo
- 7.7: Detallado del refuerzo
"""
from .limits import (
    get_minimum_thickness_one_way,
    check_thickness_one_way,
    THICKNESS_FACTORS,
)
from .reinforcement import (
    get_minimum_flexural_reinforcement,
    get_minimum_shrinkage_reinforcement,
    get_maximum_spacing,
    check_reinforcement_limits,
)

__all__ = [
    # Limites
    'get_minimum_thickness_one_way',
    'check_thickness_one_way',
    'THICKNESS_FACTORS',
    # Refuerzo
    'get_minimum_flexural_reinforcement',
    'get_minimum_shrinkage_reinforcement',
    'get_maximum_spacing',
    'check_reinforcement_limits',
]
