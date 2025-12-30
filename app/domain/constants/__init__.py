# app/structural/domain/constants/__init__.py
"""
Constantes ACI 318-25 para diseño estructural.

Módulos:
- units: Constantes de conversión de unidades
- shear: Constantes para verificación de cortante
- seismic: Categorías de diseño sísmico
- materials: Grados de acero y propiedades de materiales

Nota: ReinforcementLimitsService está en domain/reinforcement_limits.py
"""
from .units import N_TO_TONF, NMM_TO_TONFM, MM_TO_M, M_TO_MM, INCH_TO_MM
from .shear import *
from .seismic import SeismicDesignCategory, WallCategory, SDC_REQUIREMENTS
from .materials import SteelGrade, LAMBDA_NORMAL, LAMBDA_SAND_LIGHTWEIGHT, LAMBDA_ALL_LIGHTWEIGHT
