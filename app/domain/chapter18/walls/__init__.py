# app/domain/chapter18/walls/__init__.py
"""
Módulo orquestador para muros sísmicos especiales ACI 318-25 §18.10.

DIFERENCIA CON wall_piers/:
- walls/: Orquestador general que verifica TODOS los muros sísmicos (§18.10.2-6).
          Detecta si un muro es "wall pier" (lw/tw ≤ 6.0) y delega a wall_piers/.
- wall_piers/: Servicio especializado para segmentos estrechos (§18.10.8).
               Solo se invoca cuando SeismicWallService detecta un wall pier.

Flujo de verificación:
  SeismicWallService.verify_wall()
    ├── Clasificación (§18.10, Tabla R18.10.1)
    ├── Refuerzo mínimo (§18.10.2.1)
    ├── Cortante (§18.10.4)
    ├── Elementos de borde (§18.10.6)
    └── Si lw/tw ≤ 6.0 → WallPierService.design_wall_pier() (§18.10.8)

Exporta:
- SeismicWallService: Servicio principal de verificación
- Dataclasses de resultados
"""
from .service import SeismicWallService
from .results import (
    SeismicWallResult,
    WallClassificationResult,
    WallReinforcementResult,
    WallShearResult,
    WallBoundaryResult,
)

__all__ = [
    # Servicio
    "SeismicWallService",
    # Resultados
    "SeismicWallResult",
    "WallClassificationResult",
    "WallReinforcementResult",
    "WallShearResult",
    "WallBoundaryResult",
]
