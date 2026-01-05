# tests/services/analysis/test_beam_service.py
"""
Tests para BeamService - verificacion de cortante en vigas.
"""
import pytest
import math

from app.domain.entities.beam import Beam, BeamSource
from app.domain.entities.beam_forces import BeamForces
from app.domain.entities.load_combination import LoadCombination
from app.services.analysis.beam_service import BeamService, BeamShearResult


class TestBeamServiceBasics:
    """Tests basicos del servicio de vigas."""

    def setup_method(self):
        """Setup para cada test."""
        self.service = BeamService()

    def test_shear_capacity_calculation(self):
        """Verifica calculo de capacidad de cortante."""
        # Viga tipica: 300x600mm, f'c=28MPa
        beam = Beam(
            label="B1",
            story="Story1",
            length=5000,
            depth=600,
            width=300,
            fc=28.0,
            fy=420.0,
            stirrup_diameter=10,
            stirrup_spacing=150,
            n_stirrup_legs=2,
            cover=40.0
        )

        capacity = self.service.get_shear_capacity(beam)

        # Verificar que se calcularon las capacidades
        assert capacity['Vc'] > 0
        assert capacity['Vs'] > 0
        assert capacity['phi_Vn'] > 0
        assert capacity['d'] == 560  # 600 - 40
        assert capacity['bw'] == 300

    def test_shear_capacity_formula(self):
        """Verifica formulas de cortante ACI 318-25 §22.5."""
        beam = Beam(
            label="B1",
            story="Story1",
            length=5000,
            depth=600,
            width=300,
            fc=28.0,
            fy=420.0,
            stirrup_diameter=10,
            stirrup_spacing=150,
            n_stirrup_legs=2,
            cover=40.0
        )

        d = beam.d  # 560mm
        bw = beam.bw  # 300mm
        fc = beam.fc  # 28 MPa

        # Vc = 0.17 * lambda * sqrt(f'c) * bw * d
        # lambda = 1.0 para concreto normal
        Vc_expected = 0.17 * 1.0 * math.sqrt(fc) * bw * d  # en N
        Vc_expected_tonf = Vc_expected / 9806.65

        capacity = self.service.get_shear_capacity(beam)
        assert abs(capacity['Vc'] - Vc_expected_tonf) < 0.5

    def test_shear_verification_ok(self):
        """Verifica que una viga con refuerzo adecuado pasa la verificacion."""
        beam = Beam(
            label="B1",
            story="Story1",
            length=5000,
            depth=600,
            width=300,
            fc=28.0,
            fy=420.0,
            stirrup_diameter=10,
            stirrup_spacing=100,  # Espaciamiento cerrado
            n_stirrup_legs=2,
            cover=40.0
        )

        forces = BeamForces(
            beam_label="B1",
            story="Story1",
            combinations=[
                LoadCombination(name="1.2D+1.6L", location="End", step_type="", P=0, V2=15.0, V3=0, T=0, M2=0, M3=50.0),
                LoadCombination(name="1.2D+E", location="End", step_type="", P=0, V2=20.0, V3=0, T=0, M2=0, M3=80.0),
            ]
        )

        result = self.service.check_shear(beam, forces)

        assert result['status'] == 'OK'
        assert result['sf'] >= 1.0
        assert result['Vu'] == 20.0  # Cortante maximo
        assert result['critical_combo'] == '1.2D+E'

    def test_shear_verification_fail(self):
        """Verifica que una viga con cortante excesivo falla."""
        beam = Beam(
            label="B1",
            story="Story1",
            length=5000,
            depth=400,  # Viga mas pequena
            width=250,
            fc=21.0,   # Concreto mas debil
            fy=420.0,
            stirrup_diameter=8,
            stirrup_spacing=250,  # Espaciamiento amplio
            n_stirrup_legs=2,
            cover=40.0
        )

        forces = BeamForces(
            beam_label="B1",
            story="Story1",
            combinations=[
                LoadCombination(name="1.2D+1.6L", location="End", step_type="", P=0, V2=50.0, V3=0, T=0, M2=0, M3=100.0),
            ]
        )

        result = self.service.check_shear(beam, forces)

        assert result['status'] == 'NO OK'
        assert result['sf'] < 1.0
        assert result['dcr'] > 1.0

    def test_no_forces(self):
        """Verifica resultado cuando no hay fuerzas."""
        beam = Beam(
            label="B1",
            story="Story1",
            length=5000,
            depth=600,
            width=300,
            fc=28.0,
            fy=420.0
        )

        result = self.service.check_shear(beam, None)

        assert result['status'] == 'OK'
        assert result['sf'] == '>100'
        assert result['critical_combo'] == 'N/A'

    def test_empty_combinations(self):
        """Verifica resultado cuando las combinaciones estan vacias."""
        beam = Beam(
            label="B1",
            story="Story1",
            length=5000,
            depth=600,
            width=300,
            fc=28.0,
            fy=420.0
        )

        forces = BeamForces(
            beam_label="B1",
            story="Story1",
            combinations=[]
        )

        result = self.service.check_shear(beam, forces)

        assert result['status'] == 'OK'
        assert result['sf'] == '>100'


class TestBeamServiceSpandrels:
    """Tests para spandrels (vigas de acople)."""

    def setup_method(self):
        """Setup para cada test."""
        self.service = BeamService()

    def test_spandrel_shear(self):
        """Verifica cortante en spandrel."""
        spandrel = Beam(
            label="S1",
            story="Story1",
            length=1200,  # Claro corto tipico de spandrel
            depth=800,
            width=200,    # Espesor del muro
            fc=28.0,
            fy=420.0,
            source=BeamSource.SPANDREL,
            stirrup_diameter=10,
            stirrup_spacing=100,
            n_stirrup_legs=2
        )

        forces = BeamForces(
            beam_label="S1",
            story="Story1",
            combinations=[
                LoadCombination(name="1.2D+E", location="End", step_type="", P=0, V2=35.0, V3=0, T=0, M2=0, M3=100.0),
            ]
        )

        result = self.service.check_shear(spandrel, forces)

        assert 'phi_Vn' in result
        assert result['Vu'] == 35.0
        assert spandrel.is_spandrel is True


class TestBeamServiceMultiple:
    """Tests para verificacion de multiples vigas."""

    def setup_method(self):
        """Setup para cada test."""
        self.service = BeamService()

    def test_verify_all_beams(self):
        """Verifica multiples vigas a la vez."""
        beams = {
            'Story1_B1': Beam(
                label="B1", story="Story1", length=5000, depth=600, width=300,
                fc=28.0, fy=420.0, stirrup_spacing=150
            ),
            'Story1_B2': Beam(
                label="B2", story="Story1", length=6000, depth=700, width=350,
                fc=28.0, fy=420.0, stirrup_spacing=150
            ),
        }

        beam_forces = {
            'Story1_B1': BeamForces(
                beam_label="B1", story="Story1",
                combinations=[
                    LoadCombination(name="1.2D+E", location="End", step_type="", P=0, V2=20.0, V3=0, T=0, M2=0, M3=50.0),
                ]
            ),
            'Story1_B2': BeamForces(
                beam_label="B2", story="Story1",
                combinations=[
                    LoadCombination(name="1.2D+E", location="End", step_type="", P=0, V2=25.0, V3=0, T=0, M2=0, M3=70.0),
                ]
            ),
        }

        results = self.service.verify_all_beams(beams, beam_forces)

        assert len(results) == 2
        assert 'Story1_B1' in results
        assert 'Story1_B2' in results

    def test_get_summary(self):
        """Verifica resumen de verificacion."""
        beams = {
            'Story1_B1': Beam(
                label="B1", story="Story1", length=5000, depth=600, width=300,
                fc=28.0, fy=420.0, stirrup_spacing=100
            ),
            'Story1_B2': Beam(
                label="B2", story="Story1", length=5000, depth=400, width=250,
                fc=21.0, fy=420.0, stirrup_spacing=250
            ),
        }

        beam_forces = {
            'Story1_B1': BeamForces(
                beam_label="B1", story="Story1",
                combinations=[
                    LoadCombination(name="1.2D+E", location="End", step_type="", P=0, V2=15.0, V3=0, T=0, M2=0, M3=50.0),
                ]
            ),
            'Story1_B2': BeamForces(
                beam_label="B2", story="Story1",
                combinations=[
                    LoadCombination(name="1.2D+E", location="End", step_type="", P=0, V2=60.0, V3=0, T=0, M2=0, M3=100.0),
                ]
            ),
        }

        summary = self.service.get_summary(beams, beam_forces)

        assert summary['total_beams'] == 2
        assert summary['ok_count'] >= 0
        assert summary['fail_count'] >= 0
        assert summary['ok_count'] + summary['fail_count'] == 2
        assert 'min_sf' in summary
        assert 'critical_beam' in summary


class TestBeamShearResult:
    """Tests para el dataclass BeamShearResult."""

    def setup_method(self):
        """Setup para cada test."""
        self.service = BeamService()

    def test_verify_beam_returns_result(self):
        """Verifica que verify_beam retorna BeamShearResult."""
        beam = Beam(
            label="B1",
            story="Story1",
            length=5000,
            depth=600,
            width=300,
            fc=28.0,
            fy=420.0
        )

        forces = BeamForces(
            beam_label="B1",
            story="Story1",
            combinations=[
                LoadCombination(name="1.2D+E", location="End", step_type="", P=0, V2=20.0, V3=0, T=0, M2=0, M3=80.0),
            ]
        )

        result = self.service.verify_beam(beam, forces)

        assert isinstance(result, BeamShearResult)
        assert result.Vc > 0
        assert result.Vs >= 0
        assert result.phi_Vn > 0
        assert result.Vu == 20.0
        assert result.aci_reference == 'ACI 318-25 22.5'
