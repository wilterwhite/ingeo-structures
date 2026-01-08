# app/domain/chapter8/punching/vc_calculation.py
"""
Capitulo 22.6.5 ACI 318-25: Resistencia al Cortante Bidireccional.

Implementa el calculo de Vc para punzonamiento segun 22.6.5.2.
"""
from typing import Dict, Tuple
from dataclasses import dataclass
import math

from .critical_section import (
    calculate_critical_perimeter,
    get_beta_column,
    get_alpha_s,
    ColumnPosition,
)
from ...constants.shear import PHI_SHEAR


@dataclass
class PunchingResult:
    """Resultado de verificacion de punzonamiento."""
    # Geometria critica
    bo: float               # Perimetro critico (mm)
    d: float                # Profundidad efectiva (mm)
    Ac: float               # Area critica (mm2)

    # Resistencia del concreto
    Vc_a: float             # Ec. (a): Vc general (kN)
    Vc_b: float             # Ec. (b): Vc por beta (kN)
    Vc_c: float             # Ec. (c): Vc por alpha_s (kN)
    Vc: float               # Vc controlante = min(a, b, c) (kN)

    # Resistencia nominal y de diseno
    phi: float              # Factor de reduccion (0.75)
    phi_Vc: float           # Capacidad de diseno (kN)

    # Demanda
    Vu: float               # Cortante ultimo (kN)

    # Verificacion
    sf: float               # Factor de seguridad phi_Vc / Vu
    dcr: float              # Demand/Capacity Ratio
    is_ok: bool             # True si phi_Vc >= Vu

    # Parametros
    beta: float             # Relacion de columna
    alpha_s: float          # Factor por posicion
    lambda_factor: float    # Factor por concreto liviano
    lambda_s: float         # Factor de efecto de tamano

    position: str           # Posicion de columna
    aci_reference: str      # Referencia ACI


def calculate_lambda_s(d_mm: float) -> float:
    """
    Calcula el factor de efecto de tamano segun 22.5.5.1.3.

    lambda_s = sqrt(2 / (1 + 0.004*d)) <= 1.0

    Este factor reduce Vc para losas gruesas (d > 250mm).

    Args:
        d_mm: Profundidad efectiva (mm)

    Returns:
        Factor lambda_s (<= 1.0)
    """
    lambda_s = math.sqrt(2 / (1 + 0.004 * d_mm))
    return min(lambda_s, 1.0)


def calculate_punching_Vc(
    fc_mpa: float,
    c1_mm: float,
    c2_mm: float,
    d_mm: float,
    position: ColumnPosition = ColumnPosition.INTERIOR,
    lambda_factor: float = 1.0,
    Vu_kN: float = 0.0
) -> PunchingResult:
    """
    Calcula la resistencia al cortante por punzonamiento segun 22.6.5.2.

    Vc = menor de:
    (a) 0.33 * lambda * lambda_s * sqrt(f'c) * bo * d
    (b) (0.17 + 0.33/beta) * lambda * lambda_s * sqrt(f'c) * bo * d
    (c) (0.17 + 0.083*alpha_s*d/bo) * lambda * lambda_s * sqrt(f'c) * bo * d

    Unidades: f'c en MPa, dimensiones en mm, resultado en N -> convertir a kN

    Args:
        fc_mpa: Resistencia del concreto (MPa)
        c1_mm: Dimension columna direccion 1 (mm)
        c2_mm: Dimension columna direccion 2 (mm)
        d_mm: Profundidad efectiva de la losa (mm)
        position: Posicion de la columna
        lambda_factor: Factor por concreto liviano (1.0 para normal)
        Vu_kN: Cortante ultimo de demanda (kN)

    Returns:
        PunchingResult con todos los resultados
    """
    # Geometria critica
    bo = calculate_critical_perimeter(c1_mm, c2_mm, d_mm, position)
    Ac = bo * d_mm

    # Parametros
    beta = get_beta_column(c1_mm, c2_mm)
    alpha_s = get_alpha_s(position)
    lambda_s = calculate_lambda_s(d_mm)

    # Factor comun (en unidades SI: N)
    sqrt_fc = math.sqrt(fc_mpa)
    factor_comun = lambda_factor * lambda_s * sqrt_fc * bo * d_mm

    # Ecuacion (a): General
    # Vc_a = 0.33 * sqrt(f'c) * bo * d
    Vc_a_N = 0.33 * factor_comun

    # Ecuacion (b): Por relacion de columna
    # Vc_b = (0.17 + 0.33/beta) * sqrt(f'c) * bo * d
    Vc_b_N = (0.17 + 0.33 / beta) * factor_comun

    # Ecuacion (c): Por posicion y relacion bo/d
    # Vc_c = (0.17 + 0.083*alpha_s*d/bo) * sqrt(f'c) * bo * d
    Vc_c_N = (0.17 + 0.083 * alpha_s * d_mm / bo) * factor_comun

    # Vc controlante (el menor)
    Vc_N = min(Vc_a_N, Vc_b_N, Vc_c_N)

    # Convertir a kN
    Vc_a_kN = Vc_a_N / 1000
    Vc_b_kN = Vc_b_N / 1000
    Vc_c_kN = Vc_c_N / 1000
    Vc_kN = Vc_N / 1000

    # Factor de reduccion para cortante (importado de constants.shear)
    phi = PHI_SHEAR

    # Capacidad de diseno
    phi_Vc_kN = phi * Vc_kN

    # Verificacion
    if Vu_kN > 0:
        sf = phi_Vc_kN / Vu_kN
        dcr = Vu_kN / phi_Vc_kN
        is_ok = phi_Vc_kN >= Vu_kN
    else:
        sf = float('inf')
        dcr = 0.0
        is_ok = True

    return PunchingResult(
        # Geometria
        bo=bo,
        d=d_mm,
        Ac=Ac,
        # Resistencias
        Vc_a=Vc_a_kN,
        Vc_b=Vc_b_kN,
        Vc_c=Vc_c_kN,
        Vc=Vc_kN,
        phi=phi,
        phi_Vc=phi_Vc_kN,
        # Demanda
        Vu=Vu_kN,
        # Verificacion
        sf=sf,
        dcr=dcr,
        is_ok=is_ok,
        # Parametros
        beta=beta,
        alpha_s=alpha_s,
        lambda_factor=lambda_factor,
        lambda_s=lambda_s,
        position=position.value,
        aci_reference='ACI 318-25 22.6.5.2'
    )


def check_punching_shear_reinforcement_needed(
    Vu_kN: float,
    phi_Vc_kN: float
) -> Tuple[bool, str]:
    """
    Verifica si se requiere refuerzo de cortante por punzonamiento.

    Segun 22.6.6:
    - Si Vu <= 0.5*phi*Vc: No requiere refuerzo (tipicamente no aplica para punzonamiento)
    - Si Vu > phi*Vc: Requiere refuerzo o rediseno

    Args:
        Vu_kN: Cortante ultimo (kN)
        phi_Vc_kN: Capacidad de diseno del concreto (kN)

    Returns:
        Tupla (requiere_refuerzo, mensaje)
    """
    if Vu_kN <= phi_Vc_kN:
        return False, "OK - No requiere refuerzo de punzonamiento"
    else:
        return True, "Requiere refuerzo de punzonamiento (studs o barras)"


# TODO: Constante huerfana - requerida por ACI 318-25 §8.10.4.1 pero no usada aun.
# Factor maximo para Vn con refuerzo de barras/mallas: Vn <= 6*lambda*sqrt(f'c)*bo*d
# Para studs: Vn <= 8*lambda*sqrt(f'c)*bo*d
VC_MAX_FACTOR_BARS = 0.50   # 6/12 en SI (equivale a 6*sqrt(f'c) en US)
VC_MAX_FACTOR_STUDS = 0.66  # 8/12 en SI (equivale a 8*sqrt(f'c) en US)
