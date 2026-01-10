# app/domain/entities/drop_beam.py
"""
Entidad DropBeam: representa una viga capitel (losa diseñada como viga).

Las vigas capitel son losas que se diseñan a flexocompresión como muros,
considerando carga axial, flexión y posibles elementos de borde.
"""
from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING

from ..constants.materials import get_bar_area
from ..constants.reinforcement import RHO_MIN, FY_DEFAULT_MPA

if TYPE_CHECKING:
    from ..calculations.steel_layer_calculator import SteelLayer


@dataclass
class DropBeam:
    """
    Representa una viga capitel (losa diseñada como viga).

    Se diseña igual que un Pier: flexocompresión, corte sísmico,
    posibles elementos de borde.

    Unidades:
    - Dimensiones: mm
    - Esfuerzos: MPa
    - Áreas: mm²

    Convención:
    - width: espesor de la losa (similar a pier.thickness)
    - thickness: ancho tributario (similar a pier.width)
    - length: luz libre de la viga capitel
    """
    label: str              # "CL - C3" (eje - ubicación)
    story: str              # "S02"

    # Geometría (mm)
    width: float            # Espesor de la losa (sección menor)
    thickness: float        # Ancho tributario (sección mayor)
    length: float           # Luz libre de la viga capitel

    # Identificación adicional
    axis_slab: str = ""     # Eje de la losa (ej: "CL")
    location: str = ""      # Ubicación (ej: "C3")

    # Propiedades del material (MPa)
    fc: float = 28.0        # f'c del hormigón
    fy: float = FY_DEFAULT_MPA  # fy del acero (default A630-420H)

    # Configuración de armadura (malla, diámetro, espaciamiento)
    n_meshes: int = 2           # 1=malla central, 2=doble cara
    diameter_v: int = 12        # Diámetro barra vertical (mm)
    spacing_v: int = 200        # Espaciamiento vertical (mm)
    diameter_h: int = 10        # Diámetro barra horizontal (mm)
    spacing_h: int = 200        # Espaciamiento horizontal (mm)

    # Elemento de borde (barras adicionales en los extremos)
    n_edge_bars: int = 4        # Número de barras de borde por extremo
    diameter_edge: int = 16     # Diámetro barra de borde (mm)

    # Estribos de confinamiento en elemento de borde
    stirrup_diameter: int = 10  # Diámetro estribo (mm)
    stirrup_spacing: int = 150  # Espaciamiento estribos (mm)
    n_stirrup_legs: int = 2     # Número de ramas del estribo

    # Otros
    cover: float = 25.0     # Recubrimiento (mm)
    axis_angle: float = 0.0 # Ángulo del eje local

    # Clasificacion sismica (para cortante)
    is_seismic: bool = True

    # Áreas de barra precalculadas
    _bar_area_v: float = field(default=113.1, repr=False)  # φ12 por defecto
    _bar_area_h: float = field(default=78.5, repr=False)   # φ10 por defecto
    _bar_area_edge: float = field(default=201.1, repr=False)  # φ16 por defecto

    def __post_init__(self):
        """Calcula áreas de barra según diámetros."""
        self._bar_area_v = get_bar_area(self.diameter_v, 113.1)
        self._bar_area_h = get_bar_area(self.diameter_h, 78.5)
        self._bar_area_edge = get_bar_area(self.diameter_edge, 201.1)

    # =========================================================================
    # Propiedades de Armadura (idénticas a Pier)
    # =========================================================================

    @property
    def n_intermediate_bars(self) -> int:
        """Número de barras intermedias de malla (sin contar las de borde)."""
        available_length = self.thickness - 2 * self.cover
        if available_length <= 0:
            return 0
        n_spaces = available_length / self.spacing_v
        return max(0, int(n_spaces))

    @property
    def As_vertical(self) -> float:
        """Área de acero vertical de malla intermedia (mm²)."""
        return self.n_intermediate_bars * self.n_meshes * self._bar_area_v

    @property
    def As_horizontal(self) -> float:
        """Área de acero horizontal por metro de altura (mm²/m)."""
        return self.n_meshes * (self._bar_area_h / self.spacing_h) * 1000

    @property
    def As_vertical_per_m(self) -> float:
        """Área de acero vertical por metro de longitud (mm²/m)."""
        return self.n_meshes * (self._bar_area_v / self.spacing_v) * 1000

    @property
    def rho_vertical(self) -> float:
        """Cuantía de acero vertical total (malla + borde)."""
        return (self.As_vertical + self.As_edge_total) / self.Ag

    @property
    def rho_mesh_vertical(self) -> float:
        """Cuantía de acero vertical distribuido (solo malla, sin barras de borde)."""
        return self.As_vertical / self.Ag

    @property
    def rho_horizontal(self) -> float:
        """Cuantía de acero horizontal (malla distribuida)."""
        return self.As_horizontal / (self.width * 1000)

    @property
    def As_edge_total(self) -> float:
        """Área de acero de borde TOTAL (mm²)."""
        return self.n_edge_bars * 2 * self._bar_area_edge

    @property
    def As_edge_per_end(self) -> float:
        """Área de acero de borde en cada extremo (mm²)."""
        return self.n_edge_bars * self._bar_area_edge

    @property
    def n_edge_bars_per_end(self) -> int:
        """Número de barras de borde en cada extremo."""
        return self.n_edge_bars

    @property
    def As_flexure_total(self) -> float:
        """Área de acero total para flexión (mm²)."""
        return self.As_edge_total + self.As_vertical

    @property
    def n_total_vertical_bars(self) -> int:
        """Número total de barras verticales (borde + intermedias)."""
        n_edge = self.n_meshes * 2
        n_intermediate = self.n_intermediate_bars * self.n_meshes
        return n_edge + n_intermediate

    def get_steel_layers(self, direction: str = 'primary') -> List['SteelLayer']:
        """
        Genera las capas de acero para el diagrama P-M.

        Args:
            direction: 'primary' para eje fuerte, 'secondary' para eje débil

        Returns:
            Lista de SteelLayer ordenadas por posición.
        """
        from ..calculations.steel_layer_calculator import SteelLayerCalculator
        return SteelLayerCalculator.calculate_from_drop_beam(self)

    @property
    def reinforcement_description(self) -> str:
        """Descripción legible de la armadura."""
        mesh_text = "1M" if self.n_meshes == 1 else "2M"
        edge_text = f"+{self.n_edge_bars}phi{self.diameter_edge}"
        stirrup_text = f"E{self.stirrup_diameter}@{self.stirrup_spacing}"
        return f"{mesh_text} phi{self.diameter_v}@{self.spacing_v} {edge_text} {stirrup_text}"

    # =========================================================================
    # Propiedades Geométricas
    # =========================================================================

    @property
    def height(self) -> float:
        """Alias para compatibilidad con FlexuralElement protocol."""
        return self.length

    @property
    def Ag(self) -> float:
        """Área bruta de la sección (mm²)."""
        return self.thickness * self.width

    @property
    def d(self) -> float:
        """Profundidad efectiva (mm)."""
        return self.thickness - self.cover

    @property
    def Ig(self) -> float:
        """Momento de inercia de la sección bruta (mm⁴)."""
        return self.width * (self.thickness ** 3) / 12

    @property
    def y_extreme(self) -> float:
        """Distancia de la fibra extrema al eje neutro (mm)."""
        return self.thickness / 2

    @property
    def S(self) -> float:
        """Módulo de sección elástico (mm³)."""
        return self.Ig / self.y_extreme if self.y_extreme > 0 else 0

    # =========================================================================
    # Métodos de Actualización
    # =========================================================================

    def update_reinforcement(
        self,
        n_meshes: Optional[int] = None,
        diameter_v: Optional[int] = None,
        spacing_v: Optional[int] = None,
        diameter_h: Optional[int] = None,
        spacing_h: Optional[int] = None,
        diameter_edge: Optional[int] = None,
        n_edge_bars: Optional[int] = None,
        stirrup_diameter: Optional[int] = None,
        stirrup_spacing: Optional[int] = None,
        n_stirrup_legs: Optional[int] = None,
        fy: Optional[float] = None,
        cover: Optional[float] = None
    ):
        """Actualiza la configuración de armadura."""
        if n_meshes is not None:
            self.n_meshes = n_meshes
        if diameter_v is not None:
            self.diameter_v = diameter_v
            self._bar_area_v = get_bar_area(diameter_v, 113.1)
        if spacing_v is not None:
            self.spacing_v = spacing_v
        if diameter_h is not None:
            self.diameter_h = diameter_h
            self._bar_area_h = get_bar_area(diameter_h, 78.5)
        if spacing_h is not None:
            self.spacing_h = spacing_h
        if diameter_edge is not None:
            self.diameter_edge = diameter_edge
            self._bar_area_edge = get_bar_area(diameter_edge, 201.1)
        if n_edge_bars is not None:
            self.n_edge_bars = n_edge_bars
        if stirrup_diameter is not None:
            self.stirrup_diameter = stirrup_diameter
        if stirrup_spacing is not None:
            self.stirrup_spacing = stirrup_spacing
        if n_stirrup_legs is not None:
            self.n_stirrup_legs = n_stirrup_legs
        if fy is not None:
            self.fy = fy
        if cover is not None:
            self.cover = cover

    # =========================================================================
    # Métodos para Protocol FlexuralElement
    # =========================================================================

    def get_section_dimensions(self, direction: str = 'primary') -> tuple:
        """
        Obtiene las dimensiones de la sección para la curva P-M.

        Para vigas capitel:
        - 'primary': flexión en el plano (eje fuerte)
        - 'secondary': flexión fuera del plano (eje débil)

        Args:
            direction: 'primary' o 'secondary'

        Returns:
            Tuple (width, thickness) en mm
        """
        if direction == 'primary':
            return (self.thickness, self.width)
        else:
            return (self.width, self.thickness)
