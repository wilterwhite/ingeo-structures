# app/domain/entities/composite_section.py
"""
Entidades para representar secciones compuestas de piers (L, T, C).

Un pier compuesto se forma de múltiples segmentos rectangulares conectados.
Esta estructura permite calcular propiedades de sección (Ag, centroide, Ixx, Iyy, Acv)
para geometrías no rectangulares según ACI 318-25.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import math


class SectionShapeType(Enum):
    """Tipo de forma de la sección compuesta."""
    RECTANGULAR = "rectangular"
    L_SHAPE = "L"
    T_SHAPE = "T"
    C_SHAPE = "C"
    CUSTOM = "custom"


@dataclass
class WallSegment:
    """
    Un segmento rectangular de un pier compuesto.

    Representa una porción rectangular del muro definida por su línea central
    (de x1,y1 a x2,y2) y su espesor perpendicular.

    Unidades: mm
    """
    # Línea central del segmento
    x1: float  # Coordenada X del punto inicial
    y1: float  # Coordenada Y del punto inicial
    x2: float  # Coordenada X del punto final
    y2: float  # Coordenada Y del punto final
    thickness: float  # Espesor perpendicular a la línea central

    # Identificador opcional del muro original
    wall_id: Optional[int] = None

    @property
    def length(self) -> float:
        """Longitud del segmento (distancia entre puntos)."""
        return math.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)

    @property
    def area(self) -> float:
        """Área del segmento = longitud × espesor."""
        return self.length * self.thickness

    @property
    def centroid(self) -> Tuple[float, float]:
        """Centroide del segmento (punto medio de la línea central)."""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    @property
    def orientation(self) -> str:
        """
        Orientación del segmento: 'horizontal', 'vertical' o 'diagonal'.

        Tolerancia de 5 grados para considerar horizontal/vertical.
        """
        dx = abs(self.x2 - self.x1)
        dy = abs(self.y2 - self.y1)

        if self.length < 1e-6:
            return 'point'

        angle = math.atan2(dy, dx)
        angle_deg = math.degrees(angle)

        if angle_deg < 5 or angle_deg > 175:
            return 'horizontal'
        elif 85 < angle_deg < 95:
            return 'vertical'
        else:
            return 'diagonal'

    @property
    def angle_rad(self) -> float:
        """Ángulo del segmento respecto al eje X, en radianes."""
        return math.atan2(self.y2 - self.y1, self.x2 - self.x1)

    @property
    def Ixx_local(self) -> float:
        """
        Momento de inercia local respecto al eje X del segmento.

        Para un rectángulo: I = b*h³/12
        Donde b = thickness, h = length (asumiendo eje X paralelo a length)
        """
        # Inercia respecto al eje que pasa por el centroide del segmento
        # perpendicular a la longitud
        return self.thickness * (self.length ** 3) / 12

    @property
    def Iyy_local(self) -> float:
        """
        Momento de inercia local respecto al eje Y del segmento.

        Para un rectángulo: I = h*b³/12
        Donde b = thickness, h = length
        """
        return self.length * (self.thickness ** 3) / 12

    def get_corners(self) -> List[Tuple[float, float]]:
        """
        Obtiene las 4 esquinas del rectángulo del segmento.

        Returns:
            Lista de 4 tuplas (x, y) en orden antihorario.
        """
        # Vector unitario en la dirección del segmento
        length = self.length
        if length < 1e-6:
            return [(self.x1, self.y1)] * 4

        dx = (self.x2 - self.x1) / length
        dy = (self.y2 - self.y1) / length

        # Vector perpendicular (rotado 90 grados)
        nx = -dy
        ny = dx

        # Offset perpendicular = thickness / 2
        half_t = self.thickness / 2

        # 4 esquinas
        corners = [
            (self.x1 + nx * half_t, self.y1 + ny * half_t),
            (self.x2 + nx * half_t, self.y2 + ny * half_t),
            (self.x2 - nx * half_t, self.y2 - ny * half_t),
            (self.x1 - nx * half_t, self.y1 - ny * half_t),
        ]
        return corners


@dataclass
class CompositeSection:
    """
    Sección compuesta de múltiples segmentos rectangulares.

    Representa la geometría de un pier con forma L, T, C u otra forma
    compuesta por segmentos rectangulares conectados.

    Unidades: mm para dimensiones, mm² para áreas, mm⁴ para inercias.
    """
    segments: List[WallSegment]
    shape_type: SectionShapeType = field(default=SectionShapeType.CUSTOM)

    # Cache de propiedades calculadas
    _Ag: Optional[float] = field(default=None, repr=False)
    _centroid: Optional[Tuple[float, float]] = field(default=None, repr=False)
    _Ixx: Optional[float] = field(default=None, repr=False)
    _Iyy: Optional[float] = field(default=None, repr=False)

    def __post_init__(self):
        """Detecta automáticamente el tipo de forma si no se especificó."""
        if self.shape_type == SectionShapeType.CUSTOM and len(self.segments) > 1:
            self.shape_type = self.detect_shape(self.segments)

    @property
    def Ag(self) -> float:
        """Área bruta total de la sección compuesta."""
        if self._Ag is None:
            self._Ag = sum(s.area for s in self.segments)
        return self._Ag

    @property
    def centroid(self) -> Tuple[float, float]:
        """
        Centroide de la sección compuesta.

        Calculado como: x_c = Σ(Ai × xi) / Σ(Ai)
        """
        if self._centroid is None:
            if not self.segments:
                self._centroid = (0.0, 0.0)
            else:
                total_area = self.Ag
                if total_area < 1e-6:
                    self._centroid = (0.0, 0.0)
                else:
                    x_c = sum(s.area * s.centroid[0] for s in self.segments) / total_area
                    y_c = sum(s.area * s.centroid[1] for s in self.segments) / total_area
                    self._centroid = (x_c, y_c)
        return self._centroid

    @property
    def Ixx(self) -> float:
        """
        Momento de inercia respecto al eje X global que pasa por el centroide.

        Usa el teorema de ejes paralelos:
        Ixx_total = Σ(Ixx_local + Ai × dy²)

        donde dy = distancia del centroide del segmento al centroide global en Y.
        """
        if self._Ixx is None:
            y_c = self.centroid[1]
            Ixx = 0.0

            for s in self.segments:
                # Determinar qué inercia local usar según orientación
                if s.orientation == 'horizontal':
                    # Segmento horizontal: su "altura" es thickness, "base" es length
                    I_local = s.length * (s.thickness ** 3) / 12
                elif s.orientation == 'vertical':
                    # Segmento vertical: su "altura" es length, "base" es thickness
                    I_local = s.thickness * (s.length ** 3) / 12
                else:
                    # Diagonal: usar aproximación conservadora
                    I_local = s.Ixx_local

                # Distancia al centroide global
                dy = s.centroid[1] - y_c

                # Teorema de ejes paralelos
                Ixx += I_local + s.area * (dy ** 2)

            self._Ixx = Ixx
        return self._Ixx

    @property
    def Iyy(self) -> float:
        """
        Momento de inercia respecto al eje Y global que pasa por el centroide.

        Usa el teorema de ejes paralelos:
        Iyy_total = Σ(Iyy_local + Ai × dx²)
        """
        if self._Iyy is None:
            x_c = self.centroid[0]
            Iyy = 0.0

            for s in self.segments:
                # Determinar qué inercia local usar según orientación
                if s.orientation == 'horizontal':
                    # Segmento horizontal: base es length
                    I_local = s.thickness * (s.length ** 3) / 12
                elif s.orientation == 'vertical':
                    # Segmento vertical: base es thickness
                    I_local = s.length * (s.thickness ** 3) / 12
                else:
                    I_local = s.Iyy_local

                # Distancia al centroide global
                dx = s.centroid[0] - x_c

                # Teorema de ejes paralelos
                Iyy += I_local + s.area * (dx ** 2)

            self._Iyy = Iyy
        return self._Iyy

    @property
    def overall_length(self) -> float:
        """
        Longitud total de la sección (dimensión máxima en cualquier dirección).
        """
        if not self.segments:
            return 0.0

        all_corners = []
        for s in self.segments:
            all_corners.extend(s.get_corners())

        if not all_corners:
            return 0.0

        xs = [c[0] for c in all_corners]
        ys = [c[1] for c in all_corners]

        width = max(xs) - min(xs)
        height = max(ys) - min(ys)

        return max(width, height)

    @property
    def overall_width(self) -> float:
        """
        Ancho total de la sección (dimensión mínima).
        """
        if not self.segments:
            return 0.0

        all_corners = []
        for s in self.segments:
            all_corners.extend(s.get_corners())

        if not all_corners:
            return 0.0

        xs = [c[0] for c in all_corners]
        ys = [c[1] for c in all_corners]

        width = max(xs) - min(xs)
        height = max(ys) - min(ys)

        return min(width, height)

    @property
    def web_thickness(self) -> float:
        """
        Espesor del alma (segmento más largo o principal).

        Para muros flanged, el alma es el segmento vertical principal.
        """
        if not self.segments:
            return 0.0

        # Buscar el segmento más largo (típicamente el alma)
        longest = max(self.segments, key=lambda s: s.length)
        return longest.thickness

    @property
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Bounding box de la sección: (x_min, y_min, x_max, y_max).
        """
        if not self.segments:
            return (0.0, 0.0, 0.0, 0.0)

        all_corners = []
        for s in self.segments:
            all_corners.extend(s.get_corners())

        xs = [c[0] for c in all_corners]
        ys = [c[1] for c in all_corners]

        return (min(xs), min(ys), max(xs), max(ys))

    def calculate_Acv(self, direction: str = 'primary') -> float:
        """
        Área de cortante efectiva según ACI 318-25 para muros flanged.

        Para muros con alas (L, T, C), Acv incluye solo el área del alma,
        no las alas. Esto es crítico para el cálculo de resistencia a cortante.

        Args:
            direction: 'primary' usa el segmento más largo como alma,
                      'x' o 'y' especifica la dirección de cortante.

        Returns:
            Área de cortante en mm².
        """
        if not self.segments:
            return 0.0

        if len(self.segments) == 1:
            # Sección simple: toda el área es de cortante
            return self.segments[0].area

        # Para secciones compuestas, identificar el alma
        web = self._identify_web(direction)
        return web.area if web else self.Ag

    def _identify_web(self, direction: str = 'primary') -> Optional[WallSegment]:
        """
        Identifica el segmento que actúa como alma.

        El alma es típicamente el segmento más largo en la dirección
        perpendicular al cortante aplicado.
        """
        if not self.segments:
            return None

        if direction == 'primary':
            # El alma es el segmento más largo
            return max(self.segments, key=lambda s: s.length)

        elif direction == 'x':
            # Cortante en X: alma es el segmento vertical más largo
            vertical = [s for s in self.segments if s.orientation == 'vertical']
            if vertical:
                return max(vertical, key=lambda s: s.length)
            return max(self.segments, key=lambda s: s.length)

        elif direction == 'y':
            # Cortante en Y: alma es el segmento horizontal más largo
            horizontal = [s for s in self.segments if s.orientation == 'horizontal']
            if horizontal:
                return max(horizontal, key=lambda s: s.length)
            return max(self.segments, key=lambda s: s.length)

        return max(self.segments, key=lambda s: s.length)

    def get_effective_flange_width(self, hw: float) -> float:
        """
        Ancho efectivo de ala según ACI 318-25 Sección 18.10.5.2.

        bf = min(0.5 × distancia_a_alma_adyacente, 0.25 × hw)

        Args:
            hw: Altura total del muro en mm.

        Returns:
            Ancho efectivo de ala en mm.
        """
        if len(self.segments) <= 1:
            return 0.0

        # Identificar alas (segmentos que no son el alma)
        web = self._identify_web('primary')
        flanges = [s for s in self.segments if s != web]

        if not flanges:
            return 0.0

        # Calcular ancho efectivo máximo
        max_flange_length = max(f.length for f in flanges)

        # Límite por altura: 0.25 × hw
        limit_by_height = 0.25 * hw

        # Límite por distancia a alma adyacente (simplificado)
        # Asumimos que la distancia a un alma adyacente es muy grande
        limit_by_distance = max_flange_length

        return min(limit_by_distance, limit_by_height, max_flange_length)

    @classmethod
    def detect_shape(cls, segments: List[WallSegment]) -> SectionShapeType:
        """
        Detecta automáticamente el tipo de forma basado en la geometría.

        L-shape: 2 segmentos perpendiculares
        T-shape: 3 segmentos formando T (1 vertical + 2 horizontales simétricas)
        C-shape: 3 segmentos formando U/C (1 horizontal + 2 verticales en extremos)
        """
        if len(segments) == 1:
            return SectionShapeType.RECTANGULAR

        # Contar orientaciones
        orientations = [s.orientation for s in segments]
        n_horizontal = orientations.count('horizontal')
        n_vertical = orientations.count('vertical')

        if len(segments) == 2:
            # 2 segmentos perpendiculares = L
            if n_horizontal == 1 and n_vertical == 1:
                return SectionShapeType.L_SHAPE

        elif len(segments) == 3:
            if n_vertical == 1 and n_horizontal == 2:
                # 1 vertical + 2 horizontales = T
                return SectionShapeType.T_SHAPE
            elif n_horizontal == 1 and n_vertical == 2:
                # 1 horizontal + 2 verticales = C o U
                return SectionShapeType.C_SHAPE

        # Para otras configuraciones
        if len(segments) >= 2:
            if n_horizontal >= 1 and n_vertical >= 1:
                # Tiene ambas orientaciones, probablemente L, T, o C
                if len(segments) == 2:
                    return SectionShapeType.L_SHAPE
                elif n_horizontal > n_vertical:
                    return SectionShapeType.T_SHAPE
                else:
                    return SectionShapeType.C_SHAPE

        return SectionShapeType.CUSTOM

    def invalidate_cache(self):
        """Invalida el cache de propiedades calculadas."""
        self._Ag = None
        self._centroid = None
        self._Ixx = None
        self._Iyy = None

    def to_dict(self) -> dict:
        """Convierte la sección a diccionario para serialización."""
        return {
            'shape_type': self.shape_type.value,
            'n_segments': len(self.segments),
            'Ag_mm2': self.Ag,
            'Ag_cm2': self.Ag / 100,  # mm² a cm²
            'centroid_mm': self.centroid,
            'Ixx_mm4': self.Ixx,
            'Iyy_mm4': self.Iyy,
            'overall_length_mm': self.overall_length,
            'web_thickness_mm': self.web_thickness,
            'segments': [
                {
                    'x1': s.x1, 'y1': s.y1,
                    'x2': s.x2, 'y2': s.y2,
                    'thickness': s.thickness,
                    'length': s.length,
                    'orientation': s.orientation,
                }
                for s in self.segments
            ]
        }
