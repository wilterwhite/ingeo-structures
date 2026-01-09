# app/domain/proposals/design_generator.py
"""
Generador de propuestas de diseño.

Clase principal que orquesta las estrategias de propuesta
según el modo de falla detectado.
"""
from typing import Optional, Callable, TYPE_CHECKING
from copy import deepcopy
from functools import partial

from ..entities.design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
)
from ..constants.units import MIN_COLUMN_DIMENSION_MM
from .failure_analysis import determine_failure_mode, OVERDESIGNED_SF_MIN, OVERDESIGNED_DCR_MAX
from .strategies.flexure import propose_for_flexure
from .strategies.shear import propose_for_shear
from .strategies.combined import propose_combined
from .strategies.reduction import propose_for_reduction
from .strategies.thickness import (
    propose_with_thickness,
    propose_for_slenderness,
    create_best_effort_proposal,
)
from .strategies.column_min import propose_for_column_min_thickness

if TYPE_CHECKING:
    from ..entities import Pier, PierForces
    from ..chapter18.wall_piers import WallPierService


class DesignGenerator:
    """
    Generador de propuestas de diseño para piers.

    Analiza el modo de falla y delega a estrategias específicas
    para encontrar la solución mínima.

    Requiere inyección de dependencias para verificación:
    - verify_flexure: función que verifica flexión y retorna SF
    - verify_shear: función que verifica corte y retorna DCR
    - wall_pier_service: servicio para clasificación de piers

    Esto permite que la lógica de búsqueda sea independiente
    de los servicios de verificación (inversión de dependencias).
    """

    def __init__(
        self,
        verify_flexure: Callable,
        verify_shear: Callable,
        wall_pier_service: 'WallPierService'
    ):
        """
        Inicializa el generador con funciones de verificación.

        Args:
            verify_flexure: Función (pier, forces) -> SF
            verify_shear: Función (pier, forces) -> DCR
            wall_pier_service: Servicio para clasificación de piers
        """
        self._verify_flexure = verify_flexure
        self._verify_shear = verify_shear
        self._wall_pier_service = wall_pier_service

    # =========================================================================
    # CLASIFICACIÓN Y UTILIDADES
    # =========================================================================

    def _classify_pier(self, pier: 'Pier') -> tuple:
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

    def _get_min_thickness_for_pier(self, pier: 'Pier') -> float:
        """
        Obtiene el espesor mínimo para un pier según su clasificación.

        Para columnas sísmicas (ACI 318-25 §18.7.2.1): 300mm
        Para muros: sin restricción especial (usa espesor actual)

        Returns:
            Espesor mínimo en mm
        """
        _, is_column, _ = self._classify_pier(pier)
        if is_column:
            return MIN_COLUMN_DIMENSION_MM
        return pier.thickness

    def _pier_to_config(self, pier: 'Pier') -> ReinforcementConfig:
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

    def _apply_config_to_pier(self, pier: 'Pier', config: ReinforcementConfig) -> 'Pier':
        """Aplica una configuración a un pier (crea copia modificada)."""
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

    # =========================================================================
    # GENERACIÓN DE PROPUESTAS
    # =========================================================================

    def generate_proposal(
        self,
        pier: 'Pier',
        pier_forces: Optional['PierForces'],
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
            return propose_for_column_min_thickness(
                pier, pier_forces, original_config, flexure_sf, shear_dcr,
                self._verify_flexure, self._verify_shear, self._apply_config_to_pier
            )

        # Determinar modo de falla
        failure_mode = determine_failure_mode(
            flexure_sf, shear_dcr, boundary_required, slenderness_reduction
        )

        if failure_mode == FailureMode.NONE:
            return None

        # Crear configuración original
        original_config = self._pier_to_config(pier)

        # Generar propuesta según modo de falla
        return self._dispatch_to_strategy(
            failure_mode, pier, pier_forces, original_config,
            flexure_sf, shear_dcr, slenderness_reduction
        )

    def _dispatch_to_strategy(
        self,
        failure_mode: FailureMode,
        pier: 'Pier',
        pier_forces: Optional['PierForces'],
        original_config: ReinforcementConfig,
        flexure_sf: float,
        shear_dcr: float,
        slenderness_reduction: float
    ) -> Optional[DesignProposal]:
        """Despacha al estrategia correcta según modo de falla."""

        # Crear función parcial para propose_with_thickness
        thickness_fallback = partial(
            self._propose_with_thickness_wrapper
        )

        if failure_mode == FailureMode.FLEXURE:
            return propose_for_flexure(
                pier, pier_forces, original_config, flexure_sf, shear_dcr,
                self._verify_flexure, self._verify_shear, self._apply_config_to_pier,
                thickness_fallback
            )

        elif failure_mode == FailureMode.SHEAR:
            return propose_for_shear(
                pier, pier_forces, original_config, flexure_sf, shear_dcr,
                self._verify_flexure, self._verify_shear, self._apply_config_to_pier,
                thickness_fallback
            )

        elif failure_mode == FailureMode.COMBINED:
            return propose_combined(
                pier, pier_forces, original_config, flexure_sf, shear_dcr,
                self._verify_flexure, self._verify_shear, self._apply_config_to_pier,
                self._get_min_thickness_for_pier
            )

        elif failure_mode == FailureMode.SLENDERNESS:
            return propose_for_slenderness(
                pier, pier_forces, original_config, flexure_sf, slenderness_reduction,
                self._verify_flexure, self._verify_shear, self._apply_config_to_pier,
                self._get_min_thickness_for_pier, self._create_best_effort_wrapper
            )

        elif failure_mode == FailureMode.OVERDESIGNED:
            return propose_for_reduction(
                pier, pier_forces, original_config, flexure_sf, shear_dcr,
                self._verify_flexure, self._verify_shear, self._apply_config_to_pier,
                self._get_min_thickness_for_pier
            )

        return None

    def _propose_with_thickness_wrapper(
        self,
        pier: 'Pier',
        pier_forces: Optional['PierForces'],
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float,
        failure_mode: FailureMode
    ) -> Optional[DesignProposal]:
        """Wrapper para propose_with_thickness con dependencias inyectadas."""
        return propose_with_thickness(
            pier, pier_forces, original_config, original_sf, original_dcr, failure_mode,
            self._verify_flexure, self._verify_shear, self._apply_config_to_pier,
            self._get_min_thickness_for_pier, self._create_best_effort_wrapper
        )

    def _create_best_effort_wrapper(
        self,
        pier: 'Pier',
        pier_forces: Optional['PierForces'],
        failure_mode: FailureMode,
        original_config: ReinforcementConfig,
        original_sf: float,
        original_dcr: float
    ) -> DesignProposal:
        """Wrapper para create_best_effort_proposal con dependencias inyectadas."""
        return create_best_effort_proposal(
            pier, pier_forces, failure_mode, original_config, original_sf, original_dcr,
            self._verify_flexure, self._verify_shear, self._apply_config_to_pier,
            self._get_min_thickness_for_pier
        )

    # =========================================================================
    # API DE ALTO NIVEL
    # =========================================================================

    def needs_proposal(self, flexure_sf: float, shear_dcr: float) -> bool:
        """
        Determina si un pier necesita propuesta (falla o sobrediseñado).

        Args:
            flexure_sf: Factor de seguridad de flexión
            shear_dcr: DCR de corte

        Returns:
            True si necesita propuesta
        """
        fails_verification = flexure_sf < 1.0 or shear_dcr > 1.0
        is_overdesigned = (
            flexure_sf >= OVERDESIGNED_SF_MIN and
            shear_dcr <= OVERDESIGNED_DCR_MAX
        )
        return fails_verification or is_overdesigned
