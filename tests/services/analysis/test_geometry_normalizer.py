# tests/services/analysis/test_geometry_normalizer.py
"""
Tests para GeometryNormalizer - normalizacion de geometria de elementos.
"""
import pytest
import math

from app.services.analysis.geometry_normalizer import (
    GeometryNormalizer,
    ColumnGeometry,
    BeamGeometry,
    WallGeometry,
)
from app.domain.entities import (
    VerticalElement, VerticalElementSource,
    HorizontalElement, HorizontalElementSource,
    DiscreteReinforcement, MeshReinforcement,
    HorizontalDiscreteReinforcement, HorizontalMeshReinforcement,
)


@pytest.fixture
def sample_column():
    """Column de prueba (VerticalElement con source FRAME)."""
    return VerticalElement(
        label="C1",
        story="Piso 1",
        source=VerticalElementSource.FRAME,
        length=500,         # depth (mm)
        thickness=400,      # width (mm)
        height=3000,        # mm
        fc=30,              # MPa
        fy=420,             # MPa
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
def sample_pier():
    """Pier de prueba (VerticalElement con source PIER)."""
    return VerticalElement(
        label="M1-A",
        story="Cielo P1",
        source=VerticalElementSource.PIER,
        length=2000,        # lw (mm)
        thickness=200,      # tw (mm)
        height=2700,        # hw (mm)
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
def sample_beam():
    """Beam de prueba (HorizontalElement con source FRAME)."""
    return HorizontalElement(
        label="V1",
        story="Piso 1",
        source=HorizontalElementSource.FRAME,
        width=300,          # mm
        depth=600,          # mm
        length=6000,        # mm
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
def sample_drop_beam():
    """DropBeam de prueba (HorizontalElement con source DROP_BEAM)."""
    # DROP_BEAM ahora usa discrete_reinforcement (barras top/bottom) igual que BEAM
    return HorizontalElement(
        label="VC1",
        story="Cielo P1",
        source=HorizontalElementSource.DROP_BEAM,
        width=200,          # espesor losa (mm)
        depth=2400,         # ancho tributario (mm)
        length=1500,        # luz libre (mm)
        fc=25,
        fy=420,
        discrete_reinforcement=HorizontalDiscreteReinforcement(
            n_bars_top=4,
            n_bars_bottom=4,
            diameter_top=16,
            diameter_bottom=16,
        ),
    )


class TestColumnGeometry:
    """Tests para la dataclass ColumnGeometry."""

    def test_default_values(self):
        """Valores por defecto."""
        geom = ColumnGeometry()
        assert geom.b == 0.0
        assert geom.h == 0.0
        assert geom.cover == 25.0
        assert geom.fc == 25.0
        assert geom.fy == 420.0

    def test_to_dict(self):
        """Conversion a diccionario."""
        geom = ColumnGeometry(b=400, h=500, Ag=200000)
        d = geom.to_dict()

        assert d['b'] == 400
        assert d['h'] == 500
        assert d['Ag'] == 200000
        assert 'Mnc_top' in d
        assert 'Mnb_left' in d


class TestBeamGeometry:
    """Tests para la dataclass BeamGeometry."""

    def test_default_values(self):
        """Valores por defecto."""
        geom = BeamGeometry()
        assert geom.bw == 0.0
        assert geom.h == 0.0
        assert geom.d == 0.0
        assert geom.fc == 25.0

    def test_to_dict(self):
        """Conversion a diccionario."""
        geom = BeamGeometry(bw=300, h=600, d=540)
        d = geom.to_dict()

        assert d['bw'] == 300
        assert d['h'] == 600
        assert d['d'] == 540


class TestWallGeometry:
    """Tests para la dataclass WallGeometry."""

    def test_default_values(self):
        """Valores por defecto."""
        geom = WallGeometry()
        assert geom.lw == 0.0
        assert geom.tw == 0.0
        assert geom.n_stirrup_legs == 2

    def test_to_dict(self):
        """Conversion a diccionario."""
        geom = WallGeometry(lw=2000, tw=200, hw=2700)
        d = geom.to_dict()

        assert d['lw'] == 2000
        assert d['tw'] == 200
        assert d['hw'] == 2700


class TestColumnToColumnGeometry:
    """Tests para to_column() con Column."""

    def test_basic_dimensions(self, sample_column):
        """Extrae dimensiones basicas correctamente."""
        geom = GeometryNormalizer.to_column(sample_column)

        # b = min(depth, width) = min(500, 400) = 400
        # h = max(depth, width) = max(500, 400) = 500
        assert geom.b == 400
        assert geom.h == 500
        assert geom.cover == sample_column.cover
        assert geom.fc == 30
        assert geom.fy == 420

    def test_reinforcement_extracted(self, sample_column):
        """Extrae refuerzo longitudinal y transversal."""
        geom = GeometryNormalizer.to_column(sample_column)

        assert geom.Ast > 0  # Debe tener acero longitudinal
        assert geom.n_bars > 0
        assert geom.db_long == 20
        assert geom.s_transverse == 100

    def test_area_gross(self, sample_column):
        """Area bruta calculada correctamente."""
        geom = GeometryNormalizer.to_column(sample_column)
        expected_Ag = sample_column.width * sample_column.depth
        assert geom.Ag == expected_Ag


class TestPierToColumnGeometry:
    """Tests para to_column() con Pier."""

    def test_basic_dimensions(self, sample_pier):
        """Extrae dimensiones para pier como columna."""
        geom = GeometryNormalizer.to_column(sample_pier)

        # Para pier como columna, b = column_b (o thickness), h = column_h (o width)
        assert geom.b > 0
        assert geom.h > 0
        assert geom.lu == sample_pier.height
        assert geom.fc == 25

    def test_reinforcement_from_pier(self, sample_pier):
        """Extrae refuerzo de pier (barras de borde + mallas)."""
        geom = GeometryNormalizer.to_column(sample_pier)

        # Ast incluye As_vertical + As_edge_total
        assert geom.Ast > 0
        assert geom.n_bars > 0

    def test_ash_calculated(self, sample_pier):
        """Ash calculado desde estribos del pier."""
        geom = GeometryNormalizer.to_column(sample_pier)

        # Ash = area_estribo * n_legs
        stirrup_area = math.pi * (sample_pier.stirrup_diameter / 2) ** 2
        expected_Ash = stirrup_area * sample_pier.n_shear_legs
        assert abs(geom.Ash - expected_Ash) < 1


class TestBeamToColumnGeometry:
    """Tests para to_column() con Beam (viga con axial significativo)."""

    def test_basic_dimensions(self, sample_beam):
        """Extrae dimensiones de viga."""
        geom = GeometryNormalizer.to_column(sample_beam)

        assert geom.b == 300  # width
        assert geom.h == 600  # depth
        assert geom.fc == 25

    def test_combined_reinforcement(self, sample_beam):
        """Acero combinado de top y bottom."""
        geom = GeometryNormalizer.to_column(sample_beam)

        # n_bars = n_top + n_bottom
        assert geom.n_bars == 7  # 3 + 4
        # Ast = As_top + As_bottom
        assert geom.Ast > 0

    def test_db_long_is_max(self, sample_beam):
        """db_long es el maximo de top y bottom."""
        geom = GeometryNormalizer.to_column(sample_beam)

        # max(16, 20) = 20
        assert geom.db_long == 20


class TestBeamToBeamGeometry:
    """Tests para to_beam() con Beam."""

    def test_basic_dimensions(self, sample_beam):
        """Extrae dimensiones basicas de viga."""
        geom = GeometryNormalizer.to_beam(sample_beam)

        assert geom.bw == 300
        assert geom.h == 600
        assert geom.d == sample_beam.d
        assert geom.fc == 25

    def test_reinforcement_separated(self, sample_beam):
        """Refuerzo top y bottom separados."""
        geom = GeometryNormalizer.to_beam(sample_beam)

        assert geom.n_bars_top == 3
        assert geom.n_bars_bottom == 4
        assert geom.As_top > 0
        assert geom.As_bottom > 0

    def test_stirrup_data(self, sample_beam):
        """Datos de estribos extraidos."""
        geom = GeometryNormalizer.to_beam(sample_beam)

        assert geom.s_in_zone == 150
        assert geom.Av > 0


class TestColumnToBeamGeometry:
    """Tests para to_beam() con Column (axial insignificante)."""

    def test_dimensions_mapped(self, sample_column):
        """Dimensiones mapeadas correctamente."""
        geom = GeometryNormalizer.to_beam(sample_column)

        # bw = min dimension, h = max dimension
        assert geom.bw == 400  # min(500, 400)
        assert geom.h == 500   # max(500, 400)

    def test_reinforcement_split(self, sample_column):
        """Refuerzo dividido entre top y bottom."""
        geom = GeometryNormalizer.to_beam(sample_column)

        # Acero dividido en dos
        assert geom.As_top > 0
        assert geom.As_bottom > 0
        # Total aproximadamente igual al original
        total_As = geom.As_top + geom.As_bottom
        assert total_As > 0


class TestPierToWallGeometry:
    """Tests para to_wall() con Pier."""

    def test_basic_dimensions(self, sample_pier):
        """Extrae dimensiones de muro."""
        geom = GeometryNormalizer.to_wall(sample_pier)

        assert geom.lw == 2000
        assert geom.tw == 200
        assert geom.hw == 2700
        assert geom.fc == 25

    def test_areas(self, sample_pier):
        """Areas calculadas correctamente."""
        geom = GeometryNormalizer.to_wall(sample_pier)

        assert geom.Ag == sample_pier.Ag
        assert geom.Acv > 0

    def test_reinforcement_ratios(self, sample_pier):
        """Cuantias de refuerzo."""
        geom = GeometryNormalizer.to_wall(sample_pier)

        assert geom.rho_v >= 0
        assert geom.rho_h >= 0

    def test_edge_reinforcement(self, sample_pier):
        """Refuerzo de borde."""
        geom = GeometryNormalizer.to_wall(sample_pier)

        assert geom.n_edge_bars == 4
        assert geom.diameter_edge == 16
        assert geom.As_edge > 0


class TestDropBeamToWallGeometry:
    """Tests para to_wall() con DropBeam."""

    def test_basic_dimensions(self, sample_drop_beam):
        """Extrae dimensiones de viga capitel como muro equivalente."""
        geom = GeometryNormalizer.to_wall(sample_drop_beam)

        # Mapeo DropBeam → Wall (consistente con SeismicWallService):
        # hw (altura muro) ← length (luz libre viga capitel)
        # lw (longitud muro) ← thickness (ancho tributario)
        # tw (espesor muro) ← width (espesor losa)
        assert geom.hw == 1500  # length (luz libre)
        assert geom.lw == 2400  # thickness (ancho tributario)
        assert geom.tw == 200   # width (espesor losa)
        assert geom.fc == 25

    def test_edge_reinforcement(self, sample_drop_beam):
        """Refuerzo de borde de viga capitel (ahora barras top/bottom)."""
        geom = GeometryNormalizer.to_wall(sample_drop_beam)

        # DROP_BEAM usa discrete_reinforcement: n_edge_bars = n_bars_top + n_bars_bottom
        assert geom.n_edge_bars == 8  # 4 top + 4 bottom
        assert geom.diameter_edge == 16


class TestEdgeCases:
    """Tests para casos borde."""

    def test_to_column_unknown_type(self):
        """Tipo desconocido retorna geometria vacia."""
        # Pasando algo que no es Column/Pier/Beam
        geom = GeometryNormalizer.to_column(None)
        assert geom.b == 0
        assert geom.h == 0

    def test_to_beam_unknown_type(self):
        """Tipo desconocido retorna geometria vacia."""
        geom = GeometryNormalizer.to_beam(None)
        assert geom.bw == 0

    def test_to_wall_unknown_type(self):
        """Tipo desconocido retorna geometria vacia."""
        geom = GeometryNormalizer.to_wall(None)
        assert geom.lw == 0
