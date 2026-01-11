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

from ..services.analysis.element_orchestrator import ElementOrchestrator
from ..services.presentation.result_formatter import ResultFormatter
from .common import (
    handle_errors,
    require_session_data,
    require_element,
    parse_seismic_params,
    analyze_elements_generic,
)

# Blueprint para endpoints de columnas
bp = Blueprint('columns', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)

# Orquestador unificado de elementos
_orchestrator = ElementOrchestrator()


# =============================================================================
# Análisis de Columnas
# =============================================================================

@bp.route('/analyze-columns', methods=['POST'])
@handle_errors
@require_session_data
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
    if not parsed_data.has_columns:
        return jsonify({
            'success': False,
            'error': 'No hay columnas en esta sesión. Asegúrese de cargar un archivo con columnas.'
        }), 400

    # Parsear parámetros sísmicos
    category, lambda_factor = parse_seismic_params(data)

    # Analizar columnas usando función genérica
    results, statistics = analyze_elements_generic(
        elements=parsed_data.columns or {},
        forces_dict=parsed_data.column_forces or {},
        orchestrator=_orchestrator,
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

    # Información de la columna
    column_info = {
        'label': column.label,
        'story': column.story,
        'depth_mm': column.depth,
        'width_mm': column.width,
        'height_mm': column.height,
        'fc_MPa': column.fc,
        'fy_MPa': column.fy,
        'cover_mm': column.cover,
        'Ag_mm2': column.Ag,
        'section_name': column.section_name,
    }

    # Información de refuerzo
    reinforcement = {
        'n_total_bars': column.n_total_bars,
        'n_bars_depth': column.n_bars_depth,
        'n_bars_width': column.n_bars_width,
        'diameter_long': column.diameter_long,
        'As_longitudinal_mm2': round(column.As_longitudinal, 1),
        'rho_longitudinal': round(column.rho_longitudinal, 4),
        'stirrup_diameter': column.stirrup_diameter,
        'stirrup_spacing': column.stirrup_spacing,
        'n_stirrup_legs_depth': column.n_stirrup_legs_depth,
        'n_stirrup_legs_width': column.n_stirrup_legs_width,
    }

    # Fuerzas si están disponibles
    forces = None
    if column_forces:
        critical = column_forces.get_critical_combination()
        if critical:
            forces = {
                'combo_name': critical.combo_name,
                'P_tonf': round(critical.P, 2),
                'V2_tonf': round(critical.V2, 2),
                'V3_tonf': round(critical.V3, 2),
                'M2_tonf_m': round(critical.M2, 2),
                'M3_tonf_m': round(critical.M3, 2),
            }

    return jsonify({
        'success': True,
        'column': column_info,
        'reinforcement': reinforcement,
        'forces': forces
    })
