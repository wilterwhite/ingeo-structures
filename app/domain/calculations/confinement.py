# app/domain/calculations/confinement.py
"""
Cálculos de confinamiento según ACI 318-25 Tabla 18.10.6.4(g).

Funciones puras compartidas por:
- chapter18/boundary_elements/confinement.py
- chapter18/coupling_beams/confinement.py
- chapter18/piers/transverse.py

Expresiones de la Tabla 18.10.6.4(g):
- Estribos rectangulares: Ash/(s*bc) >= max[(a), (b)]
  (a) 0.3*(Ag/Ach - 1)*(f'c/fyt)
  (b) 0.09*(f'c/fyt)

- Espiral/aro circular: rho_s >= max[(c), (d)]
  (c) 0.45*(Ag/Ach - 1)*(f'c/fyt)
  (d) 0.12*(f'c/fyt)
"""


def calculate_ash_sbc(
    Ag: float,
    Ach: float,
    fc: float,
    fyt: float
) -> float:
    """
    Calcula Ash/(s*bc) para estribos rectangulares.

    Según Tabla 18.10.6.4(g):
    Ash/(s*bc) >= max(0.3*(Ag/Ach-1)*(f'c/fyt), 0.09*(f'c/fyt))

    Args:
        Ag: Área bruta (mm2)
        Ach: Área del núcleo confinado (mm2)
        fc: f'c del hormigón (MPa)
        fyt: fy del refuerzo transversal (MPa)

    Returns:
        Ash/(s*bc) requerido (adimensional)
    """
    ratio = Ag / Ach if Ach > 0 else 2.0
    expr_a = 0.3 * (ratio - 1) * (fc / fyt)
    expr_b = 0.09 * (fc / fyt)
    return max(expr_a, expr_b)


def calculate_rho_s(
    Ag: float,
    Ach: float,
    fc: float,
    fyt: float
) -> float:
    """
    Calcula rho_s para espiral o aro circular.

    Según Tabla 18.10.6.4(g):
    rho_s >= max(0.45*(Ag/Ach-1)*(f'c/fyt), 0.12*(f'c/fyt))

    Args:
        Ag: Área bruta (mm2)
        Ach: Área del núcleo confinado (mm2)
        fc: f'c del hormigón (MPa)
        fyt: fy del refuerzo transversal (MPa)

    Returns:
        rho_s requerido (adimensional)
    """
    ratio = Ag / Ach if Ach > 0 else 2.0
    expr_c = 0.45 * (ratio - 1) * (fc / fyt)
    expr_d = 0.12 * (fc / fyt)
    return max(expr_c, expr_d)


def calculate_confinement_requirements(
    Ag: float,
    Ach: float,
    fc: float,
    fyt: float
) -> tuple[float, float]:
    """
    Calcula ambos requisitos de confinamiento.

    Convenience function que retorna ambos valores.

    Args:
        Ag: Área bruta (mm2)
        Ach: Área del núcleo confinado (mm2)
        fc: f'c del hormigón (MPa)
        fyt: fy del refuerzo transversal (MPa)

    Returns:
        Tupla (Ash_sbc, rho_s)
    """
    return (
        calculate_ash_sbc(Ag, Ach, fc, fyt),
        calculate_rho_s(Ag, Ach, fc, fyt)
    )
