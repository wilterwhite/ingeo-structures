# app/domain/entities/column.py
"""
Entidad Column: representa una columna de hormigon armado desde ETABS.
"""
from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING

from ..constants.materials import get_bar_area

if TYPE_CHECKING:
    from ..calculations.steel_layer_calculator import SteelLayer


@dataclass
class Column:
    """
    Representa una columna de hormigon armado desde ETABS.

    Unidades:
    - Dimensiones: mm
    - Esfuerzos: MPa
    - Areas: mm2

    Convencion ETABS:
    - depth: dimension en direccion del eje 2 (profundidad)
    - width: dimension en direccion del eje 3 (ancho)
    """
    label: str              # "C2" (nombre de la columna en ETABS)
    story: str              # "Story4"

    # Geometria (mm)
    depth: float            # Profundidad - direccion eje 2 (Depth en ETABS)
    width: float            # Ancho - direccion eje 3 (Width en ETABS)
    height: float           # Altura del piso (calculada desde stations)

    # Propiedades del material (MPa)
    fc: float               # f'c del hormigon
    fy: float = 420.0       # fy del acero (default A630-420H)

    # Seccion ETABS (para referencia)
    section_name: str = ""  # "ConcCol" - nombre de seccion en ETABS

    # Configuracion de armadura longitudinal
    # Barras distribuidas en el perimetro de la seccion
    n_bars_depth: int = 3       # Barras en direccion de la profundidad (por cara)
    n_bars_width: int = 3       # Barras en direccion del ancho (por cara)
    diameter_long: int = 20     # Diametro barras longitudinales (mm)

    # Armadura transversal (estribos)
    stirrup_diameter: int = 10      # Diametro estribo (mm)
    stirrup_spacing: int = 150      # Espaciamiento estribos (mm)
    n_stirrup_legs_depth: int = 2   # Ramas en direccion profundidad
    n_stirrup_legs_width: int = 2   # Ramas en direccion ancho

    # Otros
    cover: float = 40.0         # Recubrimiento (mm) - 4cm default para columnas

    # Areas de barra precalculadas
    _bar_area_long: float = field(default=314.2, repr=False)  # phi20 por defecto

    def __post_init__(self):
        """Calcula areas de barra segun diametros."""
        self._bar_area_long = get_bar_area(self.diameter_long, 314.2)

    # =========================================================================
    # Propiedades de Armadura
    # =========================================================================

    @property
    def n_total_bars(self) -> int:
        """
        Numero total de barras longitudinales.

        Para seccion rectangular con barras en el perimetro:
        - 4 esquinas siempre
        - (n_bars_depth - 2) * 2 en las caras de profundidad
        - (n_bars_width - 2) * 2 en las caras de ancho
        """
        if self.n_bars_depth < 2 or self.n_bars_width < 2:
            return 4  # minimo 4 esquinas
        n_corners = 4
        n_sides_depth = max(0, self.n_bars_depth - 2) * 2
        n_sides_width = max(0, self.n_bars_width - 2) * 2
        return n_corners + n_sides_depth + n_sides_width

    @property
    def As_longitudinal(self) -> float:
        """Area total de acero longitudinal (mm2)."""
        return self.n_total_bars * self._bar_area_long

    @property
    def rho_longitudinal(self) -> float:
        """Cuantia de acero longitudinal (As/Ag)."""
        return self.As_longitudinal / self.Ag

    @property
    def As_transversal_depth(self) -> float:
        """Area de acero transversal en direccion profundidad (mm2)."""
        return self.n_stirrup_legs_depth * get_bar_area(self.stirrup_diameter)

    @property
    def As_transversal_width(self) -> float:
        """Area de acero transversal en direccion ancho (mm2)."""
        return self.n_stirrup_legs_width * get_bar_area(self.stirrup_diameter)

    @property
    def rho_transversal_depth(self) -> float:
        """Cuantia de refuerzo transversal en direccion profundidad."""
        return self.As_transversal_depth / (self.width * self.stirrup_spacing)

    @property
    def rho_transversal_width(self) -> float:
        """Cuantia de refuerzo transversal en direccion ancho."""
        return self.As_transversal_width / (self.depth * self.stirrup_spacing)

    @property
    def reinforcement_description(self) -> str:
        """Descripcion legible de la armadura."""
        return (
            f"{self.n_total_bars}phi{self.diameter_long} "
            f"E{self.stirrup_diameter}@{self.stirrup_spacing}"
        )

    # =========================================================================
    # Propiedades Geometricas
    # =========================================================================

    @property
    def Ag(self) -> float:
        """Area bruta de la columna (mm2)."""
        return self.depth * self.width

    @property
    def d_depth(self) -> float:
        """Profundidad efectiva en direccion eje 2 (mm)."""
        return self.depth - self.cover

    @property
    def d_width(self) -> float:
        """Profundidad efectiva en direccion eje 3 (mm)."""
        return self.width - self.cover

    @property
    def is_square(self) -> bool:
        """True si la columna es cuadrada."""
        return abs(self.depth - self.width) < 1.0  # tolerancia 1mm

    # =========================================================================
    # Metodos de Actualizacion
    # =========================================================================

    def update_reinforcement(
        self,
        n_bars_depth: Optional[int] = None,
        n_bars_width: Optional[int] = None,
        diameter_long: Optional[int] = None,
        stirrup_diameter: Optional[int] = None,
        stirrup_spacing: Optional[int] = None,
        n_stirrup_legs_depth: Optional[int] = None,
        n_stirrup_legs_width: Optional[int] = None,
        fy: Optional[float] = None,
        cover: Optional[float] = None
    ):
        """
        Actualiza la configuracion de armadura.
        """
        if n_bars_depth is not None:
            self.n_bars_depth = n_bars_depth
        if n_bars_width is not None:
            self.n_bars_width = n_bars_width
        if diameter_long is not None:
            self.diameter_long = diameter_long
            self._bar_area_long = get_bar_area(diameter_long, 314.2)
        if stirrup_diameter is not None:
            self.stirrup_diameter = stirrup_diameter
        if stirrup_spacing is not None:
            self.stirrup_spacing = stirrup_spacing
        if n_stirrup_legs_depth is not None:
            self.n_stirrup_legs_depth = n_stirrup_legs_depth
        if n_stirrup_legs_width is not None:
            self.n_stirrup_legs_width = n_stirrup_legs_width
        if fy is not None:
            self.fy = fy
        if cover is not None:
            self.cover = cover

    def get_steel_layers_depth(self) -> List['SteelLayer']:
        """
        Genera las capas de acero para flexion en direccion de profundidad.

        Las capas se ordenan desde el borde comprimido hacia el traccionado.
        """
        from ..calculations.steel_layer_calculator import SteelLayer

        layers = []
        # Posiciones de las barras en direccion de la profundidad
        # Primera capa: cover + db/2
        # Ultima capa: depth - cover - db/2
        if self.n_bars_depth >= 2:
            d_first = self.cover
            d_last = self.depth - self.cover
            if self.n_bars_depth == 2:
                positions = [d_first, d_last]
            else:
                spacing = (d_last - d_first) / (self.n_bars_depth - 1)
                positions = [d_first + i * spacing for i in range(self.n_bars_depth)]

            # Barras por capa: n_bars_width (las barras en cada nivel)
            bars_per_layer = self.n_bars_width
            for pos in positions:
                layers.append(SteelLayer(
                    position=pos,
                    area=bars_per_layer * self._bar_area_long
                ))

        return layers

    def get_steel_layers_width(self) -> List['SteelLayer']:
        """
        Genera las capas de acero para flexion en direccion del ancho.
        """
        from ..calculations.steel_layer_calculator import SteelLayer

        layers = []
        if self.n_bars_width >= 2:
            d_first = self.cover
            d_last = self.width - self.cover
            if self.n_bars_width == 2:
                positions = [d_first, d_last]
            else:
                spacing = (d_last - d_first) / (self.n_bars_width - 1)
                positions = [d_first + i * spacing for i in range(self.n_bars_width)]

            bars_per_layer = self.n_bars_depth
            for pos in positions:
                layers.append(SteelLayer(
                    position=pos,
                    area=bars_per_layer * self._bar_area_long
                ))

        return layers
