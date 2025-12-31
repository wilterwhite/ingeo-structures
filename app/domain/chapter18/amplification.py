# app/domain/chapter18/amplification.py
"""
Amplificación de cortante para muros estructurales especiales según ACI 318-25.

Este módulo implementa la amplificación de cortante sísmico para muros
especiales que no son wall piers ni segmentos horizontales.

Referencias ACI 318-25:
- §18.10.3.3: Amplificación de cortante (Ve = Omega_v * omega_v * Vu)
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


@dataclass
class ShearAmplificationResult:
    """Resultado de la amplificacion de cortante."""
    Vu_original: float      # Cortante original del analisis (tonf)
    Ve: float               # Cortante de diseno amplificado (tonf)
    omega_v: float          # Factor de sobrerresistencia a flexion
    omega_v_dyn: float      # Factor de amplificacion dinamica
    amplification: float    # Factor total de amplificacion
    hwcs_lw: float          # Relacion hwcs/lw
    hn_ft: Optional[float]  # Altura del edificio en pies
    applies: bool           # Si aplica la amplificacion
    aci_reference: str      # Referencia ACI


@dataclass
class ShearAmplificationFactors:
    """Factores de amplificacion de cortante segun Tabla 18.10.3.3.3."""
    Omega_v: float           # Factor de sobrerresistencia a flexion
    omega_v: float           # Factor de amplificacion dinamica
    combined: float          # Omega_v * omega_v
    hwcs_lw: float           # Relacion altura/longitud
    hn_ft: float             # Altura del edificio (pies)
    aci_reference: str       # Referencia ACI


@dataclass
class DesignShearResult:
    """Resultado del cortante de diseno amplificado."""
    Vu_Eh: float             # Cortante sismico original
    Ve: float                # Cortante de diseno amplificado
    Omega_v: float           # Factor de sobrerresistencia
    omega_v: float           # Factor dinamico
    hwcs_lw: float           # Relacion altura/longitud
    aci_reference: str       # Referencia ACI


@dataclass
class SpecialWallRequirements:
    """Requisitos para muros estructurales especiales (ACI 318-25 S18.10.2)."""
    rho_l_min: float                    # Cuantia longitudinal minima
    rho_t_min: float                    # Cuantia transversal minima
    spacing_max_mm: float               # Espaciamiento maximo (mm)
    requires_double_curtain: bool       # Si requiere doble cortina
    double_curtain_reason: str          # Razon de doble cortina
    rho_l_ge_rho_t: bool               # Si aplica rho_l >= rho_t
    is_ok: bool                         # Si cumple todos los requisitos
    warnings: List[str] = field(default_factory=list)  # Advertencias
    aci_reference: str = ""             # Referencia ACI


class ShearAmplificationService:
    """
    Servicio para calcular amplificacion de cortante segun ACI 318-25 S18.10.3.3.

    Para muros no cubiertos por S18.10.3.1 (segmentos horizontales) o
    S18.10.3.2 (pilares de muro), el cortante de diseno debe amplificarse:

    Ve = Omega_v x omega_v x VuEh

    Donde:
    - VuEh: Cortante debido al efecto sismico horizontal Eh
    - Omega_v: Factor de sobrerresistencia a flexion (Tabla 18.10.3.3.3)
    - omega_v: Factor de amplificacion dinamica (Tabla 18.10.3.3.3)

    Tabla 18.10.3.3.3:
    | hwcs/lw    | Omega_v           | omega_v                        |
    |------------|-------------------|--------------------------------|
    | <= 1.0     | 1.0               | 1.0                            |
    | 1.0 - 2.0  | interpolacion     | 1.0                            |
    | >= 2.0     | 1.5               | 0.8 + 0.09*hn^(1/3) >= 1.0    |

    Alternativas (S18.10.3.3.4-5):
    - Se permite usar Omega_v x omega_v = Omega_o si el codigo incluye factor
    - Si se usa Omega_o, se permite factor de redundancia = 1.0
    """

    def calculate_amplification_factors(
        self,
        hwcs: float,
        lw: float,
        hn_ft: float = 0
    ) -> ShearAmplificationFactors:
        """
        Calcula factores de amplificacion segun Tabla 18.10.3.3.3.

        Args:
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)
            hn_ft: Altura del edificio en pies

        Returns:
            ShearAmplificationFactors con los factores calculados
        """
        if lw <= 0:
            return ShearAmplificationFactors(
                Omega_v=1.0, omega_v=1.0, combined=1.0,
                hwcs_lw=0, hn_ft=hn_ft,
                aci_reference="ACI 318-25 18.10.3.3.3"
            )

        Omega_v = self.calculate_omega_v(hwcs, lw)
        omega_v = self.calculate_omega_v_dyn(hwcs, lw, hn_ft if hn_ft > 0 else None)

        return ShearAmplificationFactors(
            Omega_v=round(Omega_v, 2),
            omega_v=round(omega_v, 2),
            combined=round(Omega_v * omega_v, 2),
            hwcs_lw=round(hwcs / lw, 2),
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
        """
        Calcula el cortante de diseno amplificado Ve.

        Args:
            Vu_Eh: Cortante sismico horizontal (tonf)
            hwcs: Altura desde seccion critica (mm)
            lw: Longitud del muro (mm)
            hn_ft: Altura del edificio (pies)
            use_Omega_o: Si usar factor Omega_o del sistema
            Omega_o: Factor de sobrerresistencia del sistema

        Returns:
            DesignShearResult con el cortante amplificado
        """
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

    def calculate_omega_v(self, hwcs: float, lw: float) -> float:
        """
        Calcula el factor de sobrerresistencia Omega_v segun Tabla 18.10.3.3.3.

        Args:
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)

        Returns:
            Factor Omega_v
        """
        if lw <= 0:
            return OMEGA_V_MIN

        ratio = hwcs / lw

        if ratio <= 1.0:
            return OMEGA_V_MIN
        elif ratio >= WALL_PIER_HW_LW_LIMIT:
            return OMEGA_V_MAX
        else:
            # Interpolacion lineal entre 1.0 y 2.0
            return OMEGA_V_MIN + (OMEGA_V_MAX - OMEGA_V_MIN) * (ratio - 1.0)

    def calculate_omega_v_dyn(
        self,
        hwcs: float,
        lw: float,
        hn_ft: Optional[float] = None
    ) -> float:
        """
        Calcula el factor de amplificacion dinamica omega_v segun Tabla 18.10.3.3.3.

        Args:
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)
            hn_ft: Altura total del edificio en pies (opcional)

        Returns:
            Factor omega_v
        """
        if lw <= 0:
            return OMEGA_V_DYN_MIN

        ratio = hwcs / lw

        if ratio < WALL_PIER_HW_LW_LIMIT:
            return OMEGA_V_DYN_MIN

        # Para hwcs/lw >= 2.0
        if hn_ft is None or hn_ft <= 0:
            # Si no se conoce la altura, usar valor conservador
            return OMEGA_V_DYN_MIN

        # omega_v = 0.8 + 0.09 * hn^(1/3) >= 1.0
        omega_v_dyn = OMEGA_V_DYN_BASE + OMEGA_V_DYN_COEF * (hn_ft ** (1/3))
        return max(OMEGA_V_DYN_MIN, omega_v_dyn)

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
        Calcula el cortante de diseno amplificado Ve.

        Args:
            Vu: Cortante del analisis debido a sismo (tonf)
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)
            hn_ft: Altura total del edificio en pies (opcional)
            use_omega_0: Si usar Omega_0 en lugar de Omega_v x omega_v
            omega_0: Factor de sobrerresistencia del sistema (default 2.5)

        Returns:
            ShearAmplificationResult con el cortante amplificado
        """
        hwcs_lw = hwcs / lw if lw > 0 else 0

        if use_omega_0:
            # Alternativa S18.10.3.3.4
            omega_v = omega_0
            omega_v_dyn = 1.0
            amplification = omega_0
            aci_reference = "ACI 318-25 S18.10.3.3.4 (Omega_0)"
        else:
            omega_v = self.calculate_omega_v(hwcs, lw)
            omega_v_dyn = self.calculate_omega_v_dyn(hwcs, lw, hn_ft)
            amplification = omega_v * omega_v_dyn
            aci_reference = "ACI 318-25 S18.10.3.3, Tabla 18.10.3.3.3"

        Ve = amplification * abs(Vu)

        # La amplificacion aplica solo a muros (no a pilares de muro S18.10.8)
        applies = True

        return ShearAmplificationResult(
            Vu_original=Vu,
            Ve=Ve,
            omega_v=omega_v,
            omega_v_dyn=omega_v_dyn,
            amplification=amplification,
            hwcs_lw=hwcs_lw,
            hn_ft=hn_ft,
            applies=applies,
            aci_reference=aci_reference
        )

    def should_amplify(
        self,
        hwcs: float,
        lw: float,
        is_wall_pier: bool = False,
        is_coupling_beam: bool = False
    ) -> bool:
        """
        Determina si se debe aplicar amplificacion de cortante.

        La amplificacion NO aplica a:
        - Segmentos horizontales (vigas de acoplamiento) -> S18.10.3.1
        - Pilares de muro (wall piers) -> S18.10.3.2

        Args:
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)
            is_wall_pier: Si es un pilar de muro (hw/lw < 2.0)
            is_coupling_beam: Si es viga de acoplamiento

        Returns:
            True si debe amplificar el cortante
        """
        if is_coupling_beam:
            # S18.10.3.1: Segmentos horizontales usan S18.10.7
            return False

        if is_wall_pier:
            # S18.10.3.2: Pilares de muro usan S18.10.8
            return False

        return True

    # =========================================================================
    # Requisitos para muros especiales (S18.10.2)
    # =========================================================================

    # Constantes ACI 318-25 Seccion 18.10.2
    RHO_L_MIN_SPECIAL = 0.0025
    RHO_T_MIN_SPECIAL = 0.0025
    SPACING_MAX_MM = 457.2  # 18 in

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
        Verifica requisitos de refuerzo para muros especiales (18.10.2).

        Args:
            hw: Altura del muro (mm)
            lw: Longitud del muro (mm)
            tw: Espesor del muro (mm)
            rho_l: Cuantia longitudinal actual
            rho_t: Cuantia transversal actual
            spacing_v: Espaciamiento vertical (mm)
            spacing_h: Espaciamiento horizontal (mm)
            Vu: Cortante de demanda (tonf)
            fc: Resistencia del hormigon (MPa)
            lambda_factor: Factor lambda para hormigon liviano
            has_double_curtain: Si tiene doble cortina

        Returns:
            SpecialWallRequirements con resultado de la verificacion
        """
        warnings = []
        rho_l_min = self.RHO_L_MIN_SPECIAL
        rho_t_min = self.RHO_T_MIN_SPECIAL

        Acv = lw * tw
        # Umbral: lambda * sqrt(f'c) * Acv en N, convertido a tonf
        threshold = lambda_factor * math.sqrt(fc) * Acv / N_TO_TONF

        if Vu <= threshold:
            warnings.append(f"Vu={Vu:.1f} <= {threshold:.1f} tonf: Se permite rho_t segun 11.6")

        spacing_max = self.SPACING_MAX_MM
        if spacing_v > spacing_max:
            warnings.append(f"Espaciamiento vertical {spacing_v:.0f}mm > {spacing_max:.0f}mm maximo")
        if spacing_h > spacing_max:
            warnings.append(f"Espaciamiento horizontal {spacing_h:.0f}mm > {spacing_max:.0f}mm maximo")

        threshold_double = 2 * lambda_factor * math.sqrt(fc) * Acv / N_TO_TONF
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
            warnings.append(f"rho_l={rho_l:.4f} < {rho_l_min:.4f} minimo")
        if not rho_t_ok:
            warnings.append(f"rho_t={rho_t:.4f} < {rho_t_min:.4f} minimo")

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
        """
        Determina la categoria del muro basado en SDC.

        Args:
            sdc: Categoria de Diseno Sismico
            is_sfrs: Si es parte del sistema resistente a fuerzas sismicas
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
