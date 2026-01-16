# app/domain/entities/rebar.py
"""
Entidades para la armadura: RebarPosition y RebarLayout.

UNICA fuente de verdad para posiciones de armadura.
Usado tanto por visualizacion (plot_generator) como por calculos (diagrama P-M).
"""
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..calculations.steel_layer_calculator import SteelLayer


@dataclass
class RebarPosition:
    """
    Una barra individual con posicion 2D.

    Coordenadas relativas al origen de la seccion (esquina inferior izquierda).
    """
    x: float              # mm desde origen de la seccion
    y: float              # mm desde origen de la seccion
    diameter: float       # mm
    area: float           # mm2
    bar_type: str         # 'edge', 'mesh', 'intersection', 'corner'
    segment_id: int = 0   # Para secciones compuestas (identifica el segmento)

    @property
    def radius(self) -> float:
        """Radio de la barra en mm."""
        return self.diameter / 2


@dataclass
class RebarLayout:
    """
    UNICA fuente de verdad para posiciones de armadura.

    Contiene todas las barras con su posicion 2D exacta.
    Puede convertirse a capas 1D para calculos P-M (get_steel_layers).
    Para visualizacion, iterar directamente sobre .bars.
    """
    bars: List[RebarPosition] = field(default_factory=list)
    cover: float = 40.0
    section_width: float = 0.0   # lw - para convertir a capas 1D
    section_height: float = 0.0  # tw - para convertir a capas 1D

    def get_steel_layers(self, direction: str = 'primary') -> List['SteelLayer']:
        """
        Convierte barras 2D a capas 1D para calculos P-M.

        Args:
            direction: 'primary' agrupa por posicion X (flexion en eje fuerte)
                      'secondary' agrupa por posicion Y (flexion en eje debil)

        Returns:
            Lista de SteelLayer ordenadas por posicion.
        """
        if not self.bars:
            return []

        use_x = (direction == 'primary')
        return self._group_bars_by_axis(use_x=use_x)

    def _group_bars_by_axis(self, use_x: bool = True) -> List['SteelLayer']:
        """
        Agrupa barras por posicion en un eje.

        Args:
            use_x: True para agrupar por X, False para agrupar por Y

        Returns:
            Lista de SteelLayer ordenadas por posicion.
        """
        from ..calculations.steel_layer_calculator import SteelLayer

        tolerance = 5.0  # mm
        groups: dict = {}

        for bar in self.bars:
            pos = bar.x if use_x else bar.y

            # Buscar grupo existente dentro de tolerancia
            found_group = None
            for group_pos in groups:
                if abs(pos - group_pos) < tolerance:
                    found_group = group_pos
                    break

            if found_group is not None:
                groups[found_group] += bar.area
            else:
                groups[pos] = bar.area

        return [
            SteelLayer(position=p, area=a)
            for p, a in sorted(groups.items())
        ]

    @property
    def total_area(self) -> float:
        """Area total de acero (mm2)."""
        return sum(bar.area for bar in self.bars)

    @property
    def n_bars(self) -> int:
        """Numero total de barras."""
        return len(self.bars)

    def add_bar(
        self,
        x: float,
        y: float,
        diameter: float,
        area: float,
        bar_type: str = 'mesh',
        segment_id: int = 0
    ) -> None:
        """Agrega una barra al layout."""
        self.bars.append(RebarPosition(
            x=x,
            y=y,
            diameter=diameter,
            area=area,
            bar_type=bar_type,
            segment_id=segment_id
        ))

    def __repr__(self) -> str:
        return (
            f"RebarLayout(n_bars={self.n_bars}, "
            f"total_area={self.total_area:.0f}mm2, "
            f"section={self.section_width:.0f}x{self.section_height:.0f}mm)"
        )
