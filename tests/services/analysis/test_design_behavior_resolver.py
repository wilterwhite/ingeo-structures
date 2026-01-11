# tests/services/analysis/test_design_behavior_resolver.py
"""
Tests para DesignBehaviorResolver.

Verifica que:
1. WALL_PIER_COLUMN recibe verificaciones §18.7 (columna sismica)
2. Beams con axial significativo reciben verificaciones de flexocompresion
3. Beams sismicas sin axial reciben verificaciones §18.6
4. Columnas sismicas reciben verificaciones §18.7
"""
import pytest
from dataclasses import dataclass
from typing import Optional, List

from app.services.analysis.design_behavior import DesignBehavior
from app.services.analysis.design_behavior_resolver import DesignBehaviorResolver
from app.services.analysis.element_classifier import ElementType


# ============================================================================
# Fixtures: Mock Elements
# ============================================================================

@dataclass
class MockBeam:
    """Mock de Beam para tests."""
    width: float = 300  # mm
    depth: float = 600  # mm
    length: float = 5000  # mm
    fc: float = 28  # MPa
    fy: float = 420  # MPa
    cover: float = 40  # mm
    is_seismic: bool = True

    @property
    def Ag(self) -> float:
        """Area bruta en mm2."""
        return self.width * self.depth


@dataclass
class MockColumn:
    """Mock de Column para tests."""
    width: float = 400  # mm
    depth: float = 400  # mm
    height: float = 3000  # mm
    fc: float = 28  # MPa
    fy: float = 420  # MPa
    cover: float = 40  # mm
    is_seismic: bool = True

    @property
    def Ag(self) -> float:
        return self.width * self.depth


@dataclass
class MockPier:
    """Mock de Pier para tests."""
    width: float = 2000  # mm (lw)
    thickness: float = 200  # mm (tw)
    height: float = 3000  # mm (hw)
    fc: float = 28  # MPa
    fy: float = 420  # MPa
    cover: float = 25  # mm
    is_seismic: bool = True

    @property
    def Ag(self) -> float:
        return self.width * self.thickness


@dataclass
class MockLoadCombination:
    """Mock de LoadCombination."""
    name: str
    P: float = 0  # tonf
    M2: float = 0  # tonf-m
    M3: float = 0  # tonf-m
    V2: float = 0  # tonf
    V3: float = 0  # tonf


@dataclass
class MockForces:
    """Mock de Forces para tests."""
    combinations: Optional[List[MockLoadCombination]] = None

    def get_envelope(self) -> dict:
        """Retorna envolvente de fuerzas."""
        if not self.combinations:
            return {'P_max': 0, 'P_min': 0}

        P_max = max(c.P for c in self.combinations)
        P_min = min(c.P for c in self.combinations)
        return {'P_max': P_max, 'P_min': P_min}


# ============================================================================
# Tests: WALL_PIER_COLUMN
# ============================================================================

class TestWallPierColumn:
    """Tests para piers tipo columna (lw/tw <= 2.5, hw/lw < 2.0)."""

    def test_wall_pier_column_gets_seismic_column_behavior(self):
        """
        WALL_PIER_COLUMN debe recibir comportamiento SEISMIC_COLUMN.

        Esto corrige el gap arquitectonico donde los piers columnares
        no recibian verificaciones §18.7.
        """
        resolver = DesignBehaviorResolver()
        pier = MockPier(width=600, thickness=300)  # lw/tw = 2.0 <= 2.5
        forces = MockForces()

        behavior = resolver.resolve(
            ElementType.WALL_PIER_COLUMN,
            pier,
            forces,
            is_seismic=True
        )

        assert behavior == DesignBehavior.SEISMIC_COLUMN
        assert behavior.requires_column_checks
        assert behavior.aci_section == "§18.7"

    def test_wall_pier_column_requires_confinement(self):
        """WALL_PIER_COLUMN debe requerir verificacion de confinamiento."""
        resolver = DesignBehaviorResolver()
        pier = MockPier(width=500, thickness=250)  # lw/tw = 2.0

        behavior = resolver.resolve(
            ElementType.WALL_PIER_COLUMN,
            pier,
            None,
            is_seismic=True
        )

        assert behavior.requires_confinement


# ============================================================================
# Tests: Beams
# ============================================================================

class TestBeamBehavior:
    """Tests para comportamiento de vigas."""

    def test_seismic_beam_without_axial_gets_seismic_beam_behavior(self):
        """Viga sismica sin axial significativo → SEISMIC_BEAM."""
        resolver = DesignBehaviorResolver()
        beam = MockBeam()
        forces = MockForces(combinations=[
            MockLoadCombination('1.4D', P=5)  # Axial minimo
        ])

        behavior = resolver.resolve(
            ElementType.BEAM,
            beam,
            forces,
            is_seismic=True
        )

        assert behavior == DesignBehavior.SEISMIC_BEAM

    def test_beam_with_significant_axial_gets_seismic_beam_column(self):
        """
        Viga sísmica con axial > Ag*fc'/10 → SEISMIC_BEAM_COLUMN.

        Según ACI 318-25 §18.6.4.6, cuando Pu > Ag*fc'/10,
        se requieren hoops (estribos cerrados) como columna.
        Esto es SEISMIC_BEAM_COLUMN, no FLEXURE_COMPRESSION.
        """
        resolver = DesignBehaviorResolver()
        beam = MockBeam(width=300, depth=600, fc=28)
        # Ag = 300*600 = 180000 mm2
        # fc = 28 MPa
        # Umbral = 180000 * 28 / 10 = 504000 N = 51.4 tonf
        # Usamos P = 60 tonf > 51.4 tonf
        forces = MockForces(combinations=[
            MockLoadCombination('1.2D+L+E', P=60)
        ])

        behavior = resolver.resolve(
            ElementType.BEAM,
            beam,
            forces,
            is_seismic=True
        )

        assert behavior == DesignBehavior.SEISMIC_BEAM_COLUMN

    def test_nonseismic_beam_without_axial_gets_flexure_only(self):
        """Viga no-sismica sin axial → FLEXURE_ONLY."""
        resolver = DesignBehaviorResolver()
        beam = MockBeam(is_seismic=False)
        forces = MockForces(combinations=[
            MockLoadCombination('1.4D', P=0)
        ])

        behavior = resolver.resolve(
            ElementType.BEAM,
            beam,
            forces,
            is_seismic=False
        )

        assert behavior == DesignBehavior.FLEXURE_ONLY

    def test_beam_no_forces_defaults_to_seismic_beam(self):
        """Viga sismica sin fuerzas → SEISMIC_BEAM."""
        resolver = DesignBehaviorResolver()
        beam = MockBeam()

        behavior = resolver.resolve(
            ElementType.BEAM,
            beam,
            None,  # Sin fuerzas
            is_seismic=True
        )

        assert behavior == DesignBehavior.SEISMIC_BEAM


# ============================================================================
# Tests: Columns
# ============================================================================

class TestColumnBehavior:
    """Tests para comportamiento de columnas."""

    def test_seismic_column_gets_seismic_column_behavior(self):
        """Columna sismica → SEISMIC_COLUMN."""
        resolver = DesignBehaviorResolver()
        column = MockColumn()

        behavior = resolver.resolve(
            ElementType.COLUMN_SEISMIC,
            column,
            None,
            is_seismic=True
        )

        assert behavior == DesignBehavior.SEISMIC_COLUMN
        assert behavior.requires_column_checks
        assert behavior.requires_confinement

    def test_nonseismic_column_gets_flexure_compression(self):
        """Columna no-sismica → FLEXURE_COMPRESSION."""
        resolver = DesignBehaviorResolver()
        column = MockColumn(is_seismic=False)

        behavior = resolver.resolve(
            ElementType.COLUMN_NONSEISMIC,
            column,
            None,
            is_seismic=False
        )

        assert behavior == DesignBehavior.FLEXURE_COMPRESSION
        assert behavior.requires_pm_diagram
        assert not behavior.requires_seismic_checks


# ============================================================================
# Tests: Walls
# ============================================================================

class TestWallBehavior:
    """Tests para comportamiento de muros."""

    def test_wall_gets_seismic_wall_behavior(self):
        """Muro esbelto → SEISMIC_WALL."""
        resolver = DesignBehaviorResolver()
        pier = MockPier(width=4000, thickness=200, height=10000)

        behavior = resolver.resolve(
            ElementType.WALL,
            pier,
            None,
            is_seismic=True
        )

        assert behavior == DesignBehavior.SEISMIC_WALL
        assert behavior.requires_wall_checks

    def test_wall_squat_gets_seismic_wall_behavior(self):
        """Muro bajo (squat) → SEISMIC_WALL."""
        resolver = DesignBehaviorResolver()
        pier = MockPier(width=4000, thickness=200, height=4000)  # hw/lw = 1.0

        behavior = resolver.resolve(
            ElementType.WALL_SQUAT,
            pier,
            None,
            is_seismic=True
        )

        assert behavior == DesignBehavior.SEISMIC_WALL

    def test_wall_pier_alternate_gets_specific_behavior(self):
        """Pier alternativo (2.5 < lw/tw <= 6.0) → SEISMIC_WALL_PIER_ALT."""
        resolver = DesignBehaviorResolver()
        pier = MockPier(width=1000, thickness=200)  # lw/tw = 5.0

        behavior = resolver.resolve(
            ElementType.WALL_PIER_ALTERNATE,
            pier,
            None,
            is_seismic=True
        )

        assert behavior == DesignBehavior.SEISMIC_WALL_PIER_ALT


# ============================================================================
# Tests: Drop Beams
# ============================================================================

class TestDropBeamBehavior:
    """Tests para vigas capitel."""

    def test_drop_beam_gets_drop_beam_behavior(self):
        """Viga capitel → DROP_BEAM."""
        resolver = DesignBehaviorResolver()

        # Mock simple de DropBeam
        @dataclass
        class MockDropBeam:
            width: float = 800
            length: float = 2000
            thickness: float = 200
            fc: float = 28
            fy: float = 420

            @property
            def Ag(self):
                return self.width * self.thickness

        drop_beam = MockDropBeam()

        behavior = resolver.resolve(
            ElementType.DROP_BEAM,
            drop_beam,
            None,
            is_seismic=True
        )

        assert behavior == DesignBehavior.DROP_BEAM
        assert behavior.requires_pm_diagram


# ============================================================================
# Tests: Behavior Info
# ============================================================================

class TestBehaviorInfo:
    """Tests para get_behavior_info."""

    def test_behavior_info_contains_all_properties(self):
        """get_behavior_info retorna todas las propiedades."""
        resolver = DesignBehaviorResolver()

        info = resolver.get_behavior_info(DesignBehavior.SEISMIC_COLUMN)

        assert 'behavior' in info
        assert 'aci_section' in info
        assert 'requires_pm_diagram' in info
        assert 'requires_seismic_checks' in info
        assert 'requires_column_checks' in info
        assert 'requires_wall_checks' in info
        assert 'requires_confinement' in info

    def test_seismic_column_info(self):
        """Info de SEISMIC_COLUMN es correcta."""
        resolver = DesignBehaviorResolver()

        info = resolver.get_behavior_info(DesignBehavior.SEISMIC_COLUMN)

        assert info['behavior'] == 'SEISMIC_COLUMN'
        assert info['aci_section'] == '§18.7'
        assert info['requires_pm_diagram'] is True
        assert info['requires_seismic_checks'] is True
        assert info['requires_column_checks'] is True
        assert info['requires_wall_checks'] is False
        assert info['requires_confinement'] is True
