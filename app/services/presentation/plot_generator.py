# app/structural/services/presentation/plot_generator.py
"""
Generador de gráficos para análisis estructural.
Crea diagramas de interacción P-M usando matplotlib.
"""
import base64
from io import BytesIO
from typing import List, Tuple, Optional, TYPE_CHECKING
import math

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para servidor
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import numpy as np

if TYPE_CHECKING:
    from ...domain.entities import Pier


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

    # Límite máximo de SF para visualización
    SF_DISPLAY_MAX = 3.0

    def generate_summary_chart(
        self,
        results: List[dict],
        figsize: Tuple[int, int] = (10, 6)
    ) -> str:
        """
        Genera un gráfico de barras resumiendo los factores de seguridad.

        Muestra 1 barra por pier con el SF más crítico (mínimo entre flexión y corte).
        Los valores mayores a SF_DISPLAY_MAX (3.0) se muestran truncados con indicador ">3.0".

        Args:
            results: Lista de diccionarios con 'pier_label', 'flexure_sf', 'shear_sf'
            figsize: Tamaño de la figura

        Returns:
            Imagen en formato base64
        """
        fig, ax = plt.subplots(figsize=figsize)

        labels = [r['pier_label'] for r in results]

        # Calcular SF mínimo (más crítico) por pier - valores reales
        raw_sf = [
            min(
                r.get('flexure_sf', float('inf')),
                r.get('shear_sf', float('inf'))
            )
            for r in results
        ]

        # Valores truncados para visualización (máximo 3.0)
        display_sf = [min(sf, self.SF_DISPLAY_MAX) for sf in raw_sf]

        # Identificar cuáles exceden el límite
        exceeds_max = [sf > self.SF_DISPLAY_MAX for sf in raw_sf]

        x = np.arange(len(labels))
        width = 0.6

        # Crear barras con colores según si pasan o no
        colors = [
            self.COLOR_DEMAND_OK if sf >= 1.0 else self.COLOR_DEMAND_FAIL
            for sf in raw_sf
        ]
        bars = ax.bar(x, display_sf, width, color=colors, alpha=0.85, edgecolor='white')

        # Línea de referencia SF = 1
        ax.axhline(y=1, color='#374151', linewidth=1.5,
                  linestyle='--', label='SF = 1.0', zorder=1)

        # Agregar valores encima de las barras
        for bar, sf, exceeds in zip(bars, raw_sf, exceeds_max):
            height = bar.get_height()
            if exceeds:
                # Mostrar indicador de que excede el máximo
                label = f'>3.0'
                ax.annotate(label,
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8, fontweight='bold',
                           color='#6b7280')
                # Agregar puntos suspensivos en la parte superior de la barra
                ax.plot(bar.get_x() + bar.get_width() / 2, height - 0.08,
                       marker='.', color='white', markersize=4)
                ax.plot(bar.get_x() + bar.get_width() / 2, height - 0.18,
                       marker='.', color='white', markersize=4)
                ax.plot(bar.get_x() + bar.get_width() / 2, height - 0.28,
                       marker='.', color='white', markersize=4)
            else:
                ax.annotate(f'{sf:.2f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8, fontweight='bold')

        # Configuración
        ax.set_xlabel('Pier', fontsize=11)
        ax.set_ylabel('Factor de Seguridad Crítico', fontsize=11)
        ax.set_title('Resumen de Factores de Seguridad (SF mínimo por pier)', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax.grid(True, alpha=0.3, axis='y', zorder=0)

        # Leyenda simplificada
        ok_patch = mpatches.Patch(color=self.COLOR_DEMAND_OK, label='OK (SF ≥ 1.0)')
        fail_patch = mpatches.Patch(color=self.COLOR_DEMAND_FAIL, label='NO OK (SF < 1.0)')
        ax.legend(handles=[ok_patch, fail_patch], loc='upper right', fontsize=9)

        # Límites fijos: 0 a 3.0 (más un poco de margen para las etiquetas)
        ax.set_ylim(0, self.SF_DISPLAY_MAX + 0.4)

        plt.tight_layout()

        # Convertir a base64
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        plt.close(fig)

        return base64.b64encode(buffer.read()).decode('utf-8')

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

    def generate_section_diagram(
        self,
        pier: 'Pier',
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
        fig, ax = plt.subplots(figsize=figsize)

        # Dimensiones en mm
        lw = pier.width       # Largo del muro
        tw = pier.thickness   # Espesor
        cover = pier.cover

        # Escala para visualización (queremos que el muro quepa bien)
        scale = 1.0  # mm

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
        if pier.n_meshes == 1:
            # Malla simple: barras en el centro del espesor
            rows = 1
            bars_per_row = n_edge
        else:
            # Malla doble: barras en 2 capas
            rows = 2
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

            # 4. Dibujar estribos de confinamiento
            stirrup_width = boundary_length - stirrup_d
            stirrup_height = tw - 2 * cover + stirrup_d

            # Estribo izquierdo
            stirrup_left = Rectangle(
                (x0 + cover - stirrup_d/2, y0 + cover - stirrup_d/2),
                stirrup_width, stirrup_height,
                facecolor='none',
                edgecolor=self.COLOR_STIRRUP,
                linewidth=1.5,
                linestyle='-',
                zorder=4
            )
            ax.add_patch(stirrup_left)

            # Estribo derecho
            stirrup_right = Rectangle(
                (x0 + lw - boundary_length + stirrup_d/2, y0 + cover - stirrup_d/2),
                stirrup_width, stirrup_height,
                facecolor='none',
                edgecolor=self.COLOR_STIRRUP,
                linewidth=1.5,
                linestyle='-',
                zorder=4
            )
            ax.add_patch(stirrup_right)

        # 5. Dibujar barras de borde
        bar_radius = edge_bar_d / 2

        # Posiciones Y de las barras según número de filas
        if rows == 1:
            y_positions = [0]  # Centro
        else:
            y_positions = [y0 + cover + edge_bar_d/2,
                          y0 + tw - cover - edge_bar_d/2]

        # Barras en extremo izquierdo
        for row_idx, y_bar in enumerate(y_positions):
            for col_idx in range(bars_per_row):
                x_bar = x0 + cover + edge_bar_d/2 + col_idx * bar_spacing_x
                bar = Circle(
                    (x_bar, y_bar), bar_radius,
                    facecolor=self.COLOR_REBAR,
                    edgecolor='white',
                    linewidth=0.5,
                    zorder=5
                )
                ax.add_patch(bar)

        # Barras en extremo derecho
        for row_idx, y_bar in enumerate(y_positions):
            for col_idx in range(bars_per_row):
                x_bar = x0 + lw - cover - edge_bar_d/2 - col_idx * bar_spacing_x
                bar = Circle(
                    (x_bar, y_bar), bar_radius,
                    facecolor=self.COLOR_REBAR,
                    edgecolor='white',
                    linewidth=0.5,
                    zorder=5
                )
                ax.add_patch(bar)

        # 6. Dibujar armadura distribuida (malla intermedia)
        mesh_bar_d = pier.diameter_v
        mesh_bar_radius = mesh_bar_d / 2
        mesh_spacing = pier.spacing_v

        # Calcular número de barras intermedias y centrarlas
        # Si hay elementos de borde, las barras de malla van ENTRE ellos
        # Si no hay elementos de borde, van entre las barras de borde (desde cover)
        if has_boundary_element:
            # Las barras de malla van entre los elementos de borde
            mesh_start = boundary_length
            mesh_end = lw - boundary_length
        else:
            # Las barras de malla van desde cover a lw-cover
            mesh_start = cover
            mesh_end = lw - cover

        # Espacio disponible para barras intermedias
        available_span = mesh_end - mesh_start

        # Número de barras intermedias necesarias en el espacio disponible
        # El espaciamiento es el MÁXIMO permitido entre barras
        # Si available_span > spacing, necesitamos barras para que ningún tramo exceda el máximo
        if available_span > mesh_spacing:
            # Número de barras necesarias para que el espaciamiento no exceda el máximo
            # n_intermediate = ceil(available_span / mesh_spacing) - 1
            n_intermediate = math.ceil(available_span / mesh_spacing) - 1
        else:
            # El espacio ya es menor que el máximo permitido, no se necesitan barras
            n_intermediate = 0

        if n_intermediate > 0 and available_span > 0:
            # Calcular posiciones centradas
            # Distribuir n_intermediate barras en el espacio disponible
            actual_spacing = available_span / (n_intermediate + 1)

            # Posición de la primera barra intermedia
            first_bar_pos = mesh_start + actual_spacing

            # Dibujar barras intermedias centradas
            for i in range(n_intermediate):
                bar_x = x0 + first_bar_pos + i * actual_spacing
                for y_bar in y_positions:
                    bar = Circle(
                        (bar_x, y_bar), mesh_bar_radius,
                        facecolor=self.COLOR_REBAR,
                        edgecolor='white',
                        linewidth=0.5,
                        zorder=5
                    )
                    ax.add_patch(bar)

        # 7. Agregar dimensiones
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

        # 8. Agregar leyenda de armadura
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

        # 9. Título
        ax.set_title(f'Seccion Transversal - {pier.story} / {pier.label}\n'
                    f'({lw/1000:.2f}m x {tw/1000:.2f}m)',
                    fontsize=14, fontweight='bold')

        # 10. Configurar ejes
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
