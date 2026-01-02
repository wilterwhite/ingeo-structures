// app/static/js/Constants.js
/**
 * Constantes compartidas para el módulo estructural.
 * Centraliza valores de armadura, diámetros, espaciamientos, etc.
 */

// =============================================================================
// Áreas de Barras (mm²)
// =============================================================================

const BAR_AREAS = {
    6: 28.3,
    8: 50.3,
    10: 78.5,
    12: 113.1,
    16: 201.1,
    18: 254.5,
    20: 314.2,
    22: 380.1,
    25: 490.9,
    28: 615.8,
    32: 804.2,
    36: 1017.9
};

// =============================================================================
// Opciones de Diámetros (mm)
// =============================================================================

const DIAMETERS = {
    // Malla de muro (vertical/horizontal)
    malla: [6, 8, 10, 12, 16],

    // Barras de borde
    borde: [12, 16, 18, 20, 22, 25, 28, 32],

    // Estribos
    estribos: [8, 10, 12],

    // Barras longitudinales de columnas
    longitudinal: [16, 18, 20, 22, 25, 28, 32],

    // Barras de vigas de acople
    vigas: [12, 16, 18, 20, 22, 25],

    // Para PiersTable (configuración general)
    general: [6, 8, 10, 12, 16, 20, 22, 25],
    generalBorde: [10, 12, 16, 20, 22, 25]
};

// =============================================================================
// Opciones de Espaciamientos (mm)
// =============================================================================

const SPACINGS = {
    // Malla de muro
    malla: [100, 125, 150, 175, 200, 250, 300],

    // Estribos de borde
    estribos: [75, 100, 125, 150, 200],

    // Estribos de columnas
    columnas: [75, 100, 125, 150, 200, 250],

    // Para PiersTable (configuración general)
    general: [100, 150, 200, 250, 300]
};

// =============================================================================
// Opciones de Recubrimiento (mm)
// =============================================================================

const COVERS = [20, 25, 30, 40, 50];

// =============================================================================
// Opciones de Vigas de Acople
// =============================================================================

const BEAM_OPTIONS = {
    widths: [150, 200, 250, 300],
    heights: [400, 500, 600, 700, 800],
    lengths: [1000, 1200, 1500, 1800, 2000, 2500],
    nBars: [2, 3, 4, 5, 6]
};

// =============================================================================
// Opciones Generales
// =============================================================================

const MESH_OPTIONS = [1, 2];
const EDGE_BAR_COUNTS = [2, 4, 6, 8, 10, 12];
const COLUMN_BARS_PER_FACE = [2, 3, 4, 5, 6];

// =============================================================================
// Helpers para generar options HTML
// =============================================================================

/**
 * Genera opciones HTML para un select de diámetros.
 * @param {number[]} diameters - Lista de diámetros disponibles
 * @param {number} selected - Diámetro seleccionado
 * @param {string} prefix - Prefijo para mostrar (ej: 'φ', 'E')
 * @returns {string} HTML de options
 */
function generateDiameterOptions(diameters, selected, prefix = 'φ') {
    return diameters.map(d =>
        `<option value="${d}" ${d === selected ? 'selected' : ''}>${prefix}${d}</option>`
    ).join('');
}

/**
 * Genera opciones HTML para un select de espaciamientos.
 * @param {number[]} spacings - Lista de espaciamientos disponibles
 * @param {number} selected - Espaciamiento seleccionado
 * @returns {string} HTML de options
 */
function generateSpacingOptions(spacings, selected) {
    return spacings.map(s =>
        `<option value="${s}" ${s === selected ? 'selected' : ''}>@${s}</option>`
    ).join('');
}

/**
 * Genera opciones HTML para un select genérico.
 * @param {number[]} values - Lista de valores
 * @param {number} selected - Valor seleccionado
 * @param {string} suffix - Sufijo para mostrar
 * @returns {string} HTML de options
 */
function generateOptions(values, selected, suffix = '') {
    return values.map(v =>
        `<option value="${v}" ${v === selected ? 'selected' : ''}>${v}${suffix}</option>`
    ).join('');
}
