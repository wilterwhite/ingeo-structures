# app/domain/calculations/rebar_layout_calculator.py
"""
Calculador unificado de layout de armadura.

CENTRALIZA la logica de calculo de posiciones de barras que antes estaba duplicada en:
- plot_generator.generate_section_diagram (lineas 200-420)
- plot_generator._generate_composite_section_diagram (lineas 950-1250)
- steel_layer_calculator.calculate() (lineas 118-170)

Este calculador es la UNICA fuente de verdad para posiciones de barras.
"""
import math
from typing import TYPE_CHECKING, List, Tuple, Dict, Set

from ..entities.rebar import RebarLayout

if TYPE_CHECKING:
    from ..entities.vertical_element import VerticalElement
    from ..entities.composite_section import CompositeSection


class RebarLayoutCalculator:
    """
    Calcula el layout de armadura para cualquier tipo de seccion.

    Soporta:
    - Secciones rectangulares con malla (MESH layout)
    - Secciones rectangulares con barras perimetrales (STIRRUPS layout)
    - Secciones compuestas (L, T, C shapes)
    """

    @classmethod
    def calculate(cls, element: 'VerticalElement') -> RebarLayout:
        """
        Punto de entrada principal. Calcula el layout segun el tipo de elemento.

        Args:
            element: VerticalElement con configuracion de armadura

        Returns:
            RebarLayout con todas las barras posicionadas
        """
        if element.is_composite:
            return cls._calculate_composite(element)
        elif element.is_mesh_layout:
            return cls._calculate_rectangular_mesh(element)
        else:
            return cls._calculate_rectangular_discrete(element)

    @classmethod
    def _calculate_rectangular_mesh(cls, element: 'VerticalElement') -> RebarLayout:
        """
        Calcula layout para seccion rectangular con malla.

        Distribuye:
        - Barras de borde en los extremos izquierdo y derecho
        - Barras de malla intermedias con espaciamiento regular

        Origen: esquina inferior izquierda de la seccion.
        """
        if not element.mesh_reinforcement:
            return RebarLayout(
                cover=element.cover,
                section_width=element.length,
                section_height=element.thickness
            )

        mr = element.mesh_reinforcement
        length = element.length      # lw - dimension horizontal
        thickness = element.thickness  # tw - dimension vertical
        cover = element.cover
        n_edge = mr.n_edge_bars
        n_meshes = mr.n_meshes

        layout = RebarLayout(
            cover=cover,
            section_width=length,
            section_height=thickness
        )

        # Configuracion de filas segun n_meshes
        if n_meshes == 1:
            # Malla simple: barras en el centro del espesor
            y_positions = [thickness / 2]
            bars_per_row = n_edge
        else:
            # Malla doble: barras en 2 capas
            y_positions = [cover + mr.diameter_edge / 2,
                          thickness - cover - mr.diameter_edge / 2]
            bars_per_row = max(1, n_edge // 2)

        # Espaciamiento entre barras de borde
        bar_spacing_x = min(150, element.stirrup_spacing)

        # Determinar si hay elemento de borde (mas de 2 barras)
        has_boundary_element = n_edge > 2

        if has_boundary_element:
            boundary_length = cover + (bars_per_row - 1) * bar_spacing_x + cover + element.stirrup_diameter
        else:
            boundary_length = cover

        # 1. Barras de borde - extremo izquierdo
        for y in y_positions:
            for col_idx in range(bars_per_row):
                x = cover + mr.diameter_edge / 2 + col_idx * bar_spacing_x
                layout.add_bar(
                    x=x,
                    y=y,
                    diameter=mr.diameter_edge,
                    area=mr._bar_area_edge,
                    bar_type='edge'
                )

        # 2. Barras de borde - extremo derecho
        for y in y_positions:
            for col_idx in range(bars_per_row):
                x = length - cover - mr.diameter_edge / 2 - col_idx * bar_spacing_x
                layout.add_bar(
                    x=x,
                    y=y,
                    diameter=mr.diameter_edge,
                    area=mr._bar_area_edge,
                    bar_type='edge'
                )

        # 3. Barras de malla intermedias
        if has_boundary_element:
            mesh_start = boundary_length
            mesh_end = length - boundary_length
        else:
            mesh_start = cover
            mesh_end = length - cover

        available_span = mesh_end - mesh_start
        mesh_spacing = mr.spacing_v

        if available_span > mesh_spacing:
            n_intermediate = math.ceil(available_span / mesh_spacing) - 1
        else:
            n_intermediate = 0

        if n_intermediate > 0 and available_span > 0:
            actual_spacing = available_span / (n_intermediate + 1)
            first_bar_pos = mesh_start + actual_spacing

            for i in range(n_intermediate):
                x = first_bar_pos + i * actual_spacing
                for y in y_positions:
                    layout.add_bar(
                        x=x,
                        y=y,
                        diameter=mr.diameter_v,
                        area=mr._bar_area_v,
                        bar_type='mesh'
                    )

        return layout

    @classmethod
    def _calculate_rectangular_discrete(cls, element: 'VerticalElement') -> RebarLayout:
        """
        Calcula layout para seccion rectangular con barras perimetrales.

        Distribuye barras en el perimetro segun n_bars_depth x n_bars_width.
        Origen: esquina inferior izquierda de la seccion.
        """
        if not element.discrete_reinforcement:
            return RebarLayout(
                cover=element.cover,
                section_width=element.length,
                section_height=element.thickness
            )

        dr = element.discrete_reinforcement
        length = element.length      # depth para columnas
        thickness = element.thickness  # width para columnas
        cover = element.cover

        layout = RebarLayout(
            cover=cover,
            section_width=length,
            section_height=thickness
        )

        n_bars_x = dr.n_bars_length  # barras en direccion length
        n_bars_y = dr.n_bars_thickness  # barras en direccion thickness

        # Caso especial: 1 barra centrada (strut)
        if n_bars_x == 1 and n_bars_y == 1:
            layout.add_bar(
                x=length / 2,
                y=thickness / 2,
                diameter=dr.diameter,
                area=dr._bar_area,
                bar_type='corner'
            )
            return layout

        # Calcular posiciones X (a lo largo de length)
        if n_bars_x >= 2:
            x_first = cover + dr.diameter / 2
            x_last = length - cover - dr.diameter / 2
            if n_bars_x == 2:
                x_positions = [x_first, x_last]
            else:
                x_spacing = (x_last - x_first) / (n_bars_x - 1)
                x_positions = [x_first + i * x_spacing for i in range(n_bars_x)]
        else:
            x_positions = [length / 2]

        # Calcular posiciones Y (a lo largo de thickness)
        if n_bars_y >= 2:
            y_first = cover + dr.diameter / 2
            y_last = thickness - cover - dr.diameter / 2
            if n_bars_y == 2:
                y_positions = [y_first, y_last]
            else:
                y_spacing = (y_last - y_first) / (n_bars_y - 1)
                y_positions = [y_first + i * y_spacing for i in range(n_bars_y)]
        else:
            y_positions = [thickness / 2]

        # Colocar barras solo en el perimetro
        for i, y in enumerate(y_positions):
            for j, x in enumerate(x_positions):
                is_edge = (i == 0 or i == len(y_positions) - 1 or
                          j == 0 or j == len(x_positions) - 1)
                if is_edge:
                    # Determinar tipo de barra
                    is_corner = ((i == 0 or i == len(y_positions) - 1) and
                                (j == 0 or j == len(x_positions) - 1))
                    bar_type = 'corner' if is_corner else 'edge'

                    layout.add_bar(
                        x=x,
                        y=y,
                        diameter=dr.diameter,
                        area=dr._bar_area,
                        bar_type=bar_type
                    )

        return layout

    @classmethod
    def _calculate_composite(cls, element: 'VerticalElement') -> RebarLayout:
        """
        Calcula layout para seccion compuesta (L, T, C).

        Distribuye:
        - Barras de borde en extremos libres de cada segmento
        - 4 barras en cada interseccion (esquinas L, T, C)
        - Barras de malla a lo largo de cada segmento (entre conexiones)
        """
        cs = element.composite_section
        if cs is None or not element.mesh_reinforcement:
            return RebarLayout(
                cover=element.cover,
                section_width=element.length,
                section_height=element.thickness
            )

        mr = element.mesh_reinforcement
        cover = element.cover
        n_edge = mr.n_edge_bars
        n_meshes = mr.n_meshes

        # Obtener bounding box para dimensiones
        x_min, y_min, x_max, y_max = cs.bounding_box

        layout = RebarLayout(
            cover=cover,
            section_width=x_max - x_min,
            section_height=y_max - y_min
        )

        # Configuracion de filas segun n_meshes
        if n_meshes == 1:
            rows = 1
            bars_per_row = n_edge
        else:
            rows = 2
            bars_per_row = max(1, n_edge // 2)

        bar_spacing_x = min(150, element.stirrup_spacing)

        # Identificar puntos de conexion entre segmentos
        connection_info = cls._find_connections(cs)
        t_connections = cls._find_t_connections(cs, connection_info)
        connection_points = {pt for pt, segs in connection_info.items() if len(segs) >= 2}

        # 1. Barras en extremos libres de cada segmento
        for seg_idx, segment in enumerate(cs.segments):
            cls._add_edge_bars_for_segment(
                layout, segment, seg_idx, connection_points,
                cover, mr.diameter_edge, mr._bar_area_edge,
                bars_per_row, rows, bar_spacing_x
            )

        # 2. Barras en intersecciones (4 barras por interseccion)
        for conn_pt in connection_points:
            seg_indices = connection_info[conn_pt]
            if len(seg_indices) >= 2:
                cls._add_intersection_bars(
                    layout, cs, conn_pt, seg_indices,
                    cover, mr.diameter_edge, mr._bar_area_edge, rows
                )

        # 3. Barras de malla a lo largo de cada segmento
        for seg_idx, segment in enumerate(cs.segments):
            cls._add_mesh_bars_for_segment(
                layout, cs, segment, seg_idx,
                connection_info, t_connections, connection_points,
                cover, mr.diameter_v, mr._bar_area_v, mr.spacing_v,
                mr.diameter_edge, bars_per_row, bar_spacing_x, rows
            )

        return layout

    @classmethod
    def _find_connections(cls, cs: 'CompositeSection') -> Dict[Tuple[int, int], List[int]]:
        """Encuentra puntos donde conectan segmentos (extremos compartidos)."""
        connection_info: Dict[Tuple[int, int], List[int]] = {}

        for i, seg in enumerate(cs.segments):
            for pt in [(seg.x1, seg.y1), (seg.x2, seg.y2)]:
                pt_key = (round(pt[0]), round(pt[1]))
                if pt_key not in connection_info:
                    connection_info[pt_key] = []
                connection_info[pt_key].append(i)

        return connection_info

    @classmethod
    def _find_t_connections(
        cls,
        cs: 'CompositeSection',
        connection_info: Dict[Tuple[int, int], List[int]]
    ) -> Dict[Tuple[int, int], Dict[int, float]]:
        """
        Detecta conexiones T: extremo de un segmento en el MEDIO de otro.

        Returns:
            Dict[pt_key, Dict[seg_idx, position_mm]]
        """
        t_connections: Dict[Tuple[int, int], Dict[int, float]] = {}

        for i, seg_i in enumerate(cs.segments):
            for endpoint in [(seg_i.x1, seg_i.y1), (seg_i.x2, seg_i.y2)]:
                pt_key = (round(endpoint[0]), round(endpoint[1]))

                for j, seg_j in enumerate(cs.segments):
                    if i == j:
                        continue

                    dx = seg_j.x2 - seg_j.x1
                    dy = seg_j.y2 - seg_j.y1
                    length_j = math.sqrt(dx*dx + dy*dy)
                    if length_j < 1:
                        continue

                    # Proyeccion del punto sobre la linea del segmento
                    t = ((endpoint[0] - seg_j.x1) * dx + (endpoint[1] - seg_j.y1) * dy) / (length_j * length_j)

                    # Verificar si esta dentro del segmento (no en extremos)
                    if 0.1 < t < 0.9:
                        # Calcular distancia perpendicular
                        proj_x = seg_j.x1 + t * dx
                        proj_y = seg_j.y1 + t * dy
                        dist = math.sqrt((endpoint[0] - proj_x)**2 + (endpoint[1] - proj_y)**2)

                        # Si esta cerca de la linea, es una conexion T
                        if dist < seg_j.thickness / 2 + 10:
                            if pt_key not in connection_info:
                                connection_info[pt_key] = []
                            if j not in connection_info[pt_key]:
                                connection_info[pt_key].append(j)
                            if pt_key not in t_connections:
                                t_connections[pt_key] = {}
                            t_connections[pt_key][j] = t * length_j

        return t_connections

    @classmethod
    def _add_edge_bars_for_segment(
        cls,
        layout: RebarLayout,
        segment,
        seg_idx: int,
        connection_points: Set[Tuple[int, int]],
        cover: float,
        edge_diameter: float,
        edge_area: float,
        bars_per_row: int,
        rows: int,
        bar_spacing_x: float
    ) -> None:
        """Agrega barras de borde en los extremos libres de un segmento."""
        seg_thickness = segment.thickness

        dx = segment.x2 - segment.x1
        dy = segment.y2 - segment.y1
        length = math.sqrt(dx*dx + dy*dy)
        if length < 1:
            return

        ux, uy = dx / length, dy / length  # Vector unitario longitudinal
        px, py = -uy, ux  # Vector perpendicular

        # Posiciones perpendiculares segun numero de filas
        if rows == 1:
            perp_offsets = [0]
        else:
            half_t = seg_thickness / 2 - cover - edge_diameter / 2
            perp_offsets = [-half_t, half_t]

        # Procesar cada extremo
        endpoints = [(segment.x1, segment.y1, 1), (segment.x2, segment.y2, -1)]

        for base_x, base_y, sign in endpoints:
            is_connected = (round(base_x), round(base_y)) in connection_points
            if is_connected:
                continue  # Las barras de interseccion se agregan por separado

            for perp_offset in perp_offsets:
                for col_idx in range(bars_per_row):
                    long_offset = cover + edge_diameter / 2 + col_idx * bar_spacing_x
                    bar_x = base_x + sign * long_offset * ux + perp_offset * px
                    bar_y = base_y + sign * long_offset * uy + perp_offset * py

                    layout.add_bar(
                        x=bar_x,
                        y=bar_y,
                        diameter=edge_diameter,
                        area=edge_area,
                        bar_type='edge',
                        segment_id=seg_idx
                    )

    @classmethod
    def _add_intersection_bars(
        cls,
        layout: RebarLayout,
        cs: 'CompositeSection',
        conn_pt: Tuple[int, int],
        seg_indices: List[int],
        cover: float,
        edge_diameter: float,
        edge_area: float,
        rows: int
    ) -> None:
        """Agrega 4 barras en una interseccion de segmentos."""
        if len(seg_indices) < 2:
            return

        seg1 = cs.segments[seg_indices[0]]
        seg2 = cs.segments[seg_indices[1]]

        def get_perp_vector(seg):
            dx = seg.x2 - seg.x1
            dy = seg.y2 - seg.y1
            length = math.sqrt(dx*dx + dy*dy)
            if length < 1:
                return (0, 1)
            return (-dy / length, dx / length)

        px1, py1 = get_perp_vector(seg1)
        px2, py2 = get_perp_vector(seg2)

        half_t1 = seg1.thickness / 2 - cover - edge_diameter / 2
        half_t2 = seg2.thickness / 2 - cover - edge_diameter / 2

        # Las 4 barras de esquina estan en las combinaciones de offsets
        corner_offsets = [
            (half_t1 * px1 + half_t2 * px2, half_t1 * py1 + half_t2 * py2),
            (half_t1 * px1 - half_t2 * px2, half_t1 * py1 - half_t2 * py2),
            (-half_t1 * px1 + half_t2 * px2, -half_t1 * py1 + half_t2 * py2),
            (-half_t1 * px1 - half_t2 * px2, -half_t1 * py1 - half_t2 * py2),
        ]

        for off_x, off_y in corner_offsets:
            bar_x = conn_pt[0] + off_x
            bar_y = conn_pt[1] + off_y

            layout.add_bar(
                x=bar_x,
                y=bar_y,
                diameter=edge_diameter,
                area=edge_area,
                bar_type='intersection'
            )

    @classmethod
    def _add_mesh_bars_for_segment(
        cls,
        layout: RebarLayout,
        cs: 'CompositeSection',
        segment,
        seg_idx: int,
        connection_info: Dict[Tuple[int, int], List[int]],
        t_connections: Dict[Tuple[int, int], Dict[int, float]],
        connection_points: Set[Tuple[int, int]],
        cover: float,
        mesh_diameter: float,
        mesh_area: float,
        mesh_spacing: float,
        edge_diameter: float,
        bars_per_row: int,
        bar_spacing_x: float,
        rows: int
    ) -> None:
        """Agrega barras de malla a lo largo de un segmento."""
        seg_thickness = segment.thickness
        seg_length = segment.length

        dx = segment.x2 - segment.x1
        dy = segment.y2 - segment.y1
        if seg_length < 1:
            return

        ux, uy = dx / seg_length, dy / seg_length
        px, py = -uy, ux

        # Posiciones perpendiculares para las mallas
        if rows == 1:
            mesh_perp_offsets = [0]
        else:
            half_t = seg_thickness / 2 - cover - mesh_diameter / 2
            mesh_perp_offsets = [-half_t, half_t]

        # Verificar conexiones en extremos
        p1_key = (round(segment.x1), round(segment.y1))
        p2_key = (round(segment.x2), round(segment.y2))
        p1_connected = p1_key in connection_points
        p2_connected = p2_key in connection_points

        def get_connected_segment_thickness(pt_key, current_seg_idx):
            for idx in connection_info.get(pt_key, []):
                if idx != current_seg_idx:
                    return cs.segments[idx].thickness
            return seg_thickness

        # Buscar conexiones T en el MEDIO de este segmento
        mid_connections = []
        for pt_key, seg_positions in t_connections.items():
            if seg_idx in seg_positions:
                pos_mm = seg_positions[seg_idx]
                other_idx = None
                for idx in connection_info.get(pt_key, []):
                    if idx != seg_idx:
                        other_idx = idx
                        break
                if other_idx is not None:
                    mid_connections.append((pos_mm, pt_key, other_idx))

        mid_connections.sort(key=lambda x: x[0])

        def draw_mesh_bars_in_span(start_pos, end_pos, is_start_connected,
                                   is_end_connected, other_thickness_start,
                                   other_thickness_end):
            """Dibuja barras de malla en un tramo del segmento."""
            if not is_start_connected:
                last_bar_from_start = cover + edge_diameter/2 + (bars_per_row - 1) * bar_spacing_x
            else:
                last_bar_from_start = other_thickness_start / 2 - cover - edge_diameter / 2

            if not is_end_connected:
                last_bar_from_end = cover + edge_diameter/2 + (bars_per_row - 1) * bar_spacing_x
            else:
                last_bar_from_end = other_thickness_end / 2 - cover - edge_diameter / 2

            span_length = end_pos - start_pos
            dist_A = span_length - last_bar_from_start - last_bar_from_end

            if dist_A > mesh_spacing:
                n_mesh_bars = int(dist_A / mesh_spacing)
                if n_mesh_bars > 0:
                    actual_spacing = dist_A / (n_mesh_bars + 1)
                    for i in range(n_mesh_bars):
                        long_pos = start_pos + last_bar_from_start + (i + 1) * actual_spacing
                        for perp_offset in mesh_perp_offsets:
                            bar_x = segment.x1 + long_pos * ux + perp_offset * px
                            bar_y = segment.y1 + long_pos * uy + perp_offset * py

                            layout.add_bar(
                                x=bar_x,
                                y=bar_y,
                                diameter=mesh_diameter,
                                area=mesh_area,
                                bar_type='mesh',
                                segment_id=seg_idx
                            )

        # Dividir segmento en tramos si hay conexiones T
        if mid_connections:
            cut_points = [0]
            for pos_mm, pt_key, other_idx in mid_connections:
                cut_points.append(pos_mm)
            cut_points.append(seg_length)

            for i in range(len(cut_points) - 1):
                start_pos = cut_points[i]
                end_pos = cut_points[i + 1]

                if i == 0:
                    is_start_connected = p1_connected
                    other_thickness_start = get_connected_segment_thickness(p1_key, seg_idx) if p1_connected else seg_thickness
                else:
                    is_start_connected = True
                    _, pt_key, other_idx = mid_connections[i - 1]
                    other_thickness_start = cs.segments[other_idx].thickness

                if i == len(cut_points) - 2:
                    is_end_connected = p2_connected
                    other_thickness_end = get_connected_segment_thickness(p2_key, seg_idx) if p2_connected else seg_thickness
                else:
                    is_end_connected = True
                    _, pt_key, other_idx = mid_connections[i]
                    other_thickness_end = cs.segments[other_idx].thickness

                draw_mesh_bars_in_span(
                    start_pos, end_pos,
                    is_start_connected, is_end_connected,
                    other_thickness_start, other_thickness_end
                )
        else:
            # Sin conexiones T, un solo tramo
            other_thickness_start = get_connected_segment_thickness(p1_key, seg_idx) if p1_connected else seg_thickness
            other_thickness_end = get_connected_segment_thickness(p2_key, seg_idx) if p2_connected else seg_thickness

            draw_mesh_bars_in_span(
                0, seg_length,
                p1_connected, p2_connected,
                other_thickness_start, other_thickness_end
            )
