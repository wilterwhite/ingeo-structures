# app/domain/chapter18/boundary_elements/service.py
"""
Servicio de verificación de elementos de borde ACI 318-25 §18.10.6.

Orquesta:
- Método de desplazamiento (18.10.6.2)
- Método de esfuerzos (18.10.6.3)
- Dimensiones (18.10.6.4)
- Refuerzo transversal (Tabla 18.10.6.4(g))
"""
from typing import Optional

from ...constants.materials import SteelGrade, calculate_beta1
from ..results import (
    BoundaryElementMethod,
    DisplacementCheckResult,
    StressCheckResult,
    BoundaryElementDimensions,
    BoundaryTransverseReinforcement,
    BoundaryElementResult,
)
from .displacement import check_displacement_method, check_drift_capacity
from .stress import check_stress_method
from .dimensions import calculate_dimensions
from .confinement import (
    calculate_transverse_reinforcement,
    max_tie_spacing,
    check_horizontal_reinforcement_termination,
)


class BoundaryElementService:
    """
    Servicio de verificación de elementos de borde según ACI 318-25.

    Implementa las verificaciones de la sección 18.10.6 para
    determinar si se requieren elementos de borde especiales
    y sus requisitos de detallado.

    Unidades:
    - Longitudes: mm
    - Esfuerzos: MPa
    - Fuerzas: N o tonf (según contexto)
    """

    # =========================================================================
    # VERIFICACIÓN POR DESPLAZAMIENTO (18.10.6.2)
    # =========================================================================

    def check_displacement_method(
        self,
        delta_u: float,
        hwcs: float,
        lw: float,
        c: float
    ) -> DisplacementCheckResult:
        """Verifica por método de desplazamiento."""
        return check_displacement_method(delta_u, hwcs, lw, c)

    # =========================================================================
    # VERIFICACIÓN POR ESFUERZOS (18.10.6.3)
    # =========================================================================

    def check_stress_method(
        self,
        sigma_max: float,
        fc: float
    ) -> StressCheckResult:
        """Verifica por método de esfuerzos."""
        return check_stress_method(sigma_max, fc)

    # =========================================================================
    # CÁLCULO DE PROFUNDIDAD DEL EJE NEUTRO
    # =========================================================================

    def calculate_neutral_axis_depth(
        self,
        lw: float,
        tw: float,
        fc: float,
        Pu: float,
        As: float = 0,
        fy: float = 420
    ) -> float:
        """
        Calcula profundidad del eje neutro usando equilibrio de fuerzas.

        Fórmula según ACI 318-25:
        0.85×fc×β₁×c×tw = As×fy + Pu

        Resolviendo para c:
        c = (As×fy + Pu) / (0.85×fc×β₁×tw)

        Args:
            lw: Longitud del muro (mm)
            tw: Espesor del muro (mm)
            fc: f'c del hormigón (MPa)
            Pu: Carga axial última (N, positivo = compresión)
            As: Área de acero en tracción (mm²)
            fy: fy del refuerzo longitudinal (MPa)

        Returns:
            Profundidad del eje neutro c (mm), limitado a [0, lw]
        """
        beta1 = calculate_beta1(fc)

        # Numerador: fuerza total (acero + carga axial)
        numerator = As * fy + Pu

        # Denominador: capacidad del bloque de compresión
        denominator = 0.85 * fc * beta1 * tw

        if denominator <= 0:
            return lw / 2  # Fallback: mitad de la longitud

        c = numerator / denominator
        return max(0, min(c, lw))  # Limitar a [0, lw]

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
        """Calcula dimensiones requeridas."""
        return calculate_dimensions(c, lw, Mu, Vu, hu, delta_u, hwcs)

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
        """Calcula refuerzo transversal requerido."""
        return calculate_transverse_reinforcement(Ag, Ach, fc, fyt, b)

    # =========================================================================
    # ESPACIAMIENTO MÁXIMO (TABLA 18.10.6.5(b))
    # =========================================================================

    def max_tie_spacing(
        self,
        steel_grade: SteelGrade,
        db: float,
        near_critical: bool = True
    ) -> float:
        """Obtiene espaciamiento máximo según grado de acero."""
        return max_tie_spacing(steel_grade, db, near_critical)

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
        """Verifica capacidad de deriva."""
        return check_drift_capacity(lw, b, c, Ve, fc, Acv, delta_u, hwcs)

    # =========================================================================
    # VERIFICACIÓN COMPLETA
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
        # Para método de desplazamiento
        delta_u: float = 0,
        hwcs: float = 0,
        Mu: float = 0,
        Vu: float = 0,
        Ve: float = 0,
        Acv: float = 0,
        # Para método de esfuerzos
        sigma_max: float = 0
    ) -> BoundaryElementResult:
        """
        Realiza verificación completa de elemento de borde.

        Args:
            method: Método de verificación (desplazamiento o esfuerzos)
            lw: Longitud del muro (mm)
            c: Profundidad del eje neutro (mm)
            hu: Altura de piso (mm)
            fc: f'c del hormigón (MPa)
            fyt: fy del refuerzo transversal (MPa)
            Ag: Área bruta del elemento de borde (mm2)
            Ach: Área del núcleo confinado (mm2)
            b: Dimensión menor del elemento de borde propuesto (mm)

            # Para método de desplazamiento:
            delta_u: Desplazamiento de diseño (mm)
            hwcs: Altura desde sección crítica (mm)
            Mu: Momento último (tonf-m)
            Vu: Cortante último (tonf)
            Ve: Cortante de diseño (tonf)
            Acv: Área de corte (mm2)

            # Para método de esfuerzos:
            sigma_max: Esfuerzo máximo de compresión (MPa)

        Returns:
            BoundaryElementResult con verificación completa
        """
        warnings = []
        displacement_result = None
        stress_result = None
        dimensions = None
        transverse = None
        drift_check = None
        requires_special = False

        if method == BoundaryElementMethod.DISPLACEMENT:
            # Verificar por método de desplazamiento
            displacement_result = self.check_displacement_method(
                delta_u, hwcs, lw, c
            )
            requires_special = displacement_result.requires_special

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
            stress_result = self.check_stress_method(sigma_max, fc)
            requires_special = stress_result.requires_special

            if requires_special:
                dimensions = self.calculate_dimensions(
                    c, lw, Mu, Vu, hu
                )

                # Verificar ancho propuesto (mismo check que método desplazamiento)
                if b < dimensions.width_required:
                    warnings.append(
                        f"Ancho propuesto {b:.0f}mm < {dimensions.width_required:.0f}mm requerido"
                    )

        # Si requiere elemento de borde especial, calcular refuerzo
        if requires_special and Ag > 0 and Ach > 0:
            transverse = self.calculate_transverse_reinforcement(
                Ag, Ach, fc, fyt, b
            )

        return BoundaryElementResult(
            method=method,
            displacement_check=displacement_result,
            stress_check=stress_result,
            requires_special=requires_special,
            dimensions=dimensions,
            transverse_reinforcement=transverse,
            drift_capacity_check=drift_check,
            warnings=warnings,
            aci_reference="ACI 318-25 18.10.6"
        )

    # =========================================================================
    # TERMINACIÓN DE REFUERZO HORIZONTAL (18.10.6.5)
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
        """Verifica requisitos de terminación del refuerzo horizontal."""
        return check_horizontal_reinforcement_termination(
            omega_v, Omega_v, Vu, lambda_factor, fc, Acv
        )
