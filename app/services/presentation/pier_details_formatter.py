# app/services/presentation/pier_details_formatter.py
"""
Formateador de detalles de piers para UI.

Prepara datos estructurados para el modal de detalles de pier,
incluyendo capacidades, verificaciones y tablas estilo ETABS.
"""
from typing import Dict, Any, Optional, List, Tuple

from ..parsing.session_manager import SessionManager
from ...domain.constants.units import TONF_TO_N, TONFM_TO_NMM
from ...domain.constants.shear import PHI_SHEAR
from ...domain.chapter18.boundary_elements import (
    calculate_boundary_stress as _calculate_boundary_stress,
    BoundaryStressAnalysis,
)

from .plot_generator import PlotGenerator
from ..analysis.flexocompression_service import FlexocompressionService
from ..analysis.shear_service import ShearService
from ...domain.flexure import SlendernessService
from ...domain.chapter18.reinforcement import SeismicReinforcementService


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


class PierDetailsFormatter:
    """
    Servicio para cálculo de capacidades de piers.

    Calcula capacidades puras sin análisis de interacción,
    y genera diagramas de sección transversal.
    """

    def __init__(
        self,
        session_manager: SessionManager,
        flexocompression_service: Optional[FlexocompressionService] = None,
        shear_service: Optional[ShearService] = None,
        slenderness_service: Optional[SlendernessService] = None,
        plot_generator: Optional[PlotGenerator] = None
    ):
        """
        Inicializa el servicio de capacidades.

        Args:
            session_manager: Gestor de sesiones (requerido)
            flexocompression_service: Servicio de flexocompresión (opcional)
            shear_service: Servicio de corte (opcional)
            slenderness_service: Servicio de esbeltez (opcional)
            plot_generator: Generador de gráficos (opcional)
        """
        self._session_manager = session_manager
        self._flexo_service = flexocompression_service or FlexocompressionService()
        self._shear_service = shear_service or ShearService()
        self._slenderness_service = slenderness_service or SlendernessService()
        self._plot_generator = plot_generator or PlotGenerator()
        self._seismic_reinf_service = SeismicReinforcementService()

    # =========================================================================
    # Validación (delegada a SessionManager)
    # =========================================================================

    def _validate_pier(self, session_id: str, pier_key: str) -> Optional[Dict[str, Any]]:
        """Valida que el pier existe en la sesión."""
        return self._session_manager.validate_pier(session_id, pier_key)

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
        Calcula las capacidades del pier y datos de verificación estilo ETABS.

        Incluye:
        - Capacidades puras (sin interacción)
        - Verificación de flexión con combinaciones de carga
        - Verificación de corte con combinaciones de carga
        - Verificación de elementos de borde

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier (Story_Label)

        Returns:
            Diccionario con información completa del pier estilo ETABS
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        # Delegar cálculos de flexión a FlexocompressionService
        flexure_capacities = self._flexo_service.get_capacities(pier, pn_max_factor=0.80, k=0.8)

        # Delegar cálculos de corte a ShearService
        shear_capacities = self._shear_service.get_shear_capacity(pier, Nu=0)

        # Obtener datos detallados de esbeltez
        slenderness = self._slenderness_service.analyze(pier, k=0.8, braced=True)

        # Capacidad axial (sin reduccion por esbeltez - el efecto se aplica magnificando Mu)
        phi_Pn_max = flexure_capacities['phi_Pn_max']

        # Área gruesa
        Ag_m2 = (pier.width / 1000) * (pier.thickness / 1000)

        # Cuantía vertical y horizontal (usar propiedades de la entidad)
        rho_vertical = pier.rho_vertical
        rho_horizontal = pier.rho_horizontal

        # Obtener lambda del material (lightweight factor)
        lambda_factor = getattr(pier, 'lambda_factor', 1.0)

        # =================================================================
        # Verificación de cuantía mínima según ACI 318-25 §11.6.2 y §18.10.2.1
        # Delegado a SeismicReinforcementService
        # =================================================================
        reinf_check = self._seismic_reinf_service.check_minimum_reinforcement(pier)

        # =================================================================
        # Verificación de flexión con combinaciones de carga
        # =================================================================
        flexure_design = self._get_flexure_design_data(pier, pier_forces)

        # =================================================================
        # Verificación de corte con combinaciones de carga
        # =================================================================
        shear_design = self._get_shear_design_data(pier, pier_forces, shear_capacities)

        # =================================================================
        # Verificación de elementos de borde
        # =================================================================
        boundary_check = self._get_boundary_check_data(pier, pier_forces)

        # =================================================================
        # Lista de todas las combinaciones para el selector
        # =================================================================
        combinations_list = self._get_combinations_list(
            pier, pier_forces, flexure_design, shear_design
        )

        return {
            'success': True,
            # Sección 1: Pier Details
            'pier_info': {
                'label': pier.label,
                'story': pier.story,
                'width_m': round(pier.width / 1000, 3),
                'thickness_m': round(pier.thickness / 1000, 3),
                'height_m': round(pier.height / 1000, 2),
                'Ag_m2': round(Ag_m2, 4),
                'fc_MPa': pier.fc,
                'fy_MPa': pier.fy,
                'lambda': lambda_factor
            },
            # Sección 2: Reinforcement
            'reinforcement': {
                'n_meshes': pier.n_meshes,
                'diameter_v': pier.diameter_v,
                'spacing_v': pier.spacing_v,
                'diameter_h': pier.diameter_h,
                'spacing_h': pier.spacing_h,
                'diameter_edge': pier.diameter_edge,
                'n_edge_bars': pier.n_edge_bars,
                'As_vertical_mm2': round(pier.As_vertical, 1),
                'As_edge_mm2': round(pier.As_edge_total, 1),
                'As_flexure_total_mm2': round(pier.As_flexure_total, 1),
                'rho_vertical': round(rho_vertical, 5),
                'rho_horizontal': round(rho_horizontal, 5),
                'rho_mesh_vertical': round(reinf_check.rho_mesh_v_actual, 5),
                'rho_min': reinf_check.rho_v_min,
                'max_spacing': reinf_check.max_spacing,
                'rho_v_ok': reinf_check.rho_v_ok,
                'rho_h_ok': reinf_check.rho_h_ok,
                'rho_mesh_v_ok': reinf_check.rho_mesh_v_ok,
                'spacing_v_ok': reinf_check.spacing_v_ok,
                'spacing_h_ok': reinf_check.spacing_h_ok,
                'warnings': reinf_check.warnings,
                'description': pier.reinforcement_description
            },
            # Sección 3: Slenderness (ACI 318-25 §6.6.4)
            'slenderness': {
                'lambda': round(slenderness.lambda_ratio, 1),
                'k': slenderness.k,
                'lu_m': round(slenderness.lu / 1000, 2),
                'r_mm': round(slenderness.r, 1),
                'is_slender': slenderness.is_slender,
                'limit': slenderness.lambda_limit,
                'Pc_kN': round(slenderness.Pc_kN, 1),
                'delta_ns': round(slenderness.delta_ns, 3),
                'magnification_pct': round(slenderness.magnification_pct, 1)
            },
            # Sección 4: Pure Capacities
            # NOTA: phi_Pn_max no se reduce por esbeltez. El efecto de esbeltez
            # se aplica magnificando Mu segun ACI 318-25 §6.6.4: Mc = δns × Mu
            'capacities': {
                'phi_Pn_max_tonf': round(phi_Pn_max, 1),
                'phi_Mn3_tonf_m': flexure_capacities['phi_Mn3'],
                'phi_Mn2_tonf_m': flexure_capacities['phi_Mn2'],
                'phi_Vn2_tonf': shear_capacities['phi_Vn_2'],
                'phi_Vn3_tonf': shear_capacities['phi_Vn_3']
            },
            # Sección 5: Flexural Design (ETABS style)
            'flexure_design': flexure_design,
            # Sección 6: Shear Design (ETABS style)
            'shear_design': shear_design,
            # Sección 7: Boundary Element Check (ETABS style)
            'boundary_check': boundary_check,
            # Lista de combinaciones para selector
            'combinations_list': combinations_list
        }

    def _get_flexure_design_data(
        self,
        pier,
        pier_forces
    ) -> Dict[str, Any]:
        """
        Obtiene datos de verificación de flexión estilo ETABS.

        Returns:
            Dict con datos de flexión incluyendo c (eje neutro)
        """
        if not pier_forces or not pier_forces.combinations:
            return {
                'has_data': False,
                'rows': []
            }

        # Verificar flexión para obtener combinación crítica
        flexure_result = self._flexo_service.check_flexure(
            pier, pier_forces, moment_axis='M3', direction='primary', k=0.8
        )

        # Obtener M2 y M3 de la combinación crítica
        critical_combo_name = flexure_result.get('critical_combo', 'N/A')
        Pu = flexure_result.get('Pu', 0)
        Mu = flexure_result.get('Mu', 0)
        phi_Mn_at_Pu = flexure_result.get('phi_Mn_at_Pu', 0)
        sf = flexure_result.get('sf', 0)

        # Buscar la combinación crítica para obtener M2 y M3 separados
        M2_critical = 0
        M3_critical = 0
        for combo in pier_forces.combinations:
            combo_name = f"{combo.name} ({combo.location})"
            if combo_name == critical_combo_name or combo.name in critical_combo_name:
                M2_critical = combo.M2
                M3_critical = combo.M3
                break

        # Calcular c (profundidad del eje neutro) para el punto crítico
        c_mm = self._calculate_neutral_axis_depth(pier, Pu, Mu)

        # Cuantía actual (usar propiedad de la entidad)
        rho_actual = pier.rho_vertical

        # Calcular D/C (Demand/Capacity) = 1/SF = Mu/φMn
        dcr = 1 / sf if sf > 0 else 0

        return {
            'has_data': True,
            'rows': [{
                'location': 'Critical',
                'combo': critical_combo_name,
                'Pu_tonf': round(Pu, 2),
                'Mu2_tonf_m': round(M2_critical, 2),
                'Mu3_tonf_m': round(M3_critical, 2),
                'phi_Mn_tonf_m': round(phi_Mn_at_Pu, 2),
                'c_mm': round(c_mm, 0) if c_mm else '—',
                'rho_actual': round(rho_actual, 5),
                'dcr': round(dcr, 3) if dcr >= 0.01 else '<0.01'
            }]
        }

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
        except Exception:
            return None

    def _get_shear_design_data(
        self,
        pier,
        pier_forces,
        shear_capacities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Obtiene datos de verificación de corte estilo ETABS.

        Returns:
            Dict con datos de corte separados por V2 y V3
        """
        if not pier_forces or not pier_forces.combinations:
            return {
                'has_data': False,
                'rows': []
            }

        # Verificar corte
        shear_result = self._shear_service.check_shear(pier, pier_forces)

        # Extraer datos de V2
        Vc_2 = shear_result.get('Vc_2', 0)
        Vs_2 = shear_result.get('Vs_2', 0)
        phi_Vn_2 = shear_result.get('phi_Vn_2', shear_capacities.get('phi_Vn_2', 0))
        Vu_2 = shear_result.get('Vu_2', 0)
        dcr_2 = shear_result.get('dcr_2', 0)

        # Extraer datos de V3
        Vc_3 = shear_result.get('Vc_3', 0)
        Vs_3 = shear_result.get('Vs_3', 0)
        phi_Vn_3 = shear_result.get('phi_Vn_3', shear_capacities.get('phi_Vn_3', 0))
        Vu_3 = shear_result.get('Vu_3', 0)
        dcr_3 = shear_result.get('dcr_3', 0)

        # Combo crítico - buscar el nombre completo con ubicación
        critical_combo_name = shear_result.get('critical_combo', 'N/A')
        critical_combo = critical_combo_name  # Por defecto solo el nombre

        # Buscar Pu y Mu de la combinación crítica y construir nombre completo
        Pu_crit = 0
        Mu_crit = 0
        for combo in pier_forces.combinations:
            if combo.name == critical_combo_name:
                Pu_crit = combo.P
                Mu_crit = max(abs(combo.M2), abs(combo.M3))
                # Construir nombre completo con ubicación
                critical_combo = f"{combo.name} ({combo.location})"
                break

        # Obtener phi_v usado (§21.2.4.1: 0.60 para SPECIAL, 0.75 para otros)
        phi_v = shear_result.get('phi_v', PHI_SHEAR)

        # Calcular φVc usando el phi_v correcto
        phi_Vc_2 = Vc_2 * phi_v if Vc_2 else phi_Vn_2 - (Vs_2 * phi_v if Vs_2 else 0)
        phi_Vc_3 = Vc_3 * phi_v if Vc_3 else phi_Vn_3 - (Vs_3 * phi_v if Vs_3 else 0)

        rows = []

        # Fila V2
        if Vu_2 > 0 or phi_Vn_2 > 0:
            rows.append({
                'direction': 'V2',
                'dcr': round(dcr_2, 3) if dcr_2 >= 0.01 else '<0.01',
                'combo': critical_combo,
                'Pu_tonf': round(Pu_crit, 2),
                'Mu_tonf_m': round(Mu_crit, 2),
                'Vu_tonf': round(Vu_2, 2),
                'phi_Vc_tonf': round(phi_Vc_2, 2),
                'phi_Vn_tonf': round(phi_Vn_2, 2)
            })

        # Fila V3
        if Vu_3 > 0 or phi_Vn_3 > 0:
            rows.append({
                'direction': 'V3',
                'dcr': round(dcr_3, 3) if dcr_3 >= 0.01 else '<0.01',
                'combo': critical_combo,
                'Pu_tonf': round(Pu_crit, 2),
                'Mu_tonf_m': round(Mu_crit, 2),
                'Vu_tonf': round(Vu_3, 2),
                'phi_Vc_tonf': round(phi_Vc_3, 2),
                'phi_Vn_tonf': round(phi_Vn_3, 2)
            })

        return {
            'has_data': len(rows) > 0,
            'rows': rows,
            'critical_combo': critical_combo,
            'phi_v': phi_v  # Factor φv usado (0.60 SPECIAL, 0.75 otros)
        }

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

    def _get_combinations_list(
        self,
        pier,
        pier_forces,
        flexure_design: Dict[str, Any],
        shear_design: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Genera lista de todas las combinaciones con sus datos para el selector.

        Incluye información de cuál es la combinación crítica para flexión y corte.

        Args:
            pier: Pier
            pier_forces: Fuerzas del pier
            flexure_design: Resultado del análisis de flexión
            shear_design: Resultado del análisis de corte

        Returns:
            Lista de combinaciones con sus fuerzas y flags de crítica
        """
        if not pier_forces or not pier_forces.combinations:
            return []

        # Obtener nombres de combos críticos
        critical_flexure = ''
        critical_shear = ''

        if flexure_design.get('has_data') and flexure_design.get('rows'):
            critical_flexure = flexure_design['rows'][0].get('combo', '')

        if shear_design.get('has_data'):
            critical_shear = shear_design.get('critical_combo', '')

        # Usar dict para eliminar duplicados por full_name, manteniendo el primero
        seen_combos: Dict[str, int] = {}
        combinations = []

        for i, combo in enumerate(pier_forces.combinations):
            combo_name = combo.name
            full_name = f"{combo_name} ({combo.location})"

            # Saltar si ya vimos esta combinación (duplicado por step_type Max/Min)
            if full_name in seen_combos:
                continue
            seen_combos[full_name] = i

            # Comparar con el nombre completo para evitar marcar múltiples como críticas
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

        # Ordenar: críticos primero, luego por nombre
        combinations.sort(key=lambda x: (
            not x['is_critical'],
            not x['is_critical_flexure'],
            x['name']
        ))

        return combinations

    def get_combination_details(
        self,
        session_id: str,
        pier_key: str,
        combo_index: int
    ) -> Dict[str, Any]:
        """
        Calcula los detalles de diseño para una combinación específica.

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

        # Calcular datos de flexión para esta combinación
        flexure_data = self._calc_flexure_for_combo(pier, combo)

        # Calcular datos de corte para esta combinación
        shear_data = self._calc_shear_for_combo(pier, combo)

        # Calcular datos de boundary para esta combinación
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

    def _calc_flexure_for_combo(self, pier, combo) -> Dict[str, Any]:
        """Calcula datos de flexión para una combinación específica."""
        Pu = combo.P
        M2 = combo.M2
        M3 = combo.M3
        Mu = max(abs(M2), abs(M3))

        # Generar curva de interacción
        interaction_points, _ = self._flexo_service.generate_interaction_curve(
            pier, direction='primary', apply_slenderness=False, k=0.8
        )

        # Obtener φMn a este Pu
        phi_Mn_at_Pu = self._flexo_service.get_phi_Mn_at_Pu(interaction_points, Pu)

        # Calcular D/C (Demand/Capacity) = Mu/φMn
        dcr = Mu / phi_Mn_at_Pu if phi_Mn_at_Pu > 0 else 0

        # Calcular c
        c_mm = self._calculate_neutral_axis_depth(pier, Pu, Mu)

        return {
            'location': combo.location,
            'Pu_tonf': round(Pu, 2),
            'Mu2_tonf_m': round(M2, 2),
            'Mu3_tonf_m': round(M3, 2),
            'phi_Mn_tonf_m': round(phi_Mn_at_Pu, 2),
            'c_mm': round(c_mm, 0) if c_mm else '—',
            'dcr': round(dcr, 3) if dcr >= 0.01 else '<0.01'
        }

    def _calc_shear_for_combo(self, pier, combo) -> Dict[str, Any]:
        """Calcula datos de corte para una combinación específica."""
        Pu = combo.P
        V2 = abs(combo.V2)
        V3 = abs(combo.V3)
        Mu = max(abs(combo.M2), abs(combo.M3))

        # Obtener capacidades de corte
        shear_cap = self._shear_service.get_shear_capacity(pier, Nu=Pu * 9.80665)

        phi_Vn_2 = shear_cap.get('phi_Vn_2', 0)
        phi_Vn_3 = shear_cap.get('phi_Vn_3', 0)
        Vc_2 = shear_cap.get('Vc_2', 0)
        Vc_3 = shear_cap.get('Vc_3', 0)
        phi_v = shear_cap.get('phi_v', PHI_SHEAR)

        # Calcular D/C para cada dirección (phi ya incluido en phi_Vn_*)
        dcr_2 = V2 / phi_Vn_2 if phi_Vn_2 > 0 else 0
        dcr_3 = V3 / phi_Vn_3 if phi_Vn_3 > 0 else 0

        return {
            'phi_v': phi_v,  # Factor φv usado
            'rows': [
                {
                    'direction': 'V2',
                    'dcr': round(dcr_2, 3) if dcr_2 >= 0.01 else '<0.01',
                    'Pu_tonf': round(Pu, 2),
                    'Mu_tonf_m': round(Mu, 2),
                    'Vu_tonf': round(V2, 2),
                    'phi_Vc_tonf': round(Vc_2 * phi_v, 2),
                    'phi_Vn_tonf': round(phi_Vn_2, 2)
                },
                {
                    'direction': 'V3',
                    'dcr': round(dcr_3, 3) if dcr_3 >= 0.01 else '<0.01',
                    'Pu_tonf': round(Pu, 2),
                    'Mu_tonf_m': round(Mu, 2),
                    'Vu_tonf': round(V3, 2),
                    'phi_Vc_tonf': round(Vc_3 * phi_v, 2),
                    'phi_Vn_tonf': round(phi_Vn_3, 2)
                }
            ]
        }

    def _calc_boundary_for_combo(self, pier, combo) -> Dict[str, Any]:
        """Calcula datos de boundary element para una combinación específica."""
        Mu = max(abs(combo.M2), abs(combo.M3))
        stress = calculate_boundary_stress(pier, combo.P, Mu)

        c_left = self._calculate_neutral_axis_depth(pier, combo.P, Mu) if stress.required_left else None
        c_right = self._calculate_neutral_axis_depth(pier, combo.P, Mu) if stress.required_right else None

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
