# app/domain/chapter18/coupled_walls/service.py
"""
Servicio de verificación para muros acoplados dúctiles según ACI 318-25 §18.10.9.

Requisitos para calificar como muro acoplado dúctil:
- §18.10.9.1: hwcs/lw >= 2 para cada muro individual
- §18.10.9.2: ln/h >= 2 para vigas de acople en todos los niveles
- §18.10.9.3: ln/h <= 5 para al menos 90% de los niveles
"""
from typing import List, Dict, Any, Optional

from .results import (
    DuctileCoupledWallResult,
    WallGeometryCheck,
    CouplingBeamGeometryCheck,
    LevelComplianceResult,
)


# Constantes según ACI 318-25 §18.10.9
HWCS_LW_MIN = 2.0           # §18.10.9.1: Relación mínima hwcs/lw para muros
LN_H_MIN = 2.0              # §18.10.9.2: Relación mínima ln/h para vigas
LN_H_MAX = 5.0              # §18.10.9.3: Relación máxima ln/h para 90% de niveles
LEVEL_COMPLIANCE_MIN = 0.90  # §18.10.9.3: 90% de niveles deben cumplir ln/h <= 5


class DuctileCoupledWallService:
    """
    Servicio para verificar si un sistema de muros califica como
    muro acoplado dúctil según ACI 318-25 §18.10.9.
    """

    def verify_wall_geometry(
        self,
        wall_id: str,
        hwcs: float,
        lw: float,
    ) -> WallGeometryCheck:
        """
        Verifica geometría de un muro individual según §18.10.9.1.

        Args:
            wall_id: Identificador del muro
            hwcs: Altura desde sección crítica hasta tope (mm)
            lw: Longitud del muro (mm)

        Returns:
            WallGeometryCheck con resultado de verificación
        """
        hwcs_lw = hwcs / lw if lw > 0 else 0
        is_ok = hwcs_lw >= HWCS_LW_MIN

        return WallGeometryCheck(
            wall_id=wall_id,
            hwcs=hwcs,
            lw=lw,
            hwcs_lw=round(hwcs_lw, 2),
            hwcs_lw_min=HWCS_LW_MIN,
            is_ok=is_ok,
        )

    def verify_beam_geometry(
        self,
        beam_id: str,
        level: int,
        ln: float,
        h: float,
    ) -> CouplingBeamGeometryCheck:
        """
        Verifica geometría de una viga de acople según §18.10.9.2-3.

        Args:
            beam_id: Identificador de la viga
            level: Número de nivel/piso
            ln: Claro libre de la viga (mm)
            h: Peralte de la viga (mm)

        Returns:
            CouplingBeamGeometryCheck con resultado de verificación
        """
        ln_h = ln / h if h > 0 else 0
        meets_min = ln_h >= LN_H_MIN  # §18.10.9.2
        meets_max = ln_h <= LN_H_MAX  # §18.10.9.3

        return CouplingBeamGeometryCheck(
            beam_id=beam_id,
            level=level,
            ln=ln,
            h=h,
            ln_h=round(ln_h, 2),
            meets_min_ratio=meets_min,
            meets_max_ratio=meets_max,
        )

    def verify_level_compliance(
        self,
        beam_checks: List[CouplingBeamGeometryCheck],
    ) -> LevelComplianceResult:
        """
        Verifica cumplimiento por niveles según §18.10.9.3.

        Requisito: Al menos 90% de los niveles deben tener ln/h <= 5.0

        Args:
            beam_checks: Lista de verificaciones de vigas

        Returns:
            LevelComplianceResult con resultado de verificación
        """
        if not beam_checks:
            return LevelComplianceResult(
                total_levels=0,
                levels_meeting_max=0,
                compliance_ratio=0.0,
                is_ok=False,
            )

        # Agrupar por nivel y verificar si cada nivel cumple
        levels_data: Dict[int, bool] = {}
        for check in beam_checks:
            level = check.level
            # Un nivel cumple si TODAS sus vigas tienen ln/h <= 5
            if level not in levels_data:
                levels_data[level] = check.meets_max_ratio
            else:
                # Si ya había una viga que no cumple, el nivel no cumple
                levels_data[level] = levels_data[level] and check.meets_max_ratio

        total_levels = len(levels_data)
        levels_meeting_max = sum(1 for ok in levels_data.values() if ok)
        compliance_ratio = levels_meeting_max / total_levels if total_levels > 0 else 0

        return LevelComplianceResult(
            total_levels=total_levels,
            levels_meeting_max=levels_meeting_max,
            compliance_ratio=round(compliance_ratio, 3),
            required_ratio=LEVEL_COMPLIANCE_MIN,
            is_ok=compliance_ratio >= LEVEL_COMPLIANCE_MIN,
        )

    def verify_ductile_coupled_wall(
        self,
        walls: List[Dict[str, Any]],
        coupling_beams: List[Dict[str, Any]],
    ) -> DuctileCoupledWallResult:
        """
        Verifica si un sistema califica como muro acoplado dúctil.

        Args:
            walls: Lista de muros con formato:
                [{"wall_id": "W1", "hwcs": 15000, "lw": 6000}, ...]
            coupling_beams: Lista de vigas de acople con formato:
                [{"beam_id": "CB1", "level": 1, "ln": 2000, "h": 800}, ...]

        Returns:
            DuctileCoupledWallResult con resultado completo
        """
        warnings: List[str] = []

        # Verificar muros individuales (§18.10.9.1)
        wall_checks: List[WallGeometryCheck] = []
        for i, wall in enumerate(walls):
            wall_id = wall.get("wall_id", f"Wall-{i+1}")
            hwcs = wall.get("hwcs", 0)
            lw = wall.get("lw", 0)

            check = self.verify_wall_geometry(wall_id, hwcs, lw)
            wall_checks.append(check)

            if not check.is_ok:
                warnings.append(
                    f"{wall_id}: hwcs/lw = {check.hwcs_lw} < {HWCS_LW_MIN} (§18.10.9.1)"
                )

        # Verificar vigas de acople (§18.10.9.2-3)
        beam_checks: List[CouplingBeamGeometryCheck] = []
        for i, beam in enumerate(coupling_beams):
            beam_id = beam.get("beam_id", f"CB-{i+1}")
            level = beam.get("level", i + 1)
            ln = beam.get("ln", 0)
            h = beam.get("h", 0)

            check = self.verify_beam_geometry(beam_id, level, ln, h)
            beam_checks.append(check)

            if not check.meets_min_ratio:
                warnings.append(
                    f"{beam_id} (Nivel {level}): ln/h = {check.ln_h} < {LN_H_MIN} (§18.10.9.2)"
                )

        # Verificar cumplimiento por niveles (§18.10.9.3)
        level_compliance = self.verify_level_compliance(beam_checks)
        if not level_compliance.is_ok:
            warnings.append(
                f"Solo {level_compliance.compliance_ratio*100:.1f}% de niveles "
                f"cumplen ln/h <= {LN_H_MAX} (requerido: {LEVEL_COMPLIANCE_MIN*100:.0f}%) (§18.10.9.3)"
            )

        # Evaluar criterios
        all_walls_ok = all(check.is_ok for check in wall_checks) if wall_checks else False
        all_beams_min_ok = all(check.meets_min_ratio for check in beam_checks) if beam_checks else False
        level_max_ok = level_compliance.is_ok

        # Resultado final: debe cumplir TODOS los criterios
        is_ductile = all_walls_ok and all_beams_min_ok and level_max_ok

        return DuctileCoupledWallResult(
            wall_checks=wall_checks,
            beam_checks=beam_checks,
            level_compliance=level_compliance,
            all_walls_ok=all_walls_ok,
            all_beams_min_ok=all_beams_min_ok,
            level_max_ok=level_max_ok,
            is_ductile_coupled_wall=is_ductile,
            warnings=warnings,
        )
