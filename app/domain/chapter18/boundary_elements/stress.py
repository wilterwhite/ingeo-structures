# app/domain/chapter18/boundary_elements/stress.py
"""
Verificación por método de esfuerzos ACI 318-25 §18.10.6.3.

Según 18.10.6.3:
- Requiere elemento de borde si sigma_max >= 0.2 * f'c
- Puede discontinuar si sigma < 0.15 * f'c
"""
from ..results import StressCheckResult


def check_stress_method(
    sigma_max: float,
    fc: float
) -> StressCheckResult:
    """
    Verifica si se requiere elemento de borde por método de esfuerzos.

    Args:
        sigma_max: Esfuerzo máximo de compresión en fibra extrema (MPa)
        fc: Resistencia del hormigón f'c (MPa)

    Returns:
        StressCheckResult con resultado de la verificación
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
