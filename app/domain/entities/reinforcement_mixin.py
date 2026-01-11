# app/domain/entities/reinforcement_mixin.py
"""
Mixin con propiedades de armadura para elementos tipo muro (Pier, DropBeam).

Elimina duplicación de cálculos de armadura de malla distribuida y barras de borde.
"""
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..calculations.steel_layer_calculator import SteelLayer


class MeshReinforcementMixin:
    """
    Mixin que provee propiedades de armadura de malla distribuida.

    Las clases que usen este mixin deben tener los siguientes atributos:
    - n_meshes: int (número de mallas, 1 o 2)
    - spacing_v: int (espaciamiento vertical en mm)
    - spacing_h: int (espaciamiento horizontal en mm)
    - n_edge_bars: int (barras de borde por extremo)
    - _bar_area_v: float (área de barra vertical en mm²)
    - _bar_area_h: float (área de barra horizontal en mm²)
    - _bar_area_edge: float (área de barra de borde en mm²)
    - cover: float (recubrimiento en mm)
    - Ag: float (property, área bruta en mm²)
    - _get_mesh_length(): método que retorna la longitud para calcular barras

    Para Pier: _get_mesh_length() retorna width
    Para DropBeam: _get_mesh_length() retorna thickness
    """

    # Atributos requeridos (declarados para type hints)
    n_meshes: int
    spacing_v: int
    spacing_h: int
    n_edge_bars: int
    _bar_area_v: float
    _bar_area_h: float
    _bar_area_edge: float
    cover: float

    def _get_mesh_length(self) -> float:
        """
        Longitud disponible para barras de malla.

        Debe ser implementado por la clase que use el mixin.
        - Pier: retorna self.width
        - DropBeam: retorna self.thickness
        """
        raise NotImplementedError

    def _get_thickness_for_rho_h(self) -> float:
        """
        Espesor para cálculo de cuantía horizontal.

        Debe ser implementado por la clase que use el mixin.
        - Pier: retorna self.thickness
        - DropBeam: retorna self.width
        """
        raise NotImplementedError

    @property
    def Ag(self) -> float:
        """Área bruta (mm²). Debe ser implementado por la clase."""
        raise NotImplementedError

    # =========================================================================
    # Propiedades de Armadura de Malla
    # =========================================================================

    @property
    def n_intermediate_bars(self) -> int:
        """
        Número de barras intermedias de malla (sin contar las de borde).

        Cálculo:
        - Distancia disponible = mesh_length - 2×cover
        - Espacios que caben = distancia_disponible / espaciamiento
        - Barras = floor(espacios)
        """
        available_length = self._get_mesh_length() - 2 * self.cover
        if available_length <= 0:
            return 0
        n_spaces = available_length / self.spacing_v
        return max(0, int(n_spaces))

    @property
    def As_vertical(self) -> float:
        """
        Área de acero vertical de malla intermedia (mm²).

        Solo cuenta las barras intermedias (entre las de borde).
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
        debe ser rho_l >= 0.0025, calculado solo con las mallas.
        """
        return self.As_vertical / self.Ag

    @property
    def rho_horizontal(self) -> float:
        """Cuantía de acero horizontal (malla distribuida)."""
        thickness = self._get_thickness_for_rho_h()
        return self.As_horizontal / (thickness * 1000)

    # =========================================================================
    # Propiedades de Barras de Borde
    # =========================================================================

    @property
    def As_edge_total(self) -> float:
        """
        Área de acero de borde TOTAL (mm²).

        Cálculo: n_edge_bars barras × 2 extremos × área_barra
        """
        return self.n_edge_bars * 2 * self._bar_area_edge

    @property
    def As_edge_per_end(self) -> float:
        """Área de acero de borde en cada extremo (mm²)."""
        return self.n_edge_bars * self._bar_area_edge

    @property
    def n_edge_bars_per_end(self) -> int:
        """Número de barras de borde en cada extremo."""
        return self.n_edge_bars

    @property
    def As_flexure_total(self) -> float:
        """
        Área de acero total para flexión (mm²).

        Total = As_edge_total + As_vertical
        """
        return self.As_edge_total + self.As_vertical

    @property
    def n_total_vertical_bars(self) -> int:
        """Número total de barras verticales (borde + intermedias)."""
        n_edge = self.n_meshes * 2  # 2 extremos
        n_intermediate = self.n_intermediate_bars * self.n_meshes
        return n_edge + n_intermediate
