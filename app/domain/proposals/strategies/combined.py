# app/domain/proposals/strategies/combined.py
"""
Estrategia de propuesta para falla combinada (flexión + corte).

Búsqueda exhaustiva por espesor creciente, probando combinaciones
de refuerzo hasta encontrar SF >= 1.0 y DCR <= 1.0.
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
    STIRRUP_LEGS_SEQUENCE,
)
from ...constants.phi_chapter21 import RHO_MAX
from .base import TARGET_SF, create_proposal, build_changes

if TYPE_CHECKING:
    from ...entities import Pier, PierForces


def find_solution_for_thickness(
    pier: 'Pier',
    pier_forces: Optional['PierForces'],
    original_config: ReinforcementConfig,
    thickness: float,
    max_legs: int,
    original_sf: float,
    original_dcr: float,
    verify_flexure: Callable,
    verify_shear: Callable,
    apply_config: Callable
) -> Optional[DesignProposal]:
    """
    Busca la solución mínima para un espesor dado.

    Itera borde → malla → ramas hasta encontrar SF >= 1.0.
    Verifica que la cuantía no exceda ρmax para asegurar ductilidad.

    Args:
        pier: Pier a analizar
        pier_forces: Fuerzas del pier
        original_config: Configuración original
        thickness: Espesor a probar (mm)
        max_legs: Máximo de ramas de estribo para este espesor
        original_sf: SF de flexión original
        original_dcr: DCR de corte original
        verify_flexure: Función para verificar flexión
        verify_shear: Función para verificar corte
        apply_config: Función para aplicar config a pier

    Returns:
        DesignProposal si encuentra solución, None si no
    """
    proposed_config = deepcopy(original_config)
    proposed_config.thickness = thickness

    # Iterar barras de borde (ordenadas por área creciente)
    for n_bars, diameter in BOUNDARY_BAR_SEQUENCE:
        proposed_config.n_edge_bars = n_bars
        proposed_config.diameter_edge = diameter

        # Iterar espaciamiento de malla (de mayor a menor = menos acero primero)
        for spacing in MESH_SPACING_SEQUENCE:
            proposed_config.spacing_h = spacing
            proposed_config.spacing_v = spacing

            # Iterar diámetro de malla
            for mesh_diameter in MESH_DIAMETER_SEQUENCE:
                proposed_config.diameter_h = mesh_diameter
                proposed_config.diameter_v = mesh_diameter

                # Iterar ramas de estribos
                for n_legs in STIRRUP_LEGS_SEQUENCE:
                    if n_legs > max_legs:
                        continue

                    proposed_config.n_stirrup_legs = n_legs

                    test_pier = apply_config(pier, proposed_config)

                    # Verificar cuantía máxima para asegurar ductilidad
                    # Si ρ > ρmax, saltar esta configuración (falla frágil)
                    if test_pier.rho_vertical > RHO_MAX:
                        continue

                    new_sf = verify_flexure(test_pier, pier_forces)
                    new_dcr = verify_shear(test_pier, pier_forces)

                    if new_sf >= TARGET_SF and new_dcr <= 1.0:
                        changes = build_changes(original_config, proposed_config)
                        return create_proposal(
                            pier, FailureMode.COMBINED, ProposalType.COMBINED,
                            original_config, proposed_config, original_sf, new_sf,
                            original_dcr, new_dcr, 1, changes
                        )

    return None


def _get_max_config_for_thickness(
    original_config: ReinforcementConfig,
    thickness: float,
    max_legs: int
) -> ReinforcementConfig:
    """Retorna configuración máxima para un espesor dado."""
    config = deepcopy(original_config)
    config.thickness = thickness
    config.n_edge_bars, config.diameter_edge = BOUNDARY_BAR_SEQUENCE[-1]
    config.spacing_h = MESH_SPACING_SEQUENCE[-1]
    config.spacing_v = MESH_SPACING_SEQUENCE[-1]
    config.diameter_h = MESH_DIAMETER_SEQUENCE[-1]
    config.diameter_v = MESH_DIAMETER_SEQUENCE[-1]
    config.n_stirrup_legs = max_legs
    return config


def propose_combined(
    pier: 'Pier',
    pier_forces: Optional['PierForces'],
    original_config: ReinforcementConfig,
    original_sf: float,
    original_dcr: float,
    verify_flexure: Callable,
    verify_shear: Callable,
    apply_config: Callable,
    get_min_thickness: Callable
) -> Optional[DesignProposal]:
    """
    Propone solución para falla combinada (flexión + corte).

    Estrategia: búsqueda exhaustiva por espesor creciente.
    Para cada espesor, prueba combinaciones de refuerzo hasta encontrar SF >= 1.0.
    Se detiene en la primera solución viable (la más económica).

    Args:
        pier: Pier a analizar
        pier_forces: Fuerzas del pier
        original_config: Configuración original
        original_sf: SF de flexión original
        original_dcr: DCR de corte original
        verify_flexure: Función para verificar flexión
        verify_shear: Función para verificar corte
        apply_config: Función para aplicar config a pier
        get_min_thickness: Función que retorna espesor mínimo para el pier

    Returns:
        DesignProposal (con success=True si resuelve, False si no)
    """
    best_config = deepcopy(original_config)
    best_sf = original_sf
    best_dcr = original_dcr

    # Obtener espesor mínimo según clasificación del pier
    min_thickness = get_min_thickness(pier)
    effective_min = max(pier.thickness, min_thickness)

    # Iterar espesores desde el mínimo efectivo
    for thickness in THICKNESS_SEQUENCE:
        if thickness < effective_min:
            continue

        # Calcular máximo de ramas para este espesor
        max_legs = min(int(thickness // 100), STIRRUP_LEGS_SEQUENCE[-1])

        # Probar combinaciones de refuerzo para este espesor
        result = find_solution_for_thickness(
            pier, pier_forces, original_config, thickness, max_legs,
            original_sf, original_dcr,
            verify_flexure, verify_shear, apply_config
        )

        if result is not None:
            return result

        # Actualizar mejor configuración si mejoró
        test_config = _get_max_config_for_thickness(original_config, thickness, max_legs)
        test_pier = apply_config(pier, test_config)
        test_sf = verify_flexure(test_pier, pier_forces)
        test_dcr = verify_shear(test_pier, pier_forces)

        if test_sf > best_sf:
            best_config = test_config
            best_sf = test_sf
            best_dcr = test_dcr

    # No se encontró solución, retornar mejor esfuerzo con success=False
    changes = build_changes(original_config, best_config)
    changes.append("⚠️ Requiere rediseño")

    return DesignProposal(
        pier_key=f"{pier.story}_{pier.label}",
        failure_mode=FailureMode.COMBINED,
        proposal_type=ProposalType.COMBINED,
        original_config=original_config,
        proposed_config=best_config,
        original_sf_flexure=original_sf,
        proposed_sf_flexure=best_sf,
        original_dcr_shear=original_dcr,
        proposed_dcr_shear=best_dcr,
        iterations=len(THICKNESS_SEQUENCE),
        success=False,
        changes=changes
    )
