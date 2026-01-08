# app/domain/chapter18/common/categories.py
"""
Categorías sísmicas para elementos estructurales según ACI 318-25.

Define la clasificación sísmica que determina los requisitos aplicables
a vigas, columnas y nudos de pórticos.

Referencias:
- §18.3: Pórticos de momento ordinarios
- §18.4: Pórticos de momento intermedios
- §18.6-18.8: Pórticos de momento especiales
- §18.14: Miembros no parte del sistema resistente a fuerzas sísmicas
"""
from enum import Enum


class SeismicCategory(Enum):
    """
    Categoría sísmica de un elemento según ACI 318-25 Capítulo 18.

    Determina qué sección del código aplica para el diseño:
    - ORDINARY: §18.3 - Requisitos mínimos para pórticos ordinarios
    - INTERMEDIATE: §18.4 - Requisitos intermedios
    - SPECIAL: §18.6-18.8 - Requisitos más estrictos para zonas de alta sismicidad
    - NON_SFRS: §18.14 - Miembros que no forman parte del SFRS

    El valor por defecto debe ser SPECIAL (el más restrictivo).

    Attributes:
        value: Identificador de la categoría
        aci_sections: Secciones ACI aplicables por tipo de elemento
    """
    ORDINARY = "ordinary"
    INTERMEDIATE = "intermediate"
    SPECIAL = "special"
    NON_SFRS = "non_sfrs"

    @property
    def beam_section(self) -> str:
        """Sección ACI aplicable para vigas."""
        sections = {
            SeismicCategory.ORDINARY: "§18.3.2",
            SeismicCategory.INTERMEDIATE: "§18.4.2",
            SeismicCategory.SPECIAL: "§18.6",
            SeismicCategory.NON_SFRS: "§18.14.3",
        }
        return sections[self]

    @property
    def column_section(self) -> str:
        """Sección ACI aplicable para columnas."""
        sections = {
            SeismicCategory.ORDINARY: "§18.3.3",
            SeismicCategory.INTERMEDIATE: "§18.4.3",
            SeismicCategory.SPECIAL: "§18.7",
            SeismicCategory.NON_SFRS: "§18.14.3",
        }
        return sections[self]

    @property
    def joint_section(self) -> str:
        """Sección ACI aplicable para nudos."""
        sections = {
            SeismicCategory.ORDINARY: "§18.3.4",
            SeismicCategory.INTERMEDIATE: "§18.4.4",
            SeismicCategory.SPECIAL: "§18.8",
            SeismicCategory.NON_SFRS: "§18.14.3",
        }
        return sections[self]

    @property
    def description(self) -> str:
        """Descripción de la categoría."""
        descriptions = {
            SeismicCategory.ORDINARY: "Pórtico de momento ordinario",
            SeismicCategory.INTERMEDIATE: "Pórtico de momento intermedio",
            SeismicCategory.SPECIAL: "Pórtico de momento especial",
            SeismicCategory.NON_SFRS: "No parte del SFRS",
        }
        return descriptions[self]

    @classmethod
    def from_sdc(cls, sdc: str, is_sfrs: bool = True) -> "SeismicCategory":
        """
        Determina la categoría mínima requerida según SDC.

        Args:
            sdc: Categoría de Diseño Sísmico (A, B, C, D, E, F)
            is_sfrs: Si el elemento es parte del sistema resistente

        Returns:
            Categoría sísmica mínima requerida

        Note:
            Según ACI 318-25 §18.2.1:
            - SDC A, B: No requiere requisitos sísmicos especiales
            - SDC C: Intermedio o especial
            - SDC D, E, F: Especial si es SFRS
        """
        if not is_sfrs:
            return cls.NON_SFRS

        sdc_upper = sdc.upper()
        if sdc_upper in ("A", "B"):
            return cls.ORDINARY
        elif sdc_upper == "C":
            return cls.INTERMEDIATE
        else:  # D, E, F
            return cls.SPECIAL
