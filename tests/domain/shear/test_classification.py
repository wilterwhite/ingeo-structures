# tests/domain/shear/test_classification.py
"""
Tests para clasificacion de elementos segun ACI 318-25.

Verifica que la clasificacion considere:
- Tabla R18.10.1: lw/tw para muro vs columna
- S18.7.2.1(b): b/h >= 0.4 para columnas de porticos especiales
"""
import pytest
from app.domain.shear.classification import (
    WallClassificationService,
    ElementType,
)


class TestColumnAspectRatioReclassification:
    """
    Tests para reclasificacion de elementos que geometricamente
    serian columnas (lw/tw < 4) pero no cumplen S18.7.2.1(b).

    S18.7.2.1: Columns shall satisfy (a) and (b):
    (b) The ratio of the shortest cross-sectional dimension to
        the perpendicular dimension shall be at least 0.4.

    Si b/h < 0.4, el elemento NO puede ser columna de portico especial
    y debe disenarse como muro segun S18.10.
    """

    @pytest.fixture
    def service(self):
        return WallClassificationService()

    def test_column_valid_aspect_ratio(self, service):
        """Columna con b/h >= 0.4 se clasifica como COLUMN."""
        # 300x600mm: lw/tw = 2.0 < 4, b/h = 300/600 = 0.5 >= 0.4
        result = service.classify(lw=600, tw=300, hw=3000)

        assert result.element_type == ElementType.COLUMN
        assert result.design_method == "column"
        assert "22.5" in result.aci_section

    def test_column_exactly_at_limit(self, service):
        """Columna con b/h = 0.4 exacto se clasifica como COLUMN."""
        # 200x500mm: lw/tw = 2.5 < 4, b/h = 200/500 = 0.4 exacto
        result = service.classify(lw=500, tw=200, hw=3000)

        assert result.element_type == ElementType.COLUMN
        assert result.design_method == "column"

    def test_reclassify_to_wall_when_aspect_ratio_too_low(self, service):
        """
        Elemento 250x800mm: lw/tw = 3.2 < 4 (seria columna)
        pero b/h = 250/800 = 0.31 < 0.4 -> debe reclasificarse como MURO.

        hw/lw = 3000/800 = 3.75 >= 2.0 -> WALL (no WALL_SQUAT)
        """
        result = service.classify(lw=800, tw=250, hw=3000)

        assert result.element_type == ElementType.WALL
        assert result.design_method == "wall"
        assert "18.10" in result.aci_section
        assert "Reclasificado" in result.special_requirements
        assert "b/h=" in result.special_requirements
        assert "S18.7.2.1(b)" in result.special_requirements

    def test_reclassify_to_wall_squat_when_aspect_ratio_too_low(self, service):
        """
        Elemento 200x800mm: lw/tw = 4.0 exacto -> NO es columna
        Pero si fuera 200x700: lw/tw = 3.5 < 4, b/h = 200/700 = 0.29 < 0.4

        Con hw/lw < 2.0 -> WALL_SQUAT
        """
        # 200x700mm, altura 1000mm: lw/tw = 3.5 < 4, hw/lw = 1000/700 = 1.43 < 2
        result = service.classify(lw=700, tw=200, hw=1000)

        assert result.element_type == ElementType.WALL_SQUAT
        assert result.design_method == "wall"
        assert "18.10" in result.aci_section
        assert "Reclasificado" in result.special_requirements

    def test_extreme_case_20x200(self, service):
        """
        Caso extremo: 20x200cm = 200x2000mm
        lw/tw = 10 >= 4 -> es MURO normal (no aplica reclasificacion)
        """
        result = service.classify(lw=2000, tw=200, hw=3000)

        # lw/tw = 10 >= 4, asi que es muro normal, no columna
        # hw/lw = 3000/2000 = 1.5 < 2.0 -> WALL_SQUAT o WALL_PIER
        assert result.element_type in (
            ElementType.WALL,
            ElementType.WALL_SQUAT,
            ElementType.WALL_PIER_ALTERNATE
        )

    def test_narrow_column_reclassified(self, service):
        """
        Elemento muy angosto 150x600mm:
        lw/tw = 4.0 exacto -> es MURO (no aplica reclasificacion)

        Pero 150x500mm: lw/tw = 3.33 < 4, b/h = 150/500 = 0.3 < 0.4
        -> Reclasificar como muro
        """
        result = service.classify(lw=500, tw=150, hw=2500)

        # hw/lw = 2500/500 = 5.0 >= 2.0 -> WALL
        assert result.element_type == ElementType.WALL
        assert "Reclasificado" in result.special_requirements


class TestStandardClassification:
    """Tests para clasificacion estandar sin reclasificacion."""

    @pytest.fixture
    def service(self):
        return WallClassificationService()

    def test_wall_normal(self, service):
        """Muro normal con lw/tw >= 4 y hw/lw >= 2."""
        # 200x2000mm, hw=5000: lw/tw = 10, hw/lw = 2.5
        result = service.classify(lw=2000, tw=200, hw=5000)

        assert result.element_type == ElementType.WALL

    def test_wall_squat(self, service):
        """Muro rechoncho con lw/tw > 6 y hw/lw < 2."""
        # 200x2000mm, hw=3000: lw/tw = 10 > 6, hw/lw = 1.5 < 2
        result = service.classify(lw=2000, tw=200, hw=3000)

        assert result.element_type == ElementType.WALL_SQUAT

    def test_wall_pier_column(self, service):
        """Wall pier tipo columna: lw/tw <= 2.5 y hw/lw < 2."""
        # 300x600mm, hw=1000: lw/tw = 2.0 <= 2.5, hw/lw = 1.67 < 2
        # PERO b/h = 300/600 = 0.5 >= 0.4, asi que es COLUMN no WALL_PIER_COLUMN
        # Necesitamos lw/tw >= 4 para que sea wall pier
        # 200x500mm: lw/tw = 2.5, b/h = 0.4
        result = service.classify(lw=500, tw=200, hw=900)

        # b/h = 200/500 = 0.4 exacto, asi que ES columna
        assert result.element_type == ElementType.COLUMN

    def test_wall_pier_alternate(self, service):
        """Wall pier alternativo: 2.5 < lw/tw <= 6 y hw/lw < 2."""
        # 200x1000mm, hw=1500: lw/tw = 5.0, hw/lw = 1.5
        result = service.classify(lw=1000, tw=200, hw=1500)

        assert result.element_type == ElementType.WALL_PIER_ALTERNATE
