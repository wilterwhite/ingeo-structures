# app/domain/shear/concrete_shear.py
"""
Cálculo centralizado de Vc (cortante soportado por el concreto).

Unifica las fórmulas de Vc para diferentes tipos de elementos según ACI 318-25.
Los servicios específicos (SeismicBeamService, SeismicColumnService, SeismicWallService)
importan estas funciones para evitar duplicación.

Referencias ACI 318-25:
- §22.5.5.1: Vc para vigas y elementos sin carga axial significativa
- §22.5.6: Vc para elementos con carga axial (columnas)
- §18.10.4.1: Vc para muros estructurales (fórmula con αc)

Unidades: Todas las funciones usan SI (N, mm, MPa)
"""
import math
from typing import Optional
from dataclasses import dataclass

from ..constants.shear import VC_COEF_COLUMN

# Constantes locales (podrían moverse a constants/ si se reutilizan)
LAMBDA_NORMAL = 1.0  # Factor lambda para concreto de peso normal
FC_EFF_SHEAR_MAX_MPA = 70  # f'c máximo efectivo para cortante (§22.5.3.1)


@dataclass
class VcResult:
    """Resultado del cálculo de Vc."""
    Vc_N: float              # Vc en Newtons
    fc_eff: float            # f'c efectivo usado (MPa)
    lambda_factor: float     # Factor λ usado
    formula: str             # Fórmula ACI aplicada
    aci_reference: str       # Referencia ACI


def calculate_Vc_beam(
    bw: float,
    d: float,
    fc: float,
    lambda_factor: float = 1.0,
    force_Vc_zero: bool = False,
) -> VcResult:
    """
    Calcula Vc para vigas según §22.5.5.1.

    Vc = 0.17 × λ × √f'c × bw × d

    Para vigas sísmicas especiales (§18.6.5.2), puede forzarse Vc = 0
    cuando el cortante sísmico domina y Pu < Ag×f'c/20.

    Args:
        bw: Ancho del alma (mm)
        d: Altura efectiva (mm)
        fc: Resistencia del concreto (MPa)
        lambda_factor: Factor para concreto liviano (default 1.0)
        force_Vc_zero: Si True, retorna Vc = 0 (condición §18.6.5.2)

    Returns:
        VcResult con Vc en Newtons
    """
    if force_Vc_zero:
        return VcResult(
            Vc_N=0,
            fc_eff=fc,
            lambda_factor=lambda_factor,
            formula="Vc = 0 (§18.6.5.2)",
            aci_reference="§18.6.5.2"
        )

    fc_eff = min(fc, FC_EFF_SHEAR_MAX_MPA)
    Vc_N = VC_COEF_COLUMN * lambda_factor * math.sqrt(fc_eff) * bw * d

    return VcResult(
        Vc_N=Vc_N,
        fc_eff=fc_eff,
        lambda_factor=lambda_factor,
        formula=f"0.17 × {lambda_factor} × √{fc_eff:.1f} × {bw:.0f} × {d:.0f}",
        aci_reference="§22.5.5.1"
    )


def calculate_Vc_column(
    bw: float,
    d: float,
    fc: float,
    Ag: float,
    Nu: float = 0,
    lambda_factor: float = 1.0,
    force_Vc_zero: bool = False,
) -> VcResult:
    """
    Calcula Vc para columnas según §22.5.6.

    Para columnas con carga axial de compresión:
    Vc = 0.17 × (1 + Nu/(14×Ag)) × λ × √f'c × bw × d  (§22.5.6.1 SI)

    Para columnas con carga axial de tracción:
    Vc = 0.17 × (1 + Nu/(3.5×Ag)) × λ × √f'c × bw × d ≥ 0  (§22.5.6.2 SI)

    Para columnas sísmicas (§18.7.6.2), puede forzarse Vc = 0 cuando aplica.

    Args:
        bw: Ancho de sección (mm)
        d: Altura efectiva (mm)
        fc: Resistencia del concreto (MPa)
        Ag: Área bruta (mm²)
        Nu: Carga axial (N), positivo = compresión
        lambda_factor: Factor para concreto liviano (default 1.0)
        force_Vc_zero: Si True, retorna Vc = 0 (condición §18.7.6.2)

    Returns:
        VcResult con Vc en Newtons
    """
    if force_Vc_zero:
        return VcResult(
            Vc_N=0,
            fc_eff=fc,
            lambda_factor=lambda_factor,
            formula="Vc = 0 (§18.7.6.2)",
            aci_reference="§18.7.6.2"
        )

    fc_eff = min(fc, FC_EFF_SHEAR_MAX_MPA)

    if Nu >= 0:  # Compresión
        # §22.5.6.1: Factor = 1 + Nu/(14×Ag)
        axial_factor = 1 + Nu / (14 * Ag) if Ag > 0 else 1
        aci_ref = "§22.5.6.1"
        formula = f"0.17 × (1 + Nu/(14Ag)) × λ × √f'c × bw × d"
    else:  # Tracción
        # §22.5.6.2: Factor = 1 + Nu/(3.5×Ag), pero no menor que 0
        axial_factor = max(0, 1 + Nu / (3.5 * Ag)) if Ag > 0 else 0
        aci_ref = "§22.5.6.2"
        formula = f"0.17 × (1 + Nu/(3.5Ag)) × λ × √f'c × bw × d ≥ 0"

    Vc_N = VC_COEF_COLUMN * axial_factor * lambda_factor * math.sqrt(fc_eff) * bw * d

    return VcResult(
        Vc_N=Vc_N,
        fc_eff=fc_eff,
        lambda_factor=lambda_factor,
        formula=formula,
        aci_reference=aci_ref
    )


def calculate_Vc_wall(
    Acv: float,
    hw: float,
    lw: float,
    fc: float,
    lambda_factor: float = 1.0,
) -> VcResult:
    """
    Calcula Vc para muros estructurales según §18.10.4.1.

    Vc = Acv × αc × λ × √f'c

    Donde αc depende de hw/lw:
    - αc = 3.0 si hw/lw ≤ 1.5 (muros bajos)
    - αc = 2.0 si hw/lw ≥ 2.0 (muros esbeltos)
    - Interpolación lineal entre 1.5 y 2.0

    Args:
        Acv: Área de corte (mm²), típicamente lw × tw
        hw: Altura del muro (mm)
        lw: Longitud del muro (mm)
        fc: Resistencia del concreto (MPa)
        lambda_factor: Factor para concreto liviano (default 1.0)

    Returns:
        VcResult con Vc en Newtons
    """
    fc_eff = min(fc, FC_EFF_SHEAR_MAX_MPA)

    # Calcular αc según hw/lw (Tabla 18.10.4.1)
    aspect_ratio = hw / lw if lw > 0 else float('inf')

    if aspect_ratio <= 1.5:
        alpha_c = 3.0
    elif aspect_ratio >= 2.0:
        alpha_c = 2.0
    else:
        # Interpolación lineal
        alpha_c = 3.0 - (aspect_ratio - 1.5) * 2.0

    Vc_N = Acv * alpha_c * lambda_factor * math.sqrt(fc_eff)

    return VcResult(
        Vc_N=Vc_N,
        fc_eff=fc_eff,
        lambda_factor=lambda_factor,
        formula=f"Acv × {alpha_c:.2f} × {lambda_factor} × √{fc_eff:.1f}",
        aci_reference="§18.10.4.1"
    )


def check_Vc_zero_condition(
    Ve_seismic: float,
    Vu_total: float,
    Pu: float,
    Ag: float,
    fc: float,
) -> bool:
    """
    Verifica si aplica la condición Vc = 0 según §18.6.5.2 / §18.7.6.2.

    La condición Vc = 0 aplica cuando AMBAS condiciones se cumplen:
    1. Ve (cortante sísmico) ≥ 0.5 × Vu (cortante total)
    2. Pu < Ag × f'c / 20

    Args:
        Ve_seismic: Cortante inducido por sismo (N)
        Vu_total: Cortante último total (N)
        Pu: Carga axial última (N), positivo = compresión
        Ag: Área bruta de la sección (mm²)
        fc: Resistencia del concreto (MPa)

    Returns:
        True si debe usarse Vc = 0, False en caso contrario
    """
    # Condición 1: Cortante sísmico domina
    seismic_dominates = Ve_seismic >= 0.5 * Vu_total

    # Condición 2: Carga axial baja
    Pu_limit = Ag * fc / 20  # N
    low_axial = Pu < Pu_limit

    return seismic_dominates and low_axial


__all__ = [
    'VcResult',
    'calculate_Vc_beam',
    'calculate_Vc_column',
    'calculate_Vc_wall',
    'check_Vc_zero_condition',
]
