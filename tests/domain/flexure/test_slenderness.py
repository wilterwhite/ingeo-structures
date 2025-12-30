# tests/domain/flexure/test_slenderness.py
"""
Tests para esbeltez y rigidez efectiva segun ACI 318-25.

Verifica:
- Factor de rigidez 0.35 para muros agrietados
- Calculo de (EI)eff
- Carga critica de pandeo Pc
- Factor de magnificacion de momentos
"""
import pytest
import math

from app.domain.flexure.slenderness import SlendernessService, SlendernessResult
from app.domain.constants.stiffness import (
    WALL_STIFFNESS_FACTOR,
    WALL_UNCRACKED_STIFFNESS_FACTOR,
    COLUMN_STIFFNESS_FACTOR,
)
from app.domain.entities.pier import Pier


@pytest.fixture
def service():
    """Fixture que proporciona una instancia del servicio."""
    return SlendernessService()


@pytest.fixture
def pier_tipico():
    """Pier tipico para tests."""
    return Pier(
        label="P1",
        story="Piso 1",
        width=3000,      # 3m de largo
        thickness=200,   # 20cm de espesor
        height=3000,     # 3m de altura
        fc=28,           # H28
        fy=420,
    )


class TestConstantesRigidez:
    """Tests para las constantes de rigidez ACI 318-25 Tabla 6.6.3.1.1(a)."""

    def test_factor_muros_agrietados(self):
        """Muros agrietados usan 0.35*Ig."""
        assert WALL_STIFFNESS_FACTOR == 0.35

    def test_factor_muros_no_agrietados(self):
        """Muros no agrietados usan 0.70*Ig."""
        assert WALL_UNCRACKED_STIFFNESS_FACTOR == 0.70

    def test_factor_columnas(self):
        """Columnas usan 0.70*Ig."""
        assert COLUMN_STIFFNESS_FACTOR == 0.70


class TestRigidezEfectiva:
    """Tests para calculo de rigidez efectiva (EI)eff."""

    def test_calculo_ei_eff(self, service):
        """Verifica calculo de (EI)eff = 0.35 * Ec * Ig."""
        fc = 28   # MPa
        lw = 3000 # mm
        t = 200   # mm

        result = service.calculate_effective_stiffness(fc, lw, t)

        # Calculo manual
        Ec = 4700 * math.sqrt(fc)  # = 24870 MPa
        Ig = lw * t**3 / 12        # = 2.0e9 mm^4
        EI_eff_esperado = 0.35 * Ec * Ig

        assert result["stiffness_factor"] == 0.35
        assert result["Ec_MPa"] == pytest.approx(Ec, rel=1e-3)
        assert result["Ig_mm4"] == pytest.approx(Ig, rel=1e-3)
        assert result["EI_eff_Nmm2"] == pytest.approx(EI_eff_esperado, rel=1e-3)
        assert result["aci_reference"] == "ACI 318-25 Tabla 6.6.3.1.1(a)"

    def test_ei_eff_aumenta_con_fc(self, service):
        """Mayor f'c produce mayor rigidez."""
        lw = 3000
        t = 200

        result_fc25 = service.calculate_effective_stiffness(25, lw, t)
        result_fc35 = service.calculate_effective_stiffness(35, lw, t)

        assert result_fc35["EI_eff_Nmm2"] > result_fc25["EI_eff_Nmm2"]

    def test_ei_eff_aumenta_con_espesor(self, service):
        """Mayor espesor produce mayor rigidez (cubico)."""
        fc = 28
        lw = 3000

        result_t200 = service.calculate_effective_stiffness(fc, lw, 200)
        result_t300 = service.calculate_effective_stiffness(fc, lw, 300)

        # Ig es proporcional a t^3, entonces relacion debe ser (300/200)^3 = 3.375
        ratio = result_t300["Ig_mm4"] / result_t200["Ig_mm4"]
        assert ratio == pytest.approx(3.375, rel=1e-3)


class TestCargaCriticaPandeo:
    """Tests para carga critica de Euler Pc."""

    def test_pc_usa_factor_035(self, service, pier_tipico):
        """Pc se calcula usando 0.35*Ig."""
        k = 0.8
        Pc = service._calculate_euler_load(pier_tipico, k)

        # Calculo manual
        fc = pier_tipico.fc
        Ec = 4700 * math.sqrt(fc)
        lw = pier_tipico.width
        t = pier_tipico.thickness
        Ig = lw * t**3 / 12
        EI_eff = 0.35 * Ec * Ig  # Factor correcto
        lu = pier_tipico.height
        le = k * lu
        Pc_esperado = (math.pi**2 * EI_eff) / le**2 / 1000  # kN

        assert Pc == pytest.approx(Pc_esperado, rel=1e-3)

    def test_pc_disminuye_con_altura(self, service):
        """Mayor altura (esbeltez) produce menor Pc."""
        pier_corto = Pier(label="P1", story="Piso 1", width=3000, thickness=200, height=2500, fc=28, fy=420)
        pier_alto = Pier(label="P2", story="Piso 1", width=3000, thickness=200, height=4000, fc=28, fy=420)

        Pc_corto = service._calculate_euler_load(pier_corto, k=0.8)
        Pc_alto = service._calculate_euler_load(pier_alto, k=0.8)

        assert Pc_corto > Pc_alto

    def test_pc_aumenta_con_espesor(self, service):
        """Mayor espesor produce mayor Pc."""
        pier_delgado = Pier(label="P1", story="Piso 1", width=3000, thickness=150, height=3000, fc=28, fy=420)
        pier_grueso = Pier(label="P2", story="Piso 1", width=3000, thickness=250, height=3000, fc=28, fy=420)

        Pc_delgado = service._calculate_euler_load(pier_delgado, k=0.8)
        Pc_grueso = service._calculate_euler_load(pier_grueso, k=0.8)

        assert Pc_grueso > Pc_delgado


class TestAnalisisEsbeltez:
    """Tests para analisis completo de esbeltez."""

    def test_muro_corto_no_es_esbelto(self, service):
        """Muro corto (lambda < 22) no es esbelto."""
        # lambda = k*lu/r = 0.8*2000/(300/sqrt(12)) = 18.5 < 22
        pier = Pier(label="P1", story="Piso 1", width=3000, thickness=300, height=2000, fc=28, fy=420)
        result = service.analyze(pier, k=0.8)

        # lambda = 0.8*2000/86.6 = 18.5 < 22
        assert result.lambda_ratio < 22
        assert result.is_slender is False
        assert result.delta_ns == 1.0

    def test_muro_esbelto_magnifica_momentos(self, service, pier_tipico):
        """Muro esbelto (lambda > 22) tiene delta_ns calculado."""
        result = service.analyze(pier_tipico, k=0.8)

        # lambda = 0.8*3000/(200/sqrt(12)) = 41.6 > 22
        assert result.lambda_ratio > 22
        assert result.is_slender is True

    def test_resultado_contiene_referencia_correcta(self, service, pier_tipico):
        """El resultado usa valores ACI 318-25."""
        result = service.analyze(pier_tipico, k=0.8)

        # Verificar que Pc se calculo con el factor correcto
        # recalculando manualmente
        fc = pier_tipico.fc
        Ec = 4700 * math.sqrt(fc)
        lw = pier_tipico.width
        t = pier_tipico.thickness
        Ig = lw * t**3 / 12
        EI_eff = 0.35 * Ec * Ig  # Factor ACI 318-25
        lu = pier_tipico.height
        le = 0.8 * lu
        Pc_esperado = (math.pi**2 * EI_eff) / le**2 / 1000

        assert result.Pc_kN == pytest.approx(Pc_esperado, rel=1e-3)


class TestMagnificacionMomentos:
    """Tests para factor de magnificacion de momentos."""

    def test_delta_sin_carga_axial(self, service):
        """Sin carga axial, delta = 1.0."""
        delta = service._calculate_magnification_factor(Cm=1.0, Pc_kN=1000, Pu_kN=0)
        assert delta == 1.0

    def test_delta_aumenta_con_carga(self, service):
        """Mayor carga axial produce mayor magnificacion."""
        Pc = 1000  # kN

        delta_bajo = service._calculate_magnification_factor(Cm=1.0, Pc_kN=Pc, Pu_kN=100)
        delta_alto = service._calculate_magnification_factor(Cm=1.0, Pc_kN=Pc, Pu_kN=400)

        assert delta_alto > delta_bajo

    def test_delta_infinito_si_pu_excede_pc(self, service):
        """Si Pu >= 0.75*Pc, delta es infinito (inestabilidad)."""
        Pc = 1000  # kN
        Pu = 800   # > 0.75*1000 = 750

        delta = service._calculate_magnification_factor(Cm=1.0, Pc_kN=Pc, Pu_kN=Pu)
        assert delta == float('inf')

    def test_delta_minimo_1(self, service):
        """Delta siempre es >= 1.0."""
        delta = service._calculate_magnification_factor(Cm=0.5, Pc_kN=10000, Pu_kN=100)
        assert delta >= 1.0
