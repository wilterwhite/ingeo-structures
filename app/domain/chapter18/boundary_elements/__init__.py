# app/domain/chapter18/boundary_elements/__init__.py
"""
Módulo de elementos de borde ACI 318-25 §18.10.6.

Exporta:
- BoundaryElementService: Servicio principal de verificación
- Funciones de verificación por desplazamiento, esfuerzos, etc.
- Dataclasses de resultados (desde results.py)
"""
from .service import BoundaryElementService
from .displacement import check_displacement_method, check_drift_capacity
from .stress import check_stress_method, calculate_boundary_stress
from .dimensions import calculate_dimensions
from .confinement import (
    calculate_transverse_reinforcement,
    max_tie_spacing,
    check_horizontal_reinforcement_termination,
)

from ..results import (
    BoundaryElementMethod,
    DisplacementCheckResult,
    StressCheckResult,
    BoundaryStressAnalysis,
    BoundaryElementDimensions,
    BoundaryTransverseReinforcement,
    BoundaryElementResult,
)

__all__ = [
    # Servicio
    "BoundaryElementService",
    # Funciones
    "check_displacement_method",
    "check_drift_capacity",
    "check_stress_method",
    "calculate_boundary_stress",
    "calculate_dimensions",
    "calculate_transverse_reinforcement",
    "max_tie_spacing",
    "check_horizontal_reinforcement_termination",
    # Enums y Dataclasses
    "BoundaryElementMethod",
    "DisplacementCheckResult",
    "StressCheckResult",
    "BoundaryStressAnalysis",
    "BoundaryElementDimensions",
    "BoundaryTransverseReinforcement",
    "BoundaryElementResult",
]
