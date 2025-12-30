# app/structural/domain/calculations/reinforcement_calculator.py
"""
Calculador de propiedades de armadura para secciones de hormigón armado.
Extrae la lógica de cálculo que antes estaba en pier.py para mantener
la entidad Pier como un contenedor de datos puro.
"""
from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.pier import Pier


# Áreas de barras estándar (mm²)
BAR_AREAS: Dict[int, float] = {
    6: 28.3, 8: 50.3, 10: 78.5, 12: 113.1,
    16: 201.1, 18: 254.5, 20: 314.2, 22: 380.1,
    25: 490.9, 28: 615.8, 32: 804.2, 36: 1017.9,
}


@dataclass
class ReinforcementProperties:
    """Propiedades calculadas de armadura."""
    n_intermediate_bars: int      # Barras intermedias por cara
    As_vertical: float            # Área acero vertical intermedio (mm²)
    As_horizontal: float          # Área acero horizontal por metro (mm²/m)
    As_vertical_per_m: float      # Área acero vertical por metro (mm²/m)
    As_edge_total: float          # Área acero de borde total (mm²)
    As_edge_per_end: float        # Área acero de borde por extremo (mm²)
    As_flexure_total: float       # Área total para flexión (mm²)
    n_edge_bars_per_end: int      # Barras de borde por extremo
    n_total_vertical_bars: int    # Total barras verticales
    rho_vertical: float           # Cuantía vertical
    rho_horizontal: float         # Cuantía horizontal


class ReinforcementCalculator:
    """
    Calcula propiedades de armadura para secciones de hormigón armado.

    Responsabilidades:
    - Calcular número de barras intermedias
    - Calcular áreas de acero (vertical, horizontal, bordes)
    - Calcular cuantías
    - Calcular espaciamiento mínimo
    """

    @staticmethod
    def get_bar_area(diameter: int) -> float:
        """
        Obtiene el área de una barra dado su diámetro.

        Args:
            diameter: Diámetro de la barra (mm)

        Returns:
            Área de la barra (mm²)
        """
        return BAR_AREAS.get(diameter, 50.3)  # Default φ8

    @staticmethod
    def calculate_min_spacing(
        thickness: float,
        n_meshes: int,
        bar_area: float,
        rho_min: float = 0.0025
    ) -> int:
        """
        Calcula el espaciamiento para armadura mínima.

        Args:
            thickness: Espesor del muro (mm)
            n_meshes: Número de mallas (1 o 2)
            bar_area: Área de la barra (mm²)
            rho_min: Cuantía mínima (default 0.25%)

        Returns:
            Espaciamiento redondeado a valor típico (mm)
        """
        As_min_per_m = rho_min * thickness * 1000
        if As_min_per_m <= 0:
            return 200

        spacing = n_meshes * bar_area * 1000 / As_min_per_m

        # Redondear a espaciamiento típico
        typical = [100, 150, 200, 250, 300]
        for s in typical:
            if s >= spacing:
                return s
        return 200

    @staticmethod
    def calculate_n_intermediate_bars(
        width: float,
        cover: float,
        spacing_v: float
    ) -> int:
        """
        Calcula el número de barras intermedias de malla (sin contar bordes).

        Args:
            width: Largo del muro (mm)
            cover: Recubrimiento (mm)
            spacing_v: Espaciamiento vertical (mm)

        Returns:
            Número de barras intermedias por cara
        """
        available_length = width - 2 * cover
        if available_length <= 0 or spacing_v <= 0:
            return 0
        return max(0, int(available_length / spacing_v))

    @staticmethod
    def calculate_from_pier(pier: 'Pier') -> ReinforcementProperties:
        """
        Calcula todas las propiedades de armadura de un Pier.

        Args:
            pier: Entidad Pier con configuración de armadura

        Returns:
            ReinforcementProperties con todos los valores calculados
        """
        # Número de barras intermedias
        n_intermediate = ReinforcementCalculator.calculate_n_intermediate_bars(
            width=pier.width,
            cover=pier.cover,
            spacing_v=pier.spacing_v
        )

        # Áreas de acero
        As_vertical = n_intermediate * pier.n_meshes * pier._bar_area_v
        As_horizontal = pier.n_meshes * (pier._bar_area_h / pier.spacing_h) * 1000
        As_vertical_per_m = pier.n_meshes * (pier._bar_area_v / pier.spacing_v) * 1000

        # Bordes
        As_edge_total = pier.n_meshes * 2 * pier._bar_area_edge
        As_edge_per_end = pier.n_meshes * pier._bar_area_edge
        n_edge_bars_per_end = pier.n_meshes

        # Totales
        As_flexure_total = As_edge_total + As_vertical
        n_total_vertical_bars = (pier.n_meshes * 2) + (n_intermediate * pier.n_meshes)

        # Cuantías
        Ag = pier.width * pier.thickness
        rho_vertical = As_flexure_total / Ag if Ag > 0 else 0
        rho_horizontal = As_horizontal / (pier.thickness * 1000) if pier.thickness > 0 else 0

        return ReinforcementProperties(
            n_intermediate_bars=n_intermediate,
            As_vertical=As_vertical,
            As_horizontal=As_horizontal,
            As_vertical_per_m=As_vertical_per_m,
            As_edge_total=As_edge_total,
            As_edge_per_end=As_edge_per_end,
            As_flexure_total=As_flexure_total,
            n_edge_bars_per_end=n_edge_bars_per_end,
            n_total_vertical_bars=n_total_vertical_bars,
            rho_vertical=rho_vertical,
            rho_horizontal=rho_horizontal
        )
