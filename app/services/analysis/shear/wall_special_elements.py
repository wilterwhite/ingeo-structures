# app/services/analysis/shear/wall_special_elements.py
"""
Servicios para elementos especiales de muros segun ACI 318-25.

Contiene:
- WallClassificationService: Clasificacion §18.10.8
- ShearAmplificationService: Amplificacion §18.10.3.3
- BoundaryElementService: Elementos de borde §18.10.6
- CouplingBeamService: Vigas de acoplamiento §18.10.7
"""
from typing import Dict, Any, Optional

from ....domain.entities import Pier, PierForces
from ....domain.shear import (
    WallClassificationService as DomainWallClassificationService,
    WallClassification,
)
from ....domain.chapter18 import (
    ShearAmplificationService as DomainShearAmplificationService,
    BoundaryElementService as DomainBoundaryElementService,
    BoundaryElementMethod,
    BoundaryElementResult,
    CouplingBeamService as DomainCouplingBeamService,
    CouplingBeamDesignResult,
)
from ....domain.chapter18.design_forces import ShearAmplificationResult
from ....domain.constants.units import TONF_TO_N, TONFM_TO_NMM


class WallClassificationService:
    """
    Servicio para clasificacion de muros segun ACI 318-25 §18.10.8.

    Determina si el elemento es:
    - Columna (lw/tw < 4)
    - Muro estructural (lw/tw >= 4, hw/lw >= 2.0)
    - Pilar de muro con requisitos de columna (hw/lw < 2.0, lw/tw <= 2.5)
    - Pilar de muro con metodo alternativo (hw/lw < 2.0, 2.5 < lw/tw <= 6.0)
    - Muro rechoncho (hw/lw < 2.0, lw/tw > 6.0)
    """

    def __init__(self):
        self._domain_service = DomainWallClassificationService()

    def classify_wall(self, pier: Pier) -> WallClassification:
        """
        Clasifica un pier segun ACI 318-25 §18.10.8.

        Args:
            pier: Pier a clasificar

        Returns:
            WallClassification con tipo y requisitos aplicables
        """
        return self._domain_service.classify(
            lw=pier.width,
            tw=pier.thickness,
            hw=pier.height
        )

    def get_classification_dict(self, pier: Pier) -> Dict[str, Any]:
        """
        Obtiene la clasificacion del pier como diccionario.

        Args:
            pier: Pier a clasificar

        Returns:
            Dict con informacion de clasificacion
        """
        classification = self.classify_wall(pier)
        return {
            'type': classification.element_type.value,
            'lw_tw': round(classification.lw_tw, 2),
            'hw_lw': round(classification.hw_lw, 2),
            'aci_section': classification.aci_section,
            'design_method': classification.design_method,
            'special_requirements': classification.special_requirements,
            'is_wall_pier': self._domain_service.is_wall_pier(classification),
            'requires_column_detailing': self._domain_service.requires_column_detailing(classification),
            'is_squat': self._domain_service.is_squat_wall(classification)
        }

    def is_wall_pier(self, classification: WallClassification) -> bool:
        """Verifica si es un pilar de muro."""
        return self._domain_service.is_wall_pier(classification)

    def requires_column_detailing(self, classification: WallClassification) -> bool:
        """Verifica si requiere detallado de columna."""
        return self._domain_service.requires_column_detailing(classification)


class ShearAmplificationService:
    """
    Servicio para amplificacion de cortante sismico segun ACI 318-25 §18.10.3.3.

    Ve = Omega_v x omega_v x VuEh
    """

    def __init__(self):
        self._domain_service = DomainShearAmplificationService()
        self._classification_service = WallClassificationService()

    def amplify_shear(
        self,
        pier: Pier,
        Vu: float,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        use_omega_0: bool = False,
        omega_0: float = 2.5
    ) -> ShearAmplificationResult:
        """
        Amplifica el cortante sismico segun ACI 318-25 §18.10.3.3.

        Args:
            pier: Pier a verificar
            Vu: Cortante del analisis debido a sismo (tonf)
            hwcs: Altura desde seccion critica (mm), opcional
            hn_ft: Altura total del edificio (pies), opcional
            use_omega_0: Si usar Omega_0 en lugar de Omega_v x omega_v
            omega_0: Factor de sobrerresistencia del sistema (default 2.5)

        Returns:
            ShearAmplificationResult con cortante amplificado
        """
        hwcs_value = hwcs if hwcs is not None and hwcs > 0 else pier.height

        # Verificar si debe amplificar
        classification = self._classification_service.classify_wall(pier)
        is_wall_pier = self._classification_service.is_wall_pier(classification)

        if not self._domain_service.should_amplify(is_wall_pier=is_wall_pier):
            return ShearAmplificationResult(
                Vu_original=Vu,
                Ve=Vu,
                Omega_v=1.0,
                omega_v_dyn=1.0,
                amplification=1.0,
                hwcs_lw=hwcs_value / pier.width if pier.width > 0 else 0,
                hn_ft=None,
                applies=False,
                aci_reference="No aplica: pilar de muro o viga de acoplamiento"
            )

        return self._domain_service.calculate_amplified_shear(
            Vu=Vu,
            hwcs=hwcs_value,
            lw=pier.width,
            hn_ft=hn_ft,
            use_omega_0=use_omega_0,
            omega_0=omega_0
        )

    def get_amplification_dict(
        self,
        pier: Pier,
        Vu: float,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la amplificacion de cortante como diccionario.

        Args:
            pier: Pier a verificar
            Vu: Cortante del analisis (tonf)
            hwcs: Altura desde seccion critica (mm), opcional
            hn_ft: Altura total del edificio (pies), opcional

        Returns:
            Dict con informacion de amplificacion
        """
        result = self.amplify_shear(pier, Vu, hwcs=hwcs, hn_ft=hn_ft)
        return {
            'Vu_original': round(result.Vu_original, 2),
            'Ve': round(result.Ve, 2),
            'Omega_v': round(result.Omega_v, 3),
            'omega_v_dyn': round(result.omega_v_dyn, 3),
            'amplification': round(result.amplification, 3),
            'hwcs_lw': round(result.hwcs_lw, 2),
            'applies': result.applies,
            'aci_reference': result.aci_reference
        }


class BoundaryElementService:
    """
    Servicio para verificacion de elementos de borde segun ACI 318-25 §18.10.6.

    Dos metodos disponibles:
    - Desplazamiento (§18.10.6.2): Para muros con hwcs/lw >= 2.0
    - Esfuerzos (§18.10.6.3): Metodo tradicional, mas conservador
    """

    def __init__(self):
        self._domain_service = DomainBoundaryElementService()

    def check_boundary_element(
        self,
        pier: Pier,
        Pu: float,
        Mu: float,
        c: Optional[float] = None,
        delta_u: Optional[float] = None,
        Vu: float = 0,
        method: str = 'auto'
    ) -> BoundaryElementResult:
        """
        Verifica si se requiere elemento de borde segun ACI 318-25 §18.10.6.

        Args:
            pier: Pier a verificar
            Pu: Carga axial factorizada (tonf, positivo = compresion)
            Mu: Momento factorizado (tonf-m)
            c: Profundidad del eje neutro (mm)
            delta_u: Desplazamiento de diseno (mm)
            Vu: Cortante (tonf), para extension vertical
            method: 'displacement', 'stress', o 'auto'

        Returns:
            BoundaryElementResult con verificacion completa
        """
        hwcs_lw = pier.height / pier.width if pier.width > 0 else 0

        # Determinar metodo
        if method == 'auto':
            if hwcs_lw >= 2.0 and c and delta_u:
                use_method = BoundaryElementMethod.DISPLACEMENT
            else:
                use_method = BoundaryElementMethod.STRESS
        elif method == 'displacement':
            use_method = BoundaryElementMethod.DISPLACEMENT
        else:
            use_method = BoundaryElementMethod.STRESS

        # Calcular propiedades
        Ag = pier.width * pier.thickness
        Ach = Ag * 0.85

        if use_method == BoundaryElementMethod.DISPLACEMENT and c and delta_u:
            return self._domain_service.verify_boundary_element(
                method=use_method,
                lw=pier.width,
                c=c,
                hu=pier.height,
                fc=pier.fc,
                fyt=pier.fy,
                Ag=Ag,
                Ach=Ach,
                b=pier.thickness,
                delta_u=delta_u,
                hwcs=pier.height,
                Mu=Mu,
                Vu=Vu,
                Ve=Vu,
                Acv=Ag
            )
        else:
            # Calcular sigma_max usando propiedades de seccion bruta
            Ig = pier.thickness * pier.width**3 / 12
            y = pier.width / 2
            Pu_N = abs(Pu) * TONF_TO_N
            Mu_Nmm = abs(Mu) * TONFM_TO_NMM
            sigma_max = (Pu_N / Ag + Mu_Nmm * y / Ig) if Ag > 0 and Ig > 0 else 0

            return self._domain_service.verify_boundary_element(
                method=BoundaryElementMethod.STRESS,
                lw=pier.width,
                c=c or pier.width / 4,
                hu=pier.height,
                fc=pier.fc,
                fyt=pier.fy,
                Ag=Ag,
                Ach=Ach,
                b=pier.thickness,
                Mu=Mu,
                Vu=Vu,
                sigma_max=sigma_max
            )

    def get_boundary_element_dict(
        self,
        pier: Pier,
        Pu: float,
        Mu: float
    ) -> Dict[str, Any]:
        """
        Obtiene la verificacion de elemento de borde como diccionario.

        Args:
            pier: Pier a verificar
            Pu: Carga axial (tonf)
            Mu: Momento (tonf-m)

        Returns:
            Dict con informacion de elemento de borde
        """
        result = self.check_boundary_element(pier, Pu, Mu)

        response = {
            'required': result.requires_special,
            'method': result.method.value,
            'aci_reference': result.aci_reference,
            'warnings': result.warnings
        }

        if result.stress_check:
            response['stress_check'] = {
                'sigma_max': round(result.stress_check.sigma_max, 2),
                'limit': round(result.stress_check.limit_require, 2),
                'fc': result.stress_check.fc
            }

        if result.displacement_check:
            response['displacement_check'] = {
                'drift_ratio': result.displacement_check.drift_ratio,
                'limit': result.displacement_check.limit,
                'check_value': result.displacement_check.check_value
            }

        if result.dimensions:
            response['dimensions'] = {
                'length_horizontal_mm': result.dimensions.length_horizontal,
                'width_min_mm': result.dimensions.width_min,
                'vertical_extension_mm': result.dimensions.vertical_extension
            }

        if result.transverse_reinforcement:
            response['reinforcement'] = {
                'Ash_sbc': result.transverse_reinforcement.Ash_sbc_required,
                'spacing_max_mm': result.transverse_reinforcement.spacing_max,
                'hx_max_mm': result.transverse_reinforcement.hx_max
            }

        return response


class CouplingBeamService:
    """
    Servicio para vigas de acoplamiento segun ACI 318-25 §18.10.7.

    Clasifica la viga por ln/h y determina el tipo de refuerzo:
    - ln/h < 2: Requiere refuerzo diagonal
    - ln/h >= 4: Puede usar refuerzo longitudinal convencional
    - 2 <= ln/h < 4: Cualquiera de los dos
    """

    def __init__(self):
        self._domain_service = DomainCouplingBeamService()

    def check_coupling_beam(
        self,
        ln: float,
        h: float,
        bw: float,
        Vu: float,
        fc: float,
        fy_diagonal: float,
        fyt: float,
        lambda_factor: float = 1.0
    ) -> CouplingBeamDesignResult:
        """
        Verifica viga de acoplamiento segun ACI 318-25 §18.10.7.

        Args:
            ln: Claro libre de la viga (mm)
            h: Peralte de la viga (mm)
            bw: Ancho de la viga (mm)
            Vu: Cortante ultimo (tonf)
            fc: f'c del hormigon (MPa)
            fy_diagonal: Fluencia del refuerzo diagonal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            lambda_factor: Factor para concreto liviano (default 1.0)

        Returns:
            CouplingBeamDesignResult con diseno completo
        """
        return self._domain_service.design_coupling_beam(
            ln=ln,
            h=h,
            bw=bw,
            Vu=Vu,
            fc=fc,
            fy_diagonal=fy_diagonal,
            fyt=fyt,
            lambda_factor=lambda_factor
        )

    def get_coupling_beam_dict(
        self,
        ln: float,
        h: float,
        bw: float,
        Vu: float,
        fc: float,
        fy_diagonal: float,
        fyt: float
    ) -> Dict[str, Any]:
        """
        Obtiene la verificacion de viga de acople como diccionario.

        Args:
            ln: Claro libre de la viga (mm)
            h: Peralte de la viga (mm)
            bw: Ancho de la viga (mm)
            Vu: Cortante ultimo (tonf)
            fc: f'c del hormigon (MPa)
            fy_diagonal: Fluencia del refuerzo diagonal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)

        Returns:
            Dict con informacion de la viga de acoplamiento
        """
        result = self.check_coupling_beam(
            ln=ln, h=h, bw=bw, Vu=Vu,
            fc=fc, fy_diagonal=fy_diagonal, fyt=fyt
        )

        response = {
            'beam_type': result.classification.beam_type.value,
            'ln_h_ratio': round(result.classification.ln_h_ratio, 2),
            'reinforcement_type': result.reinforcement_type.value,
            'Vu': result.Vu,
            'phi_Vn': result.phi_Vn,
            'dcr': result.dcr,
            'is_ok': result.is_ok,
            'warnings': result.warnings,
            'aci_reference': result.aci_reference
        }

        if result.shear_result:
            response['shear'] = {
                'Avd': result.shear_result.Avd,
                'alpha_deg': result.shear_result.alpha_deg,
                'Vn_calc': result.shear_result.Vn_calc,
                'Vn_max': result.shear_result.Vn_max,
                'phi_Vn': result.shear_result.phi_Vn
            }

        if result.confinement:
            response['confinement'] = {
                'option': result.confinement.confinement_option.value,
                'Ash_required': result.confinement.Ash_required,
                'spacing_max': result.confinement.spacing_max
            }

        return response
