# app/domain/chapter18/common/__init__.py
"""
Infraestructura común para el Capítulo 18 de ACI 318-25.

Exporta:
- SeismicCategory: Categoría sísmica del elemento
- check_Vc_zero_condition: Condición Vc=0 para elementos SMF (§18.6.5.2, §18.7.6.2.1)
"""
from .categories import SeismicCategory
from .shear_conditions import check_Vc_zero_condition

__all__ = [
    "SeismicCategory",
    "check_Vc_zero_condition",
]
