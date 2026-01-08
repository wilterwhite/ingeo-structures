# app/routes/analysis.py
"""
Endpoints API para el módulo de análisis estructural.
"""
import uuid
import json
import logging
from flask import Blueprint, request, jsonify, current_app, Response

from ..services.pier_analysis import PierAnalysisService
from ..services.report import PDFReportGenerator, ReportConfig


# Crear blueprint
bp = Blueprint('structural', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)

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
                pass  # Ignorar si no es un número válido

        # Generar session_id
        session_id = str(uuid.uuid4())
        logger.info(f"[Upload] Iniciando parseo... session_id={session_id[:8]}")

        # Parsear (ahora acepta hn_ft como parámetro opcional)
        service = get_analysis_service()
        result = service.parse_excel(
            file_content, session_id, hn_ft=hn_ft
        )

        summary = result.get('summary', {})
        logger.info("[Upload] Parseo completado:")
        logger.info(f"         - Piers: {summary.get('total_piers', 0)}")
        logger.info(f"         - Columnas: {summary.get('total_columns', 0)}")
        logger.info(f"         - Vigas: {summary.get('total_beams', 0)}")
        logger.info(f"         - Losas: {summary.get('total_slabs', 0)}")
        return jsonify(result)

    except Exception as e:
        import traceback
        logger.error(f"[Upload] ERROR: {str(e)}")
        traceback.print_exc()
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


@bp.route('/analyze-stream', methods=['POST'])
def analyze_stream():
    """
    Ejecuta el análisis estructural con progreso en tiempo real (SSE).

    Request (JSON):
        Igual que /analyze

    Response:
        Server-Sent Events con formato:
        - data: {"type": "progress", "current": 5, "total": 100, "pier": "P1-A1"}
        - data: {"type": "complete", "result": {...}}
        - data: {"type": "error", "message": "..."}
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
        materials_config = data.get('materials_config', {})

        service = get_analysis_service()

        def generate():
            try:
                for event in service.analyze_with_progress(
                    session_id=session_id,
                    pier_updates=pier_updates,
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


@bp.route('/combination-details', methods=['POST'])
def get_combination_details():
    """
    Obtiene los detalles de diseño para una combinación específica.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "pier_key": "Story_PierLabel",
            "combo_index": 0
        }

    Response:
        {
            "success": true,
            "combo_name": "DWalS5",
            "combo_location": "Bottom",
            "forces": { "P": ..., "M2": ..., "M3": ..., "V2": ..., "V3": ... },
            "flexure": { ... },
            "shear": { "rows": [...] },
            "boundary": { "rows": [...] }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        session_id = data.get('session_id')
        pier_key = data.get('pier_key')
        combo_index = data.get('combo_index', 0)

        if not session_id or not pier_key:
            return jsonify({
                'success': False,
                'error': 'session_id and pier_key are required'
            }), 400

        service = get_analysis_service()
        result = service.get_combination_details(session_id, pier_key, combo_index)

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
            "pier_key": "Story_PierLabel",
            "proposed_config": {  // Opcional - para preview de propuesta
                "n_edge_bars": 6,
                "diameter_edge": 16,
                "n_meshes": 2,
                "diameter_v": 10,
                "spacing_v": 150,
                "thickness": 250  // Si cambió el espesor
            }
        }

    Response:
        {
            "success": true,
            "section_diagram": "base64...",
            "is_proposed": false
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        session_id = data.get('session_id')
        pier_key = data.get('pier_key')
        proposed_config = data.get('proposed_config')  # Opcional

        if not session_id or not pier_key:
            return jsonify({
                'success': False,
                'error': 'session_id and pier_key are required'
            }), 400

        service = get_analysis_service()
        result = service.get_section_diagram(session_id, pier_key, proposed_config)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@bp.route('/set-default-beam', methods=['POST'])
def set_default_beam():
    """
    Configura la viga estándar para la sesión.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "width": 200,
            "height": 500,
            "ln": 1500,
            "n_bars_top": 2,
            "diameter_top": 12,
            "n_bars_bottom": 2,
            "diameter_bottom": 12
        }

    Response:
        { "success": true }
    """
    try:
        data = request.get_json() or {}

        session_id = data.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id'
            }), 400

        service = get_analysis_service()
        service.set_default_coupling_beam(
            session_id=session_id,
            width=float(data.get('width', 200)),
            height=float(data.get('height', 500)),
            ln=float(data.get('ln', 1500)),
            n_bars_top=int(data.get('n_bars_top', 2)),
            diameter_top=int(data.get('diameter_top', 12)),
            n_bars_bottom=int(data.get('n_bars_bottom', 2)),
            diameter_bottom=int(data.get('diameter_bottom', 12))
        )

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@bp.route('/set-pier-beam', methods=['POST'])
def set_pier_beam():
    """
    Configura vigas de acople para un pier y retorna el resultado re-analizado.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "pier_key": "Story_PierLabel",
            "has_beam_left": true,
            "has_beam_right": true,
            "beam_left": { "width": 200, "height": 500, ... },
            "beam_right": { "width": 200, "height": 500, ... }
        }

    Response:
        {
            "success": true,
            "result": { ... resultado actualizado del pier ... }
        }
    """
    try:
        data = request.get_json() or {}

        session_id = data.get('session_id')
        pier_key = data.get('pier_key')

        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id'
            }), 400

        if not pier_key:
            return jsonify({
                'success': False,
                'error': 'Se requiere pier_key'
            }), 400

        # Formatear config de vigas
        def parse_beam_config(beam_data):
            if not beam_data:
                return None
            return {
                'width': float(beam_data.get('width', 200)),
                'height': float(beam_data.get('height', 500)),
                'ln': float(beam_data.get('ln', 1500)),
                'n_bars_top': int(beam_data.get('n_bars_top', 2)),
                'diameter_top': int(beam_data.get('diameter_top', 12)),
                'n_bars_bottom': int(beam_data.get('n_bars_bottom', 2)),
                'diameter_bottom': int(beam_data.get('diameter_bottom', 12))
            }

        service = get_analysis_service()

        # 1. Guardar configuración de vigas
        service.set_pier_coupling_config(
            session_id=session_id,
            pier_key=pier_key,
            has_beam_left=data.get('has_beam_left', True),
            has_beam_right=data.get('has_beam_right', True),
            beam_left_config=parse_beam_config(data.get('beam_left')),
            beam_right_config=parse_beam_config(data.get('beam_right'))
        )

        # 2. Re-analizar el pier y retornar resultado actualizado
        result = service.analyze_single_pier(
            session_id=session_id,
            pier_key=pier_key,
            generate_plot=True
        )

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@bp.route('/generate-report', methods=['POST'])
def generate_report():
    """
    Genera un informe PDF descargable.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "project_name": "Mi Proyecto",
            "top_by_load": 5,
            "top_by_cuantia": 5,
            "include_failing": true,
            "include_proposals": true,
            "include_pm_diagrams": true,
            "include_sections": true,
            "include_full_table": true,
            "moment_axis": "M3"  // Opcional: "M2", "M3", "combined", "SRSS"
        }

    Response:
        PDF file (application/pdf)
    """
    try:
        data = request.get_json() or {}

        session_id = data.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id'
            }), 400

        # Obtener datos de la sesión
        service = get_analysis_service()
        parsed_data = service.get_session_data(session_id)

        if not parsed_data:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada o expirada'
            }), 404

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

        # Obtener resultados y estadísticas
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

        # Retornar PDF como descarga
        filename = f"Informe_{config.project_name.replace(' ', '_')}.pdf"

        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': str(len(pdf_bytes))
            }
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al generar informe: {str(e)}'
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


# =============================================================================
# Endpoints para Losas
# =============================================================================

@bp.route('/analyze-slabs', methods=['POST'])
def analyze_slabs():
    """
    Analiza losas de la sesión actual.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "slab_updates": [  // Opcional - actualizar propiedades de losas
                {
                    "key": "S02_CL_C3",
                    "slab_type": "one_way",  // o "two_way"
                    "diameter_main": 16,
                    "spacing_main": 150
                }
            ],
            "lambda_factor": 1.0  // Opcional - factor por concreto liviano
        }

    Response:
        {
            "success": true,
            "results": [...],
            "statistics": {
                "total_slabs": 5,
                "ok_count": 3,
                "fail_count": 2,
                "pass_rate": 60.0
            }
        }
    """
    from ..services.analysis.slab_service import SlabService

    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id'
            }), 400

        service = get_analysis_service()
        parsed_data = service.get_session_data(session_id)

        if not parsed_data:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada o expirada'
            }), 404

        if not parsed_data.has_slabs:
            return jsonify({
                'success': False,
                'error': 'No hay losas en esta sesión. Asegúrese de cargar un archivo con tabla "Section Cut Forces - Analysis".'
            }), 400

        # Aplicar actualizaciones a las losas si se proporcionan
        slab_updates = data.get('slab_updates', [])
        if slab_updates:
            service.update_slabs_batch(session_id, slab_updates)

        # Crear servicio de losas
        lambda_factor = float(data.get('lambda_factor', 1.0))
        slab_service = SlabService(lambda_factor=lambda_factor)

        # Ejecutar verificaciones
        results = slab_service.verify_all_slabs(parsed_data.slabs, parsed_data.slab_forces)
        statistics = slab_service.get_summary(parsed_data.slabs, parsed_data.slab_forces)

        # Convertir a lista para JSON
        results_list = list(results.values())

        return jsonify({
            'success': True,
            'results': results_list,
            'statistics': statistics
        })

    except Exception as e:
        import traceback
        logger.error(f"[AnalyzeSlabs] ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error al analizar losas: {str(e)}'
        }), 500


@bp.route('/slab-capacities', methods=['POST'])
def get_slab_capacities():
    """
    Obtiene las capacidades de una losa específica.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "slab_key": "S02_CL_C3"
        }

    Response:
        {
            "success": true,
            "slab": {
                "label": "CL @ C3",
                "story": "S02",
                "thickness": 290,
                "width": 1500,
                ...
            },
            "capacities": {
                "phi_Mn": 5.54,
                "phi_Vn": 17.82,
                ...
            }
        }
    """
    from ..services.analysis.slab_service import SlabService

    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        slab_key = data.get('slab_key')

        if not session_id or not slab_key:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id y slab_key'
            }), 400

        service = get_analysis_service()
        parsed_data = service.get_session_data(session_id)

        if not parsed_data:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada o expirada'
            }), 404

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

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@bp.route('/analyze-punching', methods=['POST'])
def analyze_punching():
    """
    Analiza punzonamiento para losas 2-Way.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "slab_key": "S02_CL_C3",  // Opcional - si no se especifica, analiza todas
            "column_c1": 400,          // Opcional - dimensión columna (mm)
            "column_c2": 400,          // Opcional
            "position": "interior"     // interior, edge, corner
        }

    Response:
        {
            "success": true,
            "result": {...}  // o "results": [...] si se analizan todas
        }
    """
    from ..services.analysis.punching_service import PunchingService

    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id'
            }), 400

        service = get_analysis_service()
        parsed_data = service.get_session_data(session_id)

        if not parsed_data:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada o expirada'
            }), 404

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

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500
