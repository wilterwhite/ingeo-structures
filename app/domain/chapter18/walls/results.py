# app/domain/chapter18/walls/results.py
"""
Dataclasses de resultado para verificación de muros sísmicos §18.10.
"""
from dataclasses import dataclass, field
from typing import Optional, List

from ..results import (
    WallPierClassification,
    WallPierShearDesign,
    BoundaryElementResult,
    BoundaryZoneCheck,
    ShearAmplificationResult,
)


@dataclass
class WallClassificationResult:
    """Clasificación del muro según §18.10 y Tabla R18.10.1."""
    hw: float                   # Altura del muro (mm)
    lw: float                   # Longitud del muro (mm)
    tw: float                   # Espesor del muro (mm)
    hw_lw: float                # Relación altura/longitud
    lw_tw: float                # Relación longitud/espesor
    is_slender: bool            # hw/lw >= 2.0 (muro esbelto)
    is_wall_pier: bool          # lw/tw <= 6.0 (pilar de muro)
    requires_boundary_zones: bool  # Si requiere zonas de extremo §18.10.2.4
    aci_reference: str = "ACI 318-25 §18.10"


@dataclass
class WallReinforcementResult:
    """Verificación de refuerzo mínimo §18.10.2.1."""
    # Cuantías longitudinales (vertical)
    rho_l_min: float            # Cuantía mínima requerida
    rho_l_actual: float         # Cuantía actual
    rho_l_ok: bool

    # Cuantías transversales (horizontal)
    rho_t_min: float            # Cuantía mínima requerida
    rho_t_actual: float         # Cuantía actual
    rho_t_ok: bool

    # Espaciamiento
    spacing_max: float          # Espaciamiento máximo (mm)
    spacing_v_actual: float     # Espaciamiento vertical actual (mm)
    spacing_h_actual: float     # Espaciamiento horizontal actual (mm)
    spacing_ok: bool

    # Cortinas
    requires_double_curtain: bool
    double_curtain_reason: str
    has_double_curtain: bool

    # Requisito rho_l >= rho_t
    rho_l_ge_rho_t_required: bool
    rho_l_ge_rho_t_ok: bool

    is_ok: bool
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.10.2.1"


@dataclass
class WallShearResult:
    """Verificación de cortante §18.10.4."""
    # Demanda
    Vu: float                   # Cortante del análisis (tonf)
    Ve: float                   # Cortante de diseño amplificado (tonf)

    # Capacidad
    Vc: float                   # Resistencia del concreto (tonf)
    Vs: float                   # Resistencia del acero (tonf)
    Vn: float                   # Resistencia nominal (tonf)
    phi_Vn: float               # Resistencia de diseño (tonf)

    # Límite máximo
    Vn_max: float               # Límite §18.10.4.4 (tonf)
    Vn_max_ok: bool

    # Resultado
    dcr: float
    is_ok: bool

    # Amplificación (si aplica)
    amplification: Optional[ShearAmplificationResult] = None
    aci_reference: str = "ACI 318-25 §18.10.4"


@dataclass
class WallBoundaryResult:
    """Verificación de elementos de borde §18.10.6."""
    method_used: str            # "displacement" o "stress"
    requires_special: bool      # Si requiere elemento de borde especial

    # Resultados del método usado
    displacement_check: Optional[dict] = None
    stress_check: Optional[dict] = None

    # Dimensiones requeridas (si requiere)
    length_horizontal: float = 0  # Extensión horizontal (mm)
    vertical_extension: float = 0  # Extensión vertical (mm)

    # Confinamiento requerido
    Ash_sbc_required: float = 0   # Ash/(s*bc) requerido
    spacing_max: float = 0        # Espaciamiento máximo (mm)

    is_ok: bool = True
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.10.6"


@dataclass
class SeismicWallResult:
    """
    Resultado completo de verificación de muro sísmico especial §18.10.

    Orquesta todas las verificaciones aplicables:
    - Clasificación (Tabla R18.10.1)
    - Refuerzo mínimo (§18.10.2.1)
    - Cortante (§18.10.4)
    - Elementos de borde (§18.10.6)
    - Zonas de extremo (§18.10.2.4) si hw/lw >= 2.0
    - Verificaciones de pilar (§18.10.8) si es wall pier
    """
    classification: WallClassificationResult
    reinforcement: WallReinforcementResult
    shear: WallShearResult
    boundary: Optional[WallBoundaryResult] = None
    end_zones: Optional[BoundaryZoneCheck] = None
    wall_pier: Optional[WallPierClassification] = None

    is_ok: bool = True
    dcr_max: float = 0
    critical_check: str = ""
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.10"
