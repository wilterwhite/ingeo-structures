# app/domain/chapter7/reinforcement.py
"""
Capitulo 7.6 y 7.7 ACI 318-25: Refuerzo para Losas 1-Way.

Implementa:
- 7.6.1: Refuerzo minimo de flexion
- 7.6.4: Refuerzo de temperatura y retraccion
- 7.7.2: Espaciamiento maximo del refuerzo
"""
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class ReinforcementCheckResult:
    """Resultado de verificacion de refuerzo."""
    As_min: float          # Area minima requerida (mm2/m)
    As_provided: float     # Area provista (mm2/m)
    is_ok: bool            # True si As >= As_min
    ratio: float           # As / As_min
    rho_min: float         # Cuantia minima
    rho_provided: float    # Cuantia provista
    spacing_max: float     # Espaciamiento maximo (mm)
    spacing_provided: float # Espaciamiento provisto (mm)
    spacing_ok: bool       # True si s <= s_max
    aci_reference: str     # Referencia ACI


def get_minimum_flexural_reinforcement(
    h_mm: float,
    fy_mpa: float = 420.0,
    is_deformed_bars: bool = True
) -> Tuple[float, float]:
    """
    Calcula el refuerzo minimo de flexion segun 7.6.1.1.

    Para losas no presforzadas con barras corrugadas:
    As_min = 0.0018 * Ag  (para fy >= 420 MPa)
    As_min = 0.0020 * Ag  (para fy < 420 MPa)

    Args:
        h_mm: Espesor de la losa (mm)
        fy_mpa: Limite de fluencia del acero (MPa)
        is_deformed_bars: True si son barras corrugadas (Grado 420 o superior)

    Returns:
        Tupla (As_min por metro de ancho en mm2/m, rho_min)
    """
    # Area bruta por metro de ancho
    Ag = h_mm * 1000  # mm2/m (1000mm = 1m de ancho)

    # Cuantia minima segun 7.6.1.1
    if is_deformed_bars and fy_mpa >= 420:
        # 7.6.1.1(a): Barras corrugadas Grado 420 o mayor
        rho_min = 0.0018
    elif is_deformed_bars and fy_mpa < 420:
        # 7.6.1.1(b): Barras corrugadas menores a Grado 420
        rho_min = 0.0020
    else:
        # Barras lisas o malla electrosoldada
        rho_min = 0.0020

    As_min = rho_min * Ag

    return As_min, rho_min


def get_minimum_shrinkage_reinforcement(
    h_mm: float,
    fy_mpa: float = 420.0
) -> Tuple[float, float]:
    """
    Calcula el refuerzo minimo de temperatura y retraccion segun 7.6.4.

    El refuerzo de T&S se requiere perpendicular al refuerzo de flexion.
    As_temp >= 0.0018 * Ag (para fy >= 420 MPa)

    Args:
        h_mm: Espesor de la losa (mm)
        fy_mpa: Limite de fluencia del acero (MPa)

    Returns:
        Tupla (As_temp por metro de ancho en mm2/m, rho_temp)
    """
    # Mismo requisito que refuerzo minimo de flexion
    return get_minimum_flexural_reinforcement(h_mm, fy_mpa)


def get_maximum_spacing(
    h_mm: float,
    is_critical_section: bool = False
) -> float:
    """
    Calcula el espaciamiento maximo del refuerzo segun 7.7.2.3.

    Espaciamiento maximo:
    - En zonas de momento maximo: min(3h, 450mm)
    - En otras zonas: min(5h, 450mm)

    Args:
        h_mm: Espesor de la losa (mm)
        is_critical_section: True si es zona de momento maximo

    Returns:
        Espaciamiento maximo (mm)
    """
    if is_critical_section:
        # 7.7.2.3: Zona de momento maximo
        return min(3 * h_mm, 450)
    else:
        # 7.7.2.4: Otras zonas
        return min(5 * h_mm, 450)


def get_maximum_spacing_shrinkage(h_mm: float) -> float:
    """
    Calcula el espaciamiento maximo del refuerzo de T&S segun 7.7.6.2.1.

    Espaciamiento maximo para refuerzo de T&S:
    - min(5h, 450mm)

    Args:
        h_mm: Espesor de la losa (mm)

    Returns:
        Espaciamiento maximo (mm)
    """
    return min(5 * h_mm, 450)


def check_reinforcement_limits(
    h_mm: float,
    d_mm: float,
    As_provided: float,
    spacing_provided: float,
    fy_mpa: float = 420.0,
    is_critical_section: bool = True
) -> ReinforcementCheckResult:
    """
    Verifica los limites de refuerzo para una losa 1-Way.

    Args:
        h_mm: Espesor de la losa (mm)
        d_mm: Profundidad efectiva (mm)
        As_provided: Area de refuerzo provista por metro (mm2/m)
        spacing_provided: Espaciamiento del refuerzo (mm)
        fy_mpa: Limite de fluencia del acero (MPa)
        is_critical_section: True si es zona de momento maximo

    Returns:
        ReinforcementCheckResult con resultados de verificacion
    """
    # Refuerzo minimo
    As_min, rho_min = get_minimum_flexural_reinforcement(h_mm, fy_mpa)

    # Cuantia provista
    rho_provided = As_provided / (1000 * d_mm) if d_mm > 0 else 0

    # Espaciamiento maximo
    spacing_max = get_maximum_spacing(h_mm, is_critical_section)

    # Verificaciones
    as_ok = As_provided >= As_min
    spacing_ok = spacing_provided <= spacing_max

    return ReinforcementCheckResult(
        As_min=As_min,
        As_provided=As_provided,
        is_ok=as_ok and spacing_ok,
        ratio=As_provided / As_min if As_min > 0 else 1.0,
        rho_min=rho_min,
        rho_provided=rho_provided,
        spacing_max=spacing_max,
        spacing_provided=spacing_provided,
        spacing_ok=spacing_ok,
        aci_reference='ACI 318-25 7.6.1.1, 7.7.2.3'
    )


# Constantes de refuerzo
FLEXURE_RHO_MIN_GR420 = 0.0018  # Cuantia minima para Gr420
FLEXURE_RHO_MIN_GR300 = 0.0020  # Cuantia minima para Gr300
MAX_SPACING_FLEXURE = 450       # mm - espaciamiento maximo absoluto
MAX_SPACING_SHRINKAGE = 450     # mm - espaciamiento maximo T&S
