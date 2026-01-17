# app/domain/calculations/reinforcement_proposer.py
"""
Servicio de propuesta automatica de armadura segun geometria.

Reglas (practica chilena + ACI 318-25):
1. STRUT: Dimension menor < 15cm Y ratio lw/tw < 3 (estricto)
   - Cuadrado (14x14): 1x1, sin estribos
   - Rectangular (14x19, 19x14, 14x28): 1x2 o 2x1, con traba (1 rama)
2. MESH: ratio >= 3 (es muro, siempre lleva malla)
   - 14x42 (ratio=3.0) -> muro con malla
3. MESH: >=5 barras en cualquier lado (columnas muy grandes)
4. COLUMNA: Ambos >= 15cm -> grilla 2x2+ con estribos (2 ramas)

Espaciamiento maximo entre barras: 20cm
"""
from dataclasses import dataclass
from enum import Enum
import math

from ..constants.reinforcement import (
    STRUT_MAX_DIM_MM,
    STRUT_MAX_RATIO,
    MAX_BAR_SPACING_MM,
    MIN_BARS_FOR_MESH,
    STRUT_DEFAULTS,
    COLUMN_DEFAULTS,
    MESH_DEFAULTS,
    STIRRUP_DEFAULTS,
)


class ProposedLayout(Enum):
    """Tipo de layout propuesto."""
    STRUT = "strut"           # 1x1, sin estribos
    STIRRUPS = "stirrups"     # Grilla con estribos/trabas
    MESH = "mesh"             # Malla distribuida


@dataclass
class ReinforcementProposal:
    """Propuesta de armadura calculada segun geometria."""
    layout: ProposedLayout
    n_bars_length: int
    n_bars_thickness: int
    diameter: int
    stirrup_diameter: int
    stirrup_spacing: int
    n_shear_legs: int              # Ramas en direccion length
    n_shear_legs_secondary: int    # Ramas en direccion thickness
    has_crossties: bool            # True si usa trabas en vez de estribos completos


class ReinforcementProposer:
    """
    Calcula propuesta de armadura segun geometria de la seccion.

    Implementa las reglas de practica chilena para propuesta inicial,
    que el usuario puede modificar posteriormente.
    """

    @classmethod
    def propose(cls, length_mm: float, thickness_mm: float) -> ReinforcementProposal:
        """
        Propone armadura segun dimensiones de la seccion.

        Args:
            length_mm: Dimension mayor (lw para muros, depth para columnas)
            thickness_mm: Dimension menor (tw para muros, width para columnas)

        Returns:
            ReinforcementProposal con la configuracion sugerida
        """
        # Caso 1: STRUT (dimension menor < 15cm Y ratio < 3, no es muro)
        min_dim = min(length_mm, thickness_mm)
        max_dim = max(length_mm, thickness_mm)
        ratio = max_dim / min_dim if min_dim > 0 else 999.0

        if min_dim < STRUT_MAX_DIM_MM and ratio < STRUT_MAX_RATIO:
            return cls._propose_strut(length_mm, thickness_mm)

        # Calcular barras necesarias para cumplir espaciamiento maximo
        n_length = cls._calc_bars_for_dimension(length_mm)
        n_thickness = cls._calc_bars_for_dimension(thickness_mm)

        # Caso 2: MESH si ratio >= 3 (es muro, no columna)
        # Muros siempre llevan malla, independiente del numero de barras
        if ratio >= STRUT_MAX_RATIO:
            return cls._propose_mesh(n_length, n_thickness)

        # Caso 3: MESH (>=5 barras en algun lado)
        if n_length >= MIN_BARS_FOR_MESH or n_thickness >= MIN_BARS_FOR_MESH:
            return cls._propose_mesh(n_length, n_thickness)

        # Caso 4: STIRRUPS con grilla calculada (columnas)
        return cls._propose_stirrups(
            length_mm, thickness_mm, n_length, n_thickness
        )

    @classmethod
    def _calc_bars_for_dimension(cls, dim_mm: float) -> int:
        """
        Calcula barras necesarias para cumplir espaciamiento maximo.

        Formula: n = ceil(dim / max_spacing) + 1, minimo 2
        Esto garantiza que las barras esten separadas <= MAX_BAR_SPACING_MM.
        """
        if dim_mm < STRUT_MAX_DIM_MM:
            return 1
        # Para dim=150, n=ceil(150/200)+1=1+1=2
        # Para dim=200, n=ceil(200/200)+1=1+1=2
        # Para dim=400, n=ceil(400/200)+1=2+1=3
        return max(2, math.ceil(dim_mm / MAX_BAR_SPACING_MM) + 1)

    @classmethod
    def _propose_strut(
        cls, length_mm: float, thickness_mm: float
    ) -> ReinforcementProposal:
        """
        Propuesta para strut.

        - Cuadrado pequeno (14x14): 1x1, sin estribos
        - Rectangular (14x19, 19x14): 1x2 o 2x1, con traba (1 rama)
        """
        # Calcular barras en cada direccion
        n_length = cls._calc_bars_for_dimension(length_mm)
        n_thickness = cls._calc_bars_for_dimension(thickness_mm)

        # Strut cuadrado pequeno: 1x1 sin estribos
        if n_length == 1 and n_thickness == 1:
            return ReinforcementProposal(
                layout=ProposedLayout.STRUT,
                n_bars_length=1,
                n_bars_thickness=1,
                diameter=STRUT_DEFAULTS['diameter'],
                stirrup_diameter=0,
                stirrup_spacing=0,
                n_shear_legs=0,
                n_shear_legs_secondary=0,
                has_crossties=False,
            )

        # Strut rectangular: 1x2 o 2x1 con traba (1 rama)
        return ReinforcementProposal(
            layout=ProposedLayout.STRUT,
            n_bars_length=n_length,
            n_bars_thickness=n_thickness,
            diameter=STRUT_DEFAULTS['diameter'],
            stirrup_diameter=COLUMN_DEFAULTS['stirrup_diameter'],
            stirrup_spacing=COLUMN_DEFAULTS['stirrup_spacing'],
            n_shear_legs=1 if n_length == 1 else 2,
            n_shear_legs_secondary=1 if n_thickness == 1 else 2,
            has_crossties=True,
        )

    @classmethod
    def _propose_stirrups(
        cls,
        length_mm: float,
        thickness_mm: float,
        n_length: int,
        n_thickness: int
    ) -> ReinforcementProposal:
        """
        Propuesta para columna con estribos o trabas.

        - Grilla 1xN o Nx1: usa trabas (1 rama en direccion del lado con 1 barra)
        - Grilla NxM (ambos >= 2): usa estribos (2 ramas en cada direccion)
        """
        # Determinar si necesita trabas (grilla asimetrica 1xN)
        has_crossties = (n_length == 1 or n_thickness == 1)

        # Ramas de corte
        if has_crossties:
            # Traba: 1 rama en la direccion del lado con 1 barra
            n_shear_legs = 1 if n_length == 1 else 2
            n_shear_legs_secondary = 1 if n_thickness == 1 else 2
        else:
            # Estribos normales: 2 ramas en cada direccion
            n_shear_legs = 2
            n_shear_legs_secondary = 2

        return ReinforcementProposal(
            layout=ProposedLayout.STIRRUPS,
            n_bars_length=n_length,
            n_bars_thickness=n_thickness,
            diameter=COLUMN_DEFAULTS['diameter'],
            stirrup_diameter=COLUMN_DEFAULTS['stirrup_diameter'],
            stirrup_spacing=COLUMN_DEFAULTS['stirrup_spacing'],
            n_shear_legs=n_shear_legs,
            n_shear_legs_secondary=n_shear_legs_secondary,
            has_crossties=has_crossties,
        )

    @classmethod
    def _propose_mesh(cls, n_length: int, n_thickness: int) -> ReinforcementProposal:
        """
        Propuesta para muro con malla.

        Cuando hay >= 5 barras en algun lado, se usa layout MESH
        con fierros de borde + mallas distribuidas.
        """
        return ReinforcementProposal(
            layout=ProposedLayout.MESH,
            n_bars_length=n_length,
            n_bars_thickness=n_thickness,
            diameter=MESH_DEFAULTS['diameter_v'],
            stirrup_diameter=STIRRUP_DEFAULTS['stirrup_diameter'],
            stirrup_spacing=STIRRUP_DEFAULTS['stirrup_spacing'],
            n_shear_legs=2,
            n_shear_legs_secondary=2,
            has_crossties=False,
        )
