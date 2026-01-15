# app/domain/chapter18/coupling_beams/service.py
"""
Servicio de diseño de vigas de acoplamiento ACI 318-25 §18.10.7.

Orquesta:
- Clasificación por ln/h
- Resistencia al cortante diagonal
- Confinamiento de diagonales
"""
import math
from typing import Optional, List

from ...constants import DCR_MAX_FINITE
from ...constants.materials import SteelGrade
from ...constants.units import N_TO_TONF
from ..results import (
    CouplingBeamType,
    ReinforcementType,
    ConfinementOption,
    CouplingBeamClassification,
    DiagonalShearResult,
    DiagonalConfinementResult,
    CouplingBeamDesignResult,
)
from .classification import classify_coupling_beam
from .diagonal import (
    calculate_diagonal_shear_strength,
    required_diagonal_area,
    calculate_diagonal_angle,
)
from .confinement import (
    calculate_diagonal_confinement,
    check_shear_redistribution,
    check_penetration_limits,
)


class CouplingBeamService:
    """
    Servicio de diseño de vigas de acoplamiento según ACI 318-25.

    Proporciona clasificación, diseño de refuerzo diagonal,
    y verificación de resistencia al cortante.

    Unidades:
    - Longitudes: mm
    - Áreas: mm2
    - Esfuerzos: MPa
    - Fuerzas: tonf
    """

    # =========================================================================
    # CLASIFICACIÓN DE VIGA (18.10.7.1-18.10.7.3)
    # =========================================================================

    def classify_coupling_beam(
        self,
        ln: float,
        h: float,
        bw: float,
        Vu: float,
        fc: float,
        lambda_factor: float = 1.0
    ) -> CouplingBeamClassification:
        """Clasifica la viga según su relación ln/h."""
        return classify_coupling_beam(ln, h, bw, Vu, fc, lambda_factor)

    # =========================================================================
    # RESISTENCIA AL CORTANTE DIAGONAL (18.10.7.4)
    # =========================================================================

    def calculate_diagonal_shear_strength(
        self,
        Avd: float,
        fy: float,
        alpha_deg: float,
        fc: float,
        Acw: float
    ) -> DiagonalShearResult:
        """Calcula la resistencia al cortante con refuerzo diagonal."""
        return calculate_diagonal_shear_strength(Avd, fy, alpha_deg, fc, Acw)

    def required_diagonal_area(
        self,
        Vu: float,
        fy: float,
        alpha_deg: float,
        phi: float = 0.75
    ) -> float:
        """Calcula el área de refuerzo diagonal requerida."""
        return required_diagonal_area(Vu, fy, alpha_deg, phi)

    def calculate_diagonal_angle(
        self,
        ln: float,
        h: float,
        cover: float = 40
    ) -> float:
        """Calcula el ángulo de las diagonales."""
        return calculate_diagonal_angle(ln, h, cover)

    # =========================================================================
    # CONFINAMIENTO DE DIAGONALES (18.10.7.4(c) y (d))
    # =========================================================================

    def calculate_diagonal_confinement(
        self,
        bw: float,
        Ag: float,
        Ach: float,
        fc: float,
        fyt: float,
        steel_grade: SteelGrade,
        db_diagonal: float,
        option: ConfinementOption = ConfinementOption.INDIVIDUAL
    ) -> DiagonalConfinementResult:
        """Calcula requisitos de confinamiento para diagonales."""
        return calculate_diagonal_confinement(
            bw, Ag, Ach, fc, fyt, steel_grade, db_diagonal, option
        )

    # =========================================================================
    # REDISTRIBUCIÓN DE CORTANTE (18.10.7.5)
    # =========================================================================

    def check_shear_redistribution(
        self,
        beams_Ve: List[float],
        beams_phi_Vn: List[float],
        beams_ln_h: List[float]
    ) -> dict:
        """Verifica redistribución de cortante entre vigas."""
        return check_shear_redistribution(beams_Ve, beams_phi_Vn, beams_ln_h)

    # =========================================================================
    # PENETRACIONES (18.10.7.6)
    # =========================================================================

    def check_penetration_limits(
        self,
        h: float,
        diameter: float,
        dist_to_diagonal: float,
        dist_to_ends: float,
        dist_to_edges: float,
        dist_between: float = 0
    ) -> dict:
        """Verifica límites de penetraciones en vigas con diagonal."""
        return check_penetration_limits(
            h, diameter, dist_to_diagonal, dist_to_ends, dist_to_edges, dist_between
        )

    # =========================================================================
    # DISEÑO COMPLETO
    # =========================================================================

    def design_coupling_beam(
        self,
        ln: float,
        h: float,
        bw: float,
        Vu: float,
        fc: float,
        fy_diagonal: float,
        fyt: float,
        lambda_factor: float = 1.0,
        cover: float = 40,
        steel_grade: SteelGrade = SteelGrade.GRADE_60,
        confinement_option: ConfinementOption = ConfinementOption.INDIVIDUAL,
        use_diagonal: bool = None
    ) -> CouplingBeamDesignResult:
        """
        Realiza diseño completo de viga de acoplamiento.

        Args:
            ln: Claro libre (mm)
            h: Peralte (mm)
            bw: Ancho (mm)
            Vu: Cortante último (tonf)
            fc: f'c del hormigón (MPa)
            fy_diagonal: Fluencia del refuerzo diagonal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            lambda_factor: Factor para concreto liviano
            cover: Recubrimiento (mm)
            steel_grade: Grado del acero diagonal
            confinement_option: Opción de confinamiento
            use_diagonal: Forzar uso de diagonal (None = automático)

        Returns:
            CouplingBeamDesignResult con diseño completo
        """
        warnings = []

        # Clasificar la viga
        classification = self.classify_coupling_beam(
            ln, h, bw, Vu, fc, lambda_factor
        )

        # Determinar tipo de refuerzo
        if use_diagonal is not None:
            reinf_type = ReinforcementType.DIAGONAL if use_diagonal else ReinforcementType.LONGITUDINAL
        elif classification.beam_type == CouplingBeamType.SHORT_HIGH_SHEAR:
            reinf_type = ReinforcementType.DIAGONAL
        elif classification.beam_type == CouplingBeamType.LONG:
            reinf_type = ReinforcementType.LONGITUDINAL
        else:
            # Intermedio - preferir diagonal para mejor ductilidad
            reinf_type = ReinforcementType.DIAGONAL

        shear_result = None
        confinement = None

        if reinf_type == ReinforcementType.DIAGONAL:
            # Calcular ángulo de diagonales
            alpha = self.calculate_diagonal_angle(ln, h, cover)

            # Calcular área requerida
            Avd_req = self.required_diagonal_area(Vu, fy_diagonal, alpha)

            # Verificar resistencia (con área propuesta = área requerida)
            Acw = ln * bw
            shear_result = self.calculate_diagonal_shear_strength(
                Avd_req, fy_diagonal, alpha, fc, Acw
            )

            # Verificar límite máximo
            if shear_result.Vn_calc > shear_result.Vn_max:
                warnings.append(
                    f"Cortante diagonal {shear_result.Vn_calc:.1f} tonf "
                    f"excede límite {shear_result.Vn_max:.1f} tonf"
                )

            # Calcular confinamiento
            Ag = h * bw
            # Asumir Ach = 0.8 * Ag para estimación
            Ach = 0.8 * Ag
            db_diagonal = 25.0  # Asumir diámetro típico

            confinement = self.calculate_diagonal_confinement(
                bw, Ag, Ach, fc, fyt, steel_grade, db_diagonal,
                confinement_option
            )

            phi_Vn = shear_result.phi_Vn
        else:
            # Refuerzo longitudinal - calcular capacidad como viga
            # Vn = Acv * (alpha_c * lambda * sqrt(f'c) + rho_t * fyt)
            # Usar estimación conservadora
            Acv = ln * bw
            # Coeficiente alpha_c para ln/h >= 4: usar 0.17
            alpha_c = 0.17 if classification.ln_h_ratio >= 2.0 else 0.25
            rho_t = 0.0025  # Asumir mínimo

            Vn_N = (alpha_c * lambda_factor * math.sqrt(fc) + rho_t * fyt) * Acv
            Vn = Vn_N / N_TO_TONF
            phi_Vn = 0.75 * Vn

            warnings.append(
                "Refuerzo longitudinal seleccionado - verificar detallado según 18.6"
            )

        # Verificar demanda vs capacidad
        dcr = Vu / phi_Vn if phi_Vn > 0 else DCR_MAX_FINITE
        is_ok = dcr <= 1.0

        if not is_ok:
            warnings.append(
                f"DCR = {dcr:.2f} > 1.0: Aumentar refuerzo diagonal o "
                "revisar dimensiones"
            )

        return CouplingBeamDesignResult(
            classification=classification,
            reinforcement_type=reinf_type,
            shear_result=shear_result,
            confinement=confinement,
            Vu=Vu,
            phi_Vn=round(phi_Vn, 2),
            dcr=round(dcr, 3),
            is_ok=is_ok,
            warnings=warnings,
            aci_reference="ACI 318-25 18.10.7"
        )
