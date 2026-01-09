# app/domain/chapter18/results.py
"""
Dataclasses y enums para el capitulo 18 de ACI 318-25.

Centraliza todas las estructuras de datos para:
- Pilares de muro (piers)
- Elementos de borde (boundary_elements)
- Vigas de acople (coupling_beams)
- Amplificacion de cortante (amplification)
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


# =============================================================================
# ENUMS - Piers (Pilares de muro)
# =============================================================================

class WallPierCategory(Enum):
    """Categoria de pilar de muro segun Tabla R18.10.1."""
    WALL = "wall"              # Disenar como muro (18.10)
    COLUMN = "column"          # Disenar como columna especial (18.7)
    ALTERNATIVE = "alternative"  # Metodo alternativo (18.10.8.1)


class DesignMethod(Enum):
    """Metodo de diseno para el pilar."""
    SPECIAL_COLUMN = "special_column"  # Segun 18.7
    ALTERNATIVE = "alternative"        # Segun 18.10.8.1 alternativo
    WALL = "wall"                      # Segun 18.10 (muro)


# =============================================================================
# ENUMS - Boundary Elements (Elementos de borde)
# =============================================================================

class BoundaryElementMethod(Enum):
    """Metodo de verificacion de elementos de borde."""
    DISPLACEMENT = "displacement"  # 18.10.6.2
    STRESS = "stress"              # 18.10.6.3


# =============================================================================
# ENUMS - Coupling Beams (Vigas de acople)
# =============================================================================

class CouplingBeamType(Enum):
    """Tipo de viga de acoplamiento segun relacion ln/h."""
    LONG = "long"                      # ln/h >= 4, como viga de portico
    SHORT_HIGH_SHEAR = "short_high_shear"  # ln/h < 2 con Vu alto, diagonal obligatorio
    INTERMEDIATE = "intermediate"      # 2 <= ln/h < 4, diagonal o longitudinal


class ReinforcementType(Enum):
    """Tipo de refuerzo para viga de acoplamiento."""
    LONGITUDINAL = "longitudinal"  # Refuerzo convencional
    DIAGONAL = "diagonal"          # Refuerzo diagonal


class ConfinementOption(Enum):
    """Opcion de confinamiento para diagonales."""
    INDIVIDUAL = "individual"      # Opcion (c) - Confinamiento de diagonales individuales
    FULL_SECTION = "full_section"  # Opcion (d) - Confinamiento de seccion completa


# =============================================================================
# DATACLASSES - Piers (Pilares de muro)
# =============================================================================

@dataclass
class WallPierClassification:
    """Clasificacion del pilar de muro."""
    hw: float               # Altura del segmento (mm)
    lw: float               # Longitud del segmento (mm)
    bw: float               # Espesor del segmento (mm)
    hw_lw: float            # Relacion altura/longitud
    lw_bw: float            # Relacion longitud/espesor
    category: WallPierCategory
    design_method: DesignMethod
    requires_column_details: bool
    alternative_permitted: bool
    aci_reference: str
    # ACI 318-25 §18.7.2.1: Columnas sismicas requieren dimension >= 300mm
    column_min_thickness_ok: bool = True
    column_min_thickness_required: float = 0.0


@dataclass
class WallPierShearDesign:
    """Diseno por cortante del pilar de muro."""
    Vu: float               # Cortante ultimo (tonf)
    Ve: float               # Cortante de diseno (tonf)
    Omega_o: float          # Factor de sobrerresistencia
    use_capacity_design: bool
    phi_Vn: float           # Capacidad de corte (tonf)
    dcr: float              # Demand/Capacity ratio
    is_ok: bool
    aci_reference: str


@dataclass
class WallPierTransverseReinforcement:
    """Refuerzo transversal para pilar de muro."""
    requires_closed_hoops: bool
    hook_type: str          # "180°" para cortina simple
    spacing_max: float      # Espaciamiento maximo (mm)
    extension_above: float  # Extension arriba de altura libre (mm)
    extension_below: float  # Extension abajo de altura libre (mm)
    Ash_sbc_required: float  # Para metodo alternativo
    aci_reference: str


@dataclass
class WallPierBoundaryCheck:
    """Verificacion de elementos de borde para pilar."""
    requires_boundary: bool
    method_used: str        # "stress" segun 18.10.6.3
    sigma_max: float        # Esfuerzo maximo (MPa)
    sigma_limit: float      # Limite 0.2*f'c (MPa)
    aci_reference: str


@dataclass
class BoundaryZoneCheck:
    """
    Verificacion de refuerzo en zonas de extremo segun ACI 318-25 §18.10.2.4.

    Para muros/pilares con hw/lw >= 2.0 y seccion critica unica:
    - (a) rho >= 6*sqrt(f'c)/fy en extremos (0.15*lw x bw)
    - (b) Extension vertical >= max(lw, Mu/3Vu)
    - (c) No mas del 50% termina en una seccion
    """
    # Condiciones de aplicabilidad
    hw_lw: float                    # Relacion hw/lw
    applies: bool                   # True si hw/lw >= 2.0

    # Requisitos de cuantia (a)
    rho_min_boundary: float         # 6*sqrt(f'c)/fy (cuantia minima requerida)
    rho_actual_left: float          # Cuantia actual extremo izquierdo
    rho_actual_right: float         # Cuantia actual extremo derecho
    rho_left_ok: bool
    rho_right_ok: bool

    # Zona de extremo
    boundary_length: float          # 0.15 x lw (mm)
    boundary_width: float           # bw (mm)

    # Extension vertical (b)
    extension_required: float       # max(lw, Mu/3Vu) (mm)
    lw: float
    Mu_3Vu: float                   # Mu/(3xVu) en mm

    # Resultado global
    is_ok: bool
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.10.2.4"


@dataclass
class EdgePierCheck:
    """
    Verificacion de requisitos para pilares en borde de muro.

    Segun ACI 318-25 §18.10.8.2:
    - Proporcionar refuerzo horizontal en segmentos adyacentes
    - Disenar para transferir cortante del pilar
    """
    pier_Ve: float                      # Cortante del pilar (tonf)
    adjacent_capacity: float            # Capacidad de transferencia (tonf)
    transfer_ok: bool                   # Si la transferencia es adecuada
    required_transfer: float            # Transferencia requerida (tonf)
    aci_reference: str = "ACI 318-25 18.10.8.2"


@dataclass
class WallPierDesignResult:
    """Resultado completo del diseno del pilar de muro."""
    classification: WallPierClassification
    shear_design: WallPierShearDesign
    transverse: WallPierTransverseReinforcement
    boundary_check: Optional[WallPierBoundaryCheck]
    boundary_zone_check: Optional[BoundaryZoneCheck]
    edge_pier_check: Optional[EdgePierCheck] = None
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = ""


# =============================================================================
# DATACLASSES - Boundary Elements (Elementos de borde)
# =============================================================================

@dataclass
class DisplacementCheckResult:
    """Resultado de verificacion por metodo de desplazamiento."""
    delta_u: float              # Desplazamiento de diseno (mm)
    hwcs: float                 # Altura desde seccion critica (mm)
    lw: float                   # Longitud del muro (mm)
    c: float                    # Profundidad eje neutro (mm)
    drift_ratio: float          # delta_u / hwcs
    limit: float                # lw / (600 * c)
    check_value: float          # 1.5 * drift_ratio
    requires_special: bool       # Si requiere elemento de borde especial
    aci_reference: str


@dataclass
class StressCheckResult:
    """Resultado de verificacion por metodo de esfuerzos."""
    sigma_max: float            # Esfuerzo maximo de compresion (MPa)
    fc: float                   # Resistencia del hormigon (MPa)
    limit_require: float        # 0.2 * f'c
    limit_discontinue: float    # 0.15 * f'c
    requires_special: bool       # Si requiere elemento de borde especial
    can_discontinue: bool        # Si puede discontinuar elemento existente
    aci_reference: str


@dataclass
class BoundaryStressAnalysis:
    """
    Resultado de calculo de esfuerzos en bordes para verificacion de boundary elements.

    Usa formula: sigma = P/A +/- M*y/I

    Args:
        sigma_left: Esfuerzo borde izquierdo (MPa)
        sigma_right: Esfuerzo borde derecho (MPa)
        sigma_limit: Limite 0.2*f'c (MPa)
        Ag: Area bruta (mm2)
        Ig: Momento de inercia (mm4)
        y: Distancia al borde (mm)
    """
    sigma_left: float   # Esfuerzo borde izquierdo (MPa)
    sigma_right: float  # Esfuerzo borde derecho (MPa)
    sigma_limit: float  # Limite 0.2*f'c (MPa)
    Ag: float           # Area bruta (mm2)
    Ig: float           # Momento de inercia (mm4)
    y: float            # Distancia al borde (mm)

    @property
    def required_left(self) -> bool:
        """True si se requiere elemento de borde en el lado izquierdo."""
        return self.sigma_left >= self.sigma_limit

    @property
    def required_right(self) -> bool:
        """True si se requiere elemento de borde en el lado derecho."""
        return self.sigma_right >= self.sigma_limit


@dataclass
class BoundaryElementDimensions:
    """Dimensiones requeridas del elemento de borde."""
    length_horizontal: float    # Extension horizontal (mm)
    width_min: float           # Ancho minimo (mm)
    width_required: float      # Ancho requerido (mm)
    vertical_extension: float   # Extension vertical (mm)
    c: float                    # Profundidad eje neutro usada
    lw: float                   # Longitud del muro
    aci_reference: str


@dataclass
class BoundaryTransverseReinforcement:
    """Refuerzo transversal requerido para elemento de borde."""
    Ash_sbc_required: float     # Ash/(s*bc) requerido
    rho_s_required: float       # rho_s para espiral/aro circular
    spacing_max: float          # Espaciamiento maximo (mm)
    hx_max: float               # Espaciamiento hx maximo (mm)
    Ag: float                   # Area bruta
    Ach: float                  # Area del nucleo
    fc: float                   # f'c
    fyt: float                  # fy del refuerzo transversal
    aci_reference: str


@dataclass
class BoundaryElementResult:
    """Resultado completo de verificacion de elemento de borde."""
    method: BoundaryElementMethod
    displacement_check: Optional[DisplacementCheckResult]
    stress_check: Optional[StressCheckResult]
    requires_special: bool
    dimensions: Optional[BoundaryElementDimensions]
    transverse_reinforcement: Optional[BoundaryTransverseReinforcement]
    drift_capacity_check: Optional[dict]
    warnings: List[str]
    aci_reference: str


# =============================================================================
# DATACLASSES - Coupling Beams (Vigas de acople)
# =============================================================================

@dataclass
class CouplingBeamClassification:
    """Clasificacion de viga de acoplamiento."""
    ln: float               # Claro libre (mm)
    h: float                # Peralte de la viga (mm)
    ln_h_ratio: float       # Relacion ln/h
    beam_type: CouplingBeamType
    Vu: float               # Cortante ultimo (tonf)
    shear_threshold: float  # Umbral 4*lambda*sqrt(f'c)*Acw (tonf)
    reinforcement_options: List[ReinforcementType]
    aci_reference: str


@dataclass
class DiagonalShearResult:
    """Resultado de resistencia al cortante con refuerzo diagonal."""
    Avd: float              # Area de refuerzo en cada grupo diagonal (mm2)
    fy: float               # Fluencia del acero (MPa)
    alpha_deg: float        # Angulo de diagonales (grados)
    Vn_calc: float          # Vn calculado (tonf)
    Vn_max: float           # Vn maximo (tonf)
    Vn: float               # Vn final (tonf)
    phi_Vn: float           # Resistencia de diseno (tonf)
    aci_reference: str


@dataclass
class DiagonalConfinementResult:
    """Requisitos de confinamiento para diagonales."""
    confinement_option: ConfinementOption
    Ash_required: float          # Ash requerido (mm2)
    Ash_sbc_required: float      # Ash/(s*bc) requerido
    spacing_max: float           # Espaciamiento maximo (mm)
    spacing_perpendicular: float  # Espaciamiento perpendicular (mm)
    core_min_parallel: float     # Dimension minima paralela a bw
    core_min_other: float        # Dimension minima otros lados
    rho_perimeter: float         # Cuantia perimetral
    perimeter_spacing: float     # Espaciamiento perimetral
    aci_reference: str


@dataclass
class CouplingBeamDesignResult:
    """Resultado completo del diseno de viga de acoplamiento."""
    classification: CouplingBeamClassification
    reinforcement_type: ReinforcementType
    shear_result: Optional[DiagonalShearResult]
    confinement: Optional[DiagonalConfinementResult]
    Vu: float               # Demanda (tonf)
    phi_Vn: float           # Capacidad (tonf)
    dcr: float              # Demand/Capacity ratio
    is_ok: bool
    warnings: List[str]
    aci_reference: str


# =============================================================================
# DATACLASSES - Amplification (Amplificacion de cortante)
# =============================================================================

@dataclass
class ShearAmplificationResult:
    """Resultado de la amplificacion de cortante §18.10.3.3."""
    Vu_original: float      # Cortante original del analisis (tonf)
    Ve: float               # Cortante de diseno amplificado (tonf)
    Omega_v: float          # Factor de sobrerresistencia a flexion
    omega_v_dyn: float      # Factor de amplificacion dinamica
    amplification: float    # Factor total (Omega_v × omega_v_dyn)
    hwcs_lw: float          # Relacion hwcs/lw
    hn_ft: Optional[float]  # Altura del edificio en pies
    applies: bool           # Si aplica la amplificacion
    aci_reference: str


@dataclass
class ShearAmplificationFactors:
    """Factores de amplificacion segun Tabla 18.10.3.3.3."""
    Omega_v: float          # Factor de sobrerresistencia a flexion
    omega_v_dyn: float      # Factor de amplificacion dinamica
    combined: float         # Omega_v × omega_v_dyn
    hwcs_lw: float          # Relacion altura/longitud
    hn_ft: float            # Altura del edificio (pies)
    aci_reference: str


@dataclass
class SpecialWallRequirements:
    """Requisitos para muros estructurales especiales (ACI 318-25 §18.10.2)."""
    rho_l_min: float                    # Cuantia longitudinal minima
    rho_t_min: float                    # Cuantia transversal minima
    spacing_max_mm: float               # Espaciamiento maximo (mm)
    requires_double_curtain: bool       # Si requiere doble cortina
    double_curtain_reason: str          # Razon de doble cortina
    rho_l_ge_rho_t: bool               # Si aplica rho_l >= rho_t
    is_ok: bool                         # Si cumple todos los requisitos
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = ""
