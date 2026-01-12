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
     * Procesa un stream SSE de forma robusta.
     * @param {Response} response - Response del fetch
     * @param {Object} handlers - {onProgress, onComplete, onError}
     */
    _processSSEStream(response, { onProgress, onComplete, onError }) {
        if (!response.ok) {
            onError(new Error(`HTTP ${response.status}`));
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        const read = async () => {
            try {
                while (true) {
                    const { done, value } = await reader.read();

                    if (value) {
                        buffer += decoder.decode(value, { stream: !done });
                    }

                    // Procesar líneas completas
                    const lines = buffer.split('\n');
                    buffer = done ? '' : lines.pop();

                    for (const line of lines) {
                        if (!line.startsWith('data: ')) continue;

                        try {
                            const event = JSON.parse(line.slice(6));

                            if (event.type === 'progress') {
                                onProgress?.(event);
                            } else if (event.type === 'complete') {
                                reader.cancel();
                                onComplete(event.result);
                                return;
                            } else if (event.type === 'error') {
                                reader.cancel();
                                onError(new Error(event.message));
                                return;
                            }
                        } catch (e) {
                            console.error('SSE parse error:', e);
                        }
                    }

                    if (done) {
                        onError(new Error('Stream cerrado sin evento complete'));
                        return;
                    }
                }
            } catch (err) {
                onError(err);
            }
        };

        read();
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
     * Sube un archivo Excel con progreso en tiempo real (SSE).
     * @param {File} file - Archivo Excel
     * @param {Function} onProgress - Callback para progreso (current, total, element)
     * @returns {Promise<Object>} Resultado del upload
     */
    async uploadWithProgress(file, onProgress) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseUrl}/upload-stream`, {
            method: 'POST',
            body: formData
        });

        return new Promise((resolve, reject) => {
            this._processSSEStream(response, {
                onProgress: (e) => onProgress?.(e.current, e.total, e.element),
                onComplete: resolve,
                onError: reject
            });
        });
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

    /**
     * Análisis con progreso en tiempo real (SSE).
     * @param {Object} params - Parámetros del análisis
     * @param {Function} onProgress - Callback para progreso (current, total, pier)
     * @returns {Promise<Object>} Resultado del análisis
     */
    async analyzeWithProgress(params, onProgress) {
        const response = await fetch(`${this.baseUrl}/analyze-stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        return new Promise((resolve, reject) => {
            this._processSSEStream(response, {
                onProgress: (e) => onProgress?.(e.current, e.total, e.pier),
                onComplete: resolve,
                onError: reject
            });
        });
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
     * Obtiene capacidades de cualquier tipo de elemento estructural.
     * Endpoint unificado para pier, column, beam y drop_beam.
     * @param {string} sessionId - ID de sesión
     * @param {string} elementKey - Clave del elemento (Story_Label)
     * @param {string} elementType - 'pier', 'column', 'beam', 'drop_beam'
     * @returns {Promise<Object>} Información completa del elemento
     */
    async getElementCapacities(sessionId, elementKey, elementType = 'pier') {
        return this.request('/element-capacities', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                element_key: elementKey,
                element_type: elementType
            })
        });
    }

    /**
     * Obtiene los detalles de diseño para una combinación específica.
     * @param {string} sessionId - ID de sesión
     * @param {string} pierKey - Clave del pier (Story_Label)
     * @param {number} comboIndex - Índice de la combinación
     * @returns {Promise<Object>} Datos de flexión, corte y boundary para la combinación
     */
    async getCombinationDetails(sessionId, pierKey, comboIndex) {
        return this.request('/combination-details', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                pier_key: pierKey,
                combo_index: comboIndex
            })
        });
    }

    /**
     * Obtiene el diagrama de sección transversal de un pier.
     * @param {string} sessionId - ID de sesión
     * @param {string} pierKey - Clave del pier (Story_Label)
     * @param {Object} [proposedConfig] - Configuración propuesta opcional
     * @returns {Promise<Object>} Diagrama en base64
     */
    async getSectionDiagram(sessionId, pierKey, proposedConfig = null) {
        const body = {
            session_id: sessionId,
            pier_key: pierKey
        };
        if (proposedConfig) {
            body.proposed_config = proposedConfig;
        }
        return this.request('/section-diagram', {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }

    // =========================================================================
    // Informes PDF
    // =========================================================================

    /**
     * Genera un informe PDF.
     * @param {Object} config - Configuración del informe
     * @param {string} config.session_id - ID de sesión
     * @param {string} config.project_name - Nombre del proyecto
     * @param {number} config.top_by_load - Top piers por carga
     * @param {number} config.top_by_cuantia - Top piers por cuantía
     * @param {boolean} config.include_failing - Incluir piers que fallan
     * @param {boolean} config.include_proposals - Incluir propuestas
     * @param {boolean} config.include_pm_diagrams - Incluir diagramas P-M
     * @param {boolean} config.include_sections - Incluir secciones
     * @param {boolean} config.include_full_table - Incluir tabla completa
     * @returns {Promise<Blob>} PDF como blob
     */
    async generateReport(config) {
        const response = await fetch(`${this.baseUrl}/generate-report`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        return response.blob();
    }

    // =========================================================================
    // Vigas de Acople
    // =========================================================================

    /**
     * Configura la viga estándar para la sesión.
     * @param {string} sessionId - ID de sesión
     * @param {Object} beam - Configuración de viga {width, height, ln, nbars, diam}
     * @returns {Promise<Object>}
     */
    async setDefaultBeam(sessionId, beam) {
        return this.request('/set-default-beam', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                width: beam.width,
                height: beam.height,
                ln: beam.ln || 1500,
                n_bars_top: beam.nbars,
                diameter_top: beam.diam,
                n_bars_bottom: beam.nbars,
                diameter_bottom: beam.diam
            })
        });
    }

    /**
     * Asigna vigas del catálogo a un pier.
     * @param {string} sessionId - ID de sesión
     * @param {string} pierKey - Clave del pier (Story_Label)
     * @param {string} beamLeft - Key de viga izq ('generic', 'none', o beamKey)
     * @param {string} beamRight - Key de viga der ('generic', 'none', o beamKey)
     * @returns {Promise<Object>}
     */
    async assignCouplingBeam(sessionId, pierKey, beamLeft, beamRight) {
        return this.request('/assign-coupling-beam', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                pier_key: pierKey,
                beam_left: beamLeft,
                beam_right: beamRight
            })
        });
    }

    // =========================================================================
    // Vigas - Creación y Edición
    // =========================================================================

    /**
     * Crea una viga custom.
     * @param {string} sessionId - ID de sesión
     * @param {Object} beamData - Datos de la viga
     * @returns {Promise<Object>}
     */
    async createCustomBeam(sessionId, beamData) {
        return this.request('/create-custom-beam', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                ...beamData
            })
        });
    }

    /**
     * Actualiza la enfierradura de una viga.
     * @param {string} sessionId - ID de sesión
     * @param {string} beamKey - Clave de la viga (Story_Label)
     * @param {Object} reinforcement - Datos de enfierradura
     * @returns {Promise<Object>}
     */
    async updateBeamReinforcement(sessionId, beamKey, reinforcement) {
        return this.request('/update-beam-reinforcement', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                beam_key: beamKey,
                reinforcement
            })
        });
    }

    // =========================================================================
    // Losas
    // =========================================================================

    /**
     * Analiza todas las losas de la sesion.
     * @param {string} sessionId - ID de sesion
     * @returns {Promise<Object>} Resultados del analisis de losas
     */
    async analyzeSlabs(sessionId) {
        return this.request('/analyze-slabs', {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId })
        });
    }

    /**
     * Obtiene las capacidades de una losa especifica.
     * @param {string} sessionId - ID de sesion
     * @param {string} slabKey - Clave de la losa
     * @returns {Promise<Object>} Capacidades de la losa
     */
    async getSlabCapacities(sessionId, slabKey) {
        return this.request('/slab-capacities', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                slab_key: slabKey
            })
        });
    }

    /**
     * Verifica punzonamiento para losas 2-Way.
     * @param {string} sessionId - ID de sesion
     * @returns {Promise<Object>} Resultados de punzonamiento
     */
    async analyzePunching(sessionId) {
        return this.request('/analyze-punching', {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId })
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
