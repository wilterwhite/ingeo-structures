# tests/test_ductile_coupled_walls.py
"""
Tests para verificación de muros acoplados dúctiles según ACI 318-25 §18.10.9.
"""
import pytest
from app.domain.chapter18.coupled_walls import (
    DuctileCoupledWallService,
    DuctileCoupledWallResult,
    WallGeometryCheck,
    CouplingBeamGeometryCheck,
    LevelComplianceResult,
)


class TestWallGeometryCheck:
    """Tests para verificación de geometría de muros §18.10.9.1."""

    def test_wall_meets_hwcs_lw_minimum(self):
        """Muro con hwcs/lw >= 2.0 cumple."""
        service = DuctileCoupledWallService()
        result = service.verify_wall_geometry(
            wall_id="W1",
            hwcs=15000,  # 15m altura
            lw=6000,     # 6m longitud
        )
        # hwcs/lw = 15000/6000 = 2.5 >= 2.0
        assert result.hwcs_lw == 2.5
        assert result.is_ok is True

    def test_wall_fails_hwcs_lw_minimum(self):
        """Muro con hwcs/lw < 2.0 no cumple."""
        service = DuctileCoupledWallService()
        result = service.verify_wall_geometry(
            wall_id="W2",
            hwcs=8000,   # 8m altura
            lw=6000,     # 6m longitud
        )
        # hwcs/lw = 8000/6000 = 1.33 < 2.0
        assert result.hwcs_lw == 1.33
        assert result.is_ok is False

    def test_wall_exactly_at_limit(self):
        """Muro con hwcs/lw = 2.0 exactamente cumple."""
        service = DuctileCoupledWallService()
        result = service.verify_wall_geometry(
            wall_id="W3",
            hwcs=12000,
            lw=6000,
        )
        # hwcs/lw = 12000/6000 = 2.0
        assert result.hwcs_lw == 2.0
        assert result.is_ok is True


class TestCouplingBeamGeometryCheck:
    """Tests para verificación de geometría de vigas §18.10.9.2-3."""

    def test_beam_meets_both_limits(self):
        """Viga con 2 <= ln/h <= 5 cumple ambos criterios."""
        service = DuctileCoupledWallService()
        result = service.verify_beam_geometry(
            beam_id="CB1",
            level=1,
            ln=2400,  # 2.4m claro
            h=800,    # 0.8m peralte
        )
        # ln/h = 2400/800 = 3.0
        assert result.ln_h == 3.0
        assert result.meets_min_ratio is True   # >= 2.0
        assert result.meets_max_ratio is True   # <= 5.0

    def test_beam_fails_minimum(self):
        """Viga con ln/h < 2 no cumple mínimo."""
        service = DuctileCoupledWallService()
        result = service.verify_beam_geometry(
            beam_id="CB2",
            level=1,
            ln=1200,  # 1.2m claro
            h=800,    # 0.8m peralte
        )
        # ln/h = 1200/800 = 1.5 < 2.0
        assert result.ln_h == 1.5
        assert result.meets_min_ratio is False
        assert result.meets_max_ratio is True

    def test_beam_exceeds_maximum(self):
        """Viga con ln/h > 5 cumple mínimo pero excede máximo."""
        service = DuctileCoupledWallService()
        result = service.verify_beam_geometry(
            beam_id="CB3",
            level=1,
            ln=4800,  # 4.8m claro
            h=800,    # 0.8m peralte
        )
        # ln/h = 4800/800 = 6.0 > 5.0
        assert result.ln_h == 6.0
        assert result.meets_min_ratio is True   # >= 2.0
        assert result.meets_max_ratio is False  # > 5.0


class TestLevelComplianceCheck:
    """Tests para verificación de cumplimiento por niveles §18.10.9.3."""

    def test_all_levels_comply(self):
        """100% de niveles con ln/h <= 5 cumple."""
        service = DuctileCoupledWallService()
        beams = [
            service.verify_beam_geometry("CB1", 1, 2400, 800),  # ln/h = 3
            service.verify_beam_geometry("CB2", 2, 3200, 800),  # ln/h = 4
            service.verify_beam_geometry("CB3", 3, 4000, 800),  # ln/h = 5
        ]
        result = service.verify_level_compliance(beams)

        assert result.total_levels == 3
        assert result.levels_meeting_max == 3
        assert result.compliance_ratio == 1.0
        assert result.is_ok is True

    def test_90_percent_levels_comply(self):
        """Exactamente 90% de niveles cumple."""
        service = DuctileCoupledWallService()
        beams = [
            service.verify_beam_geometry("CB1", 1, 2400, 800),   # ln/h = 3 OK
            service.verify_beam_geometry("CB2", 2, 2400, 800),   # ln/h = 3 OK
            service.verify_beam_geometry("CB3", 3, 2400, 800),   # ln/h = 3 OK
            service.verify_beam_geometry("CB4", 4, 2400, 800),   # ln/h = 3 OK
            service.verify_beam_geometry("CB5", 5, 2400, 800),   # ln/h = 3 OK
            service.verify_beam_geometry("CB6", 6, 2400, 800),   # ln/h = 3 OK
            service.verify_beam_geometry("CB7", 7, 2400, 800),   # ln/h = 3 OK
            service.verify_beam_geometry("CB8", 8, 2400, 800),   # ln/h = 3 OK
            service.verify_beam_geometry("CB9", 9, 2400, 800),   # ln/h = 3 OK
            service.verify_beam_geometry("CB10", 10, 4800, 800), # ln/h = 6 FAIL
        ]
        result = service.verify_level_compliance(beams)

        assert result.total_levels == 10
        assert result.levels_meeting_max == 9
        assert result.compliance_ratio == 0.9
        assert result.is_ok is True  # 90% cumple

    def test_less_than_90_percent_fails(self):
        """Menos del 90% de niveles no cumple."""
        service = DuctileCoupledWallService()
        beams = [
            service.verify_beam_geometry("CB1", 1, 4800, 800),  # ln/h = 6 FAIL
            service.verify_beam_geometry("CB2", 2, 4800, 800),  # ln/h = 6 FAIL
            service.verify_beam_geometry("CB3", 3, 2400, 800),  # ln/h = 3 OK
            service.verify_beam_geometry("CB4", 4, 2400, 800),  # ln/h = 3 OK
            service.verify_beam_geometry("CB5", 5, 2400, 800),  # ln/h = 3 OK
        ]
        result = service.verify_level_compliance(beams)

        assert result.total_levels == 5
        assert result.levels_meeting_max == 3
        assert result.compliance_ratio == 0.6
        assert result.is_ok is False  # 60% < 90%


class TestDuctileCoupledWallVerification:
    """Tests para verificación completa de muro acoplado dúctil."""

    def test_system_qualifies_as_ductile(self):
        """Sistema que cumple todos los criterios califica como dúctil."""
        service = DuctileCoupledWallService()

        walls = [
            {"wall_id": "W1", "hwcs": 15000, "lw": 6000},  # hwcs/lw = 2.5 OK
            {"wall_id": "W2", "hwcs": 15000, "lw": 5000},  # hwcs/lw = 3.0 OK
        ]
        coupling_beams = [
            {"beam_id": "CB1", "level": 1, "ln": 2000, "h": 800},  # ln/h = 2.5
            {"beam_id": "CB2", "level": 2, "ln": 2000, "h": 800},  # ln/h = 2.5
            {"beam_id": "CB3", "level": 3, "ln": 2000, "h": 800},  # ln/h = 2.5
            {"beam_id": "CB4", "level": 4, "ln": 2000, "h": 800},  # ln/h = 2.5
            {"beam_id": "CB5", "level": 5, "ln": 2000, "h": 800},  # ln/h = 2.5
        ]

        result = service.verify_ductile_coupled_wall(walls, coupling_beams)

        assert result.all_walls_ok is True
        assert result.all_beams_min_ok is True
        assert result.level_max_ok is True
        assert result.is_ductile_coupled_wall is True
        assert len(result.warnings) == 0

    def test_system_fails_wall_geometry(self):
        """Sistema con muros que no cumplen no califica."""
        service = DuctileCoupledWallService()

        walls = [
            {"wall_id": "W1", "hwcs": 8000, "lw": 6000},   # hwcs/lw = 1.33 FAIL
            {"wall_id": "W2", "hwcs": 15000, "lw": 5000},  # hwcs/lw = 3.0 OK
        ]
        coupling_beams = [
            {"beam_id": "CB1", "level": 1, "ln": 2000, "h": 800},
        ]

        result = service.verify_ductile_coupled_wall(walls, coupling_beams)

        assert result.all_walls_ok is False
        assert result.is_ductile_coupled_wall is False
        assert any("W1" in w for w in result.warnings)

    def test_system_fails_beam_minimum(self):
        """Sistema con vigas cortas no califica."""
        service = DuctileCoupledWallService()

        walls = [
            {"wall_id": "W1", "hwcs": 15000, "lw": 6000},
        ]
        coupling_beams = [
            {"beam_id": "CB1", "level": 1, "ln": 1200, "h": 800},  # ln/h = 1.5 FAIL
            {"beam_id": "CB2", "level": 2, "ln": 2000, "h": 800},  # ln/h = 2.5 OK
        ]

        result = service.verify_ductile_coupled_wall(walls, coupling_beams)

        assert result.all_beams_min_ok is False
        assert result.is_ductile_coupled_wall is False
        assert any("CB1" in w and "18.10.9.2" in w for w in result.warnings)

    def test_system_fails_level_compliance(self):
        """Sistema con muchas vigas largas no califica."""
        service = DuctileCoupledWallService()

        walls = [
            {"wall_id": "W1", "hwcs": 15000, "lw": 6000},
        ]
        # 3 de 5 niveles (60%) con ln/h > 5
        coupling_beams = [
            {"beam_id": "CB1", "level": 1, "ln": 4800, "h": 800},  # ln/h = 6 FAIL
            {"beam_id": "CB2", "level": 2, "ln": 4800, "h": 800},  # ln/h = 6 FAIL
            {"beam_id": "CB3", "level": 3, "ln": 4800, "h": 800},  # ln/h = 6 FAIL
            {"beam_id": "CB4", "level": 4, "ln": 2000, "h": 800},  # ln/h = 2.5 OK
            {"beam_id": "CB5", "level": 5, "ln": 2000, "h": 800},  # ln/h = 2.5 OK
        ]

        result = service.verify_ductile_coupled_wall(walls, coupling_beams)

        assert result.level_max_ok is False
        assert result.is_ductile_coupled_wall is False
        assert any("18.10.9.3" in w for w in result.warnings)

    def test_result_summary_for_passing(self):
        """Summary correcto para sistema que califica."""
        service = DuctileCoupledWallService()

        walls = [{"wall_id": "W1", "hwcs": 15000, "lw": 6000}]
        coupling_beams = [
            {"beam_id": "CB1", "level": 1, "ln": 2000, "h": 800},
        ]

        result = service.verify_ductile_coupled_wall(walls, coupling_beams)
        assert "califica como muro acoplado dúctil" in result.summary

    def test_result_summary_for_failing(self):
        """Summary correcto para sistema que no califica."""
        service = DuctileCoupledWallService()

        walls = [{"wall_id": "W1", "hwcs": 8000, "lw": 6000}]  # FAIL
        coupling_beams = [
            {"beam_id": "CB1", "level": 1, "ln": 1200, "h": 800},  # FAIL
        ]

        result = service.verify_ductile_coupled_wall(walls, coupling_beams)
        assert "No califica" in result.summary
        assert "hwcs/lw < 2" in result.summary
        assert "ln/h < 2" in result.summary


class TestEdgeCases:
    """Tests para casos límite."""

    def test_empty_walls_list(self):
        """Lista vacía de muros no califica."""
        service = DuctileCoupledWallService()

        result = service.verify_ductile_coupled_wall(
            walls=[],
            coupling_beams=[{"beam_id": "CB1", "level": 1, "ln": 2000, "h": 800}]
        )

        assert result.all_walls_ok is False
        assert result.is_ductile_coupled_wall is False

    def test_empty_beams_list(self):
        """Lista vacía de vigas no califica."""
        service = DuctileCoupledWallService()

        result = service.verify_ductile_coupled_wall(
            walls=[{"wall_id": "W1", "hwcs": 15000, "lw": 6000}],
            coupling_beams=[]
        )

        assert result.all_beams_min_ok is False
        assert result.is_ductile_coupled_wall is False

    def test_auto_generated_ids(self):
        """IDs se generan automáticamente si no se proporcionan."""
        service = DuctileCoupledWallService()

        result = service.verify_ductile_coupled_wall(
            walls=[{"hwcs": 15000, "lw": 6000}],  # Sin wall_id
            coupling_beams=[{"level": 1, "ln": 2000, "h": 800}]  # Sin beam_id
        )

        assert result.wall_checks[0].wall_id == "Wall-1"
        assert result.beam_checks[0].beam_id == "CB-1"
