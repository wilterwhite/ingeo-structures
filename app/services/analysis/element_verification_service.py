# app/services/analysis/element_service.py
"""
Servicio unificado de verificacion para elementos estructurales.

Reemplaza BeamService, ColumnService y ElementAnalyzer con un unico
punto de entrada que clasifica automaticamente el elemento y aplica
las verificaciones correspondientes segun ACI 318-25.
"""
import math
from typing import Dict, Any, Optional, Union, TYPE_CHECKING

from ...domain.entities import Beam, Column, Pier, DropBeam
from ...domain.entities import BeamForces, ColumnForces, PierForces, DropBeamForces

from .flexocompression_service import FlexocompressionService
from .shear_service import ShearService
from .element_classifier import ElementClassifier, ElementType
from .verification_config import get_config, VerificationConfig
from ...domain.chapter11 import ReinforcementLimitsService
from ...domain.chapter18 import (
    SeismicReinforcementService,
    SeismicBeamService,
    SeismicColumnService,
    NonSfrsService,
    DuctileCoupledWallService,
    SeismicCategory,
)
from ...domain.shear import calculate_simple_shear_capacity
from .verification_result import (
    ElementVerificationResult,
    FlexureResult,
    ShearResult,
    SlendernessResult,
    WallChecks,
    WallClassification,
    BoundaryResult,
    EndZonesResult,
    MinReinforcementResult,
    # Verificaciones sismicas
    SeismicBeamChecks,
    SeismicBeamDimensionalResult,
    SeismicBeamLongitudinalResult,
    SeismicBeamTransverseResult,
    SeismicBeamShearResult,
    SeismicColumnChecks,
    SeismicColumnDimensionalResult,
    SeismicColumnStrongResult,
    SeismicColumnLongitudinalResult,
    SeismicColumnTransverseResult,
    SeismicColumnShearDetailedResult,
)

from ...domain.constants.units import N_TO_TONF
from .formatting import format_safety_factor

if TYPE_CHECKING:
    from .proposal_service import ProposalService
    from ..presentation.plot_generator import PlotGenerator
    from ..parsing.session_manager import SessionManager


# Wrapper para compatibilidad con codigo existente (usa float, no string)
def _format_sf(value: float) -> float:
    """Formatea SF: convierte inf a 100.0 para evitar problemas JSON."""
    return format_safety_factor(value, as_string=False)


class ElementService:
    """
    Servicio unificado de verificacion para cualquier elemento estructural.

    Soporta:
    - Beam (vigas frame y spandrels)
    - Column (columnas frame)
    - Pier (muros shell)

    Clasifica automaticamente el elemento y aplica las verificaciones
    correspondientes segun ACI 318-25.

    Uso:
        service = ElementService()
        result = service.verify(beam, beam_forces)
        result = service.verify(column, column_forces)
        result = service.verify(pier, pier_forces, generate_plot=True)
    """

    def __init__(
        self,
        flexocompression_service: Optional[FlexocompressionService] = None,
        shear_service: Optional[ShearService] = None,
        proposal_service: Optional['ProposalService'] = None,
        plot_generator: Optional['PlotGenerator'] = None,
        session_manager: Optional['SessionManager'] = None
    ):
        """
        Inicializa el servicio.

        Args:
            flexocompression_service: Servicio de flexocompresion (opcional)
            shear_service: Servicio de cortante (opcional)
            proposal_service: Servicio de propuestas de diseno (opcional)
            plot_generator: Generador de graficos P-M (opcional)
            session_manager: Gestor de sesiones para Mpr de vigas (opcional)
        """
        self._flexo = flexocompression_service or FlexocompressionService()
        self._shear = shear_service or ShearService()
        self._classifier = ElementClassifier()
        self._reinforcement_limits = ReinforcementLimitsService()
        self._seismic_reinforcement = SeismicReinforcementService()
        self._proposal_service = proposal_service
        self._plot_generator = plot_generator
        self._session_manager = session_manager

        # Servicios sismicos chapter18
        self._seismic_beam = SeismicBeamService()
        self._seismic_column = SeismicColumnService()
        self._non_sfrs = NonSfrsService()
        self._coupled_wall = DuctileCoupledWallService()

    # =========================================================================
    # METODO PRINCIPAL
    # =========================================================================

    def verify(
        self,
        element: Union[Beam, Column, Pier, DropBeam],
        forces: Optional[Union[BeamForces, ColumnForces, PierForces, DropBeamForces]],
        *,
        generate_plot: bool = False,
        moment_axis: str = 'M3',
        angle_deg: float = 0,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        lambda_factor: float = 1.0,
        **kwargs
    ) -> ElementVerificationResult:
        """
        Verificacion completa de cualquier elemento estructural.

        Args:
            element: Beam, Column o Pier a verificar
            forces: Fuerzas correspondientes al elemento
            generate_plot: Si generar grafico P-M (default False)
            moment_axis: Eje de momento ('M2', 'M3', 'SRSS')
            angle_deg: Angulo para momento combinado
            hwcs: Altura desde base critica (muros)
            hn_ft: Altura de piso (muros)
            lambda_factor: Factor lambda para concreto liviano
            **kwargs: Parametros adicionales

        Returns:
            ElementVerificationResult con todas las verificaciones
        """
        # 1. Clasificar elemento
        element_type = self._classifier.classify(element)
        config = get_config(element_type)

        # 2. Verificacion de flexion
        flexure = self._check_flexure(element, forces, config, moment_axis)

        # 3. Verificacion de cortante
        shear = self._check_shear(element, forces, config, element_type, lambda_factor)

        # 4. Verificaciones sismicas para vigas y columnas
        seismic_beam = None
        seismic_column = None

        if isinstance(element, Beam) and getattr(element, 'is_seismic', False):
            seismic_beam = self._check_seismic_beam(element, forces, lambda_factor)

        if isinstance(element, Column) and getattr(element, 'is_seismic', False):
            seismic_column = self._check_seismic_column(element, forces, lambda_factor)

        # 5. Verificaciones adicionales para muros
        wall_checks = None
        if element_type.is_wall:
            wall_checks = self._check_wall_requirements(
                element, forces, config, element_type,
                hwcs=hwcs, hn_ft=hn_ft
            )

        # 6. Calcular estado general
        overall_status = 'OK'
        if flexure.status != 'OK' or shear.status != 'OK':
            overall_status = 'NO OK'

        # Verificar checks de muro
        if wall_checks and self._wall_checks_failed(wall_checks):
            overall_status = 'NO OK'

        # Verificar checks sismicos
        if seismic_beam and not seismic_beam.overall_ok:
            overall_status = 'NO OK'
        if seismic_column and not seismic_column.overall_ok:
            overall_status = 'NO OK'

        # SF minimo
        overall_sf = min(
            flexure.sf if not math.isinf(flexure.sf) else 100.0,
            shear.sf if not math.isinf(shear.sf) else 100.0
        )

        # 7. Grafico P-M (opcional)
        pm_plot = None
        if generate_plot:
            pm_plot = self._generate_pm_plot(element, forces, moment_axis)

        # 8. Info del elemento
        element_info = self._get_element_info(element, element_type)

        return ElementVerificationResult(
            element_type=element_type,
            flexure=flexure,
            shear=shear,
            overall_status=overall_status,
            overall_sf=overall_sf,
            seismic_beam=seismic_beam,
            seismic_column=seismic_column,
            wall_checks=wall_checks,
            pm_plot=pm_plot,
            element_info=element_info,
        )

    # =========================================================================
    # FLEXION
    # =========================================================================

    def _check_flexure(
        self,
        element: Union[Beam, Column, Pier],
        forces: Optional[Union[BeamForces, ColumnForces, PierForces]],
        config: VerificationConfig,
        moment_axis: str = 'M3'
    ) -> FlexureResult:
        """Verificacion de flexion/flexocompresion."""

        # Resultado por defecto sin fuerzas
        if not forces or not getattr(forces, 'combinations', None):
            return FlexureResult(
                sf=100.0,
                status='OK',
                design_type='pure_flexure',
                phi_Mn=0.0,
                Mu=0.0,
                Pu=0.0,
                critical_combo='N/A',
                aci_reference='ACI 318-25'
            )

        # Determinar tipo de diseno
        design_type = 'flexocompression'
        has_significant_axial = False

        if config.check_axial_threshold:
            # Para vigas: verificar umbral Ag*f'c/divisor
            has_significant_axial = self._has_significant_axial(
                element, forces, config.axial_threshold_divisor
            )
            design_type = 'flexocompression' if has_significant_axial else 'pure_flexure'

        # Usar FlexocompressionService
        result = self._flexo.check_flexure(
            element, forces,
            moment_axis=moment_axis,
            direction='primary',
            k=config.k_factor,
            braced=config.braced
        )

        # Extraer datos de esbeltez
        slenderness = None
        if 'slenderness' in result:
            sl = result['slenderness']
            slenderness = SlendernessResult(
                lambda_ratio=sl.get('lambda', 0),
                is_slender=sl.get('is_slender', False),
                delta_ns=sl.get('delta_ns', 1.0),
                k=config.k_factor,
            )

        # Construir warning para vigas con axial significativo
        warning = ""
        if has_significant_axial:
            warning = "Viga con axial significativo: verificar confinamiento §18.7.5.2-18.7.5.4"

        # Determinar referencia ACI
        aci_ref = self._get_flexure_aci_ref(design_type, has_significant_axial)

        return FlexureResult(
            sf=_format_sf(result.get('sf', 100.0)),
            status=result.get('status', 'OK'),
            design_type=design_type,
            phi_Mn=round(result.get('phi_Mn_0', 0), 2),
            Mu=round(result.get('Mu', 0), 2),
            Pu=round(result.get('Pu', 0), 2),
            critical_combo=result.get('critical_combo', 'N/A'),
            phi_Mn_at_Pu=round(result.get('phi_Mn_at_Pu', 0), 2),
            phi_Pn_max=round(result.get('phi_Pn_max', 0), 2),
            exceeds_axial=result.get('exceeds_axial', False),
            has_tension=result.get('has_tension', False),
            has_significant_axial=has_significant_axial,
            slenderness=slenderness,
            warning=warning,
            aci_reference=aci_ref,
        )

    def _has_significant_axial(
        self,
        element: Union[Beam, Column, Pier],
        forces: Union[BeamForces, ColumnForces, PierForces],
        divisor: float = 10.0
    ) -> bool:
        """Verifica si Pu >= Ag*f'c/divisor."""
        Ag = element.Ag  # mm2
        fc = element.fc  # MPa
        # Umbral en tonf
        threshold_tonf = (Ag * fc / divisor) / 1000 / 9.80665

        # Obtener Pu maximo
        if hasattr(forces, 'get_envelope'):
            envelope = forces.get_envelope()
            Pu_max = max(
                abs(envelope.get('P_max', 0)),
                abs(envelope.get('P_min', 0))
            )
        else:
            Pu_max = 0

        return Pu_max >= threshold_tonf

    def _get_flexure_aci_ref(self, design_type: str, has_significant_axial: bool) -> str:
        """Obtiene referencia ACI para flexion."""
        if design_type == 'pure_flexure':
            return 'ACI 318-25 §9.5'
        elif has_significant_axial:
            return 'ACI 318-25 §18.6.4.6'
        else:
            return 'ACI 318-25 §22.4'

    # =========================================================================
    # CORTANTE
    # =========================================================================

    def _check_shear(
        self,
        element: Union[Beam, Column, Pier],
        forces: Optional[Union[BeamForces, ColumnForces, PierForces]],
        config: VerificationConfig,
        element_type: ElementType,
        lambda_factor: float = 1.0
    ) -> ShearResult:
        """Verificacion de cortante segun metodo configurado."""

        if config.shear_method == 'simple':
            return self._check_shear_simple(element, forces)
        elif config.shear_method == 'srss':
            return self._check_shear_srss(element, forces, element_type, config)
        else:  # 'amplified'
            return self._check_shear_amplified(element, forces, lambda_factor)

    def _check_shear_simple(
        self,
        element: Union[Beam, Column, Pier],
        forces: Optional[Union[BeamForces, ColumnForces, PierForces]]
    ) -> ShearResult:
        """Cortante simple V2 (para vigas)."""
        # Propiedades del elemento
        bw = element.bw if hasattr(element, 'bw') else element.width
        d = element.d if hasattr(element, 'd') else element.depth - element.cover

        # Obtener Av y s si tiene estribos
        Av = getattr(element, 'Av', 0.0)
        s = getattr(element, 'stirrup_spacing', 0.0)

        # Usar funcion de dominio para calcular capacidad
        capacity = calculate_simple_shear_capacity(
            bw=bw, d=d, fc=element.fc, fy=element.fy, Av=Av, s=s
        )

        # Demanda
        Vu = 0.0
        critical_combo = 'N/A'
        if forces and hasattr(forces, 'combinations'):
            for combo in forces.combinations:
                V = abs(combo.V2) if hasattr(combo, 'V2') else 0
                if V > Vu:
                    Vu = V
                    critical_combo = combo.name

        # Verificacion
        dcr = Vu / capacity.phi_Vn if capacity.phi_Vn > 0 else float('inf')
        sf = capacity.phi_Vn / Vu if Vu > 0 else float('inf')
        status = 'OK' if sf >= 1.0 else 'NO OK'

        return ShearResult(
            sf=_format_sf(sf),
            status=status,
            method='simple',
            critical_combo=critical_combo,
            phi_Vn_2=round(capacity.phi_Vn, 2),
            Vu_2=round(Vu, 2),
            dcr_2=round(dcr, 3),
            Vc=round(capacity.Vc, 2),
            Vs=round(capacity.Vs, 2),
            Vs_max=round(capacity.Vs_max, 2),
            aci_reference=capacity.aci_reference,
        )

    def _check_shear_srss(
        self,
        element: Union[Beam, Column, Pier],
        forces: Optional[Union[BeamForces, ColumnForces, PierForces]],
        element_type: ElementType,
        config: VerificationConfig
    ) -> ShearResult:
        """Cortante V2-V3 con SRSS (para columnas)."""

        # Usar ShearService para columnas
        if isinstance(element, Column):
            result = self._shear.check_column_shear(element, forces)
        elif isinstance(element, Pier) and element_type.is_wall_pier:
            # Convertir Pier a Column virtual para verificacion tipo columna
            result = self._shear.check_column_shear_from_pier(element, forces)
        else:
            # Fallback a cortante simple
            return self._check_shear_simple(element, forces)

        # Extraer resultados
        sf_2 = 1.0 / result.get('dcr_2', 1) if result.get('dcr_2', 0) > 0 else float('inf')
        sf_3 = 1.0 / result.get('dcr_3', 1) if result.get('dcr_3', 0) > 0 else float('inf')
        dcr_combined = result.get('dcr_combined', 0)
        sf_combined = 1.0 / dcr_combined if dcr_combined > 0 else float('inf')

        status = 'OK' if sf_combined >= 1.0 else 'NO OK'

        return ShearResult(
            sf=_format_sf(sf_combined),
            status=status,
            method='srss',
            critical_combo=result.get('critical_combo', 'N/A'),
            phi_Vn_2=round(result.get('phi_Vn_2', 0), 2),
            Vu_2=round(result.get('Vu_2', 0), 2),
            dcr_2=round(result.get('dcr_2', 0), 3),
            phi_Vn_3=round(result.get('phi_Vn_3', 0), 2),
            Vu_3=round(result.get('Vu_3', 0), 2),
            dcr_3=round(result.get('dcr_3', 0), 3),
            dcr_combined=round(dcr_combined, 3),
            sf_combined=_format_sf(sf_combined),
            Vc=round(result.get('Vc', 0), 2),
            Vs=round(result.get('Vs', 0), 2),
            aci_reference='ACI 318-25 §22.5',
        )

    def _check_shear_amplified(
        self,
        element: Union[Beam, Column, Pier],
        forces: Optional[Union[BeamForces, ColumnForces, PierForces]],
        lambda_factor: float = 1.0
    ) -> ShearResult:
        """Cortante amplificado para muros (§18.10.3.3)."""

        if not isinstance(element, Pier):
            return self._check_shear_simple(element, forces)

        # Usar ShearService para muros
        result = self._shear.check_shear(element, forces, lambda_factor=lambda_factor)

        dcr_combined = result.get('dcr_combined', 0)
        sf = 1.0 / dcr_combined if dcr_combined > 0 else float('inf')
        status = 'OK' if sf >= 1.0 else 'NO OK'

        return ShearResult(
            sf=_format_sf(sf),
            status=status,
            method='amplified',
            critical_combo=result.get('critical_combo', 'N/A'),
            phi_Vn_2=round(result.get('phi_Vn_2', 0), 2),
            Vu_2=round(result.get('Vu_2', 0), 2),
            dcr_2=round(result.get('dcr_2', 0), 3),
            phi_Vn_3=round(result.get('phi_Vn_3', 0), 2),
            Vu_3=round(result.get('Vu_3', 0), 2),
            dcr_3=round(result.get('dcr_3', 0), 3),
            dcr_combined=round(dcr_combined, 3),
            sf_combined=_format_sf(sf),
            Vc=round(result.get('Vc', 0), 2),
            Vs=round(result.get('Vs', 0), 2),
            Ve=round(result.get('Ve', 0), 2) if 'Ve' in result else None,
            omega_v=result.get('omega_v'),
            aci_reference='ACI 318-25 §18.10.4',
        )

    # =========================================================================
    # VERIFICACIONES ADICIONALES PARA MUROS
    # =========================================================================

    def _check_wall_requirements(
        self,
        element: Pier,
        forces: Optional[PierForces],
        config: VerificationConfig,
        element_type: ElementType,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> WallChecks:
        """Verificaciones adicionales para muros §18.10."""

        classification = None
        amplification = None
        boundary = None
        end_zones = None
        min_reinforcement = None

        # Clasificacion §18.10.8
        if config.check_classification:
            info = self._classifier.get_classification_info(element)
            classification = WallClassification(
                type=info['type'],
                lw_tw=info.get('lw_tw', 0),
                hw_lw=info.get('hw_lw', 0),
                aci_section=info['aci_section'],
                is_wall_pier=info.get('is_wall_pier', False),
            )

        # Amplificacion §18.10.3.3
        if config.check_amplification and forces:
            # Obtener Vu máximo de las fuerzas
            Vu_max = 0
            if hasattr(forces, 'combinations') and forces.combinations:
                for combo in forces.combinations:
                    Vu = abs(getattr(combo, 'V2', 0))
                    if Vu > Vu_max:
                        Vu_max = Vu
            amp_result = self._shear.get_amplification_dict(element, Vu_max, hwcs=hwcs, hn_ft=hn_ft)
            amplification = amp_result

        # Elementos de borde §18.10.6
        if config.check_boundary and forces:
            # Extraer Pu y Mu críticos de las fuerzas
            Pu_critical = 0
            Mu_critical = 0
            if hasattr(forces, 'combinations') and forces.combinations:
                for combo in forces.combinations:
                    Pu = abs(getattr(combo, 'P', 0))
                    Mu = abs(getattr(combo, 'M3', 0))
                    if Mu > Mu_critical:
                        Mu_critical = Mu
                        Pu_critical = Pu
            boundary_result = self._shear.get_boundary_element_dict(element, Pu_critical, Mu_critical)
            if boundary_result:
                boundary = BoundaryResult(
                    required=boundary_result.get('required', False),
                    method=boundary_result.get('method', ''),
                    sigma_max=boundary_result.get('stress_check', {}).get('sigma_max', 0),
                    sigma_limit=boundary_result.get('stress_check', {}).get('limit', 0),
                    length_mm=boundary_result.get('dimensions', {}).get('length_horizontal_mm', 0),
                    status='OK' if not boundary_result.get('required', False) else 'CHECK',
                    aci_reference='ACI 318-25 §18.10.6',
                )

        # Zonas de extremo §18.10.2.4
        if config.check_end_zones and hasattr(element, 'height') and hasattr(element, 'width'):
            hw_lw = element.height / element.width if element.width > 0 else 0
            if hw_lw >= 2.0:
                # Usar servicio de chapter18 para calcular rho_min = 6*sqrt(f'c)/fy
                rho_end_zone = self._seismic_reinforcement.calculate_end_zone_rho_min(
                    element.fc, element.fy
                )
                end_zones = EndZonesResult(
                    applies=True,
                    hw_lw=round(hw_lw, 2),
                    rho_min=round(rho_end_zone, 5),
                    status='CHECK',
                )
            else:
                end_zones = EndZonesResult(
                    applies=False,
                    hw_lw=round(hw_lw, 2),
                    status='N/A',
                )

        # Cuantia minima §18.10.2.1 (sismico) o §11.6.1 (no sismico)
        if config.check_min_reinforcement:
            rho_v = getattr(element, 'rho_vertical', 0)
            rho_h = getattr(element, 'rho_horizontal', 0)
            is_seismic = getattr(element, 'is_seismic', True)

            if is_seismic:
                # Muros sismicos especiales §18.10.2.1: rho_min = 0.0025
                rho_v_min = 0.0025
                rho_h_min = 0.0025
            else:
                # Muros no sismicos: usar Tabla 11.6.1 via servicio de dominio
                diameter_v = getattr(element, 'diameter_v', 8)
                diameter_h = getattr(element, 'diameter_h', 8)
                rho_h_min, rho_v_min = self._reinforcement_limits.get_min_reinforcement_low_shear(
                    diameter_v_mm=diameter_v,
                    diameter_h_mm=diameter_h,
                    fy_mpa=element.fy,
                    is_precast=False
                )

            min_reinforcement = MinReinforcementResult(
                rho_v_min=rho_v_min,
                rho_h_min=rho_h_min,
                rho_v_actual=round(rho_v, 5),
                rho_h_actual=round(rho_h, 5),
                rho_v_ok=rho_v >= rho_v_min,
                rho_h_ok=rho_h >= rho_h_min,
                spacing_max=457.0,  # 18 in
                status='OK' if (rho_v >= rho_v_min and rho_h >= rho_h_min) else 'NO OK',
            )

        return WallChecks(
            classification=classification,
            amplification=amplification,
            boundary=boundary,
            end_zones=end_zones,
            min_reinforcement=min_reinforcement,
        )

    def _wall_checks_failed(self, wall_checks: WallChecks) -> bool:
        """Verifica si alguna verificacion de muro falla."""
        if wall_checks.boundary and wall_checks.boundary.status == 'NO OK':
            return True
        if wall_checks.min_reinforcement and wall_checks.min_reinforcement.status == 'NO OK':
            return True
        if wall_checks.end_zones and wall_checks.end_zones.status == 'NO OK':
            return True
        return False

    # =========================================================================
    # UTILIDADES
    # =========================================================================

    def _generate_pm_plot(
        self,
        element: Union[Beam, Column, Pier],
        forces: Optional[Union[BeamForces, ColumnForces, PierForces]],
        moment_axis: str = 'M3'
    ) -> Optional[str]:
        """Genera grafico P-M en base64."""
        try:
            from ..plotting import PlotGenerator
            plot_gen = PlotGenerator()
            return plot_gen.generate_pm_diagram(element, forces, moment_axis)
        except Exception:
            return None

    def _get_element_info(
        self,
        element: Union[Beam, Column, Pier],
        element_type: ElementType
    ) -> Dict[str, Any]:
        """Obtiene informacion basica del elemento."""
        info = {
            'type': element_type.value,
            'label': getattr(element, 'label', ''),
            'story': getattr(element, 'story', ''),
            'fc_MPa': element.fc,
            'fy_MPa': element.fy,
        }

        # Dimensiones segun tipo
        if isinstance(element, Beam):
            info['width_mm'] = element.width
            info['depth_mm'] = element.depth
            info['length_mm'] = element.length
        elif isinstance(element, Column):
            info['depth_mm'] = element.depth
            info['width_mm'] = element.width
            info['height_mm'] = element.height
        elif isinstance(element, Pier):
            info['width_mm'] = element.width  # lw
            info['thickness_mm'] = element.thickness  # tw
            info['height_mm'] = element.height  # hw

        return info

    # =========================================================================
    # METODOS DE CONVENIENCIA
    # =========================================================================

    def verify_beam(
        self,
        beam: Beam,
        forces: Optional[BeamForces],
        **kwargs
    ) -> ElementVerificationResult:
        """Alias para verificar una viga."""
        return self.verify(beam, forces, **kwargs)

    def verify_column(
        self,
        column: Column,
        forces: Optional[ColumnForces],
        **kwargs
    ) -> ElementVerificationResult:
        """Alias para verificar una columna."""
        return self.verify(column, forces, **kwargs)

    def verify_pier(
        self,
        pier: Pier,
        forces: Optional[PierForces],
        **kwargs
    ) -> ElementVerificationResult:
        """Alias para verificar un muro/pier."""
        return self.verify(pier, forces, **kwargs)

    def verify_drop_beam(
        self,
        drop_beam: DropBeam,
        forces: Optional[DropBeamForces],
        **kwargs
    ) -> ElementVerificationResult:
        """Alias para verificar una viga capitel."""
        return self.verify(drop_beam, forces, **kwargs)

    def verify_all(
        self,
        elements: Dict[str, Union[Beam, Column, Pier]],
        forces: Dict[str, Union[BeamForces, ColumnForces, PierForces]],
        **kwargs
    ) -> Dict[str, ElementVerificationResult]:
        """
        Verifica multiples elementos.

        Args:
            elements: Dict[key, element]
            forces: Dict[key, forces]

        Returns:
            Dict[key, ElementVerificationResult]
        """
        results = {}
        for key, element in elements.items():
            element_forces = forces.get(key)
            results[key] = self.verify(element, element_forces, **kwargs)
        return results

    def get_summary(
        self,
        results: Dict[str, ElementVerificationResult]
    ) -> Dict[str, Any]:
        """
        Genera resumen de verificaciones.

        Args:
            results: Resultados de verify_all()

        Returns:
            Dict con estadisticas
        """
        total = len(results)
        ok_count = sum(1 for r in results.values() if r.is_ok)
        fail_count = total - ok_count

        min_sf = float('inf')
        critical_key = None

        for key, result in results.items():
            if result.overall_sf < min_sf:
                min_sf = result.overall_sf
                critical_key = key

        return {
            'total': total,
            'ok_count': ok_count,
            'fail_count': fail_count,
            'pass_rate': round(ok_count / total * 100, 1) if total > 0 else 100,
            'min_sf': round(min_sf, 2) if not math.isinf(min_sf) else ">100",
            'critical_element': critical_key,
        }

    # =========================================================================
    # VERIFICACIONES SISMICAS §18.6 y §18.7
    # =========================================================================

    def _check_seismic_beam(
        self,
        beam: Beam,
        forces: Optional[BeamForces],
        lambda_factor: float = 1.0
    ) -> Optional[SeismicBeamChecks]:
        """
        Verificacion sismica de vigas segun §18.6.

        Llama al SeismicBeamService del dominio para realizar todas
        las verificaciones aplicables.
        """
        try:
            # Obtener Vu de las fuerzas
            Vu = 0.0
            Pu = 0.0
            if forces and hasattr(forces, 'combinations'):
                for combo in forces.combinations:
                    V = abs(getattr(combo, 'V2', 0))
                    if V > Vu:
                        Vu = V
                    P = abs(getattr(combo, 'P', 0))
                    if P > Pu:
                        Pu = P

            # Calcular Mpr si no estan definidos
            Mpr_left = beam.Mpr_left
            Mpr_right = beam.Mpr_right
            if Mpr_left is None or Mpr_right is None:
                Mpr_neg, Mpr_pos = self._flexo.calculate_Mpr(beam)
                Mpr_left = Mpr_neg if Mpr_left is None else Mpr_left
                Mpr_right = Mpr_pos if Mpr_right is None else Mpr_right

            # Llamar al servicio de dominio
            db_long = min(beam.diameter_top, beam.diameter_bottom)

            result = self._seismic_beam.verify_beam(
                # Geometria
                bw=beam.width,
                h=beam.depth,
                d=beam.d,
                ln=beam.ln_calculated,
                cover=beam.cover,
                # Materiales
                fc=beam.fc,
                fy=beam.fy,
                fyt=beam.fy,  # Asume mismo fy para transversal
                # Refuerzo longitudinal
                As_top=beam.As_top,
                As_bottom=beam.As_bottom,
                n_bars_top=beam.n_bars_top,
                n_bars_bottom=beam.n_bars_bottom,
                db_long=db_long,
                # Refuerzo transversal
                s_in_zone=beam.stirrup_spacing,
                s_outside_zone=beam.stirrup_spacing,
                Av=beam.Av,
                first_hoop_distance=50,  # Default 50mm
                hx=beam.hx,
                # Fuerzas
                Vu=Vu,
                Mpr_left=Mpr_left,
                Mpr_right=Mpr_right,
                Pu=Pu,
                # Opciones
                category=SeismicCategory.SPECIAL,
                lambda_factor=lambda_factor,
            )

            # Convertir resultado del dominio a dataclass de servicio
            return self._convert_beam_result(result)

        except Exception as e:
            # Si hay error, retornar None y no bloquear verificacion
            import logging
            logging.warning(f"Error en verificacion sismica de viga: {e}")
            return None

    def _check_seismic_column(
        self,
        column: Column,
        forces: Optional[ColumnForces],
        lambda_factor: float = 1.0
    ) -> Optional[SeismicColumnChecks]:
        """
        Verificacion sismica de columnas segun §18.7.

        Llama al SeismicColumnService del dominio para realizar todas
        las verificaciones aplicables.
        """
        try:
            # Obtener fuerzas del elemento
            Vu_V2 = 0.0
            Vu_V3 = 0.0
            Pu = 0.0
            if forces and hasattr(forces, 'combinations'):
                for combo in forces.combinations:
                    V2 = abs(getattr(combo, 'V2', 0))
                    V3 = abs(getattr(combo, 'V3', 0))
                    P = abs(getattr(combo, 'P', 0))
                    if V2 > Vu_V2:
                        Vu_V2 = V2
                    if V3 > Vu_V3:
                        Vu_V3 = V3
                    if P > Pu:
                        Pu = P

            # Usar Ash de la columna
            Ash = column.Ash_depth  # Area en direccion de la profundidad

            # Llamar al servicio de dominio
            result = self._seismic_column.verify_column(
                # Geometria
                b=min(column.depth, column.width),
                h=max(column.depth, column.width),
                lu=column.lu_calculated,
                cover=column.cover,
                Ag=column.Ag,
                # Materiales
                fc=column.fc,
                fy=column.fy,
                fyt=column.fy,  # Asume mismo fy para transversal
                # Refuerzo longitudinal
                Ast=column.As_longitudinal,
                n_bars=column.n_total_bars,
                db_long=column.diameter_long,
                # Refuerzo transversal
                s_transverse=column.stirrup_spacing,
                Ash=Ash,
                hx=column.hx,
                # Fuerzas
                Vu_V2=Vu_V2,
                Vu_V3=Vu_V3,
                Pu=Pu,
                # Columna fuerte-viga debil (si disponible)
                Mnc_top_V2=column.Mnc_top or 0,
                Mnc_bottom_V2=column.Mnc_bottom or 0,
                Mnb_left_V2=(column.sum_Mnb_major or 0) / 2,  # Dividir entre las dos vigas
                Mnb_right_V2=(column.sum_Mnb_major or 0) / 2,
                Mnc_top_V3=column.Mnc_top or 0,  # Usa mismo Mnc para V3
                Mnc_bottom_V3=column.Mnc_bottom or 0,
                Mnb_left_V3=(column.sum_Mnb_minor or 0) / 2,
                Mnb_right_V3=(column.sum_Mnb_minor or 0) / 2,
                # Opciones
                category=SeismicCategory.SPECIAL,
                lambda_factor=lambda_factor,
            )

            # Convertir resultado del dominio a dataclass de servicio
            return self._convert_column_result(result)

        except Exception as e:
            # Si hay error, retornar None y no bloquear verificacion
            import logging
            logging.warning(f"Error en verificacion sismica de columna: {e}")
            return None

    def _convert_beam_result(self, result) -> SeismicBeamChecks:
        """Convierte SeismicBeamResult del dominio a SeismicBeamChecks del servicio."""
        dimensional = None
        # El dominio usa 'dimensional_limits', no 'dimensional'
        dim = result.dimensional_limits
        if dim:
            dimensional = SeismicBeamDimensionalResult(
                ln_d_ratio=dim.ln / dim.d if dim.d > 0 else 0,
                ln_d_ok=dim.ln_ok,
                bw=dim.bw,
                bw_min=dim.bw_min,
                bw_ok=dim.bw_ok,
                projection_ok=dim.projection_ok,
                overall_ok=dim.is_ok,
            )

        longitudinal = None
        long = result.longitudinal
        if long:
            # Calcular rho_actual como el max de ambas cuantías
            rho_actual = max(long.rho_top, long.rho_bottom)
            longitudinal = SeismicBeamLongitudinalResult(
                rho_max=long.rho_max,
                rho_actual=rho_actual,
                rho_ok=long.rho_ok,
                M_pos_ratio=long.moment_ratio_face,
                M_pos_ratio_ok=long.moment_ratio_face_ok,
                M_any_ratio=long.moment_ratio_section,
                M_any_ratio_ok=long.moment_ratio_section_ok,
                overall_ok=long.is_ok,
            )

        transverse = None
        trans = result.transverse
        if trans:
            transverse = SeismicBeamTransverseResult(
                s_hoop=trans.s_in_zone,
                s_max=trans.s_max_zone,
                s_ok=trans.s_zone_ok,
                hx=trans.hx_provided,
                hx_max=trans.hx_max,
                hx_ok=trans.hx_ok,
                first_hoop_ok=trans.first_hoop_ok,
                confinement_length=trans.zone_length,
                overall_ok=trans.is_ok,
            )

        shear = None
        sh = result.shear
        if sh:
            # SF = phi_Vn / Vu_design
            sf = sh.phi_Vn / sh.Vu_design if sh.Vu_design > 0 else float('inf')
            shear = SeismicBeamShearResult(
                Mpr_left=0,  # Mpr no se almacena en BeamShearResult
                Mpr_right=0,
                Ve=sh.Ve,
                phi_Vn=sh.phi_Vn,
                Vc=sh.Vc,
                Vs=sh.Vs,
                Vc_allowed=not sh.Vc_is_zero,
                sf=sf,
                status='OK' if sh.is_ok else 'NO OK',
            )

        return SeismicBeamChecks(
            dimensional=dimensional,
            longitudinal=longitudinal,
            transverse=transverse,
            shear=shear,
            seismic_category=result.category.value if hasattr(result, 'category') else 'SPECIAL',
            overall_ok=result.is_ok,
        )

    def _convert_column_result(self, result) -> SeismicColumnChecks:
        """Convierte SeismicColumnResult del dominio a SeismicColumnChecks del servicio."""
        dimensional = None
        # El dominio usa 'dimensional_limits', no 'dimensional'
        dim = result.dimensional_limits
        if dim:
            dimensional = SeismicColumnDimensionalResult(
                b_min=dim.min_dimension,
                b_min_ok=dim.min_dimension_ok,
                aspect_ratio=dim.aspect_ratio,
                aspect_ratio_ok=dim.aspect_ratio_ok,
                overall_ok=dim.is_ok,
            )

        strong_column = None
        strong = result.strong_column_V2
        if strong:
            strong_column = SeismicColumnStrongResult(
                sum_Mnc=strong.sum_Mnc,
                sum_Mnb=strong.sum_Mnb,
                ratio=strong.ratio,
                is_ok=strong.is_ok,
                exempt=False,  # Por defecto, no exento
            )

        longitudinal = None
        long = result.longitudinal
        if long:
            longitudinal = SeismicColumnLongitudinalResult(
                rho=long.rho,
                rho_ok=long.rho_min_ok and long.rho_max_ok,
                n_bars_ok=long.n_bars_ok,
                overall_ok=long.is_ok,
            )

        transverse = None
        trans = result.transverse
        if trans:
            transverse = SeismicColumnTransverseResult(
                lo=trans.lo,
                s=trans.s_provided,
                s_max=trans.s_max,
                s_ok=trans.s_ok,
                hx=trans.hx_provided,
                hx_max=trans.hx_max,
                hx_ok=trans.hx_ok,
                Ash_provided=trans.Ash_sbc_provided,
                Ash_required=trans.Ash_sbc_required,
                Ash_ok=trans.Ash_ok,
                overall_ok=trans.is_ok,
            )

        shear = None
        sh = result.shear
        if sh:
            # Calcular SF
            sf = 1.0 / sh.dcr if sh.dcr > 0 else float('inf')
            # Obtener Vc y Vs del capacity_V2
            Vc = sh.capacity_V2.Vc if sh.capacity_V2 else 0
            Vs = sh.capacity_V2.Vs if sh.capacity_V2 else 0
            shear = SeismicColumnShearDetailedResult(
                Mpr_top=0,  # No disponible en SeismicColumnShearResult
                Mpr_bottom=0,
                Ve=sh.Ve,
                phi_Vn=sh.phi_Vn_V2,
                Vc=Vc,
                Vs=Vs,
                Vc_allowed=not sh.Vc_is_zero,
                sf=sf,
                status='OK' if sh.is_ok else 'NO OK',
            )

        return SeismicColumnChecks(
            dimensional=dimensional,
            strong_column=strong_column,
            longitudinal=longitudinal,
            transverse=transverse,
            shear=shear,
            seismic_category=result.category.value if hasattr(result, 'category') else 'SPECIAL',
            overall_ok=result.is_ok,
        )

    # =========================================================================
    # VERIFICACIONES ADICIONALES: NON-SFRS y MUROS ACOPLADOS
    # =========================================================================

    def verify_non_sfrs(
        self,
        element: Union[Beam, Column],
        delta_u: float,
        hsx: float,
        M_induced: float = 0,
        V_induced: float = 0,
        Mn: float = 0,
        Vn: float = 0,
    ) -> 'DriftCompatibilityResult':
        """
        Verificacion §18.14 para elementos no parte del SFRS.

        Args:
            element: Viga o columna a verificar
            delta_u: Deriva de diseno (mm)
            hsx: Altura de entrepiso (mm)
            M_induced: Momento inducido por deriva (tonf-m)
            V_induced: Cortante inducido por deriva (tonf)
            Mn: Resistencia nominal a flexion (tonf-m)
            Vn: Resistencia nominal a cortante (tonf)

        Returns:
            DriftCompatibilityResult con verificacion de compatibilidad de deriva
        """
        from ...domain.chapter18 import DriftCompatibilityResult

        return self._non_sfrs.check_drift_compatibility(
            delta_u=delta_u,
            hsx=hsx,
            M_induced=M_induced,
            V_induced=V_induced,
            Mn=Mn,
            Vn=Vn,
        )

    def verify_coupled_wall_system(
        self,
        walls: list,
        coupling_beams: list,
    ) -> 'DuctileCoupledWallResult':
        """
        Verificacion §18.10.9 para sistema de muros acoplados ductiles.

        Args:
            walls: Lista de muros con formato:
                [{\"wall_id\": \"W1\", \"hwcs\": 15000, \"lw\": 6000}, ...]
            coupling_beams: Lista de vigas de acople con formato:
                [{\"beam_id\": \"CB1\", \"level\": 1, \"ln\": 2000, \"h\": 800}, ...]

        Returns:
            DuctileCoupledWallResult con verificacion del sistema
        """
        from ...domain.chapter18 import DuctileCoupledWallResult

        return self._coupled_wall.verify_ductile_coupled_wall(walls, coupling_beams)
