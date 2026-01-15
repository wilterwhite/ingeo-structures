// app/static/js/storage/ProjectStorage.js
/**
 * Capa de persistencia local para proyectos.
 *
 * Responsabilidad unica: manejo de localStorage.
 * No tiene conocimiento de UI ni de API.
 */

class ProjectStorage {
    constructor() {
        this.KEYS = {
            SESSION_ID: 'ingeo_session_id',
            PROJECT_ID: 'ingeo_project_id',
            RECENT_PROJECTS: 'ingeo_recent_projects',
        };
    }

    // =========================================================================
    // Session ID
    // =========================================================================

    saveSessionId(sessionId) {
        if (sessionId) {
            localStorage.setItem(this.KEYS.SESSION_ID, sessionId);
        }
    }

    getSessionId() {
        return localStorage.getItem(this.KEYS.SESSION_ID);
    }

    // =========================================================================
    // Project ID
    // =========================================================================

    saveProjectId(projectId) {
        if (projectId) {
            localStorage.setItem(this.KEYS.PROJECT_ID, projectId);
        }
    }

    getProjectId() {
        return localStorage.getItem(this.KEYS.PROJECT_ID);
    }

    // =========================================================================
    // Clear
    // =========================================================================

    clearSession() {
        localStorage.removeItem(this.KEYS.SESSION_ID);
        localStorage.removeItem(this.KEYS.PROJECT_ID);
    }

    // =========================================================================
    // Recent Projects
    // =========================================================================

    getRecentProjects() {
        const stored = localStorage.getItem(this.KEYS.RECENT_PROJECTS);
        return stored ? JSON.parse(stored) : [];
    }

    addRecentProject(project, maxCount = 10) {
        let recent = this.getRecentProjects();

        // Remover si ya existe
        recent = recent.filter(p => p.id !== project.id);

        // Agregar al inicio
        recent.unshift({
            id: project.id,
            name: project.name,
            date: new Date().toISOString()
        });

        // Limitar cantidad
        recent = recent.slice(0, maxCount);

        localStorage.setItem(this.KEYS.RECENT_PROJECTS, JSON.stringify(recent));
    }
}
