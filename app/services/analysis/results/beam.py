# app/services/analysis/results/beam.py
"""
Dataclasses de resultado para verificacion sismica de vigas §18.6.

ACI 318-25 Chapter 18: Earthquake-Resistant Structures
Section 18.6: Beams of Special Moment Frames
"""
from dataclasses import dataclass
from typing import Optional

from .common import AciVerificationResult


@dataclass
class SeismicBeamDimensionalResult(AciVerificationResult):
    """Verificacion de limites dimensionales de vigas §18.6.2."""
    ln_d_ratio: float = 0.0
    """Relacion luz libre / peralte efectivo."""

    ln_d_min: float = 4.0
    """Minimo requerido (4.0 para §18.6.2.1(a))."""

    ln_d_ok: bool = True
    """True si ln/d >= 4.0."""

    bw: float = 0.0
    """Ancho de la viga (mm)."""

    bw_min: float = 0.0
    """Ancho minimo requerido (mm): max(0.3h, 254mm)."""

    bw_ok: bool = True
    """True si bw >= bw_min."""

    projection_ok: bool = True
    """True si proyeccion lateral cumple §18.6.2.1(c)."""

    aci_reference: str = "ACI 318-25 §18.6.2"


@dataclass
class SeismicBeamLongitudinalResult(AciVerificationResult):
    """Verificacion de refuerzo longitudinal de vigas §18.6.3."""
    rho_max: float = 0.0
    """Cuantia maxima permitida."""

    rho_actual: float = 0.0
    """Cuantia actual."""

    rho_ok: bool = True
    """True si rho <= rho_max."""

    As_min_top: float = 0.0
    """Area minima superior (mm2)."""

    As_min_bottom: float = 0.0
    """Area minima inferior (mm2)."""

    M_pos_ratio: float = 0.0
    """Relacion M+/M- en cara de nudo."""

    M_pos_ratio_ok: bool = True
    """True si M+ >= 0.5*M- (§18.6.3.2(a))."""

    M_any_ratio: float = 0.0
    """Relacion M_any/M_max."""

    M_any_ratio_ok: bool = True
    """True si M_any >= 0.25*M_max (§18.6.3.2(b))."""

    aci_reference: str = "ACI 318-25 §18.6.3"


@dataclass
class SeismicBeamTransverseResult(AciVerificationResult):
    """Verificacion de refuerzo transversal de vigas §18.6.4."""
    s_hoop: float = 0.0
    """Espaciamiento de estribos en zona de confinamiento (mm)."""

    s_max: float = 0.0
    """Espaciamiento maximo permitido (mm): min(d/4, 6db, 150mm)."""

    s_ok: bool = True
    """True si s <= s_max."""

    hx: float = 0.0
    """Separacion maxima entre barras soportadas (mm)."""

    hx_max: float = 350.0
    """Limite hx (mm): 350mm (14 in) segun §18.6.4.4."""

    hx_ok: bool = True
    """True si hx <= hx_max."""

    first_hoop_ok: bool = True
    """True si primer estribo <= 50mm de cara de columna."""

    confinement_length: float = 0.0
    """Longitud de confinamiento requerida (mm): 2h."""

    aci_reference: str = "ACI 318-25 §18.6.4"


@dataclass
class SeismicBeamShearResult(AciVerificationResult):
    """Verificacion de cortante de vigas sismicas §18.6.5."""
    Mpr_left: float = 0.0
    """Momento probable extremo izquierdo (tonf-m)."""

    Mpr_right: float = 0.0
    """Momento probable extremo derecho (tonf-m)."""

    Ve: float = 0.0
    """Cortante de diseno por capacidad (tonf): (Mpr1+Mpr2)/ln."""

    phi_Vn: float = 0.0
    """Capacidad de cortante de diseno (tonf)."""

    Vc: float = 0.0
    """Contribucion del concreto (tonf). 0 si cortante sismico domina."""

    Vs: float = 0.0
    """Contribucion del acero (tonf)."""

    Vc_allowed: bool = True
    """True si se permite usar Vc (§18.6.5.2)."""

    sf: float = 1.0
    """Factor de seguridad (phi_Vn / Ve)."""

    aci_reference: str = "ACI 318-25 §18.6.5"


@dataclass
class SeismicBeamChecks(AciVerificationResult):
    """Resultado completo de verificacion sismica de vigas §18.6."""
    dimensional: Optional[SeismicBeamDimensionalResult] = None
    """Limites dimensionales §18.6.2."""

    longitudinal: Optional[SeismicBeamLongitudinalResult] = None
    """Refuerzo longitudinal §18.6.3."""

    transverse: Optional[SeismicBeamTransverseResult] = None
    """Refuerzo transversal §18.6.4."""

    shear: Optional[SeismicBeamShearResult] = None
    """Cortante §18.6.5."""

    seismic_category: str = "SPECIAL"
    """Categoria sismica: 'SPECIAL', 'INTERMEDIATE', 'ORDINARY'."""

    aci_reference: str = "ACI 318-25 §18.6"
