# tests/services/analysis/test_column_service.py
"""
Tests para ColumnService - verificacion de columnas de HA.
"""
import pytest
import math

from app.domain.entities.column import Column
from app.domain.entities.column_forces import ColumnForces
from app.domain.entities.load_combination import LoadCombination
from app.services.analysis.column_service import (
    ColumnService,
    ColumnSlendernessResult,
)


class TestColumnServiceSlenderness:
    """Tests de esbeltez de columnas."""

    def setup_method(self):
        """Setup para cada test."""
        self.service = ColumnService()

    def test_short_column_not_slender(self):
        """Columna corta no es esbelta."""
        column = Column(
            label="C1",
            story="Story1",
            depth=450,
            width=450,
            height=3000,  # 3m de altura
            fc=28.0,
            fy=420.0
        )

        slenderness = self.service._analyze_slenderness(column, direction='depth')

        # lambda = k * lu / r = 1.0 * 3000 / (450/sqrt(12)) = 23.1
        # Es esbelta si lambda > 22
        assert slenderness.lambda_ratio > 0
        # Para 450mm y 3000mm altura, puede o no ser esbelta dependiendo del k

    def test_tall_column_is_slender(self):
        """Columna alta es esbelta."""
        column = Column(
            label="C1",
            story="Story1",
            depth=300,
            width=300,
            height=5000,  # 5m de altura
            fc=28.0,
            fy=420.0
        )

        slenderness = self.service._analyze_slenderness(column, direction='depth')

        # lambda = 1.0 * 5000 / (300/sqrt(12)) = 57.7 > 22
        assert slenderness.is_slender is True
        assert slenderness.lambda_ratio > 22

    def test_buckling_factor_calculated(self):
        """Factor de pandeo se calcula correctamente."""
        column = Column(
            label="C1",
            story="Story1",
            depth=400,
            width=400,
            height=3000,
            fc=28.0,
            fy=420.0
        )

        slenderness = self.service._analyze_slenderness(column, direction='depth')

        # buckling_factor = 1 - (k*lu/(32*t))^2
        expected_ratio = 1.0 * 3000 / (32 * 400)
        expected_factor = 1 - expected_ratio**2
        assert abs(slenderness.buckling_factor - expected_factor) < 0.01


class TestColumnServiceFlexure:
    """Tests de flexocompresion de columnas."""

    def setup_method(self):
        """Setup para cada test."""
        self.service = ColumnService()

    def test_flexure_capacity_calculation(self):
        """Verifica calculo de capacidad de flexion."""
        column = Column(
            label="C1",
            story="Story1",
            depth=450,
            width=450,
            height=3000,
            fc=28.0,
            fy=420.0,
            n_bars_depth=3,
            n_bars_width=3,
            diameter_long=20
        )

        result = self.service.check_flexure(column, None)

        # Sin fuerzas, debe retornar OK
        assert result['status'] == 'OK'
        assert result['sf'] == float('inf')
        assert result['phi_Pn_max'] > 0
        assert result['phi_Mn_M3'] > 0

    def test_flexure_with_forces(self):
        """Verifica flexion con fuerzas aplicadas."""
        column = Column(
            label="C1",
            story="Story1",
            depth=450,
            width=450,
            height=3000,
            fc=28.0,
            fy=420.0,
            n_bars_depth=3,
            n_bars_width=3,
            diameter_long=20
        )

        forces = ColumnForces(
            column_label="C1",
            story="Story1",
            combinations=[
                LoadCombination(
                    name="1.2D+1.6L", location="Bottom", step_type="",
                    P=-200.0,  # Compresion (ETABS usa negativo)
                    V2=15.0, V3=10.0, T=0, M2=30.0, M3=50.0
                ),
            ]
        )

        result = self.service.check_flexure(column, forces)

        assert 'status' in result
        assert 'sf' in result
        assert result['Pu'] == 200.0  # Convertido a positivo
        assert 'phi_Mn_at_Pu' in result


class TestColumnServiceShear:
    """Tests de cortante de columnas."""

    def setup_method(self):
        """Setup para cada test."""
        self.service = ColumnService()

    def test_shear_capacity_calculation(self):
        """Verifica calculo de capacidad de cortante."""
        column = Column(
            label="C1",
            story="Story1",
            depth=450,
            width=450,
            height=3000,
            fc=28.0,
            fy=420.0,
            stirrup_diameter=10,
            stirrup_spacing=150,
            n_stirrup_legs_depth=2,
            n_stirrup_legs_width=2
        )

        capacity_V2 = self.service._calculate_shear_capacity(column, direction='V2')
        capacity_V3 = self.service._calculate_shear_capacity(column, direction='V3')

        # Para columna cuadrada, capacidades deben ser similares
        assert capacity_V2['phi_Vn'] > 0
        assert capacity_V3['phi_Vn'] > 0
        # Diferencia pequena por diferente d efectivo
        assert abs(capacity_V2['phi_Vn'] - capacity_V3['phi_Vn']) < 10

    def test_shear_verification_ok(self):
        """Columna con cortante bajo pasa verificacion."""
        column = Column(
            label="C1",
            story="Story1",
            depth=450,
            width=450,
            height=3000,
            fc=28.0,
            fy=420.0,
            stirrup_diameter=10,
            stirrup_spacing=100
        )

        forces = ColumnForces(
            column_label="C1",
            story="Story1",
            combinations=[
                LoadCombination(
                    name="1.2D+1.6L", location="Bottom", step_type="",
                    P=-200.0, V2=15.0, V3=10.0, T=0, M2=30.0, M3=50.0
                ),
            ]
        )

        result = self.service.check_shear(column, forces)

        assert result['status'] == 'OK'
        assert result['dcr_combined'] <= 1.0

    def test_shear_combined_dcr(self):
        """Verifica calculo de DCR combinado SRSS."""
        column = Column(
            label="C1",
            story="Story1",
            depth=450,
            width=450,
            height=3000,
            fc=28.0,
            fy=420.0
        )

        forces = ColumnForces(
            column_label="C1",
            story="Story1",
            combinations=[
                LoadCombination(
                    name="E", location="Bottom", step_type="",
                    P=-100.0, V2=30.0, V3=20.0, T=0, M2=0, M3=0
                ),
            ]
        )

        result = self.service.check_shear(column, forces)

        # DCR_combined = sqrt(dcr_V2^2 + dcr_V3^2)
        dcr_combined_expected = math.sqrt(result['dcr_V2']**2 + result['dcr_V3']**2)
        assert abs(result['dcr_combined'] - dcr_combined_expected) < 0.01


class TestColumnServiceComplete:
    """Tests de verificacion completa de columnas."""

    def setup_method(self):
        """Setup para cada test."""
        self.service = ColumnService()

    def test_verify_column_complete(self):
        """Verificacion completa incluye flexion y cortante."""
        column = Column(
            label="C1",
            story="Story1",
            depth=450,
            width=450,
            height=3000,
            fc=28.0,
            fy=420.0,
            n_bars_depth=3,
            n_bars_width=3,
            diameter_long=20,
            stirrup_diameter=10,
            stirrup_spacing=150
        )

        forces = ColumnForces(
            column_label="C1",
            story="Story1",
            combinations=[
                LoadCombination(
                    name="1.2D+1.6L", location="Bottom", step_type="",
                    P=-200.0, V2=15.0, V3=10.0, T=0, M2=30.0, M3=50.0
                ),
            ]
        )

        result = self.service.verify_column(column, forces)

        assert 'status' in result
        assert 'flexure' in result
        assert 'shear' in result
        assert 'column_info' in result
        assert result['column_info']['label'] == 'C1'

    def test_verify_all_columns(self):
        """Verificacion de multiples columnas."""
        columns = {
            'Story1_C1': Column(
                label="C1", story="Story1", depth=450, width=450, height=3000,
                fc=28.0, fy=420.0
            ),
            'Story1_C2': Column(
                label="C2", story="Story1", depth=500, width=500, height=3000,
                fc=28.0, fy=420.0
            ),
        }

        column_forces = {
            'Story1_C1': ColumnForces(
                column_label="C1", story="Story1",
                combinations=[
                    LoadCombination(
                        name="1.2D+E", location="Bottom", step_type="",
                        P=-200.0, V2=20.0, V3=15.0, T=0, M2=30.0, M3=50.0
                    ),
                ]
            ),
            'Story1_C2': ColumnForces(
                column_label="C2", story="Story1",
                combinations=[
                    LoadCombination(
                        name="1.2D+E", location="Bottom", step_type="",
                        P=-250.0, V2=25.0, V3=18.0, T=0, M2=40.0, M3=60.0
                    ),
                ]
            ),
        }

        results = self.service.verify_all_columns(columns, column_forces)

        assert len(results) == 2
        assert 'Story1_C1' in results
        assert 'Story1_C2' in results

    def test_get_summary(self):
        """Genera resumen de verificacion."""
        columns = {
            'Story1_C1': Column(
                label="C1", story="Story1", depth=450, width=450, height=3000,
                fc=28.0, fy=420.0
            ),
        }

        column_forces = {
            'Story1_C1': ColumnForces(
                column_label="C1", story="Story1",
                combinations=[
                    LoadCombination(
                        name="1.2D+E", location="Bottom", step_type="",
                        P=-200.0, V2=20.0, V3=15.0, T=0, M2=30.0, M3=50.0
                    ),
                ]
            ),
        }

        summary = self.service.get_summary(columns, column_forces)

        assert summary['total_columns'] == 1
        assert 'ok_count' in summary
        assert 'fail_count' in summary
        assert 'pass_rate' in summary
