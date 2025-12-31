# app/domain/chapter18/amplification.py
"""
Amplificación de cortante para muros estructurales especiales según ACI 318-25.

Referencias ACI 318-25:
- §18.10.3.3: Amplificación de cortante (Ve = Omega_v × omega_v × Vu)
- Tabla 18.10.3.3.3: Factores Omega_v y omega_v
- §18.10.2: Requisitos de refuerzo para muros especiales
"""
import math
from dataclasses import dataclass, field
from typing import Optional, List

from ..constants.shear import (
    OMEGA_V_MIN,
    OMEGA_V_MAX,
    OMEGA_V_DYN_COEF,
    OMEGA_V_DYN_BASE,
    OMEGA_V_DYN_MIN,
    OMEGA_0_DEFAULT,
    WALL_PIER_HW_LW_LIMIT,
)
from ..constants.seismic import SeismicDesignCategory, WallCategory
from ..constants.units import N_TO_TONF


# =============================================================================
# Dataclasses
# =============================================================================

@dataclass
class ShearAmplificationResult:
    """Resultado de la amplificación de cortante §18.10.3.3."""
    Vu_original: float      # Cortante original del análisis (tonf)
    Ve: float               # Cortante de diseño amplificado (tonf)
    Omega_v: float          # Factor de sobrerresistencia a flexión
    omega_v_dyn: float      # Factor de amplificación dinámica
    amplification: float    # Factor total (Omega_v × omega_v_dyn)
    hwcs_lw: float          # Relación hwcs/lw
    hn_ft: Optional[float]  # Altura del edificio en pies
    applies: bool           # Si aplica la amplificación
    aci_reference: str      # Referencia ACI


@dataclass
class ShearAmplificationFactors:
    """Factores de amplificación según Tabla 18.10.3.3.3."""
    Omega_v: float          # Factor de sobrerresistencia a flexión
    omega_v_dyn: float      # Factor de amplificación dinámica
    combined: float         # Omega_v × omega_v_dyn
    hwcs_lw: float          # Relación altura/longitud
    hn_ft: float            # Altura del edificio (pies)
    aci_reference: str      # Referencia ACI


@dataclass
class SpecialWallRequirements:
    """Requisitos para muros estructurales especiales (ACI 318-25 §18.10.2)."""
    rho_l_min: float                    # Cuantía longitudinal mínima
    rho_t_min: float                    # Cuantía transversal mínima
    spacing_max_mm: float               # Espaciamiento máximo (mm)
    requires_double_curtain: bool       # Si requiere doble cortina
    double_curtain_reason: str          # Razón de doble cortina
    rho_l_ge_rho_t: bool               # Si aplica rho_l >= rho_t
    is_ok: bool                         # Si cumple todos los requisitos
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = ""


# =============================================================================
# Servicio Principal
# =============================================================================

class ShearAmplificationService:
    """
    Servicio para calcular amplificación de cortante según ACI 318-25 §18.10.3.3.

    Para muros no cubiertos por §18.10.3.1 (segmentos horizontales) o
    §18.10.3.2 (pilares de muro), el cortante de diseño debe amplificarse:

        Ve = Omega_v × omega_v × Vu,Eh

    Tabla 18.10.3.3.3:
    | hwcs/lw    | Omega_v           | omega_v                      |
    |------------|-------------------|------------------------------|
    | <= 1.0     | 1.0               | 1.0                          |
    | 1.0 - 2.0  | interpolación     | 1.0                          |
    | >= 2.0     | 1.5               | 0.8 + 0.09×hn^(1/3) >= 1.0   |

    Alternativa (§18.10.3.3.4): Se permite usar Omega_v × omega_v = Omega_o
    """

    # Constantes ACI 318-25 §18.10.2
    RHO_L_MIN_SPECIAL = 0.0025
    RHO_T_MIN_SPECIAL = 0.0025
    SPACING_MAX_MM = 457.2  # 18 in

    # =========================================================================
    # Amplificación de Cortante (§18.10.3.3)
    # =========================================================================

    def calculate_omega_v(self, hwcs: float, lw: float) -> float:
        """
        Calcula factor de sobrerresistencia Omega_v según Tabla 18.10.3.3.3.

        Args:
            hwcs: Altura del muro desde sección crítica (mm)
            lw: Longitud del muro (mm)

        Returns:
            Factor Omega_v (1.0 a 1.5)
        """
        if lw <= 0:
            return OMEGA_V_MIN

        ratio = hwcs / lw

        if ratio <= 1.0:
            return OMEGA_V_MIN
        elif ratio >= WALL_PIER_HW_LW_LIMIT:
            return OMEGA_V_MAX
        else:
            # Interpolación lineal entre 1.0 y 2.0
            return OMEGA_V_MIN + (OMEGA_V_MAX - OMEGA_V_MIN) * (ratio - 1.0)

    def calculate_omega_v_dyn(
        self,
        hwcs: float,
        lw: float,
        hn_ft: Optional[float] = None
    ) -> float:
        """
        Calcula factor de amplificación dinámica omega_v según Tabla 18.10.3.3.3.

        Args:
            hwcs: Altura del muro desde sección crítica (mm)
            lw: Longitud del muro (mm)
            hn_ft: Altura total del edificio en pies

        Returns:
            Factor omega_v (>= 1.0)
        """
        if lw <= 0:
            return OMEGA_V_DYN_MIN

        ratio = hwcs / lw

        if ratio < WALL_PIER_HW_LW_LIMIT:
            return OMEGA_V_DYN_MIN

        # Para hwcs/lw >= 2.0: omega_v = 0.8 + 0.09 × hn^(1/3) >= 1.0
        if hn_ft is None or hn_ft <= 0:
            return OMEGA_V_DYN_MIN

        omega_v_dyn = OMEGA_V_DYN_BASE + OMEGA_V_DYN_COEF * (hn_ft ** (1/3))
        return max(OMEGA_V_DYN_MIN, omega_v_dyn)

    def calculate_factors(
        self,
        hwcs: float,
        lw: float,
        hn_ft: float = 0
    ) -> ShearAmplificationFactors:
        """
        Calcula factores de amplificación según Tabla 18.10.3.3.3.

        Args:
            hwcs: Altura del muro desde sección crítica (mm)
            lw: Longitud del muro (mm)
            hn_ft: Altura del edificio en pies

        Returns:
            ShearAmplificationFactors con los factores calculados
        """
        if lw <= 0:
            return ShearAmplificationFactors(
                Omega_v=1.0, omega_v_dyn=1.0, combined=1.0,
                hwcs_lw=0, hn_ft=hn_ft,
                aci_reference="ACI 318-25 Tabla 18.10.3.3.3"
            )

        Omega_v = self.calculate_omega_v(hwcs, lw)
        omega_v_dyn = self.calculate_omega_v_dyn(hwcs, lw, hn_ft if hn_ft > 0 else None)

        return ShearAmplificationFactors(
            Omega_v=round(Omega_v, 3),
            omega_v_dyn=round(omega_v_dyn, 3),
            combined=round(Omega_v * omega_v_dyn, 3),
            hwcs_lw=round(hwcs / lw, 2),
            hn_ft=hn_ft,
            aci_reference="ACI 318-25 Tabla 18.10.3.3.3"
        )

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
            Omega_v = self.calculate_omega_v(hwcs, lw)
            omega_v_dyn = self.calculate_omega_v_dyn(hwcs, lw, hn_ft)
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
        rho_l_min = self.RHO_L_MIN_SPECIAL
        rho_t_min = self.RHO_T_MIN_SPECIAL
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
        rho_l_ge_rho_t_required = hw_lw <= 2.0
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

    # =========================================================================
    # Clasificación de Muros
    # =========================================================================

    def determine_wall_category(
        self,
        sdc: SeismicDesignCategory,
        is_sfrs: bool = True,
        is_precast: bool = False
    ) -> WallCategory:
        """
        Determina la categoría del muro basado en SDC.

        Args:
            sdc: Categoría de Diseño Sísmico
            is_sfrs: Si es parte del sistema resistente a fuerzas sísmicas
            is_precast: Si es muro prefabricado

        Returns:
            WallCategory (ORDINARY, INTERMEDIATE, SPECIAL)
        """
        if sdc in (SeismicDesignCategory.A, SeismicDesignCategory.B):
            return WallCategory.ORDINARY

        if sdc == SeismicDesignCategory.C:
            return WallCategory.INTERMEDIATE if is_precast else WallCategory.ORDINARY

        # SDC D, E, F
        return WallCategory.SPECIAL if is_sfrs else WallCategory.ORDINARY


# =============================================================================
# Aliases para compatibilidad (deprecated)
# =============================================================================

# Alias para método renombrado
ShearAmplificationService.calculate_amplification_factors = ShearAmplificationService.calculate_factors
