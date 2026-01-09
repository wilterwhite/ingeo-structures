# app/routes/beams.py
"""
Endpoints API para análisis de vigas sísmicas.

Incluye:
- Análisis de vigas según ACI 318-25 §18.6 (SPECIAL)
- Verificación dimensional, longitudinal, transversal y cortante
- Soporte para vigas frame y spandrels
"""
import logging

from flask import Blueprint, jsonify

from ..domain.chapter18.beams.service import SeismicBeamService
from ..domain.chapter18.common import SeismicCategory
from .common import (
    get_analysis_service,
    handle_errors,
    require_session,
    get_session_or_404,
)

# Blueprint para endpoints de vigas
bp = Blueprint('beams', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)

# Servicio de verificación de vigas
_beam_service = SeismicBeamService()


# =============================================================================
# Análisis de Vigas
# =============================================================================

@bp.route('/analyze-beams', methods=['POST'])
@handle_errors
@require_session
def analyze_beams(session_id: str, data: dict):
    """
    Analiza vigas de la sesión actual.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "beam_updates": [...],    // Opcional
            "category": "SPECIAL",    // SPECIAL, INTERMEDIATE, ORDINARY
            "lambda_factor": 1.0      // Factor concreto liviano
        }

    Response:
        {
            "success": true,
            "results": [...],
            "statistics": {...}
        }
    """
    parsed_data, error = get_session_or_404(session_id)
    if error:
        return error

    if not parsed_data.has_beams:
        return jsonify({
            'success': False,
            'error': 'No hay vigas en esta sesión. Asegúrese de cargar un archivo con vigas.'
        }), 400

    # Parsear categoría sísmica
    category_str = data.get('category', 'SPECIAL').upper()
    try:
        category = SeismicCategory[category_str]
    except KeyError:
        category = SeismicCategory.SPECIAL

    lambda_factor = float(data.get('lambda_factor', 1.0))

    results = []
    ok_count = 0
    fail_count = 0

    for beam_key, beam in parsed_data.beams.items():
        beam_forces = parsed_data.beam_forces.get(beam_key)

        # Obtener fuerzas críticas
        Vu = 0
        if beam_forces:
            critical = beam_forces.get_critical_shear()
            if critical:
                Vu = abs(critical.V2)

        # Usar Mpr si están disponibles
        Mpr_left = beam.Mpr_left or 0
        Mpr_right = beam.Mpr_right or 0

        # Verificar viga
        result = _beam_service.verify_beam(
            bw=beam.bw,
            h=beam.depth,
            d=beam.d,
            ln=beam.ln_calculated,
            cover=beam.cover,
            fc=beam.fc,
            fy=beam.fy,
            fyt=beam.fy,  # Asume mismo fy para transversal
            As_top=beam.As_top,
            As_bottom=beam.As_bottom,
            n_bars_top=beam.n_bars_top,
            n_bars_bottom=beam.n_bars_bottom,
            db_long=min(beam.diameter_top, beam.diameter_bottom),
            s_in_zone=beam.stirrup_spacing,
            s_outside_zone=beam.stirrup_spacing,  # Simplificado
            Av=beam.Av,
            hx=beam.hx,
            Vu=Vu,
            Mpr_left=Mpr_left,
            Mpr_right=Mpr_right,
            category=category,
            lambda_factor=lambda_factor,
        )

        # Formatear resultado
        result_dict = {
            'beam_key': beam_key,
            'label': beam.label,
            'story': beam.story,
            'source': beam.source.value,
            'section': f'{beam.width}x{beam.depth}',
            'length_mm': beam.length,
            'reinforcement': beam.reinforcement_description,
            'is_ok': result.is_ok,
            'dcr_max': result.dcr_max,
            'critical_check': result.critical_check,
            'warnings': result.warnings,
            'category': category.value,
        }

        # Agregar detalles de verificaciones
        if result.dimensional_limits:
            result_dict['dimensional'] = {
                'is_ok': result.dimensional_limits.is_ok,
                'bw': result.dimensional_limits.bw,
                'h': result.dimensional_limits.h,
                'ln': result.dimensional_limits.ln,
            }

        if result.longitudinal:
            result_dict['longitudinal'] = {
                'is_ok': result.longitudinal.is_ok,
                'rho_top': result.longitudinal.rho_top,
                'rho_bottom': result.longitudinal.rho_bottom,
                'rho_max': result.longitudinal.rho_max,
            }

        if result.transverse:
            result_dict['transverse'] = {
                'is_ok': result.transverse.is_ok,
                's_in_zone': result.transverse.s_in_zone,
                's_max_zone': result.transverse.s_max_zone,
            }

        if result.shear:
            result_dict['shear'] = {
                'is_ok': result.shear.is_ok,
                'dcr': result.shear.dcr,
                'Ve': result.shear.Ve,
                'Vu': result.shear.Vu,
                'phi_Vn': result.shear.phi_Vn,
            }

        results.append(result_dict)

        if result.is_ok:
            ok_count += 1
        else:
            fail_count += 1

    total = len(results)
    statistics = {
        'total_beams': total,
        'ok_count': ok_count,
        'fail_count': fail_count,
        'pass_rate': round(ok_count / total * 100, 1) if total > 0 else 0
    }

    return jsonify({
        'success': True,
        'results': results,
        'statistics': statistics
    })


@bp.route('/beam-capacities', methods=['POST'])
@handle_errors
@require_session
def get_beam_capacities(session_id: str, data: dict):
    """
    Obtiene las capacidades de una viga específica.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "beam_key": "Story4_B1"
        }
    """
    beam_key = data.get('beam_key')
    if not beam_key:
        return jsonify({
            'success': False,
            'error': 'Se requiere beam_key'
        }), 400

    parsed_data, error = get_session_or_404(session_id)
    if error:
        return error

    if beam_key not in parsed_data.beams:
        return jsonify({
            'success': False,
            'error': f'Viga "{beam_key}" no encontrada'
        }), 404

    beam = parsed_data.beams[beam_key]
    beam_forces = parsed_data.beam_forces.get(beam_key)

    # Información de la viga
    beam_info = {
        'label': beam.label,
        'story': beam.story,
        'source': beam.source.value,
        'length_mm': beam.length,
        'depth_mm': beam.depth,
        'width_mm': beam.width,
        'fc_MPa': beam.fc,
        'fy_MPa': beam.fy,
        'cover_mm': beam.cover,
        'd_mm': round(beam.d, 1),
        'ln_mm': round(beam.ln_calculated, 1),
        'aspect_ratio': round(beam.aspect_ratio, 2),
        'is_deep': beam.is_deep,
        'section_name': beam.section_name,
    }

    # Información de refuerzo
    reinforcement = {
        'n_bars_top': beam.n_bars_top,
        'n_bars_bottom': beam.n_bars_bottom,
        'diameter_top': beam.diameter_top,
        'diameter_bottom': beam.diameter_bottom,
        'As_top_mm2': round(beam.As_top, 1),
        'As_bottom_mm2': round(beam.As_bottom, 1),
        'As_total_mm2': round(beam.As_flexure_total, 1),
        'stirrup_diameter': beam.stirrup_diameter,
        'stirrup_spacing': beam.stirrup_spacing,
        'n_stirrup_legs': beam.n_stirrup_legs,
        'Av_mm2': round(beam.Av, 1),
    }

    # Fuerzas si están disponibles
    forces = None
    if beam_forces:
        critical = beam_forces.get_critical_shear()
        if critical:
            forces = {
                'combo_name': critical.combo_name,
                'V2_tonf': round(critical.V2, 2),
                'M3_tonf_m': round(critical.M3, 2),
            }

    # Momentos probables si están calculados
    mpr_info = None
    if beam.Mpr_left or beam.Mpr_right:
        mpr_info = {
            'Mpr_left_tonf_m': round(beam.Mpr_left or 0, 2),
            'Mpr_right_tonf_m': round(beam.Mpr_right or 0, 2),
        }

    return jsonify({
        'success': True,
        'beam': beam_info,
        'reinforcement': reinforcement,
        'forces': forces,
        'mpr': mpr_info
    })
