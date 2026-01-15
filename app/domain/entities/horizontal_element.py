# app/domain/entities/horizontal_element.py
"""
Entidad HorizontalElement: representa un elemento horizontal (viga) de hormigon armado.

Soporta tres tipos:
- FRAME: vigas de portico (Element Forces - Beams)
- SPANDREL: vigas de acople tipo shell (Spandrel Forces)
- DROP_BEAM: vigas capitel (losas disenadas como vigas)
"""
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, TYPE_CHECKING
from enum import Enum

from ..constants.materials import get_bar_area
from ..constants.reinforcement import FY_DEFAULT_MPA, COVER_DEFAULT_BEAM_MM
from .reinforcement import MeshReinforcement, BeamReinforcement

if TYPE_CHECKING:
    from ..flexure import SteelLayer


class HorizontalElementSource(Enum):
    """Origen del elemento horizontal."""
    FRAME = "frame"           # Viga de portico
    SPANDREL = "spandrel"     # Viga de acople tipo shell
    DROP_BEAM = "drop_beam"   # Viga capitel (losa disenada como viga)


class HorizontalElementShape(Enum):
    """Forma de la seccion transversal."""
    RECTANGULAR = "rectangular"
    CIRCULAR = "circular"


# Aliases para compatibilidad - las clases ahora están en reinforcement.py
HorizontalMeshReinforcement = MeshReinforcement
HorizontalDiscreteReinforcement = BeamReinforcement


@dataclass
class HorizontalElement:
    """
    Representa un elemento horizontal (viga) de hormigon armado.

    Unidades:
    - Dimensiones: mm
    - Esfuerzos: MPa
    - Areas: mm2

    Soporta tres tipos (source):
    - FRAME: vigas modeladas como elementos lineales
    - SPANDREL: vigas de acople modeladas como shells
    - DROP_BEAM: vigas capitel (losas con armadura de malla)
    """
    label: str              # "B1", "S1", "CL - C3"
    story: str              # "Story4"

    # Geometria (mm)
    length: float           # Luz de la viga
    depth: float            # Altura/peralte (para DROP_BEAM = thickness)
    width: float            # Ancho

    # Propiedades del material (MPa)
    fc: float               # f'c del hormigon
    fy: float = FY_DEFAULT_MPA

    # Origen del elemento (discriminador principal)
    source: HorizontalElementSource = HorizontalElementSource.FRAME

    # Forma de la seccion
    shape: HorizontalElementShape = HorizontalElementShape.RECTANGULAR

    # Seccion ETABS
    section_name: str = ""

    # Armadura transversal (común a todos los tipos)
    stirrup_diameter: int = 10
    stirrup_spacing: int = 150
    n_stirrup_legs: int = 2

    # Armadura longitudinal - depende del tipo
    # Para FRAME/SPANDREL: usa discrete_reinforcement
    # Para DROP_BEAM: usa mesh_reinforcement
    discrete_reinforcement: Optional[HorizontalDiscreteReinforcement] = None
    mesh_reinforcement: Optional[HorizontalMeshReinforcement] = None

    # Otros
    cover: float = 40.0
    is_seismic: bool = True
    is_custom: bool = False

    # Geometria sismica §18.6 (FRAME/SPANDREL)
    ln: Optional[float] = None
    column_depth_left: float = 0
    column_depth_right: float = 0
    Mpr_left: Optional[float] = None
    Mpr_right: Optional[float] = None

    # Campos específicos DROP_BEAM (para compatibilidad)
    axis_slab: str = ""     # Eje de la losa
    location: str = ""      # Ubicación
    axis_angle: float = 0.0

    # Areas de barra precalculadas
    _bar_area_stirrup: float = field(default=78.5, repr=False)

    def __post_init__(self):
        """Inicializa armadura y valida geometria."""
        # Validar geometria
        if self.depth <= 0:
            raise ValueError(f"HorizontalElement {self.label}: depth debe ser > 0, recibido {self.depth}")
        if self.width <= 0:
            raise ValueError(f"HorizontalElement {self.label}: width debe ser > 0, recibido {self.width}")
        if self.length <= 0:
            raise ValueError(f"HorizontalElement {self.label}: length debe ser > 0, recibido {self.length}")

        self._bar_area_stirrup = get_bar_area(self.stirrup_diameter, 78.5)

        # Inicializar armadura segun tipo si no se proporciono
        if self.source == HorizontalElementSource.DROP_BEAM:
            if self.mesh_reinforcement is None:
                # Defaults específicos para vigas capitel (phi12@200)
                self.mesh_reinforcement = MeshReinforcement(
                    diameter_v=12,
                    diameter_h=10,
                    n_edge_bars=4,
                    diameter_edge=16,
                )
            # Cover default para DROP_BEAM es 25mm
            if self.cover == 40.0:
                self.cover = 25.0
        else:
            if self.discrete_reinforcement is None:
                self.discrete_reinforcement = BeamReinforcement()

    # =========================================================================
    # Propiedades de Tipo
    # =========================================================================

    @property
    def is_drop_beam(self) -> bool:
        """True si es viga capitel."""
        return self.source == HorizontalElementSource.DROP_BEAM

    @property
    def is_spandrel(self) -> bool:
        """True si es spandrel (viga de acople)."""
        return self.source == HorizontalElementSource.SPANDREL

    @property
    def is_frame(self) -> bool:
        """True si es viga de portico."""
        return self.source == HorizontalElementSource.FRAME

    # =========================================================================
    # Propiedades de Armadura (común)
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
        """Descripcion legible de la armadura."""
        if self.is_drop_beam and self.mesh_reinforcement:
            mr = self.mesh_reinforcement
            mesh_text = "1M" if mr.n_meshes == 1 else "2M"
            edge_text = f"+{mr.n_edge_bars}phi{mr.diameter_edge}"
            stirrup_text = f"E{self.stirrup_diameter}@{self.stirrup_spacing}"
            return f"{mesh_text} phi{mr.diameter_v}@{mr.spacing_v} {edge_text} {stirrup_text}"
        else:
            legs = f"{self.n_stirrup_legs}R" if self.n_stirrup_legs > 2 else ""
            return f"{legs}E{self.stirrup_diameter}@{self.stirrup_spacing}"

    # =========================================================================
    # Propiedades de Armadura (FRAME/SPANDREL)
    # =========================================================================

    @property
    def n_bars_top(self) -> int:
        """Barras superiores (FRAME/SPANDREL)."""
        if self.discrete_reinforcement:
            return self.discrete_reinforcement.n_bars_top
        return 0

    @property
    def n_bars_bottom(self) -> int:
        """Barras inferiores (FRAME/SPANDREL)."""
        if self.discrete_reinforcement:
            return self.discrete_reinforcement.n_bars_bottom
        return 0

    @property
    def diameter_top(self) -> int:
        """Diámetro barras superiores (FRAME/SPANDREL)."""
        if self.discrete_reinforcement:
            return self.discrete_reinforcement.diameter_top
        return 16

    @property
    def diameter_bottom(self) -> int:
        """Diámetro barras inferiores (FRAME/SPANDREL)."""
        if self.discrete_reinforcement:
            return self.discrete_reinforcement.diameter_bottom
        return 16

    @property
    def As_top(self) -> float:
        """Area de acero superior (mm2)."""
        return self.n_bars_top * get_bar_area(self.diameter_top)

    @property
    def As_bottom(self) -> float:
        """Area de acero inferior (mm2)."""
        return self.n_bars_bottom * get_bar_area(self.diameter_bottom)

    # =========================================================================
    # Propiedades de Armadura (DROP_BEAM - malla)
    # =========================================================================

    @property
    def n_meshes(self) -> int:
        """Número de mallas (DROP_BEAM)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.n_meshes
        return 0

    @property
    def n_edge_bars(self) -> int:
        """Barras de borde por extremo (DROP_BEAM)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.n_edge_bars
        return 0

    @property
    def diameter_edge(self) -> int:
        """Diámetro barra de borde (DROP_BEAM, mm)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.diameter_edge
        return 16

    @property
    def As_edge_total(self) -> float:
        """Área de acero de borde TOTAL (DROP_BEAM, mm²)."""
        if not self.mesh_reinforcement:
            return 0.0
        mr = self.mesh_reinforcement
        return mr.n_edge_bars * 2 * mr._bar_area_edge

    @property
    def As_vertical(self) -> float:
        """Área de acero vertical de malla (DROP_BEAM, mm²)."""
        if not self.mesh_reinforcement:
            return 0.0
        mr = self.mesh_reinforcement
        # Barras intermedias entre los bordes
        available_length = self.depth - 2 * self.cover
        if available_length <= 0:
            return 0.0
        n_intermediate = max(0, int(available_length / mr.spacing_v))
        return n_intermediate * mr.n_meshes * mr._bar_area_v

    @property
    def rho_vertical(self) -> float:
        """Cuantía vertical (DROP_BEAM)."""
        if not self.is_drop_beam:
            return 0.0
        return (self.As_vertical + self.As_edge_total) / self.Ag

    @property
    def rho_horizontal(self) -> float:
        """Cuantía horizontal (DROP_BEAM)."""
        if not self.mesh_reinforcement:
            return 0.0
        mr = self.mesh_reinforcement
        As_h = mr.n_meshes * (mr._bar_area_h / mr.spacing_h) * 1000
        return As_h / (self.width * 1000)

    @property
    def rho_mesh_vertical(self) -> float:
        """Cuantía vertical de malla (sin incluir borde, DROP_BEAM)."""
        if not self.is_drop_beam or not self.mesh_reinforcement:
            return 0.0
        return self.As_vertical / self.Ag if self.Ag > 0 else 0.0

    @property
    def diameter_v(self) -> int:
        """Diámetro barra vertical de malla (DROP_BEAM, mm)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.diameter_v
        return 12

    @property
    def spacing_v(self) -> int:
        """Espaciamiento vertical de malla (DROP_BEAM, mm)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.spacing_v
        return 200

    @property
    def diameter_h(self) -> int:
        """Diámetro barra horizontal de malla (DROP_BEAM, mm)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.diameter_h
        return 10

    @property
    def spacing_h(self) -> int:
        """Espaciamiento horizontal de malla (DROP_BEAM, mm)."""
        if self.mesh_reinforcement:
            return self.mesh_reinforcement.spacing_h
        return 200

    @property
    def As_horizontal(self) -> float:
        """Área de acero horizontal por metro de altura (DROP_BEAM, mm²/m)."""
        if not self.mesh_reinforcement:
            return 0.0
        mr = self.mesh_reinforcement
        return mr.n_meshes * (mr._bar_area_h / mr.spacing_h) * 1000

    # =========================================================================
    # Propiedades Geometricas
    # =========================================================================

    @property
    def Ag(self) -> float:
        """Area bruta de la viga (mm2)."""
        if self.shape == HorizontalElementShape.CIRCULAR:
            import math
            return math.pi * (self.depth / 2) ** 2
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
    def is_unconfined(self) -> bool:
        """True si tiene refuerzo mínimo sin estribos."""
        if self.is_drop_beam:
            return False  # DROP_BEAM siempre tiene malla
        has_minimal_bars = (self.n_bars_top <= 1 and self.n_bars_bottom <= 1)
        no_stirrups = (self.stirrup_spacing == 0 or self.stirrup_diameter == 0)
        return has_minimal_bars and no_stirrups

    @property
    def is_small_strut(self) -> bool:
        """True si califica como strut pequeño (<150mm)."""
        from ..constants.chapter23 import SMALL_COLUMN_MAX_DIM_MM
        max_dim = max(self.depth, self.width)
        return max_dim < SMALL_COLUMN_MAX_DIM_MM and self.is_unconfined

    @property
    def is_circular(self) -> bool:
        """True si es seccion circular."""
        return self.shape == HorizontalElementShape.CIRCULAR

    @property
    def diameter(self) -> float:
        """Diametro para secciones circulares (mm)."""
        return self.depth

    @property
    def height(self) -> float:
        """Altura (usa length de la viga)."""
        return self.length

    # Propiedades geométricas adicionales para DROP_BEAM
    @property
    def thickness(self) -> float:
        """Alias para compatibilidad con DropBeam (=depth)."""
        return self.depth

    @property
    def Ig(self) -> float:
        """Momento de inercia (mm⁴). Principalmente para DROP_BEAM."""
        return self.width * (self.depth ** 3) / 12

    @property
    def y_extreme(self) -> float:
        """Distancia fibra extrema al eje neutro (mm)."""
        return self.depth / 2

    @property
    def S(self) -> float:
        """Módulo de sección elástico (mm³)."""
        return self.Ig / self.y_extreme if self.y_extreme > 0 else 0

    # =========================================================================
    # Propiedades Sismicas §18.6
    # =========================================================================

    @property
    def ln_calculated(self) -> float:
        """Luz libre (mm) segun §18.6.2.1."""
        if self.ln is not None:
            return self.ln
        return self.length - self.column_depth_left / 2 - self.column_depth_right / 2

    @property
    def hx(self) -> float:
        """Separacion maxima entre barras soportadas (mm)."""
        n_bars = max(self.n_bars_top, self.n_bars_bottom)
        if n_bars <= 1:
            return self.width - 2 * self.cover
        return (self.width - 2 * self.cover) / (n_bars - 1)

    # =========================================================================
    # FlexuralElement Protocol
    # =========================================================================

    @property
    def As_flexure_total(self) -> float:
        """Area total de acero longitudinal (mm2)."""
        if self.is_drop_beam:
            return self.As_edge_total + self.As_vertical
        return self.As_top + self.As_bottom

    def get_steel_layers(self, direction: str = 'primary') -> List['SteelLayer']:
        """Capas de acero para diagrama de interaccion."""
        if self.is_drop_beam:
            from ..calculations.steel_layer_calculator import SteelLayerCalculator
            return SteelLayerCalculator.calculate_from_horizontal_element_drop(self)

        from ..calculations.steel_layer_calculator import SteelLayer

        d_top = self.cover + self.diameter_top / 2
        As_top = self.n_bars_top * get_bar_area(self.diameter_top)

        d_bottom = self.depth - self.cover - self.diameter_bottom / 2
        As_bottom = self.n_bars_bottom * get_bar_area(self.diameter_bottom)

        return [
            SteelLayer(d_top, As_top),
            SteelLayer(d_bottom, As_bottom)
        ]

    def get_section_dimensions(self, direction: str = 'primary') -> Tuple[float, float]:
        """Dimensiones para curva P-M: (depth, width)."""
        if self.is_drop_beam:
            if direction == 'primary':
                return (self.depth, self.width)
            else:
                return (self.width, self.depth)
        return (self.depth, self.width)

    # =========================================================================
    # Metodos de Actualizacion
    # =========================================================================

    def update_reinforcement(
        self,
        stirrup_diameter: Optional[int] = None,
        stirrup_spacing: Optional[int] = None,
        n_stirrup_legs: Optional[int] = None,
        # FRAME/SPANDREL
        n_bars_top: Optional[int] = None,
        n_bars_bottom: Optional[int] = None,
        diameter_top: Optional[int] = None,
        diameter_bottom: Optional[int] = None,
        # DROP_BEAM
        n_meshes: Optional[int] = None,
        diameter_v: Optional[int] = None,
        spacing_v: Optional[int] = None,
        diameter_h: Optional[int] = None,
        spacing_h: Optional[int] = None,
        diameter_edge: Optional[int] = None,
        n_edge_bars: Optional[int] = None,
        # Común
        fy: Optional[float] = None,
        cover: Optional[float] = None
    ):
        """Actualiza la configuracion de armadura."""
        # Común
        if stirrup_diameter is not None:
            self.stirrup_diameter = stirrup_diameter
            self._bar_area_stirrup = get_bar_area(stirrup_diameter, 78.5)
        if stirrup_spacing is not None:
            self.stirrup_spacing = stirrup_spacing
        if n_stirrup_legs is not None:
            self.n_stirrup_legs = n_stirrup_legs
        if fy is not None:
            self.fy = fy
        if cover is not None:
            self.cover = cover

        # FRAME/SPANDREL
        if self.discrete_reinforcement:
            if n_bars_top is not None:
                self.discrete_reinforcement.n_bars_top = n_bars_top
            if n_bars_bottom is not None:
                self.discrete_reinforcement.n_bars_bottom = n_bars_bottom
            if diameter_top is not None:
                self.discrete_reinforcement.diameter_top = diameter_top
            if diameter_bottom is not None:
                self.discrete_reinforcement.diameter_bottom = diameter_bottom

        # DROP_BEAM
        if self.mesh_reinforcement:
            mr = self.mesh_reinforcement
            if n_meshes is not None:
                mr.n_meshes = n_meshes
            if diameter_v is not None:
                mr.diameter_v = diameter_v
                mr._bar_area_v = get_bar_area(diameter_v, 113.1)
            if spacing_v is not None:
                mr.spacing_v = spacing_v
            if diameter_h is not None:
                mr.diameter_h = diameter_h
                mr._bar_area_h = get_bar_area(diameter_h, 78.5)
            if spacing_h is not None:
                mr.spacing_h = spacing_h
            if diameter_edge is not None:
                mr.diameter_edge = diameter_edge
                mr._bar_area_edge = get_bar_area(diameter_edge, 201.1)
            if n_edge_bars is not None:
                mr.n_edge_bars = n_edge_bars

    # =========================================================================
    # Serialización
    # =========================================================================

    def to_dict(self) -> dict:
        """Serializa el elemento a diccionario."""
        data = {
            'label': self.label,
            'story': self.story,
            'length': self.length,
            'depth': self.depth,
            'width': self.width,
            'fc': self.fc,
            'fy': self.fy,
            'source': self.source.value,
            'shape': self.shape.value,
            'section_name': self.section_name,
            'stirrup_diameter': self.stirrup_diameter,
            'stirrup_spacing': self.stirrup_spacing,
            'n_stirrup_legs': self.n_stirrup_legs,
            'cover': self.cover,
            'is_seismic': self.is_seismic,
            'is_custom': self.is_custom,
        }

        if self.source == HorizontalElementSource.DROP_BEAM and self.mesh_reinforcement:
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
            data['axis_slab'] = self.axis_slab
            data['location'] = self.location
            data['axis_angle'] = self.axis_angle
        else:
            if self.discrete_reinforcement:
                dr = self.discrete_reinforcement
                data['discrete_reinforcement'] = {
                    'n_bars_top': dr.n_bars_top,
                    'n_bars_bottom': dr.n_bars_bottom,
                    'diameter_top': dr.diameter_top,
                    'diameter_bottom': dr.diameter_bottom,
                }
            data['ln'] = self.ln
            data['column_depth_left'] = self.column_depth_left
            data['column_depth_right'] = self.column_depth_right
            data['Mpr_left'] = self.Mpr_left
            data['Mpr_right'] = self.Mpr_right

        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'HorizontalElement':
        """Deserializa un elemento desde diccionario."""
        source = HorizontalElementSource(data.get('source', data.get('beam_type', 'frame')))
        shape = HorizontalElementShape(data.get('shape', 'rectangular'))

        # Armadura segun tipo
        discrete_reinforcement = None
        mesh_reinforcement = None

        if source == HorizontalElementSource.DROP_BEAM:
            mr_data = data.get('mesh_reinforcement', {})
            mesh_reinforcement = HorizontalMeshReinforcement(
                n_meshes=mr_data.get('n_meshes', 2),
                diameter_v=mr_data.get('diameter_v', 12),
                spacing_v=mr_data.get('spacing_v', 200),
                diameter_h=mr_data.get('diameter_h', 10),
                spacing_h=mr_data.get('spacing_h', 200),
                n_edge_bars=mr_data.get('n_edge_bars', 4),
                diameter_edge=mr_data.get('diameter_edge', 16),
            )
        else:
            dr_data = data.get('discrete_reinforcement', {})
            discrete_reinforcement = HorizontalDiscreteReinforcement(
                n_bars_top=dr_data.get('n_bars_top', 3),
                n_bars_bottom=dr_data.get('n_bars_bottom', 3),
                diameter_top=dr_data.get('diameter_top', 16),
                diameter_bottom=dr_data.get('diameter_bottom', 16),
            )

        return cls(
            label=data['label'],
            story=data['story'],
            length=data['length'],
            depth=data['depth'],
            width=data['width'],
            fc=data['fc'],
            fy=data.get('fy', FY_DEFAULT_MPA),
            source=source,
            shape=shape,
            section_name=data.get('section_name', ''),
            stirrup_diameter=data.get('stirrup_diameter', 10),
            stirrup_spacing=data.get('stirrup_spacing', 150),
            n_stirrup_legs=data.get('n_stirrup_legs', 2),
            discrete_reinforcement=discrete_reinforcement,
            mesh_reinforcement=mesh_reinforcement,
            cover=data.get('cover', 40.0),
            is_seismic=data.get('is_seismic', True),
            is_custom=data.get('is_custom', False),
            ln=data.get('ln'),
            column_depth_left=data.get('column_depth_left', 0),
            column_depth_right=data.get('column_depth_right', 0),
            Mpr_left=data.get('Mpr_left'),
            Mpr_right=data.get('Mpr_right'),
            axis_slab=data.get('axis_slab', ''),
            location=data.get('location', ''),
            axis_angle=data.get('axis_angle', 0.0),
        )
