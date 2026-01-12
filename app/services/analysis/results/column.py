# app/services/analysis/results/column.py
"""
Dataclasses de resultado para verificacion sismica de columnas §18.7.

ACI 318-25 Chapter 18: Earthquake-Resistant Structures
Section 18.7: Columns of Special Moment Frames
"""
from dataclasses import dataclass
from typing import Optional

from .common import AciVerificationResult


@dataclass
class SeismicColumnDimensionalResult(AciVerificationResult):
    """Verificacion de limites dimensionales de columnas §18.7.2."""
    b_min: float = 0.0
    """Dimension minima de la seccion (mm)."""

    b_min_req: float = 300.0
    """Minimo requerido: 300mm (12 in) segun §18.7.2.1(a)."""

    b_min_ok: bool = True
    """True si b >= 300mm."""

    aspect_ratio: float = 1.0
    """Relacion de aspecto (menor/mayor)."""

    aspect_ratio_min: float = 0.4
    """Minimo requerido: 0.4 segun §18.7.2.1(b)."""

    aspect_ratio_ok: bool = True
    """True si aspect_ratio >= 0.4."""

    aci_reference: str = "ACI 318-25 §18.7.2"


@dataclass
class SeismicColumnStrongResult(AciVerificationResult):
    """Verificacion columna fuerte-viga debil §18.7.3.2."""
    sum_Mnc: float = 0.0
    """Suma de Mn de columnas en el nudo (tonf-m)."""

    sum_Mnb: float = 0.0
    """Suma de Mn de vigas en el nudo (tonf-m)."""

    ratio: float = 0.0
    """Relacion sum_Mnc / sum_Mnb."""

    ratio_required: float = 1.2
    """Minimo requerido: 1.2 (6/5) segun §18.7.3.2."""

    is_ok: bool = True
    """True si ratio >= 1.2."""

    exempt: bool = False
    """True si la columna esta exenta (discontinua arriba y Pu < 0.1*Ag*f'c)."""

    aci_reference: str = "ACI 318-25 §18.7.3.2"


@dataclass
class SeismicColumnLongitudinalResult(AciVerificationResult):
    """Verificacion de refuerzo longitudinal de columnas §18.7.4."""
    rho: float = 0.0
    """Cuantia longitudinal actual."""

    rho_min: float = 0.01
    """Cuantia minima: 0.01 (1%) segun §18.7.4.1."""

    rho_max: float = 0.06
    """Cuantia maxima: 0.06 (6%) segun §18.7.4.1."""

    rho_ok: bool = True
    """True si 0.01 <= rho <= 0.06."""

    n_bars_min: int = 6
    """Numero minimo de barras (6 para hoops circulares)."""

    n_bars_ok: bool = True
    """True si numero de barras cumple."""

    aci_reference: str = "ACI 318-25 §18.7.4"


@dataclass
class SeismicColumnTransverseResult(AciVerificationResult):
    """Verificacion de refuerzo transversal de columnas §18.7.5."""
    lo: float = 0.0
    """Longitud de confinamiento (mm): max(h, lu/6, 450mm)."""

    s: float = 0.0
    """Espaciamiento de estribos actual (mm)."""

    s_max: float = 0.0
    """Espaciamiento maximo en lo (mm): min(h/4, 6db, so)."""

    s_ok: bool = True
    """True si s <= s_max."""

    hx: float = 0.0
    """Separacion maxima entre barras soportadas (mm)."""

    hx_max: float = 350.0
    """Limite hx (mm): 350mm o 200mm segun condiciones."""

    hx_ok: bool = True
    """True si hx <= hx_max."""

    Ash_provided: float = 0.0
    """Area de confinamiento provista (mm2)."""

    Ash_required: float = 0.0
    """Area de confinamiento requerida (mm2) segun Tabla 18.7.5.4."""

    Ash_ok: bool = True
    """True si Ash_provided >= Ash_required."""

    aci_reference: str = "ACI 318-25 §18.7.5"


@dataclass
class SeismicColumnShearDetailedResult(AciVerificationResult):
    """Verificacion de cortante de columnas sismicas §18.7.6."""
    Mpr_top: float = 0.0
    """Momento probable en extremo superior (tonf-m)."""

    Mpr_bottom: float = 0.0
    """Momento probable en extremo inferior (tonf-m)."""

    Ve: float = 0.0
    """Cortante de diseno por capacidad (tonf): (Mpr_top + Mpr_bottom) / lu."""

    phi_Vn: float = 0.0
    """Capacidad de cortante de diseno (tonf)."""

    Vc: float = 0.0
    """Contribucion del concreto (tonf). 0 si cortante sismico domina."""

    Vs: float = 0.0
    """Contribucion del acero (tonf)."""

    Vc_allowed: bool = True
    """True si se permite usar Vc (§18.7.6.2.1)."""

    sf: float = 1.0
    """Factor de seguridad (phi_Vn / Ve)."""

    aci_reference: str = "ACI 318-25 §18.7.6"


@dataclass
class SeismicColumnChecks(AciVerificationResult):
    """Resultado completo de verificacion sismica de columnas §18.7."""
    dimensional: Optional[SeismicColumnDimensionalResult] = None
    """Limites dimensionales §18.7.2."""

    strong_column: Optional[SeismicColumnStrongResult] = None
    """Columna fuerte-viga debil §18.7.3.2."""

    longitudinal: Optional[SeismicColumnLongitudinalResult] = None
    """Refuerzo longitudinal §18.7.4."""

    transverse: Optional[SeismicColumnTransverseResult] = None
    """Refuerzo transversal §18.7.5."""

    shear: Optional[SeismicColumnShearDetailedResult] = None
    """Cortante §18.7.6."""

    seismic_category: str = "SPECIAL"
    """Categoria sismica: 'SPECIAL', 'INTERMEDIATE', 'ORDINARY'."""

    aci_reference: str = "ACI 318-25 §18.7"
