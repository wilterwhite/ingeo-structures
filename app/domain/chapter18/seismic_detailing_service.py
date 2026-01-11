# app/domain/chapter18/seismic_detailing_service.py
"""
Servicio de detallamiento sismico comun a vigas, columnas y muros.

Centraliza la logica de verificacion que es compartida entre:
- Vigas sismicas (§18.6)
- Columnas sismicas (§18.7)
- Muros estructurales (§18.10)
- Piers tipo columna (§18.10.8 + §18.7)

Referencias ACI 318-25:
- §18.6.4: Refuerzo transversal en vigas
- §18.7.5: Refuerzo transversal en columnas
- §18.10.6: Elementos de borde en muros
"""
import math
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

from .common import SeismicCategory
from ..constants.chapter18 import (
    FIRST_HOOP_MAX_MM,
    HX_MAX_MM as HX_MAX_BEAM_MM,
    HX_MAX_MM as HX_MAX_COLUMN_MM,
    MIN_WIDTH_BEAM_MM,
    MIN_COLUMN_DIM_MM,
)


# ============================================================================
# Resultados
# ============================================================================

@dataclass
class TransverseSpacingResult:
    """Resultado de verificacion de espaciamiento transversal."""
    s_provided: float       # Espaciamiento proporcionado (mm)
    s_max: float            # Espaciamiento maximo permitido (mm)
    s_ok: bool              # True si s_provided <= s_max
    aci_reference: str      # Seccion ACI aplicable
    governing_limit: str    # Que limite gobierna (d/4, 6", etc)


@dataclass
class ConfinementZoneResult:
    """Resultado de calculo de zona de confinamiento."""
    lo: float               # Longitud de zona de confinamiento (mm)
    lo_min: float           # Longitud minima segun ACI (mm)
    aci_reference: str      # Seccion ACI aplicable
    governing_limit: str    # Que limite gobierna


@dataclass
class LateralSupportResult:
    """Resultado de verificacion de soporte lateral (hx)."""
    hx_provided: float      # Espaciamiento entre barras soportadas (mm)
    hx_max: float           # Espaciamiento maximo permitido (mm)
    hx_ok: bool             # True si hx_provided <= hx_max
    aci_reference: str


@dataclass
class FirstHoopResult:
    """Resultado de verificacion de primer estribo."""
    distance: float         # Distancia proporcionada (mm)
    max_distance: float     # Distancia maxima permitida (mm)
    is_ok: bool
    aci_reference: str


# ============================================================================
# Servicio
# ============================================================================

class SeismicDetailingService:
    """
    Servicio de detallamiento sismico para elementos estructurales.

    Provee metodos comunes para verificar requisitos de:
    - Espaciamiento de refuerzo transversal
    - Longitud de zona de confinamiento
    - Soporte lateral de barras longitudinales
    - Posicion del primer estribo

    Example:
        service = SeismicDetailingService()

        # Verificar espaciamiento en zona de confinamiento
        result = service.check_transverse_spacing_in_zone(
            s_provided=100,
            d=540,
            db_long=20,
            element_type='beam',
            steel_grade=60,
            category=SeismicCategory.SPECIAL
        )

        # Calcular longitud de zona de confinamiento
        lo = service.calculate_confinement_zone_length(
            h=600,
            lu=3000,
            element_type='column'
        )
    """

    # =========================================================================
    # Espaciamiento Transversal
    # =========================================================================

    def check_transverse_spacing_in_zone(
        self,
        s_provided: float,
        d: float,
        db_long: float,
        element_type: str,
        steel_grade: int = 60,
        category: SeismicCategory = SeismicCategory.SPECIAL,
    ) -> TransverseSpacingResult:
        """
        Verifica espaciamiento de refuerzo transversal en zona de confinamiento.

        Args:
            s_provided: Espaciamiento proporcionado (mm)
            d: Profundidad efectiva (mm)
            db_long: Diametro de barra longitudinal (mm)
            element_type: 'beam', 'column', o 'wall_pier'
            steel_grade: Grado del acero (60 u 80)
            category: Categoria sismica

        Returns:
            TransverseSpacingResult con verificacion
        """
        if element_type == 'beam':
            return self._check_beam_transverse_spacing(
                s_provided, d, db_long, steel_grade, category
            )
        elif element_type in ('column', 'wall_pier'):
            return self._check_column_transverse_spacing(
                s_provided, d, db_long, steel_grade, category
            )
        else:
            # Default a reglas de columna
            return self._check_column_transverse_spacing(
                s_provided, d, db_long, steel_grade, category
            )

    def _check_beam_transverse_spacing(
        self,
        s_provided: float,
        d: float,
        db_long: float,
        steel_grade: int,
        category: SeismicCategory,
    ) -> TransverseSpacingResult:
        """
        Espaciamiento en vigas segun §18.6.4.4 (SPECIAL) o §18.4.2.4 (INTERMEDIATE).

        SPECIAL: s <= min(d/4, 6", 6*db G60, 5*db G80)
        INTERMEDIATE: s <= min(d/4, 8*db G60, 6*db G80, 12")
        """
        limits = {}

        if category == SeismicCategory.SPECIAL:
            limits['d/4'] = d / 4
            limits['6"'] = 152  # 6" = 152mm

            if steel_grade >= 80:
                limits['5*db'] = 5 * db_long
            else:
                limits['6*db'] = 6 * db_long

            aci_ref = "§18.6.4.4"

        else:  # INTERMEDIATE
            limits['d/4'] = d / 4
            limits['12"'] = 305  # 12" = 305mm

            if steel_grade >= 80:
                limits['6*db'] = 6 * db_long
            else:
                limits['8*db'] = 8 * db_long

            aci_ref = "§18.4.2.4"

        s_max = min(limits.values())
        governing = min(limits, key=limits.get)

        return TransverseSpacingResult(
            s_provided=s_provided,
            s_max=round(s_max, 0),
            s_ok=s_provided <= s_max,
            aci_reference=aci_ref,
            governing_limit=governing,
        )

    def _check_column_transverse_spacing(
        self,
        s_provided: float,
        d: float,
        db_long: float,
        steel_grade: int,
        category: SeismicCategory,
    ) -> TransverseSpacingResult:
        """
        Espaciamiento en columnas segun §18.7.5.3 (SPECIAL).

        s <= min(b/4, 6*db G60, 5*db G80, so)
        donde so = 4" + (14" - hx)/3, con 4" <= so <= 6"
        """
        limits = {}

        # b/4 (usando d como aproximacion de dimension menor)
        # En columnas, se usa la dimension menor b, no d
        limits['b/4'] = d / 4  # Aproximacion conservadora

        if steel_grade >= 80:
            limits['5*db'] = 5 * db_long
        else:
            limits['6*db'] = 6 * db_long

        # so no se puede calcular sin hx, usar limite superior
        limits['6"'] = 152  # 6" = 152mm (limite superior de so)

        s_max = min(limits.values())
        governing = min(limits, key=limits.get)

        return TransverseSpacingResult(
            s_provided=s_provided,
            s_max=round(s_max, 0),
            s_ok=s_provided <= s_max,
            aci_reference="§18.7.5.3",
            governing_limit=governing,
        )

    # =========================================================================
    # Zona de Confinamiento
    # =========================================================================

    def calculate_confinement_zone_length(
        self,
        element_type: str,
        h: float = 0,
        lu: float = 0,
        d: float = 0,
        category: SeismicCategory = SeismicCategory.SPECIAL,
    ) -> ConfinementZoneResult:
        """
        Calcula la longitud de la zona de confinamiento (lo).

        Args:
            element_type: 'beam', 'column', o 'wall_pier'
            h: Altura de seccion (mm) - para vigas y columnas
            lu: Altura libre (mm) - para columnas
            d: Profundidad efectiva (mm) - para vigas
            category: Categoria sismica

        Returns:
            ConfinementZoneResult con longitud calculada
        """
        if element_type == 'beam':
            # §18.6.4.1: lo = 2h desde cara de nudo
            lo = 2 * h
            lo_min = 2 * h
            governing = "2h"
            aci_ref = "§18.6.4.1"

        elif element_type in ('column', 'wall_pier'):
            # §18.7.5.1: lo >= max(h, lu/6, 18")
            lo_options = {
                'h': h,
                'lu/6': lu / 6 if lu > 0 else 0,
                '18"': 457,  # 18" = 457mm
            }
            lo = max(lo_options.values())
            lo_min = lo
            governing = max(lo_options, key=lo_options.get)
            aci_ref = "§18.7.5.1"

        else:
            lo = 2 * h
            lo_min = 2 * h
            governing = "2h (default)"
            aci_ref = "N/A"

        return ConfinementZoneResult(
            lo=round(lo, 0),
            lo_min=round(lo_min, 0),
            aci_reference=aci_ref,
            governing_limit=governing,
        )

    # =========================================================================
    # Soporte Lateral (hx)
    # =========================================================================

    def check_lateral_support(
        self,
        hx_provided: float,
        element_type: str,
    ) -> LateralSupportResult:
        """
        Verifica espaciamiento entre barras longitudinales soportadas.

        Args:
            hx_provided: Espaciamiento proporcionado (mm)
            element_type: 'beam', 'column', o 'wall_pier'

        Returns:
            LateralSupportResult con verificacion
        """
        if element_type == 'beam':
            hx_max = HX_MAX_BEAM_MM
            aci_ref = "§18.6.4.3"
        else:  # column, wall_pier
            hx_max = HX_MAX_COLUMN_MM
            aci_ref = "§18.7.5.2(e)"

        return LateralSupportResult(
            hx_provided=hx_provided,
            hx_max=hx_max,
            hx_ok=hx_provided <= hx_max,
            aci_reference=aci_ref,
        )

    # =========================================================================
    # Primer Estribo
    # =========================================================================

    def check_first_hoop_position(
        self,
        distance: float,
        element_type: str,
    ) -> FirstHoopResult:
        """
        Verifica posicion del primer estribo desde cara de nudo.

        §18.6.4.4 y §18.7.5.3: primer hoop a <= 2" de cara

        Args:
            distance: Distancia proporcionada (mm)
            element_type: 'beam', 'column', o 'wall_pier'

        Returns:
            FirstHoopResult con verificacion
        """
        max_distance = FIRST_HOOP_MAX_MM  # 2" para todos

        if element_type == 'beam':
            aci_ref = "§18.6.4.4"
        else:
            aci_ref = "§18.7.5.3"

        return FirstHoopResult(
            distance=distance,
            max_distance=max_distance,
            is_ok=distance <= max_distance,
            aci_reference=aci_ref,
        )

    # =========================================================================
    # Espaciamiento so (Columnas)
    # =========================================================================

    def calculate_so(self, hx: float) -> Tuple[float, str]:
        """
        Calcula espaciamiento so para columnas segun §18.7.5.3(d).

        so = 4" + (14" - hx)/3, con 4" <= so <= 6"

        Args:
            hx: Espaciamiento entre barras soportadas (mm)

        Returns:
            Tuple de (so en mm, expresion usada)
        """
        # Import lazy para evitar circular import
        from .columns.transverse import calculate_so as _calculate_so_core

        # Usar funcion centralizada de columns/transverse.py
        so_mm = _calculate_so_core(hx)

        # Generar expresion para logging/debugging
        hx_in = hx / 25.4
        so_in = so_mm / 25.4
        expr = f"4+(14-{hx_in:.1f})/3 = {so_in:.1f}\""

        return round(so_mm, 0), expr

    # =========================================================================
    # Cuantia Minima de Refuerzo Transversal (Ash)
    # =========================================================================

    def calculate_Ash_required(
        self,
        bc: float,
        s: float,
        fc: float,
        fyt: float,
        Ag: float,
        Ach: float,
        Pu_N: float,
        steel_grade: int = 60,
    ) -> Tuple[float, str]:
        """
        Calcula area de refuerzo transversal requerida segun §18.7.5.4.

        Para columnas especiales:
        Ash >= max de:
        (a) 0.3*s*bc*fc/fyt * (Ag/Ach - 1)
        (b) 0.09*s*bc*fc/fyt
        (c) 0.2*kf*kn*Pu/(fyt*Ach) * s*bc  (si Pu > 0.3*Ag*fc)

        Args:
            bc: Dimension del nucleo perpendicular a Ash (mm)
            s: Espaciamiento de estribos (mm)
            fc: f'c del concreto (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            Ag: Area bruta (mm2)
            Ach: Area del nucleo (mm2)
            Pu_N: Carga axial factorizada (N)
            steel_grade: Grado del acero

        Returns:
            Tuple de (Ash requerido en mm2, ecuacion gobernante)
        """
        # Tabla 18.7.5.4(a)
        Ash_a = 0.3 * s * bc * (fc / fyt) * (Ag / Ach - 1) if Ach > 0 else 0

        # Tabla 18.7.5.4(b)
        Ash_b = 0.09 * s * bc * fc / fyt

        # Tabla 18.7.5.4(c) - solo si Pu > 0.3*Ag*fc
        Ash_c = 0
        if Pu_N > 0.3 * Ag * fc:
            # kf segun nota (a) de Tabla 18.7.5.4
            kf = fc / 175 + 0.6 if fc <= 70 else 1.0

            # kn = nl / (nl - 2) donde nl = numero de barras en cara
            # Aproximacion conservadora: kn = 1.5 para nl = 6
            kn = 1.5

            Ash_c = 0.2 * kf * kn * Pu_N / (fyt * Ach) * s * bc if Ach > 0 else 0

        Ash_required = max(Ash_a, Ash_b, Ash_c)

        # Determinar ecuacion gobernante
        if Ash_required == Ash_c and Ash_c > 0:
            governing = "Tabla 18.7.5.4(c)"
        elif Ash_required == Ash_a:
            governing = "Tabla 18.7.5.4(a)"
        else:
            governing = "Tabla 18.7.5.4(b)"

        return round(Ash_required, 1), governing
