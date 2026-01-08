# app/services/analysis/force_extractors.py
"""
Funciones helper para extraccion de fuerzas maximas de combinaciones.

Centraliza la logica de iteracion sobre combinaciones de carga
para evitar codigo duplicado en los servicios de verificacion.
"""
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities import PierForces, ColumnForces, BeamForces


@dataclass
class MaxForces:
    """Fuerzas maximas extraidas de combinaciones."""
    Vu_max: float = 0.0       # Cortante maximo (max de V2, V3)
    Vu2_max: float = 0.0      # Cortante maximo en direccion 2
    Vu3_max: float = 0.0      # Cortante maximo en direccion 3
    Pu_max: float = 0.0       # Carga axial maxima (abs)
    Mu_max: float = 0.0       # Momento maximo
    critical_combo: str = ""  # Nombre de la combinacion critica


def extract_max_forces(forces) -> MaxForces:
    """
    Extrae fuerzas maximas de un conjunto de combinaciones.

    Funciona con PierForces, ColumnForces o BeamForces.

    Args:
        forces: Objeto con atributo .combinations que es iterable
                Cada combo debe tener P, V2, V3, y moment_resultant o M2/M3

    Returns:
        MaxForces con los valores maximos encontrados
    """
    result = MaxForces()

    if not forces or not getattr(forces, 'combinations', None):
        return result

    for combo in forces.combinations:
        V2 = abs(combo.V2) if hasattr(combo, 'V2') else 0
        V3 = abs(combo.V3) if hasattr(combo, 'V3') else 0
        Vu = max(V2, V3)
        P = abs(combo.P) if hasattr(combo, 'P') else 0

        # Momento: usar moment_resultant si existe, sino max de M2/M3
        if hasattr(combo, 'moment_resultant'):
            M = abs(combo.moment_resultant)
        else:
            M2 = abs(combo.M2) if hasattr(combo, 'M2') else 0
            M3 = abs(combo.M3) if hasattr(combo, 'M3') else 0
            M = max(M2, M3)

        # Actualizar maximos
        if V2 > result.Vu2_max:
            result.Vu2_max = V2
        if V3 > result.Vu3_max:
            result.Vu3_max = V3
        if Vu > result.Vu_max:
            result.Vu_max = Vu
            result.critical_combo = getattr(combo, 'name', '')
        if P > result.Pu_max:
            result.Pu_max = P
        if M > result.Mu_max:
            result.Mu_max = M

    return result


def extract_critical_combo(forces, criterion: str = 'shear') -> Optional[object]:
    """
    Encuentra la combinacion critica segun un criterio.

    Args:
        forces: Objeto con atributo .combinations
        criterion: 'shear' (max V), 'axial' (max P), 'moment' (max M)

    Returns:
        La combinacion critica o None si no hay combinaciones
    """
    if not forces or not getattr(forces, 'combinations', None):
        return None

    critical = None
    max_value = 0

    for combo in forces.combinations:
        if criterion == 'shear':
            V2 = abs(combo.V2) if hasattr(combo, 'V2') else 0
            V3 = abs(combo.V3) if hasattr(combo, 'V3') else 0
            value = max(V2, V3)
        elif criterion == 'axial':
            value = abs(combo.P) if hasattr(combo, 'P') else 0
        elif criterion == 'moment':
            if hasattr(combo, 'moment_resultant'):
                value = abs(combo.moment_resultant)
            else:
                M2 = abs(combo.M2) if hasattr(combo, 'M2') else 0
                M3 = abs(combo.M3) if hasattr(combo, 'M3') else 0
                value = max(M2, M3)
        else:
            value = 0

        if value > max_value:
            max_value = value
            critical = combo

    return critical
