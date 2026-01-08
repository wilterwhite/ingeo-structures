# app/domain/chapter18/columns/flexural_strength.py
"""
Resistencia mínima a flexión de columnas ACI 318-25 §18.7.3.

Implementa el requisito "columna fuerte - viga débil":
    ΣMnc >= (6/5) ΣMnb

Este requisito asegura que las rótulas plásticas se formen en las
vigas antes que en las columnas durante un sismo.

Referencias:
- ACI 318-25 §18.7.3.1: Requisito general
- ACI 318-25 §18.7.3.2: Columna fuerte - viga débil
- ACI 318-25 §18.7.3.3: Columnas que no satisfacen el requisito
"""
from typing import Tuple
from .results import StrongColumnResult

# Constantes
STRONG_COLUMN_RATIO = 1.2  # 6/5 = 1.2


def check_strong_column_weak_beam(
    Mnc_top: float,
    Mnc_bottom: float,
    Mnb_left: float,
    Mnb_right: float,
    direction: str = "V2",
) -> StrongColumnResult:
    """
    Verifica requisito columna fuerte-viga débil según §18.7.3.2.

    ΣMnc >= (6/5) ΣMnb

    Los momentos deben calcularse para la dirección de análisis considerando
    momentos en ambas caras del nudo.

    Args:
        Mnc_top: Mn de columna superior en la cara del nudo (tonf-m)
        Mnc_bottom: Mn de columna inferior en la cara del nudo (tonf-m)
        Mnb_left: Mn de viga izquierda en la cara del nudo (tonf-m)
        Mnb_right: Mn de viga derecha en la cara del nudo (tonf-m)
        direction: Dirección de análisis ("V2" o "V3")

    Returns:
        StrongColumnResult con verificación

    Note:
        - Usar Pu que resulte en MENOR Mn para columnas
        - Para vigas, incluir refuerzo de losa en ancho efectivo si desarrollado
        - Verificar para momentos en AMBAS direcciones (horario y antihorario)
    """
    sum_Mnc = Mnc_top + Mnc_bottom
    sum_Mnb = Mnb_left + Mnb_right

    if sum_Mnb > 0:
        ratio = sum_Mnc / sum_Mnb
    else:
        # Si no hay vigas, el requisito se satisface automáticamente
        ratio = float('inf')

    is_ok = ratio >= STRONG_COLUMN_RATIO

    return StrongColumnResult(
        sum_Mnc=round(sum_Mnc, 2),
        sum_Mnb=round(sum_Mnb, 2),
        ratio=round(ratio, 3) if ratio != float('inf') else 999.0,
        ratio_required=STRONG_COLUMN_RATIO,
        is_ok=is_ok,
        direction=direction,
    )


def check_exemption(
    Pu: float,
    Ag: float,
    fc: float,
    is_discontinuous_above: bool,
) -> Tuple[bool, str]:
    """
    Verifica si aplica exención del requisito §18.7.3.1.

    La columna está exenta si:
    - Es discontinua arriba del nudo, Y
    - Pu < Ag*f'c/10

    Args:
        Pu: Carga axial factorizada (N, positivo = compresión)
        Ag: Área bruta (mm²)
        fc: f'c del concreto (MPa)
        is_discontinuous_above: True si columna es discontinua arriba

    Returns:
        Tuple (is_exempt, reason)
    """
    if not is_discontinuous_above:
        return False, "Columna continua arriba del nudo"

    threshold = Ag * fc / 10
    if Pu < threshold:
        return True, f"Pu={Pu/1000:.1f}kN < Ag*f'c/10={threshold/1000:.1f}kN (§18.7.3.1)"

    return False, f"Pu={Pu/1000:.1f}kN >= Ag*f'c/10={threshold/1000:.1f}kN"
