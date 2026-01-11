# app/domain/chapter18/coupling_beams/diagonal.py
"""
Resistencia al cortante con refuerzo diagonal ACI 318-25 §18.10.7.4.

Ec. 18.10.7.4:
Vn = 2 * Avd * fy * sin(alpha) <= 10*sqrt(f'c)*Acw
"""
import math

from ...constants.phi_chapter21 import PHI_SHEAR_DIAGONAL
from ...constants.units import N_TO_TONF, TONF_TO_N
from ..results import DiagonalShearResult


def calculate_diagonal_shear_strength(
    Avd: float,
    fy: float,
    alpha_deg: float,
    fc: float,
    Acw: float
) -> DiagonalShearResult:
    """
    Calcula la resistencia al cortante con refuerzo diagonal.

    Según Ec. 18.10.7.4:
    Vn = 2 * Avd * fy * sin(alpha) <= 10*sqrt(f'c)*Acw

    Args:
        Avd: Área total de refuerzo en cada grupo diagonal (mm2)
        fy: Fluencia del acero (MPa)
        alpha_deg: Ángulo entre diagonales y eje longitudinal (grados)
        fc: f'c del hormigón (MPa)
        Acw: Área de la sección (mm2)

    Returns:
        DiagonalShearResult con resistencia calculada
    """
    # Convertir ángulo a radianes
    alpha_rad = math.radians(alpha_deg)

    # Calcular Vn
    # Unidades: mm2 * MPa = N
    Vn_calc_N = 2 * Avd * fy * math.sin(alpha_rad)

    # Límite máximo
    # 10 * sqrt(f'c) * Acw en unidades SI: 0.83 * sqrt(f'c) * Acw
    Vn_max_N = 0.83 * math.sqrt(fc) * Acw

    # Vn final
    Vn_N = min(Vn_calc_N, Vn_max_N)

    # Convertir a tonf
    Vn_calc = Vn_calc_N / N_TO_TONF
    Vn_max = Vn_max_N / N_TO_TONF
    Vn = Vn_N / N_TO_TONF

    return DiagonalShearResult(
        Avd=Avd,
        fy=fy,
        alpha_deg=alpha_deg,
        Vn_calc=round(Vn_calc, 2),
        Vn_max=round(Vn_max, 2),
        Vn=round(Vn, 2),
        phi_Vn=round(PHI_SHEAR_DIAGONAL * Vn, 2),  # φ=0.85 para refuerzo diagonal (§21.2.4.4)
        aci_reference="ACI 318-25 Ec. 18.10.7.4"
    )


def required_diagonal_area(
    Vu: float,
    fy: float,
    alpha_deg: float,
    phi: float = 0.85
) -> float:
    """
    Calcula el área de refuerzo diagonal requerida.

    De Ec. 18.10.7.4:
    Avd = Vu / (phi * 2 * fy * sin(alpha))

    Args:
        Vu: Demanda de cortante (tonf)
        fy: Fluencia del acero (MPa)
        alpha_deg: Ángulo de diagonales (grados)
        phi: Factor de reducción (default 0.85 para diagonal, §21.2.4.4)

    Returns:
        Área de refuerzo diagonal requerida en cada grupo (mm2)
    """
    # Convertir Vu a N
    Vu_N = Vu * TONF_TO_N

    alpha_rad = math.radians(alpha_deg)
    denominator = phi * 2 * fy * math.sin(alpha_rad)

    if denominator <= 0:
        return float('inf')

    Avd = Vu_N / denominator
    return round(Avd, 1)


def calculate_diagonal_angle(
    ln: float,
    h: float,
    cover: float = 40
) -> float:
    """
    Calcula el ángulo de las diagonales.

    El ángulo típico es aproximadamente:
    alpha = arctan((h - 2*cover) / ln)

    Args:
        ln: Claro libre (mm)
        h: Peralte de la viga (mm)
        cover: Recubrimiento (mm)

    Returns:
        Ángulo en grados
    """
    if ln <= 0:
        return 45.0

    vertical = h - 2 * cover
    alpha_rad = math.atan(vertical / ln)
    return round(math.degrees(alpha_rad), 1)
