# app/domain/proposals/strategies/flexure.py
"""
Estrategia de propuesta para falla por flexión.

Aumenta progresivamente las barras de borde hasta alcanzar
el factor de seguridad objetivo.
"""
from typing import Optional, Callable, TYPE_CHECKING
from copy import deepcopy

from ...entities.design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
    BOUNDARY_BAR_SEQUENCE,
)
from ...constants.phi_chapter21 import RHO_MAX
from .base import (
    TARGET_SF,
    MAX_ITERATIONS,
    create_proposal,
    find_boundary_start_index,
)

if TYPE_CHECKING:
    from ...entities import Pier, PierForces


def propose_for_flexure(
    pier: 'Pier',
    pier_forces: Optional['PierForces'],
    original_config: ReinforcementConfig,
    original_sf: float,
    original_dcr: float,
    verify_flexure: Callable,
    verify_shear: Callable,
    apply_config: Callable,
    propose_with_thickness: Callable
) -> Optional[DesignProposal]:
    """
    Propone solución para falla por flexión.

    Estrategia: Aumentar barras de borde progresivamente.
    Verifica que la cuantía no exceda ρmax para asegurar ductilidad.

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
    # Encontrar posición actual en la secuencia
    start_idx = find_boundary_start_index(original_config.As_edge, ">")

    changes = []
    proposed_config = deepcopy(original_config)

    for iteration in range(MAX_ITERATIONS):
        if start_idx + iteration >= len(BOUNDARY_BAR_SEQUENCE):
            break

        n_bars, diameter = BOUNDARY_BAR_SEQUENCE[start_idx + iteration]
        proposed_config.n_edge_bars = n_bars
        proposed_config.diameter_edge = diameter

        # Aplicar y verificar
        test_pier = apply_config(pier, proposed_config)

        # Verificar cuantía máxima para asegurar ductilidad
        if test_pier.rho_vertical > RHO_MAX:
            continue

        new_sf = verify_flexure(test_pier, pier_forces)
        new_dcr = verify_shear(test_pier, pier_forces)

        if new_sf >= TARGET_SF:
            changes.append(f"Borde: {n_bars}φ{diameter}")
            return create_proposal(
                pier, FailureMode.FLEXURE, ProposalType.BOUNDARY_BARS,
                original_config, proposed_config, original_sf, new_sf,
                original_dcr, new_dcr, iteration + 1, changes
            )

    # No se encontró solución solo con borde, intentar con espesor
    return propose_with_thickness(
        pier, pier_forces, original_config, original_sf, original_dcr,
        FailureMode.FLEXURE
    )
