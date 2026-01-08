# app/domain/chapter18/reinforcement/service.py
"""
Servicio de verificación de refuerzo mínimo para muros especiales.

Integra verificaciones de:
- §11.6.2: Cuantía mínima general (ReinforcementLimitsService de chapter11)
- §18.10.2.1: Refuerzo distribuido mínimo para muros especiales
- §18.10.4.3: ρv >= ρh para muros bajos (hw/lw <= 2.0)

Referencias ACI 318-25:
- §18.10.2.1: ρℓ >= 0.0025, ρt >= 0.0025, spacing <= 18"
- §18.10.4.3: Para hw/lw <= 2.0, ρv >= ρh
- §11.6.2: Requisitos generales de cuantía
"""
from typing import List, Optional, TYPE_CHECKING

from .results import SeismicReinforcementResult
from ...constants.reinforcement import (
    RHO_MIN,
    MAX_SPACING_SEISMIC_MM,
    check_rho_vertical_ge_horizontal,
    is_rho_v_ge_rho_h_required
)
from ...chapter11.reinforcement import ReinforcementLimitsService

if TYPE_CHECKING:
    from ...entities.pier import Pier


class SeismicReinforcementService:
    """
    Verifica refuerzo mínimo para muros estructurales especiales.

    Este servicio centraliza todas las verificaciones de cuantía mínima
    según ACI 318-25 §18.10.2.

    Uso típico:
        service = SeismicReinforcementService()
        result = service.check_minimum_reinforcement(pier)
        if not result.is_ok:
            for warning in result.warnings:
                print(warning)
    """

    def __init__(self):
        """Inicializa el servicio con dependencia de chapter11."""
        self._ch11_service = ReinforcementLimitsService()

    def check_minimum_reinforcement(
        self,
        pier: 'Pier',
        hw: Optional[float] = None
    ) -> SeismicReinforcementResult:
        """
        Verificación completa de refuerzo mínimo usando entidad Pier.

        Args:
            pier: Pier a verificar
            hw: Altura del muro (mm). Si no se provee, usa pier.height

        Returns:
            SeismicReinforcementResult con todos los checks
        """
        hw_actual = hw if hw is not None else pier.height

        return self.check_distributed_reinforcement(
            rho_mesh_v=pier.rho_mesh_vertical,
            rho_v=pier.rho_vertical,
            rho_h=pier.rho_horizontal,
            spacing_v=pier.spacing_v,
            spacing_h=pier.spacing_h,
            hw=hw_actual,
            lw=pier.width
        )

    def check_distributed_reinforcement(
        self,
        rho_mesh_v: float,
        rho_v: float,
        rho_h: float,
        spacing_v: float,
        spacing_h: float,
        hw: float = 0,
        lw: float = 0
    ) -> SeismicReinforcementResult:
        """
        Verificación directa de refuerzo distribuido.

        Args:
            rho_mesh_v: Cuantía de malla vertical (sin barras de borde)
            rho_v: Cuantía total vertical (malla + borde)
            rho_h: Cuantía horizontal
            spacing_v: Espaciamiento vertical (mm)
            spacing_h: Espaciamiento horizontal (mm)
            hw: Altura del muro (mm) - para check §18.10.4.3
            lw: Longitud del muro (mm) - para check §18.10.4.3

        Returns:
            SeismicReinforcementResult con verificación completa
        """
        warnings: List[str] = []

        # =====================================================================
        # §18.10.2.1: Cuantía distribuida (malla) >= 0.0025
        # =====================================================================
        rho_mesh_v_ok = rho_mesh_v >= RHO_MIN
        if not rho_mesh_v_ok:
            warnings.append(
                f"ρ_malla_vertical = {rho_mesh_v:.4f} < {RHO_MIN:.4f} "
                f"mínimo (§18.10.2.1)"
            )

        # =====================================================================
        # §11.6.2: Cuantía total vertical >= 0.0025
        # =====================================================================
        rho_v_ok = rho_v >= RHO_MIN
        if not rho_v_ok:
            warnings.append(
                f"ρ_vertical_total = {rho_v:.4f} < {RHO_MIN:.4f} "
                f"mínimo (§11.6.2)"
            )

        # =====================================================================
        # §18.10.2.1: Cuantía horizontal >= 0.0025
        # =====================================================================
        rho_h_ok = rho_h >= RHO_MIN
        if not rho_h_ok:
            warnings.append(
                f"ρ_horizontal = {rho_h:.4f} < {RHO_MIN:.4f} "
                f"mínimo (§18.10.2.1)"
            )

        # =====================================================================
        # §18.10.2.1: Espaciamiento <= 18" (457mm)
        # =====================================================================
        spacing_v_ok = spacing_v <= MAX_SPACING_SEISMIC_MM
        if not spacing_v_ok:
            warnings.append(
                f"Espaciamiento V = {spacing_v:.0f}mm > {MAX_SPACING_SEISMIC_MM:.0f}mm "
                f"máximo (§18.10.2.1)"
            )

        spacing_h_ok = spacing_h <= MAX_SPACING_SEISMIC_MM
        if not spacing_h_ok:
            warnings.append(
                f"Espaciamiento H = {spacing_h:.0f}mm > {MAX_SPACING_SEISMIC_MM:.0f}mm "
                f"máximo (§18.10.2.1)"
            )

        # =====================================================================
        # §18.10.4.3: Para hw/lw <= 2.0, ρv >= ρh
        # =====================================================================
        hw_lw = hw / lw if lw > 0 else 0
        rho_v_ge_rho_h_required = is_rho_v_ge_rho_h_required(hw, lw)
        rho_v_ge_rho_h_ok, warning_18_10_4_3 = check_rho_vertical_ge_horizontal(
            hw, lw, rho_v, rho_h
        )
        if warning_18_10_4_3:
            warnings.append(warning_18_10_4_3)

        # =====================================================================
        # Resultado global
        # =====================================================================
        is_ok = (
            rho_mesh_v_ok and
            rho_v_ok and
            rho_h_ok and
            spacing_v_ok and
            spacing_h_ok and
            rho_v_ge_rho_h_ok
        )

        return SeismicReinforcementResult(
            # Malla vertical
            rho_mesh_v_min=RHO_MIN,
            rho_mesh_v_actual=rho_mesh_v,
            rho_mesh_v_ok=rho_mesh_v_ok,
            # Total vertical
            rho_v_min=RHO_MIN,
            rho_v_actual=rho_v,
            rho_v_ok=rho_v_ok,
            # Horizontal
            rho_h_min=RHO_MIN,
            rho_h_actual=rho_h,
            rho_h_ok=rho_h_ok,
            # Espaciamiento
            max_spacing=MAX_SPACING_SEISMIC_MM,
            spacing_v=spacing_v,
            spacing_h=spacing_h,
            spacing_v_ok=spacing_v_ok,
            spacing_h_ok=spacing_h_ok,
            # §18.10.4.3
            hw_lw=hw_lw,
            rho_v_ge_rho_h_required=rho_v_ge_rho_h_required,
            rho_v_ge_rho_h_ok=rho_v_ge_rho_h_ok,
            # Global
            is_ok=is_ok,
            warnings=warnings,
            aci_reference="ACI 318-25 §18.10.2.1, §18.10.4.3"
        )

    def get_verification_dict(
        self,
        pier: 'Pier',
        hw: Optional[float] = None
    ) -> dict:
        """
        Obtiene verificación como diccionario para compatibilidad con API existente.

        Args:
            pier: Pier a verificar
            hw: Altura del muro (mm)

        Returns:
            Dict compatible con VerificationResult.reinforcement
        """
        result = self.check_minimum_reinforcement(pier, hw)

        return {
            'rho_v_ok': result.rho_v_ok,
            'rho_h_ok': result.rho_h_ok,
            'rho_mesh_v_ok': result.rho_mesh_v_ok,
            'rho_min': result.rho_v_min,
            'spacing_v_ok': result.spacing_v_ok,
            'spacing_h_ok': result.spacing_h_ok,
            'max_spacing': result.max_spacing,
            'warnings': result.warnings
        }
