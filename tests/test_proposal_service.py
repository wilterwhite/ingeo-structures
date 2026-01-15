# tests/test_proposal_service.py
"""
Tests para el servicio de propuestas de diseño.
"""
import pytest
from app.domain.entities import VerticalElement, VerticalElementSource, MeshReinforcement
from app.domain.entities.design_proposal import (
    DesignProposal,
    ReinforcementConfig,
    FailureMode,
    ProposalType,
    BOUNDARY_BAR_SEQUENCE,
)
from app.services.analysis.proposal_service import ProposalService
from app.domain.proposals.failure_analysis import determine_failure_mode


@pytest.fixture
def proposal_service():
    """Servicio de propuestas."""
    return ProposalService()


@pytest.fixture
def failing_pier():
    """Pier que falla por flexión."""
    return VerticalElement(
        label="Test-A1-1",
        story="Cielo P1",
        source=VerticalElementSource.PIER,
        length=2000,     # lw: 2m
        thickness=200,   # tw: 20cm
        height=2700,     # 2.7m
        fc=25,
        fy=420,
        mesh_reinforcement=MeshReinforcement(
            n_meshes=2,
            diameter_v=8,
            spacing_v=200,
            diameter_h=8,
            spacing_h=200,
            n_edge_bars=2,
            diameter_edge=10,
        ),
        stirrup_diameter=8,
        stirrup_spacing=150,
        n_shear_legs=2,
    )


@pytest.fixture
def ok_pier():
    """Pier que pasa verificación."""
    return VerticalElement(
        label="Test-A2-1",
        story="Cielo P1",
        source=VerticalElementSource.PIER,
        length=1500,     # lw: 1.5m
        thickness=300,   # tw: 30cm
        height=2700,     # 2.7m
        fc=30,
        fy=420,
        mesh_reinforcement=MeshReinforcement(
            n_meshes=2,
            diameter_v=10,
            spacing_v=150,
            diameter_h=10,
            spacing_h=150,
            n_edge_bars=4,
            diameter_edge=20,
        ),
        stirrup_diameter=10,
        stirrup_spacing=100,
        n_shear_legs=2,
    )


class TestFailureModeDetection:
    """Tests para detección de modo de falla."""

    def test_no_failure_detected(self):
        """Sin falla cuando SF >= 1.0 y DCR <= 1.0 (sin sobrediseño)."""
        mode = determine_failure_mode(
            flexure_sf=1.3,   # Menor que umbral de sobrediseño (1.5)
            shear_dcr=0.8,    # Mayor que umbral de sobrediseño (0.7)
            boundary_required=False,
            slenderness_reduction=1.0
        )
        assert mode == FailureMode.NONE

    def test_overdesigned_detected(self):
        """Detecta sobrediseño cuando SF >> 1.0 y DCR muy bajo."""
        mode = determine_failure_mode(
            flexure_sf=2.0,   # Mayor que umbral (1.5)
            shear_dcr=0.5,    # Menor que umbral (0.7)
            boundary_required=False,
            slenderness_reduction=1.0
        )
        assert mode == FailureMode.OVERDESIGNED

    def test_flexure_failure_detected(self):
        """Detecta falla por flexión."""
        mode = determine_failure_mode(
            flexure_sf=0.8,
            shear_dcr=0.5,
            boundary_required=False,
            slenderness_reduction=1.0
        )
        assert mode == FailureMode.FLEXURE

    def test_shear_failure_detected(self):
        """Detecta falla por corte."""
        mode = determine_failure_mode(
            flexure_sf=1.2,
            shear_dcr=1.3,
            boundary_required=False,
            slenderness_reduction=1.0
        )
        assert mode == FailureMode.SHEAR

    def test_combined_failure_detected(self):
        """Detecta falla combinada."""
        mode = determine_failure_mode(
            flexure_sf=0.7,
            shear_dcr=1.2,
            boundary_required=False,
            slenderness_reduction=1.0
        )
        assert mode == FailureMode.COMBINED

    def test_slenderness_failure_detected(self):
        """Detecta problema de esbeltez."""
        mode = determine_failure_mode(
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
        config = proposal_service._generator._pier_to_config(failing_pier)

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

        new_pier = proposal_service._generator._apply_config_to_pier(failing_pier, config)

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


class TestColumnMinimumThickness:
    """Tests para espesor mínimo de columnas sísmicas (ACI 318-25 §18.7.2.1)."""

    @pytest.fixture
    def column_classified_pier(self):
        """
        Pier clasificado como columna (hw/lw >= 2.0 y lw/bw <= 2.5).
        Con espesor < 300mm, debería requerir aumento.
        """
        return VerticalElement(
            label="Col-A1-1",
            story="Cielo P1",
            source=VerticalElementSource.PIER,
            length=600,      # 600mm -> lw
            thickness=200,   # 200mm -> bw (< 300mm mínimo para columna)
            height=2700,     # 2700mm -> hw (hw/lw = 4.5 >= 2.0)
            fc=25,           # lw/bw = 600/200 = 3.0 > 2.5 -> ALTERNATIVE
            fy=420,
            mesh_reinforcement=MeshReinforcement(
                n_meshes=2,
                diameter_v=8,
                spacing_v=200,
                diameter_h=8,
                spacing_h=200,
                n_edge_bars=2,
                diameter_edge=12,
            ),
            n_shear_legs=2,
        )

    @pytest.fixture
    def column_with_500mm_width(self):
        """
        Pier clasificado como columna con lw/bw <= 2.5 (columna especial).
        """
        return VerticalElement(
            label="Col-A2-1",
            story="Cielo P1",
            source=VerticalElementSource.PIER,
            length=500,      # 500mm -> lw
            thickness=200,   # 200mm -> bw (< 300mm)
            height=2700,     # hw/lw = 5.4 >= 2.0
            fc=25,           # lw/bw = 500/200 = 2.5 <= 2.5 -> COLUMN
            fy=420,
            mesh_reinforcement=MeshReinforcement(
                n_meshes=2,
                diameter_v=8,
                spacing_v=200,
                diameter_h=8,
                spacing_h=200,
                n_edge_bars=2,
                diameter_edge=12,
            ),
            n_shear_legs=2,
        )

    @pytest.fixture
    def wall_classified_pier(self):
        """
        Pier clasificado como muro (hw/lw < 2.0).
        No requiere 300mm mínimo.
        """
        return VerticalElement(
            label="Wall-A1-1",
            story="Cielo P1",
            source=VerticalElementSource.PIER,
            length=2000,     # 2000mm -> lw
            thickness=200,   # 200mm -> bw
            height=2700,     # hw/lw = 1.35 < 2.0 -> WALL
            fc=25,
            fy=420,
            mesh_reinforcement=MeshReinforcement(
                n_meshes=2,
                diameter_v=8,
                spacing_v=200,
                diameter_h=8,
                spacing_h=200,
                n_edge_bars=2,
                diameter_edge=12,
            ),
            n_shear_legs=2,
        )

    def test_classify_pier_detects_column(self, proposal_service, column_with_500mm_width):
        """Detecta correctamente cuando un pier es columna sísmica."""
        classification, is_column, needs_300mm = proposal_service._generator._classify_pier(
            column_with_500mm_width
        )

        assert is_column is True
        assert needs_300mm is True  # thickness=200 < 300
        assert classification.column_min_thickness_required == 300.0

    def test_classify_pier_detects_wall(self, proposal_service, wall_classified_pier):
        """No requiere 300mm para piers clasificados como muro."""
        classification, is_column, needs_300mm = proposal_service._generator._classify_pier(
            wall_classified_pier
        )

        assert is_column is False
        assert needs_300mm is False

    def test_min_thickness_for_column(self, proposal_service, column_with_500mm_width):
        """Columnas sísmicas tienen espesor mínimo de 300mm."""
        min_t = proposal_service._generator._get_min_thickness_for_pier(column_with_500mm_width)
        assert min_t == 300.0

    def test_min_thickness_for_wall(self, proposal_service, wall_classified_pier):
        """Muros mantienen su espesor actual como mínimo."""
        min_t = proposal_service._generator._get_min_thickness_for_pier(wall_classified_pier)
        assert min_t == 200.0  # Espesor actual

    def test_column_proposal_has_min_300mm(self, proposal_service, column_with_500mm_width):
        """Propuesta para columna con espesor < 300mm propone >= 300mm."""
        proposal = proposal_service.generate_proposal(
            pier=column_with_500mm_width,
            pier_forces=None,
            flexure_sf=1.0,  # Pasaría normalmente
            shear_dcr=0.5,
            boundary_required=False,
            slenderness_reduction=1.0
        )

        # Siempre genera propuesta para columna < 300mm
        assert proposal is not None
        assert proposal.failure_mode == FailureMode.COLUMN_MIN_THICKNESS
        assert proposal.proposed_config.thickness >= 300.0

    def test_column_min_thickness_failure_mode(self):
        """El modo de falla COLUMN_MIN_THICKNESS existe."""
        assert hasattr(FailureMode, 'COLUMN_MIN_THICKNESS')
        assert FailureMode.COLUMN_MIN_THICKNESS.value == "column_min_thickness"

    def test_wall_no_column_min_thickness_proposal(self, proposal_service, wall_classified_pier):
        """Muro con espesor 200mm no genera propuesta de espesor mínimo."""
        proposal = proposal_service.generate_proposal(
            pier=wall_classified_pier,
            pier_forces=None,
            flexure_sf=1.3,  # OK, pero no sobrediseñado
            shear_dcr=0.8,   # OK, pero no muy bajo
            boundary_required=False,
            slenderness_reduction=1.0
        )

        # No debería generar propuesta (no falla, no está sobrediseñado)
        assert proposal is None
