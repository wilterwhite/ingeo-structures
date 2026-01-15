# app/services/analysis/statistics_service.py
"""
Servicio de cálculo de estadísticas para resultados de verificación.

Proporciona funciones para agregar y resumir resultados de análisis estructural.
"""
from typing import Any, Dict, List


def calculate_statistics(
    results: List[Dict[str, Any]],
    status_key: str = 'overall_status'
) -> Dict[str, Any]:
    """
    Calcula estadísticas de resultados de verificación.

    Args:
        results: Lista de dicts con clave status_key
        status_key: Clave que contiene el estado ('OK'/'NO OK')

    Returns:
        Dict con total, ok, fail, pass_rate
    """
    if not results:
        return {'total': 0, 'ok': 0, 'fail': 0, 'pass_rate': 100.0}

    total = len(results)
    ok = sum(1 for r in results if r.get(status_key) == 'OK')
    fail = total - ok

    return {
        'total': total,
        'ok': ok,
        'fail': fail,
        'pass_rate': round(ok / total * 100, 1) if total > 0 else 100.0
    }
