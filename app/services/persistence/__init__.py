# app/services/persistence/__init__.py
"""
Servicio de persistencia de proyectos.

Estructura de proyecto:
- project.json: Metadata
- parsed_data.json: Estado parseado completo
- results.json: Resultados de análisis (carga instantánea)
- source.xlsx: Excel original (backup)
"""
from .project_manager import ProjectManager

__all__ = ['ProjectManager']
