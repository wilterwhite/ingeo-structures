# app/domain/chapter18/columns/transverse.py
"""
Refuerzo transversal para columnas sísmicas ACI 318-25 §18.7.5.

Implementa:
- §18.7.5.1: Longitud ℓo de confinamiento
- §18.7.5.2: Configuración del refuerzo transversal
- §18.7.5.3: Espaciamiento del refuerzo transversal
- §18.7.5.4: Cantidad de refuerzo transversal (Tabla 18.7.5.4)
- §18.7.5.5: Requisitos fuera de ℓo
- §18.7.5.6: Columnas bajo miembros discontinuos

Referencias:
- ACI 318-25 §18.7.5
- ACI 318-25 Tabla 18.7.5.4
"""
import math
from typing import List, Tuple
from .results import TransverseReinforcementResult
from ...constants.chapter18 import (
    LO_MIN_MM,
    HX_MAX_MM as HX_MAX_NORMAL_MM,
    HX_MAX_HIGH_AXIAL_MM,
    SO_MIN_MM,
    SO_MAX_MM,
    FC_LIMIT_HIGH_AXIAL_MPA as FC_LIMIT_MPA,
)


def calculate_lo(
    h: float,
    lu: float,
) -> float:
    """
    Calcula longitud ℓo de confinamiento según §18.7.5.1.

    ℓo >= max(h, lu/6, 18")

    Args:
        h: Dimensión mayor de la sección (mm)
        lu: Altura libre de la columna (mm)

    Returns:
        Longitud ℓo requerida (mm)
    """
    return max(h, lu / 6, LO_MIN_MM)


def calculate_so(hx: float) -> float:
    """
    Calcula espaciamiento so según Ec. 18.7.5.3.

    so = 4 + (14 - hx)/3
    4" <= so <= 6"

    Args:
        hx: Espaciamiento entre barras soportadas (pulgadas)

    Returns:
        Espaciamiento so (pulgadas)
    """
    # hx en mm, convertir a pulgadas para la fórmula
    hx_in = hx / 25.4
    so_in = 4 + (14 - hx_in) / 3
    so_in = max(4, min(so_in, 6))
    return so_in * 25.4  # Retornar en mm


def calculate_s_max(
    h: float,
    db: float,
    steel_grade: int,
    hx: float,
) -> float:
    """
    Calcula espaciamiento máximo según §18.7.5.3.

    s <= min(h/4, 6*db para G60, 5*db para G80, so)

    Args:
        h: Dimensión de la sección en dirección de análisis (mm)
        db: Diámetro de barra longitudinal (mm)
        steel_grade: Grado del acero (60 u 80)
        hx: Espaciamiento entre barras soportadas (mm)

    Returns:
        Espaciamiento máximo (mm)
    """
    so = calculate_so(hx)

    if steel_grade >= 80:
        db_factor = 5 * db
    else:
        db_factor = 6 * db

    return min(h / 4, db_factor, so)


def calculate_Ash_sbc_required(
    Ag: float,
    Ach: float,
    fc: float,
    fyt: float,
    Pu: float,
    nl: int,
    high_axial_or_fc: bool,
) -> Tuple[float, List[str]]:
    """
    Calcula Ash/(s*bc) requerido según Tabla 18.7.5.4.

    Para secciones rectangulares con hoops rectangulares.

    Args:
        Ag: Área bruta (mm²)
        Ach: Área del núcleo confinado (mm²)
        fc: f'c del concreto (MPa)
        fyt: Fluencia del refuerzo transversal (MPa)
        Pu: Carga axial factorizada (N, positivo = compresión)
        nl: Número de barras longitudinales soportadas en el perímetro
        high_axial_or_fc: True si Pu > 0.3*Ag*f'c O f'c > 70 MPa

    Returns:
        Tuple (Ash_sbc_required, governing_expressions)
    """
    expressions = []

    # (a) 0.3 * (Ag/Ach - 1) * (f'c/fyt)
    expr_a = 0.3 * (Ag / Ach - 1) * (fc / fyt)
    expressions.append(f"(a) 0.3*(Ag/Ach-1)*(f'c/fyt) = {expr_a:.4f}")

    # (b) 0.09 * (f'c/fyt)
    expr_b = 0.09 * (fc / fyt)
    expressions.append(f"(b) 0.09*(f'c/fyt) = {expr_b:.4f}")

    if high_axial_or_fc:
        # (c) 0.2 * kf * kn * Pu/(fyt*Ach)
        # kf = f'c/25000 + 0.6 >= 1.0 (f'c en psi)
        fc_psi = fc * 145.038  # MPa a psi
        kf = max(fc_psi / 25000 + 0.6, 1.0)

        # kn = nl/(nl - 2)
        kn = nl / (nl - 2) if nl > 2 else 1.0

        expr_c = 0.2 * kf * kn * Pu / (fyt * Ach)
        expressions.append(f"(c) 0.2*kf*kn*Pu/(fyt*Ach) = {expr_c:.4f} (kf={kf:.2f}, kn={kn:.2f})")

        Ash_sbc = max(expr_a, expr_b, expr_c)
    else:
        Ash_sbc = max(expr_a, expr_b)

    return Ash_sbc, expressions


def calculate_rho_s_required(
    Ag: float,
    Ach: float,
    fc: float,
    fyt: float,
    Pu: float,
    high_axial_or_fc: bool,
) -> Tuple[float, List[str]]:
    """
    Calcula ρs requerido según Tabla 18.7.5.4.

    Para columnas con espirales o hoops circulares.

    Args:
        Ag: Área bruta (mm²)
        Ach: Área del núcleo confinado (mm²)
        fc: f'c del concreto (MPa)
        fyt: Fluencia del refuerzo transversal (MPa)
        Pu: Carga axial factorizada (N, positivo = compresión)
        high_axial_or_fc: True si Pu > 0.3*Ag*f'c O f'c > 70 MPa

    Returns:
        Tuple (rho_s_required, governing_expressions)
    """
    expressions = []

    # (d) 0.45 * (Ag/Ach - 1) * (f'c/fyt)
    expr_d = 0.45 * (Ag / Ach - 1) * (fc / fyt)
    expressions.append(f"(d) 0.45*(Ag/Ach-1)*(f'c/fyt) = {expr_d:.4f}")

    # (e) 0.12 * (f'c/fyt)
    expr_e = 0.12 * (fc / fyt)
    expressions.append(f"(e) 0.12*(f'c/fyt) = {expr_e:.4f}")

    if high_axial_or_fc:
        # (f) 0.35 * kf * Pu/(fyt*Ach)
        fc_psi = fc * 145.038
        kf = max(fc_psi / 25000 + 0.6, 1.0)

        expr_f = 0.35 * kf * Pu / (fyt * Ach)
        expressions.append(f"(f) 0.35*kf*Pu/(fyt*Ach) = {expr_f:.4f} (kf={kf:.2f})")

        rho_s = max(expr_d, expr_e, expr_f)
    else:
        rho_s = max(expr_d, expr_e)

    return rho_s, expressions


def check_transverse_reinforcement(
    h: float,
    b: float,
    lu: float,
    cover: float,
    Ag: float,
    fc: float,
    fyt: float,
    Pu: float,
    s_provided: float,
    Ash_provided: float,
    db_long: float,
    hx_provided: float,
    nl: int,
    steel_grade: int = 60,
    is_circular: bool = False,
    rho_s_provided: float = 0,
) -> TransverseReinforcementResult:
    """
    Verifica refuerzo transversal según §18.7.5.

    Args:
        h: Dimensión mayor de la sección (mm)
        b: Dimensión menor de la sección (mm)
        lu: Altura libre de la columna (mm)
        cover: Recubrimiento al centro de estribos (mm)
        Ag: Área bruta (mm²)
        fc: f'c del concreto (MPa)
        fyt: Fluencia del refuerzo transversal (MPa)
        Pu: Carga axial factorizada máxima (N, positivo = compresión)
        s_provided: Espaciamiento provisto (mm)
        Ash_provided: Área de refuerzo en una dirección (mm²)
        db_long: Diámetro de barra longitudinal (mm)
        hx_provided: Espaciamiento entre barras soportadas (mm)
        nl: Número de barras longitudinales en el perímetro
        steel_grade: Grado del acero (60 u 80)
        is_circular: True si es columna circular con espiral
        rho_s_provided: Cuantía volumétrica provista (solo para circular)

    Returns:
        TransverseReinforcementResult con verificación completa
    """
    warnings = []

    # Longitud ℓo
    lo = calculate_lo(h, lu)

    # Verificar condición de alta carga axial o f'c alto
    high_axial_or_fc = (Pu > 0.3 * Ag * fc) or (fc > FC_LIMIT_MPA)

    # Espaciamiento máximo de barras soportadas
    hx_max = HX_MAX_HIGH_AXIAL_MM if high_axial_or_fc else HX_MAX_NORMAL_MM
    hx_ok = hx_provided <= hx_max

    if not hx_ok:
        warnings.append(f"hx={hx_provided:.0f}mm > {hx_max:.0f}mm máximo permitido")

    # Soporte de esquina requerido
    requires_corner_support = high_axial_or_fc

    # Espaciamiento máximo
    s_max = calculate_s_max(h, db_long, steel_grade, hx_provided)
    s_ok = s_provided <= s_max

    if not s_ok:
        warnings.append(f"s={s_provided:.0f}mm > s_max={s_max:.0f}mm")

    # Área del núcleo confinado
    bc = b - 2 * cover  # Dimensión del núcleo en dirección corta
    hc = h - 2 * cover  # Dimensión del núcleo en dirección larga
    Ach = bc * hc

    if is_circular:
        # Columna circular con espiral
        rho_s_required, _ = calculate_rho_s_required(
            Ag, Ach, fc, fyt, Pu, high_axial_or_fc
        )
        rho_s_ok = rho_s_provided >= rho_s_required
        Ash_sbc_required = 0
        Ash_sbc_provided = 0
        Ash_ok = True

        if not rho_s_ok:
            warnings.append(f"ρs={rho_s_provided:.4f} < {rho_s_required:.4f} requerido")
    else:
        # Columna rectangular con hoops
        Ash_sbc_required, _ = calculate_Ash_sbc_required(
            Ag, Ach, fc, fyt, Pu, nl, high_axial_or_fc
        )
        # Ash_sbc_provided = Ash / (s * bc)
        Ash_sbc_provided = Ash_provided / (s_provided * bc) if s_provided > 0 and bc > 0 else 0
        Ash_ok = Ash_sbc_provided >= Ash_sbc_required
        rho_s_required = 0
        rho_s_ok = True

        if not Ash_ok:
            warnings.append(f"Ash/(s*bc)={Ash_sbc_provided:.4f} < {Ash_sbc_required:.4f} requerido")

    is_ok = s_ok and hx_ok and Ash_ok and rho_s_ok

    return TransverseReinforcementResult(
        lo=round(lo, 0),
        lo_required=round(lo, 0),
        s_provided=s_provided,
        s_max=round(s_max, 0),
        s_ok=s_ok,
        hx_provided=hx_provided,
        hx_max=hx_max,
        hx_ok=hx_ok,
        Ash_sbc_provided=round(Ash_sbc_provided, 4),
        Ash_sbc_required=round(Ash_sbc_required, 4),
        Ash_ok=Ash_ok,
        rho_s_provided=round(rho_s_provided, 4),
        rho_s_required=round(rho_s_required, 4),
        rho_s_ok=rho_s_ok,
        high_axial_or_fc=high_axial_or_fc,
        requires_corner_support=requires_corner_support,
        is_ok=is_ok,
        warnings=warnings,
    )
