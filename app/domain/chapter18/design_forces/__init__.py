# app/domain/chapter18/amplification/__init__.py
"""
Módulo de amplificación de cortante ACI 318-25 §18.10.3.3.

Exporta:
- ShearAmplificationService: Servicio principal
- Funciones de cálculo de factores
- Dataclasses de resultados (desde results.py)
"""
from .service import ShearAmplificationService
from .factors import (
    calculate_omega_v,
    calculate_omega_v_dyn,
    calculate_factors,
)
from ..results import (
    ShearAmplificationResult,
    ShearAmplificationFactors,
    SpecialWallRequirements,
)

__all__ = [
    # Servicio
    "ShearAmplificationService",
    # Funciones
    "calculate_omega_v",
    "calculate_omega_v_dyn",
    "calculate_factors",
    # Dataclasses
    "ShearAmplificationResult",
    "ShearAmplificationFactors",
    "SpecialWallRequirements",
]
