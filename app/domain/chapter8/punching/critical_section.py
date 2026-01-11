# app/domain/chapter8/punching/critical_section.py
"""
Capitulo 22.6.4 ACI 318-25: Seccion Critica para Punzonamiento.

La seccion critica se ubica a d/2 de la cara de la columna o carga.
"""
from typing import Tuple
from enum import Enum
import math


class ColumnPosition(Enum):
    """Posicion de la columna para calculo de punzonamiento."""
    INTERIOR = "interior"       # Columna interior (4 lados)
    EDGE = "edge"               # Columna de borde (3 lados)
    CORNER = "corner"           # Columna de esquina (2 lados)


def calculate_critical_perimeter(
    c1_mm: float,
    c2_mm: float,
    d_mm: float,
    position: ColumnPosition = ColumnPosition.INTERIOR
) -> float:
    """
    Calcula el perimetro de la seccion critica (bo) segun 22.6.4.

    La seccion critica se ubica a d/2 de la cara de la columna.
    El perimetro depende de la posicion de la columna.

    Args:
        c1_mm: Dimension de la columna en direccion 1 (mm)
        c2_mm: Dimension de la columna en direccion 2 (mm)
        d_mm: Profundidad efectiva de la losa (mm)
        position: Posicion de la columna

    Returns:
        Perimetro critico bo (mm)
    """
    # Dimensiones de la seccion critica (a d/2 de la cara)
    b1 = c1_mm + d_mm  # Dimension en direccion 1
    b2 = c2_mm + d_mm  # Dimension en direccion 2

    if position == ColumnPosition.INTERIOR:
        # Columna interior: 4 lados
        bo = 2 * (b1 + b2)

    elif position == ColumnPosition.EDGE:
        # Columna de borde: 3 lados
        # Asumiendo borde en direccion 1
        bo = 2 * b1 + b2

    elif position == ColumnPosition.CORNER:
        # Columna de esquina: 2 lados
        bo = b1 + b2

    else:
        bo = 2 * (b1 + b2)  # Default a interior

    return bo


def calculate_critical_area(
    c1_mm: float,
    c2_mm: float,
    d_mm: float,
    position: ColumnPosition = ColumnPosition.INTERIOR
) -> float:
    """
    Calcula el area de la seccion critica (Ac).

    Ac = bo * d

    Args:
        c1_mm: Dimension de la columna en direccion 1 (mm)
        c2_mm: Dimension de la columna en direccion 2 (mm)
        d_mm: Profundidad efectiva de la losa (mm)
        position: Posicion de la columna

    Returns:
        Area de la seccion critica (mm2)
    """
    bo = calculate_critical_perimeter(c1_mm, c2_mm, d_mm, position)
    return bo * d_mm


def get_beta_column(c1_mm: float, c2_mm: float) -> float:
    """
    Calcula la relacion beta para columnas rectangulares.

    beta = lado_largo / lado_corto

    Args:
        c1_mm: Dimension de la columna en direccion 1 (mm)
        c2_mm: Dimension de la columna en direccion 2 (mm)

    Returns:
        Relacion beta (>= 1.0)
    """
    c_max = max(c1_mm, c2_mm)
    c_min = min(c1_mm, c2_mm)
    return c_max / c_min if c_min > 0 else 1.0


def get_alpha_s(position: ColumnPosition) -> float:
    """
    Obtiene el factor alpha_s segun 22.6.5.2.

    alpha_s depende de la posicion de la columna:
    - Interior: 40
    - Borde: 30
    - Esquina: 20

    Args:
        position: Posicion de la columna

    Returns:
        Factor alpha_s
    """
    alpha_values = {
        ColumnPosition.INTERIOR: 40,
        ColumnPosition.EDGE: 30,
        ColumnPosition.CORNER: 20,
    }
    return alpha_values.get(position, 40)


