# app/domain/chapter18/coupling_beams/confinement.py
"""
Confinamiento de diagonales en vigas de acople ACI 318-25 §18.10.7.4(c)-(d).

Opción (c) - Confinamiento individual:
- Dimensión mínima núcleo >= bw/2 paralelo a bw
- Dimensión mínima núcleo >= bw/5 otros lados
- Ash >= max(0.09*s*bc*f'c/fyt, 0.3*s*bc*(Ag/Ach-1)*f'c/fyt)
- Espaciamiento perpendicular <= 14"
- Refuerzo perimetral >= 0.002*bw*s

Opción (d) - Sección completa:
- Ash igual que opción (c)
- Espaciamiento vertical/horizontal <= 8"
- Cada barra soportada
"""
from typing import List

from ...calculations.confinement import calculate_ash_sbc
from ...constants.materials import SteelGrade
from ...constants.units import (
    SIX_INCH_MM,
    EIGHT_INCH_MM,
    TWELVE_INCH_MM,
    FOURTEEN_INCH_MM,
)
from ..results import ConfinementOption, DiagonalConfinementResult


def calculate_diagonal_confinement(
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

    Args:
        bw: Ancho de la viga (mm)
        Ag: Área bruta (mm2)
        Ach: Área del núcleo (mm2)
        fc: f'c del hormigón (MPa)
        fyt: fy del refuerzo transversal (MPa)
        steel_grade: Grado del acero diagonal
        db_diagonal: Diámetro de barra diagonal (mm)
        option: Opción de confinamiento

    Returns:
        DiagonalConfinementResult con requisitos
    """
    # Ash/(s*bc) requerido - usar función compartida
    Ash_sbc = calculate_ash_sbc(Ag, Ach, fc, fyt)

    # Espaciamiento máximo según Tabla 18.10.7.4
    if steel_grade == SteelGrade.GRADE_60:
        spacing_max = min(6 * db_diagonal, SIX_INCH_MM)
    elif steel_grade == SteelGrade.GRADE_80:
        spacing_max = min(5 * db_diagonal, SIX_INCH_MM)
    else:  # GRADE_100
        spacing_max = min(4 * db_diagonal, SIX_INCH_MM)

    if option == ConfinementOption.INDIVIDUAL:
        # Dimensiones de núcleo
        core_parallel = bw / 2
        core_other = bw / 5

        # Espaciamiento perpendicular
        spacing_perp = FOURTEEN_INCH_MM

        # Refuerzo perimetral
        rho_perimeter = 0.002
        perimeter_spacing = TWELVE_INCH_MM

    else:  # FULL_SECTION
        core_parallel = 0
        core_other = 0
        spacing_perp = EIGHT_INCH_MM
        rho_perimeter = 0
        perimeter_spacing = 0

    # Ash requerido (ejemplo con s = spacing_max, bc = 150mm típico)
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


def check_shear_redistribution(
    beams_Ve: List[float],
    beams_phi_Vn: List[float],
    beams_ln_h: List[float]
) -> dict:
    """
    Verifica redistribución de cortante entre vigas de acoplamiento.

    Según 18.10.7.5:
    - Permitido si vigas alineadas verticalmente
    - ln/h >= 2
    - Redistribución máxima: 20%
    - Sum(phi*Vn) >= Sum(Ve)

    Args:
        beams_Ve: Lista de cortantes de diseño (tonf)
        beams_phi_Vn: Lista de capacidades (tonf)
        beams_ln_h: Lista de relaciones ln/h

    Returns:
        Dict con resultado de verificación
    """
    # Verificar que todas las vigas tengan ln/h >= 2
    all_eligible = all(r >= 2.0 for r in beams_ln_h)

    # Verificar capacidad total
    sum_Ve = sum(beams_Ve)
    sum_phi_Vn = sum(beams_phi_Vn)
    capacity_ok = sum_phi_Vn >= sum_Ve

    # Calcular redistribución máxima permitida
    max_redistribution = [0.2 * Ve for Ve in beams_Ve]

    return {
        "eligible": all_eligible,
        "sum_Ve": round(sum_Ve, 2),
        "sum_phi_Vn": round(sum_phi_Vn, 2),
        "capacity_ok": capacity_ok,
        "max_redistribution": [round(r, 2) for r in max_redistribution],
        "aci_reference": "ACI 318-25 18.10.7.5"
    }


def check_penetration_limits(
    h: float,
    diameter: float,
    dist_to_diagonal: float,
    dist_to_ends: float,
    dist_to_edges: float,
    dist_between: float = 0
) -> dict:
    """
    Verifica límites de penetraciones en vigas con diagonal.

    Según 18.10.7.6:
    - Máximo 2 penetraciones
    - Cilíndricas horizontales
    - Diámetro <= max(h/6, 6")
    - Distancia a diagonales >= 2"
    - Distancia a extremos >= h/4
    - Distancia a bordes sup/inf >= 4"
    - Distancia entre penetraciones >= diámetro mayor

    Args:
        h: Peralte de la viga (mm)
        diameter: Diámetro de penetración (mm)
        dist_to_diagonal: Distancia libre a diagonales (mm)
        dist_to_ends: Distancia libre a extremos (mm)
        dist_to_edges: Distancia libre a bordes (mm)
        dist_between: Distancia entre penetraciones (mm)

    Returns:
        Dict con verificación de cada límite
    """
    # Límites en mm
    TWO_INCH = 50.8
    FOUR_INCH = 101.6

    # Diámetro máximo
    diam_max = max(h / 6, SIX_INCH_MM)
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
