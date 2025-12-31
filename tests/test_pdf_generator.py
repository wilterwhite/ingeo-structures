# tests/test_pdf_generator.py
"""
Tests para el generador de informes PDF.
"""
import pytest
from datetime import datetime

from app.services.report import PDFReportGenerator, ReportConfig


@pytest.fixture
def generator():
    """Instancia del generador de PDF."""
    return PDFReportGenerator()


@pytest.fixture
def sample_config():
    """Configuracion de ejemplo."""
    return ReportConfig(
        project_name="Proyecto de Prueba",
        top_by_load=3,
        top_by_cuantia=3,
        include_failing=True,
        include_proposals=True,
        include_pm_diagrams=False,
        include_sections=False,
        include_full_table=True
    )


@pytest.fixture
def sample_results():
    """Resultados de ejemplo (formato dict de to_dict())."""
    return [
        {
            'pier_label': 'P1-A1',
            'story': 'Cielo P1',
            'geometry': {
                'width_m': 2.0,
                'thickness_m': 0.2,
                'height_m': 2.7
            },
            'materials': {
                'fc_MPa': 25,
                'fy_MPa': 420
            },
            'reinforcement': {
                'As_vertical_mm2': 1000,
                'As_horizontal_mm2': 800,
                'rho_vertical': 0.0025,
                'rho_horizontal': 0.002
            },
            'flexure': {
                'sf': 1.5,
                'status': 'OK',
                'critical_combo': '1.2D+1.6L',
                'Pu': 150.0,
                'Mu': 50.0
            },
            'shear': {
                'sf': 2.0,
                'status': 'OK',
                'dcr_combined': 0.5
            },
            'overall_status': 'OK',
            'proposal': {
                'has_proposal': False
            },
            'pm_plot': ''
        },
        {
            'pier_label': 'P1-A2',
            'story': 'Cielo P1',
            'geometry': {
                'width_m': 1.5,
                'thickness_m': 0.2,
                'height_m': 2.7
            },
            'materials': {
                'fc_MPa': 25,
                'fy_MPa': 420
            },
            'reinforcement': {
                'As_vertical_mm2': 800,
                'As_horizontal_mm2': 600,
                'rho_vertical': 0.0027,
                'rho_horizontal': 0.002
            },
            'flexure': {
                'sf': 0.8,
                'status': 'NO OK',
                'critical_combo': '1.2D+1.0E',
                'Pu': 200.0,
                'Mu': 80.0
            },
            'shear': {
                'sf': 1.2,
                'status': 'OK',
                'dcr_combined': 0.85
            },
            'overall_status': 'NO OK',
            'proposal': {
                'has_proposal': True,
                'failure_mode': 'flexure',
                'description': 'Aumentar borde: 4x16'
            },
            'pm_plot': ''
        },
        {
            'pier_label': 'P2-B1',
            'story': 'Cielo P2',
            'geometry': {
                'width_m': 3.0,
                'thickness_m': 0.25,
                'height_m': 2.7
            },
            'materials': {
                'fc_MPa': 30,
                'fy_MPa': 420
            },
            'reinforcement': {
                'As_vertical_mm2': 1500,
                'As_horizontal_mm2': 1200,
                'rho_vertical': 0.002,
                'rho_horizontal': 0.0016
            },
            'flexure': {
                'sf': 1.8,
                'status': 'OK',
                'critical_combo': '1.4D',
                'Pu': 250.0,
                'Mu': 30.0
            },
            'shear': {
                'sf': 3.0,
                'status': 'OK',
                'dcr_combined': 0.33
            },
            'overall_status': 'OK',
            'proposal': {
                'has_proposal': False
            },
            'pm_plot': ''
        }
    ]


@pytest.fixture
def sample_statistics():
    """Estadisticas de ejemplo."""
    return {
        'total': 3,
        'ok': 2,
        'fail': 1,
        'pass_rate': 66.7
    }


class TestReportConfig:
    """Tests para ReportConfig."""

    def test_default_values(self):
        """Valores por defecto."""
        config = ReportConfig()
        assert config.project_name == "Proyecto Sin Nombre"
        assert config.top_by_load == 5
        assert config.top_by_cuantia == 5
        assert config.include_failing is True
        assert config.include_proposals is True

    def test_from_dict(self):
        """Creacion desde diccionario."""
        data = {
            'project_name': 'Mi Proyecto',
            'top_by_load': 10,
            'top_by_cuantia': 8
        }
        config = ReportConfig.from_dict(data)
        assert config.project_name == 'Mi Proyecto'
        assert config.top_by_load == 10
        assert config.top_by_cuantia == 8

    def test_validate_ok(self):
        """Validacion exitosa."""
        config = ReportConfig(top_by_load=5, top_by_cuantia=5)
        errors = config.validate(total_piers=10)
        assert len(errors) == 0

    def test_validate_exceeds_total(self):
        """Validacion falla cuando excede total."""
        config = ReportConfig(top_by_load=15, top_by_cuantia=5)
        errors = config.validate(total_piers=10)
        assert len(errors) == 1
        assert "excede" in errors[0]

    def test_validate_negative(self):
        """Validacion falla con valores negativos."""
        config = ReportConfig(top_by_load=-1, top_by_cuantia=5)
        errors = config.validate(total_piers=10)
        assert len(errors) == 1
        assert "negativo" in errors[0]

    def test_to_dict(self):
        """Conversion a diccionario."""
        config = ReportConfig(project_name='Test')
        d = config.to_dict()
        assert d['project_name'] == 'Test'
        assert 'generated_at' in d


class TestPDFReportGenerator:
    """Tests para PDFReportGenerator."""

    def test_generator_initialization(self, generator):
        """El generador se inicializa correctamente."""
        assert generator is not None
        assert generator.styles is not None

    def test_generate_report_returns_bytes(
        self, generator, sample_results, sample_config, sample_statistics
    ):
        """generate_report retorna bytes."""
        pdf_bytes = generator.generate_report(
            results=sample_results,
            piers={},
            config=sample_config,
            statistics=sample_statistics
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # Verificar que es un PDF valido (empieza con %PDF-)
        assert pdf_bytes[:5] == b'%PDF-'

    def test_generate_report_empty_results(self, generator, sample_config):
        """Genera PDF aunque no haya resultados."""
        pdf_bytes = generator.generate_report(
            results=[],
            piers={},
            config=sample_config,
            statistics={'total': 0, 'ok': 0, 'fail': 0, 'pass_rate': 0}
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_report_minimal_config(self, generator, sample_results):
        """Genera PDF con configuracion minima."""
        config = ReportConfig(
            project_name="Minimal",
            top_by_load=0,
            top_by_cuantia=0,
            include_failing=False,
            include_proposals=False,
            include_pm_diagrams=False,
            include_sections=False,
            include_full_table=False
        )

        pdf_bytes = generator.generate_report(
            results=sample_results,
            piers={},
            config=config
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_report_full_config(
        self, generator, sample_results, sample_statistics
    ):
        """Genera PDF con configuracion completa."""
        config = ReportConfig(
            project_name="Full Report",
            top_by_load=3,
            top_by_cuantia=3,
            include_failing=True,
            include_proposals=True,
            include_pm_diagrams=True,  # No hay plots, pero no debe fallar
            include_sections=True,
            include_full_table=True
        )

        pdf_bytes = generator.generate_report(
            results=sample_results,
            piers={},
            config=config,
            statistics=sample_statistics
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_report_with_failing_piers(
        self, generator, sample_results, sample_config
    ):
        """Genera PDF con seccion de piers que fallan."""
        # sample_results ya tiene un pier que falla
        pdf_bytes = generator.generate_report(
            results=sample_results,
            piers={},
            config=sample_config
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_report_all_piers_ok(self, generator, sample_config):
        """Genera PDF cuando todos los piers pasan."""
        results = [
            {
                'pier_label': 'P1-A1',
                'story': 'Cielo P1',
                'geometry': {'width_m': 2.0, 'thickness_m': 0.2, 'height_m': 2.7},
                'materials': {'fc_MPa': 25, 'fy_MPa': 420},
                'reinforcement': {
                    'As_vertical_mm2': 1000, 'As_horizontal_mm2': 800,
                    'rho_vertical': 0.0025, 'rho_horizontal': 0.002
                },
                'flexure': {'sf': 1.5, 'status': 'OK', 'critical_combo': '1.2D+1.6L', 'Pu': 150, 'Mu': 50},
                'shear': {'sf': 2.0, 'status': 'OK', 'dcr_combined': 0.5},
                'overall_status': 'OK',
                'proposal': {'has_proposal': False},
                'pm_plot': ''
            }
        ]

        pdf_bytes = generator.generate_report(
            results=results,
            piers={},
            config=sample_config,
            statistics={'total': 1, 'ok': 1, 'fail': 0, 'pass_rate': 100}
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestPDFReportGeneratorHelpers:
    """Tests para metodos auxiliares del generador."""

    def test_create_data_table(self, generator):
        """Crea tabla de datos correctamente."""
        data = [
            ['Header1', 'Header2', 'Estado'],
            ['Value1', 'Value2', 'OK'],
            ['Value3', 'Value4', 'NO OK']
        ]

        table = generator._create_data_table(data)
        assert table is not None

    def test_create_data_table_no_status_highlight(self, generator):
        """Crea tabla sin resaltar estado."""
        data = [
            ['Col1', 'Col2'],
            ['A', 'B']
        ]

        table = generator._create_data_table(data, highlight_status=False)
        assert table is not None

    def test_build_cover_page(self, generator, sample_config):
        """Construye portada."""
        elements = generator._build_cover_page(sample_config)
        assert len(elements) > 0

    def test_build_executive_summary(self, generator, sample_results, sample_statistics):
        """Construye resumen ejecutivo."""
        elements = generator._build_executive_summary(
            sample_results,
            sample_statistics,
            None  # Sin grafico
        )
        assert len(elements) > 0

    def test_build_critical_by_load(self, generator, sample_results):
        """Construye seccion de criticos por carga."""
        elements = generator._build_critical_by_load(sample_results, n=2)
        assert len(elements) > 0

    def test_build_critical_by_cuantia(self, generator, sample_results):
        """Construye seccion de criticos por cuantia."""
        elements = generator._build_critical_by_cuantia(sample_results, n=2)
        assert len(elements) > 0

    def test_build_failing_piers_with_proposals(self, generator, sample_results):
        """Construye seccion de piers que fallan con propuestas."""
        elements = generator._build_failing_piers(sample_results, include_proposals=True)
        assert len(elements) > 0

    def test_build_failing_piers_without_proposals(self, generator, sample_results):
        """Construye seccion de piers que fallan sin propuestas."""
        elements = generator._build_failing_piers(sample_results, include_proposals=False)
        assert len(elements) > 0

    def test_build_full_results_table(self, generator, sample_results):
        """Construye tabla completa."""
        elements = generator._build_full_results_table(sample_results)
        assert len(elements) > 0
