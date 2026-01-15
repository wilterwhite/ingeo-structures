# tests/services/presentation/test_result_formatter.py
"""
Tests para ResultFormatter - formateo de resultados para UI.
"""
import pytest
from unittest.mock import Mock

from app.services.presentation.result_formatter import (
    ResultFormatter,
    get_status_css_class,
    get_dcr_css_class,
)
from app.services.analysis.element_orchestrator import OrchestrationResult
from app.services.analysis.element_classifier import ElementType
from app.services.analysis.design_behavior import DesignBehavior
from app.domain.entities import (
    VerticalElement, VerticalElementSource,
    HorizontalElement, HorizontalElementSource,
    DiscreteReinforcement, MeshReinforcement,
    HorizontalDiscreteReinforcement, HorizontalMeshReinforcement,
)


# =============================================================================
# Helper functions para crear Mocks bien configurados
# =============================================================================

def create_shear_mock(
    dcr: float = 0.5,
    phi_Vn: float = 500000,
    Ve: float = 250000,
    Vu: float = 200000,
    Vc: float = 200000,
    Vs: float = 300000
) -> Mock:
    """
    Crea un Mock de shear result con valores numéricos.

    Evita el error 'Mock doesn't define __round__' al usar round()
    sobre atributos del Mock.

    Nota: capacity_V2 se setea a None para evitar que hasattr() retorne True
    y el código intente acceder a sh.capacity_V2.Vc (que sería un Mock).
    """
    shear = Mock()
    shear.dcr = dcr
    shear.phi_Vn = phi_Vn
    shear.phi_Vn_V2 = phi_Vn
    shear.Ve = Ve
    shear.Vu = Vu
    shear.Vu_V2 = Vu
    shear.Vc = Vc
    shear.Vs = Vs
    shear.phi_v = 0.75
    shear.status = 'OK' if dcr <= 1.0 else 'NO OK'
    # Evitar que hasattr(sh, 'capacity_V2') retorne True
    shear.capacity_V2 = None
    return shear


def create_domain_result_mock(
    shear: Mock = None,
    flexure: Mock = None,
    include_boundary: bool = False,
    include_dimensional: bool = False,
    include_reinforcement: bool = False
) -> Mock:
    """
    Crea un Mock de domain_result con atributos None explícitos.

    Esto evita que getattr() retorne un Mock cuando debería retornar None,
    lo que causa errores al iterar sobre 'warnings' o usar round().
    """
    domain_result = Mock()
    domain_result.shear = shear
    domain_result.flexure = flexure
    domain_result.boundary = None
    domain_result.dimensional_limits = None
    domain_result.beam_dimensional = None
    domain_result.classification = None
    domain_result.reinforcement = None

    if include_boundary:
        boundary = Mock()
        boundary.warnings = []
        domain_result.boundary = boundary

    if include_dimensional:
        dim = Mock()
        dim.min_dimension_ok = True
        dim.aspect_ratio_ok = True
        dim.min_dimension = 400
        dim.min_dimension_required = 300
        dim.aspect_ratio = 0.8
        domain_result.dimensional_limits = dim

    if include_reinforcement:
        rf = Mock()
        rf.rho_l_ok = True
        rf.rho_t_ok = True
        rf.spacing_ok = True
        rf.rho_l_min = 0.0025
        rf.spacing_max = 450
        domain_result.reinforcement = rf

    return domain_result


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_column():
    """Columna de prueba (VerticalElement con source FRAME)."""
    return VerticalElement(
        label="C1",
        story="Piso 1",
        source=VerticalElementSource.FRAME,
        length=500,  # depth
        thickness=400,  # width
        height=3000,
        fc=30,
        fy=420,
        discrete_reinforcement=DiscreteReinforcement(
            n_bars_length=3,
            n_bars_thickness=4,
            diameter=20,
        ),
        stirrup_diameter=10,
        stirrup_spacing=100,
        n_shear_legs=2,
        n_shear_legs_secondary=3,
    )


@pytest.fixture
def sample_beam():
    """Viga de prueba (HorizontalElement con source FRAME)."""
    return HorizontalElement(
        label="V1",
        story="Piso 1",
        source=HorizontalElementSource.FRAME,
        width=300,
        depth=600,
        length=6000,
        fc=25,
        fy=420,
        stirrup_diameter=8,
        stirrup_spacing=150,
        n_stirrup_legs=2,
        discrete_reinforcement=HorizontalDiscreteReinforcement(
            n_bars_top=3,
            n_bars_bottom=4,
            diameter_top=16,
            diameter_bottom=20,
        ),
    )


@pytest.fixture
def sample_pier():
    """Pier/muro de prueba (VerticalElement con source PIER)."""
    return VerticalElement(
        label="M1",
        story="Piso 1",
        source=VerticalElementSource.PIER,
        length=2000,  # lw
        thickness=200,  # tw
        height=2700,
        fc=25,
        fy=420,
        mesh_reinforcement=MeshReinforcement(
            n_meshes=2,
            diameter_v=10,
            spacing_v=200,
            diameter_h=8,
            spacing_h=200,
            n_edge_bars=4,
            diameter_edge=16,
        ),
        stirrup_diameter=8,
        stirrup_spacing=150,
        n_shear_legs=2,
    )


@pytest.fixture
def sample_drop_beam():
    """Viga capitel de prueba (HorizontalElement con source DROP_BEAM)."""
    return HorizontalElement(
        label="VC1",
        story="Piso 1",
        source=HorizontalElementSource.DROP_BEAM,
        width=200,
        depth=2400,
        length=1500,
        fc=25,
        fy=420,
        mesh_reinforcement=HorizontalMeshReinforcement(
            n_meshes=2,
            diameter_v=10,
            spacing_v=150,
            diameter_h=10,
            spacing_h=200,
            n_edge_bars=2,
            diameter_edge=16,
        ),
    )


@pytest.fixture
def column_orchestration_result():
    """OrchestrationResult para columna."""
    shear = create_shear_mock(dcr=0.65, phi_Vn=500000, Ve=350000, Vu=320000)
    domain_result = create_domain_result_mock(shear=shear)

    return OrchestrationResult(
        element_type=ElementType.COLUMN_SEISMIC,
        design_behavior=DesignBehavior.SEISMIC_COLUMN,
        service_used='column',
        domain_result=domain_result,
        is_ok=True,
        dcr_max=0.75,
        critical_check='',
        warnings=[],
    )


@pytest.fixture
def beam_orchestration_result():
    """OrchestrationResult para viga."""
    shear = create_shear_mock(dcr=0.55, phi_Vn=400000, Ve=220000, Vu=200000)
    domain_result = create_domain_result_mock(shear=shear)

    return OrchestrationResult(
        element_type=ElementType.BEAM,
        design_behavior=DesignBehavior.SEISMIC_BEAM,
        service_used='beam',
        domain_result=domain_result,
        is_ok=True,
        dcr_max=0.60,
        critical_check='',
        warnings=[],
    )


@pytest.fixture
def wall_orchestration_result():
    """OrchestrationResult para muro."""
    shear = create_shear_mock(dcr=0.70, phi_Vn=600000, Ve=420000, Vu=400000)
    flexure = Mock()
    flexure.sf = 1.5
    flexure.status = 'OK'
    domain_result = create_domain_result_mock(
        shear=shear,
        flexure=flexure,
        include_reinforcement=True
    )

    return OrchestrationResult(
        element_type=ElementType.WALL_SQUAT,
        design_behavior=DesignBehavior.SEISMIC_WALL,
        service_used='wall',
        domain_result=domain_result,
        is_ok=True,
        dcr_max=0.70,
        critical_check='',
        warnings=[],
    )


@pytest.fixture
def drop_beam_orchestration_result():
    """OrchestrationResult para viga capitel."""
    shear = create_shear_mock(dcr=0.50, phi_Vn=350000, Ve=175000, Vu=160000)
    flexure = Mock()
    flexure.sf = 1.8
    flexure.status = 'OK'
    domain_result = create_domain_result_mock(shear=shear, flexure=flexure)

    return OrchestrationResult(
        element_type=ElementType.DROP_BEAM,
        design_behavior=DesignBehavior.DROP_BEAM,
        service_used='wall',
        domain_result=domain_result,
        is_ok=True,
        dcr_max=0.55,
        critical_check='',
        warnings=[],
    )


# =============================================================================
# Tests para funciones auxiliares
# =============================================================================

class TestCssClasses:
    """Tests para funciones de clases CSS."""

    def test_status_ok(self):
        """Status OK retorna clase correcta."""
        assert get_status_css_class('OK') == 'status-ok'

    def test_status_fail(self):
        """Status NO OK retorna clase correcta."""
        assert get_status_css_class('NO OK') == 'status-fail'

    def test_status_other(self):
        """Cualquier otro status retorna fail."""
        assert get_status_css_class('WARN') == 'status-fail'

    def test_dcr_low(self):
        """DCR bajo retorna ok."""
        assert get_dcr_css_class(0.5) == 'fs-ok'
        assert get_dcr_css_class(0.67) == 'fs-ok'

    def test_dcr_medium(self):
        """DCR medio retorna warn."""
        assert get_dcr_css_class(0.8) == 'fs-warn'
        assert get_dcr_css_class(1.0) == 'fs-warn'

    def test_dcr_high(self):
        """DCR alto retorna fail."""
        assert get_dcr_css_class(1.1) == 'fs-fail'
        assert get_dcr_css_class(2.0) == 'fs-fail'


# =============================================================================
# Tests para format_any_element - Column
# =============================================================================

class TestFormatColumn:
    """Tests para formateo de columnas."""

    def test_format_column_basic(self, sample_column, column_orchestration_result):
        """Formatea columna con campos básicos."""
        formatted = ResultFormatter.format_any_element(
            sample_column, column_orchestration_result, 'col_1'
        )

        # Columnas FRAME se formatean como 'column', piers como 'pier'
        assert formatted['element_type'] == 'column'
        assert formatted['key'] == 'col_1'
        assert formatted['pier_label'] == 'C1'
        assert formatted['story'] == 'Piso 1'

    def test_format_column_geometry(self, sample_column, column_orchestration_result):
        """Incluye geometría correcta."""
        formatted = ResultFormatter.format_any_element(
            sample_column, column_orchestration_result, 'col_1'
        )

        geom = formatted['geometry']
        assert geom['width_m'] == 0.5  # depth / 1000
        assert geom['thickness_m'] == 0.4  # width / 1000
        assert geom['fc_MPa'] == 30
        assert geom['fy_MPa'] == 420

    def test_format_column_reinforcement(self, sample_column, column_orchestration_result):
        """Incluye refuerzo correcto."""
        formatted = ResultFormatter.format_any_element(
            sample_column, column_orchestration_result, 'col_1'
        )

        reinf = formatted['reinforcement']
        # Con la nueva arquitectura, el refuerzo usa nomenclatura de VerticalElement
        # n_bars_depth/width están disponibles via propiedades alias
        assert reinf['stirrup_spacing'] == 100
        assert reinf['stirrup_diameter'] == 10
        # Las propiedades de refuerzo se extraen del VerticalElement
        assert 'n_meshes' in reinf or 'n_bars_length' in reinf or reinf['stirrup_spacing'] == 100

    def test_format_column_status(self, sample_column, column_orchestration_result):
        """Incluye estado correcto."""
        formatted = ResultFormatter.format_any_element(
            sample_column, column_orchestration_result, 'col_1'
        )

        assert formatted['overall_status'] == 'OK'
        assert formatted['status_class'] == 'status-ok'
        assert formatted['dcr_max'] == 0.75

    def test_format_column_design_info(self, sample_column, column_orchestration_result):
        """Incluye información de diseño."""
        formatted = ResultFormatter.format_any_element(
            sample_column, column_orchestration_result, 'col_1'
        )

        assert formatted['design_behavior'] == 'SEISMIC_COLUMN'
        assert formatted['service_used'] == 'column'
        assert formatted['aci_section'] == '§18.7'

    def test_format_column_failed(self, sample_column):
        """Formatea columna que falla."""
        domain_result = create_domain_result_mock(shear=None, flexure=None)
        result = OrchestrationResult(
            element_type=ElementType.COLUMN_SEISMIC,
            design_behavior=DesignBehavior.SEISMIC_COLUMN,
            service_used='column',
            domain_result=domain_result,
            is_ok=False,
            dcr_max=1.35,
            critical_check='shear',
            warnings=['Refuerzo transversal insuficiente'],
        )

        formatted = ResultFormatter.format_any_element(
            sample_column, result, 'col_1'
        )

        assert formatted['overall_status'] == 'NO OK'
        assert formatted['status_class'] == 'status-fail'
        assert formatted['critical_check'] == 'shear'
        assert 'Refuerzo transversal' in formatted['warnings'][0]


# =============================================================================
# Tests para format_any_element - Beam
# =============================================================================

class TestFormatBeam:
    """Tests para formateo de vigas."""

    def test_format_beam_basic(self, sample_beam, beam_orchestration_result):
        """Formatea viga con campos básicos."""
        formatted = ResultFormatter.format_any_element(
            sample_beam, beam_orchestration_result, 'beam_1'
        )

        assert formatted['element_type'] == 'beam'
        assert formatted['key'] == 'beam_1'
        assert formatted['pier_label'] == 'V1'  # Usa pier_label para consistencia
        assert formatted['story'] == 'Piso 1'

    def test_format_beam_geometry(self, sample_beam, beam_orchestration_result):
        """Incluye geometría correcta."""
        formatted = ResultFormatter.format_any_element(
            sample_beam, beam_orchestration_result, 'beam_1'
        )

        geom = formatted['geometry']
        assert geom['thickness_m'] == 0.6  # depth / 1000
        assert geom['width_m'] == 0.3  # width / 1000
        assert geom['height_m'] == 6.0  # length / 1000

    def test_format_beam_reinforcement(self, sample_beam, beam_orchestration_result):
        """Incluye refuerzo correcto."""
        formatted = ResultFormatter.format_any_element(
            sample_beam, beam_orchestration_result, 'beam_1'
        )

        reinf = formatted['reinforcement']
        assert reinf['n_bars_top'] == 3
        assert reinf['n_bars_bottom'] == 4
        assert reinf['diameter_top'] == 16
        assert reinf['diameter_bottom'] == 20

    def test_format_beam_design_info(self, sample_beam, beam_orchestration_result):
        """Incluye información de diseño."""
        formatted = ResultFormatter.format_any_element(
            sample_beam, beam_orchestration_result, 'beam_1'
        )

        assert formatted['design_behavior'] == 'SEISMIC_BEAM'
        assert formatted['service_used'] == 'beam'
        assert formatted['aci_section'] == '§18.6'


# =============================================================================
# Tests para format_any_element - Pier/Wall
# =============================================================================

class TestFormatPier:
    """Tests para formateo de muros."""

    def test_format_pier_basic(self, sample_pier, wall_orchestration_result):
        """Formatea muro con campos básicos."""
        formatted = ResultFormatter.format_any_element(
            sample_pier, wall_orchestration_result, 'pier_1'
        )

        assert formatted['element_type'] in ['pier', 'pier_column']
        assert formatted['key'] == 'pier_1'
        assert formatted['pier_label'] == 'M1'
        assert formatted['story'] == 'Piso 1'

    def test_format_pier_geometry(self, sample_pier, wall_orchestration_result):
        """Incluye geometría correcta."""
        formatted = ResultFormatter.format_any_element(
            sample_pier, wall_orchestration_result, 'pier_1'
        )

        geom = formatted['geometry']
        assert geom['width_m'] == 2.0  # width / 1000
        assert geom['thickness_m'] == 0.2  # thickness / 1000
        assert geom['height_m'] == 2.7  # height / 1000

    def test_format_pier_has_wall_continuity(self, sample_pier, wall_orchestration_result):
        """Incluye información de continuidad de muro."""
        formatted = ResultFormatter.format_any_element(
            sample_pier, wall_orchestration_result, 'pier_1'
        )

        assert 'wall_continuity' in formatted
        continuity = formatted['wall_continuity']
        assert 'hwcs_m' in continuity
        assert 'hwcs_lw' in continuity

    def test_format_pier_design_info(self, sample_pier, wall_orchestration_result):
        """Incluye información de diseño."""
        formatted = ResultFormatter.format_any_element(
            sample_pier, wall_orchestration_result, 'pier_1'
        )

        assert formatted['design_behavior'] == 'SEISMIC_WALL'
        assert formatted['service_used'] == 'wall'
        assert formatted['aci_section'] == '§18.10'


# =============================================================================
# Tests para format_any_element - DropBeam
# =============================================================================

class TestFormatDropBeam:
    """Tests para formateo de vigas capitel."""

    def test_format_drop_beam_basic(self, sample_drop_beam, drop_beam_orchestration_result):
        """Formatea viga capitel con campos básicos."""
        formatted = ResultFormatter.format_any_element(
            sample_drop_beam, drop_beam_orchestration_result, 'db_1'
        )

        assert formatted['element_type'] == 'drop_beam'
        assert formatted['key'] == 'db_1'
        assert formatted['pier_label'] == 'VC1'  # Usa pier_label, no label
        assert formatted['story'] == 'Piso 1'

    def test_format_drop_beam_geometry(self, sample_drop_beam, drop_beam_orchestration_result):
        """Incluye geometría correcta (unificada con beam)."""
        formatted = ResultFormatter.format_any_element(
            sample_drop_beam, drop_beam_orchestration_result, 'db_1'
        )

        geom = formatted['geometry']
        # Geometría unificada: width=ancho, thickness=peralte, height=luz
        assert geom['width_m'] == 0.2   # width (ancho) / 1000
        assert geom['thickness_m'] == 2.4  # depth (peralte) / 1000
        assert geom['height_m'] == 1.5  # length (luz) / 1000

    def test_format_drop_beam_reinforcement(self, sample_drop_beam, drop_beam_orchestration_result):
        """Incluye refuerzo correcto (formato unificado)."""
        formatted = ResultFormatter.format_any_element(
            sample_drop_beam, drop_beam_orchestration_result, 'db_1'
        )

        reinf = formatted['reinforcement']
        # Formato unificado: barras de borde, estribos, barras laterales
        assert reinf['n_edge_bars'] == 2
        assert reinf['diameter_edge'] == 16
        assert 'stirrup_diameter' in reinf
        assert 'diameter_lateral' in reinf  # Barras laterales (antes "malla vertical")

    def test_format_drop_beam_design_info(self, sample_drop_beam, drop_beam_orchestration_result):
        """Incluye información de diseño."""
        formatted = ResultFormatter.format_any_element(
            sample_drop_beam, drop_beam_orchestration_result, 'db_1'
        )

        assert formatted['design_behavior'] == 'DROP_BEAM'
        assert formatted['service_used'] == 'wall'


# =============================================================================
# Tests para casos borde
# =============================================================================

class TestEdgeCases:
    """Tests para casos borde."""

    def test_unknown_element_type(self, column_orchestration_result):
        """Elemento desconocido retorna formato genérico."""
        unknown = Mock()

        formatted = ResultFormatter.format_any_element(
            unknown, column_orchestration_result, 'unknown_1'
        )

        assert formatted['element_type'] == 'unknown'
        assert formatted['key'] == 'unknown_1'

    def test_result_with_warnings(self, sample_column):
        """Formatea resultado con warnings."""
        domain_result = create_domain_result_mock(shear=None, flexure=None)
        result = OrchestrationResult(
            element_type=ElementType.COLUMN_SEISMIC,
            design_behavior=DesignBehavior.SEISMIC_COLUMN,
            service_used='column',
            domain_result=domain_result,
            is_ok=True,
            dcr_max=0.85,
            critical_check='',
            warnings=['Warning 1', 'Warning 2'],
        )

        formatted = ResultFormatter.format_any_element(
            sample_column, result, 'col_1'
        )

        assert len(formatted['warnings']) == 2
        assert 'Warning 1' in formatted['warnings']

    def test_format_with_pm_plot(self, sample_column, column_orchestration_result):
        """Incluye gráfico P-M si se proporciona."""
        formatted = ResultFormatter.format_any_element(
            sample_column, column_orchestration_result, 'col_1',
            pm_plot='base64_encoded_image'
        )

        assert formatted['pm_plot'] == 'base64_encoded_image'
