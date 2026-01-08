# app/services/analysis/shear/__init__.py
"""
Modulo de servicios de verificacion de cortante.

Servicios disponibles:
- ShearService: Fachada principal (orquesta todos los demas)
- ColumnShearService: Cortante de columnas (§22.5, §18.7.6)
- WallShearService: Cortante de muros (§11.5.4, §18.10.4)
- WallClassificationService: Clasificacion de muros (§18.10.8)
- ShearAmplificationService: Amplificacion de cortante (§18.10.3.3)
- BoundaryElementService: Elementos de borde (§18.10.6)
- CouplingBeamService: Vigas de acoplamiento (§18.10.7)

Uso:
    from app.services.analysis.shear import ShearService
    service = ShearService()
    result = service.check_shear(pier, forces)
"""
from .facade import ShearService
from .column_shear import ColumnShearService
from .wall_shear import WallShearService
from .wall_special_elements import (
    WallClassificationService,
    ShearAmplificationService,
    BoundaryElementService,
    CouplingBeamService,
)

__all__ = [
    'ShearService',
    'ColumnShearService',
    'WallShearService',
    'WallClassificationService',
    'ShearAmplificationService',
    'BoundaryElementService',
    'CouplingBeamService',
]
