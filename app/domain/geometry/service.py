# app/domain/geometry/service.py
"""
Servicio unificado de verificación de geometría ACI 318-25.

Centraliza todos los checks de dimensiones mínimas para:
- Columnas especiales (§18.7.2)
- Vigas especiales (§18.6.2)
- Elementos de borde (§18.10.6.4)

Este servicio puede ser usado por ElementOrchestrator para validar
geometría ANTES de delegar a servicios específicos.
"""
from ..constants.geometry import (
    COLUMN_MIN_DIMENSION_MM,
    COLUMN_MIN_ASPECT_RATIO,
    BEAM_MIN_WIDTH_MM,
    BEAM_MIN_WIDTH_RATIO,
    BE_MIN_WIDTH_SPECIAL_MM,
    BE_C_LW_THRESHOLD,
    BE_WIDTH_TO_HU_RATIO,
)
from .results import GeometryCheckResult


class GeometryChecksService:
    """
    Servicio unificado de verificación de geometría ACI 318-25.

    Proporciona métodos para verificar límites dimensionales de:
    - Columnas sísmicas especiales
    - Vigas sísmicas especiales
    - Elementos de borde en muros

    Todos los métodos retornan GeometryCheckResult con:
    - is_ok: Si pasa todas las verificaciones
    - warnings: Lista de advertencias para UI
    - checks: Dict con cada verificación individual
    - values: Dict con valores calculados
    - aci_reference: Sección ACI aplicable
    """

    def check_column(self, b: float, h: float) -> GeometryCheckResult:
        """
        Verifica límites dimensionales para columnas especiales §18.7.2.

        §18.7.2.1 requiere para columnas de pórticos especiales:
        (a) Dimensión mínima de la sección transversal >= 300mm (12")
        (b) Relación de aspecto b/h >= 0.4

        Args:
            b: Dimensión menor de la sección (mm)
            h: Dimensión mayor de la sección (mm)

        Returns:
            GeometryCheckResult con resultado de verificación
        """
        # Asegurar que b <= h
        if b > h:
            b, h = h, b

        # Verificar dimensión mínima (a)
        min_dim_ok = b >= COLUMN_MIN_DIMENSION_MM

        # Verificar relación de aspecto (b)
        aspect_ratio = b / h if h > 0 else 0
        aspect_ok = aspect_ratio >= COLUMN_MIN_ASPECT_RATIO

        # Construir resultado
        result = GeometryCheckResult(
            is_ok=min_dim_ok and aspect_ok,
            warnings=[],
            checks={
                'min_dimension': min_dim_ok,
                'aspect_ratio': aspect_ok
            },
            values={
                'b': b,
                'h': h,
                'min_dimension': b,
                'min_dimension_required': COLUMN_MIN_DIMENSION_MM,
                'aspect_ratio': aspect_ratio,
                'aspect_ratio_required': COLUMN_MIN_ASPECT_RATIO
            },
            aci_reference="ACI 318-25 §18.7.2"
        )

        # Agregar warnings
        if not min_dim_ok:
            result.add_warning(
                f"Dimensión {b:.0f}mm < {COLUMN_MIN_DIMENSION_MM:.0f}mm "
                f"mínimo (ACI §18.7.2.1(a))"
            )
        if not aspect_ok:
            result.add_warning(
                f"Relación b/h={aspect_ratio:.2f} < {COLUMN_MIN_ASPECT_RATIO} "
                f"mínimo (ACI §18.7.2.1(b))"
            )

        return result

    def check_beam(
        self, bw: float, h: float, d: float = None, ln: float = None
    ) -> GeometryCheckResult:
        """
        Verifica límites dimensionales para vigas especiales §18.6.2.

        §18.6.2.1 requiere para vigas de pórticos especiales:
        (a) bw >= 0.3h
        (b) bw >= 254mm (10")
        (c) bw no debe exceder ancho del elemento de apoyo + 0.75h

        Args:
            bw: Ancho del alma de la viga (mm)
            h: Altura total de la viga (mm)
            d: Peralte efectivo (mm), opcional
            ln: Luz libre (mm), opcional

        Returns:
            GeometryCheckResult con resultado de verificación
        """
        # Verificar ancho mínimo absoluto (b)
        min_width_abs_ok = bw >= BEAM_MIN_WIDTH_MM

        # Verificar ancho mínimo relativo (a)
        min_width_ratio = bw / h if h > 0 else 0
        min_width_rel_ok = min_width_ratio >= BEAM_MIN_WIDTH_RATIO

        # Calcular ancho mínimo requerido
        width_from_ratio = BEAM_MIN_WIDTH_RATIO * h
        width_required = max(BEAM_MIN_WIDTH_MM, width_from_ratio)

        # Construir resultado
        result = GeometryCheckResult(
            is_ok=min_width_abs_ok and min_width_rel_ok,
            warnings=[],
            checks={
                'min_width_absolute': min_width_abs_ok,
                'min_width_ratio': min_width_rel_ok
            },
            values={
                'bw': bw,
                'h': h,
                'width_ratio': min_width_ratio,
                'width_required': width_required
            },
            aci_reference="ACI 318-25 §18.6.2"
        )

        # Agregar valores opcionales si se proporcionan
        if d is not None:
            result.values['d'] = d
        if ln is not None:
            result.values['ln'] = ln

        # Agregar warnings
        if not min_width_abs_ok:
            result.add_warning(
                f"Ancho {bw:.0f}mm < {BEAM_MIN_WIDTH_MM:.0f}mm "
                f"mínimo (ACI §18.6.2.1(b))"
            )
        if not min_width_rel_ok:
            result.add_warning(
                f"Ancho/altura={min_width_ratio:.2f} < {BEAM_MIN_WIDTH_RATIO} "
                f"mínimo (ACI §18.6.2.1(a))"
            )

        return result

    def check_boundary_element(
        self, c: float, lw: float, hu: float, tw: float
    ) -> GeometryCheckResult:
        """
        Verifica dimensiones de elemento de borde §18.10.6.4.

        §18.10.6.4 requiere:
        (b) b >= hu/16
        (c) Para c/lw >= 3/8, b >= 305mm (12")

        Args:
            c: Profundidad del eje neutro (mm)
            lw: Longitud del muro (mm)
            hu: Altura de piso (mm)
            tw: Espesor del muro (mm)

        Returns:
            GeometryCheckResult con resultado de verificación
        """
        # Calcular c/lw
        c_lw = c / lw if lw > 0 else 0

        # Calcular ancho mínimo requerido
        width_from_hu = hu * BE_WIDTH_TO_HU_RATIO  # hu/16

        # Si c/lw >= 3/8, también aplica 305mm mínimo
        if c_lw >= BE_C_LW_THRESHOLD:
            width_required = max(width_from_hu, BE_MIN_WIDTH_SPECIAL_MM)
        else:
            width_required = width_from_hu

        # Verificar ancho
        width_ok = tw >= width_required

        # Construir resultado
        result = GeometryCheckResult(
            is_ok=width_ok,
            warnings=[],
            checks={
                'width': width_ok,
                'c_lw_threshold': c_lw >= BE_C_LW_THRESHOLD
            },
            values={
                'c': c,
                'lw': lw,
                'hu': hu,
                'tw': tw,
                'c_lw': c_lw,
                'width_required': width_required,
                'width_from_hu': width_from_hu
            },
            aci_reference="ACI 318-25 §18.10.6.4"
        )

        # Agregar warnings
        if not width_ok:
            if c_lw >= BE_C_LW_THRESHOLD:
                result.add_warning(
                    f"Espesor {tw:.0f}mm < {width_required:.0f}mm requerido "
                    f"(c/lw={c_lw:.2f} >= {BE_C_LW_THRESHOLD}, ACI §18.10.6.4)"
                )
            else:
                result.add_warning(
                    f"Espesor {tw:.0f}mm < {width_required:.0f}mm requerido "
                    f"(hu/16, ACI §18.10.6.4(b))"
                )

        return result

    def check_pier_as_column(self, lw: float, tw: float) -> GeometryCheckResult:
        """
        Verifica límites dimensionales para pier clasificado como columna.

        Cuando lw/tw < 4, el pier se clasifica como columna y debe cumplir
        con los requisitos de columnas especiales §18.7.2.

        Args:
            lw: Longitud del pier (dimensión mayor, mm)
            tw: Espesor del pier (dimensión menor, mm)

        Returns:
            GeometryCheckResult con resultado de verificación §18.7.2
        """
        # Para piers, tw es la dimensión menor y lw es la mayor
        return self.check_column(b=tw, h=lw)


# Instancia singleton para uso directo
_geometry_service = None


def get_geometry_service() -> GeometryChecksService:
    """Obtiene la instancia singleton del servicio de geometría."""
    global _geometry_service
    if _geometry_service is None:
        _geometry_service = GeometryChecksService()
    return _geometry_service
