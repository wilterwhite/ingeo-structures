# app/domain/chapter8/__init__.py
"""
Capitulo 8 ACI 318-25: Losas en Dos Direcciones (Two-Way Slabs).

Este modulo implementa los requisitos de diseno para losas
que trabajan en dos direcciones, incluyendo:
- Losas planas (flat plates)
- Losas con abacos (flat slabs with drop panels)
- Losas con vigas

Secciones principales:
- 8.3: Limites de diseno (espesor minimo)
- 8.6-8.7: Limites y detallado de refuerzo
- 8.10: Cortante bidireccional (punzonamiento)
"""
from .limits import (
    get_minimum_thickness_two_way,
    check_thickness_two_way,
    TwoWaySystem,
)
from .punching import (
    calculate_punching_Vc,
    calculate_critical_perimeter,
    ColumnPosition,
    PunchingResult,
)

__all__ = [
    # Limites
    'get_minimum_thickness_two_way',
    'check_thickness_two_way',
    'TwoWaySystem',
    # Punzonamiento
    'calculate_punching_Vc',
    'calculate_critical_perimeter',
    'ColumnPosition',
    'PunchingResult',
]
