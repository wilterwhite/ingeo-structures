# app/domain/shear/steel_shear.py
"""
Cálculo centralizado de Vs (cortante soportado por el acero de refuerzo).

Unifica las fórmulas de Vs para diferentes tipos de elementos según ACI 318-25.
Los servicios específicos (SeismicBeamService, SeismicColumnService, SeismicWallService)
importan estas funciones para evitar duplicación.

Referencias ACI 318-25:
- §22.5.10.5.3: Vs para vigas y columnas (Vs = Av × fyt × d / s)
- §18.10.4.1: Vs para muros estructurales (Vs = Acv × ρt × fyt)

Unidades: Todas las funciones usan SI (N, mm, MPa)
"""
import math
from dataclasses import dataclass
from typing import Optional

from ..constants.materials import get_effective_fc_shear, get_effective_fyt_shear
from ..constants.shear import VS_MAX_COEF


@dataclass
class VsResult:
    """Resultado del cálculo de Vs."""
    Vs_N: float              # Vs en Newtons
    Vs_max_N: float          # Vs máximo permitido (§22.5.1.2)
    is_limited: bool         # True si Vs fue limitado por Vs_max
    formula: str             # Fórmula ACI aplicada
    aci_reference: str       # Referencia ACI


def calculate_Vs_beam_column(
    Av: float,
    d: float,
    s: float,
    fyt: float,
    bw: float,
    fc: float,
) -> VsResult:
    """
    Calcula Vs para vigas y columnas según §22.5.10.5.3.

    Vs = Av × fyt × d / s

    Límite: Vs ≤ 0.66 × √f'c × bw × d (§22.5.1.2)

    Args:
        Av: Área de refuerzo transversal en una sección (mm²)
        d: Altura efectiva (mm)
        s: Espaciamiento de estribos (mm)
        fyt: Fluencia del acero transversal (MPa)
        bw: Ancho del alma (mm)
        fc: Resistencia del concreto (MPa)

    Returns:
        VsResult con Vs en Newtons
    """
    fc_eff = get_effective_fc_shear(fc)
    fyt_eff = get_effective_fyt_shear(fyt)

    # Calcular Vs
    if Av > 0 and s > 0 and d > 0:
        Vs_N = Av * fyt_eff * d / s
    else:
        Vs_N = 0

    # Límite de Vs: Vs ≤ 0.66 × √f'c × bw × d
    Vs_max_N = VS_MAX_COEF * math.sqrt(fc_eff) * bw * d
    is_limited = Vs_N > Vs_max_N
    Vs_N = min(Vs_N, Vs_max_N)

    return VsResult(
        Vs_N=Vs_N,
        Vs_max_N=Vs_max_N,
        is_limited=is_limited,
        formula=f"Av × fyt × d / s = {Av:.0f} × {fyt_eff:.0f} × {d:.0f} / {s:.0f}",
        aci_reference="§22.5.10.5.3"
    )


def calculate_Vs_wall(
    Acv: float,
    rho_t: float,
    fyt: float,
    fc: float,
    lw: float = 0,
    tw: float = 0,
) -> VsResult:
    """
    Calcula Vs para muros estructurales según §18.10.4.1.

    Vn = Acv × (αc × λ × √f'c + ρt × fyt)
    Donde Vs = Acv × ρt × fyt

    Límite: Vn ≤ 8 × √f'c × Acv (individual) o 6 × √f'c × Acv (grupo)

    Args:
        Acv: Área de corte (mm²), típicamente lw × tw
        rho_t: Cuantía de refuerzo horizontal
        fyt: Fluencia del acero transversal (MPa)
        fc: Resistencia del concreto (MPa)
        lw: Longitud del muro (mm) - para cálculo de Acv si no se proporciona
        tw: Espesor del muro (mm) - para cálculo de Acv si no se proporciona

    Returns:
        VsResult con Vs en Newtons
    """
    fyt_eff = get_effective_fyt_shear(fyt)
    fc_eff = get_effective_fc_shear(fc)

    # Si no se da Acv, calcular de lw × tw
    if Acv <= 0 and lw > 0 and tw > 0:
        Acv = lw * tw

    # Calcular Vs
    if Acv > 0 and rho_t > 0:
        Vs_N = Acv * rho_t * fyt_eff
    else:
        Vs_N = 0

    # Límite de Vn (no solo Vs, pero es útil para referencia)
    # §18.10.4.4: Vn ≤ 8 × √f'c × Acv (individual)
    Vs_max_N = 8 * math.sqrt(fc_eff) * Acv  # Límite práctico

    is_limited = Vs_N > Vs_max_N
    # No limitamos Vs aquí porque el límite aplica a Vn = Vc + Vs

    return VsResult(
        Vs_N=Vs_N,
        Vs_max_N=Vs_max_N,
        is_limited=is_limited,
        formula=f"Acv × ρt × fyt = {Acv:.0f} × {rho_t:.5f} × {fyt_eff:.0f}",
        aci_reference="§18.10.4.1"
    )


def calculate_Vs(
    element_type: str,
    Av: float = 0,
    d: float = 0,
    s: float = 0,
    fyt: float = 420,
    Acv: float = 0,
    rho_t: float = 0,
    bw: float = 0,
    fc: float = 25,
    lw: float = 0,
    tw: float = 0,
) -> VsResult:
    """
    Función unificada para calcular Vs según tipo de elemento.

    Args:
        element_type: 'beam', 'column', o 'wall'
        Av: Área de estribo (mm²) - para vigas/columnas
        d: Altura efectiva (mm) - para vigas/columnas
        s: Espaciamiento (mm) - para vigas/columnas
        fyt: Fluencia transversal (MPa)
        Acv: Área de corte (mm²) - para muros
        rho_t: Cuantía horizontal - para muros
        bw: Ancho alma (mm)
        fc: f'c (MPa)
        lw: Longitud muro (mm) - para muros
        tw: Espesor muro (mm) - para muros

    Returns:
        VsResult con Vs en Newtons
    """
    if element_type == 'wall':
        return calculate_Vs_wall(
            Acv=Acv,
            rho_t=rho_t,
            fyt=fyt,
            fc=fc,
            lw=lw,
            tw=tw,
        )
    else:  # beam, column
        return calculate_Vs_beam_column(
            Av=Av,
            d=d,
            s=s,
            fyt=fyt,
            bw=bw,
            fc=fc,
        )


__all__ = [
    'VsResult',
    'calculate_Vs',
    'calculate_Vs_beam_column',
    'calculate_Vs_wall',
]
