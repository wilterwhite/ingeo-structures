# app/services/analysis/verification_config.py
"""
Configuracion de verificacion por tipo de elemento.

Define que verificaciones aplicar y con que parametros segun
el tipo de elemento clasificado.
"""
from dataclasses import dataclass
from typing import Dict

from .element_classifier import ElementType


@dataclass
class VerificationConfig:
    """
    Configuracion de verificacion para un tipo de elemento.

    Define los parametros y verificaciones a aplicar segun ACI 318-25.
    """
    # =========================================================================
    # Flexion
    # =========================================================================
    check_axial_threshold: bool = False
    """Si verificar umbral de axial significativo (Pu >= Ag*f'c/divisor)."""

    axial_threshold_divisor: float = 10.0
    """Divisor para umbral de axial (10 para vigas §18.6.4.6)."""

    k_factor: float = 1.0
    """Factor de longitud efectiva (0.8 muros, 1.0 columnas/vigas)."""

    braced: bool = True
    """Si el elemento esta arriostrado lateralmente."""

    pn_max_factor: float = 0.80
    """Factor de reduccion para Pn_max (ACI 318-25 22.4.2)."""

    # =========================================================================
    # Cortante
    # =========================================================================
    shear_method: str = 'simple'
    """Metodo de cortante: 'simple' (V2), 'srss' (V2-V3), 'amplified' (muros)."""

    use_capacity_design: bool = False
    """Si usar diseno por capacidad para cortante (§18.7.6 / §18.10.8)."""

    # =========================================================================
    # Verificaciones adicionales (muros)
    # =========================================================================
    check_classification: bool = False
    """Si incluir clasificacion §18.10.8."""

    check_amplification: bool = False
    """Si verificar amplificacion de cortante §18.10.3.3."""

    check_boundary: bool = False
    """Si verificar elementos de borde §18.10.6."""

    check_end_zones: bool = False
    """Si verificar zonas de extremo §18.10.2.4."""

    check_min_reinforcement: bool = False
    """Si verificar cuantia minima §18.10.2.1."""


# =============================================================================
# Presets por tipo de elemento
# =============================================================================

BEAM_CONFIG = VerificationConfig(
    check_axial_threshold=True,
    axial_threshold_divisor=10.0,  # Ag*f'c/10
    k_factor=1.0,
    braced=True,
    shear_method='simple',
    use_capacity_design=False,
)
"""Viga §18.6 - Flexion con umbral de axial, cortante simple V2."""


COLUMN_NONSEISMIC_CONFIG = VerificationConfig(
    check_axial_threshold=False,
    k_factor=1.0,
    braced=True,
    shear_method='srss',
    use_capacity_design=False,
)
"""Columna no sismica §22 - Flexocompresion P-M, cortante V2-V3 SRSS."""


COLUMN_SEISMIC_CONFIG = VerificationConfig(
    check_axial_threshold=False,
    k_factor=1.0,
    braced=True,
    shear_method='srss',
    use_capacity_design=True,
)
"""Columna sismica §18.7 - Flexocompresion P-M, cortante por capacidad."""


WALL_PIER_COLUMN_CONFIG = VerificationConfig(
    check_axial_threshold=False,
    k_factor=1.0,
    braced=True,
    shear_method='srss',
    use_capacity_design=True,
    check_classification=True,
)
"""Wall pier tipo columna §18.10.8 (lw/tw <= 2.5) - Requisitos de columna."""


WALL_PIER_ALTERNATE_CONFIG = VerificationConfig(
    check_axial_threshold=False,
    k_factor=0.8,
    braced=True,
    shear_method='srss',
    use_capacity_design=True,
    check_classification=True,
    check_boundary=True,
)
"""Wall pier metodo alternativo §18.10.8.1 (2.5 < lw/tw <= 6.0)."""


WALL_SQUAT_CONFIG = VerificationConfig(
    check_axial_threshold=False,
    k_factor=0.8,
    braced=True,
    shear_method='amplified',
    use_capacity_design=True,
    check_classification=True,
    check_amplification=True,
    check_boundary=True,
    check_min_reinforcement=True,
)
"""Muro rechoncho §18.10 (lw/tw > 6.0, hw/lw < 2.0)."""


WALL_CONFIG = VerificationConfig(
    check_axial_threshold=False,
    k_factor=0.8,
    braced=True,
    shear_method='amplified',
    use_capacity_design=True,
    check_classification=True,
    check_amplification=True,
    check_boundary=True,
    check_end_zones=True,
    check_min_reinforcement=True,
)
"""Muro esbelto §18.10 (lw/tw > 6.0, hw/lw >= 2.0) - Todas las verificaciones."""


DROP_BEAM_CONFIG = VerificationConfig(
    check_axial_threshold=False,
    k_factor=0.8,
    braced=True,
    shear_method='simple',
    use_capacity_design=False,
    check_classification=False,
    check_amplification=False,
    check_boundary=True,
    check_end_zones=False,
    check_min_reinforcement=True,
)
"""Viga capitel (losa diseñada como viga) - Flexocompresion P-M, cortante simple."""


# =============================================================================
# Mapa de configuraciones
# =============================================================================

CONFIGS: Dict[ElementType, VerificationConfig] = {
    ElementType.BEAM: BEAM_CONFIG,
    ElementType.COLUMN_NONSEISMIC: COLUMN_NONSEISMIC_CONFIG,
    ElementType.COLUMN_SEISMIC: COLUMN_SEISMIC_CONFIG,
    ElementType.WALL_PIER_COLUMN: WALL_PIER_COLUMN_CONFIG,
    ElementType.WALL_PIER_ALTERNATE: WALL_PIER_ALTERNATE_CONFIG,
    ElementType.WALL_SQUAT: WALL_SQUAT_CONFIG,
    ElementType.WALL: WALL_CONFIG,
    ElementType.DROP_BEAM: DROP_BEAM_CONFIG,
}


def get_config(element_type: ElementType) -> VerificationConfig:
    """
    Obtiene la configuracion para un tipo de elemento.

    Args:
        element_type: Tipo de elemento clasificado

    Returns:
        VerificationConfig correspondiente
    """
    return CONFIGS.get(element_type, WALL_CONFIG)
