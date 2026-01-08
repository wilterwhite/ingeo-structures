# app/services/analysis/verification_result.py
"""
Dataclasses de resultado para verificacion de elementos estructurales.

Define estructuras de datos unificadas para todos los tipos de elementos
(Beam, Column, Pier).
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

from .element_classifier import ElementType


@dataclass
class SlendernessResult:
    """Resultado de verificacion de esbeltez."""
    lambda_ratio: float
    """Relacion de esbeltez k*lu/r."""

    is_slender: bool
    """True si supera limite de esbeltez (22 para ACI 318-25)."""

    reduction_factor: float
    """Factor de reduccion por pandeo (1.0 si no es esbelto)."""

    k: float = 1.0
    """Factor de longitud efectiva usado."""

    lu: float = 0.0
    """Longitud no arriostrada (mm)."""


@dataclass
class FlexureResult:
    """Resultado de verificacion de flexion/flexocompresion."""
    sf: float
    """Factor de seguridad (phi_Mn / Mu)."""

    status: str
    """Estado: 'OK' o 'NO OK'."""

    design_type: str
    """Tipo de diseno: 'pure_flexure' o 'flexocompression'."""

    phi_Mn: float
    """Capacidad de momento de diseno (tonf-m)."""

    Mu: float
    """Momento ultimo demandado (tonf-m)."""

    Pu: float
    """Carga axial en combinacion critica (tonf)."""

    critical_combo: str
    """Nombre de la combinacion critica."""

    # Campos adicionales
    phi_Mn_at_Pu: float = 0.0
    """Capacidad de momento a Pu critico (tonf-m)."""

    phi_Pn_max: float = 0.0
    """Capacidad axial maxima de diseno (tonf)."""

    exceeds_axial: bool = False
    """True si Pu excede phi_Pn_max."""

    has_tension: bool = False
    """True si hay traccion neta en alguna combinacion."""

    has_significant_axial: bool = False
    """True si Pu >= Ag*f'c/10 (vigas con axial significativo)."""

    slenderness: Optional[SlendernessResult] = None
    """Resultado de esbeltez si aplica."""

    warning: str = ""
    """Advertencia adicional."""

    aci_reference: str = ""
    """Referencia ACI 318-25 aplicable."""


@dataclass
class BidirectionalShearResult:
    """
    Resultado de verificacion de cortante bidireccional (V2 + V3).

    Para verificacion unidireccional, usar ShearResult de domain/shear/results.py.
    """
    sf: float
    """Factor de seguridad general."""

    status: str
    """Estado: 'OK' o 'NO OK'."""

    method: str
    """Metodo usado: 'simple', 'srss', 'amplified'."""

    critical_combo: str
    """Combinacion critica."""

    # Direccion 2 (siempre presente)
    phi_Vn_2: float
    """Capacidad en direccion 2 (tonf)."""

    Vu_2: float
    """Demanda en direccion 2 (tonf)."""

    dcr_2: float
    """DCR en direccion 2."""

    # Direccion 3 (opcional para vigas)
    phi_Vn_3: Optional[float] = None
    """Capacidad en direccion 3 (tonf)."""

    Vu_3: Optional[float] = None
    """Demanda en direccion 3 (tonf)."""

    dcr_3: Optional[float] = None
    """DCR en direccion 3."""

    # Combinado SRSS (solo si method != 'simple')
    dcr_combined: Optional[float] = None
    """DCR combinado sqrt(dcr_2^2 + dcr_3^2)."""

    sf_combined: Optional[float] = None
    """SF combinado (1/dcr_combined)."""

    # Componentes de capacidad
    Vc: float = 0.0
    """Contribucion del concreto (tonf)."""

    Vs: float = 0.0
    """Contribucion del acero (tonf)."""

    Vs_max: float = 0.0
    """Limite de Vs (tonf)."""

    # Amplificacion (muros)
    Ve: Optional[float] = None
    """Cortante amplificado (tonf)."""

    omega_v: Optional[float] = None
    """Factor de amplificacion Omega_v."""

    aci_reference: str = "ACI 318-25 §22.5"
    """Referencia ACI 318-25."""


# Alias para uso en ElementVerificationResult y servicios de verificacion.
# Nota: domain/shear/results.py tiene su propio ShearResult para cortante
# unidireccional. Este BidirectionalShearResult es para verificacion con V2+V3.
ShearResult = BidirectionalShearResult


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


@dataclass
class ElementVerificationResult:
    """
    Resultado unificado de verificacion para cualquier elemento estructural.

    Contiene los resultados de todas las verificaciones aplicadas segun
    el tipo de elemento (Beam, Column, Pier).
    """
    element_type: ElementType
    """Tipo de elemento clasificado."""

    # =========================================================================
    # Verificaciones base (todos los elementos)
    # =========================================================================
    flexure: FlexureResult
    """Resultado de flexion/flexocompresion."""

    shear: ShearResult
    """Resultado de cortante."""

    # =========================================================================
    # Estado general
    # =========================================================================
    overall_status: str
    """Estado general: 'OK' o 'NO OK'."""

    overall_sf: float
    """Factor de seguridad minimo entre todas las verificaciones."""

    # =========================================================================
    # Verificaciones adicionales (muros)
    # =========================================================================
    wall_checks: Optional[WallChecks] = None
    """Verificaciones adicionales para muros §18.10."""

    # =========================================================================
    # Extras
    # =========================================================================
    proposal: Optional[Dict[str, Any]] = None
    """Propuesta de diseno si falla o sobrediseno."""

    pm_plot: Optional[str] = None
    """Grafico P-M en base64."""

    element_info: Dict[str, Any] = field(default_factory=dict)
    """Informacion del elemento (dimensiones, materiales, etc.)."""

    @property
    def is_ok(self) -> bool:
        """True si todas las verificaciones pasan."""
        return self.overall_status == "OK"

    @property
    def flexure_ok(self) -> bool:
        """True si flexion pasa."""
        return self.flexure.status == "OK"

    @property
    def shear_ok(self) -> bool:
        """True si cortante pasa."""
        return self.shear.status == "OK"

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario para serializacion."""
        from dataclasses import asdict
        return asdict(self)
