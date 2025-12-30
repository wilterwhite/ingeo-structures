# app/domain/constants/__init__.py
"""
Constantes ACI 318-25 para diseño estructural.

Módulos:
- units: Constantes de conversión de unidades
- phi: Factores de reducción de resistencia (Cap. 21)
- shear: Constantes para verificación de cortante
- seismic: Categorías de diseño sísmico
- materials: Grados de acero y propiedades de materiales
- stiffness: Factores de rigidez efectiva (Tabla 6.6.3.1.1)
"""
from .units import N_TO_TONF, NMM_TO_TONFM, MM_TO_M, M_TO_MM, INCH_TO_MM
from .phi_chapter21 import (
    PHI_COMPRESSION,
    PHI_COMPRESSION_SPIRAL,
    PHI_TENSION,
    PHI_SHEAR,
    PHI_TORSION,
    PHI_BEARING,
    PHI_SHEAR_SEISMIC,
    PHI_SHEAR_DIAGONAL,
    EPSILON_TY,
    EPSILON_T_LIMIT,
    calculate_phi_flexure,
)
from .shear import *
from .seismic import SeismicDesignCategory, WallCategory, SDC_REQUIREMENTS
from .materials import SteelGrade, LAMBDA_NORMAL, LAMBDA_SAND_LIGHTWEIGHT, LAMBDA_ALL_LIGHTWEIGHT
from .stiffness import (
    WALL_STIFFNESS_FACTOR,
    WALL_UNCRACKED_STIFFNESS_FACTOR,
    COLUMN_STIFFNESS_FACTOR,
    BEAM_STIFFNESS_FACTOR,
    FLAT_SLAB_STIFFNESS_FACTOR,
)
