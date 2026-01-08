# app/domain/chapter18/columns/results.py
"""
Dataclasses para resultados de columnas sísmicas ACI 318-25.

Incluye resultados para:
- §18.3.3: Columnas de pórticos ordinarios
- §18.4.3: Columnas de pórticos intermedios
- §18.7: Columnas de pórticos especiales
"""
from dataclasses import dataclass, field
from typing import Optional, List

from ..common import SeismicCategory


@dataclass
class ColumnShearCapacity:
    """
    Capacidad de cortante de columna en una dirección.

    Según ACI 318-25 §22.5 y §18.7.6:
    - Vc = 0.17 * lambda * sqrt(f'c) * bw * d  [§22.5.5.1]
    - Vs = Av * fyt * d / s                    [§22.5.10.5.3]
    - Vn = Vc + Vs
    - phi_Vn = phi * Vn (phi = 0.75)

    Unidades: tonf
    """
    Vc: float               # Contribución del concreto (tonf)
    Vs: float               # Contribución del acero (tonf)
    Vn: float               # Resistencia nominal (tonf)
    phi_Vn: float           # Resistencia de diseño (tonf)


@dataclass
class SeismicColumnShearResult:
    """
    Resultado de verificación de cortante para columna sísmica.

    Según ACI 318-25 §18.7.6:
    - Ve = (Mpr_top + Mpr_bottom) / lu  [§18.7.6.1]
    - Vc = 0 si: (a) Ve >= 0.5*Vu Y (b) Pu < Ag*f'c/20 [§18.7.6.2.1]

    Unidades:
    - Fuerzas: tonf
    - Momentos: tonf-m
    """
    # Resultado general
    dcr: float                      # Demand/Capacity ratio (máximo combinado)
    is_ok: bool                     # True si dcr <= 1.0

    # Combinación crítica
    critical_combo: str             # Nombre de la combinación crítica
    Vu_V2: float                    # Cortante último en V2 (tonf)
    Vu_V3: float                    # Cortante último en V3 (tonf)

    # Capacidades
    phi_Vn_V2: float                # Capacidad en V2 (tonf)
    phi_Vn_V3: float                # Capacidad en V3 (tonf)
    capacity_V2: Optional[ColumnShearCapacity] = None
    capacity_V3: Optional[ColumnShearCapacity] = None

    # Diseño por capacidad (§18.7.6.1)
    Ve: float = 0                   # Cortante por capacidad (tonf)
    uses_capacity_design: bool = False

    # Condición Vc = 0 (§18.7.6.2.1)
    Vc_is_zero: bool = False        # True si aplica Vc = 0
    Pu_critical: float = 0          # Carga axial crítica (tonf)

    # Referencia
    aci_reference: str = "ACI 318-25 §18.7.6"


@dataclass
class DimensionalLimitsResult:
    """
    Resultado de verificación de límites dimensionales §18.7.2.

    Requisitos:
    - (a) Dimensión mínima >= 300mm (12")
    - (b) Relación de aspecto >= 0.4
    """
    min_dimension: float            # Dimensión mínima de la sección (mm)
    min_dimension_required: float   # 300mm para especial
    min_dimension_ok: bool

    aspect_ratio: float             # b/h (menor/mayor)
    aspect_ratio_required: float    # 0.4 para especial
    aspect_ratio_ok: bool

    is_ok: bool
    aci_reference: str = "ACI 318-25 §18.7.2"


@dataclass
class StrongColumnResult:
    """
    Resultado de verificación columna fuerte-viga débil §18.7.3.2.

    ΣMnc >= (6/5) ΣMnb

    Debe verificarse para momentos de viga en ambas direcciones.
    """
    sum_Mnc: float                  # Suma de Mn de columnas en el nudo (tonf-m)
    sum_Mnb: float                  # Suma de Mn de vigas en el nudo (tonf-m)
    ratio: float                    # ΣMnc / ΣMnb
    ratio_required: float           # 1.2 (6/5)
    is_ok: bool
    direction: str                  # "V2" o "V3"
    aci_reference: str = "ACI 318-25 §18.7.3.2"


@dataclass
class LongitudinalReinforcementResult:
    """
    Resultado de verificación de refuerzo longitudinal §18.7.4.

    Requisitos:
    - 0.01*Ag <= Ast <= 0.06*Ag
    - Mínimo 6 barras para hoops circulares
    """
    Ast: float                      # Área de refuerzo longitudinal (mm²)
    Ag: float                       # Área bruta (mm²)
    rho: float                      # Cuantía Ast/Ag

    rho_min: float                  # 0.01
    rho_max: float                  # 0.06
    rho_min_ok: bool
    rho_max_ok: bool

    n_bars: int                     # Número de barras
    n_bars_min: int                 # 6 para circular, 4 para rectangular
    n_bars_ok: bool

    is_ok: bool
    aci_reference: str = "ACI 318-25 §18.7.4"


@dataclass
class TransverseReinforcementResult:
    """
    Resultado de verificación de refuerzo transversal §18.7.5.

    Incluye:
    - Longitud ℓo de confinamiento
    - Espaciamiento máximo
    - Cantidad de refuerzo Ash/sbc o ρs
    """
    # Longitud de confinamiento
    lo: float                       # Longitud ℓo calculada (mm)
    lo_required: float              # max(h, lu/6, 457mm)

    # Espaciamiento
    s_provided: float               # Espaciamiento provisto (mm)
    s_max: float                    # Espaciamiento máximo permitido (mm)
    s_ok: bool

    # Soporte lateral
    hx_provided: float              # Espaciamiento entre barras soportadas (mm)
    hx_max: float                   # Máximo permitido (356mm o 203mm)
    hx_ok: bool

    # Cantidad de refuerzo (rectangular)
    Ash_sbc_provided: float         # Ash/(s*bc) provisto
    Ash_sbc_required: float         # Ash/(s*bc) requerido
    Ash_ok: bool

    # Cantidad de refuerzo (espiral)
    rho_s_provided: float = 0       # ρs provisto
    rho_s_required: float = 0       # ρs requerido
    rho_s_ok: bool = True

    # Condiciones especiales
    high_axial_or_fc: bool = False  # Pu > 0.3Ag*f'c O f'c > 70 MPa
    requires_corner_support: bool = False  # Si aplica, cada barra con soporte

    is_ok: bool = False
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.7.5"


@dataclass
class SeismicColumnResult:
    """
    Resultado completo de verificación de columna sísmica.

    Agrupa todos los checks según la categoría sísmica:
    - SPECIAL: §18.7 (todos los checks)
    - INTERMEDIATE: §18.4.3 (checks reducidos)
    - ORDINARY: §18.3.3 (solo cortante)
    """
    category: SeismicCategory

    # Verificaciones (None si no aplica para la categoría)
    dimensional_limits: Optional[DimensionalLimitsResult] = None
    strong_column_V2: Optional[StrongColumnResult] = None
    strong_column_V3: Optional[StrongColumnResult] = None
    longitudinal: Optional[LongitudinalReinforcementResult] = None
    transverse: Optional[TransverseReinforcementResult] = None
    shear: Optional[SeismicColumnShearResult] = None

    # Resultado global
    is_ok: bool = False
    dcr_max: float = 0              # DCR máximo de todas las verificaciones
    critical_check: str = ""        # Nombre del check crítico
    warnings: List[str] = field(default_factory=list)

    @property
    def aci_reference(self) -> str:
        """Referencia ACI según categoría."""
        return self.category.column_section
