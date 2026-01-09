# app/routes/common.py
"""
Utilidades compartidas para rutas de la API.

Proporciona decoradores y funciones comunes para validación,
manejo de errores y acceso a servicios.
"""
import logging
from functools import wraps
from typing import Callable, Any

from flask import request, jsonify

from ..services.structural_analysis import StructuralAnalysisService
from ..services.factory import ServiceFactory

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


def require_session_and_pier(f: Callable) -> Callable:
    """
    Decorador que valida session_id y pier_key en el request JSON.

    Extrae ambos valores, pasándolos como kwargs al endpoint.
    Retorna 400 si falta alguno.

    Uso:
        @bp.route('/endpoint', methods=['POST'])
        @handle_errors
        @require_session_and_pier
        def endpoint(session_id: str, pier_key: str, data: dict):
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Any:
        data = get_json_data()
        session_id = data.get('session_id')
        pier_key = data.get('pier_key')

        if not session_id or not pier_key:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id y pier_key'
            }), 400

        return f(*args, session_id=session_id, pier_key=pier_key, data=data, **kwargs)
    return decorated


def require_session_and_slab(f: Callable) -> Callable:
    """
    Decorador que valida session_id y slab_key en el request JSON.

    Uso:
        @bp.route('/endpoint', methods=['POST'])
        @handle_errors
        @require_session_and_slab
        def endpoint(session_id: str, slab_key: str, data: dict):
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Any:
        data = get_json_data()
        session_id = data.get('session_id')
        slab_key = data.get('slab_key')

        if not session_id or not slab_key:
            return jsonify({
                'success': False,
                'error': 'Se requiere session_id y slab_key'
            }), 400

        return f(*args, session_id=session_id, slab_key=slab_key, data=data, **kwargs)
    return decorated


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
