# app/domain/chapter22/__init__.py
"""
Capacidad de flexion y cortante segun ACI 318-25 Capitulo 22.

Este modulo centraliza los calculos de capacidad para elementos
de hormigon armado:
- 22.2: Capacidad a flexion (Mn)
- 22.5: Capacidad al corte (Vc para elementos sin refuerzo de corte)

Los factores phi se importan de constants/phi_chapter21.py
"""
from .flexural_capacity import (
    calculate_flexural_capacity,
    calculate_As_required,
    FlexuralCapacityResult,
)

__all__ = [
    'calculate_flexural_capacity',
    'calculate_As_required',
    'FlexuralCapacityResult',
]
