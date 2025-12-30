# app/structural/domain/constants/__init__.py
"""
Constantes ACI 318-25 para diseño estructural.

Módulos:
- shear: Constantes para verificación de cortante
- reinforcement: Límites de refuerzo
- seismic: Categorías de diseño sísmico
"""
from .shear import *
from .reinforcement import *
from .seismic import SeismicDesignCategory, WallCategory, SDC_REQUIREMENTS
