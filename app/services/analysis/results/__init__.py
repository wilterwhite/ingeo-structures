# app/services/analysis/results/__init__.py
"""
Dataclasses de resultado para verificaciones estructurales.

Organizados por tipo de elemento:
- common: Resultados comunes (AciVerificationResult, SlendernessResult, etc.)
- beam: Verificaciones de vigas sismicas §18.6
- column: Verificaciones de columnas sismicas §18.7
- wall: Verificaciones de muros sismicos §18.10
"""
from .common import (
    AciVerificationResult,
    SlendernessResult,
    FlexureResult,
    BidirectionalShearResult,
    ShearResult,
)
from .beam import (
    SeismicBeamDimensionalResult,
    SeismicBeamLongitudinalResult,
    SeismicBeamTransverseResult,
    SeismicBeamShearResult,
    SeismicBeamChecks,
)
from .column import (
    SeismicColumnDimensionalResult,
    SeismicColumnStrongResult,
    SeismicColumnLongitudinalResult,
    SeismicColumnTransverseResult,
    SeismicColumnShearDetailedResult,
    SeismicColumnChecks,
)
from .wall import (
    WallClassification,
    BoundaryResult,
    EndZonesResult,
    MinReinforcementResult,
    WallChecks,
)

__all__ = [
    # Common
    'AciVerificationResult',
    'SlendernessResult',
    'FlexureResult',
    'BidirectionalShearResult',
    'ShearResult',
    # Beam
    'SeismicBeamDimensionalResult',
    'SeismicBeamLongitudinalResult',
    'SeismicBeamTransverseResult',
    'SeismicBeamShearResult',
    'SeismicBeamChecks',
    # Column
    'SeismicColumnDimensionalResult',
    'SeismicColumnStrongResult',
    'SeismicColumnLongitudinalResult',
    'SeismicColumnTransverseResult',
    'SeismicColumnShearDetailedResult',
    'SeismicColumnChecks',
    # Wall
    'WallClassification',
    'BoundaryResult',
    'EndZonesResult',
    'MinReinforcementResult',
    'WallChecks',
]
