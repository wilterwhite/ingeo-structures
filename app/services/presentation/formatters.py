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
    Formatea dimensiones en formato "espesor × ancho mm".

    Args:
        width_mm: Ancho en mm (lw para muros)
        thickness_mm: Espesor en mm (tw para muros)

    Returns:
        String formateado, ej: "200 × 3000 mm"
    """
    return f"{int(thickness_mm)} × {int(width_mm)} mm"


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
