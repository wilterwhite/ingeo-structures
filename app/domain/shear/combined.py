# app/domain/shear/combined.py
"""
Cálculos de cortante combinado biaxial.

Proporciona funciones para combinar cortantes en dos direcciones
usando el método SRSS (Square Root of Sum of Squares).

Referencias:
- ACI 318-25: Combinación de efectos biaxiales
"""
import math
from typing import Union


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


def calculate_combined_sf(sf_v2: float, sf_v3: float) -> Union[float, str]:
    """
    Calcula el SF combinado de cortante biaxial.

    Fórmula: SF_combined = 1 / DCR_combined

    Args:
        sf_v2: Factor de seguridad en dirección V2
        sf_v3: Factor de seguridad en dirección V3

    Returns:
        SF combinado como float, o '>100' si DCR < 0.01

    Example:
        >>> calculate_combined_sf(2.0, 2.0)
        1.41
    """
    dcr_combined = calculate_combined_dcr(sf_v2, sf_v3)
    if dcr_combined < 0.01:
        return '>100'
    sf_combined = 1.0 / dcr_combined
    return round(sf_combined, 2) if sf_combined < 100 else '>100'


def calculate_combined_dcr_from_values(
    Vu_v2: float,
    Vu_v3: float,
    phi_Vn_v2: float,
    phi_Vn_v3: float,
) -> float:
    """
    Calcula DCR combinado directamente desde cortantes y capacidades.

    DCR_combined = sqrt((Vu_v2/φVn_v2)² + (Vu_v3/φVn_v3)²)

    Args:
        Vu_v2: Cortante último en dirección V2
        Vu_v3: Cortante último en dirección V3
        phi_Vn_v2: Capacidad φVn en dirección V2
        phi_Vn_v3: Capacidad φVn en dirección V3

    Returns:
        DCR combinado

    Example:
        >>> calculate_combined_dcr_from_values(100, 100, 200, 200)
        0.707
    """
    dcr_v2 = Vu_v2 / phi_Vn_v2 if phi_Vn_v2 > 0 else float('inf')
    dcr_v3 = Vu_v3 / phi_Vn_v3 if phi_Vn_v3 > 0 else float('inf')
    dcr_combined = math.sqrt(dcr_v2**2 + dcr_v3**2)
    return round(dcr_combined, 3)


__all__ = [
    'calculate_combined_dcr',
    'calculate_combined_sf',
    'calculate_combined_dcr_from_values',
]
