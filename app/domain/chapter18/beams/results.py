# app/domain/chapter18/beams/results.py
"""
Dataclasses para resultados de vigas sísmicas ACI 318-25.

Incluye resultados para:
- §18.3.2: Vigas de pórticos ordinarios
- §18.4.2: Vigas de pórticos intermedios
- §18.6: Vigas de pórticos especiales
"""
from dataclasses import dataclass, field
from typing import Optional, List

from ..common import SeismicCategory


@dataclass
class BeamDimensionalLimitsResult:
    """
    Resultado de verificación de límites dimensionales §18.6.2.

    Requisitos para vigas especiales:
    - (a) ln >= 4d
    - (b) bw >= max(0.3h, 254mm)
    - (c) Proyección más allá de columna <= min(c2, 0.75*c1)
    """
    # Luz libre
    ln: float                       # Luz libre (mm)
    d: float                        # Profundidad efectiva (mm)
    ln_min: float                   # 4*d
    ln_ok: bool

    # Ancho
    bw: float                       # Ancho del alma (mm)
    h: float                        # Altura total (mm)
    bw_min: float                   # max(0.3h, 254mm)
    bw_ok: bool

    # Proyección (opcional)
    projection: float = 0           # Proyección más allá de columna (mm)
    projection_max: float = 0       # min(c2, 0.75*c1)
    projection_ok: bool = True

    is_ok: bool = False
    aci_reference: str = "ACI 318-25 §18.6.2"


@dataclass
class BeamLongitudinalResult:
    """
    Resultado de verificación de refuerzo longitudinal §18.6.3.

    Requisitos:
    - Mínimo 2 barras continuas superior e inferior
    - ρ <= ρmax (0.025 G60, 0.020 G80)
    - M+ en nudo >= 0.5*M- en nudo
    - M+/M- en cualquier sección >= 0.25*Mmax en nudo
    """
    # Cuantía
    As_top: float                   # Área refuerzo superior (mm²)
    As_bottom: float                # Área refuerzo inferior (mm²)
    rho_top: float                  # Cuantía superior
    rho_bottom: float               # Cuantía inferior
    rho_max: float                  # Límite máximo
    rho_ok: bool

    # Número de barras
    n_bars_top: int
    n_bars_bottom: int
    n_bars_min: int = 2
    n_bars_ok: bool = True

    # Relaciones de momento
    Mn_pos_face: float = 0          # M+ en cara del nudo (tonf-m)
    Mn_neg_face: float = 0          # M- en cara del nudo (tonf-m)
    moment_ratio_face: float = 0    # M+/M- en cara
    moment_ratio_face_required: float = 0.5  # Para especial
    moment_ratio_face_ok: bool = True

    Mn_min_section: float = 0       # M mínimo en cualquier sección
    Mn_max_face: float = 0          # M máximo en cara de nudo
    moment_ratio_section: float = 0  # Mn_min/Mn_max
    moment_ratio_section_required: float = 0.25  # Para especial
    moment_ratio_section_ok: bool = True

    is_ok: bool = False
    aci_reference: str = "ACI 318-25 §18.6.3"


@dataclass
class BeamTransverseResult:
    """
    Resultado de verificación de refuerzo transversal §18.6.4.

    Requisitos:
    - Hoops en 2h desde cara de columna
    - Espaciamiento s <= min(d/4, 152mm, 6*db G60, 5*db G80)
    - Primer hoop <= 51mm de cara de columna
    - Fuera de zona: s <= d/2
    """
    # Longitud de zona de hoops
    zone_length: float              # 2*h (mm)
    h: float                        # Altura de la viga (mm)

    # Espaciamiento en zona
    s_in_zone: float                # Espaciamiento provisto en zona (mm)
    s_max_zone: float               # Espaciamiento máximo en zona (mm)
    s_zone_ok: bool

    # Primer hoop
    first_hoop_distance: float      # Distancia del primer hoop (mm)
    first_hoop_max: float           # 51mm (2")
    first_hoop_ok: bool

    # Fuera de zona
    s_outside_zone: float           # Espaciamiento fuera de zona (mm)
    s_max_outside: float            # d/2
    s_outside_ok: bool

    # Soporte lateral
    hx_provided: float = 0          # Espaciamiento entre barras soportadas (mm)
    hx_max: float = 356             # 14" = 356mm
    hx_ok: bool = True

    is_ok: bool = False
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.6.4"


@dataclass
class BeamShearResult:
    """
    Resultado de verificación de cortante §18.6.5.

    Diseño por capacidad:
    - Ve = (Mpr1 + Mpr2)/ln ± wu*ln/2
    - Vc = 0 si: Ve >= 0.5*Vu Y Pu < Ag*f'c/20
    """
    # Cortante de diseño
    Ve: float                       # Cortante por capacidad (tonf)
    Vu: float                       # Cortante del análisis (tonf)
    Vu_design: float                # max(Ve, Vu)

    # Capacidad
    Vc: float                       # Contribución del concreto (tonf)
    Vs: float                       # Contribución del acero (tonf)
    phi_Vn: float                   # Capacidad de diseño (tonf)

    # DCR
    dcr: float
    is_ok: bool

    # Condición Vc = 0
    Vc_is_zero: bool = False
    seismic_shear_dominates: bool = False  # Ve >= 0.5*Vu
    low_axial: bool = True                 # Pu < Ag*f'c/20 (vigas típicamente)

    aci_reference: str = "ACI 318-25 §18.6.5"


@dataclass
class SeismicBeamResult:
    """
    Resultado completo de verificación de viga sísmica.

    Agrupa todos los checks según la categoría sísmica:
    - SPECIAL: §18.6 (todos los checks)
    - INTERMEDIATE: §18.4.2 (checks reducidos)
    - ORDINARY: §18.3.2 (requisitos mínimos)
    """
    category: SeismicCategory

    # Verificaciones (None si no aplica para la categoría)
    dimensional_limits: Optional[BeamDimensionalLimitsResult] = None
    longitudinal: Optional[BeamLongitudinalResult] = None
    transverse: Optional[BeamTransverseResult] = None
    shear: Optional[BeamShearResult] = None

    # Resultado global
    is_ok: bool = False
    dcr_max: float = 0              # DCR máximo de todas las verificaciones
    critical_check: str = ""        # Nombre del check crítico
    warnings: List[str] = field(default_factory=list)

    @property
    def aci_reference(self) -> str:
        """Referencia ACI según categoría."""
        return self.category.beam_section
