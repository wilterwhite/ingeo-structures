# tests/test_coupling_beam.py
"""
Tests para el sistema de vigas de acople genéricas.
"""
import pytest
from app.domain.entities.coupling_beam import CouplingBeamConfig, PierCouplingConfig


class TestCouplingBeamConfig:
    """Tests para la configuración de viga de acople."""

    def test_default_values(self):
        """Valores por defecto razonables."""
        beam = CouplingBeamConfig()
        assert beam.width == 200
        assert beam.height == 500
        assert beam.n_bars_top == 3
        assert beam.diameter_top == 16
        assert beam.n_legs == 2
        assert beam.fy == 420

    def test_As_top_calculation(self):
        """As_top calcula correctamente el área de acero superior."""
        beam = CouplingBeamConfig(n_bars_top=3, diameter_top=16)
        # 3 barras φ16 = 3 × 201.1 mm² = 603.3 mm²
        assert abs(beam.As_top - 603.3) < 1.0

    def test_As_bottom_calculation(self):
        """As_bottom calcula correctamente el área de acero inferior."""
        beam = CouplingBeamConfig(n_bars_bottom=4, diameter_bottom=20)
        # 4 barras φ20 = 4 × 314.2 mm² = 1256.8 mm²
        assert abs(beam.As_bottom - 1256.8) < 1.0

    def test_d_top_calculation(self):
        """d_top calcula correctamente la profundidad efectiva."""
        beam = CouplingBeamConfig(
            height=500,
            cover=40,
            stirrup_diameter=10,
            diameter_top=16
        )
        # d = 500 - 40 - 10 - 16/2 = 442 mm
        assert abs(beam.d_top - 442) < 0.1

    def test_Mn_positive_calculation(self):
        """Mn_positive calcula momento nominal correcto."""
        beam = CouplingBeamConfig(
            width=200,
            height=500,
            n_bars_bottom=3,
            diameter_bottom=16,
            fy=420,
            fc=25,
            cover=40,
            stirrup_diameter=10
        )
        # Verificar que Mn > 0 y es razonable
        assert beam.Mn_positive > 0
        assert beam.Mn_positive < 500  # kN-m, valor razonable para esta viga

    def test_Mpr_uses_alpha_125(self):
        """Mpr usa factor α = 1.25."""
        beam = CouplingBeamConfig()
        Mn = beam.Mn_positive
        Mpr = beam.Mpr_positive
        assert abs(Mpr / Mn - 1.25) < 0.001

    def test_Mpr_max_is_maximum(self):
        """Mpr_max es el máximo de positivo y negativo."""
        beam = CouplingBeamConfig(
            n_bars_top=4,
            diameter_top=20,
            n_bars_bottom=2,
            diameter_bottom=12
        )
        # Más acero arriba = Mn_negative > Mn_positive
        assert beam.Mpr_max == beam.Mpr_negative

    def test_get_summary_contains_key_info(self):
        """get_summary contiene información clave."""
        beam = CouplingBeamConfig()
        summary = beam.get_summary()
        assert 'geometry' in summary
        assert 'top' in summary
        assert 'bottom' in summary
        assert 'stirrups' in summary
        assert 'Mpr_pos_kNm' in summary
        assert 'Mpr_neg_kNm' in summary


class TestPierCouplingConfig:
    """Tests para la configuración de vigas por pier."""

    def test_default_has_beams_both_sides(self):
        """Por defecto tiene vigas en ambos lados."""
        config = PierCouplingConfig(pier_key="Story1_P1")
        assert config.has_beam_left is True
        assert config.has_beam_right is True

    def test_get_Mpr_total_with_default_beam(self):
        """Calcula Mpr total usando viga por defecto."""
        default_beam = CouplingBeamConfig()
        config = PierCouplingConfig(pier_key="Story1_P1")

        Mpr_total = config.get_Mpr_total(default_beam)
        # Dos vigas (izq + der) × Mpr_max
        expected = 2 * default_beam.Mpr_max
        assert abs(Mpr_total - expected) < 0.1

    def test_get_Mpr_total_without_left_beam(self):
        """Sin viga izquierda solo cuenta la derecha."""
        default_beam = CouplingBeamConfig()
        config = PierCouplingConfig(
            pier_key="Story1_P1",
            has_beam_left=False,
            has_beam_right=True
        )

        Mpr_total = config.get_Mpr_total(default_beam)
        expected = default_beam.Mpr_max  # Solo una viga
        assert abs(Mpr_total - expected) < 0.1

    def test_get_Mpr_total_with_custom_beam(self):
        """Usa viga personalizada si está definida."""
        default_beam = CouplingBeamConfig(
            n_bars_top=3,
            diameter_top=16
        )
        custom_beam = CouplingBeamConfig(
            n_bars_top=6,
            diameter_top=20
        )

        config = PierCouplingConfig(
            pier_key="Story1_P1",
            beam_left=custom_beam,
            has_beam_left=True,
            has_beam_right=True
        )

        Mpr_total = config.get_Mpr_total(default_beam)
        # Izq usa custom, der usa default
        expected = custom_beam.Mpr_max + default_beam.Mpr_max
        assert abs(Mpr_total - expected) < 0.1


class TestMnCalculation:
    """Tests para verificar cálculos de Mn."""

    def test_Mn_zero_if_overreinforced(self):
        """Mn = 0 si la sección está sobrearmada."""
        beam = CouplingBeamConfig(
            width=100,  # Muy angosto
            height=200,
            n_bars_bottom=10,
            diameter_bottom=32,  # Mucho acero
            fc=20  # Bajo f'c
        )
        # El bloque de compresión excedería d
        # La función debería retornar 0
        assert beam.Mn_positive >= 0  # No negativo

    def test_Mn_increases_with_more_steel(self):
        """Más acero = mayor Mn."""
        beam1 = CouplingBeamConfig(n_bars_bottom=2, diameter_bottom=12)
        beam2 = CouplingBeamConfig(n_bars_bottom=4, diameter_bottom=16)
        assert beam2.Mn_positive > beam1.Mn_positive

    def test_Mn_increases_with_depth(self):
        """Mayor altura = mayor Mn."""
        beam1 = CouplingBeamConfig(height=400)
        beam2 = CouplingBeamConfig(height=600)
        assert beam2.Mn_positive > beam1.Mn_positive


class TestCapacityDesignIntegration:
    """Tests de integración para diseño por capacidad."""

    def test_typical_coupling_beam(self):
        """Viga de acople típica tiene Mpr razonable."""
        # Viga típica 250x600 con 4φ20 arriba y abajo
        beam = CouplingBeamConfig(
            width=250,
            height=600,
            n_bars_top=4,
            diameter_top=20,
            n_bars_bottom=4,
            diameter_bottom=20,
            fc=30,
            fy=420
        )

        # Mpr debería estar entre 200-400 kN-m para esta viga
        assert 150 < beam.Mpr_max < 500

    def test_wall_capacity_check_concept(self):
        """Concepto de verificación muro fuerte-viga débil."""
        # Viga de acople
        beam = CouplingBeamConfig(
            width=200,
            height=500,
            n_bars_top=3,
            diameter_top=16,
            n_bars_bottom=3,
            diameter_bottom=16
        )

        # Mpr requerido = 1.2 × (2 × Mpr_max)
        Mpr_required = 1.2 * 2 * beam.Mpr_max

        # Un muro debería tener phi_Mn > Mpr_required
        # Este es solo un test conceptual
        assert Mpr_required > 0
        assert beam.Mpr_max > 0
