# app/domain/proposals/strategies/thickness.py
"""
Estrategia de propuesta para aumento de espesor.

Usado como fallback cuando otras estrategias no resuelven,
y para problemas de esbeltez que requieren mayor rigidez.
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
from ...constants.phi_chapter21 import RHO_MAX
from .base import TARGET_SF, MAX_ITERATIONS, create_proposal, build_changes

if TYPE_CHECKING:
    from ...entities import Pier, PierForces


def propose_with_thickness(
    pier: 'Pier',
    pier_forces: Optional['PierForces'],
    original_config: ReinforcementConfig,
    original_sf: float,
    original_dcr: float,
    failure_mode: FailureMode,
    verify_flexure: Callable,
    verify_shear: Callable,
    apply_config: Callable,
    get_min_thickness: Callable,
    create_best_effort: Callable
) -> Optional[DesignProposal]:
    """
    Propone aumento de espesor cuando otras estrategias fallan.

    Para columnas sísmicas (ACI 318-25 §18.7.2.1), respeta el mínimo de 300mm.

    Args:
        pier: Pier a analizar
        pier_forces: Fuerzas del pier
        original_config: Configuración original
        original_sf: SF de flexión original
        original_dcr: DCR de corte original
        failure_mode: Modo de falla que causó esta propuesta
        verify_flexure: Función para verificar flexión
        verify_shear: Función para verificar corte
        apply_config: Función para aplicar config a pier
        get_min_thickness: Función que retorna espesor mínimo
        create_best_effort: Función para crear propuesta best-effort

    Returns:
        DesignProposal si encuentra solución, best-effort si no
    """
    changes = []
    proposed_config = deepcopy(original_config)

    # Obtener espesor mínimo según clasificación del pier
    min_thickness = get_min_thickness(pier)

    # Encontrar posición actual en secuencia de espesores
    # Considerando tanto el espesor actual como el mínimo requerido
    effective_min = max(pier.thickness, min_thickness)
    start_idx = 0
    for i, t in enumerate(THICKNESS_SEQUENCE):
        if t >= effective_min:
            start_idx = i
            break

    for iteration in range(min(MAX_ITERATIONS, len(THICKNESS_SEQUENCE) - start_idx)):
        new_thickness = THICKNESS_SEQUENCE[start_idx + iteration]
        proposed_config.thickness = new_thickness

        # Crear pier con nuevo espesor
        test_pier = apply_config(pier, proposed_config)

        new_sf = verify_flexure(test_pier, pier_forces)
        new_dcr = verify_shear(test_pier, pier_forces)

        # Verificar si pasa según el modo de falla
        passes = False
        if failure_mode == FailureMode.FLEXURE or failure_mode == FailureMode.SLENDERNESS:
            passes = new_sf >= TARGET_SF
        elif failure_mode == FailureMode.SHEAR:
            passes = new_dcr <= 1.0
        elif failure_mode == FailureMode.COMBINED:
            passes = new_sf >= TARGET_SF and new_dcr <= 1.0

        if passes:
            changes.append(f"Espesor: {int(new_thickness)}mm")
            return create_proposal(
                pier, failure_mode, ProposalType.THICKNESS,
                original_config, proposed_config, original_sf, new_sf,
                original_dcr, new_dcr, iteration + 1, changes
            )

    # No se encontró solución automática - retornar la mejor propuesta encontrada
    # con success=False para indicar que no resuelve el problema
    return create_best_effort(
        pier, pier_forces, failure_mode, original_config, original_sf, original_dcr
    )


def propose_for_slenderness(
    pier: 'Pier',
    pier_forces: Optional['PierForces'],
    original_config: ReinforcementConfig,
    original_sf: float,
    slenderness_reduction: float,
    verify_flexure: Callable,
    verify_shear: Callable,
    apply_config: Callable,
    get_min_thickness: Callable,
    create_best_effort: Callable
) -> Optional[DesignProposal]:
    """
    Propone solución para problemas de esbeltez.

    Estrategia: Aumentar espesor del muro para reducir esbeltez.

    Args:
        pier: Pier a analizar
        pier_forces: Fuerzas del pier
        original_config: Configuración original
        original_sf: SF de flexión original
        slenderness_reduction: Factor de reducción por esbeltez
        verify_flexure: Función para verificar flexión
        verify_shear: Función para verificar corte
        apply_config: Función para aplicar config a pier
        get_min_thickness: Función que retorna espesor mínimo
        create_best_effort: Función para crear propuesta best-effort

    Returns:
        DesignProposal
    """
    return propose_with_thickness(
        pier, pier_forces, original_config, original_sf, 0,
        FailureMode.SLENDERNESS,
        verify_flexure, verify_shear, apply_config,
        get_min_thickness, create_best_effort
    )


def create_best_effort_proposal(
    pier: 'Pier',
    pier_forces: Optional['PierForces'],
    failure_mode: FailureMode,
    original_config: ReinforcementConfig,
    original_sf: float,
    original_dcr: float,
    verify_flexure: Callable,
    verify_shear: Callable,
    apply_config: Callable,
    get_min_thickness: Callable
) -> DesignProposal:
    """
    Crea la mejor propuesta posible iterando incrementalmente.

    Busca la configuración mínima que logra el mejor SF/DCR posible.
    Si ninguna configuración resuelve el problema, retorna success=False.

    Args:
        pier: Pier a analizar
        pier_forces: Fuerzas del pier
        failure_mode: Modo de falla
        original_config: Configuración original
        original_sf: SF de flexión original
        original_dcr: DCR de corte original
        verify_flexure: Función para verificar flexión
        verify_shear: Función para verificar corte
        apply_config: Función para aplicar config a pier
        get_min_thickness: Función que retorna espesor mínimo

    Returns:
        DesignProposal con success=True si resuelve, False si no
    """
    proposed_config = deepcopy(original_config)
    best_config = deepcopy(original_config)
    best_sf = original_sf
    best_dcr = original_dcr
    iterations = 0

    # Obtener espesor mínimo según clasificación del pier
    min_thickness = get_min_thickness(pier)
    effective_min = max(pier.thickness, min_thickness)

    # Iterar incrementalmente: borde -> malla -> espesor
    for n_bars, diameter in BOUNDARY_BAR_SEQUENCE:
        proposed_config.n_edge_bars = n_bars
        proposed_config.diameter_edge = diameter

        for spacing in MESH_SPACING_SEQUENCE:
            proposed_config.spacing_h = spacing
            proposed_config.spacing_v = spacing

            for mesh_diameter in MESH_DIAMETER_SEQUENCE:
                proposed_config.diameter_h = mesh_diameter
                proposed_config.diameter_v = mesh_diameter

                for thickness in THICKNESS_SEQUENCE:
                    if thickness < effective_min:
                        continue

                    proposed_config.thickness = thickness
                    iterations += 1

                    test_pier = apply_config(pier, proposed_config)

                    # Verificar cuantía máxima para asegurar ductilidad
                    if test_pier.rho_vertical > RHO_MAX:
                        continue

                    new_sf = verify_flexure(test_pier, pier_forces)
                    new_dcr = verify_shear(test_pier, pier_forces)

                    # Guardar si es mejor
                    if new_sf > best_sf or (new_sf == best_sf and new_dcr < best_dcr):
                        best_config = deepcopy(proposed_config)
                        best_sf = new_sf
                        best_dcr = new_dcr

                    # Si resuelve, retornar con success=True
                    if new_sf >= TARGET_SF and new_dcr <= 1.0:
                        changes = build_changes(original_config, proposed_config)
                        return DesignProposal(
                            pier_key=f"{pier.story}_{pier.label}",
                            failure_mode=failure_mode,
                            proposal_type=ProposalType.COMBINED,
                            original_config=original_config,
                            proposed_config=proposed_config,
                            original_sf_flexure=original_sf,
                            proposed_sf_flexure=new_sf,
                            original_dcr_shear=original_dcr,
                            proposed_dcr_shear=new_dcr,
                            iterations=iterations,
                            success=True,
                            changes=changes
                        )

                    # Limitar iteraciones para evitar búsqueda exhaustiva
                    if iterations > 100:
                        break
                if iterations > 100:
                    break
            if iterations > 100:
                break
        if iterations > 100:
            break

    # No se encontró solución, retornar mejor esfuerzo
    changes = build_changes(original_config, best_config)
    changes.append("⚠️ Requiere rediseño estructural")

    return DesignProposal(
        pier_key=f"{pier.story}_{pier.label}",
        failure_mode=failure_mode,
        proposal_type=ProposalType.COMBINED,
        original_config=original_config,
        proposed_config=best_config,
        original_sf_flexure=original_sf,
        proposed_sf_flexure=best_sf,
        original_dcr_shear=original_dcr,
        proposed_dcr_shear=best_dcr,
        iterations=iterations,
        success=False,
        changes=changes
    )
