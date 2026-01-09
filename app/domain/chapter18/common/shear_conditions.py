# app/domain/chapter18/common/shear_conditions.py
"""
Condiciones de cortante compartidas para elementos sísmicos.

Este módulo centraliza las condiciones que determinan cuándo Vc = 0
según ACI 318-25 para vigas y columnas sísmicas especiales.

Referencias:
- §18.6.5.2: Vigas sísmicas especiales (SMF)
- §18.7.6.2.1: Columnas sísmicas especiales (SMF)
"""
from ...constants.units import TONF_TO_N


def check_Vc_zero_condition(
    Ve: float,
    Vu: float,
    Pu: float,
    Ag: float,
    fc: float
) -> bool:
    """
    Verifica si Vc debe ser cero según ACI 318-25.

    Para elementos sísmicos especiales (SMF), Vc = 0 cuando se cumplen
    AMBAS condiciones:
        (a) Ve >= 0.5 × Vu
        (b) Pu < Ag × f'c / 20

    Args:
        Ve: Cortante por diseño por capacidad (tonf)
        Vu: Cortante último máximo de la combinación (tonf)
        Pu: Carga axial factorizada (tonf, positivo = compresión)
        Ag: Área bruta del elemento (mm²)
        fc: f'c del concreto (MPa)

    Returns:
        True si Vc debe ser cero (ambas condiciones cumplidas)

    Referencias:
        - §18.6.5.2: Vigas sísmicas especiales
        - §18.7.6.2.1: Columnas sísmicas especiales

    Nota:
        Para vigas, Pu típicamente es cero o muy bajo, por lo que
        la condición (b) casi siempre se cumple.
    """
    # Condición (a): El cortante sísmico domina
    # Si Vu es cero o negativo, asumimos que Ve domina
    condition_a = Ve >= 0.5 * Vu if Vu > 0 else True

    # Condición (b): Carga axial baja
    # Convertir Pu a Newtons para comparar con Ag * fc / 20
    Pu_N = Pu * TONF_TO_N
    threshold = Ag * fc / 20
    condition_b = Pu_N < threshold

    return condition_a and condition_b
