# tests/services/analysis/test_force_extractor.py
"""
Tests para ForceExtractor - extraccion unificada de fuerzas.
"""
import pytest
from dataclasses import dataclass
from typing import List, Optional

from app.services.analysis.force_extractor import ForceExtractor, ForceEnvelope


# Mock classes para simular diferentes tipos de Forces
@dataclass
class MockCombination:
    """Combinacion de carga mock."""
    V2: float = 0.0
    V3: float = 0.0
    M2: float = 0.0
    M3: float = 0.0
    P: float = 0.0


@dataclass
class MockForcesWithEnvelope:
    """Forces que tiene metodo get_envelope() (patron preferido)."""

    def get_envelope(self):
        return {
            'V2_max': 15.5,
            'V3_max': 8.2,
            'M2_max': 45.0,
            'M3_max': 120.5,
            'P_max': 250.0,
            'P_min': -50.0,
        }


@dataclass
class MockForcesWithCombinations:
    """Forces que tiene lista de combinaciones."""
    combinations: List[MockCombination]


@dataclass
class MockForcesWithAttributes:
    """Forces con atributos directos."""
    V2: float = 10.0
    V3: float = 5.0
    M2: float = 30.0
    M3: float = 80.0
    P: float = 100.0


class TestForceEnvelope:
    """Tests para la dataclass ForceEnvelope."""

    def test_default_values(self):
        """Valores por defecto son cero."""
        envelope = ForceEnvelope()
        assert envelope.V2_max == 0.0
        assert envelope.V3_max == 0.0
        assert envelope.M2_max == 0.0
        assert envelope.M3_max == 0.0
        assert envelope.P_max == 0.0
        assert envelope.P_min == 0.0

    def test_to_dict(self):
        """Conversion a diccionario."""
        envelope = ForceEnvelope(
            V2_max=10.0,
            V3_max=5.0,
            M2_max=30.0,
            M3_max=80.0,
            P_max=200.0,
            P_min=-50.0,
        )
        d = envelope.to_dict()

        assert d['V2_max'] == 10.0
        assert d['V3_max'] == 5.0
        assert d['M2_max'] == 30.0
        assert d['M3_max'] == 80.0
        assert d['P_max'] == 200.0
        assert d['P_min'] == -50.0


class TestExtractEnvelope:
    """Tests para extract_envelope()."""

    def test_none_forces_returns_zero_envelope(self):
        """Forces None retorna envolvente con ceros."""
        envelope = ForceExtractor.extract_envelope(None)
        assert envelope.V2_max == 0.0
        assert envelope.P_max == 0.0

    def test_pattern_1_get_envelope(self):
        """Patron 1: Usa get_envelope() si esta disponible."""
        forces = MockForcesWithEnvelope()
        envelope = ForceExtractor.extract_envelope(forces)

        assert envelope.V2_max == 15.5
        assert envelope.V3_max == 8.2
        assert envelope.M2_max == 45.0
        assert envelope.M3_max == 120.5
        assert envelope.P_max == 250.0
        assert envelope.P_min == -50.0

    def test_pattern_2_combinations(self):
        """Patron 2: Itera sobre combinaciones."""
        combinations = [
            MockCombination(V2=10, V3=-5, M2=20, M3=50, P=100),
            MockCombination(V2=-15, V3=8, M2=-30, M3=-80, P=-40),  # V2 max aqui
            MockCombination(V2=5, V3=3, M2=25, M3=60, P=150),  # P max aqui
        ]
        forces = MockForcesWithCombinations(combinations=combinations)
        envelope = ForceExtractor.extract_envelope(forces)

        assert envelope.V2_max == 15.0  # abs(-15)
        assert envelope.V3_max == 8.0
        assert envelope.M2_max == 30.0  # abs(-30)
        assert envelope.M3_max == 80.0  # abs(-80)
        assert envelope.P_max == 150.0
        assert envelope.P_min == -40.0

    def test_pattern_3_direct_attributes(self):
        """Patron 3: Atributos directos."""
        forces = MockForcesWithAttributes(V2=-12.0, V3=7.0, M2=35.0, M3=-90.0, P=120.0)
        envelope = ForceExtractor.extract_envelope(forces)

        assert envelope.V2_max == 12.0  # abs(-12)
        assert envelope.V3_max == 7.0
        assert envelope.M2_max == 35.0
        assert envelope.M3_max == 90.0  # abs(-90)
        assert envelope.P_max == 120.0
        assert envelope.P_min == 120.0  # Mismo valor para atributos directos

    def test_empty_combinations(self):
        """Lista de combinaciones vacia usa atributos directos."""
        forces = MockForcesWithCombinations(combinations=[])
        # Deberia caer al patron 3 (atributos directos)
        envelope = ForceExtractor.extract_envelope(forces)
        # Sin atributos, retorna ceros
        assert envelope.V2_max == 0.0


class TestExtractCriticalShear:
    """Tests para extract_critical_shear()."""

    def test_v2_axis(self):
        """Extrae cortante V2."""
        forces = MockForcesWithEnvelope()
        v2 = ForceExtractor.extract_critical_shear(forces, axis='V2')
        assert v2 == 15.5

    def test_v3_axis(self):
        """Extrae cortante V3."""
        forces = MockForcesWithEnvelope()
        v3 = ForceExtractor.extract_critical_shear(forces, axis='V3')
        assert v3 == 8.2

    def test_default_axis_is_v2(self):
        """Eje por defecto es V2."""
        forces = MockForcesWithEnvelope()
        v = ForceExtractor.extract_critical_shear(forces)
        assert v == 15.5

    def test_none_forces(self):
        """Forces None retorna cero."""
        v = ForceExtractor.extract_critical_shear(None)
        assert v == 0.0


class TestExtractCriticalMoment:
    """Tests para extract_critical_moment()."""

    def test_m3_axis(self):
        """Extrae momento M3."""
        forces = MockForcesWithEnvelope()
        m3 = ForceExtractor.extract_critical_moment(forces, axis='M3')
        assert m3 == 120.5

    def test_m2_axis(self):
        """Extrae momento M2."""
        forces = MockForcesWithEnvelope()
        m2 = ForceExtractor.extract_critical_moment(forces, axis='M2')
        assert m2 == 45.0

    def test_default_axis_is_m3(self):
        """Eje por defecto es M3."""
        forces = MockForcesWithEnvelope()
        m = ForceExtractor.extract_critical_moment(forces)
        assert m == 120.5


class TestExtractCriticalAxial:
    """Tests para extract_critical_axial()."""

    def test_returns_tuple(self):
        """Retorna tupla (P_max, P_min)."""
        forces = MockForcesWithEnvelope()
        p_max, p_min = ForceExtractor.extract_critical_axial(forces)

        assert p_max == 250.0  # Compresion
        assert p_min == -50.0  # Traccion

    def test_none_forces(self):
        """Forces None retorna (0, 0)."""
        p_max, p_min = ForceExtractor.extract_critical_axial(None)
        assert p_max == 0.0
        assert p_min == 0.0


class TestExtractCombinedShear:
    """Tests para extract_combined_shear() - SRSS."""

    def test_srss_calculation(self):
        """Calcula SRSS correctamente."""
        forces = MockForcesWithEnvelope()
        # V2=15.5, V3=8.2
        # SRSS = sqrt(15.5^2 + 8.2^2) = sqrt(240.25 + 67.24) = sqrt(307.49) = 17.535
        v_combined = ForceExtractor.extract_combined_shear(forces)
        assert abs(v_combined - 17.535) < 0.01

    def test_none_forces(self):
        """Forces None retorna cero."""
        v = ForceExtractor.extract_combined_shear(None)
        assert v == 0.0


class TestHasSignificantAxial:
    """Tests para has_significant_axial() - ACI 318-25 18.6.4.6."""

    def test_significant_axial_compression(self):
        """Detecta carga axial significativa (compresion)."""
        # P_max = 250 tonf (de MockForcesWithEnvelope)
        # Ag = 400000 mm2 (ej: 500x800)
        # fc = 30 MPa
        # Umbral = 400000 * 30 / 10 / 1000 / 9.80665 = 122.4 tonf
        # 250 >= 122.4 -> True
        forces = MockForcesWithEnvelope()
        result = ForceExtractor.has_significant_axial(
            forces, Ag=400000, fc=30, divisor=10.0
        )
        assert result is True

    def test_insignificant_axial(self):
        """Detecta carga axial NO significativa."""
        # P_max = 50 tonf (pequeno)
        @dataclass
        class SmallAxialForces:
            def get_envelope(self):
                return {'V2_max': 10, 'V3_max': 5, 'M2_max': 20, 'M3_max': 50,
                        'P_max': 50, 'P_min': -20}

        forces = SmallAxialForces()
        # Umbral = 400000 * 30 / 10 / 1000 / 9.80665 = 122.4 tonf
        # 50 < 122.4 -> False
        result = ForceExtractor.has_significant_axial(
            forces, Ag=400000, fc=30, divisor=10.0
        )
        assert result is False

    def test_tension_considered(self):
        """La traccion tambien se considera."""
        @dataclass
        class TensionForces:
            def get_envelope(self):
                return {'V2_max': 10, 'V3_max': 5, 'M2_max': 20, 'M3_max': 50,
                        'P_max': 50, 'P_min': -200}  # Gran traccion

        forces = TensionForces()
        # Pu_max = max(50, 200) = 200 tonf
        # Umbral = 122.4 tonf
        # 200 >= 122.4 -> True
        result = ForceExtractor.has_significant_axial(
            forces, Ag=400000, fc=30, divisor=10.0
        )
        assert result is True

    def test_invalid_geometry(self):
        """Geometria invalida retorna False."""
        forces = MockForcesWithEnvelope()
        assert ForceExtractor.has_significant_axial(forces, Ag=0, fc=30) is False
        assert ForceExtractor.has_significant_axial(forces, Ag=400000, fc=0) is False

    def test_none_forces(self):
        """Forces None retorna False."""
        result = ForceExtractor.has_significant_axial(None, Ag=400000, fc=30)
        assert result is False


class TestCombinationsEdgeCases:
    """Tests para casos borde en extraccion de combinaciones."""

    def test_all_negative_shear(self):
        """Maneja cortantes todos negativos correctamente."""
        combinations = [
            MockCombination(V2=-10, V3=-5),
            MockCombination(V2=-20, V3=-8),
            MockCombination(V2=-5, V3=-15),
        ]
        forces = MockForcesWithCombinations(combinations=combinations)
        envelope = ForceExtractor.extract_envelope(forces)

        # Debe tomar valores absolutos
        assert envelope.V2_max == 20.0
        assert envelope.V3_max == 15.0

    def test_single_combination(self):
        """Maneja una sola combinacion."""
        combinations = [MockCombination(V2=10, V3=5, M2=20, M3=50, P=100)]
        forces = MockForcesWithCombinations(combinations=combinations)
        envelope = ForceExtractor.extract_envelope(forces)

        assert envelope.V2_max == 10.0
        assert envelope.P_max == 100.0
        assert envelope.P_min == 0.0  # No hay valores negativos

    def test_missing_attributes_in_combination(self):
        """Maneja combinaciones con atributos faltantes."""
        @dataclass
        class PartialCombination:
            V2: float = 0.0
            # Sin V3, M2, M3, P

        combinations = [PartialCombination(V2=15)]
        forces = MockForcesWithCombinations(combinations=combinations)
        envelope = ForceExtractor.extract_envelope(forces)

        assert envelope.V2_max == 15.0
        assert envelope.V3_max == 0.0  # getattr retorna 0 por defecto
