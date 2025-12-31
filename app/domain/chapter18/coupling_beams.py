# app/domain/chapter18/coupling_beams.py
"""
Verificacion de vigas de acoplamiento segun ACI 318-25 Seccion 18.10.7.

Implementa:
- Clasificacion por relacion de aspecto (ln/h)
- Refuerzo diagonal para cortante alto
- Confinamiento de diagonales
- Resistencia al cortante
- Redistribucion de cortante

Referencias ACI 318-25:
- 18.10.7.1: Vigas con ln/h >= 4 (como viga de portico)
- 18.10.7.2: Vigas con ln/h < 2 y Vu alto (diagonal obligatorio)
- 18.10.7.3: Vigas intermedias (2 <= ln/h < 4)
- 18.10.7.4: Vigas con refuerzo diagonal
- Tabla 18.10.7.4: Espaciamiento de refuerzo transversal
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import math

from ..constants.materials import SteelGrade
from ..constants.shear import PHI_SHEAR
from ..constants.units import N_TO_TONF


class CouplingBeamType(Enum):
    """Tipo de viga de acoplamiento segun relacion ln/h."""
    LONG = "long"           # ln/h >= 4, como viga de portico
    SHORT_HIGH_SHEAR = "short_high_shear"  # ln/h < 2 con Vu alto, diagonal obligatorio
    INTERMEDIATE = "intermediate"  # 2 <= ln/h < 4, diagonal o longitudinal


class ReinforcementType(Enum):
    """Tipo de refuerzo para viga de acoplamiento."""
    LONGITUDINAL = "longitudinal"  # Refuerzo convencional
    DIAGONAL = "diagonal"           # Refuerzo diagonal


class ConfinementOption(Enum):
    """Opcion de confinamiento para diagonales."""
    INDIVIDUAL = "individual"  # Opcion (c) - Confinamiento de diagonales individuales
    FULL_SECTION = "full_section"  # Opcion (d) - Confinamiento de seccion completa


@dataclass
class CouplingBeamClassification:
    """Clasificacion de viga de acoplamiento."""
    ln: float               # Claro libre (mm)
    h: float                # Peralte de la viga (mm)
    ln_h_ratio: float       # Relacion ln/h
    beam_type: CouplingBeamType
    Vu: float               # Cortante ultimo (tonf)
    shear_threshold: float  # Umbral 4*lambda*sqrt(f'c)*Acw (tonf)
    reinforcement_options: List[ReinforcementType]
    aci_reference: str


@dataclass
class DiagonalShearResult:
    """Resultado de resistencia al cortante con refuerzo diagonal."""
    Avd: float              # Area de refuerzo en cada grupo diagonal (mm2)
    fy: float               # Fluencia del acero (MPa)
    alpha_deg: float        # Angulo de diagonales (grados)
    Vn_calc: float          # Vn calculado (tonf)
    Vn_max: float           # Vn maximo (tonf)
    Vn: float               # Vn final (tonf)
    phi_Vn: float           # Resistencia de diseno (tonf)
    aci_reference: str


@dataclass
class DiagonalConfinementResult:
    """Requisitos de confinamiento para diagonales."""
    confinement_option: ConfinementOption
    # Requisitos de Ash
    Ash_required: float      # Ash requerido (mm2)
    Ash_sbc_required: float  # Ash/(s*bc) requerido
    # Espaciamiento
    spacing_max: float       # Espaciamiento maximo (mm)
    spacing_perpendicular: float  # Espaciamiento perpendicular (mm)
    # Dimensiones de nucleo (opcion individual)
    core_min_parallel: float     # Dimension minima paralela a bw
    core_min_other: float        # Dimension minima otros lados
    # Refuerzo perimetral adicional (opcion individual)
    rho_perimeter: float         # Cuantia perimetral
    perimeter_spacing: float     # Espaciamiento perimetral
    aci_reference: str


@dataclass
class CouplingBeamDesignResult:
    """Resultado completo del diseno de viga de acoplamiento."""
    classification: CouplingBeamClassification
    reinforcement_type: ReinforcementType
    shear_result: Optional[DiagonalShearResult]
    confinement: Optional[DiagonalConfinementResult]
    # Verificacion de demanda
    Vu: float               # Demanda (tonf)
    phi_Vn: float           # Capacidad (tonf)
    dcr: float              # Demand/Capacity ratio
    is_ok: bool
    warnings: List[str]
    aci_reference: str


class CouplingBeamService:
    """
    Servicio de diseno de vigas de acoplamiento segun ACI 318-25.

    Proporciona clasificacion, diseno de refuerzo diagonal,
    y verificacion de resistencia al cortante.

    Unidades:
    - Longitudes: mm
    - Areas: mm2
    - Esfuerzos: MPa
    - Fuerzas: tonf
    """

    # =========================================================================
    # CLASIFICACION DE VIGA (18.10.7.1-18.10.7.3)
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
        """
        Clasifica la viga de acoplamiento segun su relacion ln/h.

        Segun 18.10.7.1-18.10.7.3:
        - ln/h >= 4: Como viga de portico (18.6)
        - ln/h < 2 con Vu >= 4*lambda*sqrt(f'c)*Acw: Diagonal obligatorio
        - 2 <= ln/h < 4: Diagonal o longitudinal

        Args:
            ln: Claro libre de la viga (mm)
            h: Peralte de la viga (mm)
            bw: Ancho de la viga (mm)
            Vu: Cortante ultimo (tonf)
            fc: f'c del hormigon (MPa)
            lambda_factor: Factor para concreto liviano

        Returns:
            CouplingBeamClassification con tipo y opciones
        """
        ratio = ln / h if h > 0 else 0

        # Calcular umbral de cortante alto
        # 4 * lambda * sqrt(f'c) * Acw
        Acw = ln * bw  # Area de corte
        # Coeficiente SI: 4 -> 0.33 aproximadamente
        shear_threshold = 0.33 * lambda_factor * math.sqrt(fc) * Acw / N_TO_TONF

        if ratio >= 4.0:
            beam_type = CouplingBeamType.LONG
            options = [ReinforcementType.LONGITUDINAL]
        elif ratio < 2.0 and Vu >= shear_threshold:
            beam_type = CouplingBeamType.SHORT_HIGH_SHEAR
            options = [ReinforcementType.DIAGONAL]
        else:
            beam_type = CouplingBeamType.INTERMEDIATE
            options = [ReinforcementType.DIAGONAL, ReinforcementType.LONGITUDINAL]

        return CouplingBeamClassification(
            ln=ln,
            h=h,
            ln_h_ratio=round(ratio, 2),
            beam_type=beam_type,
            Vu=Vu,
            shear_threshold=round(shear_threshold, 2),
            reinforcement_options=options,
            aci_reference="ACI 318-25 18.10.7.1-18.10.7.3"
        )

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
        """
        Calcula la resistencia al cortante con refuerzo diagonal.

        Segun Ec. 18.10.7.4:
        Vn = 2 * Avd * fy * sin(alpha) <= 10*sqrt(f'c)*Acw

        Args:
            Avd: Area total de refuerzo en cada grupo diagonal (mm2)
            fy: Fluencia del acero (MPa)
            alpha_deg: Angulo entre diagonales y eje longitudinal (grados)
            fc: f'c del hormigon (MPa)
            Acw: Area de la seccion (mm2)

        Returns:
            DiagonalShearResult con resistencia calculada
        """
        # Convertir angulo a radianes
        alpha_rad = math.radians(alpha_deg)

        # Calcular Vn
        # Unidades: mm2 * MPa = N
        Vn_calc_N = 2 * Avd * fy * math.sin(alpha_rad)

        # Limite maximo
        # 10 * sqrt(f'c) * Acw en unidades SI: 0.83 * sqrt(f'c) * Acw
        Vn_max_N = 0.83 * math.sqrt(fc) * Acw

        # Vn final
        Vn_N = min(Vn_calc_N, Vn_max_N)

        # Convertir a tonf
        Vn_calc = Vn_calc_N / N_TO_TONF
        Vn_max = Vn_max_N / N_TO_TONF
        Vn = Vn_N / N_TO_TONF

        return DiagonalShearResult(
            Avd=Avd,
            fy=fy,
            alpha_deg=alpha_deg,
            Vn_calc=round(Vn_calc, 2),
            Vn_max=round(Vn_max, 2),
            Vn=round(Vn, 2),
            phi_Vn=round(PHI_SHEAR * Vn, 2),
            aci_reference="ACI 318-25 Ec. 18.10.7.4"
        )

    def required_diagonal_area(
        self,
        Vu: float,
        fy: float,
        alpha_deg: float,
        phi: float = 0.75
    ) -> float:
        """
        Calcula el area de refuerzo diagonal requerida.

        De Ec. 18.10.7.4:
        Avd = Vu / (phi * 2 * fy * sin(alpha))

        Args:
            Vu: Demanda de cortante (tonf)
            fy: Fluencia del acero (MPa)
            alpha_deg: Angulo de diagonales (grados)
            phi: Factor de reduccion (default 0.75)

        Returns:
            Area de refuerzo diagonal requerida en cada grupo (mm2)
        """
        # Convertir Vu a N
        Vu_N = Vu * 9806.65

        alpha_rad = math.radians(alpha_deg)
        denominator = phi * 2 * fy * math.sin(alpha_rad)

        if denominator <= 0:
            return float('inf')

        Avd = Vu_N / denominator
        return round(Avd, 1)

    def calculate_diagonal_angle(
        self,
        ln: float,
        h: float,
        cover: float = 40
    ) -> float:
        """
        Calcula el angulo de las diagonales.

        El angulo tipico es aproximadamente:
        alpha = arctan((h - 2*cover) / ln)

        Args:
            ln: Claro libre (mm)
            h: Peralte de la viga (mm)
            cover: Recubrimiento (mm)

        Returns:
            Angulo en grados
        """
        if ln <= 0:
            return 45.0

        vertical = h - 2 * cover
        alpha_rad = math.atan(vertical / ln)
        return round(math.degrees(alpha_rad), 1)

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
        """
        Calcula requisitos de confinamiento para diagonales.

        Opcion (c) - Confinamiento individual:
        - Dimension minima nucleo >= bw/2 paralelo a bw
        - Dimension minima nucleo >= bw/5 otros lados
        - Ash >= max(0.09*s*bc*f'c/fyt, 0.3*s*bc*(Ag/Ach-1)*f'c/fyt)
        - Espaciamiento perpendicular <= 14"
        - Refuerzo perimetral >= 0.002*bw*s

        Opcion (d) - Seccion completa:
        - Ash igual que opcion (c)
        - Espaciamiento vertical/horizontal <= 8"
        - Cada barra soportada

        Args:
            bw: Ancho de la viga (mm)
            Ag: Area bruta (mm2)
            Ach: Area del nucleo (mm2)
            fc: f'c del hormigon (MPa)
            fyt: fy del refuerzo transversal (MPa)
            steel_grade: Grado del acero diagonal
            db_diagonal: Diametro de barra diagonal (mm)
            option: Opcion de confinamiento

        Returns:
            DiagonalConfinementResult con requisitos
        """
        # Ash/(s*bc) requerido
        ratio = Ag / Ach if Ach > 0 else 2.0
        expr_i = 0.09 * (fc / fyt)
        expr_ii = 0.3 * (ratio - 1) * (fc / fyt)
        Ash_sbc = max(expr_i, expr_ii)

        # Espaciamiento maximo segun Tabla 18.10.7.4
        if steel_grade == SteelGrade.GRADE_60:
            spacing_max = min(6 * db_diagonal, 152.4)  # 6"
        elif steel_grade == SteelGrade.GRADE_80:
            spacing_max = min(5 * db_diagonal, 152.4)
        else:  # GRADE_100
            spacing_max = min(4 * db_diagonal, 152.4)

        if option == ConfinementOption.INDIVIDUAL:
            # Dimensiones de nucleo
            core_parallel = bw / 2
            core_other = bw / 5

            # Espaciamiento perpendicular
            spacing_perp = 355.6  # 14"

            # Refuerzo perimetral
            rho_perimeter = 0.002
            perimeter_spacing = 304.8  # 12"

        else:  # FULL_SECTION
            core_parallel = 0
            core_other = 0
            spacing_perp = 203.2  # 8"
            rho_perimeter = 0
            perimeter_spacing = 0

        # Ash requerido (ejemplo con s = spacing_max, bc = 150mm tipico)
        bc_example = 150.0
        Ash_required = Ash_sbc * spacing_max * bc_example

        return DiagonalConfinementResult(
            confinement_option=option,
            Ash_required=round(Ash_required, 1),
            Ash_sbc_required=round(Ash_sbc, 5),
            spacing_max=round(spacing_max, 1),
            spacing_perpendicular=round(spacing_perp, 1),
            core_min_parallel=round(core_parallel, 1),
            core_min_other=round(core_other, 1),
            rho_perimeter=rho_perimeter,
            perimeter_spacing=perimeter_spacing,
            aci_reference="ACI 318-25 18.10.7.4(c)-(d)"
        )

    # =========================================================================
    # REDISTRIBUCION DE CORTANTE (18.10.7.5)
    # =========================================================================

    def check_shear_redistribution(
        self,
        beams_Ve: List[float],
        beams_phi_Vn: List[float],
        beams_ln_h: List[float]
    ) -> dict:
        """
        Verifica redistribucion de cortante entre vigas de acoplamiento.

        Segun 18.10.7.5:
        - Permitido si vigas alineadas verticalmente
        - ln/h >= 2
        - Redistribucion maxima: 20%
        - Sum(phi*Vn) >= Sum(Ve)

        Args:
            beams_Ve: Lista de cortantes de diseno (tonf)
            beams_phi_Vn: Lista de capacidades (tonf)
            beams_ln_h: Lista de relaciones ln/h

        Returns:
            Dict con resultado de verificacion
        """
        # Verificar que todas las vigas tengan ln/h >= 2
        all_eligible = all(r >= 2.0 for r in beams_ln_h)

        # Verificar capacidad total
        sum_Ve = sum(beams_Ve)
        sum_phi_Vn = sum(beams_phi_Vn)
        capacity_ok = sum_phi_Vn >= sum_Ve

        # Calcular redistribucion maxima permitida
        max_redistribution = [0.2 * Ve for Ve in beams_Ve]

        return {
            "eligible": all_eligible,
            "sum_Ve": round(sum_Ve, 2),
            "sum_phi_Vn": round(sum_phi_Vn, 2),
            "capacity_ok": capacity_ok,
            "max_redistribution": [round(r, 2) for r in max_redistribution],
            "aci_reference": "ACI 318-25 18.10.7.5"
        }

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
        """
        Verifica limites de penetraciones en vigas con diagonal.

        Segun 18.10.7.6:
        - Maximo 2 penetraciones
        - Cilindtricas horizontales
        - Diametro <= max(h/6, 6")
        - Distancia a diagonales >= 2"
        - Distancia a extremos >= h/4
        - Distancia a bordes sup/inf >= 4"
        - Distancia entre penetraciones >= diametro mayor

        Args:
            h: Peralte de la viga (mm)
            diameter: Diametro de penetracion (mm)
            dist_to_diagonal: Distancia libre a diagonales (mm)
            dist_to_ends: Distancia libre a extremos (mm)
            dist_to_edges: Distancia libre a bordes (mm)
            dist_between: Distancia entre penetraciones (mm)

        Returns:
            Dict con verificacion de cada limite
        """
        # Limites en mm
        SIX_INCH = 152.4
        TWO_INCH = 50.8
        FOUR_INCH = 101.6

        # Diametro maximo
        diam_max = max(h / 6, SIX_INCH)
        diam_ok = diameter <= diam_max

        # Distancia a diagonales
        dist_diag_ok = dist_to_diagonal >= TWO_INCH

        # Distancia a extremos
        dist_ends_min = h / 4
        dist_ends_ok = dist_to_ends >= dist_ends_min

        # Distancia a bordes
        dist_edges_ok = dist_to_edges >= FOUR_INCH

        # Distancia entre penetraciones
        dist_between_ok = dist_between >= diameter if dist_between > 0 else True

        all_ok = all([diam_ok, dist_diag_ok, dist_ends_ok,
                      dist_edges_ok, dist_between_ok])

        return {
            "diameter_ok": diam_ok,
            "diameter_max": round(diam_max, 1),
            "dist_to_diagonal_ok": dist_diag_ok,
            "dist_to_ends_ok": dist_ends_ok,
            "dist_to_ends_min": round(dist_ends_min, 1),
            "dist_to_edges_ok": dist_edges_ok,
            "dist_between_ok": dist_between_ok,
            "all_ok": all_ok,
            "aci_reference": "ACI 318-25 18.10.7.6"
        }

    # =========================================================================
    # DISENO COMPLETO
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
        Realiza diseno completo de viga de acoplamiento.

        Args:
            ln: Claro libre (mm)
            h: Peralte (mm)
            bw: Ancho (mm)
            Vu: Cortante ultimo (tonf)
            fc: f'c del hormigon (MPa)
            fy_diagonal: Fluencia del refuerzo diagonal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            lambda_factor: Factor para concreto liviano
            cover: Recubrimiento (mm)
            steel_grade: Grado del acero diagonal
            confinement_option: Opcion de confinamiento
            use_diagonal: Forzar uso de diagonal (None = automatico)

        Returns:
            CouplingBeamDesignResult con diseno completo
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
            # Calcular angulo de diagonales
            alpha = self.calculate_diagonal_angle(ln, h, cover)

            # Calcular area requerida
            Avd_req = self.required_diagonal_area(Vu, fy_diagonal, alpha)

            # Verificar resistencia (con area propuesta = area requerida)
            Acw = ln * bw
            shear_result = self.calculate_diagonal_shear_strength(
                Avd_req, fy_diagonal, alpha, fc, Acw
            )

            # Verificar limite maximo
            if shear_result.Vn_calc > shear_result.Vn_max:
                warnings.append(
                    f"Cortante diagonal {shear_result.Vn_calc:.1f} tonf "
                    f"excede limite {shear_result.Vn_max:.1f} tonf"
                )

            # Calcular confinamiento
            Ag = h * bw
            # Asumir Ach = 0.8 * Ag para estimacion
            Ach = 0.8 * Ag
            db_diagonal = 25.0  # Asumir diametro tipico

            confinement = self.calculate_diagonal_confinement(
                bw, Ag, Ach, fc, fyt, steel_grade, db_diagonal,
                confinement_option
            )

            phi_Vn = shear_result.phi_Vn
        else:
            # Refuerzo longitudinal - calcular capacidad como viga
            # Vn = Acv * (alpha_c * lambda * sqrt(f'c) + rho_t * fyt)
            # Usar estimacion conservadora
            Acv = ln * bw
            # Coeficiente alpha_c para ln/h >= 4: usar 0.17
            alpha_c = 0.17 if classification.ln_h_ratio >= 2.0 else 0.25
            rho_t = 0.0025  # Asumir minimo

            Vn_N = (alpha_c * lambda_factor * math.sqrt(fc) + rho_t * fyt) * Acv
            Vn = Vn_N / 9806.65
            phi_Vn = 0.75 * Vn

            warnings.append(
                "Refuerzo longitudinal seleccionado - verificar detallado segun 18.6"
            )

        # Verificar demanda vs capacidad
        dcr = Vu / phi_Vn if phi_Vn > 0 else float('inf')
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
