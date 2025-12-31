# app/services/analysis/shear_service.py
"""
Servicio de verificacion de corte para piers.

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
- Capitulo 22: Resistencia al corte general (columnas/vigas)
"""
from typing import Dict, Any, Optional, List, Tuple

from ...domain.entities import Pier, PierForces
from ...domain.shear import (
    ShearVerificationService,
    WallGroupShearResult,
    WallClassificationService,
    WallClassification,
    ElementType,
)
from ...domain.chapter18 import (
    ShearAmplificationService,
    BoundaryElementService,
    BoundaryElementMethod,
    BoundaryElementResult,
)
from ...domain.chapter18.amplification import ShearAmplificationResult


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

    def check_shear(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces]
    ) -> Dict[str, Any]:
        """
        Verifica corte con interacción V2-V3 y retorna el caso crítico.

        Para cada combinación de cargas, V2 y V3 actúan simultáneamente.
        La interacción se verifica como:
        DCR = sqrt((Vu2/φVn2)² + (Vu3/φVn3)²) ≤ 1.0
        SF = 1/DCR

        También verifica cuantía mínima según §18.10.4.3.

        Args:
            pier: Pier a verificar
            pier_forces: Fuerzas del pier (combinaciones)

        Returns:
            Dict con resultados de la verificación de corte incluyendo:
            - sf: Factor de seguridad mínimo
            - status: "OK" o "NO OK"
            - rho_check_ok: Cumple §18.10.4.3
            - rho_warning: Mensaje de advertencia si no cumple
            - aci_reference: Referencia ACI usada
        """
        if not pier_forces or not pier_forces.combinations:
            return {
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
                'Vc': 0,
                'Vs': 0,
                'alpha_c': 0,
                'formula_type': 'N/A',
                'rho_check_ok': True,
                'rho_warning': '',
                'aci_reference': ''
            }

        # Variables para tracking del caso crítico
        min_sf = float('inf')
        critical_result = None
        critical_combo_name = ''

        # Obtener cuantía vertical del pier para verificación §18.10.4.3
        rho_v = pier.rho_vertical

        # Iterar por cada combinación
        for combo in pier_forces.combinations:
            P = -combo.P  # Positivo = compresión
            Vu2 = abs(combo.V2)
            Vu3 = abs(combo.V3)

            # Verificar corte combinado para esta combinación
            # Incluye rho_v para verificar §18.10.4.3
            combined_result = self._shear_verification.verify_combined_shear(
                lw=pier.width,
                tw=pier.thickness,
                hw=pier.height,
                fc=pier.fc,
                fy=pier.fy,
                rho_h=pier.rho_horizontal,
                Vu2=Vu2,
                Vu3=Vu3,
                Nu=P,
                combo_name=combo.name,
                rho_v=rho_v  # Nuevo: para verificar cuantía mínima
            )

            # Actualizar si es más crítico (menor SF = mayor DCR)
            if combined_result.sf < min_sf:
                min_sf = combined_result.sf
                critical_result = combined_result
                critical_combo_name = combo.name

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
            'Vc': critical_result.result_V2.Vc if critical_result else 0,
            'Vs': critical_result.result_V2.Vs if critical_result else 0,
            'alpha_c': critical_result.result_V2.alpha_c if critical_result else 0,
            'formula_type': critical_result.result_V2.formula_type if critical_result else 'N/A',
            # Nuevos campos para cuantía mínima §18.10.4.3
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
                omega_v=1.0,
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
