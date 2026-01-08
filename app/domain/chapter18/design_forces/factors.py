# app/domain/chapter18/amplification/factors.py
"""
Cálculo de factores de amplificación de cortante según ACI 318-25 §18.10.3.3.

Tabla 18.10.3.3.3:
| hwcs/lw    | Omega_v           | omega_v                      |
|------------|-------------------|------------------------------|
| <= 1.0     | 1.0               | 1.0                          |
| 1.0 - 2.0  | interpolación     | 1.0                          |
| >= 2.0     | 1.5               | 0.8 + 0.09×hn^(1/3) >= 1.0   |
"""
from typing import Optional

from ...constants.shear import (
    OMEGA_V_MIN,
    OMEGA_V_MAX,
    OMEGA_V_DYN_COEF,
    OMEGA_V_DYN_BASE,
    OMEGA_V_DYN_MIN,
    WALL_PIER_HW_LW_LIMIT,
)
from ..results import ShearAmplificationFactors


def calculate_omega_v(hwcs: float, lw: float) -> float:
    """
    Calcula factor de sobrerresistencia Omega_v según Tabla 18.10.3.3.3.

    Args:
        hwcs: Altura del muro desde sección crítica (mm)
        lw: Longitud del muro (mm)

    Returns:
        Factor Omega_v (1.0 a 1.5)
    """
    if lw <= 0:
        return OMEGA_V_MIN

    ratio = hwcs / lw

    if ratio <= 1.0:
        return OMEGA_V_MIN
    elif ratio >= WALL_PIER_HW_LW_LIMIT:
        return OMEGA_V_MAX
    else:
        # Interpolación lineal entre 1.0 y 2.0
        return OMEGA_V_MIN + (OMEGA_V_MAX - OMEGA_V_MIN) * (ratio - 1.0)


def calculate_omega_v_dyn(
    hwcs: float,
    lw: float,
    hn_ft: Optional[float] = None
) -> float:
    """
    Calcula factor de amplificación dinámica omega_v según Tabla 18.10.3.3.3.

    Args:
        hwcs: Altura del muro desde sección crítica (mm)
        lw: Longitud del muro (mm)
        hn_ft: Altura total del edificio en pies

    Returns:
        Factor omega_v (>= 1.0)
    """
    if lw <= 0:
        return OMEGA_V_DYN_MIN

    ratio = hwcs / lw

    if ratio < WALL_PIER_HW_LW_LIMIT:
        return OMEGA_V_DYN_MIN

    # Para hwcs/lw >= 2.0: omega_v = 0.8 + 0.09 × hn^(1/3) >= 1.0
    if hn_ft is None or hn_ft <= 0:
        return OMEGA_V_DYN_MIN

    omega_v_dyn = OMEGA_V_DYN_BASE + OMEGA_V_DYN_COEF * (hn_ft ** (1/3))
    return max(OMEGA_V_DYN_MIN, omega_v_dyn)


def calculate_factors(
    hwcs: float,
    lw: float,
    hn_ft: float = 0
) -> ShearAmplificationFactors:
    """
    Calcula factores de amplificación según Tabla 18.10.3.3.3.

    Args:
        hwcs: Altura del muro desde sección crítica (mm)
        lw: Longitud del muro (mm)
        hn_ft: Altura del edificio en pies

    Returns:
        ShearAmplificationFactors con los factores calculados
    """
    if lw <= 0:
        return ShearAmplificationFactors(
            Omega_v=1.0, omega_v_dyn=1.0, combined=1.0,
            hwcs_lw=0, hn_ft=hn_ft,
            aci_reference="ACI 318-25 Tabla 18.10.3.3.3"
        )

    omega_v = calculate_omega_v(hwcs, lw)
    omega_v_dyn_val = calculate_omega_v_dyn(hwcs, lw, hn_ft if hn_ft > 0 else None)

    return ShearAmplificationFactors(
        Omega_v=round(omega_v, 3),
        omega_v_dyn=round(omega_v_dyn_val, 3),
        combined=round(omega_v * omega_v_dyn_val, 3),
        hwcs_lw=round(hwcs / lw, 2),
        hn_ft=hn_ft,
        aci_reference="ACI 318-25 Tabla 18.10.3.3.3"
    )
