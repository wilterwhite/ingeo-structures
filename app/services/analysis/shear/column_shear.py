# app/services/analysis/shear/column_shear.py
"""
Servicio de verificacion de cortante para columnas.

Implementa verificacion de cortante segun ACI 318-25:
- Columnas no sismicas: §22.5 (simplificado)
- Columnas sismicas especiales: §18.7.6 (diseno por capacidad)

Este modulo fue extraido de shear_service.py para mejorar
la separacion de responsabilidades.
"""
import math
from typing import Dict, Any, Optional

from ....domain.entities import Pier, PierForces, Column, ColumnForces
from ....domain.constants.materials import (
    LAMBDA_NORMAL,
    get_effective_fc_shear,
    get_effective_fyt_shear,
)
from ....domain.constants.shear import (
    PHI_SHEAR,
    VC_COEF_COLUMN,
    VS_MAX_COEF,
)
from ....domain.constants.units import N_TO_TONF, TONF_TO_N
from ..formatting import format_safety_factor


class ColumnShearService:
    """
    Servicio para verificacion de cortante de columnas segun ACI 318-25.

    Responsabilidades:
    - Verificar cortante de columnas no sismicas (§22.5)
    - Verificar cortante de columnas sismicas especiales (§18.7.6)
    - Calcular Ve por diseno por capacidad
    - Determinar cuando Vc = 0 (§18.7.6.2.1)
    - Verificar wall piers tratados como columnas
    """

    def check_column_shear(
        self,
        column: Column,
        column_forces: Optional[ColumnForces],
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        lambda_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Verifica cortante de una columna segun ACI 318-25.

        El metodo de diseno depende de column.is_seismic:
        - is_seismic=True: §18.7.6 (diseno por capacidad, Ve = Mpr/lu)
        - is_seismic=False: §22.5 (simplificado, Vc = 0.17*lambda*sqrt(f'c)*bw*d)

        Para diseno sismico (§18.7.6):
        - Ve = (Mpr_top + Mpr_bottom) / lu
        - Vc = 0 si: (a) cortante sismico >= 0.5Vu Y (b) Pu < Ag*f'c/20

        Args:
            column: Columna a verificar
            column_forces: Fuerzas de la columna
            Mpr_top: Momento probable en nudo superior (tonf-m)
            Mpr_bottom: Momento probable en nudo inferior (tonf-m)
            lambda_factor: Factor para concreto liviano (default 1.0)

        Returns:
            Dict con resultados de verificacion de cortante
        """
        if column.is_seismic:
            return self._check_shear_seismic_column(
                column, column_forces,
                Mpr_top=Mpr_top, Mpr_bottom=Mpr_bottom,
                lambda_factor=lambda_factor
            )
        else:
            return self._check_shear_simple_column(
                column, column_forces,
                lambda_factor=lambda_factor
            )

    def _check_shear_simple_column(
        self,
        column: Column,
        column_forces: Optional[ColumnForces],
        lambda_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Verifica cortante de columna NO sismica segun ACI 318-25 §22.5.

        Formulas:
        - Vc = 0.17 * lambda * sqrt(f'c) * bw * d  [Ec. 22.5.5.1]
        - Vs = Av * fyt * d / s                    [Ec. 22.5.10.5.3]
        - Vn = Vc + Vs
        - phi_Vn (phi = 0.75)

        Args:
            column: Columna a verificar
            column_forces: Fuerzas de la columna
            lambda_factor: Factor para concreto liviano

        Returns:
            Dict con resultados de verificacion
        """
        default_result = self._default_column_shear_result('ACI 318-25 §22.5')

        if not column_forces or not column_forces.combinations:
            return default_result

        # Calcular capacidades en ambas direcciones
        cap_V2 = self._calc_column_capacity_simple(column, 'V2', lambda_factor)
        cap_V3 = self._calc_column_capacity_simple(column, 'V3', lambda_factor)

        # Encontrar combinacion critica
        max_dcr = 0
        critical_combo = ''
        critical_Vu2 = 0
        critical_Vu3 = 0

        for combo in column_forces.combinations:
            Vu2 = abs(combo.V2)
            Vu3 = abs(combo.V3)

            dcr_2 = Vu2 / cap_V2['phi_Vn'] if cap_V2['phi_Vn'] > 0 else float('inf')
            dcr_3 = Vu3 / cap_V3['phi_Vn'] if cap_V3['phi_Vn'] > 0 else float('inf')
            dcr_combined = math.sqrt(dcr_2**2 + dcr_3**2)

            if dcr_combined > max_dcr:
                max_dcr = dcr_combined
                critical_combo = combo.name
                critical_Vu2 = Vu2
                critical_Vu3 = Vu3

        # Calcular resultados finales
        dcr_V2 = critical_Vu2 / cap_V2['phi_Vn'] if cap_V2['phi_Vn'] > 0 else 0
        dcr_V3 = critical_Vu3 / cap_V3['phi_Vn'] if cap_V3['phi_Vn'] > 0 else 0
        sf_combined = 1.0 / max_dcr if max_dcr > 0 else float('inf')
        status = 'OK' if max_dcr <= 1.0 else 'NO OK'

        return {
            'sf': self._format_sf(sf_combined),
            'status': status,
            'critical_combo': critical_combo,
            'dcr_V2': round(dcr_V2, 3),
            'dcr_V3': round(dcr_V3, 3),
            'dcr_combined': round(max_dcr, 3),
            'phi_Vn_V2': round(cap_V2['phi_Vn'], 2),
            'phi_Vn_V3': round(cap_V3['phi_Vn'], 2),
            'Vu_V2': round(critical_Vu2, 2),
            'Vu_V3': round(critical_Vu3, 2),
            'Vc_V2': round(cap_V2['Vc'], 2),
            'Vs_V2': round(cap_V2['Vs'], 2),
            'Vc_V3': round(cap_V3['Vc'], 2),
            'Vs_V3': round(cap_V3['Vs'], 2),
            'Ve': 0,
            'uses_capacity_design': False,
            'Vc_is_zero': False,
            'aci_reference': 'ACI 318-25 §22.5'
        }

    def _check_shear_seismic_column(
        self,
        column: Column,
        column_forces: Optional[ColumnForces],
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        lambda_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Verifica cortante de columna sismica especial segun ACI 318-25 §18.7.6.

        Diseno por capacidad:
        - Ve = (Mpr_top + Mpr_bottom) / lu  [§18.7.6.1]
        - Vc = 0 si: (a) Ve >= 0.5*Vu_max Y (b) Pu < Ag*f'c/20 [§18.7.6.2.1]

        Args:
            column: Columna a verificar
            column_forces: Fuerzas de la columna
            Mpr_top: Momento probable en nudo superior (tonf-m)
            Mpr_bottom: Momento probable en nudo inferior (tonf-m)
            lambda_factor: Factor para concreto liviano

        Returns:
            Dict con resultados de verificacion
        """
        default_result = self._default_column_shear_result('ACI 318-25 §18.7.6')

        if not column_forces or not column_forces.combinations:
            return default_result

        lu = column.height  # Altura libre (mm)
        Ag = column.Ag      # Area bruta (mm2)
        fc = column.fc      # f'c (MPa)

        # Calcular Ve si hay momentos probables
        Ve = 0
        use_capacity_design = False
        if Mpr_top > 0 or Mpr_bottom > 0:
            # Ve en tonf: Mpr en tonf-m, lu en mm -> convertir
            Ve = (Mpr_top + Mpr_bottom) * 1000 / lu if lu > 0 else 0
            use_capacity_design = True

        # Calcular capacidades base en ambas direcciones
        cap_V2 = self._calc_column_capacity_simple(column, 'V2', lambda_factor)
        cap_V3 = self._calc_column_capacity_simple(column, 'V3', lambda_factor)

        # Encontrar combinacion critica
        max_dcr = 0
        critical_combo = ''
        critical_Vu2 = 0
        critical_Vu3 = 0
        critical_P = 0
        Vc_is_zero = False

        for combo in column_forces.combinations:
            Vu2 = abs(combo.V2)
            Vu3 = abs(combo.V3)
            Vu_max = max(Vu2, Vu3)
            Pu = -combo.P  # Positivo = compresion (tonf)
            Pu_N = Pu * TONF_TO_N

            # Determinar cortante de diseno
            if use_capacity_design:
                Vu2_check = max(Vu2, Ve) if Vu2 > 0 else Ve
                Vu3_check = max(Vu3, Ve) if Vu3 > 0 else Ve
            else:
                Vu2_check = Vu2
                Vu3_check = Vu3

            # Verificar si Vc = 0 segun §18.7.6.2.1
            # (a) Cortante sismico >= 0.5 * Vu_max en zona lo
            # (b) Pu < Ag * f'c / 20
            condition_a = use_capacity_design and Ve >= 0.5 * Vu_max
            condition_b = Pu_N < (Ag * fc / 20)
            Vc_zero_this_combo = condition_a and condition_b

            # Ajustar capacidades si Vc = 0
            if Vc_zero_this_combo:
                phi_Vn_V2 = PHI_SHEAR * cap_V2['Vs'] * N_TO_TONF
                phi_Vn_V3 = PHI_SHEAR * cap_V3['Vs'] * N_TO_TONF
            else:
                phi_Vn_V2 = cap_V2['phi_Vn']
                phi_Vn_V3 = cap_V3['phi_Vn']

            # Calcular DCR
            dcr_2 = Vu2_check / phi_Vn_V2 if phi_Vn_V2 > 0 else float('inf')
            dcr_3 = Vu3_check / phi_Vn_V3 if phi_Vn_V3 > 0 else float('inf')
            dcr_combined = math.sqrt(dcr_2**2 + dcr_3**2)

            if dcr_combined > max_dcr:
                max_dcr = dcr_combined
                critical_combo = combo.name
                critical_Vu2 = Vu2_check
                critical_Vu3 = Vu3_check
                critical_P = Pu
                Vc_is_zero = Vc_zero_this_combo

        # Recalcular capacidades finales con Vc = 0 si aplica
        if Vc_is_zero:
            phi_Vn_V2_final = PHI_SHEAR * cap_V2['Vs'] * N_TO_TONF
            phi_Vn_V3_final = PHI_SHEAR * cap_V3['Vs'] * N_TO_TONF
            Vc_V2_final = 0
            Vc_V3_final = 0
        else:
            phi_Vn_V2_final = cap_V2['phi_Vn']
            phi_Vn_V3_final = cap_V3['phi_Vn']
            Vc_V2_final = cap_V2['Vc']
            Vc_V3_final = cap_V3['Vc']

        dcr_V2 = critical_Vu2 / phi_Vn_V2_final if phi_Vn_V2_final > 0 else 0
        dcr_V3 = critical_Vu3 / phi_Vn_V3_final if phi_Vn_V3_final > 0 else 0
        sf_combined = 1.0 / max_dcr if max_dcr > 0 else float('inf')
        status = 'OK' if max_dcr <= 1.0 else 'NO OK'

        return {
            'sf': self._format_sf(sf_combined),
            'status': status,
            'critical_combo': critical_combo,
            'dcr_V2': round(dcr_V2, 3),
            'dcr_V3': round(dcr_V3, 3),
            'dcr_combined': round(max_dcr, 3),
            'phi_Vn_V2': round(phi_Vn_V2_final, 2),
            'phi_Vn_V3': round(phi_Vn_V3_final, 2),
            'Vu_V2': round(critical_Vu2, 2),
            'Vu_V3': round(critical_Vu3, 2),
            'Vc_V2': round(Vc_V2_final, 2),
            'Vs_V2': round(cap_V2['Vs'], 2),
            'Vc_V3': round(Vc_V3_final, 2),
            'Vs_V3': round(cap_V3['Vs'], 2),
            'Ve': round(Ve, 2),
            'uses_capacity_design': use_capacity_design,
            'Vc_is_zero': Vc_is_zero,
            'aci_reference': 'ACI 318-25 §18.7.6'
        }

    def _calc_column_capacity_simple(
        self,
        column: Column,
        direction: str,
        lambda_factor: float = 1.0
    ) -> Dict[str, float]:
        """
        Calcula capacidad de cortante simple para una columna (§22.5).

        NOTA SOBRE SIMPLIFICACION:
        Esta formula usa Vc = 0.17 * lambda * sqrt(f'c) * bw * d [Ec. 22.5.5.1]
        que NO considera el incremento por carga axial (1 + Nu/14Ag) de §22.5.6.1.

        Esto es INTENCIONAL y conservador porque:
        1. La carga axial varia entre combinaciones de carga
        2. Para columnas sismicas, §18.7.6.2.1 puede hacer Vc = 0 si Pu es bajo
        3. Usar Vc base garantiza consistencia y es conservador

        La version con carga axial (Vc = 0.17*(1 + Nu/14Ag)*lambda*sqrt(f'c)*bw*d)
        esta disponible en domain/shear/verification.py para muros donde Pu
        es mas predecible.

        V2: Cortante en direccion eje 2 -> usa depth como h, width como b
        V3: Cortante en direccion eje 3 -> usa width como h, depth como b

        Args:
            column: Columna a verificar
            direction: 'V2' o 'V3'
            lambda_factor: Factor para concreto liviano

        Returns:
            Dict con Vc, Vs, Vn, phi_Vn (en tonf)
        """
        fc_eff = get_effective_fc_shear(column.fc)
        fy_eff = get_effective_fyt_shear(column.fy)

        if direction == 'V2':
            bw = column.width
            d = column.d_depth
            Av = column.As_transversal_depth
        else:
            bw = column.depth
            d = column.d_width
            Av = column.As_transversal_width

        s = column.stirrup_spacing

        # Vc = 0.17 * lambda * sqrt(f'c) * bw * d (N)
        Vc = VC_COEF_COLUMN * lambda_factor * LAMBDA_NORMAL * math.sqrt(fc_eff) * bw * d

        # Vs = Av * fyt * d / s (N)
        if s > 0:
            Vs = Av * fy_eff * d / s
        else:
            Vs = 0

        # Limite de Vs: Vs <= 0.66 * sqrt(f'c) * bw * d
        Vs_max = VS_MAX_COEF * math.sqrt(fc_eff) * bw * d
        Vs = min(Vs, Vs_max)

        Vn = Vc + Vs
        phi_Vn = PHI_SHEAR * Vn

        return {
            'Vc': Vc / N_TO_TONF,
            'Vs': Vs / N_TO_TONF,
            'Vn': Vn / N_TO_TONF,
            'phi_Vn': phi_Vn / N_TO_TONF
        }

    def _default_column_shear_result(self, aci_ref: str) -> Dict[str, Any]:
        """Resultado por defecto cuando no hay fuerzas."""
        return {
            'sf': '>100',
            'status': 'OK',
            'critical_combo': 'N/A',
            'dcr_V2': 0,
            'dcr_V3': 0,
            'dcr_combined': 0,
            'phi_Vn_V2': 0,
            'phi_Vn_V3': 0,
            'Vu_V2': 0,
            'Vu_V3': 0,
            'Vc_V2': 0,
            'Vs_V2': 0,
            'Vc_V3': 0,
            'Vs_V3': 0,
            'Ve': 0,
            'uses_capacity_design': False,
            'Vc_is_zero': False,
            'aci_reference': aci_ref
        }

    def _format_sf(self, value: float) -> Any:
        """Formatea SF para JSON. Convierte inf a '>100'."""
        return format_safety_factor(value, as_string=True)

    def check_column_shear_from_pier(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        lambda_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Verifica cortante de un Pier tratado como columna.

        Para wall piers con lw/tw <= 2.5, se aplican requisitos de columna
        segun ACI 318-25 §18.10.8.

        Args:
            pier: Pier a verificar como columna
            pier_forces: Fuerzas del pier
            lambda_factor: Factor para concreto liviano

        Returns:
            Dict con resultados de verificacion de cortante
        """
        # Crear una columna virtual desde el pier
        virtual_column = Column(
            label=pier.label,
            story=pier.story,
            depth=pier.width,           # lw -> depth
            width=pier.thickness,       # tw -> width
            height=pier.height,
            fc=pier.fc,
            fy=pier.fy,
            n_bars_depth=pier.n_edge_bars if hasattr(pier, 'n_edge_bars') else 4,
            n_bars_width=2,
            diameter_long=pier.diameter_edge if hasattr(pier, 'diameter_edge') else 16,
            stirrup_diameter=pier.stirrup_diameter if hasattr(pier, 'stirrup_diameter') else 10,
            stirrup_spacing=pier.stirrup_spacing if hasattr(pier, 'stirrup_spacing') else 150,
            cover=pier.cover,
            is_seismic=pier.is_seismic if hasattr(pier, 'is_seismic') else True
        )

        # Convertir PierForces a ColumnForces si es necesario
        column_forces = None
        if pier_forces and pier_forces.combinations:
            from ....domain.entities import ColumnForces
            column_forces = ColumnForces(
                column_label=pier.label,
                story=pier.story,
                combinations=pier_forces.combinations
            )

        return self.check_column_shear(
            virtual_column, column_forces,
            lambda_factor=lambda_factor
        )
