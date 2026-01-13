# app/domain/shear/combined.py
"""
Cálculos de cortante combinado biaxial.

Proporciona funciones para combinar cortantes en dos direcciones
usando el método SRSS (Square Root of Sum of Squares).

Referencias:
- ACI 318-25: Combinación de efectos biaxiales
"""
import math


def calculate_combined_dcr(sf_v2: float, sf_v3: float) -> float:
    """
    Calcula el DCR combinado de cortante biaxial usando SRSS.

    Fórmula: DCR_combined = sqrt((1/SF_V2)² + (1/SF_V3)²)

    Args:
        sf_v2: Factor de seguridad en dirección V2 (V2u/φVn2)
        sf_v3: Factor de seguridad en dirección V3 (V3u/φVn3)

    Returns:
        DCR combinado (0 si ambos SF son muy altos o <= 0)

    Example:
        >>> calculate_combined_dcr(2.0, 2.0)  # DCR = sqrt(0.5² + 0.5²) ≈ 0.707
        0.707
    """
    dcr_v2 = 1.0 / sf_v2 if sf_v2 > 0 else 0
    dcr_v3 = 1.0 / sf_v3 if sf_v3 > 0 else 0
    dcr_combined = math.sqrt(dcr_v2**2 + dcr_v3**2)
    return round(dcr_combined, 3)


__all__ = [
    'calculate_combined_dcr',
]
