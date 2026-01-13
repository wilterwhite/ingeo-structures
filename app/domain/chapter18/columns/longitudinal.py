# app/domain/chapter18/columns/longitudinal.py
"""
Refuerzo longitudinal para columnas sísmicas ACI 318-25 §18.7.4.

Requisitos:
- §18.7.4.1: 0.01*Ag <= Ast <= 0.06*Ag
- §18.7.4.2: Mínimo 6 barras para hoops circulares
- §18.7.4.3: Control de adherencia
- §18.7.4.4: Empalmes en mitad central

Referencias:
- ACI 318-25 §18.7.4
"""
from .results import LongitudinalReinforcementResult

# Constantes
RHO_MIN_SPECIAL = 0.01      # Cuantía mínima para especial
RHO_MAX_SPECIAL = 0.06      # Cuantía máxima para especial
MIN_BARS_CIRCULAR = 6       # Mínimo barras con hoops circulares
MIN_BARS_RECTANGULAR = 4    # Mínimo barras con hoops rectangulares


def check_longitudinal_reinforcement(
    Ast: float,
    Ag: float,
    n_bars: int,
    is_circular: bool = False,
) -> LongitudinalReinforcementResult:
    """
    Verifica refuerzo longitudinal según §18.7.4.

    Requisitos:
    - 0.01*Ag <= Ast <= 0.06*Ag
    - Mínimo 6 barras para columnas con hoops circulares
    - Mínimo 4 barras para columnas con hoops rectangulares

    Args:
        Ast: Área total de refuerzo longitudinal (mm²)
        Ag: Área bruta de la sección (mm²)
        n_bars: Número de barras longitudinales
        is_circular: True si la columna tiene hoops circulares

    Returns:
        LongitudinalReinforcementResult con verificación completa
    """
    rho = Ast / Ag if Ag > 0 else 0

    rho_min_ok = rho >= RHO_MIN_SPECIAL
    rho_max_ok = rho <= RHO_MAX_SPECIAL

    n_bars_min = MIN_BARS_CIRCULAR if is_circular else MIN_BARS_RECTANGULAR
    n_bars_ok = n_bars >= n_bars_min

    is_ok = rho_min_ok and rho_max_ok and n_bars_ok

    return LongitudinalReinforcementResult(
        Ast=Ast,
        Ag=Ag,
        rho=round(rho, 4),
        rho_min=RHO_MIN_SPECIAL,
        rho_max=RHO_MAX_SPECIAL,
        rho_min_ok=rho_min_ok,
        rho_max_ok=rho_max_ok,
        n_bars=n_bars,
        n_bars_min=n_bars_min,
        n_bars_ok=n_bars_ok,
        is_ok=is_ok,
    )


