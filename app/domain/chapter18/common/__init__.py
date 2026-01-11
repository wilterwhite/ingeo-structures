# app/domain/chapter18/common/__init__.py
"""
Infraestructura común para el Capítulo 18 de ACI 318-25.

Exporta:
- SeismicCategory: Categoría sísmica del elemento

Nota: check_Vc_zero_condition se movió a domain/shear/concrete_shear.py
para centralizar todos los cálculos de Vc.
"""
from .categories import SeismicCategory

__all__ = [
    "SeismicCategory",
]
