# app/services/analysis/results/common.py
"""
Dataclasses comunes de resultado para verificacion de elementos estructurales.

Incluye:
- SlendernessResult: Verificacion de esbeltez
- FlexureResult: Verificacion de flexion/flexocompresion
- BidirectionalShearResult: Verificacion de cortante bidireccional
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SlendernessResult:
    """
    Resultado simplificado de verificacion de esbeltez para servicios.

    Implementa magnificacion de momentos segun ACI 318-25 §6.6.4:
    Mc = delta_ns * Mu

    Nota: La version completa con todos los parametros de calculo esta en
    app/domain/flexure/slenderness.py. Esta version simplificada se usa
    en servicios donde no se requieren todos los detalles del calculo.
    """
    lambda_ratio: float
    """Relacion de esbeltez k*lu/r."""

    is_slender: bool
    """True si supera limite de esbeltez (22 para ACI 318-25)."""

    delta_ns: float
    """Factor de magnificacion de momentos (>= 1.0). ACI 318-25 §6.6.4.5."""

    k: float = 1.0
    """Factor de longitud efectiva usado."""

    lu: float = 0.0
    """Longitud no arriostrada (mm)."""

    @property
    def magnification_pct(self) -> float:
        """Porcentaje de magnificacion del momento (para display)."""
        if self.delta_ns <= 1.0:
            return 0.0
        return (self.delta_ns - 1.0) * 100


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


# Alias para compatibilidad.
# Nota: domain/shear/results.py tiene su propio ShearResult para cortante
# unidireccional. Este BidirectionalShearResult es para verificacion con V2+V3.
ShearResult = BidirectionalShearResult
