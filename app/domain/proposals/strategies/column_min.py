# app/domain/proposals/strategies/column_min.py
"""
Estrategia de propuesta para columnas sísmicas con espesor < 300mm.

Según ACI 318-25 §18.7.2.1:
"The shortest cross-sectional dimension, measured on a straight
line passing through the centroid, shall be at least 300 mm"
"""
from typing import Optional, Callable, TYPE_CHECKING
from copy import deepcopy

from ...entities.design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
    THICKNESS_SEQUENCE,
)
from ...constants.units import MIN_COLUMN_DIMENSION_MM
from .base import TARGET_SF

if TYPE_CHECKING:
    from ...entities import VerticalElement, ElementForces


def propose_for_column_min_thickness(
    pier: 'VerticalElement',
    pier_forces: Optional['ElementForces'],
    original_config: ReinforcementConfig,
    original_sf: float,
    original_dcr: float,
    verify_flexure: Callable,
    verify_shear: Callable,
    apply_config: Callable
) -> DesignProposal:
    """
    Propone solución para columna sísmica con espesor < 300mm.

    Estrategia:
    1. Proponer espesor mínimo de 300mm
    2. Si con 300mm no pasa verificación, incrementar espesor hasta pasar

    Args:
        pier: Pier a analizar (clasificado como columna sísmica)
        pier_forces: Fuerzas del pier
        original_config: Configuración original
        original_sf: SF de flexión original
        original_dcr: DCR de corte original
        verify_flexure: Función para verificar flexión
        verify_shear: Función para verificar corte
        apply_config: Función para aplicar config a pier

    Returns:
        DesignProposal con espesor >= 300mm
    """
    proposed_config = deepcopy(original_config)
    changes = [f"⚠️ Columna sísmica: e ≥ 300mm (§18.7.2.1)"]

    # Filtrar secuencia de espesores para comenzar en 300mm
    valid_thicknesses = [t for t in THICKNESS_SEQUENCE if t >= MIN_COLUMN_DIMENSION_MM]

    if not valid_thicknesses:
        # Si no hay espesores >= 300mm en la secuencia, usar 300mm directamente
        valid_thicknesses = [MIN_COLUMN_DIMENSION_MM]

    best_sf = original_sf
    best_dcr = original_dcr
    iteration = 0

    for thickness in valid_thicknesses:
        proposed_config.thickness = thickness
        iteration += 1

        # Crear pier de prueba con nuevo espesor
        test_pier = apply_config(pier, proposed_config)

        new_sf = verify_flexure(test_pier, pier_forces)
        new_dcr = verify_shear(test_pier, pier_forces)

        # Verificar si pasa
        if new_sf >= TARGET_SF and new_dcr <= 1.0:
            changes.append(f"Espesor: {int(thickness)}mm")
            return DesignProposal(
                pier_key=f"{pier.story}_{pier.label}",
                failure_mode=FailureMode.COLUMN_MIN_THICKNESS,
                proposal_type=ProposalType.THICKNESS,
                original_config=original_config,
                proposed_config=proposed_config,
                original_sf_flexure=original_sf,
                proposed_sf_flexure=new_sf,
                original_dcr_shear=original_dcr,
                proposed_dcr_shear=new_dcr,
                iterations=iteration,
                success=True,
                changes=changes
            )

        # Guardar mejor resultado
        if new_sf > best_sf:
            best_sf = new_sf
            best_dcr = new_dcr

    # Si llegamos aquí, proponer 300mm aunque no sea suficiente
    # (requiere rediseño adicional)
    proposed_config.thickness = MIN_COLUMN_DIMENSION_MM
    changes.append(f"Espesor: {int(MIN_COLUMN_DIMENSION_MM)}mm")
    changes.append("⚠️ Requiere refuerzo adicional")

    return DesignProposal(
        pier_key=f"{pier.story}_{pier.label}",
        failure_mode=FailureMode.COLUMN_MIN_THICKNESS,
        proposal_type=ProposalType.THICKNESS,
        original_config=original_config,
        proposed_config=proposed_config,
        original_sf_flexure=original_sf,
        proposed_sf_flexure=best_sf,
        original_dcr_shear=original_dcr,
        proposed_dcr_shear=best_dcr,
        iterations=iteration,
        success=False,
        changes=changes
    )
