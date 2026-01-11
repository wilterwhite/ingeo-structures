# app/domain/chapter22/flexural_capacity.py
"""
Calculo de capacidad a flexion segun ACI 318-25 Capitulo 22.

Implementa:
- 22.2.2: Bloque de compresion rectangular equivalente
- 22.2.1: Hipotesis de diseño a flexion

Unidades: SI (N, mm, MPa)
"""
from dataclasses import dataclass
from typing import Optional

from ..constants.phi_chapter21 import PHI_TENSION
from ..constants.materials import calculate_beta1


@dataclass
class FlexuralCapacityResult:
    """Resultado del calculo de capacidad a flexion."""
    Mn: float
    """Momento nominal (N-mm)."""

    phi_Mn: float
    """Momento de diseno phi*Mn (N-mm)."""

    a: float
    """Profundidad del bloque de compresion (mm)."""

    c: float
    """Profundidad del eje neutro (mm)."""

    phi: float
    """Factor de reduccion usado."""

    epsilon_t: float
    """Deformacion en el acero de traccion."""

    is_tension_controlled: bool
    """True si la seccion es controlada por traccion."""

    aci_reference: str = "ACI 318-25 22.2"


def calculate_flexural_capacity(
    As: float,
    fy: float,
    fc: float,
    b: float,
    d: float,
    phi: Optional[float] = None,
) -> FlexuralCapacityResult:
    """
    Calcula la capacidad a flexion de una seccion rectangular.

    Implementa ACI 318-25 22.2 usando el bloque de compresion
    rectangular equivalente.

    Args:
        As: Area de acero de traccion (mm2)
        fy: Fluencia del acero (MPa)
        fc: Resistencia del concreto (MPa)
        b: Ancho de la seccion (mm)
        d: Altura efectiva (mm)
        phi: Factor de reduccion (None = calcular automaticamente)

    Returns:
        FlexuralCapacityResult con capacidad y detalles

    Example:
        >>> result = calculate_flexural_capacity(
        ...     As=1500,  # mm2
        ...     fy=420,   # MPa
        ...     fc=28,    # MPa
        ...     b=1000,   # mm
        ...     d=175     # mm
        ... )
        >>> print(f"phi*Mn = {result.phi_Mn / 1e6:.2f} kN-m")
    """
    if As <= 0 or b <= 0 or d <= 0:
        return FlexuralCapacityResult(
            Mn=0, phi_Mn=0, a=0, c=0, phi=0,
            epsilon_t=0, is_tension_controlled=True
        )

    # Bloque de compresion (22.2.2.4.1)
    # a = As * fy / (0.85 * fc * b)
    a = As * fy / (0.85 * fc * b)

    # Eje neutro
    beta1 = calculate_beta1(fc)
    c = a / beta1

    # Verificar caso degenerado
    if d <= a / 2:
        return FlexuralCapacityResult(
            Mn=0, phi_Mn=0, a=a, c=c, phi=0,
            epsilon_t=0, is_tension_controlled=False
        )

    # Deformacion en el acero de traccion (22.2.1.2)
    epsilon_cu = 0.003  # Deformacion ultima del concreto
    epsilon_t = epsilon_cu * (d - c) / c if c > 0 else float('inf')

    # Determinar si es controlada por traccion (21.2.2)
    epsilon_ty = fy / 200000  # Deformacion de fluencia
    is_tension_controlled = epsilon_t >= epsilon_ty + 0.003

    # Factor phi
    if phi is None:
        if is_tension_controlled:
            phi = PHI_TENSION  # 0.90
        else:
            # Zona de transicion (simplificado)
            phi = 0.65 + (epsilon_t - epsilon_ty) * 0.25 / 0.003
            phi = max(0.65, min(0.90, phi))

    # Momento nominal (N-mm)
    Mn = As * fy * (d - a / 2)
    phi_Mn = phi * Mn

    return FlexuralCapacityResult(
        Mn=Mn,
        phi_Mn=phi_Mn,
        a=a,
        c=c,
        phi=phi,
        epsilon_t=epsilon_t,
        is_tension_controlled=is_tension_controlled
    )


def calculate_As_required(
    Mu: float,
    fy: float,
    d: float,
    phi: float = PHI_TENSION,
    lever_arm_ratio: float = 0.9,
) -> float:
    """
    Calcula el As requerido para un momento dado (simplificado).

    Usa la aproximacion: As = Mu / (phi * fy * jd)
    donde jd = lever_arm_ratio * d

    Esta es una aproximacion conservadora. Para calculo exacto,
    usar iteracion con calculate_flexural_capacity().

    Args:
        Mu: Momento ultimo (N-mm)
        fy: Fluencia del acero (MPa)
        d: Altura efectiva (mm)
        phi: Factor de reduccion (default 0.90)
        lever_arm_ratio: jd/d ratio (default 0.9)

    Returns:
        As requerido (mm2)
    """
    if Mu <= 0:
        return 0.0

    jd = lever_arm_ratio * d
    As_req = Mu / (phi * fy * jd)

    return As_req
