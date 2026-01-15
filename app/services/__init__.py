# app/services/__init__.py
"""
Servicios del módulo estructural.

Estructura:
- structural_analysis.py: Orquestador principal
- analysis/: Servicios de análisis (flexocompresión, verificación)
- parsing/: Servicios de parsing Excel
- presentation/: Servicios de visualización
"""
from .structural_analysis import StructuralAnalysisService
from .factory import ServiceFactory
from .analysis import FlexocompressionService
from .parsing import (
    EtabsExcelParser,
    ParsedData,
    SessionManager,
    ReinforcementConfig
)
from .presentation import PlotGenerator

__all__ = [
    'StructuralAnalysisService',
    'ServiceFactory',
    'FlexocompressionService',
    'EtabsExcelParser',
    'ParsedData',
    'SessionManager',
    'ReinforcementConfig',
    'PlotGenerator'
]
