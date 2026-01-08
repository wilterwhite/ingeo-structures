# app/domain/entities/pier.py
"""
Entidad Pier: representa un muro de hormigón armado desde ETABS.
"""
from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING

from ..constants.materials import get_bar_area
from ..constants.reinforcement import RHO_MIN, FY_DEFAULT_MPA

if TYPE_CHECKING:
    from ..calculations.steel_layer_calculator import SteelLayer


@dataclass
class Pier:
    """
    Representa un pier/muro de hormigón armado desde ETABS.

    Unidades:
    - Dimensiones: mm
    - Esfuerzos: MPa
    - Áreas: mm²
    """
    label: str              # "PMar-C4-1" (Grilla-Eje-id)
    story: str              # "Cielo P2"

    # Geometría (mm)
    width: float            # Largo del muro (Width en ETABS)
    thickness: float        # Espesor del muro
    height: float           # Altura del piso

    # Propiedades del material (MPa)
    fc: float               # f'c del hormigón
    fy: float = FY_DEFAULT_MPA  # fy del acero (default A630-420H)

    # Configuración de armadura (malla, diámetro, espaciamiento)
    # spacing=0 significa "usar armadura mínima según espesor"
    n_meshes: int = 2           # 1=malla central, 2=doble cara
    diameter_v: int = 8         # Diámetro barra vertical (mm)
    spacing_v: int = 0          # Espaciamiento vertical (mm), 0=calcular mínimo
    diameter_h: int = 8         # Diámetro barra horizontal (mm)
    spacing_h: int = 0          # Espaciamiento horizontal (mm), 0=calcular mínimo

    # Elemento de borde (barras adicionales en los extremos del muro)
    n_edge_bars: int = 2        # Número de barras de borde por extremo
    diameter_edge: int = 12     # Diámetro barra de borde (mm)

    # Estribos de confinamiento en elemento de borde
    stirrup_diameter: int = 10  # Diámetro estribo (mm)
    stirrup_spacing: int = 150  # Espaciamiento estribos (mm)
    n_stirrup_legs: int = 2     # Número de ramas del estribo (2, 3 o 4)

    # Otros
    cover: float = 25.0     # Recubrimiento (mm) - 2.5cm default
    axis_angle: float = 0.0 # Ángulo del eje local

    # Clasificacion sismica (para cortante)
    # True = diseño sismico especial (§18.7.6/§18.10.4), False = no sismico (§22.5/§11.5)
    is_seismic: bool = True

    # Áreas de barra precalculadas (se calculan en __post_init__)
    _bar_area_v: float = field(default=50.3, repr=False)  # φ8 por defecto
    _bar_area_h: float = field(default=50.3, repr=False)
    _bar_area_edge: float = field(default=78.5, repr=False)  # φ10 por defecto

    def __post_init__(self):
        """Calcula áreas de barra según diámetros y aplica armadura mínima si no se especificó."""
        self._bar_area_v = get_bar_area(self.diameter_v, 50.3)
        self._bar_area_h = get_bar_area(self.diameter_h, 50.3)
        self._bar_area_edge = get_bar_area(self.diameter_edge, 78.5)

        # Si no se especificó armadura (spacing=0), calcular mínima según espesor
        if self.spacing_v == 0:
            self._apply_minimum_reinforcement()

    def _apply_minimum_reinforcement(self):
        """
        Aplica armadura mínima según ACI 318-25.

        Reglas:
        - ρmin = 0.0025 (§11.6.1)
        - Espesor ≤ 130mm: malla simple (§11.7.2.3)
        - Espesor > 130mm: malla doble
        - Diámetro por defecto: φ8
        - Espaciamiento: redondeado hacia abajo a múltiplo de 5mm
        """
        # Determinar número de mallas según espesor
        self.n_meshes = 1 if self.thickness <= 130 else 2

        # Diámetro φ8 por defecto
        self.diameter_v = 8
        self.diameter_h = 8
        self._bar_area_v = get_bar_area(8)
        self._bar_area_h = get_bar_area(8)

        # Calcular espaciamiento para ρmin = 0.0025
        spacing = self._calculate_min_spacing()
        self.spacing_v = spacing
        self.spacing_h = spacing

    def _calculate_min_spacing(self) -> int:
        """
        Calcula espaciamiento para armadura mínima (ρ=0.25%).

        Fórmula: s = n_meshes × As_barra × 1000 / (ρmin × t × 1000)
        Redondea hacia abajo a múltiplo de 5mm para cumplir ρ >= ρmin.
        """
        As_min_per_m = RHO_MIN * self.thickness * 1000  # mm²/m
        spacing_exact = self.n_meshes * self._bar_area_v * 1000 / As_min_per_m

        # Redondear hacia abajo a múltiplo de 5mm (para cumplir >= ρmin)
        spacing = int(spacing_exact // 5) * 5

        # Limitar a rango típico [100, 300]
        spacing = max(100, min(300, spacing))

        return spacing

    # =========================================================================
    # Propiedades de Armadura
    # =========================================================================

    @property
    def n_intermediate_bars(self) -> int:
        """
        Número de barras intermedias de malla (sin contar las de borde).

        Cálculo:
        - Distancia disponible = width - 2×cover (restamos recubrimiento de cada lado)
        - Espacios que caben = distancia_disponible / espaciamiento
        - Barras = floor(espacios) - estas son las barras entre las de borde

        Ejemplo 50cm con cover=2.5cm, spacing=20cm:
        - Disponible = 500 - 50 = 450mm
        - Espacios = 450/200 = 2.25
        - Barras = floor(2.25) = 2 barras intermedias por cara

        Ejemplo 20cm con cover=2.5cm, spacing=20cm:
        - Disponible = 200 - 50 = 150mm
        - Espacios = 150/200 = 0.75
        - Barras = floor(0.75) = 0 barras (solo quedan las de esquina)
        """
        # Distancia entre las barras de borde (restamos recubrimiento de cada lado)
        available_length = self.width - 2 * self.cover
        if available_length <= 0:
            return 0
        # Número de espacios que caben
        n_spaces = available_length / self.spacing_v
        # Número de barras intermedias (truncamos)
        return max(0, int(n_spaces))

    @property
    def As_vertical(self) -> float:
        """
        Área de acero vertical de malla intermedia (mm²).

        Solo cuenta las barras intermedias (entre las de borde).
        Para cada cara de malla: n_intermediate_bars × área_barra
        Total: n_intermediate_bars × n_meshes × área_barra
        """
        return self.n_intermediate_bars * self.n_meshes * self._bar_area_v

    @property
    def As_horizontal(self) -> float:
        """
        Área de acero horizontal por metro de altura (mm²/m).

        Cálculo: n_meshes × (área_barra / espaciamiento) × 1000
        """
        return self.n_meshes * (self._bar_area_h / self.spacing_h) * 1000

    @property
    def As_vertical_per_m(self) -> float:
        """Área de acero vertical por metro de longitud (mm²/m)."""
        return self.n_meshes * (self._bar_area_v / self.spacing_v) * 1000

    @property
    def rho_vertical(self) -> float:
        """Cuantía de acero vertical total (malla + borde)."""
        return (self.As_vertical + self.As_edge_total) / self.Ag

    @property
    def rho_mesh_vertical(self) -> float:
        """
        Cuantía de acero vertical distribuido (solo malla, sin barras de borde).

        Según ACI 318-25 §18.10.2.1, el refuerzo distribuido mínimo
        debe ser ρℓ ≥ 0.0025, calculado solo con las mallas.
        """
        return self.As_vertical / self.Ag

    @property
    def rho_horizontal(self) -> float:
        """Cuantía de acero horizontal (malla distribuida)."""
        return self.As_horizontal / (self.thickness * 1000)

    @property
    def As_edge_total(self) -> float:
        """
        Área de acero de borde TOTAL (mm²).

        Cálculo: n_edge_bars barras × 2 extremos × área_barra
        Ejemplo: 4 barras por extremo × 2 extremos = 8 barras total
        """
        return self.n_edge_bars * 2 * self._bar_area_edge

    @property
    def As_edge_per_end(self) -> float:
        """Área de acero de borde en cada extremo del muro (mm²)."""
        return self.n_edge_bars * self._bar_area_edge

    @property
    def n_edge_bars_per_end(self) -> int:
        """Número de barras de borde en cada extremo del muro."""
        return self.n_edge_bars

    @property
    def As_boundary_left(self) -> float:
        """
        Area de acero en zona de extremo izquierdo (0.15×lw) segun §18.10.2.4.

        Incluye:
        - Barras de borde (todas las n_edge_bars del extremo izquierdo)
        - Barras de malla dentro de la zona de 0.15×lw

        La zona de extremo empieza en x=0 (borde izquierdo) y termina en x=0.15×lw.
        """
        return self._calculate_boundary_zone_steel(is_left=True)

    @property
    def As_boundary_right(self) -> float:
        """
        Area de acero en zona de extremo derecho (0.15×lw) segun §18.10.2.4.

        Incluye:
        - Barras de borde (todas las n_edge_bars del extremo derecho)
        - Barras de malla dentro de la zona de 0.15×lw

        La zona de extremo empieza en x=(lw - 0.15×lw) y termina en x=lw.
        """
        return self._calculate_boundary_zone_steel(is_left=False)

    def _calculate_boundary_zone_steel(self, is_left: bool) -> float:
        """
        Calcula el area de acero dentro de la zona de extremo (0.15×lw).

        Args:
            is_left: True para extremo izquierdo, False para derecho

        Returns:
            Area de acero en mm² dentro de la zona de extremo
        """
        boundary_length = 0.15 * self.width

        # 1. Barras de borde: todas estan dentro de la zona de extremo
        As_edge = self.As_edge_per_end

        # 2. Barras de malla dentro de la zona
        # Las barras de malla empiezan en x=cover y se repiten cada spacing_v
        # Primera barra intermedia en x = cover + spacing_v
        As_mesh = 0.0
        if self.spacing_v > 0:
            # Calcular cuantas barras de malla caen dentro de boundary_length
            if is_left:
                # Zona izquierda: desde 0 hasta boundary_length
                # Primera barra de malla en cover, luego cada spacing_v
                x = self.cover
                while x < boundary_length and x < (self.width - self.cover):
                    As_mesh += self.n_meshes * self._bar_area_v
                    x += self.spacing_v
            else:
                # Zona derecha: desde (width - boundary_length) hasta width
                start_zone = self.width - boundary_length
                # Ultima barra en width - cover, y hacia atras cada spacing_v
                x = self.width - self.cover
                while x > start_zone and x > self.cover:
                    As_mesh += self.n_meshes * self._bar_area_v
                    x -= self.spacing_v

        return As_edge + As_mesh

    @property
    def As_flexure_total(self) -> float:
        """
        Área de acero total para flexión (mm²).

        Total = As_edge_total + As_vertical
        - As_edge_total: barras en los extremos (esquinas)
        - As_vertical: barras intermedias de malla (puede ser 0 si no caben)
        """
        return self.As_edge_total + self.As_vertical

    @property
    def n_total_vertical_bars(self) -> int:
        """Número total de barras verticales (borde + intermedias)."""
        n_edge = self.n_meshes * 2  # 2 extremos
        n_intermediate = self.n_intermediate_bars * self.n_meshes
        return n_edge + n_intermediate

    def get_steel_layers(self, direction: str = 'primary') -> List['SteelLayer']:
        """
        Genera las capas de acero con sus posiciones reales para el diagrama P-M.

        Args:
            direction: 'primary' para eje fuerte (M3), 'secondary' para eje debil (M2)
                       Para muros, primary siempre usa la distribucion normal.

        Returns:
            Lista de SteelLayer ordenadas por posición.
            - position: distancia desde el borde comprimido (mm)
            - area: área de acero en esa capa (mm²)

        Ejemplo para columna 20×20 con 4φ10:
            [SteelLayer(40, 157), SteelLayer(160, 157)]

        Ejemplo para muro 2m×0.2m con 2M φ8@200 +2φ10:
            [SteelLayer(40, 157), SteelLayer(240, 100.6), ...]
        """
        from ..calculations.steel_layer_calculator import SteelLayerCalculator
        # Para muros, usamos la misma distribucion independiente de direction
        # (el refuerzo es simetrico en ambas caras)
        return SteelLayerCalculator.calculate_from_pier(self)

    @property
    def reinforcement_description(self) -> str:
        """Descripción legible de la armadura."""
        mesh_text = "1M" if self.n_meshes == 1 else "2M"
        edge_text = f"+{self.n_edge_bars}φ{self.diameter_edge}"
        stirrup_text = f"E{self.stirrup_diameter}@{self.stirrup_spacing}"
        return f"{mesh_text} φ{self.diameter_v}@{self.spacing_v} {edge_text} {stirrup_text}"

    # =========================================================================
    # Propiedades Geométricas
    # =========================================================================

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

    @property
    def Ag(self) -> float:
        """Área bruta del muro (mm²)."""
        return self.width * self.thickness

    @property
    def d(self) -> float:
        """Profundidad efectiva (mm)."""
        return self.width - self.cover

    # =========================================================================
    # Métodos de Actualización
    # =========================================================================

    def update_reinforcement(
        self,
        n_meshes: Optional[int] = None,
        diameter_v: Optional[int] = None,
        spacing_v: Optional[int] = None,
        diameter_h: Optional[int] = None,
        spacing_h: Optional[int] = None,
        diameter_edge: Optional[int] = None,
        n_edge_bars: Optional[int] = None,
        stirrup_diameter: Optional[int] = None,
        stirrup_spacing: Optional[int] = None,
        n_stirrup_legs: Optional[int] = None,
        fy: Optional[float] = None,
        cover: Optional[float] = None
    ):
        """
        Actualiza la configuración de armadura.

        Args:
            n_meshes: Número de mallas (1 o 2)
            diameter_v: Diámetro barra vertical (mm)
            spacing_v: Espaciamiento vertical (mm)
            diameter_h: Diámetro barra horizontal (mm)
            spacing_h: Espaciamiento horizontal (mm)
            diameter_edge: Diámetro barra de borde (mm)
            n_edge_bars: Número de barras de borde por extremo
            stirrup_diameter: Diámetro estribo confinamiento (mm)
            stirrup_spacing: Espaciamiento estribos (mm)
            n_stirrup_legs: Número de ramas del estribo (2, 3 o 4)
            fy: Límite de fluencia (MPa)
            cover: Recubrimiento (mm)
        """
        if n_meshes is not None:
            self.n_meshes = n_meshes
        if diameter_v is not None:
            self.diameter_v = diameter_v
            self._bar_area_v = get_bar_area(diameter_v, 50.3)
        if spacing_v is not None:
            self.spacing_v = spacing_v
        if diameter_h is not None:
            self.diameter_h = diameter_h
            self._bar_area_h = get_bar_area(diameter_h, 50.3)
        if spacing_h is not None:
            self.spacing_h = spacing_h
        if diameter_edge is not None:
            self.diameter_edge = diameter_edge
            self._bar_area_edge = get_bar_area(diameter_edge, 78.5)
        if n_edge_bars is not None:
            self.n_edge_bars = n_edge_bars
        if stirrup_diameter is not None:
            self.stirrup_diameter = stirrup_diameter
        if stirrup_spacing is not None:
            self.stirrup_spacing = stirrup_spacing
        if n_stirrup_legs is not None:
            self.n_stirrup_legs = n_stirrup_legs
        if fy is not None:
            self.fy = fy
        if cover is not None:
            self.cover = cover

    def set_minimum_reinforcement(self, diameter: int = 8):
        """
        Configura armadura mínima con el diámetro especificado.

        Args:
            diameter: Diámetro de barra (mm), default 8
        """
        self.diameter_v = diameter
        self.diameter_h = diameter
        self._bar_area_v = get_bar_area(diameter, 50.3)
        self._bar_area_h = self._bar_area_v
        self.spacing_v = self._calculate_min_spacing()
        self.spacing_h = self.spacing_v

    # =========================================================================
    # Métodos para Protocol FlexuralElement
    # =========================================================================

    def get_section_dimensions(self, direction: str = 'primary') -> tuple:
        """
        Obtiene las dimensiones de la seccion para la curva P-M.

        Para muros/piers:
        - 'primary': flexion en el plano del muro (eje fuerte M3)
        - 'secondary': flexion fuera del plano (eje debil M2)

        Args:
            direction: 'primary' o 'secondary'

        Returns:
            Tuple (width, thickness) en mm
        """
        if direction == 'primary':
            return (self.width, self.thickness)
        else:
            return (self.thickness, self.width)

