# app/domain/proposals/strategies/__init__.py
"""
Estrategias de propuesta por modo de falla.

Cada estrategia implementa la búsqueda iterativa específica
para resolver un tipo de falla particular.
"""
from .flexure import propose_for_flexure
from .shear import propose_for_shear
from .combined import propose_combined
from .reduction import propose_for_reduction
from .thickness import propose_with_thickness, propose_for_slenderness
from .column_min import propose_for_column_min_thickness

__all__ = [
    "propose_for_flexure",
    "propose_for_shear",
    "propose_combined",
    "propose_for_reduction",
    "propose_with_thickness",
    "propose_for_slenderness",
    "propose_for_column_min_thickness",
]
