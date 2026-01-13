# app/domain/chapter18/boundary_elements/dimensions.py
"""
Cálculo de dimensiones de elementos de borde ACI 318-25 §18.10.6.4.

Incluye:
- Extensión horizontal (18.10.6.4(a))
- Ancho mínimo (18.10.6.4(b), (c))
- Extensión vertical (18.10.6.2(b)(i))
"""
import math

from ...constants.geometry import BE_MIN_WIDTH_SPECIAL_MM, BE_C_LW_THRESHOLD
from ..results import BoundaryElementDimensions


def calculate_dimensions(
    c: float,
    lw: float,
    Mu: float,
    Vu: float,
    hu: float,
    delta_u: float = 0,
    hwcs: float = 0
) -> BoundaryElementDimensions:
    """
    Calcula las dimensiones requeridas del elemento de borde.

    Según 18.10.6.4 y 18.10.6.2(b):

    (a) Extensión horizontal: mayor de (c - 0.1*lw) y (c/2)
    (b) Ancho mínimo: b >= hu/16
    (c) Para c/lw >= 3/8: b >= 12 in (305 mm)

    Para método de desplazamiento:
    (b)(ii) Ancho requerido: b >= sqrt(c*lw)/40

    Args:
        c: Profundidad del eje neutro (mm)
        lw: Longitud del muro (mm)
        Mu: Momento último (tonf-m)
        Vu: Cortante último (tonf)
        hu: Altura de piso (mm)
        delta_u: Desplazamiento de diseño (mm) - para método desplazamiento
        hwcs: Altura desde sección crítica (mm) - para método desplazamiento

    Returns:
        BoundaryElementDimensions con dimensiones calculadas
    """
    # (a) Extensión horizontal
    length_h_1 = c - 0.1 * lw
    length_h_2 = c / 2
    length_horizontal = max(length_h_1, length_h_2)

    # (b) Ancho mínimo básico
    width_min = hu / 16

    # (c) Para c/lw >= 3/8: b >= 305 mm (BE_MIN_WIDTH_SPECIAL_MM)
    if lw > 0 and (c / lw) >= BE_C_LW_THRESHOLD:
        width_min = max(width_min, BE_MIN_WIDTH_SPECIAL_MM)

    # Ancho requerido por método de desplazamiento (18.10.6.2(b)(ii))
    # El ancho requerido siempre debe ser >= width_min (que ya incluye el 305mm si c/lw >= 3/8)
    if delta_u > 0 and c > 0 and lw > 0:
        width_displacement = math.sqrt(c * lw) / 40
        width_required = max(width_displacement, width_min)
    else:
        width_required = width_min

    # (i) Extensión vertical: mayor de lw y Mu/(4*Vu)
    if Vu > 0:
        # Convertir Mu de tonf-m a tonf-mm para unidades consistentes
        Mu_mm = Mu * 1000
        vertical_ext_1 = lw
        vertical_ext_2 = Mu_mm / (4 * Vu)
        vertical_extension = max(vertical_ext_1, vertical_ext_2)
    else:
        vertical_extension = lw

    return BoundaryElementDimensions(
        length_horizontal=round(length_horizontal, 1),
        width_min=round(width_min, 1),
        width_required=round(width_required, 1),
        vertical_extension=round(vertical_extension, 1),
        c=c,
        lw=lw,
        aci_reference="ACI 318-25 18.10.6.4"
    )
