# app/domain/entities/protocols.py
"""
Protocolos (interfaces) para entidades estructurales.

Define interfaces comunes que permiten crear servicios genericos
que funcionan con diferentes tipos de elementos (Pier, Column, etc.).
"""
from typing import Protocol, List, Tuple, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..flexure import SteelLayer


@runtime_checkable
class FlexuralElement(Protocol):
    """
    Interfaz comun para elementos sujetos a flexocompresion.

    Implementada por: Pier, Column

    Permite que FlexocompressionService funcione con cualquier
    elemento que implemente esta interfaz.
    """

    # Identificacion
    label: str
    story: str

    # Materiales (MPa)
    fc: float
    fy: float
    cover: float

    # Geometria - debe ser atributo o property
    height: float

    @property
    def Ag(self) -> float:
        """Area bruta de la seccion (mm2)."""
        ...

    @property
    def As_flexure_total(self) -> float:
        """Area total de acero para flexion (mm2)."""
        ...

    def get_steel_layers(self, direction: str = 'primary') -> List['SteelLayer']:
        """
        Obtiene las capas de acero para el diagrama de interaccion.

        Args:
            direction: 'primary' para eje fuerte, 'secondary' para eje debil

        Returns:
            Lista de SteelLayer con posicion y area de cada capa
        """
        ...

    def get_section_dimensions(self, direction: str = 'primary') -> Tuple[float, float]:
        """
        Obtiene las dimensiones de la seccion para la curva P-M.

        Args:
            direction: 'primary' para eje fuerte, 'secondary' para eje debil

        Returns:
            Tuple (width, thickness) en mm
            - width: dimension perpendicular al eje de flexion
            - thickness: dimension paralela al eje de flexion
        """
        ...
