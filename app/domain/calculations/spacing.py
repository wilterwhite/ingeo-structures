# app/domain/calculations/spacing.py
"""
Cálculos centralizados de espaciamiento de refuerzo transversal.

Este módulo contiene las fórmulas de ACI 318-25 para calcular
espaciamientos máximos en elementos sísmicos.

Referencias:
- ACI 318-25 §18.7.5.3: Columnas especiales (espaciamiento en zona ℓo)
- ACI 318-25 §18.6.4: Vigas especiales (espaciamiento en zona de hoops)
- ACI 318-25 §18.10.6.4: Elementos de borde de muros

Uso:
    from app.domain.calculations.spacing import (
        calculate_so,
        calculate_s_max_column,
        calculate_s_max_beam,
    )
"""
from typing import Tuple


# Constantes de límites (pulgadas, convertidas a mm donde aplique)
SO_MIN_IN = 4.0  # §18.7.5.3(d): so mínimo
SO_MAX_IN = 6.0  # §18.7.5.3(d): so máximo
IN_TO_MM = 25.4


def calculate_so(hx_mm: float, steel_grade: int = 60) -> float:
    """
    Calcula espaciamiento so según §18.7.5.3(d).

    so = 4" + (14" - hx)/3, con 4" <= so <= 6"

    Para acero Grado 80 (fyt > 550 MPa), el límite superior es 5" en vez de 6"
    según la nota de la tabla 18.7.5.4.

    Args:
        hx_mm: Espaciamiento entre barras soportadas (mm)
        steel_grade: Grado del acero (60 u 80)

    Returns:
        Espaciamiento so (mm)

    Example:
        >>> calculate_so(150)  # hx = 150mm ≈ 6"
        127.0  # ≈ 5"
    """
    hx_in = hx_mm / IN_TO_MM
    so_in = SO_MIN_IN + (14 - hx_in) / 3

    # Límites según grado de acero
    so_max = 5.0 if steel_grade >= 80 else SO_MAX_IN
    so_in = max(SO_MIN_IN, min(so_in, so_max))

    return round(so_in * IN_TO_MM, 1)


def calculate_s_max_column(
    h_mm: float,
    db_mm: float,
    hx_mm: float,
    steel_grade: int = 60,
) -> Tuple[float, str]:
    """
    Calcula espaciamiento máximo en columnas según §18.7.5.3.

    s <= min(h/4, n*db, so) donde:
    - n = 6 para Grado 60
    - n = 5 para Grado 80

    Args:
        h_mm: Dimensión de la sección en dirección de análisis (mm)
        db_mm: Diámetro de barra longitudinal (mm)
        hx_mm: Espaciamiento entre barras soportadas (mm)
        steel_grade: Grado del acero (60 u 80)

    Returns:
        Tuple (s_max en mm, expresión que controla)

    Example:
        >>> s_max, governs = calculate_s_max_column(500, 22, 150)
        >>> print(f"s_max = {s_max}mm ({governs})")
        s_max = 125.0mm (h/4)
    """
    so = calculate_so(hx_mm, steel_grade)
    h_4 = h_mm / 4
    db_factor = 5 if steel_grade >= 80 else 6
    n_db = db_factor * db_mm

    limits = [
        (h_4, "h/4"),
        (n_db, f"{db_factor}×db"),
        (so, "so"),
    ]

    s_max, governing = min(limits, key=lambda x: x[0])
    return round(s_max, 1), governing


def calculate_s_max_beam(
    d_mm: float,
    db_long_mm: float,
    db_stirrup_mm: float = 10,
    steel_grade: int = 60,
) -> Tuple[float, str]:
    """
    Calcula espaciamiento máximo en vigas según §18.6.4.4.

    s <= min(d/4, 8*db_long, 24*db_stirrup, 300mm)

    Para acero Grado 80:
    s <= min(d/4, 6*db_long, 24*db_stirrup, 200mm)

    Args:
        d_mm: Profundidad efectiva (mm)
        db_long_mm: Diámetro de barra longitudinal más pequeña (mm)
        db_stirrup_mm: Diámetro del estribo (mm, default 10)
        steel_grade: Grado del acero (60 u 80)

    Returns:
        Tuple (s_max en mm, expresión que controla)

    Example:
        >>> s_max, governs = calculate_s_max_beam(450, 20)
        >>> print(f"s_max = {s_max}mm ({governs})")
        s_max = 112.5mm (d/4)
    """
    d_4 = d_mm / 4
    db_stir_24 = 24 * db_stirrup_mm

    if steel_grade >= 80:
        db_factor = 6
        s_abs_max = 200
    else:
        db_factor = 8
        s_abs_max = 300

    n_db = db_factor * db_long_mm

    limits = [
        (d_4, "d/4"),
        (n_db, f"{db_factor}×db"),
        (db_stir_24, "24×db_est"),
        (s_abs_max, f"{s_abs_max}mm"),
    ]

    s_max, governing = min(limits, key=lambda x: x[0])
    return round(s_max, 1), governing


def calculate_s_max_boundary(
    b_mm: float,
    steel_grade: int = 60,
) -> Tuple[float, str]:
    """
    Calcula espaciamiento máximo en elementos de borde según §18.10.6.4(e).

    s <= min(b/3, 6", 150mm para Grado 60)
    s <= min(b/3, 5", 125mm para Grado 80)

    Args:
        b_mm: Ancho del elemento de borde (mm)
        steel_grade: Grado del acero (60 u 80)

    Returns:
        Tuple (s_max en mm, expresión que controla)

    Example:
        >>> s_max, governs = calculate_s_max_boundary(400)
        >>> print(f"s_max = {s_max}mm ({governs})")
        s_max = 133.3mm (b/3)
    """
    b_3 = b_mm / 3

    if steel_grade >= 80:
        s_abs_max = 125  # 5"
        s_abs_label = "5\""
    else:
        s_abs_max = 150  # 6"
        s_abs_label = "6\""

    limits = [
        (b_3, "b/3"),
        (s_abs_max, s_abs_label),
    ]

    s_max, governing = min(limits, key=lambda x: x[0])
    return round(s_max, 1), governing
