# app/routes/beams.py
"""
Endpoints API para análisis de vigas sísmicas.

Incluye:
- Análisis de vigas según ACI 318-25 §18.6 (SPECIAL)
- Verificación dimensional, longitudinal, transversal y cortante
- Soporte para vigas frame y spandrels
- Detección automática de vigas con carga axial significativa (§18.6.4.6)

Usa ElementOrchestrator para clasificar y verificar vigas de forma unificada.
"""
import logging

from flask import Blueprint, jsonify

from ..services.analysis.element_orchestrator import ElementOrchestrator
from ..services.presentation.result_formatter import ResultFormatter
from .common import (
    handle_errors,
    require_session_data,
    require_element,
    parse_seismic_params,
    analyze_elements_generic,
)

# Blueprint para endpoints de vigas
bp = Blueprint('beams', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)

# Orquestador unificado de elementos
_orchestrator = ElementOrchestrator()


# =============================================================================
# Análisis de Vigas
# =============================================================================

@bp.route('/analyze-beams', methods=['POST'])
@handle_errors
@require_session_data
def analyze_beams(session_id: str, data: dict, parsed_data):
    """
    Analiza vigas de la sesión actual usando flujo unificado.

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

    Nota: Usa ElementOrchestrator que:
    - Clasifica automáticamente cada viga
    - Detecta vigas con carga axial significativa (§18.6.4.6)
    - Las verifica con el servicio apropiado según ACI 318-25
    """
    if not parsed_data.has_beams:
        return jsonify({
            'success': False,
            'error': 'No hay vigas en esta sesión. Asegúrese de cargar un archivo con vigas.'
        }), 400

    # Parsear parámetros sísmicos
    category, lambda_factor = parse_seismic_params(data)

    # Analizar vigas usando función genérica
    # Detecta automáticamente §18.6.4.6 si Pu > Ag×f'c/10
    results, statistics = analyze_elements_generic(
        elements=parsed_data.beams or {},
        forces_dict=parsed_data.beam_forces or {},
        orchestrator=_orchestrator,
        result_formatter=ResultFormatter,
        category=category,
        lambda_factor=lambda_factor,
    )

    return jsonify({
        'success': True,
        'results': results,
        'statistics': statistics
    })


@bp.route('/beam-capacities', methods=['POST'])
@handle_errors
@require_session_data
@require_element('beam_key', 'beams', 'Viga')
def get_beam_capacities(session_id: str, data: dict, parsed_data, beam_key: str, beam):
    """
    Obtiene las capacidades de una viga específica.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "beam_key": "Story4_B1"
        }
    """
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
