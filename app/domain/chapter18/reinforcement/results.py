# app/domain/chapter18/reinforcement/results.py
"""
Dataclasses para resultados de verificación de refuerzo sísmico.

Según ACI 318-25:
- §18.10.2.1: Refuerzo distribuido mínimo
- §18.10.4.3: ρv >= ρh para muros bajos (hw/lw <= 2.0)
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class SeismicReinforcementResult:
    """
    Resultado de verificación de refuerzo mínimo para muros especiales.

    Según ACI 318-25 §18.10.2.1:
    - ρℓ (longitudinal/vertical) >= 0.0025
    - ρt (transversal/horizontal) >= 0.0025
    - Espaciamiento <= 18" (457mm)
    """
    # =========================================================================
    # Cuantía distribuida (malla solamente, sin barras de borde)
    # §18.10.2.1 requiere refuerzo DISTRIBUIDO mínimo
    # =========================================================================
    rho_mesh_v_min: float           # 0.0025
    rho_mesh_v_actual: float
    rho_mesh_v_ok: bool

    # =========================================================================
    # Cuantía total vertical (malla + borde)
    # §11.6.2 para verificación general
    # =========================================================================
    rho_v_min: float
    rho_v_actual: float
    rho_v_ok: bool

    # =========================================================================
    # Cuantía horizontal
    # =========================================================================
    rho_h_min: float
    rho_h_actual: float
    rho_h_ok: bool

    # =========================================================================
    # Espaciamiento máximo §18.10.2.1
    # =========================================================================
    max_spacing: float              # 457mm (18")
    spacing_v: float
    spacing_h: float
    spacing_v_ok: bool
    spacing_h_ok: bool

    # =========================================================================
    # Requisito §18.10.4.3: Para hw/lw <= 2.0, ρv >= ρh
    # =========================================================================
    hw_lw: float
    rho_v_ge_rho_h_required: bool
    rho_v_ge_rho_h_ok: bool

    # =========================================================================
    # Resultado global
    # =========================================================================
    is_ok: bool
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 §18.10.2.1"

    def to_dict(self) -> dict:
        """Convierte a diccionario para API."""
        return {
            'rho_mesh_v_min': self.rho_mesh_v_min,
            'rho_mesh_v_actual': round(self.rho_mesh_v_actual, 5),
            'rho_mesh_v_ok': self.rho_mesh_v_ok,
            'rho_v_min': self.rho_v_min,
            'rho_v_actual': round(self.rho_v_actual, 5),
            'rho_v_ok': self.rho_v_ok,
            'rho_h_min': self.rho_h_min,
            'rho_h_actual': round(self.rho_h_actual, 5),
            'rho_h_ok': self.rho_h_ok,
            'max_spacing': self.max_spacing,
            'spacing_v': self.spacing_v,
            'spacing_h': self.spacing_h,
            'spacing_v_ok': self.spacing_v_ok,
            'spacing_h_ok': self.spacing_h_ok,
            'hw_lw': round(self.hw_lw, 2),
            'rho_v_ge_rho_h_required': self.rho_v_ge_rho_h_required,
            'rho_v_ge_rho_h_ok': self.rho_v_ge_rho_h_ok,
            'is_ok': self.is_ok,
            'warnings': self.warnings,
            'aci_reference': self.aci_reference
        }
