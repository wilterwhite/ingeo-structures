# app/structural/domain/detailing/seismic.py
"""
Servicio de diseño sísmico según ACI 318-25 Capítulo 18.

Implementa verificaciones para muros estructurales especiales.
"""
from dataclasses import dataclass
from typing import Tuple
import math

from ..constants.seismic import SeismicDesignCategory, WallCategory


@dataclass
class ShearAmplificationFactors:
    """Factores de amplificación de cortante según Tabla 18.10.3.3.3."""
    Omega_v: float           # Factor de sobrerresistencia a flexión
    omega_v: float           # Factor de amplificación dinámica
    combined: float          # Omega_v * omega_v
    hwcs_lw: float           # Relación altura/longitud
    hn_ft: float            # Altura del edificio (pies)
    aci_reference: str       # Referencia ACI


@dataclass
class SpecialWallRequirements:
    """Requisitos para muros estructurales especiales."""
    rho_l_min: float
    rho_t_min: float
    spacing_max_mm: float
    requires_double_curtain: bool
    double_curtain_reason: str
    rho_l_ge_rho_t: bool
    is_ok: bool
    warnings: list
    aci_reference: str


@dataclass
class DesignShearResult:
    """Resultado del cortante de diseño amplificado."""
    Vu_Eh: float
    Ve: float
    Omega_v: float
    omega_v: float
    hwcs_lw: float
    aci_reference: str


class SeismicDesignService:
    """
    Servicio de diseño sísmico según ACI 318-25 Capítulo 18.
    """

    # Constantes ACI 318-25 Sección 18.10.2
    RHO_L_MIN_SPECIAL = 0.0025
    RHO_T_MIN_SPECIAL = 0.0025
    SPACING_MAX_MM = 457.2  # 18 in

    def calculate_amplification_factors(
        self,
        hwcs: float,
        lw: float,
        hn_ft: float = 0
    ) -> ShearAmplificationFactors:
        """Calcula factores de amplificación según Tabla 18.10.3.3.3."""
        if lw <= 0:
            return ShearAmplificationFactors(
                Omega_v=1.0, omega_v=1.0, combined=1.0,
                hwcs_lw=0, hn_ft=hn_ft,
                aci_reference="ACI 318-25 18.10.3.3.3"
            )

        ratio = hwcs / lw

        if ratio <= 1.0:
            Omega_v = 1.0
        elif ratio >= 2.0:
            Omega_v = 1.5
        else:
            Omega_v = 1.0 + 0.5 * (ratio - 1.0)

        if ratio < 2.0:
            omega_v = 1.0
        else:
            if hn_ft > 0:
                omega_v = max(1.0, 0.8 + 0.09 * (hn_ft ** (1/3)))
            else:
                omega_v = 1.0

        return ShearAmplificationFactors(
            Omega_v=round(Omega_v, 2),
            omega_v=round(omega_v, 2),
            combined=round(Omega_v * omega_v, 2),
            hwcs_lw=round(ratio, 2),
            hn_ft=hn_ft,
            aci_reference="ACI 318-25 Tabla 18.10.3.3.3"
        )

    def calculate_design_shear(
        self,
        Vu_Eh: float,
        hwcs: float,
        lw: float,
        hn_ft: float = 0,
        use_Omega_o: bool = False,
        Omega_o: float = 3.0
    ) -> DesignShearResult:
        """Calcula el cortante de diseño amplificado Ve."""
        if use_Omega_o:
            Ve = Omega_o * Vu_Eh
            return DesignShearResult(
                Vu_Eh=Vu_Eh,
                Ve=round(Ve, 2),
                Omega_v=Omega_o,
                omega_v=1.0,
                hwcs_lw=hwcs / lw if lw > 0 else 0,
                aci_reference="ACI 318-25 18.10.3.3.4"
            )

        factors = self.calculate_amplification_factors(hwcs, lw, hn_ft)
        Ve = factors.combined * Vu_Eh

        return DesignShearResult(
            Vu_Eh=Vu_Eh,
            Ve=round(Ve, 2),
            Omega_v=factors.Omega_v,
            omega_v=factors.omega_v,
            hwcs_lw=factors.hwcs_lw,
            aci_reference="ACI 318-25 18.10.3.3.2"
        )

    def check_special_wall_requirements(
        self,
        hw: float,
        lw: float,
        tw: float,
        rho_l: float,
        rho_t: float,
        spacing_v: float,
        spacing_h: float,
        Vu: float,
        fc: float,
        lambda_factor: float = 1.0,
        has_double_curtain: bool = True
    ) -> SpecialWallRequirements:
        """Verifica requisitos de refuerzo para muros especiales (18.10.2)."""
        warnings = []
        rho_l_min = self.RHO_L_MIN_SPECIAL
        rho_t_min = self.RHO_T_MIN_SPECIAL

        Acv = lw * tw
        N_TO_TONF = 1e-4
        threshold = lambda_factor * math.sqrt(fc) * Acv * N_TO_TONF

        if Vu <= threshold:
            warnings.append(f"Vu={Vu:.1f} <= {threshold:.1f} tonf: Se permite rho_t según 11.6")

        spacing_max = self.SPACING_MAX_MM
        if spacing_v > spacing_max:
            warnings.append(f"Espaciamiento vertical {spacing_v:.0f}mm > {spacing_max:.0f}mm máximo")
        if spacing_h > spacing_max:
            warnings.append(f"Espaciamiento horizontal {spacing_h:.0f}mm > {spacing_max:.0f}mm máximo")

        threshold_double = 2 * lambda_factor * math.sqrt(fc) * Acv * N_TO_TONF
        hw_lw = hw / lw if lw > 0 else 0

        requires_double = (Vu > threshold_double) or (hw_lw >= 2.0)
        double_reason = ""

        if Vu > threshold_double:
            double_reason = f"Vu={Vu:.1f} > 2*lambda*sqrt(f'c)*Acv={threshold_double:.1f}"
        elif hw_lw >= 2.0:
            double_reason = f"hw/lw={hw_lw:.2f} >= 2.0"

        if requires_double and not has_double_curtain:
            warnings.append(f"Se requiere doble cortina: {double_reason}")

        rho_l_ge_rho_t_required = hw_lw <= 2.0
        rho_l_ge_rho_t_ok = rho_l >= rho_t if rho_l_ge_rho_t_required else True

        if rho_l_ge_rho_t_required and not rho_l_ge_rho_t_ok:
            warnings.append(f"Para hw/lw={hw_lw:.2f} <= 2.0, se requiere rho_l >= rho_t")

        rho_l_ok = rho_l >= rho_l_min
        rho_t_ok = rho_t >= rho_t_min

        if not rho_l_ok:
            warnings.append(f"rho_l={rho_l:.4f} < {rho_l_min:.4f} mínimo")
        if not rho_t_ok:
            warnings.append(f"rho_t={rho_t:.4f} < {rho_t_min:.4f} mínimo")

        is_ok = (
            rho_l_ok and rho_t_ok and
            rho_l_ge_rho_t_ok and
            spacing_v <= spacing_max and
            spacing_h <= spacing_max and
            (not requires_double or has_double_curtain)
        )

        return SpecialWallRequirements(
            rho_l_min=rho_l_min,
            rho_t_min=rho_t_min,
            spacing_max_mm=spacing_max,
            requires_double_curtain=requires_double,
            double_curtain_reason=double_reason,
            rho_l_ge_rho_t=rho_l_ge_rho_t_required,
            is_ok=is_ok,
            warnings=warnings,
            aci_reference="ACI 318-25 18.10.2"
        )

    def determine_wall_category(
        self,
        sdc: SeismicDesignCategory,
        is_sfrs: bool = True,
        is_precast: bool = False
    ) -> WallCategory:
        """Determina la categoría del muro basado en SDC."""
        if sdc in (SeismicDesignCategory.A, SeismicDesignCategory.B):
            return WallCategory.ORDINARY

        if sdc == SeismicDesignCategory.C:
            return WallCategory.INTERMEDIATE if is_precast else WallCategory.ORDINARY

        # SDC D, E, F
        return WallCategory.SPECIAL if is_sfrs else WallCategory.ORDINARY
