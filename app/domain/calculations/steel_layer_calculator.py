# app/structural/domain/calculations/steel_layer_calculator.py
"""
Calculador de capas de acero para secciones de hormigón armado.
Unifica la lógica que antes estaba duplicada en pier.py e interaction_diagram.py.
"""
from dataclasses import dataclass
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.pier import Pier


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
            bar_area_edge=pier._bar_area_edge,
            bar_area_v=pier._bar_area_v,
            spacing_v=pier.spacing_v
        )

    @staticmethod
    def calculate(
        width: float,
        cover: float,
        n_meshes: int,
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
            bar_area_edge: Área de cada barra de borde (mm²)
            bar_area_v: Área de cada barra de malla vertical (mm²)
            spacing_v: Espaciamiento de la malla vertical (mm)

        Returns:
            Lista de SteelLayer ordenadas por posición
        """
        layers = []

        # Capa 1: Barras de borde en el extremo superior (compresión)
        layers.append(SteelLayer(
            position=cover,
            area=n_meshes * bar_area_edge
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
            area=n_meshes * bar_area_edge
        ))

        return layers

    @staticmethod
    def to_tuples(layers: List[SteelLayer]) -> List[Tuple[float, float]]:
        """
        Convierte lista de SteelLayer a lista de tuplas (position, area).

        Útil para compatibilidad con código existente que espera tuplas.

        Args:
            layers: Lista de SteelLayer

        Returns:
            Lista de tuplas (position_mm, area_mm2)
        """
        return [(layer.position, layer.area) for layer in layers]

    @staticmethod
    def from_tuples(tuples: List[Tuple[float, float]]) -> List[SteelLayer]:
        """
        Convierte lista de tuplas a lista de SteelLayer.

        Args:
            tuples: Lista de tuplas (position_mm, area_mm2)

        Returns:
            Lista de SteelLayer
        """
        return [SteelLayer(position=t[0], area=t[1]) for t in tuples]

    @staticmethod
    def calculate_total_area(layers: List[SteelLayer]) -> float:
        """
        Calcula el área total de acero en todas las capas.

        Args:
            layers: Lista de SteelLayer

        Returns:
            Área total (mm²)
        """
        return sum(layer.area for layer in layers)
