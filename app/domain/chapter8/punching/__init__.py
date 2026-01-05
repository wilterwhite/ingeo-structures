# app/domain/chapter8/punching/__init__.py
"""
Capitulo 8.10 y 22.6 ACI 318-25: Cortante Bidireccional (Punzonamiento).

Este modulo implementa la verificacion de cortante por punzonamiento
en conexiones losa-columna.

Secciones principales:
- 8.10: Requisitos generales de cortante en losas 2-Way
- 22.6: Resistencia al cortante bidireccional (Vc)
"""
from .critical_section import (
    calculate_critical_perimeter,
    calculate_critical_area,
    ColumnPosition,
)
from .vc_calculation import (
    calculate_punching_Vc,
    calculate_lambda_s,
    PunchingResult,
)

__all__ = [
    'calculate_critical_perimeter',
    'calculate_critical_area',
    'calculate_punching_Vc',
    'calculate_lambda_s',
    'ColumnPosition',
    'PunchingResult',
]
