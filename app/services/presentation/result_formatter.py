# app/services/presentation/result_formatter.py
"""
Formateador de resultados para conversión a formato UI.

Convierte resultados de ElementOrchestrator al formato unificado
que espera el frontend.

Métodos principales:
- format_any_element: Formatea cualquier elemento (Pier, Column, Beam, DropBeam)
- format_slab_result: Formatea resultados de losas (servicio separado)
"""
from typing import Dict, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..analysis.element_orchestrator import OrchestrationResult
    from ...domain.entities import Beam, Column, Pier, DropBeam
    from ...domain.calculations.wall_continuity import WallContinuityInfo


def get_status_css_class(status: str) -> str:
    """
    Retorna la clase CSS según el estado del resultado.

    Args:
        status: Estado del elemento ('OK', 'FAIL', etc.)

    Returns:
        Clase CSS para aplicar al elemento
    """
    return 'status-ok' if status == 'OK' else 'status-fail'


def get_dcr_css_class(dcr: float) -> str:
    """
    Retorna la clase CSS según el D/C ratio.

    Args:
        dcr: Demand/Capacity ratio

    Returns:
        Clase CSS para aplicar al valor
    """
    if dcr <= 0.67:  # Equivale a SF >= 1.5
        return 'fs-ok'
    elif dcr <= 1.0:  # Equivale a SF >= 1.0
        return 'fs-warn'
    return 'fs-fail'


class ResultFormatter:
    """
    Formatea resultados de análisis para la UI.

    Convierte OrchestrationResult al formato unificado que espera el frontend.

    Uso principal:
        result = orchestrator.verify(element, forces)
        formatted = ResultFormatter.format_any_element(element, result, key)
    """

    # =========================================================================
    # Formateo de continuidad de muros
    # =========================================================================

    @staticmethod
    def _format_wall_continuity(
        pier: 'Pier',
        continuity_info: 'WallContinuityInfo' = None
    ) -> Dict[str, Any]:
        """Formatea información de continuidad del muro."""
        # Si tenemos continuity_info, usarla
        if continuity_info:
            hwcs_m = continuity_info.hwcs / 1000  # mm -> m
            lw_m = pier.width / 1000  # mm -> m
            hwcs_lw = hwcs_m / lw_m if lw_m > 0 else 0
            return {
                'hwcs_m': round(hwcs_m, 2),
                'hwcs_lw': round(hwcs_lw, 2),
                'n_stories': continuity_info.n_stories,
                'is_continuous': continuity_info.is_continuous,
                'is_base': continuity_info.is_base,
                'stories_list': continuity_info.stories_list
            }

        # Fallback: calcular de la geometría del pier
        hwcs_m = pier.height / 1000  # mm -> m
        lw_m = pier.width / 1000  # mm -> m
        hwcs_lw = hwcs_m / lw_m if lw_m > 0 else 0
        return {
            'hwcs_m': round(hwcs_m, 2),
            'hwcs_lw': round(hwcs_lw, 2),
            'n_stories': 1,
            'is_continuous': False,
            'is_base': True,
            'stories_list': [pier.story]
        }

    # =========================================================================
    # Formateo de losas (servicio separado)
    # =========================================================================

    @staticmethod
    def format_slab_result(
        slab: Any,
        slab_result: Dict[str, Any],
        punching_result: Dict[str, Any],
        key: str
    ) -> Dict[str, Any]:
        """
        Convierte resultado de losa al formato para la tabla de losas.
        """
        return {
            'slab_key': key,
            'label': slab.label,
            'story': slab.story,
            'slab_type': slab.slab_type.value if hasattr(slab.slab_type, 'value') else str(slab.slab_type),
            'thickness': slab.thickness,
            'width': slab.width,
            'thickness_check': slab_result.get('thickness_check', {}),
            'flexure': slab_result.get('flexure', {}),
            'shear': slab_result.get('shear_one_way', {}),
            'reinforcement': slab_result.get('reinforcement', {}),
            'punching': punching_result,
            'overall_status': slab_result.get('overall_status', 'N/A')
        }

    # =========================================================================
    # Formateo de resultados de ElementOrchestrator (arquitectura unificada)
    # =========================================================================

    @staticmethod
    def format_orchestration_result(
        pier: 'Pier',
        result: 'OrchestrationResult',
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """
        Formatea resultado de OrchestrationResult al formato UI.

        Este método soporta la nueva arquitectura donde ElementOrchestrator
        clasifica automáticamente los elementos y delega al servicio apropiado.

        Args:
            pier: Entidad Pier
            result: OrchestrationResult del ElementOrchestrator
            key: Clave única del elemento
            continuity_info: Información de continuidad del muro
            pm_plot: Gráfico P-M en base64 (opcional)

        Returns:
            Dict con formato unificado para UI
        """
        domain_result = result.domain_result
        service_used = result.service_used

        # Determinar tipo de elemento para UI
        element_type = 'pier'
        if result.design_behavior.requires_column_checks:
            element_type = 'pier_column'  # Pier verificado como columna

        # Extraer datos según el servicio usado
        if service_used == 'wall':
            return ResultFormatter._format_wall_orchestration(
                pier, result, domain_result, key, continuity_info, pm_plot
            )
        elif service_used == 'column':
            return ResultFormatter._format_column_orchestration(
                pier, result, domain_result, key, continuity_info, pm_plot
            )
        else:
            # Fallback para flexure
            return ResultFormatter._format_flexure_orchestration(
                pier, result, domain_result, key, continuity_info, pm_plot
            )

    @staticmethod
    def _format_wall_orchestration(
        pier: 'Pier',
        result: 'OrchestrationResult',
        domain_result,
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de pier verificado como muro (§18.10)."""
        # Clasificación
        classification = None
        if hasattr(domain_result, 'classification') and domain_result.classification:
            cls = domain_result.classification
            classification = {
                'type': 'wall',
                'lw_tw': cls.lw_tw,
                'hw_lw': cls.hw_lw,
                'is_slender': cls.is_slender,
                'is_wall_pier': cls.is_wall_pier,
                'aci_section': result.design_behavior.aci_section
            }

        # Cortante
        shear_data = {
            'sf': 1.0 / result.dcr_max if result.dcr_max > 0 else 100.0,
            'status': 'OK' if result.is_ok else 'NO OK',
            'critical_combo': 'envelope',
            'dcr_2': result.dcr_max,
            'dcr_3': 0,
            'dcr_combined': result.dcr_max,
            'phi_Vn_2': 0,
            'phi_Vn_3': 0,
            'Vu_2': 0,
            'Vu_3': 0,
            'Vc': 0,
            'Vs': 0,
            'Ve': 0,
            'omega_v': None,
            'formula_type': 'wall'
        }

        if hasattr(domain_result, 'shear') and domain_result.shear:
            sh = domain_result.shear
            shear_data.update({
                'dcr_2': sh.dcr,
                'dcr_combined': sh.dcr,
                'phi_Vn_2': sh.phi_Vn,
                'Vu_2': sh.Ve,
                'Vc': sh.Vc,
                'Vs': sh.Vs,
                'Ve': sh.Ve,
            })
            if sh.dcr > 0:
                shear_data['sf'] = round(1.0 / sh.dcr, 2)

        # Elementos de borde
        boundary = None
        if hasattr(domain_result, 'boundary') and domain_result.boundary:
            be = domain_result.boundary
            boundary = {
                'required': be.requires_special,
                'method': 'stress' if be.requires_special else 'N/A',
                'sigma_max': 0,
                'sigma_limit': 0,
                'length_mm': 0,
                'status': 'OK' if be.is_ok else 'CHECK'
            }

        # Cuantías mínimas
        reinforcement_check = None
        if hasattr(domain_result, 'reinforcement') and domain_result.reinforcement:
            rf = domain_result.reinforcement
            reinforcement_check = {
                'rho_l_ok': rf.rho_l_ok,
                'rho_t_ok': rf.rho_t_ok,
                'is_ok': rf.is_ok
            }

        overall_status = 'OK' if result.is_ok else 'NO OK'
        flexure_dcr = result.dcr_max  # DCR de flexión directo

        return {
            'element_type': 'pier',
            'key': key,
            'pier_label': pier.label,
            'story': pier.story,
            'geometry': {
                'width_m': pier.width / 1000,
                'thickness_m': pier.thickness / 1000,
                'height_m': pier.height / 1000,
                'fc_MPa': pier.fc,
                'fy_MPa': pier.fy
            },
            'reinforcement': {
                'As_vertical_mm2': pier.As_vertical,
                'As_horizontal_mm2': pier.As_horizontal,
                'As_vertical_per_m': round(pier.As_vertical_per_m, 1),
                'As_horizontal_per_m': round(pier.As_horizontal, 1),
                'rho_vertical': round(pier.rho_vertical, 5),
                'rho_horizontal': round(pier.rho_horizontal, 5)
            },
            'flexure': {
                'sf': 1.0 / flexure_dcr if flexure_dcr > 0 else 100.0,
                'dcr': flexure_dcr,  # DCR directo para evitar cálculo en frontend
                'status': 'OK' if result.is_ok else 'NO OK',
                'critical_combo': 'envelope',
                'phi_Mn_at_Pu': 0,
                'Mu': 0,
                'phi_Mn_0': 0,
                'Pu': 0,
                'phi_Pn_max': 0,
                'exceeds_axial': False,
                'has_tension': False
            },
            'shear': shear_data,
            'slenderness': {
                'lambda': 0,
                'is_slender': False,
                'delta_ns': 1.0,
                'magnification_pct': 0.0
            },
            'classification': classification,
            'amplification': None,
            'boundary_element': boundary,
            'reinforcement_check': reinforcement_check,
            'overall_status': overall_status,
            'status_class': get_status_css_class(overall_status),
            'wall_continuity': ResultFormatter._format_wall_continuity(
                pier, continuity_info
            ),
            'design_proposal': {'has_proposal': False},
            'pm_plot': pm_plot,
            # Metadata de orquestación
            'design_behavior': result.design_behavior.name,
            'service_used': result.service_used,
            'aci_section': result.design_behavior.aci_section,
            'dcr_max': result.dcr_max,
            'critical_check': result.critical_check,
            'warnings': result.warnings
        }

    @staticmethod
    def _format_column_orchestration(
        pier: 'Pier',
        result: 'OrchestrationResult',
        domain_result,
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de pier verificado como columna (§18.7)."""
        # Extraer verificaciones dimensionales
        dimensional = None
        if hasattr(domain_result, 'dimensional_limits') and domain_result.dimensional_limits:
            dim = domain_result.dimensional_limits
            dimensional = {
                'min_dimension': dim.min_dimension,
                'min_dimension_ok': dim.min_dimension_ok,
                'aspect_ratio': dim.aspect_ratio,
                'aspect_ratio_ok': dim.aspect_ratio_ok,
                'is_ok': dim.is_ok
            }

        # Refuerzo longitudinal
        longitudinal = None
        if hasattr(domain_result, 'longitudinal') and domain_result.longitudinal:
            long = domain_result.longitudinal
            longitudinal = {
                'rho': long.rho,
                'rho_ok': long.rho_min_ok and long.rho_max_ok,
                'is_ok': long.is_ok
            }

        # Refuerzo transversal
        transverse = None
        if hasattr(domain_result, 'transverse') and domain_result.transverse:
            trans = domain_result.transverse
            transverse = {
                's_provided': trans.s_provided,
                's_max': trans.s_max,
                's_ok': trans.s_ok,
                'Ash_provided': trans.Ash_sbc_provided,
                'Ash_required': trans.Ash_sbc_required,
                'Ash_ok': trans.Ash_ok,
                'is_ok': trans.is_ok
            }

        # Cortante
        shear_data = {
            'sf': 1.0 / result.dcr_max if result.dcr_max > 0 else 100.0,
            'status': 'OK' if result.is_ok else 'NO OK',
            'critical_combo': 'envelope',
            'dcr_2': 0,
            'dcr_3': 0,
            'dcr_combined': result.dcr_max,
            'phi_Vn_2': 0,
            'phi_Vn_3': 0,
            'Vu_2': 0,
            'Vu_3': 0,
            'Vc': 0,
            'Vs': 0,
            'formula_type': 'column'
        }

        if hasattr(domain_result, 'shear') and domain_result.shear:
            sh = domain_result.shear
            shear_data.update({
                'dcr_2': sh.dcr,
                'dcr_combined': sh.dcr,
                'phi_Vn_2': sh.phi_Vn_V2,
                'Vu_2': sh.Ve,
                'Vc': sh.capacity_V2.Vc if sh.capacity_V2 else 0,
                'Vs': sh.capacity_V2.Vs if sh.capacity_V2 else 0,
            })
            if sh.dcr > 0:
                shear_data['sf'] = round(1.0 / sh.dcr, 2)

        overall_status = 'OK' if result.is_ok else 'NO OK'

        # Clasificación como pier-columna
        classification = {
            'type': 'wall_pier_column',
            'lw_tw': pier.width / pier.thickness if pier.thickness > 0 else 0,
            'hw_lw': pier.height / pier.width if pier.width > 0 else 0,
            'is_slender': False,
            'is_wall_pier': True,
            'aci_section': '§18.7'
        }

        return {
            'element_type': 'pier',  # Sigue siendo pier para la UI
            'key': key,
            'pier_label': pier.label,
            'story': pier.story,
            'geometry': {
                'width_m': pier.width / 1000,
                'thickness_m': pier.thickness / 1000,
                'height_m': pier.height / 1000,
                'fc_MPa': pier.fc,
                'fy_MPa': pier.fy
            },
            'reinforcement': {
                'As_vertical_mm2': pier.As_vertical,
                'As_horizontal_mm2': pier.As_horizontal,
                'As_vertical_per_m': round(pier.As_vertical_per_m, 1),
                'As_horizontal_per_m': round(pier.As_horizontal, 1),
                'rho_vertical': round(pier.rho_vertical, 5),
                'rho_horizontal': round(pier.rho_horizontal, 5)
            },
            'flexure': {
                'sf': 1.0 / result.dcr_max if result.dcr_max > 0 else 100.0,
                'dcr': result.dcr_max,  # DCR directo
                'status': 'OK' if result.is_ok else 'NO OK',
                'critical_combo': 'envelope',
                'phi_Mn_at_Pu': 0,
                'Mu': 0,
                'phi_Mn_0': 0,
                'Pu': 0,
                'phi_Pn_max': 0,
                'exceeds_axial': False,
                'has_tension': False
            },
            'shear': shear_data,
            'slenderness': {
                'lambda': 0,
                'is_slender': False,
                'delta_ns': 1.0,
                'magnification_pct': 0.0
            },
            'classification': classification,
            'amplification': None,
            'boundary_element': None,
            'seismic_column_checks': {
                'dimensional': dimensional,
                'longitudinal': longitudinal,
                'transverse': transverse,
            },
            'overall_status': overall_status,
            'status_class': get_status_css_class(overall_status),
            'wall_continuity': ResultFormatter._format_wall_continuity(
                pier, continuity_info
            ),
            'design_proposal': {'has_proposal': False},
            'pm_plot': pm_plot,
            # Metadata de orquestación
            'design_behavior': result.design_behavior.name,
            'service_used': result.service_used,
            'aci_section': result.design_behavior.aci_section,
            'dcr_max': result.dcr_max,
            'critical_check': result.critical_check,
            'warnings': result.warnings
        }

    @staticmethod
    def _format_flexure_orchestration(
        pier: 'Pier',
        result: 'OrchestrationResult',
        domain_result,
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de pier verificado por flexocompresión."""
        overall_status = 'OK' if result.is_ok else 'NO OK'

        return {
            'element_type': 'pier',
            'key': key,
            'pier_label': pier.label,
            'story': pier.story,
            'geometry': {
                'width_m': pier.width / 1000,
                'thickness_m': pier.thickness / 1000,
                'height_m': pier.height / 1000,
                'fc_MPa': pier.fc,
                'fy_MPa': pier.fy
            },
            'reinforcement': {
                'As_vertical_mm2': pier.As_vertical,
                'As_horizontal_mm2': pier.As_horizontal,
                'As_vertical_per_m': round(pier.As_vertical_per_m, 1),
                'As_horizontal_per_m': round(pier.As_horizontal, 1),
                'rho_vertical': round(pier.rho_vertical, 5),
                'rho_horizontal': round(pier.rho_horizontal, 5)
            },
            'flexure': {
                'sf': domain_result.get('SF', 0) if isinstance(domain_result, dict) else 0,
                'dcr': result.dcr_max,  # DCR directo
                'status': 'OK' if result.is_ok else 'NO OK',
                'critical_combo': 'envelope',
                'phi_Mn_at_Pu': 0,
                'Mu': 0,
                'phi_Mn_0': 0,
                'Pu': 0,
                'phi_Pn_max': 0,
                'exceeds_axial': False,
                'has_tension': False
            },
            'shear': {
                'sf': 100.0,
                'dcr': 0,  # DCR directo
                'status': 'N/A',
                'critical_combo': 'N/A',
                'dcr_2': 0,
                'dcr_3': 0,
                'dcr_combined': 0,
                'phi_Vn_2': 0,
                'phi_Vn_3': 0,
                'Vu_2': 0,
                'Vu_3': 0,
                'Vc': 0,
                'Vs': 0,
                'Ve': 0,
                'omega_v': None,
                'formula_type': 'flexure'
            },
            'slenderness': {
                'lambda': 0,
                'is_slender': False,
                'delta_ns': 1.0,
                'magnification_pct': 0.0
            },
            'classification': None,
            'amplification': None,
            'boundary_element': None,
            'overall_status': overall_status,
            'status_class': get_status_css_class(overall_status),
            'wall_continuity': ResultFormatter._format_wall_continuity(
                pier, continuity_info
            ),
            'design_proposal': {'has_proposal': False},
            'pm_plot': pm_plot,
            # Metadata de orquestación
            'design_behavior': result.design_behavior.name,
            'service_used': result.service_used,
            'aci_section': result.design_behavior.aci_section,
            'dcr_max': result.dcr_max,
            'critical_check': result.critical_check,
            'warnings': result.warnings
        }

    # =========================================================================
    # Método unificado para cualquier elemento (nueva arquitectura)
    # =========================================================================

    @staticmethod
    def format_any_element(
        element: Union['Beam', 'Column', 'Pier', 'DropBeam'],
        result: 'OrchestrationResult',
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """
        Formatea resultado de OrchestrationResult para CUALQUIER tipo de elemento.

        Este es el método principal para la nueva arquitectura unificada.
        Detecta el tipo de elemento y delega al formateador apropiado.

        Args:
            element: Beam, Column, Pier o DropBeam
            result: OrchestrationResult del ElementOrchestrator
            key: Clave única del elemento
            continuity_info: Información de continuidad (solo muros)
            pm_plot: Gráfico P-M en base64 (opcional)

        Returns:
            Dict con formato unificado para UI
        """
        from ...domain.entities import Pier, Column, Beam, DropBeam

        # Delegar según tipo de elemento
        if isinstance(element, Pier):
            return ResultFormatter.format_orchestration_result(
                element, result, key, continuity_info, pm_plot
            )
        elif isinstance(element, Column):
            return ResultFormatter._format_column_from_orchestration(
                element, result, key, pm_plot
            )
        elif isinstance(element, Beam):
            return ResultFormatter._format_beam_from_orchestration(
                element, result, key
            )
        elif isinstance(element, DropBeam):
            return ResultFormatter._format_drop_beam_from_orchestration(
                element, result, key, pm_plot
            )

        # Fallback genérico
        return {
            'element_type': 'unknown',
            'key': key,
            'overall_status': 'OK' if result.is_ok else 'NO OK',
            'dcr_max': result.dcr_max,
        }

    @staticmethod
    def _format_column_from_orchestration(
        column: 'Column',
        result: 'OrchestrationResult',
        key: str,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de Column desde OrchestrationResult."""
        domain_result = result.domain_result
        overall_status = 'OK' if result.is_ok else 'NO OK'

        # Cortante desde dominio
        shear_data = {
            'sf': 1.0 / result.dcr_max if result.dcr_max > 0 else 100.0,
            'status': 'OK' if result.is_ok else 'NO OK',
            'critical_combo': 'envelope',
            'dcr_2': result.dcr_max,
            'dcr_3': 0,
            'dcr_combined': result.dcr_max,
            'phi_Vn_2': 0, 'phi_Vn_3': 0,
            'Vu_2': 0, 'Vu_3': 0,
            'Vc': 0, 'Vs': 0,
            'formula_type': 'column'
        }

        if hasattr(domain_result, 'shear') and domain_result.shear:
            sh = domain_result.shear
            shear_data.update({
                'dcr_2': sh.dcr,
                'dcr_combined': sh.dcr,
                'phi_Vn_2': getattr(sh, 'phi_Vn_V2', 0),
                'Vu_2': getattr(sh, 'Ve', 0),
            })
            if sh.dcr > 0:
                shear_data['sf'] = round(1.0 / sh.dcr, 2)

        return {
            'element_type': 'column',
            'key': key,
            'pier_label': column.label,
            'story': column.story,
            'geometry': {
                'width_m': column.depth / 1000,
                'thickness_m': column.width / 1000,
                'height_m': column.height / 1000,
                'fc_MPa': column.fc,
                'fy_MPa': column.fy
            },
            'reinforcement': {
                'n_total_bars': column.n_total_bars,
                'n_bars_depth': column.n_bars_depth,
                'n_bars_width': column.n_bars_width,
                'diameter_long': column.diameter_long,
                'stirrup_diameter': column.stirrup_diameter,
                'stirrup_spacing': column.stirrup_spacing,
                'As_longitudinal_mm2': round(column.As_longitudinal, 0),
                'rho_longitudinal': round(column.rho_longitudinal, 4),
                'description': column.reinforcement_description
            },
            'flexure': {
                'sf': 1.0 / result.dcr_max if result.dcr_max > 0 else 100.0,
                'dcr': result.dcr_max,  # DCR directo
                'status': overall_status,
                'critical_combo': 'envelope',
                'phi_Mn_at_Pu': 0, 'Mu': 0, 'phi_Mn_0': 0,
                'Pu': 0, 'phi_Pn_max': 0,
                'exceeds_axial': False, 'has_tension': False
            },
            'shear': shear_data,
            'slenderness': {
                'lambda': 0, 'is_slender': False,
                'delta_ns': 1.0, 'magnification_pct': 0.0
            },
            'overall_status': overall_status,
            'status_class': get_status_css_class(overall_status),
            'wall_continuity': None,
            'design_proposal': {'has_proposal': False},
            'pm_plot': pm_plot,
            'design_behavior': result.design_behavior.name,
            'service_used': result.service_used,
            'aci_section': result.design_behavior.aci_section,
            'dcr_max': result.dcr_max,
            'critical_check': result.critical_check,
            'warnings': result.warnings
        }

    @staticmethod
    def _format_beam_from_orchestration(
        beam: 'Beam',
        result: 'OrchestrationResult',
        key: str
    ) -> Dict[str, Any]:
        """Formatea resultado de Beam desde OrchestrationResult."""
        overall_status = 'OK' if result.is_ok else 'NO OK'

        shear_data = {
            'sf': 1.0 / result.dcr_max if result.dcr_max > 0 else 100.0,
            'status': overall_status,
            'critical_combo': 'envelope',
            'dcr_2': result.dcr_max, 'dcr_3': 0, 'dcr_combined': result.dcr_max,
            'phi_Vn_2': 0, 'phi_Vn_3': 0,
            'Vu_2': 0, 'Vu_3': 0,
            'Vc': 0, 'Vs': 0,
            'formula_type': 'beam'
        }

        return {
            'element_type': 'beam',
            'key': key,
            'pier_label': beam.label,
            'story': beam.story,
            'geometry': {
                'width_m': beam.width / 1000,
                'thickness_m': beam.depth / 1000,
                'height_m': beam.length / 1000,
                'fc_MPa': beam.fc,
                'fy_MPa': beam.fy
            },
            'reinforcement': {
                'n_bars_top': beam.n_bars_top,
                'n_bars_bottom': beam.n_bars_bottom,
                'diameter_top': beam.diameter_top,
                'diameter_bottom': beam.diameter_bottom,
                'stirrup_diameter': beam.stirrup_diameter,
                'stirrup_spacing': beam.stirrup_spacing,
                'description': f"{beam.n_bars_top}phi{beam.diameter_top} + {beam.n_bars_bottom}phi{beam.diameter_bottom}"
            },
            'flexure': {
                'sf': 1.0 / result.dcr_max if result.dcr_max > 0 else 100.0,
                'dcr': result.dcr_max,  # DCR directo
                'status': overall_status,
                'critical_combo': 'envelope',
                'phi_Mn_at_Pu': 0, 'Mu': 0, 'phi_Mn_0': 0,
                'Pu': 0, 'phi_Pn_max': 0,
                'exceeds_axial': False, 'has_tension': False
            },
            'shear': shear_data,
            'slenderness': {
                'lambda': 0, 'is_slender': False,
                'delta_ns': 1.0, 'magnification_pct': 0.0
            },
            'overall_status': overall_status,
            'status_class': get_status_css_class(overall_status),
            'wall_continuity': None,
            'design_proposal': {'has_proposal': False},
            'pm_plot': None,
            'design_behavior': result.design_behavior.name,
            'service_used': result.service_used,
            'aci_section': result.design_behavior.aci_section,
            'dcr_max': result.dcr_max,
            'critical_check': result.critical_check,
            'warnings': result.warnings
        }

    @staticmethod
    def _format_drop_beam_from_orchestration(
        drop_beam: 'DropBeam',
        result: 'OrchestrationResult',
        key: str,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de DropBeam desde OrchestrationResult."""
        domain_result = result.domain_result
        overall_status = 'OK' if result.is_ok else 'NO OK'

        shear_data = {
            'sf': 1.0 / result.dcr_max if result.dcr_max > 0 else 100.0,
            'status': overall_status,
            'critical_combo': 'envelope',
            'dcr_2': result.dcr_max, 'dcr_3': 0, 'dcr_combined': result.dcr_max,
            'phi_Vn_2': 0, 'phi_Vn_3': 0,
            'Vu_2': 0, 'Vu_3': 0,
            'Vc': 0, 'Vs': 0,
            'formula_type': 'wall'
        }

        if hasattr(domain_result, 'shear') and domain_result.shear:
            sh = domain_result.shear
            shear_data.update({
                'dcr_2': sh.dcr,
                'dcr_combined': sh.dcr,
                'phi_Vn_2': getattr(sh, 'phi_Vn', 0),
                'Vu_2': getattr(sh, 'Ve', 0),
                'Vc': getattr(sh, 'Vc', 0),
                'Vs': getattr(sh, 'Vs', 0),
            })
            if sh.dcr > 0:
                shear_data['sf'] = round(1.0 / sh.dcr, 2)

        return {
            'element_type': 'drop_beam',
            'key': key,
            'pier_label': drop_beam.label,
            'story': drop_beam.story,
            'geometry': {
                'width_m': drop_beam.length / 1000,
                'thickness_m': drop_beam.thickness / 1000,
                'height_m': drop_beam.width / 1000,
                'fc_MPa': drop_beam.fc,
                'fy_MPa': drop_beam.fy
            },
            'reinforcement': {
                'As_vertical_mm2': drop_beam.As_vertical,
                'As_edge_total': drop_beam.As_edge_total,
                'n_edge_bars': drop_beam.n_edge_bars,
                'diameter_edge': drop_beam.diameter_edge,
                'rho_vertical': round(drop_beam.rho_vertical, 5),
                'description': drop_beam.reinforcement_description
            },
            'flexure': {
                'sf': 1.0 / result.dcr_max if result.dcr_max > 0 else 100.0,
                'dcr': result.dcr_max,  # DCR directo
                'status': overall_status,
                'critical_combo': 'envelope',
                'phi_Mn_at_Pu': 0, 'Mu': 0, 'phi_Mn_0': 0,
                'Pu': 0, 'phi_Pn_max': 0,
                'exceeds_axial': False, 'has_tension': False
            },
            'shear': shear_data,
            'slenderness': {
                'lambda': 0, 'is_slender': False,
                'delta_ns': 1.0, 'magnification_pct': 0.0
            },
            'overall_status': overall_status,
            'status_class': get_status_css_class(overall_status),
            'wall_continuity': None,
            'design_proposal': {'has_proposal': False},
            'pm_plot': pm_plot,
            'design_behavior': result.design_behavior.name,
            'service_used': result.service_used,
            'aci_section': result.design_behavior.aci_section,
            'dcr_max': result.dcr_max,
            'critical_check': result.critical_check,
            'warnings': result.warnings
        }

    # =========================================================================
    # Formateo de Capacidades (sin OrchestrationResult)
    # =========================================================================

    @staticmethod
    def format_beam_capacities(
        beam: 'Beam',
        beam_forces=None
    ) -> Dict[str, Any]:
        """
        Formatea capacidades y propiedades de una viga para la UI.

        Este método NO usa OrchestrationResult, solo formatea las propiedades
        del elemento Beam directamente.

        Args:
            beam: Entidad Beam
            beam_forces: Fuerzas de la viga (opcional)

        Returns:
            Dict con propiedades formateadas
        """
        # Información de la viga
        beam_info = {
            'label': beam.label,
            'story': beam.story,
            'source': beam.source.value if hasattr(beam.source, 'value') else str(beam.source),
            'length_mm': beam.length,
            'depth_mm': beam.depth,
            'width_mm': beam.width,
            'fc_MPa': beam.fc,
            'fy_MPa': beam.fy,
            'cover_mm': beam.cover,
            'd_mm': round(beam.d, 1),
            'ln_mm': round(beam.ln_calculated, 1),
            'aspect_ratio': round(beam.aspect_ratio, 2),
            'is_deep': beam.is_deep,
            'section_name': beam.section_name,
        }

        # Información de refuerzo
        reinforcement = {
            'n_bars_top': beam.n_bars_top,
            'n_bars_bottom': beam.n_bars_bottom,
            'diameter_top': beam.diameter_top,
            'diameter_bottom': beam.diameter_bottom,
            'As_top_mm2': round(beam.As_top, 1),
            'As_bottom_mm2': round(beam.As_bottom, 1),
            'As_total_mm2': round(beam.As_flexure_total, 1),
            'stirrup_diameter': beam.stirrup_diameter,
            'stirrup_spacing': beam.stirrup_spacing,
            'n_stirrup_legs': beam.n_stirrup_legs,
            'Av_mm2': round(beam.Av, 1),
        }

        # Fuerzas si están disponibles
        forces = None
        if beam_forces:
            critical = beam_forces.get_critical_shear()
            if critical:
                forces = {
                    'combo_name': critical.combo_name,
                    'V2_tonf': round(critical.V2, 2),
                    'M3_tonf_m': round(critical.M3, 2),
                }

        # Momentos probables si están calculados
        mpr_info = None
        if beam.Mpr_left or beam.Mpr_right:
            mpr_info = {
                'Mpr_left_tonf_m': round(beam.Mpr_left or 0, 2),
                'Mpr_right_tonf_m': round(beam.Mpr_right or 0, 2),
            }

        return {
            'beam': beam_info,
            'reinforcement': reinforcement,
            'forces': forces,
            'mpr': mpr_info
        }

    @staticmethod
    def format_column_capacities(
        column: 'Column',
        column_forces=None
    ) -> Dict[str, Any]:
        """
        Formatea capacidades y propiedades de una columna para la UI.

        Este método NO usa OrchestrationResult, solo formatea las propiedades
        del elemento Column directamente.

        Args:
            column: Entidad Column
            column_forces: Fuerzas de la columna (opcional)

        Returns:
            Dict con propiedades formateadas
        """
        # Información de la columna
        column_info = {
            'label': column.label,
            'story': column.story,
            'depth_mm': column.depth,
            'width_mm': column.width,
            'height_mm': column.height,
            'fc_MPa': column.fc,
            'fy_MPa': column.fy,
            'cover_mm': column.cover,
            'Ag_mm2': column.Ag,
            'section_name': column.section_name,
        }

        # Información de refuerzo
        reinforcement = {
            'n_total_bars': column.n_total_bars,
            'n_bars_depth': column.n_bars_depth,
            'n_bars_width': column.n_bars_width,
            'diameter_long': column.diameter_long,
            'As_longitudinal_mm2': round(column.As_longitudinal, 1),
            'rho_longitudinal': round(column.rho_longitudinal, 4),
            'stirrup_diameter': column.stirrup_diameter,
            'stirrup_spacing': column.stirrup_spacing,
            'n_stirrup_legs_depth': column.n_stirrup_legs_depth,
            'n_stirrup_legs_width': column.n_stirrup_legs_width,
        }

        # Fuerzas si están disponibles
        forces = None
        if column_forces:
            critical = column_forces.get_critical_combination()
            if critical:
                forces = {
                    'combo_name': critical.combo_name,
                    'P_tonf': round(critical.P, 2),
                    'V2_tonf': round(critical.V2, 2),
                    'V3_tonf': round(critical.V3, 2),
                    'M2_tonf_m': round(critical.M2, 2),
                    'M3_tonf_m': round(critical.M3, 2),
                }

        return {
            'column': column_info,
            'reinforcement': reinforcement,
            'forces': forces
        }
