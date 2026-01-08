# app/services/analysis/shear/wall_shear.py
"""
Servicio de verificacion de cortante para muros.

Implementa verificacion de cortante segun ACI 318-25:
- §11.5.4: Cortante en el plano
- §18.10.4: Resistencia al corte de muros especiales
- §18.10.4.3: Cuantia minima
- §18.10.4.4: Grupos de segmentos
"""
from typing import Dict, Any, Optional, List, Tuple

from ....domain.entities import Pier, PierForces
from ....domain.shear import (
    ShearVerificationService,
    WallGroupShearResult,
)
from ....domain.chapter18.wall_piers.shear_design import calculate_design_shear


class WallShearService:
    """
    Servicio para verificacion de cortante de muros segun ACI 318-25.

    Responsabilidades:
    - Verificar corte con interaccion V2-V3
    - Encontrar la combinacion critica
    - Calcular factores de seguridad
    - Verificar cuantia minima §18.10.4.3
    - Verificar grupos de segmentos §18.10.4.4
    """

    def __init__(self):
        self._shear_verification = ShearVerificationService()

    def check_shear(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        Mpr_total: float = 0,
        lu: float = 0,
        lambda_factor: float = 1.0,
        classification=None
    ) -> Dict[str, Any]:
        """
        Verifica corte con interaccion V2-V3 y retorna el caso critico.

        Para cada combinacion de cargas, V2 y V3 actuan simultaneamente.
        La interaccion se verifica como:
        DCR = sqrt((Vu2/phiVn2)^2 + (Vu3/phiVn3)^2) <= 1.0
        SF = 1/DCR

        Para pilares de muro con vigas de acople (§18.10.8.1(a), §18.7.6.1):
        Ve = Mpr_total / lu (diseno por capacidad)
        Ve = min(Ve, Omega_0 x Vu) donde Omega_0 = 3.0

        Args:
            pier: Pier a verificar
            pier_forces: Fuerzas del pier (combinaciones)
            Mpr_total: Momento probable total de vigas de acople (kN-m)
            lu: Altura libre del pier (mm)
            lambda_factor: Factor de concreto liviano
            classification: Clasificacion del muro (opcional)

        Returns:
            Dict con resultados de la verificacion de corte
        """
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

        # Convertir Mpr_total de kN-m a tonf-m
        Mpr_total_tonf_m = Mpr_total / 9.80665 if Mpr_total > 0 else 0

        # Variables para tracking del caso critico
        min_sf = float('inf')
        critical_result = None
        critical_combo_name = ''
        Ve_used = 0
        use_capacity_design = False

        # Obtener cuantia vertical del pier para verificacion §18.10.4.3
        rho_v = pier.rho_vertical

        # Iterar por cada combinacion
        for combo in pier_forces.combinations:
            P = -combo.P  # Positivo = compresion
            Vu2 = abs(combo.V2)
            Vu3 = abs(combo.V3)
            Vu_max = max(Vu2, Vu3)

            # Calcular Ve usando funcion centralizada de chapter18
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
                Vu2_check = Ve if Vu2 > 0 else 0
                Vu3_check = Ve if Vu3 > 0 else 0
            else:
                Vu2_check = Vu2
                Vu3_check = Vu3

            # Verificar corte combinado para esta combinacion
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

            # Actualizar si es mas critico
            if combined_result.sf < min_sf:
                min_sf = combined_result.sf
                critical_result = combined_result
                critical_combo_name = combo.name
                Ve_used = Ve if use_capacity_design else 0

        status = "OK" if min_sf >= 1.0 else "NO OK"

        # Obtener informacion de verificacion de cuantia
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
            Nu: Carga axial (tonf, positivo = compresion)

        Returns:
            Dict con capacidades phiVn2, phiVn3 y verificacion de cuantia
        """
        rho_v = pier.rho_vertical

        shear_V2, shear_V3 = self._shear_verification.verify_bidirectional_shear(
            lw=pier.width,
            tw=pier.thickness,
            hw=pier.height,
            fc=pier.fc,
            fy=pier.fy,
            rho_h=pier.rho_horizontal,
            Vu2_max=1.0,
            Vu3_max=1.0,
            Nu=Nu,
            rho_v=rho_v
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
        Expone el metodo de verificacion bidireccional del servicio de dominio.

        Args:
            lw: Largo del muro (mm)
            tw: Espesor del muro (mm)
            hw: Altura del muro (mm)
            fc: f'c del hormigon (MPa)
            fy: fy del acero (MPa)
            rho_h: Cuantia horizontal
            Vu2_max: Corte maximo V2 (tonf)
            Vu3_max: Corte maximo V3 (tonf)
            Nu: Carga axial (tonf, positivo = compresion)
            rho_v: Cuantia vertical (opcional, para §18.10.4.3)

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
        Verifica un grupo de segmentos de muro segun ACI 318-14 §18.10.4.4.

        Para segmentos verticales coplanares que resisten una fuerza
        lateral comun, la suma de sus Vn no debe exceder:
        Vn_grupo <= 0.66 x sqrt(f'c) x Acv_total

        Args:
            segments: Lista de tuplas (lw, tw, hw) para cada segmento en mm
            fc: Resistencia del hormigon f'c (MPa)
            fy: Fluencia del acero (MPa)
            rho_h: Cuantia horizontal comun
            Vu_total: Demanda de corte total del grupo (tonf)
            Nu: Carga axial total (tonf)
            rho_v: Cuantia vertical (opcional, para §18.10.4.3)

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
