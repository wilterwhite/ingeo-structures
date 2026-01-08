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
from ...domain.constants.phi_chapter21 import RHO_MAX
from ...domain.constants.reinforcement import RHO_MIN
from ...domain.entities.design_proposal import (
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
from ...domain.chapter18.wall_piers import WallPierService, WallPierCategory
from .flexocompression_service import FlexocompressionService
from .shear import ShearService


class ProposalService:
    """
    Servicio para generar propuestas de diseño inteligentes.

    Analiza el modo de falla y propone correcciones específicas
    usando un enfoque iterativo para encontrar la solución mínima.

    También detecta piers sobrediseñados (SF >> 1.0) y propone
    reducción de armadura manteniendo la cuantía mínima.
    """

    # Factor de seguridad objetivo
    TARGET_SF = 1.05  # Pequeño margen sobre 1.0

    # Umbrales para detección de sobrediseño
    OVERDESIGNED_SF_MIN = 1.5   # SF mínimo para considerar sobrediseño
    OVERDESIGNED_DCR_MAX = 0.7  # DCR máximo para considerar sobrediseño

    # Cuantía mínima vertical según ACI 318-25 §11.6.1

    # Máximo de iteraciones por propuesta
    MAX_ITERATIONS = 30

    # Espesor mínimo para columnas sísmicas (ACI 318-25 §18.7.2.1)
    COLUMN_MIN_THICKNESS_MM = 300.0

    def __init__(
        self,
        flexocompression_service: Optional[FlexocompressionService] = None,
        shear_service: Optional[ShearService] = None,
        wall_pier_service: Optional[WallPierService] = None
    ):
        self._flexo_service = flexocompression_service or FlexocompressionService()
        self._shear_service = shear_service or ShearService()
        self._wall_pier_service = wall_pier_service or WallPierService()

    def _classify_pier(self, pier: Pier) -> tuple:
        """
        Clasifica el pier según Tabla R18.10.1 y verifica espesor mínimo.

        Returns:
            (classification, is_column, needs_300mm)
        """
        classification = self._wall_pier_service.classify_wall_pier(
            hw=pier.height,
            lw=pier.width,
            bw=pier.thickness
        )
        is_column = classification.requires_column_details
        needs_300mm = is_column and not classification.column_min_thickness_ok
        return classification, is_column, needs_300mm

    def _get_min_thickness_for_pier(self, pier: Pier) -> float:
        """
        Obtiene el espesor mínimo para un pier según su clasificación.

        Para columnas sísmicas (ACI 318-25 §18.7.2.1): 300mm
        Para muros: sin restricción especial (usa espesor actual)

        Returns:
            Espesor mínimo en mm
        """
        _, is_column, _ = self._classify_pier(pier)
        if is_column:
            return self.COLUMN_MIN_THICKNESS_MM
        return pier.thickness

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
        # Verificar primero si es columna sísmica que no cumple espesor mínimo
        classification, is_column, needs_300mm = self._classify_pier(pier)

        if needs_300mm:
            # Prioridad máxima: columna sísmica < 300mm
            original_config = self._pier_to_config(pier)
            return self._propose_for_column_min_thickness(
                pier, pier_forces, original_config, flexure_sf, shear_dcr
            )

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
        elif failure_mode == FailureMode.OVERDESIGNED:
            return self._propose_for_reduction(
                pier, pier_forces, original_config, flexure_sf, shear_dcr
            )

        return None

    def _determine_failure_mode(
        self,
        flexure_sf: float,
        shear_dcr: float,
        boundary_required: bool,
        slenderness_reduction: float,
        check_overdesign: bool = True
    ) -> FailureMode:
        """Determina el modo de falla principal (o sobrediseño)."""
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

        # Detectar sobrediseño: SF alto Y DCR bajo
        if check_overdesign:
            is_overdesigned = (
                flexure_sf >= self.OVERDESIGNED_SF_MIN and
                shear_dcr <= self.OVERDESIGNED_DCR_MAX
            )
            if is_overdesigned:
                return FailureMode.OVERDESIGNED

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
            n_stirrup_legs=pier.n_stirrup_legs,
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
            stirrup_spacing=config.stirrup_spacing,
            n_stirrup_legs=config.n_stirrup_legs
        )
        if config.thickness and config.thickness != pier.thickness:
            new_pier.thickness = config.thickness
        return new_pier

    def _verify_flexure(self, pier: Pier, pier_forces: Optional[PierForces]) -> float:
        """Verifica flexión y retorna SF."""
        result = self._flexo_service.check_flexure(
            pier, pier_forces, moment_axis='M3', direction='primary', k=0.8
        )
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

        Estrategia: búsqueda exhaustiva por espesor creciente.
        Para cada espesor, prueba combinaciones de refuerzo hasta encontrar SF >= 1.0.
        Se detiene en la primera solución viable (la más económica).
        """
        best_config = deepcopy(original_config)
        best_sf = original_sf
        best_dcr = original_dcr

        # Obtener espesor mínimo según clasificación del pier
        min_thickness = self._get_min_thickness_for_pier(pier)
        effective_min = max(pier.thickness, min_thickness)

        # Iterar espesores desde el mínimo efectivo
        for thickness in THICKNESS_SEQUENCE:
            if thickness < effective_min:
                continue

            # Calcular máximo de ramas para este espesor
            max_legs = min(int(thickness // 100), STIRRUP_LEGS_SEQUENCE[-1])

            # Probar combinaciones de refuerzo para este espesor
            result = self._find_solution_for_thickness(
                pier, pier_forces, original_config, thickness, max_legs,
                original_sf, original_dcr
            )

            if result is not None:
                return result

            # Actualizar mejor configuración si mejoró
            test_config = self._get_max_config_for_thickness(original_config, thickness, max_legs)
            test_pier = self._apply_config_to_pier(pier, test_config)
            test_pier.thickness = thickness
            test_sf = self._verify_flexure(test_pier, pier_forces)
            test_dcr = self._verify_shear(test_pier, pier_forces)

            if test_sf > best_sf:
                best_config = test_config
                best_sf = test_sf
                best_dcr = test_dcr

        # No se encontró solución, retornar mejor esfuerzo con success=False
        changes = self._build_changes(original_config, best_config)
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

    def _find_solution_for_thickness(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        original_config: ReinforcementConfig,
        thickness: float,
        max_legs: int,
        original_sf: float,
        original_dcr: float
    ) -> Optional[DesignProposal]:
        """
        Busca la solución mínima para un espesor dado.
        Itera borde → malla → ramas hasta encontrar SF >= 1.0.
        Verifica que la cuantía no exceda ρmax para asegurar ductilidad.
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

                        test_pier = self._apply_config_to_pier(pier, proposed_config)
                        test_pier.thickness = thickness

                        # Verificar cuantía máxima para asegurar ductilidad
                        # Si ρ > ρmax, saltar esta configuración (falla frágil)
                        if test_pier.rho_vertical > RHO_MAX:
                            continue

                        new_sf = self._verify_flexure(test_pier, pier_forces)
                        new_dcr = self._verify_shear(test_pier, pier_forces)

                        if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
                            changes = self._build_changes(original_config, proposed_config)
                            return self._create_proposal(
                                pier, FailureMode.COMBINED, ProposalType.COMBINED,
                                original_config, proposed_config, original_sf, new_sf,
                                original_dcr, new_dcr, 1, changes
                            )

        return None

    def _get_max_config_for_thickness(
        self,
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

    def _propose_combined_with_thickness(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float,
        best_config: Optional[ReinforcementConfig],
        best_sf: float,
        best_dcr: float
    ) -> Optional[DesignProposal]:
        """
        Propone solución combinada con aumento incremental.

        Orden de prioridad (antes de aumentar espesor):
        1. Aumentar ramas de estribos (2 → 3 → 4)
        2. Aumentar espesor de a 50mm
        """
        # Usar la mejor configuración de refuerzo encontrada o la original
        base_config = best_config or deepcopy(original_config)

        # =====================================================================
        # PASO 1: Intentar aumentar ramas de estribos antes de espesor
        # Regla: máximo 1 rama cada 100mm de espesor
        #   - e=200mm → máx 2 ramas
        #   - e=300mm → máx 3 ramas
        #   - e=400mm → máx 4 ramas
        # =====================================================================
        max_legs_for_thickness = int(pier.thickness // 100)
        max_legs_for_thickness = min(max_legs_for_thickness, STIRRUP_LEGS_SEQUENCE[-1])

        current_legs_idx = STIRRUP_LEGS_SEQUENCE.index(base_config.n_stirrup_legs) \
            if base_config.n_stirrup_legs in STIRRUP_LEGS_SEQUENCE else 0

        for legs_offset in range(1, len(STIRRUP_LEGS_SEQUENCE) - current_legs_idx):
            new_legs = STIRRUP_LEGS_SEQUENCE[current_legs_idx + legs_offset]

            # Verificar si caben las ramas en el espesor actual
            if new_legs > max_legs_for_thickness:
                continue

            proposed_config = deepcopy(base_config)
            proposed_config.n_stirrup_legs = new_legs

            test_pier = self._apply_config_to_pier(pier, proposed_config)
            new_sf = self._verify_flexure(test_pier, pier_forces)
            new_dcr = self._verify_shear(test_pier, pier_forces)

            if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
                changes = self._build_changes(original_config, proposed_config)
                if new_legs != original_config.n_stirrup_legs:
                    changes.append(f"{new_legs}R estribos")
                return self._create_proposal(
                    pier, FailureMode.COMBINED, ProposalType.COMBINED,
                    original_config, proposed_config, original_sf, new_sf,
                    original_dcr, new_dcr, legs_offset, changes
                )

        # =====================================================================
        # PASO 2: Iterar espesor + ramas proporcionales
        # Regla: 1 rama cada 100mm de espesor
        # Para columnas sísmicas: mínimo 300mm (§18.7.2.1)
        # =====================================================================
        min_thickness = self._get_min_thickness_for_pier(pier)
        effective_min = max(pier.thickness, min_thickness)

        thickness_start_idx = 0
        for i, t in enumerate(THICKNESS_SEQUENCE):
            if t >= effective_min:
                thickness_start_idx = i
                break

        for thickness_offset in range(len(THICKNESS_SEQUENCE) - thickness_start_idx):
            new_thickness = THICKNESS_SEQUENCE[thickness_start_idx + thickness_offset]

            # Calcular máximo de ramas para este espesor
            max_legs = min(int(new_thickness // 100), STIRRUP_LEGS_SEQUENCE[-1])

            proposed_config = deepcopy(base_config)
            proposed_config.thickness = new_thickness
            proposed_config.n_stirrup_legs = max_legs

            test_pier = self._apply_config_to_pier(pier, proposed_config)
            test_pier.thickness = new_thickness

            new_sf = self._verify_flexure(test_pier, pier_forces)
            new_dcr = self._verify_shear(test_pier, pier_forces)

            if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
                changes = self._build_changes(original_config, proposed_config)
                if max_legs != original_config.n_stirrup_legs:
                    changes.append(f"{max_legs}R")
                return self._create_proposal(
                    pier, FailureMode.COMBINED, ProposalType.COMBINED,
                    original_config, proposed_config, original_sf, new_sf,
                    original_dcr, new_dcr, thickness_offset + 1, changes
                )

        # Si aún no resuelve, retornar propuesta con mejor configuración encontrada
        return self._create_best_effort_proposal(
            pier, pier_forces, FailureMode.COMBINED, original_config, original_sf, original_dcr
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

    def _propose_for_column_min_thickness(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float
    ) -> DesignProposal:
        """
        Propone solución para columna sísmica con espesor < 300mm.

        Según ACI 318-25 §18.7.2.1:
        "The shortest cross-sectional dimension, measured on a straight
        line passing through the centroid, shall be at least 300 mm"

        Estrategia:
        1. Proponer espesor mínimo de 300mm
        2. Si con 300mm no pasa verificación, incrementar espesor hasta pasar

        Returns:
            DesignProposal con espesor >= 300mm
        """
        proposed_config = deepcopy(original_config)
        changes = [f"⚠️ Columna sísmica: e ≥ 300mm (§18.7.2.1)"]

        # Filtrar secuencia de espesores para comenzar en 300mm
        valid_thicknesses = [t for t in THICKNESS_SEQUENCE if t >= self.COLUMN_MIN_THICKNESS_MM]

        if not valid_thicknesses:
            # Si no hay espesores >= 300mm en la secuencia, usar 300mm directamente
            valid_thicknesses = [self.COLUMN_MIN_THICKNESS_MM]

        best_sf = original_sf
        best_dcr = original_dcr
        iteration = 0

        for thickness in valid_thicknesses:
            proposed_config.thickness = thickness
            iteration += 1

            # Crear pier de prueba con nuevo espesor
            test_pier = self._apply_config_to_pier(pier, proposed_config)
            test_pier.thickness = thickness

            new_sf = self._verify_flexure(test_pier, pier_forces)
            new_dcr = self._verify_shear(test_pier, pier_forces)

            # Verificar si pasa
            if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
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
        proposed_config.thickness = self.COLUMN_MIN_THICKNESS_MM
        changes.append(f"Espesor: {int(self.COLUMN_MIN_THICKNESS_MM)}mm")
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

    def _propose_for_reduction(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float
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
        min_thickness = self._get_min_thickness_for_pier(pier)

        if original_sf > 2.0:
            # Iterar espesores menores
            for thickness in reversed(THICKNESS_SEQUENCE):
                if thickness >= pier.thickness:
                    continue  # Solo espesores menores
                if thickness < min_thickness:
                    continue  # Respetar mínimo para columnas sísmicas

                proposed_config = deepcopy(original_config)
                proposed_config.thickness = thickness

                test_pier = self._apply_config_to_pier(pier, proposed_config)
                test_pier.thickness = thickness
                iterations += 1

                # Verificar cuantía mínima
                if test_pier.rho_vertical < RHO_MIN:
                    continue

                new_sf = self._verify_flexure(test_pier, pier_forces)
                new_dcr = self._verify_shear(test_pier, pier_forces)

                # Verificar viabilidad
                if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
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
            changes = self._build_reduction_changes(original_config, best_config)
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

        current_as = proposed_config.As_edge
        current_boundary_idx = 0
        for i, (n, d) in enumerate(BOUNDARY_BAR_SEQUENCE):
            bar_area = get_bar_area(d, 78.5)
            seq_as = n * 2 * bar_area
            if seq_as >= current_as:
                current_boundary_idx = i
                break

        for boundary_idx in range(current_boundary_idx - 1, -1, -1):
            n_bars, diameter = BOUNDARY_BAR_SEQUENCE[boundary_idx]
            proposed_config.n_edge_bars = n_bars
            proposed_config.diameter_edge = diameter

            test_pier = self._apply_config_to_pier(pier, proposed_config)
            if proposed_config.thickness:
                test_pier.thickness = proposed_config.thickness
            iterations += 1

            if test_pier.rho_vertical < RHO_MIN:
                break

            new_sf = self._verify_flexure(test_pier, pier_forces)
            new_dcr = self._verify_shear(test_pier, pier_forces)

            if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
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

            test_pier = self._apply_config_to_pier(pier, proposed_config)
            if proposed_config.thickness:
                test_pier.thickness = proposed_config.thickness
            iterations += 1

            if test_pier.rho_vertical < RHO_MIN:
                proposed_config.spacing_v = best_config.spacing_v
                proposed_config.spacing_h = best_config.spacing_h
                break

            new_sf = self._verify_flexure(test_pier, pier_forces)
            new_dcr = self._verify_shear(test_pier, pier_forces)

            if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
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

            test_pier = self._apply_config_to_pier(pier, proposed_config)
            if proposed_config.thickness:
                test_pier.thickness = proposed_config.thickness
            iterations += 1

            if test_pier.rho_vertical < RHO_MIN:
                proposed_config.diameter_v = best_config.diameter_v
                proposed_config.diameter_h = best_config.diameter_h
                break

            new_sf = self._verify_flexure(test_pier, pier_forces)
            new_dcr = self._verify_shear(test_pier, pier_forces)

            if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
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
            changes = self._build_reduction_changes(original_config, best_config)
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

    def _build_reduction_changes(
        self,
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

        Para columnas sísmicas (ACI 318-25 §18.7.2.1), respeta el mínimo de 300mm.
        """
        changes = []
        proposed_config = deepcopy(original_config)

        # Obtener espesor mínimo según clasificación del pier
        min_thickness = self._get_min_thickness_for_pier(pier)

        # Encontrar posición actual en secuencia de espesores
        # Considerando tanto el espesor actual como el mínimo requerido
        effective_min = max(pier.thickness, min_thickness)
        start_idx = 0
        for i, t in enumerate(THICKNESS_SEQUENCE):
            if t >= effective_min:
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
        Crea la mejor propuesta posible iterando incrementalmente.

        Busca la configuración mínima que logra el mejor SF/DCR posible.
        Si ninguna configuración resuelve el problema, retorna success=False.
        """
        proposed_config = deepcopy(original_config)
        best_config = deepcopy(original_config)
        best_sf = original_sf
        best_dcr = original_dcr
        iterations = 0

        # Obtener espesor mínimo según clasificación del pier
        min_thickness = self._get_min_thickness_for_pier(pier)
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

                        test_pier = self._apply_config_to_pier(pier, proposed_config)
                        test_pier.thickness = thickness
                        new_sf = self._verify_flexure(test_pier, pier_forces)
                        new_dcr = self._verify_shear(test_pier, pier_forces)

                        # Guardar si es mejor
                        if new_sf > best_sf or (new_sf == best_sf and new_dcr < best_dcr):
                            best_config = deepcopy(proposed_config)
                            best_sf = new_sf
                            best_dcr = new_dcr

                        # Si resuelve, retornar con success=True
                        if new_sf >= self.TARGET_SF and new_dcr <= 1.0:
                            changes = self._build_changes(original_config, proposed_config)
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
        changes = self._build_changes(original_config, best_config)
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

    def _build_changes(
        self,
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
        flexure_result = self._flexo_service.check_flexure(
            pier, pier_forces, moment_axis='M3', direction='primary', k=0.8
        )
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

        # Generar propuesta si falla O si está sobrediseñado
        proposal = None
        needs_proposal = (
            not verification['overall_ok'] or  # Falla verificación
            (flexure_sf >= self.OVERDESIGNED_SF_MIN and shear_dcr <= self.OVERDESIGNED_DCR_MAX)  # Sobrediseñado
        )

        if needs_proposal:
            proposal = self.generate_proposal(
                pier=pier,
                pier_forces=pier_forces,
                flexure_sf=flexure_sf,
                shear_dcr=shear_dcr,
                slenderness_reduction=slenderness_reduction
            )

        return verification, proposal
