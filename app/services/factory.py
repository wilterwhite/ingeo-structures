# app/structural/services/factory.py
"""
Factory para crear servicios de análisis estructural.
Centraliza la creación de servicios y sus dependencias.
"""
from typing import Optional

from .pier_analysis import PierAnalysisService
from .parsing.session_manager import SessionManager
from .analysis.flexure_service import FlexureService
from .analysis.shear_service import ShearService
from .analysis.statistics_service import StatisticsService
from .presentation.plot_generator import PlotGenerator
from ..domain.flexure import InteractionDiagramService, SlendernessService


class ServiceFactory:
    """
    Factory para crear servicios de análisis estructural.

    Uso:
        # Crear servicio con defaults
        service = ServiceFactory.create_analysis_service()

        # Crear servicio con dependencias personalizadas (testing)
        mock_session = MockSessionManager()
        service = ServiceFactory.create_analysis_service(
            session_manager=mock_session
        )
    """

    @staticmethod
    def create_analysis_service(
        session_manager: Optional[SessionManager] = None,
        flexure_service: Optional[FlexureService] = None,
        shear_service: Optional[ShearService] = None,
        statistics_service: Optional[StatisticsService] = None,
        slenderness_service: Optional[SlendernessService] = None,
        interaction_service: Optional[InteractionDiagramService] = None,
        plot_generator: Optional[PlotGenerator] = None
    ) -> PierAnalysisService:
        """
        Crea una instancia de PierAnalysisService.

        Args:
            session_manager: Gestor de sesiones (opcional)
            flexure_service: Servicio de flexión (opcional)
            shear_service: Servicio de corte (opcional)
            statistics_service: Servicio de estadísticas (opcional)
            slenderness_service: Servicio de esbeltez (opcional)
            interaction_service: Servicio de diagrama interacción (opcional)
            plot_generator: Generador de gráficos (opcional)

        Returns:
            PierAnalysisService configurado
        """
        return PierAnalysisService(
            session_manager=session_manager,
            flexure_service=flexure_service,
            shear_service=shear_service,
            statistics_service=statistics_service,
            slenderness_service=slenderness_service,
            interaction_service=interaction_service,
            plot_generator=plot_generator
        )

    @staticmethod
    def create_default_analysis_service() -> PierAnalysisService:
        """Crea un servicio de análisis con todas las dependencias por defecto."""
        return PierAnalysisService()
