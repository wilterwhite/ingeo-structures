# app/domain/chapter18/common/dimensional.py
"""
Verificaciones dimensionales comunes para elementos sísmicos.

Este módulo centraliza las verificaciones de límites dimensionales
que son similares entre columnas, vigas y elementos de borde.

Referencias:
- ACI 318-25 §18.7.2.1: Límites dimensionales para columnas especiales
- ACI 318-25 §18.6.2.1: Límites dimensionales para vigas especiales
- ACI 318-25 §18.10.6.4: Elementos de borde de muros

Uso:
    from app.domain.chapter18.common.dimensional import (
        check_min_dimension,
        check_aspect_ratio,
        check_span_depth_ratio,
    )
"""
from dataclasses import dataclass


@dataclass
class DimensionalCheckResult:
    """Resultado de una verificación dimensional."""
    is_ok: bool
    value: float
    limit: float
    reference: str

    @property
    def ratio(self) -> float:
        """Razón valor/límite (>1 significa que no cumple)."""
        if self.limit <= 0:
            return 0.0
        return self.value / self.limit


def check_min_dimension(
    b_mm: float,
    h_mm: float,
    min_mm: float = 300,
    reference: str = "§18.7.2.1(a)",
) -> DimensionalCheckResult:
    """
    Verifica que la dimensión menor cumpla el mínimo requerido.

    Para columnas especiales: min(b, h) >= 300mm (12")

    Args:
        b_mm: Dimensión menor de la sección (mm)
        h_mm: Dimensión mayor de la sección (mm)
        min_mm: Dimensión mínima requerida (mm, default 300)
        reference: Referencia ACI

    Returns:
        DimensionalCheckResult con is_ok, value, limit, reference
    """
    min_dim = min(b_mm, h_mm)
    return DimensionalCheckResult(
        is_ok=min_dim >= min_mm,
        value=min_dim,
        limit=min_mm,
        reference=reference,
    )


def check_aspect_ratio(
    b_mm: float,
    h_mm: float,
    max_ratio: float = 2.5,
    reference: str = "§18.7.2.1(b)",
) -> DimensionalCheckResult:
    """
    Verifica que la relación de aspecto no exceda el límite.

    Para columnas especiales: h/b <= 2.5 (o b/h si b > h)

    Args:
        b_mm: Dimensión menor de la sección (mm)
        h_mm: Dimensión mayor de la sección (mm)
        max_ratio: Relación máxima permitida (default 2.5)
        reference: Referencia ACI

    Returns:
        DimensionalCheckResult con is_ok, value, limit, reference
    """
    min_dim = min(b_mm, h_mm)
    max_dim = max(b_mm, h_mm)
    ratio = max_dim / min_dim if min_dim > 0 else float('inf')

    return DimensionalCheckResult(
        is_ok=ratio <= max_ratio,
        value=round(ratio, 2),
        limit=max_ratio,
        reference=reference,
    )


def check_span_depth_ratio(
    ln_mm: float,
    d_mm: float,
    min_ratio: float = 4.0,
    reference: str = "§18.6.2.1(a)",
) -> DimensionalCheckResult:
    """
    Verifica que la relación luz/peralte cumpla el mínimo.

    Para vigas especiales: ln/d >= 4

    Args:
        ln_mm: Luz libre de la viga (mm)
        d_mm: Profundidad efectiva (mm)
        min_ratio: Relación mínima requerida (default 4.0)
        reference: Referencia ACI

    Returns:
        DimensionalCheckResult con is_ok, value, limit, reference
    """
    ratio = ln_mm / d_mm if d_mm > 0 else 0

    return DimensionalCheckResult(
        is_ok=ratio >= min_ratio,
        value=round(ratio, 2),
        limit=min_ratio,
        reference=reference,
    )


def check_min_width(
    bw_mm: float,
    h_mm: float,
    min_mm: float = 250,
    h_factor: float = 0.3,
    reference: str = "§18.6.2.1(b)",
) -> DimensionalCheckResult:
    """
    Verifica que el ancho del alma cumpla los requisitos.

    Para vigas especiales: bw >= max(0.3h, 250mm)

    Args:
        bw_mm: Ancho del alma (mm)
        h_mm: Altura total de la viga (mm)
        min_mm: Ancho mínimo absoluto (mm, default 250)
        h_factor: Factor de altura (default 0.3)
        reference: Referencia ACI

    Returns:
        DimensionalCheckResult con is_ok, value, limit, reference
    """
    min_required = max(h_factor * h_mm, min_mm)

    return DimensionalCheckResult(
        is_ok=bw_mm >= min_required,
        value=bw_mm,
        limit=round(min_required, 1),
        reference=reference,
    )
