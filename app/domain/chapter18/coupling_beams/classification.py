# app/domain/chapter18/coupling_beams/classification.py
"""
Clasificación de vigas de acoplamiento según ACI 318-25 §18.10.7.1-18.10.7.3.

Según relación ln/h:
- ln/h >= 4: Como viga de pórtico (18.6)
- ln/h < 2 con Vu alto: Diagonal obligatorio
- 2 <= ln/h < 4: Diagonal o longitudinal
"""
import math

from ...constants.units import N_TO_TONF
from ..results import (
    CouplingBeamType,
    ReinforcementType,
    CouplingBeamClassification,
)


def classify_coupling_beam(
    ln: float,
    h: float,
    bw: float,
    Vu: float,
    fc: float,
    lambda_factor: float = 1.0
) -> CouplingBeamClassification:
    """
    Clasifica la viga de acoplamiento según su relación ln/h.

    Según 18.10.7.1-18.10.7.3:
    - ln/h >= 4: Como viga de pórtico (18.6)
    - ln/h < 2 con Vu >= 4*lambda*sqrt(f'c)*Acw: Diagonal obligatorio
    - 2 <= ln/h < 4: Diagonal o longitudinal

    Args:
        ln: Claro libre de la viga (mm)
        h: Peralte de la viga (mm)
        bw: Ancho de la viga (mm)
        Vu: Cortante último (tonf)
        fc: f'c del hormigón (MPa)
        lambda_factor: Factor para concreto liviano

    Returns:
        CouplingBeamClassification con tipo y opciones
    """
    ratio = ln / h if h > 0 else 0

    # Calcular umbral de cortante alto
    # 4 * lambda * sqrt(f'c) * Acw
    Acw = ln * bw  # Área de corte
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
