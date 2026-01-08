# app/services/analysis/shear/__init__.py
"""
Modulo de servicios de verificacion de cortante.

Organizado en sub-servicios especializados:
- column_shear: Cortante de columnas (§22.5, §18.7.6)
- ShearService: Servicio principal en shear_service.py (nivel superior)

Uso:
    from app.services.analysis.shear import ColumnShearService
    from app.services.analysis.shear_service import ShearService
"""
from .column_shear import ColumnShearService


__all__ = [
    'ColumnShearService',
]
