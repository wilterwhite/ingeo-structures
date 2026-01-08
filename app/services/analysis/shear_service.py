# app/services/analysis/shear_service.py
"""
Servicio de verificacion de corte para piers y columnas.

Maneja la verificacion de corte V2-V3 con interaccion segun ACI 318-25.

Referencias ACI 318-25:
- Capitulo 11: Muros (Walls)
  - 11.5.4: Cortante en el plano
  - 11.6.2: Cuantia minima para cortante alto
- Capitulo 18: Muros estructurales especiales
  - 18.10.3.3: Amplificacion de cortante
  - 18.10.4: Resistencia al corte
  - 18.10.4.3: Cuantia minima (rho_v >= rho_h cuando hw/lw <= 2.0)
  - 18.10.6: Elementos de borde
  - 18.10.8: Pilares de muro (wall piers)
  - 18.7.6: Cortante de diseño para columnas sismicas especiales
- Capitulo 22: Resistencia al corte general (columnas/vigas no sismicas)
  - 22.5: Resistencia al cortante
"""
import math
from typing import Dict, Any, Optional, List, Tuple, Union

from ...domain.entities import Pier, PierForces, Column, ColumnForces
from ...domain.shear import (
    ShearVerificationService,
    WallGroupShearResult,
    WallClassificationService,
    WallClassification,
    ElementType,
)
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
from ...domain.chapter18 import (
    ShearAmplificationService,
    BoundaryElementService,
    BoundaryElementMethod,
    BoundaryElementResult,
    CouplingBeamService,
    CouplingBeamDesignResult,
)
from ...domain.chapter18.design_forces import ShearAmplificationResult
from ...domain.chapter18.wall_piers.shear_design import calculate_design_shear


class ShearService:
    """
    Servicio para verificación de corte de piers según ACI 318-25.

    Responsabilidades:
    - Verificar corte con interacción V2-V3
    - Encontrar la combinación crítica
    - Calcular factores de seguridad
    - Verificar cuantía mínima §18.10.4.3
    - Verificar grupos de segmentos §18.10.4.4
    - Clasificar muros y pilares de muro §18.10.8
    - Amplificar cortante para muros especiales §18.10.3.3
    - Verificar elementos de borde §18.10.6
    """

    def __init__(self):
        self._shear_verification = ShearVerificationService()
        self._wall_classification = WallClassificationService()
        self._shear_amplification = ShearAmplificationService()
        self._boundary_element = BoundaryElementService()
        self._coupling_beam = CouplingBeamService()

    def check_shear(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        Mpr_total: float = 0,
        lu: float = 0,
        lambda_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Verifica corte con interacción V2-V3 y retorna el caso crítico.

        Para cada combinación de cargas, V2 y V3 actúan simultáneamente.
        La interacción se verifica como:
        DCR = sqrt((Vu2/φVn2)² + (Vu3/φVn3)²) ≤ 1.0
        SF = 1/DCR

        Para pilares de muro con vigas de acople (§18.10.8.1(a), §18.7.6.1):
        Ve = Mpr_total / lu (diseño por capacidad)
        Ve = min(Ve, Ω₀ × Vu) donde Ω₀ = 3.0

        Args:
            pier: Pier a verificar
            pier_forces: Fuerzas del pier (combinaciones)
            Mpr_total: Momento probable total de vigas de acople (kN-m)
            lu: Altura libre del pier (mm)
            lambda_factor: Factor de concreto liviano (1.0=normal, 0.85=arena, 0.75=todo liviano)

        Returns:
            Dict con resultados de la verificación de corte
        """
        # Resultado por defecto cuando no hay fuerzas
        default_result = {
            'sf': float('inf'),
            'status': 'OK',
            'critical_combo': 'N/A',
            'dcr_2': 0,
            'dcr_3': 0,
            'dcr_combined': 0,
            'phi_Vn_2': 0,
            'phi_Vn_3': 0,
            'Vu_2': 0,
            'Vu_3': 0,
            'Ve': 0,
            'uses_capacity_design': False,
            'Vc': 0,
            'Vs': 0,
            'alpha_c': 0,
            'formula_type': 'N/A',
            'rho_check_ok': True,
            'rho_warning': '',
            'aci_reference': ''
        }

        if not pier_forces or not pier_forces.combinations:
            return default_result

        # Clasificar elemento (para información, no para decidir diseño por capacidad)
        classification = self.classify_wall(pier)

        # Convertir Mpr_total de kN-m a tonf-m para usar función de chapter18
        Mpr_total_tonf_m = Mpr_total / 9.80665 if Mpr_total > 0 else 0

        # Variables para tracking del caso crítico
        min_sf = float('inf')
        critical_result = None
        critical_combo_name = ''
        Ve_used = 0
        use_capacity_design = False

        # Obtener cuantía vertical del pier para verificación §18.10.4.3
        rho_v = pier.rho_vertical

        # Iterar por cada combinación
        for combo in pier_forces.combinations:
            P = -combo.P  # Positivo = compresión
            Vu2 = abs(combo.V2)
            Vu3 = abs(combo.V3)
            Vu_max = max(Vu2, Vu3)

            # Calcular Ve usando función centralizada de chapter18
            # Aplica diseño por capacidad si Mpr_total > 0 y lu > 0
            # Según ACI 318-25 §18.7.6.1 (columnas) y §18.10.8.1(a) (wall piers)
            design_shear = calculate_design_shear(
                Vu=Vu_max,
                lu=lu,
                Mpr_total=Mpr_total_tonf_m,
                Omega_o=3.0
            )

            Ve = design_shear.Ve
            use_capacity_design = design_shear.use_capacity_design

            # Determinar cortantes a verificar
            if use_capacity_design:
                # Usar Ve para ambas direcciones (conservador)
                Vu2_check = Ve if Vu2 > 0 else 0
                Vu3_check = Ve if Vu3 > 0 else 0
            else:
                Vu2_check = Vu2
                Vu3_check = Vu3

            # Verificar corte combinado para esta combinación
            combined_result = self._shear_verification.verify_combined_shear(
                lw=pier.width,
                tw=pier.thickness,
                hw=pier.height,
                fc=pier.fc,
                fy=pier.fy,
                rho_h=pier.rho_horizontal,
                Vu2=Vu2_check,
                Vu3=Vu3_check,
                Nu=P,
                combo_name=combo.name,
                rho_v=rho_v,
                lambda_factor=lambda_factor
            )

            # Actualizar si es más crítico (menor SF = mayor DCR)
            if combined_result.sf < min_sf:
                min_sf = combined_result.sf
                critical_result = combined_result
                critical_combo_name = combo.name
                Ve_used = Ve if use_capacity_design else 0

        status = "OK" if min_sf >= 1.0 else "NO OK"

        # Obtener información de verificación de cuantía del resultado crítico
        rho_check_ok = True
        rho_warning = ''
        aci_reference = ''
        if critical_result:
            rho_check_ok = critical_result.result_V2.rho_check_ok
            rho_warning = critical_result.result_V2.rho_warning
            aci_reference = critical_result.result_V2.aci_reference

        return {
            'sf': min_sf,
            'status': status,
            'critical_combo': critical_combo_name,
            'dcr_2': critical_result.dcr_2 if critical_result else 0,
            'dcr_3': critical_result.dcr_3 if critical_result else 0,
            'dcr_combined': critical_result.dcr_combined if critical_result else 0,
            'phi_Vn_2': critical_result.result_V2.phi_Vn if critical_result else 0,
            'phi_Vn_3': critical_result.result_V3.phi_Vn if critical_result else 0,
            'Vu_2': critical_result.result_V2.Vu if critical_result else 0,
            'Vu_3': critical_result.result_V3.Vu if critical_result else 0,
            'Ve': round(Ve_used, 2),
            'uses_capacity_design': use_capacity_design,
            'Vc': critical_result.result_V2.Vc if critical_result else 0,
            'Vs': critical_result.result_V2.Vs if critical_result else 0,
            'alpha_c': critical_result.result_V2.alpha_c if critical_result else 0,
            'formula_type': critical_result.result_V2.formula_type if critical_result else 'N/A',
            'rho_check_ok': rho_check_ok,
            'rho_warning': rho_warning,
            'aci_reference': aci_reference
        }

    def get_shear_capacity(
        self,
        pier: Pier,
        Nu: float = 0
    ) -> Dict[str, Any]:
        """
        Calcula las capacidades de corte puro del pier.

        Args:
            pier: Pier a analizar
            Nu: Carga axial (tonf, positivo = compresión)

        Returns:
            Dict con capacidades φVn2, φVn3 y verificación de cuantía
        """
        # Obtener cuantía vertical para verificación §18.10.4.3
        rho_v = pier.rho_vertical

        shear_V2, shear_V3 = self._shear_verification.verify_bidirectional_shear(
            lw=pier.width,
            tw=pier.thickness,
            hw=pier.height,
            fc=pier.fc,
            fy=pier.fy,
            rho_h=pier.rho_horizontal,
            Vu2_max=1.0,  # Valor dummy
            Vu3_max=1.0,
            Nu=Nu,
            rho_v=rho_v  # Para verificar cuantía mínima
        )

        return {
            'phi_Vn_2': round(shear_V2.phi_Vn, 1),
            'phi_Vn_3': round(shear_V3.phi_Vn, 1),
            'Vc_2': round(shear_V2.Vc, 2),
            'Vc_3': round(shear_V3.Vc, 2),
            'Vs_2': round(shear_V2.Vs, 2),
            'Vs_3': round(shear_V3.Vs, 2),
            'rho_check_ok': shear_V2.rho_check_ok,
            'rho_warning': shear_V2.rho_warning,
            'aci_reference': shear_V2.aci_reference
        }

    def verify_bidirectional_shear(
        self,
        lw: float,
        tw: float,
        hw: float,
        fc: float,
        fy: float,
        rho_h: float,
        Vu2_max: float,
        Vu3_max: float,
        Nu: float = 0,
        rho_v: Optional[float] = None
    ):
        """
        Expone el método de verificación bidireccional del servicio de dominio.

        Args:
            lw: Largo del muro (mm)
            tw: Espesor del muro (mm)
            hw: Altura del muro (mm)
            fc: f'c del hormigón (MPa)
            fy: fy del acero (MPa)
            rho_h: Cuantía horizontal
            Vu2_max: Corte máximo V2 (tonf)
            Vu3_max: Corte máximo V3 (tonf)
            Nu: Carga axial (tonf, positivo = compresión)
            rho_v: Cuantía vertical (opcional, para §18.10.4.3)

        Returns:
            Tuple (ShearResult_V2, ShearResult_V3)
        """
        return self._shear_verification.verify_bidirectional_shear(
            lw=lw, tw=tw, hw=hw, fc=fc, fy=fy, rho_h=rho_h,
            Vu2_max=Vu2_max, Vu3_max=Vu3_max, Nu=Nu, rho_v=rho_v
        )

    def verify_wall_group(
        self,
        segments: List[Tuple[float, float, float]],
        fc: float,
        fy: float,
        rho_h: float,
        Vu_total: float,
        Nu: float = 0,
        rho_v: Optional[float] = None
    ) -> WallGroupShearResult:
        """
        Verifica un grupo de segmentos de muro según ACI 318-14 §18.10.4.4.

        Para segmentos verticales coplanares que resisten una fuerza
        lateral común, la suma de sus Vn no debe exceder:
        Vn_grupo ≤ 0.66 × √f'c × Acv_total

        Aplicaciones:
        - Muros con aberturas (ventanas, puertas)
        - Muros acoplados por vigas
        - Grupos de muros trabajando juntos

        Args:
            segments: Lista de tuplas (lw, tw, hw) para cada segmento en mm
            fc: Resistencia del hormigón f'c (MPa)
            fy: Fluencia del acero (MPa)
            rho_h: Cuantía horizontal común
            Vu_total: Demanda de corte total del grupo (tonf)
            Nu: Carga axial total (tonf)
            rho_v: Cuantía vertical (opcional, para §18.10.4.3)

        Returns:
            WallGroupShearResult con resultados del grupo
        """
        return self._shear_verification.verify_wall_group(
            segments=segments,
            fc=fc,
            fy=fy,
            rho_h=rho_h,
            Vu_total=Vu_total,
            Nu=Nu,
            rho_v=rho_v
        )

    # =========================================================================
    # CLASIFICACION DE MUROS (§18.10.8)
    # =========================================================================

    def classify_wall(self, pier: Pier) -> WallClassification:
        """
        Clasifica un pier según ACI 318-25 §18.10.8.

        Determina si el elemento es:
        - Columna (lw/tw < 4)
        - Muro estructural (lw/tw >= 4, hw/lw >= 2.0)
        - Pilar de muro con requisitos de columna (hw/lw < 2.0, lw/tw <= 2.5)
        - Pilar de muro con método alternativo (hw/lw < 2.0, 2.5 < lw/tw <= 6.0)
        - Muro rechoncho (hw/lw < 2.0, lw/tw > 6.0)

        Args:
            pier: Pier a clasificar

        Returns:
            WallClassification con tipo y requisitos aplicables
        """
        return self._wall_classification.classify(
            lw=pier.width,
            tw=pier.thickness,
            hw=pier.height
        )

    def get_classification_dict(self, pier: Pier) -> Dict[str, Any]:
        """
        Obtiene la clasificación del pier como diccionario.

        Args:
            pier: Pier a clasificar

        Returns:
            Dict con información de clasificación
        """
        classification = self.classify_wall(pier)
        return {
            'type': classification.element_type.value,
            'lw_tw': round(classification.lw_tw, 2),
            'hw_lw': round(classification.hw_lw, 2),
            'aci_section': classification.aci_section,
            'design_method': classification.design_method,
            'special_requirements': classification.special_requirements,
            'is_wall_pier': self._wall_classification.is_wall_pier(classification),
            'requires_column_detailing': self._wall_classification.requires_column_detailing(classification),
            'is_squat': self._wall_classification.is_squat_wall(classification)
        }

    # =========================================================================
    # AMPLIFICACION DE CORTANTE (§18.10.3.3)
    # =========================================================================

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
        Amplifica el cortante sísmico según ACI 318-25 §18.10.3.3.

        Ve = Ωv × ωv × VuEh

        Args:
            pier: Pier a verificar
            Vu: Cortante del análisis debido a sismo (tonf)
            hwcs: Altura desde sección crítica (mm), opcional (default: pier.height)
            hn_ft: Altura total del edificio (pies), opcional
            use_omega_0: Si usar Ω₀ en lugar de Ωv × ωv
            omega_0: Factor de sobrerresistencia del sistema (default 2.5)

        Returns:
            ShearAmplificationResult con cortante amplificado
        """
        # Usar hwcs proporcionado o altura del pier
        hwcs_value = hwcs if hwcs is not None and hwcs > 0 else pier.height

        # Verificar si debe amplificar
        classification = self.classify_wall(pier)
        is_wall_pier = self._wall_classification.is_wall_pier(classification)

        if not self._shear_amplification.should_amplify(
            is_wall_pier=is_wall_pier
        ):
            # No amplifica, retornar valores sin amplificar
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

        return self._shear_amplification.calculate_amplified_shear(
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
        Obtiene la amplificación de cortante como diccionario.

        Args:
            pier: Pier a verificar
            Vu: Cortante del análisis (tonf)
            hwcs: Altura desde sección crítica (mm), opcional
            hn_ft: Altura total del edificio (pies), opcional

        Returns:
            Dict con información de amplificación
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

    # =========================================================================
    # ELEMENTOS DE BORDE (§18.10.6)
    # =========================================================================

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
        Verifica si se requiere elemento de borde según ACI 318-25 §18.10.6.

        Dos métodos disponibles:
        - Desplazamiento (§18.10.6.2): Para muros con hwcs/lw >= 2.0
        - Esfuerzos (§18.10.6.3): Método tradicional, más conservador

        Args:
            pier: Pier a verificar
            Pu: Carga axial factorizada (tonf, positivo = compresión)
            Mu: Momento factorizado (tonf-m)
            c: Profundidad del eje neutro (mm), para método de desplazamiento
            delta_u: Desplazamiento de diseño (mm), para método de desplazamiento
            Vu: Cortante (tonf), para extensión vertical
            method: 'displacement', 'stress', o 'auto'

        Returns:
            BoundaryElementResult con verificación completa
        """
        hwcs_lw = pier.height / pier.width if pier.width > 0 else 0

        # Determinar método
        if method == 'auto':
            # Usar desplazamiento si hwcs/lw >= 2.0 y hay datos disponibles
            if hwcs_lw >= 2.0 and c and delta_u:
                use_method = BoundaryElementMethod.DISPLACEMENT
            else:
                use_method = BoundaryElementMethod.STRESS
        elif method == 'displacement':
            use_method = BoundaryElementMethod.DISPLACEMENT
        else:
            use_method = BoundaryElementMethod.STRESS

        # Calcular propiedades para refuerzo transversal
        # Estimar Ach como 85% de Ag (aproximación conservadora)
        Ag = pier.width * pier.thickness
        Ach = Ag * 0.85

        if use_method == BoundaryElementMethod.DISPLACEMENT and c and delta_u:
            return self._boundary_element.verify_boundary_element(
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
            # Calcular sigma_max usando propiedades de sección bruta
            Ig = pier.thickness * pier.width**3 / 12
            y = pier.width / 2
            Pu_N = abs(Pu) * 9806.65
            Mu_Nmm = abs(Mu) * 9806650
            sigma_max = (Pu_N / Ag + Mu_Nmm * y / Ig) if Ag > 0 and Ig > 0 else 0

            return self._boundary_element.verify_boundary_element(
                method=BoundaryElementMethod.STRESS,
                lw=pier.width,
                c=c or pier.width / 4,  # Estimación si no se proporciona
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
        Obtiene la verificación de elemento de borde como diccionario.

        Args:
            pier: Pier a verificar
            Pu: Carga axial (tonf)
            Mu: Momento (tonf-m)

        Returns:
            Dict con información de elemento de borde
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

    # =========================================================================
    # VERIFICACION COMPLETA
    # =========================================================================

    def check_complete(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Realiza verificación completa del pier incluyendo todas las mejoras ACI 318-25.

        Incluye:
        - Clasificación del elemento (§18.10.8)
        - Verificación de cortante con interacción V2-V3
        - Amplificación de cortante (§18.10.3.3)
        - Verificación de elementos de borde (§18.10.6)

        Args:
            pier: Pier a verificar
            pier_forces: Fuerzas del pier
            hwcs: Altura desde sección crítica (mm), opcional
            hn_ft: Altura total del edificio (pies), opcional

        Returns:
            Dict con verificación completa
        """
        # 1. Clasificación
        classification = self.get_classification_dict(pier)

        # 2. Verificación de cortante básica
        shear_result = self.check_shear(pier, pier_forces)

        # 3. Amplificación de cortante (si aplica)
        Vu_max = shear_result.get('Vu_2', 0)
        amplification = self.get_amplification_dict(pier, Vu_max, hwcs=hwcs, hn_ft=hn_ft)

        # 4. Verificación de elementos de borde (si hay fuerzas)
        boundary = None
        if pier_forces and pier_forces.combinations:
            # Obtener cargas críticas
            critical_combo = None
            for combo in pier_forces.combinations:
                if combo.name == shear_result.get('critical_combo'):
                    critical_combo = combo
                    break

            if critical_combo:
                Pu = -critical_combo.P  # Positivo = compresión
                Mu = abs(critical_combo.M3)
                boundary = self.get_boundary_element_dict(pier, Pu, Mu)

        return {
            'classification': classification,
            'shear': shear_result,
            'amplification': amplification,
            'boundary_element': boundary
        }

    # =========================================================================
    # VIGAS DE ACOPLAMIENTO (§18.10.7)
    # =========================================================================

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
        Verifica viga de acoplamiento según ACI 318-25 §18.10.7.

        Clasifica la viga por ln/h y determina el tipo de refuerzo:
        - ln/h < 2: Requiere refuerzo diagonal
        - ln/h >= 4: Puede usar refuerzo longitudinal convencional
        - 2 <= ln/h < 4: Cualquiera de los dos

        Args:
            ln: Claro libre de la viga (mm)
            h: Peralte de la viga (mm)
            bw: Ancho de la viga (mm)
            Vu: Cortante último (tonf)
            fc: f'c del hormigón (MPa)
            fy_diagonal: Fluencia del refuerzo diagonal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)
            lambda_factor: Factor para concreto liviano (default 1.0)

        Returns:
            CouplingBeamDesignResult con diseño completo
        """
        return self._coupling_beam.design_coupling_beam(
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
        Obtiene la verificación de viga de acople como diccionario.

        Args:
            ln: Claro libre de la viga (mm)
            h: Peralte de la viga (mm)
            bw: Ancho de la viga (mm)
            Vu: Cortante último (tonf)
            fc: f'c del hormigón (MPa)
            fy_diagonal: Fluencia del refuerzo diagonal (MPa)
            fyt: Fluencia del refuerzo transversal (MPa)

        Returns:
            Dict con información de la viga de acoplamiento
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

    # =========================================================================
    # CORTANTE DE COLUMNAS (§22.5 y §18.7.6)
    # =========================================================================

    def check_column_shear(
        self,
        column: Column,
        column_forces: Optional[ColumnForces],
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        lambda_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Verifica cortante de una columna según ACI 318-25.

        El método de diseño depende de column.is_seismic:
        - is_seismic=True: §18.7.6 (diseño por capacidad, Ve = Mpr/lu)
        - is_seismic=False: §22.5 (simplificado, Vc = 0.17λ√f'c·bw·d)

        Para diseño sísmico (§18.7.6):
        - Ve = (Mpr_top + Mpr_bottom) / lu
        - Vc = 0 si: (a) cortante sísmico ≥ 0.5Vu Y (b) Pu < Ag·f'c/20

        Args:
            column: Columna a verificar
            column_forces: Fuerzas de la columna
            Mpr_top: Momento probable en nudo superior (tonf-m)
            Mpr_bottom: Momento probable en nudo inferior (tonf-m)
            lambda_factor: Factor para concreto liviano (default 1.0)

        Returns:
            Dict con resultados de verificación de cortante
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
        Verifica cortante de columna NO sísmica según ACI 318-25 §22.5.

        Fórmulas:
        - Vc = 0.17 × λ × √f'c × bw × d  [Ec. 22.5.5.1]
        - Vs = Av × fyt × d / s          [Ec. 22.5.10.5.3]
        - Vn = Vc + Vs
        - φVn (φ = 0.75)

        Args:
            column: Columna a verificar
            column_forces: Fuerzas de la columna
            lambda_factor: Factor para concreto liviano

        Returns:
            Dict con resultados de verificación
        """
        default_result = self._default_column_shear_result('ACI 318-25 §22.5')

        if not column_forces or not column_forces.combinations:
            return default_result

        # Calcular capacidades en ambas direcciones
        cap_V2 = self._calc_column_capacity_simple(column, 'V2', lambda_factor)
        cap_V3 = self._calc_column_capacity_simple(column, 'V3', lambda_factor)

        # Encontrar combinación crítica
        max_dcr = 0
        critical_combo = ''
        critical_Vu2 = 0
        critical_Vu3 = 0
        critical_P = 0

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
                critical_P = -combo.P  # Positivo = compresión

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
        Verifica cortante de columna sísmica especial según ACI 318-25 §18.7.6.

        Diseño por capacidad:
        - Ve = (Mpr_top + Mpr_bottom) / lu  [§18.7.6.1]
        - Vc = 0 si: (a) Ve ≥ 0.5×Vu_max Y (b) Pu < Ag×f'c/20 [§18.7.6.2.1]

        Args:
            column: Columna a verificar
            column_forces: Fuerzas de la columna
            Mpr_top: Momento probable en nudo superior (tonf-m)
            Mpr_bottom: Momento probable en nudo inferior (tonf-m)
            lambda_factor: Factor para concreto liviano

        Returns:
            Dict con resultados de verificación
        """
        default_result = self._default_column_shear_result('ACI 318-25 §18.7.6')

        if not column_forces or not column_forces.combinations:
            return default_result

        lu = column.height  # Altura libre (mm)
        Ag = column.Ag       # Área bruta (mm²)
        fc = column.fc       # f'c (MPa)

        # Calcular Ve si hay momentos probables
        Ve = 0
        use_capacity_design = False
        if Mpr_top > 0 or Mpr_bottom > 0:
            # Ve en tonf: Mpr en tonf-m, lu en mm → convertir
            Ve = (Mpr_top + Mpr_bottom) * 1000 / lu if lu > 0 else 0
            use_capacity_design = True

        # Calcular capacidades base en ambas direcciones
        cap_V2 = self._calc_column_capacity_simple(column, 'V2', lambda_factor)
        cap_V3 = self._calc_column_capacity_simple(column, 'V3', lambda_factor)

        # Encontrar combinación crítica
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
            Pu = -combo.P  # Positivo = compresión (tonf)
            Pu_N = Pu * 9806.65  # Convertir a N

            # Determinar cortante de diseño
            if use_capacity_design:
                Vu2_check = max(Vu2, Ve) if Vu2 > 0 else Ve
                Vu3_check = max(Vu3, Ve) if Vu3 > 0 else Ve
            else:
                Vu2_check = Vu2
                Vu3_check = Vu3

            # Verificar si Vc = 0 según §18.7.6.2.1
            # (a) Cortante sísmico ≥ 0.5 × Vu_max en zona lo
            # (b) Pu < Ag × f'c / 20
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

        V2: Cortante en dirección eje 2 → usa depth como h, width como b
        V3: Cortante en dirección eje 3 → usa width como h, depth como b

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

        # Vc = 0.17 × λ × √f'c × bw × d (N)
        Vc = VC_COEF_COLUMN * lambda_factor * LAMBDA_NORMAL * math.sqrt(fc_eff) * bw * d

        # Vs = Av × fyt × d / s (N)
        if s > 0:
            Vs = Av * fy_eff * d / s
        else:
            Vs = 0

        # Límite de Vs: Vs ≤ 0.66 × √f'c × bw × d
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
        if math.isinf(value):
            return '>100'
        return round(value, 2)

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
            from ...domain.entities import ColumnForces, LoadCombination
            column_forces = ColumnForces(
                column_label=pier.label,
                story=pier.story,
                combinations=pier_forces.combinations
            )

        return self.check_column_shear(
            virtual_column, column_forces,
            lambda_factor=lambda_factor
        )
