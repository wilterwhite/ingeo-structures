# app/domain/chapter18/coupled_walls/results.py
"""
Dataclasses para resultados de verificación de muros acoplados dúctiles.

ACI 318-25 §18.10.9: Ductile Coupled Walls
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class WallGeometryCheck:
    """
    Verificación de geometría de muro individual según §18.10.9.1.

    Requisito: hwcs/lw >= 2.0 para cada muro individual.
    """
    wall_id: str                    # Identificador del muro
    hwcs: float                     # Altura desde sección crítica (mm)
    lw: float                       # Longitud del muro (mm)
    hwcs_lw: float                  # Relación hwcs/lw
    hwcs_lw_min: float = 2.0        # Límite mínimo
    is_ok: bool = False
    aci_reference: str = "ACI 318-25 §18.10.9.1"


@dataclass
class CouplingBeamGeometryCheck:
    """
    Verificación de geometría de viga de acople según §18.10.9.2-3.

    Requisitos:
    - §18.10.9.2: ln/h >= 2.0 para todos los niveles
    - §18.10.9.3: ln/h <= 5.0 para al menos 90% de los niveles
    """
    beam_id: str                    # Identificador de la viga
    level: int                      # Nivel/piso
    ln: float                       # Claro libre (mm)
    h: float                        # Peralte (mm)
    ln_h: float                     # Relación ln/h
    meets_min_ratio: bool           # ln/h >= 2.0 (§18.10.9.2)
    meets_max_ratio: bool           # ln/h <= 5.0 (§18.10.9.3)
    aci_reference: str = "ACI 318-25 §18.10.9.2-3"


@dataclass
class LevelComplianceResult:
    """
    Resultado de cumplimiento por niveles para §18.10.9.3.

    Requisito: Al menos 90% de los niveles deben tener ln/h <= 5.0
    """
    total_levels: int               # Total de niveles con vigas de acople
    levels_meeting_max: int         # Niveles con ln/h <= 5.0
    compliance_ratio: float         # Porcentaje de cumplimiento
    required_ratio: float = 0.90    # 90% requerido
    is_ok: bool = False
    aci_reference: str = "ACI 318-25 §18.10.9.3"


@dataclass
class DuctileCoupledWallResult:
    """
    Resultado completo de verificación de muro acoplado dúctil.

    Un sistema califica como muro acoplado dúctil si cumple TODOS:
    1. §18.10.9.1: hwcs/lw >= 2 para cada muro individual
    2. §18.10.9.2: ln/h >= 2 para vigas de acople en todos los niveles
    3. §18.10.9.3: ln/h <= 5 para al menos 90% de los niveles
    """
    # Verificaciones individuales
    wall_checks: List[WallGeometryCheck]
    beam_checks: List[CouplingBeamGeometryCheck]
    level_compliance: LevelComplianceResult

    # Resultados por criterio
    all_walls_ok: bool              # §18.10.9.1 - Todos los muros cumplen
    all_beams_min_ok: bool          # §18.10.9.2 - Todas las vigas cumplen mínimo
    level_max_ok: bool              # §18.10.9.3 - 90% cumple máximo

    # Resultado final
    is_ductile_coupled_wall: bool   # Si califica como muro acoplado dúctil

    # Metadata
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.10.9"

    @property
    def summary(self) -> str:
        """Resumen del resultado."""
        if self.is_ductile_coupled_wall:
            return "Sistema califica como muro acoplado dúctil"

        issues = []
        if not self.all_walls_ok:
            issues.append("muros con hwcs/lw < 2")
        if not self.all_beams_min_ok:
            issues.append("vigas con ln/h < 2")
        if not self.level_max_ok:
            issues.append(f"< 90% de niveles con ln/h <= 5")

        return f"No califica: {', '.join(issues)}"
