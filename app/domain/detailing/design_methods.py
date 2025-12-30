# app/structural/domain/wall_design_methods.py
"""
Metodos de diseno para muros segun ACI 318-25 Capitulo 11.

Implementa:
- 11.5.3: Metodo simplificado para carga axial y flexion fuera del plano
- 11.8: Metodo alternativo para muros esbeltos

Referencias ACI 318-25:
- Ec. 11.5.3.1: Resistencia nominal simplificada
- Tabla 11.5.3.2: Factor de longitud efectiva k
- Ec. 11.8.3.1a-d: Momento magnificado para muros esbeltos
- Ec. 11.8.3.1c: Inercia agrietada
- Tabla 11.8.4.1: Deflexion de servicio
"""
from dataclasses import dataclass
from typing import Optional, Tuple, TYPE_CHECKING
from enum import Enum
import math

if TYPE_CHECKING:
    from .entities.pier import Pier


class BoundaryCondition(Enum):
    """Condiciones de borde para factor k."""
    BRACED_RESTRAINED = "braced_restrained"     # Arriostrado, restringido rotacion
    BRACED_UNRESTRAINED = "braced_unrestrained" # Arriostrado, sin restriccion
    UNBRACED = "unbraced"                        # No arriostrado


@dataclass
class SimplifiedMethodResult:
    """Resultado del metodo simplificado 11.5.3."""
    # Parametros de entrada
    fc_mpa: float               # f'c (MPa)
    Ag_mm2: float               # Area bruta (mm2)
    k: float                    # Factor de longitud efectiva
    lc_mm: float                # Longitud no soportada (mm)
    h_mm: float                 # Espesor del muro (mm)

    # Resultados
    Pn_N: float                 # Resistencia nominal (N)
    phi_Pn_N: float             # Resistencia de diseno (N)
    Pn_tonf: float              # Resistencia nominal (tonf)
    phi_Pn_tonf: float          # Resistencia de diseno (tonf)
    slenderness_term: float     # Termino [1 - (k*lc/32h)^2]
    is_applicable: bool         # Si el metodo es aplicable
    applicability_note: str     # Nota sobre aplicabilidad

    aci_reference: str          # Referencia ACI


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


class WallDesignMethodsService:
    """
    Servicio para metodos de diseno de muros segun ACI 318-25.

    Unidades:
    - Dimensiones: mm
    - Esfuerzos: MPa
    - Fuerzas: N (internamente), tonf (salida)
    - Momentos: N-mm (internamente), tonf-m (salida)
    """

    # Factor de conversion
    N_TO_TONF = 9806.65
    NMM_TO_TONFM = 9806650.0

    # Factores de reduccion (ACI 318-25 21.2.2)
    PHI_COMPRESSION = 0.65
    PHI_TENSION = 0.90

    # Modulo de elasticidad del acero
    ES_MPA = 200000

    # Deformacion ultima del concreto
    EPSILON_CU = 0.003

    # =========================================================================
    # METODO SIMPLIFICADO 11.5.3
    # =========================================================================

    def get_k_factor(self, condition: BoundaryCondition) -> float:
        """
        Obtiene factor k segun Tabla 11.5.3.2.

        Args:
            condition: Condicion de borde

        Returns:
            Factor k
        """
        k_values = {
            BoundaryCondition.BRACED_RESTRAINED: 0.8,
            BoundaryCondition.BRACED_UNRESTRAINED: 1.0,
            BoundaryCondition.UNBRACED: 2.0
        }
        return k_values.get(condition, 1.0)

    def check_simplified_method_applicability(
        self,
        eccentricity_mm: float,
        h_mm: float
    ) -> Tuple[bool, str]:
        """
        Verifica si aplica el metodo simplificado (11.5.3.1).

        Condicion: Resultante dentro del tercio medio (e <= h/6)

        Args:
            eccentricity_mm: Excentricidad de la carga (mm)
            h_mm: Espesor del muro (mm)

        Returns:
            Tuple (es_aplicable, nota)
        """
        e_limit = h_mm / 6
        is_applicable = eccentricity_mm <= e_limit

        if is_applicable:
            note = f"Aplica: e={eccentricity_mm:.1f}mm <= h/6={e_limit:.1f}mm"
        else:
            note = f"No aplica: e={eccentricity_mm:.1f}mm > h/6={e_limit:.1f}mm (usar metodo general)"

        return (is_applicable, note)

    def calculate_simplified_Pn(
        self,
        fc_mpa: float,
        Ag_mm2: float,
        k: float,
        lc_mm: float,
        h_mm: float,
        eccentricity_mm: float = 0
    ) -> SimplifiedMethodResult:
        """
        Calcula resistencia nominal por metodo simplificado Ec. 11.5.3.1.

        Pn = 0.55 * f'c * Ag * [1 - (k*lc/(32*h))^2]

        Args:
            fc_mpa: Resistencia del concreto f'c (MPa)
            Ag_mm2: Area bruta de la seccion (mm2)
            k: Factor de longitud efectiva
            lc_mm: Longitud no soportada (mm)
            h_mm: Espesor del muro (mm)
            eccentricity_mm: Excentricidad de la carga (mm)

        Returns:
            SimplifiedMethodResult con resultado del calculo
        """
        # Verificar aplicabilidad
        is_applicable, note = self.check_simplified_method_applicability(
            eccentricity_mm, h_mm
        )

        # Calcular termino de esbeltez
        slenderness_ratio = k * lc_mm / (32 * h_mm)

        if slenderness_ratio >= 1.0:
            # Muro demasiado esbelto - Pn = 0
            slenderness_term = 0.0
            is_applicable = False
            note = f"Muro muy esbelto: k*lc/(32h) = {slenderness_ratio:.2f} >= 1.0"
        else:
            slenderness_term = 1 - slenderness_ratio**2

        # Resistencia nominal
        Pn_N = 0.55 * fc_mpa * Ag_mm2 * slenderness_term

        # Resistencia de diseno (phi para compresion)
        phi_Pn_N = self.PHI_COMPRESSION * Pn_N

        return SimplifiedMethodResult(
            fc_mpa=fc_mpa,
            Ag_mm2=Ag_mm2,
            k=k,
            lc_mm=lc_mm,
            h_mm=h_mm,
            Pn_N=Pn_N,
            phi_Pn_N=phi_Pn_N,
            Pn_tonf=Pn_N / self.N_TO_TONF,
            phi_Pn_tonf=phi_Pn_N / self.N_TO_TONF,
            slenderness_term=slenderness_term,
            is_applicable=is_applicable,
            applicability_note=note,
            aci_reference="ACI 318-25 Ec. 11.5.3.1"
        )

    def calculate_simplified_from_pier(
        self,
        pier: 'Pier',
        boundary_condition: BoundaryCondition = BoundaryCondition.BRACED_RESTRAINED,
        eccentricity_mm: float = 0
    ) -> SimplifiedMethodResult:
        """
        Calcula resistencia por metodo simplificado desde un Pier.

        Args:
            pier: Entidad Pier
            boundary_condition: Condicion de borde
            eccentricity_mm: Excentricidad de la carga

        Returns:
            SimplifiedMethodResult
        """
        k = self.get_k_factor(boundary_condition)

        return self.calculate_simplified_Pn(
            fc_mpa=pier.fc,
            Ag_mm2=pier.Ag,
            k=k,
            lc_mm=pier.height,
            h_mm=pier.thickness,
            eccentricity_mm=eccentricity_mm
        )

    # =========================================================================
    # METODO ALTERNATIVO PARA MUROS ESBELTOS 11.8
    # =========================================================================

    def calculate_Ec(self, fc_mpa: float) -> float:
        """Modulo de elasticidad del concreto (MPa)."""
        return 4700 * math.sqrt(fc_mpa)

    def calculate_fr(self, fc_mpa: float) -> float:
        """Modulo de ruptura del concreto (MPa) segun 19.2.3."""
        return 0.62 * math.sqrt(fc_mpa)

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
        fr = self.calculate_fr(fc_mpa)
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
        # Beta1
        if fc_mpa <= 28:
            beta1 = 0.85
        elif fc_mpa >= 55:
            beta1 = 0.65
        else:
            beta1 = 0.85 - 0.05 * (fc_mpa - 28) / 7

        # Equilibrio simplificado
        # Fuerza de compresion = Fuerza del acero + Carga axial
        # 0.85 * fc * a * lw = As * fy + Pu
        # a = beta1 * c

        numerator = As_mm2 * fy_mpa + Pu_N
        denominator = 0.85 * fc_mpa * beta1 * lw_mm

        if denominator > 0:
            c = numerator / denominator
        else:
            c = 0.1 * d_mm

        # Limitar c a valores razonables
        c = max(0.05 * d_mm, min(c, 0.9 * d_mm))

        return c

    def calculate_magnified_moment_iterative(
        self,
        Mua_Nmm: float,
        Pu_N: float,
        lc_mm: float,
        Ec_mpa: float,
        Icr_mm4: float
    ) -> Tuple[float, float]:
        """
        Calcula momento magnificado Mu iterativamente segun Ec. 11.8.3.1a-b.

        Mu = Mua + Pu * Delta_u
        Delta_u = (5 * Mu * lc^2) / (0.75 * 48 * Ec * Icr)

        Args:
            Mua_Nmm: Momento sin efectos P-Delta (N-mm)
            Pu_N: Carga axial factorada (N)
            lc_mm: Longitud no soportada (mm)
            Ec_mpa: Modulo de elasticidad (MPa)
            Icr_mm4: Inercia agrietada (mm4)

        Returns:
            Tuple (Mu_Nmm, Delta_u_mm)
        """
        # Constante para deflexion
        # Delta_u = (5 * Mu * lc^2) / (0.75 * 48 * Ec * Icr)
        denom = 0.75 * 48 * Ec_mpa * Icr_mm4

        if denom <= 0:
            return (Mua_Nmm, 0.0)

        # Metodo iterativo
        Mu = Mua_Nmm
        max_iterations = 20
        tolerance = 0.001

        for _ in range(max_iterations):
            Delta_u = (5 * Mu * lc_mm**2) / denom
            Mu_new = Mua_Nmm + Pu_N * Delta_u

            if abs(Mu_new - Mu) / max(Mu, 1) < tolerance:
                Mu = Mu_new
                break
            Mu = Mu_new

        Delta_u = (5 * Mu * lc_mm**2) / denom

        return (Mu, Delta_u)

    def calculate_magnified_moment_direct(
        self,
        Mua_Nmm: float,
        Pu_N: float,
        lc_mm: float,
        Ec_mpa: float,
        Icr_mm4: float
    ) -> Tuple[float, float]:
        """
        Calcula momento magnificado Mu directamente segun Ec. 11.8.3.1d.

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

        # Denominador del factor de magnificacion
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
    ) -> float:
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
            Delta_s en mm
        """
        # Deflexiones de referencia (Ec. 11.8.4.3a-b)
        Delta_cr = (5 * Mcr_Nmm * lc_mm**2) / (48 * Ec_mpa * Ig_mm4)
        Delta_n = (5 * Mn_Nmm * lc_mm**2) / (48 * Ec_mpa * Icr_mm4)

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

        return Delta_s

    def check_slender_wall_applicability(
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
        (e) Deflexion <= lc/150 (verificada separadamente)

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
        checks['Pu_limit'] = Pu_N <= Pu_limit
        checks['Pu_limit_value'] = Pu_limit / self.N_TO_TONF

        is_applicable = all([
            checks['constant_section'],
            checks['phi_Mn_ge_Mcr'],
            checks['Pu_limit']
        ])

        return (is_applicable, checks)

    def analyze_slender_wall(
        self,
        pier: 'Pier',
        Pu_N: float,
        Mua_Nmm: float,
        As_tension_mm2: float,
        Ma_service_Nmm: float = 0,
        Ps_service_N: float = 0,
        has_openings: bool = False
    ) -> SlenderWallResult:
        """
        Analiza muro esbelto segun metodo alternativo 11.8.

        Args:
            pier: Entidad Pier
            Pu_N: Carga axial factorada a media altura (N)
            Mua_Nmm: Momento factorado sin P-Delta (N-mm)
            As_tension_mm2: Area de acero en zona de traccion (mm2)
            Ma_service_Nmm: Momento de servicio (N-mm)
            Ps_service_N: Carga axial de servicio (N)
            has_openings: Tiene aberturas grandes

        Returns:
            SlenderWallResult con resultados del analisis
        """
        # Propiedades
        lc = pier.height
        h = pier.thickness
        lw = pier.width
        d = pier.width - pier.cover  # Profundidad efectiva
        fc = pier.fc
        fy = pier.fy

        # Modulos
        Ec = self.calculate_Ec(fc)

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
            self.ES_MPA, Ec, As_tension_mm2, Pu_N, fy, h, d, c, lw
        )

        # Momento nominal simplificado (As*fy*(d-a/2))
        # Esto es una aproximacion; el valor exacto viene del diagrama P-M
        a = As_tension_mm2 * fy / (0.85 * fc * lw)
        Mn = As_tension_mm2 * fy * (d - a / 2)
        phi_Mn = self.PHI_TENSION * Mn

        # Verificar aplicabilidad
        is_applicable, checks = self.check_slender_wall_applicability(
            pier, Pu_N, phi_Mn, Mcr, has_openings
        )

        # Momento magnificado
        Mu, Delta_u = self.calculate_magnified_moment_direct(
            Mua_Nmm, Pu_N, lc, Ec, Icr
        )

        magnification = Mu / Mua_Nmm if Mua_Nmm > 0 else 1.0

        # Deflexiones
        Delta_cr = (5 * Mcr * lc**2) / (48 * Ec * Ig) if Ig > 0 else 0
        Delta_n = (5 * Mn * lc**2) / (48 * Ec * Icr) if Icr > 0 else 0

        # Deflexion de servicio (si se proporcionan cargas de servicio)
        if Ma_service_Nmm > 0:
            Delta_s = self.calculate_service_deflection(
                Ma_service_Nmm, Mcr, Mn, lc, Ec, Ig, Icr
            )
        else:
            # Estimar como fraccion de Delta_u
            Delta_s = Delta_u * 0.7  # Aproximacion

        # Limite de deflexion
        Delta_limit = lc / 150
        deflection_ok = Delta_s <= Delta_limit

        # Actualizar verificacion de deflexion en checks
        checks['deflection'] = deflection_ok
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
