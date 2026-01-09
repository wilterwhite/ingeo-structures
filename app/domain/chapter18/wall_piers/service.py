# app/domain/chapter18/piers/service.py
"""
Servicio de verificación de pilares de muro según ACI 318-25 §18.10.8.

Orquesta:
- Clasificación (Tabla R18.10.1)
- Diseño por cortante
- Refuerzo transversal
- Elementos de borde
"""
from typing import Optional, List, TYPE_CHECKING

from ..boundary_elements import BoundaryElementService
from ..results import (
    DesignMethod,
    WallPierClassification,
    WallPierShearDesign,
    WallPierTransverseReinforcement,
    WallPierBoundaryCheck,
    BoundaryZoneCheck,
    EdgePierCheck,
    WallPierDesignResult,
)
from .classification import classify_wall_pier
from .shear_design import calculate_design_shear, verify_shear_strength
from .transverse import calculate_transverse_requirements
from .boundary_zones import check_boundary_zone_reinforcement

if TYPE_CHECKING:
    from ...entities.pier import Pier


class WallPierService:
    """
    Servicio de verificación de pilares de muro según ACI 318-25.

    Proporciona clasificación, diseño por cortante, y requisitos
    de detallado para pilares de muro (segmentos verticales estrechos).

    Usa servicios existentes para evitar duplicación:
    - ShearVerificationService: Verificación de cortante
    - BoundaryElementService: Verificación de elementos de borde

    Unidades:
    - Longitudes: mm
    - Esfuerzos: MPa
    - Fuerzas: tonf
    """

    def __init__(self):
        """Inicializa los servicios dependientes."""
        self._boundary_service = BoundaryElementService()

    # =========================================================================
    # CLASIFICACIÓN DEL PILAR (TABLA R18.10.1)
    # =========================================================================

    def classify_wall_pier(
        self,
        hw: float,
        lw: float,
        bw: float
    ) -> WallPierClassification:
        """Clasifica el pilar de muro según Tabla R18.10.1."""
        return classify_wall_pier(hw, lw, bw)

    # =========================================================================
    # CORTANTE DE DISEÑO (18.10.8.1(a))
    # =========================================================================

    def calculate_design_shear(
        self,
        Vu: float,
        lu: float = 0,
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        Omega_o: float = 3.0
    ) -> WallPierShearDesign:
        """
        Calcula el cortante de diseño Ve para el pilar.

        Delega a calculate_design_shear() de shear_design.py.
        El diseño por capacidad se aplica automáticamente si Mpr > 0 y lu > 0.
        """
        return calculate_design_shear(
            Vu=Vu,
            lu=lu,
            Mpr_top=Mpr_top,
            Mpr_bottom=Mpr_bottom,
            Omega_o=Omega_o
        )

    def verify_shear_strength(
        self,
        Ve: float,
        lw: float,
        bw: float,
        fc: float,
        rho_h: float,
        fyt: float,
        hw: float = 0
    ) -> WallPierShearDesign:
        """Verifica la resistencia al cortante del pilar."""
        return verify_shear_strength(Ve, lw, bw, fc, rho_h, fyt, hw)

    # =========================================================================
    # REFUERZO TRANSVERSAL (18.10.8.1(c)-(e))
    # =========================================================================

    def calculate_transverse_requirements(
        self,
        classification: WallPierClassification,
        has_single_curtain: bool = False,
        fc: float = 28,
        fyt: float = 420
    ) -> WallPierTransverseReinforcement:
        """Calcula requisitos de refuerzo transversal para pilar."""
        return calculate_transverse_requirements(
            classification, has_single_curtain, fc, fyt
        )

    # =========================================================================
    # ELEMENTOS DE BORDE (18.10.8.1(f))
    # =========================================================================

    def check_boundary_elements(
        self,
        sigma_max: float,
        fc: float
    ) -> WallPierBoundaryCheck:
        """
        Verifica si se requieren elementos de borde para el pilar.

        Delega a BoundaryElementService para el método de esfuerzos.

        Según 18.10.8.1(f):
        Si se requiere por 18.10.6.3 (método de esfuerzos)

        Args:
            sigma_max: Esfuerzo máximo de compresión (MPa)
            fc: f'c del hormigón (MPa)

        Returns:
            WallPierBoundaryCheck con resultado
        """
        # Usar BoundaryElementService para la verificación
        stress_result = self._boundary_service.check_stress_method(sigma_max, fc)

        return WallPierBoundaryCheck(
            requires_boundary=stress_result.requires_special,
            method_used="stress (18.10.6.3)",
            sigma_max=stress_result.sigma_max,
            sigma_limit=stress_result.limit_require,
            aci_reference="ACI 318-25 18.10.8.1(f), 18.10.6.3"
        )

    # =========================================================================
    # ZONAS DE EXTREMO (18.10.2.4)
    # =========================================================================

    def check_boundary_zones(
        self,
        pier: 'Pier',
        Mu: float = 0,
        Vu: float = 0
    ) -> BoundaryZoneCheck:
        """
        Verifica refuerzo en zonas de extremo segun ACI 318-25 §18.10.2.4.

        Para muros/pilares con hw/lw >= 2.0 y seccion critica unica:
        - (a) rho >= 6*sqrt(f'c)/fy en extremos (0.15*lw x bw)
        - (b) Extension vertical >= max(lw, Mu/3Vu)

        Args:
            pier: Entidad Pier con geometria y armadura
            Mu: Momento ultimo en seccion critica (tonf-m)
            Vu: Cortante ultimo en seccion critica (tonf)

        Returns:
            BoundaryZoneCheck con resultado de la verificacion
        """
        return check_boundary_zone_reinforcement(
            hw=pier.height,
            lw=pier.width,
            bw=pier.thickness,
            fc=pier.fc,
            fy=pier.fy,
            As_left=pier.As_boundary_left,
            As_right=pier.As_boundary_right,
            Mu=Mu,
            Vu=Vu
        )

    # =========================================================================
    # PILARES EN BORDE DE MURO (18.10.8.2)
    # =========================================================================

    def check_edge_pier_requirements(
        self,
        pier_Ve: float,
        adjacent_segments_capacity: List[float]
    ) -> EdgePierCheck:
        """
        Verifica requisitos para pilares en borde de muro.

        Según 18.10.8.2:
        - Proporcionar refuerzo horizontal en segmentos adyacentes
        - Diseñar para transferir cortante del pilar

        Args:
            pier_Ve: Cortante del pilar (tonf)
            adjacent_segments_capacity: Capacidad de transferencia de
                                       segmentos adyacentes (tonf)

        Returns:
            EdgePierCheck con verificación
        """
        total_capacity = sum(adjacent_segments_capacity)
        is_ok = total_capacity >= pier_Ve

        return EdgePierCheck(
            pier_Ve=pier_Ve,
            adjacent_capacity=total_capacity,
            transfer_ok=is_ok,
            required_transfer=pier_Ve
        )

    # =========================================================================
    # DISEÑO COMPLETO
    # =========================================================================

    def design_wall_pier(
        self,
        hw: float,
        lw: float,
        bw: float,
        Vu: float,
        fc: float,
        fy: float,
        fyt: float,
        rho_h: float,
        sigma_max: float = 0,
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        has_single_curtain: bool = False,
        use_capacity_design: bool = True,
        Omega_o: float = 3.0,
        lambda_factor: float = 1.0,
        As_boundary_left: float = 0,
        As_boundary_right: float = 0,
        Mu: float = 0,
        adjacent_segments_capacity: Optional[List[float]] = None
    ) -> WallPierDesignResult:
        """
        Realiza diseño completo del pilar de muro.

        Args:
            hw: Altura del segmento (mm)
            lw: Longitud del segmento (mm)
            bw: Espesor del segmento (mm)
            Vu: Cortante del análisis (tonf)
            fc: f'c del hormigón (MPa)
            fy: Fluencia del refuerzo longitudinal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            rho_h: Cuantía horizontal
            sigma_max: Esfuerzo máximo para elementos de borde (MPa)
            Mpr_top: Momento probable superior (tonf-m)
            Mpr_bottom: Momento probable inferior (tonf-m)
            has_single_curtain: Si tiene cortina simple
            use_capacity_design: Si usar diseño por capacidad
            Omega_o: Factor de sobrerresistencia
            lambda_factor: Factor para concreto liviano
            As_boundary_left: Área de acero en extremo izquierdo (mm2), para §18.10.2.4
            As_boundary_right: Área de acero en extremo derecho (mm2), para §18.10.2.4
            Mu: Momento último en sección crítica (tonf-m), para §18.10.2.4
            adjacent_segments_capacity: Capacidad de transferencia de segmentos
                                       adyacentes (tonf), para §18.10.8.2

        Returns:
            WallPierDesignResult con diseño completo
        """
        warnings = []

        # Clasificar el pilar
        classification = self.classify_wall_pier(hw, lw, bw)

        # Calcular cortante de diseño
        # Nota: lu = hw para pilares de muro
        # Si use_capacity_design=False, no pasar Mpr para desactivar diseño por capacidad
        shear_design = self.calculate_design_shear(
            Vu=Vu,
            lu=hw,
            Mpr_top=Mpr_top if use_capacity_design else 0,
            Mpr_bottom=Mpr_bottom if use_capacity_design else 0,
            Omega_o=Omega_o
        )

        # Verificar resistencia al cortante
        Ve = shear_design.Ve
        shear_result = self.verify_shear_strength(
            Ve, lw, bw, fc, rho_h, fyt, hw
        )

        # Actualizar shear_design con resultados
        shear_design.phi_Vn = shear_result.phi_Vn
        shear_design.dcr = shear_result.dcr
        shear_design.is_ok = shear_result.is_ok

        if not shear_design.is_ok:
            warnings.append(
                f"DCR cortante = {shear_design.dcr:.2f} > 1.0: "
                "Aumentar refuerzo horizontal o espesor"
            )

        # Calcular requisitos de refuerzo transversal
        transverse = self.calculate_transverse_requirements(
            classification, has_single_curtain, fc, fyt
        )

        # Verificar elementos de borde (si aplica)
        boundary_check = None
        if classification.design_method in [DesignMethod.ALTERNATIVE,
                                            DesignMethod.SPECIAL_COLUMN]:
            if sigma_max > 0:
                boundary_check = self.check_boundary_elements(sigma_max, fc)

                if boundary_check.requires_boundary:
                    warnings.append(
                        f"Se requieren elementos de borde: sigma={sigma_max:.1f} MPa "
                        f">= 0.2*f'c={boundary_check.sigma_limit:.1f} MPa"
                    )

        # Advertencias adicionales
        if classification.requires_column_details:
            warnings.append(
                f"Pilar con lw/bw={classification.lw_bw:.1f}: "
                "Verificar requisitos de columna especial (18.7)"
            )

        # Verificar espesor mínimo para columnas sísmicas (18.7.2.1)
        if not classification.column_min_thickness_ok:
            warnings.append(
                f"Espesor {bw:.0f}mm < 300mm mínimo para columna sísmica "
                "(ACI 318-25 §18.7.2.1) - Aumentar espesor"
            )

        if classification.alternative_permitted:
            warnings.append(
                "Método alternativo permitido (18.10.8.1) - "
                "verificar (a)-(f)"
            )

        # Verificar zonas de extremo §18.10.2.4 (si hw/lw >= 2.0)
        boundary_zone_check = None
        hw_lw = hw / lw if lw > 0 else 0
        if hw_lw >= 2.0 and (As_boundary_left > 0 or As_boundary_right > 0):
            boundary_zone_check = check_boundary_zone_reinforcement(
                hw=hw,
                lw=lw,
                bw=bw,
                fc=fc,
                fy=fy,
                As_left=As_boundary_left,
                As_right=As_boundary_right,
                Mu=Mu,
                Vu=Vu
            )
            if not boundary_zone_check.is_ok:
                warnings.extend(boundary_zone_check.warnings)

        # Verificar requisitos de pilar en borde §18.10.8.2 (si se provee capacidad)
        edge_pier_check = None
        if adjacent_segments_capacity is not None:
            Ve = shear_design.Ve
            edge_pier_check = self.check_edge_pier_requirements(
                pier_Ve=Ve,
                adjacent_segments_capacity=adjacent_segments_capacity
            )
            if not edge_pier_check.transfer_ok:
                warnings.append(
                    f"Transferencia de cortante insuficiente: capacidad={edge_pier_check.adjacent_capacity:.1f} tonf "
                    f"< Ve={edge_pier_check.pier_Ve:.1f} tonf (§18.10.8.2)"
                )

        return WallPierDesignResult(
            classification=classification,
            shear_design=shear_design,
            transverse=transverse,
            boundary_check=boundary_check,
            boundary_zone_check=boundary_zone_check,
            edge_pier_check=edge_pier_check,
            warnings=warnings,
            aci_reference="ACI 318-25 18.10.8"
        )

    # =========================================================================
    # VERIFICACIÓN DESDE PIER
    # =========================================================================

    def verify_from_pier(
        self,
        pier: 'Pier',
        Vu: float = 0,
        sigma_max: float = 0,
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        Mu: float = 0,
        adjacent_segments_capacity: Optional[List[float]] = None
    ) -> WallPierDesignResult:
        """
        Verifica un Pier como pilar de muro.

        Args:
            pier: Entidad Pier con geometría y armadura
            Vu: Cortante del análisis (tonf)
            sigma_max: Esfuerzo máximo (MPa)
            Mpr_top: Momento probable superior (tonf-m)
            Mpr_bottom: Momento probable inferior (tonf-m)
            Mu: Momento último en sección crítica (tonf-m), para §18.10.2.4
            adjacent_segments_capacity: Capacidad de transferencia de segmentos
                                       adyacentes (tonf), para §18.10.8.2

        Returns:
            WallPierDesignResult
        """
        return self.design_wall_pier(
            hw=pier.height,
            lw=pier.width,
            bw=pier.thickness,
            Vu=Vu,
            fc=pier.fc,
            fy=pier.fy,
            fyt=pier.fy,  # Asumir mismo fy
            rho_h=pier.rho_horizontal,
            sigma_max=sigma_max,
            Mpr_top=Mpr_top,
            Mpr_bottom=Mpr_bottom,
            has_single_curtain=pier.n_meshes == 1,
            As_boundary_left=pier.As_boundary_left,
            As_boundary_right=pier.As_boundary_right,
            Mu=Mu,
            adjacent_segments_capacity=adjacent_segments_capacity
        )
