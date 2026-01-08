# app/domain/entities/beam.py
"""
Entidad Beam: representa una viga de hormigon armado desde ETABS.
Soporta vigas tipo frame y spandrels (vigas de acople tipo shell).
"""
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, TYPE_CHECKING
from enum import Enum

from ..constants.materials import get_bar_area
from ..constants.reinforcement import FY_DEFAULT_MPA, COVER_DEFAULT_BEAM_MM

if TYPE_CHECKING:
    from ..flexure import SteelLayer


class BeamSource(Enum):
    """Origen de la viga en ETABS."""
    FRAME = "frame"         # Viga tipo frame (Element Forces - Beams)
    SPANDREL = "spandrel"   # Viga de acople tipo shell (Spandrel Forces)


@dataclass
class Beam:
    """
    Representa una viga de hormigon armado desde ETABS.

    Unidades:
    - Dimensiones: mm
    - Esfuerzos: MPa
    - Areas: mm2

    Soporta dos fuentes:
    - Frame beams: vigas modeladas como elementos lineales
    - Spandrels: vigas de acople modeladas como shells (entre piers)
    """
    label: str              # "B1" o "S1" (nombre en ETABS)
    story: str              # "Story4"

    # Geometria (mm)
    length: float           # Luz de la viga (longitud)
    depth: float            # Altura de la viga (peralte)
    width: float            # Ancho de la viga (espesor)

    # Propiedades del material (MPa)
    fc: float               # f'c del hormigon
    fy: float = FY_DEFAULT_MPA  # fy del acero (default A630-420H)

    # Origen y seccion
    source: BeamSource = BeamSource.FRAME   # frame o spandrel
    section_name: str = ""                  # Nombre seccion ETABS

    # Armadura transversal (para verificacion de cortante)
    stirrup_diameter: int = 10      # Diametro estribo (mm)
    stirrup_spacing: int = 150      # Espaciamiento estribos (mm)
    n_stirrup_legs: int = 2         # Numero de ramas del estribo

    # Armadura longitudinal (para referencia, no se usa en cortante)
    n_bars_top: int = 3             # Barras superiores
    n_bars_bottom: int = 3          # Barras inferiores
    diameter_top: int = 16          # Diametro barras superiores
    diameter_bottom: int = 16       # Diametro barras inferiores

    # Otros
    cover: float = 40.0             # Recubrimiento (mm)

    # Clasificacion sismica (para verificacion §18.6)
    is_seismic: bool = True         # True = portico especial/intermedio

    # Geometria para verificacion sismica §18.6
    ln: Optional[float] = None      # Luz libre explicita (mm), si None se calcula
    column_depth_left: float = 0    # Profundidad columna izquierda (mm)
    column_depth_right: float = 0   # Profundidad columna derecha (mm)

    # Momentos probables (calculados por FlexocompressionService) §18.6.5
    Mpr_left: Optional[float] = None   # Mpr extremo izquierdo (tonf-m)
    Mpr_right: Optional[float] = None  # Mpr extremo derecho (tonf-m)

    # Areas de barra precalculadas
    _bar_area_stirrup: float = field(default=78.5, repr=False)

    def __post_init__(self):
        """Calcula areas de barra segun diametros."""
        self._bar_area_stirrup = get_bar_area(self.stirrup_diameter, 78.5)

    # =========================================================================
    # Propiedades de Armadura para Cortante
    # =========================================================================

    @property
    def Av(self) -> float:
        """Area de refuerzo transversal (mm2)."""
        return self.n_stirrup_legs * self._bar_area_stirrup

    @property
    def rho_transversal(self) -> float:
        """Cuantia de refuerzo transversal."""
        return self.Av / (self.width * self.stirrup_spacing)

    @property
    def reinforcement_description(self) -> str:
        """Descripcion legible de la armadura transversal."""
        legs = f"{self.n_stirrup_legs}R" if self.n_stirrup_legs > 2 else ""
        return f"{legs}E{self.stirrup_diameter}@{self.stirrup_spacing}"

    # =========================================================================
    # Propiedades Geometricas
    # =========================================================================

    @property
    def Ag(self) -> float:
        """Area bruta de la viga (mm2)."""
        return self.depth * self.width

    @property
    def d(self) -> float:
        """Profundidad efectiva (mm)."""
        return self.depth - self.cover

    @property
    def bw(self) -> float:
        """Ancho del alma para calculo de cortante (mm)."""
        return self.width

    @property
    def aspect_ratio(self) -> float:
        """Relacion luz/peralte (ln/h)."""
        return self.length / self.depth if self.depth > 0 else 0

    @property
    def is_deep(self) -> bool:
        """True si es viga profunda (ln/h < 4)."""
        return self.aspect_ratio < 4.0

    @property
    def is_spandrel(self) -> bool:
        """True si es un spandrel (viga de acople tipo shell)."""
        return self.source == BeamSource.SPANDREL

    @property
    def height(self) -> float:
        """Altura para Protocol FlexuralElement (usa length de la viga)."""
        return self.length

    # =========================================================================
    # Propiedades Sismicas §18.6
    # =========================================================================

    @property
    def ln_calculated(self) -> float:
        """
        Luz libre de la viga (mm) segun §18.6.2.1.

        Si ln fue especificado explicitamente, lo usa.
        Si no, calcula: length - column_depth_left/2 - column_depth_right/2
        """
        if self.ln is not None:
            return self.ln
        return self.length - self.column_depth_left / 2 - self.column_depth_right / 2

    @property
    def hx(self) -> float:
        """
        Separacion maxima entre barras longitudinales soportadas lateralmente (mm).

        Simplificado: asume barras distribuidas uniformemente en el ancho.
        Para §18.6.4.4: hx <= 350mm (14 in)
        """
        n_bars = max(self.n_bars_top, self.n_bars_bottom)
        if n_bars <= 1:
            return self.width - 2 * self.cover
        return (self.width - 2 * self.cover) / (n_bars - 1)

    @property
    def As_top(self) -> float:
        """Area de acero superior (mm2)."""
        return self.n_bars_top * get_bar_area(self.diameter_top)

    @property
    def As_bottom(self) -> float:
        """Area de acero inferior (mm2)."""
        return self.n_bars_bottom * get_bar_area(self.diameter_bottom)

    # =========================================================================
    # Implementacion de FlexuralElement Protocol
    # =========================================================================

    @property
    def As_flexure_total(self) -> float:
        """Area total de acero longitudinal (mm2)."""
        As_top = self.n_bars_top * get_bar_area(self.diameter_top)
        As_bottom = self.n_bars_bottom * get_bar_area(self.diameter_bottom)
        return As_top + As_bottom

    def get_steel_layers(self, direction: str = 'primary') -> List['SteelLayer']:
        """
        Capas de acero para diagrama de interaccion.

        Para vigas, direction no tiene efecto significativo ya que
        tipicamente se flexionan solo en un plano.

        Returns:
            Lista con 2 capas: superior (compresion) e inferior (traccion)
        """
        from ..flexure import SteelLayer

        # Capa superior (compresion bajo momento positivo)
        d_top = self.cover + self.diameter_top / 2
        As_top = self.n_bars_top * get_bar_area(self.diameter_top)

        # Capa inferior (traccion bajo momento positivo)
        d_bottom = self.depth - self.cover - self.diameter_bottom / 2
        As_bottom = self.n_bars_bottom * get_bar_area(self.diameter_bottom)

        return [
            SteelLayer(d_top, As_top),
            SteelLayer(d_bottom, As_bottom)
        ]

    def get_section_dimensions(self, direction: str = 'primary') -> Tuple[float, float]:
        """
        Dimensiones para curva P-M: (ancho, peralte).

        Para vigas, siempre retorna (width, depth) ya que
        tipicamente se flexionan solo en un plano (M3).
        """
        return (self.width, self.depth)

    # =========================================================================
    # Metodos de Actualizacion
    # =========================================================================

    def update_reinforcement(
        self,
        stirrup_diameter: Optional[int] = None,
        stirrup_spacing: Optional[int] = None,
        n_stirrup_legs: Optional[int] = None,
        n_bars_top: Optional[int] = None,
        n_bars_bottom: Optional[int] = None,
        diameter_top: Optional[int] = None,
        diameter_bottom: Optional[int] = None,
        fy: Optional[float] = None,
        cover: Optional[float] = None
    ):
        """
        Actualiza la configuracion de armadura.
        """
        if stirrup_diameter is not None:
            self.stirrup_diameter = stirrup_diameter
            self._bar_area_stirrup = get_bar_area(stirrup_diameter, 78.5)
        if stirrup_spacing is not None:
            self.stirrup_spacing = stirrup_spacing
        if n_stirrup_legs is not None:
            self.n_stirrup_legs = n_stirrup_legs
        if n_bars_top is not None:
            self.n_bars_top = n_bars_top
        if n_bars_bottom is not None:
            self.n_bars_bottom = n_bars_bottom
        if diameter_top is not None:
            self.diameter_top = diameter_top
        if diameter_bottom is not None:
            self.diameter_bottom = diameter_bottom
        if fy is not None:
            self.fy = fy
        if cover is not None:
            self.cover = cover
