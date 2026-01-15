# app/services/analysis/proposal_service.py
"""
Servicio de propuestas de diseño para piers.

Orquesta la generación de propuestas delegando la lógica de búsqueda
a domain/proposals/. Este servicio usa ElementOrchestrator para
verificaciones, garantizando consistencia con el resto del sistema.
"""
from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING

from ...domain.entities import VerticalElement, ElementForces
from ...domain.entities.design_proposal import DesignProposal
from ...domain.chapter18.wall_piers import WallPierService
from ...domain.proposals import DesignGenerator
from ...domain.proposals.failure_analysis import OVERDESIGNED_SF_MIN, OVERDESIGNED_DCR_MAX

if TYPE_CHECKING:
    from .element_orchestrator import ElementOrchestrator


class ProposalService:
    """
    Servicio para generar propuestas de diseño inteligentes.

    Orquesta:
    - ElementOrchestrator: Verificación unificada de elementos
    - DesignGenerator: Lógica de búsqueda iterativa (en domain/)

    Este servicio es un thin wrapper que:
    1. Coordina las verificaciones a través del orquestador
    2. Delega la generación de propuestas a domain/proposals/
    """

    def __init__(
        self,
        orchestrator: Optional['ElementOrchestrator'] = None,
        wall_pier_service: Optional[WallPierService] = None
    ):
        # Import lazy para evitar circular
        if orchestrator is None:
            from .element_orchestrator import ElementOrchestrator
            orchestrator = ElementOrchestrator()

        self._orchestrator = orchestrator
        self._wall_pier_service = wall_pier_service or WallPierService()

        # Crear generador con funciones de verificación inyectadas
        self._generator = DesignGenerator(
            verify_flexure=self._verify_flexure,
            verify_shear=self._verify_shear,
            wall_pier_service=self._wall_pier_service
        )

    def _verify_flexure(self, pier: VerticalElement, pier_forces: Optional[ElementForces]) -> float:
        """
        Verifica flexión y retorna SF.

        Usa el orquestador para verificación consistente.
        """
        result = self._orchestrator.verify(pier, pier_forces)
        # El orquestador devuelve dcr_max, convertir a SF
        if result.dcr_max > 0:
            sf = 1 / result.dcr_max
        else:
            sf = 100
        return min(sf, 100)  # Cap at 100

    def _verify_shear(self, pier: VerticalElement, pier_forces: Optional[ElementForces]) -> float:
        """
        Verifica corte y retorna DCR.

        Usa verificación por combinación para obtener DCR combinado.
        """
        if pier_forces is None or not pier_forces.combinations:
            return 0

        # Verificar todas las combinaciones y obtener el peor DCR
        results = self._orchestrator.verify_all_combinations(pier, pier_forces)
        if not results:
            return 0

        # El peor DCR combinado
        max_dcr = max(r.shear_dcr_combined for r in results)
        return max_dcr

    def generate_proposal(
        self,
        pier: VerticalElement,
        pier_forces: Optional[ElementForces],
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
        pier: VerticalElement,
        pier_forces: Optional[ElementForces]
    ) -> Tuple[Dict[str, Any], Optional[DesignProposal]]:
        """
        Analiza un pier y genera propuesta si falla.

        Usa ElementOrchestrator para verificaciones, garantizando
        consistencia con el resto del sistema.

        Args:
            pier: Pier a analizar
            pier_forces: Fuerzas del pier

        Returns:
            Tuple (verification_results, proposal)
        """
        # Usar orquestador para verificación completa
        result = self._orchestrator.verify(pier, pier_forces)

        # Convertir DCR a SF para flexión
        if result.dcr_max > 0:
            flexure_sf = 1 / result.dcr_max
        else:
            flexure_sf = 100

        # Obtener DCR de corte combinado
        shear_dcr = self._verify_shear(pier, pier_forces)

        # Determinar slenderness_reduction del domain_result si disponible
        slenderness_reduction = 1.0
        if hasattr(result.domain_result, 'slenderness_reduction'):
            slenderness_reduction = result.domain_result.slenderness_reduction

        verification = {
            'flexure_sf': flexure_sf,
            'flexure_status': 'OK' if flexure_sf >= 1.0 else 'NO OK',
            'shear_dcr': shear_dcr,
            'shear_status': 'OK' if shear_dcr <= 1.0 else 'NO OK',
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
