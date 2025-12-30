# app/structural/domain/reinforcement_limits.py
"""
Verificacion de limites de refuerzo para muros segun ACI 318-25 Capitulo 11.

Implementa:
- 11.6.1: Refuerzo minimo para cortante bajo
- 11.6.2: Refuerzo minimo para cortante alto
- Verificacion de cuantias segun tipo de muro y barra

Referencias ACI 318-25:
- Tabla 11.6.1: Cuantia minima para cortante en plano bajo
- Ec. 11.6.2: Cuantia longitudinal para cortante alto
"""
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from enum import Enum
import math

from .constants.materials import SteelGrade

if TYPE_CHECKING:
    from .entities.pier import Pier


class BarSize(Enum):
    """Clasificacion de tamano de barra."""
    SMALL = "small"       # <= No.5 (16mm)
    LARGE = "large"       # > No.5 (16mm)


# SteelGrade importado desde constants.materials


@dataclass
class MinReinforcementResult:
    """Resultado de verificacion de refuerzo minimo."""
    rho_l_min: float         # Cuantia longitudinal minima requerida
    rho_t_min: float         # Cuantia transversal minima requerida
    rho_l_actual: float      # Cuantia longitudinal actual
    rho_t_actual: float      # Cuantia transversal actual
    rho_l_ok: bool           # Cumple cuantia longitudinal
    rho_t_ok: bool           # Cumple cuantia transversal
    is_ok: bool              # Cumple ambas
    is_high_shear: bool      # Aplica criterio de cortante alto
    aci_reference: str       # Referencia ACI
    notes: str               # Notas adicionales


@dataclass
class ShearReinforcementResult:
    """Resultado de verificacion especifica para cortante."""
    rho_v_min: float         # Cuantia vertical minima (rho_l)
    rho_h_min: float         # Cuantia horizontal minima (rho_t)
    rho_v_required: float    # Cuantia vertical requerida por Ec. 11.6.2
    hw_lw: float             # Relacion altura/longitud
    rho_v_ok: bool           # Cumple cuantia vertical
    rho_h_ok: bool           # Cumple cuantia horizontal
    rho_v_ge_rho_h: bool     # Cumple rho_v >= rho_h (si aplica)
    is_ok: bool              # Cumple todos los requisitos
    aci_reference: str       # Referencia ACI


class ReinforcementLimitsService:
    """
    Servicio para verificacion de limites de refuerzo segun ACI 318-25.

    Unidades:
    - Diametros: mm
    - Esfuerzos: MPa
    - Cuantias: adimensional
    """

    # =========================================================================
    # CONSTANTES ACI 318-25 TABLA 11.6.1
    # =========================================================================

    # Cuantias minimas para cortante bajo - Colado en sitio
    # Barras <= No.5 (16mm) con fy >= 60ksi (420 MPa)
    RHO_L_MIN_SMALL_HIGH_FY = 0.0012
    RHO_T_MIN_SMALL_HIGH_FY = 0.0020

    # Barras <= No.5 (16mm) con fy < 60ksi
    RHO_L_MIN_SMALL_LOW_FY = 0.0015
    RHO_T_MIN_SMALL_LOW_FY = 0.0025

    # Barras > No.5 (cualquier fy)
    RHO_L_MIN_LARGE = 0.0015
    RHO_T_MIN_LARGE = 0.0025

    # Malla electrosoldada <= W31/D31 (cualquier fy)
    RHO_L_MIN_WWR = 0.0012
    RHO_T_MIN_WWR = 0.0020

    # Prefabricados (cualquier refuerzo)
    RHO_L_MIN_PRECAST = 0.0010
    RHO_T_MIN_PRECAST = 0.0010

    # Cuantias minimas para cortante alto (11.6.2)
    RHO_MIN_HIGH_SHEAR = 0.0025

    # Limite de diametro para clasificacion (No.5 = 16mm = 5/8")
    BAR_SIZE_LIMIT_MM = 16

    # Limite de fluencia para clasificacion (60 ksi = 420 MPa)
    FY_HIGH_LIMIT_MPA = 420

    # =========================================================================
    # CLASIFICACION DE REFUERZO
    # =========================================================================

    def classify_bar_size(self, diameter_mm: int) -> BarSize:
        """Clasifica el tamano de barra segun ACI."""
        if diameter_mm <= self.BAR_SIZE_LIMIT_MM:
            return BarSize.SMALL
        return BarSize.LARGE

    def classify_steel_grade(self, fy_mpa: float) -> SteelGrade:
        """
        Clasifica el grado de acero segun fluencia.

        Retorna el grado mas cercano basado en fy:
        - fy >= 690 MPa: GRADE_100
        - fy >= 550 MPa: GRADE_80
        - fy >= 420 MPa: GRADE_60
        - else: GRADE_40
        """
        if fy_mpa >= 690:
            return SteelGrade.GRADE_100
        elif fy_mpa >= 550:
            return SteelGrade.GRADE_80
        elif fy_mpa >= self.FY_HIGH_LIMIT_MPA:  # 420 MPa
            return SteelGrade.GRADE_60
        return SteelGrade.GRADE_40

    def is_high_strength_steel(self, fy_mpa: float) -> bool:
        """Verifica si el acero es de alta resistencia (fy >= 420 MPa)."""
        return fy_mpa >= self.FY_HIGH_LIMIT_MPA

    # =========================================================================
    # CUANTIAS MINIMAS PARA CORTANTE BAJO (11.6.1)
    # =========================================================================

    def get_min_reinforcement_low_shear(
        self,
        diameter_v_mm: int,
        diameter_h_mm: int,
        fy_mpa: float,
        is_precast: bool = False,
        is_welded_wire: bool = False
    ) -> tuple:
        """
        Obtiene cuantias minimas para cortante bajo segun Tabla 11.6.1.

        Args:
            diameter_v_mm: Diametro barra vertical (mm)
            diameter_h_mm: Diametro barra horizontal (mm)
            fy_mpa: Fluencia del acero (MPa)
            is_precast: Muro prefabricado
            is_welded_wire: Malla electrosoldada

        Returns:
            Tuple (rho_l_min, rho_t_min)
        """
        if is_precast:
            return (self.RHO_L_MIN_PRECAST, self.RHO_T_MIN_PRECAST)

        if is_welded_wire:
            return (self.RHO_L_MIN_WWR, self.RHO_T_MIN_WWR)

        bar_size_v = self.classify_bar_size(diameter_v_mm)
        bar_size_h = self.classify_bar_size(diameter_h_mm)
        steel_grade = self.classify_steel_grade(fy_mpa)

        # Longitudinal (vertical) - segun barra vertical
        # "High fy" significa fy >= 420 MPa (GRADE_60 o superior)
        is_high_fy = steel_grade.value >= 60

        if bar_size_v == BarSize.LARGE:
            rho_l_min = self.RHO_L_MIN_LARGE
        elif is_high_fy:
            rho_l_min = self.RHO_L_MIN_SMALL_HIGH_FY
        else:
            rho_l_min = self.RHO_L_MIN_SMALL_LOW_FY

        # Transversal (horizontal) - segun barra horizontal
        if bar_size_h == BarSize.LARGE:
            rho_t_min = self.RHO_T_MIN_LARGE
        elif is_high_fy:
            rho_t_min = self.RHO_T_MIN_SMALL_HIGH_FY
        else:
            rho_t_min = self.RHO_T_MIN_SMALL_LOW_FY

        return (rho_l_min, rho_t_min)

    # =========================================================================
    # CUANTIAS MINIMAS PARA CORTANTE ALTO (11.6.2)
    # =========================================================================

    def get_min_reinforcement_high_shear(
        self,
        hw: float,
        lw: float,
        rho_t: float
    ) -> tuple:
        """
        Calcula cuantias minimas para cortante alto segun 11.6.2.

        rho_l >= 0.0025 + 0.5*(2.5 - hw/lw)*(rho_t - 0.0025)
        rho_l minimo = 0.0025
        rho_t minimo = 0.0025

        Args:
            hw: Altura del muro (mm)
            lw: Longitud del muro (mm)
            rho_t: Cuantia transversal actual

        Returns:
            Tuple (rho_l_min, rho_t_min, rho_l_required_by_formula)
        """
        if lw <= 0:
            return (self.RHO_MIN_HIGH_SHEAR, self.RHO_MIN_HIGH_SHEAR, self.RHO_MIN_HIGH_SHEAR)

        hw_lw = hw / lw

        # Ecuacion 11.6.2
        rho_l_calc = self.RHO_MIN_HIGH_SHEAR + 0.5 * (2.5 - hw_lw) * (rho_t - self.RHO_MIN_HIGH_SHEAR)

        # Limites
        rho_l_min = max(rho_l_calc, self.RHO_MIN_HIGH_SHEAR)

        # No necesita exceder rho_t requerido por resistencia
        # Pero siempre al menos 0.0025
        rho_t_min = self.RHO_MIN_HIGH_SHEAR

        return (rho_l_min, rho_t_min, rho_l_calc)

    # =========================================================================
    # VERIFICACION DE REFUERZO MINIMO
    # =========================================================================

    def check_minimum_reinforcement(
        self,
        rho_l: float,
        rho_t: float,
        diameter_v_mm: int,
        diameter_h_mm: int,
        fy_mpa: float,
        hw: float,
        lw: float,
        Vu: float = 0,
        phi_alpha_c_lambda_sqrt_fc_Acv: float = 0,
        is_precast: bool = False
    ) -> MinReinforcementResult:
        """
        Verifica refuerzo minimo segun condicion de cortante.

        Condicion para cortante bajo (11.6.1):
        Vu <= 0.5 * phi * alpha_c * lambda * sqrt(f'c) * Acv

        Condicion para cortante alto (11.6.2):
        Vu > 0.5 * phi * alpha_c * lambda * sqrt(f'c) * Acv

        Args:
            rho_l: Cuantia longitudinal actual
            rho_t: Cuantia transversal actual
            diameter_v_mm: Diametro barra vertical (mm)
            diameter_h_mm: Diametro barra horizontal (mm)
            fy_mpa: Fluencia del acero (MPa)
            hw: Altura del muro (mm)
            lw: Longitud del muro (mm)
            Vu: Demanda de cortante (tonf)
            phi_alpha_c_lambda_sqrt_fc_Acv: 0.5 * phi * alpha_c * lambda * sqrt(f'c) * Acv
            is_precast: Muro prefabricado

        Returns:
            MinReinforcementResult con resultado de la verificacion
        """
        # Determinar si es cortante alto o bajo
        threshold = phi_alpha_c_lambda_sqrt_fc_Acv
        is_high_shear = Vu > threshold if threshold > 0 else False

        if is_high_shear:
            # Cortante alto - usar 11.6.2
            rho_l_min, rho_t_min, rho_l_calc = self.get_min_reinforcement_high_shear(
                hw, lw, rho_t
            )
            aci_ref = "ACI 318-25 11.6.2"
            notes = f"Cortante alto: Vu={Vu:.1f} > 0.5*phi*Vc={threshold:.1f} tonf"
        else:
            # Cortante bajo - usar Tabla 11.6.1
            rho_l_min, rho_t_min = self.get_min_reinforcement_low_shear(
                diameter_v_mm, diameter_h_mm, fy_mpa, is_precast
            )
            aci_ref = "ACI 318-25 Tabla 11.6.1"
            notes = f"Cortante bajo: Vu={Vu:.1f} <= 0.5*phi*Vc={threshold:.1f} tonf"

        rho_l_ok = rho_l >= rho_l_min
        rho_t_ok = rho_t >= rho_t_min

        return MinReinforcementResult(
            rho_l_min=rho_l_min,
            rho_t_min=rho_t_min,
            rho_l_actual=rho_l,
            rho_t_actual=rho_t,
            rho_l_ok=rho_l_ok,
            rho_t_ok=rho_t_ok,
            is_ok=rho_l_ok and rho_t_ok,
            is_high_shear=is_high_shear,
            aci_reference=aci_ref,
            notes=notes
        )

    # =========================================================================
    # VERIFICACION PARA CORTANTE EN EL PLANO
    # =========================================================================

    def check_shear_reinforcement(
        self,
        rho_v: float,
        rho_h: float,
        hw: float,
        lw: float
    ) -> ShearReinforcementResult:
        """
        Verifica refuerzo para cortante en el plano segun 11.6.2.

        Requisitos adicionales:
        - Si hw/lw <= 2.0, entonces rho_v >= rho_h

        Args:
            rho_v: Cuantia vertical actual
            rho_h: Cuantia horizontal actual
            hw: Altura del muro (mm)
            lw: Longitud del muro (mm)

        Returns:
            ShearReinforcementResult con resultado de la verificacion
        """
        hw_lw = hw / lw if lw > 0 else 0

        # Cuantias minimas
        rho_v_min = self.RHO_MIN_HIGH_SHEAR
        rho_h_min = self.RHO_MIN_HIGH_SHEAR

        # Cuantia vertical requerida por Ec. 11.6.2
        rho_v_calc = self.RHO_MIN_HIGH_SHEAR + 0.5 * (2.5 - hw_lw) * (rho_h - self.RHO_MIN_HIGH_SHEAR)
        rho_v_required = max(rho_v_calc, self.RHO_MIN_HIGH_SHEAR)

        # Verificaciones
        rho_v_ok = rho_v >= rho_v_required
        rho_h_ok = rho_h >= rho_h_min

        # Requisito adicional: si hw/lw <= 2.0, rho_v >= rho_h
        if hw_lw <= 2.0:
            rho_v_ge_rho_h = rho_v >= rho_h
        else:
            rho_v_ge_rho_h = True  # No aplica

        is_ok = rho_v_ok and rho_h_ok and rho_v_ge_rho_h

        return ShearReinforcementResult(
            rho_v_min=rho_v_min,
            rho_h_min=rho_h_min,
            rho_v_required=rho_v_required,
            hw_lw=hw_lw,
            rho_v_ok=rho_v_ok,
            rho_h_ok=rho_h_ok,
            rho_v_ge_rho_h=rho_v_ge_rho_h,
            is_ok=is_ok,
            aci_reference="ACI 318-25 11.6.2, 18.10.4.3"
        )

    # =========================================================================
    # VERIFICACION DESDE PIER
    # =========================================================================

    def check_from_pier(
        self,
        pier: 'Pier',
        Vu: float = 0,
        phi_Vc: float = 0,
        alpha_c: float = 0.25,
        is_precast: bool = False
    ) -> MinReinforcementResult:
        """
        Verificacion simplificada desde un Pier.

        Args:
            pier: Entidad Pier con geometria y armadura
            Vu: Demanda de corte (tonf)
            phi_Vc: Capacidad de corte del concreto phi*Vc (tonf)
            alpha_c: Coeficiente alpha_c para calculo de umbral
            is_precast: Muro prefabricado

        Returns:
            MinReinforcementResult con resultado de la verificacion
        """
        # Calcular umbral para cortante bajo/alto
        # 0.5 * phi * Vc (ya que phi_Vc = phi * alpha_c * lambda * sqrt(fc) * Acv)
        threshold = 0.5 * phi_Vc if phi_Vc > 0 else 0

        return self.check_minimum_reinforcement(
            rho_l=pier.rho_vertical,
            rho_t=pier.rho_horizontal,
            diameter_v_mm=pier.diameter_v,
            diameter_h_mm=pier.diameter_h,
            fy_mpa=pier.fy,
            hw=pier.height,
            lw=pier.width,
            Vu=Vu,
            phi_alpha_c_lambda_sqrt_fc_Acv=threshold,
            is_precast=is_precast
        )
