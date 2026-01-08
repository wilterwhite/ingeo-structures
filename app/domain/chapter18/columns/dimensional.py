# app/domain/chapter18/columns/dimensional.py
"""
Límites dimensionales para columnas sísmicas ACI 318-25.

§18.7.2 - Límites dimensionales para columnas de pórticos especiales:
- (a) Dimensión mínima >= 300mm (12")
- (b) Relación de aspecto >= 0.4

Referencias:
- ACI 318-25 §18.7.2.1
"""
from .results import DimensionalLimitsResult

# Constantes
MIN_DIMENSION_SPECIAL_MM = 300  # 12 pulgadas en mm
MIN_ASPECT_RATIO_SPECIAL = 0.4


def check_dimensional_limits(
    b: float,
    h: float,
) -> DimensionalLimitsResult:
    """
    Verifica límites dimensionales según §18.7.2.

    Para columnas de pórticos especiales:
    - (a) Dimensión mínima >= 300mm medida en línea recta por el centroide
    - (b) Relación de aspecto b/h >= 0.4

    Args:
        b: Dimensión menor de la sección (mm)
        h: Dimensión mayor de la sección (mm)

    Returns:
        DimensionalLimitsResult con verificación completa
    """
    # Asegurar que b <= h
    if b > h:
        b, h = h, b

    min_dim = b
    aspect_ratio = b / h if h > 0 else 0

    min_dim_ok = min_dim >= MIN_DIMENSION_SPECIAL_MM
    aspect_ok = aspect_ratio >= MIN_ASPECT_RATIO_SPECIAL

    return DimensionalLimitsResult(
        min_dimension=min_dim,
        min_dimension_required=MIN_DIMENSION_SPECIAL_MM,
        min_dimension_ok=min_dim_ok,
        aspect_ratio=round(aspect_ratio, 3),
        aspect_ratio_required=MIN_ASPECT_RATIO_SPECIAL,
        aspect_ratio_ok=aspect_ok,
        is_ok=min_dim_ok and aspect_ok,
    )
