# app/domain/constants/reinforcement.py
"""
Verificaciones de refuerzo según ACI 318-25.

Contiene función compartida para verificar rho_v >= rho_h
usada en shear/verification.py, chapter18/amplification/, chapter11/reinforcement.py.
"""
from typing import Tuple

from .shear import HW_LW_SLENDER_LIMIT


def check_rho_vertical_ge_horizontal(
    hw: float,
    lw: float,
    rho_v: float,
    rho_h: float
) -> Tuple[bool, str]:
    """
    Verifica §18.10.4.3: Para hw/lw <= 2.0, rho_v >= rho_h.

    Requisito para muros bajos donde la resistencia al cortante
    depende más del refuerzo vertical que del horizontal.

    Args:
        hw: Altura del muro (mm)
        lw: Longitud del muro (mm)
        rho_v: Cuantía de refuerzo vertical
        rho_h: Cuantía de refuerzo horizontal

    Returns:
        Tupla (es_ok, mensaje_advertencia)
        - es_ok: True si cumple o no aplica (hw/lw > 2.0)
        - mensaje: Advertencia si no cumple, cadena vacía si cumple
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
