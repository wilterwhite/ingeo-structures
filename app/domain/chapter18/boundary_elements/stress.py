# app/domain/chapter18/boundary_elements/stress.py
"""
Verificación por método de esfuerzos ACI 318-25 §18.10.6.3.

Según 18.10.6.3:
- Requiere elemento de borde si sigma_max >= 0.2 * f'c
- Puede discontinuar si sigma < 0.15 * f'c
"""
from ..results import StressCheckResult, BoundaryStressAnalysis


def calculate_boundary_stress(
    width: float,
    thickness: float,
    fc: float,
    P_N: float,
    M_Nmm: float
) -> BoundaryStressAnalysis:
    """
    Calcula el esfuerzo en los bordes del muro para verificación de boundary elements.

    Usa la fórmula: σ = P/A ± M*y/I

    Args:
        width: Ancho del muro (mm) - dimension en planta
        thickness: Espesor del muro (mm)
        fc: Resistencia del hormigón f'c (MPa)
        P_N: Carga axial en N (positivo = compresión)
        M_Nmm: Momento flector en N-mm (valor absoluto)

    Returns:
        BoundaryStressAnalysis con esfuerzos calculados
    """
    # Propiedades geométricas
    Ag = width * thickness  # mm²
    Ig = thickness * (width ** 3) / 12  # mm⁴
    y = width / 2  # mm (distancia al borde)

    # Límite de esfuerzo según ACI 318-25 §18.10.6.3
    sigma_limit = 0.2 * fc  # MPa

    # Calcular esfuerzos en bordes (MPa)
    # Borde izquierdo: compresión cuando M positivo
    sigma_left = P_N / Ag + abs(M_Nmm) * y / Ig
    # Borde derecho
    sigma_right = P_N / Ag - abs(M_Nmm) * y / Ig

    return BoundaryStressAnalysis(
        sigma_left=sigma_left,
        sigma_right=sigma_right,
        sigma_limit=sigma_limit,
        Ag=Ag,
        Ig=Ig,
        y=y
    )


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
