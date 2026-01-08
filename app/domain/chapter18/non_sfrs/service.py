# app/domain/chapter18/non_sfrs/service.py
"""
Servicio de verificación para miembros no-SFRS ACI 318-25 §18.14.

Para estructuras en SDC D, E, F, los miembros que no forman parte del
sistema resistente a fuerzas sísmicas (SFRS) deben verificarse para
compatibilidad de deriva.

Incluye:
- §18.14.3: Vigas, columnas y nudos
- §18.14.5: Conexiones losa-columna
- §18.14.6: Pilares de muro no-SFRS
"""
import math
from typing import Optional, List

from .results import (
    NonSfrsResult,
    DriftCompatibilityResult,
    SlabColumnShearResult,
    DriftCheckType,
)

# Constantes
DRIFT_LIMIT_NO_PRESTRESS = 0.005    # Límite sin refuerzo para losa no pretensada
DRIFT_LIMIT_PRESTRESSED = 0.01     # Límite sin refuerzo para losa postensada


class NonSfrsService:
    """
    Servicio para verificación de miembros no parte del SFRS.

    Aplica a miembros en estructuras SDC D, E, F que no están designados
    como parte del sistema resistente a fuerzas sísmicas.

    Example:
        service = NonSfrsService()

        # Verificar compatibilidad de deriva de una columna
        result = service.check_drift_compatibility(
            delta_u=50,      # mm
            hsx=3000,        # mm
            M_induced=15,    # tonf-m
            V_induced=8,     # tonf
            Mn=25,           # tonf-m
            Vn=20,           # tonf
        )

        # Verificar conexión losa-columna
        result = service.check_slab_column_shear(
            drift_ratio=0.02,
            vuv=0.8,         # MPa
            phi_vc=1.2,      # MPa
            fc=28,           # MPa
            slab_thickness=200,
        )
    """

    def check_drift_compatibility(
        self,
        delta_u: float,
        hsx: float,
        M_induced: float = 0,
        V_induced: float = 0,
        Mn: float = 0,
        Vn: float = 0,
        phi: float = 0.9,
    ) -> DriftCompatibilityResult:
        """
        Verifica compatibilidad de deriva según §18.14.3.

        Los miembros no-SFRS deben poder acomodar el desplazamiento de diseño δu
        mientras resisten cargas de gravedad.

        Args:
            delta_u: Desplazamiento de diseño (mm)
            hsx: Altura de entrepiso (mm)
            M_induced: Momento inducido por deriva (tonf-m), 0 si no calculado
            V_induced: Cortante inducido por deriva (tonf), 0 si no calculado
            Mn: Resistencia nominal a flexión (tonf-m)
            Vn: Resistencia nominal a cortante (tonf)
            phi: Factor de reducción (0.9 para flexión)

        Returns:
            DriftCompatibilityResult con verificación completa
        """
        warnings = []
        drift_ratio = delta_u / hsx if hsx > 0 else 0

        # Determinar tipo de verificación
        if M_induced == 0 and V_induced == 0:
            # No se calcularon efectos de deriva -> usar §18.14.3.3
            check_type = DriftCheckType.NOT_CALCULATED
            within_capacity = True  # Asumir, pero aplicar requisitos más estrictos
            M_within_capacity = True
            V_within_capacity = True
            warnings.append("Efectos de δu no calculados - aplicar §18.14.3.3")
        else:
            # Verificar si momentos/cortantes exceden capacidad
            M_within_capacity = M_induced <= phi * Mn if Mn > 0 else True
            V_within_capacity = V_induced <= phi * Vn if Vn > 0 else True
            within_capacity = M_within_capacity and V_within_capacity

            if within_capacity:
                check_type = DriftCheckType.WITHIN_CAPACITY
            else:
                check_type = DriftCheckType.EXCEEDS_CAPACITY
                if not M_within_capacity:
                    warnings.append(f"M_inducido={M_induced:.1f} > φMn={phi*Mn:.1f} - aplicar §18.14.3.3")
                if not V_within_capacity:
                    warnings.append(f"V_inducido={V_induced:.1f} > φVn={phi*Vn:.1f} - aplicar §18.14.3.3")

        is_ok = within_capacity

        return DriftCompatibilityResult(
            delta_u=delta_u,
            hsx=hsx,
            drift_ratio=round(drift_ratio, 4),
            check_type=check_type,
            M_induced=M_induced,
            V_induced=V_induced,
            Mn=Mn,
            Vn=Vn,
            M_within_capacity=M_within_capacity,
            V_within_capacity=V_within_capacity,
            within_capacity=within_capacity,
            is_ok=is_ok,
            warnings=warnings,
        )

    def check_slab_column_shear(
        self,
        drift_ratio: float,
        vuv: float,
        phi_vc: float,
        fc: float,
        slab_thickness: float,
        is_prestressed: bool = False,
    ) -> SlabColumnShearResult:
        """
        Verifica conexión losa-columna según §18.14.5.

        Determina si se requiere refuerzo de cortante basado en la deriva
        y el nivel de esfuerzo cortante.

        Criterio de refuerzo:
        - No pretensada: Δx/hsx >= 0.035 - (1/20)*(vuv/φvc)
        - Postensada: Δx/hsx >= 0.040 - (1/20)*(vuv/φvc)

        Exentas si:
        - No pretensada: Δx/hsx <= 0.005
        - Postensada: Δx/hsx <= 0.01

        Args:
            drift_ratio: Δx/hsx (mayor de pisos adyacentes)
            vuv: Esfuerzo cortante por gravedad + sismo vertical (MPa)
            phi_vc: φvc calculado según §22.6.5 (MPa)
            fc: f'c del concreto (MPa)
            slab_thickness: Espesor de losa (mm)
            is_prestressed: True si losa postensada

        Returns:
            SlabColumnShearResult con verificación completa
        """
        warnings = []

        # Límites según tipo de losa
        if is_prestressed:
            drift_limit_no_reinf = DRIFT_LIMIT_PRESTRESSED
            base_threshold = 0.040
        else:
            drift_limit_no_reinf = DRIFT_LIMIT_NO_PRESTRESS
            base_threshold = 0.035

        # Calcular ratio de esfuerzo
        stress_ratio = vuv / phi_vc if phi_vc > 0 else 0

        # Umbral de deriva para requerir refuerzo
        drift_threshold = base_threshold - (1/20) * stress_ratio

        # Verificar exención por baja deriva
        is_exempt = drift_ratio <= drift_limit_no_reinf

        # Verificar si requiere refuerzo
        if is_exempt:
            requires_shear_reinf = False
        else:
            requires_shear_reinf = drift_ratio >= drift_threshold

        # Calcular refuerzo requerido si aplica
        if requires_shear_reinf:
            vs_required = 3.5 * math.sqrt(fc)  # MPa
            extension_required = 4 * slab_thickness  # mm
            warnings.append(f"Requiere refuerzo de cortante vs >= {vs_required:.2f} MPa")
        else:
            vs_required = 0
            extension_required = 0

        is_ok = not requires_shear_reinf or (vs_required > 0)

        return SlabColumnShearResult(
            drift_ratio=round(drift_ratio, 4),
            is_prestressed=is_prestressed,
            vuv=round(vuv, 3),
            phi_vc=round(phi_vc, 3),
            stress_ratio=round(stress_ratio, 3),
            drift_limit_no_reinf=drift_limit_no_reinf,
            drift_threshold=round(drift_threshold, 4),
            requires_shear_reinf=requires_shear_reinf,
            is_exempt=is_exempt,
            vs_required=round(vs_required, 2),
            extension_required=round(extension_required, 0),
            is_ok=is_ok,
            warnings=warnings,
        )

    def verify_non_sfrs_member(
        self,
        element_type: str,
        delta_u: float,
        hsx: float,
        M_induced: float = 0,
        V_induced: float = 0,
        Mn: float = 0,
        Vn: float = 0,
        # Para losa-columna
        vuv: float = 0,
        phi_vc: float = 0,
        fc: float = 0,
        slab_thickness: float = 0,
        is_prestressed: bool = False,
    ) -> NonSfrsResult:
        """
        Verificación completa de miembro no-SFRS.

        Args:
            element_type: "beam", "column", "joint", "slab_column", "wall_pier"
            delta_u: Desplazamiento de diseño (mm)
            hsx: Altura de entrepiso (mm)
            M_induced: Momento inducido por deriva (tonf-m)
            V_induced: Cortante inducido por deriva (tonf)
            Mn: Resistencia nominal a flexión (tonf-m)
            Vn: Resistencia nominal a cortante (tonf)
            vuv: Esfuerzo cortante (solo losa-columna, MPa)
            phi_vc: φvc (solo losa-columna, MPa)
            fc: f'c del concreto (MPa)
            slab_thickness: Espesor de losa (mm)
            is_prestressed: True si losa postensada

        Returns:
            NonSfrsResult con todas las verificaciones aplicables
        """
        warnings: List[str] = []
        drift_compat = None
        slab_shear = None

        # Verificar compatibilidad de deriva para vigas/columnas
        if element_type in ("beam", "column", "wall_pier"):
            drift_compat = self.check_drift_compatibility(
                delta_u, hsx, M_induced, V_induced, Mn, Vn
            )
            if not drift_compat.is_ok:
                warnings.extend(drift_compat.warnings)

        # Verificar conexión losa-columna
        if element_type == "slab_column":
            drift_ratio = delta_u / hsx if hsx > 0 else 0
            slab_shear = self.check_slab_column_shear(
                drift_ratio, vuv, phi_vc, fc, slab_thickness, is_prestressed
            )
            if not slab_shear.is_ok:
                warnings.extend(slab_shear.warnings)

        # Determinar resultado global
        is_ok = True
        if drift_compat and not drift_compat.is_ok:
            is_ok = False
        if slab_shear and not slab_shear.is_ok:
            is_ok = False

        return NonSfrsResult(
            element_type=element_type,
            drift_compatibility=drift_compat,
            slab_column_shear=slab_shear,
            is_ok=is_ok,
            warnings=warnings,
        )
