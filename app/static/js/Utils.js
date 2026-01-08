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
// Cálculos de Armadura
// =============================================================================

/**
 * Calcula el área de acero por metro lineal.
 * @param {number} nMeshes - Número de mallas (1 o 2)
 * @param {number} diameter - Diámetro de barra (mm)
 * @param {number} spacing - Espaciamiento (mm)
 * @returns {number} Área de acero (mm²/m)
 */
function calculateAsPerMeter(nMeshes, diameter, spacing) {
    const barArea = BAR_AREAS[diameter] || 50.3;
    return nMeshes * (barArea / spacing) * 1000;
}

