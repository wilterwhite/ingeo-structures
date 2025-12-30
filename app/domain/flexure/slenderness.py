# app/domain/flexure/slenderness.py
"""
Verificacion de esbeltez para muros segun ACI 318-25.

Implementa:
- Calculo de esbeltez lambda = k*lu/r
- Magnificacion de momentos para muros esbeltos
- Reduccion de capacidad por pandeo

Referencias:
- ACI 318-25 Seccion 6.2.5: Efectos de esbeltez
- ACI 318-25 Seccion 6.6.4: Magnificacion de momentos
- ACI 318-25 Tabla 6.6.3.1.1(a): Rigidez efectiva
"""
import math
from app.domain.constants.stiffness import WALL_STIFFNESS_FACTOR
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities.pier import Pier


@dataclass
class SlendernessResult:
    """Resultado del análisis de esbeltez."""
    # Parámetros geométricos
    lu: float               # Altura libre (mm)
    t: float                # Espesor (mm)
    k: float                # Factor de longitud efectiva
    r: float                # Radio de giro (mm)

    # Esbeltez
    lambda_ratio: float     # λ = k×lu/r
    is_slender: bool        # True si λ > límite
    lambda_limit: float     # Límite de esbeltez (22 o 34)

    # Magnificación de momentos
    Pc_kN: float            # Carga crítica de Euler (kN)
    Cm: float               # Factor de momento equivalente
    delta_ns: float         # Factor de magnificación (≥ 1.0)

    # Reducción por pandeo (método empírico)
    buckling_factor: float  # Factor [1 - (k×lc/32t)²]


class SlendernessService:
    """
    Servicio para analisis de esbeltez de muros segun ACI 318-25.

    Referencias:
    - ACI 318-25 Seccion 6.2.5: Efectos de esbeltez
    - ACI 318-25 Seccion 6.6.4: Magnificacion de momentos
    - ACI 318-25 Seccion 11.5.3: Metodo empirico para muros
    - ACI 318-25 Tabla 6.6.3.1.1(a): Rigidez efectiva
    """

    # Limites de esbeltez ACI 318-25
    LAMBDA_LIMIT_BRACED = 22      # Porticos arriostrados (Tabla 6.2.5)
    LAMBDA_LIMIT_UNBRACED = 22    # Porticos no arriostrados
    LAMBDA_MAX = 100              # Limite maximo permitido

    # Factor k típico para muros
    K_BRACED_BOTH = 0.8           # Arriostrado arriba y abajo
    K_CANTILEVER = 2.0            # En voladizo

    def analyze(
        self,
        pier: 'Pier',
        k: float = 0.8,
        braced: bool = True,
        Cm: float = 1.0
    ) -> SlendernessResult:
        """
        Analiza la esbeltez de un muro.

        Args:
            pier: Entidad Pier con geometría y materiales
            k: Factor de longitud efectiva (default 0.8 para muros arriostrados)
            braced: True si el pórtico está arriostrado lateralmente
            Cm: Factor de momento equivalente (default 1.0 conservador)

        Returns:
            SlendernessResult con todos los parámetros calculados
        """
        # Geometría
        t = pier.thickness           # Espesor (mm)
        lu = pier.height             # Altura libre (mm)
        b = pier.width               # Largo del muro (mm)

        # Radio de giro para sección rectangular
        # r = I/A = (b×t³/12) / (b×t) = t/√12
        r = t / math.sqrt(12)

        # Esbeltez
        lambda_ratio = k * lu / r

        # Límite según condición de arriostramiento
        lambda_limit = self.LAMBDA_LIMIT_BRACED if braced else self.LAMBDA_LIMIT_UNBRACED
        is_slender = lambda_ratio > lambda_limit

        # Carga crítica de Euler
        Pc_kN = self._calculate_euler_load(pier, k)

        # Factor de magnificación (solo si es esbelto)
        if is_slender:
            delta_ns = self._calculate_magnification_factor(Cm, Pc_kN)
        else:
            delta_ns = 1.0

        # Factor de reducción por pandeo (método empírico ACI 11.5.3.1)
        # [1 - (k×lc/(32×t))²]
        buckling_ratio = k * lu / (32 * t)
        if buckling_ratio >= 1.0:
            # El muro es demasiado esbelto para el método empírico
            buckling_factor = 0.0
        else:
            buckling_factor = 1 - buckling_ratio**2

        return SlendernessResult(
            lu=lu,
            t=t,
            k=k,
            r=r,
            lambda_ratio=lambda_ratio,
            is_slender=is_slender,
            lambda_limit=lambda_limit,
            Pc_kN=Pc_kN,
            Cm=Cm,
            delta_ns=delta_ns,
            buckling_factor=buckling_factor
        )

    def _calculate_euler_load(self, pier: 'Pier', k: float) -> float:
        """
        Calcula la carga critica de pandeo de Euler.

        Pc = pi^2 * (EI)eff / (k*lu)^2

        Para muros agrietados: (EI)eff = 0.35*Ec*Ig
        ACI 318-25 Tabla 6.6.3.1.1(a)
        """
        # Modulo de elasticidad del hormigon
        # Ec = 4700*sqrt(fc) (MPa) para concreto de peso normal
        fc = pier.fc
        Ec = 4700 * math.sqrt(fc)  # MPa

        # Momento de inercia bruto
        # Ig = b*t^3/12 para flexion fuera del plano
        b = pier.width      # mm
        t = pier.thickness  # mm
        Ig = b * t**3 / 12  # mm^4

        # Rigidez efectiva para muros agrietados (diseno sismico)
        # ACI 318-25 Tabla 6.6.3.1.1(a): I = 0.35*Ig
        EI_eff = WALL_STIFFNESS_FACTOR * Ec * Ig  # N-mm^2

        # Longitud efectiva
        lu = pier.height  # mm
        le = k * lu       # mm

        # Carga crítica de Euler
        if le > 0:
            Pc = math.pi**2 * EI_eff / le**2  # N
        else:
            Pc = float('inf')

        return Pc / 1000  # kN

    def _calculate_magnification_factor(
        self,
        Cm: float,
        Pc_kN: float,
        Pu_kN: float = 0
    ) -> float:
        """
        Calcula el factor de magnificacion de momentos.

        delta_ns = Cm / (1 - Pu/(0.75*Pc)) >= 1.0

        ACI 318-25 Ec. 6.6.4.5.2
        """
        if Pu_kN <= 0 or Pc_kN <= 0:
            return 1.0

        denominator = 1 - Pu_kN / (0.75 * Pc_kN)

        if denominator <= 0:
            # Inestabilidad - carga mayor que capacidad de pandeo
            return float('inf')

        delta = Cm / denominator
        return max(delta, 1.0)

    def get_moment_magnification(
        self,
        slenderness: SlendernessResult,
        Pu_kN: float
    ) -> float:
        """
        Obtiene el factor de magnificación para una carga axial específica.

        Args:
            slenderness: Resultado del análisis de esbeltez
            Pu_kN: Carga axial de demanda (kN)

        Returns:
            Factor de magnificación δns ≥ 1.0
        """
        if not slenderness.is_slender:
            return 1.0

        return self._calculate_magnification_factor(
            slenderness.Cm,
            slenderness.Pc_kN,
            abs(Pu_kN)
        )

    def reduce_compression_capacity(
        self,
        phi_Pn_max_kN: float,
        slenderness: SlendernessResult
    ) -> float:
        """
        Reduce la capacidad de compresión por efectos de pandeo.

        Método híbrido:
        - Para λ ≤ 25: Sin reducción (muro corto)
        - Para 25 < λ ≤ 100: Reducción proporcional
        - Para λ > 100: No permitido

        Args:
            phi_Pn_max_kN: Capacidad nominal sin reducción por pandeo (kN)
            slenderness: Resultado del análisis de esbeltez

        Returns:
            Capacidad reducida (kN)
        """
        lambda_ratio = slenderness.lambda_ratio

        if lambda_ratio <= 25:
            # Muro corto - sin reducción
            reduction_factor = 1.0
        elif lambda_ratio > self.LAMBDA_MAX:
            # Demasiado esbelto
            reduction_factor = 0.0
        else:
            # Reducción gradual basada en el método empírico
            # Usar el factor de pandeo pero escalado
            reduction_factor = slenderness.buckling_factor

            # Asegurar que no sea negativo
            reduction_factor = max(reduction_factor, 0.0)

        return phi_Pn_max_kN * reduction_factor

    def calculate_effective_stiffness(
        self,
        fc: float,
        lw: float,
        t: float
    ) -> dict:
        """
        Calcula rigidez efectiva (EI)eff segun ACI 318-25 Tabla 6.6.3.1.1(a).

        Muros siempre se consideran agrietados (0.35*Ig) para diseno sismico.

        Args:
            fc: Resistencia del hormigon (MPa)
            lw: Largo del muro (mm)
            t: Espesor del muro (mm)

        Returns:
            dict con Ec, Ig, factor, EI_eff, referencia ACI
        """
        # Modulo de elasticidad
        Ec = 4700 * math.sqrt(fc)  # MPa

        # Momento de inercia bruto
        Ig = lw * t**3 / 12  # mm^4

        # Rigidez efectiva (muros agrietados)
        EI_eff = WALL_STIFFNESS_FACTOR * Ec * Ig  # N-mm^2

        return {
            "Ec_MPa": round(Ec, 1),
            "Ig_mm4": round(Ig, 0),
            "stiffness_factor": WALL_STIFFNESS_FACTOR,
            "EI_eff_Nmm2": round(EI_eff, 0),
            "aci_reference": "ACI 318-25 Tabla 6.6.3.1.1(a)"
        }
