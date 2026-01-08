# tests/domain/shear/test_alpha_sh_materials.py
"""
Tests para factor alpha_sh (§18.10.4.4) y validaciones de materiales (§18.2).
"""
import pytest
import math

from app.domain.constants.shear import (
    calculate_alpha_sh,
    ALPHA_SH_MIN,
    ALPHA_SH_MAX,
)
from app.domain.constants.materials import (
    get_effective_fc_shear,
    get_effective_fyt_shear,
    get_effective_fyt_confinement,
    FC_MAX_SHEAR_MPA,
    FYT_MAX_SHEAR_MPA,
    FYT_MAX_CONFINEMENT_MPA,
)
from app.domain.constants.units import N_TO_TONF
from app.domain.shear.verification import ShearVerificationService


class TestAlphaSh:
    """Tests para factor alpha_sh segun Ec. 18.10.4.4."""

    def test_muro_rectangular_sin_alas_usa_minimo(self):
        """Muro rectangular sin alas: alpha_sh = 1.0 (conservador)."""
        # Para muro rectangular: 0.7 * (1 + 0)^2 = 0.7 < 1.0
        # Debe usar limite inferior 1.0
        alpha_sh = calculate_alpha_sh(bw=300, bcf=0, tcf=0, lw=2000)
        assert alpha_sh == ALPHA_SH_MIN  # 1.0

    def test_muro_con_alas_aumenta_alpha_sh(self):
        """Muro con alas debe tener alpha_sh > 1.0."""
        # Muro T con ala significativa
        alpha_sh = calculate_alpha_sh(
            bw=300,      # alma
            bcf=600,     # ancho ala
            tcf=300,     # espesor ala
            lw=2000
        )
        assert alpha_sh > ALPHA_SH_MIN
        assert alpha_sh <= ALPHA_SH_MAX

    def test_limite_superior_alpha_sh(self):
        """alpha_sh no debe exceder 1.2."""
        # Ala muy grande para forzar limite
        alpha_sh = calculate_alpha_sh(
            bw=200,
            bcf=2000,  # ala muy ancha
            tcf=500,   # espesor grande
            lw=1000
        )
        assert alpha_sh == ALPHA_SH_MAX  # 1.2

    def test_ecuacion_alpha_sh_valores_conocidos(self):
        """Verifica formula: alpha_sh = 0.7 * (1 + (bw + bcf) * tcf / Acx)^2."""
        bw = 300
        bcf = 600
        tcf = 200
        lw = 2000

        # Calcular manualmente
        Acx = bw * lw + bcf * tcf  # Area total
        flange_term = (bw + bcf) * tcf / Acx
        expected = 0.7 * (1 + flange_term) ** 2
        expected = max(1.0, min(expected, 1.2))

        alpha_sh = calculate_alpha_sh(bw=bw, bcf=bcf, tcf=tcf, lw=lw)
        assert abs(alpha_sh - expected) < 0.001

    def test_permite_usar_alpha_sh_1_conservador(self):
        """Se permite usar alpha_sh = 1.0 conservadoramente."""
        # Incluso con alas, el minimo es 1.0
        alpha_sh = calculate_alpha_sh(bw=300, bcf=0, tcf=0, lw=2000)
        assert alpha_sh == 1.0


class TestMaterialLimits:
    """Tests para limites de materiales segun §18.2."""

    def test_fc_shear_limite_normal(self):
        """f'c <= 82.7 MPa para cortante de muros especiales."""
        assert get_effective_fc_shear(50) == 50.0
        assert get_effective_fc_shear(80) == 80.0
        assert get_effective_fc_shear(82.7) == pytest.approx(82.7)

    def test_fc_shear_limita_alto(self):
        """f'c > 82.7 MPa se limita a 82.7 MPa."""
        assert get_effective_fc_shear(100) == FC_MAX_SHEAR_MPA
        assert get_effective_fc_shear(150) == FC_MAX_SHEAR_MPA

    def test_fc_lightweight_limite_mas_bajo(self):
        """Concreto liviano: f'c max = 35 MPa."""
        assert get_effective_fc_shear(50, is_lightweight=True) == 35.0
        assert get_effective_fc_shear(30, is_lightweight=True) == 30.0

    def test_fyt_shear_limite_420mpa(self):
        """fyt para cortante no debe exceder 420 MPa."""
        assert get_effective_fyt_shear(420) == 420.0
        assert get_effective_fyt_shear(550) == FYT_MAX_SHEAR_MPA  # 420

    def test_fyt_confinement_limite_690mpa(self):
        """fyt para confinamiento puede ser hasta 690 MPa."""
        assert get_effective_fyt_confinement(550) == 550.0
        assert get_effective_fyt_confinement(700) == FYT_MAX_CONFINEMENT_MPA  # 690


class TestShearWithMaterialLimits:
    """Tests de integracion: verificacion de cortante con limites de materiales."""

    def setup_method(self):
        self.service = ShearVerificationService()

    def test_fc_alto_se_limita_en_calculo(self):
        """f'c = 100 MPa se limita a 82.7 MPa en calculo de Vn."""
        # Dos calculos: uno con fc=82.7, otro con fc=100
        result_limit = self.service.verify_shear(
            lw=2000, tw=300, hw=3000,
            fc=82.7, fy=420, rho_h=0.0030, Vu=100
        )
        result_high = self.service.verify_shear(
            lw=2000, tw=300, hw=3000,
            fc=100, fy=420, rho_h=0.0030, Vu=100
        )
        # Deben dar el mismo resultado porque fc=100 se limita a 82.7
        assert result_limit.Vn == pytest.approx(result_high.Vn, rel=0.01)

    def test_fyt_alto_se_limita_en_calculo(self):
        """fyt = 550 MPa se limita a 420 MPa en calculo de Vn."""
        result_limit = self.service.verify_shear(
            lw=2000, tw=300, hw=3000,
            fc=35, fy=420, rho_h=0.0030, Vu=100
        )
        result_high = self.service.verify_shear(
            lw=2000, tw=300, hw=3000,
            fc=35, fy=550, rho_h=0.0030, Vu=100
        )
        # Deben dar el mismo resultado porque fy=550 se limita a 420
        assert result_limit.Vn == pytest.approx(result_high.Vn, rel=0.01)

    def test_vn_max_con_alpha_sh(self):
        """Vn_max incluye factor alpha_sh."""
        result = self.service.verify_shear(
            lw=2000, tw=300, hw=3000,
            fc=35, fy=420, rho_h=0.0030, Vu=100
        )
        # alpha_sh debe ser 1.0 para muro rectangular
        assert result.alpha_sh == 1.0

        # Vn_max = alpha_sh * 0.83 * sqrt(fc) * Acv
        Acv = 2000 * 300
        expected_Vn_max = 1.0 * 0.83 * math.sqrt(35) * Acv / N_TO_TONF
        assert result.Vn_max == pytest.approx(expected_Vn_max, rel=0.01)

    def test_shear_result_incluye_alpha_sh(self):
        """ShearResult incluye campo alpha_sh."""
        result = self.service.verify_shear(
            lw=2000, tw=300, hw=3000,
            fc=35, fy=420, rho_h=0.0030, Vu=100
        )
        assert hasattr(result, 'alpha_sh')
        assert 1.0 <= result.alpha_sh <= 1.2


class TestWallGroupWithAlphaSh:
    """Tests para grupos de muros con alpha_sh."""

    def setup_method(self):
        self.service = ShearVerificationService()

    def test_grupo_usa_alpha_sh_por_segmento(self):
        """Limite de grupo usa alpha_sh de cada segmento."""
        segments = [
            (2000, 300, 3000),  # lw, tw, hw
            (1500, 250, 3000),
        ]
        result = self.service.verify_wall_group(
            segments=segments,
            fc=35, fy=420, rho_h=0.0030,
            Vu_total=200
        )
        # Verifica que cada segmento tiene alpha_sh
        for seg_result in result.segments:
            assert hasattr(seg_result, 'alpha_sh')
            assert seg_result.alpha_sh >= ALPHA_SH_MIN
