# app/domain/chapter18/piers/__init__.py
"""
Módulo de pilares de muro ACI 318-25 §18.10.8.

Exporta:
- WallPierService: Servicio principal de verificación
- Funciones de clasificación, cortante, refuerzo transversal
- Dataclasses de resultados (desde results.py)
"""
from .service import WallPierService
from .classification import classify_wall_pier
from .shear_design import calculate_design_shear, verify_shear_strength
from ...constants.units import MIN_COLUMN_DIMENSION_MM
from .transverse import calculate_transverse_requirements, EXTENSION_MIN_MM
from .boundary_zones import check_boundary_zone_reinforcement

from ..results import (
    WallPierCategory,
    DesignMethod,
    WallPierClassification,
    WallPierShearDesign,
    WallPierTransverseReinforcement,
    WallPierBoundaryCheck,
    BoundaryZoneCheck,
    EdgePierCheck,
    WallPierDesignResult,
)

__all__ = [
    # Servicio
    "WallPierService",
    # Funciones
    "classify_wall_pier",
    "calculate_design_shear",
    "verify_shear_strength",
    "calculate_transverse_requirements",
    "check_boundary_zone_reinforcement",
    # Constantes
    "MIN_COLUMN_DIMENSION_MM",
    "EXTENSION_MIN_MM",
    # Enums y Dataclasses
    "WallPierCategory",
    "DesignMethod",
    "WallPierClassification",
    "WallPierShearDesign",
    "WallPierTransverseReinforcement",
    "WallPierBoundaryCheck",
    "BoundaryZoneCheck",
    "EdgePierCheck",
    "WallPierDesignResult",
]
