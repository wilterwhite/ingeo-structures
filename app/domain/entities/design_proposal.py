# app/domain/entities/design_proposal.py
"""
Entidades para propuestas de diseño de piers.

Sistema inteligente que propone soluciones cuando un pier falla verificación,
analizando el modo de falla y proponiendo correcciones específicas.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List

from ..constants.materials import get_bar_area


class FailureMode(Enum):
    """Modos de falla detectados en verificación."""
    NONE = "none"
    FLEXURE = "flexure"           # SF flexión < 1.0
    SHEAR = "shear"               # DCR corte > 1.0
    CONFINEMENT = "confinement"   # Elemento de borde requerido
    SLENDERNESS = "slenderness"   # Esbeltez excesiva
    COMBINED = "combined"         # Múltiples fallas
    OVERDESIGNED = "overdesigned" # SF >> 1.0, se puede optimizar


class ProposalType(Enum):
    """Tipos de propuesta de diseño."""
    NONE = "none"
    BOUNDARY_BARS = "boundary_bars"     # Aumentar barras de borde
    MESH = "mesh"                       # Aumentar malla
    STIRRUPS = "stirrups"               # Aumentar estribos
    THICKNESS = "thickness"             # Aumentar espesor
    COMBINED = "combined"               # Múltiples cambios
    REDUCTION = "reduction"             # Reducir refuerzo (optimización)


@dataclass
class ReinforcementConfig:
    """Configuración de armadura para propuestas."""
    # Barras de borde
    n_edge_bars: int = 2
    diameter_edge: int = 12

    # Malla
    n_meshes: int = 2
    diameter_v: int = 8
    spacing_v: int = 200
    diameter_h: int = 8
    spacing_h: int = 200

    # Estribos de confinamiento
    stirrup_diameter: int = 10
    stirrup_spacing: int = 150
    n_stirrup_legs: int = 2  # Número de ramas (2, 3 o 4)

    # Geometría (para propuestas de espesor)
    thickness: Optional[float] = None

    @property
    def As_edge(self) -> float:
        """Área de acero de borde total (mm²)."""
        bar_area = get_bar_area(self.diameter_edge, 78.5)
        return self.n_edge_bars * 2 * bar_area  # 2 extremos

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            'n_edge_bars': self.n_edge_bars,
            'diameter_edge': self.diameter_edge,
            'n_meshes': self.n_meshes,
            'diameter_v': self.diameter_v,
            'spacing_v': self.spacing_v,
            'diameter_h': self.diameter_h,
            'spacing_h': self.spacing_h,
            'stirrup_diameter': self.stirrup_diameter,
            'stirrup_spacing': self.stirrup_spacing,
            'n_stirrup_legs': self.n_stirrup_legs,
            'thickness': self.thickness,
            'As_edge': round(self.As_edge, 1)
        }

    def description(self, original_thickness: float = None) -> str:
        """Descripción corta de la configuración."""
        parts = []

        # Borde
        parts.append(f"{self.n_edge_bars}φ{self.diameter_edge}")

        # Malla
        mesh_prefix = "1M" if self.n_meshes == 1 else "2M"
        parts.append(f"{mesh_prefix} φ{self.diameter_v}@{self.spacing_v}")

        # Espesor solo si cambió respecto al original
        if self.thickness and original_thickness and self.thickness != original_thickness:
            parts.append(f"e={int(self.thickness)}mm")

        return " + ".join(parts)


@dataclass
class DesignProposal:
    """
    Propuesta de diseño para un pier que falla verificación.

    Contiene la configuración original, la propuesta, y los factores
    de seguridad antes y después del cambio.
    """
    # Identificación
    pier_key: str

    # Modo de falla detectado
    failure_mode: FailureMode

    # Tipo de propuesta
    proposal_type: ProposalType

    # Configuraciones
    original_config: ReinforcementConfig
    proposed_config: ReinforcementConfig

    # Factores de seguridad
    original_sf_flexure: float = 0.0
    proposed_sf_flexure: float = 0.0
    original_dcr_shear: float = 0.0
    proposed_dcr_shear: float = 0.0

    # Iteraciones necesarias
    iterations: int = 0

    # Estado
    success: bool = False  # True si la propuesta resuelve el problema

    # Cambios específicos realizados
    changes: List[str] = field(default_factory=list)

    @property
    def sf_improvement(self) -> float:
        """Mejora porcentual en SF de flexión."""
        if self.original_sf_flexure > 0:
            return (self.proposed_sf_flexure - self.original_sf_flexure) / self.original_sf_flexure * 100
        return 0.0

    @property
    def dcr_improvement(self) -> float:
        """Mejora porcentual en DCR de corte (reducción)."""
        if self.original_dcr_shear > 0:
            return (self.original_dcr_shear - self.proposed_dcr_shear) / self.original_dcr_shear * 100
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON."""
        # Obtener espesor original para comparación en descripción
        original_thickness = self.original_config.thickness

        return {
            'pier_key': self.pier_key,
            'failure_mode': self.failure_mode.value,
            'proposal_type': self.proposal_type.value,
            'original_config': self.original_config.to_dict(),
            'proposed_config': self.proposed_config.to_dict(),
            'original_sf_flexure': round(self.original_sf_flexure, 3),
            'proposed_sf_flexure': round(self.proposed_sf_flexure, 3),
            'original_dcr_shear': round(self.original_dcr_shear, 3),
            'proposed_dcr_shear': round(self.proposed_dcr_shear, 3),
            'iterations': self.iterations,
            'success': self.success,
            'changes': self.changes,
            'sf_improvement': round(self.sf_improvement, 1),
            'dcr_improvement': round(self.dcr_improvement, 1),
            'description': self.proposed_config.description(original_thickness)
        }


# =============================================================================
# SECUENCIAS DE INCREMENTO
# =============================================================================

# Secuencia de barras de borde ordenadas por As creciente
# Formato: (n_bars, diameter_mm)
# As = n_bars × 2_extremos × area_barra
# Ordenado estrictamente por área total
BOUNDARY_BAR_SEQUENCE = [
    (2, 10),   # 314 mm²
    (2, 12),   # 452 mm²
    (4, 10),   # 628 mm²
    (2, 16),   # 804 mm²
    (4, 12),   # 905 mm²
    (6, 10),   # 942 mm²
    (2, 20),   # 1257 mm²
    (6, 12),   # 1357 mm²
    (4, 16),   # 1609 mm²
    (8, 12),   # 1810 mm²
    (2, 25),   # 1964 mm²
    (6, 16),   # 2413 mm²
    (4, 20),   # 2513 mm²
    (8, 16),   # 3218 mm²
    (6, 20),   # 3770 mm²
    (4, 25),   # 3927 mm²
    (10, 16),  # 4022 mm²
    (8, 20),   # 5027 mm²
    (6, 25),   # 5891 mm²
    (10, 20),  # 6284 mm²
    (6, 28),   # 7390 mm²
    (8, 25),   # 7854 mm²
    (6, 32),   # 9650 mm²
    (10, 25),  # 9818 mm²
    (8, 28),   # 9853 mm²
    (10, 28),  # 12316 mm²
    (8, 32),   # 12867 mm²
    (12, 28),  # 14779 mm²
    (10, 32),  # 16084 mm²
    (12, 32),  # 19301 mm²
]

# Secuencia de diámetros de malla
MESH_DIAMETER_SEQUENCE = [6, 8, 10, 12, 16]

# Secuencia de espaciamientos de malla (mm)
MESH_SPACING_SEQUENCE = [300, 250, 200, 150, 100]

# Secuencia de espesores de muro (mm) - incrementos de 25mm
THICKNESS_SEQUENCE = [150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500]

# Secuencia de diámetros de estribo (máx φ12)
STIRRUP_DIAMETER_SEQUENCE = [8, 10, 12]

# Secuencia de espaciamientos de estribo (mm)
STIRRUP_SPACING_SEQUENCE = [150, 125, 100, 75]

# Secuencia de ramas de estribo (para aumentar capacidad a corte)
STIRRUP_LEGS_SEQUENCE = [2, 3, 4]
