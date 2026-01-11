# app/domain/chapter18/beams/service.py
"""
Servicio de verificación para vigas sísmicas ACI 318-25.

Orquesta las verificaciones según la categoría sísmica:
- SPECIAL: §18.6 (todos los checks)
- INTERMEDIATE: §18.4.2 (checks reducidos)
- ORDINARY: §18.3.2 (requisitos mínimos)
- NON_SFRS: §18.14.3 (deriva compatible)

Referencias:
- ACI 318-25 §18.3.2: Vigas de pórticos ordinarios
- ACI 318-25 §18.4.2: Vigas de pórticos intermedios
- ACI 318-25 §18.6: Vigas de pórticos especiales
"""
import math
from typing import List

from ..common import SeismicCategory
from ..seismic_detailing_service import SeismicDetailingService
from ...constants.shear import PHI_SHEAR_SEISMIC
from ...constants.units import N_TO_TONF, TONF_TO_N
from ...shear.concrete_shear import calculate_Vc_beam, check_Vc_zero_condition
from ...shear.steel_shear import calculate_Vs_beam_column
from ...constants.chapter18 import (
    MIN_WIDTH_BEAM_MM as MIN_WIDTH_SPECIAL_MM,
    FIRST_HOOP_MAX_MM,
    HX_MAX_MM,
)
from .results import (
    SeismicBeamResult,
    BeamDimensionalLimitsResult,
    BeamLongitudinalResult,
    BeamTransverseResult,
    BeamShearResult,
)


class SeismicBeamService:
    """
    Servicio principal para verificación de vigas sísmicas.

    Realiza todas las verificaciones aplicables según la categoría sísmica.
    Por defecto asume categoría SPECIAL (la más restrictiva).

    Usa SeismicDetailingService para cálculos comunes de detallamiento.

    Example:
        service = SeismicBeamService()

        # Verificación especial (default)
        result = service.verify_beam(...)

        # Verificación intermedia
        result = service.verify_beam(..., category=SeismicCategory.INTERMEDIATE)
    """

    def __init__(self):
        """Inicializa el servicio con dependencias."""
        self._detailing = SeismicDetailingService()

    def verify_beam(
        self,
        # Geometría
        bw: float,
        h: float,
        d: float,
        ln: float,
        cover: float,
        # Materiales
        fc: float,
        fy: float,
        fyt: float,
        # Refuerzo longitudinal
        As_top: float,
        As_bottom: float,
        n_bars_top: int,
        n_bars_bottom: int,
        db_long: float,
        # Refuerzo transversal
        s_in_zone: float,
        s_outside_zone: float,
        Av: float,
        first_hoop_distance: float = 50,
        hx: float = 200,
        # Fuerzas
        Vu: float = 0,
        Mpr_left: float = 0,
        Mpr_right: float = 0,
        Pu: float = 0,
        # Momentos para verificación de relaciones
        Mn_pos_face: float = 0,
        Mn_neg_face: float = 0,
        Mn_min_section: float = 0,
        Mn_max_face: float = 0,
        # Columna (para proyección)
        c1: float = 0,
        c2: float = 0,
        projection: float = 0,
        # Opciones
        category: SeismicCategory = SeismicCategory.SPECIAL,
        steel_grade: int = 60,
        lambda_factor: float = 1.0,
    ) -> SeismicBeamResult:
        """
        Verifica una viga según los requisitos sísmicos aplicables.

        Args:
            bw: Ancho del alma (mm)
            h: Altura total de la viga (mm)
            d: Profundidad efectiva (mm)
            ln: Luz libre (mm)
            cover: Recubrimiento (mm)
            fc: f'c del concreto (MPa)
            fy: Fluencia del refuerzo longitudinal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            As_top: Área de refuerzo superior (mm²)
            As_bottom: Área de refuerzo inferior (mm²)
            n_bars_top: Número de barras superiores
            n_bars_bottom: Número de barras inferiores
            db_long: Diámetro de barra longitudinal más pequeña (mm)
            s_in_zone: Espaciamiento en zona de hoops (mm)
            s_outside_zone: Espaciamiento fuera de zona (mm)
            Av: Área de refuerzo transversal (mm²)
            first_hoop_distance: Distancia del primer hoop a cara (mm)
            hx: Espaciamiento entre barras soportadas (mm)
            Vu: Cortante último del análisis (tonf)
            Mpr_left: Momento probable izquierdo (tonf-m)
            Mpr_right: Momento probable derecho (tonf-m)
            Pu: Carga axial (tonf, generalmente 0 para vigas)
            Mn_pos_face: M+ en cara del nudo (tonf-m)
            Mn_neg_face: M- en cara del nudo (tonf-m)
            Mn_min_section: M mínimo en cualquier sección (tonf-m)
            Mn_max_face: M máximo en cara de cualquier nudo (tonf-m)
            c1: Dimensión de columna paralela a ln (mm)
            c2: Dimensión de columna perpendicular a ln (mm)
            projection: Proyección de viga más allá de columna (mm)
            category: Categoría sísmica (default SPECIAL)
            steel_grade: Grado del acero (60 u 80)
            lambda_factor: Factor para concreto liviano

        Returns:
            SeismicBeamResult con todas las verificaciones aplicables
        """
        warnings: List[str] = []
        dcr_max = 0.0
        critical_check = ""

        # Inicializar resultados como None
        dimensional = None
        longitudinal = None
        transverse = None
        shear = None

        # ==== VERIFICACIONES SEGÚN CATEGORÍA ====

        if category == SeismicCategory.SPECIAL:
            # §18.6.2 - Límites dimensionales
            dimensional = self._check_dimensional_limits(
                bw, h, d, ln, c1, c2, projection
            )
            if not dimensional.is_ok:
                dcr_max = max(dcr_max, 1.5)
                critical_check = "dimensional_limits"
                warnings.append("No cumple límites dimensionales §18.6.2")

            # §18.6.3 - Refuerzo longitudinal
            longitudinal = self._check_longitudinal(
                As_top, As_bottom, bw, d, n_bars_top, n_bars_bottom,
                Mn_pos_face, Mn_neg_face, Mn_min_section, Mn_max_face,
                steel_grade, category
            )
            if not longitudinal.is_ok:
                if not longitudinal.rho_ok:
                    dcr = max(longitudinal.rho_top, longitudinal.rho_bottom) / longitudinal.rho_max
                    if dcr > dcr_max:
                        dcr_max = dcr
                        critical_check = "longitudinal_rho"
                warnings.append("No cumple refuerzo longitudinal §18.6.3")

            # §18.6.4 - Refuerzo transversal
            transverse = self._check_transverse(
                h, d, db_long, s_in_zone, s_outside_zone,
                first_hoop_distance, hx, steel_grade, category
            )
            if not transverse.is_ok:
                warnings.extend(transverse.warnings)
                if transverse.s_in_zone > transverse.s_max_zone:
                    dcr = transverse.s_in_zone / transverse.s_max_zone
                    if dcr > dcr_max:
                        dcr_max = dcr
                        critical_check = "transverse"

        elif category == SeismicCategory.INTERMEDIATE:
            # §18.4.2 - Requisitos intermedios (simplificados)
            longitudinal = self._check_longitudinal(
                As_top, As_bottom, bw, d, n_bars_top, n_bars_bottom,
                Mn_pos_face, Mn_neg_face, Mn_min_section, Mn_max_face,
                steel_grade, category
            )
            if not longitudinal.is_ok:
                warnings.append("No cumple refuerzo longitudinal §18.4.2")

            transverse = self._check_transverse(
                h, d, db_long, s_in_zone, s_outside_zone,
                first_hoop_distance, hx, steel_grade, category
            )
            if not transverse.is_ok:
                warnings.extend(transverse.warnings)

        elif category == SeismicCategory.ORDINARY:
            # §18.3.2 - Solo requisitos mínimos de continuidad
            longitudinal = self._check_longitudinal(
                As_top, As_bottom, bw, d, n_bars_top, n_bars_bottom,
                0, 0, 0, 0,  # Sin verificación de relaciones de momento
                steel_grade, category
            )
            if not longitudinal.is_ok:
                warnings.append("No cumple refuerzo longitudinal §18.3.2")

        # §18.6.5 / §18.4.2.3 - Cortante (aplica para SPECIAL e INTERMEDIATE)
        if category in (SeismicCategory.SPECIAL, SeismicCategory.INTERMEDIATE):
            if Vu > 0 or (Mpr_left > 0 and Mpr_right > 0):
                Ag = bw * h
                shear = self._check_shear(
                    bw, d, ln, fc, fyt, Av, s_in_zone,
                    Vu, Mpr_left, Mpr_right, Pu, Ag,
                    lambda_factor, category
                )
                if shear.dcr > dcr_max:
                    dcr_max = shear.dcr
                    critical_check = "shear"
                if not shear.is_ok:
                    warnings.append(f"No cumple cortante {category.beam_section}")

        # Determinar resultado global
        is_ok = dcr_max <= 1.0 and len(warnings) == 0

        return SeismicBeamResult(
            category=category,
            dimensional_limits=dimensional,
            longitudinal=longitudinal,
            transverse=transverse,
            shear=shear,
            is_ok=is_ok,
            dcr_max=round(dcr_max, 3),
            critical_check=critical_check,
            warnings=warnings,
        )

    def _check_dimensional_limits(
        self,
        bw: float,
        h: float,
        d: float,
        ln: float,
        c1: float,
        c2: float,
        projection: float,
    ) -> BeamDimensionalLimitsResult:
        """Verifica límites dimensionales §18.6.2."""
        # (a) ln >= 4d
        ln_min = 4 * d
        ln_ok = ln >= ln_min

        # (b) bw >= max(0.3h, 10")
        bw_min = max(0.3 * h, MIN_WIDTH_SPECIAL_MM)
        bw_ok = bw >= bw_min

        # (c) Proyección <= min(c2, 0.75*c1)
        if c1 > 0 and c2 > 0:
            projection_max = min(c2, 0.75 * c1)
            projection_ok = projection <= projection_max
        else:
            projection_max = 0
            projection_ok = True

        is_ok = ln_ok and bw_ok and projection_ok

        return BeamDimensionalLimitsResult(
            ln=ln,
            d=d,
            ln_min=ln_min,
            ln_ok=ln_ok,
            bw=bw,
            h=h,
            bw_min=bw_min,
            bw_ok=bw_ok,
            projection=projection,
            projection_max=projection_max,
            projection_ok=projection_ok,
            is_ok=is_ok,
        )

    def _check_longitudinal(
        self,
        As_top: float,
        As_bottom: float,
        bw: float,
        d: float,
        n_bars_top: int,
        n_bars_bottom: int,
        Mn_pos_face: float,
        Mn_neg_face: float,
        Mn_min_section: float,
        Mn_max_face: float,
        steel_grade: int,
        category: SeismicCategory,
    ) -> BeamLongitudinalResult:
        """Verifica refuerzo longitudinal §18.6.3 / §18.4.2.1 / §18.3.2."""
        # Cuantías
        rho_top = As_top / (bw * d) if bw * d > 0 else 0
        rho_bottom = As_bottom / (bw * d) if bw * d > 0 else 0

        # ρmax según grado
        if steel_grade >= 80:
            rho_max = 0.020
        else:
            rho_max = 0.025

        rho_ok = rho_top <= rho_max and rho_bottom <= rho_max

        # Número mínimo de barras
        n_bars_min = 2
        n_bars_ok = n_bars_top >= n_bars_min and n_bars_bottom >= n_bars_min

        # Relaciones de momento (solo para SPECIAL)
        if category == SeismicCategory.SPECIAL:
            moment_ratio_face_required = 0.5
            moment_ratio_section_required = 0.25
        elif category == SeismicCategory.INTERMEDIATE:
            moment_ratio_face_required = 1/3
            moment_ratio_section_required = 1/5
        else:
            moment_ratio_face_required = 0
            moment_ratio_section_required = 0

        # M+ >= ratio * M- en cara
        if Mn_neg_face > 0:
            moment_ratio_face = Mn_pos_face / Mn_neg_face
        else:
            moment_ratio_face = 1.0

        moment_ratio_face_ok = moment_ratio_face >= moment_ratio_face_required or moment_ratio_face_required == 0

        # M en sección >= ratio * Mmax en cara
        if Mn_max_face > 0:
            moment_ratio_section = Mn_min_section / Mn_max_face
        else:
            moment_ratio_section = 1.0

        moment_ratio_section_ok = moment_ratio_section >= moment_ratio_section_required or moment_ratio_section_required == 0

        is_ok = rho_ok and n_bars_ok and moment_ratio_face_ok and moment_ratio_section_ok

        return BeamLongitudinalResult(
            As_top=As_top,
            As_bottom=As_bottom,
            rho_top=round(rho_top, 4),
            rho_bottom=round(rho_bottom, 4),
            rho_max=rho_max,
            rho_ok=rho_ok,
            n_bars_top=n_bars_top,
            n_bars_bottom=n_bars_bottom,
            n_bars_min=n_bars_min,
            n_bars_ok=n_bars_ok,
            Mn_pos_face=Mn_pos_face,
            Mn_neg_face=Mn_neg_face,
            moment_ratio_face=round(moment_ratio_face, 3),
            moment_ratio_face_required=moment_ratio_face_required,
            moment_ratio_face_ok=moment_ratio_face_ok,
            Mn_min_section=Mn_min_section,
            Mn_max_face=Mn_max_face,
            moment_ratio_section=round(moment_ratio_section, 3),
            moment_ratio_section_required=moment_ratio_section_required,
            moment_ratio_section_ok=moment_ratio_section_ok,
            is_ok=is_ok,
        )

    def _check_transverse(
        self,
        h: float,
        d: float,
        db_long: float,
        s_in_zone: float,
        s_outside_zone: float,
        first_hoop_distance: float,
        hx: float,
        steel_grade: int,
        category: SeismicCategory,
    ) -> BeamTransverseResult:
        """
        Verifica refuerzo transversal §18.6.4 / §18.4.2.4.

        Delega cálculos comunes a SeismicDetailingService.
        """
        warnings = []

        # Usar SeismicDetailingService para cálculos comunes
        # Longitud de zona de confinamiento
        zone_result = self._detailing.calculate_confinement_zone_length(
            element_type='beam', h=h, d=d, category=category
        )
        zone_length = zone_result.lo

        # Espaciamiento en zona
        spacing_result = self._detailing.check_transverse_spacing_in_zone(
            s_provided=s_in_zone,
            d=d,
            db_long=db_long,
            element_type='beam',
            steel_grade=steel_grade,
            category=category,
        )
        s_max_zone = spacing_result.s_max
        s_zone_ok = spacing_result.s_ok
        if not s_zone_ok:
            warnings.append(f"s en zona={s_in_zone:.0f}mm > s_max={s_max_zone:.0f}mm ({spacing_result.governing_limit})")

        # Primer hoop
        first_hoop_result = self._detailing.check_first_hoop_position(
            distance=first_hoop_distance, element_type='beam'
        )
        first_hoop_max = first_hoop_result.max_distance
        first_hoop_ok = first_hoop_result.is_ok
        if not first_hoop_ok:
            warnings.append(f"Primer hoop={first_hoop_distance:.0f}mm > {first_hoop_max:.0f}mm")

        # Fuera de zona: s <= d/2
        s_max_outside = d / 2
        s_outside_ok = s_outside_zone <= s_max_outside
        if not s_outside_ok:
            warnings.append(f"s fuera zona={s_outside_zone:.0f}mm > d/2={s_max_outside:.0f}mm")

        # Soporte lateral (hx)
        hx_result = self._detailing.check_lateral_support(
            hx_provided=hx, element_type='beam'
        )
        hx_ok = hx_result.hx_ok
        if not hx_ok:
            warnings.append(f"hx={hx:.0f}mm > {hx_result.hx_max:.0f}mm")

        is_ok = s_zone_ok and first_hoop_ok and s_outside_ok and hx_ok

        return BeamTransverseResult(
            zone_length=zone_length,
            h=h,
            s_in_zone=s_in_zone,
            s_max_zone=round(s_max_zone, 0),
            s_zone_ok=s_zone_ok,
            first_hoop_distance=first_hoop_distance,
            first_hoop_max=first_hoop_max,
            first_hoop_ok=first_hoop_ok,
            s_outside_zone=s_outside_zone,
            s_max_outside=round(s_max_outside, 0),
            s_outside_ok=s_outside_ok,
            hx_provided=hx,
            hx_max=hx_result.hx_max,
            hx_ok=hx_ok,
            is_ok=is_ok,
            warnings=warnings,
        )

    def _check_shear(
        self,
        bw: float,
        d: float,
        ln: float,
        fc: float,
        fyt: float,
        Av: float,
        s: float,
        Vu: float,
        Mpr_left: float,
        Mpr_right: float,
        Pu: float,
        Ag: float,
        lambda_factor: float,
        category: SeismicCategory,
    ) -> BeamShearResult:
        """
        Verifica cortante §18.6.5 / §18.4.2.3.

        Delega cálculos de Vc y Vs a funciones centralizadas en domain/shear/.
        """
        # Calcular Ve por capacidad (Mpr1 + Mpr2)/ln
        if Mpr_left > 0 or Mpr_right > 0:
            # Mpr en tonf-m, ln en mm -> Ve en tonf
            Ve = (Mpr_left + Mpr_right) * 1000 / ln
        else:
            Ve = Vu

        # Cortante de diseño
        Vu_design = max(Ve, Vu)

        # Calcular condiciones individuales para reporte
        seismic_shear_dominates = Ve >= 0.5 * Vu if Vu > 0 else True
        Pu_N = Pu * TONF_TO_N
        low_axial = Pu_N < (Ag * fc / 20)

        # Verificar condición Vc = 0 según §18.6.5.2
        Vc_is_zero = check_Vc_zero_condition(Ve, Vu, Pu, Ag, fc)

        # Usar funciones centralizadas de domain/shear/
        vc_result = calculate_Vc_beam(bw, d, fc, lambda_factor, force_Vc_zero=Vc_is_zero)
        vs_result = calculate_Vs_beam_column(Av, d, s, fyt, bw, fc)

        Vc = vc_result.Vc_N
        Vs = vs_result.Vs_N

        # Vn y phi_Vn
        # φ = 0.60 para vigas sísmicas especiales (§21.2.4.1)
        Vn = Vc + Vs
        phi_Vn = PHI_SHEAR_SEISMIC * Vn

        # Convertir a tonf (dividir N por TONF_TO_N)
        Vc_tonf = Vc / TONF_TO_N
        Vs_tonf = Vs / TONF_TO_N
        phi_Vn_tonf = phi_Vn / TONF_TO_N

        # DCR
        dcr = Vu_design / phi_Vn_tonf if phi_Vn_tonf > 0 else float('inf')
        is_ok = dcr <= 1.0

        return BeamShearResult(
            Ve=round(Ve, 2),
            Vu=round(Vu, 2),
            Vu_design=round(Vu_design, 2),
            Vc=round(Vc_tonf, 2),
            Vs=round(Vs_tonf, 2),
            phi_Vn=round(phi_Vn_tonf, 2),
            dcr=round(dcr, 3),
            is_ok=is_ok,
            Vc_is_zero=Vc_is_zero,
            seismic_shear_dominates=seismic_shear_dominates,
            low_axial=low_axial,
        )
