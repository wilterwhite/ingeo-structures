# app/domain/geometry/__init__.py
"""
Servicios de verificación de geometría ACI 318-25.

Este módulo centraliza todas las verificaciones de dimensiones mínimas:
- Columnas especiales (§18.7.2)
- Vigas especiales (§18.6.2)
- Elementos de borde (§18.10.6.4)
"""
from .service import GeometryChecksService
from .results import GeometryCheckResult

__all__ = [
    'GeometryChecksService',
    'GeometryCheckResult',
]
