# app/domain/chapter8/limits.py
"""
Capitulo 8.3 ACI 318-25: Limites de Diseno para Losas 2-Way.

Implementa:
- Tabla 8.3.1.1: Espesor minimo de losas 2-Way sin vigas interiores
- Tabla 8.3.1.2: Espesor minimo de losas 2-Way con vigas entre apoyos
"""
from typing import Dict, Tuple
from enum import Enum
from dataclasses import dataclass


class TwoWaySystem(Enum):
    """Tipo de sistema de losa 2-Way segun Tabla 8.3.1.1."""
    FLAT_PLATE = "flat_plate"                  # Losa plana sin capiteles ni abacos
    FLAT_SLAB_DROP_PANEL = "flat_slab_drop"    # Losa con abaco (drop panel)
    SLAB_WITH_BEAMS = "slab_with_beams"        # Losa con vigas entre apoyos


class PanelType(Enum):
    """Tipo de panel para espesor minimo."""
    EXTERIOR_WITHOUT_EDGE_BEAM = "ext_no_beam"    # Panel exterior sin viga de borde
    EXTERIOR_WITH_EDGE_BEAM = "ext_with_beam"     # Panel exterior con viga de borde
    INTERIOR = "interior"                          # Panel interior


# Tabla 8.3.1.1: Factores para losas sin vigas interiores
# h_min = ln / factor
THICKNESS_FACTORS_NO_BEAMS = {
    # Sin abaco (drop panel)
    (TwoWaySystem.FLAT_PLATE, PanelType.EXTERIOR_WITHOUT_EDGE_BEAM): 30,
    (TwoWaySystem.FLAT_PLATE, PanelType.EXTERIOR_WITH_EDGE_BEAM): 33,
    (TwoWaySystem.FLAT_PLATE, PanelType.INTERIOR): 33,
    # Con abaco (drop panel)
    (TwoWaySystem.FLAT_SLAB_DROP_PANEL, PanelType.EXTERIOR_WITHOUT_EDGE_BEAM): 33,
    (TwoWaySystem.FLAT_SLAB_DROP_PANEL, PanelType.EXTERIOR_WITH_EDGE_BEAM): 36,
    (TwoWaySystem.FLAT_SLAB_DROP_PANEL, PanelType.INTERIOR): 36,
}

# Espesores minimos absolutos (mm)
MIN_THICKNESS_NO_DROP = 125      # 125 mm sin abaco
MIN_THICKNESS_WITH_DROP = 100    # 100 mm con abaco
MIN_THICKNESS_WITH_BEAMS = 90    # 90 mm con vigas


@dataclass
class TwoWayThicknessResult:
    """Resultado de verificacion de espesor para losa 2-Way."""
    h_min: float           # Espesor minimo requerido (mm)
    h_provided: float      # Espesor provisto (mm)
    is_ok: bool            # True si h >= h_min
    ratio: float           # h / h_min
    system_type: str       # Tipo de sistema
    panel_type: str        # Tipo de panel
    ln_mm: float           # Luz libre (mm)
    fy_factor: float       # Factor de correccion por fy
    aci_reference: str     # Referencia ACI


def get_fy_correction_factor(fy_mpa: float) -> float:
    """
    Calcula el factor de correccion por fy.

    Para fy != 420 MPa, se corrige por (0.4 + fy/700).

    Args:
        fy_mpa: Limite de fluencia del acero (MPa)

    Returns:
        Factor de correccion (1.0 para fy=420)
    """
    return 0.4 + fy_mpa / 700


def get_minimum_thickness_two_way(
    ln_mm: float,
    system_type: TwoWaySystem,
    panel_type: PanelType = PanelType.INTERIOR,
    fy_mpa: float = 420.0,
    alpha_fm: float = 0.0
) -> Tuple[float, Dict]:
    """
    Calcula el espesor minimo de una losa 2-Way.

    Para losas sin vigas interiores (Tabla 8.3.1.1):
    h_min = ln / factor * fy_correction

    Para losas con vigas (8.3.1.2):
    Depende de alpha_fm (rigidez relativa)

    Args:
        ln_mm: Luz libre en direccion larga (mm)
        system_type: Tipo de sistema de losa
        panel_type: Tipo de panel (interior/exterior)
        fy_mpa: Limite de fluencia del acero (MPa)
        alpha_fm: Rigidez relativa promedio (para losas con vigas)

    Returns:
        Tupla (h_min_mm, detalles)
    """
    fy_factor = get_fy_correction_factor(fy_mpa)
    details = {
        'ln_mm': ln_mm,
        'system_type': system_type.value,
        'panel_type': panel_type.value,
        'fy_factor': fy_factor,
        'alpha_fm': alpha_fm
    }

    if system_type == TwoWaySystem.SLAB_WITH_BEAMS:
        # Losa con vigas - Tabla 8.3.1.2
        h_min = _calculate_thickness_with_beams(ln_mm, alpha_fm, fy_factor)
        h_min = max(h_min, MIN_THICKNESS_WITH_BEAMS)
        details['aci_reference'] = 'ACI 318-25 Tabla 8.3.1.2'
    else:
        # Losa sin vigas interiores - Tabla 8.3.1.1
        factor = THICKNESS_FACTORS_NO_BEAMS.get(
            (system_type, panel_type), 33
        )
        h_min = (ln_mm / factor) * fy_factor

        # Aplicar espesor minimo absoluto
        if system_type == TwoWaySystem.FLAT_SLAB_DROP_PANEL:
            h_min = max(h_min, MIN_THICKNESS_WITH_DROP)
        else:
            h_min = max(h_min, MIN_THICKNESS_NO_DROP)

        details['factor'] = factor
        details['aci_reference'] = 'ACI 318-25 Tabla 8.3.1.1'

    return h_min, details


def _calculate_thickness_with_beams(
    ln_mm: float,
    alpha_fm: float,
    fy_factor: float
) -> float:
    """
    Calcula espesor minimo para losas con vigas segun Tabla 8.3.1.2.

    Args:
        ln_mm: Luz libre (mm)
        alpha_fm: Rigidez relativa promedio
        fy_factor: Factor de correccion por fy

    Returns:
        Espesor minimo (mm)
    """
    if alpha_fm <= 0.2:
        # Usar Tabla 8.3.1.1 (como sin vigas)
        return (ln_mm / 33) * fy_factor

    elif alpha_fm < 2.0:
        # Interpolacion segun 8.3.1.2
        # h_min = ln * (0.8 + fy/1400) / (36 + 5*beta*(alpha_fm - 0.2))
        # Simplificado: h_min = ln / (36 + 5*(alpha_fm - 0.2)) * fy_factor
        beta = 1.0  # Relacion de luces (simplificado)
        divisor = 36 + 5 * beta * (alpha_fm - 0.2)
        return (ln_mm / divisor) * fy_factor

    else:  # alpha_fm >= 2.0
        # h_min = ln * (0.8 + fy/1400) / (36 + 9*beta)
        # Simplificado con beta=1: h_min = ln/45 * fy_factor
        beta = 1.0
        divisor = 36 + 9 * beta
        return (ln_mm / divisor) * fy_factor


def check_thickness_two_way(
    h_provided_mm: float,
    ln_mm: float,
    system_type: TwoWaySystem,
    panel_type: PanelType = PanelType.INTERIOR,
    fy_mpa: float = 420.0,
    alpha_fm: float = 0.0
) -> TwoWayThicknessResult:
    """
    Verifica si el espesor de la losa 2-Way cumple con el minimo.

    Args:
        h_provided_mm: Espesor provisto de la losa (mm)
        ln_mm: Luz libre en direccion larga (mm)
        system_type: Tipo de sistema de losa
        panel_type: Tipo de panel
        fy_mpa: Limite de fluencia del acero (MPa)
        alpha_fm: Rigidez relativa promedio

    Returns:
        TwoWayThicknessResult con resultados de verificacion
    """
    h_min, details = get_minimum_thickness_two_way(
        ln_mm, system_type, panel_type, fy_mpa, alpha_fm
    )

    is_ok = h_provided_mm >= h_min
    ratio = h_provided_mm / h_min if h_min > 0 else 1.0

    return TwoWayThicknessResult(
        h_min=h_min,
        h_provided=h_provided_mm,
        is_ok=is_ok,
        ratio=ratio,
        system_type=system_type.value,
        panel_type=panel_type.value,
        ln_mm=ln_mm,
        fy_factor=details['fy_factor'],
        aci_reference=details['aci_reference']
    )
