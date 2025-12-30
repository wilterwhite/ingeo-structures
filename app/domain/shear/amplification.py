# app/structural/domain/shear/amplification.py
"""
Amplificacion de cortante para muros estructurales especiales segun ACI 318-25.

Referencias:
- Seccion 18.10.3.3: Amplificacion de cortante
- Tabla 18.10.3.3.3: Factores Omega_v y omega_v
"""
import math
from dataclasses import dataclass
from typing import Optional

from ..constants.shear import (
    OMEGA_V_MIN,
    OMEGA_V_MAX,
    OMEGA_V_DYN_COEF,
    OMEGA_V_DYN_BASE,
    OMEGA_V_DYN_MIN,
    OMEGA_0_DEFAULT,
    WALL_PIER_HW_LW_LIMIT,
)


@dataclass
class ShearAmplificationResult:
    """Resultado de la amplificacion de cortante."""
    Vu_original: float      # Cortante original del analisis (tonf)
    Ve: float               # Cortante de diseno amplificado (tonf)
    omega_v: float          # Factor de sobrerresistencia a flexion
    omega_v_dyn: float      # Factor de amplificacion dinamica
    amplification: float    # Factor total de amplificacion
    hwcs_lw: float          # Relacion hwcs/lw
    hn_ft: Optional[float]  # Altura del edificio en pies
    applies: bool           # Si aplica la amplificacion
    aci_reference: str      # Referencia ACI


class ShearAmplificationService:
    """
    Servicio para calcular amplificacion de cortante segun ACI 318-25 S18.10.3.3.

    Para muros no cubiertos por S18.10.3.1 (segmentos horizontales) o
    S18.10.3.2 (pilares de muro), el cortante de diseno debe amplificarse:

    Ve = Omega_v x omega_v x VuEh

    Donde:
    - VuEh: Cortante debido al efecto sismico horizontal Eh
    - Omega_v: Factor de sobrerresistencia a flexion (Tabla 18.10.3.3.3)
    - omega_v: Factor de amplificacion dinamica (Tabla 18.10.3.3.3)

    Tabla 18.10.3.3.3:
    | hwcs/lw    | Omega_v           | omega_v                        |
    |------------|-------------------|--------------------------------|
    | <= 1.0     | 1.0               | 1.0                            |
    | 1.0 - 2.0  | interpolacion     | 1.0                            |
    | >= 2.0     | 1.5               | 0.8 + 0.09*hn^(1/3) >= 1.0    |

    Alternativas (S18.10.3.3.4-5):
    - Se permite usar Omega_v x omega_v = Omega_o si el codigo incluye factor
    - Si se usa Omega_o, se permite factor de redundancia = 1.0
    """

    def calculate_omega_v(self, hwcs: float, lw: float) -> float:
        """
        Calcula el factor de sobrerresistencia Omega_v segun Tabla 18.10.3.3.3.

        Args:
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)

        Returns:
            Factor Omega_v
        """
        if lw <= 0:
            return OMEGA_V_MIN

        ratio = hwcs / lw

        if ratio <= 1.0:
            return OMEGA_V_MIN
        elif ratio >= WALL_PIER_HW_LW_LIMIT:
            return OMEGA_V_MAX
        else:
            # Interpolacion lineal entre 1.0 y 2.0
            return OMEGA_V_MIN + (OMEGA_V_MAX - OMEGA_V_MIN) * (ratio - 1.0)

    def calculate_omega_v_dyn(
        self,
        hwcs: float,
        lw: float,
        hn_ft: Optional[float] = None
    ) -> float:
        """
        Calcula el factor de amplificacion dinamica omega_v segun Tabla 18.10.3.3.3.

        Args:
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)
            hn_ft: Altura total del edificio en pies (opcional)

        Returns:
            Factor omega_v
        """
        if lw <= 0:
            return OMEGA_V_DYN_MIN

        ratio = hwcs / lw

        if ratio < WALL_PIER_HW_LW_LIMIT:
            return OMEGA_V_DYN_MIN

        # Para hwcs/lw >= 2.0
        if hn_ft is None or hn_ft <= 0:
            # Si no se conoce la altura, usar valor conservador
            return OMEGA_V_DYN_MIN

        # omega_v = 0.8 + 0.09 * hn^(1/3) >= 1.0
        omega_v_dyn = OMEGA_V_DYN_BASE + OMEGA_V_DYN_COEF * (hn_ft ** (1/3))
        return max(OMEGA_V_DYN_MIN, omega_v_dyn)

    def calculate_amplified_shear(
        self,
        Vu: float,
        hwcs: float,
        lw: float,
        hn_ft: Optional[float] = None,
        use_omega_0: bool = False,
        omega_0: float = OMEGA_0_DEFAULT
    ) -> ShearAmplificationResult:
        """
        Calcula el cortante de diseno amplificado Ve.

        Args:
            Vu: Cortante del analisis debido a sismo (tonf)
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)
            hn_ft: Altura total del edificio en pies (opcional)
            use_omega_0: Si usar Omega_0 en lugar de Omega_v x omega_v
            omega_0: Factor de sobrerresistencia del sistema (default 2.5)

        Returns:
            ShearAmplificationResult con el cortante amplificado
        """
        hwcs_lw = hwcs / lw if lw > 0 else 0

        if use_omega_0:
            # Alternativa S18.10.3.3.4
            omega_v = omega_0
            omega_v_dyn = 1.0
            amplification = omega_0
            aci_reference = "ACI 318-25 S18.10.3.3.4 (Omega_0)"
        else:
            omega_v = self.calculate_omega_v(hwcs, lw)
            omega_v_dyn = self.calculate_omega_v_dyn(hwcs, lw, hn_ft)
            amplification = omega_v * omega_v_dyn
            aci_reference = "ACI 318-25 S18.10.3.3, Tabla 18.10.3.3.3"

        Ve = amplification * abs(Vu)

        # La amplificacion aplica solo a muros (no a pilares de muro S18.10.8)
        applies = True

        return ShearAmplificationResult(
            Vu_original=Vu,
            Ve=Ve,
            omega_v=omega_v,
            omega_v_dyn=omega_v_dyn,
            amplification=amplification,
            hwcs_lw=hwcs_lw,
            hn_ft=hn_ft,
            applies=applies,
            aci_reference=aci_reference
        )

    def should_amplify(
        self,
        hwcs: float,
        lw: float,
        is_wall_pier: bool = False,
        is_coupling_beam: bool = False
    ) -> bool:
        """
        Determina si se debe aplicar amplificacion de cortante.

        La amplificacion NO aplica a:
        - Segmentos horizontales (vigas de acoplamiento) -> S18.10.3.1
        - Pilares de muro (wall piers) -> S18.10.3.2

        Args:
            hwcs: Altura del muro desde seccion critica (mm)
            lw: Longitud del muro (mm)
            is_wall_pier: Si es un pilar de muro (hw/lw < 2.0)
            is_coupling_beam: Si es viga de acoplamiento

        Returns:
            True si debe amplificar el cortante
        """
        if is_coupling_beam:
            # S18.10.3.1: Segmentos horizontales usan S18.10.7
            return False

        if is_wall_pier:
            # S18.10.3.2: Pilares de muro usan S18.10.8
            return False

        return True


def convert_m_to_ft(height_m: float) -> float:
    """Convierte altura de metros a pies."""
    return height_m * 3.28084


def convert_mm_to_ft(height_mm: float) -> float:
    """Convierte altura de mm a pies."""
    return height_mm / 304.8
