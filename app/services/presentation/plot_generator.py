# app/structural/services/presentation/plot_generator.py
"""
Generador de gráficos para análisis estructural.
Crea diagramas de interacción P-M usando matplotlib.
"""
import base64
from io import BytesIO
from typing import List, Tuple, TYPE_CHECKING
import math

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para servidor
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

if TYPE_CHECKING:
    from ...domain.entities import VerticalElement
    from ...domain.entities.rebar import RebarLayout


class PlotGenerator:
    """
    Genera gráficos de curvas de interacción P-M.
    """

    # Colores
    COLOR_CAPACITY = '#2563eb'      # Azul
    COLOR_DEMAND_OK = '#16a34a'     # Verde
    COLOR_DEMAND_FAIL = '#dc2626'   # Rojo
    COLOR_FILL = '#3b82f6'          # Azul claro

    def __init__(self, dpi: int = 150):
        self.dpi = dpi

    def generate_pm_diagram(
        self,
        capacity_curve: List[Tuple[float, float]],
        demand_points: List[Tuple[float, float, str]],
        pier_label: str,
        safety_factor: float,
        show_legend: bool = True,
        figsize: Tuple[int, int] = (8, 6),
        moment_axis: str = 'M3',
        angle_deg: float = 0
    ) -> str:
        """
        Genera el diagrama de interacción P-M.

        Args:
            capacity_curve: Lista de (φMn, φPn) en tonf-m y tonf
            demand_points: Lista de (Pu, Mu, combo_name) en tonf y tonf-m
            pier_label: Etiqueta del pier
            safety_factor: Factor de seguridad calculado
            show_legend: Mostrar leyenda
            figsize: Tamaño de la figura
            moment_axis: 'M2', 'M3', 'combined', o 'SRSS'
            angle_deg: Ángulo para vista combinada

        Returns:
            Imagen en formato base64
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Extraer datos de la curva de capacidad
        M_capacity = [p[0] for p in capacity_curve]
        P_capacity = [p[1] for p in capacity_curve]

        # Cerrar la curva para el relleno
        M_closed = M_capacity + [M_capacity[0]]
        P_closed = P_capacity + [P_capacity[0]]

        # Dibujar curva de capacidad
        ax.plot(M_capacity, P_capacity, color=self.COLOR_CAPACITY,
                linewidth=2, label='Curva φPn-φMn', zorder=2)

        # Rellenar área de capacidad
        ax.fill(M_closed, P_closed, color=self.COLOR_FILL, alpha=0.15, zorder=1)

        # Dibujar puntos de demanda
        for Pu, Mu, combo_name in demand_points:
            # Determinar color según si está dentro o fuera
            is_inside = self._point_inside_curve(Mu, Pu, capacity_curve)
            color = self.COLOR_DEMAND_OK if is_inside else self.COLOR_DEMAND_FAIL
            marker = 'o' if is_inside else 'x'

            ax.plot(Mu, Pu, marker=marker, color=color, markersize=8,
                    markeredgewidth=2, zorder=3)

            # Solo mostrar etiqueta para puntos críticos o fuera de la curva
            if not is_inside:
                ax.annotate(combo_name, (Mu, Pu), fontsize=7,
                           xytext=(5, 5), textcoords='offset points',
                           color=color)

        # Configurar ejes
        ax.axhline(y=0, color='black', linewidth=0.5, linestyle='-')
        ax.axvline(x=0, color='black', linewidth=0.5, linestyle='-')

        # Etiquetas dinámicas según el eje de momento
        if moment_axis == 'M2':
            moment_label = 'Momento φM2 (tonf-m)'
        elif moment_axis == 'M3':
            moment_label = 'Momento φM3 (tonf-m)'
        elif moment_axis == 'combined':
            moment_label = f'Momento φM (tonf-m) - Plano {angle_deg}°'
        elif moment_axis == 'SRSS':
            moment_label = 'Momento φM SRSS (tonf-m)'
        else:
            moment_label = 'Momento φMn (tonf-m)'

        ax.set_xlabel(moment_label, fontsize=11)
        ax.set_ylabel('Carga Axial φPn (tonf)', fontsize=11)

        # Título con factor de seguridad
        status = "OK" if safety_factor >= 1.0 else "NO OK"
        status_color = self.COLOR_DEMAND_OK if safety_factor >= 1.0 else self.COLOR_DEMAND_FAIL
        ax.set_title(f'Diagrama de Interacción - {pier_label}\n'
                    f'Factor de Seguridad: {safety_factor:.2f} ({status})',
                    fontsize=12)

        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')

        # Leyenda
        if show_legend:
            capacity_patch = mpatches.Patch(color=self.COLOR_CAPACITY, label='Capacidad')
            ok_patch = mpatches.Patch(color=self.COLOR_DEMAND_OK, label='Demanda OK')
            fail_patch = mpatches.Patch(color=self.COLOR_DEMAND_FAIL, label='Demanda NO OK')
            ax.legend(handles=[capacity_patch, ok_patch, fail_patch],
                     loc='upper right', fontsize=9)

        # Ajustar límites con margen
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        margin_x = (x_max - x_min) * 0.1
        margin_y = (y_max - y_min) * 0.1
        ax.set_xlim(x_min - margin_x, x_max + margin_x)
        ax.set_ylim(y_min - margin_y, y_max + margin_y)

        plt.tight_layout()

        # Convertir a base64
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        plt.close(fig)

        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return image_base64

    def _point_inside_curve(
        self,
        M: float,
        P: float,
        curve: List[Tuple[float, float]]
    ) -> bool:
        """
        Verifica si un punto está dentro de la curva de capacidad.

        Usa el algoritmo de ray casting.
        """
        n = len(curve)
        inside = False

        x, y = M, P

        j = n - 1
        for i in range(n):
            xi, yi = curve[i]
            xj, yj = curve[j]

            if ((yi > y) != (yj > y)) and \
               (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi):
                inside = not inside

            j = i

        return inside

    # =========================================================================
    # Section Diagram
    # =========================================================================

    # Colores para sección
    COLOR_CONCRETE = '#d1d5db'      # Gris claro
    COLOR_CONCRETE_EDGE = '#6b7280' # Gris oscuro
    COLOR_REBAR = '#1f2937'         # Negro/gris muy oscuro
    COLOR_STIRRUP = '#374151'       # Gris oscuro (para estribos)
    COLOR_DIMENSION = '#374151'     # Gris
    COLOR_BOUNDARY = '#fef3c7'      # Amarillo claro para zona de borde

    @staticmethod
    def _calculate_edge_bar_distribution(n_meshes: int, n_edge: int) -> Tuple[int, int]:
        """
        Calcula distribucion de barras de borde para leyenda.

        Args:
            n_meshes: Numero de mallas (1 o 2)
            n_edge: Numero total de barras de borde

        Returns:
            Tupla (rows, bars_per_row) para mostrar en leyenda
        """
        if n_meshes == 1:
            return 1, n_edge
        else:
            return 2, max(1, n_edge // 2)

    def _draw_bars_from_layout(
        self,
        ax,
        layout: 'RebarLayout',
        offset_x: float = 0,
        offset_y: float = 0
    ) -> None:
        """
        Dibuja todas las barras del layout en el axes.

        Args:
            ax: Axes de matplotlib
            layout: RebarLayout con las barras a dibujar
            offset_x: Offset para centrar la seccion en X
            offset_y: Offset para centrar la seccion en Y
        """
        for bar in layout.bars:
            circle = Circle(
                (bar.x + offset_x, bar.y + offset_y),
                bar.radius,
                facecolor=self.COLOR_REBAR,
                edgecolor='white',
                linewidth=0.5,
                zorder=5
            )
            ax.add_patch(circle)

    def generate_section_diagram(
        self,
        pier: 'VerticalElement',
        figsize: Tuple[int, int] = (10, 8)
    ) -> str:
        """
        Genera un diagrama de la sección transversal del muro.

        Muestra:
        - Sección de hormigón
        - Armadura distribuida (malla)
        - Elemento de borde con barras y estribos
        - Dimensiones y recubrimientos

        Args:
            pier: Entidad Pier con la configuración
            figsize: Tamaño de la figura

        Returns:
            Imagen en formato base64
        """
        # Si es sección compuesta (L, T, C), usar método especializado
        if pier.is_composite:
            return self._generate_composite_section_diagram(pier, figsize)

        fig, ax = plt.subplots(figsize=figsize)

        # Dimensiones en mm
        lw = pier.length      # Largo del muro
        tw = pier.thickness   # Espesor
        cover = pier.cover

        # Origen centrado
        x0 = -lw / 2
        y0 = -tw / 2

        # 1. Dibujar sección de hormigón
        concrete = Rectangle(
            (x0, y0), lw, tw,
            facecolor=self.COLOR_CONCRETE,
            edgecolor=self.COLOR_CONCRETE_EDGE,
            linewidth=2,
            zorder=1
        )
        ax.add_patch(concrete)

        # 2. Calcular dimensiones del elemento de borde
        # Longitud del elemento de borde (aproximada)
        n_edge = pier.n_edge_bars
        edge_bar_d = pier.diameter_edge
        stirrup_d = pier.stirrup_diameter
        stirrup_s = pier.stirrup_spacing

        # Configuración del elemento de borde
        # Asumimos barras distribuidas en filas según n_meshes
        # Calcular distribucion para estribos
        rows, bars_per_row = self._calculate_edge_bar_distribution(pier.n_meshes, n_edge)
        if pier.n_meshes == 2:
            bars_per_row = max(1, n_edge // 2)

        # Espaciamiento entre barras en el elemento de borde
        bar_spacing_y = (tw - 2 * cover - edge_bar_d) / max(1, rows - 1) if rows > 1 else 0
        bar_spacing_x = min(150, stirrup_s)  # Espaciamiento horizontal entre barras de borde

        # Longitud del elemento de borde (desde el extremo)
        boundary_length = cover + (bars_per_row - 1) * bar_spacing_x + cover + stirrup_d

        # 3. Dibujar zonas de elementos de borde y estribos (solo si hay más de 2 barras)
        has_boundary_element = n_edge > 2

        if has_boundary_element:
            # Zona de borde izquierdo (fondo amarillo)
            boundary_left = Rectangle(
                (x0, y0), boundary_length, tw,
                facecolor=self.COLOR_BOUNDARY,
                edgecolor='none',
                alpha=0.5,
                zorder=1.5
            )
            ax.add_patch(boundary_left)

            # Zona de borde derecho (fondo amarillo)
            boundary_right = Rectangle(
                (x0 + lw - boundary_length, y0), boundary_length, tw,
                facecolor=self.COLOR_BOUNDARY,
                edgecolor='none',
                alpha=0.5,
                zorder=1.5
            )
            ax.add_patch(boundary_right)

            # 4. Dibujar estribos de confinamiento con esquinas redondeadas
            # El estribo envuelve las barras con un pequeño margen
            stirrup_clearance = stirrup_d  # Espacio entre barra y estribo

            # Ancho del estribo: desde la primera a la última barra + clearance
            stirrup_width = (bars_per_row - 1) * bar_spacing_x + edge_bar_d + 2 * stirrup_clearance
            stirrup_height = tw - 2 * cover

            # Posición X del estribo izquierdo
            stirrup_left_x = x0 + cover - stirrup_clearance
            stirrup_y = y0 + cover

            # Radio de esquina para los estribos
            corner_radius = min(stirrup_d * 2, stirrup_width * 0.2, stirrup_height * 0.2)

            # Estribo izquierdo
            stirrup_left = FancyBboxPatch(
                (stirrup_left_x, stirrup_y),
                stirrup_width, stirrup_height,
                boxstyle=f"round,pad=0,rounding_size={corner_radius}",
                facecolor='none',
                edgecolor=self.COLOR_STIRRUP,
                linewidth=1.5,
                zorder=4
            )
            ax.add_patch(stirrup_left)

            # Estribo derecho
            stirrup_right_x = x0 + lw - cover - (bars_per_row - 1) * bar_spacing_x - edge_bar_d - stirrup_clearance

            stirrup_right = FancyBboxPatch(
                (stirrup_right_x, stirrup_y),
                stirrup_width, stirrup_height,
                boxstyle=f"round,pad=0,rounding_size={corner_radius}",
                facecolor='none',
                edgecolor=self.COLOR_STIRRUP,
                linewidth=1.5,
                zorder=4
            )
            ax.add_patch(stirrup_right)

        # 5. Dibujar barras usando el layout unificado
        layout = pier.get_rebar_layout()
        self._draw_bars_from_layout(ax, layout, offset_x=x0, offset_y=y0)

        # Variables para info de armadura (mantener compatibilidad)
        rows, bars_per_row = self._calculate_edge_bar_distribution(pier.n_meshes, n_edge)

        # 6. Agregar dimensiones
        dim_offset = tw * 0.3
        arrow_props = dict(arrowstyle='<->', color=self.COLOR_DIMENSION, lw=1.5)

        # Dimensión del largo total (lw)
        ax.annotate('', xy=(x0, y0 - dim_offset), xytext=(x0 + lw, y0 - dim_offset),
                   arrowprops=arrow_props)
        ax.text(x0 + lw/2, y0 - dim_offset - 15, f'lw = {lw:.0f} mm',
               ha='center', va='top', fontsize=10, color=self.COLOR_DIMENSION)

        # Dimensión del espesor (tw)
        ax.annotate('', xy=(x0 - dim_offset, y0), xytext=(x0 - dim_offset, y0 + tw),
                   arrowprops=arrow_props)
        ax.text(x0 - dim_offset - 15, y0 + tw/2, f'tw = {tw:.0f} mm',
               ha='right', va='center', fontsize=10, color=self.COLOR_DIMENSION,
               rotation=90)

        # Dimensión del recubrimiento
        ax.annotate('', xy=(x0, y0 + tw + 10), xytext=(x0 + cover, y0 + tw + 10),
                   arrowprops=dict(arrowstyle='<->', color='#9ca3af', lw=1))
        ax.text(x0 + cover/2, y0 + tw + 25, f'r={cover:.0f}',
               ha='center', va='bottom', fontsize=8, color='#9ca3af')

        # 7. Agregar leyenda de armadura
        info_x = x0 + lw + dim_offset + 20
        info_y = y0 + tw

        # Construir información de armadura
        info_lines = [
            f"ARMADURA:",
            f"",
            f"Malla: {pier.n_meshes}M phi{pier.diameter_v}@{pier.spacing_v}",
            f"",
            f"Borde: {n_edge}phi{edge_bar_d}",
            f"       ({bars_per_row} x {rows} por extremo)",
        ]

        # Solo mostrar info de estribos si hay elemento de borde
        if has_boundary_element:
            info_lines.extend([
                f"",
                f"Estribos: E{stirrup_d}@{stirrup_s}",
            ])

        info_lines.extend([
            f"",
            f"Recubrimiento: {cover:.0f} mm",
            f"",
            f"As borde total: {pier.As_edge_total:.0f} mm2",
            f"As malla: {pier.As_vertical:.0f} mm2",
            f"As flexion total: {pier.As_flexure_total:.0f} mm2",
        ])

        for i, line in enumerate(info_lines):
            ax.text(info_x, info_y - i * 18, line,
                   ha='left', va='top', fontsize=9,
                   fontfamily='monospace', color='#374151')

        # 8. Título
        ax.set_title(f'Seccion Transversal - {pier.story} / {pier.label}\n'
                    f'({lw/1000:.2f}m x {tw/1000:.2f}m)',
                    fontsize=14, fontweight='bold')

        # 9. Configurar ejes
        ax.set_aspect('equal')
        ax.set_xlim(x0 - dim_offset * 2, x0 + lw + dim_offset * 3 + 180)
        ax.set_ylim(y0 - dim_offset * 2, y0 + tw + dim_offset * 2)
        ax.axis('off')

        plt.tight_layout()

        # Convertir a base64
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        plt.close(fig)

        return base64.b64encode(buffer.read()).decode('utf-8')

    def generate_column_section_diagram(
        self,
        column: 'VerticalElement',
        figsize: Tuple[int, int] = (8, 8)
    ) -> str:
        """
        Genera un diagrama de la sección transversal de una columna.

        Muestra:
        - Sección de hormigón rectangular
        - Armadura longitudinal distribuida en el perímetro
        - Estribos con esquinas redondeadas
        - Dimensiones y recubrimientos

        Args:
            column: Entidad Column con la configuración
            figsize: Tamaño de la figura

        Returns:
            Imagen en formato base64
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Dimensiones en mm
        depth = column.depth    # Profundidad (eje 2)
        width = column.width    # Ancho (eje 3)
        cover = column.cover

        # Origen centrado
        x0 = -width / 2
        y0 = -depth / 2

        # 1. Dibujar sección de hormigón
        concrete = Rectangle(
            (x0, y0), width, depth,
            facecolor=self.COLOR_CONCRETE,
            edgecolor=self.COLOR_CONCRETE_EDGE,
            linewidth=2,
            zorder=1
        )
        ax.add_patch(concrete)

        # 2. Dibujar estribos con esquinas redondeadas
        stirrup_d = column.stirrup_diameter
        stirrup_clearance = stirrup_d / 2

        # Dimensiones del estribo (desde el interior del recubrimiento)
        stirrup_width = width - 2 * cover + 2 * stirrup_clearance
        stirrup_height = depth - 2 * cover + 2 * stirrup_clearance

        # Posición del estribo
        stirrup_x = x0 + cover - stirrup_clearance
        stirrup_y = y0 + cover - stirrup_clearance

        # Radio de esquina
        corner_radius = min(stirrup_d * 3, stirrup_width * 0.15, stirrup_height * 0.15)

        stirrup = FancyBboxPatch(
            (stirrup_x, stirrup_y),
            stirrup_width, stirrup_height,
            boxstyle=f"round,pad=0,rounding_size={corner_radius}",
            facecolor='none',
            edgecolor=self.COLOR_STIRRUP,
            linewidth=1.5,
            zorder=3
        )
        ax.add_patch(stirrup)

        # 3. Dibujar barras longitudinales desde layout unificado
        # Layout tiene origen en (0,0), necesitamos trasladar a (x0, y0)
        layout = column.get_rebar_layout()
        self._draw_bars_from_layout(ax, layout, offset_x=x0, offset_y=y0)

        n_bars_depth = column.n_bars_depth
        n_bars_width = column.n_bars_width

        # 4. Agregar dimensiones
        dim_offset = max(depth, width) * 0.15
        arrow_props = dict(arrowstyle='<->', color=self.COLOR_DIMENSION, lw=1.5)

        # Dimensión del ancho (width - horizontal)
        ax.annotate('', xy=(x0, y0 - dim_offset), xytext=(x0 + width, y0 - dim_offset),
                   arrowprops=arrow_props)
        ax.text(x0 + width/2, y0 - dim_offset - 15, f'b = {width:.0f} mm',
               ha='center', va='top', fontsize=10, color=self.COLOR_DIMENSION)

        # Dimensión de la profundidad (depth - vertical)
        ax.annotate('', xy=(x0 - dim_offset, y0), xytext=(x0 - dim_offset, y0 + depth),
                   arrowprops=arrow_props)
        ax.text(x0 - dim_offset - 15, y0 + depth/2, f'h = {depth:.0f} mm',
               ha='right', va='center', fontsize=10, color=self.COLOR_DIMENSION,
               rotation=90)

        # Dimensión del recubrimiento
        ax.annotate('', xy=(x0, y0 + depth + 10), xytext=(x0 + cover, y0 + depth + 10),
                   arrowprops=dict(arrowstyle='<->', color='#9ca3af', lw=1))
        ax.text(x0 + cover/2, y0 + depth + 25, f'r={cover:.0f}',
               ha='center', va='bottom', fontsize=8, color='#9ca3af')

        # 5. Agregar leyenda de armadura
        info_x = x0 + width + dim_offset + 20
        info_y = y0 + depth

        # Determinar tipo de refuerzo transversal
        if column.has_crossties:
            transverse_label = f"Trabas: T{column.stirrup_diameter}@{column.stirrup_spacing}"
            transverse_note = "  (no confinado)"
        else:
            transverse_label = f"Estribos: E{column.stirrup_diameter}@{column.stirrup_spacing}"
            transverse_note = ""

        info_lines = [
            f"ARMADURA:",
            f"",
            f"Longitudinal: {column.n_total_bars}phi{column.diameter_long}",
            f"  ({n_bars_depth} x {n_bars_width})",
            f"",
            transverse_label,
        ]
        if transverse_note:
            info_lines.append(transverse_note)
        info_lines.extend([
            f"",
            f"Recubrimiento: {cover:.0f} mm",
            f"",
            f"As total: {column.As_longitudinal:.0f} mm2",
            f"rho: {column.rho_longitudinal*100:.2f}%",
        ])

        for i, line in enumerate(info_lines):
            ax.text(info_x, info_y - i * 18, line,
                   ha='left', va='top', fontsize=9,
                   fontfamily='monospace', color='#374151')

        # 6. Título
        ax.set_title(f'Seccion Transversal - {column.story} / {column.label}\n'
                    f'({width/1000:.2f}m x {depth/1000:.2f}m)',
                    fontsize=14, fontweight='bold')

        # 7. Configurar ejes
        ax.set_aspect('equal')
        ax.set_xlim(x0 - dim_offset * 2, x0 + width + dim_offset * 2 + 150)
        ax.set_ylim(y0 - dim_offset * 2, y0 + depth + dim_offset * 2)
        ax.axis('off')

        plt.tight_layout()

        # Convertir a base64
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        plt.close(fig)

        return base64.b64encode(buffer.read()).decode('utf-8')

    def generate_strut_section_diagram(
        self,
        element: 'VerticalElement',
        figsize: Tuple[int, int] = (8, 8)
    ) -> str:
        """
        Genera diagrama de seccion para strut (1x1, sin estribos).

        Muestra:
        - Seccion de hormigon cuadrada/rectangular
        - 1 barra centrada
        - Dimensiones
        - Info: "1phi{d} (strut)"

        Args:
            element: VerticalElement configurado como strut
            figsize: Tamano de la figura

        Returns:
            Imagen en formato base64
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Dimensiones en mm (usar depth/width para columnas, length/thickness para piers)
        if hasattr(element, 'depth') and element.depth > 0:
            width = element.width
            depth = element.depth
        else:
            width = element.thickness
            depth = element.length

        cover = element.cover

        # Origen centrado
        x0 = -width / 2
        y0 = -depth / 2

        # 1. Dibujar seccion de hormigon
        concrete = Rectangle(
            (x0, y0), width, depth,
            facecolor=self.COLOR_CONCRETE,
            edgecolor=self.COLOR_CONCRETE_EDGE,
            linewidth=2,
            zorder=1
        )
        ax.add_patch(concrete)

        # 2. Dibujar barra centrada desde layout unificado
        bar_d = element.diameter_long if hasattr(element, 'diameter_long') else 12
        layout = element.get_rebar_layout()
        self._draw_bars_from_layout(ax, layout, offset_x=x0, offset_y=y0)

        # 3. Agregar dimensiones
        dim_offset = max(depth, width) * 0.15
        arrow_props = dict(arrowstyle='<->', color=self.COLOR_DIMENSION, lw=1.5)

        # Dimension del ancho (width - horizontal)
        ax.annotate('', xy=(x0, y0 - dim_offset), xytext=(x0 + width, y0 - dim_offset),
                   arrowprops=arrow_props)
        ax.text(x0 + width/2, y0 - dim_offset - 15, f'lw = {width:.0f} mm',
               ha='center', va='top', fontsize=10, color=self.COLOR_DIMENSION)

        # Dimension de la profundidad (depth - vertical)
        ax.annotate('', xy=(x0 - dim_offset, y0), xytext=(x0 - dim_offset, y0 + depth),
                   arrowprops=arrow_props)
        ax.text(x0 - dim_offset - 15, y0 + depth/2, f'tw = {depth:.0f} mm',
               ha='right', va='center', fontsize=10, color=self.COLOR_DIMENSION,
               rotation=90)

        # Dimension del recubrimiento
        ax.annotate('', xy=(x0, y0 + depth + 10), xytext=(x0 + cover, y0 + depth + 10),
                   arrowprops=dict(arrowstyle='<->', color='#9ca3af', lw=1))
        ax.text(x0 + cover/2, y0 + depth + 25, f'r={cover:.0f}',
               ha='center', va='bottom', fontsize=8, color='#9ca3af')

        # 4. Agregar leyenda de armadura
        info_x = x0 + width + dim_offset + 20
        info_y = y0 + depth

        # Calcular area de acero
        As = math.pi * (bar_d / 2) ** 2

        info_lines = [
            f"ARMADURA:",
            f"",
            f"Longitudinal: 1phi{bar_d}",
            f"  (1 x 1 centrada)",
            f"",
            f"Estribos: sin confinar",
            f"  (strut hormigon simple)",
            f"",
            f"Recubrimiento: {cover:.0f} mm",
            f"",
            f"As total: {As:.0f} mm2",
        ]

        for i, line in enumerate(info_lines):
            ax.text(info_x, info_y - i * 18, line,
                   ha='left', va='top', fontsize=9,
                   fontfamily='monospace', color='#374151')

        # 5. Titulo
        ax.set_title(f'Seccion - Strut - {element.story} / {element.label}\n'
                    f'({width/1000:.2f}m x {depth/1000:.2f}m)',
                    fontsize=14, fontweight='bold')

        # 6. Configurar ejes
        ax.set_aspect('equal')
        ax.set_xlim(x0 - dim_offset * 2, x0 + width + dim_offset * 2 + 150)
        ax.set_ylim(y0 - dim_offset * 2, y0 + depth + dim_offset * 2)
        ax.axis('off')

        plt.tight_layout()

        # Convertir a base64
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        plt.close(fig)

        return base64.b64encode(buffer.read()).decode('utf-8')

    # =========================================================================
    # Composite Section Diagram (L, T, C shapes)
    # =========================================================================

    def _generate_composite_section_diagram(
        self,
        pier: 'VerticalElement',
        figsize: Tuple[int, int] = (12, 10)
    ) -> str:
        """
        Genera diagrama de seccion compuesta (L, T, C).

        Muestra:
        - Seccion unificada (union de segmentos sin bordes internos)
        - Refuerzo en extremos de cada segmento
        - Centroide de la seccion compuesta
        - Dimensiones generales
        - Informacion de propiedades

        Args:
            pier: VerticalElement con composite_section
            figsize: Tamano de la figura

        Returns:
            Imagen en formato base64
        """
        fig, ax = plt.subplots(figsize=figsize)

        cs = pier.composite_section
        if cs is None:
            plt.close(fig)
            return ""

        # Obtener bounding box de la seccion
        x_min, y_min, x_max, y_max = cs.bounding_box

        # Centrar la seccion
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2

        # 1. Crear poligono unificado usando shapely si disponible, sino usar union manual
        try:
            from shapely.geometry import Polygon
            from shapely.ops import unary_union

            # Crear poligonos para cada segmento, extendiendolos para que se solapen
            # en las esquinas donde se conectan con otros segmentos
            polygons = []

            # Encontrar puntos de conexion entre segmentos
            connection_points = set()
            for i, seg1 in enumerate(cs.segments):
                for j, seg2 in enumerate(cs.segments):
                    if i >= j:
                        continue
                    # Verificar si comparten un extremo (con tolerancia)
                    for p1 in [(seg1.x1, seg1.y1), (seg1.x2, seg1.y2)]:
                        for p2 in [(seg2.x1, seg2.y1), (seg2.x2, seg2.y2)]:
                            if abs(p1[0] - p2[0]) < 1 and abs(p1[1] - p2[1]) < 1:
                                connection_points.add((round(p1[0]), round(p1[1])))

            for segment in cs.segments:
                # Obtener esquinas del segmento
                corners = segment.get_corners()
                if len(corners) < 3:
                    continue

                # Extender el segmento en los extremos que conectan con otros
                # Esto asegura que los poligonos se solapen en las esquinas
                ext_corners = list(corners)

                # Vector direccion del segmento
                length = segment.length
                if length > 0:
                    dx = (segment.x2 - segment.x1) / length
                    dy = (segment.y2 - segment.y1) / length
                    # Vector perpendicular
                    nx, ny = -dy, dx

                    # Verificar si cada extremo es un punto de conexion
                    p1 = (round(segment.x1), round(segment.y1))
                    p2 = (round(segment.x2), round(segment.y2))

                    half_t = segment.thickness / 2

                    # Si el extremo 1 conecta, extender las esquinas 0 y 3 hacia atras
                    if p1 in connection_points:
                        ext_corners[0] = (corners[0][0] - dx * half_t, corners[0][1] - dy * half_t)
                        ext_corners[3] = (corners[3][0] - dx * half_t, corners[3][1] - dy * half_t)

                    # Si el extremo 2 conecta, extender las esquinas 1 y 2 hacia adelante
                    if p2 in connection_points:
                        ext_corners[1] = (corners[1][0] + dx * half_t, corners[1][1] + dy * half_t)
                        ext_corners[2] = (corners[2][0] + dx * half_t, corners[2][1] + dy * half_t)

                poly = Polygon(ext_corners)
                if poly.is_valid:
                    polygons.append(poly)

            if polygons:
                # Unir todos los poligonos
                unified = unary_union(polygons)

                # Dibujar el poligono unificado
                if unified.geom_type == 'Polygon':
                    ext_coords = list(unified.exterior.coords)
                    xs = [c[0] - center_x for c in ext_coords]
                    ys = [c[1] - center_y for c in ext_coords]
                    ax.fill(xs, ys, color=self.COLOR_CONCRETE, edgecolor=self.COLOR_CONCRETE_EDGE,
                           linewidth=2, zorder=1)
                elif unified.geom_type == 'MultiPolygon':
                    for poly in unified.geoms:
                        ext_coords = list(poly.exterior.coords)
                        xs = [c[0] - center_x for c in ext_coords]
                        ys = [c[1] - center_y for c in ext_coords]
                        ax.fill(xs, ys, color=self.COLOR_CONCRETE, edgecolor=self.COLOR_CONCRETE_EDGE,
                               linewidth=2, zorder=1)
            else:
                raise ValueError("No valid polygons")

        except (ImportError, Exception):
            # Fallback: dibujar cada segmento por separado (comportamiento anterior)
            for segment in cs.segments:
                corners = segment.get_corners()
                translated_corners = [(x - center_x, y - center_y) for x, y in corners]
                xs = [c[0] for c in translated_corners] + [translated_corners[0][0]]
                ys = [c[1] for c in translated_corners] + [translated_corners[0][1]]
                ax.fill(xs, ys, color=self.COLOR_CONCRETE, edgecolor=self.COLOR_CONCRETE_EDGE,
                       linewidth=2, zorder=1)

        # 2. Dibujar refuerzo usando el layout unificado
        layout = pier.get_rebar_layout()
        self._draw_bars_from_layout(ax, layout, offset_x=-center_x, offset_y=-center_y)

        # Variables para info (compatibilidad con leyenda)
        cover = pier.cover
        edge_bar_d = pier.diameter_edge
        n_edge = pier.n_edge_bars
        bar_radius = edge_bar_d / 2

        rows, bars_per_row = self._calculate_edge_bar_distribution(pier.n_meshes, n_edge)

        # 3. Marcar centroide
        cx, cy = cs.centroid
        ax.plot(cx - center_x, cy - center_y, 'r+', markersize=15, markeredgewidth=2,
               label='Centroide', zorder=10)

        # 4. Agregar dimensiones generales
        width = x_max - x_min
        height = y_max - y_min
        dim_offset = max(width, height) * 0.1

        arrow_props = dict(arrowstyle='<->', color=self.COLOR_DIMENSION, lw=1.5)

        # Dimension horizontal
        ax.annotate('', xy=(-width/2, -height/2 - dim_offset),
                   xytext=(width/2, -height/2 - dim_offset),
                   arrowprops=arrow_props)
        ax.text(0, -height/2 - dim_offset - 30, f'{width:.0f} mm',
               ha='center', va='top', fontsize=10, color=self.COLOR_DIMENSION)

        # Dimension vertical
        ax.annotate('', xy=(-width/2 - dim_offset, -height/2),
                   xytext=(-width/2 - dim_offset, height/2),
                   arrowprops=arrow_props)
        ax.text(-width/2 - dim_offset - 20, 0, f'{height:.0f} mm',
               ha='right', va='center', fontsize=10, color=self.COLOR_DIMENSION,
               rotation=90)

        # 5. Informacion de propiedades
        info_x = width/2 + dim_offset + 30
        info_y = height/2

        # Mapeo de tipos de forma a nombres
        shape_names = {
            'L': 'Forma L',
            'T': 'Forma T',
            'C': 'Forma C / U',
            'rectangular': 'Rectangular',
            'custom': 'Custom'
        }
        shape_name = shape_names.get(cs.shape_type.value, cs.shape_type.value)

        info_lines = [
            f"SECCION COMPUESTA",
            f"",
            f"Tipo: {shape_name}",
            f"Segmentos: {len(cs.segments)}",
            f"",
            f"PROPIEDADES:",
            f"Ag: {cs.Ag/100:.0f} cm2",
            f"Ixx: {cs.Ixx/1e8:.1f} x10^8 mm4",
            f"Iyy: {cs.Iyy/1e8:.1f} x10^8 mm4",
            f"",
            f"Centroide:",
            f"  x: {cs.centroid[0]:.0f} mm",
            f"  y: {cs.centroid[1]:.0f} mm",
            f"",
            f"Acv (alma): {cs.calculate_Acv('primary')/100:.0f} cm2",
        ]

        for i, line in enumerate(info_lines):
            ax.text(info_x, info_y - i * 20, line,
                   ha='left', va='top', fontsize=9,
                   fontfamily='monospace', color='#374151')

        # 6. Titulo
        ax.set_title(f'Seccion Compuesta - {pier.story} / {pier.label}\n'
                    f'({shape_name})',
                    fontsize=14, fontweight='bold')

        # 7. Configurar ejes
        ax.set_aspect('equal')
        margin = max(width, height) * 0.2
        ax.set_xlim(-width/2 - margin, width/2 + margin + 200)
        ax.set_ylim(-height/2 - margin, height/2 + margin)
        ax.axis('off')
        ax.legend(loc='lower right')

        plt.tight_layout()

        # Convertir a base64
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        plt.close(fig)

        return base64.b64encode(buffer.read()).decode('utf-8')