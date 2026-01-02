# app/domain/chapter18/piers/classification.py
"""
Clasificación de pilares de muro según ACI 318-25 Tabla R18.10.1.

Usa WallClassificationService de shear/classification.py como servicio
base y mapea a tipos específicos de chapter18.

Tabla R18.10.1 - Provisiones de Diseño por Tipo de Segmento:

| hw/lw | lw/bw <= 2.5 | 2.5 < lw/bw <= 6.0 | lw/bw > 6.0 |
|-------|--------------|--------------------|-----------  |
| < 2.0 | Muro         | Muro               | Muro        |
| >= 2.0| Pilar(col)   | Pilar(col o alt)   | Muro        |
"""
from ...shear.classification import (
    WallClassificationService,
    ElementType,
    COLUMN_MIN_THICKNESS_MM,
)
from ..results import (
    WallPierCategory,
    DesignMethod,
    WallPierClassification,
)

# Mapeo de ElementType a WallPierCategory
_ELEMENT_TO_PIER_CATEGORY = {
    ElementType.COLUMN: WallPierCategory.COLUMN,
    ElementType.WALL: WallPierCategory.WALL,
    ElementType.WALL_PIER_COLUMN: WallPierCategory.COLUMN,
    ElementType.WALL_PIER_ALTERNATE: WallPierCategory.ALTERNATIVE,
    ElementType.WALL_SQUAT: WallPierCategory.WALL,
}

# Mapeo de ElementType a DesignMethod
_ELEMENT_TO_DESIGN_METHOD = {
    ElementType.COLUMN: DesignMethod.SPECIAL_COLUMN,
    ElementType.WALL: DesignMethod.WALL,
    ElementType.WALL_PIER_COLUMN: DesignMethod.SPECIAL_COLUMN,
    ElementType.WALL_PIER_ALTERNATE: DesignMethod.ALTERNATIVE,
    ElementType.WALL_SQUAT: DesignMethod.WALL,
}


def classify_wall_pier(
    hw: float,
    lw: float,
    bw: float
) -> WallPierClassification:
    """
    Clasifica el pilar de muro según Tabla R18.10.1.

    Usa WallClassificationService internamente para unificar la lógica
    de clasificación en un solo lugar.

    Args:
        hw: Altura del segmento (mm)
        lw: Longitud del segmento (mm)
        bw: Espesor del segmento (mm)

    Returns:
        WallPierClassification con categoría y método de diseño
    """
    if lw <= 0 or bw <= 0:
        return WallPierClassification(
            hw=hw, lw=lw, bw=bw,
            hw_lw=0, lw_bw=0,
            category=WallPierCategory.WALL,
            design_method=DesignMethod.WALL,
            requires_column_details=False,
            alternative_permitted=False,
            aci_reference="ACI 318-25 Tabla R18.10.1"
        )

    # Usar servicio unificado de clasificación
    wall_service = WallClassificationService()
    classification = wall_service.classify(lw=lw, tw=bw, hw=hw)

    # Mapear a tipos de chapter18
    category = _ELEMENT_TO_PIER_CATEGORY.get(
        classification.element_type, WallPierCategory.WALL
    )
    design_method = _ELEMENT_TO_DESIGN_METHOD.get(
        classification.element_type, DesignMethod.WALL
    )

    # Determinar si requiere detallado de columna
    requires_column = wall_service.requires_column_detailing(classification)

    # Determinar si permite método alternativo
    alternative_ok = classification.element_type == ElementType.WALL_PIER_ALTERNATE

    # Verificar espesor mínimo para columnas sísmicas (§18.7.2.1)
    column_min_ok = True
    column_min_required = 0.0
    if requires_column:
        column_min_ok, column_min_required = wall_service.check_column_min_thickness(bw)

    return WallPierClassification(
        hw=hw,
        lw=lw,
        bw=bw,
        hw_lw=round(classification.hw_lw, 2),
        lw_bw=round(classification.lw_tw, 2),  # lw_tw es lo mismo que lw_bw
        category=category,
        design_method=design_method,
        requires_column_details=requires_column,
        alternative_permitted=alternative_ok,
        aci_reference="ACI 318-25 Tabla R18.10.1, 18.10.8.1",
        column_min_thickness_ok=column_min_ok,
        column_min_thickness_required=column_min_required
    )
