# app/services/analysis/section_diagram_service.py
"""
Servicio para generación de diagramas de sección transversal.

Extraído de PierCapacityService para separar responsabilidades.
"""
from typing import Dict, Any, Optional

from ..parsing.session_manager import SessionManager
from ..presentation.plot_generator import PlotGenerator
from ...domain.entities import Pier


class SectionDiagramService:
    """
    Servicio para generar diagramas de sección transversal de piers.

    Responsabilidad única: generación visual de secciones.
    """

    def __init__(
        self,
        session_manager: SessionManager,
        plot_generator: Optional[PlotGenerator] = None
    ):
        """
        Inicializa el servicio.

        Args:
            session_manager: Gestor de sesiones (requerido)
            plot_generator: Generador de gráficos (opcional)
        """
        self._session_manager = session_manager
        self._plot_generator = plot_generator or PlotGenerator()

    def get_section_diagram(
        self,
        session_id: str,
        pier_key: str,
        proposed_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera un diagrama de la sección transversal del pier.

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier (Story_Label)
            proposed_config: Configuración propuesta opcional (para preview)

        Returns:
            Dict con section_diagram en base64
        """
        error = self._session_manager.validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)

        # Si hay configuración propuesta, crear copia y aplicar cambios
        if proposed_config:
            pier = self._apply_proposed_config(pier, proposed_config)

        section_diagram = self._plot_generator.generate_section_diagram(pier)

        return {
            'success': True,
            'pier_key': pier_key,
            'section_diagram': section_diagram,
            'is_proposed': proposed_config is not None
        }

    def _apply_proposed_config(self, pier: Pier, config: Dict[str, Any]) -> Pier:
        """
        Crea una copia del pier con la configuración propuesta aplicada.

        Args:
            pier: Pier original
            config: Configuración propuesta

        Returns:
            Copia del pier con los cambios aplicados
        """
        # Crear copia del pier con campos modificados
        return Pier(
            label=pier.label,
            story=pier.story,
            width=pier.width,  # Largo del muro no cambia
            thickness=config.get('thickness', pier.thickness),
            height=pier.height,
            fc=pier.fc,
            fy=pier.fy,
            n_meshes=config.get('n_meshes', pier.n_meshes),
            diameter_v=config.get('diameter_v', pier.diameter_v),
            spacing_v=config.get('spacing_v', pier.spacing_v),
            diameter_h=config.get('diameter_h', pier.diameter_h),
            spacing_h=config.get('spacing_h', pier.spacing_h),
            n_edge_bars=config.get('n_edge_bars', pier.n_edge_bars),
            diameter_edge=config.get('diameter_edge', pier.diameter_edge),
            stirrup_diameter=config.get('stirrup_diameter', pier.stirrup_diameter),
            stirrup_spacing=config.get('stirrup_spacing', pier.stirrup_spacing),
            n_stirrup_legs=config.get('n_stirrup_legs', getattr(pier, 'n_stirrup_legs', 2)),
            cover=pier.cover,
            axis_angle=pier.axis_angle
        )
