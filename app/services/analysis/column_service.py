# app/services/analysis/column_service.py
"""
Servicio de verificacion para columnas de HA.

Implementa verificaciones segun ACI 318-25:
1. Flexocompresion: Diagrama de interaccion P-M
2. Cortante: En ambas direcciones (V2, V3)

Limitaciones actuales:
- Solo secciones rectangulares
- Verificacion simple (sin requisitos sismicos especiales §18.7)
"""
import math
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple

from ...domain.entities import Column, ColumnForces
from ...domain.flexure import (
    InteractionDiagramService,
    SteelLayer,
    InteractionPoint,
    FlexureChecker,
)
from ...domain.shear import ShearVerificationService
from ...domain.constants.materials import (
    LAMBDA_NORMAL,
    get_effective_fc_shear,
    get_effective_fyt_shear,
)
from ...domain.constants.shear import (
    PHI_SHEAR,
    VC_COEF_COLUMN,
    VS_MAX_COEF,
    N_TO_TONF,
)
from ...domain.constants.phi_chapter21 import PHI_COMPRESSION


def _format_sf(value: float) -> Any:
    """Formatea SF para JSON. Convierte inf a '>100'."""
    if math.isinf(value):
        return ">100"
    return round(value, 2)


@dataclass
class ColumnFlexureResult:
    """Resultado de verificacion de flexocompresion para una columna."""
    # Factor de seguridad y estado
    sf: float                   # min(phi_Mn/Mu, phi_Pn/Pu)
    status: str                 # "OK" o "NO OK"
    critical_combo: str         # Combinacion critica

    # Capacidades
    phi_Pn_max: float           # Capacidad axial maxima (tonf)
    phi_Mn_M3: float            # Capacidad de momento M3 a P=0 (tonf-m)
    phi_Mn_M2: float            # Capacidad de momento M2 a P=0 (tonf-m)
    phi_Mn_at_Pu: float         # Capacidad de momento en Pu critico (tonf-m)

    # Demanda critica
    Pu: float                   # Carga axial critica (tonf)
    Mu: float                   # Momento critico (tonf-m)

    # Esbeltez
    lambda_ratio: float         # Relacion de esbeltez
    is_slender: bool            # True si es esbelta
    slenderness_factor: float   # Factor de reduccion por esbeltez

    # Referencia ACI
    aci_reference: str = "ACI 318-25 22.4"


@dataclass
class ColumnShearResult:
    """Resultado de verificacion de cortante para una columna."""
    # Verificacion V2 (eje 2)
    sf_V2: float                # Factor de seguridad V2
    dcr_V2: float               # DCR en direccion V2
    phi_Vn_V2: float            # Capacidad V2 (tonf)
    Vu_V2: float                # Demanda V2 (tonf)

    # Verificacion V3 (eje 3)
    sf_V3: float                # Factor de seguridad V3
    dcr_V3: float               # DCR en direccion V3
    phi_Vn_V3: float            # Capacidad V3 (tonf)
    Vu_V3: float                # Demanda V3 (tonf)

    # Verificacion combinada (SRSS)
    dcr_combined: float         # DCR combinado sqrt((Vu2/phiVn2)^2 + (Vu3/phiVn3)^2)
    sf_combined: float          # Factor de seguridad combinado

    # Estado general
    status: str                 # "OK" o "NO OK"
    critical_combo: str         # Combinacion critica

    # Referencia ACI
    aci_reference: str = "ACI 318-25 22.5"


@dataclass
class ColumnSlendernessResult:
    """Resultado simplificado de esbeltez para columnas."""
    lambda_ratio: float     # Relacion de esbeltez k*lu/r
    is_slender: bool        # True si es esbelta (lambda > 22)
    buckling_factor: float  # Factor de reduccion por pandeo


class ColumnService:
    """
    Servicio para verificacion de columnas de HA segun ACI 318-25.

    Responsabilidades:
    - Verificar flexocompresion (diagrama P-M)
    - Verificar cortante en ambas direcciones
    - Calcular factores de seguridad

    Limitaciones actuales:
    - Solo secciones rectangulares
    - Sin requisitos sismicos especiales (§18.7)
    """

    # Constantes de esbeltez
    LAMBDA_LIMIT = 22       # Limite de esbeltez ACI 318-25

    def __init__(self):
        self._interaction_service = InteractionDiagramService()
        self._shear_service = ShearVerificationService()

    # =========================================================================
    # FLEXOCOMPRESION
    # =========================================================================

    def check_flexure(
        self,
        column: Column,
        column_forces: Optional[ColumnForces],
        moment_axis: str = 'M3'
    ) -> Dict[str, Any]:
        """
        Verifica flexocompresion de una columna.

        Args:
            column: Columna a verificar
            column_forces: Fuerzas de la columna
            moment_axis: Eje del momento ('M2', 'M3', o 'SRSS')

        Returns:
            Dict con resultados de la verificacion
        """
        # Generar curvas de interaccion
        interaction_M3, slenderness = self._generate_interaction_curve(
            column, direction='depth'
        )
        interaction_M2, _ = self._generate_interaction_curve(
            column, direction='width'
        )

        # Capacidad axial maxima
        phi_Pn_max = self._calculate_phi_Pn_max(column)

        # Capacidades a P=0
        phi_Mn_M3 = FlexureChecker.get_phi_Mn_at_P0(interaction_M3)
        phi_Mn_M2 = FlexureChecker.get_phi_Mn_at_P0(interaction_M2)

        # Sin fuerzas -> todo OK
        if not column_forces or not column_forces.combinations:
            return {
                'sf': ">100",
                'status': 'OK',
                'critical_combo': 'N/A',
                'phi_Pn_max': round(phi_Pn_max, 1),
                'phi_Mn_M3': round(phi_Mn_M3, 2),
                'phi_Mn_M2': round(phi_Mn_M2, 2),
                'phi_Mn_at_Pu': 0,
                'Pu': 0,
                'Mu': 0,
                'slenderness': {
                    'lambda': round(slenderness.lambda_ratio, 1),
                    'is_slender': slenderness.is_slender,
                    'factor': round(slenderness.buckling_factor, 3)
                },
                'aci_reference': 'ACI 318-25 22.4'
            }

        # Obtener puntos de demanda
        demand_points = column_forces.get_critical_pm_points(moment_axis=moment_axis)

        # Seleccionar curva segun eje
        if moment_axis == 'M2':
            interaction = interaction_M2
        else:
            interaction = interaction_M3

        # Verificar usando FlexureChecker
        check_result = FlexureChecker.check_flexure(interaction, demand_points)

        return {
            'sf': round(check_result.safety_factor, 2),
            'status': check_result.status,
            'critical_combo': check_result.critical_combo,
            'phi_Pn_max': round(phi_Pn_max, 1),
            'phi_Mn_M3': round(phi_Mn_M3, 2),
            'phi_Mn_M2': round(phi_Mn_M2, 2),
            'phi_Mn_at_Pu': round(check_result.phi_Mn_at_Pu, 2),
            'Pu': round(check_result.critical_Pu, 2),
            'Mu': round(check_result.critical_Mu, 2),
            'exceeds_axial_capacity': check_result.exceeds_axial_capacity,
            'has_tension': check_result.has_tension,
            'tension_combos': check_result.tension_combos,
            'slenderness': {
                'lambda': round(slenderness.lambda_ratio, 1),
                'is_slender': slenderness.is_slender,
                'factor': round(slenderness.buckling_factor, 3)
            },
            'aci_reference': 'ACI 318-25 22.4'
        }

    def _analyze_slenderness(
        self,
        column: Column,
        direction: str = 'depth',
        k: float = 1.0
    ) -> ColumnSlendernessResult:
        """
        Analiza esbeltez de la columna para una direccion.

        Args:
            column: Columna a analizar
            direction: 'depth' o 'width'
            k: Factor de longitud efectiva (1.0 por defecto)

        Returns:
            ColumnSlendernessResult
        """
        # Dimension en direccion de la flexion
        if direction == 'depth':
            t = column.depth  # Profundidad efectiva para M3
        else:
            t = column.width  # Ancho efectivo para M2

        # Radio de giro: r = t / sqrt(12) para seccion rectangular
        r = t / math.sqrt(12)

        # Esbeltez: lambda = k * lu / r
        lu = column.height
        lambda_ratio = k * lu / r if r > 0 else float('inf')

        # Verificar si es esbelta (limite = 22)
        is_slender = lambda_ratio > self.LAMBDA_LIMIT

        # Factor de reduccion por pandeo (metodo empirico)
        buckling_ratio = k * lu / (32 * t) if t > 0 else float('inf')
        if buckling_ratio >= 1.0:
            buckling_factor = 0.0
        else:
            buckling_factor = 1 - buckling_ratio**2

        return ColumnSlendernessResult(
            lambda_ratio=lambda_ratio,
            is_slender=is_slender,
            buckling_factor=buckling_factor
        )

    def _generate_interaction_curve(
        self,
        column: Column,
        direction: str = 'depth'
    ) -> Tuple[List[InteractionPoint], ColumnSlendernessResult]:
        """
        Genera la curva de interaccion P-M para una direccion.

        Args:
            column: Columna a analizar
            direction: 'depth' para M3 o 'width' para M2

        Returns:
            Tuple (interaction_points, slenderness_result)
        """
        # Analizar esbeltez
        slenderness = self._analyze_slenderness(column, direction, k=1.0)

        # Generar capas de acero
        if direction == 'depth':
            steel_layers = column.get_steel_layers_depth()
            width = column.depth
            thickness = column.width
        else:
            steel_layers = column.get_steel_layers_width()
            width = column.width
            thickness = column.depth

        # Generar curva
        interaction = self._interaction_service.generate_interaction_curve(
            width=width,
            thickness=thickness,
            fc=column.fc,
            fy=column.fy,
            As_total=column.As_longitudinal,
            cover=column.cover,
            n_points=30,
            steel_layers=steel_layers
        )

        # Aplicar reduccion por esbeltez si corresponde
        if slenderness.is_slender:
            factor = slenderness.buckling_factor
            for point in interaction:
                point.phi_Pn *= factor
                point.Pn *= factor

        return interaction, slenderness

    def _calculate_phi_Pn_max(self, column: Column) -> float:
        """
        Calcula la capacidad axial maxima de la columna.

        Pn_max = 0.80 * [0.85*f'c*(Ag - As) + fy*As]  (§22.4.2.1)
        phi_Pn_max = phi * Pn_max
        """
        Ag = column.Ag
        As = column.As_longitudinal
        Pn_max = 0.80 * (0.85 * column.fc * (Ag - As) + column.fy * As)
        phi_Pn_max = PHI_COMPRESSION * Pn_max / N_TO_TONF
        return phi_Pn_max

    # =========================================================================
    # CORTANTE
    # =========================================================================

    def check_shear(
        self,
        column: Column,
        column_forces: Optional[ColumnForces]
    ) -> Dict[str, Any]:
        """
        Verifica cortante de una columna en ambas direcciones.

        El cortante se verifica en ambas direcciones con interaccion SRSS:
        DCR_combined = sqrt((Vu2/phiVn2)^2 + (Vu3/phiVn3)^2)

        Args:
            column: Columna a verificar
            column_forces: Fuerzas de la columna

        Returns:
            Dict con resultados de la verificacion
        """
        # Resultado por defecto
        default_result = {
            'sf_V2': ">100",
            'sf_V3': ">100",
            'sf_combined': ">100",
            'dcr_V2': 0,
            'dcr_V3': 0,
            'dcr_combined': 0,
            'status': 'OK',
            'critical_combo': 'N/A',
            'phi_Vn_V2': 0,
            'phi_Vn_V3': 0,
            'Vu_V2': 0,
            'Vu_V3': 0,
            'aci_reference': 'ACI 318-25 22.5'
        }

        if not column_forces or not column_forces.combinations:
            return default_result

        # Calcular capacidades de cortante
        capacity_V2 = self._calculate_shear_capacity(
            column, direction='V2'
        )
        capacity_V3 = self._calculate_shear_capacity(
            column, direction='V3'
        )

        phi_Vn_V2 = capacity_V2['phi_Vn']
        phi_Vn_V3 = capacity_V3['phi_Vn']

        # Encontrar combinacion critica (max DCR combinado)
        max_dcr_combined = 0
        critical_combo = ''
        critical_Vu2 = 0
        critical_Vu3 = 0

        for combo in column_forces.combinations:
            Vu2 = abs(combo.V2)
            Vu3 = abs(combo.V3)

            dcr_2 = Vu2 / phi_Vn_V2 if phi_Vn_V2 > 0 else float('inf')
            dcr_3 = Vu3 / phi_Vn_V3 if phi_Vn_V3 > 0 else float('inf')
            dcr_combined = math.sqrt(dcr_2**2 + dcr_3**2)

            if dcr_combined > max_dcr_combined:
                max_dcr_combined = dcr_combined
                critical_combo = combo.name
                critical_Vu2 = Vu2
                critical_Vu3 = Vu3

        # Calcular resultados finales
        dcr_V2 = critical_Vu2 / phi_Vn_V2 if phi_Vn_V2 > 0 else 0
        dcr_V3 = critical_Vu3 / phi_Vn_V3 if phi_Vn_V3 > 0 else 0
        sf_V2 = phi_Vn_V2 / critical_Vu2 if critical_Vu2 > 0 else float('inf')
        sf_V3 = phi_Vn_V3 / critical_Vu3 if critical_Vu3 > 0 else float('inf')
        sf_combined = 1.0 / max_dcr_combined if max_dcr_combined > 0 else float('inf')
        status = 'OK' if max_dcr_combined <= 1.0 else 'NO OK'

        return {
            'sf_V2': _format_sf(sf_V2),
            'sf_V3': _format_sf(sf_V3),
            'sf_combined': _format_sf(sf_combined),
            'dcr_V2': round(dcr_V2, 3),
            'dcr_V3': round(dcr_V3, 3),
            'dcr_combined': round(max_dcr_combined, 3),
            'status': status,
            'critical_combo': critical_combo,
            'phi_Vn_V2': round(phi_Vn_V2, 2),
            'phi_Vn_V3': round(phi_Vn_V3, 2),
            'Vu_V2': round(critical_Vu2, 2),
            'Vu_V3': round(critical_Vu3, 2),
            'Vc_V2': round(capacity_V2['Vc'], 2),
            'Vs_V2': round(capacity_V2['Vs'], 2),
            'Vc_V3': round(capacity_V3['Vc'], 2),
            'Vs_V3': round(capacity_V3['Vs'], 2),
            'aci_reference': 'ACI 318-25 22.5'
        }

    def _calculate_shear_capacity(
        self,
        column: Column,
        direction: str = 'V2'
    ) -> Dict[str, float]:
        """
        Calcula Vc, Vs, phi_Vn para una direccion de cortante.

        V2: Cortante en direccion del eje 2 -> usa depth como h, width como b
        V3: Cortante en direccion del eje 3 -> usa width como h, depth como b

        Formulas ACI 318-25 §22.5:
        - Vc = 0.17 * lambda * sqrt(f'c) * bw * d
        - Vs = Av * fy * d / s
        """
        fc_eff = get_effective_fc_shear(column.fc)
        fy_eff = get_effective_fyt_shear(column.fy)

        if direction == 'V2':
            # Cortante en direccion eje 2
            bw = column.width
            d = column.d_depth
            Av = column.As_transversal_depth
        else:
            # Cortante en direccion eje 3
            bw = column.depth
            d = column.d_width
            Av = column.As_transversal_width

        s = column.stirrup_spacing

        # Vc = 0.17 * lambda * sqrt(f'c) * bw * d
        Vc = VC_COEF_COLUMN * LAMBDA_NORMAL * math.sqrt(fc_eff) * bw * d

        # Vs = Av * fy * d / s
        if s > 0:
            Vs = Av * fy_eff * d / s
        else:
            Vs = 0

        # Limite de Vs
        Vs_max = VS_MAX_COEF * math.sqrt(fc_eff) * bw * d
        if Vs > Vs_max:
            Vs = Vs_max

        Vn = Vc + Vs
        phi_Vn = PHI_SHEAR * Vn

        return {
            'Vc': Vc / N_TO_TONF,
            'Vs': Vs / N_TO_TONF,
            'Vn': Vn / N_TO_TONF,
            'phi_Vn': phi_Vn / N_TO_TONF
        }

    # =========================================================================
    # VERIFICACION COMPLETA
    # =========================================================================

    def verify_column(
        self,
        column: Column,
        column_forces: Optional[ColumnForces]
    ) -> Dict[str, Any]:
        """
        Realiza verificacion completa de la columna.

        Incluye:
        - Flexocompresion (P-M)
        - Cortante (V2-V3)

        Returns:
            Dict con resultados completos
        """
        flexure_result = self.check_flexure(column, column_forces)
        shear_result = self.check_shear(column, column_forces)

        # Estado general: FAIL si cualquiera falla
        overall_status = 'OK'
        if flexure_result['status'] == 'NO OK' or shear_result['status'] == 'NO OK':
            overall_status = 'NO OK'

        # SF minimo (manejar strings ">100")
        sf_flexure = flexure_result['sf']
        sf_shear = shear_result['sf_combined']

        # Convertir a float para comparar (">100" -> 100)
        sf_flex_val = 100.0 if sf_flexure == ">100" else float(sf_flexure)
        sf_shear_val = 100.0 if sf_shear == ">100" else float(sf_shear)
        min_sf_val = min(sf_flex_val, sf_shear_val)

        # Formatear resultado
        min_sf = ">100" if min_sf_val >= 100 else round(min_sf_val, 2)

        return {
            'status': overall_status,
            'min_sf': min_sf,
            'flexure': flexure_result,
            'shear': shear_result,
            'column_info': {
                'label': column.label,
                'story': column.story,
                'depth': column.depth,
                'width': column.width,
                'height': column.height,
                'fc': column.fc,
                'fy': column.fy,
                'Ag': column.Ag,
                'As': round(column.As_longitudinal, 1),
                'rho': round(column.rho_longitudinal, 4),
                'reinforcement': column.reinforcement_description
            }
        }

    def verify_all_columns(
        self,
        columns: Dict[str, Column],
        column_forces: Dict[str, ColumnForces]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Verifica todas las columnas.

        Args:
            columns: Diccionario de columnas indexadas por key
            column_forces: Diccionario de fuerzas indexadas por key

        Returns:
            Dict[column_key, verification_result]
        """
        results = {}
        for column_key, column in columns.items():
            forces = column_forces.get(column_key)
            results[column_key] = self.verify_column(column, forces)
        return results

    def get_summary(
        self,
        columns: Dict[str, Column],
        column_forces: Dict[str, ColumnForces]
    ) -> Dict[str, Any]:
        """
        Genera resumen de verificacion de todas las columnas.

        Returns:
            Dict con estadisticas de verificacion
        """
        results = self.verify_all_columns(columns, column_forces)

        total = len(results)
        ok_count = sum(1 for r in results.values() if r['status'] == 'OK')
        fail_count = total - ok_count

        # Estadisticas por tipo de verificacion
        flexure_fail = sum(
            1 for r in results.values()
            if r['flexure']['status'] == 'NO OK'
        )
        shear_fail = sum(
            1 for r in results.values()
            if r['shear']['status'] == 'NO OK'
        )

        # Encontrar columna critica
        min_sf_val = float('inf')
        critical_column = None
        for col_key, result in results.items():
            sf = result.get('min_sf')
            if sf is not None:
                sf_val = 100.0 if sf == ">100" else float(sf)
                if sf_val < min_sf_val:
                    min_sf_val = sf_val
                    critical_column = col_key

        # Formatear resultado
        min_sf = ">100" if min_sf_val >= 100 else round(min_sf_val, 2)

        return {
            'total_columns': total,
            'ok_count': ok_count,
            'fail_count': fail_count,
            'pass_rate': round(ok_count / total * 100, 1) if total > 0 else 100,
            'flexure_failures': flexure_fail,
            'shear_failures': shear_fail,
            'min_sf': min_sf if min_sf_val != float('inf') else None,
            'critical_column': critical_column
        }
