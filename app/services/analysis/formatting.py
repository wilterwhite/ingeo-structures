# app/services/analysis/formatting.py
"""
Funciones de formateo para resultados de analisis estructural.

Centraliza la logica de formateo para evitar duplicacion y garantizar
consistencia en las respuestas JSON.
"""
import math
from typing import Any, Callable, Dict, List, Union


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


def calculate_summary_stats(
    results: Union[List, Dict],
    ok_filter: Callable[[Any], bool]
) -> Dict[str, Any]:
    """
    Calcula estadisticas resumidas de resultados de verificacion.

    Args:
        results: Lista o diccionario de resultados
        ok_filter: Funcion que retorna True si el resultado es OK

    Returns:
        Dict con total, ok, fail, pass_rate

    Examples:
        >>> results = [{'status': 'OK'}, {'status': 'NO OK'}]
        >>> calculate_summary_stats(results, lambda r: r['status'] == 'OK')
        {'total': 2, 'ok': 1, 'fail': 1, 'pass_rate': 50.0}
    """
    items = list(results.values()) if isinstance(results, dict) else list(results)
    total = len(items)

    if total == 0:
        return {
            'total': 0,
            'ok': 0,
            'fail': 0,
            'pass_rate': 100.0
        }

    ok_count = sum(1 for r in items if ok_filter(r))

    return {
        'total': total,
        'ok': ok_count,
        'fail': total - ok_count,
        'pass_rate': round(ok_count / total * 100, 1)
    }


def format_dcr(value: float, precision: int = 3) -> float:
    """
    Formatea Demand-Capacity Ratio (DCR).

    Args:
        value: DCR a formatear
        precision: Decimales (default 3)

    Returns:
        DCR redondeado
    """
    if math.isinf(value):
        return 0.0  # DCR infinito indica capacidad cero
    return round(value, precision)
