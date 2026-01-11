# app/routes/columns.py
"""
Endpoints API para análisis de columnas sísmicas.

Incluye:
- Análisis de columnas según ACI 318-25 §18.7 (SPECIAL)
- Verificación dimensional, longitudinal, transversal y cortante
- Verificación columna fuerte-viga débil

Usa ElementOrchestrator para clasificar y verificar columnas de forma unificada.
"""
import logging

from flask import Blueprint, jsonify

from ..services.presentation.result_formatter import ResultFormatter
from .common import (
    get_orchestrator,
    handle_errors,
    require_session_data,
    require_element,
    require_element_type,
    parse_seismic_params,
    analyze_elements_generic,
)

# Blueprint para endpoints de columnas
bp = Blueprint('columns', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)


# =============================================================================
# Análisis de Columnas
# =============================================================================

@bp.route('/analyze-columns', methods=['POST'])
@handle_errors
@require_session_data
@require_element_type('columns')
def analyze_columns(session_id: str, data: dict, parsed_data):
    """
    Analiza columnas de la sesión actual usando flujo unificado.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "column_updates": [...],  // Opcional
            "category": "SPECIAL",    // SPECIAL, INTERMEDIATE, ORDINARY
            "lambda_factor": 1.0      // Factor concreto liviano
        }

    Response:
        {
            "success": true,
            "results": [...],
            "statistics": {...}
        }

    Nota: Usa ElementOrchestrator que clasifica automáticamente cada columna
    y la verifica con el servicio apropiado según ACI 318-25.
    """
    # Parsear parámetros sísmicos
    category, lambda_factor = parse_seismic_params(data)

    # Analizar columnas usando función genérica
    results, statistics = analyze_elements_generic(
        elements=parsed_data.columns or {},
        forces_dict=parsed_data.column_forces or {},
        orchestrator=get_orchestrator(),
        result_formatter=ResultFormatter,
        category=category,
        lambda_factor=lambda_factor,
    )

    return jsonify({
        'success': True,
        'results': results,
        'statistics': statistics
    })


@bp.route('/column-capacities', methods=['POST'])
@handle_errors
@require_session_data
@require_element('column_key', 'columns', 'Columna')
def get_column_capacities(session_id: str, data: dict, parsed_data, column_key: str, column):
    """
    Obtiene las capacidades de una columna específica.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "column_key": "Story4_C2"
        }
    """
    column_forces = parsed_data.column_forces.get(column_key)

    # Usar formatter para construir respuesta
    formatted = ResultFormatter.format_column_capacities(column, column_forces)

    return jsonify({
        'success': True,
        **formatted
    })
