# app/structural/routes/analysis.py
"""
Endpoints API para el módulo de análisis estructural.
"""
import uuid
from flask import Blueprint, request, jsonify, current_app

from ..services.pier_analysis import PierAnalysisService


# Crear blueprint
bp = Blueprint('structural', __name__, url_prefix='/structural')

# Instancia global del servicio (para modo standalone)
_analysis_service = None


def get_analysis_service() -> PierAnalysisService:
    """Obtiene o crea la instancia del servicio de análisis."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = PierAnalysisService()
    return _analysis_service


@bp.route('/upload', methods=['POST'])
def upload_excel():
    """
    Sube y parsea un archivo Excel de ETABS.

    Request:
        multipart/form-data con campos:
        - 'file': archivo Excel (requerido)
        - 'hn_ft': altura del edificio en pies (opcional)

    Response:
        {
            "success": true,
            "session_id": "uuid-xxx",
            "summary": {
                "total_piers": 10,
                "total_stories": 3,
                "stories": ["Cielo P1", "Cielo P2", ...],
                "piers_list": [...],
                "building": {
                    "n_stories": 3,
                    "hn_ft": 98.4,
                    "hn_m": 30.0,
                    "total_height_mm": 30000
                }
            }
        }
    """
    # Validar archivo
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No se proporcionó archivo. Use el campo "file".'
        }), 400

    file = request.files['file']

    if not file.filename:
        return jsonify({
            'success': False,
            'error': 'Archivo vacío'
        }), 400

    if not file.filename.lower().endswith('.xlsx'):
        return jsonify({
            'success': False,
            'error': 'El archivo debe ser un Excel (.xlsx)'
        }), 400

    try:
        # Leer contenido
        file_content = file.read()

        # Obtener hn_ft opcional (altura del edificio en pies)
        hn_ft = None
        hn_ft_str = request.form.get('hn_ft')
        if hn_ft_str:
            try:
                hn_ft = float(hn_ft_str)
            except ValueError:
                pass  # Ignorar si no es un número válido

        # Generar session_id
        session_id = str(uuid.uuid4())

        # Parsear (ahora acepta hn_ft como parámetro opcional)
        service = get_analysis_service()
        result = service._session_manager.create_session(
            file_content, session_id, hn_ft=hn_ft
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al procesar el archivo: {str(e)}'
        }), 500


@bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Ejecuta el análisis estructural.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "pier_updates": [  // Opcional
                {"key": "Cielo P2_PMar-C4-1", "As_vertical": 1200, "fy": 420},
                ...
            ],
            "generate_plots": true,  // Opcional, default true
            "moment_axis": "M3",     // Opcional: "M2", "M3", "combined", "SRSS"
            "angle_deg": 0           // Opcional: ángulo para vista combinada
        }

    Response:
        {
            "success": true,
            "statistics": {
                "total": 10,
                "ok": 8,
                "fail": 2,
                "pass_rate": 80.0
            },
            "results": [...],
            "summary_plot": "base64..."
        }
    """
    try:
        data = request.get_json() or {}

        session_id = data.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id'
            }), 400

        pier_updates = data.get('pier_updates')
        generate_plots = data.get('generate_plots', True)
        moment_axis = data.get('moment_axis', 'M3')
        angle_deg = data.get('angle_deg', 0)

        service = get_analysis_service()
        result = service.analyze(
            session_id=session_id,
            pier_updates=pier_updates,
            generate_plots=generate_plots,
            moment_axis=moment_axis,
            angle_deg=angle_deg
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en el análisis: {str(e)}'
        }), 500


@bp.route('/analyze-direct', methods=['POST'])
def analyze_direct():
    """
    Análisis directo en un solo paso (sin sesión).
    Útil para pruebas rápidas.

    Request:
        multipart/form-data con campo 'file'

    Response:
        Igual que /analyze
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No se proporcionó archivo'
        }), 400

    file = request.files['file']

    if not file.filename.lower().endswith('.xlsx'):
        return jsonify({
            'success': False,
            'error': 'El archivo debe ser un Excel (.xlsx)'
        }), 400

    try:
        file_content = file.read()
        generate_plots = request.form.get('generate_plots', 'true').lower() == 'true'

        service = get_analysis_service()
        result = service.analyze_direct(
            file_content=file_content,
            generate_plots=generate_plots
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@bp.route('/clear-session/<session_id>', methods=['DELETE'])
def clear_session(session_id: str):
    """
    Limpia una sesión del cache.

    Response:
        {"success": true}
    """
    service = get_analysis_service()
    cleared = service.clear_session(session_id)

    return jsonify({
        'success': True,
        'cleared': cleared
    })


@bp.route('/pier-combinations/<session_id>/<pier_key>', methods=['GET'])
def get_pier_combinations(session_id: str, pier_key: str):
    """
    Obtiene las combinaciones de carga de un pier con sus ángulos.

    Response:
        {
            "success": true,
            "pier_key": "Cielo P2_PMar-C4-1",
            "combinations": [
                {
                    "index": 0,
                    "name": "1.2D+1.6L",
                    "location": "Top",
                    "P": 120.5,
                    "M2": 5.2,
                    "M3": 12.8,
                    "M_resultant": 13.8,
                    "angle_deg": 22.1,
                    "full_name": "1.2D+1.6L (Top)"
                },
                ...
            ],
            "unique_angles": [
                {"angle_deg": 0, "count": 5, "max_M_resultant": 15.2},
                ...
            ]
        }
    """
    service = get_analysis_service()
    result = service.get_pier_combinations(session_id, pier_key)
    return jsonify(result)


@bp.route('/analyze-combination', methods=['POST'])
def analyze_combination():
    """
    Analiza un pier específico para una combinación específica.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "pier_key": "Cielo P2_PMar-C4-1",
            "combination_index": 0,  // Índice de la combinación
            "generate_plot": true
        }

    Response:
        {
            "success": true,
            "combination": {...},
            "pm_plot": "base64...",
            "safety_factor": 1.25,
            "status": "OK"
        }
    """
    try:
        data = request.get_json() or {}

        session_id = data.get('session_id')
        pier_key = data.get('pier_key')
        combination_index = data.get('combination_index', 0)
        generate_plot = data.get('generate_plot', True)

        if not session_id or not pier_key:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id y pier_key'
            }), 400

        service = get_analysis_service()
        result = service.analyze_single_combination(
            session_id=session_id,
            pier_key=pier_key,
            combination_index=combination_index,
            generate_plot=generate_plot
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@bp.route('/summary-plot', methods=['POST'])
def get_summary_plot():
    """
    Genera el gráfico resumen filtrado.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "pier_keys": ["key1", "key2"],  // Opcional
            "story_filter": "Cielo P2",      // Opcional
            "axis_filter": "A10"             // Opcional
        }

    Response:
        {
            "success": true,
            "summary_plot": "base64...",
            "count": 5
        }
    """
    try:
        data = request.get_json() or {}

        session_id = data.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id'
            }), 400

        pier_keys = data.get('pier_keys')
        story_filter = data.get('story_filter', '')
        axis_filter = data.get('axis_filter', '')

        service = get_analysis_service()
        result = service.generate_filtered_summary_plot(
            session_id=session_id,
            pier_keys=pier_keys,
            story_filter=story_filter,
            axis_filter=axis_filter
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@bp.route('/pier-capacities', methods=['POST'])
def get_pier_capacities():
    """
    Obtiene las capacidades puras de un pier (sin interacción).

    Request:
        {
            "session_id": "uuid-xxx",
            "pier_key": "Story_PierLabel"
        }

    Response:
        {
            "success": true,
            "pier_info": {
                "label": "Test-A1-1",
                "story": "Piso 1",
                "width_m": 0.20,
                "thickness_m": 0.20,
                "height_m": 3.0,
                "fc_MPa": 25,
                "fy_MPa": 420
            },
            "reinforcement": {
                "n_meshes": 2,
                "diameter_v": 8,
                "spacing_v": 200,
                "diameter_edge": 10,
                "As_vertical_mm2": 503,
                "As_edge_mm2": 314,
                "As_flexure_total_mm2": 817
            },
            "capacities": {
                "phi_Pn_max_tonf": 150.5,
                "phi_Mn3_tonf_m": 12.3,
                "phi_Mn2_tonf_m": 8.5,
                "phi_Vn2_tonf": 25.0,
                "phi_Vn3_tonf": 18.0
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        session_id = data.get('session_id')
        pier_key = data.get('pier_key')

        if not session_id or not pier_key:
            return jsonify({
                'success': False,
                'error': 'session_id and pier_key are required'
            }), 400

        service = get_analysis_service()
        result = service.get_pier_capacities(session_id, pier_key)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@bp.route('/section-diagram', methods=['POST'])
def get_section_diagram():
    """
    Genera un diagrama de la sección transversal del pier.

    Request:
        {
            "session_id": "uuid-xxx",
            "pier_key": "Story_PierLabel"
        }

    Response:
        {
            "success": true,
            "section_diagram": "base64..."
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        session_id = data.get('session_id')
        pier_key = data.get('pier_key')

        if not session_id or not pier_key:
            return jsonify({
                'success': False,
                'error': 'session_id and pier_key are required'
            }), 400

        service = get_analysis_service()
        result = service.get_section_diagram(session_id, pier_key)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check del módulo.
    """
    return jsonify({
        'status': 'ok',
        'module': 'structural',
        'version': '1.0.0'
    })
