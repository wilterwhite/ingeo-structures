# app/domain/chapter18/boundary_elements/displacement.py
"""
Verificación por método de desplazamiento ACI 318-25 §18.10.6.2.

Según 18.10.6.2(a):
1.5 * (delta_u / hwcs) >= lw / (600 * c)

Donde delta_u / hwcs no debe tomarse menor que 0.005.
"""
import math

from ..results import DisplacementCheckResult


def check_displacement_method(
    delta_u: float,
    hwcs: float,
    lw: float,
    c: float
) -> DisplacementCheckResult:
    """
    Verifica si se requiere elemento de borde por método de desplazamiento.

    Args:
        delta_u: Desplazamiento de diseño en tope del muro (mm)
        hwcs: Altura del muro desde sección crítica (mm)
        lw: Longitud del muro (mm)
        c: Profundidad del eje neutro (mm), mayor valor calculado

    Returns:
        DisplacementCheckResult con resultado de la verificación
    """
    if hwcs <= 0 or c <= 0:
        return DisplacementCheckResult(
            delta_u=delta_u, hwcs=hwcs, lw=lw, c=c,
            drift_ratio=0, limit=0, check_value=0,
            requires_special=True,  # Conservador
            aci_reference="ACI 318-25 18.10.6.2(a)"
        )

    # Calcular drift ratio (no menor que 0.005)
    drift_ratio = max(delta_u / hwcs, 0.005)

    # Calcular límite
    limit = lw / (600 * c)

    # Verificar si requiere elemento de borde especial
    check_value = 1.5 * drift_ratio
    requires_special = check_value >= limit

    return DisplacementCheckResult(
        delta_u=delta_u,
        hwcs=hwcs,
        lw=lw,
        c=c,
        drift_ratio=round(drift_ratio, 5),
        limit=round(limit, 5),
        check_value=round(check_value, 5),
        requires_special=requires_special,
        aci_reference="ACI 318-25 18.10.6.2(a)"
    )


def check_drift_capacity(
    lw: float,
    b: float,
    c: float,
    Ve: float,
    fc: float,
    Acv: float,
    delta_u: float,
    hwcs: float
) -> dict:
    """
    Verifica capacidad de deriva según 18.10.6.2(b)(iii).

    delta_c/hwcs >= 1.5 * delta_u/hwcs

    Donde:
    delta_c/hwcs = (1/100) * [4 - 1/50 - (lw/b)*(c/b) - Ve/(8*sqrt(f'c)*Acv)]

    Mínimo: delta_c/hwcs >= 0.015

    Args:
        lw: Longitud del muro (mm)
        b: Ancho del elemento de borde (mm)
        c: Profundidad del eje neutro (mm)
        Ve: Cortante de diseño (tonf)
        fc: f'c del hormigón (MPa)
        Acv: Área de corte (mm2)
        delta_u: Desplazamiento de diseño (mm)
        hwcs: Altura desde sección crítica (mm)

    Returns:
        Dict con resultados de la verificación
    """
    if b <= 0 or hwcs <= 0:
        return {
            "delta_c_hwcs": 0,
            "delta_u_hwcs": 0,
            "limit": 0,
            "is_ok": False,
            "aci_reference": "ACI 318-25 18.10.6.2(b)(iii)"
        }

    # Convertir Ve a N para unidades consistentes
    Ve_N = Ve * 9806.65  # tonf a N

    # Calcular término de cortante
    # 8 * sqrt(f'c) * Acv en unidades SI
    shear_term = Ve_N / (0.66 * math.sqrt(fc) * Acv) if Acv > 0 else 0

    # Calcular capacidad de deriva
    delta_c_hwcs = (1/100) * (4 - 0.02 - (lw/b) * (c/b) - shear_term)
    delta_c_hwcs = max(delta_c_hwcs, 0.015)

    # Calcular deriva de diseño
    delta_u_hwcs = max(delta_u / hwcs, 0.005)

    # Verificar
    limit = 1.5 * delta_u_hwcs
    is_ok = delta_c_hwcs >= limit

    return {
        "delta_c_hwcs": round(delta_c_hwcs, 5),
        "delta_u_hwcs": round(delta_u_hwcs, 5),
        "limit": round(limit, 5),
        "is_ok": is_ok,
        "aci_reference": "ACI 318-25 18.10.6.2(b)(iii)"
    }
