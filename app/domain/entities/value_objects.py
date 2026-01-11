# app/domain/entities/value_objects.py
"""
Value Objects compartidos para entidades del dominio.

Los Value Objects son objetos inmutables que representan conceptos
del dominio sin identidad propia. Se comparan por valor, no por referencia.
"""
from dataclasses import dataclass

from ..constants.materials import get_bar_area


@dataclass(frozen=True)
class MeshReinforcementConfig:
    """
    Configuración de armadura de malla para muros y vigas capitel.

    Esta configuración se comparte entre Pier y DropBeam, eliminando
    la duplicación de atributos.

    Atributos:
        n_meshes: Número de mallas (1=central, 2=doble cara)
        diameter_v: Diámetro barra vertical (mm)
        spacing_v: Espaciamiento vertical (mm)
        diameter_h: Diámetro barra horizontal (mm)
        spacing_h: Espaciamiento horizontal (mm)
    """
    n_meshes: int = 2
    diameter_v: int = 12
    spacing_v: int = 200
    diameter_h: int = 10
    spacing_h: int = 200

    @property
    def bar_area_v(self) -> float:
        """Área de cada barra vertical (mm²)."""
        return get_bar_area(self.diameter_v)

    @property
    def bar_area_h(self) -> float:
        """Área de cada barra horizontal (mm²)."""
        return get_bar_area(self.diameter_h)

    @property
    def As_per_meter_v(self) -> float:
        """Área de acero vertical por metro lineal (mm²/m)."""
        return self.n_meshes * (self.bar_area_v / self.spacing_v) * 1000

    @property
    def As_per_meter_h(self) -> float:
        """Área de acero horizontal por metro lineal (mm²/m)."""
        return self.n_meshes * (self.bar_area_h / self.spacing_h) * 1000


@dataclass(frozen=True)
class EdgeBarConfig:
    """
    Configuración de barras de borde para elementos de muro.

    Usado en Pier y DropBeam para definir el refuerzo concentrado
    en los extremos del elemento.

    Atributos:
        n_bars: Número de barras por extremo
        diameter: Diámetro de barras de borde (mm)
    """
    n_bars: int = 4
    diameter: int = 16

    @property
    def bar_area(self) -> float:
        """Área de cada barra de borde (mm²)."""
        return get_bar_area(self.diameter)

    @property
    def As_per_end(self) -> float:
        """Área total de acero en un extremo (mm²)."""
        return self.n_bars * self.bar_area

    @property
    def As_total(self) -> float:
        """Área total de barras de borde (ambos extremos) (mm²)."""
        return 2 * self.As_per_end


@dataclass(frozen=True)
class StirrupConfig:
    """
    Configuración de estribos de confinamiento.

    Usado para estribos en elementos de borde de muros y columnas.

    Atributos:
        diameter: Diámetro del estribo (mm)
        spacing: Espaciamiento de estribos (mm)
        n_legs: Número de ramas
    """
    diameter: int = 10
    spacing: int = 150
    n_legs: int = 2

    @property
    def bar_area(self) -> float:
        """Área de cada rama del estribo (mm²)."""
        return get_bar_area(self.diameter)

    @property
    def As_stirrup(self) -> float:
        """Área total de acero transversal por estribo (mm²)."""
        return self.n_legs * self.bar_area


@dataclass(frozen=True)
class BoundaryZoneDefinition:
    """
    Definición de zona de borde según ACI 318-25 §18.10.2.4.

    La zona de extremo se define como un porcentaje de la longitud
    del muro (típicamente 0.15 × lw).

    Atributos:
        ratio: Ratio de la longitud del muro que define la zona (default 0.15)
        wall_length: Longitud del muro (mm)
    """
    wall_length: float
    ratio: float = 0.15

    @property
    def length(self) -> float:
        """Longitud de la zona de borde (mm)."""
        return self.ratio * self.wall_length
