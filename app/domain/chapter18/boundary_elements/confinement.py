# app/domain/chapter18/boundary_elements/confinement.py
"""
Refuerzo transversal para elementos de borde ACI 318-25 §18.10.6.4.

Incluye:
- Tabla 18.10.6.4(g): Ash/(s*bc) y rho_s
- §18.10.6.4(e): Espaciamiento máximo
- §18.10.6.4(f): Espaciamiento hx
- Tabla 18.10.6.5(b): Espaciamiento máximo por grado
"""
import math

from ...calculations.confinement import calculate_ash_sbc, calculate_rho_s
from ...constants.materials import SteelGrade
from ...constants.units import N_TO_TONF
from ..results import BoundaryTransverseReinforcement


def calculate_transverse_reinforcement(
    Ag: float,
    Ach: float,
    fc: float,
    fyt: float,
    b: float
) -> BoundaryTransverseReinforcement:
    """
    Calcula el refuerzo transversal requerido para elemento de borde.

    Según Tabla 18.10.6.4(g):
    - Ash/(s*bc) >= max(0.3*(Ag/Ach-1)*(f'c/fyt), 0.09*(f'c/fyt))
    - rho_s >= max(0.45*(Ag/Ach-1)*(f'c/fyt), 0.12*(f'c/fyt))

    Según 18.10.6.4(e):
    - Espaciamiento <= 1/3 de dimensión menor del elemento de borde

    Según 18.10.6.4(f):
    - hx <= menor de 14" (356 mm) y (2/3)*b

    Args:
        Ag: Área bruta del elemento de borde (mm2)
        Ach: Área del núcleo confinado (mm2)
        fc: f'c del hormigón (MPa)
        fyt: fy del refuerzo transversal (MPa)
        b: Dimensión menor del elemento de borde (mm)

    Returns:
        BoundaryTransverseReinforcement con requisitos
    """
    # Usar funciones compartidas de calculations/confinement.py
    Ash_sbc = calculate_ash_sbc(Ag, Ach, fc, fyt)
    rho_s = calculate_rho_s(Ag, Ach, fc, fyt)

    # Espaciamiento máximo
    spacing_max = b / 3

    # Espaciamiento hx máximo
    hx_max = min(356.0, (2/3) * b)

    return BoundaryTransverseReinforcement(
        Ash_sbc_required=round(Ash_sbc, 5),
        rho_s_required=round(rho_s, 5),
        spacing_max=round(spacing_max, 1),
        hx_max=round(hx_max, 1),
        Ag=Ag,
        Ach=Ach,
        fc=fc,
        fyt=fyt,
        aci_reference="ACI 318-25 Tabla 18.10.6.4(g)"
    )


def max_tie_spacing(
    steel_grade: SteelGrade,
    db: float,
    near_critical: bool = True
) -> float:
    """
    Obtiene espaciamiento máximo de refuerzo transversal en borde.

    Según Tabla 18.10.6.5(b):

    | Grado | Cerca de sección crítica | Otras ubicaciones |
    |-------|-------------------------|-------------------|
    | 60    | min(6*db, 6")          | min(8*db, 8")     |
    | 80    | min(5*db, 6")          | min(6*db, 6")     |
    | 100   | min(4*db, 6")          | min(6*db, 6")     |

    Args:
        steel_grade: Grado del acero (60, 80, 100)
        db: Diámetro de barra longitudinal más pequeña (mm)
        near_critical: True si está dentro de lw o Mu/(4*Vu)
                      de la sección crítica

    Returns:
        Espaciamiento máximo en mm
    """
    # Convertir pulgadas a mm
    SIX_INCH = 152.4
    EIGHT_INCH = 203.2

    if steel_grade == SteelGrade.GRADE_60:
        if near_critical:
            return min(6 * db, SIX_INCH)
        else:
            return min(8 * db, EIGHT_INCH)

    elif steel_grade == SteelGrade.GRADE_80:
        if near_critical:
            return min(5 * db, SIX_INCH)
        else:
            return min(6 * db, SIX_INCH)

    else:  # GRADE_100
        if near_critical:
            return min(4 * db, SIX_INCH)
        else:
            return min(6 * db, SIX_INCH)


def check_horizontal_reinforcement_termination(
    omega_v: float,
    Omega_v: float,
    Vu: float,
    lambda_factor: float,
    fc: float,
    Acv: float
) -> dict:
    """
    Verifica requisitos de terminación del refuerzo horizontal.

    Según 18.10.6.5(a):
    - Si omega_v * Omega_v * Vu < lambda * sqrt(f'c) * Acv:
      No requiere gancho
    - Caso contrario: Gancho estándar o estribos en U

    Args:
        omega_v: Factor de amplificación dinámica
        Omega_v: Factor de sobrerresistencia
        Vu: Cortante último (tonf)
        lambda_factor: Factor lambda para concreto liviano
        fc: f'c del hormigón (MPa)
        Acv: Área de corte (mm2)

    Returns:
        Dict con resultado de verificación
    """
    # Calcular cortante amplificado
    Vu_amp = omega_v * Omega_v * Vu

    # Calcular umbral (convertir a tonf)
    threshold = lambda_factor * math.sqrt(fc) * Acv / N_TO_TONF

    requires_hook = Vu_amp >= threshold

    return {
        "Vu_amplified": round(Vu_amp, 2),
        "threshold": round(threshold, 2),
        "requires_hook": requires_hook,
        "hook_type": "Gancho estándar o estribos en U" if requires_hook else "No requerido",
        "aci_reference": "ACI 318-25 18.10.6.5(a)"
    }
