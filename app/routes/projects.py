# app/routes/projects.py
"""
Endpoints para gestión de proyectos con persistencia.

Proporciona:
- Crear nuevo proyecto desde Excel
- Guardar estado parseado y resultados
- Cargar proyecto existente (instantáneo)
- Listar y eliminar proyectos
"""
import threading
import uuid
from flask import Blueprint, request, jsonify

from .common import (
    handle_errors,
    require_session,
    get_analysis_service,
    get_json_data,
)
from ..services.persistence import ProjectManager

bp = Blueprint('projects', __name__, url_prefix='/api/projects')

_project_manager = None
_pm_lock = threading.Lock()


def get_project_manager() -> ProjectManager:
    """Obtiene o crea la instancia del ProjectManager. Thread-safe."""
    global _project_manager
    if _project_manager is None:
        with _pm_lock:
            if _project_manager is None:
                _project_manager = ProjectManager()
    return _project_manager


# =============================================================================
# LISTAR PROYECTOS
# =============================================================================

@bp.route('/list', methods=['GET'])
@handle_errors
def list_projects():
    """Lista todos los proyectos disponibles."""
    pm = get_project_manager()
    projects = pm.list_projects()
    return jsonify({
        'success': True,
        'projects': projects
    })


# =============================================================================
# CREAR PROYECTO
# =============================================================================

@bp.route('/create', methods=['POST'])
@handle_errors
def create_project():
    """Crea un nuevo proyecto desde un archivo Excel."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Se requiere un archivo Excel'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No se selecciono ningun archivo'}), 400

    name = request.form.get('name', file.filename.rsplit('.', 1)[0])
    description = request.form.get('description', '')
    hn_ft_str = request.form.get('hn_ft')
    hn_ft = float(hn_ft_str) if hn_ft_str else None

    excel_content = file.read()

    pm = get_project_manager()
    result = pm.create_project(
        name=name,
        excel_content=excel_content,
        excel_filename=file.filename,
        description=description,
        hn_ft=hn_ft
    )

    return jsonify(result)


# =============================================================================
# GUARDAR PROYECTO
# =============================================================================

@bp.route('/save', methods=['POST'])
@handle_errors
@require_session
def save_project(session_id: str, data: dict):
    """Guarda el estado parseado y los resultados de análisis."""
    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'success': False, 'error': 'Se requiere project_id'}), 400

    service = get_analysis_service()
    parsed_data = service.get_session_data(session_id)
    if not parsed_data:
        return jsonify({'success': False, 'error': 'Sesion no encontrada'}), 404

    pm = get_project_manager()

    # Guardar parsed_data
    result = pm.save_parsed_data(project_id, parsed_data)

    # Guardar resultados de análisis si vienen en el request
    results = data.get('results')
    if results and result.get('success'):
        pm.save_results(project_id, results)

    return jsonify(result)


# =============================================================================
# CARGAR PROYECTO
# =============================================================================

@bp.route('/load', methods=['POST'])
@handle_errors
def load_project():
    """Carga un proyecto existente y crea una sesión con los datos."""
    data = get_json_data()
    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'success': False, 'error': 'Se requiere project_id'}), 400

    pm = get_project_manager()
    result = pm.load_project(project_id)

    if not result.get('success'):
        return jsonify(result), 404

    service = get_analysis_service()
    session_id = str(uuid.uuid4())

    parsed_data = result['parsed_data']

    # Registrar en session_manager
    service._session_manager._sessions[session_id] = parsed_data

    # Construir summary para el frontend
    summary = _build_summary_from_parsed_data(parsed_data)

    return jsonify({
        'success': True,
        'session_id': session_id,
        'project_id': project_id,
        'metadata': result['metadata'],
        'summary': summary,
        'results': result.get('results'),
        'has_results': result.get('has_results', False),
    })


def _build_summary_from_parsed_data(parsed_data) -> dict:
    """Construye el summary para el frontend desde ParsedData."""
    from ..domain.entities import VerticalElementSource, HorizontalElementSource

    # Separar elementos verticales por source
    piers_list = []
    columns_list = []
    for key, elem in parsed_data.vertical_elements.items():
        item = {
            'key': key,
            'label': elem.label,
            'story': elem.story,
            'width': elem.thickness,  # tw
            'fc': elem.fc,
        }
        if elem.source == VerticalElementSource.PIER:
            item['grilla'] = getattr(elem, 'grilla', '')
            item['eje'] = getattr(elem, 'eje', '')
            item['thickness'] = elem.thickness
            piers_list.append(item)
        else:  # FRAME (column)
            item['section'] = getattr(elem, 'section_name', '')
            item['depth'] = elem.length
            columns_list.append(item)

    # Separar elementos horizontales por source
    beams_list = []
    drop_beams_list = []
    for key, elem in parsed_data.horizontal_elements.items():
        item = {
            'key': key,
            'label': elem.label,
            'story': elem.story,
            'depth': elem.depth,
            'width': elem.width,
            'fc': elem.fc,
        }
        if elem.source == HorizontalElementSource.DROP_BEAM:
            drop_beams_list.append(item)
        else:  # FRAME or SPANDREL
            item['section'] = getattr(elem, 'section_name', '')
            beams_list.append(item)

    # Grillas y ejes solo de piers
    grillas = sorted(set(
        getattr(e, 'grilla', '') for e in parsed_data.vertical_elements.values()
        if e.source == VerticalElementSource.PIER and getattr(e, 'grilla', '')
    ))
    axes = sorted(set(
        getattr(e, 'eje', '') for e in parsed_data.vertical_elements.values()
        if e.source == VerticalElementSource.PIER and getattr(e, 'eje', '')
    ))

    return {
        'total_piers': len(piers_list),
        'total_columns': len(columns_list),
        'total_beams': len(beams_list),
        'total_drop_beams': len(drop_beams_list),
        'piers_list': piers_list,
        'columns_list': columns_list,
        'beams_list': beams_list,
        'drop_beams_list': drop_beams_list,
        'stories': parsed_data.stories,
        'grillas': grillas,
        'axes': axes,
        'materials': parsed_data.materials,
    }


# =============================================================================
# ELIMINAR PROYECTO
# =============================================================================

@bp.route('/delete', methods=['POST'])
@handle_errors
def delete_project():
    """Elimina un proyecto."""
    data = get_json_data()
    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'success': False, 'error': 'Se requiere project_id'}), 400

    pm = get_project_manager()
    result = pm.delete_project(project_id)

    if not result.get('success'):
        return jsonify(result), 404

    return jsonify(result)


# =============================================================================
# ACTUALIZAR METADATA
# =============================================================================

@bp.route('/update', methods=['POST'])
@handle_errors
def update_project():
    """Actualiza nombre y descripción de un proyecto."""
    data = get_json_data()
    project_id = data.get('project_id')
    name = data.get('name')

    if not project_id or not name:
        return jsonify({'success': False, 'error': 'Se requiere project_id y name'}), 400

    pm = get_project_manager()
    result = pm.update_project_name(
        project_id=project_id,
        name=name,
        description=data.get('description')
    )

    if not result.get('success'):
        return jsonify(result), 404

    return jsonify(result)


# =============================================================================
# OBTENER METADATA
# =============================================================================

@bp.route('/info/<project_id>', methods=['GET'])
@handle_errors
def get_project_info(project_id: str):
    """Obtiene la metadata de un proyecto."""
    pm = get_project_manager()
    metadata = pm.get_project_metadata(project_id)

    if not metadata:
        return jsonify({'success': False, 'error': 'Proyecto no encontrado'}), 404

    return jsonify({
        'success': True,
        'metadata': metadata
    })
