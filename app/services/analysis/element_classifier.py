# app/services/analysis/element_classifier.py
"""
Clasificador automatico de elementos estructurales segun ACI 318-25.

Clasifica Beam, Column y Pier en tipos especificos para aplicar
las verificaciones correspondientes.

Usa WallClassificationService del dominio para clasificacion de piers,
evitando duplicacion de logica.
"""
from enum import Enum
from typing import Union, TYPE_CHECKING

from ...domain.shear import WallClassificationService
from ...domain.shear.classification import ElementType as DomainElementType

if TYPE_CHECKING:
    from ...domain.entities import VerticalElement, HorizontalElement


class ElementType(Enum):
    """
    Tipos de elementos estructurales segun ACI 318-25.

    Cada tipo determina que verificaciones aplicar y con que parametros.

    Nota: Para piers/muros, los valores coinciden con domain.shear.ElementType
    para facilitar la conversion.
    """
    # Vigas - §18.6
    BEAM = "beam"

    # Columnas - §18.7 o §22
    COLUMN_NONSEISMIC = "column_nonseismic"
    COLUMN_SEISMIC = "column_seismic"

    # Muros y pilares de muro - §18.10 (valores coinciden con domain.shear.ElementType)
    WALL_PIER_COLUMN = "wall_pier_column"      # lw/tw <= 2.5, requisitos columna
    WALL_PIER_ALTERNATE = "wall_pier_alt"      # 2.5 < lw/tw <= 6.0, §18.10.8.1
    WALL_SQUAT = "wall_squat"                  # lw/tw > 6.0, hw/lw < 2.0
    WALL = "wall"                              # lw/tw > 6.0, hw/lw >= 2.0

    # Vigas capitel - diseño flexocompresión tipo muro
    DROP_BEAM = "drop_beam"

    @property
    def is_beam(self) -> bool:
        """True si es una viga."""
        return self == ElementType.BEAM

    @property
    def is_column(self) -> bool:
        """True si es una columna (sismica o no sismica)."""
        return self in (ElementType.COLUMN_SEISMIC, ElementType.COLUMN_NONSEISMIC)

    @property
    def is_drop_beam(self) -> bool:
        """True si es una viga capitel."""
        return self == ElementType.DROP_BEAM

    @property
    def is_wall(self) -> bool:
        """True si es un muro o pilar de muro."""
        return self in (
            ElementType.WALL,
            ElementType.WALL_SQUAT,
            ElementType.WALL_PIER_COLUMN,
            ElementType.WALL_PIER_ALTERNATE,
            ElementType.DROP_BEAM,  # Vigas capitel se diseñan como muros
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
            ElementType.DROP_BEAM: "§18.10",  # Vigas capitel como muros
        }
        return sections.get(self, "")


# Mapeo de ElementType del dominio a ElementType de services
_DOMAIN_TO_SERVICE_TYPE = {
    DomainElementType.COLUMN: ElementType.COLUMN_SEISMIC,  # Default sismico
    DomainElementType.WALL: ElementType.WALL,
    DomainElementType.WALL_PIER_COLUMN: ElementType.WALL_PIER_COLUMN,
    DomainElementType.WALL_PIER_ALTERNATE: ElementType.WALL_PIER_ALTERNATE,
    DomainElementType.WALL_SQUAT: ElementType.WALL_SQUAT,
}


class ElementClassifier:
    """
    Clasificador automatico de elementos estructurales.

    Determina el tipo de elemento basandose en:
    - Tipo de entidad (Beam, Column, Pier)
    - Propiedades geometricas (lw/tw, hw/lw)
    - Flag sismico (is_seismic)

    Para Piers, delega a WallClassificationService del dominio
    para evitar duplicacion de la logica de clasificacion.
    """

    def __init__(self):
        """Inicializa el clasificador con el servicio de clasificacion del dominio."""
        self._wall_classification = WallClassificationService()

    def classify(
        self,
        element: Union['Beam', 'Column', 'Pier', 'DropBeam']
    ) -> ElementType:
        """
        Clasifica un elemento estructural.

        Args:
            element: Beam, Column, Pier o DropBeam a clasificar

        Returns:
            ElementType correspondiente
        """
        from ...domain.entities import VerticalElement, HorizontalElement

        # HorizontalElement: Vigas y vigas capitel
        if isinstance(element, HorizontalElement):
            if element.is_drop_beam:
                return ElementType.DROP_BEAM
            return ElementType.BEAM

        # VerticalElement: Columnas y piers
        if isinstance(element, VerticalElement):
            if element.is_frame_source:
                return self._classify_column(element)
            else:  # PIER source
                return self._classify_pier(element)

        raise ValueError(f"Tipo de elemento no soportado: {type(element)}")

    def _classify_column(self, column: 'VerticalElement') -> ElementType:
        """Clasifica una columna segun su flag sismico."""
        if hasattr(column, 'is_seismic') and column.is_seismic:
            return ElementType.COLUMN_SEISMIC
        return ElementType.COLUMN_NONSEISMIC

    def _classify_pier(self, pier: 'VerticalElement') -> ElementType:
        """
        Clasifica un pier usando WallClassificationService del dominio.

        Delega la logica de clasificacion al dominio y mapea
        el resultado al ElementType de services.
        """
        # Usar el servicio del dominio para clasificar
        # length=lw, thickness=tw para pier
        classification = self._wall_classification.classify(
            lw=pier.length,
            tw=pier.thickness,
            hw=pier.height
        )

        # Mapear el tipo del dominio al tipo de services
        domain_type = classification.element_type
        return _DOMAIN_TO_SERVICE_TYPE.get(domain_type, ElementType.WALL)

    def get_classification_info(
        self,
        element: Union['VerticalElement', 'HorizontalElement']
    ) -> dict:
        """
        Obtiene informacion detallada de la clasificacion.

        Args:
            element: Elemento a clasificar

        Returns:
            Dict con tipo, ratios geometricos y seccion ACI
        """
        from ...domain.entities import VerticalElement, HorizontalElement

        element_type = self.classify(element)

        info = {
            'type': element_type.value,
            'aci_section': element_type.aci_section,
            'is_seismic': element_type.is_seismic,
        }

        if isinstance(element, VerticalElement) and element.is_pier_source:
            # Usar WallClassificationService para obtener ratios ya calculados
            classification = self._wall_classification.classify(
                lw=element.length,
                tw=element.thickness,
                hw=element.height
            )
            info['lw_tw'] = round(classification.lw_tw, 2)
            info['hw_lw'] = round(classification.hw_lw, 2)
            info['is_wall_pier'] = element_type.is_wall_pier

        if isinstance(element, HorizontalElement) and element.is_drop_beam:
            # Para vigas capitel, agregar info similar a pier
            lw_tw = element.depth / element.width if element.width > 0 else 0
            hw_lw = element.length / element.depth if element.depth > 0 else 0
            info['lw_tw'] = round(lw_tw, 2)
            info['hw_lw'] = round(hw_lw, 2)
            info['is_wall_pier'] = False

        return info
