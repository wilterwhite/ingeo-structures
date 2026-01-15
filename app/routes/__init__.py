# app/routes/__init__.py
"""
Rutas API del módulo estructural.

Organización:
- piers.py: Endpoints para análisis de muros (piers) y elementos genéricos
- projects.py: Endpoints para gestión de proyectos persistentes
- common.py: Utilidades compartidas (decoradores, servicios) + /api/constants
"""
from .piers import bp as piers_bp
from .projects import bp as projects_bp
from .common import bp as common_bp

__all__ = ['piers_bp', 'projects_bp', 'common_bp']
