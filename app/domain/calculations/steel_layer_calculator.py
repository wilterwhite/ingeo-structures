# app/structural/domain/calculations/steel_layer_calculator.py
"""
Calculador de capas de acero para secciones de hormigón armado.
Unifica la lógica que antes estaba duplicada en pier.py e interaction_diagram.py.
"""
from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.pier import Pier
    from ..entities.drop_beam import DropBeam
    from ..entities.column import Column


@dataclass
class SteelLayer:
    """Una capa de acero en la sección."""
    position: float  # Distancia desde el borde superior/comprimido (mm)
    area: float      # Área de acero en esta capa (mm²)


class SteelLayerCalculator:
    """
    Calcula las capas de acero con sus posiciones reales para análisis P-M.

    Las capas incluyen:
    1. Barras de borde en el extremo superior (zona de compresión)
    2. Barras intermedias de malla a intervalos regulares
    3. Barras de borde en el extremo inferior (zona de tracción)
    """

    @staticmethod
    def calculate_from_pier(pier: 'Pier') -> List[SteelLayer]:
        """
        Genera las capas de acero a partir de un objeto Pier.

        Args:
            pier: Entidad Pier con la configuración de armadura

        Returns:
            Lista de SteelLayer ordenadas por posición
        """
        return SteelLayerCalculator.calculate(
            width=pier.width,
            cover=pier.cover,
            n_meshes=pier.n_meshes,
            n_edge_bars=pier.n_edge_bars,
            bar_area_edge=pier._bar_area_edge,
            bar_area_v=pier._bar_area_v,
            spacing_v=pier.spacing_v
        )

    @staticmethod
    def calculate_from_drop_beam(drop_beam: 'DropBeam') -> List[SteelLayer]:
        """
        Genera las capas de acero a partir de un objeto DropBeam.

        Args:
            drop_beam: Entidad DropBeam con la configuración de armadura

        Returns:
            Lista de SteelLayer ordenadas por posición
        """
        return SteelLayerCalculator.calculate(
            width=drop_beam.thickness,  # thickness es la dimensión mayor (ancho tributario)
            cover=drop_beam.cover,
            n_meshes=drop_beam.n_meshes,
            n_edge_bars=drop_beam.n_edge_bars,
            bar_area_edge=drop_beam._bar_area_edge,
            bar_area_v=drop_beam._bar_area_v,
            spacing_v=drop_beam.spacing_v
        )

    @staticmethod
    def calculate(
        width: float,
        cover: float,
        n_meshes: int,
        n_edge_bars: int,
        bar_area_edge: float,
        bar_area_v: float,
        spacing_v: float
    ) -> List[SteelLayer]:
        """
        Genera las capas de acero con sus posiciones reales.

        Args:
            width: Largo del muro en la dirección del momento (mm)
            cover: Recubrimiento al centro de la barra (mm)
            n_meshes: Número de mallas (1 o 2)
            n_edge_bars: Número de barras de borde por extremo
            bar_area_edge: Área de cada barra de borde (mm²)
            bar_area_v: Área de cada barra de malla vertical (mm²)
            spacing_v: Espaciamiento de la malla vertical (mm)

        Returns:
            Lista de SteelLayer ordenadas por posición
        """
        layers = []

        # Capa 1: Barras de borde en el extremo superior (compresión)
        # Todas las barras de borde se agrupan en una capa (simplificación conservadora)
        layers.append(SteelLayer(
            position=cover,
            area=n_edge_bars * bar_area_edge
        ))

        # Capas intermedias: barras de malla
        available_length = width - 2 * cover
        if available_length > 0 and spacing_v > 0:
            n_intermediate = int(available_length / spacing_v)
            for i in range(1, n_intermediate + 1):
                pos = cover + i * spacing_v
                # Solo agregar si está antes de la barra de borde opuesta
                if pos < width - cover - 1:  # -1mm de tolerancia
                    layers.append(SteelLayer(
                        position=pos,
                        area=n_meshes * bar_area_v
                    ))

        # Capa final: Barras de borde en el extremo inferior (tracción)
        layers.append(SteelLayer(
            position=width - cover,
            area=n_edge_bars * bar_area_edge
        ))

        return layers

    @staticmethod
    def calculate_from_column(
        column: 'Column',
        direction: str = 'depth'
    ) -> List[SteelLayer]:
        """
        Genera las capas de acero a partir de una columna rectangular.

        Las columnas tienen barras distribuidas en el perímetro, diferente
        a los muros que tienen malla + barras de borde.

        Args:
            column: Entidad Column con la configuración de armadura
            direction: 'depth' para M3, 'width' para M2

        Returns:
            Lista de SteelLayer ordenadas por posición
        """
        if direction == 'depth':
            return SteelLayerCalculator._calculate_column_layers(
                dimension=column.depth,
                cover=column.cover,
                n_layers=column.n_bars_depth,
                bars_per_layer=column.n_bars_width,
                bar_area=column._bar_area_long
            )
        else:
            return SteelLayerCalculator._calculate_column_layers(
                dimension=column.width,
                cover=column.cover,
                n_layers=column.n_bars_width,
                bars_per_layer=column.n_bars_depth,
                bar_area=column._bar_area_long
            )

    @staticmethod
    def _calculate_column_layers(
        dimension: float,
        cover: float,
        n_layers: int,
        bars_per_layer: int,
        bar_area: float
    ) -> List[SteelLayer]:
        """
        Genera capas de acero para una columna rectangular.

        Args:
            dimension: Dimensión en la dirección del momento (mm)
            cover: Recubrimiento (mm)
            n_layers: Número de capas de barras
            bars_per_layer: Barras por capa
            bar_area: Área de cada barra (mm²)

        Returns:
            Lista de SteelLayer ordenadas por posición
        """
        layers = []

        if n_layers < 2:
            # Mínimo 2 capas (una en cada extremo)
            return layers

        d_first = cover
        d_last = dimension - cover

        if n_layers == 2:
            positions = [d_first, d_last]
        else:
            spacing = (d_last - d_first) / (n_layers - 1)
            positions = [d_first + i * spacing for i in range(n_layers)]

        for pos in positions:
            layers.append(SteelLayer(
                position=pos,
                area=bars_per_layer * bar_area
            ))

        return layers
