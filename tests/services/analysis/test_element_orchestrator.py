# tests/services/analysis/test_element_orchestrator.py
"""
Tests para ElementOrchestrator - orquestador central de verificación.
"""
import pytest
from unittest.mock import Mock, MagicMock

from app.services.analysis.element_orchestrator import (
    ElementOrchestrator,
    OrchestrationResult,
)
from app.services.analysis.element_classifier import ElementType
from app.services.analysis.design_behavior import DesignBehavior
from app.domain.entities import Column, Beam, Pier, DropBeam
from app.domain.chapter18 import SeismicCategory


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_column():
    """Columna de prueba."""
    return Column(
        label="C1",
        story="Piso 1",
        depth=500,
        width=400,
        height=3000,
        fc=30,
        fy=420,
        diameter_long=20,
        n_bars_depth=3,
        n_bars_width=4,
        stirrup_diameter=10,
        stirrup_spacing=100,
        n_stirrup_legs_depth=2,
        n_stirrup_legs_width=3,
    )


@pytest.fixture
def sample_beam():
    """Viga de prueba."""
    return Beam(
        label="V1",
        story="Piso 1",
        width=300,
        depth=600,
        length=6000,
        fc=25,
        fy=420,
        diameter_top=16,
        n_bars_top=3,
        diameter_bottom=20,
        n_bars_bottom=4,
        stirrup_diameter=8,
        stirrup_spacing=150,
        n_stirrup_legs=2,
    )


@pytest.fixture
def sample_pier():
    """Pier/muro de prueba."""
    return Pier(
        label="M1",
        story="Piso 1",
        width=2000,
        thickness=200,
        height=2700,
        fc=25,
        fy=420,
        n_meshes=2,
        diameter_v=10,
        spacing_v=200,
        diameter_h=8,
        spacing_h=200,
        n_edge_bars=4,
        diameter_edge=16,
        stirrup_diameter=8,
        stirrup_spacing=150,
    )


@pytest.fixture
def sample_drop_beam():
    """Viga capitel de prueba."""
    return DropBeam(
        label="VC1",
        story="Piso 1",
        width=200,
        thickness=2400,
        length=1500,
        fc=25,
        fy=420,
        n_meshes=2,
        diameter_v=10,
        spacing_v=150,
        diameter_h=10,
        spacing_h=200,
        n_edge_bars=2,
        diameter_edge=16,
    )


@pytest.fixture
def mock_column_service():
    """Mock de SeismicColumnService."""
    service = Mock()
    result = Mock()
    result.is_ok = True
    result.dcr_max = 0.75
    result.critical_check = ''
    result.warnings = []
    service.verify_column.return_value = result
    return service


@pytest.fixture
def mock_beam_service():
    """Mock de SeismicBeamService."""
    service = Mock()
    result = Mock()
    result.is_ok = True
    result.dcr_max = 0.60
    result.critical_check = ''
    result.warnings = []
    service.verify_beam.return_value = result
    return service


@pytest.fixture
def mock_wall_service():
    """Mock de SeismicWallService."""
    service = Mock()
    result = Mock()
    result.is_ok = True
    result.dcr_max = 0.80
    result.critical_check = ''
    result.warnings = []
    service.verify_wall.return_value = result
    service.verify_drop_beam.return_value = result
    return service


@pytest.fixture
def mock_flexo_service():
    """Mock de FlexocompressionService."""
    service = Mock()
    service.check_flexure.return_value = {'SF': 2.0, 'status': 'OK'}
    return service


# =============================================================================
# Tests para OrchestrationResult
# =============================================================================

class TestOrchestrationResult:
    """Tests para el dataclass OrchestrationResult."""

    def test_creation(self):
        """Puede crear un OrchestrationResult."""
        result = OrchestrationResult(
            element_type=ElementType.COLUMN_SEISMIC,
            design_behavior=DesignBehavior.SEISMIC_COLUMN,
            service_used='column',
            domain_result={'test': 'data'},
            is_ok=True,
            dcr_max=0.75,
            critical_check='',
            warnings=[],
        )
        assert result.element_type == ElementType.COLUMN_SEISMIC
        assert result.service_used == 'column'
        assert result.is_ok is True
        assert result.dcr_max == 0.75

    def test_with_warnings(self):
        """Puede contener warnings."""
        result = OrchestrationResult(
            element_type=ElementType.WALL,
            design_behavior=DesignBehavior.SEISMIC_WALL,
            service_used='wall',
            domain_result=None,
            is_ok=False,
            dcr_max=1.25,
            critical_check='shear',
            warnings=['Refuerzo insuficiente', 'Verificar confinamiento'],
        )
        assert result.is_ok is False
        assert len(result.warnings) == 2
        assert result.critical_check == 'shear'


# =============================================================================
# Tests para ElementOrchestrator - Inicialización
# =============================================================================

class TestOrchestratorInit:
    """Tests para inicialización del orquestador."""

    def test_default_init(self):
        """Inicializa con servicios por defecto."""
        orchestrator = ElementOrchestrator()
        assert orchestrator._classifier is not None
        assert orchestrator._resolver is not None
        assert orchestrator._column_service is not None
        assert orchestrator._beam_service is not None
        assert orchestrator._wall_service is not None
        assert orchestrator._flexo_service is not None

    def test_custom_services(self, mock_column_service):
        """Acepta servicios personalizados (para testing)."""
        orchestrator = ElementOrchestrator(
            column_service=mock_column_service
        )
        assert orchestrator._column_service is mock_column_service


# =============================================================================
# Tests para ElementOrchestrator - Clasificación
# =============================================================================

class TestOrchestratorClassify:
    """Tests para método classify()."""

    def test_classify_column(self, sample_column):
        """Clasifica columna correctamente."""
        orchestrator = ElementOrchestrator()
        element_type = orchestrator.classify(sample_column)
        # Columna sísmica por defecto
        assert element_type == ElementType.COLUMN_SEISMIC

    def test_classify_beam(self, sample_beam):
        """Clasifica viga correctamente."""
        orchestrator = ElementOrchestrator()
        element_type = orchestrator.classify(sample_beam)
        assert element_type == ElementType.BEAM

    def test_classify_wall(self, sample_pier):
        """Clasifica muro correctamente."""
        orchestrator = ElementOrchestrator()
        element_type = orchestrator.classify(sample_pier)
        # Pier con lw/tw = 10 es WALL o WALL_SQUAT dependiendo de hw/lw
        assert element_type.is_wall

    def test_classify_drop_beam(self, sample_drop_beam):
        """Clasifica viga capitel correctamente."""
        orchestrator = ElementOrchestrator()
        element_type = orchestrator.classify(sample_drop_beam)
        assert element_type == ElementType.DROP_BEAM


# =============================================================================
# Tests para ElementOrchestrator - Resolución de comportamiento
# =============================================================================

class TestOrchestratorResolveBehavior:
    """Tests para método resolve_behavior()."""

    def test_column_gets_seismic_column(self, sample_column):
        """Columna sísmica obtiene comportamiento SEISMIC_COLUMN."""
        orchestrator = ElementOrchestrator()
        behavior = orchestrator.resolve_behavior(sample_column)
        assert behavior == DesignBehavior.SEISMIC_COLUMN
        assert behavior.service_type == 'column'

    def test_beam_gets_seismic_beam(self, sample_beam):
        """Viga sísmica obtiene comportamiento SEISMIC_BEAM."""
        orchestrator = ElementOrchestrator()
        behavior = orchestrator.resolve_behavior(sample_beam)
        assert behavior == DesignBehavior.SEISMIC_BEAM
        assert behavior.service_type == 'beam'

    def test_wall_gets_seismic_wall(self, sample_pier):
        """Muro sísmico obtiene comportamiento SEISMIC_WALL."""
        orchestrator = ElementOrchestrator()
        behavior = orchestrator.resolve_behavior(sample_pier)
        assert behavior == DesignBehavior.SEISMIC_WALL
        assert behavior.service_type == 'wall'

    def test_drop_beam_gets_drop_beam(self, sample_drop_beam):
        """Viga capitel obtiene comportamiento DROP_BEAM."""
        orchestrator = ElementOrchestrator()
        behavior = orchestrator.resolve_behavior(sample_drop_beam)
        assert behavior == DesignBehavior.DROP_BEAM
        assert behavior.service_type == 'wall'


# =============================================================================
# Tests para ElementOrchestrator - Verificación
# =============================================================================

class TestOrchestratorVerifyColumn:
    """Tests para verificación de columnas."""

    def test_verify_column_delegates_to_column_service(
        self, sample_column, mock_column_service
    ):
        """Columna delega a SeismicColumnService."""
        orchestrator = ElementOrchestrator(
            column_service=mock_column_service
        )
        result = orchestrator.verify(sample_column)

        assert mock_column_service.verify_column.called
        assert result.service_used == 'column'
        assert result.element_type == ElementType.COLUMN_SEISMIC

    def test_verify_column_returns_orchestration_result(
        self, sample_column, mock_column_service
    ):
        """Retorna OrchestrationResult con datos correctos."""
        orchestrator = ElementOrchestrator(
            column_service=mock_column_service
        )
        result = orchestrator.verify(sample_column)

        assert isinstance(result, OrchestrationResult)
        assert result.is_ok is True
        assert result.dcr_max == 0.75
        assert result.design_behavior == DesignBehavior.SEISMIC_COLUMN


class TestOrchestratorVerifyBeam:
    """Tests para verificación de vigas."""

    def test_verify_beam_delegates_to_beam_service(
        self, sample_beam, mock_beam_service
    ):
        """Viga delega a SeismicBeamService."""
        orchestrator = ElementOrchestrator(
            beam_service=mock_beam_service
        )
        result = orchestrator.verify(sample_beam)

        assert mock_beam_service.verify_beam.called
        assert result.service_used == 'beam'
        assert result.element_type == ElementType.BEAM

    def test_verify_beam_returns_orchestration_result(
        self, sample_beam, mock_beam_service
    ):
        """Retorna OrchestrationResult con datos correctos."""
        orchestrator = ElementOrchestrator(
            beam_service=mock_beam_service
        )
        result = orchestrator.verify(sample_beam)

        assert isinstance(result, OrchestrationResult)
        assert result.is_ok is True
        assert result.dcr_max == 0.60


class TestOrchestratorVerifyWall:
    """Tests para verificación de muros."""

    def test_verify_wall_delegates_to_wall_service(
        self, sample_pier, mock_wall_service
    ):
        """Muro delega a SeismicWallService."""
        orchestrator = ElementOrchestrator(
            wall_service=mock_wall_service
        )
        result = orchestrator.verify(sample_pier)

        assert mock_wall_service.verify_wall.called
        assert result.service_used == 'wall'

    def test_verify_drop_beam_delegates_to_wall_service(
        self, sample_drop_beam, mock_wall_service
    ):
        """Viga capitel delega a SeismicWallService.verify_drop_beam."""
        orchestrator = ElementOrchestrator(
            wall_service=mock_wall_service
        )
        result = orchestrator.verify(sample_drop_beam)

        assert mock_wall_service.verify_drop_beam.called
        assert result.service_used == 'wall'
        assert result.element_type == ElementType.DROP_BEAM


# =============================================================================
# Tests para ElementOrchestrator - get_verification_info
# =============================================================================

class TestOrchestratorVerificationInfo:
    """Tests para método get_verification_info()."""

    def test_column_info(self, sample_column):
        """Retorna info correcta para columna."""
        orchestrator = ElementOrchestrator()
        info = orchestrator.get_verification_info(sample_column)

        assert info['element_type'] == 'column_seismic'
        assert info['design_behavior'] == 'SEISMIC_COLUMN'
        assert info['aci_section'] == '§18.7'
        assert 'SeismicColumnService' in info['service']
        assert info['requires_seismic_checks'] is True

    def test_beam_info(self, sample_beam):
        """Retorna info correcta para viga."""
        orchestrator = ElementOrchestrator()
        info = orchestrator.get_verification_info(sample_beam)

        assert info['element_type'] == 'beam'
        assert info['design_behavior'] == 'SEISMIC_BEAM'
        assert info['aci_section'] == '§18.6'
        assert 'SeismicBeamService' in info['service']

    def test_wall_info(self, sample_pier):
        """Retorna info correcta para muro."""
        orchestrator = ElementOrchestrator()
        info = orchestrator.get_verification_info(sample_pier)

        # Puede ser wall o wall_squat dependiendo de hw/lw
        assert 'wall' in info['element_type']
        assert info['design_behavior'] == 'SEISMIC_WALL'
        assert '§18.10' in info['aci_section']
        assert 'SeismicWallService' in info['service']

    def test_drop_beam_info(self, sample_drop_beam):
        """Retorna info correcta para viga capitel."""
        orchestrator = ElementOrchestrator()
        info = orchestrator.get_verification_info(sample_drop_beam)

        assert info['element_type'] == 'drop_beam'
        assert info['design_behavior'] == 'DROP_BEAM'


# =============================================================================
# Tests para parámetros opcionales
# =============================================================================

class TestOrchestratorParameters:
    """Tests para parámetros opcionales de verify()."""

    def test_lambda_factor_passed(self, sample_column, mock_column_service):
        """lambda_factor se pasa al servicio."""
        orchestrator = ElementOrchestrator(
            column_service=mock_column_service
        )
        orchestrator.verify(sample_column, lambda_factor=0.85)

        call_kwargs = mock_column_service.verify_column.call_args[1]
        assert call_kwargs['lambda_factor'] == 0.85

    def test_category_passed(self, sample_column, mock_column_service):
        """category se pasa al servicio."""
        orchestrator = ElementOrchestrator(
            column_service=mock_column_service
        )
        orchestrator.verify(sample_column, category=SeismicCategory.INTERMEDIATE)

        call_kwargs = mock_column_service.verify_column.call_args[1]
        assert call_kwargs['category'] == SeismicCategory.INTERMEDIATE

    def test_hwcs_passed_to_wall(self, sample_pier, mock_wall_service):
        """hwcs se pasa al servicio de muros."""
        orchestrator = ElementOrchestrator(
            wall_service=mock_wall_service
        )
        orchestrator.verify(sample_pier, hwcs=5000.0)

        call_kwargs = mock_wall_service.verify_wall.call_args[1]
        assert call_kwargs['hwcs'] == 5000.0

    def test_verify_without_forces(self, sample_column, mock_column_service):
        """Puede verificar sin fuerzas (usa ceros)."""
        orchestrator = ElementOrchestrator(
            column_service=mock_column_service
        )
        result = orchestrator.verify(sample_column, forces=None)

        assert result is not None
        call_kwargs = mock_column_service.verify_column.call_args[1]
        assert call_kwargs['Vu_V2'] == 0
        assert call_kwargs['Vu_V3'] == 0
        assert call_kwargs['Pu'] == 0
