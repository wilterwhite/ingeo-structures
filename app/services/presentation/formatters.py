# app/services/presentation/formatters.py
"""
Funciones auxiliares de formateo para presentación.

Módulo separado para evitar imports circulares.
"""
import math
from typing import Union


def format_safety_factor(
    value: float,
    as_string: bool = True,
    max_value: float = 100.0
) -> Union[float, str]:
    """
    Formatea factor de seguridad para serialización JSON.

    Args:
        value: Factor de seguridad a formatear
        as_string: Si True, retorna ">100" para valores grandes; si False, retorna 100.0
        max_value: Valor máximo a mostrar (default 100.0)

    Returns:
        Factor formateado como string ">100" o float redondeado
    """
    if math.isinf(value) or value > max_value:
        return f">{int(max_value)}" if as_string else max_value
    return round(value, 2)


def get_status_css_class(status: str) -> str:
    """
    Retorna la clase CSS según el estado del resultado.

    Args:
        status: Estado del elemento ('OK', 'FAIL', etc.)

    Returns:
        Clase CSS para aplicar al elemento
    """
    return 'status-ok' if status == 'OK' else 'status-fail'


def format_dimensions(width_mm: float, thickness_mm: float) -> str:
    """
    Formatea dimensiones en formato "ancho × espesor cm".

    Para muros: lw (largo) × tw (espesor)
    Para columnas: depth × width (como en nomenclatura COL_40x20)
    Para vigas: ancho × peralte

    Args:
        width_mm: Ancho/largo en mm (lw para muros, depth para columnas)
        thickness_mm: Espesor en mm (tw para muros, width para columnas)

    Returns:
        String formateado, ej: "40 × 20 cm" para COL_40x20
    """
    return f"{int(width_mm / 10)} × {int(thickness_mm / 10)} cm"


def format_dcr_display(dcr: float) -> str:
    """
    Formatea DCR para mostrar en UI.

    Args:
        dcr: Demand/Capacity ratio

    Returns:
        String formateado, ej: "0.85" o ">100"
    """
    if math.isinf(dcr) or dcr > 100:
        return '>100'
    return f"{dcr:.2f}"
