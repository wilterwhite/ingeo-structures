# app/domain/entities/reinforcement.py
"""
Clases unificadas de armadura para elementos estructurales.

Unifica:
- MeshReinforcement (vertical) + HorizontalMeshReinforcement -> MeshReinforcement
- DiscreteReinforcement (vertical) -> DiscreteReinforcement (sin cambio)
- HorizontalDiscreteReinforcement -> BeamReinforcement (renombrada, diferente estructura)

Las clases de vigas mantienen nombres diferentes porque tienen estructura distinta
(top/bottom vs length/thickness).
"""
from dataclasses import dataclass, field

from ..constants.materials import get_bar_area


@dataclass
class MeshReinforcement:
    """
    Armadura de malla distribuida + barras de borde.

    Usada para:
    - Muros (VerticalElement con layout MESH)
    - Vigas capitel (HorizontalElement con source DROP_BEAM)

    Los defaults son genéricos. Cada entidad puede especificar
    valores apropiados al instanciar.
    """
    n_meshes: int = 2           # 1=malla central, 2=doble cara
    diameter_v: int = 10        # Diámetro barra vertical (mm)
    spacing_v: int = 200        # Espaciamiento vertical (mm)
    diameter_h: int = 10        # Diámetro barra horizontal (mm)
    spacing_h: int = 200        # Espaciamiento horizontal (mm)

    # Barras de borde
    n_edge_bars: int = 2        # Barras por extremo
    diameter_edge: int = 12     # Diámetro barra de borde (mm)

    # Áreas precalculadas
    _bar_area_v: float = field(default=78.5, repr=False)
    _bar_area_h: float = field(default=78.5, repr=False)
    _bar_area_edge: float = field(default=113.1, repr=False)

    def __post_init__(self):
        """Calcula áreas de barra según diámetros."""
        self._bar_area_v = get_bar_area(self.diameter_v, 78.5)
        self._bar_area_h = get_bar_area(self.diameter_h, 78.5)
        self._bar_area_edge = get_bar_area(self.diameter_edge, 113.1)


@dataclass
class DiscreteReinforcement:
    """
    Armadura discreta perimetral para columnas y pier-columns.

    Distribución perimetral típica de columnas con estribos.
    """
    n_bars_length: int = 3      # Barras en dirección length
    n_bars_thickness: int = 3   # Barras en dirección thickness
    diameter: int = 20          # Diámetro barras longitudinales (mm)

    # Área precalculada
    _bar_area: float = field(default=314.2, repr=False)

    def __post_init__(self):
        """Calcula área de barra."""
        self._bar_area = get_bar_area(self.diameter, 314.2)

    @property
    def n_total_bars(self) -> int:
        """Número total de barras."""
        # Caso especial: 1 fierro centrado
        if self.n_bars_length == 1 and self.n_bars_thickness == 1:
            return 1

        # Caso normal: distribución perimetral
        if self.n_bars_length < 2 or self.n_bars_thickness < 2:
            return 4  # mínimo 4 esquinas
        n_corners = 4
        n_sides_length = max(0, self.n_bars_length - 2) * 2
        n_sides_thickness = max(0, self.n_bars_thickness - 2) * 2
        return n_corners + n_sides_length + n_sides_thickness

    @property
    def As_total(self) -> float:
        """Área total de acero longitudinal (mm2)."""
        return self.n_total_bars * self._bar_area


@dataclass
class BeamReinforcement:
    """
    Armadura discreta para vigas (top/bottom).

    Distribución típica de vigas con barras superiores e inferiores.
    """
    n_bars_top: int = 3         # Barras superiores
    n_bars_bottom: int = 3      # Barras inferiores
    diameter_top: int = 16      # Diámetro barras superiores (mm)
    diameter_bottom: int = 16   # Diámetro barras inferiores (mm)
