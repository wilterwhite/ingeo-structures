# app/domain/chapter18/coupled_walls/__init__.py
"""
Verificación de Muros Acoplados Dúctiles según ACI 318-25 §18.10.9.

Este módulo verifica si un sistema de muros acoplados cumple los requisitos
para ser clasificado como "muro acoplado dúctil" según §18.10.9:

Requisitos:
-----------
§18.10.9.1: hwcs/lw >= 2 para cada muro individual
§18.10.9.2: ln/h >= 2 para vigas de acople en todos los niveles
§18.10.9.3: ln/h <= 5 para al menos 90% de los niveles

Uso típico:
----------
    from app.domain.chapter18.coupled_walls import (
        DuctileCoupledWallService,
        DuctileCoupledWallResult,
    )

    service = DuctileCoupledWallService()
    result = service.verify_ductile_coupled_wall(
        walls=[
            {"hwcs": 15000, "lw": 6000},
            {"hwcs": 15000, "lw": 5000},
        ],
        coupling_beams=[
            {"ln": 2000, "h": 800, "level": 1},
            {"ln": 2000, "h": 800, "level": 2},
            ...
        ]
    )

    if result.is_ductile_coupled_wall:
        print("Sistema califica como muro acoplado dúctil")
"""
from .service import DuctileCoupledWallService
from .results import (
    DuctileCoupledWallResult,
    WallGeometryCheck,
    CouplingBeamGeometryCheck,
    LevelComplianceResult,
)

__all__ = [
    "DuctileCoupledWallService",
    "DuctileCoupledWallResult",
    "WallGeometryCheck",
    "CouplingBeamGeometryCheck",
    "LevelComplianceResult",
]
