# app/domain/chapter18/coupling_beams/__init__.py
"""
Módulo de vigas de acoplamiento ACI 318-25 §18.10.7.

Exporta:
- CouplingBeamService: Servicio principal de diseño
- Funciones de clasificación, diagonal, confinamiento
- Dataclasses de resultados (desde results.py)
"""
from .service import CouplingBeamService
from .classification import classify_coupling_beam
from .diagonal import (
    calculate_diagonal_shear_strength,
    required_diagonal_area,
    calculate_diagonal_angle,
)
from .confinement import (
    calculate_diagonal_confinement,
    check_shear_redistribution,
    check_penetration_limits,
)

from ..results import (
    CouplingBeamType,
    ReinforcementType,
    ConfinementOption,
    CouplingBeamClassification,
    DiagonalShearResult,
    DiagonalConfinementResult,
    CouplingBeamDesignResult,
)

__all__ = [
    # Servicio
    "CouplingBeamService",
    # Funciones
    "classify_coupling_beam",
    "calculate_diagonal_shear_strength",
    "required_diagonal_area",
    "calculate_diagonal_angle",
    "calculate_diagonal_confinement",
    "check_shear_redistribution",
    "check_penetration_limits",
    # Enums y Dataclasses
    "CouplingBeamType",
    "ReinforcementType",
    "ConfinementOption",
    "CouplingBeamClassification",
    "DiagonalShearResult",
    "DiagonalConfinementResult",
    "CouplingBeamDesignResult",
]
