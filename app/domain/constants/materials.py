# app/domain/constants/materials.py
"""
Constantes de materiales para diseno estructural segun ACI 318-25.

Centraliza propiedades de materiales usadas en multiples modulos.
"""
from enum import Enum


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
