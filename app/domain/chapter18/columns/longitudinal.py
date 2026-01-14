# app/domain/chapter18/columns/longitudinal.py
"""
Refuerzo longitudinal para columnas sísmicas ACI 318-25 §18.7.4.

Requisitos:
- §18.7.4.1: 0.01*Ag <= Ast <= 0.06*Ag
- §18.7.4.2: Mínimo 6 barras para hoops circulares
- §18.7.4.3: Control de adherencia
- §18.7.4.4: Empalmes en mitad central

Excepción para hormigón no confinado (Cap. 14):
- 1 barra centrada permitida como dowel de transferencia
- Verificación de esbeltez H <= 3h (warning si excede)
- φ = 0.60 (se aplica en el orquestador)

Referencias:
- ACI 318-25 §18.7.4
- ACI 318-25 §14 (Hormigón Simple)
"""
from .results import LongitudinalReinforcementResult

# Constantes
RHO_MIN_SPECIAL = 0.01      # Cuantía mínima para especial
RHO_MAX_SPECIAL = 0.06      # Cuantía máxima para especial
MIN_BARS_CIRCULAR = 6       # Mínimo barras con hoops circulares
MIN_BARS_RECTANGULAR = 4    # Mínimo barras con hoops rectangulares
MIN_BARS_UNCONFINED = 1     # Mínimo barras para hormigón no confinado

# Límites para hormigón no confinado (Cap. 14)
SLENDERNESS_LIMIT_PEDESTAL = 3.0  # H/h máximo para pedestales


def check_longitudinal_reinforcement(
    Ast: float,
    Ag: float,
    n_bars: int,
    is_circular: bool = False,
    is_unconfined: bool = False,
    slenderness_ratio: float = 0,
) -> LongitudinalReinforcementResult:
    """
    Verifica refuerzo longitudinal según §18.7.4.

    Requisitos normales:
    - 0.01*Ag <= Ast <= 0.06*Ag
    - Mínimo 6 barras para columnas con hoops circulares
    - Mínimo 4 barras para columnas con hoops rectangulares

    Excepción para hormigón no confinado (1 barra centrada):
    - Se permite 1 barra actuando como dowel de transferencia
    - Se ignoran requisitos de cuantía mínima
    - Warning si H/h > 3 (límite de pedestal §14.3.3)

    Args:
        Ast: Área total de refuerzo longitudinal (mm²)
        Ag: Área bruta de la sección (mm²)
        n_bars: Número de barras longitudinales
        is_circular: True si la columna tiene hoops circulares
        is_unconfined: True si es hormigón no confinado (1 barra centrada)
        slenderness_ratio: H/h para verificación de pedestal

    Returns:
        LongitudinalReinforcementResult con verificación completa
    """
    warnings = []
    rho = Ast / Ag if Ag > 0 else 0

    # Caso especial: hormigón no confinado (1 barra centrada)
    if is_unconfined:
        warnings.append(
            "Hormigón no confinado (Cap. 14): diseñar como pedestal con φ=0.60"
        )

        # Verificar límite de esbeltez para pedestales
        if slenderness_ratio > SLENDERNESS_LIMIT_PEDESTAL:
            warnings.append(
                f"⚠ Esbeltez H/h={slenderness_ratio:.1f} > 3 excede límite de pedestal §14.3.3"
            )

        # Para hormigón no confinado, no aplican los límites normales de cuantía
        return LongitudinalReinforcementResult(
            Ast=Ast,
            Ag=Ag,
            rho=round(rho, 4),
            rho_min=0,  # No aplica para hormigón no confinado
            rho_max=RHO_MAX_SPECIAL,
            rho_min_ok=True,  # Siempre OK para no confinado
            rho_max_ok=rho <= RHO_MAX_SPECIAL,
            n_bars=n_bars,
            n_bars_min=MIN_BARS_UNCONFINED,
            n_bars_ok=True,  # 1 barra es suficiente para no confinado
            is_ok=True,
            is_unconfined=True,
            slenderness_ratio=slenderness_ratio,
            warnings=warnings,
        )

    # Caso normal: columna con refuerzo convencional
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
        is_unconfined=False,
        slenderness_ratio=slenderness_ratio,
        warnings=warnings,
    )


