# app/routes/common.py
"""
Utilidades compartidas para rutas de la API.

Proporciona decoradores y funciones comunes para validación,
manejo de errores y acceso a servicios.
"""
import logging
from functools import wraps
from typing import Callable, Any, Tuple

from flask import request, jsonify

from ..services.structural_analysis import StructuralAnalysisService
from ..services.factory import ServiceFactory
from ..domain.chapter18.common import SeismicCategory

logger = logging.getLogger(__name__)

# Instancia global del servicio
_analysis_service = None


def get_analysis_service() -> StructuralAnalysisService:
    """
    Obtiene o crea la instancia del servicio de análisis.

    Nota: Este patrón singleton simple es suficiente para Flask
    en modo desarrollo. Para producción con workers múltiples,
    considerar usar Flask-Caching o similar.
    """
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = ServiceFactory.create_default_analysis_service()
    return _analysis_service


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
            logger.exception(f"Error en {f.__name__}: {str(e)}")
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


def require_session_and_slab(f: Callable) -> Callable:
    """Alias de require_session_and_element('slab_key')."""
    return require_session_and_element('slab_key')(f)


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


def calculate_statistics(results: list) -> dict:
    """
    Calcula estadísticas OK/FAIL de una lista de resultados.

    Args:
        results: Lista de resultados con campo 'overall_status'

    Returns:
        Dict con total, ok_count, fail_count, pass_rate
    """
    total = len(results)
    ok_count = sum(1 for r in results if r.get('overall_status') == 'OK')
    return {
        'total': total,
        'ok_count': ok_count,
        'fail_count': total - ok_count,
        'pass_rate': round(ok_count / total * 100, 1) if total > 0 else 0,
    }


def analyze_elements_generic(
    elements: dict,
    forces_dict: dict,
    orchestrator,
    result_formatter,
    category: SeismicCategory,
    lambda_factor: float,
) -> Tuple[list, dict]:
    """
    Análisis genérico para cualquier tipo de elemento estructural.

    Este método centraliza la lógica común de análisis de beams, columns,
    y otros elementos que usan ElementOrchestrator.

    Args:
        elements: Diccionario {element_key: element}
        forces_dict: Diccionario {element_key: forces}
        orchestrator: Instancia de ElementOrchestrator
        result_formatter: Clase ResultFormatter para formateo
        category: Categoría sísmica
        lambda_factor: Factor para concreto liviano

    Returns:
        Tuple (results_list, statistics_dict)
    """
    results = []

    for key, element in elements.items():
        forces = forces_dict.get(key)

        # Verificar usando orquestador (clasifica y delega automáticamente)
        orchestration_result = orchestrator.verify(
            element=element,
            forces=forces,
            lambda_factor=lambda_factor,
            category=category,
        )

        # Formatear resultado para UI
        formatted = result_formatter.format_any_element(
            element, orchestration_result, key
        )
        results.append(formatted)

    statistics = calculate_statistics(results)
    return results, statistics
