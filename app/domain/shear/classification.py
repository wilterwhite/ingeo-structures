# app/structural/domain/shear/classification.py
"""
Clasificacion de muros y pilares de muro segun ACI 318-25.

Referencias:
- Seccion 18.10.8: Pilares de muro (Wall Piers)
- Tabla R18.10.1: Clasificacion segun hw/lw y lw/bw
- Seccion 11.5: Muros ordinarios
- Seccion 22.5: Columnas y vigas
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ..constants.shear import (
    ASPECT_RATIO_WALL_LIMIT,
    WALL_PIER_HW_LW_LIMIT,
    WALL_PIER_COLUMN_LIMIT,
    WALL_PIER_ALTERNATE_LIMIT,
)


class WallType(Enum):
    """Tipos de elementos segun ACI 318-25."""
    COLUMN = "column"           # lw/tw < 4, usa S22.5
    WALL = "wall"               # lw/tw >= 4, hw/lw >= 2.0, usa S18.10.4
    WALL_PIER_COLUMN = "wall_pier_column"  # hw/lw < 2.0, lw/bw <= 2.5, usa S18.7
    WALL_PIER_ALTERNATE = "wall_pier_alt"  # hw/lw < 2.0, 2.5 < lw/bw <= 6.0
    WALL_SQUAT = "wall_squat"   # hw/lw < 2.0, lw/bw > 6.0 (muro rechoncho)


@dataclass
class WallClassification:
    """Resultado de la clasificacion de un muro."""
    wall_type: WallType
    lw: float               # Largo del muro (mm)
    tw: float               # Espesor del muro (mm)
    hw: float               # Altura del muro (mm)
    lw_tw: float            # Relacion lw/tw
    hw_lw: float            # Relacion hw/lw
    aci_section: str        # Seccion ACI aplicable
    design_method: str      # Metodo de diseno recomendado
    special_requirements: str  # Requisitos especiales


class WallClassificationService:
    """
    Servicio para clasificar muros segun ACI 318-25.

    Implementa la clasificacion de Tabla R18.10.1:

    | hw/lw   | lw/bw      | Clasificacion                    |
    |---------|------------|----------------------------------|
    | >= 2.0  | cualquiera | Muro (S18.10.4)                 |
    | < 2.0   | <= 2.5     | Pilar - requisitos columna S18.7|
    | < 2.0   | 2.5-6.0    | Pilar - metodo alternativo      |
    | < 2.0   | > 6.0      | Muro rechoncho                  |
    | N/A     | < 4        | Columna (S22.5)                 |
    """

    def classify(
        self,
        lw: float,
        tw: float,
        hw: float
    ) -> WallClassification:
        """
        Clasifica un elemento segun sus dimensiones.

        Args:
            lw: Largo del muro (mm)
            tw: Espesor del muro (mm)
            hw: Altura del muro (mm)

        Returns:
            WallClassification con el tipo y requisitos aplicables
        """
        lw_tw = lw / tw if tw > 0 else 0
        hw_lw = hw / lw if lw > 0 else 0

        # Primero verificar si es columna (lw/tw < 4)
        if lw_tw < ASPECT_RATIO_WALL_LIMIT:
            return WallClassification(
                wall_type=WallType.COLUMN,
                lw=lw, tw=tw, hw=hw,
                lw_tw=lw_tw, hw_lw=hw_lw,
                aci_section="22.5",
                design_method="column",
                special_requirements="Disenar como columna segun Capitulo 22"
            )

        # Es muro (lw/tw >= 4), verificar si es wall pier (hw/lw < 2.0)
        if hw_lw >= WALL_PIER_HW_LW_LIMIT:
            # Muro esbelto (comportamiento controlado por flexion)
            return WallClassification(
                wall_type=WallType.WALL,
                lw=lw, tw=tw, hw=hw,
                lw_tw=lw_tw, hw_lw=hw_lw,
                aci_section="18.10.4",
                design_method="wall",
                special_requirements="Muro estructural especial"
            )

        # Wall pier (hw/lw < 2.0)
        if lw_tw <= WALL_PIER_COLUMN_LIMIT:
            # Pilar con requisitos de columna
            return WallClassification(
                wall_type=WallType.WALL_PIER_COLUMN,
                lw=lw, tw=tw, hw=hw,
                lw_tw=lw_tw, hw_lw=hw_lw,
                aci_section="18.10.8.1 -> 18.7",
                design_method="column_special",
                special_requirements=(
                    "Satisfacer requisitos de columnas de porticos especiales (S18.7.4, 18.7.5, 18.7.6). "
                    "Caras de nudo en parte superior e inferior."
                )
            )
        elif lw_tw <= WALL_PIER_ALTERNATE_LIMIT:
            # Pilar con metodo alternativo
            return WallClassification(
                wall_type=WallType.WALL_PIER_ALTERNATE,
                lw=lw, tw=tw, hw=hw,
                lw_tw=lw_tw, hw_lw=hw_lw,
                aci_section="18.10.8.1(a)-(f)",
                design_method="wall_pier_alternate",
                special_requirements=(
                    "Metodo alternativo: (a) Ve segun S18.7.6.1 o <= Omega_o*Vu, "
                    "(b) Vn segun S18.10.4, (c) estribos cerrados con ganchos 180, "
                    "(d) espaciamiento <= 6in, (e) extension >= 12in, "
                    "(f) elementos de borde si requerido por S18.10.6.3"
                )
            )
        else:
            # lw/bw > 6.0: Muro rechoncho
            return WallClassification(
                wall_type=WallType.WALL_SQUAT,
                lw=lw, tw=tw, hw=hw,
                lw_tw=lw_tw, hw_lw=hw_lw,
                aci_section="18.10.4",
                design_method="wall",
                special_requirements=(
                    "Muro rechoncho (hw/lw < 2.0). "
                    "Requiere rho_v >= rho_h segun S18.10.4.3. "
                    "Considerar amplificacion de cortante S18.10.3.3"
                )
            )

    def is_wall_pier(self, classification: WallClassification) -> bool:
        """Verifica si la clasificacion corresponde a un wall pier."""
        return classification.wall_type in (
            WallType.WALL_PIER_COLUMN,
            WallType.WALL_PIER_ALTERNATE
        )

    def requires_column_detailing(self, classification: WallClassification) -> bool:
        """Verifica si requiere detallado de columna."""
        return classification.wall_type in (
            WallType.COLUMN,
            WallType.WALL_PIER_COLUMN
        )

    def is_squat_wall(self, classification: WallClassification) -> bool:
        """Verifica si es un muro rechoncho (hw/lw < 2.0)."""
        return classification.hw_lw < WALL_PIER_HW_LW_LIMIT
