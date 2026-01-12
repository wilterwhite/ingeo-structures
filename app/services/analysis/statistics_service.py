# app/services/analysis/statistics_service.py
"""
Servicio de estadísticas y generación de gráficos resumen.

Trabaja con resultados en formato dict (desde format_any_element).
"""
from typing import Dict, List, Any

from ..presentation.plot_generator import PlotGenerator


class StatisticsService:
    """
    Servicio para cálculo de estadísticas y generación de gráficos resumen.

    Responsabilidades:
    - Calcular estadísticas de resultados de verificación
    - Generar gráficos resumen de factores de seguridad
    """

    def __init__(self):
        self._plot_generator = PlotGenerator()

    def calculate_dict_statistics(
        self,
        results: List[Dict[str, Any]],
        status_key: str = 'overall_status'
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas de resultados en formato dict.

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

    def generate_summary_from_dict(self, summary_data: List[Dict[str, Any]]) -> str:
        """
        Genera el gráfico resumen desde datos en formato dict.

        Args:
            summary_data: Lista de dicts con pier_label, flexure_sf, shear_sf

        Returns:
            Gráfico en base64
        """
        return self._plot_generator.generate_summary_chart(summary_data)
