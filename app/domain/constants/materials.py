# app/domain/constants/materials.py
"""
Constantes de materiales para diseno estructural segun ACI 318-25.

Centraliza propiedades de materiales usadas en multiples modulos.
"""
from enum import Enum
import math


class SteelGrade(Enum):
    """
    Grado del acero de refuerzo segun ASTM A615/A706.

    Grados y su fluencia en MPa:
    - GRADE_40: fy = 280 MPa
    - GRADE_60: fy = 420 MPa (mas comun)
    - GRADE_80: fy = 550 MPa
    - GRADE_100: fy = 690 MPa

    Referencias:
    - ASTM A615: Barras de acero corrugado
    - ASTM A706: Barras de bajo carbono para soldadura
    - ACI 318-25 Tabla 20.2.2.4(a): Limites de fy
    """
    GRADE_40 = 40    # 280 MPa
    GRADE_60 = 60    # 420 MPa
    GRADE_80 = 80    # 550 MPa
    GRADE_100 = 100  # 690 MPa

    @property
    def fy_mpa(self) -> float:
        """Retorna el limite de fluencia en MPa."""
        conversion = {40: 280.0, 60: 420.0, 80: 550.0, 100: 690.0}
        return conversion[self.value]


# =============================================================================
# BARRAS DE REFUERZO
# =============================================================================

# Áreas de barras estándar en mm² (según diámetro nominal en mm)
# Referencia: Tablas de fabricantes de acero de refuerzo
BAR_AREAS: dict[int, float] = {
    6: 28.3,    # φ6mm  = π×3² = 28.27 mm²
    8: 50.3,    # φ8mm  = π×4² = 50.27 mm²
    10: 78.5,   # φ10mm = π×5² = 78.54 mm²
    12: 113.1,  # φ12mm = π×6² = 113.10 mm²
    16: 201.1,  # φ16mm = π×8² = 201.06 mm²
    18: 254.5,  # φ18mm = π×9² = 254.47 mm²
    20: 314.2,  # φ20mm = π×10² = 314.16 mm²
    22: 380.1,  # φ22mm = π×11² = 380.13 mm²
    25: 490.9,  # φ25mm = π×12.5² = 490.87 mm²
    28: 615.8,  # φ28mm = π×14² = 615.75 mm²
    32: 804.2,  # φ32mm = π×16² = 804.25 mm²
    36: 1017.9, # φ36mm = π×18² = 1017.88 mm²
}

# Diámetros disponibles ordenados
AVAILABLE_DIAMETERS = sorted(BAR_AREAS.keys())


def get_bar_area(diameter: int, default: float = 50.3) -> float:
    """
    Obtiene el área de una barra dado su diámetro.

    Args:
        diameter: Diámetro de la barra (mm)
        default: Valor por defecto si no se encuentra (φ8 = 50.3 mm²)

    Returns:
        Área de la barra (mm²)
    """
    return BAR_AREAS.get(diameter, default)


# =============================================================================
# CONCRETO LIVIANO
# =============================================================================

# Factor de modificacion para concreto liviano (λ)
# ACI 318-25 Tabla 19.2.4.2
LAMBDA_NORMAL = 1.0           # Concreto peso normal
LAMBDA_SAND_LIGHTWEIGHT = 0.85  # Arena liviana
LAMBDA_ALL_LIGHTWEIGHT = 0.75   # Todo liviano


# =============================================================================
# LIMITES DE MATERIALES PARA DISENO SISMICO (ACI 318-25 Seccion 18.2)
# =============================================================================

# Limite de f'c para calculo de Vn en muros especiales (18.10.4.1)
# Nota: f'c para calculos de cortante no debe exceder 12,000 psi
FC_MAX_SHEAR_PSI = 12000          # psi
FC_MAX_SHEAR_MPA = 82.7           # MPa (12000 psi)

# Limite de f'c para concreto liviano en diseno sismico (18.2.5)
FC_MAX_LIGHTWEIGHT_PSI = 5000     # psi
FC_MAX_LIGHTWEIGHT_MPA = 35.0     # MPa (5000 psi)

# Limite de fyt para resistencia nominal al cortante (18.2.6)
# "fyt para resistencia nominal al cortante no debe exceder 60,000 psi"
FYT_MAX_SHEAR_PSI = 60000         # psi
FYT_MAX_SHEAR_MPA = 420.0         # MPa (60000 psi)

# Limite de fyt para refuerzo de confinamiento (18.2.6)
FYT_MAX_CONFINEMENT_PSI = 100000  # psi
FYT_MAX_CONFINEMENT_MPA = 690.0   # MPa (100000 psi)


def get_effective_fc_shear(fc: float, is_lightweight: bool = False) -> float:
    """
    Obtiene el f'c efectivo para calculo de cortante segun 18.10.4.1 y 18.2.5.

    Args:
        fc: Resistencia especificada del concreto (MPa)
        is_lightweight: True si es concreto liviano

    Returns:
        f'c efectivo limitado segun ACI 318-25 (MPa)
    """
    if is_lightweight:
        return min(fc, FC_MAX_LIGHTWEIGHT_MPA)
    return min(fc, FC_MAX_SHEAR_MPA)


def get_effective_fyt_shear(fyt: float) -> float:
    """
    Obtiene el fyt efectivo para calculo de cortante segun 18.2.6.

    "fyt usado para calcular resistencia nominal al cortante
    no debe exceder 60,000 psi (420 MPa)"

    Args:
        fyt: Resistencia del acero transversal (MPa)

    Returns:
        fyt efectivo limitado a 420 MPa
    """
    return min(fyt, FYT_MAX_SHEAR_MPA)


def get_effective_fyt_confinement(fyt: float) -> float:
    """
    Obtiene el fyt efectivo para calculo de confinamiento segun 18.2.6.

    Args:
        fyt: Resistencia del acero de confinamiento (MPa)

    Returns:
        fyt efectivo limitado a 690 MPa
    """
    return min(fyt, FYT_MAX_CONFINEMENT_MPA)


# =============================================================================
# PROPIEDADES DEL ACERO (ACI 318-25 §20.2)
# =============================================================================

# Módulo de elasticidad del acero (§20.2.2.2)
ES_MPA = 200000  # MPa (29,000 ksi)

# Deformación última del concreto (§22.2.2.1)
EPSILON_CU = 0.003


# =============================================================================
# PROPIEDADES DEL CONCRETO (ACI 318-25 §19.2)
# =============================================================================

def calculate_Ec(fc_mpa: float) -> float:
    """
    Calcula el módulo de elasticidad del concreto según §19.2.2.1.

    Ec = 4700 * sqrt(f'c) para concreto de peso normal (wc = 2300 kg/m³)

    Args:
        fc_mpa: Resistencia especificada del concreto (MPa)

    Returns:
        Módulo de elasticidad Ec (MPa)

    Examples:
        >>> calculate_Ec(28)  # f'c = 28 MPa
        24870.0
        >>> calculate_Ec(35)  # f'c = 35 MPa
        27806.0
    """
    return 4700 * math.sqrt(fc_mpa)


def calculate_fr(fc_mpa: float) -> float:
    """
    Calcula el módulo de ruptura del concreto según §19.2.3.1.

    fr = 0.62 * lambda * sqrt(f'c) para concreto de peso normal (lambda = 1.0)

    Args:
        fc_mpa: Resistencia especificada del concreto (MPa)

    Returns:
        Módulo de ruptura fr (MPa)

    Examples:
        >>> calculate_fr(28)  # f'c = 28 MPa
        3.28
        >>> calculate_fr(35)  # f'c = 35 MPa
        3.67
    """
    return 0.62 * math.sqrt(fc_mpa)


# =============================================================================
# BLOQUE DE ESFUERZOS DE WHITNEY
# =============================================================================

def calculate_beta1(fc_mpa: float) -> float:
    """
    Calcula el factor beta1 para el bloque de esfuerzos de Whitney.

    Segun ACI 318-25 §22.2.2.4.3:
    - fc <= 28 MPa (4000 psi): beta1 = 0.85
    - fc >= 55 MPa (8000 psi): beta1 = 0.65
    - Entre 28 y 55 MPa: interpolacion lineal

    La formula reduce beta1 en 0.05 por cada 7 MPa (1000 psi) sobre 28 MPa.

    Args:
        fc_mpa: Resistencia especificada del concreto en MPa

    Returns:
        Factor beta1 (entre 0.65 y 0.85)

    Examples:
        >>> calculate_beta1(25)  # f'c = 25 MPa
        0.85
        >>> calculate_beta1(35)  # f'c = 35 MPa
        0.80
        >>> calculate_beta1(60)  # f'c = 60 MPa
        0.65
    """
    if fc_mpa <= 28:
        return 0.85
    elif fc_mpa >= 55:
        return 0.65
    else:
        return 0.85 - 0.05 * (fc_mpa - 28) / 7
