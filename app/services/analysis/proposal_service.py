# app/services/analysis/proposal_service.py
"""
Servicio de propuestas de diseño para piers.

Orquesta la generación de propuestas delegando la lógica de búsqueda
a domain/proposals/. Este servicio solo coordina los servicios de
verificación y el generador de propuestas.
"""
from typing import Dict, Any, Optional, Tuple

from ...domain.entities import Pier, PierForces
from ...domain.entities.design_proposal import DesignProposal
from ...domain.chapter18.wall_piers import WallPierService
from ...domain.proposals import DesignGenerator
from ...domain.proposals.failure_analysis import OVERDESIGNED_SF_MIN, OVERDESIGNED_DCR_MAX
from .flexocompression_service import FlexocompressionService
from .shear_service import ShearService


class ProposalService:
    """
    Servicio para generar propuestas de diseño inteligentes.

    Orquesta:
    - FlexocompressionService: Verificación de flexión
    - ShearService: Verificación de corte
    - DesignGenerator: Lógica de búsqueda iterativa (en domain/)

    Este servicio es un thin wrapper que:
    1. Coordina las verificaciones
    2. Delega la generación de propuestas a domain/proposals/
    """

    def __init__(
        self,
        flexocompression_service: Optional[FlexocompressionService] = None,
        shear_service: Optional[ShearService] = None,
        wall_pier_service: Optional[WallPierService] = None
    ):
        self._flexo_service = flexocompression_service or FlexocompressionService()
        self._shear_service = shear_service or ShearService()
        self._wall_pier_service = wall_pier_service or WallPierService()

        # Crear generador con funciones de verificación inyectadas
        self._generator = DesignGenerator(
            verify_flexure=self._verify_flexure,
            verify_shear=self._verify_shear,
            wall_pier_service=self._wall_pier_service
        )

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

    # =========================================================================
    # MÉTODOS DELEGADOS AL GENERADOR (para compatibilidad con tests)
    # =========================================================================

    def _pier_to_config(self, pier: Pier):
        """Convierte pier a configuración de armadura."""
        return self._generator._pier_to_config(pier)

    def _apply_config_to_pier(self, pier: Pier, config):
        """Aplica configuración a pier (crea copia)."""
        return self._generator._apply_config_to_pier(pier, config)

    def _classify_pier(self, pier: Pier):
        """Clasifica pier según Tabla R18.10.1."""
        return self._generator._classify_pier(pier)

    def _get_min_thickness_for_pier(self, pier: Pier) -> float:
        """Obtiene espesor mínimo según clasificación."""
        return self._generator._get_min_thickness_for_pier(pier)

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
        return self._generator.generate_proposal(
            pier=pier,
            pier_forces=pier_forces,
            flexure_sf=flexure_sf,
            shear_dcr=shear_dcr,
            boundary_required=boundary_required,
            slenderness_reduction=slenderness_reduction
        )

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
        if self._generator.needs_proposal(flexure_sf, shear_dcr):
            proposal = self.generate_proposal(
                pier=pier,
                pier_forces=pier_forces,
                flexure_sf=flexure_sf,
                shear_dcr=shear_dcr,
                slenderness_reduction=slenderness_reduction
            )

        return verification, proposal
