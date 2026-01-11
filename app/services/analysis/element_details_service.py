# app/services/analysis/element_details_service.py
"""
Servicio base genérico para detalles de elementos estructurales.

Provee la infraestructura común para obtener capacidades y verificaciones
de cualquier tipo de elemento estructural (Pier, Column, Beam, DropBeam).

Subclases especializadas:
- PierDetailsService: Agrega verificación de boundary elements (§18.10.6)

Uso:
    service = ElementDetailsService(session_manager)
    element, forces = service.get_element_and_forces(session_id, key, 'pier')
"""
from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING

from ..parsing.session_manager import SessionManager
from ..presentation.plot_generator import PlotGenerator
from .flexocompression_service import FlexocompressionService
from .shear_service import ShearService
from ...domain.flexure import SlendernessService

if TYPE_CHECKING:
    from .element_orchestrator import ElementOrchestrator


class ElementDetailsService:
    """
    Servicio base para obtener detalles de elementos estructurales.

    Provee métodos genéricos que funcionan con cualquier elemento que
    implemente el protocolo FlexuralElement:
    - get_element_and_forces(): Obtiene elemento y fuerzas por tipo
    - get_section_diagram(): Genera diagrama de sección transversal
    - get_flexure_capacities(): Calcula capacidades a flexión
    - get_shear_capacities(): Calcula capacidades a cortante
    """

    # Mapeo de tipos de elemento a métodos de SessionManager
    ELEMENT_GETTERS = {
        'pier': ('get_pier', 'get_pier_forces'),
        'column': ('get_column', 'get_column_forces'),
        'beam': ('get_beam', 'get_beam_forces'),
        'drop_beam': ('get_drop_beam', 'get_drop_beam_forces'),
    }

    def __init__(
        self,
        session_manager: SessionManager,
        orchestrator: Optional['ElementOrchestrator'] = None,
        flexocompression_service: Optional[FlexocompressionService] = None,
        shear_service: Optional[ShearService] = None,
        slenderness_service: Optional[SlendernessService] = None,
        plot_generator: Optional[PlotGenerator] = None
    ):
        """
        Inicializa el servicio de detalles.

        Args:
            session_manager: Gestor de sesiones (requerido)
            orchestrator: Orquestador de verificación (opcional)
            flexocompression_service: Servicio para gráficos P-M (opcional)
            shear_service: Servicio para capacidades de corte (opcional)
            slenderness_service: Servicio de esbeltez (opcional)
            plot_generator: Generador de gráficos (opcional)
        """
        self._session_manager = session_manager

        # Import lazy para evitar circular
        if orchestrator is None:
            from .element_orchestrator import ElementOrchestrator
            orchestrator = ElementOrchestrator()
        self._orchestrator = orchestrator

        # Servicios de dominio
        self._flexo_service = flexocompression_service or FlexocompressionService()
        self._shear_service = shear_service or ShearService()
        self._slenderness_service = slenderness_service or SlendernessService()
        self._plot_generator = plot_generator or PlotGenerator()

    def get_element_and_forces(
        self,
        session_id: str,
        element_key: str,
        element_type: str
    ) -> Tuple[Any, Any, Optional[Dict[str, Any]]]:
        """
        Obtiene un elemento y sus fuerzas según el tipo.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento (Story_Label)
            element_type: Tipo de elemento ('pier', 'column', 'beam', 'drop_beam')

        Returns:
            Tuple (elemento, fuerzas, error_dict o None)
            - Si hay error: (None, None, {'success': False, 'error': '...'})
            - Si OK: (elemento, fuerzas, None)
        """
        if element_type not in self.ELEMENT_GETTERS:
            return None, None, {
                'success': False,
                'error': f'Tipo de elemento no soportado: {element_type}'
            }

        getter_name, forces_getter_name = self.ELEMENT_GETTERS[element_type]
        getter = getattr(self._session_manager, getter_name)
        forces_getter = getattr(self._session_manager, forces_getter_name)

        element = getter(session_id, element_key)
        if element is None:
            return None, None, {
                'success': False,
                'error': f'{element_type.capitalize()} no encontrado: {element_key}'
            }

        forces = forces_getter(session_id, element_key)
        return element, forces, None

    def get_section_diagram(
        self,
        session_id: str,
        element_key: str,
        element_type: str = 'pier',
        proposed_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera un diagrama de la sección transversal del elemento.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento (Story_Label)
            element_type: Tipo de elemento ('pier', 'column')
            proposed_config: Configuración propuesta opcional (para preview)

        Returns:
            Dict con section_diagram en base64
        """
        element, _, error = self.get_element_and_forces(
            session_id, element_key, element_type
        )
        if error:
            return error

        # Generar diagrama según tipo
        if element_type == 'pier':
            if proposed_config:
                element = self._apply_proposed_config_pier(element, proposed_config)
            section_diagram = self._plot_generator.generate_section_diagram(element)
        elif element_type == 'column':
            section_diagram = self._plot_generator.generate_column_section_diagram(element)
        else:
            return {'success': False, 'error': f'Diagrama no soportado para {element_type}'}

        return {
            'success': True,
            'element_key': element_key,
            'element_type': element_type,
            'section_diagram': section_diagram,
            'is_proposed': proposed_config is not None
        }

    def get_flexure_capacities(
        self,
        element,
        pn_max_factor: float = 0.80,
        k: float = 0.8
    ) -> Dict[str, Any]:
        """
        Obtiene las capacidades a flexión de un elemento.

        Args:
            element: Elemento estructural (Pier, Column, etc.)
            pn_max_factor: Factor de reducción Pn máximo (default 0.80)
            k: Factor de longitud efectiva (default 0.8)

        Returns:
            Dict con phi_Pn_max, phi_Mn3, phi_Mn2
        """
        return self._flexo_service.get_capacities(element, pn_max_factor, k)

    def get_shear_capacities(
        self,
        element,
        Nu: float = 0
    ) -> Dict[str, Any]:
        """
        Obtiene las capacidades a cortante de un elemento.

        Args:
            element: Elemento estructural
            Nu: Carga axial última (N)

        Returns:
            Dict con phi_Vn_2, phi_Vn_3, Vc_2, Vc_3, etc.
        """
        return self._shear_service.get_shear_capacity(element, Nu)

    def get_slenderness_analysis(
        self,
        element,
        k: float = 0.8,
        braced: bool = True
    ) -> Any:
        """
        Obtiene el análisis de esbeltez de un elemento.

        Args:
            element: Elemento estructural
            k: Factor de longitud efectiva
            braced: Si el pórtico está arriostrado

        Returns:
            SlendernessResult con lambda, delta_ns, etc.
        """
        return self._slenderness_service.analyze(element, k, braced)

    def _apply_proposed_config_pier(self, pier, config: Dict[str, Any]):
        """
        Crea una copia del pier con la configuración propuesta aplicada.

        Args:
            pier: Pier original
            config: Configuración propuesta

        Returns:
            Copia del pier con los cambios aplicados
        """
        from ...domain.entities import Pier

        return Pier(
            label=pier.label,
            story=pier.story,
            width=pier.width,
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
