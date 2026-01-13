// app/static/js/Utils.js
/**
 * Utilidades compartidas para el módulo estructural.
 * Funciones de formateo, validación y helpers comunes.
 *
 * NOTA: Las funciones getDcrClass() y getFsClass() usan umbrales
 * de StructuralConstants (cargados desde /api/constants).
 */

// =============================================================================
// Formateo de Factor de Seguridad
// =============================================================================

/**
 * Retorna la clase CSS según el factor de seguridad.
 * Convierte SF a DCR y usa StructuralConstants para consistencia.
 * @param {string|number} sf - Factor de seguridad (SF = 1/DCR)
 * @returns {string} Clase CSS ('fs-ok', 'fs-warn', 'fs-fail')
 */
function getFsClass(sf) {
    if (sf === '>100') return 'fs-ok';
    const val = parseFloat(sf);
    if (isNaN(val)) return 'fs-fail';

    // Convertir SF a DCR: SF = 1/DCR → DCR = 1/SF
    const dcr = val > 0 ? 1.0 / val : 100;
    return StructuralConstants.getDcrClass(dcr);
}

/**
 * Retorna la clase CSS según el D/C (Demand/Capacity ratio).
 * Delega a StructuralConstants (cargados desde backend).
 *
 * @param {string|number} dcr - Demand/Capacity ratio
 * @returns {string} Clase CSS ('fs-ok', 'fs-warn', 'fs-fail')
 */
function getDcrClass(dcr) {
    return StructuralConstants.getDcrClass(dcr);
}

// =============================================================================
// Formateo de Textos
// =============================================================================

/**
 * Formatea un valor DCR para mostrar.
 * @param {number} dcr - Demand/Capacity Ratio
 * @returns {string} DCR formateado
 */
function formatDcr(dcr) {
    if (dcr === undefined || dcr === null) return '-';
    if (dcr < 0.001) return '≈0';
    return dcr.toFixed(2);
}

// =============================================================================
// Conversiones de Unidades
// =============================================================================

/**
 * Convierte metros a milímetros.
 * @param {number} meters - Valor en metros
 * @returns {number} Valor en milímetros (redondeado)
 */
function metersToMm(meters) {
    return Math.round((meters || 0) * 1000);
}

/**
 * Convierte metros a centímetros.
 * @param {number} meters - Valor en metros
 * @param {number} decimals - Decimales (default: 0)
 * @returns {string} Valor en centímetros formateado
 */
function metersToCm(meters, decimals = 0) {
    return ((meters || 0) * 100).toFixed(decimals);
}

/**
 * Formatea dimensiones de sección (ancho x alto).
 * @param {number} width_m - Ancho en metros
 * @param {number} height_m - Alto en metros
 * @param {string} unit - Unidad ('mm' o 'cm', default: 'mm')
 * @returns {string} "ancho × alto" formateado
 */
function formatSectionDimensions(width_m, height_m, unit = 'mm') {
    if (unit === 'cm') {
        return `${metersToCm(width_m)} × ${metersToCm(height_m)}`;
    }
    return `${metersToMm(width_m)} × ${metersToMm(height_m)}`;
}

// =============================================================================
// Estadísticas de Elementos
// =============================================================================

/**
 * Calcula estadísticas de elementos (total, ok, fail, rate).
 * @param {Array} results - Array de resultados con overall_status
 * @returns {Object} { total, ok, fail, rate }
 */
function calculateElementStats(results) {
    const total = results?.length || 0;
    const ok = results?.filter(r => isStatusOk(r)).length || 0;
    const fail = total - ok;
    const rate = total > 0 ? ((ok / total) * 100).toFixed(0) : 0;
    return { total, ok, fail, rate };
}

// =============================================================================
// Helpers de Estado
// =============================================================================

/**
 * Verifica si un resultado tiene estado OK.
 * @param {Object} result - Resultado con overall_status
 * @returns {boolean}
 */
function isStatusOk(result) {
    return result?.overall_status === 'OK';
}

/**
 * Retorna clase CSS según estado del resultado.
 * Usa status_class del backend si está disponible,
 * de lo contrario calcula localmente.
 * @param {Object} result - Resultado con overall_status y opcionalmente status_class
 * @returns {string} 'status-ok' o 'status-fail'
 */
function getStatusClass(result) {
    // Preferir la clase CSS calculada por el backend
    if (result?.status_class) {
        return result.status_class;
    }
    // Fallback: calcular localmente
    return isStatusOk(result) ? 'status-ok' : 'status-fail';
}

/**
 * Obtiene el texto de DCR formateado, preferiendo el valor del backend.
 * @param {Object} result - Resultado con dcr_display y dcr_max
 * @returns {string} DCR formateado
 */
function getDcrDisplay(result) {
    // Preferir el valor pre-formateado del backend
    if (result?.dcr_display) {
        return result.dcr_display;
    }
    // Fallback: formatear localmente
    return formatDcr(result?.dcr_max);
}

/**
 * Obtiene las dimensiones formateadas, preferiendo el valor del backend.
 * @param {Object} result - Resultado con dimensions_display y geometry
 * @returns {string} Dimensiones formateadas
 */
function getDimensionsDisplay(result) {
    // Preferir el valor pre-formateado del backend
    if (result?.dimensions_display) {
        return result.dimensions_display;
    }
    // Fallback: formatear localmente desde geometry
    // Orden consistente: width (largo) × thickness (espesor)
    const g = result?.geometry;
    if (g) {
        return formatSectionDimensions(g.width_m, g.thickness_m, 'mm');
    }
    return '-';
}

