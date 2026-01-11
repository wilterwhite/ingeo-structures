# app/services/analysis/element_analysis_service.py
"""
Servicio de análisis genérico para elementos estructurales.

Centraliza la lógica de verificación que era común a múltiples routes,
mejorando la separación de responsabilidades.

Uso:
    service = ElementAnalysisService()
    results, stats = service.analyze_elements(
        elements=parsed_data.columns,
        forces_dict=parsed_data.column_forces,
        category=SeismicCategory.SPECIAL,
        lambda_factor=1.0,
    )
"""
from typing import Dict, Tuple, List

from ..presentation.result_formatter import ResultFormatter
from .element_orchestrator import ElementOrchestrator
from .statistics_service import StatisticsService
from ...domain.chapter18.common import SeismicCategory


class ElementAnalysisService:
    """
    Servicio para análisis genérico de elementos estructurales.

    Orquesta la verificación de elementos usando ElementOrchestrator
    y formatea los resultados para la UI.
    """

    def __init__(self):
        """Inicializa el servicio con sus dependencias."""
        self._orchestrator = ElementOrchestrator()
        self._statistics = StatisticsService()

    def analyze_elements(
        self,
        elements: Dict,
        forces_dict: Dict,
        category: SeismicCategory,
        lambda_factor: float = 1.0,
    ) -> Tuple[List[dict], dict]:
        """
        Analiza elementos usando el orquestador unificado.

        Args:
            elements: Diccionario {element_key: element}
            forces_dict: Diccionario {element_key: forces}
            category: Categoría sísmica (SPECIAL, INTERMEDIATE, ORDINARY)
            lambda_factor: Factor para concreto liviano (default 1.0)

        Returns:
            Tuple (results_list, statistics_dict)
            - results_list: Lista de resultados formateados para UI
            - statistics_dict: Estadísticas {total, ok, fail, pass_rate}
        """
        results = []

        for key, element in elements.items():
            forces = forces_dict.get(key)

            # Verificar usando orquestador (clasifica y delega automáticamente)
            orchestration_result = self._orchestrator.verify(
                element=element,
                forces=forces,
                lambda_factor=lambda_factor,
                category=category,
            )

            # Formatear resultado para UI
            formatted = ResultFormatter.format_any_element(
                element, orchestration_result, key
            )
            results.append(formatted)

        statistics = self._statistics.calculate_dict_statistics(results)
        return results, statistics
