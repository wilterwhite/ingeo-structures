# app/services/parsing/config_parser.py
"""
Funciones de parseo y validación de configuraciones desde requests HTTP.

Centraliza la conversión de datos JSON del frontend a diccionarios
con valores validados y defaults aplicados.
"""
from typing import Optional, Dict, Any


def parse_beam_config(beam_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Parsea y valida configuración de viga de acoplamiento desde JSON.

    Aplica valores por defecto para campos faltantes y convierte
    tipos según sea necesario.

    Args:
        beam_data: Diccionario con datos de la viga desde el request
                   Puede contener: width, height, ln, n_bars_top,
                   diameter_top, n_bars_bottom, diameter_bottom

    Returns:
        Diccionario normalizado con todos los campos, o None si beam_data es None
    """
    if not beam_data:
        return None

    return {
        'width': float(beam_data.get('width', 200)),
        'height': float(beam_data.get('height', 500)),
        'ln': float(beam_data.get('ln', 1500)),
        'n_bars_top': int(beam_data.get('n_bars_top', 2)),
        'diameter_top': int(beam_data.get('diameter_top', 12)),
        'n_bars_bottom': int(beam_data.get('n_bars_bottom', 2)),
        'diameter_bottom': int(beam_data.get('diameter_bottom', 12))
    }
