# app/domain/entities/vertical_element.py
"""
Entidad VerticalElement: representa un elemento vertical (columna o pier) de hormigon armado.

Unifica Column y Pier en una sola entidad con:
- VerticalElementSource: origen del elemento (FRAME o PIER)
- ReinforcementLayout: tipo de armadura (STIRRUPS o MESH), calculado automaticamente
"""
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, TYPE_CHECKING
from enum import Enum

from ..constants.materials import get_bar_area
from ..constants.reinforcement import (
    FY_DEFAULT_MPA,
    COVER_DEFAULT_COLUMN_MM,
    COVER_DEFAULT_PIER_MM,
    MESH_DEFAULTS,
)
from .reinforcement import MeshReinforcement, DiscreteReinforcement
from .composite_section import CompositeSection, SectionShapeType

if TYPE_CHECKING:
    from ..calculations.steel_layer_calculator import SteelLayer


class VerticalElementSource(Enum):
    """Origen del elemento vertical en ETABS."""
    FRAME = "frame"      # Viene de Frame en ETABS (columna)
    PIER = "pier"        # Viene de Pier/Shell en ETABS


class ReinforcementLayout(Enum):
    """Tipo de configuracion de armadura."""
    STIRRUPS = "stirrups"  # Barras perimetrales + estribos (columnas, pier-column)
    MESH = "mesh"          # Malla distribuida + barras borde (muros)


@dataclass
class VerticalElement:
    """
    Elemento vertical unificado: columna o pier.

    Unidades:
    - Dimensiones: mm
    - Esfuerzos: MPa
    - Areas: mm2

    El reinforcement_layout se determina automaticamente basado en
    la clasificacion geometrica (lw/tw ratio).
    """
    # Identificacion
    label: str              # "C2" o "PMar-C4-1"
    story: str              # "Story4"

    # Geometria UNIFICADA (mm)
    length: float           # Dimension mayor (lw para pier, depth para column)
    thickness: float        # Dimension menor (tw para pier, width para column)
    height: float           # Altura del elemento

    # Propiedades del material (MPa)
    fc: float               # f'c del hormigon
    fy: float = FY_DEFAULT_MPA  # fy del acero (default A630-420H)

    # Origen del elemento
    source: VerticalElementSource = VerticalElementSource.FRAME

    # Seccion ETABS (para referencia)
    section_name: str = ""

    # Armadura longitudinal (se inicializa en __post_init__ segun layout)
    discrete_reinforcement: Optional[DiscreteReinforcement] = None
    mesh_reinforcement: Optional[MeshReinforcement] = None

    # Armadura transversal (estribos) - UNIFICADA
    stirrup_diameter: int = 10      # Diametro estribo (mm)
    stirrup_spacing: int = 150      # Espaciamiento estribos (mm)
    n_shear_legs: int = 2           # Ramas de corte principal
    n_shear_legs_secondary: Optional[int] = None  # Ramas secundarias (solo columns)

    # Otros
    cover: float = COVER_DEFAULT_COLUMN_MM  # Recubrimiento (mm)
    is_seismic: bool = True  # Clasificacion sismica

    # Categoria sismica individual (opcional)
    seismic_category: Optional[str] = None

    # Campos especificos FRAME (datos para columna fuerte-viga debil)
    Mnc_top: Optional[float] = None
    Mnc_bottom: Optional[float] = None
    sum_Mnb_major: Optional[float] = None
    sum_Mnb_minor: Optional[float] = None
    lu: Optional[float] = None  # Altura libre explicita

    # Campos especificos PIER
    axis_angle: float = 0.0

    # Geometria compuesta (opcional, para piers L, T, C)
    composite_section: Optional[CompositeSection] = None

    # Layout calculado (se determina en __post_init__)
    _reinforcement_layout: Optional[ReinforcementLayout] = field(default=None, repr=False)

    def __post_init__(self):
        """Inicializa armadura segun geometria usando ReinforcementProposer."""
        from ..calculations.reinforcement_proposer import (
            ReinforcementProposer,
            ProposedLayout,
        )

        # Validar geometria
        if self.length <= 0:
            raise ValueError(f"VerticalElement {self.label}: length debe ser > 0")
        if self.thickness <= 0:
            raise ValueError(f"VerticalElement {self.label}: thickness debe ser > 0")
        if self.height <= 0:
            raise ValueError(f"VerticalElement {self.label}: height debe ser > 0")

        # Obtener propuesta automatica segun geometria
        proposal = ReinforcementProposer.propose(self.length, self.thickness)

        # Asignar layout segun propuesta
        if proposal.layout == ProposedLayout.MESH:
            self._reinforcement_layout = ReinforcementLayout.MESH
        else:
            self._reinforcement_layout = ReinforcementLayout.STIRRUPS

        # Inicializar armadura si no se proporciono
        if self._reinforcement_layout == ReinforcementLayout.STIRRUPS:
            if self.discrete_reinforcement is None:
                self.discrete_reinforcement = DiscreteReinforcement(
                    n_bars_length=proposal.n_bars_length,
                    n_bars_thickness=proposal.n_bars_thickness,
                    diameter=proposal.diameter,
                )
            # Estribos/trabas segun propuesta (solo si no es strut)
            if proposal.stirrup_diameter > 0:
                # Solo actualizar si tienen valores por defecto
                if self.stirrup_diameter == 10 and self.stirrup_spacing == 150:
                    self.stirrup_diameter = proposal.stirrup_diameter
                    self.stirrup_spacing = proposal.stirrup_spacing
                if self.n_shear_legs == 2 and self.n_shear_legs_secondary is None:
                    self.n_shear_legs = proposal.n_shear_legs
                    if proposal.n_shear_legs_secondary != proposal.n_shear_legs:
                        self.n_shear_legs_secondary = proposal.n_shear_legs_secondary
            else:
                # Strut: sin estribos
                self.stirrup_diameter = 0
                self.stirrup_spacing = 0
                self.n_shear_legs = 0
            # Cover para columnas
            if self.source == VerticalElementSource.FRAME and self.cover == COVER_DEFAULT_PIER_MM:
                self.cover = COVER_DEFAULT_COLUMN_MM
        else:
            # MESH layout
            if self.mesh_reinforcement is None:
                self.mesh_reinforcement = MeshReinforcement(
                    n_meshes=MESH_DEFAULTS['n_meshes'],
                    diameter_v=MESH_DEFAULTS['diameter_v'],
                    spacing_v=MESH_DEFAULTS['spacing_v'],
                    diameter_h=MESH_DEFAULTS['diameter_h'],
                    spacing_h=MESH_DEFAULTS['spacing_h'],
                    n_edge_bars=MESH_DEFAULTS['n_edge_bars'],
                    diameter_edge=MESH_DEFAULTS['diameter_edge'],
                )
            # Cover para muros
            if self.source == VerticalElementSource.PIER and self.cover == COVER_DEFAULT_COLUMN_MM:
                self.cover = COVER_DEFAULT_PIER_MM

    # =========================================================================
    # Propiedades de Layout
    # =========================================================================

    @property
    def reinforcement_layout(self) -> ReinforcementLayout:
        """Tipo de armadura (STIRRUPS o MESH)."""
        if self._reinforcement_layout is None:
            # Fallback: usar proposer si no se inicializo
            from ..calculations.reinforcement_proposer import (
                ReinforcementProposer,
                ProposedLayout,
            )
            proposal = ReinforcementProposer.propose(self.length, self.thickness)
            if proposal.layout == ProposedLayout.MESH:
                self._reinforcement_layout = ReinforcementLayout.MESH
            else:
                self._reinforcement_layout = ReinforcementLayout.STIRRUPS
        return self._reinforcement_layout

    @property
    def is_stirrups_layout(self) -> bool:
        """True si usa armadura tipo estribos."""
        return self.reinforcement_layout == ReinforcementLayout.STIRRUPS

    @property
    def is_mesh_layout(self) -> bool:
        """True si usa armadura tipo malla."""
        return self.reinforcement_layout == ReinforcementLayout.MESH

    @property
    def is_frame_source(self) -> bool:
        """True si viene de Frame en ETABS."""
        return self.source == VerticalElementSource.FRAME

    @property
    def is_pier_source(self) -> bool:
        """True si viene de Pier/Shell en ETABS."""
        return self.source == VerticalElementSource.PIER

    # =========================================================================
    # Propiedades de Seccion Compuesta
    # =========================================================================

    @property
    def is_composite(self) -> bool:
        """True si tiene geometria compuesta (L, T, C)."""
        return self.composite_section is not None

    @property
    def shape_type(self) -> str:
        """Tipo de forma: rectangular, L, T, C, custom."""
        if self.composite_section:
            return self.composite_section.shape_type.value
        return "rectangular"

    # =========================================================================
    # Properties Semanticas (compatibilidad Column/Pier)
    # =========================================================================

    @property
    def depth(self) -> float:
        """Profundidad (compatibilidad Column). Para FRAME: dimension eje 2."""
        return self.length

    @property
    def width(self) -> float:
        """Ancho. Para FRAME: dimension eje 3. Para PIER: longitud del muro."""
        if self.source == VerticalElementSource.FRAME:
            return self.thickness
        return self.length  # Para PIER, width = lw

    @property
    def lw(self) -> float:
        """Longitud del muro (alias para PIER)."""
        return self.length

    @property
    def tw(self) -> float:
        """Espesor del muro (alias para PIER)."""
        return self.thickness

    # =========================================================================
    # Propiedades Geometricas
    # =========================================================================

    @property
    def Ag(self) -> float:
        """Area bruta de la seccion (mm2)."""
        if self.composite_section:
            return self.composite_section.Ag
        return self.length * self.thickness

    @property
    def d(self) -> float:
        """Profundidad efectiva (mm)."""
        return self.length - self.cover

    @property
    def d_length(self) -> float:
        """Profundidad efectiva en direccion length (mm)."""
        return self.length - self.cover

    @property
    def d_thickness(self) -> float:
        """Profundidad efectiva en direccion thickness (mm)."""
        return self.thickness - self.cover

    @property
    def is_square(self) -> bool:
        """True si es cuadrado."""
        return abs(self.length - self.thickness) < 1.0

    @property
    def lw_tw_ratio(self) -> float:
        """Razon lw/tw para clasificacion."""
        return self.length / self.thickness if self.thickness > 0 else 0

    # =========================================================================
    # Propiedades de Armadura
    # =========================================================================

    @property
    def As_longitudinal(self) -> float:
        """Area total de acero longitudinal (mm2)."""
        if self.is_stirrups_layout and self.discrete_reinforcement:
            return self.discrete_reinforcement.As_total
        elif self.is_mesh_layout and self.mesh_reinforcement:
            return self.As_edge_total + self.As_vertical
        return 0.0

    @property
    def As_flexure_total(self) -> float:
        """Area total de acero para flexion (mm2). Alias de As_longitudinal."""
        return self.As_longitudinal

    @property
    def rho_longitudinal(self) -> float:
        """Cuantia de acero longitudinal (As/Ag)."""
        return self.As_longitudinal / self.Ag if self.Ag > 0 else 0.0

    @property
    def n_total_bars(self) -> int:
        """Numero total de barras longitudinales."""
        if self.is_stirrups_layout and self.discrete_reinforcement:
            return self.discrete_reinforcement.n_total_bars
        elif self.is_mesh_layout:
            return self.n_total_vertical_bars
        return 0

    # =========================================================================
    # Propiedades STIRRUPS Layout (armadura discreta)
    # =========================================================================

    @property
    def n_bars_depth(self) -> int:
        """Barras en direccion depth/length (STIRRUPS)."""
        if self.discrete_reinforcement:
            return self.discrete_reinforcement.n_bars_length
        return 0

    @property
    def n_bars_width(self) -> int:
        """Barras en direccion width/thickness (STIRRUPS)."""
        if self.discrete_reinforcement:
            return self.discrete_reinforcement.n_bars_thickness
        return 0

    @property
    def diameter_long(self) -> int:
        """Diametro barras longitudinales (STIRRUPS)."""
        if self.discrete_reinforcement:
            return self.discrete_reinforcement.diameter
        return 20

    @property
    def n_stirrup_legs_depth(self) -> int:
        """Ramas de estribo en direccion depth/length."""
        return self.n_shear_legs

    @property
    def n_stirrup_legs_width(self) -> int:
        """Ramas de estribo en direccion width/thickness."""
        if self.n_shear_legs_secondary is not None:
            return self.n_shear_legs_secondary
        return self.n_shear_legs

    @property
    def As_transversal_depth(self) -> float:
        """Area de acero transversal en direccion depth (mm2)."""
        return self.n_stirrup_legs_depth * get_bar_area(self.stirrup_diameter)

    @property
    def As_transversal_width(self) -> float:
        """Area de acero transversal en direccion width (mm2)."""
        return self.n_stirrup_legs_width * get_bar_area(self.stirrup_diameter)

    # =========================================================================
    # Propiedades MESH Layout (armadura de malla)
    # =========================================================================

    @property
    def n_meshes(self) -> int:
        """Numero de mallas (MESH layout)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.n_meshes
        return 0

    @property
    def diameter_v(self) -> int:
        """Diametro barra vertical (MESH)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.diameter_v
        return 8

    @property
    def spacing_v(self) -> int:
        """Espaciamiento vertical (MESH)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.spacing_v
        return 200

    @property
    def diameter_h(self) -> int:
        """Diametro barra horizontal (MESH)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.diameter_h
        return 8

    @property
    def spacing_h(self) -> int:
        """Espaciamiento horizontal (MESH)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.spacing_h
        return 200

    @property
    def n_edge_bars(self) -> int:
        """Barras de borde por extremo (MESH)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.n_edge_bars
        return 0

    @property
    def diameter_edge(self) -> int:
        """Diametro barra de borde (MESH)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.diameter_edge
        return 12

    @property
    def n_intermediate_bars(self) -> int:
        """Numero de barras intermedias de malla (MESH)."""
        if not self.mesh_reinforcement:
            return 0
        available = self.length - 2 * self.cover
        if available <= 0:
            return 0
        return max(0, int(available / self.mesh_reinforcement.spacing_v))

    @property
    def As_vertical(self) -> float:
        """Area de acero vertical de malla intermedia (MESH, mm2)."""
        if not self.mesh_reinforcement:
            return 0.0
        return self.n_intermediate_bars * self.n_meshes * self.mesh_reinforcement._bar_area_v

    @property
    def As_horizontal(self) -> float:
        """Area de acero horizontal por metro de altura (MESH, mm2/m)."""
        if not self.mesh_reinforcement:
            return 0.0
        mr = self.mesh_reinforcement
        return mr.n_meshes * (mr._bar_area_h / mr.spacing_h) * 1000

    @property
    def As_vertical_per_m(self) -> float:
        """Area de acero vertical por metro de longitud (MESH, mm2/m)."""
        if not self.mesh_reinforcement:
            return 0.0
        mr = self.mesh_reinforcement
        spacing = mr.spacing_v or 200  # Default 200mm si es 0
        return mr.n_meshes * (mr._bar_area_v / spacing) * 1000

    @property
    def As_edge_total(self) -> float:
        """Area de acero de borde TOTAL (MESH, mm2)."""
        if not self.mesh_reinforcement:
            return 0.0
        mr = self.mesh_reinforcement
        return mr.n_edge_bars * 2 * mr._bar_area_edge

    @property
    def As_edge_per_end(self) -> float:
        """Area de acero de borde en cada extremo (MESH, mm2)."""
        if not self.mesh_reinforcement:
            return 0.0
        mr = self.mesh_reinforcement
        return mr.n_edge_bars * mr._bar_area_edge

    @property
    def n_total_vertical_bars(self) -> int:
        """Numero total de barras verticales (MESH)."""
        if not self.mesh_reinforcement:
            return 0
        n_edge = self.n_meshes * 2  # 2 extremos
        n_intermediate = self.n_intermediate_bars * self.n_meshes
        return n_edge + n_intermediate

    @property
    def rho_vertical(self) -> float:
        """Cuantia de acero vertical total (MESH)."""
        return (self.As_vertical + self.As_edge_total) / self.Ag if self.Ag > 0 else 0.0

    @property
    def rho_horizontal(self) -> float:
        """Cuantia de acero horizontal (MESH)."""
        if not self.mesh_reinforcement:
            return 0.0
        return self.As_horizontal / (self.thickness * 1000)

    @property
    def rho_mesh_vertical(self) -> float:
        """Cuantia de acero vertical de malla (sin incluir borde, MESH)."""
        if not self.mesh_reinforcement:
            return 0.0
        return self.As_vertical / self.Ag if self.Ag > 0 else 0.0

    # =========================================================================
    # Propiedades Especiales (unconfined, small_strut)
    # =========================================================================

    @property
    def is_unconfined(self) -> bool:
        """
        True si tiene refuerzo no confinado.

        Para STIRRUPS: 1 barra centrada sin estribos.
        Para MESH: malla simple sin estribos.
        """
        if self.is_stirrups_layout:
            if self.discrete_reinforcement:
                return (self.discrete_reinforcement.n_bars_length == 1 and
                        self.discrete_reinforcement.n_bars_thickness == 1)
        else:
            no_confinement = (self.stirrup_spacing == 0 or self.stirrup_diameter == 0)
            single_mesh = (self.n_meshes == 1)
            return no_confinement and single_mesh
        return False

    @property
    def is_small_strut(self) -> bool:
        """True si califica para diseno como strut pequeno (<150mm)."""
        from ..constants.chapter23 import SMALL_COLUMN_MAX_DIM_MM
        max_dim = max(self.length, self.thickness)
        return max_dim < SMALL_COLUMN_MAX_DIM_MM and self.is_unconfined

    # =========================================================================
    # Propiedades Sismicas
    # =========================================================================

    @property
    def lu_calculated(self) -> float:
        """Altura libre de la columna (mm)."""
        if self.lu is not None:
            return self.lu
        return self.height

    @property
    def hx(self) -> float:
        """Separacion maxima entre barras soportadas lateralmente (mm)."""
        if self.is_stirrups_layout and self.discrete_reinforcement:
            dr = self.discrete_reinforcement
            hx_length = self._calculate_hx_direction(self.length, dr.n_bars_length)
            hx_thickness = self._calculate_hx_direction(self.thickness, dr.n_bars_thickness)
            return max(hx_length, hx_thickness)
        return self.length - 2 * self.cover

    def _calculate_hx_direction(self, dimension: float, n_bars: int) -> float:
        """Calcula hx para una direccion."""
        if n_bars <= 1:
            return dimension - 2 * self.cover
        return (dimension - 2 * self.cover) / (n_bars - 1)

    @property
    def Ash_depth(self) -> float:
        """Area de refuerzo transversal perpendicular a depth (mm2)."""
        return self.As_transversal_depth

    @property
    def Ash_width(self) -> float:
        """Area de refuerzo transversal perpendicular a width (mm2)."""
        return self.As_transversal_width

    @property
    def bc_depth(self) -> float:
        """Dimension del nucleo confinado perpendicular a depth (mm)."""
        return self.length - 2 * self.cover

    @property
    def bc_width(self) -> float:
        """Dimension del nucleo confinado perpendicular a width (mm)."""
        return self.thickness - 2 * self.cover

    # =========================================================================
    # Propiedades PIER adicionales (zonas de borde)
    # =========================================================================

    @property
    def Ig(self) -> float:
        """Momento de inercia de la seccion bruta (mm4)."""
        if self.composite_section:
            return self.composite_section.Ixx
        return self.thickness * (self.length ** 3) / 12

    @property
    def y_extreme(self) -> float:
        """Distancia de la fibra extrema al eje neutro (mm)."""
        return self.length / 2

    @property
    def S(self) -> float:
        """Modulo de seccion elastico (mm3)."""
        return self.Ig / self.y_extreme if self.y_extreme > 0 else 0

    @property
    def Acv(self) -> float:
        """
        Area de cortante efectiva (mm2).

        Para secciones compuestas (L, T, C): solo area del alma segun ACI 318-25.
        Para secciones rectangulares: area bruta completa.
        """
        if self.composite_section:
            return self.composite_section.calculate_Acv('primary')
        return self.length * self.thickness

    @property
    def As_boundary_left(self) -> float:
        """Area de acero en zona de extremo izquierdo (0.15*lw) segun 18.10.2.4."""
        if not self.is_mesh_layout:
            return 0.0
        from ..calculations.wall_boundary_zone import WallBoundaryZoneService
        return WallBoundaryZoneService.calculate_steel_in_zone(self, is_left=True)

    @property
    def As_boundary_right(self) -> float:
        """Area de acero en zona de extremo derecho (0.15*lw) segun 18.10.2.4."""
        if not self.is_mesh_layout:
            return 0.0
        from ..calculations.wall_boundary_zone import WallBoundaryZoneService
        return WallBoundaryZoneService.calculate_steel_in_zone(self, is_left=False)

    # Propiedades para parsing de label PIER
    @property
    def grilla(self) -> str:
        """Extrae la grilla del label (ej: 'PMar' de 'PMar-C4-1')."""
        parts = self.label.split('-')
        return parts[0] if parts else ''

    @property
    def eje(self) -> str:
        """Extrae el eje del label (ej: 'C4' de 'PMar-C4-1')."""
        parts = self.label.split('-')
        return parts[1] if len(parts) > 1 else ''

    @property
    def pier_id(self) -> str:
        """Extrae el id del pier del label (ej: '1' de 'PMar-C4-1')."""
        parts = self.label.split('-')
        return parts[2] if len(parts) > 2 else '1'

    # =========================================================================
    # Deteccion de Strut
    # =========================================================================

    @property
    def is_strut(self) -> bool:
        """True si el elemento es un strut (ambas dimensiones < 15cm)."""
        from ..calculations.reinforcement_proposer import ReinforcementProposer, ProposedLayout
        proposal = ReinforcementProposer.propose(self.length, self.thickness)
        return proposal.layout == ProposedLayout.STRUT

    # =========================================================================
    # Descripcion de Armadura
    # =========================================================================

    @property
    def reinforcement_description(self) -> str:
        """Descripcion legible de la armadura."""
        # Caso strut: 1 barra centrada, sin estribos
        if self.is_strut and self.discrete_reinforcement:
            dr = self.discrete_reinforcement
            return f"1phi{dr.diameter} (strut)"

        if self.is_stirrups_layout and self.discrete_reinforcement:
            dr = self.discrete_reinforcement
            return (
                f"{dr.n_total_bars}phi{dr.diameter} "
                f"E{self.stirrup_diameter}@{self.stirrup_spacing}"
            )
        elif self.is_mesh_layout and self.mesh_reinforcement:
            mr = self.mesh_reinforcement
            mesh_text = "1M" if mr.n_meshes == 1 else "2M"
            edge_text = f"+{mr.n_edge_bars}phi{mr.diameter_edge}"
            stirrup_text = f"E{self.stirrup_diameter}@{self.stirrup_spacing}"
            return f"{mesh_text} phi{mr.diameter_v}@{mr.spacing_v} {edge_text} {stirrup_text}"
        return "Sin armadura definida"

    # =========================================================================
    # Metodos de Actualizacion
    # =========================================================================

    def update_reinforcement(
        self,
        # Comun
        stirrup_diameter: Optional[int] = None,
        stirrup_spacing: Optional[int] = None,
        n_shear_legs: Optional[int] = None,
        n_shear_legs_secondary: Optional[int] = None,
        fy: Optional[float] = None,
        cover: Optional[float] = None,
        # STIRRUPS layout
        n_bars_depth: Optional[int] = None,
        n_bars_width: Optional[int] = None,
        diameter_long: Optional[int] = None,
        # MESH layout
        n_meshes: Optional[int] = None,
        diameter_v: Optional[int] = None,
        spacing_v: Optional[int] = None,
        diameter_h: Optional[int] = None,
        spacing_h: Optional[int] = None,
        diameter_edge: Optional[int] = None,
        n_edge_bars: Optional[int] = None,
        # Geometria
        thickness: Optional[float] = None,
        # Categoria
        seismic_category: Optional[str] = None
    ):
        """Actualiza la configuracion de armadura."""
        # Comun
        if stirrup_diameter is not None:
            self.stirrup_diameter = stirrup_diameter
        if stirrup_spacing is not None:
            self.stirrup_spacing = stirrup_spacing
        if n_shear_legs is not None:
            self.n_shear_legs = n_shear_legs
        if n_shear_legs_secondary is not None:
            self.n_shear_legs_secondary = n_shear_legs_secondary
        if fy is not None:
            self.fy = fy
        if cover is not None:
            self.cover = cover
        if thickness is not None:
            self.thickness = thickness
        if seismic_category is not None:
            self.seismic_category = seismic_category

        # STIRRUPS layout
        if self.discrete_reinforcement:
            dr = self.discrete_reinforcement
            if n_bars_depth is not None:
                dr.n_bars_length = n_bars_depth
            if n_bars_width is not None:
                dr.n_bars_thickness = n_bars_width
            if diameter_long is not None:
                dr.diameter = diameter_long
                dr._bar_area = get_bar_area(diameter_long, 314.2)

        # MESH layout
        if self.mesh_reinforcement:
            mr = self.mesh_reinforcement
            if n_meshes is not None:
                mr.n_meshes = n_meshes
            if diameter_v is not None:
                mr.diameter_v = diameter_v
                mr._bar_area_v = get_bar_area(diameter_v, 50.3)
            if spacing_v is not None:
                mr.spacing_v = spacing_v
            if diameter_h is not None:
                mr.diameter_h = diameter_h
                mr._bar_area_h = get_bar_area(diameter_h, 50.3)
            if spacing_h is not None:
                mr.spacing_h = spacing_h
            if diameter_edge is not None:
                mr.diameter_edge = diameter_edge
                mr._bar_area_edge = get_bar_area(diameter_edge, 113.1)
            if n_edge_bars is not None:
                mr.n_edge_bars = n_edge_bars

    # =========================================================================
    # Metodos para FlexuralElement Protocol
    # =========================================================================

    def get_steel_layers(self, direction: str = 'primary') -> List['SteelLayer']:
        """
        Genera las capas de acero para el diagrama de interaccion.

        Args:
            direction: 'primary' para eje fuerte, 'secondary' para eje debil

        Returns:
            Lista de SteelLayer ordenadas por posicion.
        """
        from ..calculations.steel_layer_calculator import SteelLayerCalculator

        if self.is_stirrups_layout:
            return SteelLayerCalculator.calculate_from_vertical_element_discrete(
                self, direction=direction
            )
        else:
            return SteelLayerCalculator.calculate_from_vertical_element_mesh(self)

    def get_section_dimensions(self, direction: str = 'primary') -> Tuple[float, float]:
        """
        Obtiene las dimensiones de la seccion para la curva P-M.

        Args:
            direction: 'primary' o 'secondary'

        Returns:
            Tuple (width, thickness) en mm
        """
        if direction == 'primary':
            return (self.length, self.thickness)
        else:
            return (self.thickness, self.length)

    # =========================================================================
    # Serializacion
    # =========================================================================

    def to_dict(self) -> dict:
        """Serializa el elemento a diccionario."""
        data = {
            'label': self.label,
            'story': self.story,
            'length': self.length,
            'thickness': self.thickness,
            'height': self.height,
            'fc': self.fc,
            'fy': self.fy,
            'source': self.source.value,
            'section_name': self.section_name,
            'reinforcement_layout': self.reinforcement_layout.value,
            'stirrup_diameter': self.stirrup_diameter,
            'stirrup_spacing': self.stirrup_spacing,
            'n_shear_legs': self.n_shear_legs,
            'n_shear_legs_secondary': self.n_shear_legs_secondary,
            'cover': self.cover,
            'is_seismic': self.is_seismic,
            'seismic_category': self.seismic_category,
            'axis_angle': self.axis_angle,
        }

        if self.is_stirrups_layout and self.discrete_reinforcement:
            dr = self.discrete_reinforcement
            data['discrete_reinforcement'] = {
                'n_bars_length': dr.n_bars_length,
                'n_bars_thickness': dr.n_bars_thickness,
                'diameter': dr.diameter,
            }
            # Campos FRAME
            data['Mnc_top'] = self.Mnc_top
            data['Mnc_bottom'] = self.Mnc_bottom
            data['sum_Mnb_major'] = self.sum_Mnb_major
            data['sum_Mnb_minor'] = self.sum_Mnb_minor
            data['lu'] = self.lu

        elif self.is_mesh_layout and self.mesh_reinforcement:
            mr = self.mesh_reinforcement
            data['mesh_reinforcement'] = {
                'n_meshes': mr.n_meshes,
                'diameter_v': mr.diameter_v,
                'spacing_v': mr.spacing_v,
                'diameter_h': mr.diameter_h,
                'spacing_h': mr.spacing_h,
                'n_edge_bars': mr.n_edge_bars,
                'diameter_edge': mr.diameter_edge,
            }

        # Seccion compuesta
        if self.composite_section:
            data['composite_section'] = self.composite_section.to_dict()
            data['shape_type'] = self.shape_type

        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'VerticalElement':
        """Deserializa un elemento desde diccionario."""
        source = VerticalElementSource(data.get('source', 'frame'))

        # Armadura segun layout
        discrete_reinforcement = None
        mesh_reinforcement = None

        dr_data = data.get('discrete_reinforcement')
        mr_data = data.get('mesh_reinforcement')

        if dr_data:
            discrete_reinforcement = DiscreteReinforcement(
                n_bars_length=dr_data.get('n_bars_length', 3),
                n_bars_thickness=dr_data.get('n_bars_thickness', 3),
                diameter=dr_data.get('diameter', 20),
            )
        if mr_data:
            mesh_reinforcement = MeshReinforcement(
                n_meshes=mr_data.get('n_meshes', 2),
                diameter_v=mr_data.get('diameter_v', 8),
                spacing_v=mr_data.get('spacing_v', 200),
                diameter_h=mr_data.get('diameter_h', 8),
                spacing_h=mr_data.get('spacing_h', 200),
                n_edge_bars=mr_data.get('n_edge_bars', 2),
                diameter_edge=mr_data.get('diameter_edge', 12),
            )

        return cls(
            label=data['label'],
            story=data['story'],
            length=data['length'],
            thickness=data['thickness'],
            height=data['height'],
            fc=data['fc'],
            fy=data.get('fy', FY_DEFAULT_MPA),
            source=source,
            section_name=data.get('section_name', ''),
            discrete_reinforcement=discrete_reinforcement,
            mesh_reinforcement=mesh_reinforcement,
            stirrup_diameter=data.get('stirrup_diameter', 10),
            stirrup_spacing=data.get('stirrup_spacing', 150),
            n_shear_legs=data.get('n_shear_legs', 2),
            n_shear_legs_secondary=data.get('n_shear_legs_secondary'),
            cover=data.get('cover', COVER_DEFAULT_COLUMN_MM),
            is_seismic=data.get('is_seismic', True),
            seismic_category=data.get('seismic_category'),
            Mnc_top=data.get('Mnc_top'),
            Mnc_bottom=data.get('Mnc_bottom'),
            sum_Mnb_major=data.get('sum_Mnb_major'),
            sum_Mnb_minor=data.get('sum_Mnb_minor'),
            lu=data.get('lu'),
            axis_angle=data.get('axis_angle', 0.0),
        )
