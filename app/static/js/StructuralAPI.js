// app/structural/static/js/StructuralAPI.js
/**
 * Cliente API para el módulo de análisis estructural.
 * Sigue el patrón BaseAPI de la aplicación principal.
 */
class StructuralAPI {
    constructor() {
        this.baseUrl = '/structural';
    }

    /**
     * Realiza una petición HTTP.
     * @param {string} endpoint - Endpoint relativo
     * @param {Object} options - Opciones de fetch
     * @returns {Promise<Object>} Respuesta JSON
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        return response.json();
    }

    // =========================================================================
    // Sesiones y Upload
    // =========================================================================

    /**
     * Sube un archivo Excel de ETABS.
     * @param {File} file - Archivo Excel
     * @returns {Promise<Object>} Respuesta con session_id y summary
     */
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseUrl}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        return response.json();
    }

    /**
     * Limpia una sesión.
     * @param {string} sessionId - ID de sesión
     * @returns {Promise<Object>}
     */
    async clearSession(sessionId) {
        return this.request(`/clear-session/${sessionId}`, {
            method: 'DELETE'
        });
    }

    // =========================================================================
    // Análisis
    // =========================================================================

    /**
     * Ejecuta el análisis estructural completo.
     * @param {Object} params - Parámetros del análisis
     * @returns {Promise<Object>} Resultados del análisis
     */
    async analyze(params) {
        return this.request('/analyze', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    /**
     * Análisis directo (upload + analyze en un paso).
     * @param {File} file - Archivo Excel
     * @param {boolean} generatePlots - Generar gráficos
     * @returns {Promise<Object>}
     */
    async analyzeDirect(file, generatePlots = true) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('generate_plots', generatePlots);

        const response = await fetch(`${this.baseUrl}/analyze-direct`, {
            method: 'POST',
            body: formData
        });

        return response.json();
    }

    // =========================================================================
    // Combinaciones de Carga
    // =========================================================================

    /**
     * Obtiene las combinaciones de carga de un pier.
     * @param {string} sessionId - ID de sesión
     * @param {string} pierKey - Clave del pier (Story_Label)
     * @returns {Promise<Object>} Combinaciones con ángulos
     */
    async getPierCombinations(sessionId, pierKey) {
        return this.request(
            `/pier-combinations/${sessionId}/${encodeURIComponent(pierKey)}`
        );
    }

    /**
     * Analiza una combinación específica de un pier.
     * @param {Object} params - Parámetros
     * @returns {Promise<Object>} Resultado con diagrama P-M
     */
    async analyzeCombination(params) {
        return this.request('/analyze-combination', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    /**
     * Obtiene el gráfico resumen filtrado.
     * @param {Object} params - Parámetros de filtro
     * @param {string} params.session_id - ID de sesión
     * @param {string[]} [params.pier_keys] - Lista de pier keys a incluir
     * @param {string} [params.story_filter] - Filtro por piso
     * @param {string} [params.axis_filter] - Filtro por eje
     * @returns {Promise<Object>} Gráfico en base64
     */
    async getSummaryPlot(params) {
        return this.request('/summary-plot', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    /**
     * Obtiene las capacidades puras de un pier.
     * @param {string} sessionId - ID de sesión
     * @param {string} pierKey - Clave del pier (Story_Label)
     * @returns {Promise<Object>} Información y capacidades del pier
     */
    async getPierCapacities(sessionId, pierKey) {
        return this.request('/pier-capacities', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                pier_key: pierKey
            })
        });
    }

    /**
     * Obtiene el diagrama de sección transversal de un pier.
     * @param {string} sessionId - ID de sesión
     * @param {string} pierKey - Clave del pier (Story_Label)
     * @returns {Promise<Object>} Diagrama en base64
     */
    async getSectionDiagram(sessionId, pierKey) {
        return this.request('/section-diagram', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                pier_key: pierKey
            })
        });
    }

    // =========================================================================
    // Health Check
    // =========================================================================

    /**
     * Verifica el estado del módulo.
     * @returns {Promise<Object>}
     */
    async healthCheck() {
        return this.request('/health');
    }
}

// Instancia singleton
const structuralAPI = new StructuralAPI();
