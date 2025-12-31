# app/services/analysis/proposal_service.py
"""
Servicio de propuestas de diseño para piers.

Sistema inteligente que propone soluciones cuando un pier falla verificación,
analizando el modo de falla y proponiendo correcciones específicas.

Lógica de propuestas:
- Flexión falla → Aumentar barras de borde
- Corte falla → Aumentar malla (diámetro o reducir espaciamiento)
- Confinamiento requerido → Aumentar estribos del elemento de borde
- Esbeltez excesiva → Aumentar espesor del muro
"""
from typing import Dict, Any, Optional, List, Tuple
from copy import deepcopy
from dataclasses import replace

from ...domain.entities import Pier, PierForces
from ...domain.constants.materials import get_bar_area
from ...domain.entities.design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
    BOUNDARY_BAR_SEQUENCE,
    MESH_DIAMETER_SEQUENCE,
    MESH_SPACING_SEQUENCE,
    THICKNESS_SEQUENCE,
)
from .flexure_service import FlexureService
from .shear_service import ShearService


class ProposalService:
    """
    Servicio para generar propuestas de diseño inteligentes.

    Analiza el modo de falla y propone correcciones específicas
    usando un enfoque iterativo para encontrar la solución mínima.
    """

    # Factor de seguridad objetivo
    TARGET_SF = 1.05  # Pequeño margen sobre 1.0

    # Máximo de iteraciones por propuesta
    MAX_ITERATIONS = 30

    def __init__(
        self,
        flexure_service: Optional[FlexureService] = None,
        shear_service: Optional[ShearService] = None
    ):
        self._flexure_service = flexure_service or FlexureService()
        self._shear_service = shear_service or ShearService()

    def generate_proposal(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        flexure_sf: float,
        shear_dcr: float,
        boundary_required: bool = False,
        slenderness_reduction: float = 1.0
    ) -> Optional[DesignProposal]:
        """
        Genera una propuesta de diseño si el pier falla verificación.

        Args:
            pier: Pier a analizar
            pier_forces: Fuerzas del pier
            flexure_sf: Factor de seguridad de flexión actual
            shear_dcr: DCR de corte actual (> 1.0 = falla)
            boundary_required: Si se requiere elemento de borde
            slenderness_reduction: Factor de reducción por esbeltez

        Returns:
            DesignProposal si hay propuesta, None si pasa o no hay solución
        """
        # Determinar modo de falla
        failure_mode = self._determine_failure_mode(
            flexure_sf, shear_dcr, boundary_required, slenderness_reduction
        )

        if failure_mode == FailureMode.NONE:
            return None

        # Crear configuración original
        original_config = self._pier_to_config(pier)

        # Generar propuesta según modo de falla
        if failure_mode == FailureMode.FLEXURE:
            return self._propose_for_flexure(
                pier, pier_forces, original_config, flexure_sf, shear_dcr
            )
        elif failure_mode == FailureMode.SHEAR:
            return self._propose_for_shear(
                pier, pier_forces, original_config, flexure_sf, shear_dcr
            )
        elif failure_mode == FailureMode.COMBINED:
            return self._propose_combined(
                pier, pier_forces, original_config, flexure_sf, shear_dcr
            )
        elif failure_mode == FailureMode.SLENDERNESS:
            return self._propose_for_slenderness(
                pier, pier_forces, original_config, flexure_sf, slenderness_reduction
            )

        return None

    def _determine_failure_mode(
        self,
        flexure_sf: float,
        shear_dcr: float,
        boundary_required: bool,
        slenderness_reduction: float
    ) -> FailureMode:
        """Determina el modo de falla principal."""
        flexure_fails = flexure_sf < 1.0
        shear_fails = shear_dcr > 1.0
        slenderness_issue = slenderness_reduction < 0.7  # Reducción significativa

        if flexure_fails and shear_fails:
            return FailureMode.COMBINED
        elif flexure_fails:
            if slenderness_issue:
                return FailureMode.SLENDERNESS
            return FailureMode.FLEXURE
        elif shear_fails:
            return FailureMode.SHEAR
        elif boundary_required:
            return FailureMode.CONFINEMENT

        return FailureMode.NONE

    def _pier_to_config(self, pier: Pier) -> ReinforcementConfig:
        """Convierte pier a configuración de armadura."""
        return ReinforcementConfig(
            n_edge_bars=pier.n_edge_bars,
            diameter_edge=pier.diameter_edge,
            n_meshes=pier.n_meshes,
            diameter_v=pier.diameter_v,
            spacing_v=pier.spacing_v,
            diameter_h=pier.diameter_h,
            spacing_h=pier.spacing_h,
            stirrup_diameter=pier.stirrup_diameter,
            stirrup_spacing=pier.stirrup_spacing,
            thickness=pier.thickness
        )

    def _apply_config_to_pier(self, pier: Pier, config: ReinforcementConfig) -> Pier:
        """Aplica una configuración a un pier (crea copia modificada)."""
        # Crear copia del pier
        new_pier = deepcopy(pier)
        new_pier.update_reinforcement(
            n_edge_bars=config.n_edge_bars,
            diameter_edge=config.diameter_edge,
            n_meshes=config.n_meshes,
            diameter_v=config.diameter_v,
            spacing_v=config.spacing_v,
            diameter_h=config.diameter_h,
            spacing_h=config.spacing_h,
            stirrup_diameter=config.stirrup_diameter,
            stirrup_spacing=config.stirrup_spacing
        )
        if config.thickness and config.thickness != pier.thickness:
            new_pier.thickness = config.thickness
        return new_pier

    def _verify_flexure(self, pier: Pier, pier_forces: Optional[PierForces]) -> float:
        """Verifica flexión y retorna SF."""
        result = self._flexure_service.check_flexure(pier, pier_forces)
        sf = result.get('sf', 0)
        return min(sf, 100)  # Cap at 100

    def _verify_shear(self, pier: Pier, pier_forces: Optional[PierForces]) -> float:
        """Verifica corte y retorna DCR."""
        result = self._shear_service.check_shear(pier, pier_forces)
        return result.get('dcr_combined', 0)

    def _create_proposal(
        self,
        pier: Pier,
        failure_mode: FailureMode,
        proposal_type: ProposalType,
        original_config: ReinforcementConfig,
        proposed_config: ReinforcementConfig,
        original_sf: float,
        new_sf: float,
        original_dcr: float,
        new_dcr: float,
        iterations: int,
        changes: List[str]
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
            success=True,
            changes=changes
        )

    # =========================================================================
    # PROPUESTAS POR MODO DE FALLA
    # =========================================================================

    def _propose_for_flexure(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float
    ) -> Optional[DesignProposal]:
        """
        Propone solución para falla por flexión.

        Estrategia: Aumentar barras de borde progresivamente.
        """
        # Encontrar posición actual en la secuencia
        current_as = original_config.As_edge
        start_idx = 0
        for i, (n, d) in enumerate(BOUNDARY_BAR_SEQUENCE):
            bar_area = get_bar_area(d, 78.5)
            seq_as = n * 2 * bar_area
            if seq_as > current_as:
                start_idx = i
                break

        changes = []
        proposed_config = deepcopy(original_config)

        for iteration in range(self.MAX_ITERATIONS):
            if start_idx + iteration >= len(BOUNDARY_BAR_SEQUENCE):
                break

            n_bars, diameter = BOUNDARY_BAR_SEQUENCE[start_idx + iteration]
            proposed_config.n_edge_bars = n_bars
            proposed_config.diameter_edge = diameter

            # Aplicar y verificar
            test_pier = self._apply_config_to_pier(pier, proposed_config)
            new_sf = self._verify_flexure(test_pier, pier_forces)
            new_dcr = self._verify_shear(test_pier, pier_forces)

            if new_sf >= self.TARGET_SF:
                changes.append(f"Borde: {n_bars}φ{diameter}")
                return self._create_proposal(
                    pier, FailureMode.FLEXURE, ProposalType.BOUNDARY_BARS,
                    original_config, proposed_config, original_sf, new_sf,
                    original_dcr, new_dcr, iteration + 1, changes
                )

        # No se encontró solución solo con borde, intentar con espesor
        return self._propose_with_thickness(
            pier, pier_forces, original_config, original_sf, original_dcr,
            FailureMode.FLEXURE
        )

    def _propose_for_shear(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float
    ) -> Optional[DesignProposal]:
        """
        Propone solución para falla por corte.

        Estrategia:
        1. Primero reducir espaciamiento de malla
        2. Luego aumentar diámetro de malla
        3. Si no alcanza, agregar segunda malla
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
            if iteration >= self.MAX_ITERATIONS:
                break

            proposed_config.spacing_h = MESH_SPACING_SEQUENCE[spacing_idx]
            proposed_config.spacing_v = MESH_SPACING_SEQUENCE[spacing_idx]

            test_pier = self._apply_config_to_pier(pier, proposed_config)
            new_dcr = self._verify_shear(test_pier, pier_forces)
            new_sf = self._verify_flexure(test_pier, pier_forces)
            iteration += 1

            if new_dcr <= 1.0:
                changes.append(f"Malla @{proposed_config.spacing_h}")
                return self._create_proposal(
                    pier, FailureMode.SHEAR, ProposalType.MESH,
                    original_config, proposed_config, original_sf, new_sf,
                    original_dcr, new_dcr, iteration, changes
                )

        # Estrategia 2: Aumentar diámetro
        for diameter_idx in range(current_diameter_idx + 1, len(MESH_DIAMETER_SEQUENCE)):
            if iteration >= self.MAX_ITERATIONS:
                break

            proposed_config.diameter_h = MESH_DIAMETER_SEQUENCE[diameter_idx]
            proposed_config.diameter_v = MESH_DIAMETER_SEQUENCE[diameter_idx]

            # Resetear espaciamiento al mínimo probado
            proposed_config.spacing_h = MESH_SPACING_SEQUENCE[-1]
            proposed_config.spacing_v = MESH_SPACING_SEQUENCE[-1]

            test_pier = self._apply_config_to_pier(pier, proposed_config)
            new_dcr = self._verify_shear(test_pier, pier_forces)
            new_sf = self._verify_flexure(test_pier, pier_forces)
            iteration += 1

            if new_dcr <= 1.0:
                changes.append(f"Malla φ{proposed_config.diameter_h}@{proposed_config.spacing_h}")
                return self._create_proposal(
                    pier, FailureMode.SHEAR, ProposalType.MESH,
                    original_config, proposed_config, original_sf, new_sf,
                    original_dcr, new_dcr, iteration, changes
                )

        # Estrategia 3: Agregar segunda malla si solo tiene una
        if original_config.n_meshes == 1:
            proposed_config.n_meshes = 2
            test_pier = self._apply_config_to_pier(pier, proposed_config)
            new_dcr = self._verify_shear(test_pier, pier_forces)
            new_sf = self._verify_flexure(test_pier, pier_forces)
            iteration += 1

            if new_dcr <= 1.0:
                changes.append("2 mallas")
                return self._create_proposal(
                    pier, FailureMode.SHEAR, ProposalType.MESH,
                    original_config, proposed_config, original_sf, new_sf,
                    original_dcr, new_dcr, iteration, changes
                )

        # Si nada funciona, proponer aumento de espesor
        return self._propose_with_thickness(
            pier, pier_forces, original_config, original_sf, original_dcr,
            FailureMode.SHEAR
        )

    def _propose_combined(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float
    ) -> Optional[DesignProposal]:
        """
        Propone solución para falla combinada (flexión + corte).

        Estrategia: Aumentar ambos (borde para flexión, malla para corte).
        """
        changes = []
        proposed_config = deepcopy(original_config)

        # Encontrar posiciones actuales
        current_as = original_config.As_edge
        boundary_start_idx = 0
        for i, (n, d) in enumerate(BOUNDARY_BAR_SEQUENCE):
            bar_area = get_bar_area(d, 78.5)
            seq_as = n * 2 * bar_area
            if seq_as > current_as:
                boundary_start_idx = i
                break

        current_spacing_idx = MESH_SPACING_SEQUENCE.index(proposed_config.spacing_h) \
            if proposed_config.spacing_h in MESH_SPACING_SEQUENCE else 0

        # Iterar combinaciones
        for iteration in range(self.MAX_ITERATIONS):
            # Avanzar en ambas secuencias alternadamente
            boundary_idx = boundary_start_idx + (iteration // 2)
            spacing_idx = min(current_spacing_idx + 1 + (iteration // 2), len(MESH_SPACING_SEQUENCE) - 1)

            if boundary_idx >= len(BOUNDARY_BAR_SEQUENCE):
                break

            n_bars, diameter = BOUNDARY_BAR_SEQUENCE[boundary_idx]
            proposed_config.n_edge_bars = n_bars
            proposed_config.diameter_edge = diameter
            proposed_config.spacing_h = MESH_SPACING_SEQUENCE[spacing_idx]
            proposed_config.spacing_v = MESH_SPACING_SEQUENCE[spacing_idx]

            test_pier = self._apply_config_to_pier(pier, proposed_config)
            new_sf = self._verify_flexure(test_pier, pier_forces)
            new_dcr = self._verify_shear(test_pier, pier_forces)

            if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
                changes.append(f"Borde: {n_bars}φ{diameter}")
                changes.append(f"Malla @{proposed_config.spacing_h}")
                return self._create_proposal(
                    pier, FailureMode.COMBINED, ProposalType.COMBINED,
                    original_config, proposed_config, original_sf, new_sf,
                    original_dcr, new_dcr, iteration + 1, changes
                )

        # Si no encuentra solución, intentar con espesor
        return self._propose_with_thickness(
            pier, pier_forces, original_config, original_sf, original_dcr,
            FailureMode.COMBINED
        )

    def _propose_for_slenderness(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        original_config: ReinforcementConfig,
        original_sf: float,
        slenderness_reduction: float
    ) -> Optional[DesignProposal]:
        """
        Propone solución para problemas de esbeltez.

        Estrategia: Aumentar espesor del muro.
        """
        return self._propose_with_thickness(
            pier, pier_forces, original_config, original_sf, 0,
            FailureMode.SLENDERNESS
        )

    def _propose_with_thickness(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float,
        failure_mode: FailureMode
    ) -> Optional[DesignProposal]:
        """
        Propone aumento de espesor cuando otras estrategias fallan.
        """
        changes = []
        proposed_config = deepcopy(original_config)

        # Encontrar posición actual en secuencia de espesores
        current_thickness = pier.thickness
        start_idx = 0
        for i, t in enumerate(THICKNESS_SEQUENCE):
            if t > current_thickness:
                start_idx = i
                break

        for iteration in range(min(self.MAX_ITERATIONS, len(THICKNESS_SEQUENCE) - start_idx)):
            new_thickness = THICKNESS_SEQUENCE[start_idx + iteration]
            proposed_config.thickness = new_thickness

            # Crear pier con nuevo espesor
            test_pier = deepcopy(pier)
            test_pier.thickness = new_thickness

            new_sf = self._verify_flexure(test_pier, pier_forces)
            new_dcr = self._verify_shear(test_pier, pier_forces)

            # Verificar si pasa según el modo de falla
            passes = False
            if failure_mode == FailureMode.FLEXURE or failure_mode == FailureMode.SLENDERNESS:
                passes = new_sf >= self.TARGET_SF
            elif failure_mode == FailureMode.SHEAR:
                passes = new_dcr <= 1.0
            elif failure_mode == FailureMode.COMBINED:
                passes = new_sf >= self.TARGET_SF and new_dcr <= 1.0

            if passes:
                changes.append(f"Espesor: {int(new_thickness)}mm")
                return self._create_proposal(
                    pier, failure_mode, ProposalType.THICKNESS,
                    original_config, proposed_config, original_sf, new_sf,
                    original_dcr, new_dcr, iteration + 1, changes
                )

        # No se encontró solución automática - retornar la mejor propuesta encontrada
        # con success=False para indicar que no resuelve el problema
        return self._create_best_effort_proposal(
            pier, pier_forces, failure_mode, original_config, original_sf, original_dcr
        )

    def _create_best_effort_proposal(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        failure_mode: FailureMode,
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float
    ) -> DesignProposal:
        """
        Crea una propuesta con la configuración máxima disponible.

        Se usa cuando ninguna estrategia logra resolver el problema.
        Retorna success=False para indicar que requiere rediseño estructural.
        """
        # Configurar con los máximos disponibles
        proposed_config = deepcopy(original_config)
        changes = []

        # Máximas barras de borde
        max_n_bars, max_diameter = BOUNDARY_BAR_SEQUENCE[-1]
        proposed_config.n_edge_bars = max_n_bars
        proposed_config.diameter_edge = max_diameter
        changes.append(f"Borde: {max_n_bars}φ{max_diameter}")

        # Máxima malla
        proposed_config.diameter_h = MESH_DIAMETER_SEQUENCE[-1]
        proposed_config.diameter_v = MESH_DIAMETER_SEQUENCE[-1]
        proposed_config.spacing_h = MESH_SPACING_SEQUENCE[-1]
        proposed_config.spacing_v = MESH_SPACING_SEQUENCE[-1]
        changes.append(f"Malla φ{MESH_DIAMETER_SEQUENCE[-1]}@{MESH_SPACING_SEQUENCE[-1]}")

        # Máximo espesor
        proposed_config.thickness = THICKNESS_SEQUENCE[-1]
        changes.append(f"Espesor: {THICKNESS_SEQUENCE[-1]}mm")

        # Verificar con la configuración máxima
        test_pier = self._apply_config_to_pier(pier, proposed_config)
        test_pier.thickness = THICKNESS_SEQUENCE[-1]
        new_sf = self._verify_flexure(test_pier, pier_forces)
        new_dcr = self._verify_shear(test_pier, pier_forces)

        changes.append("⚠️ Requiere rediseño")

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
            iterations=self.MAX_ITERATIONS,
            success=False,  # Indica que no resuelve el problema
            changes=changes
        )

    # =========================================================================
    # API PÚBLICA
    # =========================================================================

    def analyze_and_propose(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces]
    ) -> Tuple[Dict[str, Any], Optional[DesignProposal]]:
        """
        Analiza un pier y genera propuesta si falla.

        Convenience method que realiza verificaciones y genera propuesta
        en una sola llamada.

        Args:
            pier: Pier a analizar
            pier_forces: Fuerzas del pier

        Returns:
            Tuple (verification_results, proposal)
        """
        # Verificar flexión
        flexure_result = self._flexure_service.check_flexure(pier, pier_forces)
        flexure_sf = flexure_result.get('sf', 100)
        slenderness = flexure_result.get('slenderness', {})
        slenderness_reduction = slenderness.get('reduction', 1.0)

        # Verificar corte
        shear_result = self._shear_service.check_shear(pier, pier_forces)
        shear_dcr = shear_result.get('dcr_combined', 0)

        verification = {
            'flexure_sf': flexure_sf,
            'flexure_status': flexure_result.get('status', 'OK'),
            'shear_dcr': shear_dcr,
            'shear_status': shear_result.get('status', 'OK'),
            'slenderness_reduction': slenderness_reduction,
            'overall_ok': flexure_sf >= 1.0 and shear_dcr <= 1.0
        }

        # Generar propuesta si falla
        proposal = None
        if not verification['overall_ok']:
            proposal = self.generate_proposal(
                pier=pier,
                pier_forces=pier_forces,
                flexure_sf=flexure_sf,
                shear_dcr=shear_dcr,
                slenderness_reduction=slenderness_reduction
            )

        return verification, proposal
