# app/domain/chapter18/beams/__init__.py
"""
Vigas de pórticos sísmicos ACI 318-25.

Implementa verificaciones para:
- §18.3.2: Vigas de pórticos ordinarios
- §18.4.2: Vigas de pórticos intermedios
- §18.6: Vigas de pórticos especiales

Exporta:
- SeismicBeamService: Servicio principal de verificación
- Dataclasses de resultados
"""
from .service import SeismicBeamService
from .results import (
    SeismicBeamResult,
    BeamDimensionalLimitsResult,
    BeamLongitudinalResult,
    BeamTransverseResult,
    BeamShearResult,
)

__all__ = [
    "SeismicBeamService",
    "SeismicBeamResult",
    "BeamDimensionalLimitsResult",
    "BeamLongitudinalResult",
    "BeamTransverseResult",
    "BeamShearResult",
]
