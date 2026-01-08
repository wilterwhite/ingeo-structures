# app/domain/chapter18/non_sfrs/results.py
"""
Dataclasses para miembros no-SFRS ACI 318-25 §18.14.
"""
from dataclasses import dataclass, field
from typing import List
from enum import Enum


class DriftCheckType(Enum):
    """Tipo de verificación según §18.14.3."""
    WITHIN_CAPACITY = "within_capacity"      # §18.14.3.2
    EXCEEDS_CAPACITY = "exceeds_capacity"    # §18.14.3.3
    NOT_CALCULATED = "not_calculated"        # No se calculó, usar §18.14.3.3


@dataclass
class DriftCompatibilityResult:
    """
    Resultado de verificación de compatibilidad de deriva §18.14.3.

    Los miembros no-SFRS deben poder acomodar el desplazamiento de diseño δu
    mientras resisten cargas de gravedad.
    """
    # Deriva de diseño
    delta_u: float              # Desplazamiento de diseño (mm)
    hsx: float                  # Altura de entrepiso (mm)
    drift_ratio: float          # Δu/hsx

    # Tipo de verificación
    check_type: DriftCheckType

    # Momentos/cortantes inducidos por deriva
    M_induced: float = 0        # Momento inducido por δu (tonf-m)
    V_induced: float = 0        # Cortante inducido por δu (tonf)

    # Capacidad
    Mn: float = 0               # Resistencia nominal a flexión (tonf-m)
    Vn: float = 0               # Resistencia nominal a cortante (tonf)

    # Verificación de capacidad
    M_within_capacity: bool = True  # M_induced <= φMn
    V_within_capacity: bool = True  # V_induced <= φVn
    within_capacity: bool = True    # Ambos OK

    is_ok: bool = True
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.14.3"


@dataclass
class SlabColumnShearResult:
    """
    Resultado de verificación de conexiones losa-columna §18.14.5.

    Determina si se requiere refuerzo de cortante basado en la deriva
    y el nivel de esfuerzo cortante.
    """
    # Deriva
    drift_ratio: float          # Δx/hsx
    is_prestressed: bool        # True si losa postensada

    # Esfuerzos
    vuv: float                  # Esfuerzo cortante por gravedad + sismo vert (MPa)
    phi_vc: float               # φvc calculado según §22.6.5 (MPa)
    stress_ratio: float         # vuv / φvc

    # Límites de deriva
    drift_limit_no_reinf: float    # 0.005 (no pret) o 0.01 (postensada)
    drift_threshold: float         # 0.035 - (1/20)*(vuv/φvc) o 0.040 - ...

    # Resultados
    requires_shear_reinf: bool     # True si se requiere refuerzo
    is_exempt: bool                # True si está exento por baja deriva

    # Refuerzo requerido si aplica
    vs_required: float = 0         # vs >= 3.5√f'c (MPa)
    extension_required: float = 0  # >= 4 * espesor de losa (mm)

    is_ok: bool = True
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.14.5"


@dataclass
class NonSfrsResult:
    """
    Resultado completo de verificación para miembro no-SFRS.
    """
    element_type: str           # "beam", "column", "slab_column"

    # Verificaciones
    drift_compatibility: DriftCompatibilityResult = None
    slab_column_shear: SlabColumnShearResult = None

    # Resultado global
    is_ok: bool = True
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.14"
