# app/services/analysis/slab_service.py
"""
Servicio de verificacion de losas de HA segun ACI 318-25.

Implementa verificaciones para:
- Espesor minimo (Cap. 7 y 8)
- Flexion (momento resistente)
- Cortante unidireccional
- Refuerzo minimo

Las verificaciones de punzonamiento se manejan en punching_service.py.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List

from ...domain.entities.slab import Slab, SlabType
from ...domain.entities.slab_forces import SlabForces
from ...domain.chapter7.limits import (
    check_thickness_one_way,
    SupportCondition as OneWaySupportCondition,
)
from ...domain.chapter7.reinforcement import (
    check_reinforcement_limits,
    get_minimum_flexural_reinforcement,
)
from ...domain.chapter8.limits import (
    check_thickness_two_way,
    TwoWaySystem,
    PanelType,
)
from ...domain.constants.materials import LAMBDA_NORMAL
from ...domain.constants.shear import PHI_SHEAR
from ...domain.constants.units import N_TO_TONF, NMM_TO_TONFM
from ...domain.chapter22 import calculate_flexural_capacity, calculate_As_required
from ...domain.shear.concrete_shear import calculate_Vc_beam
from .formatting import format_safety_factor
from ..presentation.result_formatter import get_dcr_css_class


# Wrapper para compatibilidad - usa string ">100"
def _format_sf(value: float) -> Any:
    """Formatea SF para JSON. Convierte inf a '>100'."""
    return format_safety_factor(value, as_string=True)


@dataclass
class SlabFlexureResult:
    """Resultado de verificacion de flexion."""
    phi_Mn: float           # Capacidad (tonf-m/m)
    Mu: float               # Demanda (tonf-m/m)
    sf: float               # Factor de seguridad
    dcr: float              # Demand/Capacity Ratio
    status: str             # OK / NO OK
    As_required: float      # As requerido (mm2/m)
    As_provided: float      # As provisto (mm2/m)
    rho: float              # Cuantia provista
    rho_min: float          # Cuantia minima
    critical_combo: str     # Combinacion critica
    aci_reference: str = "ACI 318-25 22.2"


@dataclass
class SlabShearResult:
    """Resultado de verificacion de cortante unidireccional."""
    phi_Vn: float           # Capacidad (tonf/m)
    Vu: float               # Demanda (tonf/m)
    sf: float               # Factor de seguridad
    dcr: float              # Demand/Capacity Ratio
    status: str             # OK / NO OK
    Vc: float               # Resistencia del concreto
    critical_combo: str     # Combinacion critica
    aci_reference: str = "ACI 318-25 22.5"


@dataclass
class SlabVerificationResult:
    """Resultado completo de verificacion de losa."""
    slab_key: str
    slab_label: str
    story: str
    slab_type: str

    # Verificaciones
    thickness_check: Dict[str, Any]
    flexure: Dict[str, Any]
    shear_one_way: Dict[str, Any]
    reinforcement_check: Dict[str, Any]

    # Estado global
    overall_status: str
    critical_check: str     # Verificacion que controla


class SlabService:
    """
    Servicio para verificacion de losas segun ACI 318-25.

    Responsabilidades:
    - Verificar espesor minimo (Cap. 7 o 8)
    - Verificar flexion
    - Verificar cortante unidireccional
    - Verificar refuerzo minimo
    """

    def __init__(self, lambda_factor: float = LAMBDA_NORMAL):
        """
        Inicializa el servicio.

        Args:
            lambda_factor: Factor por tipo de concreto (1.0 normal)
        """
        self.lambda_factor = lambda_factor

    def verify_slab(
        self,
        slab: Slab,
        slab_forces: Optional[SlabForces]
    ) -> Dict[str, Any]:
        """
        Verificacion completa de una losa.

        Args:
            slab: Losa a verificar
            slab_forces: Fuerzas de la losa

        Returns:
            Dict con todas las verificaciones
        """
        # 1. Verificar espesor minimo
        thickness_result = self._check_thickness(slab)

        # 2. Verificar flexion
        flexure_result = self._check_flexure(slab, slab_forces)

        # 3. Verificar cortante unidireccional
        shear_result = self._check_shear_one_way(slab, slab_forces)

        # 4. Verificar refuerzo minimo
        reinf_result = self._check_reinforcement(slab)

        # 5. Determinar estado global
        checks = [
            ('thickness', thickness_result.get('is_ok', True)),
            ('flexure', flexure_result.get('status') == 'OK'),
            ('shear', shear_result.get('status') == 'OK'),
            ('reinforcement', reinf_result.get('is_ok', True)),
        ]

        overall_ok = all(check[1] for check in checks)
        overall_status = "OK" if overall_ok else "NO OK"

        # Encontrar verificacion critica
        critical_check = 'N/A'
        min_sf = float('inf')
        for check_name, check_result in [
            ('flexure', flexure_result),
            ('shear', shear_result)
        ]:
            sf = check_result.get('sf', '>100')
            sf_val = 100.0 if sf == '>100' else float(sf)
            if sf_val < min_sf:
                min_sf = sf_val
                critical_check = check_name

        return {
            'slab_key': f"{slab.story}_{slab.axis_slab}_{slab.location}",
            'slab_label': slab.label,
            'story': slab.story,
            'slab_type': slab.slab_type.value,
            'thickness_check': thickness_result,
            'flexure': flexure_result,
            'shear_one_way': shear_result,
            'reinforcement_check': reinf_result,
            'overall_status': overall_status,
            'critical_check': critical_check
        }

    def _check_thickness(self, slab: Slab) -> Dict[str, Any]:
        """Verifica espesor minimo segun tipo de losa."""
        if slab.slab_type == SlabType.ONE_WAY:
            # Mapear condicion de apoyo
            support_map = {
                'simply_supported': OneWaySupportCondition.SIMPLY_SUPPORTED,
                'one_end_continuous': OneWaySupportCondition.ONE_END_CONTINUOUS,
                'both_ends_continuous': OneWaySupportCondition.BOTH_ENDS_CONTINUOUS,
                'cantilever': OneWaySupportCondition.CANTILEVER,
            }
            support = support_map.get(
                slab.support_condition.value,
                OneWaySupportCondition.ONE_END_CONTINUOUS
            )

            result = check_thickness_one_way(
                h_provided_mm=slab.thickness,
                ln_mm=slab.span_length,
                support_condition=support,
                fy_mpa=slab.fy
            )

            return {
                'h_min': round(result.h_min, 1),
                'h_provided': round(result.h_provided, 1),
                'is_ok': result.is_ok,
                'ratio': round(result.ratio, 2),
                'support_condition': result.support_condition,
                'aci_reference': result.aci_reference
            }
        else:
            # Losa 2-Way
            result = check_thickness_two_way(
                h_provided_mm=slab.thickness,
                ln_mm=slab.span_length,
                system_type=TwoWaySystem.FLAT_PLATE,
                panel_type=PanelType.INTERIOR,
                fy_mpa=slab.fy
            )

            return {
                'h_min': round(result.h_min, 1),
                'h_provided': round(result.h_provided, 1),
                'is_ok': result.is_ok,
                'ratio': round(result.ratio, 2),
                'system_type': result.system_type,
                'aci_reference': result.aci_reference
            }

    def _check_flexure(
        self,
        slab: Slab,
        slab_forces: Optional[SlabForces]
    ) -> Dict[str, Any]:
        """Verifica flexion de la losa."""
        # Resultado por defecto
        default = {
            'phi_Mn': 0,
            'Mu': 0,
            'Mu_total': 0,
            'sf': '>100',
            'dcr': 0,
            'status': 'OK',
            'As_required': 0,
            'As_provided': round(slab.As_main, 1),
            'rho': round(slab.rho_main, 5),
            'rho_min': 0.0018,
            'critical_combo': 'N/A',
            'aci_reference': 'ACI 318-25 22.2'
        }

        if not slab_forces or not slab_forces.combinations:
            return default

        # Calcular capacidad a flexion (phi*Mn por metro de ancho)
        phi_Mn = self._calculate_flexure_capacity(slab)

        # Encontrar momento maximo (total para el ancho del corte)
        moments = slab_forces.get_max_moment()
        Mu_total = moments.get('M_max', 0)  # tonf-m total

        # Normalizar momento por metro de ancho
        width_m = slab.width / 1000  # Ancho del corte en metros
        Mu = Mu_total / width_m if width_m > 0 else Mu_total  # tonf-m/m

        # Encontrar combinacion critica
        critical_combo = slab_forces.get_critical_moment_combo()
        combo_name = critical_combo.name if critical_combo else 'N/A'

        # Calcular As requerido (simplificado)
        As_req = self._calculate_As_required(Mu, slab)

        # Verificacion - DCR = Mu/phi_Mn, SF = 1/DCR
        dcr = Mu / phi_Mn if phi_Mn > 0 else 0
        sf = 1 / dcr if dcr > 0 else float('inf')
        status = "OK" if dcr <= 1.0 else "NO OK"

        dcr_rounded = round(dcr, 3)
        return {
            'phi_Mn': round(phi_Mn, 3),
            'Mu': round(Mu, 3),
            'Mu_total': round(Mu_total, 3),
            'sf': _format_sf(sf),
            'dcr': dcr_rounded,
            'dcr_class': get_dcr_css_class(dcr_rounded),
            'status': status,
            'As_required': round(As_req, 1),
            'As_provided': round(slab.As_main, 1),
            'rho': round(slab.rho_main, 5),
            'rho_min': 0.0018,
            'critical_combo': combo_name,
            'aci_reference': 'ACI 318-25 22.2'
        }

    def _calculate_flexure_capacity(self, slab: Slab) -> float:
        """
        Calcula phi*Mn por metro de ancho.

        Delega a domain/chapter22/flexural_capacity.py

        Returns:
            phi*Mn en tonf-m/m
        """
        result = calculate_flexural_capacity(
            As=slab.As_main,  # mm2/m
            fy=slab.fy,       # MPa
            fc=slab.fc,       # MPa
            b=1000,           # mm (1 metro de ancho)
            d=slab.d          # mm
        )

        # Convertir de N-mm a tonf-m
        return result.phi_Mn / NMM_TO_TONFM

    def _calculate_As_required(self, Mu: float, slab: Slab) -> float:
        """
        Calcula el As requerido para un momento dado.

        Delega a domain/chapter22/flexural_capacity.py

        Returns:
            As requerido en mm2/m
        """
        if Mu <= 0:
            return 0.0

        # Convertir Mu de tonf-m a N-mm
        Mu_Nmm = Mu * NMM_TO_TONFM

        return calculate_As_required(
            Mu=Mu_Nmm,
            fy=slab.fy,
            d=slab.d
        )

    def _check_shear_one_way(
        self,
        slab: Slab,
        slab_forces: Optional[SlabForces]
    ) -> Dict[str, Any]:
        """Verifica cortante unidireccional."""
        default = {
            'phi_Vn': 0,
            'Vu': 0,
            'sf': '>100',
            'dcr': 0,
            'status': 'OK',
            'Vc': 0,
            'critical_combo': 'N/A',
            'aci_reference': 'ACI 318-25 22.5'
        }

        if not slab_forces or not slab_forces.combinations:
            return default

        # Calcular capacidad de cortante (por metro de ancho)
        phi_Vc = self._calculate_shear_capacity(slab)

        # Encontrar cortante maximo
        shears = slab_forces.get_max_shear()
        Vu = shears.get('V_max', 0)  # tonf

        # Normalizar por ancho de corte
        # El cortante del corte ya es por el ancho del corte
        # Asi que Vu ya esta en tonf para el ancho dado

        # Encontrar combinacion critica
        critical_combo = slab_forces.get_critical_shear_combo()
        combo_name = critical_combo.name if critical_combo else 'N/A'

        # Verificacion
        # Escalar capacidad por ancho de corte
        width_m = slab.width / 1000  # m
        phi_Vn_total = phi_Vc * width_m  # tonf para el ancho del corte

        # DCR = Vu/phi_Vn, SF = 1/DCR
        dcr = Vu / phi_Vn_total if phi_Vn_total > 0 else 0
        sf = 1 / dcr if dcr > 0 else float('inf')
        status = "OK" if dcr <= 1.0 else "NO OK"

        dcr_rounded = round(dcr, 3)
        return {
            'phi_Vn': round(phi_Vn_total, 2),
            'Vu': round(Vu, 2),
            'sf': _format_sf(sf),
            'dcr': dcr_rounded,
            'dcr_class': get_dcr_css_class(dcr_rounded),
            'status': status,
            'Vc': round(phi_Vc * width_m / PHI_SHEAR, 2),
            'critical_combo': combo_name,
            'aci_reference': 'ACI 318-25 22.5'
        }

    def _calculate_shear_capacity(self, slab: Slab) -> float:
        """
        Calcula phi*Vc por metro de ancho.

        Delega a domain/shear/concrete_shear.py

        Returns:
            phi*Vc en tonf/m
        """
        result = calculate_Vc_beam(
            bw=1000,              # mm (1 metro de ancho)
            d=slab.d,             # mm
            fc=slab.fc,           # MPa
            lambda_factor=self.lambda_factor
        )

        # result.Vc_N esta en Newtons, aplicar phi y convertir a tonf
        phi_Vc = PHI_SHEAR * result.Vc_N

        return phi_Vc / N_TO_TONF

    def _check_reinforcement(self, slab: Slab) -> Dict[str, Any]:
        """Verifica requisitos de refuerzo minimo."""
        result = check_reinforcement_limits(
            h_mm=slab.thickness,
            d_mm=slab.d,
            As_provided=slab.As_main,
            spacing_provided=slab.spacing_main,
            fy_mpa=slab.fy,
            is_critical_section=True
        )

        return {
            'As_min': round(result.As_min, 1),
            'As_provided': round(result.As_provided, 1),
            'is_ok': result.is_ok,
            'ratio': round(result.ratio, 2),
            'rho_min': round(result.rho_min, 5),
            'rho_provided': round(result.rho_provided, 5),
            'spacing_max': round(result.spacing_max, 0),
            'spacing_provided': round(result.spacing_provided, 0),
            'spacing_ok': result.spacing_ok,
            'aci_reference': result.aci_reference
        }

    def verify_all_slabs(
        self,
        slabs: Dict[str, Slab],
        slab_forces: Dict[str, SlabForces]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Verifica todas las losas.

        Args:
            slabs: Diccionario de losas
            slab_forces: Diccionario de fuerzas

        Returns:
            Dict[slab_key, verification_result]
        """
        results = {}

        for slab_key, slab in slabs.items():
            forces = slab_forces.get(slab_key)
            results[slab_key] = self.verify_slab(slab, forces)

        return results

    def get_summary(
        self,
        slabs: Dict[str, Slab],
        slab_forces: Dict[str, SlabForces]
    ) -> Dict[str, Any]:
        """Genera resumen de verificacion de todas las losas."""
        results = self.verify_all_slabs(slabs, slab_forces)

        total = len(results)
        ok_count = sum(1 for r in results.values() if r['overall_status'] == 'OK')
        fail_count = total - ok_count

        # Encontrar losa critica
        min_sf = float('inf')
        critical_slab = None

        for slab_key, result in results.items():
            # Buscar SF minimo entre flexion y cortante
            for check in ['flexure', 'shear_one_way']:
                sf = result.get(check, {}).get('sf', '>100')
                sf_val = 100.0 if sf == '>100' else float(sf)
                if sf_val < min_sf:
                    min_sf = sf_val
                    critical_slab = slab_key

        return {
            'total_slabs': total,
            'ok_count': ok_count,
            'fail_count': fail_count,
            'pass_rate': round(ok_count / total * 100, 1) if total > 0 else 100,
            'min_sf': _format_sf(min_sf) if min_sf != float('inf') else None,
            'critical_slab': critical_slab
        }
