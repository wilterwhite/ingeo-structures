# app/domain/chapter18/reinforcement/__init__.py
"""
Verificación de refuerzo mínimo para muros especiales según ACI 318-25.

Módulo que centraliza:
- §18.10.2.1: Refuerzo distribuido mínimo (ρℓ, ρt >= 0.0025, s <= 18")
- §18.10.4.3: ρv >= ρh para muros bajos (hw/lw <= 2.0)

Integra con chapter11/reinforcement.py para verificaciones de §11.6.

Uso:
    from app.domain.chapter18.reinforcement import SeismicReinforcementService

    service = SeismicReinforcementService()
    result = service.check_minimum_reinforcement(pier)
"""
from .service import SeismicReinforcementService
from .results import SeismicReinforcementResult

__all__ = [
    'SeismicReinforcementService',
    'SeismicReinforcementResult',
]
