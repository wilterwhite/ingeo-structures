# app/domain/chapter18/non_sfrs/__init__.py
"""
Miembros no parte del SFRS - ACI 318-25 §18.14.

Para estructuras en SDC D, E, F, los miembros que no forman parte del
sistema resistente a fuerzas sísmicas (SFRS) deben verificarse para
compatibilidad de deriva.

Exporta:
- NonSfrsService: Servicio principal de verificación
- Dataclasses de resultados
"""
from .service import NonSfrsService
from .results import (
    NonSfrsResult,
    DriftCompatibilityResult,
    SlabColumnShearResult,
    DriftCheckType,
)

__all__ = [
    "NonSfrsService",
    "NonSfrsResult",
    "DriftCompatibilityResult",
    "SlabColumnShearResult",
    "DriftCheckType",
]
