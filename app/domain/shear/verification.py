# app/domain/shear/verification.py
"""
Servicio de verificacion de corte para muros y columnas segun ACI 318-25.

Este modulo implementa la verificacion de resistencia al corte para:
- Muros estructurales (Capitulo 11, Seccion 11.5.4)
- Muros estructurales especiales (Capitulo 18, Seccion 18.10.4)
- Columnas y vigas (Capitulo 22, Seccion 22.5)

Ver constants/shear.py para las referencias ACI completas.
"""
import math
from typing import Tuple, List, Optional

from ..constants.materials import (
    LAMBDA_NORMAL,
    get_effective_fc_shear,
    get_effective_fyt_shear,
)
from ..constants.shear import (
    PHI_SHEAR,
    ALPHA_C_SQUAT,
    ALPHA_C_SLENDER,
    HW_LW_SQUAT_LIMIT,
    HW_LW_SLENDER_LIMIT,
    ALPHA_C_TENSION_STRESS_MPA,
    VN_MAX_INDIVIDUAL_COEF,
    VN_MAX_GROUP_COEF,
    VC_COEF_COLUMN,
    VS_MAX_COEF,
    ASPECT_RATIO_WALL_LIMIT,
    DEFAULT_COVER_MM,
    N_TO_TONF,
    calculate_alpha_sh,
    ALPHA_SH_MIN,
)
from ..constants.reinforcement import check_rho_vertical_ge_horizontal
from .results import (
    ShearResult,
    CombinedShearResult,
    WallGroupShearResult,
)


class ShearVerificationService:
    """
    Servicio para verificacion de corte en muros y columnas segun ACI 318-25.

    Selecciona automaticamente la formula correcta segun la relacion de aspecto:
    - lw/tw >= 4: MUROS (Seccion 18.10.4)
    - lw/tw < 4:  COLUMNAS (Seccion 22.5)

    Unidades: entrada en mm/MPa, salida en tonf.
    """

    def is_wall(self, lw: float, tw: float) -> bool:
        """Determina si la seccion es muro (lw/tw >= 4) o columna."""
        if tw <= 0:
            return True
        return (lw / tw) >= ASPECT_RATIO_WALL_LIMIT

    def calculate_alpha_c(
        self,
        hw: float,
        lw: float,
        hw_wall_total: Optional[float] = None,
        Nu: float = 0,
        Ag: float = 0
    ) -> float:
        """
        Calcula el coeficiente alpha_c segun Tabla 18.10.4.1 y Ec. 11.5.4.4.

        Para muros sin tension axial neta:
        - alpha_c = 0.25 si hw/lw <= 1.5 (muros rechonchos)
        - alpha_c = 0.17 si hw/lw >= 2.0 (muros esbeltos)
        - Interpolacion lineal entre 1.5 y 2.0

        Para muros con tension axial neta (Nu < 0):
        - alpha_c = 2 * (1 + Nu/(3.45*Ag)) >= 0  [Ec. 11.5.4.4]
        - Donde 3.45 MPa = 500 psi

        Args:
            hw: Altura del segmento/piso (mm)
            lw: Largo del muro (mm)
            hw_wall_total: Altura total del muro (opcional, para segmentos)
            Nu: Carga axial factorada (N, negativo para tension)
            Ag: Area bruta de la seccion (mm²)
        """
        if lw <= 0:
            return ALPHA_C_SLENDER

        # Ecuacion 11.5.4.4: Muros con tension axial neta
        # Nu es negativo para tension
        # US: alpha_c = 2 * (1 + Nu/(500*Ag)) >= 0
        # SI: alpha_c = 0.17 * (1 + (Nu/Ag)/3.45) >= 0
        # Donde 2 (US) = 0.17 (SI) y 500 psi = 3.45 MPa
        if Nu < 0 and Ag > 0:
            sigma_u = Nu / Ag  # Esfuerzo axial en MPa (negativo para tension)
            alpha_c_tension = ALPHA_C_SLENDER * (1.0 + sigma_u / ALPHA_C_TENSION_STRESS_MPA)
            return max(0.0, alpha_c_tension)

        # Caso normal: usar Tabla 18.10.4.1 basada en hw/lw
        ratio = hw / lw

        if hw_wall_total is not None and hw_wall_total > 0:
            ratio = max(ratio, hw_wall_total / lw)

        if ratio <= HW_LW_SQUAT_LIMIT:
            return ALPHA_C_SQUAT
        elif ratio >= HW_LW_SLENDER_LIMIT:
            return ALPHA_C_SLENDER
        else:
            return ALPHA_C_SQUAT - (ALPHA_C_SQUAT - ALPHA_C_SLENDER) * \
                   (ratio - HW_LW_SQUAT_LIMIT) / (HW_LW_SLENDER_LIMIT - HW_LW_SQUAT_LIMIT)

    def check_minimum_reinforcement(
        self,
        hw: float,
        lw: float,
        rho_vertical: float,
        rho_horizontal: float
    ) -> Tuple[bool, str]:
        """
        Verifica cuantia minima segun 18.10.4.3.

        Requisito: Si hw/lw <= 2.0, entonces rho_v >= rho_h
        Usa función compartida de constants/reinforcement.py.
        """
        return check_rho_vertical_ge_horizontal(hw, lw, rho_vertical, rho_horizontal)

    # =========================================================================
    # CALCULO DE RESISTENCIA NOMINAL
    # =========================================================================

    def calculate_Vn_wall(
        self,
        lw: float,
        tw: float,
        hw: float,
        fc: float,
        fy: float,
        rho_h: float,
        Nu: float = 0,
        bcf: float = 0,
        tcf: float = 0,
        is_lightweight: bool = False,
        lambda_factor: float = 1.0
    ) -> Tuple[float, float, float, float, float, float]:
        """
        Calcula Vn para MUROS segun Ec. 18.10.4.1 y 11.5.4.4.

        Vn = Acv x (alpha_c x lambda x sqrt(f'c) + rho_t x fyt)
        Limite: Vn <= alpha_sh x 0.83 x sqrt(f'c) x Acv

        Para tension axial neta (Nu < 0):
        alpha_c = 2 * (1 + Nu/(3.45*Ag)) >= 0  [Ec. 11.5.4.4]

        Validaciones de materiales (ACI 318-25 §18.2.5, §18.2.6):
        - f'c efectivo: min(f'c, 82.7 MPa) para cortante
        - fyt efectivo: min(fyt, 420 MPa) para cortante

        Factor alpha_sh (ACI 318-25 §18.10.4.4):
        - alpha_sh = 0.7 * (1 + (bw + bcf) * tcf / Acx)^2
        - 1.0 <= alpha_sh <= 1.2

        Args:
            lw: Largo del muro (mm)
            tw: Espesor del muro (mm)
            hw: Altura del muro (mm)
            fc: Resistencia del concreto (MPa)
            fy: Resistencia del acero (MPa)
            rho_h: Cuantia de refuerzo horizontal
            Nu: Carga axial factorada (N, negativo para tension)
            bcf: Ancho del ala comprimida (mm), 0 si no hay ala
            tcf: Espesor del ala comprimida (mm), 0 si no hay ala
            is_lightweight: True si es concreto liviano
            lambda_factor: Factor de concreto liviano (1.0=normal, 0.85=arena, 0.75=todo liviano)

        Returns:
            Tuple (Vc, Vs, Vn, Vn_max, alpha_c, alpha_sh) en tonf
        """
        Acv = lw * tw
        Ag = Acv  # Para muros, Ag = Acv

        # Aplicar limites de materiales (§18.2.5, §18.2.6)
        fc_eff = get_effective_fc_shear(fc, is_lightweight)
        fy_eff = get_effective_fyt_shear(fy)

        # Calcula alpha_c considerando tension axial si aplica
        alpha_c = self.calculate_alpha_c(hw, lw, Nu=Nu, Ag=Ag)

        # Calcula alpha_sh para limite de Vn (§18.10.4.4)
        alpha_sh = calculate_alpha_sh(bw=tw, bcf=bcf, tcf=tcf, lw=lw)

        Vc = Acv * alpha_c * lambda_factor * math.sqrt(fc_eff)
        Vs = Acv * rho_h * fy_eff
        Vn = Vc + Vs

        # Limite con factor alpha_sh (§18.10.4.4)
        Vn_max = alpha_sh * VN_MAX_INDIVIDUAL_COEF * math.sqrt(fc_eff) * Acv
        if Vn > Vn_max:
            Vn = Vn_max

        return (
            Vc / N_TO_TONF,
            Vs / N_TO_TONF,
            Vn / N_TO_TONF,
            Vn_max / N_TO_TONF,
            alpha_c,
            alpha_sh
        )

    def calculate_Vn_column(
        self,
        lw: float,
        tw: float,
        fc: float,
        fy: float,
        rho_h: float,
        cover: float = None
    ) -> Tuple[float, float, float, float, float]:
        """
        Calcula Vn para COLUMNAS/VIGAS segun Seccion 22.5.

        Vc = 0.17 x lambda x sqrt(f'c) x bw x d
        Vs = rho_t x bw x fy x d
        Limite: Vs <= 0.66 x sqrt(f'c) x bw x d

        Returns:
            Tuple (Vc, Vs, Vn, Vn_max, alpha_c) en tonf
        """
        if cover is None:
            cover = DEFAULT_COVER_MM

        bw = tw
        d = max(lw - cover, lw * 0.9)
        alpha_c = VC_COEF_COLUMN

        Vc = VC_COEF_COLUMN * LAMBDA_NORMAL * math.sqrt(fc) * bw * d
        Vs = rho_h * bw * fy * d

        Vs_max = VS_MAX_COEF * math.sqrt(fc) * bw * d
        if Vs > Vs_max:
            Vs = Vs_max

        Vn = Vc + Vs
        Vn_max = Vc + Vs_max

        return (
            Vc / N_TO_TONF,
            Vs / N_TO_TONF,
            Vn / N_TO_TONF,
            Vn_max / N_TO_TONF,
            alpha_c
        )

    # =========================================================================
    # VERIFICACION DE CORTE
    # =========================================================================

    def verify_shear(
        self,
        lw: float,
        tw: float,
        hw: float,
        fc: float,
        fy: float,
        rho_h: float,
        Vu: float,
        Nu: float = 0,
        rho_v: Optional[float] = None,
        bcf: float = 0,
        tcf: float = 0,
        is_lightweight: bool = False,
        lambda_factor: float = 1.0
    ) -> ShearResult:
        """
        Verifica resistencia al corte del muro o columna.

        Selecciona automaticamente la formula segun lw/tw:
        - >= 4: MUROS (18.10.4)
        - < 4:  COLUMNAS (22.5)

        Para muros con tension axial neta (Nu < 0), aplica Ec. 11.5.4.4.

        Validaciones de materiales (ACI 318-25 §18.2.5, §18.2.6):
        - f'c efectivo: min(f'c, 82.7 MPa) para cortante
        - fyt efectivo: min(fyt, 420 MPa) para cortante

        Args:
            Nu: Carga axial factorada (tonf, negativo para tension)
            bcf: Ancho del ala comprimida (mm), 0 si no hay ala
            tcf: Espesor del ala comprimida (mm), 0 si no hay ala
            is_lightweight: True si es concreto liviano
        """
        # Convertir Nu de tonf a N para calculo interno
        Nu_N = Nu * N_TO_TONF
        alpha_sh = ALPHA_SH_MIN  # Default para columnas

        if self.is_wall(lw, tw):
            Vc, Vs, Vn, Vn_max, alpha_c, alpha_sh = self.calculate_Vn_wall(
                lw, tw, hw, fc, fy, rho_h, Nu=Nu_N,
                bcf=bcf, tcf=tcf, is_lightweight=is_lightweight,
                lambda_factor=lambda_factor
            )
            formula_type = "wall"
            aci_reference = "ACI 318-25 11.5.4.3, 18.10.4.1, 18.10.4.4"
            # Agregar referencia a 11.5.4.4 si hay tension
            if Nu < 0:
                aci_reference += ", 11.5.4.4"
        else:
            Vc, Vs, Vn, Vn_max, alpha_c = self.calculate_Vn_column(
                lw, tw, fc, fy, rho_h
            )
            formula_type = "column"
            aci_reference = "ACI 318-25 22.5.5.1"

        phi_Vn = PHI_SHEAR * Vn
        Vu_abs = abs(Vu)
        sf = phi_Vn / Vu_abs if Vu_abs > 0 else float('inf')
        status = "OK" if sf >= 1.0 else "NO OK"
        hw_lw = hw / lw if lw > 0 else 0

        # Verificar cuantia minima (solo muros)
        rho_check_ok = True
        rho_warning = ""
        if formula_type == "wall" and rho_v is not None:
            rho_check_ok, rho_warning = self.check_minimum_reinforcement(
                hw, lw, rho_v, rho_h
            )

        return ShearResult(
            Vc=Vc, Vs=Vs, Vn=Vn, phi_Vn=phi_Vn, Vn_max=Vn_max,
            Vu=Vu_abs, sf=sf, status=status,
            alpha_c=alpha_c, alpha_sh=alpha_sh, hw_lw=hw_lw, formula_type=formula_type,
            rho_check_ok=rho_check_ok, rho_warning=rho_warning,
            aci_reference=aci_reference
        )

    def verify_bidirectional_shear(
        self,
        lw: float,
        tw: float,
        hw: float,
        fc: float,
        fy: float,
        rho_h: float,
        Vu2_max: float,
        Vu3_max: float,
        Nu: float = 0,
        rho_v: Optional[float] = None
    ) -> Tuple[ShearResult, ShearResult]:
        """
        Verifica corte en ambas direcciones.

        - V2: Corte EN EL PLANO (usa lw como dimension)
        - V3: Corte FUERA DEL PLANO (usa tw como dimension)
        """
        result_V2 = self.verify_shear(
            lw=lw, tw=tw, hw=hw, fc=fc, fy=fy, rho_h=rho_h,
            Vu=Vu2_max, Nu=Nu, rho_v=rho_v
        )

        # V3: intercambiar dimensiones (el muro actua como viga)
        result_V3 = self.verify_shear(
            lw=tw, tw=lw, hw=hw, fc=fc, fy=fy, rho_h=rho_h,
            Vu=Vu3_max, Nu=Nu, rho_v=rho_v
        )

        return result_V2, result_V3

    def verify_combined_shear(
        self,
        lw: float,
        tw: float,
        hw: float,
        fc: float,
        fy: float,
        rho_h: float,
        Vu2: float,
        Vu3: float,
        Nu: float = 0,
        combo_name: str = "",
        rho_v: Optional[float] = None,
        lambda_factor: float = 1.0
    ) -> CombinedShearResult:
        """
        Verifica interaccion V2-V3 con SRSS.

        DCR = sqrt[(Vu2/phi*Vn2)^2 + (Vu3/phi*Vn3)^2] <= 1.0
        """
        result_V2 = self.verify_shear(
            lw=lw, tw=tw, hw=hw, fc=fc, fy=fy, rho_h=rho_h,
            Vu=Vu2, Nu=Nu, rho_v=rho_v, lambda_factor=lambda_factor
        )

        result_V3 = self.verify_shear(
            lw=tw, tw=lw, hw=hw, fc=fc, fy=fy, rho_h=rho_h,
            Vu=Vu3, Nu=Nu, rho_v=rho_v, lambda_factor=lambda_factor
        )

        dcr_2 = abs(Vu2) / result_V2.phi_Vn if result_V2.phi_Vn > 0 else 0
        dcr_3 = abs(Vu3) / result_V3.phi_Vn if result_V3.phi_Vn > 0 else 0
        dcr_combined = math.sqrt(dcr_2**2 + dcr_3**2)

        sf = 1.0 / dcr_combined if dcr_combined > 0 else float('inf')
        status = "OK" if dcr_combined <= 1.0 else "NO OK"

        return CombinedShearResult(
            result_V2=result_V2, result_V3=result_V3,
            dcr_2=dcr_2, dcr_3=dcr_3, dcr_combined=dcr_combined,
            sf=sf, status=status, combo_name=combo_name
        )

    def verify_wall_group(
        self,
        segments: List[Tuple[float, float, float]],
        fc: float,
        fy: float,
        rho_h: float,
        Vu_total: float,
        Nu: float = 0,
        rho_v: Optional[float] = None,
        is_lightweight: bool = False,
        lambda_factor: float = 1.0
    ) -> WallGroupShearResult:
        """
        Verifica grupo de segmentos segun 18.10.4.4.

        Limite: Vn_grupo <= Sum(alpha_sh * 0.66 x sqrt(f'c) x Acv)

        Validaciones de materiales (ACI 318-25 §18.2.5, §18.2.6):
        - f'c efectivo: min(f'c, 82.7 MPa) para cortante
        """
        if not segments:
            raise ValueError("Se requiere al menos un segmento")

        # Aplicar limite de materiales
        fc_eff = get_effective_fc_shear(fc, is_lightweight)

        segment_results: List[ShearResult] = []
        Acv_total = 0.0
        Vn_total = 0.0
        Vn_max_contributions = 0.0  # Sum(alpha_sh * 0.66 * sqrt(fc) * Acv)
        total_area = sum(s[0] * s[1] for s in segments)

        for lw, tw, hw in segments:
            Acv_segment = lw * tw
            Acv_total += Acv_segment
            area_ratio = Acv_segment / total_area if total_area > 0 else 1

            result = self.verify_shear(
                lw=lw, tw=tw, hw=hw, fc=fc, fy=fy, rho_h=rho_h,
                Vu=Vu_total * area_ratio, Nu=Nu * area_ratio, rho_v=rho_v,
                is_lightweight=is_lightweight, lambda_factor=lambda_factor
            )
            segment_results.append(result)
            Vn_total += result.Vn

            # Contribucion al limite del grupo con alpha_sh de cada segmento
            alpha_sh = result.alpha_sh
            Vn_max_contributions += alpha_sh * VN_MAX_GROUP_COEF * math.sqrt(fc_eff) * Acv_segment / N_TO_TONF

        Vn_max_group = Vn_max_contributions
        controls_group_limit = Vn_total > Vn_max_group
        Vn_effective = min(Vn_total, Vn_max_group)
        phi_Vn_effective = PHI_SHEAR * Vn_effective

        Vu_abs = abs(Vu_total)
        sf = phi_Vn_effective / Vu_abs if Vu_abs > 0 else float('inf')
        status = "OK" if sf >= 1.0 else "NO OK"

        return WallGroupShearResult(
            segments=segment_results,
            Vn_total=Vn_total, Vn_max_group=Vn_max_group,
            Vn_effective=Vn_effective, phi_Vn_effective=phi_Vn_effective,
            controls_group_limit=controls_group_limit,
            sf=sf, status=status,
            Acv_total=Acv_total, fc=fc, n_segments=len(segments)
        )
