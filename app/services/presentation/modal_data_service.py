# app/services/presentation/modal_data_service.py
"""
Servicio de datos para el modal de detalles de elementos.

Prepara datos estructurados para el modal de detalles,
leyendo del cache de análisis (sin recálculos).

MÉTODO PRINCIPAL:
    get_element_capacities(session_id, element_key, element_type)

Uso:
    service = ElementDetailsService(session_manager)
    result = service.get_element_capacities(session_id, 'Story1_P1', 'pier')
"""
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING
import logging

from ..parsing.session_manager import SessionManager

logger = logging.getLogger(__name__)
from ...domain.constants.units import TONF_TO_N, TONFM_TO_NMM
from ...domain.chapter18.boundary_elements import (
    calculate_boundary_stress as _calculate_boundary_stress,
    BoundaryStressAnalysis,
)

from .plot_generator import PlotGenerator
from ..analysis.flexocompression_service import FlexocompressionService
from ..analysis.shear_service import ShearService
from ...domain.flexure import SlendernessService
from ...domain.chapter18.reinforcement import SeismicReinforcementService
from ...domain.entities import VerticalElement

if TYPE_CHECKING:
    from ..analysis.element_orchestrator import ElementOrchestrator


def calculate_boundary_stress(pier, P_tonf: float, M_tonfm: float) -> BoundaryStressAnalysis:
    """
    Wrapper que convierte unidades y delega a domain/.

    Args:
        pier: Pier con width, thickness y fc
        P_tonf: Carga axial en tonf (positivo = compresión)
        M_tonfm: Momento flector en tonf-m (valor absoluto)

    Returns:
        BoundaryStressAnalysis con esfuerzos calculados
    """
    P_N = P_tonf * TONF_TO_N
    M_Nmm = abs(M_tonfm) * TONFM_TO_NMM
    return _calculate_boundary_stress(
        width=pier.width,
        thickness=pier.thickness,
        fc=pier.fc,
        P_N=P_N,
        M_Nmm=M_Nmm
    )


class ElementDetailsService:
    """
    Servicio unificado de detalles de elementos estructurales.

    Soporta: pier, column, beam, drop_beam.

    Responsabilidades:
    - Obtener capacidades de elementos (flexión, cortante)
    - Generar diagramas de sección transversal
    - Verificar boundary elements (§18.10.6)
    - Calcular detalles por combinación de carga
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
        Inicializa el servicio de detalles de elementos.

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
        self._seismic_reinf_service = SeismicReinforcementService()

    # =========================================================================
    # Métodos de Acceso a Elementos (antes en clase base)
    # =========================================================================

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

    def _apply_proposed_config_pier(self, pier, config: Dict[str, Any]):
        """
        Crea una copia del pier con la configuración propuesta aplicada.

        Args:
            pier: VerticalElement original
            config: Configuración propuesta

        Returns:
            Copia del pier con los cambios aplicados
        """
        return VerticalElement(
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
            n_shear_legs=config.get('n_shear_legs', getattr(pier, 'n_shear_legs', 2)),
            cover=pier.cover,
            axis_angle=pier.axis_angle
        )

    # =========================================================================
    # Validación (delegada a SessionManager)
    # =========================================================================

    def _validate_pier(self, session_id: str, pier_key: str) -> Optional[Dict[str, Any]]:
        """Valida que el pier existe en la sesión."""
        return self._session_manager.validate_pier(session_id, pier_key)

    def _find_critical_combination(
        self,
        pier_forces,
        critical_combo_name: str
    ) -> Optional[Any]:
        """
        Busca una combinación por nombre en la lista de combinaciones.

        Args:
            pier_forces: Objeto con lista de combinaciones
            critical_combo_name: Nombre de la combinación a buscar
                                 (puede ser "name" o "name (location)")

        Returns:
            La combinación encontrada o None
        """
        for combo in pier_forces.combinations:
            # Coincidencia exacta con nombre completo
            combo_full_name = f"{combo.name} ({combo.location})"
            if combo_full_name == critical_combo_name:
                return combo
            # Coincidencia parcial con solo el nombre
            if combo.name == critical_combo_name or combo.name in critical_combo_name:
                return combo
        return None

    # =========================================================================
    # Capacidades y Diagramas
    # =========================================================================

    def get_section_diagram(
        self,
        session_id: str,
        element_key: str,
        proposed_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera un diagrama de la sección transversal del pier o columna.

        Intenta primero como pier, luego como columna.
        Override del método base para mantener compatibilidad con API existente.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento (Story_Label)
            proposed_config: Configuración propuesta opcional (para preview)

        Returns:
            Dict con section_diagram en base64
        """
        # Intentar obtener como pier primero
        pier = self._session_manager.get_pier(session_id, element_key)
        if pier is not None:
            if proposed_config:
                pier = self._apply_proposed_config_pier(pier, proposed_config)
            section_diagram = self._plot_generator.generate_section_diagram(pier)
            return {
                'success': True,
                'pier_key': element_key,
                'section_diagram': section_diagram,
                'is_proposed': proposed_config is not None
            }

        # Intentar obtener como columna
        column = self._session_manager.get_column(session_id, element_key)
        if column is not None:
            section_diagram = self._plot_generator.generate_column_section_diagram(column)
            return {
                'success': True,
                'pier_key': element_key,
                'section_diagram': section_diagram,
                'is_proposed': False
            }

        # Ni pier ni columna encontrado
        return {'success': False, 'error': f'Element not found: {element_key}'}

    def get_pier_capacities(self, session_id: str, pier_key: str) -> Dict[str, Any]:
        """
        Calcula las capacidades del pier y datos de verificación estilo ETABS.

        DEPRECATED: Usar get_element_capacities(session_id, pier_key, 'pier').
        Este método se mantiene por compatibilidad de API.

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier (Story_Label)

        Returns:
            Diccionario con información completa del pier estilo ETABS
        """
        result = self.get_element_capacities(session_id, pier_key, 'pier')

        # Adaptar formato para compatibilidad con API legacy
        if result.get('success') and 'element_info' in result:
            result['pier_info'] = result.pop('element_info')

        return result

    def _calculate_neutral_axis_depth(
        self,
        pier,
        Pu: float,
        Mu: float
    ) -> Optional[float]:
        """
        Calcula la profundidad del eje neutro para un punto de demanda.

        Delega a FlexocompressionService.get_c_at_point().

        Args:
            pier: Pier
            Pu: Carga axial (tonf)
            Mu: Momento (tonf-m)

        Returns:
            Profundidad c en mm, o None si no se puede calcular
        """
        try:
            interaction_points, _ = self._flexo_service.generate_interaction_curve(
                pier, direction='primary', apply_slenderness=False, k=0.8
            )
            return self._flexo_service.get_c_at_point(interaction_points, Pu, Mu)
        except Exception as e:
            logger.warning(
                "Error calculando eje neutro para Pu=%.2f, Mu=%.2f: %s",
                Pu, Mu, str(e)
            )
            return None

    def _get_boundary_check_data(
        self,
        pier,
        pier_forces
    ) -> Dict[str, Any]:
        """
        Obtiene datos de verificación de elementos de borde estilo ETABS.

        Returns:
            Dict con datos de boundary element check
        """
        if not pier_forces or not pier_forces.combinations:
            return {
                'has_data': False,
                'rows': []
            }

        # Buscar la combinación con mayor esfuerzo de compresión en cada borde
        max_sigma_left = 0.0
        max_sigma_right = 0.0
        critical_combo_left = 'N/A'
        critical_combo_right = 'N/A'
        Pu_left = 0.0
        Mu_left = 0.0
        Pu_right = 0.0
        Mu_right = 0.0
        sigma_limit = 0.2 * pier.fc  # Se usará para el resultado

        for combo in pier_forces.combinations:
            M_max = max(abs(combo.M2), abs(combo.M3))
            stress = calculate_boundary_stress(pier, combo.P, M_max)
            combo_name = f"{combo.name} ({combo.location})"

            if stress.sigma_left > max_sigma_left:
                max_sigma_left = stress.sigma_left
                critical_combo_left = combo_name
                Pu_left = combo.P
                Mu_left = M_max

            if stress.sigma_right > max_sigma_right:
                max_sigma_right = stress.sigma_right
                critical_combo_right = combo_name
                Pu_right = combo.P
                Mu_right = M_max

        # Determinar si se requiere elemento de borde
        required_left = max_sigma_left >= sigma_limit
        required_right = max_sigma_right >= sigma_limit

        # Calcular c para la combinación crítica (si se requiere)
        c_left = self._calculate_neutral_axis_depth(pier, Pu_left, Mu_left) if required_left else None
        c_right = self._calculate_neutral_axis_depth(pier, Pu_right, Mu_right) if required_right else None

        rows = [
            {
                'location': 'Left',
                'combo': critical_combo_left,
                'Pu_tonf': round(Pu_left, 2),
                'Mu_tonf_m': round(Mu_left, 2),
                'sigma_comp_MPa': round(max_sigma_left, 2),
                'sigma_limit_MPa': round(sigma_limit, 2),
                'c_mm': round(c_left, 0) if c_left else '—',
                'required': 'Yes' if required_left else 'No'
            },
            {
                'location': 'Right',
                'combo': critical_combo_right,
                'Pu_tonf': round(Pu_right, 2),
                'Mu_tonf_m': round(Mu_right, 2),
                'sigma_comp_MPa': round(max_sigma_right, 2),
                'sigma_limit_MPa': round(sigma_limit, 2),
                'c_mm': round(c_right, 0) if c_right else '—',
                'required': 'Yes' if required_right else 'No'
            }
        ]

        return {
            'has_data': True,
            'rows': rows,
            'any_required': required_left or required_right
        }

    def get_combination_details(
        self,
        session_id: str,
        pier_key: str,
        combo_index: int
    ) -> Dict[str, Any]:
        """
        Obtiene los detalles de diseño para una combinación específica.

        ARQUITECTURA: Lee SIEMPRE del cache de combo_results calculado durante
        el análisis inicial. Esto garantiza que el modal muestre el mismo DCR
        que la tabla (sin recálculos que pueden dar resultados diferentes).

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier
            combo_index: Índice de la combinación

        Returns:
            Dict con datos de flexión, corte y boundary para esa combinación
        """
        # Obtener cache del análisis inicial (obligatorio)
        cached_result = self._session_manager.get_analysis_result(session_id, pier_key)
        if not cached_result:
            return {
                'success': False,
                'error': f'Elemento {pier_key} no encontrado en cache. Ejecute análisis primero.'
            }

        # Validar combo_index
        if combo_index is None:
            combo_index = 0

        # Obtener fuerzas para info adicional
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)
        if not pier_forces or not pier_forces.combinations:
            return {'success': False, 'error': 'No hay combinaciones de carga'}

        if combo_index < 0 or combo_index >= len(pier_forces.combinations):
            return {'success': False, 'error': 'Índice de combinación inválido'}

        combo = pier_forces.combinations[combo_index]

        # =====================================================================
        # LEER FLEXURE DEL CACHE (combo_results)
        # =====================================================================
        cached_flexure = cached_result.get('flexure', {})
        flexure_combo_results = cached_flexure.get('combo_results', [])

        if combo_index < len(flexure_combo_results):
            # Usar resultado pre-calculado del combo específico
            flex_combo = flexure_combo_results[combo_index]
            flexure_data = {
                'location': flex_combo.get('location', combo.location),
                'Pu_tonf': flex_combo.get('Pu', round(combo.P, 2)),
                'Mu2_tonf_m': round(combo.M2, 2),
                'Mu3_tonf_m': flex_combo.get('Mu', round(combo.M3, 2)),
                'phi_Mn_tonf_m': flex_combo.get('phi_Mn_at_Pu', 0),
                'c_mm': '—',  # No calculado por combo
                'dcr': flex_combo.get('dcr', 0),
                'sf': flex_combo.get('sf', 0),
                'status': flex_combo.get('status', 'OK'),
            }
        else:
            # Fallback: usar datos críticos del cache (no debería pasar)
            flexure_data = self._build_flexure_from_cache(cached_result, combo)

        # =====================================================================
        # LEER SHEAR DEL CACHE (combo_results)
        # =====================================================================
        cached_shear = cached_result.get('shear', {})
        shear_combo_results = cached_shear.get('combo_results', [])

        if combo_index < len(shear_combo_results):
            # Usar resultado pre-calculado del combo específico
            shear_combo = shear_combo_results[combo_index]
            shear_data = {
                'rows': [{
                    'direction': 'V2',
                    'dcr': shear_combo.get('dcr_combined', shear_combo.get('dcr_2', 0)),
                    'combo': f"{combo.name} ({combo.location})",
                    'Pu_tonf': shear_combo.get('Pu', round(combo.P, 2)),
                    'Mu_tonf_m': round(max(abs(combo.M2), abs(combo.M3)), 2),
                    'Vu_tonf': shear_combo.get('Vu_2', round(abs(combo.V2), 2)),
                    'phi_Vc_tonf': shear_combo.get('phi_Vc', 0),
                    'phi_Vn_tonf': shear_combo.get('phi_Vn_2', 0),
                }],
                'has_data': True,
                'dcr_combined': shear_combo.get('dcr_combined', 0),
            }
        else:
            # Fallback: usar datos críticos del cache
            shear_data = self._build_shear_from_cache(cached_result, combo)

        # =====================================================================
        # BOUNDARY: Calcular para este combo (no se cachea por combo)
        # =====================================================================
        pier = self._session_manager.get_pier(session_id, pier_key)
        if pier:
            boundary_data = self._calc_boundary_for_combo(pier, combo)
        else:
            boundary_data = {'rows': []}

        return {
            'success': True,
            'combo_name': combo.name,
            'combo_location': combo.location,
            'forces': {
                'P': round(combo.P, 2),
                'M2': round(combo.M2, 2),
                'M3': round(combo.M3, 2),
                'V2': round(combo.V2, 2),
                'V3': round(combo.V3, 2)
            },
            'flexure': flexure_data,
            'shear': shear_data,
            'boundary': boundary_data
        }

    def _build_flexure_from_cache(
        self,
        cached_result: Dict[str, Any],
        combo
    ) -> Dict[str, Any]:
        """Construye datos de flexión desde el cache del análisis inicial."""
        cached_flexure = cached_result.get('flexure', {})
        return {
            'location': combo.location,
            'Pu_tonf': round(combo.P, 2),
            'Mu2_tonf_m': round(combo.M2, 2),
            'Mu3_tonf_m': round(combo.M3, 2),
            'phi_Mn_tonf_m': cached_flexure.get('phi_Mn_at_Pu', 0),
            'c_mm': cached_flexure.get('c', '—'),
            'dcr': cached_flexure.get('dcr', 0)
        }

    def _build_shear_from_cache(
        self,
        cached_result: Dict[str, Any],
        combo
    ) -> Dict[str, Any]:
        """Construye datos de cortante desde el cache del análisis inicial."""
        cached_shear = cached_result.get('shear', {})
        return {
            'rows': [
                {
                    'direction': 'V2',
                    'dcr': cached_shear.get('dcr', 0),
                    'combo': f"{combo.name} ({combo.location})",
                    'Pu_tonf': round(combo.P, 2),
                    'Mu_tonf_m': round(max(abs(combo.M2), abs(combo.M3)), 2),
                    'Vu_tonf': round(abs(combo.V2), 2),
                    'phi_Vc_tonf': cached_shear.get('phi_Vc', 0),
                    'phi_Vn_tonf': cached_shear.get('phi_Vn', 0)
                }
            ],
            'has_data': True
        }

    def _calc_boundary_for_combo(self, pier, combo) -> Dict[str, Any]:
        """
        Calcula datos de boundary element para una combinación específica.

        IMPORTANTE: Convención de signos:
        - ETABS: P negativo = compresión
        - calculate_boundary_stress: P positivo = compresión
        - Por eso usamos -combo.P
        """
        # CORREGIDO: Convertir a convención positivo = compresión
        Pu = -combo.P
        Mu = max(abs(combo.M2), abs(combo.M3))
        stress = calculate_boundary_stress(pier, Pu, Mu)

        c_left = self._calculate_neutral_axis_depth(pier, Pu, Mu) if stress.required_left else None
        c_right = self._calculate_neutral_axis_depth(pier, Pu, Mu) if stress.required_right else None

        return {
            'rows': [
                {
                    'location': 'Left',
                    'Pu_tonf': round(combo.P, 2),
                    'Mu_tonf_m': round(Mu, 2),
                    'sigma_comp_MPa': round(stress.sigma_left, 2),
                    'sigma_limit_MPa': round(stress.sigma_limit, 2),
                    'c_mm': round(c_left, 0) if c_left else '—',
                    'required': 'Yes' if stress.required_left else 'No'
                },
                {
                    'location': 'Right',
                    'Pu_tonf': round(combo.P, 2),
                    'Mu_tonf_m': round(Mu, 2),
                    'sigma_comp_MPa': round(stress.sigma_right, 2),
                    'sigma_limit_MPa': round(stress.sigma_limit, 2),
                    'c_mm': round(c_right, 0) if c_right else '—',
                    'required': 'Yes' if stress.required_right else 'No'
                }
            ]
        }


    # =========================================================================
    # Capacidades Unificadas para Todos los Elementos
    # =========================================================================

    def get_element_capacities(
        self,
        session_id: str,
        element_key: str,
        element_type: str = 'pier'
    ) -> Dict[str, Any]:
        """
        Obtiene capacidades de un elemento DESDE EL CACHE.

        No recalcula - usa los mismos datos que muestra la tabla.
        Esto garantiza consistencia entre tabla y modal.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento (Story_Label)
            element_type: 'pier', 'column', 'beam', 'drop_beam'

        Returns:
            Dict con información completa del elemento estilo ETABS
        """
        # =====================================================================
        # PASO 1: Leer del cache (obligatorio - sin fallbacks)
        # =====================================================================
        cached = self._session_manager.get_analysis_result(session_id, element_key)
        if not cached:
            return {
                'success': False,
                'error': f'Elemento {element_key} no encontrado en cache. Ejecute análisis primero.'
            }

        # Detectar si es strut desde el cache o desde el elemento
        is_strut = cached.get('element_type') == 'strut'

        # =====================================================================
        # PASO 2: Obtener elemento para info adicional (geometría, refuerzo)
        # =====================================================================
        element, forces, error = self.get_element_and_forces(
            session_id, element_key, element_type
        )
        if error:
            return error

        # =====================================================================
        # PASO 3: Construir resultado extrayendo del cache
        # =====================================================================
        result = {
            'success': True,
            'element_type': cached.get('element_type', element_type),
            'element_info': self._format_element_info(element, element_type, is_strut=is_strut),
            'reinforcement': self._format_reinforcement(element, element_type, is_strut=is_strut),
        }

        # Capacidades: extraer del cache
        result['capacities'] = self._extract_capacities_from_cache(cached)

        # Esbeltez: extraer del cache si existe
        result['slenderness'] = cached.get('slenderness')

        # Flexión: extraer del cache (mismo DCR que la tabla)
        result['flexure_design'] = self._extract_flexure_from_cache(cached)

        # Cortante: extraer del cache
        result['shear_design'] = self._extract_shear_from_cache(cached)

        # Boundary: extraer del cache si existe
        result['boundary_check'] = cached.get('boundary_element')

        # Lista de combinaciones: simplificada desde fuerzas
        if forces and forces.combinations:
            result['combinations_list'] = self._get_combinations_list_from_cache(
                forces, cached
            )
        else:
            result['combinations_list'] = []

        # Configuración de display
        result['display_config'] = self._get_display_config(
            cached.get('element_type', element_type),
            is_strut=is_strut
        )

        return result

    def _get_display_config(self, element_type: str, is_strut: bool = False) -> Dict[str, bool]:
        """
        Retorna configuración de visibilidad de secciones del modal.

        Centraliza la lógica de qué secciones mostrar según el tipo de elemento,
        evitando duplicar esta lógica en el frontend.
        """
        return {
            # Esbeltez: pier y column, pero NO struts (sin confinamiento)
            'show_slenderness': element_type in ('pier', 'column') and not is_strut,
            # Elementos de borde: pier y drop_beam (ACI 318-25 §18.10.6)
            'show_boundary_check': element_type in ('pier', 'drop_beam'),
            # Capacidades puras P-M: todos excepto beams sin carga axial
            'show_pure_capacities': element_type != 'beam',
            # Vigas de acoplamiento: solo pier
            'show_coupling_beams': element_type == 'pier',
            # Detallado sísmico: todos los elementos
            'show_seismic_detailing': True,
            # Armadura de refuerzo: todos
            'show_reinforcement': True,
            # Warning de strut (modelo simplificado Cap. 23)
            'show_strut_warning': is_strut,
        }

    def _format_element_info(
        self,
        element,
        element_type: str,
        is_strut: bool = False
    ) -> Dict[str, Any]:
        """Formatea información general del elemento según su tipo."""
        info = {
            'label': element.label,
            'story': element.story,
            'fc_MPa': element.fc,
            'fy_MPa': element.fy,
        }

        # Struts: usar la geometría del elemento original (pier o column)
        if is_strut:
            # Determinar dimensiones según tipo de elemento subyacente
            if hasattr(element, 'depth') and hasattr(element, 'width'):
                # Column-based strut
                width_m = element.width / 1000
                thickness_m = element.depth / 1000
                height_m = element.height / 1000
            elif hasattr(element, 'thickness'):
                # Pier-based strut
                width_m = element.width / 1000
                thickness_m = element.thickness / 1000
                height_m = element.height / 1000
            else:
                # Fallback
                import math
                side = math.sqrt(element.Ag) / 1000
                width_m = thickness_m = side
                height_m = 0

            info.update({
                'width_m': round(width_m, 3),
                'thickness_m': round(thickness_m, 3),
                'height_m': round(height_m, 2),
                'Ag_m2': round(element.Ag / 1e6, 4),
                'is_strut': True,
                'note': 'Elemento pequeno verificado como strut (ACI 318-25 Cap. 23)'
            })
        elif element_type == 'pier':
            info.update({
                'width_m': round(element.width / 1000, 3),
                'thickness_m': round(element.thickness / 1000, 3),
                'height_m': round(element.height / 1000, 2),
                'Ag_m2': round((element.width / 1000) * (element.thickness / 1000), 4),
                'lambda': getattr(element, 'lambda_factor', 1.0)
            })
        elif element_type == 'column':
            info.update({
                'depth_m': round(element.depth / 1000, 3),
                'width_m': round(element.width / 1000, 3),
                'height_m': round(element.height / 1000, 2),
                'Ag_m2': round(element.Ag / 1e6, 4),
                'shape': getattr(element, 'shape', 'rectangular')
            })
        elif element_type in ('beam', 'drop_beam'):
            info.update({
                'depth_m': round(element.depth / 1000, 3),
                'width_m': round(element.width / 1000, 3),
                'length_m': round(element.length / 1000, 2),
                'Ag_m2': round(element.Ag / 1e6, 4),
                'is_spandrel': getattr(element, 'is_spandrel', False)
            })

        return info

    def _format_reinforcement(
        self,
        element,
        element_type: str,
        is_strut: bool = False
    ) -> Dict[str, Any]:
        """Formatea información de armadura según tipo de elemento."""
        # Struts: refuerzo simplificado (1 barra como acero constructivo)
        if is_strut:
            import math
            # Obtener diámetro de la barra central
            if hasattr(element, 'diameter_long'):
                diameter = element.diameter_long
            elif hasattr(element, 'diameter_v'):
                diameter = element.diameter_v
            else:
                diameter = 12  # Default

            As_bar = math.pi * (diameter / 2) ** 2

            return {
                'type': 'strut_unconfined',
                'n_total_bars': 1,
                'diameter_long': diameter,
                'As_long_mm2': round(As_bar, 1),
                'stirrup_spacing': 0,  # Sin estribos
                'note': 'Barra central como acero constructivo (no As de compresion)',
                'description': f'1phi{diameter} (strut sin confinamiento)'
            }

        if element_type == 'pier':
            # Malla + borde
            reinf_check = self._seismic_reinf_service.check_minimum_reinforcement(element)
            return {
                'type': 'mesh_edge',
                'n_meshes': element.n_meshes,
                'diameter_v': element.diameter_v,
                'spacing_v': element.spacing_v,
                'diameter_h': element.diameter_h,
                'spacing_h': element.spacing_h,
                'diameter_edge': element.diameter_edge,
                'n_edge_bars': element.n_edge_bars,
                'As_vertical_mm2': round(element.As_vertical, 1),
                'As_edge_mm2': round(element.As_edge_total, 1),
                'As_flexure_total_mm2': round(element.As_flexure_total, 1),
                'rho_vertical': round(element.rho_vertical, 5),
                'rho_horizontal': round(element.rho_horizontal, 5),
                'rho_mesh_vertical': round(reinf_check.rho_mesh_v_actual, 5),
                'rho_min': reinf_check.rho_v_min,
                'max_spacing': reinf_check.max_spacing,
                'rho_v_ok': reinf_check.rho_v_ok,
                'rho_h_ok': reinf_check.rho_h_ok,
                'rho_mesh_v_ok': reinf_check.rho_mesh_v_ok,
                'spacing_v_ok': reinf_check.spacing_v_ok,
                'spacing_h_ok': reinf_check.spacing_h_ok,
                'warnings': reinf_check.warnings,
                'description': element.reinforcement_description
            }

        elif element_type == 'column':
            # Barras longitudinales + estribos
            return {
                'type': 'bars_stirrups',
                'n_bars_depth': element.n_bars_depth,
                'n_bars_width': element.n_bars_width,
                'diameter_long': element.diameter_long,
                'stirrup_diameter': element.stirrup_diameter,
                'stirrup_spacing': element.stirrup_spacing,
                'As_long_mm2': round(element.As_flexure_total, 1),
                'rho_long': round(element.rho_longitudinal, 5),
                'description': element.reinforcement_description
            }

        elif element_type == 'beam':
            # Barras top/bottom + estribos
            return {
                'type': 'bars_top_bottom',
                'n_bars_top': element.n_bars_top,
                'diameter_top': element.diameter_top,
                'n_bars_bottom': element.n_bars_bottom,
                'diameter_bottom': element.diameter_bottom,
                'stirrup_diameter': element.stirrup_diameter,
                'stirrup_spacing': element.stirrup_spacing,
                'n_stirrup_legs': element.n_stirrup_legs,
                'As_top_mm2': round(element.As_top, 1),
                'As_bottom_mm2': round(element.As_bottom, 1),
                'As_total_mm2': round(element.As_flexure_total, 1),
                'description': element.reinforcement_description
            }

        elif element_type == 'drop_beam':
            # Malla + borde (similar a pier)
            return {
                'type': 'mesh_edge',
                'n_meshes': getattr(element, 'n_meshes', 2),
                'diameter_v': getattr(element, 'diameter_v', 12),
                'spacing_v': getattr(element, 'spacing_v', 200),
                'diameter_h': getattr(element, 'diameter_h', 10),
                'spacing_h': getattr(element, 'spacing_h', 200),
                'diameter_edge': getattr(element, 'diameter_edge', 16),
                'n_edge_bars': getattr(element, 'n_edge_bars', 4),
                'stirrup_diameter': getattr(element, 'stirrup_diameter', 10),
                'stirrup_spacing': getattr(element, 'stirrup_spacing', 150),
                'As_flexure_total_mm2': round(element.As_flexure_total, 1),
                'description': getattr(element, 'reinforcement_description', '')
            }

        return {'type': 'unknown'}

    # =========================================================================
    # Métodos de Extracción del Cache (sin recálculos)
    # =========================================================================

    def _extract_flexure_from_cache(self, cached: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae datos de flexión del cache sin transformación.

        El cache ya tiene los datos correctos calculados durante el análisis.
        Esto garantiza que el modal muestre el mismo DCR que la tabla.
        """
        flexure = cached.get('flexure', {})
        if not flexure:
            return {'has_data': False, 'rows': []}

        is_strut = cached.get('element_type') == 'strut'

        # DCR viene del cache (mismo que la tabla)
        dcr = flexure.get('dcr', cached.get('dcr_max', 0))

        # Momento: el cache usa 'Mu' singular para todos los tipos
        Mu = flexure.get('Mu', 0)

        # Capacidad: depende del tipo
        if is_strut:
            phi_Mn = flexure.get('phi_Mn_0', flexure.get('phi_Mcr', 0))
        else:
            phi_Mn = flexure.get('phi_Mn_at_Pu', flexure.get('phi_Mn_0', 0))

        row = {
            'location': 'Critical',
            'combo': flexure.get('critical_combo', cached.get('critical_combo', 'Envolvente')),
            'Pu_tonf': flexure.get('Pu', 0),
            'Mu2_tonf_m': 0,  # Simplificado: solo eje principal
            'Mu3_tonf_m': Mu,
            'phi_Mn_tonf_m': phi_Mn,
            'c_mm': flexure.get('c', '—'),
            'dcr': dcr,
        }

        return {
            'has_data': True,
            'rows': [row],
            'is_strut': is_strut,
            'has_tension': flexure.get('has_tension', False),
            'tension_combos': flexure.get('tension_combos', 0),
            'warnings': flexure.get('warnings', cached.get('warnings', [])),
            # Resultados de TODAS las combinaciones (para modal sin recálculo)
            'combo_results': flexure.get('combo_results', []),
        }

    def _extract_shear_from_cache(self, cached: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae datos de cortante del cache y los formatea para el modal.

        El cache tiene formato plano (Vu_2, Vu_3, phi_Vn_2, etc.)
        El frontend espera filas por dirección con campos específicos.
        """
        shear = cached.get('shear', {})
        if not shear:
            return {'has_data': False, 'rows': []}

        # Extraer datos del cache
        Vu_2 = shear.get('Vu_2', 0) or 0
        Vu_3 = shear.get('Vu_3', 0) or 0
        phi_Vn_2 = shear.get('phi_Vn_2', 0) or 0
        phi_Vn_3 = shear.get('phi_Vn_3', 0) or 0
        Vc = shear.get('Vc', 0) or 0
        phi_v = shear.get('phi_v', 0.60)
        phi_Vc = round(Vc * phi_v, 2)

        dcr_2 = shear.get('dcr_2', 0) or 0
        dcr_3 = shear.get('dcr_3', 0) or 0
        combo = shear.get('critical_combo', 'Envolvente')

        # Obtener Pu y Mu del análisis de flexión para contexto
        flexure = cached.get('flexure', {})
        Pu = flexure.get('Pu', 0) or 0
        Mu = flexure.get('Mu', 0) or 0

        rows = []

        # Fila para Dir 2 (solo si hay demanda)
        if Vu_2 > 0 or phi_Vn_2 > 0:
            rows.append({
                'direction': 'Dir 2',
                'dcr': round(dcr_2, 2),
                'combo': combo,
                'Pu_tonf': round(Pu, 2),
                'Mu_tonf_m': round(Mu, 2),
                'Vu_tonf': round(Vu_2, 2),
                'phi_Vc_tonf': phi_Vc,
                'phi_Vn_tonf': round(phi_Vn_2, 2),
            })

        # Fila para Dir 3 (solo si hay demanda)
        if Vu_3 > 0 or phi_Vn_3 > 0:
            rows.append({
                'direction': 'Dir 3',
                'dcr': round(dcr_3, 2),
                'combo': combo,
                'Pu_tonf': round(Pu, 2),
                'Mu_tonf_m': round(Mu, 2),
                'Vu_tonf': round(Vu_3, 2),
                'phi_Vc_tonf': phi_Vc,
                'phi_Vn_tonf': round(phi_Vn_3, 2),
            })

        # Si no hay filas, crear una fila vacía para indicar sin demanda
        if not rows:
            rows.append({
                'direction': 'N/A',
                'dcr': 0,
                'combo': '—',
                'Pu_tonf': 0,
                'Mu_tonf_m': 0,
                'Vu_tonf': 0,
                'phi_Vc_tonf': phi_Vc,
                'phi_Vn_tonf': max(phi_Vn_2, phi_Vn_3),
            })

        return {
            'has_data': True,
            'rows': rows,
            'phi_v': phi_v,
            'warnings': shear.get('warnings', []),
        }

    def _extract_capacities_from_cache(self, cached: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrae capacidades del cache."""
        flexure = cached.get('flexure', {})
        shear = cached.get('shear', {})

        if not flexure and not shear:
            return None

        return {
            'phi_Pn_max_tonf': flexure.get('phi_Pn_max', flexure.get('phi_Fns', 0)),
            'phi_Mn3_tonf_m': flexure.get('phi_Mn_at_Pu', flexure.get('phi_Mn_0', 0)),
            'phi_Mn2_tonf_m': flexure.get('phi_Mn_at_Pu', flexure.get('phi_Mn_0', 0)),
            'phi_Vn2_tonf': shear.get('phi_Vn_2', 0),
            'phi_Vn3_tonf': shear.get('phi_Vn_3', 0),
        }

    def _get_combinations_list_from_cache(
        self,
        forces,
        cached: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Genera lista de combinaciones con datos del cache.

        Incluye fuerzas y flags de combinación crítica para el frontend.
        El frontend espera campos P, M2, M3, V2, V3 (sin sufijos).
        """
        if not forces or not forces.combinations:
            return []

        # Obtener combinación crítica del cache
        flexure = cached.get('flexure', {})
        shear = cached.get('shear', {})
        critical_flexure = flexure.get('critical_combo', '')
        critical_shear = shear.get('critical_combo', '')

        seen_combos: Dict[str, int] = {}
        combos_list = []

        for i, combo in enumerate(forces.combinations):
            combo_name = combo.name
            full_name = f"{combo_name} ({combo.location})"

            # Evitar duplicados
            if full_name in seen_combos:
                continue
            seen_combos[full_name] = i

            is_critical_flexure = full_name == critical_flexure
            is_critical_shear = full_name == critical_shear

            combos_list.append({
                'index': i,
                'name': combo_name,
                'location': combo.location,
                'full_name': full_name,
                # Frontend espera P, M2, M3, V2, V3 (sin sufijos)
                'P': round(combo.P, 2),
                'M2': round(combo.M2, 2),
                'M3': round(combo.M3, 2),
                'V2': round(combo.V2, 2),
                'V3': round(combo.V3, 2),
                'is_critical_flexure': is_critical_flexure,
                'is_critical_shear': is_critical_shear,
                'is_critical': is_critical_flexure or is_critical_shear
            })

        # Ordenar: críticas primero
        combos_list.sort(key=lambda x: (
            not x['is_critical'],
            not x['is_critical_flexure'],
            x['name']
        ))

        return combos_list


