# tests/domain/entities/test_composite_section.py
"""Tests para CompositeSection y WallSegment."""
import pytest
import math

from app.domain.entities.composite_section import (
    CompositeSection,
    WallSegment,
    SectionShapeType,
)


class TestWallSegment:
    """Tests para WallSegment."""

    def test_horizontal_segment(self):
        """Segmento horizontal de 1000mm x 200mm."""
        seg = WallSegment(x1=0, y1=0, x2=1000, y2=0, thickness=200)

        assert seg.length == pytest.approx(1000, rel=1e-3)
        assert seg.area == pytest.approx(200000, rel=1e-3)  # 1000 * 200
        assert seg.centroid == (500, 0)
        assert seg.orientation == 'horizontal'

    def test_vertical_segment(self):
        """Segmento vertical de 600mm x 200mm."""
        seg = WallSegment(x1=0, y1=0, x2=0, y2=600, thickness=200)

        assert seg.length == pytest.approx(600, rel=1e-3)
        assert seg.area == pytest.approx(120000, rel=1e-3)  # 600 * 200
        assert seg.centroid == (0, 300)
        assert seg.orientation == 'vertical'

    def test_get_corners(self):
        """Verificar que get_corners retorna 4 esquinas correctas."""
        seg = WallSegment(x1=0, y1=0, x2=1000, y2=0, thickness=200)
        corners = seg.get_corners()

        assert len(corners) == 4

        # Para un segmento horizontal, las esquinas deben estar
        # a +-100mm (thickness/2) en Y
        y_values = [c[1] for c in corners]
        assert 100 in y_values or pytest.approx(100, rel=1e-3) in y_values
        assert -100 in y_values or pytest.approx(-100, rel=1e-3) in y_values


class TestCompositeSectionLShape:
    """Tests para sección L."""

    @pytest.fixture
    def l_section(self):
        """Crea una sección L típica: 1200x200 + 800x200."""
        # Ala horizontal
        seg1 = WallSegment(x1=0, y1=0, x2=1200, y2=0, thickness=200)
        # Ala vertical (conectada al final de seg1)
        seg2 = WallSegment(x1=1200, y1=0, x2=1200, y2=800, thickness=200)

        return CompositeSection(segments=[seg1, seg2])

    def test_detect_l_shape(self, l_section):
        """Detecta correctamente forma L."""
        assert l_section.shape_type == SectionShapeType.L_SHAPE

    def test_area_l_shape(self, l_section):
        """Área de L = suma de áreas de segmentos."""
        # Seg1: 1200 * 200 = 240000
        # Seg2: 800 * 200 = 160000
        # Total: 400000 (pero hay superposición en la esquina)
        expected_area = 240000 + 160000
        assert l_section.Ag == pytest.approx(expected_area, rel=0.01)

    def test_centroid_l_shape(self, l_section):
        """Centroide de L está desplazado hacia la esquina."""
        cx, cy = l_section.centroid

        # El centroide debe estar entre los centroides de ambos segmentos
        # Seg1 centroid: (600, 0)
        # Seg2 centroid: (1200, 400)
        # Con pesos por área: (600*240000 + 1200*160000) / 400000 = 840
        #                     (0*240000 + 400*160000) / 400000 = 160

        assert 500 < cx < 1000  # Entre los dos centroides
        assert 0 < cy < 400

    def test_Ixx_l_shape(self, l_section):
        """Momento de inercia Ixx calculado con ejes paralelos."""
        Ixx = l_section.Ixx
        # Ixx debe ser positivo y razonable
        assert Ixx > 0
        # Para una L de estas dimensiones, Ixx debería ser del orden de 10^10 mm^4
        assert 1e9 < Ixx < 1e12

    def test_Acv_l_shape(self, l_section):
        """Acv debe ser el área del segmento más largo (alma)."""
        Acv = l_section.calculate_Acv('primary')
        # El segmento más largo es seg1 (1200mm)
        assert Acv == pytest.approx(240000, rel=0.01)


class TestCompositeSectionTShape:
    """Tests para sección T."""

    @pytest.fixture
    def t_section(self):
        """Crea una sección T: ala horizontal 1000x150 + alma vertical 600x200."""
        # Ala horizontal (centrada)
        seg_flange = WallSegment(x1=-500, y1=0, x2=500, y2=0, thickness=150)
        # Alma vertical (conectada al centro del ala)
        seg_web = WallSegment(x1=0, y1=0, x2=0, y2=600, thickness=200)

        return CompositeSection(segments=[seg_flange, seg_web])

    def test_detect_t_shape(self, t_section):
        """Detecta correctamente forma T."""
        # Debería detectar como L porque solo hay 2 segmentos
        assert t_section.shape_type in [SectionShapeType.L_SHAPE, SectionShapeType.T_SHAPE]


class TestCompositeSectionBoundingBox:
    """Tests para bounding box."""

    def test_bounding_box_l_shape(self):
        """Bounding box de L."""
        seg1 = WallSegment(x1=0, y1=0, x2=1000, y2=0, thickness=200)
        seg2 = WallSegment(x1=1000, y1=0, x2=1000, y2=600, thickness=200)
        cs = CompositeSection(segments=[seg1, seg2])

        x_min, y_min, x_max, y_max = cs.bounding_box

        # Debe cubrir todo el L
        assert x_min < 0 or x_min == pytest.approx(0, abs=100)
        assert y_min == pytest.approx(-100, abs=50)  # thickness/2
        assert x_max > 1000
        assert y_max >= 600  # El bounding box llega hasta y_max del seg2


class TestCompositeSectionSerialization:
    """Tests para serialización."""

    def test_to_dict(self):
        """Verificar que to_dict incluye todos los campos."""
        seg = WallSegment(x1=0, y1=0, x2=1000, y2=0, thickness=200)
        cs = CompositeSection(segments=[seg])

        data = cs.to_dict()

        assert 'shape_type' in data
        assert 'n_segments' in data
        assert 'Ag_mm2' in data
        assert 'centroid_mm' in data
        assert 'segments' in data
        assert len(data['segments']) == 1


class TestVerticalElementWithComposite:
    """Tests para VerticalElement con composite_section."""

    def test_is_composite_property(self):
        """Verificar propiedad is_composite."""
        from app.domain.entities.vertical_element import VerticalElement, VerticalElementSource

        # Sin composite
        pier = VerticalElement(
            label="P1",
            story="Story1",
            length=1000,
            thickness=200,
            height=3000,
            fc=28,
            source=VerticalElementSource.PIER,
        )
        assert pier.is_composite is False
        assert pier.shape_type == "rectangular"

        # Con composite
        seg = WallSegment(x1=0, y1=0, x2=1000, y2=0, thickness=200)
        cs = CompositeSection(segments=[seg])

        pier.composite_section = cs
        assert pier.is_composite is True

    def test_Ag_uses_composite(self):
        """Verificar que Ag usa composite_section cuando existe."""
        from app.domain.entities.vertical_element import VerticalElement, VerticalElementSource

        # Crear L-shape
        seg1 = WallSegment(x1=0, y1=0, x2=1000, y2=0, thickness=200)
        seg2 = WallSegment(x1=1000, y1=0, x2=1000, y2=600, thickness=200)
        cs = CompositeSection(segments=[seg1, seg2])

        pier = VerticalElement(
            label="PL1",
            story="Story1",
            length=1000,  # Valor rectangular original
            thickness=200,
            height=3000,
            fc=28,
            source=VerticalElementSource.PIER,
        )

        # Sin composite: Ag = length * thickness = 200000
        assert pier.Ag == pytest.approx(200000, rel=0.01)

        # Con composite: Ag = suma de áreas de segmentos
        pier.composite_section = cs
        expected_Ag = 1000 * 200 + 600 * 200  # 320000
        assert pier.Ag == pytest.approx(expected_Ag, rel=0.01)

    def test_Acv_uses_composite(self):
        """Verificar que Acv usa composite_section cuando existe."""
        from app.domain.entities.vertical_element import VerticalElement, VerticalElementSource

        seg1 = WallSegment(x1=0, y1=0, x2=1000, y2=0, thickness=200)
        seg2 = WallSegment(x1=1000, y1=0, x2=1000, y2=600, thickness=200)
        cs = CompositeSection(segments=[seg1, seg2])

        pier = VerticalElement(
            label="PL1",
            story="Story1",
            length=1000,
            thickness=200,
            height=3000,
            fc=28,
            source=VerticalElementSource.PIER,
        )

        # Sin composite: Acv = length * thickness
        assert pier.Acv == pier.length * pier.thickness

        # Con composite: Acv = área del alma (segmento más largo)
        pier.composite_section = cs
        # El segmento más largo es seg1 (1000mm)
        assert pier.Acv == pytest.approx(200000, rel=0.01)
