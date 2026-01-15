# app/services/presentation/result_formatter.py
"""
Formateador de resultados para conversión a formato UI.

Convierte resultados de ElementOrchestrator al formato unificado
que espera el frontend.

Métodos principales:
- format_any_element: Formatea cualquier elemento (Pier, Column, Beam, DropBeam)
"""
import math
from typing import Dict, Any, Union, TYPE_CHECKING

from ...domain.constants.phi_chapter21 import get_dcr_status, RHO_MAX
from ...domain.constants.reinforcement import RHO_MIN, MAX_SPACING_SEISMIC_MM
from ...domain.constants.geometry import COLUMN_MIN_DIMENSION_MM
from ..analysis.statistics_service import calculate_statistics
from .formatters import (
    format_safety_factor,
    get_status_css_class,
    format_dimensions,
    format_dcr_display,
)

if TYPE_CHECKING:
    from ..analysis.element_orchestrator import OrchestrationResult
    from ...domain.entities import HorizontalElement, VerticalElement
    from ...domain.calculations.wall_continuity import WallContinuityInfo


def get_dcr_css_class(dcr: float) -> str:
    """
    Retorna la clase CSS según el D/C ratio.

    Args:
        dcr: Demand/Capacity ratio

    Returns:
        Clase CSS para aplicar al valor (fs-ok, fs-warn, fs-fail)

    Usa umbrales centralizados del domain (DCR_OK=0.67, DCR_WARN=1.0).
    """
    status = get_dcr_status(dcr)  # 'ok', 'warn', 'fail'
    return f'fs-{status}'


class ResultFormatter:
    """
    Formatea resultados de análisis para la UI.

    Convierte OrchestrationResult al formato unificado que espera el frontend.

    Uso principal:
        result = orchestrator.verify(element, forces)
        formatted = ResultFormatter.format_any_element(element, key, result)
    """

    # =========================================================================
    # Formateo de continuidad de muros
    # =========================================================================

    @staticmethod
    def _format_wall_continuity(
        pier: 'VerticalElement',
        continuity_info: 'WallContinuityInfo' = None
    ) -> Dict[str, Any]:
        """Formatea información de continuidad del muro."""
        # Si tenemos continuity_info, usar propiedades del domain
        if continuity_info:
            return {
                'hwcs_m': round(continuity_info.hwcs_m, 2),
                'hwcs_lw': round(continuity_info.get_hwcs_lw(pier.width), 2),
                'n_stories': continuity_info.n_stories,
                'is_continuous': continuity_info.is_continuous,
                'is_base': continuity_info.is_base,
                'stories_list': continuity_info.stories_list
            }

        # Fallback: calcular de la geometría del pier
        hwcs_m = pier.height / 1000  # mm -> m
        lw_m = pier.length / 1000  # mm -> m
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
    # Estructura base común para todos los elementos
    # =========================================================================

    @staticmethod
    def _build_base_result(
        element_type: str,
        key: str,
        label: str,
        story: str,
        result: 'OrchestrationResult',
        geometry: Dict[str, Any],
        reinforcement: Dict[str, Any],
        pm_plot: str = None,
        seismic_category: str = None
    ) -> Dict[str, Any]:
        """
        Construye la estructura base común para todos los tipos de elementos.

        Esta función centraliza la lógica común de formateo, reduciendo
        duplicación en los métodos especializados.

        Args:
            seismic_category: Categoría sísmica del elemento ('SPECIAL', 'INTERMEDIATE', 'ORDINARY', 'NON_SFRS')
        """
        overall_status = 'OK' if result.is_ok else 'NO OK'
        dcr = result.dcr_max

        # Datos base mínimos - normalmente sobrescritos por _extract_*_from_*()
        # Solo mantener campos esenciales para fallback
        flexure_data = {'sf': 0, 'dcr': dcr, 'status': overall_status}
        shear_data = {'sf': 0, 'dcr': dcr, 'status': overall_status, 'formula_type': element_type}
        slenderness_data = {'lambda': 0, 'is_slender': False, 'delta_ns': 1.0}

        return {
            'element_type': element_type,
            'key': key,
            'pier_label': label,
            'story': story,
            # Campos pre-formateados para UI
            'dimensions_display': format_dimensions(
                geometry.get('width_mm', 0),
                geometry.get('thickness_mm', 0)
            ),
            'dcr_display': format_dcr_display(dcr),
            'dcr_class': get_dcr_css_class(dcr),
            'geometry': {
                'width_m': geometry.get('width_mm', 0) / 1000,
                'thickness_m': geometry.get('thickness_mm', 0) / 1000,
                'height_m': geometry.get('height_mm', 0) / 1000,
                'length_m': geometry.get('length_mm', geometry.get('height_mm', 0)) / 1000,  # Para vigas
                'fc_MPa': geometry.get('fc', 0),
                'fy_MPa': geometry.get('fy', 0)
            },
            'reinforcement': reinforcement,
            'flexure': flexure_data,
            'shear': shear_data,
            'slenderness': slenderness_data,
            'classification': None,
            'amplification': None,
            'boundary_element': None,
            'overall_status': overall_status,
            'status_class': get_status_css_class(overall_status),
            'wall_continuity': None,
            'design_proposal': {'has_proposal': False},
            'pm_plot': pm_plot,
            # Metadata de orquestación
            'design_behavior': result.design_behavior.name,
            'service_used': result.service_used,
            'aci_section': result.design_behavior.aci_section,
            'dcr_max': result.dcr_max,
            'critical_check': result.critical_check,
            'warnings': result.warnings,
            # Categoría sísmica individual del elemento (null = usar global)
            'seismic_category': seismic_category
        }

    @staticmethod
    def _extract_pier_geometry_reinforcement(pier: 'VerticalElement') -> tuple:
        """
        Extrae geometría y refuerzo base de un Pier.

        Centraliza la lógica común para _format_wall/column/flexure_orchestration.
        Detecta campos modificados comparando contra el MÍNIMO CALCULADO para
        cada pier (no contra constantes hardcodeadas).

        Returns:
            (geometry, reinforcement) dicts
        """
        from ...domain.calculations.minimum_reinforcement import MinimumReinforcementCalculator

        geometry = {
            'width_mm': pier.length,
            'width_m': pier.length / 1000,
            'thickness_mm': pier.thickness,
            'thickness_m': pier.thickness / 1000,
            'height_mm': pier.height,
            'fc': pier.fc,
            'fy': pier.fy
        }

        # Verificar cuantía máxima (4% según ACI 318-25 §18.10.2.1)
        rho_v_exceeds_max = pier.rho_vertical > RHO_MAX

        # Calcular enfierradura mínima para ESTE pier (según espesor y cover)
        min_config = MinimumReinforcementCalculator.calculate_for_pier(pier.thickness)
        min_n_edge, min_diam_edge = MinimumReinforcementCalculator.calculate_edge_reinforcement(
            pier.thickness, pier.cover
        )

        # Detectar campos modificados respecto al MÍNIMO CALCULADO
        modified_fields = []
        if pier.n_meshes != min_config.n_meshes:
            modified_fields.append('n_meshes')
        if pier.diameter_v != min_config.diameter:
            modified_fields.append('diameter_v')
        if pier.spacing_v != min_config.spacing:
            modified_fields.append('spacing_v')
        if pier.diameter_h != min_config.diameter:
            modified_fields.append('diameter_h')
        if pier.spacing_h != min_config.spacing:
            modified_fields.append('spacing_h')
        if pier.n_edge_bars != min_n_edge:
            modified_fields.append('n_edge_bars')
        if pier.diameter_edge != min_diam_edge:
            modified_fields.append('diameter_edge')
        # Estribos: no hay mínimo calculado, mantener check simple contra valores típicos
        if pier.stirrup_diameter != 10:
            modified_fields.append('stirrup_diameter')
        if pier.stirrup_spacing != 150:
            modified_fields.append('stirrup_spacing')

        reinforcement = {
            # Valores calculados
            'As_vertical_mm2': pier.As_vertical,
            'As_horizontal_mm2': pier.As_horizontal,
            'As_vertical_per_m': round(pier.As_vertical_per_m, 1),
            'As_horizontal_per_m': round(pier.As_horizontal, 1),
            'rho_vertical': round(pier.rho_vertical, 5),
            'rho_horizontal': round(pier.rho_horizontal, 5),
            # Valores de configuración (para que el frontend pueda actualizar dropdowns)
            'n_meshes': pier.n_meshes,
            'diameter_v': pier.diameter_v,
            'spacing_v': pier.spacing_v,
            'diameter_h': pier.diameter_h,
            'spacing_h': pier.spacing_h,
            'n_edge_bars': pier.n_edge_bars,
            'diameter_edge': pier.diameter_edge,
            'stirrup_diameter': pier.stirrup_diameter,
            'stirrup_spacing': pier.stirrup_spacing,
            # Validaciones adicionales
            'rho_v_exceeds_max': rho_v_exceeds_max,
            'rho_max': RHO_MAX,
            # Campos modificados respecto al default
            'modified_fields': modified_fields,
        }
        return geometry, reinforcement

    @staticmethod
    def _extract_shear_from_domain(
        domain_result,
        base_dcr: float,
        formula_type: str = 'wall'
    ) -> Dict[str, Any]:
        """Extrae datos de cortante del resultado de dominio."""
        shear_data = {
            'sf': 1.0 / base_dcr if base_dcr > 0 else 100.0,
            'dcr': base_dcr,
            'dcr_class': get_dcr_css_class(base_dcr),
            'status': 'OK' if base_dcr <= 1.0 else 'NO OK',
            'critical_combo': 'envelope',
            'dcr_2': base_dcr,
            'dcr_3': 0,
            'dcr_combined': base_dcr,
            'phi_Vn_2': 0,
            'phi_Vn_3': 0,
            'Vu_2': 0,
            'Vu_3': 0,
            'Vc': 0,
            'Vs': 0,
            'Ve': 0,
            'omega_v': None,
            'formula_type': formula_type,
            'phi_v': 0.60  # Default para SPECIAL (§21.2.4.1)
        }

        if hasattr(domain_result, 'shear') and domain_result.shear:
            sh = domain_result.shear
            dcr = getattr(sh, 'dcr', base_dcr)
            Vc = getattr(sh, 'Vc', 0) if not hasattr(sh, 'capacity_V2') else (sh.capacity_V2.Vc if sh.capacity_V2 else 0)
            Vs = getattr(sh, 'Vs', 0) if not hasattr(sh, 'capacity_V2') else (sh.capacity_V2.Vs if sh.capacity_V2 else 0)
            # Obtener Vu original - puede ser 'Vu' (vigas/muros) o 'Vu_V2' (columnas)
            Vu_original = getattr(sh, 'Vu', 0) or getattr(sh, 'Vu_V2', 0)
            Ve_amplified = getattr(sh, 'Ve', Vu_original)  # Fallback a Vu si no hay Ve
            shear_data.update({
                'dcr': round(dcr, 2),
                'dcr_class': get_dcr_css_class(dcr),
                'dcr_2': round(dcr, 2),
                'dcr_combined': round(dcr, 2),
                'phi_Vn_2': round(getattr(sh, 'phi_Vn', getattr(sh, 'phi_Vn_V2', 0)), 2),
                'Vu_2': round(Ve_amplified, 2),  # Mantener compatibilidad (usado para DCR)
                'Vu_original': round(Vu_original, 2),  # Vu del análisis
                'Ve': round(Ve_amplified, 2),  # Ve amplificado (§18.10.3.3)
                'Vc': round(Vc, 2),
                'Vs': round(Vs, 2),
                'phi_v': getattr(sh, 'phi_v', 0.60),  # Factor φv usado
            })
            if dcr > 0:
                shear_data['sf'] = round(1.0 / dcr, 2)

        return shear_data

    @staticmethod
    def _extract_flexure_from_result(
        result: 'OrchestrationResult',
        base_dcr: float
    ) -> Dict[str, Any]:
        """
        Extrae datos de flexión del OrchestrationResult.

        Prioriza flexure_data del result (calculado por FlexocompressionService)
        sobre datos del domain_result (que puede no tener flexure).
        """
        flexure_data = {
            'sf': 1.0 / base_dcr if base_dcr > 0 else 100.0,
            'dcr': round(base_dcr, 2),
            'dcr_class': get_dcr_css_class(base_dcr),
            'status': 'OK' if base_dcr <= 1.0 else 'NO OK',
            'critical_combo': 'envelope',
            'phi_Mn_at_Pu': 0,
            'Mu': 0,
            'phi_Mn_0': 0,
            'Pu': 0,
            'phi_Pn_max': 0,
            'exceeds_axial': False,
            'has_tension': False,
            'tension_combos': 0
        }

        # Buscar datos de flexure en result.flexure_data (del FlexocompressionService)
        if hasattr(result, 'flexure_data') and result.flexure_data:
            flex = result.flexure_data
            # DCR y SF vienen centralizados del servicio (calculados vía ray-casting)
            dcr = flex.get('dcr', base_dcr)
            sf = flex.get('sf', 1.0 / dcr if dcr > 0 else 100.0)
            flexure_data.update({
                'Mu': round(flex.get('Mu', 0), 2),
                'phi_Mn_at_Pu': round(flex.get('phi_Mn_at_Pu', 0), 2),
                'phi_Mn_0': round(flex.get('phi_Mn_0', 0), 2),
                'Pu': round(flex.get('Pu', 0), 2),
                'phi_Pn_max': round(flex.get('phi_Pn_max', 0), 2),
                'exceeds_axial': flex.get('exceeds_axial_capacity', False),
                'exceeds_tension': flex.get('exceeds_tension', False),
                'phi_Pt_min': round(flex.get('phi_Pt_min', 0), 2),
                'has_tension': flex.get('has_tension', False),
                'tension_combos': flex.get('tension_combos', 0),
                'critical_combo': flex.get('critical_combo', 'envelope'),
                'sf': round(sf, 2) if sf < 100 else 100.0,
                'dcr': round(dcr, 3),  # Precisión 3 decimales como el servicio
                'status': flex.get('status', 'OK'),
                # Resultados de TODAS las combinaciones (para modal sin recálculo)
                'combo_results': flex.get('combo_results', []),
            })
            flexure_data['dcr_class'] = get_dcr_css_class(flexure_data['dcr'])

        return flexure_data

    # =========================================================================
    # Extracción centralizada de geometry_warnings
    # =========================================================================

    @staticmethod
    def _extract_geometry_warnings(
        domain_result,
        element_type: str = 'pier'
    ) -> list:
        """
        Extrae geometry_warnings de cualquier tipo de resultado de dominio.

        Centraliza la lógica de extracción de advertencias geométricas que
        deben mostrarse en la celda de Geometría del frontend.

        Args:
            domain_result: Resultado del dominio (SeismicColumnResult, etc.)
            element_type: Tipo de elemento ('pier', 'column', 'beam', 'drop_beam')

        Returns:
            Lista de strings con advertencias de geometría
        """
        warnings = []

        # Columnas sísmicas: dimensional_limits con min_dimension_ok (§18.7.2.1)
        # Nota: Vigas también usan dimensional_limits pero con bw_ok/ln_ok, no min_dimension_ok
        if hasattr(domain_result, 'dimensional_limits') and domain_result.dimensional_limits:
            dim = domain_result.dimensional_limits
            # Solo procesar si es resultado de columna (tiene min_dimension_ok)
            if hasattr(dim, 'min_dimension_ok') and not dim.min_dimension_ok:
                min_required = getattr(dim, 'min_dimension_required', COLUMN_MIN_DIMENSION_MM)
                warnings.append(
                    f"Espesor {dim.min_dimension:.0f}mm < {min_required:.0f}mm "
                    f"mínimo (ACI §18.7.2.1)"
                )
            if hasattr(dim, 'aspect_ratio_ok') and not dim.aspect_ratio_ok:
                warnings.append(
                    f"Relación b/h={dim.aspect_ratio:.2f} < 0.4 mínimo (ACI §18.7.2.1)"
                )
            # Vigas: dimensional_limits con bw_ok/ln_ok (§18.6.2)
            if hasattr(dim, 'bw_ok') and not dim.bw_ok:
                warnings.append(
                    f"Ancho bw={dim.bw:.0f}mm < {dim.bw_min:.0f}mm "
                    f"mínimo (ACI §18.6.2.1)"
                )
            if hasattr(dim, 'ln_ok') and not dim.ln_ok:
                warnings.append(
                    f"Luz ln={dim.ln:.0f}mm < 4d={dim.ln_min:.0f}mm "
                    f"mínimo (ACI §18.6.2.1)"
                )

        # Muros: boundary element warnings (§18.10.6.4)
        if hasattr(domain_result, 'boundary') and domain_result.boundary:
            be = domain_result.boundary
            # Filtrar solo warnings relacionados con espesor/geometría
            for w in getattr(be, 'warnings', []):
                if any(kw in w for kw in ['Espesor', 'espesor', '305', '300', 'ancho']):
                    warnings.append(w)

        # Vigas: dimensional_limits (§18.6.2)
        if hasattr(domain_result, 'beam_dimensional') and domain_result.beam_dimensional:
            bd = domain_result.beam_dimensional
            if hasattr(bd, 'min_width_ok') and not bd.min_width_ok:
                warnings.append(
                    f"Ancho {bd.width:.0f}mm < {bd.min_width_required:.0f}mm "
                    f"mínimo (ACI §18.6.2)"
                )

        return warnings

    # =========================================================================
    # Formateo de resultados de ElementOrchestrator (arquitectura unificada)
    # =========================================================================

    @staticmethod
    def format_orchestration_result(
        pier: 'VerticalElement',
        result: 'OrchestrationResult',
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """
        Formatea resultado de OrchestrationResult al formato UI.

        Método unificado que soporta wall, column, y flexure según service_used.
        """
        service_used = result.service_used
        domain_result = result.domain_result

        # Extraer geometría y refuerzo usando helper
        geometry, reinforcement = ResultFormatter._extract_pier_geometry_reinforcement(pier)

        # Configurar refuerzo según tipo de servicio
        if service_used == 'wall' and hasattr(domain_result, 'reinforcement') and domain_result.reinforcement:
            rf = domain_result.reinforcement
            rho_min = rf.rho_l_min
            max_spacing = rf.spacing_max
            rho_v_ok = rf.rho_l_ok
            rho_h_ok = rf.rho_t_ok
            spacing_v_ok = rf.spacing_ok
            spacing_h_ok = rf.spacing_ok
        else:
            # Columnas y flexure usan valores por defecto
            rho_min = RHO_MIN
            max_spacing = MAX_SPACING_SEISMIC_MM
            rho_v_ok = True
            rho_h_ok = True
            spacing_v_ok = True
            spacing_h_ok = True

        # Pre-calcular warnings para el frontend (§18.10.2.1)
        warnings_v = []
        warnings_h = []
        if not rho_v_ok:
            warnings_v.append(f'ρ_malla < {rho_min * 100}%')
        if not spacing_v_ok:
            warnings_v.append(f's > {max_spacing}mm')
        if not rho_h_ok:
            warnings_h.append(f'ρ < {rho_min * 100}%')
        if not spacing_h_ok:
            warnings_h.append(f's > {max_spacing}mm')

        reinforcement.update({
            'rho_v_ok': rho_v_ok,
            'rho_h_ok': rho_h_ok,
            'rho_mesh_v_ok': rho_v_ok,
            'spacing_v_ok': spacing_v_ok,
            'spacing_h_ok': spacing_h_ok,
            'rho_min': rho_min,
            'max_spacing': max_spacing,
            # Warnings pre-calculados
            'warnings_v': warnings_v,
            'warnings_h': warnings_h,
        })

        # Determinar tipo de elemento: priorizar service_used, luego source
        if service_used == 'strut':
            element_type = 'strut'
        elif pier.is_frame_source:
            element_type = 'column'
        else:
            element_type = 'pier'

        # Construir resultado base
        formatted = ResultFormatter._build_base_result(
            element_type=element_type,
            key=key,
            label=pier.label,
            story=pier.story,
            result=result,
            geometry=geometry,
            reinforcement=reinforcement,
            pm_plot=pm_plot,
            seismic_category=getattr(pier, 'seismic_category', None)
        )

        # Campos comunes de pier
        formatted['grilla'] = pier.grilla
        formatted['axis'] = pier.eje

        # Extraer datos de flexión
        formatted['flexure'] = ResultFormatter._extract_flexure_from_result(
            result, result.dcr_max
        )

        # Configurar según tipo de servicio
        if service_used == 'wall':
            ResultFormatter._format_wall_specific(formatted, pier, result, domain_result)
        elif service_used == 'column':
            ResultFormatter._format_column_specific(formatted, pier, result, domain_result)
        else:
            ResultFormatter._format_flexure_specific(formatted, domain_result)

        # Continuidad del muro (común a todos)
        formatted['wall_continuity'] = ResultFormatter._format_wall_continuity(
            pier, continuity_info
        )

        return formatted

    @staticmethod
    def _format_wall_specific(
        formatted: Dict,
        pier: 'VerticalElement',
        result: 'OrchestrationResult',
        domain_result
    ) -> None:
        """Agrega campos específicos de muro (§18.10) al resultado formateado."""
        # Clasificación
        if hasattr(domain_result, 'classification') and domain_result.classification:
            cls = domain_result.classification
            formatted['classification'] = {
                'type': 'wall',
                'lw_tw': cls.lw_tw,
                'hw_lw': cls.hw_lw,
                'is_slender': cls.is_slender,
                'is_wall_pier': cls.is_wall_pier,
                'aci_section': result.design_behavior.aci_section
            }

        # Cortante tipo muro (extraer del domain para datos del critical combo)
        formatted['shear'] = ResultFormatter._extract_shear_from_domain(
            domain_result, result.dcr_max, 'wall'
        )
        # Agregar combo_results del ShearService (para modal sin recálculos)
        if hasattr(result, 'shear_data') and result.shear_data:
            formatted['shear']['combo_results'] = result.shear_data.get('combo_results', [])

        # Elementos de borde
        if hasattr(domain_result, 'boundary') and domain_result.boundary:
            be = domain_result.boundary
            geometry_warnings = ResultFormatter._extract_geometry_warnings(
                domain_result, 'pier'
            )
            formatted['boundary_element'] = {
                'required': be.requires_special,
                'method': be.method_used if be.requires_special else 'N/A',
                'sigma_max': be.stress_check.get('sigma_max', 0) if be.stress_check else 0,
                'sigma_limit': be.stress_check.get('limit', 0) if be.stress_check else 0,
                'length_mm': be.length_horizontal,
                'status': 'OK' if be.is_ok else 'CHECK',
                'warnings': be.warnings,
                'geometry_warnings': geometry_warnings,
            }

        # Cuantías mínimas
        if hasattr(domain_result, 'reinforcement') and domain_result.reinforcement:
            rf = domain_result.reinforcement
            formatted['reinforcement_check'] = {
                'rho_l_ok': rf.rho_l_ok,
                'rho_t_ok': rf.rho_t_ok,
                'is_ok': rf.is_ok
            }

    @staticmethod
    def _format_column_specific(
        formatted: Dict,
        pier: 'VerticalElement',
        result: 'OrchestrationResult',
        domain_result
    ) -> None:
        """Agrega campos específicos de columna (§18.7) al resultado formateado."""
        # Clasificación como pier-columna
        formatted['classification'] = {
            'type': 'wall_pier_column',
            'lw_tw': pier.length / pier.thickness if pier.thickness > 0 else 0,
            'hw_lw': pier.height / pier.length if pier.length > 0 else 0,
            'is_slender': False,
            'is_wall_pier': True,
            'aci_section': '§18.7'
        }

        # Cortante tipo columna (extraer del domain para datos del critical combo)
        formatted['shear'] = ResultFormatter._extract_shear_from_domain(
            domain_result, result.dcr_max, 'column'
        )
        # Agregar combo_results del ShearService (para modal sin recálculos)
        if hasattr(result, 'shear_data') and result.shear_data:
            formatted['shear']['combo_results'] = result.shear_data.get('combo_results', [])

        # Verificaciones sísmicas de columna
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

        longitudinal = None
        if hasattr(domain_result, 'longitudinal') and domain_result.longitudinal:
            long = domain_result.longitudinal
            longitudinal = {
                'rho': long.rho,
                'rho_ok': long.rho_min_ok and long.rho_max_ok,
                'is_ok': long.is_ok
            }

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

        formatted['seismic_column_checks'] = {
            'dimensional': dimensional,
            'longitudinal': longitudinal,
            'transverse': transverse,
        }

        # Boundary element placeholder con geometry_warnings
        geometry_warnings = ResultFormatter._extract_geometry_warnings(
            domain_result, 'column'
        )
        formatted['boundary_element'] = {
            'required': False,
            'method': 'N/A',
            'status': 'OK' if not geometry_warnings else 'CHECK',
            'warnings': [],
            'geometry_warnings': geometry_warnings,
        }

    @staticmethod
    def _format_flexure_specific(formatted: Dict, domain_result) -> None:
        """Agrega campos específicos de verificación por flexocompresión."""
        # Shear básico (sin datos detallados)
        formatted['shear']['formula_type'] = 'flexure'
        formatted['shear']['status'] = 'N/A'
        formatted['shear']['dcr'] = 0
        formatted['shear']['dcr_2'] = 0
        formatted['shear']['dcr_combined'] = 0

        # Boundary element placeholder
        geometry_warnings = ResultFormatter._extract_geometry_warnings(
            domain_result, 'pier'
        )
        formatted['boundary_element'] = {
            'required': False,
            'method': 'N/A',
            'status': 'OK' if not geometry_warnings else 'CHECK',
            'warnings': [],
            'geometry_warnings': geometry_warnings,
        }

    # =========================================================================
    # Método unificado para cualquier elemento (nueva arquitectura)
    # =========================================================================

    @staticmethod
    def format_any_element(
        element: Union['HorizontalElement', 'VerticalElement'],
        result: 'OrchestrationResult',
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """
        Formatea resultado de OrchestrationResult para CUALQUIER tipo de elemento.

        Este es el método principal para la nueva arquitectura unificada.
        Detecta el tipo de elemento y delega al formateador apropiado.
        """
        from ...domain.entities import VerticalElement, HorizontalElement, VerticalElementSource

        # PRIORIDAD: Si es strut (servicio 'strut'), usar formateador de strut
        # Esto aplica a columnas, muros, vigas pequeñas (<15cm)
        if result.service_used == 'strut':
            return ResultFormatter._format_strut_element(
                element, result, key
            )

        # Delegar según tipo de elemento
        if isinstance(element, VerticalElement):
            return ResultFormatter.format_orchestration_result(
                element, result, key, continuity_info, pm_plot
            )
        elif isinstance(element, HorizontalElement):
            # Verificar si es DROP_BEAM antes que BEAM genérico
            if element.is_drop_beam:
                return ResultFormatter._format_drop_beam_element(
                    element, result, key, pm_plot
                )
            return ResultFormatter._format_beam_element(
                element, result, key
            )

        # Fallback genérico
        return {
            'element_type': 'unknown',
            'key': key,
            'overall_status': 'OK' if result.is_ok else 'NO OK',
            'dcr_max': result.dcr_max,
        }

    @staticmethod
    def _format_column_element(
        column: 'VerticalElement',
        result: 'OrchestrationResult',
        key: str,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de Column desde OrchestrationResult."""
        domain_result = result.domain_result

        geometry = {
            'width_mm': column.depth,
            'thickness_mm': column.width,
            'height_mm': column.height,
            'fc': column.fc,
            'fy': column.fy
        }
        reinforcement = {
            'n_total_bars': column.n_total_bars,
            'n_bars_depth': column.n_bars_depth,
            'n_bars_width': column.n_bars_width,
            'diameter_long': column.diameter_long,
            'stirrup_diameter': column.stirrup_diameter,
            'stirrup_spacing': column.stirrup_spacing,
            'As_longitudinal_mm2': round(column.As_longitudinal, 0),
            'rho_longitudinal': round(column.rho_longitudinal, 4),
            'description': column.reinforcement_description
        }

        formatted = ResultFormatter._build_base_result(
            element_type='column',
            key=key,
            label=column.label,
            story=column.story,
            result=result,
            geometry=geometry,
            reinforcement=reinforcement,
            pm_plot=pm_plot,
            seismic_category=getattr(column, 'seismic_category', None)
        )

        # Extraer datos de flexión y cortante
        formatted['flexure'] = ResultFormatter._extract_flexure_from_result(
            result, result.dcr_max
        )
        formatted['shear'] = ResultFormatter._extract_shear_from_domain(
            domain_result, result.dcr_max, 'column'
        )

        # Usar helper centralizado para geometry_warnings
        geometry_warnings = ResultFormatter._extract_geometry_warnings(
            domain_result, 'column'
        )
        formatted['boundary_element'] = {
            'required': False,
            'method': 'N/A',
            'status': 'OK' if not geometry_warnings else 'CHECK',
            'warnings': [],
            'geometry_warnings': geometry_warnings,
        }

        return formatted

    @staticmethod
    def _format_strut_element(
        element: Union['VerticalElement', 'HorizontalElement'],
        result: 'OrchestrationResult',
        key: str
    ) -> Dict[str, Any]:
        """
        Formatea resultado de elemento pequeño verificado como strut no confinado.

        Aplica a columnas, muros, vigas pequeñas (<15cm) según ACI 318-25 Cap. 23.
        La barra central NO cuenta como refuerzo de compresión.

        Capacidad: Fns = 0.34 × fc' × Acs
        Factor: phi = 0.60 (diseño sísmico)
        """
        domain_result = result.domain_result

        # Obtener DCR del orchestrator (ya corregido para mostrar compresión, no 100)
        flex_data = result.flexure_data or {}
        dcr_display = flex_data.get('dcr', domain_result.dcr)

        # Obtener geometría del elemento (genérico)
        if hasattr(element, 'depth') and hasattr(element, 'width'):
            # Column
            width_mm = element.depth
            thickness_mm = element.width
            height_mm = element.height
        elif hasattr(element, 'width') and hasattr(element, 'thickness'):
            # Pier o DropBeam
            width_mm = element.width
            thickness_mm = element.thickness
            height_mm = element.height
        else:
            width_mm = 0
            thickness_mm = 0
            height_mm = 0

        geometry = {
            'width_mm': width_mm,
            'thickness_mm': thickness_mm,
            'height_mm': height_mm,
            'fc': getattr(element, 'fc', 0),
            'fy': getattr(element, 'fy', 0)
        }

        # Refuerzo simplificado para strut
        # Calcular As de la barra central (aunque no cuenta para compresión)
        import math
        diameter = getattr(element, 'diameter_long', 12)
        n_bars = getattr(element, 'n_total_bars', 1)
        As_per_bar = math.pi * (diameter / 2) ** 2  # mm²
        As_total = As_per_bar * n_bars

        reinforcement = {
            'type': 'strut_unconfined',
            'n_total_bars': n_bars,
            'n_bars_depth': 1,  # STRUT siempre 1×1
            'n_bars_width': 1,
            'diameter_long': diameter,
            'As_longitudinal_mm2': round(As_total, 0),
            'stirrup_spacing': 0,  # Sin estribos
            'note': 'Barra central como acero constructivo (no As de compresion)',
            'description': f"1phi{diameter} (strut)"
        }

        # Datos específicos de strut desde StrutCapacityResult
        strut_data = {
            'Acs_mm2': domain_result.Acs,
            'b_mm': domain_result.b,
            'h_mm': domain_result.h,
            'fce_MPa': domain_result.fce,
            'beta_s': domain_result.beta_s,
            'beta_c': domain_result.beta_c,
            'fr_MPa': domain_result.fr,
            # Capacidades
            'Fns_tonf': domain_result.Fns,
            'phi_Fns_tonf': domain_result.phi_Fns,
            'Mcr_tonfm': domain_result.Mcr,
            'phi_Mcr_tonfm': domain_result.phi_Mcr,
            # Demandas
            'Pu_tonf': domain_result.Pu,
            'Mu_tonfm': domain_result.Mu,
            # DCR (usa dcr_display que ya es el valor corregido)
            'dcr': dcr_display,
            'dcr_P': domain_result.dcr_P,
            'dcr_M': domain_result.dcr_M,
            'formula_P': 'Fns = 0.34 x fc x Acs (ACI 23.4)',
            'formula_M': 'Mcr = fr x S = 0.62√fc x bh²/6 (ACI 19.2.3)',
        }

        # Clasificación especial para strut
        classification = {
            'type': 'strut_unconfined',
            'aci_section': 'ACI 318-25 23.4',
            'description': 'Elemento pequeno como strut no confinado',
        }

        # Generar datos de diagrama P-M simplificado
        pm_plot = None
        if hasattr(domain_result, 'diagram_points') and domain_result.diagram_points:
            pm_plot = {
                'phi_Mn_values': [p.phi_Mn for p in domain_result.diagram_points],
                'phi_Pn_values': [p.phi_Pn for p in domain_result.diagram_points],
                'demand_points': [{
                    'Mu': domain_result.Mu,
                    'Pu': domain_result.Pu,
                    'combo': 'Envolvente',
                }],
                'is_strut_diagram': True,
            }

        formatted = ResultFormatter._build_base_result(
            element_type='strut',
            key=key,
            label=getattr(element, 'label', key),
            story=getattr(element, 'story', ''),
            result=result,
            geometry=geometry,
            reinforcement=reinforcement,
            pm_plot=pm_plot,  # Ahora sí incluye diagrama P-M simplificado
            seismic_category=getattr(element, 'seismic_category', None)
        )

        # Agregar datos específicos de strut
        formatted['strut'] = strut_data
        formatted['classification'] = classification

        # Info de tracción viene del orchestrator (conteo real de combinaciones)
        flex_data = result.flexure_data or {}
        has_tension = flex_data.get('has_tension', False)
        tension_combos = flex_data.get('tension_combos', 0)
        combo_results = flex_data.get('combo_results', [])
        critical_combo = flex_data.get('critical_combo', 'Envolvente')

        # DCR real de la envolvente (ya no forzamos 100 por tracción)
        dcr_display = flex_data.get('dcr', domain_result.dcr)

        # Flexocompresión para struts (campos normalizados para frontend)
        formatted['flexure'] = {
            'status': 'OK' if result.is_ok else 'NO OK',
            'note': 'Diagrama P-M simplificado (traccion=0, compresion=Fns, flexion=Mcr)',
            'dcr': dcr_display,
            'dcr_class': get_dcr_css_class(dcr_display),
            'dcr_P': domain_result.dcr_P,
            'dcr_M': domain_result.dcr_M,
            # Campos normalizados (igual que pier/column)
            'Pu': domain_result.Pu,
            'Mu': domain_result.Mu,
            'phi_Mn_at_Pu': domain_result.phi_Fns,  # Capacidad axial como referencia
            'phi_Mn_0': domain_result.phi_Mcr,  # Capacidad a flexión pura
            'critical_combo': critical_combo,
            # Campos específicos de strut (para debug/detalles)
            'phi_Fns': domain_result.phi_Fns,
            'phi_Mcr': domain_result.phi_Mcr,
            # Indicador de tracción para mostrar ⚡ en UI (conteo real de combos)
            'has_tension': has_tension,
            'tension_combos': tension_combos,
            # Resultados de TODAS las combinaciones (para modal sin recálculo)
            'combo_results': combo_results,
        }
        formatted['shear'] = {
            'status': 'N/A',
            'note': 'Struts sin estribos - cortante no verificado',
        }
        formatted['boundary_element'] = {
            'required': False,
            'method': 'N/A',
            'status': 'N/A',
            'warnings': [],
            'geometry_warnings': [],
        }

        return formatted

    @staticmethod
    def _format_beam_element(
        beam: 'HorizontalElement',
        result: 'OrchestrationResult',
        key: str,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """
        Formatea resultado de Beam (FRAME, SPANDREL o DROP_BEAM) desde OrchestrationResult.

        Unifica el formato JSON para todos los tipos de vigas, usando nomenclatura
        consistente:
        - Barras de borde (n_edge_bars, diameter_edge)
        - Estribos (stirrup_diameter, stirrup_spacing)
        - Barras laterales (n_lateral_bars, diameter_lateral, spacing_lateral)
        """
        domain_result = result.domain_result
        is_drop_beam = beam.is_drop_beam

        # Geometría unificada: ancho × peralte × luz
        geometry = {
            'width_mm': beam.width,
            'thickness_mm': beam.depth,
            'height_mm': beam.length,
            'length_mm': beam.length,
            'fc': beam.fc,
            'fy': beam.fy
        }

        # Armadura unificada
        if is_drop_beam:
            # DROP_BEAM: mapear terminología de malla a terminología de viga
            mr = beam.mesh_reinforcement
            reinforcement = {
                # Barras de borde (extremos superior e inferior)
                'n_edge_bars': mr.n_edge_bars if mr else 0,
                'diameter_edge': mr.diameter_edge if mr else 16,
                # Estribos
                'stirrup_diameter': beam.stirrup_diameter,
                'stirrup_spacing': beam.stirrup_spacing,
                # Barras laterales (distribuidas en el alma)
                'n_lateral_bars': 0,  # Calculado por espaciamiento
                'diameter_lateral': mr.diameter_v if mr else 12,
                'spacing_lateral': mr.spacing_v if mr else 200,
                # Descripción legible
                'description': beam.reinforcement_description
            }
        else:
            # FRAME/SPANDREL: armadura discreta top/bottom
            dr = beam.discrete_reinforcement
            reinforcement = {
                # Barras de borde = barras top + bottom
                'n_edge_bars': (dr.n_bars_top if dr else 0) + (dr.n_bars_bottom if dr else 0),
                'diameter_edge': max(dr.diameter_top if dr else 16, dr.diameter_bottom if dr else 16),
                # Detalle top/bottom para compatibilidad
                'n_bars_top': dr.n_bars_top if dr else 0,
                'n_bars_bottom': dr.n_bars_bottom if dr else 0,
                'diameter_top': dr.diameter_top if dr else 16,
                'diameter_bottom': dr.diameter_bottom if dr else 16,
                # Estribos
                'stirrup_diameter': beam.stirrup_diameter,
                'stirrup_spacing': beam.stirrup_spacing,
                # Barras laterales (vigas normales no suelen tener)
                'n_lateral_bars': 0,
                'diameter_lateral': 0,
                'spacing_lateral': 0,
                # Descripción legible
                'description': f"{dr.n_bars_top if dr else 0}phi{dr.diameter_top if dr else 16} + {dr.n_bars_bottom if dr else 0}phi{dr.diameter_bottom if dr else 16}"
            }

        element_type = 'drop_beam' if is_drop_beam else 'beam'
        shear_type = 'wall' if is_drop_beam else 'beam'

        formatted = ResultFormatter._build_base_result(
            element_type=element_type,
            key=key,
            label=beam.label,
            story=beam.story,
            result=result,
            geometry=geometry,
            reinforcement=reinforcement,
            pm_plot=pm_plot,
            seismic_category=getattr(beam, 'seismic_category', None)
        )

        # Extraer datos de flexión y cortante
        formatted['flexure'] = ResultFormatter._extract_flexure_from_result(
            result, result.dcr_max
        )
        formatted['shear'] = ResultFormatter._extract_shear_from_domain(
            domain_result, result.dcr_max, shear_type
        )

        # Usar helper centralizado para geometry_warnings
        geometry_warnings = ResultFormatter._extract_geometry_warnings(
            domain_result, element_type
        )
        formatted['boundary_element'] = {
            'required': False,
            'method': 'N/A',
            'status': 'OK' if not geometry_warnings else 'CHECK',
            'warnings': [],
            'geometry_warnings': geometry_warnings,
        }

        return formatted

    @staticmethod
    def _format_drop_beam_element(
        drop_beam: 'HorizontalElement',
        result: 'OrchestrationResult',
        key: str,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """
        Formatea resultado de DropBeam (alias de Beam con beam_type=DROP_BEAM).

        Delega a _format_beam_element que maneja ambos tipos.
        """
        return ResultFormatter._format_beam_element(drop_beam, result, key, pm_plot)

    # =========================================================================
    # Formateo de Capacidades (sin OrchestrationResult)
    # =========================================================================

    @staticmethod
    def format_beam_capacities(
        beam: 'HorizontalElement',
        beam_forces=None
    ) -> Dict[str, Any]:
        """
        Formatea capacidades y propiedades de una viga para la UI.

        Este método NO usa OrchestrationResult, solo formatea las propiedades
        del elemento Beam directamente.
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
        column: 'VerticalElement',
        column_forces=None
    ) -> Dict[str, Any]:
        """
        Formatea capacidades y propiedades de una columna para la UI.

        Este método NO usa OrchestrationResult, solo formatea las propiedades
        del elemento Column directamente.
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
