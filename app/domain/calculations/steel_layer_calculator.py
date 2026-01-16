# app/domain/calculations/steel_layer_calculator.py
"""
Calculador de capas de acero para secciones de hormigon armado.
Unifica la logica para VerticalElement y HorizontalElement.
"""
from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.vertical_element import VerticalElement


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
    def calculate_from_vertical_element_discrete(
        element: 'VerticalElement',
        direction: str = 'primary'
    ) -> List[SteelLayer]:
        """
        Genera capas de acero para VerticalElement con layout STIRRUPS.

        Args:
            element: VerticalElement con discrete_reinforcement
            direction: 'primary' para length, 'secondary' para thickness

        Returns:
            Lista de SteelLayer ordenadas por posicion
        """
        if not element.discrete_reinforcement:
            return []

        dr = element.discrete_reinforcement
        if direction == 'primary':
            return SteelLayerCalculator._calculate_column_layers(
                dimension=element.length,
                cover=element.cover,
                n_layers=dr.n_bars_length,
                bars_per_layer=dr.n_bars_thickness,
                bar_area=dr._bar_area
            )
        else:
            return SteelLayerCalculator._calculate_column_layers(
                dimension=element.thickness,
                cover=element.cover,
                n_layers=dr.n_bars_thickness,
                bars_per_layer=dr.n_bars_length,
                bar_area=dr._bar_area
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

        # Caso especial: 1 barra centrada (hormigón no confinado, ACI Cap. 14)
        # Para pilares ICF pequeños con 1 fierro central
        if n_layers == 1 and bars_per_layer == 1:
            layers.append(SteelLayer(
                position=dimension / 2,  # Barra centrada
                area=bar_area
            ))
            return layers

        if n_layers < 2:
            # Caso inesperado (ej: n_layers=1, bars_per_layer>1)
            # Retornar vacío, se manejará como error arriba
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
