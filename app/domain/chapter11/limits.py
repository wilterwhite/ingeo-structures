# app/domain/walls/limits.py
"""
Verificacion de limites de diseno para muros segun ACI 318-25 Capitulo 11.

Implementa:
- 11.3.1: Espesor minimo de muros solidos
- 11.7.2: Espaciamiento maximo de refuerzo longitudinal
- 11.7.3: Espaciamiento maximo de refuerzo transversal
- 11.7.2.3: Requisito de doble cortina

Referencias ACI 318-25:
- Tabla 11.3.1.1: Espesor minimo h
- 11.7.2.1: Espaciamiento refuerzo longitudinal (colado en sitio)
- 11.7.3.1: Espaciamiento refuerzo transversal (colado en sitio)
"""
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from ..entities.pier import Pier


class WallType(Enum):
    """Tipo de muro segun ACI 318-25."""
    BEARING = "bearing"           # Muro de carga
    NONBEARING = "nonbearing"     # Muro sin carga
    BASEMENT = "basement"         # Muro de sotano exterior
    FOUNDATION = "foundation"     # Muro de cimentacion


class WallCastType(Enum):
    """Tipo de construccion del muro."""
    CAST_IN_PLACE = "cast_in_place"  # Colado en sitio
    PRECAST = "precast"              # Prefabricado


@dataclass
class ThicknessCheckResult:
    """Resultado de verificacion de espesor minimo."""
    h_min_mm: float              # Espesor minimo requerido (mm)
    h_actual_mm: float           # Espesor actual (mm)
    is_ok: bool                  # Cumple requisito
    controlling_criterion: str   # Criterio que controla
    wall_type: WallType          # Tipo de muro
    aci_reference: str           # Referencia ACI


@dataclass
class SpacingCheckResult:
    """Resultado de verificacion de espaciamiento."""
    s_max_long_mm: float         # Espaciamiento max longitudinal (mm)
    s_max_trans_mm: float        # Espaciamiento max transversal (mm)
    s_actual_long_mm: float      # Espaciamiento actual longitudinal
    s_actual_trans_mm: float     # Espaciamiento actual transversal
    long_ok: bool                # Cumple espaciamiento longitudinal
    trans_ok: bool               # Cumple espaciamiento transversal
    is_ok: bool                  # Cumple ambos
    requires_shear_reinf: bool   # Requiere refuerzo por cortante
    aci_reference: str           # Referencia ACI


@dataclass
class DoubleCurtainCheckResult:
    """Resultado de verificacion de doble cortina."""
    h_limit_mm: float            # Limite de espesor para doble cortina (mm)
    h_actual_mm: float           # Espesor actual (mm)
    requires_double: bool        # Requiere doble cortina
    has_double: bool             # Tiene doble cortina (n_meshes >= 2)
    is_ok: bool                  # Cumple requisito
    is_exception: bool           # Aplica excepcion (sotano 1 piso)
    aci_reference: str           # Referencia ACI


@dataclass
class WallLimitsResult:
    """Resultado completo de verificacion de limites."""
    thickness: ThicknessCheckResult
    spacing: SpacingCheckResult
    double_curtain: DoubleCurtainCheckResult
    all_ok: bool                 # Cumple todos los requisitos
    warnings: List[str]          # Lista de advertencias


class WallLimitsService:
    """
    Servicio para verificacion de limites de diseno de muros segun ACI 318-25.

    Unidades: mm para dimensiones, MPa para esfuerzos.
    """

    # =========================================================================
    # CONSTANTES ACI 318-25 CAPITULO 11
    # =========================================================================

    # Espesor minimo absoluto (Tabla 11.3.1.1)
    H_MIN_ABSOLUTE_MM = 100.0        # 4 in = 100 mm
    H_MIN_BASEMENT_MM = 190.0        # 7.5 in = 190 mm

    # Factores de esbeltez para espesor minimo (Tabla 11.3.1.1)
    SLENDERNESS_BEARING = 25         # 1/25 para muros de carga
    SLENDERNESS_NONBEARING = 30      # 1/30 para muros sin carga

    # Espaciamiento maximo (11.7.2.1, 11.7.3.1)
    S_MAX_FACTOR = 3                 # 3h
    S_MAX_ABSOLUTE_MM = 457.0        # 18 in = 457 mm

    # Espaciamiento maximo para cortante (11.7.2.1, 11.7.3.1)
    S_MAX_SHEAR_LONG_FACTOR = 3      # lw/3 para longitudinal
    S_MAX_SHEAR_TRANS_FACTOR = 5     # lw/5 para transversal

    # Limite de espesor para doble cortina (11.7.2.3)
    H_DOUBLE_CURTAIN_MM = 254.0      # 10 in = 254 mm

    # Espaciamiento para prefabricados (11.7.2.2, 11.7.3.2)
    S_MAX_PRECAST_FACTOR = 5         # 5h
    S_MAX_PRECAST_EXTERIOR_MM = 457.0  # 18 in
    S_MAX_PRECAST_INTERIOR_MM = 762.0  # 30 in

    # =========================================================================
    # VERIFICACION DE ESPESOR MINIMO
    # =========================================================================

    def check_minimum_thickness(
        self,
        h: float,
        lw: float,
        lu: float,
        wall_type: WallType = WallType.BEARING,
        use_simplified_method: bool = True
    ) -> ThicknessCheckResult:
        """
        Verifica espesor minimo segun ACI 318-25 Tabla 11.3.1.1.

        Args:
            h: Espesor del muro (mm)
            lw: Longitud del muro (mm)
            lu: Altura no soportada (mm)
            wall_type: Tipo de muro
            use_simplified_method: Si usa metodo simplificado 11.5.3

        Returns:
            ThicknessCheckResult con resultado de la verificacion
        """
        h_min = self.H_MIN_ABSOLUTE_MM
        controlling = "minimum_absolute"

        if wall_type in (WallType.BASEMENT, WallType.FOUNDATION):
            # Muros de sotano exterior y cimentacion
            h_min = self.H_MIN_BASEMENT_MM
            controlling = "basement_foundation"
            aci_ref = "ACI 318-25 Tabla 11.3.1.1(e)"

        elif wall_type == WallType.BEARING and use_simplified_method:
            # Muro de carga usando metodo simplificado
            # h >= max(100mm, menor(lw, lu)/25)
            slenderness_limit = min(lw, lu) / self.SLENDERNESS_BEARING
            if slenderness_limit > h_min:
                h_min = slenderness_limit
                controlling = "slenderness_bearing"
            aci_ref = "ACI 318-25 Tabla 11.3.1.1(a,b)"

        elif wall_type == WallType.NONBEARING:
            # Muro sin carga
            # h >= max(100mm, menor(lw, lu)/30)
            slenderness_limit = min(lw, lu) / self.SLENDERNESS_NONBEARING
            if slenderness_limit > h_min:
                h_min = slenderness_limit
                controlling = "slenderness_nonbearing"
            aci_ref = "ACI 318-25 Tabla 11.3.1.1(c,d)"

        else:
            aci_ref = "ACI 318-25 Tabla 11.3.1.1"

        is_ok = h >= h_min

        return ThicknessCheckResult(
            h_min_mm=round(h_min, 1),
            h_actual_mm=h,
            is_ok=is_ok,
            controlling_criterion=controlling,
            wall_type=wall_type,
            aci_reference=aci_ref
        )

    # =========================================================================
    # VERIFICACION DE ESPACIAMIENTO MAXIMO
    # =========================================================================

    def check_spacing(
        self,
        h: float,
        lw: float,
        spacing_v: float,
        spacing_h: float,
        requires_shear_reinforcement: bool = False,
        cast_type: WallCastType = WallCastType.CAST_IN_PLACE,
        is_exterior: bool = True
    ) -> SpacingCheckResult:
        """
        Verifica espaciamiento maximo de refuerzo segun ACI 318-25 11.7.2-11.7.3.

        Args:
            h: Espesor del muro (mm)
            lw: Longitud del muro (mm)
            spacing_v: Espaciamiento refuerzo vertical/longitudinal (mm)
            spacing_h: Espaciamiento refuerzo horizontal/transversal (mm)
            requires_shear_reinforcement: Si Vu > 0.5*phi*Vc
            cast_type: Tipo de construccion
            is_exterior: Si es muro exterior (para prefabricados)

        Returns:
            SpacingCheckResult con resultado de la verificacion
        """
        if cast_type == WallCastType.CAST_IN_PLACE:
            # 11.7.2.1 y 11.7.3.1: Colado en sitio
            s_max_general = min(self.S_MAX_FACTOR * h, self.S_MAX_ABSOLUTE_MM)

            if requires_shear_reinforcement:
                # Limites adicionales por cortante
                s_max_long = min(s_max_general, lw / self.S_MAX_SHEAR_LONG_FACTOR)
                s_max_trans = min(s_max_general, lw / self.S_MAX_SHEAR_TRANS_FACTOR)
            else:
                s_max_long = s_max_general
                s_max_trans = s_max_general

            aci_ref = "ACI 318-25 11.7.2.1, 11.7.3.1"

        else:
            # 11.7.2.2 y 11.7.3.2: Prefabricado
            s_max_abs = self.S_MAX_PRECAST_EXTERIOR_MM if is_exterior else self.S_MAX_PRECAST_INTERIOR_MM
            s_max_general = min(self.S_MAX_PRECAST_FACTOR * h, s_max_abs)

            if requires_shear_reinforcement:
                s_max_general_shear = min(
                    self.S_MAX_FACTOR * h,
                    self.S_MAX_ABSOLUTE_MM
                )
                s_max_long = min(s_max_general_shear, lw / self.S_MAX_SHEAR_LONG_FACTOR)
                s_max_trans = min(s_max_general_shear, lw / self.S_MAX_SHEAR_TRANS_FACTOR)
            else:
                s_max_long = s_max_general
                s_max_trans = s_max_general

            aci_ref = "ACI 318-25 11.7.2.2, 11.7.3.2"

        long_ok = spacing_v <= s_max_long
        trans_ok = spacing_h <= s_max_trans

        return SpacingCheckResult(
            s_max_long_mm=round(s_max_long, 1),
            s_max_trans_mm=round(s_max_trans, 1),
            s_actual_long_mm=spacing_v,
            s_actual_trans_mm=spacing_h,
            long_ok=long_ok,
            trans_ok=trans_ok,
            is_ok=long_ok and trans_ok,
            requires_shear_reinf=requires_shear_reinforcement,
            aci_reference=aci_ref
        )

    # =========================================================================
    # VERIFICACION DE DOBLE CORTINA
    # =========================================================================

    def check_double_curtain(
        self,
        h: float,
        n_meshes: int,
        is_basement_one_story: bool = False,
        is_cantilever_retaining: bool = False
    ) -> DoubleCurtainCheckResult:
        """
        Verifica requisito de doble cortina segun ACI 318-25 11.7.2.3.

        Para muros con espesor > 10 in (254 mm), el refuerzo debe
        colocarse en al menos dos cortinas.

        Excepciones:
        - Muros de sotano de un piso
        - Muros de retencion en voladizo

        Args:
            h: Espesor del muro (mm)
            n_meshes: Numero de mallas/cortinas de refuerzo
            is_basement_one_story: Muro de sotano de un solo piso
            is_cantilever_retaining: Muro de retencion en voladizo

        Returns:
            DoubleCurtainCheckResult con resultado de la verificacion
        """
        is_exception = is_basement_one_story or is_cantilever_retaining
        requires_double = h > self.H_DOUBLE_CURTAIN_MM and not is_exception
        has_double = n_meshes >= 2

        is_ok = not requires_double or has_double

        return DoubleCurtainCheckResult(
            h_limit_mm=self.H_DOUBLE_CURTAIN_MM,
            h_actual_mm=h,
            requires_double=requires_double,
            has_double=has_double,
            is_ok=is_ok,
            is_exception=is_exception,
            aci_reference="ACI 318-25 11.7.2.3"
        )

    # =========================================================================
    # VERIFICACION COMPLETA
    # =========================================================================

    def check_wall_limits(
        self,
        pier: 'Pier',
        wall_type: WallType = WallType.BEARING,
        requires_shear_reinforcement: bool = False,
        cast_type: WallCastType = WallCastType.CAST_IN_PLACE,
        is_basement_one_story: bool = False
    ) -> WallLimitsResult:
        """
        Ejecuta todas las verificaciones de limites de diseno.

        Args:
            pier: Entidad Pier con geometria y armadura
            wall_type: Tipo de muro
            requires_shear_reinforcement: Si requiere refuerzo por cortante
            cast_type: Tipo de construccion
            is_basement_one_story: Si es sotano de un piso

        Returns:
            WallLimitsResult con todos los resultados
        """
        warnings = []

        # 1. Espesor minimo
        thickness_result = self.check_minimum_thickness(
            h=pier.thickness,
            lw=pier.width,
            lu=pier.height,
            wall_type=wall_type
        )
        if not thickness_result.is_ok:
            warnings.append(
                f"Espesor insuficiente: {pier.thickness}mm < {thickness_result.h_min_mm}mm "
                f"({thickness_result.aci_reference})"
            )

        # 2. Espaciamiento maximo
        spacing_result = self.check_spacing(
            h=pier.thickness,
            lw=pier.width,
            spacing_v=pier.spacing_v,
            spacing_h=pier.spacing_h,
            requires_shear_reinforcement=requires_shear_reinforcement,
            cast_type=cast_type
        )
        if not spacing_result.long_ok:
            warnings.append(
                f"Espaciamiento vertical excede maximo: {pier.spacing_v}mm > "
                f"{spacing_result.s_max_long_mm}mm ({spacing_result.aci_reference})"
            )
        if not spacing_result.trans_ok:
            warnings.append(
                f"Espaciamiento horizontal excede maximo: {pier.spacing_h}mm > "
                f"{spacing_result.s_max_trans_mm}mm ({spacing_result.aci_reference})"
            )

        # 3. Doble cortina
        double_result = self.check_double_curtain(
            h=pier.thickness,
            n_meshes=pier.n_meshes,
            is_basement_one_story=is_basement_one_story
        )
        if not double_result.is_ok:
            warnings.append(
                f"Se requiere doble cortina para espesor {pier.thickness}mm > "
                f"{double_result.h_limit_mm}mm ({double_result.aci_reference})"
            )

        all_ok = thickness_result.is_ok and spacing_result.is_ok and double_result.is_ok

        return WallLimitsResult(
            thickness=thickness_result,
            spacing=spacing_result,
            double_curtain=double_result,
            all_ok=all_ok,
            warnings=warnings
        )

