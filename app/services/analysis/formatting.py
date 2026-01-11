# app/services/analysis/formatting.py
"""
Funciones de formateo para resultados de analisis estructural.

Centraliza la logica de formateo para evitar duplicacion y garantizar
consistencia en las respuestas JSON.
"""
import math
from typing import Union


def format_safety_factor(
    value: float,
    as_string: bool = True,
    max_value: float = 100.0
) -> Union[float, str]:
    """
    Formatea factor de seguridad para serializacion JSON.

    Args:
        value: Factor de seguridad a formatear
        as_string: Si True, retorna ">100" para valores grandes; si False, retorna 100.0
        max_value: Valor maximo a mostrar (default 100.0)

    Returns:
        Factor formateado como string ">100" o float redondeado

    Examples:
        >>> format_safety_factor(float('inf'))
        '>100'
        >>> format_safety_factor(float('inf'), as_string=False)
        100.0
        >>> format_safety_factor(2.567)
        2.57
    """
    if math.isinf(value) or value > max_value:
        return f">{int(max_value)}" if as_string else max_value
    return round(value, 2)


