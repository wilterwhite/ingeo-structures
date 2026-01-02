# app/domain/chapter18/piers/__init__.py
"""
Módulo de pilares de muro ACI 318-25 §18.10.8.

Exporta:
- WallPierService: Servicio principal de verificación
- Funciones de clasificación, cortante, refuerzo transversal
- Dataclasses de resultados (desde results.py)
"""
from .service import WallPierService
from .classification import classify_wall_pier, COLUMN_MIN_THICKNESS_MM
from .shear_design import calculate_design_shear, verify_shear_strength
from .transverse import calculate_transverse_requirements, EXTENSION_MIN_MM

from ..results import (
    WallPierCategory,
    DesignMethod,
    WallPierClassification,
    WallPierShearDesign,
    WallPierTransverseReinforcement,
    WallPierBoundaryCheck,
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
    # Constantes
    "COLUMN_MIN_THICKNESS_MM",
    "EXTENSION_MIN_MM",
    # Enums y Dataclasses
    "WallPierCategory",
    "DesignMethod",
    "WallPierClassification",
    "WallPierShearDesign",
    "WallPierTransverseReinforcement",
    "WallPierBoundaryCheck",
    "WallPierDesignResult",
]
