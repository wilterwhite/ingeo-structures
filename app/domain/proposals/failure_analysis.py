# app/domain/proposals/failure_analysis.py
"""
Análisis de modo de falla para propuestas de diseño.

Determina el modo de falla principal basándose en los resultados
de verificación de flexión y corte.
"""
from ..entities.design_proposal import FailureMode


# Umbrales para detección de sobrediseño
OVERDESIGNED_SF_MIN = 1.5   # SF mínimo para considerar sobrediseño
OVERDESIGNED_DCR_MAX = 0.7  # DCR máximo para considerar sobrediseño


def determine_failure_mode(
    flexure_sf: float,
    shear_dcr: float,
    boundary_required: bool = False,
    slenderness_reduction: float = 1.0,
    check_overdesign: bool = True
) -> FailureMode:
    """
    Determina el modo de falla principal (o sobrediseño).

    Prioridad de fallas:
    1. COMBINED: Falla flexión Y corte simultáneamente
    2. SLENDERNESS: Falla flexión con reducción por esbeltez significativa
    3. FLEXURE: Solo falla flexión
    4. SHEAR: Solo falla corte
    5. CONFINEMENT: Requiere elemento de borde pero no falla
    6. OVERDESIGNED: SF alto y DCR bajo (optimizable)
    7. NONE: Pasa todas las verificaciones

    Args:
        flexure_sf: Factor de seguridad de flexión (< 1.0 = falla)
        shear_dcr: DCR de corte (> 1.0 = falla)
        boundary_required: Si se requiere elemento de borde
        slenderness_reduction: Factor de reducción por esbeltez
        check_overdesign: Si verificar condición de sobrediseño

    Returns:
        FailureMode indicando el modo de falla principal
    """
    flexure_fails = flexure_sf < 1.0
    shear_fails = shear_dcr > 1.0
    slenderness_issue = slenderness_reduction < 0.7  # Reducción significativa

    if flexure_fails and shear_fails:
        return FailureMode.COMBINED
    elif flexure_fails:
        if slenderness_issue:
            return FailureMode.SLENDERNESS
        return FailureMode.FLEXURE
    elif shear_fails:
        return FailureMode.SHEAR
    elif boundary_required:
        return FailureMode.CONFINEMENT

    # Detectar sobrediseño: SF alto Y DCR bajo
    if check_overdesign:
        is_overdesigned = (
            flexure_sf >= OVERDESIGNED_SF_MIN and
            shear_dcr <= OVERDESIGNED_DCR_MAX
        )
        if is_overdesigned:
            return FailureMode.OVERDESIGNED

    return FailureMode.NONE
