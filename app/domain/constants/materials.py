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


# Constantes adicionales de materiales

# Factor de modificacion para concreto liviano
LAMBDA_NORMAL = 1.0      # Concreto peso normal
LAMBDA_SAND_LIGHTWEIGHT = 0.85  # Arena liviana
LAMBDA_ALL_LIGHTWEIGHT = 0.75   # Todo liviano
