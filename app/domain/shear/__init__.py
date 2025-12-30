# app/domain/shear/__init__.py
"""
Verificación de capacidad al corte según ACI 318-25.

Este módulo calcula la resistencia nominal Vn usando las ecuaciones
de los capítulos 11, 18 y 22 según corresponda por geometría.

Módulos:
- verification: Cálculo de Vn (§11.5.4, §18.10.4, §22.5)
- classification: Clasificación muro vs columna vs wall pier
- results: Dataclasses para resultados de verificación

Nota: La amplificación de cortante sísmico (§18.10.3.3) está en chapter18/.
"""
from .verification import ShearVerificationService
from .classification import WallClassificationService, WallClassification, ElementType
from .results import ShearResult, CombinedShearResult, WallGroupShearResult

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
]
