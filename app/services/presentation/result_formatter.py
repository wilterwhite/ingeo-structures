# app/services/presentation/result_formatter.py
"""
Formateador de resultados para conversion a formato UI.

Convierte resultados de ElementService al formato unificado
que espera el frontend.
"""
from typing import Dict, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..analysis.verification_result import ElementVerificationResult
    from ...domain.entities import Beam, Column, Pier
    from ...domain.calculations.wall_continuity import WallContinuityInfo


class ResultFormatter:
    """
    Formatea resultados de analisis para la UI.

    Convierte ElementVerificationResult al formato unificado
    que espera la tabla del frontend.
    """

    @staticmethod
    def format_element_result(
        element: Union['Beam', 'Column', 'Pier'],
        result: 'ElementVerificationResult',
        key: str,
        continuity_info: 'WallContinuityInfo' = None
    ) -> Dict[str, Any]:
        """
        Formatea resultado de cualquier elemento al formato UI.

        Args:
            element: Beam, Column o Pier
            result: ElementVerificationResult del servicio
            key: Clave unica del elemento
            continuity_info: Información de continuidad del muro (solo piers)

        Returns:
            Dict con formato unificado para UI
        """
        from ..analysis.element_classifier import ElementType

        element_type = result.element_type

        if element_type == ElementType.BEAM:
            return ResultFormatter._format_beam(element, result, key)
        elif element_type.is_column:
            return ResultFormatter._format_column(element, result, key)
        else:
            return ResultFormatter._format_pier(element, result, key, continuity_info)

    @staticmethod
    def _format_column(
        column: 'Column',
        result: 'ElementVerificationResult',
        key: str
    ) -> Dict[str, Any]:
        """Formatea resultado de columna."""
        flexure = result.flexure
        shear = result.shear
        slenderness = flexure.slenderness

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
                'sf': flexure.sf,
                'status': flexure.status,
                'critical_combo': flexure.critical_combo,
                'phi_Mn_at_Pu': flexure.phi_Mn_at_Pu,
                'Mu': flexure.Mu,
                'phi_Mn_0': flexure.phi_Mn,
                'Pu': flexure.Pu,
                'phi_Pn_max': flexure.phi_Pn_max,
                'exceeds_axial': flexure.exceeds_axial,
                'has_tension': flexure.has_tension,
                'tension_combos': 0
            },
            'shear': {
                'sf': shear.sf_combined or shear.sf,
                'status': shear.status,
                'critical_combo': shear.critical_combo,
                'dcr_2': shear.dcr_2,
                'dcr_3': shear.dcr_3 or 0,
                'dcr_combined': shear.dcr_combined or shear.dcr_2,
                'phi_Vn_2': shear.phi_Vn_2,
                'phi_Vn_3': shear.phi_Vn_3 or 0,
                'Vu_2': shear.Vu_2,
                'Vu_3': shear.Vu_3 or 0,
                'Vc': shear.Vc,
                'Vs': shear.Vs,
                'formula_type': 'column'
            },
            'slenderness': {
                'lambda': slenderness.lambda_ratio if slenderness else 0,
                'is_slender': slenderness.is_slender if slenderness else False,
                'delta_ns': slenderness.delta_ns if slenderness else 1.0,
                'magnification_pct': round(slenderness.magnification_pct, 1) if slenderness else 0.0
            },
            'overall_status': result.overall_status,
            'wall_continuity': None,
            'classification': None,
            'amplification': None,
            'boundary_element': None,
            'design_proposal': {'has_proposal': False},
            'pm_plot': result.pm_plot
        }

    @staticmethod
    def _format_beam(
        beam: 'Beam',
        result: 'ElementVerificationResult',
        key: str
    ) -> Dict[str, Any]:
        """Formatea resultado de viga."""
        flexure = result.flexure
        shear = result.shear

        return {
            'element_type': 'beam',
            'key': key,
            'label': beam.label,
            'story': beam.story,
            'source': beam.source.value,
            'is_custom': getattr(beam, 'is_custom', False),
            'geometry': {
                'length_m': beam.length / 1000,
                'depth_m': beam.depth / 1000,
                'width_m': beam.width / 1000,
                'fc_MPa': beam.fc,
                'fy_MPa': beam.fy
            },
            'reinforcement': {
                # Longitudinal
                'n_bars_top': beam.n_bars_top,
                'n_bars_bottom': beam.n_bars_bottom,
                'diameter_top': beam.diameter_top,
                'diameter_bottom': beam.diameter_bottom,
                # Transversal
                'stirrup_diameter': beam.stirrup_diameter,
                'stirrup_spacing': beam.stirrup_spacing,
                'n_stirrup_legs': beam.n_stirrup_legs,
                'Av': round(beam.Av, 1),
                'rho_transversal': round(beam.rho_transversal, 5)
            },
            'flexure': {
                'sf': flexure.sf,
                'status': flexure.status,
                'design_type': flexure.design_type,
                'phi_Mn': flexure.phi_Mn,
                'Mu': flexure.Mu,
                'Pu': flexure.Pu,
                'critical_combo': flexure.critical_combo,
                'has_significant_axial': flexure.has_significant_axial,
                'warning': flexure.warning
            },
            'shear': {
                'sf': shear.sf,
                'status': shear.status,
                'critical_combo': shear.critical_combo,
                'phi_Vn': shear.phi_Vn_2,
                'Vu': shear.Vu_2,
                'dcr': shear.dcr_2,
                'Vc': shear.Vc,
                'Vs': shear.Vs,
                'Vs_max': shear.Vs_max,
                'aci_reference': shear.aci_reference
            },
            'overall_status': result.overall_status
        }

    @staticmethod
    def _format_pier(
        pier: 'Pier',
        result: 'ElementVerificationResult',
        key: str,
        continuity_info: 'WallContinuityInfo' = None
    ) -> Dict[str, Any]:
        """Formatea resultado de muro/pier."""
        from dataclasses import asdict

        flexure = result.flexure
        shear = result.shear
        slenderness = flexure.slenderness
        wall_checks = result.wall_checks

        # Clasificacion
        classification = None
        if wall_checks and wall_checks.classification:
            classification = {
                'type': wall_checks.classification.type,
                'lw_tw': wall_checks.classification.lw_tw,
                'hw_lw': wall_checks.classification.hw_lw,
                'aci_section': wall_checks.classification.aci_section,
                'is_wall_pier': wall_checks.classification.is_wall_pier
            }

        # Amplificacion
        amplification = None
        if wall_checks and wall_checks.amplification:
            amplification = wall_checks.amplification

        # Elementos de borde
        boundary = None
        if wall_checks and wall_checks.boundary:
            boundary = {
                'required': wall_checks.boundary.required,
                'method': wall_checks.boundary.method,
                'sigma_max': wall_checks.boundary.sigma_max,
                'sigma_limit': wall_checks.boundary.sigma_limit,
                'length_mm': wall_checks.boundary.length_mm,
                'status': wall_checks.boundary.status
            }

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
                'rho_vertical': round(pier.rho_vertical, 5),
                'rho_horizontal': round(pier.rho_horizontal, 5)
            },
            'flexure': {
                'sf': flexure.sf,
                'status': flexure.status,
                'critical_combo': flexure.critical_combo,
                'phi_Mn_at_Pu': flexure.phi_Mn_at_Pu,
                'Mu': flexure.Mu,
                'phi_Mn_0': flexure.phi_Mn,
                'Pu': flexure.Pu,
                'phi_Pn_max': flexure.phi_Pn_max,
                'exceeds_axial': flexure.exceeds_axial,
                'has_tension': flexure.has_tension
            },
            'shear': {
                'sf': shear.sf,
                'status': shear.status,
                'critical_combo': shear.critical_combo,
                'dcr_2': shear.dcr_2,
                'dcr_3': shear.dcr_3 or 0,
                'dcr_combined': shear.dcr_combined or shear.dcr_2,
                'phi_Vn_2': shear.phi_Vn_2,
                'phi_Vn_3': shear.phi_Vn_3 or 0,
                'Vu_2': shear.Vu_2,
                'Vu_3': shear.Vu_3 or 0,
                'Vc': shear.Vc,
                'Vs': shear.Vs,
                'Ve': shear.Ve,
                'omega_v': shear.omega_v,
                'formula_type': 'wall'
            },
            'slenderness': {
                'lambda': slenderness.lambda_ratio if slenderness else 0,
                'is_slender': slenderness.is_slender if slenderness else False,
                'delta_ns': slenderness.delta_ns if slenderness else 1.0,
                'magnification_pct': round(slenderness.magnification_pct, 1) if slenderness else 0.0
            },
            'classification': classification,
            'amplification': amplification,
            'boundary_element': boundary,
            'overall_status': result.overall_status,
            'wall_continuity': ResultFormatter._format_wall_continuity(
                pier, continuity_info
            ),
            'design_proposal': {'has_proposal': result.proposal is not None},
            'pm_plot': result.pm_plot
        }

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
    # Metodos de compatibilidad (para transicion gradual)
    # =========================================================================

    @staticmethod
    def format_column_result(
        column: Any,
        col_result: Dict[str, Any],
        key: str
    ) -> Dict[str, Any]:
        """
        Compatibilidad: Convierte resultado de columna (formato antiguo).

        DEPRECATED: Usar format_element_result con ElementVerificationResult.
        """
        flexure = col_result.get('flexure', {})
        shear = col_result.get('shear', {})
        slenderness = flexure.get('slenderness', {})

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
                'sf': flexure.get('sf', 0),
                'status': flexure.get('status', 'N/A'),
                'critical_combo': flexure.get('critical_combo', ''),
                'phi_Mn_at_Pu': flexure.get('phi_Mn_at_Pu', 0),
                'Mu': flexure.get('Mu', 0),
                'phi_Mn_0': flexure.get('phi_Mn_M3', 0),
                'Pu': flexure.get('Pu', 0),
                'phi_Pn_max': flexure.get('phi_Pn_max', 0),
                'exceeds_axial': flexure.get('exceeds_axial_capacity', False),
                'has_tension': flexure.get('has_tension', False),
                'tension_combos': flexure.get('tension_combos', 0)
            },
            'shear': {
                'sf': shear.get('sf_combined', 0),
                'status': shear.get('status', 'N/A'),
                'critical_combo': shear.get('critical_combo', ''),
                'dcr_2': shear.get('dcr_V2', 0),
                'dcr_3': shear.get('dcr_V3', 0),
                'dcr_combined': shear.get('dcr_combined', 0),
                'phi_Vn_2': shear.get('phi_Vn_V2', 0),
                'phi_Vn_3': shear.get('phi_Vn_V3', 0),
                'Vu_2': shear.get('Vu_V2', 0),
                'Vu_3': shear.get('Vu_V3', 0),
                'Vc': shear.get('Vc_V2', 0),
                'Vs': shear.get('Vs_V2', 0),
                'formula_type': 'column'
            },
            'slenderness': {
                'lambda': slenderness.get('lambda', 0),
                'is_slender': slenderness.get('is_slender', False),
                'reduction': slenderness.get('factor', 1.0),
                'reduction_pct': round((1 - slenderness.get('factor', 1.0)) * 100, 1)
            },
            'overall_status': col_result.get('status', 'N/A'),
            'wall_continuity': None,
            'classification': None,
            'amplification': None,
            'boundary_element': None,
            'design_proposal': {'has_proposal': False},
            'pm_plot': None
        }

    @staticmethod
    def format_beam_result(
        beam: Any,
        shear_result: Dict[str, Any],
        key: str
    ) -> Dict[str, Any]:
        """
        Compatibilidad: Convierte resultado de viga (formato antiguo).

        DEPRECATED: Usar format_element_result con ElementVerificationResult.
        """
        return {
            'element_type': 'beam',
            'key': key,
            'label': beam.label,
            'story': beam.story,
            'source': beam.source.value,
            'is_custom': getattr(beam, 'is_custom', False),
            'geometry': {
                'length_m': beam.length / 1000,
                'depth_m': beam.depth / 1000,
                'width_m': beam.width / 1000,
                'fc_MPa': beam.fc,
                'fy_MPa': beam.fy
            },
            'reinforcement': {
                # Longitudinal
                'n_bars_top': beam.n_bars_top,
                'n_bars_bottom': beam.n_bars_bottom,
                'diameter_top': beam.diameter_top,
                'diameter_bottom': beam.diameter_bottom,
                # Transversal
                'stirrup_diameter': beam.stirrup_diameter,
                'stirrup_spacing': beam.stirrup_spacing,
                'n_stirrup_legs': beam.n_stirrup_legs,
                'Av': round(beam.Av, 1),
                'rho_transversal': round(beam.rho_transversal, 5)
            },
            'shear': shear_result,
            'overall_status': shear_result.get('status', 'N/A')
        }

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
