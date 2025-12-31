# app/domain/flexure/__init__.py
"""
Verificación de flexión según ACI 318-25.

Módulos:
- interaction_diagram: Diagramas de interacción P-M
- slenderness: Efectos de esbeltez
- checker: Verificación de capacidad a flexión
"""
from .interaction_diagram import InteractionDiagramService, InteractionPoint
from .slenderness import SlendernessService, SlendernessResult
from .checker import FlexureChecker, FlexureCheckResult
from ..calculations.steel_layer_calculator import SteelLayer

__all__ = [
    'InteractionDiagramService',
    'InteractionPoint',
    'SlendernessService',
    'SlendernessResult',
    'FlexureChecker',
    'FlexureCheckResult',
    'SteelLayer',
]
