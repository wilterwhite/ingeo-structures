# tests/domain/calculations/test_reinforcement_proposer.py
"""
Tests para ReinforcementProposer.

Verifica las reglas de propuesta de armadura segun geometria:
1. Ambos < 15cm → STRUT (1×1, sin estribos)
2. Un lado >= 15cm, otro < 15cm → grilla asimetrica con traba
3. Ambos >= 15cm → grilla 2×2+ con estribos
4. >= 5 barras en algun lado → MESH
"""
import pytest
from app.domain.calculations.reinforcement_proposer import (
    ReinforcementProposer,
    ReinforcementProposal,
    ProposedLayout,
)
from app.domain.constants.reinforcement import (
    STRUT_MAX_DIM_MM,
    MAX_BAR_SPACING_MM,
    MIN_BARS_FOR_MESH,
)


class TestStrut:
    """Tests para propuesta STRUT (columnas pequenas < 15cm)."""

    def test_12x12_is_strut(self):
        """12x12cm → STRUT (1×1, sin estribos)."""
        proposal = ReinforcementProposer.propose(120, 120)
        assert proposal.layout == ProposedLayout.STRUT
        assert proposal.n_bars_length == 1
        assert proposal.n_bars_thickness == 1
        assert proposal.stirrup_diameter == 0
        assert proposal.stirrup_spacing == 0

    def test_14x14_is_strut(self):
        """14x14cm → STRUT (ambos < 15cm)."""
        proposal = ReinforcementProposer.propose(140, 140)
        assert proposal.layout == ProposedLayout.STRUT
        assert proposal.n_bars_length == 1
        assert proposal.n_bars_thickness == 1

    def test_exactly_149mm_is_strut(self):
        """149x149mm → STRUT (ambos < 150mm)."""
        proposal = ReinforcementProposer.propose(149, 149)
        assert proposal.layout == ProposedLayout.STRUT

    def test_strut_has_no_crossties(self):
        """Strut no tiene trabas ni estribos."""
        proposal = ReinforcementProposer.propose(120, 120)
        assert proposal.has_crossties is False
        assert proposal.n_shear_legs == 0


class TestStirrupsWithCrossties:
    """Tests para grillas asimetricas con trabas."""

    def test_150x120_uses_crossties(self):
        """15x12cm → grilla 2×1 con traba (1 rama en thickness)."""
        proposal = ReinforcementProposer.propose(150, 120)
        assert proposal.layout == ProposedLayout.STIRRUPS
        assert proposal.n_bars_length == 2  # >= 15cm
        assert proposal.n_bars_thickness == 1  # < 15cm
        assert proposal.has_crossties is True
        # Traba: 1 rama en direccion del lado con 1 barra
        assert proposal.n_shear_legs == 2  # length tiene 2 barras
        assert proposal.n_shear_legs_secondary == 1  # thickness tiene 1 barra

    def test_120x200_uses_crossties(self):
        """12x20cm → grilla 1×2 con traba (1 rama en length)."""
        proposal = ReinforcementProposer.propose(120, 200)
        assert proposal.layout == ProposedLayout.STIRRUPS
        assert proposal.n_bars_length == 1  # < 15cm
        assert proposal.n_bars_thickness == 2  # >= 15cm
        assert proposal.has_crossties is True
        assert proposal.n_shear_legs == 1  # length tiene 1 barra
        assert proposal.n_shear_legs_secondary == 2  # thickness tiene 2 barras


class TestStirrupsNormal:
    """Tests para columnas normales con estribos."""

    def test_150x150_is_stirrups_2x2(self):
        """15x15cm → STIRRUPS 2×2 con estribos (2 ramas)."""
        proposal = ReinforcementProposer.propose(150, 150)
        assert proposal.layout == ProposedLayout.STIRRUPS
        assert proposal.n_bars_length == 2
        assert proposal.n_bars_thickness == 2
        assert proposal.has_crossties is False
        assert proposal.n_shear_legs == 2
        assert proposal.n_shear_legs_secondary == 2

    def test_200x200_is_stirrups_2x2(self):
        """20x20cm → STIRRUPS 2×2."""
        proposal = ReinforcementProposer.propose(200, 200)
        assert proposal.layout == ProposedLayout.STIRRUPS
        assert proposal.n_bars_length == 2
        assert proposal.n_bars_thickness == 2

    def test_400x200_is_stirrups_3x2(self):
        """40x20cm → STIRRUPS 3×2 (40cm/20cm = 3 barras, 20cm/20cm = 2 barras)."""
        proposal = ReinforcementProposer.propose(400, 200)
        assert proposal.layout == ProposedLayout.STIRRUPS
        assert proposal.n_bars_length == 3  # ceil(400/200)+1 = 3
        assert proposal.n_bars_thickness == 2  # ceil(200/200)+1 = 2

    def test_stirrups_has_default_diameter(self):
        """Columnas normales usan diametro por defecto (16mm)."""
        proposal = ReinforcementProposer.propose(300, 300)
        assert proposal.diameter == 16
        assert proposal.stirrup_diameter == 10
        assert proposal.stirrup_spacing == 150


class TestMesh:
    """Tests para muros que usan layout MESH."""

    def test_800x200_is_mesh(self):
        """80x20cm → MESH (5 barras en length >= MIN_BARS_FOR_MESH)."""
        proposal = ReinforcementProposer.propose(800, 200)
        assert proposal.layout == ProposedLayout.MESH
        assert proposal.n_bars_length >= 5

    def test_200x800_is_mesh(self):
        """20x80cm → MESH (5 barras en thickness >= MIN_BARS_FOR_MESH)."""
        proposal = ReinforcementProposer.propose(200, 800)
        assert proposal.layout == ProposedLayout.MESH
        assert proposal.n_bars_thickness >= 5

    def test_2000x200_is_mesh(self):
        """200x20cm → MESH (muro tipico)."""
        proposal = ReinforcementProposer.propose(2000, 200)
        assert proposal.layout == ProposedLayout.MESH
        # 2000/200 = 10 -> ceil(10)+1 = 11 barras
        assert proposal.n_bars_length >= 10

    def test_mesh_has_correct_defaults(self):
        """MESH usa diametro por defecto de malla (8mm)."""
        proposal = ReinforcementProposer.propose(1000, 200)
        assert proposal.diameter == 8  # MESH_DEFAULTS['diameter_v']


class TestBarCalculation:
    """Tests para el calculo de cantidad de barras."""

    def test_150mm_gives_2_bars(self):
        """150mm → 2 barras (minimo para >= 15cm)."""
        n = ReinforcementProposer._calc_bars_for_dimension(150)
        assert n == 2

    def test_200mm_gives_2_bars(self):
        """200mm → 2 barras (200/200=1, ceil+1=2)."""
        n = ReinforcementProposer._calc_bars_for_dimension(200)
        assert n == 2

    def test_400mm_gives_3_bars(self):
        """400mm → 3 barras (400/200=2, ceil+1=3)."""
        n = ReinforcementProposer._calc_bars_for_dimension(400)
        assert n == 3

    def test_800mm_gives_5_bars(self):
        """800mm → 5 barras (800/200=4, ceil+1=5) → transicion a MESH."""
        n = ReinforcementProposer._calc_bars_for_dimension(800)
        assert n == 5

    def test_less_than_150_gives_1_bar(self):
        """< 150mm → 1 barra (strut)."""
        n = ReinforcementProposer._calc_bars_for_dimension(140)
        assert n == 1


class TestConstants:
    """Tests para verificar las constantes estan correctas."""

    def test_strut_limit(self):
        """El limite para strut es 150mm."""
        assert STRUT_MAX_DIM_MM == 150.0

    def test_max_bar_spacing(self):
        """El espaciamiento maximo es 200mm."""
        assert MAX_BAR_SPACING_MM == 200.0

    def test_min_bars_for_mesh(self):
        """Minimo 5 barras para cambiar a MESH."""
        assert MIN_BARS_FOR_MESH == 5
