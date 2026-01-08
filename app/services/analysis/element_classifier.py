# app/services/analysis/element_classifier.py
"""
Clasificador automatico de elementos estructurales segun ACI 318-25.

Clasifica Beam, Column y Pier en tipos especificos para aplicar
las verificaciones correspondientes.
"""
from enum import Enum
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities import Beam, Column, Pier


class ElementType(Enum):
    """
    Tipos de elementos estructurales segun ACI 318-25.

    Cada tipo determina que verificaciones aplicar y con que parametros.
    """
    # Vigas - §18.6
    BEAM = "beam"

    # Columnas - §18.7 o §22
    COLUMN_NONSEISMIC = "column_nonseismic"
    COLUMN_SEISMIC = "column_seismic"

    # Muros y pilares de muro - §18.10
    WALL_PIER_COLUMN = "wall_pier_column"      # lw/tw <= 2.5, requisitos columna
    WALL_PIER_ALTERNATE = "wall_pier_alt"      # 2.5 < lw/tw <= 6.0, §18.10.8.1
    WALL_SQUAT = "wall_squat"                  # lw/tw > 6.0, hw/lw < 2.0
    WALL = "wall"                              # lw/tw > 6.0, hw/lw >= 2.0

    @property
    def is_beam(self) -> bool:
        """True si es una viga."""
        return self == ElementType.BEAM

    @property
    def is_column(self) -> bool:
        """True si es una columna (sismica o no sismica)."""
        return self in (ElementType.COLUMN_SEISMIC, ElementType.COLUMN_NONSEISMIC)

    @property
    def is_wall(self) -> bool:
        """True si es un muro o pilar de muro."""
        return self in (
            ElementType.WALL,
            ElementType.WALL_SQUAT,
            ElementType.WALL_PIER_COLUMN,
            ElementType.WALL_PIER_ALTERNATE
        )

    @property
    def is_wall_pier(self) -> bool:
        """True si es un pilar de muro (lw/tw <= 6.0)."""
        return self in (ElementType.WALL_PIER_COLUMN, ElementType.WALL_PIER_ALTERNATE)

    @property
    def is_seismic(self) -> bool:
        """True si requiere verificaciones sismicas."""
        return self not in (ElementType.COLUMN_NONSEISMIC,)

    @property
    def aci_section(self) -> str:
        """Seccion ACI 318-25 aplicable."""
        sections = {
            ElementType.BEAM: "§18.6",
            ElementType.COLUMN_NONSEISMIC: "§22",
            ElementType.COLUMN_SEISMIC: "§18.7",
            ElementType.WALL_PIER_COLUMN: "§18.10.8 (column)",
            ElementType.WALL_PIER_ALTERNATE: "§18.10.8.1",
            ElementType.WALL_SQUAT: "§18.10 (squat)",
            ElementType.WALL: "§18.10",
        }
        return sections.get(self, "")


class ElementClassifier:
    """
    Clasificador automatico de elementos estructurales.

    Determina el tipo de elemento basandose en:
    - Tipo de entidad (Beam, Column, Pier)
    - Propiedades geometricas (lw/tw, hw/lw)
    - Flag sismico (is_seismic)
    """

    def classify(
        self,
        element: Union['Beam', 'Column', 'Pier']
    ) -> ElementType:
        """
        Clasifica un elemento estructural.

        Args:
            element: Beam, Column o Pier a clasificar

        Returns:
            ElementType correspondiente
        """
        from ...domain.entities import Beam, Column, Pier

        if isinstance(element, Beam):
            return ElementType.BEAM

        if isinstance(element, Column):
            return self._classify_column(element)

        if isinstance(element, Pier):
            return self._classify_pier(element)

        raise ValueError(f"Tipo de elemento no soportado: {type(element)}")

    def _classify_column(self, column: 'Column') -> ElementType:
        """Clasifica una columna segun su flag sismico."""
        if hasattr(column, 'is_seismic') and column.is_seismic:
            return ElementType.COLUMN_SEISMIC
        return ElementType.COLUMN_NONSEISMIC

    def _classify_pier(self, pier: 'Pier') -> ElementType:
        """
        Clasifica un pier segun ACI 318-25 §18.10.8.

        Criterios:
        - lw/tw <= 2.5: Wall pier tipo columna (requisitos de columna)
        - 2.5 < lw/tw <= 6.0: Wall pier metodo alternativo
        - lw/tw > 6.0 + hw/lw < 2.0: Muro rechoncho
        - lw/tw > 6.0 + hw/lw >= 2.0: Muro esbelto
        """
        # lw = ancho del muro (width)
        # tw = espesor del muro (thickness)
        # hw = altura del muro (height)
        lw = pier.width
        tw = pier.thickness
        hw = pier.height

        if tw <= 0 or lw <= 0:
            return ElementType.WALL

        lw_tw = lw / tw
        hw_lw = hw / lw if lw > 0 else 0

        if lw_tw <= 2.5:
            return ElementType.WALL_PIER_COLUMN
        elif lw_tw <= 6.0:
            return ElementType.WALL_PIER_ALTERNATE
        elif hw_lw < 2.0:
            return ElementType.WALL_SQUAT
        else:
            return ElementType.WALL

    def get_classification_info(
        self,
        element: Union['Beam', 'Column', 'Pier']
    ) -> dict:
        """
        Obtiene informacion detallada de la clasificacion.

        Args:
            element: Elemento a clasificar

        Returns:
            Dict con tipo, ratios geometricos y seccion ACI
        """
        from ...domain.entities import Beam, Column, Pier

        element_type = self.classify(element)

        info = {
            'type': element_type.value,
            'aci_section': element_type.aci_section,
            'is_seismic': element_type.is_seismic,
        }

        if isinstance(element, Pier):
            lw = element.width
            tw = element.thickness
            hw = element.height
            info['lw_tw'] = round(lw / tw, 2) if tw > 0 else 0
            info['hw_lw'] = round(hw / lw, 2) if lw > 0 else 0
            info['is_wall_pier'] = element_type.is_wall_pier

        return info
