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

from ...domain.constants.phi_chapter21 import get_dcr_status
from ...domain.constants.reinforcement import RHO_MIN, MAX_SPACING_SEISMIC_MM

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
        Clase CSS para aplicar al valor (fs-ok, fs-warn, fs-fail)

    Usa umbrales centralizados del domain (DCR_OK=0.67, DCR_WARN=1.0).
    """
    status = get_dcr_status(dcr)  # 'ok', 'warn', 'fail'
    return f'fs-{status}'


def format_dimensions(width_mm: float, thickness_mm: float) -> str:
    """
    Formatea dimensiones en formato "espesor × ancho mm".

    Args:
        width_mm: Ancho en mm (lw para muros)
        thickness_mm: Espesor en mm (tw para muros)

    Returns:
        String formateado, ej: "200 × 3000 mm"
    """
    return f"{int(thickness_mm)} × {int(width_mm)} mm"


def format_dcr_display(dcr: float) -> str:
    """
    Formatea DCR para mostrar en UI.

    Args:
        dcr: Demand/Capacity ratio

    Returns:
        String formateado, ej: "0.85" o ">100"
    """
    if dcr > 100:
        return '>100'
    return f"{dcr:.2f}"


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
        pier: 'Pier',
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
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """
        Construye la estructura base común para todos los tipos de elementos.

        Esta función centraliza la lógica común de formateo, reduciendo
        duplicación en los métodos especializados.
        """
        overall_status = 'OK' if result.is_ok else 'NO OK'
        dcr = result.dcr_max

        # Datos de flexure base
        flexure_data = {
            'sf': 1.0 / dcr if dcr > 0 else 100.0,
            'dcr': dcr,
            'status': overall_status,
            'critical_combo': 'envelope',
            'phi_Mn_at_Pu': 0,
            'Mu': 0,
            'phi_Mn_0': 0,
            'Pu': 0,
            'phi_Pn_max': 0,
            'exceeds_axial': False,
            'has_tension': False
        }

        # Datos de shear base
        shear_data = {
            'sf': 1.0 / dcr if dcr > 0 else 100.0,
            'dcr': dcr,
            'dcr_class': get_dcr_css_class(dcr),
            'status': overall_status,
            'critical_combo': 'envelope',
            'dcr_2': dcr,
            'dcr_3': 0,
            'dcr_combined': dcr,
            'phi_Vn_2': 0,
            'phi_Vn_3': 0,
            'Vu_2': 0,
            'Vu_3': 0,
            'Vc': 0,
            'Vs': 0,
            'formula_type': element_type
        }

        # Datos de slenderness base
        slenderness_data = {
            'lambda': 0,
            'is_slender': False,
            'delta_ns': 1.0,
            'magnification_pct': 0.0
        }

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
            'warnings': result.warnings
        }

    @staticmethod
    def _extract_pier_geometry_reinforcement(pier: 'Pier') -> tuple:
        """
        Extrae geometría y refuerzo base de un Pier.

        Centraliza la lógica común para _format_wall/column/flexure_orchestration.

        Returns:
            (geometry, reinforcement) dicts
        """
        geometry = {
            'width_mm': pier.width,
            'thickness_mm': pier.thickness,
            'height_mm': pier.height,
            'fc': pier.fc,
            'fy': pier.fy
        }
        reinforcement = {
            'As_vertical_mm2': pier.As_vertical,
            'As_horizontal_mm2': pier.As_horizontal,
            'As_vertical_per_m': round(pier.As_vertical_per_m, 1),
            'As_horizontal_per_m': round(pier.As_horizontal, 1),
            'rho_vertical': round(pier.rho_vertical, 5),
            'rho_horizontal': round(pier.rho_horizontal, 5)
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
            'formula_type': formula_type
        }

        if hasattr(domain_result, 'shear') and domain_result.shear:
            sh = domain_result.shear
            dcr = getattr(sh, 'dcr', base_dcr)
            shear_data.update({
                'dcr': dcr,
                'dcr_class': get_dcr_css_class(dcr),
                'dcr_2': dcr,
                'dcr_combined': dcr,
                'phi_Vn_2': getattr(sh, 'phi_Vn', getattr(sh, 'phi_Vn_V2', 0)),
                'Vu_2': getattr(sh, 'Ve', 0),
                'Vc': getattr(sh, 'Vc', 0) if not hasattr(sh, 'capacity_V2') else (sh.capacity_V2.Vc if sh.capacity_V2 else 0),
                'Vs': getattr(sh, 'Vs', 0) if not hasattr(sh, 'capacity_V2') else (sh.capacity_V2.Vs if sh.capacity_V2 else 0),
            })
            if dcr > 0:
                shear_data['sf'] = round(1.0 / dcr, 2)

        return shear_data

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
        """
        service_used = result.service_used

        # Delegar según servicio usado
        if service_used == 'wall':
            return ResultFormatter._format_wall_orchestration(
                pier, result, key, continuity_info, pm_plot
            )
        elif service_used == 'column':
            return ResultFormatter._format_column_orchestration(
                pier, result, key, continuity_info, pm_plot
            )
        else:
            return ResultFormatter._format_flexure_orchestration(
                pier, result, key, continuity_info, pm_plot
            )

    @staticmethod
    def _format_wall_orchestration(
        pier: 'Pier',
        result: 'OrchestrationResult',
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de pier verificado como muro (§18.10)."""
        domain_result = result.domain_result

        # Extraer geometría y refuerzo usando helper
        geometry, reinforcement = ResultFormatter._extract_pier_geometry_reinforcement(pier)

        # Agregar flags de validación desde domain_result.reinforcement (§18.10.2.1)
        if hasattr(domain_result, 'reinforcement') and domain_result.reinforcement:
            rf = domain_result.reinforcement
            reinforcement.update({
                'rho_v_ok': rf.rho_l_ok,
                'rho_h_ok': rf.rho_t_ok,
                'rho_mesh_v_ok': rf.rho_l_ok,  # Para compatibilidad con frontend
                'spacing_v_ok': rf.spacing_ok,
                'spacing_h_ok': rf.spacing_ok,
                'rho_min': rf.rho_l_min,
                'max_spacing': rf.spacing_max
            })

        # Construir resultado base
        formatted = ResultFormatter._build_base_result(
            element_type='pier',
            key=key,
            label=pier.label,
            story=pier.story,
            result=result,
            geometry=geometry,
            reinforcement=reinforcement,
            pm_plot=pm_plot
        )

        # Agregar campos específicos de pier
        formatted['grilla'] = pier.grilla
        formatted['axis'] = pier.eje

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

        # Cortante específico de muros
        formatted['shear'] = ResultFormatter._extract_shear_from_domain(
            domain_result, result.dcr_max, 'wall'
        )

        # Elementos de borde
        if hasattr(domain_result, 'boundary') and domain_result.boundary:
            be = domain_result.boundary
            formatted['boundary_element'] = {
                'required': be.requires_special,
                'method': 'stress' if be.requires_special else 'N/A',
                'sigma_max': 0,
                'sigma_limit': 0,
                'length_mm': 0,
                'status': 'OK' if be.is_ok else 'CHECK'
            }

        # Cuantías mínimas
        if hasattr(domain_result, 'reinforcement') and domain_result.reinforcement:
            rf = domain_result.reinforcement
            formatted['reinforcement_check'] = {
                'rho_l_ok': rf.rho_l_ok,
                'rho_t_ok': rf.rho_t_ok,
                'is_ok': rf.is_ok
            }

        # Continuidad del muro
        formatted['wall_continuity'] = ResultFormatter._format_wall_continuity(
            pier, continuity_info
        )

        return formatted

    @staticmethod
    def _format_column_orchestration(
        pier: 'Pier',
        result: 'OrchestrationResult',
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de pier verificado como columna (§18.7)."""
        domain_result = result.domain_result

        # Extraer geometría y refuerzo usando helper
        geometry, reinforcement = ResultFormatter._extract_pier_geometry_reinforcement(pier)

        # Para columnas §18.7, agregar constantes de refuerzo para el frontend
        # (las columnas tienen requisitos diferentes a muros)
        reinforcement.update({
            'rho_v_ok': True,  # Columnas no usan mismo check de muro
            'rho_h_ok': True,
            'rho_mesh_v_ok': True,
            'spacing_v_ok': True,
            'spacing_h_ok': True,
            'rho_min': RHO_MIN,  # domain/constants/reinforcement.py
            'max_spacing': MAX_SPACING_SEISMIC_MM
        })

        # Construir resultado base
        formatted = ResultFormatter._build_base_result(
            element_type='pier',
            key=key,
            label=pier.label,
            story=pier.story,
            result=result,
            geometry=geometry,
            reinforcement=reinforcement,
            pm_plot=pm_plot
        )

        # Agregar campos específicos de pier
        formatted['grilla'] = pier.grilla
        formatted['axis'] = pier.eje

        # Clasificación como pier-columna
        formatted['classification'] = {
            'type': 'wall_pier_column',
            'lw_tw': pier.width / pier.thickness if pier.thickness > 0 else 0,
            'hw_lw': pier.height / pier.width if pier.width > 0 else 0,
            'is_slender': False,
            'is_wall_pier': True,
            'aci_section': '§18.7'
        }

        # Cortante específico de columnas
        formatted['shear'] = ResultFormatter._extract_shear_from_domain(
            domain_result, result.dcr_max, 'column'
        )

        # Verificaciones dimensionales
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

        formatted['seismic_column_checks'] = {
            'dimensional': dimensional,
            'longitudinal': longitudinal,
            'transverse': transverse,
        }

        # Continuidad del muro
        formatted['wall_continuity'] = ResultFormatter._format_wall_continuity(
            pier, continuity_info
        )

        return formatted

    @staticmethod
    def _format_flexure_orchestration(
        pier: 'Pier',
        result: 'OrchestrationResult',
        key: str,
        continuity_info: 'WallContinuityInfo' = None,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de pier verificado por flexocompresión."""
        domain_result = result.domain_result

        # Extraer geometría y refuerzo usando helper
        geometry, reinforcement = ResultFormatter._extract_pier_geometry_reinforcement(pier)

        # Para verificación por flexocompresión, agregar valores por defecto
        reinforcement.update({
            'rho_v_ok': True,
            'rho_h_ok': True,
            'rho_mesh_v_ok': True,
            'spacing_v_ok': True,
            'spacing_h_ok': True,
            'rho_min': RHO_MIN,  # domain/constants/reinforcement.py
            'max_spacing': MAX_SPACING_SEISMIC_MM
        })

        # Construir resultado base
        formatted = ResultFormatter._build_base_result(
            element_type='pier',
            key=key,
            label=pier.label,
            story=pier.story,
            result=result,
            geometry=geometry,
            reinforcement=reinforcement,
            pm_plot=pm_plot
        )

        # Agregar campos específicos de pier
        formatted['grilla'] = pier.grilla
        formatted['axis'] = pier.eje

        # Actualizar flexure con SF del domain_result si existe
        if isinstance(domain_result, dict) and 'SF' in domain_result:
            formatted['flexure']['sf'] = domain_result['SF']

        # Shear básico para flexure (sin datos detallados)
        formatted['shear']['formula_type'] = 'flexure'
        formatted['shear']['status'] = 'N/A'
        formatted['shear']['dcr'] = 0
        formatted['shear']['dcr_2'] = 0
        formatted['shear']['dcr_combined'] = 0

        # Continuidad del muro
        formatted['wall_continuity'] = ResultFormatter._format_wall_continuity(
            pier, continuity_info
        )

        return formatted

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
        """
        from ...domain.entities import Pier, Column, Beam, DropBeam

        # Delegar según tipo de elemento
        if isinstance(element, Pier):
            return ResultFormatter.format_orchestration_result(
                element, result, key, continuity_info, pm_plot
            )
        elif isinstance(element, Column):
            return ResultFormatter._format_column_element(
                element, result, key, pm_plot
            )
        elif isinstance(element, Beam):
            return ResultFormatter._format_beam_element(
                element, result, key
            )
        elif isinstance(element, DropBeam):
            return ResultFormatter._format_drop_beam_element(
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
    def _format_column_element(
        column: 'Column',
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
            pm_plot=pm_plot
        )

        # Cortante específico de columnas
        formatted['shear'] = ResultFormatter._extract_shear_from_domain(
            domain_result, result.dcr_max, 'column'
        )

        return formatted

    @staticmethod
    def _format_beam_element(
        beam: 'Beam',
        result: 'OrchestrationResult',
        key: str
    ) -> Dict[str, Any]:
        """Formatea resultado de Beam desde OrchestrationResult."""
        # Para beams: width_m=width, thickness_m=depth, height_m=length
        geometry = {
            'width_mm': beam.width,
            'thickness_mm': beam.depth,
            'height_mm': beam.length,
            'fc': beam.fc,
            'fy': beam.fy
        }
        reinforcement = {
            'n_bars_top': beam.n_bars_top,
            'n_bars_bottom': beam.n_bars_bottom,
            'diameter_top': beam.diameter_top,
            'diameter_bottom': beam.diameter_bottom,
            'stirrup_diameter': beam.stirrup_diameter,
            'stirrup_spacing': beam.stirrup_spacing,
            'description': f"{beam.n_bars_top}phi{beam.diameter_top} + {beam.n_bars_bottom}phi{beam.diameter_bottom}"
        }

        formatted = ResultFormatter._build_base_result(
            element_type='beam',
            key=key,
            label=beam.label,
            story=beam.story,
            result=result,
            geometry=geometry,
            reinforcement=reinforcement,
            pm_plot=None
        )

        formatted['shear']['formula_type'] = 'beam'

        return formatted

    @staticmethod
    def _format_drop_beam_element(
        drop_beam: 'DropBeam',
        result: 'OrchestrationResult',
        key: str,
        pm_plot: str = None
    ) -> Dict[str, Any]:
        """Formatea resultado de DropBeam desde OrchestrationResult."""
        domain_result = result.domain_result

        # Para drop beams: width_m=length (luz libre), thickness_m=thickness (ancho tributario), height_m=width (espesor losa)
        geometry = {
            'width_mm': drop_beam.length,
            'thickness_mm': drop_beam.thickness,
            'height_mm': drop_beam.width,
            'fc': drop_beam.fc,
            'fy': drop_beam.fy
        }
        reinforcement = {
            'As_vertical_mm2': drop_beam.As_vertical,
            'As_edge_total': drop_beam.As_edge_total,
            'n_edge_bars': drop_beam.n_edge_bars,
            'diameter_edge': drop_beam.diameter_edge,
            'rho_vertical': round(drop_beam.rho_vertical, 5),
            'description': drop_beam.reinforcement_description
        }

        formatted = ResultFormatter._build_base_result(
            element_type='drop_beam',
            key=key,
            label=drop_beam.label,
            story=drop_beam.story,
            result=result,
            geometry=geometry,
            reinforcement=reinforcement,
            pm_plot=pm_plot
        )

        # Cortante específico de drop beams (usa formato wall)
        formatted['shear'] = ResultFormatter._extract_shear_from_domain(
            domain_result, result.dcr_max, 'wall'
        )

        return formatted

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
