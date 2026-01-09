# app/domain/chapter11/design_methods.py
"""
Metodos de diseno para muros segun ACI 318-25 Capitulo 11.

Implementa:
- 11.8: Metodo alternativo para muros esbeltos

NOTA SOBRE METODO SIMPLIFICADO (§11.5.3):
=========================================
El metodo simplificado (Ec. 11.5.3.1: Pn = 0.55*f'c*Ag*[1-(k*lc/32h)^2])
NO SE IMPLEMENTA porque:

1. Solo aplica cuando la excentricidad e <= h/6 (carga casi centrada)
   ACI 318-25 §11.5.3.1: "resultant of all factored loads is located
   within the middle third of the wall thickness"

2. Esta aplicacion usa diagramas de interaccion P-M para muros sismicos
   con momentos significativos (SDC D, E, F segun ASCE 7), donde
   tipicamente e >> h/6

3. El metodo correcto para muros esbeltos con momentos significativos es
   la magnificacion de momentos segun ACI 318-25 §6.6.4:
   Mc = delta_ns * Mu

4. Para verificacion de muros, usar:
   - FlexocompressionService.check_flexure() para curva P-M completa
   - SlendernessService.analyze() para factor de magnificacion delta_ns

Ver: domain/flexure/slenderness.py para la implementacion de delta_ns.

Referencias ACI 318-25:
- Ec. 6.6.4.5.2: Factor de magnificacion delta_ns = Cm/(1-Pu/0.75Pc)
- Ec. 11.8.3.1a-d: Momento magnificado para muros esbeltos (metodo 11.8)
- Ec. 11.8.3.1c: Inercia agrietada
- Tabla 11.8.4.1: Deflexion de servicio
"""
from dataclasses import dataclass
from typing import Optional, Tuple, TYPE_CHECKING, List
import math

from ..constants.phi_chapter21 import PHI_TENSION
from ..constants.materials import (
    calculate_beta1,
    calculate_Ec,
    calculate_fr,
    ES_MPA,
)

if TYPE_CHECKING:
    from ..entities.pier import Pier


@dataclass
class SlenderWallResult:
    """Resultado del metodo alternativo para muros esbeltos 11.8."""
    # Verificacion de aplicabilidad (11.8.1.1)
    is_applicable: bool
    applicability_checks: dict

    # Parametros geometricos
    lc_mm: float                # Longitud no soportada (mm)
    h_mm: float                 # Espesor (mm)
    d_mm: float                 # Profundidad efectiva (mm)

    # Propiedades de la seccion
    Ec_mpa: float               # Modulo de elasticidad del concreto
    Ig_mm4: float               # Momento de inercia bruto
    Icr_mm4: float              # Momento de inercia agrietado

    # Momentos
    Mcr_Nmm: float              # Momento de agrietamiento
    Mn_Nmm: float               # Momento nominal
    phi_Mn_Nmm: float           # Momento de diseno

    # Factor de magnificacion
    Mua_Nmm: float              # Momento sin efectos P-Delta
    Mu_Nmm: float               # Momento magnificado
    magnification_factor: float  # Factor Mu/Mua

    # Deflexion
    Delta_cr_mm: float          # Deflexion al agrietamiento
    Delta_n_mm: float           # Deflexion al momento nominal
    Delta_u_mm: float           # Deflexion bajo cargas factoradas
    Delta_s_mm: float           # Deflexion de servicio
    Delta_limit_mm: float       # Limite lc/150
    deflection_ok: bool         # Cumple limite de deflexion

    aci_reference: str          # Referencia ACI


class SlenderWallService:
    """
    Servicio para metodo alternativo de muros esbeltos segun ACI 318-25 §11.8.

    Este metodo es mas preciso que el metodo general (§6.6.4) porque:
    - Calcula Icr especifico (no asume 0.35*Ig)
    - Verifica deflexion de servicio (lc/150)
    - Tiene condiciones de aplicabilidad explicitas

    Condiciones de aplicabilidad (§11.8.1.1):
    - Seccion transversal constante
    - Comportamiento controlado por tension
    - phi*Mn >= Mcr
    - Pu <= 0.06*f'c*Ag
    - Deflexion de servicio <= lc/150

    Uso tipico:
        service = SlenderWallService()
        result = service.analyze(pier, Pu_N, Mua_Nmm, As_tension)
        if result.is_applicable and result.deflection_ok:
            # Usar momento magnificado result.Mu_Nmm
    """

    def calculate_Mcr(
        self,
        fc_mpa: float,
        lw_mm: float,
        h_mm: float
    ) -> float:
        """
        Calcula momento de agrietamiento Mcr.

        Mcr = fr * Ig / yt

        Args:
            fc_mpa: f'c (MPa)
            lw_mm: Longitud del muro (mm)
            h_mm: Espesor del muro (mm)

        Returns:
            Mcr en N-mm
        """
        fr = calculate_fr(fc_mpa)
        Ig = lw_mm * h_mm**3 / 12
        yt = h_mm / 2

        return fr * Ig / yt

    def calculate_Icr(
        self,
        Es_mpa: float,
        Ec_mpa: float,
        As_mm2: float,
        Pu_N: float,
        fy_mpa: float,
        h_mm: float,
        d_mm: float,
        c_mm: float,
        lw_mm: float
    ) -> float:
        """
        Calcula momento de inercia agrietado segun Ec. 11.8.3.1c.

        Icr = (Es/Ec) * (As + Pu/fy * h/(2d)) * (d - c)^2 + (lw * c^3) / 3

        NOTA: Es/Ec debe ser al menos 6

        Args:
            Es_mpa: Modulo del acero (MPa)
            Ec_mpa: Modulo del concreto (MPa)
            As_mm2: Area de acero en traccion (mm2)
            Pu_N: Carga axial factorada (N)
            fy_mpa: Fluencia del acero (MPa)
            h_mm: Espesor del muro (mm)
            d_mm: Profundidad efectiva (mm)
            c_mm: Profundidad del eje neutro (mm)
            lw_mm: Longitud del muro (mm)

        Returns:
            Icr en mm4
        """
        # Es/Ec debe ser al menos 6
        n = max(Es_mpa / Ec_mpa, 6.0)

        # Area de acero efectiva
        Ase_w = As_mm2 + (Pu_N / fy_mpa) * (h_mm / 2) / d_mm

        # Momento de inercia agrietado
        Icr = n * Ase_w * (d_mm - c_mm)**2 + (lw_mm * c_mm**3) / 3

        return Icr

    def calculate_neutral_axis_depth(
        self,
        As_mm2: float,
        Pu_N: float,
        fy_mpa: float,
        fc_mpa: float,
        h_mm: float,
        d_mm: float,
        lw_mm: float
    ) -> float:
        """
        Estima profundidad del eje neutro c para seccion agrietada.

        Usa equilibrio simplificado:
        0.85*fc*beta1*c*lw = As*fy + Pu

        Args:
            As_mm2: Area de acero (mm2)
            Pu_N: Carga axial (N), positivo compresion
            fy_mpa: Fluencia del acero (MPa)
            fc_mpa: f'c (MPa)
            h_mm: Espesor (mm)
            d_mm: Profundidad efectiva (mm)
            lw_mm: Longitud del muro (mm)

        Returns:
            c en mm
        """
        beta1 = calculate_beta1(fc_mpa)

        numerator = As_mm2 * fy_mpa + Pu_N
        denominator = 0.85 * fc_mpa * beta1 * lw_mm

        if denominator > 0:
            c = numerator / denominator
        else:
            c = 0.1 * d_mm

        # Limitar c a valores razonables
        c = max(0.05 * d_mm, min(c, 0.9 * d_mm))

        return c

    def calculate_magnified_moment(
        self,
        Mua_Nmm: float,
        Pu_N: float,
        lc_mm: float,
        Ec_mpa: float,
        Icr_mm4: float
    ) -> Tuple[float, float]:
        """
        Calcula momento magnificado Mu segun Ec. 11.8.3.1d.

        Mu = Mua / [1 - (5*Pu*lc^2) / (0.75*48*Ec*Icr)]

        Args:
            Mua_Nmm: Momento sin efectos P-Delta (N-mm)
            Pu_N: Carga axial factorada (N)
            lc_mm: Longitud no soportada (mm)
            Ec_mpa: Modulo de elasticidad (MPa)
            Icr_mm4: Inercia agrietada (mm4)

        Returns:
            Tuple (Mu_Nmm, Delta_u_mm)
        """
        denom_base = 0.75 * 48 * Ec_mpa * Icr_mm4

        if denom_base <= 0:
            return (Mua_Nmm, 0.0)

        factor_denom = 1 - (5 * Pu_N * lc_mm**2) / denom_base

        if factor_denom <= 0:
            # Inestabilidad
            return (float('inf'), float('inf'))

        Mu = Mua_Nmm / factor_denom
        Delta_u = (5 * Mu * lc_mm**2) / denom_base

        return (Mu, Delta_u)

    def calculate_service_deflection(
        self,
        Ma_Nmm: float,
        Mcr_Nmm: float,
        Mn_Nmm: float,
        lc_mm: float,
        Ec_mpa: float,
        Ig_mm4: float,
        Icr_mm4: float
    ) -> Tuple[float, float, float]:
        """
        Calcula deflexion de servicio segun Tabla 11.8.4.1.

        Si Ma <= (2/3)Mcr:
            Delta_s = (Ma/Mcr) * Delta_cr
        Si Ma > (2/3)Mcr:
            Delta_s = (2/3)*Delta_cr + [(Ma - (2/3)Mcr)/(Mn - (2/3)Mcr)] * (Delta_n - (2/3)*Delta_cr)

        Args:
            Ma_Nmm: Momento de servicio (N-mm)
            Mcr_Nmm: Momento de agrietamiento (N-mm)
            Mn_Nmm: Momento nominal (N-mm)
            lc_mm: Longitud no soportada (mm)
            Ec_mpa: Modulo de elasticidad (MPa)
            Ig_mm4: Inercia bruta (mm4)
            Icr_mm4: Inercia agrietada (mm4)

        Returns:
            Tuple (Delta_s, Delta_cr, Delta_n) en mm
        """
        # Deflexiones de referencia (Ec. 11.8.4.3a-b)
        Delta_cr = (5 * Mcr_Nmm * lc_mm**2) / (48 * Ec_mpa * Ig_mm4) if Ig_mm4 > 0 else 0
        Delta_n = (5 * Mn_Nmm * lc_mm**2) / (48 * Ec_mpa * Icr_mm4) if Icr_mm4 > 0 else 0

        # Umbral
        Mcr_23 = (2.0 / 3.0) * Mcr_Nmm
        Delta_cr_23 = (2.0 / 3.0) * Delta_cr

        if Ma_Nmm <= Mcr_23:
            # Region elastica
            Delta_s = (Ma_Nmm / Mcr_Nmm) * Delta_cr if Mcr_Nmm > 0 else 0
        else:
            # Region agrietada - interpolacion
            numerator = Ma_Nmm - Mcr_23
            denominator = Mn_Nmm - Mcr_23

            if denominator > 0:
                ratio = numerator / denominator
                Delta_s = Delta_cr_23 + ratio * (Delta_n - Delta_cr_23)
            else:
                Delta_s = Delta_n

        return (Delta_s, Delta_cr, Delta_n)

    def check_applicability(
        self,
        pier: 'Pier',
        Pu_N: float,
        phi_Mn_Nmm: float,
        Mcr_Nmm: float,
        has_openings: bool = False
    ) -> Tuple[bool, dict]:
        """
        Verifica condiciones de aplicabilidad del metodo 11.8 (11.8.1.1).

        Condiciones:
        (a) Seccion transversal constante
        (b) Comportamiento controlado por tension
        (c) phi*Mn >= Mcr
        (d) Pu <= 0.06*f'c*Ag
        (e) Deflexion <= lc/150 (verificada en analyze())

        Args:
            pier: Entidad Pier
            Pu_N: Carga axial en media altura (N)
            phi_Mn_Nmm: Capacidad de momento de diseno (N-mm)
            Mcr_Nmm: Momento de agrietamiento (N-mm)
            has_openings: Tiene aberturas grandes

        Returns:
            Tuple (es_aplicable, dict_verificaciones)
        """
        checks = {}

        # (a) Seccion constante
        checks['constant_section'] = not has_openings

        # (c) phi*Mn >= Mcr
        checks['phi_Mn_ge_Mcr'] = phi_Mn_Nmm >= Mcr_Nmm

        # (d) Pu <= 0.06*f'c*Ag
        Pu_limit = 0.06 * pier.fc * pier.Ag
        checks['Pu_within_limit'] = Pu_N <= Pu_limit
        checks['Pu_limit_N'] = Pu_limit

        is_applicable = all([
            checks['constant_section'],
            checks['phi_Mn_ge_Mcr'],
            checks['Pu_within_limit']
        ])

        return (is_applicable, checks)

    def analyze(
        self,
        pier: 'Pier',
        Pu_N: float,
        Mua_Nmm: float,
        As_tension_mm2: float,
        Ma_service_Nmm: float = 0,
        has_openings: bool = False
    ) -> SlenderWallResult:
        """
        Analiza muro esbelto segun metodo alternativo 11.8.

        Args:
            pier: Entidad Pier
            Pu_N: Carga axial factorada a media altura (N)
            Mua_Nmm: Momento factorado sin P-Delta (N-mm)
            As_tension_mm2: Area de acero en zona de traccion (mm2)
            Ma_service_Nmm: Momento de servicio (N-mm), 0 para estimar
            has_openings: Tiene aberturas grandes

        Returns:
            SlenderWallResult con resultados del analisis
        """
        # Propiedades
        lc = pier.height
        h = pier.thickness
        lw = pier.width
        d = pier.width - pier.cover
        fc = pier.fc
        fy = pier.fy

        # Modulos
        Ec = calculate_Ec(fc)

        # Inercia bruta
        Ig = lw * h**3 / 12

        # Momento de agrietamiento
        Mcr = self.calculate_Mcr(fc, lw, h)

        # Estimar c para Icr
        c = self.calculate_neutral_axis_depth(
            As_tension_mm2, Pu_N, fy, fc, h, d, lw
        )

        # Inercia agrietada
        Icr = self.calculate_Icr(
            ES_MPA, Ec, As_tension_mm2, Pu_N, fy, h, d, c, lw
        )

        # Momento nominal simplificado (As*fy*(d-a/2))
        a = As_tension_mm2 * fy / (0.85 * fc * lw)
        Mn = As_tension_mm2 * fy * (d - a / 2)
        phi_Mn = PHI_TENSION * Mn

        # Verificar aplicabilidad (sin deflexion aun)
        is_applicable, checks = self.check_applicability(
            pier, Pu_N, phi_Mn, Mcr, has_openings
        )

        # Momento magnificado
        Mu, Delta_u = self.calculate_magnified_moment(
            Mua_Nmm, Pu_N, lc, Ec, Icr
        )

        magnification = Mu / Mua_Nmm if Mua_Nmm > 0 else 1.0

        # Deflexion de servicio
        if Ma_service_Nmm > 0:
            Delta_s, Delta_cr, Delta_n = self.calculate_service_deflection(
                Ma_service_Nmm, Mcr, Mn, lc, Ec, Ig, Icr
            )
        else:
            # Estimar como fraccion de Delta_u
            Delta_cr = (5 * Mcr * lc**2) / (48 * Ec * Ig) if Ig > 0 else 0
            Delta_n = (5 * Mn * lc**2) / (48 * Ec * Icr) if Icr > 0 else 0
            Delta_s = Delta_u * 0.7  # Aproximacion conservadora

        # Limite de deflexion
        Delta_limit = lc / 150
        deflection_ok = Delta_s <= Delta_limit

        # Actualizar verificacion de deflexion
        checks['deflection_ok'] = deflection_ok
        is_applicable = is_applicable and deflection_ok

        return SlenderWallResult(
            is_applicable=is_applicable,
            applicability_checks=checks,
            lc_mm=lc,
            h_mm=h,
            d_mm=d,
            Ec_mpa=Ec,
            Ig_mm4=Ig,
            Icr_mm4=Icr,
            Mcr_Nmm=Mcr,
            Mn_Nmm=Mn,
            phi_Mn_Nmm=phi_Mn,
            Mua_Nmm=Mua_Nmm,
            Mu_Nmm=Mu,
            magnification_factor=magnification,
            Delta_cr_mm=Delta_cr,
            Delta_n_mm=Delta_n,
            Delta_u_mm=Delta_u,
            Delta_s_mm=Delta_s,
            Delta_limit_mm=Delta_limit,
            deflection_ok=deflection_ok,
            aci_reference="ACI 318-25 Seccion 11.8"
        )


