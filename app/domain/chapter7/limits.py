# app/domain/chapter7/limits.py
"""
Capitulo 7.3 ACI 318-25: Limites de Diseno para Losas 1-Way.

Implementa:
- Tabla 7.3.1.1: Espesor minimo de losas 1-Way no presforzadas
- 7.3.1.1.1: Factores de correccion por fy
- 7.3.1.1.2: Factores de correccion por concreto liviano
"""
from typing import Dict, Tuple
from enum import Enum
from dataclasses import dataclass


class SupportCondition(Enum):
    """Condicion de apoyo segun Tabla 7.3.1.1."""
    SIMPLY_SUPPORTED = "simply_supported"     # Simplemente apoyado
    ONE_END_CONTINUOUS = "one_end_continuous"  # Un extremo continuo
    BOTH_ENDS_CONTINUOUS = "both_ends_continuous"  # Ambos extremos continuos
    CANTILEVER = "cantilever"                  # Voladizo


# Tabla 7.3.1.1: Factores para espesor minimo (h_min = ln / factor)
# Para fy = 420 MPa (60 ksi) y concreto de peso normal
THICKNESS_FACTORS = {
    SupportCondition.SIMPLY_SUPPORTED: 20,      # ln/20
    SupportCondition.ONE_END_CONTINUOUS: 24,    # ln/24
    SupportCondition.BOTH_ENDS_CONTINUOUS: 28,  # ln/28
    SupportCondition.CANTILEVER: 10,            # ln/10
}


@dataclass
class ThicknessCheckResult:
    """Resultado de verificacion de espesor."""
    h_min: float           # Espesor minimo requerido (mm)
    h_provided: float      # Espesor provisto (mm)
    is_ok: bool            # True si h >= h_min
    ratio: float           # h / h_min
    support_condition: str # Condicion de apoyo
    fy_factor: float       # Factor de correccion por fy
    lambda_factor: float   # Factor de correccion por peso
    aci_reference: str     # Referencia ACI


def get_fy_correction_factor(fy_mpa: float) -> float:
    """
    Calcula el factor de correccion por fy segun 7.3.1.1.1.

    h_min se modifica por (0.4 + fy/700) para fy en MPa.
    Base: fy = 420 MPa -> factor = 1.0

    Args:
        fy_mpa: Limite de fluencia del acero (MPa)

    Returns:
        Factor de correccion (1.0 para fy=420)
    """
    # Formula ACI: (0.4 + fy/700) para fy en MPa
    # Simplificado: factor = (0.4 + fy/700) / (0.4 + 420/700)
    # = (0.4 + fy/700) / 1.0 = 0.4 + fy/700
    return 0.4 + fy_mpa / 700


def get_lightweight_correction_factor(
    wc_kg_m3: float,
    is_all_lightweight: bool = False,
    is_sand_lightweight: bool = False
) -> float:
    """
    Calcula el factor de correccion por concreto liviano segun 7.3.1.1.2.

    Para concreto liviano con wc entre 1440 y 1840 kg/m3:
    - Factor = max(1.65 - 0.0003*wc, 1.09)

    Para concreto de peso normal: factor = 1.0

    Args:
        wc_kg_m3: Peso unitario del concreto (kg/m3)
        is_all_lightweight: True si es todo liviano (agregados gruesos y finos)
        is_sand_lightweight: True si es arena liviana (solo agregado grueso)

    Returns:
        Factor de correccion (1.0 para concreto normal)
    """
    # Concreto de peso normal: ~2400 kg/m3
    if wc_kg_m3 >= 2000:
        return 1.0

    # Concreto liviano: 1440 - 1840 kg/m3
    if 1440 <= wc_kg_m3 <= 1840:
        factor = 1.65 - 0.0003 * wc_kg_m3
        return max(factor, 1.09)

    # Fuera de rango: usar factor conservador
    if wc_kg_m3 < 1440:
        return 1.65  # Muy liviano
    return 1.0


def get_minimum_thickness_one_way(
    ln_mm: float,
    support_condition: SupportCondition,
    fy_mpa: float = 420.0,
    wc_kg_m3: float = 2400.0
) -> Tuple[float, Dict]:
    """
    Calcula el espesor minimo de una losa 1-Way segun Tabla 7.3.1.1.

    h_min = ln / factor * (0.4 + fy/700) * lambda_correction

    Args:
        ln_mm: Luz libre de la losa (mm)
        support_condition: Condicion de apoyo
        fy_mpa: Limite de fluencia del acero (MPa)
        wc_kg_m3: Peso unitario del concreto (kg/m3)

    Returns:
        Tupla (h_min_mm, detalles)
    """
    # Factor base de tabla
    base_factor = THICKNESS_FACTORS.get(support_condition, 24)

    # Factores de correccion
    fy_factor = get_fy_correction_factor(fy_mpa)
    lambda_factor = get_lightweight_correction_factor(wc_kg_m3)

    # Espesor minimo
    h_min = (ln_mm / base_factor) * fy_factor * lambda_factor

    details = {
        'ln_mm': ln_mm,
        'base_factor': base_factor,
        'fy_factor': fy_factor,
        'lambda_factor': lambda_factor,
        'support_condition': support_condition.value,
        'aci_reference': 'ACI 318-25 Tabla 7.3.1.1'
    }

    return h_min, details


def check_thickness_one_way(
    h_provided_mm: float,
    ln_mm: float,
    support_condition: SupportCondition,
    fy_mpa: float = 420.0,
    wc_kg_m3: float = 2400.0
) -> ThicknessCheckResult:
    """
    Verifica si el espesor de la losa cumple con el minimo.

    Si h >= h_min, no se requiere calcular deflexiones.
    Si h < h_min, se deben calcular deflexiones segun 24.2.

    Args:
        h_provided_mm: Espesor provisto de la losa (mm)
        ln_mm: Luz libre de la losa (mm)
        support_condition: Condicion de apoyo
        fy_mpa: Limite de fluencia del acero (MPa)
        wc_kg_m3: Peso unitario del concreto (kg/m3)

    Returns:
        ThicknessCheckResult con resultados de verificacion
    """
    h_min, details = get_minimum_thickness_one_way(
        ln_mm, support_condition, fy_mpa, wc_kg_m3
    )

    is_ok = h_provided_mm >= h_min
    ratio = h_provided_mm / h_min if h_min > 0 else 1.0

    return ThicknessCheckResult(
        h_min=h_min,
        h_provided=h_provided_mm,
        is_ok=is_ok,
        ratio=ratio,
        support_condition=support_condition.value,
        fy_factor=details['fy_factor'],
        lambda_factor=details['lambda_factor'],
        aci_reference='ACI 318-25 Tabla 7.3.1.1'
    )


# Constantes adicionales
MINIMUM_SLAB_THICKNESS_MM = 100  # Espesor minimo absoluto recomendado
