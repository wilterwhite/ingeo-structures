# app/domain/proposals/strategies/reduction.py
"""
Estrategia de propuesta para piers sobrediseñados.

Reduce armadura manteniendo SF >= 1.05 y ρ >= ρmin,
buscando optimizar el diseño sin comprometer seguridad.
"""
from typing import Optional, Callable, TYPE_CHECKING
from copy import deepcopy

from ...entities.design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
    BOUNDARY_BAR_SEQUENCE,
    MESH_DIAMETER_SEQUENCE,
    MESH_SPACING_SEQUENCE,
    THICKNESS_SEQUENCE,
)
from ...constants.reinforcement import RHO_MIN
from .base import TARGET_SF, build_reduction_changes, find_boundary_start_index

if TYPE_CHECKING:
    from ...entities import VerticalElement, ElementForces


def propose_for_reduction(
    pier: 'VerticalElement',
    pier_forces: Optional['ElementForces'],
    original_config: ReinforcementConfig,
    original_sf: float,
    original_dcr: float,
    verify_flexure: Callable,
    verify_shear: Callable,
    apply_config: Callable,
    get_min_thickness: Callable
) -> Optional[DesignProposal]:
    """
    Propone reducción de armadura para piers sobrediseñados.

    Estrategia (mantiene SF >= 1.05 y ρ >= ρmin):
    1. Reducir espesor (si hay margen suficiente)
    2. Reducir barras de borde
    3. Aumentar espaciamiento de malla
    4. Reducir diámetro de malla

    La reducción se detiene cuando:
    - SF < 1.15 (cercano al objetivo)
    - Se alcanza la cuantía mínima ρmin = 0.25%
    - DCR > 0.85 (cercano al límite de corte)

    Args:
        pier: Pier a analizar
        pier_forces: Fuerzas del pier
        original_config: Configuración original
        original_sf: SF de flexión original (debe ser > 1.5)
        original_dcr: DCR de corte original (debe ser < 0.7)
        verify_flexure: Función para verificar flexión
        verify_shear: Función para verificar corte
        apply_config: Función para aplicar config a pier
        get_min_thickness: Función que retorna espesor mínimo

    Returns:
        DesignProposal si encuentra reducción válida, None si no
    """
    proposed_config = deepcopy(original_config)

    best_config = deepcopy(original_config)
    best_sf = original_sf
    best_dcr = original_dcr
    iterations = 0

    # =================================================================
    # Estrategia 0: Reducir espesor primero (mayor ahorro de material)
    # Solo si SF > 2.0 y hay espesores menores disponibles
    # Para columnas sísmicas: no reducir por debajo de 300mm (§18.7.2.1)
    # =================================================================
    min_thickness = get_min_thickness(pier)

    if original_sf > 2.0:
        # Iterar espesores menores
        for thickness in reversed(THICKNESS_SEQUENCE):
            if thickness >= pier.thickness:
                continue  # Solo espesores menores
            if thickness < min_thickness:
                continue  # Respetar mínimo para columnas sísmicas

            proposed_config = deepcopy(original_config)
            proposed_config.thickness = thickness

            test_pier = apply_config(pier, proposed_config)
            iterations += 1

            # Verificar cuantía mínima
            if test_pier.rho_vertical < RHO_MIN:
                continue

            new_sf = verify_flexure(test_pier, pier_forces)
            new_dcr = verify_shear(test_pier, pier_forces)

            # Verificar viabilidad
            if new_sf >= TARGET_SF and new_dcr <= 1.0:
                best_config = deepcopy(proposed_config)
                best_sf = new_sf
                best_dcr = new_dcr

                # Si SF está en rango aceptable, usar esta configuración
                if new_sf < 1.5:
                    break
            else:
                # Espesor muy pequeño, no seguir reduciendo
                break

    # Si ya encontramos una buena reducción con espesor, retornar
    if best_sf < original_sf and best_sf < 1.5:
        changes = build_reduction_changes(original_config, best_config)
        return DesignProposal(
            pier_key=f"{pier.story}_{pier.label}",
            failure_mode=FailureMode.OVERDESIGNED,
            proposal_type=ProposalType.REDUCTION,
            original_config=original_config,
            proposed_config=best_config,
            original_sf_flexure=original_sf,
            proposed_sf_flexure=best_sf,
            original_dcr_shear=original_dcr,
            proposed_dcr_shear=best_dcr,
            iterations=iterations,
            success=True,
            changes=changes
        )

    # =================================================================
    # Estrategia 1: Reducir barras de borde
    # =================================================================
    proposed_config = deepcopy(best_config)

    current_boundary_idx = find_boundary_start_index(proposed_config.As_edge, ">=")

    for boundary_idx in range(current_boundary_idx - 1, -1, -1):
        n_bars, diameter = BOUNDARY_BAR_SEQUENCE[boundary_idx]
        proposed_config.n_edge_bars = n_bars
        proposed_config.diameter_edge = diameter

        test_pier = apply_config(pier, proposed_config)
        iterations += 1

        if test_pier.rho_vertical < RHO_MIN:
            break

        new_sf = verify_flexure(test_pier, pier_forces)
        new_dcr = verify_shear(test_pier, pier_forces)

        if new_sf >= TARGET_SF and new_dcr <= 1.0:
            best_config = deepcopy(proposed_config)
            best_sf = new_sf
            best_dcr = new_dcr

            if new_sf < 1.15:
                break
        else:
            proposed_config = deepcopy(best_config)
            break

    # =================================================================
    # Estrategia 2: Aumentar espaciamiento de malla
    # =================================================================
    current_spacing_idx = MESH_SPACING_SEQUENCE.index(proposed_config.spacing_v) \
        if proposed_config.spacing_v in MESH_SPACING_SEQUENCE else len(MESH_SPACING_SEQUENCE) - 1

    for spacing_idx in range(current_spacing_idx - 1, -1, -1):
        proposed_config.spacing_v = MESH_SPACING_SEQUENCE[spacing_idx]
        proposed_config.spacing_h = MESH_SPACING_SEQUENCE[spacing_idx]

        test_pier = apply_config(pier, proposed_config)
        iterations += 1

        if test_pier.rho_vertical < RHO_MIN:
            proposed_config.spacing_v = best_config.spacing_v
            proposed_config.spacing_h = best_config.spacing_h
            break

        new_sf = verify_flexure(test_pier, pier_forces)
        new_dcr = verify_shear(test_pier, pier_forces)

        if new_sf >= TARGET_SF and new_dcr <= 1.0:
            best_config = deepcopy(proposed_config)
            best_sf = new_sf
            best_dcr = new_dcr

            if new_sf < 1.15:
                break
        else:
            proposed_config = deepcopy(best_config)
            break

    # =================================================================
    # Estrategia 3: Reducir diámetro de malla
    # =================================================================
    current_diameter_idx = MESH_DIAMETER_SEQUENCE.index(proposed_config.diameter_v) \
        if proposed_config.diameter_v in MESH_DIAMETER_SEQUENCE else 0

    for diameter_idx in range(current_diameter_idx - 1, -1, -1):
        proposed_config.diameter_v = MESH_DIAMETER_SEQUENCE[diameter_idx]
        proposed_config.diameter_h = MESH_DIAMETER_SEQUENCE[diameter_idx]

        test_pier = apply_config(pier, proposed_config)
        iterations += 1

        if test_pier.rho_vertical < RHO_MIN:
            proposed_config.diameter_v = best_config.diameter_v
            proposed_config.diameter_h = best_config.diameter_h
            break

        new_sf = verify_flexure(test_pier, pier_forces)
        new_dcr = verify_shear(test_pier, pier_forces)

        if new_sf >= TARGET_SF and new_dcr <= 1.0:
            best_config = deepcopy(proposed_config)
            best_sf = new_sf
            best_dcr = new_dcr

            if new_sf < 1.15:
                break
        else:
            proposed_config = deepcopy(best_config)
            break

    # Si se encontró una reducción válida, crear propuesta
    if best_sf < original_sf:
        changes = build_reduction_changes(original_config, best_config)
        return DesignProposal(
            pier_key=f"{pier.story}_{pier.label}",
            failure_mode=FailureMode.OVERDESIGNED,
            proposal_type=ProposalType.REDUCTION,
            original_config=original_config,
            proposed_config=best_config,
            original_sf_flexure=original_sf,
            proposed_sf_flexure=best_sf,
            original_dcr_shear=original_dcr,
            proposed_dcr_shear=best_dcr,
            iterations=iterations,
            success=True,
            changes=changes
        )

    return None
