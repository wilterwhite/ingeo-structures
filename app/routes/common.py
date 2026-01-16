# app/routes/common.py
"""
Utilidades compartidas para rutas de la API.

Proporciona decoradores y funciones comunes para validación,
manejo de errores y acceso a servicios.
"""
import logging
import threading
from functools import wraps
from typing import Callable, Any, Tuple

from flask import request, jsonify, Blueprint

from ..services.structural_analysis import StructuralAnalysisService
from ..services.factory import ServiceFactory
from ..services.analysis.element_orchestrator import ElementOrchestrator
from ..services.presentation.modal_data_service import ElementDetailsService
from ..services.presentation.result_formatter import ResultFormatter
from ..services.analysis.statistics_service import calculate_statistics
from ..domain.chapter18.common import SeismicCategory
from ..domain.constants.materials import (
    BAR_AREAS,
    AVAILABLE_DIAMETERS,
    LAMBDA_NORMAL,
    LAMBDA_SAND_LIGHTWEIGHT,
    LAMBDA_ALL_LIGHTWEIGHT,
)
from ..domain.constants.reinforcement import (
    RHO_MIN,
    MAX_SPACING_SEISMIC_MM,
    FY_DEFAULT_MPA,
    COVER_DEFAULT_PIER_MM,
    COVER_DEFAULT_COLUMN_MM,
    COVER_DEFAULT_BEAM_MM,
)
from ..domain.constants.phi_chapter21 import DCR_OK, DCR_WARN

# Blueprint para endpoints comunes
bp = Blueprint('common', __name__, url_prefix='/api')

logger = logging.getLogger(__name__)

# Path para el archivo de log del frontend (se sobreescribe, no acumula)
FRONTEND_LOG_PATH = 'frontend_state.log'

# Instancias globales (singleton pattern con thread-safety)
_analysis_service = None
_orchestrator = None
_element_details_service = None
_singleton_lock = threading.Lock()


def get_analysis_service() -> StructuralAnalysisService:
    """
    Obtiene o crea la instancia del servicio de análisis.

    Thread-safe mediante double-checked locking pattern.
    """
    global _analysis_service
    if _analysis_service is None:
        with _singleton_lock:
            if _analysis_service is None:
                _analysis_service = ServiceFactory.create_default_analysis_service()
    return _analysis_service


def get_orchestrator() -> ElementOrchestrator:
    """
    Obtiene o crea la instancia del orquestador de elementos.

    ElementOrchestrator es stateless, por lo que una sola instancia
    es suficiente para toda la aplicación. Thread-safe.
    """
    global _orchestrator
    if _orchestrator is None:
        with _singleton_lock:
            if _orchestrator is None:
                _orchestrator = ElementOrchestrator()
    return _orchestrator


def get_element_details_service() -> ElementDetailsService:
    """Obtiene o crea la instancia del servicio de detalles de elementos. Thread-safe."""
    global _element_details_service
    if _element_details_service is None:
        with _singleton_lock:
            if _element_details_service is None:
                session_manager = get_analysis_service()._session_manager
                _element_details_service = ElementDetailsService(session_manager)
    return _element_details_service


def get_json_data() -> dict:
    """Obtiene datos JSON del request de forma estandarizada."""
    return request.get_json() or {}


def handle_errors(f: Callable) -> Callable:
    """
    Decorador para manejo uniforme de excepciones.

    Captura excepciones y retorna respuestas JSON consistentes:
    - ValueError: 400 Bad Request
    - KeyError: 400 Bad Request
    - Exception: 500 Internal Server Error (con logging)
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Any:
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except KeyError as e:
            return jsonify({
                'success': False,
                'error': f'Campo requerido faltante: {e}'
            }), 400
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Error en {f.__name__}: {str(e)}\n{tb}")
            return jsonify({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }), 500
    return decorated


def require_session(f: Callable) -> Callable:
    """
    Decorador que valida session_id en el request JSON.

    Extrae session_id y data, pasándolos como kwargs al endpoint.
    Retorna 400 si no hay session_id.

    Uso:
        @bp.route('/endpoint', methods=['POST'])
        @handle_errors
        @require_session
        def endpoint(session_id: str, data: dict):
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Any:
        data = get_json_data()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id'
            }), 400

        return f(*args, session_id=session_id, data=data, **kwargs)
    return decorated


def require_session_and_element(element_key_name: str) -> Callable:
    """
    Decorador genérico que valida session_id y una clave de elemento.

    Args:
        element_key_name: Nombre de la clave del elemento (ej: 'pier_key', 'slab_key')

    Uso:
        @bp.route('/endpoint', methods=['POST'])
        @handle_errors
        @require_session_and_element('pier_key')
        def endpoint(session_id: str, pier_key: str, data: dict):
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs) -> Any:
            data = get_json_data()
            session_id = data.get('session_id')
            element_key = data.get(element_key_name)

            if not session_id or not element_key:
                return jsonify({
                    'success': False,
                    'error': f'Se requiere session_id y {element_key_name}'
                }), 400

            # Pasar element_key con su nombre original
            kwargs[element_key_name] = element_key
            return f(*args, session_id=session_id, data=data, **kwargs)
        return decorated
    return decorator


# Aliases para compatibilidad hacia atrás
def require_session_and_pier(f: Callable) -> Callable:
    """Alias de require_session_and_element('pier_key')."""
    return require_session_and_element('pier_key')(f)


def get_session_or_404(session_id: str):
    """
    Obtiene datos de sesión o retorna error 404.

    Args:
        session_id: ID de la sesión

    Returns:
        Tuple (parsed_data, None) si existe
        Tuple (None, error_response) si no existe
    """
    service = get_analysis_service()
    parsed_data = service.get_session_data(session_id)

    if not parsed_data:
        return None, (jsonify({
            'success': False,
            'error': 'Sesión no encontrada o expirada'
        }), 404)

    return parsed_data, None


def require_session_data(f: Callable) -> Callable:
    """
    Decorador que valida session_id y obtiene parsed_data.

    Combina require_session + get_session_or_404 en un solo decorador.
    Pasa session_id, data y parsed_data como kwargs.

    Uso:
        @bp.route('/endpoint', methods=['POST'])
        @handle_errors
        @require_session_data
        def endpoint(session_id: str, data: dict, parsed_data):
            # parsed_data ya está validado y disponible
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Any:
        data = get_json_data()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id'
            }), 400

        parsed_data, error = get_session_or_404(session_id)
        if error:
            return error

        return f(*args, session_id=session_id, data=data, parsed_data=parsed_data, **kwargs)
    return decorated


def require_element(element_key_name: str, collection_name: str, element_type_label: str) -> Callable:
    """
    Decorador que valida existencia de un elemento en parsed_data.

    Debe usarse DESPUÉS de require_session_data.

    Args:
        element_key_name: Nombre del parámetro en data (ej: 'column_key')
        collection_name: Nombre de la colección en parsed_data (ej: 'columns')
        element_type_label: Etiqueta para mensajes de error (ej: 'Columna')

    Uso:
        @bp.route('/endpoint', methods=['POST'])
        @handle_errors
        @require_session_data
        @require_element('column_key', 'columns', 'Columna')
        def endpoint(session_id: str, data: dict, parsed_data, column_key: str, column):
            # column ya está validada y disponible
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, session_id: str, data: dict, parsed_data, **kwargs) -> Any:
            element_key = data.get(element_key_name)

            if not element_key:
                return jsonify({
                    'success': False,
                    'error': f'Se requiere {element_key_name}'
                }), 400

            collection = getattr(parsed_data, collection_name, {})
            if element_key not in collection:
                return jsonify({
                    'success': False,
                    'error': f'{element_type_label} "{element_key}" no encontrada'
                }), 404

            element = collection[element_key]
            kwargs[element_key_name] = element_key
            kwargs[collection_name.rstrip('s')] = element  # 'columns' -> 'column'

            return f(*args, session_id=session_id, data=data, parsed_data=parsed_data, **kwargs)
        return decorated
    return decorator


def validate_positive_numeric(data: dict, fields: dict) -> Tuple[dict, list]:
    """
    Valida que los campos numéricos del request sean positivos.

    Args:
        data: Diccionario con datos del request JSON
        fields: Dict {field_name: (type, required)}
                type puede ser 'int' o 'float'
                required es bool

    Returns:
        Tuple (validated_data, errors)
        - validated_data: Dict con valores convertidos y validados
        - errors: Lista de mensajes de error (vacía si todo OK)

    Example:
        fields = {
            'diameter': ('int', True),
            'spacing': ('int', True),
            'cover': ('float', False)
        }
        validated, errors = validate_positive_numeric(data, fields)
    """
    validated = {}
    errors = []

    for field_name, (field_type, required) in fields.items():
        value = data.get(field_name)

        # Si no existe y es requerido
        if value is None:
            if required:
                errors.append(f"Campo requerido: {field_name}")
            continue

        # Convertir al tipo correcto
        try:
            if field_type == 'int':
                converted = int(value)
            else:  # float
                converted = float(value)

            # Validar que sea positivo
            if converted <= 0:
                errors.append(f"{field_name} debe ser positivo (recibido: {converted})")
            else:
                validated[field_name] = converted

        except (ValueError, TypeError):
            errors.append(f"{field_name} debe ser un número válido (recibido: {value})")

    return validated, errors


def parse_seismic_params(data: dict) -> Tuple[SeismicCategory, float]:
    """
    Parsea parámetros sísmicos desde request data.

    Extrae la categoría sísmica y el factor lambda del diccionario
    de datos del request, con valores por defecto seguros.

    Args:
        data: Diccionario con datos del request JSON

    Returns:
        Tuple con (SeismicCategory, lambda_factor)
        - category: SPECIAL, INTERMEDIATE u ORDINARY (default: SPECIAL)
        - lambda_factor: Factor para concreto liviano (default: 1.0)
    """
    category_str = data.get('category', 'SPECIAL').upper()
    try:
        category = SeismicCategory[category_str]
    except KeyError:
        category = SeismicCategory.SPECIAL

    lambda_factor = float(data.get('lambda_factor', 1.0))
    return category, lambda_factor


# =============================================================================
# Helpers de Upload y Response
# =============================================================================

def validate_upload_file(
    req,
    allowed_extensions: list = None,
    field_name: str = 'file'
) -> Tuple[Any, str]:
    """
    Valida archivo subido en request.

    Args:
        req: Flask request object
        allowed_extensions: Lista de extensiones permitidas (ej: ['.xlsx', '.e2k'])
        field_name: Nombre del campo en el form (default: 'file')

    Returns:
        Tuple (file_object, error_message)
        - Si válido: (file, None)
        - Si error: (None, mensaje_de_error)

    Example:
        file, error = validate_upload_file(request, ['.xlsx'])
        if error:
            return jsonify({'success': False, 'error': error}), 400
    """
    if allowed_extensions is None:
        allowed_extensions = ['.xlsx']

    if field_name not in req.files:
        return None, f'No se proporcionó archivo. Use el campo "{field_name}".'

    file = req.files[field_name]

    if not file.filename:
        return None, 'Archivo vacío'

    # Verificar extensión
    filename_lower = file.filename.lower()
    if not any(filename_lower.endswith(ext) for ext in allowed_extensions):
        ext_list = ', '.join(allowed_extensions)
        return None, f'El archivo debe tener extensión: {ext_list}'

    return file, None


def parse_hn_ft(form_data) -> float:
    """
    Extrae y convierte hn_ft (altura del edificio en pies) desde form data.

    Args:
        form_data: request.form o diccionario similar

    Returns:
        float si válido, None si no existe o inválido
    """
    hn_ft_str = form_data.get('hn_ft')
    if hn_ft_str:
        try:
            return float(hn_ft_str)
        except ValueError:
            pass
    return None


def error_response(message: str, code: int = 400, details: dict = None):
    """
    Genera respuesta JSON de error estandarizada.

    Args:
        message: Mensaje de error principal
        code: Código HTTP (default 400)
        details: Diccionario con detalles adicionales (opcional)

    Returns:
        Tuple (Response, code) para retornar desde endpoint
    """
    response = {
        'success': False,
        'error': message
    }
    if details:
        response.update(details)
    return jsonify(response), code


def success_response(data: dict = None, code: int = 200):
    """
    Genera respuesta JSON de éxito estandarizada.

    Args:
        data: Diccionario con datos a incluir (opcional)
        code: Código HTTP (default 200)

    Returns:
        Tuple (Response, code) para retornar desde endpoint
    """
    response = {'success': True}
    if data:
        response.update(data)
    return jsonify(response), code


# =============================================================================
# ENDPOINT: Constantes del Backend
# =============================================================================

@bp.route('/frontend-log', methods=['POST'])
def write_frontend_log():
    """
    Escribe el estado del frontend a un archivo de log.

    Se sobreescribe en cada llamada (no acumula).
    Útil para debugging: permite ver el estado de las tablas sin acceso al navegador.
    """
    data = get_json_data()
    content = data.get('content', '')

    try:
        with open(FRONTEND_LOG_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error escribiendo frontend log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/constants', methods=['GET'])
def get_constants():
    """
    Retorna constantes ACI 318-25 para uso en frontend.

    Este endpoint es la ÚNICA fuente de verdad para constantes estructurales.
    El frontend debe consumir estos valores en lugar de definirlos localmente.

    Response:
        {
            "bar_areas": {6: 28.3, 8: 50.3, ...},
            "available_diameters": [6, 8, 10, ...],
            "lambda_factors": {"normal": 1.0, "sand_lightweight": 0.85, ...},
            "dcr_thresholds": {"ok": 0.67, "warn": 1.0},
            "reinforcement": {"rho_min": 0.0025, "max_spacing_mm": 457, ...},
            "covers": {"pier": 40, "column": 40, "beam": 40},
            "diameters": {"malla": [...], "borde": [...], ...},
            "spacings": {"malla": [...], "estribos": [...], ...}
        }
    """
    return jsonify({
        # Áreas de barras (mm²)
        'bar_areas': {str(k): v for k, v in BAR_AREAS.items()},
        'available_diameters': AVAILABLE_DIAMETERS,

        # Factores lambda para concreto liviano
        'lambda_factors': {
            'normal': LAMBDA_NORMAL,
            'sand_lightweight': LAMBDA_SAND_LIGHTWEIGHT,
            'all_lightweight': LAMBDA_ALL_LIGHTWEIGHT,
        },

        # Umbrales DCR para clasificación visual (desde domain/constants)
        # DCR <= 0.67 (SF >= 1.5): OK
        # DCR <= 1.0 (SF >= 1.0): WARN
        # DCR > 1.0: FAIL
        'dcr_thresholds': {
            'ok': DCR_OK,
            'warn': DCR_WARN,
        },

        # Constantes de refuerzo
        'reinforcement': {
            'rho_min': RHO_MIN,
            'max_spacing_mm': MAX_SPACING_SEISMIC_MM,
            'fy_default_mpa': FY_DEFAULT_MPA,
        },

        # Recubrimientos por defecto (mm)
        'covers': {
            'pier': COVER_DEFAULT_PIER_MM,
            'column': COVER_DEFAULT_COLUMN_MM,
            'beam': COVER_DEFAULT_BEAM_MM,
        },

        # Opciones de diámetros por uso
        'diameters': {
            'malla': [6, 8, 10, 12, 16],
            'borde': [8, 10, 12, 16, 18, 20, 22, 25, 28, 32],
            'estribos': [8, 10, 12],
            'longitudinal': [16, 18, 20, 22, 25, 28, 32],
            'vigas': [12, 16, 18, 20, 22, 25],
            'laterales': [0, 6, 8, 10, 12, 16],  # 0 = sin laterales, resto igual a malla
        },

        # Opciones de espaciamientos (mm)
        'spacings': {
            'malla': [100, 125, 150, 175, 200, 250, 300],
            'estribos': [75, 100, 125, 150, 200],
            'columnas': [75, 100, 125, 150, 200, 250],
            'laterales': [100, 125, 150, 175, 200, 250, 300],  # Mismos que malla
        },

        # Opciones generales
        'options': {
            'mesh_counts': [1, 2],
            'edge_bar_counts': [2, 4, 6, 8, 10, 12],
            'column_bars_per_face': [1, 2, 3, 4, 5, 6],
            'beam_bar_counts': [2, 3, 4, 5, 6, 8],
            'stirrup_legs': [2, 3, 4],
            'covers': [20, 25, 30, 40, 50],
        },
    })


