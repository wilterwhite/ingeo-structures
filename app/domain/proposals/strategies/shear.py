# app/domain/proposals/strategies/shear.py
"""
Estrategia de propuesta para falla por corte.

Intenta resolver en orden:
1. Reducir espaciamiento de malla
2. Aumentar diámetro de malla
3. Agregar segunda malla (si solo tiene una)
4. Aumentar espesor (fallback)
"""
from typing import Optional, Callable, TYPE_CHECKING
from copy import deepcopy

from ...entities.design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
    MESH_DIAMETER_SEQUENCE,
    MESH_SPACING_SEQUENCE,
)
from ...constants.phi_chapter21 import RHO_MAX
from .base import MAX_ITERATIONS, create_proposal

if TYPE_CHECKING:
    from ...entities import VerticalElement, ElementForces


def propose_for_shear(
    pier: 'VerticalElement',
    pier_forces: Optional['ElementForces'],
    original_config: ReinforcementConfig,
    original_sf: float,
    original_dcr: float,
    verify_flexure: Callable,
    verify_shear: Callable,
    apply_config: Callable,
    propose_with_thickness: Callable
) -> Optional[DesignProposal]:
    """
    Propone solución para falla por corte.

    Estrategia:
    1. Primero reducir espaciamiento de malla
    2. Luego aumentar diámetro de malla
    3. Si no alcanza, agregar segunda malla

    Args:
        pier: Pier a analizar
        pier_forces: Fuerzas del pier
        original_config: Configuración original
        original_sf: SF de flexión original
        original_dcr: DCR de corte original
        verify_flexure: Función para verificar flexión
        verify_shear: Función para verificar corte
        apply_config: Función para aplicar config a pier
        propose_with_thickness: Función fallback para aumentar espesor

    Returns:
        DesignProposal si encuentra solución, None si no
    """
    changes = []
    proposed_config = deepcopy(original_config)

    # Encontrar posición actual en secuencias
    current_spacing_idx = MESH_SPACING_SEQUENCE.index(proposed_config.spacing_h) \
        if proposed_config.spacing_h in MESH_SPACING_SEQUENCE else 0
    current_diameter_idx = MESH_DIAMETER_SEQUENCE.index(proposed_config.diameter_h) \
        if proposed_config.diameter_h in MESH_DIAMETER_SEQUENCE else 0

    iteration = 0

    # Estrategia 1: Reducir espaciamiento
    for spacing_idx in range(current_spacing_idx + 1, len(MESH_SPACING_SEQUENCE)):
        if iteration >= MAX_ITERATIONS:
            break

        proposed_config.spacing_h = MESH_SPACING_SEQUENCE[spacing_idx]
        proposed_config.spacing_v = MESH_SPACING_SEQUENCE[spacing_idx]

        test_pier = apply_config(pier, proposed_config)

        # Verificar cuantía máxima para asegurar ductilidad
        if test_pier.rho_vertical > RHO_MAX:
            continue

        new_dcr = verify_shear(test_pier, pier_forces)
        new_sf = verify_flexure(test_pier, pier_forces)
        iteration += 1

        if new_dcr <= 1.0:
            changes.append(f"Malla @{proposed_config.spacing_h}")
            return create_proposal(
                pier, FailureMode.SHEAR, ProposalType.MESH,
                original_config, proposed_config, original_sf, new_sf,
                original_dcr, new_dcr, iteration, changes
            )

    # Estrategia 2: Aumentar diámetro
    for diameter_idx in range(current_diameter_idx + 1, len(MESH_DIAMETER_SEQUENCE)):
        if iteration >= MAX_ITERATIONS:
            break

        proposed_config.diameter_h = MESH_DIAMETER_SEQUENCE[diameter_idx]
        proposed_config.diameter_v = MESH_DIAMETER_SEQUENCE[diameter_idx]

        # Resetear espaciamiento al mínimo probado
        proposed_config.spacing_h = MESH_SPACING_SEQUENCE[-1]
        proposed_config.spacing_v = MESH_SPACING_SEQUENCE[-1]

        test_pier = apply_config(pier, proposed_config)

        # Verificar cuantía máxima para asegurar ductilidad
        if test_pier.rho_vertical > RHO_MAX:
            continue

        new_dcr = verify_shear(test_pier, pier_forces)
        new_sf = verify_flexure(test_pier, pier_forces)
        iteration += 1

        if new_dcr <= 1.0:
            changes.append(f"Malla φ{proposed_config.diameter_h}@{proposed_config.spacing_h}")
            return create_proposal(
                pier, FailureMode.SHEAR, ProposalType.MESH,
                original_config, proposed_config, original_sf, new_sf,
                original_dcr, new_dcr, iteration, changes
            )

    # Estrategia 3: Agregar segunda malla si solo tiene una
    if original_config.n_meshes == 1:
        proposed_config.n_meshes = 2
        test_pier = apply_config(pier, proposed_config)

        # Verificar cuantía máxima para asegurar ductilidad
        if test_pier.rho_vertical <= RHO_MAX:
            new_dcr = verify_shear(test_pier, pier_forces)
            new_sf = verify_flexure(test_pier, pier_forces)
            iteration += 1

            if new_dcr <= 1.0:
                changes.append("2 mallas")
                return create_proposal(
                    pier, FailureMode.SHEAR, ProposalType.MESH,
                    original_config, proposed_config, original_sf, new_sf,
                    original_dcr, new_dcr, iteration, changes
                )

    # Si nada funciona, proponer aumento de espesor
    return propose_with_thickness(
        pier, pier_forces, original_config, original_sf, original_dcr,
        FailureMode.SHEAR
    )
