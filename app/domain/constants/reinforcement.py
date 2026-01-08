# app/domain/constants/reinforcement.py
"""
Constantes y verificaciones de refuerzo segun ACI 318-25.

Constantes:
    - RHO_MIN: Cuantia minima para muros (0.0025)
    - FY_DEFAULT_MPA: Fluencia por defecto del acero (420 MPa, A630-420H)
    - COVER_DEFAULT_PIER_MM: Recubrimiento por defecto muros (25 mm)
    - COVER_DEFAULT_COLUMN_MM: Recubrimiento por defecto columnas (40 mm)

Funciones:
    - check_rho_vertical_ge_horizontal: Verifica S18.10.4.3
    - is_rho_v_ge_rho_h_required: Determina si aplica verificacion
"""
from typing import Tuple

# =============================================================================
# CONSTANTES DE REFUERZO
# =============================================================================

# Cuantia minima de refuerzo para muros S11.6.1 y S18.10.2.1
RHO_MIN = 0.0025

# Espaciamiento maximo para muros especiales S18.10.2.1 (18 pulgadas)
MAX_SPACING_SEISMIC_MM = 457.0

# Fluencia por defecto del acero (MPa) - A630-420H
FY_DEFAULT_MPA = 420.0

# Recubrimientos por defecto (mm)
COVER_DEFAULT_PIER_MM = 25.0
COVER_DEFAULT_COLUMN_MM = 40.0
COVER_DEFAULT_BEAM_MM = 40.0

from .shear import HW_LW_SLENDER_LIMIT


def check_rho_vertical_ge_horizontal(
    hw: float,
    lw: float,
    rho_v: float,
    rho_h: float
) -> Tuple[bool, str]:
    """
    Verifica S18.10.4.3: Para hw/lw <= 2.0, rho_v >= rho_h.

    Requisito para muros bajos donde la resistencia al cortante
    depende mas del refuerzo vertical que del horizontal.

    Args:
        hw: Altura del muro (mm)
        lw: Longitud del muro (mm)
        rho_v: Cuantia de refuerzo vertical
        rho_h: Cuantia de refuerzo horizontal

    Returns:
        Tupla (es_ok, mensaje_advertencia)
        - es_ok: True si cumple o no aplica (hw/lw > 2.0)
        - mensaje: Advertencia si no cumple, cadena vacia si cumple
    """
    if lw <= 0:
        return True, ""

    hw_lw = hw / lw

    if hw_lw <= HW_LW_SLENDER_LIMIT:  # 2.0
        if rho_v < rho_h:
            warning = (
                f"ADVERTENCIA 18.10.4.3: Para hw/lw={hw_lw:.2f} <= 2.0, "
                f"se requiere rho_v >= rho_h. Actual: rho_v={rho_v:.5f}, "
                f"rho_h={rho_h:.5f}"
            )
            return False, warning

    return True, ""


def is_rho_v_ge_rho_h_required(hw: float, lw: float) -> bool:
    """
    Determina si se requiere verificar rho_v >= rho_h.

    Args:
        hw: Altura del muro (mm)
        lw: Longitud del muro (mm)

    Returns:
        True si hw/lw <= 2.0 (muro bajo)
    """
    if lw <= 0:
        return False
    return (hw / lw) <= HW_LW_SLENDER_LIMIT
