// app/static/js/Utils.js
/**
 * Utilidades compartidas para el módulo estructural.
 * Funciones de formateo, validación y helpers comunes.
 */

// =============================================================================
// Formateo de Factor de Seguridad
// =============================================================================

/**
 * Retorna la clase CSS según el factor de seguridad.
 * @param {string|number} sf - Factor de seguridad
 * @returns {string} Clase CSS ('fs-ok', 'fs-warn', 'fs-fail')
 */
function getFsClass(sf) {
    if (sf === '>100') return 'fs-ok';
    const val = parseFloat(sf);
    if (isNaN(val)) return 'fs-fail';
    if (val >= 1.5) return 'fs-ok';
    if (val >= 1.0) return 'fs-warn';
    return 'fs-fail';
}

/**
 * Retorna la clase CSS según el D/C (Demand/Capacity ratio).
 * D/C <= 1.0 es OK, D/C > 1.0 es falla.
 * @param {string|number} dcr - Demand/Capacity ratio
 * @returns {string} Clase CSS ('fs-ok', 'fs-warn', 'fs-fail')
 */
function getDcrClass(dcr) {
    if (dcr === '<0.01') return 'fs-ok';
    const val = parseFloat(dcr);
    if (isNaN(val)) return 'fs-fail';
    if (val <= 0.67) return 'fs-ok';  // Equivale a SF >= 1.5
    if (val <= 1.0) return 'fs-warn'; // Equivale a SF >= 1.0
    return 'fs-fail';
}

// =============================================================================
// Formateo de Textos
// =============================================================================

/**
 * Trunca el nombre de una combinación para mostrar en tabla.
 * @param {string} name - Nombre de la combinación
 * @param {number} maxLen - Longitud máxima (default: 20)
 * @returns {string} Nombre truncado
 */
function truncateCombo(name, maxLen = 20) {
    if (!name) return '';
    return name.length > maxLen ? name.substring(0, maxLen - 2) + '...' : name;
}

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
// Labels y Traducciones
// =============================================================================

/**
 * Retorna la etiqueta legible para un modo de falla.
 * @param {string} mode - Modo de falla (flexure, shear, etc.)
 * @returns {string} Etiqueta en español
 */
function getFailureModeLabel(mode) {
    const labels = {
        flexure: 'Flexión',
        shear: 'Corte',
        combined: 'Combinado',
        slenderness: 'Esbeltez',
        confinement: 'Confinamiento',
        overdesigned: 'Optimizar'
    };
    return labels[mode] || mode;
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

