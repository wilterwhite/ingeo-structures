# app/domain/chapter18/columns/__init__.py
"""
Columnas de pórticos sísmicos ACI 318-25.

Implementa verificaciones para:
- §18.3.3: Columnas de pórticos ordinarios
- §18.4.3: Columnas de pórticos intermedios
- §18.7: Columnas de pórticos especiales

Exporta:
- SeismicColumnService: Servicio principal de verificación
- SeismicColumnShearService: Verificación de cortante §18.7.6
- Dataclasses de resultados
"""
from .service import SeismicColumnService
from .shear import SeismicColumnShearService
from .results import (
    # Resultados de columnas
    SeismicColumnResult,
    SeismicColumnShearResult,
    ColumnShearCapacity,
    DimensionalLimitsResult,
    StrongColumnResult,
    LongitudinalReinforcementResult,
    TransverseReinforcementResult,
)

# Funciones de verificación individuales
from .dimensional import check_dimensional_limits
from .flexural_strength import check_strong_column_weak_beam
from .longitudinal import check_longitudinal_reinforcement
from .transverse import (
    check_transverse_reinforcement,
    calculate_lo,
    calculate_s_max,
    calculate_Ash_sbc_required,
    calculate_rho_s_required,
)

__all__ = [
    # Servicios
    "SeismicColumnService",
    "SeismicColumnShearService",
    # Resultados
    "SeismicColumnResult",
    "SeismicColumnShearResult",
    "ColumnShearCapacity",
    "DimensionalLimitsResult",
    "StrongColumnResult",
    "LongitudinalReinforcementResult",
    "TransverseReinforcementResult",
    # Funciones de verificación
    "check_dimensional_limits",
    "check_strong_column_weak_beam",
    "check_longitudinal_reinforcement",
    "check_transverse_reinforcement",
    "calculate_lo",
    "calculate_s_max",
    "calculate_Ash_sbc_required",
    "calculate_rho_s_required",
]
