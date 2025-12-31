# app/domain/shear/shear_friction.py
"""
Servicio de friccion por cortante segun ACI 318-25 Seccion 22.9.

Este modulo implementa el calculo de resistencia por friccion para:
- Juntas de construccion horizontales en muros
- Interfaces entre concretos colocados en diferentes tiempos
- Transferencia de cortante a traves de grietas existentes o potenciales

Referencias ACI 318-25:
- 22.9.1: Aplicabilidad
- 22.9.4.2: Refuerzo perpendicular al plano de cortante
- 22.9.4.3: Refuerzo inclinado al plano de cortante
- 22.9.4.4: Limites maximos de Vn
- Tabla 22.9.4.2: Coeficientes de friccion

Unidades: entrada en mm/MPa, salida en tonf.
"""
import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ..constants.materials import LAMBDA_NORMAL
from ..constants.shear import (
    PHI_SHEAR_FRICTION,
    SHEAR_FRICTION_MU,
    SHEAR_FRICTION_VN_MAX_COEF_1,
    SHEAR_FRICTION_VN_MAX_COEF_2_BASE,
    SHEAR_FRICTION_VN_MAX_COEF_2_FC,
    SHEAR_FRICTION_VN_MAX_LIMIT_MPa,
    SHEAR_FRICTION_VN_MAX_OTHER_MPa,
    SHEAR_FRICTION_FY_LIMIT_MPa,
    N_TO_TONF,
)


class SurfaceCondition(Enum):
    """
    Condicion de la superficie de contacto segun Tabla 22.9.4.2.

    Determina el coeficiente de friccion (mu) a usar.
    """
    MONOLITHIC = 'monolithic'           # Concreto colocado monoliticamente
    ROUGHENED = 'roughened'             # Rugosidad intencional ~6mm (1/4")
    NOT_ROUGHENED = 'not_roughened'     # Sin rugosidad intencional
    STEEL = 'steel'                     # Concreto contra acero estructural


@dataclass
class ShearFrictionResult:
    """
    Resultado de la verificacion de friccion por cortante.

    Todos los valores de fuerza estan en tonf.
    Referencias ACI 318-25 Seccion 22.9.
    """
    # Capacidades calculadas
    Vn: float               # Resistencia nominal por friccion (tonf)
    Vn_max: float           # Limite maximo de Vn segun 22.9.4.4 (tonf)
    Vn_effective: float     # min(Vn, Vn_max) (tonf)
    phi_Vn: float           # Resistencia de diseno phi*Vn (tonf)

    # Componentes del calculo
    mu: float               # Coeficiente de friccion usado
    mu_effective: float     # mu * lambda (efectivo)
    Avf_fy: float           # Avf * fy (N) - aporte del acero
    Nu_contribution: float  # mu * Nu (N) - aporte de compresion axial

    # Demanda y verificacion
    Vu: float               # Demanda de cortante mayorado (tonf)
    sf: float               # Factor de seguridad = phi*Vn / Vu
    status: str             # "OK" si sf >= 1.0, "NO OK" si sf < 1.0

    # Parametros de entrada
    surface_condition: str  # Condicion de superficie usada
    Ac: float               # Area de contacto (mm2)
    Avf: float              # Area de refuerzo de friccion (mm2)
    fy: float               # Resistencia del acero (MPa)
    fc: float               # Resistencia del concreto (MPa)

    # Control de limites
    controls_max_limit: bool  # True si Vn_max gobierna
    fy_limited: bool          # True si fy fue limitado a 420 MPa

    # Referencia ACI
    aci_reference: str = "ACI 318-25 22.9"


@dataclass
class ShearFrictionDesignResult:
    """
    Resultado del diseno de refuerzo de friccion por cortante.

    Calcula el area de refuerzo requerida para resistir Vu.
    """
    # Refuerzo requerido
    Avf_required: float     # Area de refuerzo requerida (mm2)
    Avf_per_meter: float    # Area por metro de junta (mm2/m)

    # Parametros de diseno
    Vu: float               # Demanda de cortante (tonf)
    mu: float               # Coeficiente de friccion
    fy: float               # Resistencia del acero (MPa)
    Nu: float               # Carga axial concurrente (tonf, + compresion)

    # Verificacion de limites
    Vn_max: float           # Limite maximo de Vn (tonf)
    is_feasible: bool       # True si Vu <= phi*Vn_max

    # Geometria
    Ac: float               # Area de contacto (mm2)
    length: float           # Longitud de la junta (mm)

    aci_reference: str = "ACI 318-25 22.9"


class ShearFrictionService:
    """
    Servicio para calculo de friccion por cortante segun ACI 318-25.

    Aplicaciones tipicas:
    - Juntas de construccion horizontales en muros
    - Conexiones viga-columna
    - Interfaces prefabricado-in situ
    - Transferencia de cortante en losas compuestas

    Unidades:
    - Entrada: mm, MPa, N (o tonf para Vu, Nu)
    - Salida: tonf para fuerzas

    Ejemplo de uso:
    >>> service = ShearFrictionService()
    >>> result = service.verify_shear_friction(
    ...     Ac=300*1000,        # Area de contacto 300mm x 1000mm
    ...     Avf=4*113,          # 4 barras #12 (4 x 113 mm2)
    ...     fc=28,              # f'c = 28 MPa
    ...     fy=420,             # fy = 420 MPa
    ...     Vu=50,              # Demanda = 50 tonf
    ...     surface=SurfaceCondition.ROUGHENED
    ... )
    """

    def get_mu(
        self,
        surface: SurfaceCondition,
        lambda_concrete: float = LAMBDA_NORMAL
    ) -> float:
        """
        Obtiene el coeficiente de friccion segun Tabla 22.9.4.2.

        Args:
            surface: Condicion de la superficie de contacto
            lambda_concrete: Factor lambda para concreto liviano (1.0 normal)

        Returns:
            Coeficiente de friccion mu * lambda

        Note:
            Para superficie 'not_roughened', lambda no se aplica (ACI 318-25).
        """
        mu_base = SHEAR_FRICTION_MU[surface.value]

        # ACI 318-25: lambda no aplica a superficie no rugosa
        if surface == SurfaceCondition.NOT_ROUGHENED:
            return mu_base

        return mu_base * lambda_concrete

    def calculate_Vn_max(
        self,
        fc: float,
        Ac: float,
        surface: SurfaceCondition
    ) -> float:
        """
        Calcula el limite maximo de Vn segun Tabla 22.9.4.4.

        Para concreto de peso normal, monolitico o rugoso:
            Vn_max = min(0.2*f'c*Ac, (3.3 + 0.08*f'c)*Ac, 11*Ac)

        Para otros casos (no rugoso, contra acero):
            Vn_max = min(0.2*f'c*Ac, 5.5*Ac)

        Args:
            fc: Resistencia del concreto (MPa)
            Ac: Area de contacto (mm2)
            surface: Condicion de la superficie

        Returns:
            Vn_max en N
        """
        # Limite comun: 0.2 * f'c * Ac
        limit_1 = SHEAR_FRICTION_VN_MAX_COEF_1 * fc * Ac

        if surface in (SurfaceCondition.MONOLITHIC, SurfaceCondition.ROUGHENED):
            # Casos normales: tres limites
            limit_2 = (SHEAR_FRICTION_VN_MAX_COEF_2_BASE +
                      SHEAR_FRICTION_VN_MAX_COEF_2_FC * fc) * Ac
            limit_3 = SHEAR_FRICTION_VN_MAX_LIMIT_MPa * Ac
            return min(limit_1, limit_2, limit_3)
        else:
            # Otros casos: dos limites
            limit_2 = SHEAR_FRICTION_VN_MAX_OTHER_MPa * Ac
            return min(limit_1, limit_2)

    def calculate_Vn_perpendicular(
        self,
        Avf: float,
        fy: float,
        mu: float,
        Nu: float = 0
    ) -> float:
        """
        Calcula Vn para refuerzo perpendicular al plano de cortante.

        Ec. 22.9.4.2:
            Vn = mu * (Avf * fy + Nu)

        Args:
            Avf: Area de refuerzo de friccion (mm2)
            fy: Resistencia del acero (MPa), sera limitado a 420 MPa
            mu: Coeficiente de friccion efectivo (mu * lambda)
            Nu: Carga axial minima concurrente (N, positivo para compresion)

        Returns:
            Vn en N

        Note:
            Nu debe ser la carga de compresion minima que actua
            simultaneamente con Vu. Se permite tomar Nu = 0.
        """
        # Limitar fy segun 22.9.1.3
        fy_eff = min(fy, SHEAR_FRICTION_FY_LIMIT_MPa)

        # Ec. 22.9.4.2
        Vn = mu * (Avf * fy_eff + Nu)

        return max(0, Vn)  # Vn no puede ser negativo

    def calculate_Vn_inclined(
        self,
        Avf: float,
        fy: float,
        mu: float,
        alpha_deg: float,
        Nu: float = 0
    ) -> float:
        """
        Calcula Vn para refuerzo inclinado al plano de cortante.

        Ec. 22.9.4.3:
            Vn = Avf * fy * (mu * sin(alpha) + cos(alpha)) + mu * Nu

        Args:
            Avf: Area de refuerzo de friccion (mm2)
            fy: Resistencia del acero (MPa)
            mu: Coeficiente de friccion efectivo
            alpha_deg: Angulo entre refuerzo y plano de cortante (grados)
            Nu: Carga axial concurrente (N, positivo para compresion)

        Returns:
            Vn en N, o 0 si el cortante induce compresion en el refuerzo

        Note:
            Si el cortante induce compresion en el refuerzo (alpha < 0 efectivo),
            la friccion por cortante no aplica y se retorna Vn = 0.
        """
        # Limitar fy
        fy_eff = min(fy, SHEAR_FRICTION_FY_LIMIT_MPa)

        # Convertir a radianes
        alpha_rad = math.radians(alpha_deg)

        # Verificar que el cortante induce tension
        # (si mu*sin(alpha) + cos(alpha) < 0, el refuerzo esta en compresion)
        factor = mu * math.sin(alpha_rad) + math.cos(alpha_rad)
        if factor <= 0:
            return 0

        # Ec. 22.9.4.3
        Vn = Avf * fy_eff * factor + mu * Nu

        return max(0, Vn)

    def verify_shear_friction(
        self,
        Ac: float,
        Avf: float,
        fc: float,
        fy: float,
        Vu: float,
        surface: SurfaceCondition = SurfaceCondition.ROUGHENED,
        Nu: float = 0,
        alpha_deg: Optional[float] = None,
        lambda_concrete: float = LAMBDA_NORMAL
    ) -> ShearFrictionResult:
        """
        Verifica resistencia por friccion por cortante.

        Args:
            Ac: Area de contacto (mm2)
            Avf: Area de refuerzo de friccion perpendicular al plano (mm2)
            fc: Resistencia del concreto (MPa)
            fy: Resistencia del acero (MPa)
            Vu: Demanda de cortante mayorado (tonf)
            surface: Condicion de la superficie de contacto
            Nu: Carga axial concurrente (tonf, positivo para compresion)
            alpha_deg: Angulo del refuerzo (grados). None = perpendicular (90)
            lambda_concrete: Factor lambda para concreto liviano

        Returns:
            ShearFrictionResult con todos los resultados
        """
        # Convertir demandas de tonf a N
        Vu_N = abs(Vu) * N_TO_TONF
        Nu_N = Nu * N_TO_TONF  # Nu ya es positivo para compresion

        # Obtener coeficiente de friccion
        mu = self.get_mu(surface, lambda_concrete)
        mu_base = SHEAR_FRICTION_MU[surface.value]

        # Verificar si fy fue limitado
        fy_limited = fy > SHEAR_FRICTION_FY_LIMIT_MPa
        fy_eff = min(fy, SHEAR_FRICTION_FY_LIMIT_MPa)

        # Calcular Vn segun tipo de refuerzo
        if alpha_deg is None or alpha_deg == 90:
            # Refuerzo perpendicular (caso mas comun)
            Vn_N = self.calculate_Vn_perpendicular(Avf, fy_eff, mu, Nu_N)
            aci_eq = "22.9.4.2"
        else:
            # Refuerzo inclinado
            Vn_N = self.calculate_Vn_inclined(Avf, fy_eff, mu, alpha_deg, Nu_N)
            aci_eq = "22.9.4.3"

        # Calcular limite maximo
        Vn_max_N = self.calculate_Vn_max(fc, Ac, surface)

        # Aplicar limite
        controls_max_limit = Vn_N > Vn_max_N
        Vn_effective_N = min(Vn_N, Vn_max_N)

        # Convertir a tonf
        Vn = Vn_N / N_TO_TONF
        Vn_max = Vn_max_N / N_TO_TONF
        Vn_effective = Vn_effective_N / N_TO_TONF

        # Resistencia de diseno
        phi_Vn = PHI_SHEAR_FRICTION * Vn_effective

        # Verificacion
        Vu_abs = abs(Vu)
        sf = phi_Vn / Vu_abs if Vu_abs > 0 else float('inf')
        status = "OK" if sf >= 1.0 else "NO OK"

        return ShearFrictionResult(
            Vn=Vn,
            Vn_max=Vn_max,
            Vn_effective=Vn_effective,
            phi_Vn=phi_Vn,
            mu=mu_base,
            mu_effective=mu,
            Avf_fy=Avf * fy_eff,
            Nu_contribution=mu * Nu_N,
            Vu=Vu_abs,
            sf=sf,
            status=status,
            surface_condition=surface.value,
            Ac=Ac,
            Avf=Avf,
            fy=fy_eff,
            fc=fc,
            controls_max_limit=controls_max_limit,
            fy_limited=fy_limited,
            aci_reference=f"ACI 318-25 Ec. {aci_eq}, Tabla 22.9.4.4"
        )

    def design_shear_friction(
        self,
        Ac: float,
        fc: float,
        fy: float,
        Vu: float,
        surface: SurfaceCondition = SurfaceCondition.ROUGHENED,
        Nu: float = 0,
        length: Optional[float] = None,
        lambda_concrete: float = LAMBDA_NORMAL
    ) -> ShearFrictionDesignResult:
        """
        Disena refuerzo de friccion por cortante.

        Calcula el area de refuerzo requerida para resistir Vu.

        Ec. R22.9.4.2:
            Avf = (Vu/phi - mu*Nu) / (mu*fy)

        Args:
            Ac: Area de contacto (mm2)
            fc: Resistencia del concreto (MPa)
            fy: Resistencia del acero (MPa)
            Vu: Demanda de cortante mayorado (tonf)
            surface: Condicion de la superficie
            Nu: Carga axial concurrente (tonf, positivo para compresion)
            length: Longitud de la junta (mm), para calcular Avf/m
            lambda_concrete: Factor lambda

        Returns:
            ShearFrictionDesignResult con refuerzo requerido
        """
        # Convertir a N
        Vu_N = abs(Vu) * N_TO_TONF
        Nu_N = Nu * N_TO_TONF

        # Obtener mu y limitar fy
        mu = self.get_mu(surface, lambda_concrete)
        fy_eff = min(fy, SHEAR_FRICTION_FY_LIMIT_MPa)

        # Calcular Vn_max
        Vn_max_N = self.calculate_Vn_max(fc, Ac, surface)
        Vn_max = Vn_max_N / N_TO_TONF

        # Verificar factibilidad
        phi_Vn_max = PHI_SHEAR_FRICTION * Vn_max
        is_feasible = abs(Vu) <= phi_Vn_max

        # Calcular Avf requerido (Ec. R22.9.4.2)
        # Avf = (Vu/phi - mu*Nu) / (mu*fy)
        Vn_required = Vu_N / PHI_SHEAR_FRICTION
        Avf_required = (Vn_required - mu * Nu_N) / (mu * fy_eff)
        Avf_required = max(0, Avf_required)

        # Calcular Avf por metro si se proporciona longitud
        if length is not None and length > 0:
            Avf_per_meter = Avf_required / length * 1000
        else:
            Avf_per_meter = 0
            length = 0

        return ShearFrictionDesignResult(
            Avf_required=Avf_required,
            Avf_per_meter=Avf_per_meter,
            Vu=abs(Vu),
            mu=mu,
            fy=fy_eff,
            Nu=Nu,
            Vn_max=Vn_max,
            is_feasible=is_feasible,
            Ac=Ac,
            length=length,
            aci_reference="ACI 318-25 22.9.4.2"
        )

    def verify_construction_joint(
        self,
        lw: float,
        tw: float,
        fc: float,
        fy: float,
        Vu: float,
        rho_v: float,
        Nu: float = 0,
        surface: SurfaceCondition = SurfaceCondition.ROUGHENED
    ) -> ShearFrictionResult:
        """
        Verifica junta de construccion horizontal en muro.

        Caso tipico: junta entre coladas de muro donde el refuerzo
        vertical atraviesa la junta.

        Args:
            lw: Longitud del muro (mm)
            tw: Espesor del muro (mm)
            fc: Resistencia del concreto (MPa)
            fy: Resistencia del acero (MPa)
            Vu: Demanda de cortante en la junta (tonf)
            rho_v: Cuantia de refuerzo vertical que cruza la junta
            Nu: Carga axial en la junta (tonf, + compresion)
            surface: Condicion de preparacion de la junta

        Returns:
            ShearFrictionResult
        """
        # Area de contacto = area de la seccion
        Ac = lw * tw

        # Area de refuerzo que cruza la junta
        Avf = rho_v * Ac

        return self.verify_shear_friction(
            Ac=Ac,
            Avf=Avf,
            fc=fc,
            fy=fy,
            Vu=Vu,
            surface=surface,
            Nu=Nu
        )
