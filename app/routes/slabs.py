# app/routes/slabs.py
"""
Endpoints API para análisis de losas.

Incluye:
- Análisis de losas one-way y two-way
- Verificación de punzonamiento
- Capacidades de losas individuales
"""
import logging

from flask import Blueprint, jsonify

from ..services.analysis.slab_service import SlabService
from ..services.analysis.punching_service import PunchingService
from .common import (
    get_analysis_service,
    handle_errors,
    require_session,
    require_session_and_slab,
    get_session_or_404,
)

# Blueprint para endpoints de losas
bp = Blueprint('slabs', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)


# =============================================================================
# Análisis de Losas
# =============================================================================

@bp.route('/analyze-slabs', methods=['POST'])
@handle_errors
@require_session
def analyze_slabs(session_id: str, data: dict):
    """
    Analiza losas de la sesión actual.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "slab_updates": [...],
            "lambda_factor": 1.0
        }
    """
    parsed_data, error = get_session_or_404(session_id)
    if error:
        return error

    if not parsed_data.has_slabs:
        return jsonify({
            'success': False,
            'error': 'No hay losas en esta sesión. Asegúrese de cargar un archivo con tabla "Section Cut Forces - Analysis".'
        }), 400

    # Aplicar actualizaciones a las losas si se proporcionan
    slab_updates = data.get('slab_updates', [])
    if slab_updates:
        service = get_analysis_service()
        service.update_slabs_batch(session_id, slab_updates)

    # Crear servicio de losas
    lambda_factor = float(data.get('lambda_factor', 1.0))
    slab_service = SlabService(lambda_factor=lambda_factor)

    # Ejecutar verificaciones
    results = slab_service.verify_all_slabs(parsed_data.slabs, parsed_data.slab_forces)
    statistics = slab_service.get_summary(parsed_data.slabs, parsed_data.slab_forces)

    return jsonify({
        'success': True,
        'results': list(results.values()),
        'statistics': statistics
    })


@bp.route('/slab-capacities', methods=['POST'])
@handle_errors
@require_session_and_slab
def get_slab_capacities(session_id: str, slab_key: str, data: dict):
    """
    Obtiene las capacidades de una losa específica.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "slab_key": "S02_CL_C3"
        }
    """
    parsed_data, error = get_session_or_404(session_id)
    if error:
        return error

    if slab_key not in parsed_data.slabs:
        return jsonify({
            'success': False,
            'error': f'Losa "{slab_key}" no encontrada'
        }), 404

    slab = parsed_data.slabs[slab_key]
    slab_forces = parsed_data.slab_forces.get(slab_key)

    # Crear servicio y obtener verificación completa
    slab_service = SlabService()
    result = slab_service.verify_slab(slab, slab_forces)

    # Datos de la losa
    slab_info = {
        'label': slab.label,
        'story': slab.story,
        'slab_type': slab.slab_type.value,
        'thickness_mm': slab.thickness,
        'width_mm': slab.width,
        'span_mm': slab.span_length,
        'fc_MPa': slab.fc,
        'fy_MPa': slab.fy,
        'd_mm': round(slab.d, 1),
        'cover_mm': slab.cover,
        # Refuerzo
        'diameter_main': slab.diameter_main,
        'spacing_main': slab.spacing_main,
        'As_main_mm2_m': round(slab.As_main, 1),
        'rho_main': round(slab.rho_main, 5),
        'diameter_temp': slab.diameter_temp,
        'spacing_temp': slab.spacing_temp,
        'As_temp_mm2_m': round(slab.As_temp, 1),
        # Columna (para punzonamiento)
        'column_width_mm': slab.column_width,
        'column_depth_mm': slab.column_depth,
        'is_interior_column': slab.is_interior_column
    }

    return jsonify({
        'success': True,
        'slab': slab_info,
        'verification': result
    })


# =============================================================================
# Punzonamiento
# =============================================================================

@bp.route('/analyze-punching', methods=['POST'])
@handle_errors
@require_session
def analyze_punching(session_id: str, data: dict):
    """
    Analiza punzonamiento para losas 2-Way.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "slab_key": "S02_CL_C3",  // Opcional - si no se especifica, analiza todas
            "column_c1": 400,
            "column_c2": 400,
            "position": "interior"
        }
    """
    parsed_data, error = get_session_or_404(session_id)
    if error:
        return error

    # Crear servicio de punzonamiento
    punching_service = PunchingService()

    # Parsear posición de columna
    position_str = data.get('position', 'interior')
    position = PunchingService.parse_position(position_str)

    slab_key = data.get('slab_key')

    if slab_key:
        # Analizar una losa específica
        if slab_key not in parsed_data.slabs:
            return jsonify({
                'success': False,
                'error': f'Losa "{slab_key}" no encontrada'
            }), 404

        slab = parsed_data.slabs[slab_key]
        slab_forces = parsed_data.slab_forces.get(slab_key)

        result = punching_service.check_punching(
            slab=slab,
            slab_forces=slab_forces,
            column_c1_mm=data.get('column_c1'),
            column_c2_mm=data.get('column_c2'),
            position=position
        )

        return jsonify({
            'success': True,
            'result': result
        })
    else:
        # Analizar todas las losas 2-Way
        results = punching_service.check_all_punching(
            parsed_data.slabs, parsed_data.slab_forces
        )
        statistics = punching_service.get_summary(
            parsed_data.slabs, parsed_data.slab_forces
        )

        return jsonify({
            'success': True,
            'results': list(results.values()),
            'statistics': statistics
        })
