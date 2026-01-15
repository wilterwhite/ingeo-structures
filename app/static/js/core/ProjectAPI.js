// app/static/js/core/ProjectAPI.js
/**
 * Cliente API para operaciones de proyectos.
 *
 * Responsabilidad unica: comunicacion HTTP con el backend.
 * No tiene conocimiento de UI ni de localStorage.
 */

class ProjectAPI {
    constructor(baseUrl = '/api/projects') {
        this.baseUrl = baseUrl;
    }

    // =========================================================================
    // List
    // =========================================================================

    /**
     * Lista todos los proyectos disponibles.
     * @returns {Promise<Array>} Lista de proyectos
     */
    async list() {
        const response = await fetch(`${this.baseUrl}/list`);
        const data = await response.json();
        return data.success ? data.projects : [];
    }

    // =========================================================================
    // Create
    // =========================================================================

    /**
     * Crea un nuevo proyecto desde un archivo Excel.
     * @param {string} name - Nombre del proyecto
     * @param {string} description - Descripcion opcional
     * @param {File} file - Archivo Excel
     * @returns {Promise<Object>} Resultado de la operacion
     */
    async create(name, description, file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', name);
        formData.append('description', description || '');

        const response = await fetch(`${this.baseUrl}/create`, {
            method: 'POST',
            body: formData
        });

        return response.json();
    }

    // =========================================================================
    // Save
    // =========================================================================

    /**
     * Guarda las modificaciones de una sesion en un proyecto.
     * @param {string} sessionId - ID de la sesion
     * @param {string} projectId - ID del proyecto
     * @param {Object} results - Resultados del análisis (opcional)
     * @returns {Promise<Object>} Resultado de la operacion
     */
    async save(sessionId, projectId, results = null) {
        const response = await fetch(`${this.baseUrl}/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                project_id: projectId,
                results: results
            })
        });

        return response.json();
    }

    // =========================================================================
    // Load
    // =========================================================================

    /**
     * Carga un proyecto existente.
     * @param {string} projectId - ID del proyecto
     * @returns {Promise<Object>} Resultado con session_id, metadata y summary
     */
    async load(projectId) {
        const response = await fetch(`${this.baseUrl}/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_id: projectId })
        });

        return response.json();
    }

    // =========================================================================
    // Delete
    // =========================================================================

    /**
     * Elimina un proyecto.
     * @param {string} projectId - ID del proyecto
     * @returns {Promise<Object>} Resultado de la operacion
     */
    async delete(projectId) {
        const response = await fetch(`${this.baseUrl}/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_id: projectId })
        });

        return response.json();
    }
}
