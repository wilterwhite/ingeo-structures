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
from app.domain.constants.stiffness import (
    WALL_STIFFNESS_FACTOR,
    M2_MIN_ECCENTRICITY_BASE,
    M2_MIN_ECCENTRICITY_FACTOR,
    SECOND_ORDER_LIMIT,
    CM_BASE,
    CM_FACTOR,
    CM_MIN,
    CM_TRANSVERSE,
)
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..entities.pier import Pier
    from ..entities.column import Column
    from ..entities.protocols import FlexuralElement


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
        element: Union['Pier', 'Column', 'FlexuralElement'],
        k: float = 0.8,
        braced: bool = True,
        Cm: float = 1.0,
        direction: str = 'primary'
    ) -> SlendernessResult:
        """
        Analiza la esbeltez de un elemento (Pier o Column).

        Args:
            element: Pier, Column, o cualquier FlexuralElement
            k: Factor de longitud efectiva (default 0.8 para muros, 1.0 para columnas)
            braced: True si el pórtico está arriostrado lateralmente
            Cm: Factor de momento equivalente (default 1.0 conservador)
            direction: 'primary' o 'secondary' para obtener dimensiones

        Returns:
            SlendernessResult con todos los parámetros calculados
        """
        # Obtener geometria usando Protocol FlexuralElement
        b, t = element.get_section_dimensions(direction)
        lu = element.height

        # Radio de giro para sección rectangular
        # r = I/A = (b×t³/12) / (b×t) = t/√12
        r = t / math.sqrt(12)

        # Esbeltez
        lambda_ratio = k * lu / r

        # Límite según condición de arriostramiento
        lambda_limit = self.LAMBDA_LIMIT_BRACED if braced else self.LAMBDA_LIMIT_UNBRACED
        is_slender = lambda_ratio > lambda_limit

        # Carga crítica de Euler
        Pc_kN = self._calculate_euler_load(element, k, direction)

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

    def _calculate_euler_load(
        self,
        element: Union['Pier', 'Column', 'FlexuralElement'],
        k: float,
        direction: str = 'primary'
    ) -> float:
        """
        Calcula la carga critica de pandeo de Euler.

        Pc = pi^2 * (EI)eff / (k*lu)^2

        Para muros agrietados: (EI)eff = 0.35*Ec*Ig
        ACI 318-25 Tabla 6.6.3.1.1(a)
        """
        # Modulo de elasticidad del hormigon
        # Ec = 4700*sqrt(fc) (MPa) para concreto de peso normal
        fc = element.fc
        Ec = 4700 * math.sqrt(fc)  # MPa

        # Obtener dimensiones
        if hasattr(element, 'get_section_dimensions'):
            b, t = element.get_section_dimensions(direction)
        elif hasattr(element, 'thickness'):
            b = element.width
            t = element.thickness
        else:
            b = element.depth if direction == 'primary' else element.width
            t = element.width if direction == 'primary' else element.depth

        # Momento de inercia bruto
        # Ig = b*t^3/12 para flexion fuera del plano
        Ig = b * t**3 / 12  # mm^4

        # Rigidez efectiva para muros agrietados (diseno sismico)
        # ACI 318-25 Tabla 6.6.3.1.1(a): I = 0.35*Ig
        EI_eff = WALL_STIFFNESS_FACTOR * Ec * Ig  # N-mm^2

        # Longitud efectiva
        lu = element.height  # mm
        le = k * lu          # mm

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

    def calculate_Cm(
        self,
        M1: float,
        M2: float,
        has_transverse_loads: bool = False
    ) -> dict:
        """
        Calcula el factor Cm segun ACI 318-25 Seccion 6.6.4.5.3.

        Cm = 0.6 - 0.4*(M1/M2) para miembros sin cargas transversales
        Cm = 1.0 para miembros con cargas transversales

        Convencion de signos:
        - M1 = momento menor en extremo (valor absoluto menor)
        - M2 = momento mayor en extremo (valor absoluto mayor)
        - Curvatura doble: M1 y M2 tienen mismo signo → M1/M2 positivo → Cm bajo
        - Curvatura simple: M1 y M2 tienen signos opuestos → M1/M2 negativo → Cm alto

        Args:
            M1: Momento en extremo 1 (cualquier unidad, con signo)
            M2: Momento en extremo 2 (cualquier unidad, con signo)
            has_transverse_loads: True si hay cargas transversales entre apoyos

        Returns:
            dict con Cm, tipo de curvatura, y referencia ACI
        """
        # Si hay cargas transversales, Cm = 1.0
        if has_transverse_loads:
            return {
                "Cm": CM_TRANSVERSE,
                "M1": M1,
                "M2": M2,
                "M1_M2_ratio": None,
                "curvature": "transverse_loads",
                "aci_reference": "ACI 318-25 Sec. 6.6.4.5.3"
            }

        # Determinar cual es mayor en valor absoluto
        abs_M1 = abs(M1)
        abs_M2 = abs(M2)

        # M2 debe ser el mayor, M1 el menor
        if abs_M1 > abs_M2:
            M1_calc, M2_calc = M2, M1
        else:
            M1_calc, M2_calc = M1, M2

        # Evitar division por cero
        if abs(M2_calc) < 1e-10:
            # Si M2 ≈ 0, usar Cm = 1.0 (conservador)
            return {
                "Cm": CM_TRANSVERSE,
                "M1": M1,
                "M2": M2,
                "M1_M2_ratio": 0.0,
                "curvature": "negligible_moment",
                "aci_reference": "ACI 318-25 Sec. 6.6.4.5.3"
            }

        # Calcular ratio M1/M2
        # Positivo = curvatura doble (momentos mismo signo)
        # Negativo = curvatura simple (momentos signos opuestos)
        ratio = M1_calc / M2_calc

        # Calcular Cm
        Cm = CM_BASE - CM_FACTOR * ratio

        # Aplicar limite minimo
        Cm = max(Cm, CM_MIN)

        # Determinar tipo de curvatura
        if ratio > 0:
            curvature = "double"  # Curvatura doble
        elif ratio < 0:
            curvature = "single"  # Curvatura simple
        else:
            curvature = "zero_M1"  # M1 = 0

        return {
            "Cm": round(Cm, 3),
            "M1": M1_calc,
            "M2": M2_calc,
            "M1_M2_ratio": round(ratio, 3),
            "curvature": curvature,
            "aci_reference": "ACI 318-25 Sec. 6.6.4.5.3"
        }

    def calculate_M2_min(
        self,
        Pu_kN: float,
        h_mm: float
    ) -> dict:
        """
        Calcula el momento minimo M2,min segun ACI 318-25 Seccion 6.6.4.5.4.

        M2,min = Pu * e_min
        e_min = 15 + 0.03*h (mm)

        Este momento minimo asegura que el diseno considere una
        excentricidad minima, evitando disenar con momentos muy pequenos.

        Args:
            Pu_kN: Carga axial factorada (kN)
            h_mm: Dimension de la seccion en direccion de estabilidad (mm)
                  Para muros, tipicamente es el espesor.

        Returns:
            dict con e_min, M2_min, y referencia ACI
        """
        # Excentricidad minima (mm)
        e_min = M2_MIN_ECCENTRICITY_BASE + M2_MIN_ECCENTRICITY_FACTOR * h_mm

        # Momento minimo
        # M2,min (kN-m) = Pu (kN) * e_min (mm) / 1000
        M2_min_kNm = abs(Pu_kN) * e_min / 1000

        return {
            "e_min_mm": round(e_min, 1),
            "M2_min_kNm": round(M2_min_kNm, 2),
            "Pu_kN": abs(Pu_kN),
            "h_mm": h_mm,
            "aci_reference": "ACI 318-25 Ec. 6.6.4.5.4"
        }

    def get_design_moment(
        self,
        M2_kNm: float,
        Pu_kN: float,
        h_mm: float,
        delta: float = 1.0
    ) -> dict:
        """
        Obtiene el momento de diseno considerando M2,min y magnificacion.

        Mc = delta * max(M2, M2_min)

        Args:
            M2_kNm: Momento de analisis de primer orden (kN-m)
            Pu_kN: Carga axial factorada (kN)
            h_mm: Dimension de la seccion (mm)
            delta: Factor de magnificacion (default 1.0)

        Returns:
            dict con momento de diseno y si M2_min controla
        """
        # Calcular M2,min
        M2_min_result = self.calculate_M2_min(Pu_kN, h_mm)
        M2_min = M2_min_result["M2_min_kNm"]

        # M2 para diseno (el mayor entre M2 y M2,min)
        M2_abs = abs(M2_kNm)
        M2_design = max(M2_abs, M2_min)
        controls_min = M2_min > M2_abs

        # Momento magnificado
        Mc = delta * M2_design

        return {
            "M2_kNm": M2_abs,
            "M2_min_kNm": M2_min,
            "e_min_mm": M2_min_result["e_min_mm"],
            "M2_design_kNm": round(M2_design, 2),
            "delta": delta,
            "Mc_kNm": round(Mc, 2),
            "controls_M2_min": controls_min,
            "aci_reference": "ACI 318-25 Ec. 6.6.4.5.1, 6.6.4.5.4"
        }

    def verify_second_order_limit(
        self,
        Mu_first_order: float,
        Mu_second_order: float
    ) -> dict:
        """
        Verifica limite de efectos de segundo orden segun ACI 318-25 Seccion 6.2.5.3.

        Mu (2do orden) <= 1.4 * Mu (1er orden)

        Si se excede este limite, el sistema estructural es potencialmente
        inestable y debe ser revisado (aumentar rigidez, reducir esbeltez, etc.)

        Args:
            Mu_first_order: Momento de analisis de primer orden (cualquier unidad)
            Mu_second_order: Momento con efectos de segundo orden (misma unidad)

        Returns:
            dict con ratio, limite, status, y recomendacion
        """
        # Usar valores absolutos
        Mu_1 = abs(Mu_first_order)
        Mu_2 = abs(Mu_second_order)

        # Evitar division por cero
        if Mu_1 == 0:
            if Mu_2 == 0:
                ratio = 1.0
            else:
                ratio = float('inf')
        else:
            ratio = Mu_2 / Mu_1

        # Verificar limite
        limit = SECOND_ORDER_LIMIT
        passes = ratio <= limit

        # Determinar status y mensaje
        if passes:
            status = "OK"
            message = "Efectos de 2do orden dentro de limites aceptables"
        else:
            status = "NO OK"
            message = "Excede limite 1.4x - revisar sistema estructural"

        return {
            "Mu_first_order": Mu_1,
            "Mu_second_order": Mu_2,
            "ratio": round(ratio, 3) if ratio != float('inf') else float('inf'),
            "limit": limit,
            "status": status,
            "passes": passes,
            "message": message,
            "aci_reference": "ACI 318-25 Seccion 6.2.5.3"
        }

    def check_stability(
        self,
        pier: 'Pier',
        Pu_kN: float,
        Mu_kNm: float,
        k: float = 0.8
    ) -> dict:
        """
        Verificacion completa de estabilidad para un pier.

        Incluye:
        - Analisis de esbeltez
        - Magnificacion de momentos (si aplica)
        - Verificacion de limite 1.4x
        - Momento minimo M2,min

        Args:
            pier: Entidad Pier
            Pu_kN: Carga axial factorada (kN)
            Mu_kNm: Momento de primer orden (kN-m)
            k: Factor de longitud efectiva

        Returns:
            dict con resultados completos de estabilidad
        """
        # Analisis de esbeltez
        slenderness = self.analyze(pier, k=k)

        # Factor de magnificacion
        if slenderness.is_slender and Pu_kN > 0:
            delta = self.get_moment_magnification(slenderness, Pu_kN)
        else:
            delta = 1.0

        # Momento de diseno (considera M2,min)
        design = self.get_design_moment(
            M2_kNm=Mu_kNm,
            Pu_kN=Pu_kN,
            h_mm=pier.thickness,
            delta=delta
        )

        # Verificar limite 1.4x
        second_order_check = self.verify_second_order_limit(
            Mu_first_order=max(abs(Mu_kNm), design["M2_min_kNm"]),
            Mu_second_order=design["Mc_kNm"]
        )

        return {
            "slenderness": {
                "lambda": round(slenderness.lambda_ratio, 1),
                "is_slender": slenderness.is_slender,
                "Pc_kN": round(slenderness.Pc_kN, 1),
            },
            "magnification": {
                "delta": round(delta, 3) if delta != float('inf') else float('inf'),
                "Cm": slenderness.Cm,
            },
            "moments": {
                "Mu_first_order_kNm": abs(Mu_kNm),
                "M2_min_kNm": design["M2_min_kNm"],
                "controls_M2_min": design["controls_M2_min"],
                "Mc_design_kNm": design["Mc_kNm"],
            },
            "second_order_check": {
                "ratio": second_order_check["ratio"],
                "limit": SECOND_ORDER_LIMIT,
                "passes": second_order_check["passes"],
                "status": second_order_check["status"],
            },
            "overall_status": "OK" if second_order_check["passes"] else "REVISAR SISTEMA",
            "aci_reference": "ACI 318-25 Secciones 6.2.5, 6.6.4"
        }
