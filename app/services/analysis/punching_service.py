# app/services/analysis/punching_service.py
"""
Servicio de verificacion de punzonamiento para losas 2-Way.

Implementa verificacion segun ACI 318-25:
- Capitulo 8.10: Requisitos de cortante bidireccional
- Capitulo 22.6: Resistencia al cortante bidireccional
"""
from typing import Dict, Any, Optional
from dataclasses import asdict

from ...domain.entities.slab import Slab, SlabType
from ...domain.entities.slab_forces import SlabForces
from ...domain.chapter8.punching import (
    calculate_punching_Vc,
    ColumnPosition,
    PunchingResult,
)
from ...domain.constants.materials import LAMBDA_NORMAL


class PunchingService:
    """
    Servicio para verificacion de punzonamiento en losas 2-Way.

    Solo aplica para losas clasificadas como TWO_WAY.
    """

    # Mapeo de strings a enum para uso desde routes
    POSITION_MAP = {
        'interior': ColumnPosition.INTERIOR,
        'edge': ColumnPosition.EDGE,
        'corner': ColumnPosition.CORNER
    }

    def __init__(self, lambda_factor: float = LAMBDA_NORMAL):
        """
        Inicializa el servicio.

        Args:
            lambda_factor: Factor por tipo de concreto (1.0 normal)
        """
        self.lambda_factor = lambda_factor

    @classmethod
    def parse_position(cls, position_str: str) -> ColumnPosition:
        """Convierte string a ColumnPosition enum."""
        return cls.POSITION_MAP.get(position_str.lower(), ColumnPosition.INTERIOR)

    def check_punching(
        self,
        slab: Slab,
        slab_forces: Optional[SlabForces],
        column_c1_mm: Optional[float] = None,
        column_c2_mm: Optional[float] = None,
        position: ColumnPosition = ColumnPosition.INTERIOR
    ) -> Dict[str, Any]:
        """
        Verifica punzonamiento en una losa 2-Way.

        Args:
            slab: Losa a verificar
            slab_forces: Fuerzas de la losa
            column_c1_mm: Dimension columna dir 1 (None usa slab.column_width)
            column_c2_mm: Dimension columna dir 2 (None usa slab.column_depth)
            position: Posicion de la columna

        Returns:
            Dict con resultados de punzonamiento
        """
        # Verificar que sea losa 2-Way
        if slab.slab_type != SlabType.TWO_WAY:
            return {
                'applicable': False,
                'message': 'Punzonamiento solo aplica para losas 2-Way',
                'aci_reference': 'ACI 318-25 8.10'
            }

        # Usar dimensiones de columna de la losa o las provistas
        c1 = column_c1_mm if column_c1_mm else slab.column_width
        c2 = column_c2_mm if column_c2_mm else slab.column_depth

        # Obtener cortante de demanda
        Vu_kN = 0.0
        critical_combo = 'N/A'

        if slab_forces and slab_forces.combinations:
            punching_data = slab_forces.get_punching_shear()
            # Convertir de tonf a kN (1 tonf = 9.80665 kN)
            Vu_kN = punching_data['Vu_max'] * 9.80665
            critical_combo = punching_data['critical_combo']

        # Calcular resistencia
        result = calculate_punching_Vc(
            fc_mpa=slab.fc,
            c1_mm=c1,
            c2_mm=c2,
            d_mm=slab.d,
            position=position,
            lambda_factor=self.lambda_factor,
            Vu_kN=Vu_kN
        )

        # Convertir kN a tonf para consistencia
        phi_Vc_tonf = result.phi_Vc / 9.80665
        Vu_tonf = result.Vu / 9.80665

        return {
            'applicable': True,
            # Geometria
            'bo': round(result.bo, 1),
            'd': round(result.d, 1),
            'Ac': round(result.Ac, 0),
            # Capacidades (en tonf)
            'Vc_a': round(result.Vc_a / 9.80665, 2),
            'Vc_b': round(result.Vc_b / 9.80665, 2),
            'Vc_c': round(result.Vc_c / 9.80665, 2),
            'Vc': round(result.Vc / 9.80665, 2),
            'phi_Vc': round(phi_Vc_tonf, 2),
            # Demanda
            'Vu': round(Vu_tonf, 2),
            'critical_combo': critical_combo,
            # Verificacion
            'sf': round(result.sf, 2) if result.sf < 100 else '>100',
            'dcr': round(result.dcr, 3),
            'status': 'OK' if result.is_ok else 'NO OK',
            # Parametros
            'beta': round(result.beta, 2),
            'alpha_s': result.alpha_s,
            'lambda_s': round(result.lambda_s, 3),
            'column_position': result.position,
            'aci_reference': result.aci_reference
        }

    def check_all_punching(
        self,
        slabs: Dict[str, Slab],
        slab_forces: Dict[str, SlabForces]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Verifica punzonamiento en todas las losas 2-Way.

        Args:
            slabs: Diccionario de losas
            slab_forces: Diccionario de fuerzas

        Returns:
            Dict[slab_key, punching_result] solo para losas 2-Way
        """
        results = {}

        for slab_key, slab in slabs.items():
            if slab.slab_type == SlabType.TWO_WAY:
                forces = slab_forces.get(slab_key)
                results[slab_key] = self.check_punching(slab, forces)

        return results

    def get_summary(
        self,
        slabs: Dict[str, Slab],
        slab_forces: Dict[str, SlabForces]
    ) -> Dict[str, Any]:
        """
        Genera resumen de verificacion de punzonamiento.

        Returns:
            Dict con estadisticas
        """
        results = self.check_all_punching(slabs, slab_forces)

        # Solo contar losas 2-Way con verificacion aplicable
        applicable = [r for r in results.values() if r.get('applicable', False)]
        total = len(applicable)

        if total == 0:
            return {
                'total': 0,
                'ok': 0,
                'fail': 0,
                'pass_rate': 100,
                'message': 'No hay losas 2-Way para verificar punzonamiento'
            }

        ok = sum(1 for r in applicable if r['status'] == 'OK')
        fail = total - ok

        # Encontrar caso critico
        min_sf = float('inf')
        critical_slab = None

        for slab_key, result in results.items():
            if not result.get('applicable'):
                continue
            sf = result.get('sf', '>100')
            sf_val = 100.0 if sf == '>100' else float(sf)
            if sf_val < min_sf:
                min_sf = sf_val
                critical_slab = slab_key

        return {
            'total': total,
            'ok': ok,
            'fail': fail,
            'pass_rate': round(ok / total * 100, 1) if total > 0 else 100,
            'min_sf': round(min_sf, 2) if min_sf < 100 else '>100',
            'critical_slab': critical_slab
        }
