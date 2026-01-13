# app/domain/entities/section_cut.py
"""
Entidad SectionCutInfo para datos de Section Cut Forces de ETABS.

Esta clase representa la información geométrica de un corte de sección,
utilizada por vigas capitel (drop beams) y otros elementos derivados
de Section Cut Forces - Analysis.
"""
from dataclasses import dataclass


@dataclass
class SectionCutInfo:
    """
    Representa un corte de sección desde ETABS.

    Formato del nombre en ETABS:
    "Scut Losa S02-29x150 eje CL - Eje C3"
           |    |   |       |       |
           |    |   |       |       +-- Ubicación del corte
           |    |   |       +-- Eje del elemento
           |    |   +-- Ancho del corte (cm)
           |    +-- Espesor (cm)
           +-- Story/Piso
    """
    name: str                   # Nombre completo del corte
    story: str                  # Piso extraído del nombre (ej: "S02")
    thickness_mm: float         # Espesor extraído del nombre (mm)
    width_mm: float             # Ancho del corte extraído del nombre (mm)
    axis_slab: str              # Eje del elemento (ej: "CL")
    location: str               # Ubicación del corte (ej: "Eje C3", "C3")

    @property
    def element_key(self) -> str:
        """Clave única para identificar el elemento."""
        return f"{self.story}_{self.axis_slab}_{self.location}"

    @property
    def display_name(self) -> str:
        """Nombre legible para mostrar en UI."""
        return f"{self.axis_slab} @ {self.location}"


# Alias para compatibilidad (vigas capitel usan este nombre)
SlabSectionCut = SectionCutInfo
