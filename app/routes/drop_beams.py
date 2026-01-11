# app/routes/drop_beams.py
"""
Endpoints API para análisis de vigas capitel (drop beams).

Las vigas capitel son losas diseñadas como vigas a flexocompresión,
usando análisis P-M similar a muros según ACI 318-25 §18.10.

Usa ElementOrchestrator para clasificar y verificar de forma unificada.
"""
import logging
from flask import Blueprint, request, jsonify

from ..services.analysis.reinforcement_update_service import ReinforcementUpdateService
from ..services.presentation.result_formatter import ResultFormatter
from .common import (
    get_analysis_service,
    get_orchestrator,
    handle_errors,
    require_session,
    require_session_data,
    require_element,
    require_element_type,
    parse_seismic_params,
    analyze_elements_generic,
    validate_positive_numeric,
)

bp = Blueprint('drop_beams', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)


@bp.route('/analyze-drop-beams', methods=['POST'])
@handle_errors
@require_session_data
@require_element_type('drop_beams')
def analyze_drop_beams(session_id: str, data: dict, parsed_data):
    """
    Analiza vigas capitel de la sesión actual usando flujo unificado.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "drop_beam_updates": [...],
            "category": "SPECIAL",
            "lambda_factor": 1.0
        }

    Response:
        {
            "success": true,
            "results": [...],
            "statistics": {...}
        }

    Nota: Usa ElementOrchestrator que clasifica automáticamente cada viga capitel
    y la verifica con el servicio apropiado según ACI 318-25 §18.10.
    """
    # Aplicar actualizaciones de refuerzo usando servicio centralizado
    drop_beam_updates = data.get('drop_beam_updates')
    if drop_beam_updates:
        ReinforcementUpdateService.apply_drop_beam_updates(
            parsed_data.drop_beams, drop_beam_updates
        )

    # Parsear parámetros sísmicos
    category, lambda_factor = parse_seismic_params(data)

    # Analizar vigas capitel usando función genérica
    results, statistics = analyze_elements_generic(
        elements=parsed_data.drop_beams or {},
        forces_dict=parsed_data.drop_beam_forces or {},
        orchestrator=get_orchestrator(),
        result_formatter=ResultFormatter,
        category=category,
        lambda_factor=lambda_factor,
    )

    return jsonify({
        'success': True,
        'results': results,
        'statistics': statistics
    })


@bp.route('/drop-beam-section-diagram', methods=['POST'])
@handle_errors
@require_session
def get_drop_beam_section_diagram(session_id: str, data: dict):
    """
    Genera un diagrama de la sección transversal de una viga capitel.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "drop_beam_key": "S02_CL_C3"
        }

    Response:
        {
            "success": true,
            "plot": "base64_image..."
        }
    """
    drop_beam_key = data.get('drop_beam_key')

    if not drop_beam_key:
        return jsonify({
            'success': False,
            'error': 'Se requiere drop_beam_key'
        }), 400

    # Delegar al servicio de análisis
    service = get_analysis_service()
    result = service.generate_drop_beam_section_diagram(session_id, drop_beam_key)

    if not result.get('success'):
        return jsonify(result), 404

    return jsonify(result)


@bp.route('/update-drop-beam-reinforcement', methods=['POST'])
@handle_errors
@require_session
def update_drop_beam_reinforcement(session_id: str, data: dict):
    """
    Actualiza la armadura de una viga capitel.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "drop_beam_key": "S02_CL_C3",
            "reinforcement": {
                "n_meshes": 2,
                "diameter_v": 12,
                "spacing_v": 200,
                ...
            }
        }
    """
    drop_beam_key = data.get('drop_beam_key')
    reinforcement = data.get('reinforcement', {})

    if not drop_beam_key:
        return jsonify({
            'success': False,
            'error': 'Se requiere drop_beam_key'
        }), 400

    # Validar parámetros numéricos si están presentes
    numeric_fields = {
        'n_meshes': ('int', False),
        'diameter_v': ('int', False),
        'spacing_v': ('int', False),
        'diameter_h': ('int', False),
        'spacing_h': ('int', False),
        'diameter_edge': ('int', False),
        'n_edge_bars': ('int', False),
        'stirrup_diameter': ('int', False),
        'stirrup_spacing': ('int', False),
        'fy': ('float', False),
        'cover': ('float', False),
    }
    validated, errors = validate_positive_numeric(reinforcement, numeric_fields)
    if errors:
        return jsonify({
            'success': False,
            'error': 'Errores de validación',
            'validation_errors': errors
        }), 400

    service = get_analysis_service()
    parsed_data = service.get_session_data(session_id)

    if not parsed_data:
        return jsonify({
            'success': False,
            'error': f'Sesión no encontrada: {session_id}'
        }), 404

    drop_beam = parsed_data.drop_beams.get(drop_beam_key)
    if not drop_beam:
        return jsonify({
            'success': False,
            'error': f'Viga capitel no encontrada: {drop_beam_key}'
        }), 404

    # Actualizar armadura con valores validados
    drop_beam.update_reinforcement(
        n_meshes=validated.get('n_meshes'),
        diameter_v=validated.get('diameter_v'),
        spacing_v=validated.get('spacing_v'),
        diameter_h=validated.get('diameter_h'),
        spacing_h=validated.get('spacing_h'),
        diameter_edge=validated.get('diameter_edge'),
        n_edge_bars=validated.get('n_edge_bars'),
        stirrup_diameter=validated.get('stirrup_diameter'),
        stirrup_spacing=validated.get('stirrup_spacing'),
        fy=validated.get('fy'),
        cover=validated.get('cover')
    )

    return jsonify({
        'success': True,
        'drop_beam_key': drop_beam_key
    })
