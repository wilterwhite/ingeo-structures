# app/domain/chapter18/piers/transverse.py
"""
Requisitos de refuerzo transversal para pilares de muro ACI 318-25 §18.10.8.1(c)-(e).

Incluye:
- Tipo de estribos (cerrados, ganchos)
- Espaciamiento máximo
- Extensiones arriba/abajo
- Cuantía requerida Ash/(s*bc)
"""
from ...calculations.confinement import calculate_ash_sbc
from ...constants.units import SIX_INCH_MM, TWELVE_INCH_MM, EIGHTEEN_INCH_MM
from ..results import (
    DesignMethod,
    WallPierClassification,
    WallPierTransverseReinforcement,
)

# Alias para compatibilidad con imports existentes
EXTENSION_MIN_MM = TWELVE_INCH_MM


def calculate_transverse_requirements(
    classification: WallPierClassification,
    has_single_curtain: bool = False,
    fc: float = 28,
    fyt: float = 420
) -> WallPierTransverseReinforcement:
    """
    Calcula requisitos de refuerzo transversal para pilar.

    Según 18.10.8.1 alternativo:
    (c) Estribos cerrados (ganchos 180° si cortina simple)
    (d) Espaciamiento vertical <= 6"
    (e) Extensión >= 12" arriba y abajo de altura libre
    (f) Elementos de borde si se requieren por 18.10.6.3

    Args:
        classification: Clasificación del pilar
        has_single_curtain: Si tiene cortina simple
        fc: f'c del hormigón (MPa)
        fyt: Fluencia del refuerzo transversal (MPa)

    Returns:
        WallPierTransverseReinforcement con requisitos
    """
    if classification.design_method == DesignMethod.WALL:
        # Requisitos de muro - espaciamiento máximo 18"
        return WallPierTransverseReinforcement(
            requires_closed_hoops=False,
            hook_type="90°",
            spacing_max=EIGHTEEN_INCH_MM,
            extension_above=0,
            extension_below=0,
            Ash_sbc_required=0,
            aci_reference="ACI 318-25 18.10.2"
        )

    # Método alternativo o columna
    if has_single_curtain:
        hook_type = "180°"
    else:
        hook_type = "135° o 180°"

    # Espaciamiento máximo (18.10.8.1(d))
    spacing_max = SIX_INCH_MM

    # Extensión (18.10.8.1(e))
    extension = EXTENSION_MIN_MM  # 12"

    # Ash/(s*bc) para método alternativo - usar función compartida
    # Nota: Para pilares, Ag ≈ Ach (área pequeña), expr_b domina
    Ash_sbc = calculate_ash_sbc(Ag=1.0, Ach=1.0, fc=fc, fyt=fyt)

    return WallPierTransverseReinforcement(
        requires_closed_hoops=True,
        hook_type=hook_type,
        spacing_max=round(spacing_max, 1),
        extension_above=extension,
        extension_below=extension,
        Ash_sbc_required=round(Ash_sbc, 5),
        aci_reference="ACI 318-25 18.10.8.1(c)-(e)"
    )
