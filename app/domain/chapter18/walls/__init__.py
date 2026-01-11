# app/domain/chapter18/walls/__init__.py
"""
Módulo de muros sísmicos especiales ACI 318-25 §18.10.

Exporta:
- SeismicWallService: Servicio principal de verificación
- Dataclasses de resultados
"""
from .service import SeismicWallService
from .results import (
    SeismicWallResult,
    WallClassificationResult,
    WallReinforcementResult,
    WallShearResult,
    WallBoundaryResult,
)

__all__ = [
    # Servicio
    "SeismicWallService",
    # Resultados
    "SeismicWallResult",
    "WallClassificationResult",
    "WallReinforcementResult",
    "WallShearResult",
    "WallBoundaryResult",
]
