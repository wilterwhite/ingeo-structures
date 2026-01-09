# app/domain/proposals/__init__.py
"""
Módulo de generación de propuestas de diseño.

Proporciona lógica de búsqueda iterativa para encontrar soluciones
cuando un pier falla verificación estructural.

Componentes:
- DesignGenerator: Clase principal que genera propuestas
- failure_analysis: Determina modo de falla desde resultados
- strategies/: Estrategias específicas por modo de falla
"""
from .design_generator import DesignGenerator
from .failure_analysis import determine_failure_mode

__all__ = [
    "DesignGenerator",
    "determine_failure_mode",
]
