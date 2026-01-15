# app/domain/chapter18/amplification/service.py
"""
Servicio de amplificación de cortante para muros especiales ACI 318-25.

Referencias:
- §18.10.3.3: Amplificación de cortante (Ve = Omega_v × omega_v × Vu)
- §18.10.2: Requisitos de refuerzo para muros especiales
"""
import math
from typing import Optional

from ...constants.shear import OMEGA_0_DEFAULT
from ...constants.seismic import SeismicDesignCategory
from ...constants.units import N_TO_TONF
from ...constants.reinforcement import is_rho_v_ge_rho_h_required
from ..results import (
    ShearAmplificationResult,
    ShearAmplificationFactors,
    SpecialWallRequirements,
)
from .factors import calculate_omega_v, calculate_omega_v_dyn, calculate_factors


class ShearAmplificationService:
    """
    Servicio para calcular amplificación de cortante según ACI 318-25 §18.10.3.3.

    Para muros no cubiertos por §18.10.3.1 (segmentos horizontales) o
    §18.10.3.2 (pilares de muro), el cortante de diseño debe amplificarse:

        Ve = Omega_v × omega_v × Vu,Eh

    Alternativa (§18.10.3.3.4): Se permite usar Omega_v × omega_v = Omega_o
    """

    # Constantes ACI 318-25 §18.10.2
    SPACING_MAX_MM = 457.2  # 18 in

    # =========================================================================
    # Amplificación de Cortante (§18.10.3.3)
    # =========================================================================

    def calculate_omega_v(self, hwcs: float, lw: float) -> float:
        """Calcula factor Omega_v. Ver factors.calculate_omega_v."""
        return calculate_omega_v(hwcs, lw)

    def calculate_omega_v_dyn(
        self,
        hwcs: float,
        lw: float,
        hn_ft: Optional[float] = None
    ) -> float:
        """Calcula factor omega_v. Ver factors.calculate_omega_v_dyn."""
        return calculate_omega_v_dyn(hwcs, lw, hn_ft)

    def calculate_factors(
        self,
        hwcs: float,
        lw: float,
        hn_ft: float = 0
    ) -> ShearAmplificationFactors:
        """Calcula factores. Ver factors.calculate_factors."""
        return calculate_factors(hwcs, lw, hn_ft)

    def calculate_amplified_shear(
        self,
        Vu: float,
        hwcs: float,
        lw: float,
        hn_ft: Optional[float] = None,
        use_omega_0: bool = False,
        omega_0: float = OMEGA_0_DEFAULT
    ) -> ShearAmplificationResult:
        """
        Calcula el cortante de diseño amplificado Ve.

        Args:
            Vu: Cortante del análisis debido a sismo (tonf)
            hwcs: Altura del muro desde sección crítica (mm)
            lw: Longitud del muro (mm)
            hn_ft: Altura total del edificio en pies
            use_omega_0: Si usar Omega_0 en lugar de Omega_v × omega_v
            omega_0: Factor de sobrerresistencia del sistema (default 2.5)

        Returns:
            ShearAmplificationResult con el cortante amplificado
        """
        hwcs_lw = hwcs / lw if lw > 0 else 0

        if use_omega_0:
            # Alternativa §18.10.3.3.4
            Omega_v = omega_0
            omega_v_dyn = 1.0
            amplification = omega_0
            aci_reference = "ACI 318-25 §18.10.3.3.4 (Omega_0)"
        else:
            Omega_v = calculate_omega_v(hwcs, lw)
            omega_v_dyn = calculate_omega_v_dyn(hwcs, lw, hn_ft)
            amplification = Omega_v * omega_v_dyn
            aci_reference = "ACI 318-25 §18.10.3.3, Tabla 18.10.3.3.3"

        Ve = amplification * abs(Vu)

        return ShearAmplificationResult(
            Vu_original=Vu,
            Ve=round(Ve, 2),
            Omega_v=round(Omega_v, 3),
            omega_v_dyn=round(omega_v_dyn, 3),
            amplification=round(amplification, 3),
            hwcs_lw=round(hwcs_lw, 2),
            hn_ft=hn_ft,
            applies=True,
            aci_reference=aci_reference
        )

    def should_amplify(
        self,
        is_wall_pier: bool = False,
        is_coupling_beam: bool = False
    ) -> bool:
        """
        Determina si se debe aplicar amplificación de cortante.

        La amplificación NO aplica a:
        - Segmentos horizontales (vigas de acoplamiento) → §18.10.3.1
        - Pilares de muro (wall piers) → §18.10.3.2

        Args:
            is_wall_pier: Si es un pilar de muro
            is_coupling_beam: Si es viga de acoplamiento

        Returns:
            True si debe amplificar el cortante
        """
        if is_coupling_beam:
            return False  # §18.10.3.1
        if is_wall_pier:
            return False  # §18.10.3.2
        return True

    # =========================================================================
    # Requisitos de Refuerzo (§18.10.2)
    # =========================================================================

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
        """
        Verifica requisitos de refuerzo para muros especiales (§18.10.2).

        Args:
            hw: Altura del muro (mm)
            lw: Longitud del muro (mm)
            tw: Espesor del muro (mm)
            rho_l: Cuantía longitudinal actual
            rho_t: Cuantía transversal actual
            spacing_v: Espaciamiento vertical (mm)
            spacing_h: Espaciamiento horizontal (mm)
            Vu: Cortante de demanda (tonf)
            fc: Resistencia del hormigón (MPa)
            lambda_factor: Factor lambda para hormigón liviano
            has_double_curtain: Si tiene doble cortina

        Returns:
            SpecialWallRequirements con resultado de la verificación
        """
        warnings = []
        rho_l_min = RHO_MIN
        rho_t_min = RHO_MIN
        spacing_max = self.SPACING_MAX_MM

        Acv = lw * tw
        # Umbral: lambda × sqrt(f'c) × Acv
        threshold = lambda_factor * math.sqrt(fc) * Acv / N_TO_TONF

        if Vu <= threshold:
            warnings.append(f"Vu={Vu:.1f} <= {threshold:.1f} tonf: Se permite rho_t según §11.6")

        # Verificar espaciamientos
        if spacing_v > spacing_max:
            warnings.append(f"Espaciamiento vertical {spacing_v:.0f}mm > {spacing_max:.0f}mm máximo")
        if spacing_h > spacing_max:
            warnings.append(f"Espaciamiento horizontal {spacing_h:.0f}mm > {spacing_max:.0f}mm máximo")

        # Verificar doble cortina (§18.10.2.2)
        threshold_double = 2 * lambda_factor * math.sqrt(fc) * Acv / N_TO_TONF
        hw_lw = hw / lw if lw > 0 else 0

        requires_double = (Vu > threshold_double) or (hw_lw >= 2.0)
        double_reason = ""

        if Vu > threshold_double:
            double_reason = f"Vu={Vu:.1f} > 2×lambda×sqrt(f'c)×Acv={threshold_double:.1f}"
        elif hw_lw >= 2.0:
            double_reason = f"hw/lw={hw_lw:.2f} >= 2.0"

        if requires_double and not has_double_curtain:
            warnings.append(f"Se requiere doble cortina: {double_reason}")

        # Verificar rho_l >= rho_t para muros bajos (§18.10.4.3)
        # Usa función compartida de constants/reinforcement.py
        rho_l_ge_rho_t_required = is_rho_v_ge_rho_h_required(hw, lw)
        rho_l_ge_rho_t_ok = rho_l >= rho_t if rho_l_ge_rho_t_required else True

        if rho_l_ge_rho_t_required and not rho_l_ge_rho_t_ok:
            warnings.append(f"Para hw/lw={hw_lw:.2f} <= 2.0, se requiere rho_l >= rho_t")

        # Verificar cuantías mínimas
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
            aci_reference="ACI 318-25 §18.10.2"
        )


# =============================================================================
# Alias para compatibilidad
# =============================================================================
ShearAmplificationService.calculate_amplification_factors = ShearAmplificationService.calculate_factors


# =============================================================================
# Verificación de Carga Axial Significativa - ACI 318-25 §18.6.4.6
# =============================================================================

def has_significant_axial(
    Ag: float,
    fc: float,
    Pu: float,
    divisor: float = 10.0
) -> bool:
    """
    Verifica si la carga axial es significativa según ACI 318-25 §18.6.4.6.

    Cuando la carga axial factorizada excede Ag*f'c/10, se requieren
    verificaciones adicionales de confinamiento.

    Args:
        Ag: Área bruta de la sección (mm²)
        fc: Resistencia del concreto (MPa)
        Pu: Carga axial máxima factorizada (tonf), valor absoluto
        divisor: Divisor del umbral (default 10.0 para Ag*f'c/10)

    Returns:
        True si |Pu| >= Ag*f'c/divisor

    Reference:
        ACI 318-25 §18.6.4.6
    """
    if Ag <= 0 or fc <= 0:
        return False

    # Umbral: Ag * f'c / divisor, convertido a tonf
    # (mm² × MPa) = N → / TONF_TO_N → tonf
    TONF_TO_N = 9806.65  # 1 tonf = 9806.65 N
    threshold_N = Ag * fc / divisor
    threshold_tonf = threshold_N / TONF_TO_N

    return abs(Pu) >= threshold_tonf
