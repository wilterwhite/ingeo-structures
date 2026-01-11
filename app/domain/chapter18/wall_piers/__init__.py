# app/domain/chapter18/wall_piers/__init__.py
"""
Módulo especializado para pilares de muro ACI 318-25 §18.10.8.

DEFINICIÓN (Tabla R18.10.1):
Un "wall pier" (pilar de muro) es un segmento vertical de muro que cumple:
- lw/tw ≤ 6.0 (relación longitud/espesor)
- hw/lw < 2.0 (relación altura/longitud)

DIFERENCIA CON walls/:
- walls/: Orquestador general para TODOS los muros sísmicos (§18.10.2-6).
- wall_piers/: Servicio especializado que walls/ invoca cuando detecta lw/tw ≤ 6.0.

REQUISITOS ADICIONALES (§18.10.8):
- §18.10.8.1(a): Cortante por capacidad o Ω₀×Vu
- §18.10.8.1(b): Vn según §18.10.4
- §18.10.8.1(c)-(e): Refuerzo transversal con ganchos de 180°
- §18.10.8.1(f): Elementos de borde según §18.10.6.3

CLASIFICACIÓN POR lw/bw:
- lw/bw ≤ 2.5: Diseñar como columna especial (§18.7)
- 2.5 < lw/bw ≤ 6.0: Método alternativo permitido (§18.10.8.1)

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
