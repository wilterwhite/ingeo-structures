# app/domain/chapter18/columns/shear.py
"""
Verificación de cortante para columnas sísmicas ACI 318-25 §18.7.6.

Incluye:
- Diseño por capacidad: Ve = (Mpr_top + Mpr_bottom) / lu
- Condición Vc = 0: cuando Ve >= 0.5*Vu y Pu < Ag*f'c/20
- Cálculo de capacidad Vc + Vs

Referencias:
- §18.7.6.1: Diseño por capacidad (Ve basado en Mpr)
- §18.7.6.2.1: Condiciones para Vc = 0
- §22.5.5.1: Vc = 0.17 * lambda * sqrt(f'c) * bw * d
- §22.5.10.5.3: Vs = Av * fyt * d / s
"""
import math
from typing import Optional

from ...constants import DCR_MAX_FINITE
from ...constants.materials import LAMBDA_NORMAL
from ...constants.shear import PHI_SHEAR_SEISMIC
from ...constants.units import N_TO_TONF
from ...shear.concrete_shear import calculate_Vc_beam, check_Vc_zero_condition
from ...shear.steel_shear import calculate_Vs_beam_column
from .results import SeismicColumnShearResult, ColumnShearCapacity


class SeismicColumnShearService:
    """
    Servicio para verificación de cortante de columnas sísmicas.

    Implementa ACI 318-25 §18.7.6:
    - §18.7.6.1: Ve por diseño por capacidad
    - §18.7.6.2.1: Condiciones para Vc = 0

    Unidades:
    - Longitudes: mm
    - Esfuerzos: MPa
    - Fuerzas: tonf (entrada/salida), N (cálculos internos)
    - Momentos: tonf-m
    """

    def calculate_design_shear(
        self,
        Mpr_top: float,
        Mpr_bottom: float,
        lu: float
    ) -> float:
        """
        Calcula el cortante de diseño Ve por capacidad según §18.7.6.1.

        Ve = (Mpr_top + Mpr_bottom) / lu

        Args:
            Mpr_top: Momento probable en nudo superior (tonf-m)
            Mpr_bottom: Momento probable en nudo inferior (tonf-m)
            lu: Altura libre de la columna (mm)

        Returns:
            Ve en tonf
        """
        if lu <= 0:
            return 0
        # Mpr en tonf-m, lu en mm -> Ve en tonf
        Ve = (Mpr_top + Mpr_bottom) * 1000 / lu
        return Ve

    def calculate_shear_capacity(
        self,
        bw: float,
        d: float,
        fc: float,
        Av: float,
        fyt: float,
        s: float,
        lambda_factor: float = LAMBDA_NORMAL,
        Vc_is_zero: bool = False
    ) -> ColumnShearCapacity:
        """
        Calcula la capacidad de cortante de la columna.

        Delega a funciones centralizadas en domain/shear/:
        - calculate_Vc_beam() para Vc conservador (sin incremento por axial)
        - calculate_Vs_beam_column() para Vs

        NOTA: Esta fórmula de Vc NO incluye el incremento por carga axial
        (1 + Nu/14Ag) de §22.5.6.1. Esto es conservador porque:
        1. La carga axial varía entre combinaciones
        2. Para columnas sísmicas, §18.7.6.2.1 puede hacer Vc = 0

        Args:
            bw: Ancho del alma (mm)
            d: Profundidad efectiva (mm)
            fc: f'c del concreto (MPa)
            Av: Área de refuerzo transversal (mm²)
            fyt: Fluencia del refuerzo transversal (MPa)
            s: Espaciamiento de estribos (mm)
            lambda_factor: Factor para concreto liviano
            Vc_is_zero: Si True, Vc = 0 por §18.7.6.2.1

        Returns:
            ColumnShearCapacity con Vc, Vs, Vn, phi_Vn en tonf
        """
        # Usar funciones centralizadas de domain/shear/
        vc_result = calculate_Vc_beam(bw, d, fc, lambda_factor, force_Vc_zero=Vc_is_zero)
        vs_result = calculate_Vs_beam_column(Av, d, s, fyt, bw, fc)

        Vc = vc_result.Vc_N
        Vs = vs_result.Vs_N

        # Vn y phi_Vn
        # φ = 0.60 para columnas sísmicas especiales (§21.2.4.1)
        Vn = Vc + Vs
        phi_Vn = PHI_SHEAR_SEISMIC * Vn

        return ColumnShearCapacity(
            Vc=Vc / N_TO_TONF,
            Vs=Vs / N_TO_TONF,
            Vn=Vn / N_TO_TONF,
            phi_Vn=phi_Vn / N_TO_TONF
        )

    def verify_seismic_column_shear(
        self,
        lu: float,
        Ag: float,
        fc: float,
        bw_V2: float,
        d_V2: float,
        Av_V2: float,
        bw_V3: float,
        d_V3: float,
        Av_V3: float,
        fyt: float,
        s: float,
        Vu_V2: float,
        Vu_V3: float,
        Pu: float,
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        lambda_factor: float = LAMBDA_NORMAL
    ) -> SeismicColumnShearResult:
        """
        Verifica cortante de columna sísmica según ACI 318-25 §18.7.6.

        Args:
            lu: Altura libre (mm)
            Ag: Área bruta (mm²)
            fc: f'c del concreto (MPa)
            bw_V2, d_V2, Av_V2: Geometría para cortante V2
            bw_V3, d_V3, Av_V3: Geometría para cortante V3
            fyt: Fluencia del refuerzo transversal (MPa)
            s: Espaciamiento de estribos (mm)
            Vu_V2: Cortante último en dirección V2 (tonf)
            Vu_V3: Cortante último en dirección V3 (tonf)
            Pu: Carga axial (tonf, positivo = compresión)
            Mpr_top: Momento probable superior (tonf-m)
            Mpr_bottom: Momento probable inferior (tonf-m)
            lambda_factor: Factor para concreto liviano

        Returns:
            SeismicColumnShearResult con verificación completa
        """
        # Calcular Ve si hay momentos probables
        Ve = 0
        uses_capacity_design = False
        if Mpr_top > 0 or Mpr_bottom > 0:
            Ve = self.calculate_design_shear(Mpr_top, Mpr_bottom, lu)
            uses_capacity_design = True

        # Determinar cortante de diseño
        Vu_max = max(Vu_V2, Vu_V3)
        if uses_capacity_design:
            Vu_V2_design = max(Vu_V2, Ve) if Vu_V2 > 0 else Ve
            Vu_V3_design = max(Vu_V3, Ve) if Vu_V3 > 0 else Ve
        else:
            Vu_V2_design = Vu_V2
            Vu_V3_design = Vu_V3

        # Verificar condición Vc = 0
        Vc_is_zero = False
        if uses_capacity_design:
            Vc_is_zero = check_Vc_zero_condition(Ve, Vu_max, Pu, Ag, fc)

        # Calcular capacidades
        cap_V2 = self.calculate_shear_capacity(
            bw_V2, d_V2, fc, Av_V2, fyt, s, lambda_factor, Vc_is_zero
        )
        cap_V3 = self.calculate_shear_capacity(
            bw_V3, d_V3, fc, Av_V3, fyt, s, lambda_factor, Vc_is_zero
        )

        # Calcular DCR
        dcr_V2 = Vu_V2_design / cap_V2.phi_Vn if cap_V2.phi_Vn > 0 else DCR_MAX_FINITE
        dcr_V3 = Vu_V3_design / cap_V3.phi_Vn if cap_V3.phi_Vn > 0 else DCR_MAX_FINITE
        dcr = math.sqrt(dcr_V2**2 + dcr_V3**2)

        return SeismicColumnShearResult(
            dcr=round(dcr, 3),
            is_ok=dcr <= 1.0,
            critical_combo="",  # Se llena en el servicio de aplicación
            Vu_V2=round(Vu_V2_design, 2),
            Vu_V3=round(Vu_V3_design, 2),
            phi_Vn_V2=round(cap_V2.phi_Vn, 2),
            phi_Vn_V3=round(cap_V3.phi_Vn, 2),
            capacity_V2=cap_V2,
            capacity_V3=cap_V3,
            Ve=round(Ve, 2),
            uses_capacity_design=uses_capacity_design,
            Vc_is_zero=Vc_is_zero,
            Pu_critical=round(Pu, 2),
            aci_reference="ACI 318-25 §18.7.6"
        )
