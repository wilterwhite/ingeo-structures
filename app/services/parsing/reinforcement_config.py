# app/structural/services/parsing/reinforcement_config.py
"""
Configuración de armadura para muros de hormigón armado.

Calcula áreas de acero a partir de malla, diámetro y espaciamiento.
Usa constantes centralizadas de domain/constants/.
"""
from dataclasses import dataclass

from ...domain.constants.reinforcement import (
    RHO_MIN,
    FY_DEFAULT_MPA,
    MESH_DEFAULTS,
)
from ...domain.constants.materials import BAR_AREAS, AVAILABLE_DIAMETERS, get_bar_area

# Usar constantes centralizadas
DEFAULT_DIAMETER = MESH_DEFAULTS['diameter_v']
TYPICAL_SPACINGS = [100, 150, 200, 250, 300]


# =============================================================================
# Dataclass de Configuración
# =============================================================================

@dataclass
class ReinforcementConfig:
    """
    Configuración de armadura de un muro.

    Attributes:
        n_meshes: Número de mallas (1=central, 2=doble cara)
        diameter_v: Diámetro barra vertical (mm)
        spacing_v: Espaciamiento vertical (mm)
        diameter_h: Diámetro barra horizontal (mm)
        spacing_h: Espaciamiento horizontal (mm)
        fy: Límite de fluencia del acero (MPa)
    """
    n_meshes: int = 2
    diameter_v: int = DEFAULT_DIAMETER
    spacing_v: int = 200
    diameter_h: int = DEFAULT_DIAMETER
    spacing_h: int = 200
    fy: float = FY_DEFAULT_MPA

    def __post_init__(self):
        """Validar valores."""
        if self.n_meshes not in (1, 2):
            raise ValueError("n_meshes debe ser 1 o 2")
        if self.diameter_v not in BAR_AREAS:
            raise ValueError(f"Diámetro vertical {self.diameter_v} no disponible")
        if self.diameter_h not in BAR_AREAS:
            raise ValueError(f"Diámetro horizontal {self.diameter_h} no disponible")

    @property
    def bar_area_v(self) -> float:
        """Área de una barra vertical (mm²)."""
        return BAR_AREAS[self.diameter_v]

    @property
    def bar_area_h(self) -> float:
        """Área de una barra horizontal (mm²)."""
        return BAR_AREAS[self.diameter_h]

    @property
    def As_vertical_per_m(self) -> float:
        """
        Área de acero vertical por metro de longitud (mm²/m).

        Fórmula: n_meshes × (área_barra / espaciamiento) × 1000
        """
        spacing = self.spacing_v or 200  # Default 200mm si es 0
        return self.n_meshes * (self.bar_area_v / spacing) * 1000

    @property
    def As_horizontal_per_m(self) -> float:
        """
        Área de acero horizontal por metro de altura (mm²/m).

        Fórmula: n_meshes × (área_barra / espaciamiento) × 1000
        """
        spacing = self.spacing_h or 200  # Default 200mm si es 0
        return self.n_meshes * (self.bar_area_h / spacing) * 1000

    def get_As_vertical_total(self, wall_length_mm: float) -> float:
        """
        Área total de acero vertical en el muro (mm²).

        Args:
            wall_length_mm: Longitud del muro en mm

        Returns:
            Área total de acero vertical en mm²
        """
        return self.As_vertical_per_m * (wall_length_mm / 1000)

    def get_As_horizontal_total(self, wall_height_mm: float) -> float:
        """
        Área total de acero horizontal en el muro (mm²).

        Args:
            wall_height_mm: Altura del muro en mm

        Returns:
            Área total de acero horizontal en mm²
        """
        return self.As_horizontal_per_m * (wall_height_mm / 1000)

    def get_rho_vertical(self, thickness_mm: float) -> float:
        """
        Cuantía de acero vertical.

        Args:
            thickness_mm: Espesor del muro en mm

        Returns:
            Cuantía ρ = As / (b × 1000)
        """
        thickness = thickness_mm or 1  # Evitar división por cero
        return self.As_vertical_per_m / (thickness * 1000)

    def get_rho_horizontal(self, thickness_mm: float) -> float:
        """
        Cuantía de acero horizontal.

        Args:
            thickness_mm: Espesor del muro en mm

        Returns:
            Cuantía ρ = As / (b × 1000)
        """
        thickness = thickness_mm or 1  # Evitar división por cero
        return self.As_horizontal_per_m / (thickness * 1000)

    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización."""
        return {
            'n_meshes': self.n_meshes,
            'diameter_v': self.diameter_v,
            'spacing_v': self.spacing_v,
            'diameter_h': self.diameter_h,
            'spacing_h': self.spacing_h,
            'fy': self.fy,
            'As_vertical_per_m': round(self.As_vertical_per_m, 1),
            'As_horizontal_per_m': round(self.As_horizontal_per_m, 1)
        }

    def description(self) -> str:
        """Descripción legible de la configuración."""
        mesh_text = "1 malla central" if self.n_meshes == 1 else "2 mallas"
        return (
            f"{mesh_text}, "
            f"V: φ{self.diameter_v}@{self.spacing_v}, "
            f"H: φ{self.diameter_h}@{self.spacing_h}"
        )


# =============================================================================
# Funciones de Utilidad
# =============================================================================

def create_minimum_config(
    thickness_mm: float,
    n_meshes: int = 2,
    preferred_diameter: int = DEFAULT_DIAMETER
) -> ReinforcementConfig:
    """
    Crea una configuración con armadura mínima según ACI 318-19.

    Calcula el espaciamiento necesario para cumplir ρ_min = 0.25%
    usando el diámetro preferido.

    Args:
        thickness_mm: Espesor del muro en mm
        n_meshes: Número de mallas (1 o 2)
        preferred_diameter: Diámetro de barra preferido (mm)

    Returns:
        ReinforcementConfig con armadura mínima
    """
    bar_area = BAR_AREAS.get(preferred_diameter, BAR_AREAS[8])

    # As_min por metro = ρ_min × thickness × 1000
    As_min_per_m = RHO_MIN * thickness_mm * 1000

    # Espaciamiento = n_meshes × área_barra × 1000 / As_min
    spacing = n_meshes * bar_area * 1000 / As_min_per_m

    # Redondear a espaciamiento típico (hacia abajo para ser conservador)
    spacing = max(s for s in TYPICAL_SPACINGS if s <= spacing) if spacing >= min(TYPICAL_SPACINGS) else min(TYPICAL_SPACINGS)

    return ReinforcementConfig(
        n_meshes=n_meshes,
        diameter_v=preferred_diameter,
        spacing_v=spacing,
        diameter_h=preferred_diameter,
        spacing_h=spacing
    )


def calculate_spacing_for_As(
    target_As_per_m: float,
    diameter: int,
    n_meshes: int = 2
) -> int:
    """
    Calcula el espaciamiento necesario para lograr un As objetivo.

    Args:
        target_As_per_m: Área de acero objetivo (mm²/m)
        diameter: Diámetro de barra (mm)
        n_meshes: Número de mallas

    Returns:
        Espaciamiento en mm (redondeado a típico)
    """
    bar_area = get_bar_area(diameter)
    spacing = n_meshes * bar_area * 1000 / target_As_per_m

    # Encontrar espaciamiento típico más cercano (conservador)
    for s in sorted(TYPICAL_SPACINGS):
        if s >= spacing:
            return s

    return max(TYPICAL_SPACINGS)
