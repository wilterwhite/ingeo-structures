# app/structural/services/analysis/aci_318_25_service.py
"""
Servicio de verificacion de conformidad ACI 318-25 para muros.

Integra todas las verificaciones del Capitulo 11 y Capitulo 18:
- Limites de diseno (espesores, espaciamiento, doble cortina)
- Refuerzo minimo diferenciado
- Metodo simplificado para carga axial
- Metodo alternativo para muros esbeltos
- Cortante en el plano
- Muros estructurales especiales (18.10)
- Elementos de borde (18.10.6)
- Pilares de muro (18.10.8)

Este servicio actua como orquestador de todas las verificaciones ACI.
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, TYPE_CHECKING

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
    DesignShearResult,
    BoundaryElementService,
    BoundaryElementMethod,
    BoundaryElementResult,
    WallPierService,
    WallPierDesignResult,
    WallPierCategory,
)
from ...domain.shear import ShearVerificationService
from ...domain.flexure import SlendernessService
from ...domain.constants import SeismicDesignCategory, WallCategory, N_TO_TONF, NMM_TO_TONFM

if TYPE_CHECKING:
    from ...domain.entities import Pier, PierForces


@dataclass
class ACI318_25_VerificationResult:
    """Resultado completo de verificacion ACI 318-25."""
    # Limites de diseno (11.3, 11.7)
    wall_limits: WallLimitsResult

    # Refuerzo minimo (11.6)
    reinforcement: MinReinforcementResult

    # Cortante (11.5.4, 18.10.4)
    shear_reinforcement: ShearReinforcementResult

    # Metodo simplificado (11.5.3) - opcional
    simplified_method: Optional[SimplifiedMethodResult]

    # Metodo muros esbeltos (11.8) - opcional
    slender_wall: Optional[SlenderWallResult]

    # Resumen
    all_ok: bool
    critical_issues: List[str]
    warnings: List[str]
    aci_chapter: str  # "11" o "18"


@dataclass
class Chapter18_VerificationResult:
    """Resultado de verificacion segun Capitulo 18 (Sismico)."""
    # Categoria de diseno sismico
    sdc: SeismicDesignCategory
    wall_category: WallCategory

    # Amplificacion de cortante (18.10.3.3)
    shear_amplification: Optional[ShearAmplificationFactors]

    # Requisitos de muro especial (18.10.2)
    special_wall: Optional[SpecialWallRequirements]

    # Elementos de borde (18.10.6)
    boundary_element: Optional[BoundaryElementResult]

    # Pilar de muro (18.10.8) - si aplica
    wall_pier: Optional[WallPierDesignResult]

    # Resumen
    all_ok: bool
    critical_issues: List[str]
    warnings: List[str]
    aci_reference: str


class ACI318_25_Service:
    """
    Servicio integrado de verificacion ACI 318-25.

    Coordina todas las verificaciones de los Capitulos 11 y 18
    para muros de hormigon armado.
    """

    def __init__(self):
        # Chapter 11 services
        self._wall_limits = WallLimitsService()
        self._reinforcement_limits = ReinforcementLimitsService()
        self._design_methods = WallDesignMethodsService()
        self._shear_verification = ShearVerificationService()
        self._slenderness = SlendernessService()

        # Chapter 18 services
        self._shear_amplification = ShearAmplificationService()
        self._boundary_elements = BoundaryElementService()
        self._wall_piers = WallPierService()

    def verify_chapter_11(
        self,
        pier: 'Pier',
        Vu: float = 0,
        Pu: float = 0,
        Mua: float = 0,
        wall_type: WallType = WallType.BEARING,
        cast_type: WallCastType = WallCastType.CAST_IN_PLACE,
        boundary_condition: BoundaryCondition = BoundaryCondition.BRACED_RESTRAINED,
        check_simplified: bool = True,
        check_slender: bool = True
    ) -> ACI318_25_VerificationResult:
        """
        Ejecuta verificacion completa segun ACI 318-25 Capitulo 11.

        Args:
            pier: Entidad Pier con geometria y armadura
            Vu: Demanda de cortante en el plano (tonf)
            Pu: Carga axial factorada (tonf), positivo = compresion
            Mua: Momento factorado sin P-Delta (tonf-m)
            wall_type: Tipo de muro
            cast_type: Tipo de construccion
            boundary_condition: Condicion de borde para factor k
            check_simplified: Verificar metodo simplificado 11.5.3
            check_slender: Verificar metodo muros esbeltos 11.8

        Returns:
            ACI318_25_VerificationResult con todos los resultados
        """
        critical_issues = []
        warnings = []

        # =====================================================================
        # 1. Verificar limites de diseno (11.3, 11.7)
        # =====================================================================

        # Calcular phi*Vc para determinar si requiere refuerzo por cortante
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
        phi_Vc = shear_result.Vc * 0.75  # Vc ya viene en tonf

        requires_shear_reinf = Vu > 0.5 * phi_Vc

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

        # =====================================================================
        # 2. Verificar refuerzo minimo (11.6)
        # =====================================================================

        # Umbral para cortante alto/bajo
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

        # =====================================================================
        # 3. Verificar refuerzo para cortante (11.6.2)
        # =====================================================================

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

        # =====================================================================
        # 4. Metodo simplificado (11.5.3) - opcional
        # =====================================================================

        simplified_method = None
        if check_simplified:
            # Estimar excentricidad
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

        # =====================================================================
        # 5. Metodo muros esbeltos (11.8) - opcional
        # =====================================================================

        slender_wall = None
        if check_slender:
            # Verificar si el muro es esbelto
            slenderness = self._slenderness.analyze(pier, k=0.8, braced=True)

            if slenderness.is_slender:
                # Convertir unidades para el analisis
                Pu_N = Pu * N_TO_TONF
                Mua_Nmm = Mua * NMM_TO_TONFM

                # Usar As_flexure_total como As en traccion (conservador)
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

        # =====================================================================
        # Resumen
        # =====================================================================

        all_ok = (
            wall_limits.all_ok and
            reinforcement.is_ok and
            (slender_wall is None or slender_wall.deflection_ok)
        )

        return ACI318_25_VerificationResult(
            wall_limits=wall_limits,
            reinforcement=reinforcement,
            shear_reinforcement=shear_reinforcement,
            simplified_method=simplified_method,
            slender_wall=slender_wall,
            all_ok=all_ok,
            critical_issues=critical_issues,
            warnings=warnings,
            aci_chapter="11"
        )

    def verify_from_pier_forces(
        self,
        pier: 'Pier',
        pier_forces: 'PierForces',
        wall_type: WallType = WallType.BEARING
    ) -> ACI318_25_VerificationResult:
        """
        Verificacion usando fuerzas de PierForces.

        Encuentra la combinacion critica y ejecuta la verificacion.

        Args:
            pier: Entidad Pier
            pier_forces: Fuerzas del pier (combinaciones)
            wall_type: Tipo de muro

        Returns:
            ACI318_25_VerificationResult
        """
        if not pier_forces or not pier_forces.combinations:
            return self.verify_chapter_11(pier, wall_type=wall_type)

        # Encontrar valores criticos
        Vu_max = 0
        Pu_max = 0
        Mua_max = 0

        for combo in pier_forces.combinations:
            V2 = abs(combo.V2)
            V3 = abs(combo.V3)
            Vu = max(V2, V3)
            P = abs(combo.P)
            M = combo.moment_resultant

            if Vu > Vu_max:
                Vu_max = Vu
            if P > Pu_max:
                Pu_max = P
            if M > Mua_max:
                Mua_max = M

        return self.verify_chapter_11(
            pier=pier,
            Vu=Vu_max,
            Pu=Pu_max,
            Mua=Mua_max,
            wall_type=wall_type
        )

    def get_verification_summary(
        self,
        result: ACI318_25_VerificationResult
    ) -> Dict[str, Any]:
        """
        Genera resumen de la verificacion para respuesta JSON.

        Args:
            result: Resultado de la verificacion

        Returns:
            Dict con resumen estructurado
        """
        return {
            'all_ok': result.all_ok,
            'aci_chapter': result.aci_chapter,
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

    # =========================================================================
    # CAPITULO 18: ESTRUCTURAS RESISTENTES A SISMOS
    # =========================================================================

    def verify_chapter_18(
        self,
        pier: 'Pier',
        sdc: SeismicDesignCategory = SeismicDesignCategory.D,
        Vu: float = 0,
        Vu_Eh: float = 0,
        delta_u: float = 0,
        hwcs: float = 0,
        hn_ft: float = 0,
        sigma_max: float = 0,
        use_displacement_method: bool = True,
        is_wall_pier: bool = False
    ) -> Chapter18_VerificationResult:
        """
        Ejecuta verificacion segun ACI 318-25 Capitulo 18.

        Verifica muros estructurales especiales segun 18.10.

        Args:
            pier: Entidad Pier con geometria y armadura
            sdc: Categoria de Diseno Sismico (default D)
            Vu: Cortante ultimo del analisis (tonf)
            Vu_Eh: Cortante debido a efecto sismico horizontal (tonf)
            delta_u: Desplazamiento de diseno en tope (mm)
            hwcs: Altura del muro desde seccion critica (mm)
            hn_ft: Altura total del edificio (pies)
            sigma_max: Esfuerzo maximo de compresion (MPa) - para elementos de borde
            use_displacement_method: Usar metodo de desplazamiento para bordes
            is_wall_pier: Si es un pilar de muro (segmento estrecho)

        Returns:
            Chapter18_VerificationResult con todos los resultados
        """
        critical_issues = []
        warnings = []

        # Determinar categoria del muro
        wall_category = self._shear_amplification.determine_wall_category(
            sdc, is_sfrs=True, is_precast=False
        )

        # Variables para resultados
        shear_amplification = None
        special_wall = None
        boundary_element = None
        wall_pier_result = None

        # =====================================================================
        # 1. Amplificacion de cortante (18.10.3.3)
        # =====================================================================

        if wall_category == WallCategory.SPECIAL and Vu_Eh > 0:
            # Usar altura del muro si hwcs no se proporciona
            if hwcs <= 0:
                hwcs = pier.height

            shear_amplification = self._shear_amplification.calculate_amplification_factors(
                hwcs=hwcs,
                lw=pier.width,
                hn_ft=hn_ft
            )

            # Calcular cortante de diseno amplificado
            design_shear = self._shear_amplification.calculate_design_shear(
                Vu_Eh=Vu_Eh,
                hwcs=hwcs,
                lw=pier.width,
                hn_ft=hn_ft
            )

            if design_shear.Ve > Vu:
                warnings.append(
                    f"Cortante amplificado Ve={design_shear.Ve:.1f} > Vu={Vu:.1f} tonf "
                    f"(Omega_v={shear_amplification.Omega_v}, omega_v={shear_amplification.omega_v})"
                )

        # =====================================================================
        # 2. Requisitos de muro especial (18.10.2)
        # =====================================================================

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
                has_double_curtain=pier.double_layer
            )

            if not special_wall.is_ok:
                for warn in special_wall.warnings:
                    if "rho" in warn.lower() or "cortina" in warn.lower():
                        critical_issues.append(warn)
                    else:
                        warnings.append(warn)

        # =====================================================================
        # 3. Elementos de borde (18.10.6)
        # =====================================================================

        if wall_category == WallCategory.SPECIAL:
            # Estimar profundidad de eje neutro (conservador)
            c_estimate = pier.width * 0.3  # Estimacion conservadora

            # Calcular areas para refuerzo transversal
            # Asumir elemento de borde de ancho = espesor del muro
            b_boundary = pier.thickness
            Ag_boundary = b_boundary * (c_estimate * 0.5)  # Area aproximada
            Ach_boundary = Ag_boundary * 0.85

            # Altura de piso estimada
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

        # =====================================================================
        # 4. Pilar de muro (18.10.8) - si aplica
        # =====================================================================

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
                has_single_curtain=not pier.double_layer
            )

            if not wall_pier_result.shear_design.is_ok:
                critical_issues.append(
                    f"Pilar de muro: DCR cortante = {wall_pier_result.shear_design.dcr:.2f} > 1.0"
                )

            warnings.extend(wall_pier_result.warnings)

        # =====================================================================
        # Resumen
        # =====================================================================

        all_ok = (
            (special_wall is None or special_wall.is_ok) and
            (wall_pier_result is None or wall_pier_result.shear_design.is_ok) and
            len(critical_issues) == 0
        )

        return Chapter18_VerificationResult(
            sdc=sdc,
            wall_category=wall_category,
            shear_amplification=shear_amplification,
            special_wall=special_wall,
            boundary_element=boundary_element,
            wall_pier=wall_pier_result,
            all_ok=all_ok,
            critical_issues=critical_issues,
            warnings=warnings,
            aci_reference="ACI 318-25 Capitulo 18"
        )

    def get_chapter_18_summary(
        self,
        result: Chapter18_VerificationResult
    ) -> Dict[str, Any]:
        """
        Genera resumen del Capitulo 18 para respuesta JSON.

        Args:
            result: Resultado de la verificacion

        Returns:
            Dict con resumen estructurado
        """
        summary = {
            'all_ok': result.all_ok,
            'sdc': result.sdc.value,
            'wall_category': result.wall_category.value,
            'critical_issues': result.critical_issues,
            'warnings': result.warnings,
            'aci_reference': result.aci_reference
        }

        # Amplificacion de cortante
        if result.shear_amplification:
            summary['shear_amplification'] = {
                'Omega_v': result.shear_amplification.Omega_v,
                'omega_v': result.shear_amplification.omega_v,
                'combined': result.shear_amplification.combined,
                'hwcs_lw': result.shear_amplification.hwcs_lw,
                'reference': result.shear_amplification.aci_reference
            }

        # Muro especial
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

        # Elementos de borde
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

        # Pilar de muro
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

    def verify_combined(
        self,
        pier: 'Pier',
        pier_forces: 'PierForces' = None,
        sdc: SeismicDesignCategory = SeismicDesignCategory.D,
        delta_u: float = 0,
        hwcs: float = 0,
        hn_ft: float = 0,
        sigma_max: float = 0,
        is_wall_pier: bool = False
    ) -> Dict[str, Any]:
        """
        Verificacion combinada de Capitulos 11 y 18.

        Args:
            pier: Entidad Pier
            pier_forces: Fuerzas del pier
            sdc: Categoria de Diseno Sismico
            delta_u: Desplazamiento de diseno (mm)
            hwcs: Altura desde seccion critica (mm)
            hn_ft: Altura del edificio (pies)
            sigma_max: Esfuerzo maximo (MPa)
            is_wall_pier: Si es pilar de muro

        Returns:
            Dict con resultados de ambos capitulos
        """
        # Obtener valores criticos de fuerzas
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
                    Vu_Eh = Vu  # Asumir que Vu maximo es sismico
                if P > Pu_max:
                    Pu_max = P
                if M > Mua_max:
                    Mua_max = M

        # Verificar Capitulo 11
        chapter_11 = self.verify_chapter_11(
            pier=pier,
            Vu=Vu_max,
            Pu=Pu_max,
            Mua=Mua_max
        )

        # Verificar Capitulo 18 si SDC >= B
        chapter_18 = None
        if sdc != SeismicDesignCategory.A:
            chapter_18 = self.verify_chapter_18(
                pier=pier,
                sdc=sdc,
                Vu=Vu_max,
                Vu_Eh=Vu_Eh,
                delta_u=delta_u,
                hwcs=hwcs,
                hn_ft=hn_ft,
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
            'all_ok': all_ok,
            'critical_issues': all_issues,
            'warnings': all_warnings,
            'chapter_11': self.get_verification_summary(chapter_11),
            'chapter_18': self.get_chapter_18_summary(chapter_18) if chapter_18 else None
        }
