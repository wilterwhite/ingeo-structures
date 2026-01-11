# app/services/analysis/results/wall.py
"""
Dataclasses de resultado para verificacion sismica de muros §18.10.

ACI 318-25 Chapter 18: Earthquake-Resistant Structures
Section 18.10: Special Structural Walls
"""
from dataclasses import dataclass
from typing import Dict, Optional, Any


@dataclass
class WallClassification:
    """Clasificacion de muro segun §18.10.8."""
    type: str
    """Tipo de clasificacion."""

    lw_tw: float
    """Relacion ancho/espesor."""

    hw_lw: float
    """Relacion altura/ancho."""

    aci_section: str
    """Seccion ACI aplicable."""

    is_wall_pier: bool
    """True si es wall pier (lw/tw <= 6.0)."""


@dataclass
class BoundaryResult:
    """Resultado de verificacion de elementos de borde §18.10.6."""
    required: bool
    """True si se requieren elementos de borde."""

    method: str
    """Metodo de verificacion: 'displacement' o 'stress'."""

    sigma_max: float = 0.0
    """Esfuerzo maximo (MPa)."""

    sigma_limit: float = 0.0
    """Limite de esfuerzo (MPa)."""

    length_mm: float = 0.0
    """Longitud requerida de elemento de borde (mm)."""

    status: str = "OK"
    """Estado de verificacion."""

    aci_reference: str = "ACI 318-25 §18.10.6"


@dataclass
class EndZonesResult:
    """Resultado de verificacion de zonas de extremo §18.10.2.4."""
    applies: bool
    """True si aplica (hw/lw >= 2.0)."""

    hw_lw: float = 0.0
    """Relacion hw/lw."""

    rho_min: float = 0.0
    """Cuantia minima requerida."""

    rho_left: float = 0.0
    """Cuantia en zona izquierda."""

    rho_right: float = 0.0
    """Cuantia en zona derecha."""

    left_ok: bool = True
    """True si zona izquierda cumple."""

    right_ok: bool = True
    """True si zona derecha cumple."""

    status: str = "OK"
    """Estado general."""

    length_mm: float = 0.0
    """Longitud de zona de extremo (mm)."""


@dataclass
class MinReinforcementResult:
    """Resultado de verificacion de cuantia minima §18.10.2.1."""
    rho_v_min: float
    """Cuantia vertical minima requerida."""

    rho_h_min: float
    """Cuantia horizontal minima requerida."""

    rho_v_actual: float
    """Cuantia vertical actual."""

    rho_h_actual: float
    """Cuantia horizontal actual."""

    rho_v_ok: bool
    """True si cuantia vertical cumple."""

    rho_h_ok: bool
    """True si cuantia horizontal cumple."""

    spacing_max: float = 457.0
    """Espaciamiento maximo permitido (mm)."""

    spacing_v_ok: bool = True
    """True si espaciamiento vertical cumple."""

    spacing_h_ok: bool = True
    """True si espaciamiento horizontal cumple."""

    status: str = "OK"
    """Estado general."""


@dataclass
class WallChecks:
    """Verificaciones adicionales para muros §18.10."""
    classification: Optional[WallClassification] = None
    """Clasificacion §18.10.8."""

    amplification: Optional[Dict[str, Any]] = None
    """Amplificacion de cortante §18.10.3.3."""

    boundary: Optional[BoundaryResult] = None
    """Elementos de borde §18.10.6."""

    end_zones: Optional[EndZonesResult] = None
    """Zonas de extremo §18.10.2.4."""

    min_reinforcement: Optional[MinReinforcementResult] = None
    """Cuantia minima §18.10.2.1."""
