# app/domain/entities/coupling_beam.py
"""
Configuracion de viga de acople generica para prediseno.

Permite definir una viga estandar que se aplica a todos los piers,
con posibilidad de sobre-escribir valores individuales.
"""
from dataclasses import dataclass, field
from typing import Optional
import math

from ..constants.materials import BAR_AREAS, get_bar_area


@dataclass
class CouplingBeamConfig:
    """
    Configuracion de una viga de acople.

    Atributos geometricos:
        width: Ancho de la viga (mm)
        height: Altura de la viga (mm)

    Armadura longitudinal:
        n_bars_top: Numero de barras superiores
        diameter_top: Diametro de barras superiores (mm)
        n_bars_bottom: Numero de barras inferiores
        diameter_bottom: Diametro de barras inferiores (mm)

    Estribos:
        stirrup_diameter: Diametro de estribos (mm)
        stirrup_spacing: Espaciamiento de estribos (mm)
        n_legs: Numero de ramas del estribo (default 2)

    Materiales:
        fy: Fluencia del acero (MPa), default 420
        fc: Resistencia del concreto (MPa), default 25
        cover: Recubrimiento (mm), default 40
    """
    # Geometria
    width: float = 200.0      # mm
    height: float = 500.0     # mm

    # Armadura superior
    n_bars_top: int = 3
    diameter_top: int = 16    # mm

    # Armadura inferior
    n_bars_bottom: int = 3
    diameter_bottom: int = 16  # mm

    # Estribos
    stirrup_diameter: int = 10  # mm
    stirrup_spacing: float = 150.0  # mm
    n_legs: int = 2

    # Materiales
    fy: float = 420.0   # MPa
    fc: float = 25.0    # MPa
    cover: float = 40.0  # mm

    @property
    def As_top(self) -> float:
        """Area de acero superior (mm²)."""
        return self.n_bars_top * get_bar_area(self.diameter_top)

    @property
    def As_bottom(self) -> float:
        """Area de acero inferior (mm²)."""
        return self.n_bars_bottom * get_bar_area(self.diameter_bottom)

    @property
    def d_top(self) -> float:
        """Profundidad efectiva para momento negativo (mm)."""
        return self.height - self.cover - self.stirrup_diameter - self.diameter_top / 2

    @property
    def d_bottom(self) -> float:
        """Profundidad efectiva para momento positivo (mm)."""
        return self.height - self.cover - self.stirrup_diameter - self.diameter_bottom / 2

    def calculate_Mn(self, As: float, d: float) -> float:
        """
        Calcula momento nominal para una capa de acero.

        Usando bloque rectangular de Whitney:
        a = As * fy / (0.85 * fc * b)
        Mn = As * fy * (d - a/2)

        Args:
            As: Area de acero (mm²)
            d: Profundidad efectiva (mm)

        Returns:
            Mn en kN-m
        """
        # Profundidad del bloque de compresion
        a = As * self.fy / (0.85 * self.fc * self.width)

        # Verificar que a < d (armadura en tension)
        if a >= d:
            return 0.0

        # Momento nominal (N-mm -> kN-m)
        Mn_Nmm = As * self.fy * (d - a / 2)
        return Mn_Nmm / 1e6  # kN-m

    @property
    def Mn_positive(self) -> float:
        """Momento nominal positivo (armadura inferior en tension) en kN-m."""
        return self.calculate_Mn(self.As_bottom, self.d_bottom)

    @property
    def Mn_negative(self) -> float:
        """Momento nominal negativo (armadura superior en tension) en kN-m."""
        return self.calculate_Mn(self.As_top, self.d_top)

    def calculate_Mpr(self, Mn: float, alpha: float = 1.25) -> float:
        """
        Calcula momento probable.

        Mpr = alpha * Mn, donde alpha = 1.25 segun ACI 318-25.

        Args:
            Mn: Momento nominal (kN-m)
            alpha: Factor de sobrerresistencia (default 1.25)

        Returns:
            Mpr en kN-m
        """
        return alpha * Mn

    @property
    def Mpr_positive(self) -> float:
        """Momento probable positivo en kN-m."""
        return self.calculate_Mpr(self.Mn_positive)

    @property
    def Mpr_negative(self) -> float:
        """Momento probable negativo en kN-m."""
        return self.calculate_Mpr(self.Mn_negative)

    @property
    def Mpr_max(self) -> float:
        """Momento probable maximo (el mayor de positivo y negativo) en kN-m."""
        return max(self.Mpr_positive, self.Mpr_negative)

    def get_summary(self) -> dict:
        """Retorna resumen de la configuracion."""
        return {
            'geometry': f'{self.width:.0f}x{self.height:.0f} mm',
            'top': f'{self.n_bars_top}φ{self.diameter_top}',
            'bottom': f'{self.n_bars_bottom}φ{self.diameter_bottom}',
            'stirrups': f'φ{self.stirrup_diameter}@{self.stirrup_spacing:.0f} ({self.n_legs}R)',
            'As_top_mm2': round(self.As_top, 1),
            'As_bottom_mm2': round(self.As_bottom, 1),
            'Mn_pos_kNm': round(self.Mn_positive, 1),
            'Mn_neg_kNm': round(self.Mn_negative, 1),
            'Mpr_pos_kNm': round(self.Mpr_positive, 1),
            'Mpr_neg_kNm': round(self.Mpr_negative, 1),
        }


@dataclass
class PierCouplingConfig:
    """
    Configuracion de vigas de acople para un pier especifico.

    Permite sobre-escribir la viga generica para un pier particular.
    """
    pier_key: str                              # Clave del pier (Story_Label)
    beam_left: Optional[CouplingBeamConfig] = None   # Viga izquierda (None = usar generica)
    beam_right: Optional[CouplingBeamConfig] = None  # Viga derecha (None = usar generica)
    has_beam_left: bool = True                 # Si tiene viga a la izquierda
    has_beam_right: bool = True                # Si tiene viga a la derecha

    def get_Mpr_total(self, default_beam: CouplingBeamConfig) -> float:
        """
        Calcula Mpr total de las vigas conectadas al pier.

        Args:
            default_beam: Viga generica por defecto

        Returns:
            Suma de Mpr_max de vigas izquierda y derecha (kN-m)
        """
        total = 0.0

        if self.has_beam_left:
            beam = self.beam_left or default_beam
            total += beam.Mpr_max

        if self.has_beam_right:
            beam = self.beam_right or default_beam
            total += beam.Mpr_max

        return total
