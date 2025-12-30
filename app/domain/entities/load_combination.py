# app/structural/domain/entities/load_combination.py
"""
Entidad LoadCombination: representa una combinación de carga para un pier.
"""
import math
from dataclasses import dataclass


@dataclass
class LoadCombination:
    """
    Combinación de carga para un pier.

    Unidades (compatibles con ETABS):
    - Fuerzas: tonf
    - Momentos: tonf-m

    Convención de signos (ETABS):
    - P positivo = tracción
    - P negativo = compresión
    """
    name: str           # Nombre de la combinación (ej: "1.2D+1.6L")
    location: str       # "Top" o "Bottom"
    step_type: str      # "" o "Max" o "Min" (para envolventes)

    P: float            # Carga axial (tonf)
    V2: float           # Corte en dirección 2 (tonf)
    V3: float           # Corte en dirección 3 (tonf)
    T: float            # Torsión (tonf-m)
    M2: float           # Momento en dirección 2 (tonf-m)
    M3: float           # Momento en dirección 3 (tonf-m)

    @property
    def P_compression(self) -> float:
        """P en convención positivo = compresión (para cálculos)."""
        return -self.P  # Invertir signo de ETABS

    @property
    def moment_angle_deg(self) -> float:
        """Ángulo del plano de momento en grados (0°=M3 puro, 90°=M2 puro)."""
        M2_abs = abs(self.M2)
        M3_abs = abs(self.M3)
        if M2_abs < 1e-10 and M3_abs < 1e-10:
            return 0.0
        return math.degrees(math.atan2(M2_abs, M3_abs))

    @property
    def moment_resultant(self) -> float:
        """Momento resultante SRSS (tonf-m)."""
        return math.sqrt(self.M2**2 + self.M3**2)
