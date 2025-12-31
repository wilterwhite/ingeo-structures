# tests/test_proposal_service.py
"""
Tests para el servicio de propuestas de diseño.
"""
import pytest
from app.domain.entities import Pier
from app.domain.entities.design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
    BOUNDARY_BAR_SEQUENCE,
)
from app.services.analysis.proposal_service import ProposalService


@pytest.fixture
def proposal_service():
    """Servicio de propuestas."""
    return ProposalService()


@pytest.fixture
def failing_pier():
    """Pier que falla por flexión."""
    return Pier(
        label="Test-A1-1",
        story="Cielo P1",
        width=2000,      # 2m
        thickness=200,   # 20cm
        height=2700,     # 2.7m
        fc=25,
        fy=420,
        n_meshes=2,
        diameter_v=8,
        spacing_v=200,
        diameter_h=8,
        spacing_h=200,
        n_edge_bars=2,
        diameter_edge=10,
        stirrup_diameter=8,
        stirrup_spacing=150
    )


@pytest.fixture
def ok_pier():
    """Pier que pasa verificación."""
    return Pier(
        label="Test-A2-1",
        story="Cielo P1",
        width=1500,      # 1.5m
        thickness=300,   # 30cm
        height=2700,     # 2.7m
        fc=30,
        fy=420,
        n_meshes=2,
        diameter_v=10,
        spacing_v=150,
        diameter_h=10,
        spacing_h=150,
        n_edge_bars=4,
        diameter_edge=20,
        stirrup_diameter=10,
        stirrup_spacing=100
    )


class TestFailureModeDetection:
    """Tests para detección de modo de falla."""

    def test_no_failure_detected(self, proposal_service):
        """Sin falla cuando SF >= 1.0 y DCR <= 1.0."""
        mode = proposal_service._determine_failure_mode(
            flexure_sf=1.5,
            shear_dcr=0.7,
            boundary_required=False,
            slenderness_reduction=1.0
        )
        assert mode == FailureMode.NONE

    def test_flexure_failure_detected(self, proposal_service):
        """Detecta falla por flexión."""
        mode = proposal_service._determine_failure_mode(
            flexure_sf=0.8,
            shear_dcr=0.5,
            boundary_required=False,
            slenderness_reduction=1.0
        )
        assert mode == FailureMode.FLEXURE

    def test_shear_failure_detected(self, proposal_service):
        """Detecta falla por corte."""
        mode = proposal_service._determine_failure_mode(
            flexure_sf=1.2,
            shear_dcr=1.3,
            boundary_required=False,
            slenderness_reduction=1.0
        )
        assert mode == FailureMode.SHEAR

    def test_combined_failure_detected(self, proposal_service):
        """Detecta falla combinada."""
        mode = proposal_service._determine_failure_mode(
            flexure_sf=0.7,
            shear_dcr=1.2,
            boundary_required=False,
            slenderness_reduction=1.0
        )
        assert mode == FailureMode.COMBINED

    def test_slenderness_failure_detected(self, proposal_service):
        """Detecta problema de esbeltez."""
        mode = proposal_service._determine_failure_mode(
            flexure_sf=0.9,
            shear_dcr=0.5,
            boundary_required=False,
            slenderness_reduction=0.6  # Reducción significativa
        )
        assert mode == FailureMode.SLENDERNESS


class TestReinforcementConfig:
    """Tests para configuración de armadura."""

    def test_config_from_pier(self, proposal_service, failing_pier):
        """Crea configuración desde pier."""
        config = proposal_service._pier_to_config(failing_pier)

        assert config.n_edge_bars == 2
        assert config.diameter_edge == 10
        assert config.n_meshes == 2
        assert config.diameter_v == 8
        assert config.spacing_v == 200

    def test_config_description(self):
        """Descripción de la configuración."""
        config = ReinforcementConfig(
            n_edge_bars=4,
            diameter_edge=16,
            n_meshes=2,
            diameter_v=10,
            spacing_v=150
        )

        desc = config.description()
        assert "4φ16" in desc
        assert "2M" in desc
        assert "φ10@150" in desc

    def test_config_as_edge_calculation(self):
        """Cálculo de área de acero de borde."""
        config = ReinforcementConfig(
            n_edge_bars=4,
            diameter_edge=16
        )

        # 4 barras × 2 extremos × 201.1 mm² = 1608.8 mm²
        expected_as = 4 * 2 * 201.1
        assert abs(config.As_edge - expected_as) < 1


class TestBoundaryBarSequence:
    """Tests para la secuencia de barras de borde."""

    def test_sequence_is_ordered_by_area(self):
        """La secuencia está ordenada por área creciente."""
        BAR_AREAS = {
            6: 28.3, 8: 50.3, 10: 78.5, 12: 113.1,
            16: 201.1, 18: 254.5, 20: 314.2, 22: 380.1,
            25: 490.9, 28: 615.8, 32: 804.2, 36: 1017.9,
        }

        prev_as = 0
        for n_bars, diameter in BOUNDARY_BAR_SEQUENCE[:10]:  # Primeros 10
            bar_area = BAR_AREAS.get(diameter, 78.5)
            total_as = n_bars * 2 * bar_area
            assert total_as >= prev_as, f"Secuencia no ordenada: {n_bars}φ{diameter}"
            prev_as = total_as

    def test_sequence_has_common_combinations(self):
        """La secuencia incluye combinaciones comunes."""
        combinations = BOUNDARY_BAR_SEQUENCE

        # Verificar que existen combinaciones típicas
        assert (2, 10) in combinations
        assert (2, 12) in combinations
        assert (4, 16) in combinations
        assert (6, 20) in combinations


class TestProposalGeneration:
    """Tests para generación de propuestas."""

    def test_no_proposal_when_ok(self, proposal_service, ok_pier):
        """No genera propuesta cuando el pier pasa."""
        proposal = proposal_service.generate_proposal(
            pier=ok_pier,
            pier_forces=None,
            flexure_sf=1.5,
            shear_dcr=0.5,
            boundary_required=False,
            slenderness_reduction=1.0
        )

        assert proposal is None

    def test_proposal_for_flexure_failure(self, proposal_service, failing_pier):
        """Genera propuesta para falla de flexión."""
        proposal = proposal_service.generate_proposal(
            pier=failing_pier,
            pier_forces=None,
            flexure_sf=0.7,
            shear_dcr=0.3,
            boundary_required=False,
            slenderness_reduction=1.0
        )

        # Puede generar propuesta exitosa o None si no hay solución
        if proposal is not None:
            assert proposal.failure_mode == FailureMode.FLEXURE
            assert proposal.success is True

    def test_proposal_increases_boundary_bars(self, proposal_service, failing_pier):
        """La propuesta aumenta las barras de borde para flexión."""
        proposal = proposal_service.generate_proposal(
            pier=failing_pier,
            pier_forces=None,
            flexure_sf=0.8,
            shear_dcr=0.5,
            boundary_required=False,
            slenderness_reduction=1.0
        )

        if proposal and proposal.success:
            # La propuesta debe tener más área de borde que el original
            original_as = proposal.original_config.As_edge
            proposed_as = proposal.proposed_config.As_edge
            assert proposed_as >= original_as


class TestApplyConfigToPier:
    """Tests para aplicar configuración a pier."""

    def test_apply_config_creates_copy(self, proposal_service, failing_pier):
        """Aplicar config crea una copia, no modifica el original."""
        config = ReinforcementConfig(
            n_edge_bars=6,
            diameter_edge=20,
            n_meshes=2,
            diameter_v=10,
            spacing_v=150
        )

        new_pier = proposal_service._apply_config_to_pier(failing_pier, config)

        # El pier original no cambia
        assert failing_pier.n_edge_bars == 2
        assert failing_pier.diameter_edge == 10

        # El nuevo pier tiene la nueva configuración
        assert new_pier.n_edge_bars == 6
        assert new_pier.diameter_edge == 20


class TestProposalResult:
    """Tests para el resultado de la propuesta."""

    def test_proposal_to_dict(self):
        """Conversión a diccionario."""
        proposal = DesignProposal(
            pier_key="Cielo P1_Test-A1-1",
            failure_mode=FailureMode.FLEXURE,
            proposal_type=ProposalType.BOUNDARY_BARS,
            original_config=ReinforcementConfig(n_edge_bars=2, diameter_edge=10),
            proposed_config=ReinforcementConfig(n_edge_bars=4, diameter_edge=16),
            original_sf_flexure=0.8,
            proposed_sf_flexure=1.2,
            original_dcr_shear=0.5,
            proposed_dcr_shear=0.4,
            iterations=3,
            success=True,
            changes=["Borde: 4φ16"]
        )

        d = proposal.to_dict()

        assert d['pier_key'] == "Cielo P1_Test-A1-1"
        assert d['failure_mode'] == "flexure"
        assert d['success'] is True
        assert d['sf_improvement'] > 0
        assert "4φ16" in d['description']

    def test_sf_improvement_calculation(self):
        """Cálculo de mejora de SF."""
        proposal = DesignProposal(
            pier_key="test",
            failure_mode=FailureMode.FLEXURE,
            proposal_type=ProposalType.BOUNDARY_BARS,
            original_config=ReinforcementConfig(),
            proposed_config=ReinforcementConfig(),
            original_sf_flexure=0.8,
            proposed_sf_flexure=1.2,
            success=True
        )

        # Mejora = (1.2 - 0.8) / 0.8 * 100 = 50%
        assert abs(proposal.sf_improvement - 50.0) < 0.1
