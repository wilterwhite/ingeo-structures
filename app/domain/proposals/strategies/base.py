# app/domain/proposals/strategies/base.py
"""
Utilidades base para estrategias de propuesta.

Proporciona funciones comunes y el protocolo de verificación
que todas las estrategias utilizan.
"""
from typing import Protocol, List, Optional, Tuple, TYPE_CHECKING

from ...entities.design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
    BOUNDARY_BAR_SEQUENCE,
)
from ...constants.materials import get_bar_area

if TYPE_CHECKING:
    from ...entities import Pier, PierForces


# Factor de seguridad objetivo (pequeño margen sobre 1.0)
TARGET_SF = 1.05

# Máximo de iteraciones por propuesta
MAX_ITERATIONS = 30


def find_boundary_start_index(current_as: float, comparison: str = ">") -> int:
    """
    Encuentra el índice inicial en BOUNDARY_BAR_SEQUENCE para una As dada.

    Args:
        current_as: Área de acero de borde actual (mm²)
        comparison: ">" para aumentar (flexure), ">=" para reducir (reduction)

    Returns:
        Índice en BOUNDARY_BAR_SEQUENCE donde comenzar la búsqueda
    """
    for i, (n, d) in enumerate(BOUNDARY_BAR_SEQUENCE):
        bar_area = get_bar_area(d, 78.5)
        seq_as = n * 2 * bar_area
        if comparison == ">" and seq_as > current_as:
            return i
        if comparison == ">=" and seq_as >= current_as:
            return i
    return len(BOUNDARY_BAR_SEQUENCE) - 1


class VerificationProtocol(Protocol):
    """Protocolo para funciones de verificación."""

    def verify_flexure(self, pier: 'Pier', pier_forces: Optional['PierForces']) -> float:
        """Verifica flexión y retorna SF."""
        ...

    def verify_shear(self, pier: 'Pier', pier_forces: Optional['PierForces']) -> float:
        """Verifica corte y retorna DCR."""
        ...

    def apply_config_to_pier(self, pier: 'Pier', config: ReinforcementConfig) -> 'Pier':
        """Aplica configuración a pier (crea copia)."""
        ...


def create_proposal(
    pier: 'Pier',
    failure_mode: FailureMode,
    proposal_type: ProposalType,
    original_config: ReinforcementConfig,
    proposed_config: ReinforcementConfig,
    original_sf: float,
    new_sf: float,
    original_dcr: float,
    new_dcr: float,
    iterations: int,
    changes: List[str],
    success: bool = True
) -> DesignProposal:
    """Crea una propuesta de diseño con los parámetros dados."""
    return DesignProposal(
        pier_key=f"{pier.story}_{pier.label}",
        failure_mode=failure_mode,
        proposal_type=proposal_type,
        original_config=original_config,
        proposed_config=proposed_config,
        original_sf_flexure=original_sf,
        proposed_sf_flexure=new_sf,
        original_dcr_shear=original_dcr,
        proposed_dcr_shear=new_dcr,
        iterations=iterations,
        success=success,
        changes=changes
    )


def build_changes(
    original: ReinforcementConfig,
    proposed: ReinforcementConfig
) -> List[str]:
    """Construye lista de cambios entre configuraciones."""
    changes = []
    if proposed.n_edge_bars != original.n_edge_bars or proposed.diameter_edge != original.diameter_edge:
        changes.append(f"Borde: {proposed.n_edge_bars}φ{proposed.diameter_edge}")
    if proposed.spacing_h != original.spacing_h or proposed.diameter_h != original.diameter_h:
        changes.append(f"Malla φ{proposed.diameter_h}@{proposed.spacing_h}")
    if proposed.n_stirrup_legs != original.n_stirrup_legs:
        changes.append(f"{proposed.n_stirrup_legs}R")
    if proposed.thickness and proposed.thickness != original.thickness:
        changes.append(f"e={int(proposed.thickness)}mm")
    return changes


def build_reduction_changes(
    original: ReinforcementConfig,
    proposed: ReinforcementConfig
) -> List[str]:
    """Construye lista de cambios de reducción."""
    changes = []
    # Mostrar cambio de espesor primero (es el más importante)
    if proposed.thickness and proposed.thickness != original.thickness:
        changes.append(f"e={int(proposed.thickness)}mm")
    if proposed.n_edge_bars != original.n_edge_bars or proposed.diameter_edge != original.diameter_edge:
        changes.append(f"Borde: {proposed.n_edge_bars}φ{proposed.diameter_edge}")
    if proposed.spacing_h != original.spacing_h:
        changes.append(f"Malla @{proposed.spacing_h}")
    if proposed.diameter_h != original.diameter_h:
        changes.append(f"φ{proposed.diameter_h}")
    changes.append("↓ Optimizado")
    return changes
