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
    validate_upload_file,
    parse_hn_ft,
    error_response,
    success_response,
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
    # Validar archivo
    file, error = validate_upload_file(request, ['.xlsx'])
    if error:
        return error_response(error)

    try:
        logger.info(f"[Upload] Recibiendo archivo: {file.filename}")
        file_content = file.read()
        logger.info(f"[Upload] Tamaño: {len(file_content) / 1024:.1f} KB")

        hn_ft = parse_hn_ft(request.form)
        session_id = str(uuid.uuid4())
        logger.info(f"[Upload] Iniciando parseo... session_id={session_id[:8]}")

        service = get_analysis_service()
        result = service.parse_excel(file_content, session_id, hn_ft=hn_ft)

        summary = result.get('summary', {})
        logger.info(f"[Upload] Parseo completado: {summary.get('total_piers', 0)} piers")

        return jsonify(result)

    except Exception as e:
        logger.exception(f"[Upload] ERROR: {str(e)}")
        return error_response(f'Error al procesar el archivo: {str(e)}', 500)


@bp.route('/upload-stream', methods=['POST'])
def upload_stream():
    """
    Sube y parsea un archivo Excel de ETABS con progreso en tiempo real (SSE).

    Request:
        multipart/form-data con campos:
        - 'file': archivo Excel (requerido)
        - 'hn_ft': altura del edificio en pies (opcional)
        - 'session_id': ID de sesión existente para merge (opcional)

    Response:
        Stream SSE con eventos:
        - progress: {type: 'progress', phase, current, total, element}
        - complete: {type: 'complete', result: {success, session_id, summary}}
        - error: {type: 'error', message}

    Si se proporciona session_id existente, combina datos con la sesión existente.
    """
    # Validar archivo
    file, error = validate_upload_file(request, ['.xlsx'])
    if error:
        return error_response(error)

    try:
        logger.info(f"[Upload-Stream] Recibiendo archivo: {file.filename}")
        file_content = file.read()
        logger.info(f"[Upload-Stream] Tamaño: {len(file_content) / 1024:.1f} KB")

        hn_ft = parse_hn_ft(request.form)

        # Obtener session_id existente o crear nuevo
        existing_session_id = request.form.get('session_id')
        session_id = existing_session_id or str(uuid.uuid4())
        merge = bool(existing_session_id)

        if merge:
            logger.info(f"[Upload-Stream] Combinando con sesión existente: {session_id[:8]}")
        else:
            logger.info(f"[Upload-Stream] Nueva sesión: {session_id[:8]}")

        service = get_analysis_service()
        filename = file.filename or "unknown.xlsx"

        def generate():
            try:
                for event in service.parse_excel_with_progress(
                    file_content, session_id, hn_ft=hn_ft, merge=merge, filename=filename
                ):
                    yield f"data: {json.dumps(event)}\n\n"
            except Exception as e:
                logger.exception(f"[Upload-Stream] ERROR: {str(e)}")
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
        logger.exception(f"[Upload-Stream] ERROR: {str(e)}")
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
    seismic_category = data.get('seismic_category', 'SPECIAL')

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
                materials_config=materials_config,
                seismic_category=seismic_category
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


# =============================================================================
# Sesiones y Combinaciones
# =============================================================================


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

@bp.route('/combination-details', methods=['POST'])
@handle_errors
@require_session_and_pier
def get_combination_details(session_id: str, pier_key: str, data: dict):
    """Obtiene los detalles de diseño para una combinación específica."""
    combo_index = data.get('combo_index', 0)

    service = get_analysis_service()
    result = service.get_combination_details(session_id, pier_key, combo_index)

    return jsonify(result)


@bp.route('/element-capacities', methods=['POST'])
@handle_errors
@require_session
def get_element_capacities(session_id: str, data: dict):
    """
    Obtiene capacidades de cualquier tipo de elemento estructural.

    Endpoint unificado para pier, column, beam y drop_beam.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "element_key": "Story1_M1",
            "element_type": "pier"  // pier, column, beam, drop_beam
        }

    Response:
        {
            "success": true,
            "element_type": "pier",
            "element_info": {...},
            "reinforcement": {...},
            "capacities": {...},
            "slenderness": {...},
            "flexure_design": {...},
            "shear_design": {...},
            "boundary_check": {...},  // solo pier/drop_beam
            "combinations_list": [...]
        }
    """
    element_type = data.get('element_type', 'pier')
    element_key = data.get('element_key')

    if not element_key:
        return jsonify({
            'success': False,
            'error': 'element_key es requerido'
        }), 400

    valid_types = ('pier', 'column', 'beam', 'drop_beam', 'strut')
    if element_type not in valid_types:
        return jsonify({
            'success': False,
            'error': f'element_type debe ser uno de: {", ".join(valid_types)}'
        }), 400

    # STRUT es internamente un Column verificado sin confinamiento
    # Usar 'column' para obtener capacidades
    effective_type = 'column' if element_type == 'strut' else element_type

    service = get_analysis_service()
    result = service.get_element_capacities(session_id, element_key, effective_type)

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
    total_piers = len(parsed_data.vertical_elements)
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
        piers=parsed_data.vertical_elements,
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
# Property Modifiers (Cracking/Agrietamiento)
# =============================================================================

@bp.route('/apply-cracking', methods=['POST'])
@handle_errors
@require_session_data
def apply_cracking(session_id: str, data: dict, parsed_data):
    """
    Aplica agrietamiento a un elemento basado en su DCR.

    El factor de agrietamiento es 1/DCR, aplicado sobre los Property Modifiers
    actuales del elemento. Esto modifica la rigidez del elemento para que
    redistribuya cargas a otros elementos del modelo.

    Request:
        {
            "session_id": "uuid-xxx",
            "element_key": "Story1_C1",
            "element_type": "column" | "pier" | "beam" | "strut",
            "dcr": 5.0,
            "mode": "flexure" | "shear" | "axial" | "all"
        }

    Response:
        {
            "success": true,
            "element_key": "Story1_C1",
            "new_section_name": "C45x45-PM:0.20M2-0.20M3",
            "property_modifiers": {
                "pm_axial": 1.0,
                "pm_m2": 0.20,
                "pm_m3": 0.20,
                ...
            }
        }
    """
    element_key = data.get('element_key')
    element_type = data.get('element_type', 'column')
    dcr = float(data.get('dcr', 1.0))
    mode = data.get('mode', 'flexure')

    if not element_key:
        return error_response('Se requiere element_key')

    if dcr <= 0:
        return error_response('DCR debe ser mayor a 0')

    # Buscar elemento según tipo
    element = None
    if element_type in ('column', 'pier', 'strut'):
        element = parsed_data.piers.get(element_key)
    elif element_type in ('beam', 'drop_beam'):
        element = parsed_data.beams.get(element_key)

    if not element:
        return error_response(f'{element_type.capitalize()} {element_key} no encontrado')

    # Aplicar agrietamiento
    try:
        element.apply_cracking(dcr, mode)
    except ValueError as e:
        return error_response(str(e))

    logger.info(
        f"[Cracking] {element_type} {element_key}: DCR={dcr:.2f}, "
        f"mode={mode}, new_section={element.section_name}"
    )

    return jsonify({
        'success': True,
        'element_key': element_key,
        'new_section_name': element.section_name,
        'property_modifiers': {
            'pm_axial': element.pm_axial,
            'pm_m2': element.pm_m2,
            'pm_m3': element.pm_m3,
            'pm_v2': element.pm_v2,
            'pm_v3': element.pm_v3,
            'pm_torsion': element.pm_torsion,
            'pm_weight': element.pm_weight,
            'summary': element.pm_summary,
            'has_modifiers': element.has_property_modifiers,
        }
    })


@bp.route('/reset-cracking', methods=['POST'])
@handle_errors
@require_session_data
def reset_cracking(session_id: str, data: dict, parsed_data):
    """
    Resetea los Property Modifiers de un elemento a 1.0.

    Request:
        {
            "session_id": "uuid-xxx",
            "element_key": "Story1_C1",
            "element_type": "column" | "pier" | "beam" | "strut"
        }

    Response:
        {
            "success": true,
            "element_key": "Story1_C1",
            "new_section_name": "C45x45"
        }
    """
    element_key = data.get('element_key')
    element_type = data.get('element_type', 'column')

    if not element_key:
        return error_response('Se requiere element_key')

    # Buscar elemento según tipo
    element = None
    if element_type in ('column', 'pier', 'strut'):
        element = parsed_data.piers.get(element_key)
    elif element_type in ('beam', 'drop_beam'):
        element = parsed_data.beams.get(element_key)

    if not element:
        return error_response(f'{element_type.capitalize()} {element_key} no encontrado')

    # Resetear Property Modifiers
    element.reset_property_modifiers()

    logger.info(f"[Cracking] Reset {element_type} {element_key} -> {element.section_name}")

    return jsonify({
        'success': True,
        'element_key': element_key,
        'new_section_name': element.section_name,
    })


# =============================================================================
# E2K Section Cuts Generator
# =============================================================================

@bp.route('/process-e2k', methods=['POST'])
def process_e2k():
    """
    Procesa un archivo E2K de ETABS y genera Section Cuts para todos los grupos.

    Request:
        multipart/form-data con campos:
        - 'file': archivo E2K (requerido)

    Returns:
        El archivo E2K modificado con los Section Cuts generados.
    """
    from ..services.parsing.e2k_processor import E2KProcessor

    # Validar archivo
    file, error = validate_upload_file(request, ['.e2k'])
    if error:
        return error_response(error)

    try:
        processor = E2KProcessor()
        result = processor.process(file.read())

        # Nombre del archivo de salida
        original_name = file.filename.rsplit('.', 1)[0]
        output_filename = f"{original_name}_with_scuts.e2k"

        return Response(
            result.content.encode('utf-8'),
            mimetype='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename="{output_filename}"',
                'X-Section-Cuts-Generated': str(result.n_section_cuts),
                'X-Total-Groups': str(result.n_groups)
            }
        )

    except ValueError as e:
        # Error esperado (no hay section cuts nuevos)
        return error_response(str(e))
    except Exception as e:
        logger.error(f"Error procesando E2K: {e}")
        return error_response(str(e), 500)


# =============================================================================
# Tablas ETABS (Vista de verificación)
# =============================================================================

@bp.route('/session/<session_id>/tables', methods=['GET'])
@handle_errors
def get_session_tables(session_id: str):
    """
    Obtiene las tablas crudas de ETABS de una sesión.

    Retorna las tablas extraídas del Excel en formato JSON para que el
    usuario pueda verificar que los datos se leyeron correctamente.

    Response:
        {
            "success": true,
            "tables": {
                "pier_props": {
                    "columns": ["Story", "Pier", "Width Bottom", ...],
                    "rows": [["Story1", "P1", "300", ...], ...],
                    "total_rows": 45
                },
                "frame_section": {...},
                ...
            }
        }
    """
    service = get_analysis_service()
    tables = service.get_raw_tables(session_id)

    if tables is None:
        return error_response('Sesión no encontrada o sin tablas cargadas', 404)

    return jsonify({
        'success': True,
        'tables': tables
    })


@bp.route('/export-cracked-e2k', methods=['POST'])
@handle_errors
@require_session_data
def export_cracked_e2k(session_id: str, data: dict, parsed_data):
    """
    Exporta un archivo E2K con las secciones agrietadas.

    Crea nuevas secciones de frame con Property Modifiers aplicados
    y actualiza las asignaciones de elementos a las nuevas secciones.

    Request:
        multipart/form-data con campos:
        - 'file': archivo E2K original (requerido)
        - 'session_id': ID de sesión (requerido)

    Response:
        El archivo E2K modificado con secciones agrietadas.
    """
    from ..services.parsing.e2k_processor import E2KProcessor

    # Validar archivo E2K
    file, error = validate_upload_file(request, ['.e2k'])
    if error:
        return error_response(error)

    # Recolectar elementos agrietados de la sesión
    cracked_elements = []

    # Columnas/Piers con PM modificados
    for key, element in parsed_data.piers.items():
        if element.has_property_modifiers:
            cracked_elements.append({
                'section_name': element.section_name,
                'base_section_name': element.base_section_name,
                'new_section_name': element.section_name,
                'pm_axial': element.pm_axial,
                'pm_m2': element.pm_m2,
                'pm_m3': element.pm_m3,
                'pm_v2': element.pm_v2,
                'pm_v3': element.pm_v3,
                'pm_torsion': element.pm_torsion,
                'pm_weight': element.pm_weight,
            })

    # Vigas con PM modificados
    for key, element in parsed_data.beams.items():
        if element.has_property_modifiers:
            cracked_elements.append({
                'section_name': element.section_name,
                'base_section_name': element.base_section_name,
                'new_section_name': element.section_name,
                'pm_axial': element.pm_axial,
                'pm_m2': element.pm_m2,
                'pm_m3': element.pm_m3,
                'pm_v2': element.pm_v2,
                'pm_v3': element.pm_v3,
                'pm_torsion': element.pm_torsion,
                'pm_weight': element.pm_weight,
            })

    if not cracked_elements:
        return error_response('No hay elementos agrietados para exportar')

    try:
        processor = E2KProcessor()
        result = processor.export_cracked_sections(
            file.read(),
            cracked_elements
        )

        # Nombre del archivo de salida
        original_name = file.filename.rsplit('.', 1)[0]
        output_filename = f"{original_name}_cracked.e2k"

        logger.info(
            f"[E2K Export] {result.n_sections_modified} secciones, "
            f"{result.n_elements_updated} elementos actualizados"
        )

        return Response(
            result.content.encode('utf-8'),
            mimetype='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename="{output_filename}"',
                'X-Sections-Modified': str(result.n_sections_modified),
                'X-Elements-Updated': str(result.n_elements_updated)
            }
        )

    except Exception as e:
        logger.error(f"Error exportando E2K agrietado: {e}")
        return error_response(str(e), 500)
