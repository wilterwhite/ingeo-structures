# app/domain/chapter18/walls/service.py
"""
Servicio de verificación para muros sísmicos especiales ACI 318-25 §18.10.

Orquesta las verificaciones:
- Clasificación (Tabla R18.10.1)
- Refuerzo mínimo (§18.10.2.1)
- Cortante y amplificación (§18.10.3, §18.10.4)
- Elementos de borde (§18.10.6)
- Zonas de extremo (§18.10.2.4) si hw/lw >= 2.0
- Verificaciones de pilar de muro (§18.10.8) si lw/tw <= 6.0

Diseñado para ser consistente con SeismicColumnService y SeismicBeamService.
"""
import math
from typing import Optional, List, TYPE_CHECKING

from ..common import SeismicCategory
from ..boundary_elements import BoundaryElementService
from ..wall_piers import WallPierService, classify_wall_pier
from ..reinforcement import SeismicReinforcementService
from ..design_forces import ShearAmplificationService
from ...constants.reinforcement import RHO_MIN, MAX_SPACING_SEISMIC_MM
from ...constants.materials import get_effective_fc_shear
from ...constants.shear import PHI_SHEAR
from ...constants.units import N_TO_TONF

from .results import (
    SeismicWallResult,
    WallClassificationResult,
    WallReinforcementResult,
    WallShearResult,
    WallBoundaryResult,
)

if TYPE_CHECKING:
    from ...entities.pier import Pier


class SeismicWallService:
    """
    Servicio principal para verificación de muros sísmicos especiales §18.10.

    Realiza todas las verificaciones aplicables para muros estructurales
    especiales según ACI 318-25, incluyendo:

    - §18.10.2: Refuerzo mínimo y doble cortina
    - §18.10.3: Fuerzas de diseño (amplificación)
    - §18.10.4: Resistencia al cortante
    - §18.10.6: Elementos de borde
    - §18.10.8: Pilares de muro (wall piers)

    Example:
        service = SeismicWallService()

        # Verificación desde entidad Pier
        result = service.verify_wall(pier, Vu=150, Mu=500)

        # Verificación directa con parámetros
        result = service.verify_wall_direct(
            hw=3000, lw=4000, tw=200,
            fc=28, fy=420, fyt=420,
            rho_v=0.0030, rho_h=0.0028,
            Vu=150, Mu=500
        )
    """

    def __init__(self):
        """Inicializa el servicio con dependencias."""
        self._boundary_service = BoundaryElementService()
        self._wall_pier_service = WallPierService()
        self._reinforcement_service = SeismicReinforcementService()
        self._amplification_service = ShearAmplificationService()

    # =========================================================================
    # VERIFICACIÓN PRINCIPAL
    # =========================================================================

    def verify_wall(
        self,
        pier: 'Pier',
        Vu: float = 0,
        Mu: float = 0,
        Pu: float = 0,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        lambda_factor: float = 1.0,
        check_boundary: bool = True,
        use_omega_0: bool = False,
    ) -> SeismicWallResult:
        """
        Verifica un muro sísmico especial usando entidad Pier.

        Args:
            pier: Entidad Pier con geometría y armadura
            Vu: Cortante último del análisis (tonf)
            Mu: Momento último (tonf-m)
            Pu: Carga axial (tonf, positivo = compresión)
            hwcs: Altura desde sección crítica (mm). Si None, usa pier.height
            hn_ft: Altura total del edificio en pies (para amplificación)
            lambda_factor: Factor para concreto liviano (default 1.0)
            check_boundary: Si verificar elementos de borde (default True)
            use_omega_0: Si usar Omega_0 en lugar de factores §18.10.3.3

        Returns:
            SeismicWallResult con todas las verificaciones
        """
        hwcs_actual = hwcs if hwcs is not None else pier.height

        return self.verify_wall_direct(
            hw=pier.height,
            lw=pier.width,
            tw=pier.thickness,
            fc=pier.fc,
            fy=pier.fy,
            fyt=pier.fy,  # Asumir mismo fy para transversal
            rho_v=pier.rho_vertical,
            rho_h=pier.rho_horizontal,
            rho_mesh_v=pier.rho_mesh_vertical,
            spacing_v=pier.spacing_v,
            spacing_h=pier.spacing_h,
            n_meshes=pier.n_meshes,
            Vu=Vu,
            Mu=Mu,
            Pu=Pu,
            hwcs=hwcs_actual,
            hn_ft=hn_ft,
            lambda_factor=lambda_factor,
            check_boundary=check_boundary,
            use_omega_0=use_omega_0,
        )

    def verify_wall_direct(
        self,
        # Geometría
        hw: float,
        lw: float,
        tw: float,
        # Materiales
        fc: float,
        fy: float,
        fyt: float,
        # Refuerzo
        rho_v: float,
        rho_h: float,
        rho_mesh_v: float = 0,
        spacing_v: float = 200,
        spacing_h: float = 200,
        n_meshes: int = 2,
        # Fuerzas
        Vu: float = 0,
        Mu: float = 0,
        Pu: float = 0,
        # Amplificación
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        use_omega_0: bool = False,
        # Opciones
        lambda_factor: float = 1.0,
        check_boundary: bool = True,
        category: SeismicCategory = SeismicCategory.SPECIAL,
    ) -> SeismicWallResult:
        """
        Verifica un muro sísmico especial con parámetros directos.

        Args:
            hw: Altura del muro (mm)
            lw: Longitud del muro (mm)
            tw: Espesor del muro (mm)
            fc: f'c del concreto (MPa)
            fy: Fluencia del refuerzo longitudinal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            rho_v: Cuantía vertical total
            rho_h: Cuantía horizontal
            rho_mesh_v: Cuantía vertical de malla (sin borde)
            spacing_v: Espaciamiento vertical (mm)
            spacing_h: Espaciamiento horizontal (mm)
            n_meshes: Número de cortinas (1 o 2)
            Vu: Cortante último (tonf)
            Mu: Momento último (tonf-m)
            Pu: Carga axial (tonf)
            hwcs: Altura desde sección crítica (mm)
            hn_ft: Altura del edificio (pies)
            use_omega_0: Si usar Omega_0 para amplificación
            lambda_factor: Factor para concreto liviano
            check_boundary: Si verificar elementos de borde
            category: Categoría sísmica

        Returns:
            SeismicWallResult con todas las verificaciones
        """
        warnings: List[str] = []
        dcr_max = 0.0
        critical_check = ""

        hwcs_actual = hwcs if hwcs is not None else hw

        # =====================================================================
        # 1. CLASIFICACIÓN
        # =====================================================================
        classification = self._classify_wall(hw, lw, tw)

        # =====================================================================
        # 2. REFUERZO MÍNIMO (§18.10.2.1)
        # =====================================================================
        reinforcement = self._check_reinforcement(
            hw, lw, tw, fc, fy,
            rho_v, rho_h, rho_mesh_v,
            spacing_v, spacing_h, n_meshes,
            Vu, lambda_factor
        )

        if not reinforcement.is_ok:
            warnings.extend(reinforcement.warnings)
            # DCR para refuerzo: usar peor ratio
            if reinforcement.rho_l_actual > 0:
                dcr_rho = reinforcement.rho_l_min / reinforcement.rho_l_actual
                if dcr_rho > dcr_max:
                    dcr_max = dcr_rho
                    critical_check = "reinforcement_rho_v"

        # =====================================================================
        # 3. CORTANTE (§18.10.3, §18.10.4)
        # =====================================================================
        shear = self._check_shear(
            hw, lw, tw, fc, fyt, rho_h,
            Vu, hwcs_actual, hn_ft,
            classification.is_wall_pier, use_omega_0, lambda_factor
        )

        if shear.dcr > dcr_max:
            dcr_max = shear.dcr
            critical_check = "shear"

        if not shear.is_ok:
            warnings.append(
                f"DCR cortante = {shear.dcr:.2f} > 1.0: "
                "Aumentar refuerzo horizontal o espesor"
            )

        # =====================================================================
        # 4. ELEMENTOS DE BORDE (§18.10.6)
        # =====================================================================
        boundary = None
        if check_boundary and (Pu > 0 or Mu > 0):
            boundary = self._check_boundary_elements(
                hw, lw, tw, fc, fyt, Pu, Mu, hwcs_actual
            )

            if boundary.requires_special and not boundary.is_ok:
                warnings.extend(boundary.warnings)
                # No hay DCR directo para boundary, pero marca como crítico
                if dcr_max < 1.0:
                    dcr_max = 1.1
                    critical_check = "boundary"

        # =====================================================================
        # 5. ZONAS DE EXTREMO (§18.10.2.4) si hw/lw >= 2.0
        # =====================================================================
        end_zones = None
        if classification.requires_boundary_zones:
            rho_end_min = self._reinforcement_service.calculate_end_zone_rho_min(fc, fy)
            end_zone_length = self._reinforcement_service.get_end_zone_length(lw)
            warnings.append(
                f"hw/lw={classification.hw_lw:.2f} >= 2.0: Verificar zonas de extremo "
                f"(0.15×lw={end_zone_length:.0f}mm) con ρ >= {rho_end_min:.4f}"
            )

        # =====================================================================
        # 6. PILAR DE MURO (§18.10.8) si lw/tw <= 6.0
        # =====================================================================
        wall_pier = None
        if classification.is_wall_pier:
            wall_pier = classify_wall_pier(hw, lw, tw)
            if wall_pier.requires_column_details:
                warnings.append(
                    f"Pilar de muro (lw/tw={classification.lw_tw:.1f}): "
                    "Verificar requisitos de columna especial §18.7"
                )

        # =====================================================================
        # RESULTADO GLOBAL
        # =====================================================================
        is_ok = (
            reinforcement.is_ok and
            shear.is_ok and
            (boundary is None or boundary.is_ok)
        )

        return SeismicWallResult(
            classification=classification,
            reinforcement=reinforcement,
            shear=shear,
            boundary=boundary,
            end_zones=end_zones,
            wall_pier=wall_pier,
            is_ok=is_ok,
            dcr_max=round(dcr_max, 3),
            critical_check=critical_check,
            warnings=warnings,
            aci_reference="ACI 318-25 §18.10",
        )

    # =========================================================================
    # MÉTODOS PRIVADOS
    # =========================================================================

    def _classify_wall(
        self,
        hw: float,
        lw: float,
        tw: float
    ) -> WallClassificationResult:
        """Clasifica el muro según §18.10 y Tabla R18.10.1."""
        hw_lw = hw / lw if lw > 0 else 0
        lw_tw = lw / tw if tw > 0 else 0

        is_slender = hw_lw >= 2.0
        is_wall_pier = lw_tw <= 6.0 and hw_lw < 2.0
        requires_boundary_zones = hw_lw >= 2.0

        return WallClassificationResult(
            hw=hw,
            lw=lw,
            tw=tw,
            hw_lw=round(hw_lw, 2),
            lw_tw=round(lw_tw, 2),
            is_slender=is_slender,
            is_wall_pier=is_wall_pier,
            requires_boundary_zones=requires_boundary_zones,
            aci_reference="ACI 318-25 §18.10, Tabla R18.10.1",
        )

    def _check_reinforcement(
        self,
        hw: float,
        lw: float,
        tw: float,
        fc: float,
        fy: float,
        rho_v: float,
        rho_h: float,
        rho_mesh_v: float,
        spacing_v: float,
        spacing_h: float,
        n_meshes: int,
        Vu: float,
        lambda_factor: float,
    ) -> WallReinforcementResult:
        """Verifica refuerzo mínimo §18.10.2.1."""
        warnings: List[str] = []

        # Cuantías mínimas
        rho_l_min = RHO_MIN
        rho_t_min = RHO_MIN
        spacing_max = MAX_SPACING_SEISMIC_MM

        # Verificar cuantías
        rho_l_ok = rho_v >= rho_l_min
        rho_t_ok = rho_h >= rho_t_min

        if not rho_l_ok:
            warnings.append(f"ρ_vertical={rho_v:.4f} < {rho_l_min:.4f} mínimo (§18.10.2.1)")
        if not rho_t_ok:
            warnings.append(f"ρ_horizontal={rho_h:.4f} < {rho_t_min:.4f} mínimo (§18.10.2.1)")

        # Verificar espaciamiento
        spacing_v_ok = spacing_v <= spacing_max
        spacing_h_ok = spacing_h <= spacing_max

        if not spacing_v_ok:
            warnings.append(f"Espaciamiento V={spacing_v:.0f}mm > {spacing_max:.0f}mm (§18.10.2.1)")
        if not spacing_h_ok:
            warnings.append(f"Espaciamiento H={spacing_h:.0f}mm > {spacing_max:.0f}mm (§18.10.2.1)")

        # Doble cortina (§18.10.2.2)
        Acv = lw * tw
        hw_lw = hw / lw if lw > 0 else 0
        threshold_double = 2 * lambda_factor * math.sqrt(fc) * Acv * N_TO_TONF

        requires_double = (abs(Vu) > threshold_double) or (hw_lw >= 2.0)
        has_double = n_meshes >= 2

        if abs(Vu) > threshold_double:
            double_reason = f"Vu={abs(Vu):.1f} > 2×λ×√f'c×Acv={threshold_double:.1f}"
        elif hw_lw >= 2.0:
            double_reason = f"hw/lw={hw_lw:.2f} >= 2.0"
        else:
            double_reason = ""

        if requires_double and not has_double:
            warnings.append(f"Se requiere doble cortina: {double_reason}")

        # rho_l >= rho_t para muros bajos (§18.10.4.3)
        rho_l_ge_rho_t_required = hw_lw <= 2.0 if hw_lw > 0 else False
        rho_l_ge_rho_t_ok = rho_v >= rho_h if rho_l_ge_rho_t_required else True

        if rho_l_ge_rho_t_required and not rho_l_ge_rho_t_ok:
            warnings.append(
                f"Para hw/lw={hw_lw:.2f} <= 2.0, se requiere ρ_v >= ρ_h (§18.10.4.3)"
            )

        is_ok = (
            rho_l_ok and rho_t_ok and
            spacing_v_ok and spacing_h_ok and
            rho_l_ge_rho_t_ok and
            (not requires_double or has_double)
        )

        return WallReinforcementResult(
            rho_l_min=rho_l_min,
            rho_l_actual=round(rho_v, 5),
            rho_l_ok=rho_l_ok,
            rho_t_min=rho_t_min,
            rho_t_actual=round(rho_h, 5),
            rho_t_ok=rho_t_ok,
            spacing_max=spacing_max,
            spacing_v_actual=spacing_v,
            spacing_h_actual=spacing_h,
            spacing_ok=spacing_v_ok and spacing_h_ok,
            requires_double_curtain=requires_double,
            double_curtain_reason=double_reason,
            has_double_curtain=has_double,
            rho_l_ge_rho_t_required=rho_l_ge_rho_t_required,
            rho_l_ge_rho_t_ok=rho_l_ge_rho_t_ok,
            is_ok=is_ok,
            warnings=warnings,
            aci_reference="ACI 318-25 §18.10.2.1",
        )

    def _check_shear(
        self,
        hw: float,
        lw: float,
        tw: float,
        fc: float,
        fyt: float,
        rho_h: float,
        Vu: float,
        hwcs: float,
        hn_ft: Optional[float],
        is_wall_pier: bool,
        use_omega_0: bool,
        lambda_factor: float,
    ) -> WallShearResult:
        """Verifica cortante §18.10.3, §18.10.4."""
        Acv = lw * tw  # mm²
        fc_eff = get_effective_fc_shear(fc)

        # Amplificación (solo si no es wall pier)
        amplification = None
        if not is_wall_pier and abs(Vu) > 0:
            amplification = self._amplification_service.calculate_amplified_shear(
                Vu=Vu,
                hwcs=hwcs,
                lw=lw,
                hn_ft=hn_ft,
                use_omega_0=use_omega_0,
            )
            Ve = amplification.Ve
        else:
            Ve = abs(Vu)

        # Calcular Vc según §18.10.4.1
        hw_lw = hw / lw if lw > 0 else 0
        if hw_lw <= 1.5:
            alpha_c = 0.25
        elif hw_lw >= 2.0:
            alpha_c = 0.17
        else:
            # Interpolar
            alpha_c = 0.25 - 0.08 * (hw_lw - 1.5) / 0.5

        # Vc = alpha_c × lambda × sqrt(f'c) × Acv (en N)
        Vc_N = alpha_c * lambda_factor * math.sqrt(fc_eff) * Acv
        Vc_tonf = Vc_N * N_TO_TONF

        # Vs = rho_h × fyt × Acv (en N)
        Vs_N = rho_h * fyt * Acv
        Vs_tonf = Vs_N * N_TO_TONF

        # Vn
        Vn_tonf = Vc_tonf + Vs_tonf
        phi_Vn = PHI_SHEAR * Vn_tonf

        # Límite máximo §18.10.4.4: Vn <= 0.66 × sqrt(f'c) × Acv
        Vn_max_N = 0.66 * math.sqrt(fc_eff) * Acv
        Vn_max_tonf = Vn_max_N * N_TO_TONF
        Vn_max_ok = Vn_tonf <= Vn_max_tonf

        # DCR
        dcr = Ve / phi_Vn if phi_Vn > 0 else float('inf')
        is_ok = dcr <= 1.0 and Vn_max_ok

        return WallShearResult(
            Vu=round(abs(Vu), 2),
            Ve=round(Ve, 2),
            Vc=round(Vc_tonf, 2),
            Vs=round(Vs_tonf, 2),
            Vn=round(Vn_tonf, 2),
            phi_Vn=round(phi_Vn, 2),
            Vn_max=round(Vn_max_tonf, 2),
            Vn_max_ok=Vn_max_ok,
            dcr=round(dcr, 3),
            is_ok=is_ok,
            amplification=amplification,
            aci_reference="ACI 318-25 §18.10.4",
        )

    def _check_boundary_elements(
        self,
        hw: float,
        lw: float,
        tw: float,
        fc: float,
        fyt: float,
        Pu: float,
        Mu: float,
        hwcs: float,
    ) -> WallBoundaryResult:
        """Verifica elementos de borde §18.10.6."""
        warnings: List[str] = []

        # Calcular esfuerzo máximo por método de esfuerzos
        Ag = lw * tw
        Ig = tw * (lw ** 3) / 12
        y = lw / 2

        # P en N, M en N-mm
        Pu_N = abs(Pu) * 9806.65  # tonf a N
        Mu_Nmm = abs(Mu) * 9806.65 * 1000  # tonf-m a N-mm

        # sigma = P/A + M×y/I
        sigma_axial = Pu_N / Ag if Ag > 0 else 0
        sigma_moment = (Mu_Nmm * y / Ig) if Ig > 0 else 0
        sigma_max = (sigma_axial + sigma_moment)  # MPa (ya en N/mm² = MPa)

        # Verificar por método de esfuerzos
        stress_result = self._boundary_service.check_stress_method(sigma_max, fc)
        requires_special = stress_result.requires_special

        stress_check = {
            'sigma_max': round(sigma_max, 2),
            'limit': round(stress_result.limit_require, 2),
            'requires_special': requires_special,
        }

        # Si requiere, calcular dimensiones
        length_horizontal = 0
        vertical_extension = 0
        Ash_sbc_required = 0
        spacing_max = 0

        if requires_special:
            # Calcular c (profundidad eje neutro) aproximado
            # Simplificado: c = lw × (0.5 + sigma_axial / (2 × 0.85 × f'c))
            c = lw * (0.5 + sigma_axial / (2 * 0.85 * fc)) if fc > 0 else lw / 2
            c = min(c, lw)  # No mayor que lw

            # Extensión horizontal: max(c - 0.1×lw, c/2)
            length_horizontal = max(c - 0.1 * lw, c / 2)

            # Extensión vertical
            if hwcs > 0 and lw > 0:
                vertical_extension = max(lw, abs(Mu) * 1000 / (3 * abs(Pu))) if Pu > 0 else lw
            else:
                vertical_extension = lw

            warnings.append(
                f"Se requieren elementos de borde: σ_max={sigma_max:.1f}MPa >= "
                f"0.2×f'c={stress_result.limit_require:.1f}MPa"
            )

            # Calcular confinamiento requerido
            Ach = length_horizontal * tw * 0.85  # Aproximado
            if Ach > 0 and Ag > 0:
                transverse = self._boundary_service.calculate_transverse_reinforcement(
                    Ag=Ag, Ach=Ach, fc=fc, fyt=fyt, b=tw
                )
                Ash_sbc_required = transverse.Ash_sbc_required
                spacing_max = transverse.spacing_max

        is_ok = not requires_special or (requires_special and len(warnings) == 1)

        return WallBoundaryResult(
            method_used="stress",
            requires_special=requires_special,
            stress_check=stress_check,
            length_horizontal=round(length_horizontal, 0),
            vertical_extension=round(vertical_extension, 0),
            Ash_sbc_required=round(Ash_sbc_required, 5),
            spacing_max=round(spacing_max, 0),
            is_ok=is_ok,
            warnings=warnings,
            aci_reference="ACI 318-25 §18.10.6",
        )

    # =========================================================================
    # MÉTODOS DE CONVENIENCIA
    # =========================================================================

    def verify_drop_beam(
        self,
        drop_beam,
        Vu: float = 0,
        Mu: float = 0,
        Pu: float = 0,
        lambda_factor: float = 1.0,
    ) -> SeismicWallResult:
        """
        Verifica una viga capitel como muro.

        Las vigas capitel se diseñan como muros a flexocompresión
        según el plan de unificación.

        Args:
            drop_beam: Entidad DropBeam
            Vu: Cortante último (tonf)
            Mu: Momento último (tonf-m)
            Pu: Carga axial (tonf)
            lambda_factor: Factor para concreto liviano

        Returns:
            SeismicWallResult con verificaciones
        """
        return self.verify_wall_direct(
            hw=drop_beam.length,       # Altura = luz
            lw=drop_beam.thickness,    # Longitud = ancho tributario
            tw=drop_beam.width,        # Espesor = espesor losa
            fc=drop_beam.fc,
            fy=drop_beam.fy,
            fyt=drop_beam.fy,
            rho_v=drop_beam.rho_vertical,
            rho_h=drop_beam.rho_horizontal,
            rho_mesh_v=drop_beam.rho_mesh_vertical,
            spacing_v=drop_beam.spacing_v,
            spacing_h=drop_beam.spacing_h,
            n_meshes=drop_beam.n_meshes,
            Vu=Vu,
            Mu=Mu,
            Pu=Pu,
            lambda_factor=lambda_factor,
            check_boundary=True,
        )
