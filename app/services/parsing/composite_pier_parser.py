# app/services/parsing/composite_pier_parser.py
"""
Parser para piers con geometria compuesta (L, T, C) desde ETABS.

Lee 3 tablas de ETABS para ensamblar la geometria de piers compuestos:
1. Wall Object Connectivity: Define cada muro como rectangulo con 4 puntos
2. Point Object Connectivity: Coordenadas X, Y, Z de todos los puntos
3. Area Assigns - Pier Labels: Agrupa multiples muros en un Pier
"""
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import pandas as pd
import math
import logging

from app.domain.entities.composite_section import (
    CompositeSection,
    WallSegment,
    SectionShapeType,
)

logger = logging.getLogger(__name__)


@dataclass
class WallRectangle:
    """Rectangulo de un muro individual con sus 4 vertices."""
    wall_id: int
    story: str
    wall_bay: str
    vertices: List[Tuple[float, float, float]]  # 4 puntos (x, y, z)
    area: float
    perimeter: float


class CompositePierParser:
    """Parser para piers con geometria compuesta desde ETABS."""

    # Tolerancia para considerar dos puntos como coincidentes (mm)
    POINT_TOLERANCE = 1.0

    # Tolerancia angular para considerar segmentos colineales (grados)
    ANGLE_TOLERANCE = 5.0

    def parse_composite_piers(
        self,
        walls_df: pd.DataFrame,
        points_df: pd.DataFrame,
        pier_assigns_df: pd.DataFrame,
        unit_factor: float = 1000.0,  # Factor de conversion a mm (default: m -> mm)
        pier_thicknesses: Optional[Dict[str, float]] = None  # Espesores de Pier Section Props (mm)
    ) -> Dict[str, CompositeSection]:
        """
        Parsea piers compuestos agrupando muros por Pier Name.

        Args:
            walls_df: DataFrame de "Wall Object Connectivity"
            points_df: DataFrame de "Point Object Connectivity"
            pier_assigns_df: DataFrame de "Area Assigns - Pier Labels"
            unit_factor: Factor para convertir unidades a mm (1000 para m->mm)

        Returns:
            Dict[pier_key -> CompositeSection] donde pier_key = "Story_PierName"
        """
        if walls_df is None or points_df is None or pier_assigns_df is None:
            return {}

        # 1. Construir lookup de puntos: point_id -> (x, y, z)
        points_lookup = self._build_points_lookup(points_df, unit_factor)
        if not points_lookup:
            logger.warning("No se encontraron puntos en Point Object Connectivity")
            return {}

        # 2. Construir lookup de muros: wall_id -> WallRectangle
        walls_lookup = self._build_walls_lookup(walls_df, points_lookup, unit_factor)
        if not walls_lookup:
            logger.warning("No se encontraron muros en Wall Object Connectivity")
            return {}

        # 3. Agrupar muros por (Story, Pier Name)
        pier_groups = self._group_walls_by_pier(pier_assigns_df, walls_lookup)

        # 4. Para cada grupo, crear CompositeSection
        result: Dict[str, CompositeSection] = {}
        pier_thicknesses = pier_thicknesses or {}

        for (story, pier_name), wall_rectangles in pier_groups.items():
            if len(wall_rectangles) < 2:
                # Solo 1 muro = rectangular simple, no necesita composite
                continue

            try:
                # Obtener espesor del pier desde Pier Section Properties (fallback)
                pier_key = f"{story}_{pier_name}"
                fallback_thickness = pier_thicknesses.get(pier_key, 0.0)

                # Extraer segmentos de los muros
                segments = self._extract_segments_from_walls(wall_rectangles, fallback_thickness)

                if not segments:
                    continue

                # Unir segmentos colineales
                merged_segments = self._merge_collinear_segments(segments)

                if not merged_segments:
                    continue

                # Crear CompositeSection
                composite = CompositeSection(
                    segments=merged_segments,
                    shape_type=SectionShapeType.CUSTOM  # Se detectara en __post_init__
                )

                # Solo agregar si tiene mas de 1 segmento efectivo
                if len(merged_segments) >= 2:
                    key = f"{story}_{pier_name}"
                    result[key] = composite
                    logger.info(
                        f"Pier compuesto {key}: {composite.shape_type.value}, "
                        f"{len(merged_segments)} segmentos, Ag={composite.Ag/100:.0f} cm2"
                    )

            except Exception as e:
                logger.error(f"Error procesando pier {story}_{pier_name}: {e}")
                continue

        return result

    def _build_points_lookup(
        self,
        points_df: pd.DataFrame,
        unit_factor: float
    ) -> Dict[int, Tuple[float, float, float]]:
        """
        Construye diccionario point_id -> (X, Y, Z).

        Args:
            points_df: DataFrame con columnas UniqueName, X, Y, Z
            unit_factor: Factor de conversion a mm

        Returns:
            Dict[point_id -> (x_mm, y_mm, z_mm)]
        """
        lookup = {}

        # Buscar columnas (case-insensitive)
        cols = {c.lower(): c for c in points_df.columns}

        id_col = cols.get('uniquename') or cols.get('unique name') or cols.get('name')
        x_col = cols.get('x')
        y_col = cols.get('y')
        z_col = cols.get('z')

        if not all([id_col, x_col, y_col, z_col]):
            logger.warning(f"Columnas faltantes en Point Object. Disponibles: {list(points_df.columns)}")
            return lookup

        for _, row in points_df.iterrows():
            try:
                point_id = int(row[id_col])
                x = float(row[x_col]) * unit_factor
                y = float(row[y_col]) * unit_factor
                z = float(row[z_col]) * unit_factor
                lookup[point_id] = (x, y, z)
            except (ValueError, TypeError):
                continue

        return lookup

    def _build_walls_lookup(
        self,
        walls_df: pd.DataFrame,
        points_lookup: Dict[int, Tuple[float, float, float]],
        unit_factor: float
    ) -> Dict[int, WallRectangle]:
        """
        Construye diccionario wall_id -> WallRectangle.

        Args:
            walls_df: DataFrame de Wall Object Connectivity
            points_lookup: Diccionario de puntos
            unit_factor: Factor de conversion

        Returns:
            Dict[wall_id -> WallRectangle]
        """
        lookup = {}

        # Buscar columnas (case-insensitive)
        cols = {c.lower().replace(' ', ''): c for c in walls_df.columns}

        id_col = cols.get('uniquename') or cols.get('name')
        story_col = cols.get('story')
        bay_col = cols.get('wallbay') or cols.get('bay')
        pt1_col = cols.get('uniquept1') or cols.get('pt1')
        pt2_col = cols.get('uniquept2') or cols.get('pt2')
        pt3_col = cols.get('uniquept3') or cols.get('pt3')
        pt4_col = cols.get('uniquept4') or cols.get('pt4')
        area_col = cols.get('area')
        perim_col = cols.get('perimeter')

        if not id_col or not all([pt1_col, pt2_col, pt3_col, pt4_col]):
            logger.warning(f"Columnas faltantes en Wall Object. Disponibles: {list(walls_df.columns)}")
            return lookup

        for _, row in walls_df.iterrows():
            try:
                wall_id = int(row[id_col])
                story = str(row[story_col]) if story_col else ""
                bay = str(row[bay_col]) if bay_col else ""

                # Obtener los 4 puntos
                pt_ids = [
                    int(row[pt1_col]),
                    int(row[pt2_col]),
                    int(row[pt3_col]),
                    int(row[pt4_col]),
                ]

                vertices = []
                for pt_id in pt_ids:
                    if pt_id in points_lookup:
                        vertices.append(points_lookup[pt_id])
                    else:
                        logger.debug(f"Punto {pt_id} no encontrado para muro {wall_id}")
                        break

                if len(vertices) != 4:
                    continue

                # Area y perimetro
                area = float(row[area_col]) * (unit_factor ** 2) if area_col else 0.0
                perimeter = float(row[perim_col]) * unit_factor if perim_col else 0.0

                lookup[wall_id] = WallRectangle(
                    wall_id=wall_id,
                    story=story,
                    wall_bay=bay,
                    vertices=vertices,
                    area=area,
                    perimeter=perimeter,
                )

            except (ValueError, TypeError) as e:
                logger.debug(f"Error procesando muro: {e}")
                continue

        return lookup

    def _group_walls_by_pier(
        self,
        pier_assigns_df: pd.DataFrame,
        walls_lookup: Dict[int, WallRectangle]
    ) -> Dict[Tuple[str, str], List[WallRectangle]]:
        """
        Agrupa muros por (Story, Pier Name).

        Args:
            pier_assigns_df: DataFrame de Area Assigns - Pier Labels
            walls_lookup: Diccionario de muros

        Returns:
            Dict[(story, pier_name) -> List[WallRectangle]]
        """
        groups: Dict[Tuple[str, str], List[WallRectangle]] = {}

        # Buscar columnas
        cols = {c.lower().replace(' ', ''): c for c in pier_assigns_df.columns}

        story_col = cols.get('story')
        wall_id_col = cols.get('uniquename') or cols.get('name')
        pier_col = cols.get('piername') or cols.get('pier') or cols.get('piernames')

        if not all([story_col, wall_id_col, pier_col]):
            logger.warning(f"Columnas faltantes en Pier Labels. Disponibles: {list(pier_assigns_df.columns)}")
            return groups

        for _, row in pier_assigns_df.iterrows():
            try:
                story = str(row[story_col])
                wall_id = int(row[wall_id_col])
                pier_name = str(row[pier_col])

                if wall_id not in walls_lookup:
                    continue

                key = (story, pier_name)
                if key not in groups:
                    groups[key] = []

                groups[key].append(walls_lookup[wall_id])

            except (ValueError, TypeError):
                continue

        return groups

    def _extract_segments_from_walls(
        self,
        wall_rectangles: List[WallRectangle],
        fallback_thickness: float = 0.0
    ) -> List[WallSegment]:
        """
        Extrae segmentos de linea central de los muros.

        Cada muro rectangular se convierte en un segmento definido por
        su linea central (promedio de lados paralelos) y su espesor.
        """
        segments = []

        for wall in wall_rectangles:
            segment = self._wall_to_segment(wall, fallback_thickness)
            if segment:
                segments.append(segment)

        return segments

    def _wall_to_segment(
        self,
        wall: WallRectangle,
        fallback_thickness: float = 0.0
    ) -> Optional[WallSegment]:
        """
        Convierte un muro rectangular a un segmento de linea central.

        Proyecta a 2D (plano XY) y calcula la linea central y espesor.

        NOTA: En ETABS, los muros son elementos 3D verticales. Los 4 puntos definen
        un rectangulo donde 2 puntos estan en la base (Z baja) y 2 en el tope (Z alta).
        Cuando proyectamos a XY, los puntos base y tope pueden coincidir (mismo X,Y),
        resultando en thickness=0.

        Solucion: Si el calculo geometrico da thickness~0, inferimos el espesor
        desde el area y perimetro del muro.
        """
        if len(wall.vertices) != 4:
            return None

        # Proyectar a 2D (ignorar Z)
        pts_2d = [(v[0], v[1]) for v in wall.vertices]

        # Calcular distancias entre puntos consecutivos
        d12 = self._distance_2d(pts_2d[0], pts_2d[1])
        d23 = self._distance_2d(pts_2d[1], pts_2d[2])
        d34 = self._distance_2d(pts_2d[2], pts_2d[3])
        d41 = self._distance_2d(pts_2d[3], pts_2d[0])

        # Determinar cuales son los lados largos y cuales los cortos
        avg_12_34 = (d12 + d34) / 2
        avg_23_41 = (d23 + d41) / 2

        if avg_12_34 >= avg_23_41:
            mid1 = self._midpoint_2d(pts_2d[3], pts_2d[0])
            mid2 = self._midpoint_2d(pts_2d[1], pts_2d[2])
            thickness = avg_23_41
            length_2d = avg_12_34
        else:
            mid1 = self._midpoint_2d(pts_2d[0], pts_2d[1])
            mid2 = self._midpoint_2d(pts_2d[2], pts_2d[3])
            thickness = avg_12_34
            length_2d = avg_23_41

        # CASO ESPECIAL: Muros verticales en ETABS (proyeccion 2D colapsa a linea)
        # En ETABS, los muros son rectangulos 3D verticales donde:
        # - Area = longitud_en_planta * altura (superficie del muro, NO seccion transversal)
        # - Perimeter = 2*(longitud + altura)
        # El espesor NO esta en Area/Perimeter, viene de Pier Section Properties
        if thickness < 1.0 and fallback_thickness > 0:
            thickness = fallback_thickness
            logger.debug(
                f"[COMPOSITE] Wall {wall.wall_id}: thickness desde Pier Section Properties: "
                f"t={thickness:.1f}mm"
            )

        # Calcular length del segmento en 2D
        segment_length = self._distance_2d(mid1, mid2)

        # Si la longitud en 2D es 0 (puntos coinciden), el muro es vertical
        # y necesitamos usar los puntos unicos para definir la linea central
        if segment_length < 1.0:
            # Encontrar los 2 puntos unicos en XY
            unique_pts = []
            for p in pts_2d:
                is_duplicate = False
                for up in unique_pts:
                    if self._distance_2d(p, up) < 1.0:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_pts.append(p)

            if len(unique_pts) >= 2:
                mid1 = unique_pts[0]
                mid2 = unique_pts[1]
                segment_length = self._distance_2d(mid1, mid2)

        # Crear segmento
        segment = WallSegment(
            x1=mid1[0],
            y1=mid1[1],
            x2=mid2[0],
            y2=mid2[1],
            thickness=thickness,
            wall_id=wall.wall_id,
        )

        logger.debug(
            f"[COMPOSITE] Wall {wall.wall_id}: thickness={thickness:.1f}mm, length={segment.length:.1f}mm"
        )

        return segment

    def _merge_collinear_segments(
        self,
        segments: List[WallSegment]
    ) -> List[WallSegment]:
        """
        Une segmentos que son colineales (en la misma linea).

        Esto simplifica la representacion cuando multiples muros
        forman una sola pared continua.
        """
        if len(segments) <= 1:
            return segments

        # Agrupar por orientacion y posicion
        groups = self._group_collinear(segments)

        # Fusionar cada grupo en un solo segmento
        merged = []
        for group in groups:
            if len(group) == 1:
                merged.append(group[0])
            else:
                merged_segment = self._merge_segment_group(group)
                if merged_segment:
                    merged.append(merged_segment)

        return merged

    def _group_collinear(
        self,
        segments: List[WallSegment]
    ) -> List[List[WallSegment]]:
        """
        Agrupa segmentos colineales.

        Dos segmentos son colineales si:
        1. Tienen el mismo angulo (o angulo opuesto)
        2. La distancia perpendicular entre sus lineas es menor que la tolerancia
        """
        if not segments:
            return []

        used = set()
        groups = []

        for i, seg_i in enumerate(segments):
            if i in used:
                continue

            group = [seg_i]
            used.add(i)

            for j, seg_j in enumerate(segments):
                if j in used:
                    continue

                if self._are_collinear(seg_i, seg_j):
                    group.append(seg_j)
                    used.add(j)

            groups.append(group)

        return groups

    def _are_collinear(self, seg1: WallSegment, seg2: WallSegment) -> bool:
        """Verifica si dos segmentos son colineales."""
        # Comparar angulos
        angle1 = seg1.angle_rad
        angle2 = seg2.angle_rad

        # Normalizar angulos a [0, pi)
        angle1 = angle1 % math.pi
        angle2 = angle2 % math.pi

        angle_diff = abs(angle1 - angle2)
        if angle_diff > math.radians(self.ANGLE_TOLERANCE):
            return False

        # Verificar distancia perpendicular
        # Calcular distancia del centroide de seg2 a la linea de seg1
        cx2, cy2 = seg2.centroid
        dist = self._point_to_line_distance(
            cx2, cy2,
            seg1.x1, seg1.y1, seg1.x2, seg1.y2
        )

        # La distancia maxima permitida es la suma de espesores / 2
        max_dist = (seg1.thickness + seg2.thickness) / 2 + self.POINT_TOLERANCE

        return dist < max_dist

    def _merge_segment_group(self, group: List[WallSegment]) -> Optional[WallSegment]:
        """Fusiona un grupo de segmentos colineales en uno solo."""
        if not group:
            return None

        if len(group) == 1:
            return group[0]

        # Recolectar todos los puntos extremos
        points = []
        for seg in group:
            points.append((seg.x1, seg.y1))
            points.append((seg.x2, seg.y2))

        # Encontrar los dos puntos mas alejados
        max_dist = 0
        p1, p2 = points[0], points[1]

        for i, pi in enumerate(points):
            for pj in points[i+1:]:
                d = self._distance_2d(pi, pj)
                if d > max_dist:
                    max_dist = d
                    p1, p2 = pi, pj

        # Espesor promedio
        avg_thickness = sum(s.thickness for s in group) / len(group)

        return WallSegment(
            x1=p1[0], y1=p1[1],
            x2=p2[0], y2=p2[1],
            thickness=avg_thickness,
        )

    # =========================================================================
    # Utilidades geometricas
    # =========================================================================

    @staticmethod
    def _distance_2d(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Distancia euclidiana 2D."""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    @staticmethod
    def _midpoint_2d(
        p1: Tuple[float, float],
        p2: Tuple[float, float]
    ) -> Tuple[float, float]:
        """Punto medio entre dos puntos 2D."""
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    @staticmethod
    def _point_to_line_distance(
        px: float, py: float,
        x1: float, y1: float,
        x2: float, y2: float
    ) -> float:
        """Distancia de un punto a una linea definida por dos puntos."""
        # Vector de la linea
        dx = x2 - x1
        dy = y2 - y1

        length_sq = dx*dx + dy*dy
        if length_sq < 1e-10:
            return math.sqrt((px - x1)**2 + (py - y1)**2)

        # Distancia perpendicular usando producto cruzado
        dist = abs(dx * (y1 - py) - (x1 - px) * dy) / math.sqrt(length_sq)
        return dist
