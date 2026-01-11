# app/routes/piers.py
"""
Endpoints API para análisis de piers (muros estructurales).

Incluye:
- Upload de archivos Excel ETABS
- Análisis de piers (flexión, corte, boundary elements)
- Generación de reportes PDF
- Configuración de vigas de acople

Usa ElementOrchestrator para clasificar y verificar piers de forma unificada.
"""
import uuid
import json
import logging

from flask import Blueprint, request, jsonify, Response

from ..services.report import PDFReportGenerator, ReportConfig
from ..services.parsing.config_parser import parse_beam_config
from ..services.analysis.reinforcement_update_service import ReinforcementUpdateService
from .common import (
    get_analysis_service,
    get_json_data,
    handle_errors,
    require_session,
    require_session_data,
    require_session_and_pier,
    require_element,
    get_session_or_404,
    validate_positive_numeric,
)

# Blueprint para endpoints de piers
bp = Blueprint('piers', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)


# =============================================================================
# Upload y Análisis Principal
# =============================================================================

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
            "summary": {...}
        }
    """
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
        logger.info(f"[Upload] Recibiendo archivo: {file.filename}")
        file_content = file.read()
        logger.info(f"[Upload] Tamaño: {len(file_content) / 1024:.1f} KB")

        # Obtener hn_ft opcional (altura del edificio en pies)
        hn_ft = None
        hn_ft_str = request.form.get('hn_ft')
        if hn_ft_str:
            try:
                hn_ft = float(hn_ft_str)
            except ValueError:
                pass

        session_id = str(uuid.uuid4())
        logger.info(f"[Upload] Iniciando parseo... session_id={session_id[:8]}")

        service = get_analysis_service()
        result = service.parse_excel(file_content, session_id, hn_ft=hn_ft)

        summary = result.get('summary', {})
        logger.info(f"[Upload] Parseo completado: {summary.get('total_piers', 0)} piers")

        return jsonify(result)

    except Exception as e:
        logger.exception(f"[Upload] ERROR: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al procesar el archivo: {str(e)}'
        }), 500


@bp.route('/analyze', methods=['POST'])
@handle_errors
@require_session
def analyze(session_id: str, data: dict):
    """
    Ejecuta el análisis estructural.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "pier_updates": [...],
            "column_updates": [...],
            "beam_updates": [...],
            "drop_beam_updates": [...],
            "generate_plots": true,
            "moment_axis": "M3",
            "angle_deg": 0
        }
    """
    pier_updates = data.get('pier_updates')
    column_updates = data.get('column_updates')
    beam_updates = data.get('beam_updates')
    drop_beam_updates = data.get('drop_beam_updates')
    generate_plots = data.get('generate_plots', True)
    moment_axis = data.get('moment_axis', 'M3')
    angle_deg = data.get('angle_deg', 0)

    service = get_analysis_service()
    result = service.analyze(
        session_id=session_id,
        pier_updates=pier_updates,
        column_updates=column_updates,
        beam_updates=beam_updates,
        drop_beam_updates=drop_beam_updates,
        generate_plots=generate_plots,
        moment_axis=moment_axis,
        angle_deg=angle_deg
    )

    return jsonify(result)


@bp.route('/analyze-stream', methods=['POST'])
@handle_errors
@require_session
def analyze_stream(session_id: str, data: dict):
    """
    Ejecuta el análisis estructural con progreso en tiempo real (SSE).
    """
    pier_updates = data.get('pier_updates')
    column_updates = data.get('column_updates')
    beam_updates = data.get('beam_updates')
    drop_beam_updates = data.get('drop_beam_updates')
    generate_plots = data.get('generate_plots', True)
    moment_axis = data.get('moment_axis', 'M3')
    angle_deg = data.get('angle_deg', 0)
    materials_config = data.get('materials_config', {})

    service = get_analysis_service()

    def generate():
        try:
            for event in service.analyze_with_progress(
                session_id=session_id,
                pier_updates=pier_updates,
                column_updates=column_updates,
                beam_updates=beam_updates,
                drop_beam_updates=drop_beam_updates,
                generate_plots=generate_plots,
                moment_axis=moment_axis,
                angle_deg=angle_deg,
                materials_config=materials_config
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@bp.route('/analyze-direct', methods=['POST'])
@handle_errors
def analyze_direct():
    """
    Análisis directo en un solo paso (sin sesión).
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

    file_content = file.read()
    generate_plots = request.form.get('generate_plots', 'true').lower() == 'true'

    service = get_analysis_service()
    result = service.analyze_direct(
        file_content=file_content,
        generate_plots=generate_plots
    )

    return jsonify(result)


# =============================================================================
# Sesiones y Combinaciones
# =============================================================================

@bp.route('/clear-session/<session_id>', methods=['DELETE'])
def clear_session(session_id: str):
    """Limpia una sesión del cache."""
    service = get_analysis_service()
    cleared = service.clear_session(session_id)

    return jsonify({
        'success': True,
        'cleared': cleared
    })


@bp.route('/pier-combinations/<session_id>/<pier_key>', methods=['GET'])
@handle_errors
def get_pier_combinations(session_id: str, pier_key: str):
    """Obtiene las combinaciones de carga de un pier con sus ángulos."""
    service = get_analysis_service()
    result = service.get_pier_combinations(session_id, pier_key)
    return jsonify(result)


@bp.route('/analyze-combination', methods=['POST'])
@handle_errors
@require_session_and_pier
def analyze_combination(session_id: str, pier_key: str, data: dict):
    """Analiza un pier específico para una combinación específica."""
    combination_index = data.get('combination_index', 0)
    generate_plot = data.get('generate_plot', True)

    service = get_analysis_service()
    result = service.analyze_single_combination(
        session_id=session_id,
        pier_key=pier_key,
        combination_index=combination_index,
        generate_plot=generate_plot
    )

    return jsonify(result)


# =============================================================================
# Gráficos y Capacidades
# =============================================================================

@bp.route('/summary-plot', methods=['POST'])
@handle_errors
@require_session
def get_summary_plot(session_id: str, data: dict):
    """Genera el gráfico resumen filtrado."""
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


@bp.route('/pier-capacities', methods=['POST'])
@handle_errors
@require_session_and_pier
def get_pier_capacities(session_id: str, pier_key: str, data: dict):
    """Obtiene las capacidades puras de un pier (sin interacción)."""
    service = get_analysis_service()
    result = service.get_pier_capacities(session_id, pier_key)
    return jsonify(result)


@bp.route('/combination-details', methods=['POST'])
@handle_errors
@require_session_and_pier
def get_combination_details(session_id: str, pier_key: str, data: dict):
    """Obtiene los detalles de diseño para una combinación específica."""
    combo_index = data.get('combo_index', 0)

    service = get_analysis_service()
    result = service.get_combination_details(session_id, pier_key, combo_index)

    return jsonify(result)


@bp.route('/section-diagram', methods=['POST'])
@handle_errors
@require_session_and_pier
def get_section_diagram(session_id: str, pier_key: str, data: dict):
    """Genera un diagrama de la sección transversal del pier."""
    proposed_config = data.get('proposed_config')

    service = get_analysis_service()
    result = service.get_section_diagram(session_id, pier_key, proposed_config)

    return jsonify(result)


# =============================================================================
# Vigas de Acople
# =============================================================================

@bp.route('/set-default-beam', methods=['POST'])
@handle_errors
@require_session
def set_default_beam(session_id: str, data: dict):
    """Configura la viga estándar para la sesión."""
    # Validar parámetros numéricos
    numeric_fields = {
        'width': ('float', False),
        'height': ('float', False),
        'ln': ('float', False),
        'n_bars_top': ('int', False),
        'diameter_top': ('int', False),
        'n_bars_bottom': ('int', False),
        'diameter_bottom': ('int', False),
    }
    validated, errors = validate_positive_numeric(data, numeric_fields)
    if errors:
        return jsonify({
            'success': False,
            'error': 'Errores de validación',
            'validation_errors': errors
        }), 400

    service = get_analysis_service()
    service.set_default_coupling_beam(
        session_id=session_id,
        width=validated.get('width', 200),
        height=validated.get('height', 500),
        ln=validated.get('ln', 1500),
        n_bars_top=validated.get('n_bars_top', 2),
        diameter_top=validated.get('diameter_top', 12),
        n_bars_bottom=validated.get('n_bars_bottom', 2),
        diameter_bottom=validated.get('diameter_bottom', 12)
    )

    return jsonify({'success': True})


@bp.route('/assign-coupling-beam', methods=['POST'])
@handle_errors
@require_session_and_pier
def assign_coupling_beam(session_id: str, pier_key: str, data: dict):
    """
    Asigna una viga del catálogo como viga de acople de un pier.

    Request:
        {
            "session_id": "uuid-xxx",
            "pier_key": "Story1_M1",
            "beam_left": "generic" | "none" | "Story1_B1",
            "beam_right": "generic" | "none" | "Story1_B2"
        }

    Response:
        {"success": true, "result": {...}}
    """
    service = get_analysis_service()

    beam_left_key = data.get('beam_left', 'generic')
    beam_right_key = data.get('beam_right', 'generic')

    # Resolver vigas usando el servicio (lógica de negocio delegada)
    beam_left_config = service.resolve_beam_config(session_id, beam_left_key)
    beam_right_config = service.resolve_beam_config(session_id, beam_right_key)

    # Guardar configuración de vigas
    service.set_pier_coupling_config(
        session_id=session_id,
        pier_key=pier_key,
        has_beam_left=beam_left_key != 'none',
        has_beam_right=beam_right_key != 'none',
        beam_left_config=beam_left_config,
        beam_right_config=beam_right_config
    )

    # Re-analizar el pier y retornar resultado actualizado
    result = service.analyze_single_pier(
        session_id=session_id,
        pier_key=pier_key,
        generate_plot=True
    )

    return jsonify({
        'success': True,
        'result': result
    })


# =============================================================================
# Reportes
# =============================================================================

@bp.route('/generate-report', methods=['POST'])
@handle_errors
@require_session
def generate_report(session_id: str, data: dict):
    """Genera un informe PDF descargable."""
    parsed_data, error = get_session_or_404(session_id)
    if error:
        return error

    # Crear configuración del informe
    config = ReportConfig.from_dict(data)

    # Validar configuración
    total_piers = len(parsed_data.piers)
    validation_errors = config.validate(total_piers)
    if validation_errors:
        return jsonify({
            'success': False,
            'error': 'Errores de validación',
            'validation_errors': validation_errors
        }), 400

    # Ejecutar análisis para obtener resultados actualizados
    moment_axis = data.get('moment_axis', 'M3')
    service = get_analysis_service()
    analysis_result = service.analyze(
        session_id=session_id,
        generate_plots=config.include_pm_diagrams,
        moment_axis=moment_axis
    )

    if not analysis_result.get('success'):
        return jsonify({
            'success': False,
            'error': 'Error al ejecutar análisis: ' + analysis_result.get('error', '')
        }), 500

    results = analysis_result.get('results', [])
    statistics = analysis_result.get('statistics', {})

    if not results:
        return jsonify({
            'success': False,
            'error': 'No se generaron resultados de análisis'
        }), 400

    # Generar PDF
    generator = PDFReportGenerator()
    pdf_bytes = generator.generate_report(
        results=results,
        piers=parsed_data.piers,
        config=config,
        statistics=statistics
    )

    filename = f"Informe_{config.project_name.replace(' ', '_')}.pdf"

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(len(pdf_bytes))
        }
    )


# =============================================================================
# Vigas - Edición de Enfierradura
# =============================================================================

@bp.route('/create-custom-beam', methods=['POST'])
@handle_errors
@require_session
def create_custom_beam(session_id: str, data: dict):
    """
    Crea una viga custom (definida por el usuario, no de ETABS).

    Request:
        {
            "session_id": "uuid-xxx",
            "label": "VC1",
            "story": "Story1",
            "width": 200,
            "depth": 500,
            "length": 3000,
            "fc": 28,
            "n_bars_top": 3,
            "diameter_top": 16,
            "n_bars_bottom": 3,
            "diameter_bottom": 16,
            "stirrup_diameter": 10,
            "stirrup_spacing": 150,
            "n_stirrup_legs": 2
        }

    Response:
        {"success": true, "beam_key": "Story1_VC1"}
    """
    service = get_analysis_service()

    # Delegar creación de viga al servicio
    result = service.create_custom_beam(
        session_id=session_id,
        label=data.get('label', 'Custom'),
        story=data.get('story', 'Story1'),
        length=data.get('length', 3000),
        depth=data.get('depth', 500),
        width=data.get('width', 200),
        fc=data.get('fc', 28),
        n_bars_top=data.get('n_bars_top', 3),
        n_bars_bottom=data.get('n_bars_bottom', 3),
        diameter_top=data.get('diameter_top', 16),
        diameter_bottom=data.get('diameter_bottom', 16),
        stirrup_diameter=data.get('stirrup_diameter', 10),
        stirrup_spacing=data.get('stirrup_spacing', 150),
        n_stirrup_legs=data.get('n_stirrup_legs', 2)
    )

    if not result.get('success'):
        return jsonify(result), 400

    return jsonify(result)


@bp.route('/update-beam-reinforcement', methods=['POST'])
@handle_errors
@require_session_data
@require_element('beam_key', 'beams', 'Viga')
def update_beam_reinforcement(session_id: str, data: dict, parsed_data, beam_key: str, beam):
    """
    Actualiza la enfierradura de una viga.

    Request:
        {
            "session_id": "uuid-xxx",
            "beam_key": "Story1_B1",
            "reinforcement": {
                "n_bars_top": 3,
                "n_bars_bottom": 3,
                "diameter_top": 16,
                "diameter_bottom": 16,
                "stirrup_diameter": 10,
                "stirrup_spacing": 150,
                "n_stirrup_legs": 2
            }
        }

    Response:
        {"success": true, "beam_key": "Story1_B1"}
    """
    reinforcement = data.get('reinforcement', {})

    beam.update_reinforcement(
        n_bars_top=reinforcement.get('n_bars_top'),
        n_bars_bottom=reinforcement.get('n_bars_bottom'),
        diameter_top=reinforcement.get('diameter_top'),
        diameter_bottom=reinforcement.get('diameter_bottom'),
        stirrup_diameter=reinforcement.get('stirrup_diameter'),
        stirrup_spacing=reinforcement.get('stirrup_spacing'),
        n_stirrup_legs=reinforcement.get('n_stirrup_legs')
    )

    return jsonify({
        'success': True,
        'beam_key': beam_key
    })


# =============================================================================
# Health Check
# =============================================================================

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check del módulo."""
    return jsonify({
        'status': 'ok',
        'module': 'structural',
        'version': '1.0.0'
    })
