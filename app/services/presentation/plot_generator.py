# app/structural/services/presentation/plot_generator.py
"""
Generador de gráficos para análisis estructural.
Crea diagramas de interacción P-M usando matplotlib.
"""
import base64
from io import BytesIO
from typing import List, Tuple, Optional

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para servidor
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


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

    def generate_summary_chart(
        self,
        results: List[dict],
        figsize: Tuple[int, int] = (10, 6)
    ) -> str:
        """
        Genera un gráfico de barras resumiendo los factores de seguridad.

        Muestra 1 barra por pier con el SF más crítico (mínimo entre flexión y corte).

        Args:
            results: Lista de diccionarios con 'pier_label', 'flexure_sf', 'shear_sf'
            figsize: Tamaño de la figura

        Returns:
            Imagen en formato base64
        """
        fig, ax = plt.subplots(figsize=figsize)

        labels = [r['pier_label'] for r in results]
        # Calcular SF mínimo (más crítico) por pier, limitado a 3 para visualización
        min_sf = [
            min(
                min(r.get('flexure_sf', float('inf')), 3),
                min(r.get('shear_sf', float('inf')), 3)
            )
            for r in results
        ]

        x = np.arange(len(labels))
        width = 0.6

        # Crear barras con colores según si pasan o no
        colors = [
            self.COLOR_DEMAND_OK if sf >= 1.0 else self.COLOR_DEMAND_FAIL
            for sf in min_sf
        ]
        bars = ax.bar(x, min_sf, width, color=colors, alpha=0.85, edgecolor='white')

        # Línea de referencia SF = 1
        ax.axhline(y=1, color='#374151', linewidth=1.5,
                  linestyle='--', label='SF = 1.0', zorder=1)

        # Agregar valores encima de las barras
        for bar, sf in zip(bars, min_sf):
            height = bar.get_height()
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

        # Límites
        ax.set_ylim(0, max(min_sf) * 1.25 if min_sf else 2)

        plt.tight_layout()

        # Convertir a base64
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        plt.close(fig)

        return base64.b64encode(buffer.read()).decode('utf-8')
