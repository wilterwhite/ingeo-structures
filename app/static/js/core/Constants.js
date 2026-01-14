// app/static/js/core/Constants.js
/**
 * Constantes estructurales cargadas desde el backend.
 *
 * IMPORTANTE: Este módulo carga constantes desde /api/constants al inicio.
 * NO definas constantes ACI localmente - usa siempre StructuralConstants.
 *
 * Uso:
 *   await StructuralConstants.load();
 *   const area = StructuralConstants.getBarArea(16);  // 201.1 mm²
 */

const StructuralConstants = {
    // Estado de carga
    _loaded: false,
    _loading: null,

    // Datos cargados del backend
    bar_areas: {},
    available_diameters: [],
    lambda_factors: {},
    dcr_thresholds: {},
    reinforcement: {},
    covers: {},
    diameters: {},
    spacings: {},
    options: {},

    /**
     * Carga las constantes desde el backend.
     * Se puede llamar múltiples veces - solo carga una vez.
     * @returns {Promise<void>}
     */
    async load() {
        if (this._loaded) return;

        // Evitar cargas paralelas
        if (this._loading) return this._loading;

        this._loading = this._fetchConstants();
        await this._loading;
        this._loading = null;
    },

    async _fetchConstants() {
        try {
            const response = await fetch('/api/constants');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            // Copiar datos
            this.bar_areas = data.bar_areas || {};
            this.available_diameters = data.available_diameters || [];
            this.lambda_factors = data.lambda_factors || {};
            this.dcr_thresholds = data.dcr_thresholds || {};
            this.reinforcement = data.reinforcement || {};
            this.covers = data.covers || {};
            this.diameters = data.diameters || {};
            this.spacings = data.spacings || {};
            this.options = data.options || {};

            this._loaded = true;
        } catch (error) {
            console.error('[Constants] Error cargando constantes:', error);
            // Usar fallbacks si falla la carga
            this._useFallbacks();
        }
    },

    /**
     * Fallbacks si el backend no responde.
     * Solo para desarrollo - en producción el backend debe estar disponible.
     */
    _useFallbacks() {
        console.warn('[Constants] Usando fallbacks locales');
        this.bar_areas = {
            '6': 28.3, '8': 50.3, '10': 78.5, '12': 113.1,
            '16': 201.1, '18': 254.5, '20': 314.2, '22': 380.1,
            '25': 490.9, '28': 615.8, '32': 804.2, '36': 1017.9
        };
        this.available_diameters = [6, 8, 10, 12, 16, 18, 20, 22, 25, 28, 32, 36];
        this.lambda_factors = { normal: 1.0, sand_lightweight: 0.85, all_lightweight: 0.75 };
        this.dcr_thresholds = { ok: 0.67, warn: 1.0 };
        this.diameters = {
            malla: [6, 8, 10, 12, 16],
            borde: [8, 10, 12, 16, 18, 20, 22, 25, 28, 32],
            estribos: [8, 10, 12],
            longitudinal: [16, 18, 20, 22, 25, 28, 32],
            vigas: [12, 16, 18, 20, 22, 25]
        };
        this.spacings = {
            malla: [100, 125, 150, 175, 200, 250, 300],
            estribos: [75, 100, 125, 150, 200],
            columnas: [75, 100, 125, 150, 200, 250]
        };
        this.options = {
            mesh_counts: [1, 2],
            edge_bar_counts: [2, 4, 6, 8, 10, 12],
            column_bars_per_face: [1, 2, 3, 4, 5, 6],
            beam_bar_counts: [2, 3, 4, 5, 6, 8],
            stirrup_legs: [2, 3, 4],
            covers: [20, 25, 30, 40, 50]
        };
        this.reinforcement = {
            rho_min: 0.0025,
            max_spacing_mm: 457,
            fy_default_mpa: 420
        };
        this.covers = {
            pier: 40,
            column: 40,
            beam: 40
        };
        this._loaded = true;
    },

    // =========================================================================
    // Métodos de acceso
    // =========================================================================

    /**
     * Obtiene el área de una barra dado su diámetro.
     * @param {number} diameter - Diámetro en mm
     * @returns {number} Área en mm²
     */
    getBarArea(diameter) {
        const area = this.bar_areas[String(diameter)];
        if (!area) {
            console.warn(`[Constants] Área no encontrada para φ${diameter}`);
            return Math.PI * (diameter / 2) ** 2;  // Fórmula geométrica como fallback
        }
        return area;
    },

    /**
     * Obtiene el factor lambda para un tipo de concreto.
     * @param {string} type - 'normal', 'sand_lightweight', 'all_lightweight'
     * @returns {number} Factor lambda
     */
    getLambda(type) {
        return this.lambda_factors[type] || 1.0;
    },

    /**
     * Obtiene la clase CSS para un valor DCR.
     * @param {number} dcr - Demand/Capacity ratio
     * @returns {string} 'fs-ok', 'fs-warn', o 'fs-fail'
     */
    getDcrClass(dcr) {
        if (dcr === '<0.01' || dcr < 0.01) return 'fs-ok';
        const val = parseFloat(dcr);
        if (isNaN(val)) return 'fs-fail';
        if (val <= this.dcr_thresholds.ok) return 'fs-ok';
        if (val <= this.dcr_thresholds.warn) return 'fs-warn';
        return 'fs-fail';
    },

    // =========================================================================
    // Helpers para generar options HTML
    // =========================================================================

    /**
     * Genera opciones HTML para un select de diámetros.
     * @param {string} type - Tipo de diámetros ('malla', 'borde', etc.)
     * @param {number} selected - Diámetro seleccionado
     * @param {string} prefix - Prefijo para mostrar (default: 'φ')
     * @returns {string} HTML de options
     */
    generateDiameterOptions(type, selected, prefix = 'φ') {
        const diameters = this.diameters[type] || this.available_diameters;
        return diameters.map(d =>
            `<option value="${d}" ${d === selected ? 'selected' : ''}>${prefix}${d}</option>`
        ).join('');
    },

    /**
     * Genera opciones HTML para un select de espaciamientos.
     * @param {string} type - Tipo de espaciamientos ('malla', 'estribos', etc.)
     * @param {number} selected - Espaciamiento seleccionado
     * @returns {string} HTML de options
     */
    generateSpacingOptions(type, selected) {
        const spacings = this.spacings[type] || this.spacings.malla;
        return spacings.map(s =>
            `<option value="${s}" ${s === selected ? 'selected' : ''}>@${s}</option>`
        ).join('');
    },

    /**
     * Genera opciones HTML para un select genérico.
     * @param {string} optionType - Tipo de opciones ('mesh_counts', 'edge_bar_counts', etc.)
     * @param {number} selected - Valor seleccionado
     * @param {string} suffix - Sufijo para mostrar
     * @returns {string} HTML de options
     */
    generateOptions(optionType, selected, suffix = '') {
        const values = this.options[optionType] || [];
        return values.map(v =>
            `<option value="${v}" ${v === selected ? 'selected' : ''}>${v}${suffix}</option>`
        ).join('');
    }
};

// Legacy aliases eliminados - usar StructuralConstants directamente
