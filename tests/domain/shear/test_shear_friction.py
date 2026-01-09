# tests/domain/shear/test_shear_friction.py
"""
Tests para friccion por cortante segun ACI 318-25 Seccion 22.9.

Casos de prueba basados en ejemplos del codigo y calculos manuales.
"""
import pytest
import math

from app.domain.shear import (
    ShearFrictionService,
    ShearFrictionResult,
    ShearFrictionDesignResult,
    SurfaceCondition,
)
from app.domain.constants.shear import (
    SHEAR_FRICTION_MU,
    PHI_SHEAR_FRICTION,
)
from app.domain.constants.units import N_TO_TONF


@pytest.fixture
def service():
    """Fixture que proporciona una instancia del servicio."""
    return ShearFrictionService()


class TestCoeficientesFriccion:
    """Tests para los coeficientes de friccion (Tabla 22.9.4.2)."""

    def test_mu_monolitico(self, service):
        """mu = 1.4*lambda para concreto monolitico."""
        mu = service.get_mu(SurfaceCondition.MONOLITHIC, lambda_concrete=1.0)
        assert mu == pytest.approx(1.4, rel=1e-3)

    def test_mu_rugoso(self, service):
        """mu = 1.0*lambda para superficie rugosa (~6mm)."""
        mu = service.get_mu(SurfaceCondition.ROUGHENED, lambda_concrete=1.0)
        assert mu == pytest.approx(1.0, rel=1e-3)

    def test_mu_no_rugoso(self, service):
        """mu = 0.6 para superficie no rugosa (sin lambda)."""
        mu = service.get_mu(SurfaceCondition.NOT_ROUGHENED, lambda_concrete=1.0)
        assert mu == pytest.approx(0.6, rel=1e-3)

    def test_mu_acero(self, service):
        """mu = 0.7*lambda para concreto contra acero."""
        mu = service.get_mu(SurfaceCondition.STEEL, lambda_concrete=1.0)
        assert mu == pytest.approx(0.7, rel=1e-3)

    def test_mu_concreto_liviano(self, service):
        """Verificar que lambda se aplica correctamente."""
        lambda_lw = 0.75  # Concreto liviano
        mu = service.get_mu(SurfaceCondition.ROUGHENED, lambda_concrete=lambda_lw)
        assert mu == pytest.approx(1.0 * 0.75, rel=1e-3)

    def test_mu_no_rugoso_ignora_lambda(self, service):
        """ACI 318-25: lambda no aplica a superficie no rugosa."""
        mu_normal = service.get_mu(SurfaceCondition.NOT_ROUGHENED, lambda_concrete=1.0)
        mu_liviano = service.get_mu(SurfaceCondition.NOT_ROUGHENED, lambda_concrete=0.75)
        assert mu_normal == mu_liviano == 0.6


class TestCalculoVnMax:
    """Tests para limites maximos de Vn (Tabla 22.9.4.4)."""

    def test_vn_max_monolitico(self, service):
        """Limite para superficie monolitica: min(0.2*fc*Ac, (3.3+0.08fc)*Ac, 11*Ac)."""
        fc = 28  # MPa
        Ac = 300 * 1000  # 300mm x 1000mm = 300,000 mm2

        Vn_max = service.calculate_Vn_max(fc, Ac, SurfaceCondition.MONOLITHIC)

        # Calculos manuales
        limit_1 = 0.2 * fc * Ac                    # = 1,680,000 N
        limit_2 = (3.3 + 0.08 * fc) * Ac           # = (3.3 + 2.24) * Ac = 1,662,000 N
        limit_3 = 11.0 * Ac                        # = 3,300,000 N
        expected = min(limit_1, limit_2, limit_3)  # = 1,662,000 N

        assert Vn_max == pytest.approx(expected, rel=1e-3)

    def test_vn_max_no_rugoso(self, service):
        """Limite para superficie no rugosa: min(0.2*fc*Ac, 5.5*Ac)."""
        fc = 28  # MPa
        Ac = 300 * 1000  # mm2

        Vn_max = service.calculate_Vn_max(fc, Ac, SurfaceCondition.NOT_ROUGHENED)

        limit_1 = 0.2 * fc * Ac  # = 1,680,000 N
        limit_2 = 5.5 * Ac       # = 1,650,000 N
        expected = min(limit_1, limit_2)

        assert Vn_max == pytest.approx(expected, rel=1e-3)


class TestCalculoVnPerpendicular:
    """Tests para Vn con refuerzo perpendicular (Ec. 22.9.4.2)."""

    def test_vn_basico(self, service):
        """Vn = mu * Avf * fy para caso sin carga axial."""
        Avf = 4 * 113  # 4 barras #12 = 452 mm2
        fy = 420       # MPa
        mu = 1.0       # Superficie rugosa

        Vn = service.calculate_Vn_perpendicular(Avf, fy, mu, Nu=0)

        expected = mu * Avf * fy  # = 1.0 * 452 * 420 = 189,840 N
        assert Vn == pytest.approx(expected, rel=1e-3)

    def test_vn_con_compresion_axial(self, service):
        """Vn = mu * (Avf*fy + Nu) con compresion axial."""
        Avf = 452      # mm2
        fy = 420       # MPa
        mu = 1.0
        Nu = 100_000   # N (compresion)

        Vn = service.calculate_Vn_perpendicular(Avf, fy, mu, Nu)

        expected = mu * (Avf * fy + Nu)  # = 1.0 * (189,840 + 100,000) = 289,840 N
        assert Vn == pytest.approx(expected, rel=1e-3)

    def test_fy_limitado_420mpa(self, service):
        """fy se limita a 420 MPa segun 22.9.1.3."""
        Avf = 452
        fy = 500  # > 420 MPa
        mu = 1.0

        Vn = service.calculate_Vn_perpendicular(Avf, fy, mu, Nu=0)

        # Debe usar fy = 420, no 500
        expected = mu * Avf * 420
        assert Vn == pytest.approx(expected, rel=1e-3)


class TestCalculoVnInclinado:
    """Tests para Vn con refuerzo inclinado (Ec. 22.9.4.3)."""

    def test_refuerzo_45_grados(self, service):
        """Vn con refuerzo a 45 grados."""
        Avf = 452
        fy = 420
        mu = 1.0
        alpha = 45  # grados

        Vn = service.calculate_Vn_inclined(Avf, fy, mu, alpha, Nu=0)

        # Vn = Avf * fy * (mu*sin(45) + cos(45))
        # = 452 * 420 * (1.0*0.707 + 0.707) = 452 * 420 * 1.414
        expected = Avf * fy * (mu * math.sin(math.radians(45)) + math.cos(math.radians(45)))
        assert Vn == pytest.approx(expected, rel=1e-3)

    def test_refuerzo_90_grados_igual_perpendicular(self, service):
        """Refuerzo a 90 grados debe dar mismo resultado que perpendicular."""
        Avf = 452
        fy = 420
        mu = 1.0

        Vn_inclined = service.calculate_Vn_inclined(Avf, fy, mu, alpha_deg=90, Nu=0)
        Vn_perp = service.calculate_Vn_perpendicular(Avf, fy, mu, Nu=0)

        # sin(90) = 1, cos(90) = 0, entonces: Vn = Avf*fy*mu = mismo que perpendicular
        assert Vn_inclined == pytest.approx(Vn_perp, rel=1e-3)


class TestVerificacionFriccion:
    """Tests para verificacion completa de friccion por cortante."""

    def test_verificacion_ok(self, service):
        """Verificacion que cumple (sf >= 1.0)."""
        result = service.verify_shear_friction(
            Ac=300 * 1000,        # 300mm x 1000mm
            Avf=4 * 113,          # 4 #12
            fc=28,
            fy=420,
            Vu=10,                # tonf - demanda baja
            surface=SurfaceCondition.ROUGHENED
        )

        assert result.status == "OK"
        assert result.sf >= 1.0
        assert result.mu == 1.0
        assert result.aci_reference == "ACI 318-25 Ec. 22.9.4.2, Tabla 22.9.4.4"

    def test_verificacion_no_ok(self, service):
        """Verificacion que no cumple (sf < 1.0)."""
        result = service.verify_shear_friction(
            Ac=300 * 1000,
            Avf=2 * 113,          # Solo 2 barras - insuficiente
            fc=28,
            fy=420,
            Vu=50,                # tonf - demanda alta
            surface=SurfaceCondition.ROUGHENED
        )

        assert result.status == "NO OK"
        assert result.sf < 1.0

    def test_limite_vn_max_controla(self, service):
        """Verificar que Vn_max limita la capacidad."""
        # Mucho refuerzo para forzar que Vn_max controle
        result = service.verify_shear_friction(
            Ac=200 * 200,         # Area pequena
            Avf=20 * 200,         # Mucho refuerzo
            fc=28,
            fy=420,
            Vu=10,
            surface=SurfaceCondition.NOT_ROUGHENED  # Limite mas restrictivo
        )

        assert result.controls_max_limit is True
        assert result.Vn_effective == result.Vn_max


class TestDisenoFriccion:
    """Tests para diseno de refuerzo de friccion."""

    def test_diseno_basico(self, service):
        """Calculo de Avf requerido."""
        result = service.design_shear_friction(
            Ac=300 * 1000,
            fc=28,
            fy=420,
            Vu=20,  # tonf
            surface=SurfaceCondition.ROUGHENED,
            length=1000  # mm - para calcular Avf/m
        )

        assert result.Avf_required > 0
        assert result.Avf_per_meter > 0
        assert result.is_feasible is True

    def test_diseno_con_compresion(self, service):
        """Compresion axial reduce refuerzo requerido."""
        result_sin_Nu = service.design_shear_friction(
            Ac=300 * 1000,
            fc=28,
            fy=420,
            Vu=20,
            Nu=0,
            surface=SurfaceCondition.ROUGHENED
        )

        result_con_Nu = service.design_shear_friction(
            Ac=300 * 1000,
            fc=28,
            fy=420,
            Vu=20,
            Nu=10,  # 10 tonf de compresion
            surface=SurfaceCondition.ROUGHENED
        )

        # Con compresion deberia requerir menos refuerzo
        assert result_con_Nu.Avf_required < result_sin_Nu.Avf_required

    def test_diseno_no_factible(self, service):
        """Demanda excede capacidad maxima."""
        result = service.design_shear_friction(
            Ac=100 * 100,         # Area muy pequena
            fc=28,
            fy=420,
            Vu=100,               # Demanda muy alta
            surface=SurfaceCondition.NOT_ROUGHENED
        )

        assert result.is_feasible is False


class TestJuntaConstruccion:
    """Tests para junta de construccion en muros."""

    def test_junta_tipica(self, service):
        """Verificacion de junta horizontal tipica en muro."""
        result = service.verify_construction_joint(
            lw=3000,              # 3m de largo
            tw=300,               # 30cm de espesor
            fc=28,
            fy=420,
            Vu=50,                # tonf
            rho_v=0.0025,         # Cuantia minima
            Nu=20,                # Compresion
            surface=SurfaceCondition.ROUGHENED
        )

        # El area de contacto es lw * tw
        assert result.Ac == 3000 * 300

        # Avf = rho_v * Ac
        expected_Avf = 0.0025 * 3000 * 300
        assert result.Avf == pytest.approx(expected_Avf, rel=1e-3)


class TestUnidades:
    """Tests para verificar conversiones de unidades."""

    def test_salida_en_tonf(self, service):
        """Verificar que la salida esta en tonf."""
        result = service.verify_shear_friction(
            Ac=300 * 1000,
            Avf=4 * 113,
            fc=28,
            fy=420,
            Vu=10,
            surface=SurfaceCondition.ROUGHENED
        )

        # Calcular Vn esperado en N
        Vn_N = 1.0 * 4 * 113 * 420  # = 189,840 N

        # Verificar conversion a tonf
        Vn_tonf = Vn_N / N_TO_TONF
        assert result.Vn == pytest.approx(Vn_tonf, rel=1e-3)


class TestCasosEspeciales:
    """Tests para casos especiales y edge cases."""

    def test_vu_cero(self, service):
        """Vu = 0 debe dar sf = infinito."""
        result = service.verify_shear_friction(
            Ac=300 * 1000,
            Avf=4 * 113,
            fc=28,
            fy=420,
            Vu=0,
            surface=SurfaceCondition.ROUGHENED
        )

        assert result.sf == float('inf')
        assert result.status == "OK"

    def test_vu_negativo_usa_absoluto(self, service):
        """Vu negativo debe usar valor absoluto."""
        result_pos = service.verify_shear_friction(
            Ac=300 * 1000,
            Avf=4 * 113,
            fc=28,
            fy=420,
            Vu=10,
            surface=SurfaceCondition.ROUGHENED
        )

        result_neg = service.verify_shear_friction(
            Ac=300 * 1000,
            Avf=4 * 113,
            fc=28,
            fy=420,
            Vu=-10,
            surface=SurfaceCondition.ROUGHENED
        )

        assert result_pos.sf == result_neg.sf
        assert result_pos.Vu == result_neg.Vu == 10
