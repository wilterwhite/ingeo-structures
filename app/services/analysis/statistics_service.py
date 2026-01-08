# app/structural/services/analysis/statistics_service.py
"""
Servicio de estadísticas y generación de gráficos resumen.
"""
from typing import Dict, List, Any, Optional

from ..presentation.plot_generator import PlotGenerator
from .verification_result import ElementVerificationResult


class StatisticsService:
    """
    Servicio para cálculo de estadísticas y generación de gráficos resumen.

    Responsabilidades:
    - Calcular estadísticas de resultados de verificación
    - Generar gráficos resumen de factores de seguridad
    """

    def __init__(self):
        self._plot_generator = PlotGenerator()

    def calculate_statistics(self, results: List[ElementVerificationResult]) -> Dict[str, Any]:
        """
        Calcula estadísticas de los resultados de verificación.

        Args:
            results: Lista de ElementVerificationResult

        Returns:
            Dict con total, ok, fail, pass_rate
        """
        total = len(results)
        ok_count = sum(1 for r in results if r.is_ok)
        fail_count = total - ok_count

        return {
            'total': total,
            'ok': ok_count,
            'fail': fail_count,
            'pass_rate': ok_count / total * 100 if total > 0 else 0
        }

    def generate_summary_plot(self, results: List[ElementVerificationResult]) -> str:
        """
        Genera el gráfico resumen de factores de seguridad.

        Args:
            results: Lista de ElementVerificationResult

        Returns:
            Gráfico en base64
        """
        summary_data = [
            {
                'pier_label': r.element_info.get('label', ''),
                'flexure_sf': r.flexure.sf,
                'shear_sf': r.shear.sf
            }
            for r in results
        ]
        return self._plot_generator.generate_summary_chart(summary_data)

    def generate_summary_from_dict(self, summary_data: List[Dict[str, Any]]) -> str:
        """
        Genera el gráfico resumen desde datos en formato dict.

        Args:
            summary_data: Lista de dicts con pier_label, flexure_sf, shear_sf

        Returns:
            Gráfico en base64
        """
        return self._plot_generator.generate_summary_chart(summary_data)

    def get_detailed_statistics(
        self,
        results: List[ElementVerificationResult]
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas detalladas por tipo de verificación.

        Args:
            results: Lista de ElementVerificationResult

        Returns:
            Dict con estadísticas detalladas
        """
        if not results:
            return {
                'total': 0,
                'overall': {'ok': 0, 'fail': 0, 'pass_rate': 0},
                'flexure': {'ok': 0, 'fail': 0, 'pass_rate': 0},
                'shear': {'ok': 0, 'fail': 0, 'pass_rate': 0},
                'sf_distribution': {
                    'flexure': {'min': 0, 'max': 0, 'avg': 0},
                    'shear': {'min': 0, 'max': 0, 'avg': 0}
                }
            }

        total = len(results)

        # Estadísticas globales
        overall_ok = sum(1 for r in results if r.is_ok)

        # Estadísticas flexión
        flexure_ok = sum(1 for r in results if r.flexure.status == "OK")

        # Estadísticas corte
        shear_ok = sum(1 for r in results if r.shear.status == "OK")

        # Distribución de SF
        flexure_sfs = [r.flexure.sf for r in results if r.flexure.sf < 100]
        shear_sfs = [r.shear.sf for r in results if r.shear.sf < 100]

        return {
            'total': total,
            'overall': {
                'ok': overall_ok,
                'fail': total - overall_ok,
                'pass_rate': round(overall_ok / total * 100, 1)
            },
            'flexure': {
                'ok': flexure_ok,
                'fail': total - flexure_ok,
                'pass_rate': round(flexure_ok / total * 100, 1)
            },
            'shear': {
                'ok': shear_ok,
                'fail': total - shear_ok,
                'pass_rate': round(shear_ok / total * 100, 1)
            },
            'sf_distribution': {
                'flexure': {
                    'min': round(min(flexure_sfs), 2) if flexure_sfs else 0,
                    'max': round(max(flexure_sfs), 2) if flexure_sfs else 0,
                    'avg': round(sum(flexure_sfs) / len(flexure_sfs), 2) if flexure_sfs else 0
                },
                'shear': {
                    'min': round(min(shear_sfs), 2) if shear_sfs else 0,
                    'max': round(max(shear_sfs), 2) if shear_sfs else 0,
                    'avg': round(sum(shear_sfs) / len(shear_sfs), 2) if shear_sfs else 0
                }
            }
        }

    def calculate_dict_statistics(
        self,
        results: List[Dict[str, Any]],
        status_key: str = 'overall_status'
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas de resultados en formato dict.

        Útil para columnas, vigas, losas que retornan dicts formateados.

        Args:
            results: Lista de dicts con clave status_key
            status_key: Clave que contiene el estado ('OK'/'NO OK')

        Returns:
            Dict con total, ok, fail, pass_rate
        """
        if not results:
            return {'total': 0, 'ok': 0, 'fail': 0, 'pass_rate': 100.0}

        total = len(results)
        ok_count = sum(1 for r in results if r.get(status_key) == 'OK')
        fail_count = total - ok_count

        return {
            'total': total,
            'ok': ok_count,
            'fail': fail_count,
            'pass_rate': round(ok_count / total * 100, 1) if total > 0 else 100.0
        }

    def get_critical_piers(
        self,
        results: List[ElementVerificationResult],
        n: int = 5,
        sort_by: str = 'overall'
    ) -> List[Dict[str, Any]]:
        """
        Obtiene los N piers más críticos.

        Args:
            results: Lista de ElementVerificationResult
            n: Número de piers a retornar
            sort_by: 'overall', 'flexure', o 'shear'

        Returns:
            Lista de los N piers más críticos
        """
        if not results:
            return []

        # Función para obtener el SF según criterio
        def get_sf(r: ElementVerificationResult) -> float:
            if sort_by == 'flexure':
                return r.flexure.sf
            elif sort_by == 'shear':
                return r.shear.sf
            else:  # overall - el mínimo
                return min(r.flexure.sf, r.shear.sf)

        # Ordenar por SF ascendente (más crítico primero)
        sorted_results = sorted(results, key=get_sf)

        # Retornar los N primeros
        critical = []
        for r in sorted_results[:n]:
            sf = get_sf(r)
            critical.append({
                'pier_label': r.element_info.get('label', ''),
                'story': r.element_info.get('story', ''),
                'overall_status': r.overall_status,
                'flexure_sf': round(r.flexure.sf, 2) if r.flexure.sf < 100 else '>100',
                'shear_sf': round(r.shear.sf, 2) if r.shear.sf < 100 else '>100',
                'critical_sf': round(sf, 2) if sf < 100 else '>100'
            })

        return critical
