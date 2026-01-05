# app/domain/entities/slab.py
"""
Entidad Slab: representa una losa de hormigon armado desde ETABS.
Soporta losas en una direccion (1-Way) y dos direcciones (2-Way).
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from ..constants.materials import get_bar_area
from ..constants.reinforcement import FY_DEFAULT_MPA, COVER_DEFAULT_BEAM_MM


class SlabType(Enum):
    """Tipo de losa segun direccion de carga."""
    ONE_WAY = "one_way"     # Losa en una direccion (Cap. 7)
    TWO_WAY = "two_way"     # Losa en dos direcciones (Cap. 8)


class SupportCondition(Enum):
    """Condicion de apoyo para espesor minimo."""
    SIMPLY_SUPPORTED = "simply_supported"   # Simplemente apoyada
    ONE_END_CONTINUOUS = "one_end_continuous"  # Un extremo continuo
    BOTH_ENDS_CONTINUOUS = "both_ends_continuous"  # Ambos extremos continuos
    CANTILEVER = "cantilever"  # Voladizo


@dataclass
class Slab:
    """
    Representa una losa de hormigon armado desde ETABS.

    Unidades:
    - Dimensiones: mm
    - Esfuerzos: MPa
    - Areas: mm2

    Los datos provienen de Section Cut Forces - Analysis de ETABS.
    """
    label: str              # Nombre del corte de seccion
    story: str              # Piso (ej: "S02")

    # Tipo de losa
    slab_type: SlabType = SlabType.ONE_WAY

    # Geometria (mm)
    thickness: float = 200.0        # Espesor (h)
    width: float = 1000.0           # Ancho del corte (tributario)
    span_length: float = 5000.0     # Luz libre (ln)

    # Ubicacion del corte
    axis_slab: str = ""             # Eje de la losa (ej: "CL")
    location: str = ""              # Ubicacion del corte (ej: "Eje C3")

    # Propiedades del material (MPa)
    fc: float = 28.0                # f'c del hormigon
    fy: float = FY_DEFAULT_MPA      # fy del acero (default A630-420H)

    # Condicion de apoyo (para espesor minimo)
    support_condition: SupportCondition = SupportCondition.ONE_END_CONTINUOUS

    # Armadura principal (direccion del momento)
    diameter_main: int = 12         # Diametro refuerzo principal (mm)
    spacing_main: int = 200         # Espaciamiento principal (mm)
    n_layers: int = 1               # Capas de refuerzo

    # Armadura de temperatura y retraccion (perpendicular)
    diameter_temp: int = 8          # Diametro refuerzo T&S (mm)
    spacing_temp: int = 250         # Espaciamiento T&S (mm)

    # Recubrimiento
    cover: float = 25.0             # Recubrimiento libre (mm)

    # Para punzonamiento (solo 2-Way)
    column_width: float = 400.0     # Ancho columna (mm)
    column_depth: float = 400.0     # Profundidad columna (mm)
    is_interior_column: bool = True # Columna interior vs borde/esquina

    # Areas de barra precalculadas
    _bar_area_main: float = field(default=113.1, repr=False)
    _bar_area_temp: float = field(default=50.3, repr=False)

    def __post_init__(self):
        """Calcula areas de barra segun diametros."""
        self._bar_area_main = get_bar_area(self.diameter_main, 113.1)
        self._bar_area_temp = get_bar_area(self.diameter_temp, 50.3)

    # =========================================================================
    # Propiedades Geometricas
    # =========================================================================

    @property
    def d(self) -> float:
        """Profundidad efectiva (mm)."""
        return self.thickness - self.cover - self.diameter_main / 2

    @property
    def Ag(self) -> float:
        """Area bruta por metro de ancho (mm2/m)."""
        return self.thickness * 1000  # 1000mm = 1m de ancho

    @property
    def aspect_ratio(self) -> float:
        """Relacion luz/espesor (ln/h)."""
        return self.span_length / self.thickness if self.thickness > 0 else 0

    # =========================================================================
    # Propiedades de Armadura
    # =========================================================================

    @property
    def As_main(self) -> float:
        """Area de refuerzo principal por metro de ancho (mm2/m)."""
        n_bars_per_meter = 1000 / self.spacing_main
        return n_bars_per_meter * self._bar_area_main * self.n_layers

    @property
    def As_temp(self) -> float:
        """Area de refuerzo T&S por metro de ancho (mm2/m)."""
        n_bars_per_meter = 1000 / self.spacing_temp
        return n_bars_per_meter * self._bar_area_temp

    @property
    def rho_main(self) -> float:
        """Cuantia de refuerzo principal."""
        return self.As_main / (1000 * self.d) if self.d > 0 else 0

    @property
    def rho_temp(self) -> float:
        """Cuantia de refuerzo T&S."""
        return self.As_temp / self.Ag if self.Ag > 0 else 0

    @property
    def reinforcement_description(self) -> str:
        """Descripcion legible de la armadura principal."""
        return f"φ{self.diameter_main}@{self.spacing_main}"

    @property
    def temp_reinforcement_description(self) -> str:
        """Descripcion legible de la armadura T&S."""
        return f"φ{self.diameter_temp}@{self.spacing_temp}"

    # =========================================================================
    # Propiedades para Punzonamiento (2-Way)
    # =========================================================================

    @property
    def alpha_s(self) -> float:
        """Factor alpha_s segun posicion de columna (22.6.5.2)."""
        if self.is_interior_column:
            return 40.0  # Columna interior
        else:
            return 30.0  # Columna de borde (simplificado)

    @property
    def beta_column(self) -> float:
        """Relacion lado largo/lado corto de la columna."""
        c_max = max(self.column_width, self.column_depth)
        c_min = min(self.column_width, self.column_depth)
        return c_max / c_min if c_min > 0 else 1.0

    @property
    def bo(self) -> float:
        """Perimetro de la seccion critica a d/2 de la columna (mm)."""
        # Seccion critica a d/2 de la cara de la columna
        c1 = self.column_width + self.d
        c2 = self.column_depth + self.d
        if self.is_interior_column:
            return 2 * (c1 + c2)  # 4 lados
        else:
            # Simplificado: columna de borde (3 lados)
            return 2 * c1 + c2

    # =========================================================================
    # Metodos de Actualizacion
    # =========================================================================

    def update_reinforcement(
        self,
        diameter_main: Optional[int] = None,
        spacing_main: Optional[int] = None,
        diameter_temp: Optional[int] = None,
        spacing_temp: Optional[int] = None,
        n_layers: Optional[int] = None,
        cover: Optional[float] = None
    ):
        """Actualiza la configuracion de armadura."""
        if diameter_main is not None:
            self.diameter_main = diameter_main
            self._bar_area_main = get_bar_area(diameter_main, 113.1)
        if spacing_main is not None:
            self.spacing_main = spacing_main
        if diameter_temp is not None:
            self.diameter_temp = diameter_temp
            self._bar_area_temp = get_bar_area(diameter_temp, 50.3)
        if spacing_temp is not None:
            self.spacing_temp = spacing_temp
        if n_layers is not None:
            self.n_layers = n_layers
        if cover is not None:
            self.cover = cover

    def update_column_info(
        self,
        column_width: Optional[float] = None,
        column_depth: Optional[float] = None,
        is_interior: Optional[bool] = None
    ):
        """Actualiza informacion de columna para punzonamiento."""
        if column_width is not None:
            self.column_width = column_width
        if column_depth is not None:
            self.column_depth = column_depth
        if is_interior is not None:
            self.is_interior_column = is_interior

    def set_slab_type(self, slab_type: SlabType):
        """Establece el tipo de losa."""
        self.slab_type = slab_type

    @property
    def is_one_way(self) -> bool:
        """True si es losa en una direccion."""
        return self.slab_type == SlabType.ONE_WAY

    @property
    def is_two_way(self) -> bool:
        """True si es losa en dos direcciones."""
        return self.slab_type == SlabType.TWO_WAY
