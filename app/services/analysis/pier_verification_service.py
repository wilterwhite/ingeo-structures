# app/services/analysis/pier_verification_service.py
"""
Servicio de verificación ACI 318-25 para piers.

Orquesta verificaciones de conformidad con:
- Capítulo 11: Muros (Walls)
- Capítulo 18: Estructuras resistentes a sismos

Usa directamente los servicios de dominio sin capas intermedias.
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from ..parsing.session_manager import SessionManager
from ...domain.entities import Pier, PierForces
from ...domain.chapter11 import (
    WallLimitsService,
    WallLimitsResult,
    WallType,
    WallCastType,
    WallDesignMethodsService,
    SimplifiedMethodResult,
    SlenderWallResult,
    BoundaryCondition,
    ReinforcementLimitsService,
    MinReinforcementResult,
    ShearReinforcementResult,
)
from ...domain.chapter18 import (
    ShearAmplificationService,
    ShearAmplificationFactors,
    SpecialWallRequirements,
    BoundaryElementService,
    BoundaryElementMethod,
    BoundaryElementResult,
    WallPierService,
    WallPierDesignResult,
)
from ...domain.shear import ShearVerificationService
from ...domain.flexure import SlendernessService
from ...domain.constants import SeismicDesignCategory, WallCategory, N_TO_TONF, NMM_TO_TONFM
from .force_extractors import extract_max_forces


# =========================================================================
# DATACLASSES PARA RESULTADOS
# =========================================================================

@dataclass
class Chapter11Result:
    """Resultado de verificación ACI 318-25 Capítulo 11."""
    wall_limits: WallLimitsResult
    reinforcement: MinReinforcementResult
    shear_reinforcement: ShearReinforcementResult
    simplified_method: Optional[SimplifiedMethodResult]
    slender_wall: Optional[SlenderWallResult]
    all_ok: bool
    critical_issues: List[str]
    warnings: List[str]


@dataclass
class Chapter18Result:
    """Resultado de verificación ACI 318-25 Capítulo 18."""
    sdc: SeismicDesignCategory
    wall_category: WallCategory
    shear_amplification: Optional[ShearAmplificationFactors]
    special_wall: Optional[SpecialWallRequirements]
    boundary_element: Optional[BoundaryElementResult]
    wall_pier: Optional[WallPierDesignResult]
    all_ok: bool
    critical_issues: List[str]
    warnings: List[str]


class PierVerificationService:
    """
    Servicio de verificación ACI 318-25 para piers.

    Orquesta verificaciones de conformidad con los capítulos 11 y 18
    del código ACI 318-25, usando directamente servicios de dominio.
    """

    def __init__(self, session_manager: SessionManager):
        """
        Inicializa el servicio de verificación.

        Args:
            session_manager: Gestor de sesiones (requerido)
        """
        self._session_manager = session_manager

        # Servicios de dominio - Capítulo 11
        self._wall_limits = WallLimitsService()
        self._reinforcement_limits = ReinforcementLimitsService()
        self._design_methods = WallDesignMethodsService()
        self._shear_verification = ShearVerificationService()
        self._slenderness = SlendernessService()

        # Servicios de dominio - Capítulo 18
        self._shear_amplification = ShearAmplificationService()
        self._boundary_elements = BoundaryElementService()
        self._wall_piers = WallPierService()

    # =========================================================================
    # METODOS INTERNOS DE ORQUESTACION
    # =========================================================================

    def _verify_chapter_11(
        self,
        pier: Pier,
        Vu: float = 0,
        Pu: float = 0,
        Mua: float = 0,
        wall_type: WallType = WallType.BEARING,
        cast_type: WallCastType = WallCastType.CAST_IN_PLACE,
        boundary_condition: BoundaryCondition = BoundaryCondition.BRACED_RESTRAINED,
        check_simplified: bool = True,
        check_slender: bool = True
    ) -> Chapter11Result:
        """
        Orquesta verificación completa según ACI 318-25 Capítulo 11.

        Args:
            pier: Entidad Pier con geometría y armadura
            Vu: Demanda de cortante en el plano (tonf)
            Pu: Carga axial factorada (tonf), positivo = compresión
            Mua: Momento factorado sin P-Delta (tonf-m)
            wall_type: Tipo de muro
            cast_type: Tipo de construcción
            boundary_condition: Condición de borde para factor k
            check_simplified: Verificar método simplificado 11.5.3
            check_slender: Verificar método muros esbeltos 11.8

        Returns:
            Chapter11Result con todos los resultados
        """
        critical_issues = []
        warnings = []

        # 1. Calcular phi*Vc para determinar si requiere refuerzo por cortante
        shear_result = self._shear_verification.verify_shear(
            lw=pier.width,
            tw=pier.thickness,
            hw=pier.height,
            fc=pier.fc,
            fy=pier.fy,
            rho_h=pier.rho_horizontal,
            Vu=Vu,
            rho_v=pier.rho_vertical
        )
        phi_Vc = shear_result.Vc * 0.75
        requires_shear_reinf = Vu > 0.5 * phi_Vc

        # 2. Verificar límites de diseño (11.3, 11.7)
        wall_limits = self._wall_limits.check_wall_limits(
            pier=pier,
            wall_type=wall_type,
            requires_shear_reinforcement=requires_shear_reinf,
            cast_type=cast_type
        )

        if not wall_limits.thickness.is_ok:
            critical_issues.append(
                f"Espesor minimo: {pier.thickness}mm < {wall_limits.thickness.h_min_mm}mm"
            )
        if not wall_limits.spacing.is_ok:
            if not wall_limits.spacing.long_ok:
                critical_issues.append(
                    f"Espaciamiento vertical: {pier.spacing_v}mm > {wall_limits.spacing.s_max_long_mm}mm"
                )
            if not wall_limits.spacing.trans_ok:
                critical_issues.append(
                    f"Espaciamiento horizontal: {pier.spacing_h}mm > {wall_limits.spacing.s_max_trans_mm}mm"
                )
        if not wall_limits.double_curtain.is_ok:
            critical_issues.append(
                f"Se requiere doble cortina para e={pier.thickness}mm > 254mm"
            )
        warnings.extend(wall_limits.warnings)

        # 3. Verificar refuerzo mínimo (11.6)
        threshold = 0.5 * phi_Vc
        reinforcement = self._reinforcement_limits.check_minimum_reinforcement(
            rho_l=pier.rho_vertical,
            rho_t=pier.rho_horizontal,
            diameter_v_mm=pier.diameter_v,
            diameter_h_mm=pier.diameter_h,
            fy_mpa=pier.fy,
            hw=pier.height,
            lw=pier.width,
            Vu=Vu,
            phi_alpha_c_lambda_sqrt_fc_Acv=threshold,
            is_precast=(cast_type == WallCastType.PRECAST)
        )

        if not reinforcement.rho_l_ok:
            critical_issues.append(
                f"Cuantia vertical: {reinforcement.rho_l_actual:.4f} < {reinforcement.rho_l_min:.4f}"
            )
        if not reinforcement.rho_t_ok:
            critical_issues.append(
                f"Cuantia horizontal: {reinforcement.rho_t_actual:.4f} < {reinforcement.rho_t_min:.4f}"
            )

        # 4. Verificar refuerzo para cortante (11.6.2)
        shear_reinforcement = self._reinforcement_limits.check_shear_reinforcement(
            rho_v=pier.rho_vertical,
            rho_h=pier.rho_horizontal,
            hw=pier.height,
            lw=pier.width
        )

        if not shear_reinforcement.rho_v_ge_rho_h and shear_reinforcement.hw_lw <= 2.0:
            warnings.append(
                f"Para hw/lw={shear_reinforcement.hw_lw:.2f} <= 2.0, "
                f"se recomienda rho_v >= rho_h (ACI 318-25 11.6.2)"
            )

        # 5. Método simplificado (11.5.3) - opcional
        simplified_method = None
        if check_simplified:
            if Pu > 0 and Mua > 0:
                e_mm = (Mua * NMM_TO_TONFM) / (Pu * N_TO_TONF)
            else:
                e_mm = 0

            simplified_method = self._design_methods.calculate_simplified_from_pier(
                pier=pier,
                boundary_condition=boundary_condition,
                eccentricity_mm=e_mm
            )
            if not simplified_method.is_applicable:
                warnings.append(simplified_method.applicability_note)

        # 6. Método muros esbeltos (11.8) - opcional
        slender_wall = None
        if check_slender:
            slenderness = self._slenderness.analyze(pier, k=0.8, braced=True)
            if slenderness.is_slender:
                Pu_N = Pu * N_TO_TONF
                Mua_Nmm = Mua * NMM_TO_TONFM
                As_tension = pier.As_flexure_total / 2

                slender_wall = self._design_methods.analyze_slender_wall(
                    pier=pier,
                    Pu_N=Pu_N,
                    Mua_Nmm=Mua_Nmm,
                    As_tension_mm2=As_tension
                )
                if not slender_wall.deflection_ok:
                    critical_issues.append(
                        f"Deflexion excede limite: {slender_wall.Delta_s_mm:.1f}mm > "
                        f"{slender_wall.Delta_limit_mm:.1f}mm (lc/150)"
                    )

        # Resumen
        all_ok = (
            wall_limits.all_ok and
            reinforcement.is_ok and
            (slender_wall is None or slender_wall.deflection_ok)
        )

        return Chapter11Result(
            wall_limits=wall_limits,
            reinforcement=reinforcement,
            shear_reinforcement=shear_reinforcement,
            simplified_method=simplified_method,
            slender_wall=slender_wall,
            all_ok=all_ok,
            critical_issues=critical_issues,
            warnings=warnings
        )

    def _verify_from_pier_forces(
        self,
        pier: Pier,
        pier_forces: PierForces,
        wall_type: WallType = WallType.BEARING
    ) -> Chapter11Result:
        """Verificación Cap 11 usando envolventes de PierForces."""
        if not pier_forces or not pier_forces.combinations:
            return self._verify_chapter_11(pier, wall_type=wall_type)

        max_forces = extract_max_forces(pier_forces)

        return self._verify_chapter_11(
            pier=pier,
            Vu=max_forces.Vu_max,
            Pu=max_forces.Pu_max,
            Mua=max_forces.Mu_max,
            wall_type=wall_type
        )

    def _verify_chapter_18(
        self,
        pier: Pier,
        sdc: SeismicDesignCategory = SeismicDesignCategory.D,
        Vu: float = 0,
        Vu_Eh: float = 0,
        delta_u: float = 0,
        hwcs: float = 0,
        hn_ft: float = 0,
        sigma_max: float = 0,
        use_displacement_method: bool = True,
        is_wall_pier: bool = False
    ) -> Chapter18Result:
        """
        Orquesta verificación según ACI 318-25 Capítulo 18.

        Args:
            pier: Entidad Pier con geometría y armadura
            sdc: Categoría de Diseño Sísmico
            Vu: Cortante último del análisis (tonf)
            Vu_Eh: Cortante debido a efecto sísmico horizontal (tonf)
            delta_u: Desplazamiento de diseño en tope (mm)
            hwcs: Altura del muro desde sección crítica (mm)
            hn_ft: Altura total del edificio (pies)
            sigma_max: Esfuerzo máximo de compresión (MPa)
            use_displacement_method: Usar método de desplazamiento para bordes
            is_wall_pier: Si es un pilar de muro

        Returns:
            Chapter18Result con todos los resultados
        """
        critical_issues = []
        warnings = []

        # Determinar categoría del muro
        wall_category = self._shear_amplification.determine_wall_category(
            sdc, is_sfrs=True, is_precast=False
        )

        shear_amplification = None
        special_wall = None
        boundary_element = None
        wall_pier_result = None

        # 1. Amplificación de cortante (18.10.3.3)
        if wall_category == WallCategory.SPECIAL and Vu_Eh > 0:
            if hwcs <= 0:
                hwcs = pier.height

            shear_amplification = self._shear_amplification.calculate_amplified_shear(
                Vu=Vu_Eh,
                hwcs=hwcs,
                lw=pier.width,
                hn_ft=hn_ft
            )

            if shear_amplification.Ve > Vu:
                warnings.append(
                    f"Cortante amplificado Ve={shear_amplification.Ve:.1f} > Vu={Vu:.1f} tonf "
                    f"(Omega_v={shear_amplification.Omega_v}, omega_v={shear_amplification.omega_v_dyn})"
                )

        # 2. Requisitos de muro especial (18.10.2)
        if wall_category == WallCategory.SPECIAL:
            special_wall = self._shear_amplification.check_special_wall_requirements(
                hw=pier.height,
                lw=pier.width,
                tw=pier.thickness,
                rho_l=pier.rho_vertical,
                rho_t=pier.rho_horizontal,
                spacing_v=pier.spacing_v,
                spacing_h=pier.spacing_h,
                Vu=Vu,
                fc=pier.fc,
                lambda_factor=1.0,
                has_double_curtain=pier.n_meshes >= 2
            )

            if not special_wall.is_ok:
                for warn in special_wall.warnings:
                    if "rho" in warn.lower() or "cortina" in warn.lower():
                        critical_issues.append(warn)
                    else:
                        warnings.append(warn)

        # 3. Elementos de borde (18.10.6)
        if wall_category == WallCategory.SPECIAL:
            c_estimate = pier.width * 0.3
            b_boundary = pier.thickness
            Ag_boundary = b_boundary * (c_estimate * 0.5)
            Ach_boundary = Ag_boundary * 0.85
            hu = pier.height

            if use_displacement_method and delta_u > 0 and hwcs > 0:
                method = BoundaryElementMethod.DISPLACEMENT
                boundary_element = self._boundary_elements.verify_boundary_element(
                    method=method,
                    lw=pier.width,
                    c=c_estimate,
                    hu=hu,
                    fc=pier.fc,
                    fyt=pier.fy,
                    Ag=Ag_boundary,
                    Ach=Ach_boundary,
                    b=b_boundary,
                    delta_u=delta_u,
                    hwcs=hwcs,
                    Mu=0,
                    Vu=Vu,
                    Ve=Vu,
                    Acv=pier.width * pier.thickness
                )
            elif sigma_max > 0:
                method = BoundaryElementMethod.STRESS
                boundary_element = self._boundary_elements.verify_boundary_element(
                    method=method,
                    lw=pier.width,
                    c=c_estimate,
                    hu=hu,
                    fc=pier.fc,
                    fyt=pier.fy,
                    Ag=Ag_boundary,
                    Ach=Ach_boundary,
                    b=b_boundary,
                    sigma_max=sigma_max
                )

            if boundary_element and boundary_element.requires_special:
                warnings.append(
                    f"Se requieren elementos de borde especiales (18.10.6) - "
                    f"metodo: {boundary_element.method.value}"
                )
                warnings.extend(boundary_element.warnings)

        # 4. Pilar de muro (18.10.8)
        if is_wall_pier:
            wall_pier_result = self._wall_piers.design_wall_pier(
                hw=pier.height,
                lw=pier.width,
                bw=pier.thickness,
                Vu=Vu,
                fc=pier.fc,
                fy=pier.fy,
                fyt=pier.fy,
                rho_h=pier.rho_horizontal,
                sigma_max=sigma_max,
                has_single_curtain=pier.n_meshes == 1
            )

            if not wall_pier_result.shear_design.is_ok:
                critical_issues.append(
                    f"Pilar de muro: DCR cortante = {wall_pier_result.shear_design.dcr:.2f} > 1.0"
                )
            warnings.extend(wall_pier_result.warnings)

        # Resumen
        all_ok = (
            (special_wall is None or special_wall.is_ok) and
            (wall_pier_result is None or wall_pier_result.shear_design.is_ok) and
            len(critical_issues) == 0
        )

        return Chapter18Result(
            sdc=sdc,
            wall_category=wall_category,
            shear_amplification=shear_amplification,
            special_wall=special_wall,
            boundary_element=boundary_element,
            wall_pier=wall_pier_result,
            all_ok=all_ok,
            critical_issues=critical_issues,
            warnings=warnings
        )

    # =========================================================================
    # FORMATEO DE RESULTADOS
    # =========================================================================

    def _format_chapter_11_summary(self, result: Chapter11Result) -> Dict[str, Any]:
        """Genera resumen del Capítulo 11 para respuesta JSON."""
        return {
            'all_ok': result.all_ok,
            'aci_chapter': '11',
            'critical_issues': result.critical_issues,
            'warnings': result.warnings,
            'checks': {
                'thickness': {
                    'ok': result.wall_limits.thickness.is_ok,
                    'min_mm': result.wall_limits.thickness.h_min_mm,
                    'actual_mm': result.wall_limits.thickness.h_actual_mm,
                    'reference': result.wall_limits.thickness.aci_reference
                },
                'spacing': {
                    'ok': result.wall_limits.spacing.is_ok,
                    'longitudinal': {
                        'ok': result.wall_limits.spacing.long_ok,
                        'max_mm': result.wall_limits.spacing.s_max_long_mm,
                        'actual_mm': result.wall_limits.spacing.s_actual_long_mm
                    },
                    'transversal': {
                        'ok': result.wall_limits.spacing.trans_ok,
                        'max_mm': result.wall_limits.spacing.s_max_trans_mm,
                        'actual_mm': result.wall_limits.spacing.s_actual_trans_mm
                    },
                    'reference': result.wall_limits.spacing.aci_reference
                },
                'double_curtain': {
                    'ok': result.wall_limits.double_curtain.is_ok,
                    'required': result.wall_limits.double_curtain.requires_double,
                    'has_double': result.wall_limits.double_curtain.has_double,
                    'reference': result.wall_limits.double_curtain.aci_reference
                },
                'reinforcement': {
                    'ok': result.reinforcement.is_ok,
                    'is_high_shear': result.reinforcement.is_high_shear,
                    'longitudinal': {
                        'ok': result.reinforcement.rho_l_ok,
                        'min': result.reinforcement.rho_l_min,
                        'actual': result.reinforcement.rho_l_actual
                    },
                    'transversal': {
                        'ok': result.reinforcement.rho_t_ok,
                        'min': result.reinforcement.rho_t_min,
                        'actual': result.reinforcement.rho_t_actual
                    },
                    'reference': result.reinforcement.aci_reference
                },
                'shear_reinforcement': {
                    'ok': result.shear_reinforcement.is_ok,
                    'hw_lw': round(result.shear_reinforcement.hw_lw, 2),
                    'rho_v_ge_rho_h': result.shear_reinforcement.rho_v_ge_rho_h,
                    'reference': result.shear_reinforcement.aci_reference
                }
            },
            'simplified_method': None if result.simplified_method is None else {
                'applicable': result.simplified_method.is_applicable,
                'phi_Pn_tonf': round(result.simplified_method.phi_Pn_tonf, 1),
                'slenderness_term': round(result.simplified_method.slenderness_term, 3),
                'note': result.simplified_method.applicability_note,
                'reference': result.simplified_method.aci_reference
            },
            'slender_wall': None if result.slender_wall is None else {
                'applicable': result.slender_wall.is_applicable,
                'magnification_factor': round(result.slender_wall.magnification_factor, 2),
                'deflection_ok': result.slender_wall.deflection_ok,
                'Delta_s_mm': round(result.slender_wall.Delta_s_mm, 1),
                'Delta_limit_mm': round(result.slender_wall.Delta_limit_mm, 1),
                'reference': result.slender_wall.aci_reference
            }
        }

    def _format_chapter_18_summary(self, result: Chapter18Result) -> Dict[str, Any]:
        """Genera resumen del Capítulo 18 para respuesta JSON."""
        summary = {
            'all_ok': result.all_ok,
            'sdc': result.sdc.value,
            'wall_category': result.wall_category.value,
            'critical_issues': result.critical_issues,
            'warnings': result.warnings,
            'aci_reference': 'ACI 318-25 Capitulo 18'
        }

        if result.shear_amplification:
            summary['shear_amplification'] = {
                'Omega_v': result.shear_amplification.Omega_v,
                'omega_v': result.shear_amplification.omega_v,
                'combined': result.shear_amplification.combined,
                'hwcs_lw': result.shear_amplification.hwcs_lw,
                'reference': result.shear_amplification.aci_reference
            }

        if result.special_wall:
            summary['special_wall'] = {
                'is_ok': result.special_wall.is_ok,
                'rho_l_min': result.special_wall.rho_l_min,
                'rho_t_min': result.special_wall.rho_t_min,
                'spacing_max_mm': result.special_wall.spacing_max_mm,
                'requires_double_curtain': result.special_wall.requires_double_curtain,
                'rho_l_ge_rho_t': result.special_wall.rho_l_ge_rho_t,
                'reference': result.special_wall.aci_reference
            }

        if result.boundary_element:
            be = result.boundary_element
            summary['boundary_element'] = {
                'method': be.method.value,
                'requires_special': be.requires_special,
                'warnings': be.warnings,
                'reference': be.aci_reference
            }
            if be.dimensions:
                summary['boundary_element']['dimensions'] = {
                    'length_horizontal': be.dimensions.length_horizontal,
                    'width_min': be.dimensions.width_min,
                    'vertical_extension': be.dimensions.vertical_extension
                }
            if be.transverse_reinforcement:
                summary['boundary_element']['transverse'] = {
                    'Ash_sbc_required': be.transverse_reinforcement.Ash_sbc_required,
                    'spacing_max': be.transverse_reinforcement.spacing_max
                }

        if result.wall_pier:
            wp = result.wall_pier
            summary['wall_pier'] = {
                'classification': {
                    'hw_lw': wp.classification.hw_lw,
                    'lw_bw': wp.classification.lw_bw,
                    'category': wp.classification.category.value,
                    'design_method': wp.classification.design_method.value
                },
                'shear_design': {
                    'Ve': wp.shear_design.Ve,
                    'phi_Vn': wp.shear_design.phi_Vn,
                    'dcr': wp.shear_design.dcr,
                    'is_ok': wp.shear_design.is_ok
                },
                'transverse': {
                    'requires_closed_hoops': wp.transverse.requires_closed_hoops,
                    'spacing_max': wp.transverse.spacing_max
                },
                'reference': wp.aci_reference
            }

        return summary

    # =========================================================================
    # Helpers
    # =========================================================================

    def _get_sdc_enum(self, sdc: str) -> SeismicDesignCategory:
        """Convierte string SDC a enum."""
        return {
            'A': SeismicDesignCategory.A,
            'B': SeismicDesignCategory.B,
            'C': SeismicDesignCategory.C,
            'D': SeismicDesignCategory.D,
            'E': SeismicDesignCategory.E,
            'F': SeismicDesignCategory.F
        }.get(sdc.upper(), SeismicDesignCategory.D)

    def _get_wall_type_enum(self, wall_type: str) -> WallType:
        """Convierte string wall_type a enum."""
        return {
            'bearing': WallType.BEARING,
            'nonbearing': WallType.NONBEARING,
            'basement': WallType.BASEMENT,
            'foundation': WallType.FOUNDATION
        }.get(wall_type, WallType.BEARING)

    def _get_max_Vu(self, pier_forces: Optional[PierForces]) -> tuple:
        """Obtiene el cortante máximo de las combinaciones."""
        Vu = 0.0
        Vu_Eh = 0.0
        if pier_forces and pier_forces.combinations:
            for combo in pier_forces.combinations:
                Vu_combo = max(abs(combo.V2), abs(combo.V3))
                if Vu_combo > Vu:
                    Vu = Vu_combo
                    Vu_Eh = Vu_combo
        return Vu, Vu_Eh

    def _get_hwcs_hn(
        self,
        session_id: str,
        pier_key: str,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> tuple:
        """Obtiene hwcs y hn_ft, usando valores calculados si no se proporcionan."""
        if hwcs is None or hwcs <= 0:
            hwcs = self._session_manager.get_hwcs(session_id, pier_key)
        if hn_ft is None or hn_ft <= 0:
            hn_ft = self._session_manager.get_hn_ft(session_id)
        return hwcs, hn_ft

    # =========================================================================
    # Validación (delegada a SessionManager)
    # =========================================================================

    def _validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Valida que la sesión existe."""
        return self._session_manager.validate_session(session_id)

    def _validate_pier(self, session_id: str, pier_key: str) -> Optional[Dict[str, Any]]:
        """Valida que el pier existe en la sesión."""
        return self._session_manager.validate_pier(session_id, pier_key)

    # =========================================================================
    # Verificación ACI 318-25 Capítulo 11
    # =========================================================================

    def verify_aci_318_25(
        self,
        session_id: str,
        pier_key: str,
        wall_type: str = 'bearing',
        cast_type: str = 'cast_in_place'
    ) -> Dict[str, Any]:
        """
        Verifica conformidad ACI 318-25 Capitulo 11 para un pier.

        Incluye verificaciones de:
        - Espesor minimo (11.3.1)
        - Espaciamiento maximo de refuerzo (11.7)
        - Doble cortina (11.7.2.3)
        - Refuerzo minimo (11.6)
        - Metodo simplificado (11.5.3)
        - Muros esbeltos (11.8)

        Args:
            session_id: ID de sesion
            pier_key: Clave del pier (Story_Label)
            wall_type: Tipo de muro ('bearing', 'nonbearing', 'basement')
            cast_type: Tipo de construccion ('cast_in_place', 'precast')

        Returns:
            Dict con resultados de verificacion ACI 318-25
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        # Convertir tipos
        wall_type_enum = self._get_wall_type_enum(wall_type)
        cast_type_enum = {
            'cast_in_place': WallCastType.CAST_IN_PLACE,
            'precast': WallCastType.PRECAST
        }.get(cast_type, WallCastType.CAST_IN_PLACE)

        # Ejecutar verificacion usando métodos internos
        if pier_forces:
            result = self._verify_from_pier_forces(
                pier=pier,
                pier_forces=pier_forces,
                wall_type=wall_type_enum
            )
        else:
            result = self._verify_chapter_11(
                pier=pier,
                wall_type=wall_type_enum,
                cast_type=cast_type_enum
            )

        summary = self._format_chapter_11_summary(result)

        return {
            'success': True,
            'pier_key': pier_key,
            'aci_318_25': summary
        }

    def verify_all_piers_aci_318_25(
        self,
        session_id: str,
        wall_type: str = 'bearing'
    ) -> Dict[str, Any]:
        """
        Verifica conformidad ACI 318-25 para todos los piers de la sesion.

        Args:
            session_id: ID de sesion
            wall_type: Tipo de muro por defecto

        Returns:
            Dict con resultados de verificacion para todos los piers
        """
        error = self._validate_session(session_id)
        if error:
            return error

        parsed_data = self._session_manager.get_session(session_id)

        results = []
        issues_count = 0
        warnings_count = 0
        wall_type_enum = self._get_wall_type_enum(wall_type)

        for key, pier in parsed_data.piers.items():
            pier_forces = parsed_data.pier_forces.get(key)

            if pier_forces:
                result = self._verify_from_pier_forces(
                    pier=pier,
                    pier_forces=pier_forces,
                    wall_type=wall_type_enum
                )
            else:
                result = self._verify_chapter_11(
                    pier=pier,
                    wall_type=wall_type_enum
                )

            issues_count += len(result.critical_issues)
            warnings_count += len(result.warnings)

            results.append({
                'pier_key': key,
                'story': pier.story,
                'label': pier.label,
                'all_ok': result.all_ok,
                'critical_issues': result.critical_issues,
                'warnings': result.warnings
            })

        # Estadisticas
        total = len(results)
        ok_count = sum(1 for r in results if r['all_ok'])
        not_ok_count = total - ok_count

        return {
            'success': True,
            'statistics': {
                'total_piers': total,
                'ok': ok_count,
                'not_ok': not_ok_count,
                'total_issues': issues_count,
                'total_warnings': warnings_count,
                'compliance_rate': round(ok_count / total * 100, 1) if total > 0 else 0
            },
            'results': results
        }

    # =========================================================================
    # Verificación ACI 318-25 Capítulo 18 (Sísmico)
    # =========================================================================

    def verify_seismic(
        self,
        session_id: str,
        pier_key: str,
        sdc: str = 'D',
        delta_u: float = 0,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        sigma_max: float = 0,
        is_wall_pier: bool = False
    ) -> Dict[str, Any]:
        """
        Verifica conformidad ACI 318-25 Capitulo 18 para un pier.

        Verifica requisitos sismicos para muros estructurales especiales:
        - Amplificacion de cortante (18.10.3.3)
        - Requisitos de muro especial (18.10.2)
        - Elementos de borde (18.10.6)
        - Pilar de muro (18.10.8)

        Args:
            session_id: ID de sesion
            pier_key: Clave del pier (Story_Label)
            sdc: Categoria de Diseno Sismico ('A', 'B', 'C', 'D', 'E', 'F')
            delta_u: Desplazamiento de diseno en tope (mm)
            hwcs: Altura del muro desde seccion critica (mm), None = usar calculado
            hn_ft: Altura total del edificio (pies), None = usar calculado
            sigma_max: Esfuerzo maximo de compresion (MPa)
            is_wall_pier: Si es un pilar de muro (segmento estrecho)

        Returns:
            Dict con resultados de verificacion sismica
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        # Obtener hwcs/hn_ft calculados si no se proporcionan
        hwcs, hn_ft = self._get_hwcs_hn(session_id, pier_key, hwcs, hn_ft)

        # Convertir SDC y obtener Vu máximo
        sdc_enum = self._get_sdc_enum(sdc)
        Vu, Vu_Eh = self._get_max_Vu(pier_forces)

        # Ejecutar verificacion usando método interno
        result = self._verify_chapter_18(
            pier=pier,
            sdc=sdc_enum,
            Vu=Vu,
            Vu_Eh=Vu_Eh,
            delta_u=delta_u,
            hwcs=hwcs if hwcs and hwcs > 0 else pier.height,
            hn_ft=hn_ft if hn_ft else 0,
            sigma_max=sigma_max,
            is_wall_pier=is_wall_pier
        )

        summary = self._format_chapter_18_summary(result)

        return {
            'success': True,
            'pier_key': pier_key,
            'chapter_18': summary
        }

    def verify_combined_aci(
        self,
        session_id: str,
        pier_key: str,
        wall_type: str = 'bearing',
        sdc: str = 'D',
        delta_u: float = 0,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        sigma_max: float = 0,
        is_wall_pier: bool = False
    ) -> Dict[str, Any]:
        """
        Verificacion combinada de Capitulos 11 y 18 para un pier.

        Args:
            session_id: ID de sesion
            pier_key: Clave del pier
            wall_type: Tipo de muro
            sdc: Categoria de Diseno Sismico
            delta_u: Desplazamiento de diseno (mm)
            hwcs: Altura desde seccion critica (mm), None = usar calculado
            hn_ft: Altura del edificio (pies), None = usar calculado
            sigma_max: Esfuerzo maximo (MPa)
            is_wall_pier: Si es pilar de muro

        Returns:
            Dict con resultados combinados
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        # Usar helpers para hwcs/hn_ft y SDC
        hwcs, hn_ft = self._get_hwcs_hn(session_id, pier_key, hwcs, hn_ft)
        sdc_enum = self._get_sdc_enum(sdc)

        # Ejecutar verificación combinada usando métodos internos
        # Obtener valores críticos de fuerzas
        Vu_max = 0
        Pu_max = 0
        Mua_max = 0
        Vu_Eh = 0

        if pier_forces and pier_forces.combinations:
            for combo in pier_forces.combinations:
                V2 = abs(combo.V2)
                V3 = abs(combo.V3)
                Vu = max(V2, V3)
                P = abs(combo.P)
                M = combo.moment_resultant

                if Vu > Vu_max:
                    Vu_max = Vu
                    Vu_Eh = Vu
                if P > Pu_max:
                    Pu_max = P
                if M > Mua_max:
                    Mua_max = M

        # Verificar Capítulo 11
        chapter_11 = self._verify_chapter_11(
            pier=pier,
            Vu=Vu_max,
            Pu=Pu_max,
            Mua=Mua_max
        )

        # Verificar Capítulo 18 si SDC >= B
        chapter_18 = None
        if sdc_enum != SeismicDesignCategory.A:
            chapter_18 = self._verify_chapter_18(
                pier=pier,
                sdc=sdc_enum,
                Vu=Vu_max,
                Vu_Eh=Vu_Eh,
                delta_u=delta_u,
                hwcs=hwcs if hwcs and hwcs > 0 else pier.height,
                hn_ft=hn_ft if hn_ft else 0,
                sigma_max=sigma_max,
                is_wall_pier=is_wall_pier
            )

        # Combinar resultados
        all_ok = chapter_11.all_ok and (chapter_18 is None or chapter_18.all_ok)
        all_issues = chapter_11.critical_issues.copy()
        all_warnings = chapter_11.warnings.copy()

        if chapter_18:
            all_issues.extend(chapter_18.critical_issues)
            all_warnings.extend(chapter_18.warnings)

        return {
            'success': True,
            'pier_key': pier_key,
            'all_ok': all_ok,
            'critical_issues': all_issues,
            'warnings': all_warnings,
            'chapter_11': self._format_chapter_11_summary(chapter_11),
            'chapter_18': self._format_chapter_18_summary(chapter_18) if chapter_18 else None
        }

    def verify_all_piers_seismic(
        self,
        session_id: str,
        sdc: str = 'D',
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Verifica conformidad sismica para todos los piers de la sesion.

        Args:
            session_id: ID de sesion
            sdc: Categoria de Diseno Sismico
            hn_ft: Altura del edificio (pies), None = usar calculado

        Returns:
            Dict con resultados para todos los piers
        """
        error = self._validate_session(session_id)
        if error:
            return error

        parsed_data = self._session_manager.get_session(session_id)

        # Usar hn_ft calculado si no se proporciona
        if hn_ft is None or hn_ft <= 0:
            hn_ft = self._session_manager.get_hn_ft(session_id)

        sdc_enum = self._get_sdc_enum(sdc)
        results = []
        issues_count = 0
        warnings_count = 0

        for key, pier in parsed_data.piers.items():
            pier_forces = parsed_data.pier_forces.get(key)

            # Obtener hwcs para este pier
            hwcs = pier.height  # default
            if parsed_data.continuity_info and key in parsed_data.continuity_info:
                hwcs = parsed_data.continuity_info[key].hwcs

            # Obtener cortante maximo
            Vu, Vu_Eh = self._get_max_Vu(pier_forces)

            result = self._verify_chapter_18(
                pier=pier,
                sdc=sdc_enum,
                Vu=Vu,
                Vu_Eh=Vu_Eh,
                hwcs=hwcs,
                hn_ft=hn_ft if hn_ft else 0
            )

            issues_count += len(result.critical_issues)
            warnings_count += len(result.warnings)

            results.append({
                'pier_key': key,
                'story': pier.story,
                'label': pier.label,
                'sdc': result.sdc.value,
                'wall_category': result.wall_category.value,
                'all_ok': result.all_ok,
                'critical_issues': result.critical_issues,
                'warnings': result.warnings
            })

        # Estadisticas
        total = len(results)
        ok_count = sum(1 for r in results if r['all_ok'])
        not_ok_count = total - ok_count

        return {
            'success': True,
            'sdc': sdc,
            'statistics': {
                'total_piers': total,
                'ok': ok_count,
                'not_ok': not_ok_count,
                'total_issues': issues_count,
                'total_warnings': warnings_count,
                'compliance_rate': round(ok_count / total * 100, 1) if total > 0 else 0
            },
            'results': results
        }
