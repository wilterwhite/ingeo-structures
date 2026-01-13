# app/domain/chapter18/columns/dimensional.py
"""
Límites dimensionales para columnas sísmicas ACI 318-25.

§18.7.2 - Límites dimensionales para columnas de pórticos especiales:
- (a) Dimensión mínima >= 300mm (12")
- (b) Relación de aspecto >= 0.4

Este módulo delega al servicio unificado de geometría (app.domain.geometry)
pero mantiene la interfaz DimensionalLimitsResult para compatibilidad.

Referencias:
- ACI 318-25 §18.7.2.1
"""
from .results import DimensionalLimitsResult
from ...geometry import GeometryChecksService
from ...constants.geometry import COLUMN_MIN_DIMENSION_MM, COLUMN_MIN_ASPECT_RATIO

# Servicio de geometría (singleton-like)
_geometry_service = GeometryChecksService()


def check_dimensional_limits(
    b: float,
    h: float,
) -> DimensionalLimitsResult:
    """
    Verifica límites dimensionales según §18.7.2.

    Para columnas de pórticos especiales:
    - (a) Dimensión mínima >= 300mm medida en línea recta por el centroide
    - (b) Relación de aspecto b/h >= 0.4

    Delega al GeometryChecksService para la lógica de verificación,
    pero retorna DimensionalLimitsResult para compatibilidad.

    Args:
        b: Dimensión menor de la sección (mm)
        h: Dimensión mayor de la sección (mm)

    Returns:
        DimensionalLimitsResult con verificación completa
    """
    # Delegar a servicio unificado
    result = _geometry_service.check_column(b, h)

    # Convertir a DimensionalLimitsResult para compatibilidad
    return DimensionalLimitsResult(
        min_dimension=result.values['min_dimension'],
        min_dimension_required=result.values['min_dimension_required'],
        min_dimension_ok=result.checks['min_dimension'],
        aspect_ratio=round(result.values['aspect_ratio'], 3),
        aspect_ratio_required=result.values['aspect_ratio_required'],
        aspect_ratio_ok=result.checks['aspect_ratio'],
        is_ok=result.is_ok,
    )
