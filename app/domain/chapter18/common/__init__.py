# app/domain/chapter18/common/__init__.py
"""
Infraestructura común para el Capítulo 18 de ACI 318-25.

Exporta:
- SeismicCategory: Categoría sísmica del elemento
- Constantes y requisitos compartidos
"""
from .categories import SeismicCategory

__all__ = [
    "SeismicCategory",
]
