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
    """
    Resultado simplificado de verificacion de esbeltez para servicios.

    Nota: La version completa con todos los parametros de calculo esta en
    app/domain/flexure/slenderness.py. Esta version simplificada se usa
    en servicios donde no se requieren todos los detalles del calculo.
    """
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

    # Para compatibilidad con version del dominio
    @property
    def buckling_factor(self) -> float:
        """Alias de reduction_factor para compatibilidad con dominio."""
        return self.reduction_factor


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


# =============================================================================
# VERIFICACIONES SISMICAS §18.6 (Vigas) y §18.7 (Columnas)
# =============================================================================

@dataclass
class SeismicBeamDimensionalResult:
    """Verificacion de limites dimensionales de vigas §18.6.2."""
    ln_d_ratio: float
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

    overall_ok: bool = True
    """True si todos los limites cumplen."""

    aci_reference: str = "ACI 318-25 §18.6.2"


@dataclass
class SeismicBeamLongitudinalResult:
    """Verificacion de refuerzo longitudinal de vigas §18.6.3."""
    rho_max: float
    """Cuantia maxima permitida."""

    rho_actual: float
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

    overall_ok: bool = True
    """True si todos los requisitos cumplen."""

    aci_reference: str = "ACI 318-25 §18.6.3"


@dataclass
class SeismicBeamTransverseResult:
    """Verificacion de refuerzo transversal de vigas §18.6.4."""
    s_hoop: float
    """Espaciamiento de estribos en zona de confinamiento (mm)."""

    s_max: float
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

    overall_ok: bool = True
    """True si todos los requisitos cumplen."""

    aci_reference: str = "ACI 318-25 §18.6.4"


@dataclass
class SeismicBeamShearResult:
    """Verificacion de cortante de vigas sismicas §18.6.5."""
    Mpr_left: float
    """Momento probable extremo izquierdo (tonf-m)."""

    Mpr_right: float
    """Momento probable extremo derecho (tonf-m)."""

    Ve: float
    """Cortante de diseno por capacidad (tonf): (Mpr1+Mpr2)/ln."""

    phi_Vn: float
    """Capacidad de cortante de diseno (tonf)."""

    Vc: float = 0.0
    """Contribucion del concreto (tonf). 0 si cortante sismico domina."""

    Vs: float = 0.0
    """Contribucion del acero (tonf)."""

    Vc_allowed: bool = True
    """True si se permite usar Vc (§18.6.5.2)."""

    sf: float = 1.0
    """Factor de seguridad (phi_Vn / Ve)."""

    status: str = "OK"
    """Estado: 'OK' o 'NO OK'."""

    aci_reference: str = "ACI 318-25 §18.6.5"


@dataclass
class SeismicBeamChecks:
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

    overall_ok: bool = True
    """True si todas las verificaciones pasan."""

    aci_reference: str = "ACI 318-25 §18.6"


@dataclass
class SeismicColumnDimensionalResult:
    """Verificacion de limites dimensionales de columnas §18.7.2."""
    b_min: float
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

    overall_ok: bool = True
    """True si todos los limites cumplen."""

    aci_reference: str = "ACI 318-25 §18.7.2"


@dataclass
class SeismicColumnStrongResult:
    """Verificacion columna fuerte-viga debil §18.7.3.2."""
    sum_Mnc: float
    """Suma de Mn de columnas en el nudo (tonf-m)."""

    sum_Mnb: float
    """Suma de Mn de vigas en el nudo (tonf-m)."""

    ratio: float
    """Relacion sum_Mnc / sum_Mnb."""

    ratio_required: float = 1.2
    """Minimo requerido: 1.2 (6/5) segun §18.7.3.2."""

    is_ok: bool = True
    """True si ratio >= 1.2."""

    exempt: bool = False
    """True si la columna esta exenta (discontinua arriba y Pu < 0.1*Ag*f'c)."""

    aci_reference: str = "ACI 318-25 §18.7.3.2"


@dataclass
class SeismicColumnLongitudinalResult:
    """Verificacion de refuerzo longitudinal de columnas §18.7.4."""
    rho: float
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

    overall_ok: bool = True
    """True si todos los requisitos cumplen."""

    aci_reference: str = "ACI 318-25 §18.7.4"


@dataclass
class SeismicColumnTransverseResult:
    """Verificacion de refuerzo transversal de columnas §18.7.5."""
    lo: float
    """Longitud de confinamiento (mm): max(h, lu/6, 450mm)."""

    s: float
    """Espaciamiento de estribos actual (mm)."""

    s_max: float
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

    overall_ok: bool = True
    """True si todos los requisitos cumplen."""

    aci_reference: str = "ACI 318-25 §18.7.5"


@dataclass
class SeismicColumnShearDetailedResult:
    """Verificacion de cortante de columnas sismicas §18.7.6."""
    Mpr_top: float
    """Momento probable en extremo superior (tonf-m)."""

    Mpr_bottom: float
    """Momento probable en extremo inferior (tonf-m)."""

    Ve: float
    """Cortante de diseno por capacidad (tonf): (Mpr_top + Mpr_bottom) / lu."""

    phi_Vn: float
    """Capacidad de cortante de diseno (tonf)."""

    Vc: float = 0.0
    """Contribucion del concreto (tonf). 0 si cortante sismico domina."""

    Vs: float = 0.0
    """Contribucion del acero (tonf)."""

    Vc_allowed: bool = True
    """True si se permite usar Vc (§18.7.6.2.1)."""

    sf: float = 1.0
    """Factor de seguridad (phi_Vn / Ve)."""

    status: str = "OK"
    """Estado: 'OK' o 'NO OK'."""

    aci_reference: str = "ACI 318-25 §18.7.6"


@dataclass
class SeismicColumnChecks:
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

    overall_ok: bool = True
    """True si todas las verificaciones pasan."""

    aci_reference: str = "ACI 318-25 §18.7"


# =============================================================================
# VERIFICACIONES DE MUROS §18.10
# =============================================================================

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
    # Verificaciones sismicas (vigas y columnas §18.6-18.7)
    # =========================================================================
    seismic_beam: Optional[SeismicBeamChecks] = None
    """Verificaciones sismicas para vigas §18.6."""

    seismic_column: Optional[SeismicColumnChecks] = None
    """Verificaciones sismicas para columnas §18.7."""

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
