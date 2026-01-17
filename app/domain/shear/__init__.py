# app/domain/shear/__init__.py
"""
Verificación de capacidad al corte según ACI 318-25.

Este módulo calcula la resistencia nominal Vn usando las ecuaciones
de los capítulos 11, 18 y 22 según corresponda por geometría.

Módulos:
- verification: Cálculo de Vn (§11.5.4, §18.10.4, §22.5)
- classification: Clasificación muro vs columna vs wall pier
- results: Dataclasses para resultados de verificación
- shear_friction: Fricción por cortante (§22.9)

Nota: La amplificación de cortante sísmico (§18.10.3.3) está en chapter18/.
"""
from .verification import ShearVerificationService
from .classification import WallClassificationService, WallClassification, ElementType
from .results import ShearResult, CombinedShearResult, WallGroupShearResult
from .shear_friction import (
    ShearFrictionService,
    ShearFrictionResult,
    ShearFrictionDesignResult,
    SurfaceCondition,
)
from .combined import calculate_combined_dcr
from .concrete_shear import (
    VcResult,
    calculate_Vc_beam,
    check_Vc_zero_condition,
)
from .steel_shear import (
    VsResult,
    calculate_Vs,
    calculate_Vs_beam_column,
    calculate_Vs_wall,
)

__all__ = [
    # verification
    'ShearVerificationService',
    # results
    'ShearResult',
    'CombinedShearResult',
    'WallGroupShearResult',
    # classification
    'WallClassificationService',
    'WallClassification',
    'ElementType',
    # shear_friction (§22.9)
    'ShearFrictionService',
    'ShearFrictionResult',
    'ShearFrictionDesignResult',
    'SurfaceCondition',
    # combined biaxial shear
    'calculate_combined_dcr',
    # concrete shear (Vc) - centralized calculations
    'VcResult',
    'calculate_Vc_beam',
    'check_Vc_zero_condition',
    # steel shear (Vs) - centralized calculations
    'VsResult',
    'calculate_Vs',
    'calculate_Vs_beam_column',
    'calculate_Vs_wall',
]
