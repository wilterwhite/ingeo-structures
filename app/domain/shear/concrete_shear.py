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

from ..constants.shear import VC_COEF_COLUMN, FC_EFF_SHEAR_MAX_MPA


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


def check_Vc_zero_condition(
    Ve: float,
    Vu: float,
    Pu: float,
    Ag: float,
    fc: float
) -> bool:
    """
    Verifica si Vc debe ser cero según ACI 318-25.

    Para elementos sísmicos especiales (SMF), Vc = 0 cuando se cumplen
    AMBAS condiciones:
        (a) Ve >= 0.5 × Vu
        (b) Pu < Ag × f'c / 20

    Args:
        Ve: Cortante por diseño por capacidad (tonf)
        Vu: Cortante último máximo de la combinación (tonf)
        Pu: Carga axial factorizada (tonf, positivo = compresión)
        Ag: Área bruta del elemento (mm²)
        fc: f'c del concreto (MPa)

    Returns:
        True si Vc debe ser cero (ambas condiciones cumplidas)

    Referencias:
        - §18.6.5.2: Vigas sísmicas especiales
        - §18.7.6.2.1: Columnas sísmicas especiales

    Nota:
        Para vigas, Pu típicamente es cero o muy bajo, por lo que
        la condición (b) casi siempre se cumple.
    """
    from ..constants.units import TONF_TO_N

    # Condición (a): El cortante sísmico domina
    # Si Vu es cero o negativo, asumimos que Ve domina
    condition_a = Ve >= 0.5 * Vu if Vu > 0 else True

    # Condición (b): Carga axial baja
    # Convertir Pu a Newtons para comparar con Ag * fc / 20
    Pu_N = Pu * TONF_TO_N
    threshold = Ag * fc / 20
    condition_b = Pu_N < threshold

    return condition_a and condition_b


__all__ = [
    'VcResult',
    'calculate_Vc_beam',
    'check_Vc_zero_condition',
]
