# app/services/analysis/shear_service.py
"""
Servicio unificado de cortante - delega directamente a domain/.

Este archivo consolida la funcionalidad de:
- facade.py (orquestación)
- wall_shear.py (cortante de muros)
- column_shear.py (cortante de columnas)
- wall_special_elements.py (clasificación, amplificación, borde, vigas acople)

Mantiene la misma API pública pero elimina capas de indirección.
"""
from typing import Dict, Any, Optional, List, Tuple

from ...domain.entities import VerticalElement, ElementForces
from ...domain.shear import (
    ShearVerificationService,
    WallClassificationService as DomainWallClassificationService,
    WallClassification,
    WallGroupShearResult,
)
from ...domain.chapter18 import (
    ShearAmplificationService as DomainShearAmplificationService,
    BoundaryElementService as DomainBoundaryElementService,
    BoundaryElementMethod,
    BoundaryElementResult,
    CouplingBeamService as DomainCouplingBeamService,
    CouplingBeamDesignResult,
)
from ...domain.chapter18.common import SeismicCategory
from ...domain.chapter18.design_forces import ShearAmplificationResult
from ...domain.constants.units import TONF_TO_N, TONFM_TO_NMM, N_TO_TONF
from ...domain.constants.shear import PHI_SHEAR
from ..presentation.formatters import format_safety_factor


class ShearService:
    """
    Servicio unificado de cortante.

    Delega directamente a servicios de domain/:
    - domain/shear/: Verificación de cortante genérico
    - domain/chapter18/: Requisitos sísmicos (clasificación, amplificación, borde)

    API pública preservada para compatibilidad.
    """

    def __init__(self):
        # Servicios de domain/
        self._shear_verification = ShearVerificationService()
        self._classification = DomainWallClassificationService()
        self._amplification = DomainShearAmplificationService()
        self._boundary = DomainBoundaryElementService()
        self._coupling = DomainCouplingBeamService()

    # =========================================================================
    # VERIFICACIÓN DE MUROS
    # =========================================================================

    def check_shear(
        self,
        pier: 'VerticalElement',
        pier_forces: Optional[ElementForces],
        Mpr_total: float = 0,
        lu: float = 0,
        lambda_factor: float = 1.0,
        seismic_category: SeismicCategory = None
    ) -> Dict[str, Any]:
        """
        Verifica corte con interacción V2-V3 y retorna el caso crítico.

        Args:
            pier: Pier a verificar
            pier_forces: Fuerzas del pier (combinaciones)
            Mpr_total: Momento probable total de vigas de acople (tonf-m)
            lu: Altura libre del pier (mm)
            lambda_factor: Factor de concreto liviano
            seismic_category: Categoría sísmica (SPECIAL usa φ=0.60, otros φ=0.75)

        Returns:
            Dict con resultados de la verificación de corte
        """
        if not pier_forces or not pier_forces.combinations:
            return self._empty_shear_result()

        # Default seismic_category a SPECIAL si no se proporciona
        if seismic_category is None:
            seismic_category = SeismicCategory.SPECIAL

        # Clasificar el elemento
        classification = self._classification.classify(
            lw=pier.length, tw=pier.thickness, hw=pier.height
        )

        # Encontrar combinación crítica y cachear TODOS los resultados
        critical_result = None
        critical_combo = None
        max_dcr = 0
        combo_shear_results = []  # Cachear resultado de CADA combinación

        for combo in pier_forces.combinations:
            Vu2 = abs(combo.V2) if hasattr(combo, 'V2') else 0
            Vu3 = abs(combo.V3) if hasattr(combo, 'V3') else 0
            Nu = -combo.P if hasattr(combo, 'P') else 0  # Compresión positiva

            result = self._shear_verification.verify_combined_shear(
                lw=pier.length,
                tw=pier.thickness,
                hw=pier.height,
                fc=pier.fc,
                fy=pier.fy,
                rho_h=pier.rho_horizontal,
                Vu2=Vu2,
                Vu3=Vu3,
                Nu=Nu,
                combo_name=combo.name,
                rho_v=pier.rho_vertical,
                lambda_factor=lambda_factor,
                seismic_category=seismic_category
            )

            # Cachear resultado de este combo (ya se calculó, no desperdiciar)
            r2 = result.result_V2
            r3 = result.result_V3
            combo_shear_results.append({
                'combo_name': combo.name,
                'combo_location': combo.location if hasattr(combo, 'location') else 'Middle',
                'Vu_2': round(Vu2, 2),
                'Vu_3': round(Vu3, 2),
                'Pu': round(-Nu, 2),
                'phi_Vn_2': round(r2.phi_Vn, 2),
                'phi_Vn_3': round(r3.phi_Vn, 2),
                'phi_Vc': round(r2.Vc * result.phi_v, 2),
                'Vc': round(r2.Vc, 2),
                'Vs': round(r2.Vs, 2),
                'dcr_2': round(result.dcr_2, 3),
                'dcr_3': round(result.dcr_3, 3),
                'dcr_combined': round(result.dcr_combined, 3),
                'sf': round(1.0 / result.dcr_combined, 2) if result.dcr_combined > 0 else 100.0,
                'status': 'OK' if result.dcr_combined <= 1.0 else 'NO OK'
            })

            if result.dcr_combined > max_dcr:
                max_dcr = result.dcr_combined
                critical_result = result
                critical_combo = combo

        if critical_result is None:
            return self._empty_shear_result()

        sf = 1.0 / critical_result.dcr_combined if critical_result.dcr_combined > 0 else float('inf')

        # Extraer resultados de V2 y V3 del CombinedShearResult
        r2 = critical_result.result_V2
        r3 = critical_result.result_V3

        return {
            'status': 'OK' if sf >= 1.0 else 'NO OK',
            'critical_combo': critical_combo.name if critical_combo else 'N/A',
            'phi_Vn_2': round(r2.phi_Vn, 2),
            'Vu_2': round(r2.Vu, 2),
            'dcr_2': round(critical_result.dcr_2, 3),
            'phi_Vn_3': round(r3.phi_Vn, 2),
            'Vu_3': round(r3.Vu, 2),
            'dcr_3': round(critical_result.dcr_3, 3),
            'dcr_combined': round(critical_result.dcr_combined, 3),
            'sf': format_safety_factor(sf),
            'Vc': round(r2.Vc, 2),
            'Vs': round(r2.Vs, 2),
            'aci_reference': r2.aci_reference,
            'phi_v': critical_result.phi_v,
            'combo_results': combo_shear_results,  # Resultados de TODAS las combinaciones
        }

    def _empty_shear_result(self) -> Dict[str, Any]:
        """Resultado vacío cuando no hay fuerzas."""
        return {
            'status': 'OK',
            'critical_combo': 'N/A',
            'phi_Vn_2': 0, 'Vu_2': 0, 'dcr_2': 0,
            'phi_Vn_3': 0, 'Vu_3': 0, 'dcr_3': 0,
            'dcr_combined': 0, 'sf': 100.0,
            'Vc': 0, 'Vs': 0,
            'aci_reference': 'ACI 318-25 §22.5',
            'phi_v': 0.60,  # Default SPECIAL
        }

    def get_shear_capacity(
        self,
        pier: 'VerticalElement',
        Nu: float = 0,
        seismic_category: SeismicCategory = None
    ) -> Dict[str, Any]:
        """Calcula las capacidades de corte puro del pier en ambas direcciones."""
        # Default seismic_category a SPECIAL si no se proporciona
        if seismic_category is None:
            seismic_category = SeismicCategory.SPECIAL

        # Usar verify_combined_shear con Vu=0 para obtener capacidades en V2 y V3
        result = self._shear_verification.verify_combined_shear(
            lw=pier.length,
            tw=pier.thickness,
            hw=pier.height,
            fc=pier.fc,
            fy=pier.fy,
            rho_h=pier.rho_horizontal,
            Vu2=0,  # Solo queremos las capacidades
            Vu3=0,
            Nu=Nu,  # Ya en tonf
            rho_v=pier.rho_vertical,
            seismic_category=seismic_category
        )
        # Extraer resultados de ambas direcciones
        r2 = result.result_V2
        r3 = result.result_V3
        return {
            'Vc_2': round(r2.Vc, 2),
            'Vs_2': round(r2.Vs, 2),
            'phi_Vn_2': round(r2.phi_Vn, 2),
            'Vc_3': round(r3.Vc, 2),
            'Vs_3': round(r3.Vs, 2),
            'phi_Vn_3': round(r3.phi_Vn, 2),
            'phi_v': result.phi_v,
        }

    def verify_bidirectional_shear(
        self,
        lw: float, tw: float, hw: float,
        fc: float, fy: float, rho_h: float,
        Vu2_max: float, Vu3_max: float,
        Nu: float = 0, rho_v: Optional[float] = None,
        lambda_factor: float = 1.0,
        seismic_category: SeismicCategory = None
    ):
        """
        Verifica cortante bidireccional (V2 y V3).

        Args:
            lw: Longitud del muro (mm)
            tw: Espesor del muro (mm)
            hw: Altura del muro (mm)
            fc: Resistencia del concreto (MPa)
            fy: Fluencia del acero (MPa)
            rho_h: Cuantía horizontal
            Vu2_max: Cortante en plano V2 (N)
            Vu3_max: Cortante fuera de plano V3 (N)
            Nu: Carga axial (N)
            rho_v: Cuantía vertical (opcional)
            lambda_factor: Factor para concreto liviano (1.0=normal)
            seismic_category: Categoría sísmica

        Returns:
            CombinedShearResult con DCR combinado SRSS
        """
        if seismic_category is None:
            seismic_category = SeismicCategory.SPECIAL
        return self._shear_verification.verify_combined_shear(
            lw=lw, tw=tw, hw=hw, fc=fc, fy=fy, rho_h=rho_h,
            Vu2=Vu2_max, Vu3=Vu3_max, Nu=Nu, rho_v=rho_v,
            lambda_factor=lambda_factor,
            seismic_category=seismic_category
        )

    def verify_wall_group(
        self,
        segments: List[Tuple[float, float, float]],
        fc: float, fy: float, rho_h: float,
        Vu_total: float, Nu: float = 0,
        rho_v: Optional[float] = None,
        seismic_category: SeismicCategory = None
    ) -> WallGroupShearResult:
        """Verifica un grupo de segmentos de muro según §18.10.4.4."""
        if seismic_category is None:
            seismic_category = SeismicCategory.SPECIAL
        return self._shear_verification.verify_wall_group(
            segments, fc, fy, rho_h, Vu_total, Nu, rho_v,
            seismic_category=seismic_category
        )

    # =========================================================================
    # CLASIFICACIÓN DE MUROS (§18.10.8)
    # =========================================================================

    def classify_wall(self, pier: 'VerticalElement') -> WallClassification:
        """Clasifica un pier según ACI 318-25 §18.10.8."""
        return self._classification.classify(
            lw=pier.length, tw=pier.thickness, hw=pier.height
        )

    def get_classification_dict(self, pier: 'VerticalElement') -> Dict[str, Any]:
        """Obtiene la clasificación del pier como diccionario."""
        classification = self.classify_wall(pier)
        return {
            'type': classification.element_type.value,
            'lw_tw': round(classification.lw_tw, 2),
            'hw_lw': round(classification.hw_lw, 2),
            'aci_section': classification.aci_section,
            'design_method': classification.design_method,
            'special_requirements': classification.special_requirements,
            'is_wall_pier': self._classification.is_wall_pier(classification),
            'requires_column_detailing': self._classification.requires_column_detailing(classification),
            'is_squat': self._classification.is_squat_wall(classification),
        }

    # =========================================================================
    # AMPLIFICACIÓN DE CORTANTE (§18.10.3.3)
    # =========================================================================

    def amplify_shear(
        self,
        pier: 'VerticalElement',
        Vu: float,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        use_omega_0: bool = False,
        omega_0: float = 2.5
    ) -> ShearAmplificationResult:
        """Amplifica el cortante sísmico según ACI 318-25 §18.10.3.3."""
        hwcs_value = hwcs if hwcs and hwcs > 0 else pier.height
        classification = self.classify_wall(pier)
        is_wall_pier = self._classification.is_wall_pier(classification)

        if not self._amplification.should_amplify(is_wall_pier=is_wall_pier):
            return ShearAmplificationResult(
                Vu_original=Vu,
                Ve=Vu,
                Omega_v=1.0,
                omega_v_dyn=1.0,
                amplification=1.0,
                hwcs_lw=hwcs_value / pier.length if pier.length > 0 else 0,
                hn_ft=None,
                applies=False,
                aci_reference="No aplica: pilar de muro o viga de acoplamiento"
            )

        return self._amplification.calculate_amplified_shear(
            Vu=Vu, hwcs=hwcs_value, lw=pier.length,
            hn_ft=hn_ft, use_omega_0=use_omega_0, omega_0=omega_0
        )

    def get_amplification_dict(
        self,
        pier: 'VerticalElement',
        Vu: float,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """Obtiene la amplificación de cortante como diccionario."""
        result = self.amplify_shear(pier, Vu, hwcs=hwcs, hn_ft=hn_ft)
        return {
            'Vu_original': round(result.Vu_original, 2),
            'Ve': round(result.Ve, 2),
            'Omega_v': round(result.Omega_v, 3),
            'omega_v_dyn': round(result.omega_v_dyn, 3),
            'amplification': round(result.amplification, 3),
            'hwcs_lw': round(result.hwcs_lw, 2),
            'applies': result.applies,
            'aci_reference': result.aci_reference,
        }

    # =========================================================================
    # ELEMENTOS DE BORDE (§18.10.6)
    # =========================================================================

    def check_boundary_element(
        self,
        pier: 'VerticalElement',
        Pu: float,
        Mu: float,
        c: Optional[float] = None,
        delta_u: Optional[float] = None,
        Vu: float = 0,
        method: str = 'auto'
    ) -> BoundaryElementResult:
        """Verifica si se requiere elemento de borde según §18.10.6."""
        hwcs_lw = pier.height / pier.length if pier.length > 0 else 0
        Ag = pier.Ag
        Ach = Ag * 0.85

        # Determinar método
        if method == 'auto':
            use_method = BoundaryElementMethod.DISPLACEMENT if (
                hwcs_lw >= 2.0 and c and delta_u
            ) else BoundaryElementMethod.STRESS
        elif method == 'displacement':
            use_method = BoundaryElementMethod.DISPLACEMENT
        else:
            use_method = BoundaryElementMethod.STRESS

        if use_method == BoundaryElementMethod.DISPLACEMENT and c and delta_u:
            return self._boundary.verify_boundary_element(
                method=use_method,
                lw=pier.length, c=c, hu=pier.height,
                fc=pier.fc, fyt=pier.fy, Ag=Ag, Ach=Ach,
                b=pier.thickness, delta_u=delta_u,
                hwcs=pier.height, Mu=Mu, Vu=Vu, Ve=Vu, Acv=Ag
            )
        else:
            # Calcular sigma_max usando propiedades geométricas de la entidad
            Pu_N = abs(Pu) * TONF_TO_N
            Mu_Nmm = abs(Mu) * TONFM_TO_NMM
            sigma_max = (Pu_N / Ag + Mu_Nmm * pier.y_extreme / pier.Ig) if Ag > 0 and pier.Ig > 0 else 0

            return self._boundary.verify_boundary_element(
                method=BoundaryElementMethod.STRESS,
                lw=pier.length, c=c or pier.length / 4, hu=pier.height,
                fc=pier.fc, fyt=pier.fy, Ag=Ag, Ach=Ach,
                b=pier.thickness, Mu=Mu, Vu=Vu, sigma_max=sigma_max
            )

    def get_boundary_element_dict(
        self,
        pier: 'VerticalElement',
        Pu: float,
        Mu: float
    ) -> Dict[str, Any]:
        """Obtiene la verificación de elemento de borde como diccionario."""
        result = self.check_boundary_element(pier, Pu, Mu)
        response = {
            'required': result.requires_special,
            'method': result.method.value,
            'aci_reference': result.aci_reference,
            'warnings': result.warnings,
        }
        if result.stress_check:
            response['stress_check'] = {
                'sigma_max': round(result.stress_check.sigma_max, 2),
                'limit': round(result.stress_check.limit_require, 2),
                'fc': result.stress_check.fc,
            }
        if result.displacement_check:
            response['displacement_check'] = {
                'drift_ratio': result.displacement_check.drift_ratio,
                'limit': result.displacement_check.limit,
                'check_value': result.displacement_check.check_value,
            }
        if result.dimensions:
            response['dimensions'] = {
                'length_horizontal_mm': result.dimensions.length_horizontal,
                'width_min_mm': result.dimensions.width_min,
                'vertical_extension_mm': result.dimensions.vertical_extension,
            }
        if result.transverse_reinforcement:
            response['reinforcement'] = {
                'Ash_sbc': result.transverse_reinforcement.Ash_sbc_required,
                'spacing_max_mm': result.transverse_reinforcement.spacing_max,
                'hx_max_mm': result.transverse_reinforcement.hx_max,
            }
        return response

    # =========================================================================
    # VERIFICACIÓN COMPLETA
    # =========================================================================

    def check_complete(
        self,
        pier: 'VerticalElement',
        pier_forces: Optional[ElementForces],
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """Realiza verificación completa del pier incluyendo todas las mejoras ACI 318-25."""
        classification = self.get_classification_dict(pier)
        shear_result = self.check_shear(pier, pier_forces)

        Vu_max = shear_result.get('Vu_2', 0)
        amplification = self.get_amplification_dict(pier, Vu_max, hwcs=hwcs, hn_ft=hn_ft)

        boundary = None
        if pier_forces and pier_forces.combinations:
            for combo in pier_forces.combinations:
                if combo.name == shear_result.get('critical_combo'):
                    Pu = -combo.P
                    Mu = abs(combo.M3)
                    boundary = self.get_boundary_element_dict(pier, Pu, Mu)
                    break

        return {
            'classification': classification,
            'shear': shear_result,
            'amplification': amplification,
            'boundary_element': boundary,
        }

    # =========================================================================
    # VIGAS DE ACOPLAMIENTO (§18.10.7)
    # =========================================================================

    def check_coupling_beam(
        self,
        ln: float, h: float, bw: float, Vu: float,
        fc: float, fy_diagonal: float, fyt: float,
        lambda_factor: float = 1.0
    ) -> CouplingBeamDesignResult:
        """Verifica viga de acoplamiento según ACI 318-25 §18.10.7."""
        return self._coupling.design_coupling_beam(
            ln=ln, h=h, bw=bw, Vu=Vu,
            fc=fc, fy_diagonal=fy_diagonal, fyt=fyt,
            lambda_factor=lambda_factor
        )

    def get_coupling_beam_dict(
        self,
        ln: float, h: float, bw: float, Vu: float,
        fc: float, fy_diagonal: float, fyt: float
    ) -> Dict[str, Any]:
        """Obtiene la verificación de viga de acople como diccionario."""
        result = self.check_coupling_beam(ln, h, bw, Vu, fc, fy_diagonal, fyt)
        response = {
            'beam_type': result.classification.beam_type.value,
            'ln_h_ratio': round(result.classification.ln_h_ratio, 2),
            'reinforcement_type': result.reinforcement_type.value,
            'Vu': result.Vu,
            'phi_Vn': result.phi_Vn,
            'dcr': result.dcr,
            'is_ok': result.is_ok,
            'warnings': result.warnings,
            'aci_reference': result.aci_reference,
        }
        if result.shear_result:
            response['shear'] = {
                'Avd': result.shear_result.Avd,
                'alpha_deg': result.shear_result.alpha_deg,
                'Vn_calc': result.shear_result.Vn_calc,
                'Vn_max': result.shear_result.Vn_max,
                'phi_Vn': result.shear_result.phi_Vn,
            }
        if result.confinement:
            response['confinement'] = {
                'option': result.confinement.confinement_option.value,
                'Ash_required': result.confinement.Ash_required,
                'spacing_max': result.confinement.spacing_max,
            }
        return response

