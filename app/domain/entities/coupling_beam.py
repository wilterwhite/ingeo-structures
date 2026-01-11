# app/domain/entities/coupling_beam.py
"""
Configuracion de viga de acople generica para prediseno.

Permite definir una viga estandar que se aplica a todos los piers,
con posibilidad de sobre-escribir valores individuales.
"""
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from ..constants.reinforcement import FY_DEFAULT_MPA
from ..constants.materials import get_bar_area

if TYPE_CHECKING:
    from ..calculations.coupling_beam_capacity import CouplingBeamCapacityService


@dataclass
class CouplingBeamConfig:
    """
    Configuracion de una viga de acople.

    Atributos geometricos:
        width: Ancho de la viga (mm)
        height: Altura de la viga (mm)
        ln: Largo libre de la viga (mm) - distancia entre caras de muros

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
    ln: float = 1500.0        # mm - largo libre (claro entre muros)

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
    fy: float = FY_DEFAULT_MPA  # MPa
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

    @property
    def Mn_positive(self) -> float:
        """Momento nominal positivo (armadura inferior en tension) en kN-m."""
        from ..calculations.coupling_beam_capacity import CouplingBeamCapacityService
        return CouplingBeamCapacityService.calculate_Mn(
            As=self.As_bottom, d=self.d_bottom, b=self.width, fy=self.fy, fc=self.fc
        )

    @property
    def Mn_negative(self) -> float:
        """Momento nominal negativo (armadura superior en tension) en kN-m."""
        from ..calculations.coupling_beam_capacity import CouplingBeamCapacityService
        return CouplingBeamCapacityService.calculate_Mn(
            As=self.As_top, d=self.d_top, b=self.width, fy=self.fy, fc=self.fc
        )

    @property
    def Mpr_positive(self) -> float:
        """Momento probable positivo en kN-m."""
        from ..calculations.coupling_beam_capacity import CouplingBeamCapacityService
        return CouplingBeamCapacityService.calculate_Mpr(self.Mn_positive)

    @property
    def Mpr_negative(self) -> float:
        """Momento probable negativo en kN-m."""
        from ..calculations.coupling_beam_capacity import CouplingBeamCapacityService
        return CouplingBeamCapacityService.calculate_Mpr(self.Mn_negative)

    @property
    def Mpr_max(self) -> float:
        """Momento probable maximo (el mayor de positivo y negativo) en kN-m."""
        return max(self.Mpr_positive, self.Mpr_negative)

    @property
    def ln_h_ratio(self) -> float:
        """Relacion ln/h para clasificacion de viga."""
        return self.ln / self.height if self.height > 0 else 0

    def get_summary(self) -> dict:
        """Retorna resumen de la configuracion."""
        return {
            'geometry': f'{self.width:.0f}x{self.height:.0f} mm',
            'ln_mm': round(self.ln, 0),
            'ln_h_ratio': round(self.ln_h_ratio, 2),
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
