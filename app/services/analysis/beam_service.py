# app/services/analysis/beam_service.py
"""
Servicio de verificacion de cortante para vigas de HA.

Implementa verificacion de cortante segun ACI 318-25 Capitulo 22:
- Vc = 0.17 * lambda * sqrt(f'c) * bw * d
- Vs = Av * fy * d / s
- phi_Vn = phi * (Vc + Vs)
- Limite: Vs <= 0.66 * sqrt(f'c) * bw * d

Soporta:
- Vigas frame (Element Forces - Beams)
- Spandrels (vigas de acople tipo shell)
"""
import math
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

from ...domain.entities import Beam, BeamForces
from ...domain.constants.materials import (
    LAMBDA_NORMAL,
    get_effective_fc_shear,
    get_effective_fyt_shear,
)
from ...domain.constants.shear import (
    PHI_SHEAR,
    VC_COEF_COLUMN,  # 0.17 - coeficiente para vigas/columnas
    VS_MAX_COEF,     # 0.66 - limite de Vs
    N_TO_TONF,
)


@dataclass
class BeamShearResult:
    """Resultado de verificacion de cortante para una viga."""
    # Capacidades (tonf)
    Vc: float              # Resistencia del concreto
    Vs: float              # Resistencia del acero
    Vn: float              # Resistencia nominal total
    phi_Vn: float          # Resistencia de diseno
    Vs_max: float          # Limite de Vs

    # Demanda
    Vu: float              # Cortante ultimo (tonf)
    critical_combo: str    # Combinacion critica

    # Verificacion
    sf: float              # Factor de seguridad (phi_Vn / Vu)
    dcr: float             # Demand/Capacity Ratio (Vu / phi_Vn)
    status: str            # "OK" o "NO OK"

    # Referencia ACI
    aci_reference: str = "ACI 318-25 22.5"


class BeamService:
    """
    Servicio para verificacion de cortante en vigas segun ACI 318-25.

    Responsabilidades:
    - Verificar cortante (V2) para vigas frame y spandrels
    - Encontrar la combinacion critica
    - Calcular factores de seguridad

    Limitaciones actuales:
    - Solo verificacion de cortante (no flexion)
    - Solo secciones rectangulares
    """

    def check_shear(
        self,
        beam: Beam,
        beam_forces: Optional[BeamForces]
    ) -> Dict[str, Any]:
        """
        Verifica cortante de una viga y retorna el caso critico.

        El cortante principal en vigas es V2 (vertical).

        Args:
            beam: Viga a verificar
            beam_forces: Fuerzas de la viga (combinaciones)

        Returns:
            Dict con resultados de la verificacion de cortante
        """
        # Resultado por defecto cuando no hay fuerzas
        default_result = {
            'sf': float('inf'),
            'dcr': 0,
            'status': 'OK',
            'critical_combo': 'N/A',
            'phi_Vn': 0,
            'Vu': 0,
            'Vc': 0,
            'Vs': 0,
            'Vs_max': 0,
            'aci_reference': 'ACI 318-25 22.5'
        }

        if not beam_forces or not beam_forces.combinations:
            return default_result

        # Calcular capacidad de cortante
        shear_capacity = self._calculate_shear_capacity(beam)

        # Encontrar cortante maximo (V2 es el cortante vertical en vigas)
        Vu_max = 0.0
        critical_combo_name = ''

        for combo in beam_forces.combinations:
            Vu = abs(combo.V2)
            if Vu > Vu_max:
                Vu_max = Vu
                critical_combo_name = combo.name

        # Calcular DCR y SF
        phi_Vn = shear_capacity['phi_Vn']
        dcr = Vu_max / phi_Vn if phi_Vn > 0 else float('inf')
        sf = phi_Vn / Vu_max if Vu_max > 0 else float('inf')
        status = "OK" if sf >= 1.0 else "NO OK"

        return {
            'sf': round(sf, 2),
            'dcr': round(dcr, 3),
            'status': status,
            'critical_combo': critical_combo_name,
            'phi_Vn': round(phi_Vn, 2),
            'Vu': round(Vu_max, 2),
            'Vc': round(shear_capacity['Vc'], 2),
            'Vs': round(shear_capacity['Vs'], 2),
            'Vs_max': round(shear_capacity['Vs_max'], 2),
            'aci_reference': 'ACI 318-25 22.5'
        }

    def get_shear_capacity(self, beam: Beam) -> Dict[str, Any]:
        """
        Calcula la capacidad de cortante puro de la viga.

        Args:
            beam: Viga a analizar

        Returns:
            Dict con capacidades Vc, Vs, phi_Vn
        """
        capacity = self._calculate_shear_capacity(beam)
        return {
            'Vc': round(capacity['Vc'], 2),
            'Vs': round(capacity['Vs'], 2),
            'Vn': round(capacity['Vn'], 2),
            'phi_Vn': round(capacity['phi_Vn'], 2),
            'Vs_max': round(capacity['Vs_max'], 2),
            'd': round(beam.d, 1),
            'bw': round(beam.bw, 1),
            'Av': round(beam.Av, 1),
            'rho_v': round(beam.rho_transversal, 5)
        }

    def _calculate_shear_capacity(self, beam: Beam) -> Dict[str, float]:
        """
        Calcula Vc, Vs, Vn para una viga segun ACI 318-25 §22.5.

        Formulas:
        - Vc = 0.17 * lambda * sqrt(f'c) * bw * d
        - Vs = Av * fy * d / s
        - Vn = Vc + Vs
        - Limite: Vs <= 0.66 * sqrt(f'c) * bw * d

        Returns:
            Dict con Vc, Vs, Vn, phi_Vn, Vs_max (en tonf)
        """
        # Aplicar limites de materiales (§18.2.5, §18.2.6)
        fc_eff = get_effective_fc_shear(beam.fc)
        fy_eff = get_effective_fyt_shear(beam.fy)

        bw = beam.bw  # mm
        d = beam.d    # mm
        Av = beam.Av  # mm2
        s = beam.stirrup_spacing  # mm

        # Vc = 0.17 * lambda * sqrt(f'c) * bw * d
        Vc = VC_COEF_COLUMN * LAMBDA_NORMAL * math.sqrt(fc_eff) * bw * d

        # Vs = Av * fy * d / s
        if s > 0:
            Vs = Av * fy_eff * d / s
        else:
            Vs = 0

        # Limite de Vs: 0.66 * sqrt(f'c) * bw * d
        Vs_max = VS_MAX_COEF * math.sqrt(fc_eff) * bw * d
        if Vs > Vs_max:
            Vs = Vs_max

        Vn = Vc + Vs
        phi_Vn = PHI_SHEAR * Vn

        return {
            'Vc': Vc / N_TO_TONF,
            'Vs': Vs / N_TO_TONF,
            'Vn': Vn / N_TO_TONF,
            'phi_Vn': phi_Vn / N_TO_TONF,
            'Vs_max': Vs_max / N_TO_TONF
        }

    def verify_beam(
        self,
        beam: Beam,
        beam_forces: Optional[BeamForces]
    ) -> BeamShearResult:
        """
        Verifica cortante y retorna BeamShearResult estructurado.

        Args:
            beam: Viga a verificar
            beam_forces: Fuerzas de la viga

        Returns:
            BeamShearResult con verificacion completa
        """
        # Calcular capacidad
        capacity = self._calculate_shear_capacity(beam)

        # Encontrar cortante critico
        Vu_max = 0.0
        critical_combo = 'N/A'

        if beam_forces and beam_forces.combinations:
            for combo in beam_forces.combinations:
                Vu = abs(combo.V2)
                if Vu > Vu_max:
                    Vu_max = Vu
                    critical_combo = combo.name

        # Calcular verificacion
        phi_Vn = capacity['phi_Vn']
        dcr = Vu_max / phi_Vn if phi_Vn > 0 else float('inf')
        sf = phi_Vn / Vu_max if Vu_max > 0 else float('inf')
        status = "OK" if sf >= 1.0 else "NO OK"

        return BeamShearResult(
            Vc=capacity['Vc'],
            Vs=capacity['Vs'],
            Vn=capacity['Vn'],
            phi_Vn=phi_Vn,
            Vs_max=capacity['Vs_max'],
            Vu=Vu_max,
            critical_combo=critical_combo,
            sf=sf,
            dcr=dcr,
            status=status,
            aci_reference='ACI 318-25 22.5'
        )

    def verify_all_beams(
        self,
        beams: Dict[str, Beam],
        beam_forces: Dict[str, BeamForces]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Verifica cortante para todas las vigas.

        Args:
            beams: Diccionario de vigas indexadas por key
            beam_forces: Diccionario de fuerzas indexadas por key

        Returns:
            Dict[beam_key, shear_result]
        """
        results = {}

        for beam_key, beam in beams.items():
            forces = beam_forces.get(beam_key)
            results[beam_key] = self.check_shear(beam, forces)

        return results

    def get_summary(
        self,
        beams: Dict[str, Beam],
        beam_forces: Dict[str, BeamForces]
    ) -> Dict[str, Any]:
        """
        Genera resumen de verificacion de todas las vigas.

        Returns:
            Dict con estadisticas de verificacion
        """
        results = self.verify_all_beams(beams, beam_forces)

        total = len(results)
        ok_count = sum(1 for r in results.values() if r['status'] == 'OK')
        fail_count = total - ok_count

        min_sf = float('inf')
        max_dcr = 0
        critical_beam = None

        for beam_key, result in results.items():
            if result['sf'] < min_sf:
                min_sf = result['sf']
                max_dcr = result['dcr']
                critical_beam = beam_key

        return {
            'total_beams': total,
            'ok_count': ok_count,
            'fail_count': fail_count,
            'pass_rate': round(ok_count / total * 100, 1) if total > 0 else 100,
            'min_sf': round(min_sf, 2) if min_sf != float('inf') else None,
            'max_dcr': round(max_dcr, 3),
            'critical_beam': critical_beam
        }
