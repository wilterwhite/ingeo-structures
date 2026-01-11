# app/domain/chapter18/columns/service.py
"""
Servicio de verificación para columnas sísmicas ACI 318-25.

Orquesta las verificaciones según la categoría sísmica:
- SPECIAL: §18.7 (todos los checks)
- INTERMEDIATE: §18.4.3 (checks reducidos)
- ORDINARY: §18.3.3 (solo cortante)
- NON_SFRS: §18.14.3 (deriva compatible)

Referencias:
- ACI 318-25 §18.3.3: Columnas de pórticos ordinarios
- ACI 318-25 §18.4.3: Columnas de pórticos intermedios
- ACI 318-25 §18.7: Columnas de pórticos especiales
"""
from typing import Optional, List

from ...constants.units import TONF_TO_N
from ..common import SeismicCategory
from ..seismic_detailing_service import SeismicDetailingService
from .results import (
    SeismicColumnResult,
    SeismicColumnShearResult,
    DimensionalLimitsResult,
    StrongColumnResult,
    LongitudinalReinforcementResult,
    TransverseReinforcementResult,
)
from .dimensional import check_dimensional_limits
from .flexural_strength import check_strong_column_weak_beam
from .longitudinal import check_longitudinal_reinforcement
from .transverse import check_transverse_reinforcement
from .shear import SeismicColumnShearService


class SeismicColumnService:
    """
    Servicio principal para verificación de columnas sísmicas.

    Realiza todas las verificaciones aplicables según la categoría sísmica.
    Por defecto asume categoría SPECIAL (la más restrictiva).

    Example:
        service = SeismicColumnService()

        # Verificación especial (default)
        result = service.verify_column(...)

        # Verificación intermedia
        result = service.verify_column(..., category=SeismicCategory.INTERMEDIATE)
    """

    def __init__(self):
        """Inicializa el servicio con dependencias."""
        self._shear_service = SeismicColumnShearService()
        self._detailing = SeismicDetailingService()

    def verify_column(
        self,
        # Geometría
        b: float,
        h: float,
        lu: float,
        cover: float,
        Ag: float,
        # Materiales
        fc: float,
        fy: float,
        fyt: float,
        # Refuerzo longitudinal
        Ast: float,
        n_bars: int,
        db_long: float,
        # Refuerzo transversal
        s_transverse: float,
        Ash: float,
        hx: float,
        # Fuerzas (para cortante)
        Vu_V2: float = 0,
        Vu_V3: float = 0,
        Pu: float = 0,
        # Para diseño por capacidad
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        # Columna fuerte-viga débil (solo SPECIAL)
        Mnc_top_V2: float = 0,
        Mnc_bottom_V2: float = 0,
        Mnb_left_V2: float = 0,
        Mnb_right_V2: float = 0,
        Mnc_top_V3: float = 0,
        Mnc_bottom_V3: float = 0,
        Mnb_left_V3: float = 0,
        Mnb_right_V3: float = 0,
        # Opciones
        category: SeismicCategory = SeismicCategory.SPECIAL,
        steel_grade: int = 60,
        is_circular: bool = False,
        lambda_factor: float = 1.0,
    ) -> SeismicColumnResult:
        """
        Verifica una columna según los requisitos sísmicos aplicables.

        Args:
            b: Dimensión menor de la sección (mm)
            h: Dimensión mayor de la sección (mm)
            lu: Altura libre de la columna (mm)
            cover: Recubrimiento al centro de estribos (mm)
            Ag: Área bruta de la sección (mm²)
            fc: f'c del concreto (MPa)
            fy: Fluencia del refuerzo longitudinal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            Ast: Área total de refuerzo longitudinal (mm²)
            n_bars: Número de barras longitudinales
            db_long: Diámetro de barra longitudinal (mm)
            s_transverse: Espaciamiento de refuerzo transversal (mm)
            Ash: Área de refuerzo transversal en una dirección (mm²)
            hx: Espaciamiento entre barras soportadas (mm)
            Vu_V2: Cortante último en dirección V2 (tonf)
            Vu_V3: Cortante último en dirección V3 (tonf)
            Pu: Carga axial factorizada (tonf, positivo = compresión)
            Mpr_top: Momento probable superior para Ve (tonf-m)
            Mpr_bottom: Momento probable inferior para Ve (tonf-m)
            Mnc_top_V2: Mn columna superior dir V2 (tonf-m)
            Mnc_bottom_V2: Mn columna inferior dir V2 (tonf-m)
            Mnb_left_V2: Mn viga izquierda dir V2 (tonf-m)
            Mnb_right_V2: Mn viga derecha dir V2 (tonf-m)
            Mnc_top_V3: Mn columna superior dir V3 (tonf-m)
            Mnc_bottom_V3: Mn columna inferior dir V3 (tonf-m)
            Mnb_left_V3: Mn viga izquierda dir V3 (tonf-m)
            Mnb_right_V3: Mn viga derecha dir V3 (tonf-m)
            category: Categoría sísmica (default SPECIAL)
            steel_grade: Grado del acero (60 u 80)
            is_circular: True si es columna circular
            lambda_factor: Factor para concreto liviano

        Returns:
            SeismicColumnResult con todas las verificaciones aplicables
        """
        warnings: List[str] = []
        dcr_max = 0
        critical_check = ""

        # Inicializar resultados como None
        dimensional = None
        strong_V2 = None
        strong_V3 = None
        longitudinal = None
        transverse = None
        shear = None

        # Pu en N para cálculos internos
        Pu_N = Pu * TONF_TO_N

        # ==== VERIFICACIONES SEGÚN CATEGORÍA ====

        if category == SeismicCategory.SPECIAL:
            # §18.7.2 - Límites dimensionales
            dimensional = check_dimensional_limits(b, h)
            if not dimensional.is_ok:
                dcr_max = max(dcr_max, 1.5)  # Penalizar
                critical_check = "dimensional_limits"
                warnings.append("No cumple límites dimensionales §18.7.2")

            # §18.7.3.2 - Columna fuerte-viga débil
            if Mnb_left_V2 > 0 or Mnb_right_V2 > 0:
                strong_V2 = check_strong_column_weak_beam(
                    Mnc_top_V2, Mnc_bottom_V2, Mnb_left_V2, Mnb_right_V2, "V2"
                )
                if not strong_V2.is_ok:
                    if 1.2 / strong_V2.ratio > dcr_max:
                        dcr_max = 1.2 / strong_V2.ratio
                        critical_check = "strong_column_V2"
                    warnings.append(f"No cumple columna fuerte-viga débil V2 §18.7.3.2")

            if Mnb_left_V3 > 0 or Mnb_right_V3 > 0:
                strong_V3 = check_strong_column_weak_beam(
                    Mnc_top_V3, Mnc_bottom_V3, Mnb_left_V3, Mnb_right_V3, "V3"
                )
                if not strong_V3.is_ok:
                    if 1.2 / strong_V3.ratio > dcr_max:
                        dcr_max = 1.2 / strong_V3.ratio
                        critical_check = "strong_column_V3"
                    warnings.append(f"No cumple columna fuerte-viga débil V3 §18.7.3.2")

            # §18.7.4 - Refuerzo longitudinal
            longitudinal = check_longitudinal_reinforcement(
                Ast, Ag, n_bars, is_circular
            )
            if not longitudinal.is_ok:
                if longitudinal.rho < longitudinal.rho_min:
                    dcr = longitudinal.rho_min / longitudinal.rho
                elif longitudinal.rho > longitudinal.rho_max:
                    dcr = longitudinal.rho / longitudinal.rho_max
                else:
                    dcr = 1.1
                if dcr > dcr_max:
                    dcr_max = dcr
                    critical_check = "longitudinal"
                warnings.append("No cumple refuerzo longitudinal §18.7.4")

            # §18.7.5 - Refuerzo transversal
            transverse = check_transverse_reinforcement(
                h=h,
                b=b,
                lu=lu,
                cover=cover,
                Ag=Ag,
                fc=fc,
                fyt=fyt,
                Pu=Pu_N,
                s_provided=s_transverse,
                Ash_provided=Ash,
                db_long=db_long,
                hx_provided=hx,
                nl=n_bars,
                steel_grade=steel_grade,
                is_circular=is_circular,
            )
            if not transverse.is_ok:
                warnings.extend(transverse.warnings)
                if transverse.Ash_sbc_required > 0 and transverse.Ash_sbc_provided > 0:
                    dcr = transverse.Ash_sbc_required / transverse.Ash_sbc_provided
                    if dcr > dcr_max:
                        dcr_max = dcr
                        critical_check = "transverse"

        elif category == SeismicCategory.INTERMEDIATE:
            # §18.4.3 - Requisitos intermedios (simplificados)
            # No verifica límites dimensionales ni columna fuerte
            # Solo refuerzo transversal simplificado y cortante

            # Refuerzo transversal con requisitos reducidos
            transverse = check_transverse_reinforcement(
                h=h,
                b=b,
                lu=lu,
                cover=cover,
                Ag=Ag,
                fc=fc,
                fyt=fyt,
                Pu=Pu_N,
                s_provided=s_transverse,
                Ash_provided=Ash,
                db_long=db_long,
                hx_provided=hx,
                nl=n_bars,
                steel_grade=steel_grade,
                is_circular=is_circular,
            )
            if not transverse.is_ok:
                warnings.extend(transverse.warnings)

        # §18.7.6 / §18.4.3.1 / §18.3.3 - Cortante
        # Aplica para todas las categorías
        if Vu_V2 > 0 or Vu_V3 > 0:
            # Calcular profundidades efectivas
            d_V2 = h - cover  # Para cortante en dirección V2
            d_V3 = b - cover  # Para cortante en dirección V3
            Av_V2 = Ash  # Área de estribos perpendiculares a V2
            Av_V3 = Ash  # Área de estribos perpendiculares a V3

            shear = self._shear_service.verify_seismic_column_shear(
                lu=lu,
                Ag=Ag,
                fc=fc,
                bw_V2=b,
                d_V2=d_V2,
                Av_V2=Av_V2,
                bw_V3=h,
                d_V3=d_V3,
                Av_V3=Av_V3,
                fyt=fyt,
                s=s_transverse,
                Vu_V2=Vu_V2,
                Vu_V3=Vu_V3,
                Pu=Pu,
                Mpr_top=Mpr_top if category == SeismicCategory.SPECIAL else 0,
                Mpr_bottom=Mpr_bottom if category == SeismicCategory.SPECIAL else 0,
                lambda_factor=lambda_factor,
            )
            if shear.dcr > dcr_max:
                dcr_max = shear.dcr
                critical_check = "shear"
            if not shear.is_ok:
                warnings.append(f"No cumple cortante {category.column_section}")

        # Determinar resultado global
        is_ok = dcr_max <= 1.0 and len(warnings) == 0

        return SeismicColumnResult(
            category=category,
            dimensional_limits=dimensional,
            strong_column_V2=strong_V2,
            strong_column_V3=strong_V3,
            longitudinal=longitudinal,
            transverse=transverse,
            shear=shear,
            is_ok=is_ok,
            dcr_max=round(dcr_max, 3),
            critical_check=critical_check,
            warnings=warnings,
        )
