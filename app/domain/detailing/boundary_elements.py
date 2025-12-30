# app/structural/domain/boundary_elements.py
"""
Verificacion de elementos de borde para muros estructurales especiales.

Implementa ACI 318-25 Seccion 18.10.6:
- Metodo basado en desplazamiento (18.10.6.2)
- Metodo basado en esfuerzos (18.10.6.3)
- Requisitos de elementos de borde especiales (18.10.6.4)
- Espaciamiento de refuerzo transversal (Tabla 18.10.6.5(b))

Referencias ACI 318-25:
- 18.10.6.2: Enfoque basado en desplazamiento
- 18.10.6.3: Enfoque basado en esfuerzos
- 18.10.6.4: Requisitos para elementos de borde especiales
- Tabla 18.10.6.4(g): Refuerzo transversal
- Tabla 18.10.6.5(b): Espaciamiento maximo
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, List
import math


class BoundaryElementMethod(Enum):
    """Metodo de verificacion de elementos de borde."""
    DISPLACEMENT = "displacement"  # 18.10.6.2
    STRESS = "stress"              # 18.10.6.3


class SteelGrade(Enum):
    """Grado del acero de refuerzo."""
    GRADE_60 = 60
    GRADE_80 = 80
    GRADE_100 = 100


@dataclass
class DisplacementCheckResult:
    """Resultado de verificacion por metodo de desplazamiento."""
    delta_u: float              # Desplazamiento de diseno (mm)
    hwcs: float                 # Altura desde seccion critica (mm)
    lw: float                   # Longitud del muro (mm)
    c: float                    # Profundidad eje neutro (mm)
    drift_ratio: float          # delta_u / hwcs
    limit: float                # lw / (600 * c)
    check_value: float          # 1.5 * drift_ratio
    requires_special: bool       # Si requiere elemento de borde especial
    aci_reference: str


@dataclass
class StressCheckResult:
    """Resultado de verificacion por metodo de esfuerzos."""
    sigma_max: float            # Esfuerzo maximo de compresion (MPa)
    fc: float                   # Resistencia del hormigon (MPa)
    limit_require: float        # 0.2 * f'c
    limit_discontinue: float    # 0.15 * f'c
    requires_special: bool       # Si requiere elemento de borde especial
    can_discontinue: bool        # Si puede discontinuar elemento existente
    aci_reference: str


@dataclass
class BoundaryElementDimensions:
    """Dimensiones requeridas del elemento de borde."""
    length_horizontal: float    # Extension horizontal (mm) - desde 18.10.6.4(a)
    width_min: float           # Ancho minimo (mm) - desde 18.10.6.4(b)
    width_required: float      # Ancho requerido (mm) - desde 18.10.6.2(b)(ii)
    vertical_extension: float   # Extension vertical (mm) - desde 18.10.6.2(b)(i)
    c: float                    # Profundidad eje neutro usada
    lw: float                   # Longitud del muro
    aci_reference: str


@dataclass
class BoundaryTransverseReinforcement:
    """Refuerzo transversal requerido para elemento de borde."""
    # Requisitos segun Tabla 18.10.6.4(g)
    Ash_sbc_required: float     # Ash/(s*bc) requerido
    rho_s_required: float       # rho_s para espiral/aro circular

    # Espaciamiento maximo segun 18.10.6.4(e)
    spacing_max: float          # Espaciamiento maximo (mm)

    # Espaciamiento hx segun 18.10.6.4(f)
    hx_max: float               # Espaciamiento hx maximo (mm)

    # Inputs usados
    Ag: float                   # Area bruta
    Ach: float                  # Area del nucleo
    fc: float                   # f'c
    fyt: float                  # fy del refuerzo transversal

    aci_reference: str


@dataclass
class BoundaryElementResult:
    """Resultado completo de verificacion de elemento de borde."""
    method: BoundaryElementMethod
    displacement_check: Optional[DisplacementCheckResult]
    stress_check: Optional[StressCheckResult]
    requires_special: bool
    dimensions: Optional[BoundaryElementDimensions]
    transverse_reinforcement: Optional[BoundaryTransverseReinforcement]
    drift_capacity_check: Optional[dict]  # Verificacion 18.10.6.2(b)(iii)
    warnings: List[str]
    aci_reference: str


class BoundaryElementService:
    """
    Servicio de verificacion de elementos de borde segun ACI 318-25.

    Implementa las verificaciones de la seccion 18.10.6 para
    determinar si se requieren elementos de borde especiales
    y sus requisitos de detallado.

    Unidades:
    - Longitudes: mm
    - Esfuerzos: MPa
    - Fuerzas: N o tonf (segun contexto)
    """

    # =========================================================================
    # VERIFICACION POR DESPLAZAMIENTO (18.10.6.2)
    # =========================================================================

    def check_displacement_method(
        self,
        delta_u: float,
        hwcs: float,
        lw: float,
        c: float
    ) -> DisplacementCheckResult:
        """
        Verifica si se requiere elemento de borde por metodo de desplazamiento.

        Segun 18.10.6.2(a):
        1.5 * (delta_u / hwcs) >= lw / (600 * c)

        Donde delta_u / hwcs no debe tomarse menor que 0.005.

        Args:
            delta_u: Desplazamiento de diseno en tope del muro (mm)
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)
            c: Profundidad del eje neutro (mm), mayor valor calculado

        Returns:
            DisplacementCheckResult con resultado de la verificacion
        """
        if hwcs <= 0 or c <= 0:
            return DisplacementCheckResult(
                delta_u=delta_u, hwcs=hwcs, lw=lw, c=c,
                drift_ratio=0, limit=0, check_value=0,
                requires_special=True,  # Conservador
                aci_reference="ACI 318-25 18.10.6.2(a)"
            )

        # Calcular drift ratio (no menor que 0.005)
        drift_ratio = max(delta_u / hwcs, 0.005)

        # Calcular limite
        limit = lw / (600 * c)

        # Verificar si requiere elemento de borde especial
        check_value = 1.5 * drift_ratio
        requires_special = check_value >= limit

        return DisplacementCheckResult(
            delta_u=delta_u,
            hwcs=hwcs,
            lw=lw,
            c=c,
            drift_ratio=round(drift_ratio, 5),
            limit=round(limit, 5),
            check_value=round(check_value, 5),
            requires_special=requires_special,
            aci_reference="ACI 318-25 18.10.6.2(a)"
        )

    # =========================================================================
    # VERIFICACION POR ESFUERZOS (18.10.6.3)
    # =========================================================================

    def check_stress_method(
        self,
        sigma_max: float,
        fc: float
    ) -> StressCheckResult:
        """
        Verifica si se requiere elemento de borde por metodo de esfuerzos.

        Segun 18.10.6.3:
        - Requiere elemento de borde si sigma_max >= 0.2 * f'c
        - Puede discontinuar si sigma < 0.15 * f'c

        Args:
            sigma_max: Esfuerzo maximo de compresion en fibra extrema (MPa)
            fc: Resistencia del hormigon f'c (MPa)

        Returns:
            StressCheckResult con resultado de la verificacion
        """
        limit_require = 0.2 * fc
        limit_discontinue = 0.15 * fc

        requires_special = sigma_max >= limit_require
        can_discontinue = sigma_max < limit_discontinue

        return StressCheckResult(
            sigma_max=sigma_max,
            fc=fc,
            limit_require=limit_require,
            limit_discontinue=limit_discontinue,
            requires_special=requires_special,
            can_discontinue=can_discontinue,
            aci_reference="ACI 318-25 18.10.6.3"
        )

    # =========================================================================
    # DIMENSIONES DEL ELEMENTO DE BORDE (18.10.6.4)
    # =========================================================================

    def calculate_dimensions(
        self,
        c: float,
        lw: float,
        Mu: float,
        Vu: float,
        hu: float,
        delta_u: float = 0,
        hwcs: float = 0
    ) -> BoundaryElementDimensions:
        """
        Calcula las dimensiones requeridas del elemento de borde.

        Segun 18.10.6.4 y 18.10.6.2(b):

        (a) Extension horizontal: mayor de (c - 0.1*lw) y (c/2)
        (b) Ancho minimo: b >= hu/16
        (c) Para c/lw >= 3/8: b >= 12 in (305 mm)

        Para metodo de desplazamiento:
        (b)(ii) Ancho requerido: b >= sqrt(c*lw)/40

        Args:
            c: Profundidad del eje neutro (mm)
            lw: Longitud del muro (mm)
            Mu: Momento ultimo (tonf-m)
            Vu: Cortante ultimo (tonf)
            hu: Altura de piso (mm)
            delta_u: Desplazamiento de diseno (mm) - para metodo desplazamiento
            hwcs: Altura desde seccion critica (mm) - para metodo desplazamiento

        Returns:
            BoundaryElementDimensions con dimensiones calculadas
        """
        # (a) Extension horizontal
        length_h_1 = c - 0.1 * lw
        length_h_2 = c / 2
        length_horizontal = max(length_h_1, length_h_2)

        # (b) Ancho minimo basico
        width_min = hu / 16

        # (c) Para c/lw >= 3/8: b >= 305 mm
        if lw > 0 and (c / lw) >= 0.375:
            width_min = max(width_min, 305.0)

        # Ancho requerido por metodo de desplazamiento (18.10.6.2(b)(ii))
        if delta_u > 0 and c > 0 and lw > 0:
            width_required = math.sqrt(c * lw) / 40
        else:
            width_required = width_min

        # (i) Extension vertical: mayor de lw y Mu/(4*Vu)
        if Vu > 0:
            # Convertir Mu de tonf-m a tonf-mm para unidades consistentes
            Mu_mm = Mu * 1000
            vertical_ext_1 = lw
            vertical_ext_2 = Mu_mm / (4 * Vu)
            vertical_extension = max(vertical_ext_1, vertical_ext_2)
        else:
            vertical_extension = lw

        return BoundaryElementDimensions(
            length_horizontal=round(length_horizontal, 1),
            width_min=round(width_min, 1),
            width_required=round(width_required, 1),
            vertical_extension=round(vertical_extension, 1),
            c=c,
            lw=lw,
            aci_reference="ACI 318-25 18.10.6.4"
        )

    # =========================================================================
    # REFUERZO TRANSVERSAL (TABLA 18.10.6.4(g))
    # =========================================================================

    def calculate_transverse_reinforcement(
        self,
        Ag: float,
        Ach: float,
        fc: float,
        fyt: float,
        b: float
    ) -> BoundaryTransverseReinforcement:
        """
        Calcula el refuerzo transversal requerido para elemento de borde.

        Segun Tabla 18.10.6.4(g):
        - Ash/(s*bc) >= max(0.3*(Ag/Ach-1)*(f'c/fyt), 0.09*(f'c/fyt))
        - rho_s >= max(0.45*(Ag/Ach-1)*(f'c/fyt), 0.12*(f'c/fyt))

        Segun 18.10.6.4(e):
        - Espaciamiento <= 1/3 de dimension menor del elemento de borde

        Segun 18.10.6.4(f):
        - hx <= menor de 14" (356 mm) y (2/3)*b

        Args:
            Ag: Area bruta del elemento de borde (mm2)
            Ach: Area del nucleo confinado (mm2)
            fc: f'c del hormigon (MPa)
            fyt: fy del refuerzo transversal (MPa)
            b: Dimension menor del elemento de borde (mm)

        Returns:
            BoundaryTransverseReinforcement con requisitos
        """
        ratio = Ag / Ach if Ach > 0 else 2.0

        # Ash/(s*bc) - Estribos rectangulares
        expr_a = 0.3 * (ratio - 1) * (fc / fyt)
        expr_b = 0.09 * (fc / fyt)
        Ash_sbc = max(expr_a, expr_b)

        # rho_s - Espiral o aro circular
        expr_c = 0.45 * (ratio - 1) * (fc / fyt)
        expr_d = 0.12 * (fc / fyt)
        rho_s = max(expr_c, expr_d)

        # Espaciamiento maximo
        spacing_max = b / 3

        # Espaciamiento hx maximo
        hx_max = min(356.0, (2/3) * b)

        return BoundaryTransverseReinforcement(
            Ash_sbc_required=round(Ash_sbc, 5),
            rho_s_required=round(rho_s, 5),
            spacing_max=round(spacing_max, 1),
            hx_max=round(hx_max, 1),
            Ag=Ag,
            Ach=Ach,
            fc=fc,
            fyt=fyt,
            aci_reference="ACI 318-25 Tabla 18.10.6.4(g)"
        )

    # =========================================================================
    # ESPACIAMIENTO MAXIMO (TABLA 18.10.6.5(b))
    # =========================================================================

    def max_tie_spacing(
        self,
        steel_grade: SteelGrade,
        db: float,
        near_critical: bool = True
    ) -> float:
        """
        Obtiene espaciamiento maximo de refuerzo transversal en borde.

        Segun Tabla 18.10.6.5(b):

        | Grado | Cerca de seccion critica | Otras ubicaciones |
        |-------|-------------------------|-------------------|
        | 60    | min(6*db, 6")          | min(8*db, 8")     |
        | 80    | min(5*db, 6")          | min(6*db, 6")     |
        | 100   | min(4*db, 6")          | min(6*db, 6")     |

        Args:
            steel_grade: Grado del acero (60, 80, 100)
            db: Diametro de barra longitudinal mas pequena (mm)
            near_critical: True si esta dentro de lw o Mu/(4*Vu)
                          de la seccion critica

        Returns:
            Espaciamiento maximo en mm
        """
        # Convertir pulgadas a mm
        SIX_INCH = 152.4
        EIGHT_INCH = 203.2

        if steel_grade == SteelGrade.GRADE_60:
            if near_critical:
                return min(6 * db, SIX_INCH)
            else:
                return min(8 * db, EIGHT_INCH)

        elif steel_grade == SteelGrade.GRADE_80:
            if near_critical:
                return min(5 * db, SIX_INCH)
            else:
                return min(6 * db, SIX_INCH)

        else:  # GRADE_100
            if near_critical:
                return min(4 * db, SIX_INCH)
            else:
                return min(6 * db, SIX_INCH)

    # =========================================================================
    # CAPACIDAD DE DERIVA (18.10.6.2(b)(iii))
    # =========================================================================

    def check_drift_capacity(
        self,
        lw: float,
        b: float,
        c: float,
        Ve: float,
        fc: float,
        Acv: float,
        delta_u: float,
        hwcs: float
    ) -> dict:
        """
        Verifica capacidad de deriva segun 18.10.6.2(b)(iii).

        delta_c/hwcs >= 1.5 * delta_u/hwcs

        Donde:
        delta_c/hwcs = (1/100) * [4 - 1/50 - (lw/b)*(c/b) - Ve/(8*sqrt(f'c)*Acv)]

        Minimo: delta_c/hwcs >= 0.015

        Args:
            lw: Longitud del muro (mm)
            b: Ancho del elemento de borde (mm)
            c: Profundidad del eje neutro (mm)
            Ve: Cortante de diseno (tonf)
            fc: f'c del hormigon (MPa)
            Acv: Area de corte (mm2)
            delta_u: Desplazamiento de diseno (mm)
            hwcs: Altura desde seccion critica (mm)

        Returns:
            Dict con resultados de la verificacion
        """
        if b <= 0 or hwcs <= 0:
            return {
                "delta_c_hwcs": 0,
                "delta_u_hwcs": 0,
                "limit": 0,
                "is_ok": False,
                "aci_reference": "ACI 318-25 18.10.6.2(b)(iii)"
            }

        # Convertir Ve a N para unidades consistentes
        Ve_N = Ve * 9806.65  # tonf a N

        # Calcular termino de cortante
        # 8 * sqrt(f'c) * Acv en unidades SI
        shear_term = Ve_N / (0.66 * math.sqrt(fc) * Acv) if Acv > 0 else 0

        # Calcular capacidad de deriva
        delta_c_hwcs = (1/100) * (4 - 0.02 - (lw/b) * (c/b) - shear_term)
        delta_c_hwcs = max(delta_c_hwcs, 0.015)

        # Calcular deriva de diseno
        delta_u_hwcs = max(delta_u / hwcs, 0.005)

        # Verificar
        limit = 1.5 * delta_u_hwcs
        is_ok = delta_c_hwcs >= limit

        return {
            "delta_c_hwcs": round(delta_c_hwcs, 5),
            "delta_u_hwcs": round(delta_u_hwcs, 5),
            "limit": round(limit, 5),
            "is_ok": is_ok,
            "aci_reference": "ACI 318-25 18.10.6.2(b)(iii)"
        }

    # =========================================================================
    # VERIFICACION COMPLETA
    # =========================================================================

    def verify_boundary_element(
        self,
        method: BoundaryElementMethod,
        lw: float,
        c: float,
        hu: float,
        fc: float,
        fyt: float,
        Ag: float,
        Ach: float,
        b: float,
        # Para metodo de desplazamiento
        delta_u: float = 0,
        hwcs: float = 0,
        Mu: float = 0,
        Vu: float = 0,
        Ve: float = 0,
        Acv: float = 0,
        # Para metodo de esfuerzos
        sigma_max: float = 0
    ) -> BoundaryElementResult:
        """
        Realiza verificacion completa de elemento de borde.

        Args:
            method: Metodo de verificacion (desplazamiento o esfuerzos)
            lw: Longitud del muro (mm)
            c: Profundidad del eje neutro (mm)
            hu: Altura de piso (mm)
            fc: f'c del hormigon (MPa)
            fyt: fy del refuerzo transversal (MPa)
            Ag: Area bruta del elemento de borde (mm2)
            Ach: Area del nucleo confinado (mm2)
            b: Dimension menor del elemento de borde propuesto (mm)

            # Para metodo de desplazamiento:
            delta_u: Desplazamiento de diseno (mm)
            hwcs: Altura desde seccion critica (mm)
            Mu: Momento ultimo (tonf-m)
            Vu: Cortante ultimo (tonf)
            Ve: Cortante de diseno (tonf)
            Acv: Area de corte (mm2)

            # Para metodo de esfuerzos:
            sigma_max: Esfuerzo maximo de compresion (MPa)

        Returns:
            BoundaryElementResult con verificacion completa
        """
        warnings = []
        displacement_check = None
        stress_check = None
        dimensions = None
        transverse = None
        drift_check = None
        requires_special = False

        if method == BoundaryElementMethod.DISPLACEMENT:
            # Verificar por metodo de desplazamiento
            displacement_check = self.check_displacement_method(
                delta_u, hwcs, lw, c
            )
            requires_special = displacement_check.requires_special

            if requires_special:
                # Calcular dimensiones requeridas
                dimensions = self.calculate_dimensions(
                    c, lw, Mu, Vu, hu, delta_u, hwcs
                )

                # Verificar ancho propuesto
                if b < dimensions.width_required:
                    warnings.append(
                        f"Ancho propuesto {b:.0f}mm < {dimensions.width_required:.0f}mm requerido"
                    )

                # Verificar capacidad de deriva
                if Ve > 0 and Acv > 0:
                    drift_check = self.check_drift_capacity(
                        lw, b, c, Ve, fc, Acv, delta_u, hwcs
                    )
                    if not drift_check["is_ok"]:
                        warnings.append(
                            f"Capacidad de deriva {drift_check['delta_c_hwcs']:.4f} < "
                            f"{drift_check['limit']:.4f} requerido"
                        )

        else:  # STRESS method
            stress_check = self.check_stress_method(sigma_max, fc)
            requires_special = stress_check.requires_special

            if requires_special:
                dimensions = self.calculate_dimensions(
                    c, lw, Mu, Vu, hu
                )

        # Si requiere elemento de borde especial, calcular refuerzo
        if requires_special and Ag > 0 and Ach > 0:
            transverse = self.calculate_transverse_reinforcement(
                Ag, Ach, fc, fyt, b
            )

        return BoundaryElementResult(
            method=method,
            displacement_check=displacement_check,
            stress_check=stress_check,
            requires_special=requires_special,
            dimensions=dimensions,
            transverse_reinforcement=transverse,
            drift_capacity_check=drift_check,
            warnings=warnings,
            aci_reference="ACI 318-25 18.10.6"
        )

    # =========================================================================
    # TERMINACION DE REFUERZO HORIZONTAL (18.10.6.5)
    # =========================================================================

    def check_horizontal_reinforcement_termination(
        self,
        omega_v: float,
        Omega_v: float,
        Vu: float,
        lambda_factor: float,
        fc: float,
        Acv: float
    ) -> dict:
        """
        Verifica requisitos de terminacion del refuerzo horizontal.

        Segun 18.10.6.5(a):
        - Si omega_v * Omega_v * Vu < lambda * sqrt(f'c) * Acv:
          No requiere gancho
        - Caso contrario: Gancho estandar o estribos en U

        Args:
            omega_v: Factor de amplificacion dinamica
            Omega_v: Factor de sobrerresistencia
            Vu: Cortante ultimo (tonf)
            lambda_factor: Factor lambda para concreto liviano
            fc: f'c del hormigon (MPa)
            Acv: Area de corte (mm2)

        Returns:
            Dict con resultado de verificacion
        """
        # Calcular cortante amplificado
        Vu_amp = omega_v * Omega_v * Vu

        # Calcular umbral (convertir a tonf)
        N_TO_TONF = 9806.65
        threshold = lambda_factor * math.sqrt(fc) * Acv / N_TO_TONF

        requires_hook = Vu_amp >= threshold

        return {
            "Vu_amplified": round(Vu_amp, 2),
            "threshold": round(threshold, 2),
            "requires_hook": requires_hook,
            "hook_type": "Gancho estandar o estribos en U" if requires_hook else "No requerido",
            "aci_reference": "ACI 318-25 18.10.6.5(a)"
        }
