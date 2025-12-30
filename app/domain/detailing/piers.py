# app/structural/domain/wall_piers.py
"""
Verificacion de pilares de muro (wall piers) segun ACI 318-25 Seccion 18.10.8.

Implementa:
- Clasificacion de pilares por geometria (lw/bw)
- Requisitos de columna especial vs alternativo
- Refuerzo transversal
- Cortante de diseno

Referencias ACI 318-25:
- 18.10.8.1: Requisitos generales
- 18.10.8.2: Pilares en borde de muro
- Tabla R18.10.1: Clasificacion por hw/lw y lw/bw

Definicion:
Un "pilar de muro" (wall pier) es un segmento vertical estrecho de muro,
tipicamente creado por aberturas como puertas o ventanas.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .entities.pier import Pier


class WallPierCategory(Enum):
    """Categoria de pilar de muro segun Tabla R18.10.1."""
    WALL = "wall"          # Disenar como muro (18.10)
    COLUMN = "column"      # Disenar como columna especial (18.7)
    ALTERNATIVE = "alternative"  # Metodo alternativo (18.10.8.1)


class DesignMethod(Enum):
    """Metodo de diseno para el pilar."""
    SPECIAL_COLUMN = "special_column"      # Segun 18.7
    ALTERNATIVE = "alternative"            # Segun 18.10.8.1 alternativo
    WALL = "wall"                          # Segun 18.10 (muro)


@dataclass
class WallPierClassification:
    """Clasificacion del pilar de muro."""
    hw: float               # Altura del segmento (mm)
    lw: float               # Longitud del segmento (mm)
    bw: float               # Espesor del segmento (mm)
    hw_lw: float            # Relacion altura/longitud
    lw_bw: float            # Relacion longitud/espesor
    category: WallPierCategory
    design_method: DesignMethod
    requires_column_details: bool
    alternative_permitted: bool
    aci_reference: str


@dataclass
class WallPierShearDesign:
    """Diseno por cortante del pilar de muro."""
    Vu: float               # Cortante ultimo (tonf)
    Ve: float               # Cortante de diseno (tonf)
    Omega_o: float          # Factor de sobrerresistencia
    use_capacity_design: bool
    phi_Vn: float           # Capacidad de corte (tonf)
    dcr: float              # Demand/Capacity ratio
    is_ok: bool
    aci_reference: str


@dataclass
class WallPierTransverseReinforcement:
    """Refuerzo transversal para pilar de muro."""
    # Requisitos de estribos
    requires_closed_hoops: bool
    hook_type: str          # "180°" para cortina simple
    spacing_max: float      # Espaciamiento maximo (mm)

    # Extension del refuerzo
    extension_above: float  # Extension arriba de altura libre (mm)
    extension_below: float  # Extension abajo de altura libre (mm)

    # Cuantia requerida
    Ash_sbc_required: float  # Para metodo alternativo

    aci_reference: str


@dataclass
class WallPierBoundaryCheck:
    """Verificacion de elementos de borde para pilar."""
    requires_boundary: bool
    method_used: str        # "stress" segun 18.10.6.3
    sigma_max: float        # Esfuerzo maximo (MPa)
    sigma_limit: float      # Limite 0.2*f'c (MPa)
    aci_reference: str


@dataclass
class WallPierDesignResult:
    """Resultado completo del diseno del pilar de muro."""
    classification: WallPierClassification
    shear_design: WallPierShearDesign
    transverse: WallPierTransverseReinforcement
    boundary_check: Optional[WallPierBoundaryCheck]
    warnings: List[str]
    aci_reference: str


class WallPierService:
    """
    Servicio de verificacion de pilares de muro segun ACI 318-25.

    Proporciona clasificacion, diseno por cortante, y requisitos
    de detallado para pilares de muro (segmentos verticales estrechos).

    Unidades:
    - Longitudes: mm
    - Esfuerzos: MPa
    - Fuerzas: tonf
    """

    # Constantes
    EXTENSION_MIN_MM = 304.8  # 12" en mm

    # =========================================================================
    # CLASIFICACION DEL PILAR (TABLA R18.10.1)
    # =========================================================================

    def classify_wall_pier(
        self,
        hw: float,
        lw: float,
        bw: float
    ) -> WallPierClassification:
        """
        Clasifica el pilar de muro segun Tabla R18.10.1.

        Tabla R18.10.1 - Provisiones de Diseno por Tipo de Segmento:

        | hw/lw | lw/bw <= 2.5 | 2.5 < lw/bw <= 6.0 | lw/bw > 6.0 |
        |-------|--------------|--------------------|-----------  |
        | < 2.0 | Muro         | Muro               | Muro        |
        | >= 2.0| Pilar(col)   | Pilar(col o alt)   | Muro        |

        Args:
            hw: Altura del segmento (mm)
            lw: Longitud del segmento (mm)
            bw: Espesor del segmento (mm)

        Returns:
            WallPierClassification con categoria y metodo de diseno
        """
        if lw <= 0 or bw <= 0:
            return WallPierClassification(
                hw=hw, lw=lw, bw=bw,
                hw_lw=0, lw_bw=0,
                category=WallPierCategory.WALL,
                design_method=DesignMethod.WALL,
                requires_column_details=False,
                alternative_permitted=False,
                aci_reference="ACI 318-25 Tabla R18.10.1"
            )

        hw_lw = hw / lw
        lw_bw = lw / bw

        # Determinar categoria y metodo
        if hw_lw < 2.0:
            # Siempre disenar como muro
            category = WallPierCategory.WALL
            design_method = DesignMethod.WALL
            requires_column = False
            alternative_ok = False

        elif lw_bw <= 2.5:
            # Pilar esbelto - requisitos de columna
            category = WallPierCategory.COLUMN
            design_method = DesignMethod.SPECIAL_COLUMN
            requires_column = True
            alternative_ok = False

        elif lw_bw <= 6.0:
            # Pilar intermedio - columna o alternativo
            category = WallPierCategory.ALTERNATIVE
            design_method = DesignMethod.ALTERNATIVE
            requires_column = True
            alternative_ok = True

        else:
            # lw/bw > 6.0 - disenar como muro
            category = WallPierCategory.WALL
            design_method = DesignMethod.WALL
            requires_column = False
            alternative_ok = False

        return WallPierClassification(
            hw=hw,
            lw=lw,
            bw=bw,
            hw_lw=round(hw_lw, 2),
            lw_bw=round(lw_bw, 2),
            category=category,
            design_method=design_method,
            requires_column_details=requires_column,
            alternative_permitted=alternative_ok,
            aci_reference="ACI 318-25 Tabla R18.10.1, 18.10.8.1"
        )

    # =========================================================================
    # CORTANTE DE DISENO (18.10.8.1(a))
    # =========================================================================

    def calculate_design_shear(
        self,
        Vu: float,
        use_capacity_design: bool = True,
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        lu: float = 0,
        Omega_o: float = 3.0
    ) -> WallPierShearDesign:
        """
        Calcula el cortante de diseno para el pilar.

        Segun 18.10.8.1(a):
        - Cortante segun 18.7.6.1 (diseno por capacidad), O
        - Ve <= Omega_o * Vu del analisis

        Para 18.7.6.1:
        Ve = (Mpr_top + Mpr_bottom) / lu

        Args:
            Vu: Cortante del analisis (tonf)
            use_capacity_design: Si usar diseno por capacidad
            Mpr_top: Momento probable en extremo superior (tonf-m)
            Mpr_bottom: Momento probable en extremo inferior (tonf-m)
            lu: Altura libre del pilar (mm)
            Omega_o: Factor de sobrerresistencia del codigo general

        Returns:
            WallPierShearDesign con cortante de diseno
        """
        if use_capacity_design and lu > 0:
            # Diseno por capacidad: Ve = (Mpr_top + Mpr_bottom) / lu
            # Convertir lu a m para unidades consistentes
            lu_m = lu / 1000
            Ve_capacity = (Mpr_top + Mpr_bottom) / lu_m
            Ve = min(Ve_capacity, Omega_o * Vu)
        else:
            # Alternativa: Ve = Omega_o * Vu
            Ve = Omega_o * Vu

        return WallPierShearDesign(
            Vu=Vu,
            Ve=round(Ve, 2),
            Omega_o=Omega_o,
            use_capacity_design=use_capacity_design,
            phi_Vn=0,  # Se llena despues
            dcr=0,
            is_ok=True,
            aci_reference="ACI 318-25 18.10.8.1(a), 18.7.6.1"
        )

    def verify_shear_strength(
        self,
        Ve: float,
        lw: float,
        bw: float,
        fc: float,
        rho_h: float,
        fyt: float,
        lambda_factor: float = 1.0
    ) -> WallPierShearDesign:
        """
        Verifica la resistencia al cortante del pilar.

        Usa formulas de 18.10.4 para Vn.

        Args:
            Ve: Cortante de diseno (tonf)
            lw: Longitud del pilar (mm)
            bw: Espesor del pilar (mm)
            fc: f'c del hormigon (MPa)
            rho_h: Cuantia horizontal
            fyt: Fluencia del refuerzo horizontal (MPa)
            lambda_factor: Factor para concreto liviano

        Returns:
            WallPierShearDesign actualizado con capacidad
        """
        # Calcular Vn segun 18.10.4.1
        # Vn = (alpha_c * lambda * sqrt(f'c) + rho_t * fyt) * Acv
        Acv = lw * bw

        # Para pilar, usar alpha_c conservador
        alpha_c = 0.17  # Conservador

        Vn_N = (alpha_c * lambda_factor * math.sqrt(fc) + rho_h * fyt) * Acv

        # Limites de 18.10.4.4
        # Vn <= 0.83 * sqrt(f'c) * Acv para segmento individual
        Vn_max_N = 0.83 * math.sqrt(fc) * Acv
        Vn_N = min(Vn_N, Vn_max_N)

        # Convertir a tonf
        N_TO_TONF = 9806.65
        Vn = Vn_N / N_TO_TONF
        phi_Vn = 0.75 * Vn

        dcr = Ve / phi_Vn if phi_Vn > 0 else float('inf')
        is_ok = dcr <= 1.0

        return WallPierShearDesign(
            Vu=0,
            Ve=Ve,
            Omega_o=0,
            use_capacity_design=False,
            phi_Vn=round(phi_Vn, 2),
            dcr=round(dcr, 3),
            is_ok=is_ok,
            aci_reference="ACI 318-25 18.10.4, 18.10.8.1(b)"
        )

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
        """
        Calcula requisitos de refuerzo transversal para pilar.

        Segun 18.10.8.1 alternativo:
        (c) Estribos cerrados (ganchos 180° si cortina simple)
        (d) Espaciamiento vertical <= 6"
        (e) Extension >= 12" arriba y abajo de altura libre
        (f) Elementos de borde si se requieren por 18.10.6.3

        Args:
            classification: Clasificacion del pilar
            has_single_curtain: Si tiene cortina simple
            fc: f'c del hormigon (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)

        Returns:
            WallPierTransverseReinforcement con requisitos
        """
        if classification.design_method == DesignMethod.WALL:
            # Requisitos de muro - espaciamiento maximo 18"
            return WallPierTransverseReinforcement(
                requires_closed_hoops=False,
                hook_type="90°",
                spacing_max=457.2,  # 18"
                extension_above=0,
                extension_below=0,
                Ash_sbc_required=0,
                aci_reference="ACI 318-25 18.10.2"
            )

        # Metodo alternativo o columna
        if has_single_curtain:
            hook_type = "180°"
        else:
            hook_type = "135° o 180°"

        # Espaciamiento maximo (18.10.8.1(d))
        spacing_max = 152.4  # 6"

        # Extension (18.10.8.1(e))
        extension = self.EXTENSION_MIN_MM  # 12"

        # Ash/(s*bc) para metodo alternativo
        # Usar requisitos basicos de confinamiento
        Ash_sbc = 0.09 * (fc / fyt)

        return WallPierTransverseReinforcement(
            requires_closed_hoops=True,
            hook_type=hook_type,
            spacing_max=round(spacing_max, 1),
            extension_above=extension,
            extension_below=extension,
            Ash_sbc_required=round(Ash_sbc, 5),
            aci_reference="ACI 318-25 18.10.8.1(c)-(e)"
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

        Segun 18.10.8.1(f):
        Si se requiere por 18.10.6.3 (metodo de esfuerzos)

        Args:
            sigma_max: Esfuerzo maximo de compresion (MPa)
            fc: f'c del hormigon (MPa)

        Returns:
            WallPierBoundaryCheck con resultado
        """
        sigma_limit = 0.2 * fc
        requires_boundary = sigma_max >= sigma_limit

        return WallPierBoundaryCheck(
            requires_boundary=requires_boundary,
            method_used="stress (18.10.6.3)",
            sigma_max=sigma_max,
            sigma_limit=sigma_limit,
            aci_reference="ACI 318-25 18.10.8.1(f), 18.10.6.3"
        )

    # =========================================================================
    # PILARES EN BORDE DE MURO (18.10.8.2)
    # =========================================================================

    def check_edge_pier_requirements(
        self,
        pier_Ve: float,
        adjacent_segments_capacity: List[float]
    ) -> dict:
        """
        Verifica requisitos para pilares en borde de muro.

        Segun 18.10.8.2:
        - Proporcionar refuerzo horizontal en segmentos adyacentes
        - Disenar para transferir cortante del pilar

        Args:
            pier_Ve: Cortante del pilar (tonf)
            adjacent_segments_capacity: Capacidad de transferencia de
                                       segmentos adyacentes (tonf)

        Returns:
            Dict con verificacion
        """
        total_capacity = sum(adjacent_segments_capacity)
        is_ok = total_capacity >= pier_Ve

        return {
            "pier_Ve": pier_Ve,
            "adjacent_capacity": total_capacity,
            "transfer_ok": is_ok,
            "required_transfer": pier_Ve,
            "aci_reference": "ACI 318-25 18.10.8.2"
        }

    # =========================================================================
    # DISENO COMPLETO
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
        lambda_factor: float = 1.0
    ) -> WallPierDesignResult:
        """
        Realiza diseno completo del pilar de muro.

        Args:
            hw: Altura del segmento (mm)
            lw: Longitud del segmento (mm)
            bw: Espesor del segmento (mm)
            Vu: Cortante del analisis (tonf)
            fc: f'c del hormigon (MPa)
            fy: Fluencia del refuerzo longitudinal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            rho_h: Cuantia horizontal
            sigma_max: Esfuerzo maximo para elementos de borde (MPa)
            Mpr_top: Momento probable superior (tonf-m)
            Mpr_bottom: Momento probable inferior (tonf-m)
            has_single_curtain: Si tiene cortina simple
            use_capacity_design: Si usar diseno por capacidad
            Omega_o: Factor de sobrerresistencia
            lambda_factor: Factor para concreto liviano

        Returns:
            WallPierDesignResult con diseno completo
        """
        warnings = []

        # Clasificar el pilar
        classification = self.classify_wall_pier(hw, lw, bw)

        # Calcular cortante de diseno
        shear_design = self.calculate_design_shear(
            Vu, use_capacity_design, Mpr_top, Mpr_bottom, hw, Omega_o
        )

        # Verificar resistencia al cortante
        Ve = shear_design.Ve
        shear_result = self.verify_shear_strength(
            Ve, lw, bw, fc, rho_h, fyt, lambda_factor
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

        if classification.alternative_permitted:
            warnings.append(
                "Metodo alternativo permitido (18.10.8.1) - "
                "verificar (a)-(f)"
            )

        return WallPierDesignResult(
            classification=classification,
            shear_design=shear_design,
            transverse=transverse,
            boundary_check=boundary_check,
            warnings=warnings,
            aci_reference="ACI 318-25 18.10.8"
        )

    # =========================================================================
    # VERIFICACION DESDE PIER
    # =========================================================================

    def verify_from_pier(
        self,
        pier: 'Pier',
        Vu: float = 0,
        sigma_max: float = 0,
        Mpr_top: float = 0,
        Mpr_bottom: float = 0
    ) -> WallPierDesignResult:
        """
        Verifica un Pier como pilar de muro.

        Args:
            pier: Entidad Pier con geometria y armadura
            Vu: Cortante del analisis (tonf)
            sigma_max: Esfuerzo maximo (MPa)
            Mpr_top: Momento probable superior (tonf-m)
            Mpr_bottom: Momento probable inferior (tonf-m)

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
            has_single_curtain=not pier.double_layer
        )
