# app/services/analysis/element_details_service.py
"""
Servicio unificado de detalles de elementos estructurales.

Prepara datos estructurados para el modal de detalles,
incluyendo capacidades, verificaciones y tablas estilo ETABS.

ELEMENTOS SOPORTADOS:
- pier: Verificación completa con boundary elements
- column: Verificación de flexocompresión biaxial
- beam: Verificación de flexión y cortante
- drop_beam: Verificación con boundary elements

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
from ...domain.constants.shear import PHI_SHEAR_SEISMIC
from ...domain.chapter18.boundary_elements import (
    calculate_boundary_stress as _calculate_boundary_stress,
    BoundaryStressAnalysis,
)
from ...domain.shear.concrete_shear import calculate_Vc_beam, calculate_Vc_column
from ...domain.shear.steel_shear import calculate_Vs_beam_column

from ..presentation.plot_generator import PlotGenerator
from .flexocompression_service import FlexocompressionService
from .shear_service import ShearService
from ...domain.flexure import SlendernessService
from ...domain.chapter18.reinforcement import SeismicReinforcementService
from ...domain.entities import Pier

if TYPE_CHECKING:
    from .element_orchestrator import ElementOrchestrator


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
            pier: Pier original
            config: Configuración propuesta

        Returns:
            Copia del pier con los cambios aplicados
        """
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

        IMPORTANTE: Esta función usa el cache del análisis inicial para evitar
        recálculos. Para combinaciones no críticas, delega a los servicios
        centralizados con la convención de signos correcta.

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier
            combo_index: Índice de la combinación

        Returns:
            Dict con datos de flexión, corte y boundary para esa combinación
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        if not pier_forces or not pier_forces.combinations:
            return {'success': False, 'error': 'No hay combinaciones de carga'}

        if combo_index < 0 or combo_index >= len(pier_forces.combinations):
            return {'success': False, 'error': 'Índice de combinación inválido'}

        combo = pier_forces.combinations[combo_index]
        combo_full_name = f"{combo.name} ({combo.location})"

        # Intentar obtener resultado del cache (calculado durante análisis inicial)
        cached_result = self._session_manager.get_analysis_result(session_id, pier_key)

        # Verificar si esta combinación es la crítica (ya calculada en el cache)
        is_critical_flexure = False
        is_critical_shear = False

        if cached_result:
            cached_flexure = cached_result.get('flexure', {})
            cached_shear = cached_result.get('shear', {})

            # Verificar si el combo actual es el crítico de flexión
            critical_flex_combo = cached_flexure.get('critical_combo', '')
            if combo_full_name == critical_flex_combo or combo.name == critical_flex_combo:
                is_critical_flexure = True

            # Verificar si el combo actual es el crítico de cortante
            critical_shear_combo = cached_shear.get('critical_combo', '')
            if combo_full_name == critical_shear_combo or combo.name == critical_shear_combo:
                is_critical_shear = True

        # Obtener datos de flexión
        if is_critical_flexure and cached_result:
            # Usar datos del cache (ya calculados correctamente)
            flexure_data = self._build_flexure_from_cache(cached_result, combo)
        else:
            # Calcular usando servicio centralizado (con convención de signos correcta)
            flexure_data = self._calc_flexure_for_combo(pier, combo)

        # Obtener datos de cortante
        if is_critical_shear and cached_result:
            # Usar datos del cache
            shear_data = self._build_shear_from_cache(cached_result, combo)
        else:
            # Calcular usando servicio centralizado
            shear_data = self._calc_shear_for_combo(pier, combo)

        # Calcular datos de boundary (siempre recalcular para la combo específica)
        boundary_data = self._calc_boundary_for_combo(pier, combo)

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

    def _calc_flexure_for_combo(self, pier, combo) -> Dict[str, Any]:
        """
        Calcula datos de flexión para una combinación específica.

        Usa método ray-casting consistente con check_flexure() para
        garantizar que DCR y φMn sean coherentes entre tabla y modal.

        IMPORTANTE: Convención de signos:
        - ETABS: P negativo = compresión
        - FlexureChecker: P positivo = compresión
        - Por eso usamos -combo.P
        """
        from ...domain.flexure import FlexureChecker

        # CORREGIDO: Convertir a convención positivo = compresión
        Pu = -combo.P  # ETABS: negativo = compresión → positivo para cálculo
        M2 = combo.M2
        M3 = combo.M3
        Mu = max(abs(M2), abs(M3))

        # Generar curva de interacción
        interaction_points, _ = self._flexo_service.generate_interaction_curve(
            pier, direction='primary', apply_slenderness=False, k=0.8
        )

        # Calcular SF usando ray-casting (consistente con check_flexure)
        sf, _ = FlexureChecker.calculate_safety_factor(interaction_points, Pu, Mu)

        # DCR = 1/SF (consistente con método ray-casting)
        dcr = 1 / sf if sf > 0 and sf < float('inf') else 0

        # φMn "efectivo" del ray-casting = Mu × SF
        # Esto garantiza consistencia: DCR = Mu / φMn = Mu / (Mu × SF) = 1/SF
        if sf > 0 and sf < float('inf') and Mu > 0:
            phi_Mn_at_Pu = Mu * sf
        else:
            # Fallback para casos sin demanda
            phi_Mn_at_Pu = self._flexo_service.get_phi_Mn_at_Pu(interaction_points, Pu)

        # Calcular c (también con Pu convertido)
        c_mm = self._calculate_neutral_axis_depth(pier, Pu, Mu)

        return {
            'location': combo.location,
            'Pu_tonf': round(combo.P, 2),  # Mostrar P original de ETABS para display
            'Mu2_tonf_m': round(M2, 2),
            'Mu3_tonf_m': round(M3, 2),
            'phi_Mn_tonf_m': round(phi_Mn_at_Pu, 2),
            'c_mm': round(c_mm, 0) if c_mm else '—',
            'dcr': round(dcr, 3) if dcr >= 0.01 else '<0.01'
        }

    def _calc_shear_for_combo(self, pier, combo) -> Dict[str, Any]:
        """
        Calcula datos de corte para una combinación específica.

        IMPORTANTE: Convención de signos:
        - ETABS: P negativo = compresión
        - ShearService.get_shear_capacity: Nu positivo = compresión (en kN)
        - Por eso usamos -combo.P y convertimos a kN
        """
        # CORREGIDO: Convertir a convención positivo = compresión
        Pu = -combo.P  # ETABS: negativo = compresión → positivo para cálculo
        V2 = abs(combo.V2)
        V3 = abs(combo.V3)
        Mu = max(abs(combo.M2), abs(combo.M3))

        # Obtener capacidades de corte (Nu en kN, positivo = compresión)
        shear_cap = self._shear_service.get_shear_capacity(pier, Nu=Pu * 9.80665)

        phi_Vn_2 = shear_cap.get('phi_Vn_2', 0)
        phi_Vn_3 = shear_cap.get('phi_Vn_3', 0)
        Vc_2 = shear_cap.get('Vc_2', 0)
        Vc_3 = shear_cap.get('Vc_3', 0)
        phi_v = shear_cap.get('phi_v', PHI_SHEAR_SEISMIC)

        # Calcular D/C para cada dirección (phi ya incluido en phi_Vn_*)
        dcr_2 = V2 / phi_Vn_2 if phi_Vn_2 > 0 else 0
        dcr_3 = V3 / phi_Vn_3 if phi_Vn_3 > 0 else 0

        return {
            'phi_v': phi_v,  # Factor φv usado
            'rows': [
                {
                    'direction': 'V2',
                    'dcr': round(dcr_2, 3) if dcr_2 >= 0.01 else '<0.01',
                    'Pu_tonf': round(combo.P, 2),  # Mostrar P original de ETABS
                    'Mu_tonf_m': round(Mu, 2),
                    'Vu_tonf': round(V2, 2),
                    'phi_Vc_tonf': round(Vc_2 * phi_v, 2),
                    'phi_Vn_tonf': round(phi_Vn_2, 2)
                },
                {
                    'direction': 'V3',
                    'dcr': round(dcr_3, 3) if dcr_3 >= 0.01 else '<0.01',
                    'Pu_tonf': round(combo.P, 2),  # Mostrar P original de ETABS
                    'Mu_tonf_m': round(Mu, 2),
                    'Vu_tonf': round(V3, 2),
                    'phi_Vc_tonf': round(Vc_3 * phi_v, 2),
                    'phi_Vn_tonf': round(phi_Vn_3, 2)
                }
            ]
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
        Obtiene capacidades de cualquier tipo de elemento estructural.

        Método unificado que soporta pier, column, beam y drop_beam.
        Reutiliza la lógica existente con adaptaciones por tipo.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento (Story_Label)
            element_type: 'pier', 'column', 'beam', 'drop_beam'

        Returns:
            Dict con información completa del elemento estilo ETABS
        """
        # Obtener elemento y fuerzas usando método genérico de clase base
        element, forces, error = self.get_element_and_forces(
            session_id, element_key, element_type
        )
        if error:
            return error

        # Datos comunes a todos los elementos
        result = {
            'success': True,
            'element_type': element_type,
            'element_info': self._format_element_info(element, element_type),
            'reinforcement': self._format_reinforcement(element, element_type),
        }

        # Verificar si tiene carga axial alta (para beams)
        has_high_axial = self._has_high_axial(element, forces)

        # Obtener capacidades de cortante según tipo de elemento
        # beam y column usan funciones específicas, pier y drop_beam usan ShearService
        if element_type == 'beam':
            shear_capacities = self._get_beam_shear_capacities(element)
        elif element_type == 'column':
            shear_capacities = self._get_column_shear_capacities(element, Nu=0)
        else:  # pier, drop_beam
            shear_capacities = self._shear_service.get_shear_capacity(element, Nu=0)

        # Capacidades puras (P-M) - solo para elementos en flexocompresión
        if element_type != 'beam' or has_high_axial:
            flexure_capacities = self._flexo_service.get_capacities(
                element, pn_max_factor=0.80, k=0.8
            )

            result['capacities'] = {
                'phi_Pn_max_tonf': round(flexure_capacities['phi_Pn_max'], 1),
                'phi_Mn3_tonf_m': flexure_capacities['phi_Mn3'],
                'phi_Mn2_tonf_m': flexure_capacities['phi_Mn2'],
                'phi_Vn2_tonf': shear_capacities['phi_Vn_2'],
                'phi_Vn3_tonf': shear_capacities['phi_Vn_3']
            }
        else:
            result['capacities'] = None

        # Esbeltez: solo para pier, column, y beams con carga axial alta
        if element_type in ('pier', 'column') or (element_type == 'beam' and has_high_axial):
            slenderness = self._slenderness_service.analyze(element, k=0.8, braced=True)
            result['slenderness'] = {
                'lambda': round(slenderness.lambda_ratio, 1),
                'k': slenderness.k,
                'lu_m': round(slenderness.lu / 1000, 2),
                'r_mm': round(slenderness.r, 1),
                'is_slender': slenderness.is_slender,
                'limit': slenderness.lambda_limit,
                'Pc_kN': round(slenderness.Pc_kN, 1),
                'delta_ns': round(slenderness.delta_ns, 3),
                'magnification_pct': round(slenderness.magnification_pct, 1)
            }
        else:
            result['slenderness'] = None

        # Datos de diseño a flexión
        result['flexure_design'] = self._get_flexure_design_data_generic(
            element, forces, element_type
        )

        # Datos de diseño a cortante
        result['shear_design'] = self._get_shear_design_data_generic(
            element, forces, shear_capacities, element_type
        )

        # Boundary Element Check: solo para pier y drop_beam
        if element_type in ('pier', 'drop_beam'):
            result['boundary_check'] = self._get_boundary_check_data(element, forces)
        else:
            result['boundary_check'] = None

        # Lista de combinaciones
        if forces and forces.combinations:
            result['combinations_list'] = self._get_combinations_list_generic(
                element, forces, result.get('flexure_design', {}),
                result.get('shear_design', {}), element_type
            )
        else:
            result['combinations_list'] = []

        # Configuración de display para el frontend
        result['display_config'] = self._get_display_config(element_type)

        return result

    def _get_display_config(self, element_type: str) -> Dict[str, bool]:
        """
        Retorna configuración de visibilidad de secciones del modal.

        Centraliza la lógica de qué secciones mostrar según el tipo de elemento,
        evitando duplicar esta lógica en el frontend.
        """
        return {
            # Esbeltez: pier y column (drop_beam y beam no la tienen)
            'show_slenderness': element_type in ('pier', 'column'),
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
        }

    def _format_element_info(
        self,
        element,
        element_type: str
    ) -> Dict[str, Any]:
        """Formatea información general del elemento según su tipo."""
        info = {
            'label': element.label,
            'story': element.story,
            'fc_MPa': element.fc,
            'fy_MPa': element.fy,
        }

        if element_type == 'pier':
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
        element_type: str
    ) -> Dict[str, Any]:
        """Formatea información de armadura según tipo de elemento."""
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
                'rho_long': round(element.rho_long, 5),
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

    def _has_high_axial(self, element, forces) -> bool:
        """
        Determina si el elemento tiene carga axial alta.

        Para beams: Pu > Ag×f'c/10 (criterio ACI §18.6.4.6)
        """
        if not forces or not forces.combinations:
            return False

        # Encontrar máximo Pu (compresión)
        max_Pu = 0
        for combo in forces.combinations:
            # ETABS: P negativo = compresión
            Pu = abs(combo.P)
            if Pu > max_Pu:
                max_Pu = Pu

        # Calcular límite: Ag×f'c/10 (en tonf)
        Ag_mm2 = element.Ag
        fc_MPa = element.fc
        # Límite en N, convertir a tonf
        limit_N = Ag_mm2 * fc_MPa / 10
        limit_tonf = limit_N / 9806.65  # N to tonf

        return max_Pu > limit_tonf

    def _get_beam_shear_capacities(self, beam) -> Dict[str, Any]:
        """
        Calcula capacidades de cortante para vigas.

        Usa las funciones específicas de cortante para vigas (calculate_Vc_beam,
        calculate_Vs_beam_column) en lugar del ShearService que está diseñado
        para muros/piers.

        Args:
            beam: Entidad Beam con propiedades bw, d, fc, fy, Av, stirrup_spacing

        Returns:
            Dict con phi_Vn_2, phi_Vn_3, Vc, Vs (formato compatible con ShearService)
        """
        # Parámetros de la viga
        bw = beam.bw  # Ancho del alma
        d = beam.d    # Profundidad efectiva
        fc = beam.fc
        fyt = beam.fy  # Fluencia del estribo (asumimos igual a fy)
        Av = beam.Av   # Área transversal (n_legs × As_estribo)
        s = beam.stirrup_spacing
        lambda_factor = getattr(beam, 'lambda_factor', 1.0)

        # Calcular Vc usando función de vigas
        vc_result = calculate_Vc_beam(bw, d, fc, lambda_factor)
        Vc_N = vc_result.Vc_N

        # Calcular Vs usando función de vigas/columnas
        vs_result = calculate_Vs_beam_column(Av, d, s, fyt, bw, fc)
        Vs_N = vs_result.Vs_N

        # Capacidad total con φ = 0.75 (φ sísmica para vigas)
        phi_v = PHI_SHEAR_SEISMIC
        Vn_N = Vc_N + Vs_N
        phi_Vn_N = phi_v * Vn_N

        # Convertir a tonf (dividir N por 9806.65)
        N_TO_TONF = 1 / 9806.65
        Vc_tonf = Vc_N * N_TO_TONF
        Vs_tonf = Vs_N * N_TO_TONF
        phi_Vn_tonf = phi_Vn_N * N_TO_TONF

        # Para vigas, el cortante principal es V2 (en el plano de flexión)
        # V3 (fuera del plano) generalmente no aplica, usamos mismo valor
        return {
            'Vc_2': round(Vc_tonf, 2),
            'Vs_2': round(Vs_tonf, 2),
            'phi_Vn_2': round(phi_Vn_tonf, 2),
            'Vc_3': round(Vc_tonf, 2),  # Mismo valor (vigas son unidireccionales)
            'Vs_3': round(Vs_tonf, 2),
            'phi_Vn_3': round(phi_Vn_tonf, 2),
            'phi_v': phi_v,
        }

    def _get_column_shear_capacities(self, column, Nu: float = 0) -> Dict[str, Any]:
        """
        Calcula capacidades de cortante para columnas.

        Usa calculate_Vc_column y calculate_Vs_beam_column para ambas direcciones.

        Args:
            column: Entidad Column con propiedades depth, width, d_depth, d_width,
                   As_transversal_depth, As_transversal_width, stirrup_spacing
            Nu: Carga axial en Newtons (positivo = compresión)

        Returns:
            Dict con phi_Vn_2, phi_Vn_3, Vc, Vs para ambas direcciones
        """
        phi_v = PHI_SHEAR_SEISMIC
        N_TO_TONF = 1 / 9806.65

        # Dirección principal (eje 2) - cortante en dirección del ancho
        bw_2 = column.width
        d_2 = column.d_depth
        Av_2 = column.As_transversal_depth

        vc_2 = calculate_Vc_column(bw_2, d_2, column.fc, column.Ag, Nu)
        vs_2 = calculate_Vs_beam_column(Av_2, d_2, column.stirrup_spacing, column.fy, bw_2, column.fc)

        Vc_2_tonf = vc_2.Vc_N * N_TO_TONF
        Vs_2_tonf = vs_2.Vs_N * N_TO_TONF
        phi_Vn_2 = phi_v * (Vc_2_tonf + Vs_2_tonf)

        # Dirección secundaria (eje 3) - cortante en dirección de la profundidad
        bw_3 = column.depth
        d_3 = column.d_width
        Av_3 = column.As_transversal_width

        vc_3 = calculate_Vc_column(bw_3, d_3, column.fc, column.Ag, Nu)
        vs_3 = calculate_Vs_beam_column(Av_3, d_3, column.stirrup_spacing, column.fy, bw_3, column.fc)

        Vc_3_tonf = vc_3.Vc_N * N_TO_TONF
        Vs_3_tonf = vs_3.Vs_N * N_TO_TONF
        phi_Vn_3 = phi_v * (Vc_3_tonf + Vs_3_tonf)

        return {
            'Vc_2': round(Vc_2_tonf, 2),
            'Vs_2': round(Vs_2_tonf, 2),
            'phi_Vn_2': round(phi_Vn_2, 2),
            'Vc_3': round(Vc_3_tonf, 2),
            'Vs_3': round(Vs_3_tonf, 2),
            'phi_Vn_3': round(phi_Vn_3, 2),
            'phi_v': phi_v,
        }

    def _get_flexure_design_data_generic(
        self,
        element,
        forces,
        element_type: str
    ) -> Dict[str, Any]:
        """
        Obtiene datos de verificación de flexión para cualquier elemento.

        Reutiliza _get_flexure_design_data para piers, adapta para otros.
        """
        if not forces or not forces.combinations:
            return {'has_data': False, 'rows': []}

        # Verificar flexión
        flexure_result = self._flexo_service.check_flexure(
            element, forces, moment_axis='M3', direction='primary', k=0.8
        )

        critical_combo_name = flexure_result.get('critical_combo', 'N/A')
        Pu = flexure_result.get('Pu', 0)
        Mu = flexure_result.get('Mu', 0)
        phi_Mn_at_Pu = flexure_result.get('phi_Mn_at_Pu', 0)
        sf = flexure_result.get('sf', 0)

        # Buscar M2 y M3 separados
        M2_critical = 0
        M3_critical = 0
        critical_combo = self._find_critical_combination(forces, critical_combo_name)
        if critical_combo:
            M2_critical = critical_combo.M2
            M3_critical = critical_combo.M3

        # Calcular c (eje neutro)
        c_mm = None
        if element_type in ('pier', 'column') or self._has_high_axial(element, forces):
            c_mm = self._calculate_neutral_axis_depth(element, Pu, Mu)

        # DCR
        dcr = flexure_result.get('dcr', 1 / sf if sf > 0 else 0)

        # Cuantía (si aplica)
        rho_actual = None
        if hasattr(element, 'rho_vertical'):
            rho_actual = element.rho_vertical
        elif hasattr(element, 'rho_long'):
            rho_actual = element.rho_long

        row = {
            'location': 'Critical',
            'combo': critical_combo_name,
            'Pu_tonf': round(Pu, 2),
            'Mu2_tonf_m': round(M2_critical, 2),
            'Mu3_tonf_m': round(M3_critical, 2),
            'phi_Mn_tonf_m': round(phi_Mn_at_Pu, 2),
            'c_mm': round(c_mm, 0) if c_mm else '—',
            'dcr': round(dcr, 3) if dcr >= 0.01 else '<0.01'
        }

        if rho_actual is not None:
            row['rho_actual'] = round(rho_actual, 5)

        return {'has_data': True, 'rows': [row]}

    def _get_simple_shear_design_data(
        self,
        element,
        forces,
        shear_capacities: Dict[str, Any],
        element_type: str
    ) -> Dict[str, Any]:
        """
        Calcula datos de cortante para beam/column usando capacidades pre-calculadas.

        No usa ShearService (que está diseñado para muros/piers).
        Simplemente calcula D/C usando Vu de las combinaciones y phi_Vn ya calculado.
        """
        if not forces or not forces.combinations:
            return {'has_data': False, 'rows': []}

        phi_Vn_2 = shear_capacities.get('phi_Vn_2', 0)
        phi_Vn_3 = shear_capacities.get('phi_Vn_3', 0)
        Vc_2 = shear_capacities.get('Vc_2', 0)
        Vs_2 = shear_capacities.get('Vs_2', 0)
        phi_v = shear_capacities.get('phi_v', PHI_SHEAR_SEISMIC)

        # Encontrar combinación crítica
        critical_combo = None
        max_dcr = 0
        max_Vu_2 = 0
        max_Vu_3 = 0

        for combo in forces.combinations:
            V2 = abs(getattr(combo, 'V2', 0))
            V3 = abs(getattr(combo, 'V3', 0))

            dcr_2 = V2 / phi_Vn_2 if phi_Vn_2 > 0 else 0
            dcr_3 = V3 / phi_Vn_3 if phi_Vn_3 > 0 else 0
            dcr = max(dcr_2, dcr_3)

            if dcr > max_dcr:
                max_dcr = dcr
                critical_combo = combo
                max_Vu_2 = V2
                max_Vu_3 = V3

        if not critical_combo:
            return {'has_data': False, 'rows': []}

        critical_combo_display = f"{critical_combo.name}"
        if hasattr(critical_combo, 'location'):
            critical_combo_display = f"{critical_combo.name} ({critical_combo.location})"

        Pu_crit = abs(getattr(critical_combo, 'P', 0))
        Mu_crit = max(abs(getattr(critical_combo, 'M2', 0)), abs(getattr(critical_combo, 'M3', 0)))

        dcr_2 = max_Vu_2 / phi_Vn_2 if phi_Vn_2 > 0 else 0
        dcr_3 = max_Vu_3 / phi_Vn_3 if phi_Vn_3 > 0 else 0

        phi_Vc_2 = Vc_2 * phi_v
        phi_Vc_3 = shear_capacities.get('Vc_3', 0) * phi_v

        rows = []

        if max_Vu_2 > 0 or phi_Vn_2 > 0:
            rows.append({
                'direction': 'V2',
                'dcr': round(dcr_2, 3) if dcr_2 >= 0.01 else '<0.01',
                'combo': critical_combo_display,
                'Pu_tonf': round(Pu_crit, 2),
                'Mu_tonf_m': round(Mu_crit, 2),
                'Vu_tonf': round(max_Vu_2, 2),
                'phi_Vc_tonf': round(phi_Vc_2, 2),
                'phi_Vn_tonf': round(phi_Vn_2, 2)
            })

        # Para vigas, V3 generalmente no aplica (unidireccional)
        # Para columnas, sí incluir V3
        if element_type == 'column' and (max_Vu_3 > 0 or phi_Vn_3 > 0):
            rows.append({
                'direction': 'V3',
                'dcr': round(dcr_3, 3) if dcr_3 >= 0.01 else '<0.01',
                'combo': critical_combo_display,
                'Pu_tonf': round(Pu_crit, 2),
                'Mu_tonf_m': round(Mu_crit, 2),
                'Vu_tonf': round(max_Vu_3, 2),
                'phi_Vc_tonf': round(phi_Vc_3, 2),
                'phi_Vn_tonf': round(phi_Vn_3, 2)
            })

        return {
            'has_data': len(rows) > 0,
            'rows': rows,
            'critical_combo': critical_combo_display,
            'phi_v': phi_v
        }

    def _get_shear_design_data_generic(
        self,
        element,
        forces,
        shear_capacities: Dict[str, Any],
        element_type: str
    ) -> Dict[str, Any]:
        """
        Obtiene datos de verificación de cortante para cualquier elemento.

        Para pier y drop_beam: usa ShearService.check_shear() completo
        Para beam y column: usa _get_simple_shear_design_data() con capacidades pre-calculadas
        """
        if not forces or not forces.combinations:
            return {'has_data': False, 'rows': []}

        # Para beam y column: usar método simplificado que no depende de ShearService
        if element_type in ('beam', 'column'):
            return self._get_simple_shear_design_data(element, forces, shear_capacities, element_type)

        # Para pier y drop_beam: usar ShearService completo
        shear_result = self._shear_service.check_shear(element, forces)

        # Extraer datos
        Vc_2 = shear_result.get('Vc_2', 0)
        Vs_2 = shear_result.get('Vs_2', 0)
        phi_Vn_2 = shear_result.get('phi_Vn_2', shear_capacities.get('phi_Vn_2', 0))
        Vu_2 = shear_result.get('Vu_2', 0)
        dcr_2 = shear_result.get('dcr_2', 0)

        Vc_3 = shear_result.get('Vc_3', 0)
        Vs_3 = shear_result.get('Vs_3', 0)
        phi_Vn_3 = shear_result.get('phi_Vn_3', shear_capacities.get('phi_Vn_3', 0))
        Vu_3 = shear_result.get('Vu_3', 0)
        dcr_3 = shear_result.get('dcr_3', 0)

        critical_combo_name = shear_result.get('critical_combo', 'N/A')
        critical_combo_display = critical_combo_name

        Pu_crit = 0
        Mu_crit = 0
        found_combo = self._find_critical_combination(forces, critical_combo_name)
        if found_combo:
            Pu_crit = found_combo.P
            Mu_crit = max(abs(found_combo.M2), abs(found_combo.M3))
            critical_combo_display = f"{found_combo.name} ({found_combo.location})"

        phi_v = shear_result.get('phi_v', PHI_SHEAR_SEISMIC)
        phi_Vc_2 = Vc_2 * phi_v if Vc_2 else phi_Vn_2 - (Vs_2 * phi_v if Vs_2 else 0)
        phi_Vc_3 = Vc_3 * phi_v if Vc_3 else phi_Vn_3 - (Vs_3 * phi_v if Vs_3 else 0)

        rows = []

        if Vu_2 > 0 or phi_Vn_2 > 0:
            rows.append({
                'direction': 'V2',
                'dcr': round(dcr_2, 3) if dcr_2 >= 0.01 else '<0.01',
                'combo': critical_combo_display,
                'Pu_tonf': round(Pu_crit, 2),
                'Mu_tonf_m': round(Mu_crit, 2),
                'Vu_tonf': round(Vu_2, 2),
                'phi_Vc_tonf': round(phi_Vc_2, 2),
                'phi_Vn_tonf': round(phi_Vn_2, 2)
            })

        if Vu_3 > 0 or phi_Vn_3 > 0:
            rows.append({
                'direction': 'V3',
                'dcr': round(dcr_3, 3) if dcr_3 >= 0.01 else '<0.01',
                'combo': critical_combo_display,
                'Pu_tonf': round(Pu_crit, 2),
                'Mu_tonf_m': round(Mu_crit, 2),
                'Vu_tonf': round(Vu_3, 2),
                'phi_Vc_tonf': round(phi_Vc_3, 2),
                'phi_Vn_tonf': round(phi_Vn_3, 2)
            })

        return {
            'has_data': len(rows) > 0,
            'rows': rows,
            'critical_combo': critical_combo_display,
            'phi_v': phi_v
        }

    def _get_combinations_list_generic(
        self,
        element,
        forces,
        flexure_design: Dict[str, Any],
        shear_design: Dict[str, Any],
        element_type: str
    ) -> List[Dict[str, Any]]:
        """
        Genera lista de combinaciones para cualquier elemento.

        Reutiliza _get_combinations_list pero funciona con cualquier tipo.
        """
        if not forces or not forces.combinations:
            return []

        critical_flexure = ''
        critical_shear = ''

        if flexure_design.get('has_data') and flexure_design.get('rows'):
            critical_flexure = flexure_design['rows'][0].get('combo', '')

        if shear_design.get('has_data'):
            critical_shear = shear_design.get('critical_combo', '')

        seen_combos: Dict[str, int] = {}
        combinations = []

        for i, combo in enumerate(forces.combinations):
            combo_name = combo.name
            full_name = f"{combo_name} ({combo.location})"

            if full_name in seen_combos:
                continue
            seen_combos[full_name] = i

            is_critical_flexure = full_name == critical_flexure
            is_critical_shear = full_name == critical_shear

            combinations.append({
                'index': i,
                'name': combo_name,
                'location': combo.location,
                'full_name': full_name,
                'P': round(combo.P, 2),
                'M2': round(combo.M2, 2),
                'M3': round(combo.M3, 2),
                'V2': round(combo.V2, 2),
                'V3': round(combo.V3, 2),
                'is_critical_flexure': is_critical_flexure,
                'is_critical_shear': is_critical_shear,
                'is_critical': is_critical_flexure or is_critical_shear
            })

        combinations.sort(key=lambda x: (
            not x['is_critical'],
            not x['is_critical_flexure'],
            x['name']
        ))

        return combinations


