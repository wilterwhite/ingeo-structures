# app/services/analysis/pier_capacity_service.py
"""
Servicio de capacidades de piers.

Calcula capacidades puras (flexión, corte, esbeltez) y genera diagramas.
"""
from typing import Dict, Any, Optional

from ..parsing.session_manager import SessionManager
from ..presentation.plot_generator import PlotGenerator
from .flexure_service import FlexureService
from .shear_service import ShearService
from ...domain.flexure import SlendernessService


class PierCapacityService:
    """
    Servicio para cálculo de capacidades de piers.

    Calcula capacidades puras sin análisis de interacción,
    y genera diagramas de sección transversal.
    """

    def __init__(
        self,
        session_manager: SessionManager,
        flexure_service: Optional[FlexureService] = None,
        shear_service: Optional[ShearService] = None,
        slenderness_service: Optional[SlendernessService] = None,
        plot_generator: Optional[PlotGenerator] = None
    ):
        """
        Inicializa el servicio de capacidades.

        Args:
            session_manager: Gestor de sesiones (requerido)
            flexure_service: Servicio de flexión (opcional)
            shear_service: Servicio de corte (opcional)
            slenderness_service: Servicio de esbeltez (opcional)
            plot_generator: Generador de gráficos (opcional)
        """
        self._session_manager = session_manager
        self._flexure_service = flexure_service or FlexureService()
        self._shear_service = shear_service or ShearService()
        self._slenderness_service = slenderness_service or SlendernessService()
        self._plot_generator = plot_generator or PlotGenerator()

    # =========================================================================
    # Validación
    # =========================================================================

    def _validate_pier(
        self,
        session_id: str,
        pier_key: str
    ) -> Optional[Dict[str, Any]]:
        """Valida que el pier existe en la sesión."""
        if not self._session_manager.has_session(session_id):
            return {
                'success': False,
                'error': 'Session not found. Please upload the file again.'
            }

        pier = self._session_manager.get_pier(session_id, pier_key)
        if pier is None:
            return {'success': False, 'error': f'Pier not found: {pier_key}'}
        return None

    # =========================================================================
    # Capacidades y Diagramas
    # =========================================================================

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
        error = self._validate_pier(session_id, pier_key)
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

    def _apply_proposed_config(self, pier, config: Dict[str, Any]):
        """
        Crea una copia del pier con la configuración propuesta aplicada.

        Args:
            pier: Pier original
            config: Configuración propuesta

        Returns:
            Copia del pier con los cambios aplicados
        """
        from copy import deepcopy
        from ...domain.entities import Pier

        # Crear copia del pier
        pier_copy = Pier(
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

        return pier_copy

    def get_pier_capacities(self, session_id: str, pier_key: str) -> Dict[str, Any]:
        """
        Calcula las capacidades puras del pier (sin interacción).

        Delega a FlexureService y ShearService para los cálculos.

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier (Story_Label)

        Returns:
            Diccionario con información del pier y sus capacidades
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)

        # Delegar cálculos de flexión a FlexureService
        flexure_capacities = self._flexure_service.get_capacities(pier)

        # Delegar cálculos de corte a ShearService
        shear_capacities = self._shear_service.get_shear_capacity(pier, Nu=0)

        # Obtener datos detallados de esbeltez
        slenderness = self._slenderness_service.analyze(pier, k=0.8, braced=True)

        # Calcular capacidad reducida por esbeltez
        phi_Pn_max = flexure_capacities['phi_Pn_max']
        phi_Pn_reduced = (
            phi_Pn_max * slenderness.buckling_factor
            if slenderness.is_slender else phi_Pn_max
        )

        return {
            'success': True,
            'pier_info': {
                'label': pier.label,
                'story': pier.story,
                'width_m': round(pier.width / 1000, 3),
                'thickness_m': round(pier.thickness / 1000, 3),
                'height_m': round(pier.height / 1000, 2),
                'fc_MPa': pier.fc,
                'fy_MPa': pier.fy
            },
            'reinforcement': {
                'n_meshes': pier.n_meshes,
                'diameter_v': pier.diameter_v,
                'spacing_v': pier.spacing_v,
                'diameter_h': pier.diameter_h,
                'spacing_h': pier.spacing_h,
                'diameter_edge': pier.diameter_edge,
                'As_vertical_mm2': round(pier.As_vertical, 1),
                'As_edge_mm2': round(pier.As_edge_total, 1),
                'As_flexure_total_mm2': round(pier.As_flexure_total, 1),
                'description': pier.reinforcement_description
            },
            'slenderness': {
                'lambda': round(slenderness.lambda_ratio, 1),
                'k': slenderness.k,
                'lu_m': round(slenderness.lu / 1000, 2),
                'r_mm': round(slenderness.r, 1),
                'is_slender': slenderness.is_slender,
                'limit': slenderness.lambda_limit,
                'Pc_kN': round(slenderness.Pc_kN, 1),
                'buckling_factor': round(slenderness.buckling_factor, 3),
                'reduction_pct': (
                    round((1 - slenderness.buckling_factor) * 100, 0)
                    if slenderness.is_slender else 0
                )
            },
            'capacities': {
                'phi_Pn_max_tonf': round(phi_Pn_max, 1),
                'phi_Pn_reduced_tonf': round(phi_Pn_reduced, 1),
                'phi_Mn3_tonf_m': flexure_capacities['phi_Mn3'],
                'phi_Mn2_tonf_m': flexure_capacities['phi_Mn2'],
                'phi_Vn2_tonf': shear_capacities['phi_Vn_2'],
                'phi_Vn3_tonf': shear_capacities['phi_Vn_3']
            }
        }
