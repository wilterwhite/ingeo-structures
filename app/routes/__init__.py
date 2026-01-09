# app/routes/__init__.py
"""
Rutas API del módulo estructural.

Organización:
- piers.py: Endpoints para análisis de muros (piers)
- columns.py: Endpoints para análisis de columnas sísmicas
- beams.py: Endpoints para análisis de vigas sísmicas
- slabs.py: Endpoints para análisis de losas
- common.py: Utilidades compartidas (decoradores, servicios)
"""
from .piers import bp as piers_bp
from .columns import bp as columns_bp
from .beams import bp as beams_bp
from .slabs import bp as slabs_bp

__all__ = ['piers_bp', 'columns_bp', 'beams_bp', 'slabs_bp']
