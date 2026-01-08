# app/domain/shear/results.py
"""
Dataclasses de resultados para verificacion de corte segun ACI 318-25.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class ShearResult:
    """
    Resultado de la verificacion de corte en una direccion.

    Todos los valores de fuerza estan en tonf (compatibles con ETABS).
    Referencias ACI: 18.10.4 (muros) y 22.5 (columnas/vigas).
    """
    # Capacidades calculadas
    Vc: float           # Contribucion del hormigon (tonf)
    Vs: float           # Contribucion del acero (tonf)
    Vn: float           # Resistencia nominal Vn = Vc + Vs (tonf)
    phi_Vn: float       # Resistencia de diseno phi*Vn (tonf)
    Vn_max: float       # Limite maximo segun 18.10.4.4 (tonf)

    # Demanda y verificacion
    Vu: float           # Demanda de corte mayorado (tonf)
    sf: float           # Factor de seguridad = phi*Vn / Vu
    status: str         # "OK" si sf >= 1.0, "NO OK" si sf < 1.0

    # Parametros de calculo
    alpha_c: float      # Coeficiente alpha_c segun Tabla 18.10.4.1
    alpha_sh: float = 1.0  # Factor alpha_sh segun Ec. 18.10.4.4 (1.0-1.2)
    hw_lw: float = 0    # Relacion altura/largo del elemento
    formula_type: str = "wall"  # "wall" (18.10.4) o "column" (22.5)

    # Verificacion de cuantia minima (18.10.4.3)
    rho_check_ok: bool = True   # True si cumple rho_v >= rho_h
    rho_warning: str = ""       # Mensaje de advertencia si no cumple

    # Referencia ACI para trazabilidad
    aci_reference: str = ""     # Ej: "ACI 318-25 18.10.4.1"


@dataclass
class CombinedShearResult:
    """
    Resultado de la verificacion de corte combinado V2+V3.

    Usa interaccion SRSS (eliptica):
    DCR = sqrt[(Vu2/phi*Vn2)^2 + (Vu3/phi*Vn3)^2] <= 1.0
    """
    # Resultados individuales
    result_V2: ShearResult
    result_V3: ShearResult

    # Interaccion SRSS
    dcr_2: float        # Demand/Capacity ratio V2 = Vu2/phi*Vn2
    dcr_3: float        # Demand/Capacity ratio V3 = Vu3/phi*Vn3
    dcr_combined: float # DCR combinado SRSS: sqrt(dcr_2^2 + dcr_3^2)
    sf: float           # Factor de seguridad = 1/dcr_combined
    status: str         # "OK" o "NO OK"

    # Info de la combinacion
    combo_name: str = ""


@dataclass
class WallGroupShearResult:
    """
    Resultado para un grupo de segmentos de muro (ACI 318-25 18.10.4.4).

    Para segmentos verticales coplanares que resisten una fuerza lateral
    comun, la suma de sus Vn no debe exceder:

    Vn_grupo <= 0.66 x sqrt(f'c) x Acv_total

    Aplicaciones:
    - Muros con aberturas (multiples segmentos)
    - Muros acoplados
    - Grupos de muros que trabajan juntos
    """
    # Resultados de cada segmento individual
    segments: List[ShearResult]

    # Capacidades del grupo
    Vn_total: float           # Suma de Vn de todos los segmentos (tonf)
    Vn_max_group: float       # Limite 0.66*Acv_total*sqrt(f'c) (tonf)
    Vn_effective: float       # min(Vn_total, Vn_max_group) (tonf)
    phi_Vn_effective: float   # phi x Vn_effective (tonf)

    # Verificacion
    controls_group_limit: bool  # True si el limite de grupo gobierna
    sf: float                   # Factor de seguridad del grupo
    status: str                 # "OK" o "NO OK"

    # Informacion del grupo
    Acv_total: float          # Area de corte total del grupo (mm2)
    fc: float                 # f'c usado para el calculo (MPa)
    n_segments: int           # Numero de segmentos en el grupo


@dataclass
class SimpleShearCapacity:
    """
    Capacidad de corte simple para vigas (una direccion).

    Usado para calculo basico de Vc + Vs segun ACI 318-25 §22.5.
    Unidades: tonf para fuerzas.
    """
    Vc: float       # Contribucion del concreto (tonf)
    Vs: float       # Contribucion del acero (tonf)
    Vs_max: float   # Limite de Vs (tonf)
    phi_Vn: float   # Capacidad de diseno (tonf)
    aci_reference: str = "ACI 318-25 §22.5"
