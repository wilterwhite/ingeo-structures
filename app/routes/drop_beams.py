# app/routes/drop_beams.py
"""
Endpoints API para análisis de vigas capitel (drop beams).

Las vigas capitel son losas diseñadas como vigas a flexocompresión,
usando análisis P-M similar a muros.
"""
import logging
from flask import Blueprint, request, jsonify

from .common import (
    get_analysis_service,
    handle_errors,
    require_session,
)

bp = Blueprint('drop_beams', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)


@bp.route('/analyze-drop-beams', methods=['POST'])
@handle_errors
@require_session
def analyze_drop_beams(session_id: str, data: dict):
    """
    Ejecuta el análisis de vigas capitel.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "drop_beam_updates": [...],
            "generate_plots": true,
            "moment_axis": "M3"
        }

    Response:
        {
            "success": true,
            "results": [...],
            "statistics": {...}
        }
    """
    drop_beam_updates = data.get('drop_beam_updates')
    generate_plots = data.get('generate_plots', True)
    moment_axis = data.get('moment_axis', 'M3')

    service = get_analysis_service()
    result = service.analyze_drop_beams(
        session_id=session_id,
        drop_beam_updates=drop_beam_updates,
        generate_plots=generate_plots,
        moment_axis=moment_axis
    )

    return jsonify(result)


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

    # Generar diagrama de sección
    from ..services.presentation.plot_generator import PlotGenerator
    plot_gen = PlotGenerator()
    plot = plot_gen.generate_drop_beam_section_diagram(drop_beam)

    return jsonify({
        'success': True,
        'plot': plot
    })


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

    # Actualizar armadura
    drop_beam.update_reinforcement(
        n_meshes=reinforcement.get('n_meshes'),
        diameter_v=reinforcement.get('diameter_v'),
        spacing_v=reinforcement.get('spacing_v'),
        diameter_h=reinforcement.get('diameter_h'),
        spacing_h=reinforcement.get('spacing_h'),
        diameter_edge=reinforcement.get('diameter_edge'),
        n_edge_bars=reinforcement.get('n_edge_bars'),
        stirrup_diameter=reinforcement.get('stirrup_diameter'),
        stirrup_spacing=reinforcement.get('stirrup_spacing'),
        fy=reinforcement.get('fy'),
        cover=reinforcement.get('cover')
    )

    return jsonify({
        'success': True,
        'drop_beam_key': drop_beam_key
    })
