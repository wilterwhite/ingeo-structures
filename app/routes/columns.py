# app/routes/columns.py
"""
Endpoints API para análisis de columnas sísmicas.

Incluye:
- Análisis de columnas según ACI 318-25 §18.7 (SPECIAL)
- Verificación dimensional, longitudinal, transversal y cortante
- Verificación columna fuerte-viga débil
"""
import logging

from flask import Blueprint, jsonify

from ..domain.chapter18.columns.service import SeismicColumnService
from ..domain.chapter18.common import SeismicCategory
from .common import (
    get_analysis_service,
    handle_errors,
    require_session,
    get_session_or_404,
)

# Blueprint para endpoints de columnas
bp = Blueprint('columns', __name__, url_prefix='/structural')
logger = logging.getLogger(__name__)

# Servicio de verificación de columnas
_column_service = SeismicColumnService()


# =============================================================================
# Análisis de Columnas
# =============================================================================

@bp.route('/analyze-columns', methods=['POST'])
@handle_errors
@require_session
def analyze_columns(session_id: str, data: dict):
    """
    Analiza columnas de la sesión actual.

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
    """
    parsed_data, error = get_session_or_404(session_id)
    if error:
        return error

    if not parsed_data.has_columns:
        return jsonify({
            'success': False,
            'error': 'No hay columnas en esta sesión. Asegúrese de cargar un archivo con columnas.'
        }), 400

    # Parsear categoría sísmica
    category_str = data.get('category', 'SPECIAL').upper()
    try:
        category = SeismicCategory[category_str]
    except KeyError:
        category = SeismicCategory.SPECIAL

    lambda_factor = float(data.get('lambda_factor', 1.0))

    results = []
    ok_count = 0
    fail_count = 0

    for column_key, column in parsed_data.columns.items():
        column_forces = parsed_data.column_forces.get(column_key)

        # Obtener fuerzas críticas
        Vu_V2 = 0
        Vu_V3 = 0
        Pu = 0

        if column_forces:
            # Usar la combinación más crítica
            critical = column_forces.get_critical_combination()
            if critical:
                Vu_V2 = abs(critical.V2)
                Vu_V3 = abs(critical.V3)
                Pu = critical.P

        # Verificar columna
        result = _column_service.verify_column(
            b=min(column.depth, column.width),
            h=max(column.depth, column.width),
            lu=column.lu_calculated,
            cover=column.cover,
            Ag=column.Ag,
            fc=column.fc,
            fy=column.fy,
            fyt=column.fy,  # Asume mismo fy para transversal
            Ast=column.As_longitudinal,
            n_bars=column.n_total_bars,
            db_long=column.diameter_long,
            s_transverse=column.stirrup_spacing,
            Ash=column.Ash_depth,
            hx=column.hx,
            Vu_V2=Vu_V2,
            Vu_V3=Vu_V3,
            Pu=Pu,
            category=category,
            lambda_factor=lambda_factor,
        )

        # Formatear resultado
        result_dict = {
            'column_key': column_key,
            'label': column.label,
            'story': column.story,
            'section': f'{column.depth}x{column.width}',
            'reinforcement': column.reinforcement_description,
            'is_ok': result.is_ok,
            'dcr_max': result.dcr_max,
            'critical_check': result.critical_check,
            'warnings': result.warnings,
            'category': category.value,
        }

        # Agregar detalles de verificaciones
        if result.dimensional_limits:
            result_dict['dimensional'] = {
                'is_ok': result.dimensional_limits.is_ok,
                'b': result.dimensional_limits.b,
                'h': result.dimensional_limits.h,
            }

        if result.longitudinal:
            result_dict['longitudinal'] = {
                'is_ok': result.longitudinal.is_ok,
                'rho': result.longitudinal.rho,
                'rho_min': result.longitudinal.rho_min,
                'rho_max': result.longitudinal.rho_max,
            }

        if result.transverse:
            result_dict['transverse'] = {
                'is_ok': result.transverse.is_ok,
                's_provided': result.transverse.s_provided,
                's_max': result.transverse.s_max,
            }

        if result.shear:
            result_dict['shear'] = {
                'is_ok': result.shear.is_ok,
                'dcr': result.shear.dcr,
                'phi_Vn_V2': result.shear.phi_Vn_V2,
                'phi_Vn_V3': result.shear.phi_Vn_V3,
            }

        results.append(result_dict)

        if result.is_ok:
            ok_count += 1
        else:
            fail_count += 1

    total = len(results)
    statistics = {
        'total_columns': total,
        'ok_count': ok_count,
        'fail_count': fail_count,
        'pass_rate': round(ok_count / total * 100, 1) if total > 0 else 0
    }

    return jsonify({
        'success': True,
        'results': results,
        'statistics': statistics
    })


@bp.route('/column-capacities', methods=['POST'])
@handle_errors
@require_session
def get_column_capacities(session_id: str, data: dict):
    """
    Obtiene las capacidades de una columna específica.

    Request (JSON):
        {
            "session_id": "uuid-xxx",
            "column_key": "Story4_C2"
        }
    """
    column_key = data.get('column_key')
    if not column_key:
        return jsonify({
            'success': False,
            'error': 'Se requiere column_key'
        }), 400

    parsed_data, error = get_session_or_404(session_id)
    if error:
        return error

    if column_key not in parsed_data.columns:
        return jsonify({
            'success': False,
            'error': f'Columna "{column_key}" no encontrada'
        }), 404

    column = parsed_data.columns[column_key]
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
