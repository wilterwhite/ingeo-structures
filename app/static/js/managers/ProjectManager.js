// app/static/js/managers/ProjectManager.js
/**
 * Gestor de proyectos - Coordinador de UI.
 *
 * Responsabilidades:
 * - Coordinar ProjectStorage (localStorage) y ProjectAPI (HTTP)
 * - Manejar UI de modales y estado visual
 * - Auto-guardado
 *
 * Delega a:
 * - ProjectStorage: persistencia en localStorage
 * - ProjectAPI: llamadas HTTP al backend
 */

class ProjectManager {
    constructor(page) {
        this.page = page;
        this.currentProjectId = null;
        this.currentProjectName = null;
        this.hasUnsavedChanges = false;
        this.autoSaveEnabled = true;
        this.autoSaveDelay = 30000; // 30 segundos
        this.autoSaveTimer = null;

        // Dependencias (se inyectan para desacoplar)
        this.storage = new ProjectStorage();
        this.api = new ProjectAPI();

        // Controller para event delegation (evita memory leaks)
        this._projectListController = null;
    }

    // =========================================================================
    // Inicializacion
    // =========================================================================

    init() {
        this._restoreFromStorage();
        this._bindWindowEvents();
    }

    _bindWindowEvents() {
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges && this.currentProjectId) {
                e.preventDefault();
                e.returnValue = 'Tienes cambios sin guardar. ¿Deseas salir?';
            }
        });
    }

    async _restoreFromStorage() {
        const projectId = this.storage.getProjectId();
        if (!projectId) {
            this.storage.clearSession();
            return;
        }

        try {
            const result = await this.loadProject(projectId);
            if (result.success) {
                this.page.showNotification(
                    `Proyecto "${result.metadata.name}" restaurado`,
                    'info'
                );
            }
        } catch (e) {
            console.warn('No se pudo restaurar el proyecto:', e);
            this.storage.clearSession();
        }
    }

    // =========================================================================
    // Operaciones de Proyecto (coordinan storage + API)
    // =========================================================================

    /**
     * Crea un nuevo proyecto.
     */
    async createProject(name, description, file) {
        const data = await this.api.create(name, description, file);

        if (data.success) {
            this.currentProjectId = data.project_id;
            this.currentProjectName = name;
            this.hasUnsavedChanges = false;

            this.storage.saveProjectId(data.project_id);
            this.storage.addRecentProject({ id: data.project_id, name });
            this.updateProjectUI();
        }

        return data;
    }

    /**
     * Guarda el proyecto actual.
     * Si no hay proyecto, abre modal de guardar como.
     */
    async saveProject() {
        if (!this.currentProjectId && this.page.sessionId) {
            this.openSaveAsModal();
            return { success: false, error: 'Abrir modal de guardar' };
        }

        if (!this.currentProjectId || !this.page.sessionId) {
            this.page.showNotification('No hay sesion activa para guardar', 'error');
            return { success: false, error: 'No hay proyecto activo' };
        }

        // Recopilar resultados actuales para persistir
        const results = {
            piers: this.page.results || [],
            columns: this.page.columnResults || [],
            beams: this.page.beamResults || [],
            drop_beams: this.page.dropBeamResults || [],
            seismic_category: this.page.getSeismicCategory ? this.page.getSeismicCategory() : 'SPECIAL'
        };

        const data = await this.api.save(this.page.sessionId, this.currentProjectId, results);

        if (data.success) {
            this.hasUnsavedChanges = false;
            this.updateSaveIndicator();
            this.page.showNotification('Proyecto guardado', 'success');
        }

        return data;
    }

    /**
     * Carga un proyecto existente.
     */
    async loadProject(projectId) {
        const data = await this.api.load(projectId);

        if (data.success) {
            // Actualizar estado
            this.currentProjectId = data.project_id;
            this.currentProjectName = data.metadata.name;
            this.page.sessionId = data.session_id;
            this.hasUnsavedChanges = false;

            // Persistir en storage
            this.storage.saveSessionId(data.session_id);
            this.storage.saveProjectId(data.project_id);
            this.storage.addRecentProject({
                id: data.project_id,
                name: data.metadata.name
            });

            // Actualizar UI
            this.updateProjectUI();

            // Usar resultados cacheados si existen, sino ejecutar análisis
            if (this.page.uploadManager) {
                if (data.has_results && data.results) {
                    // Carga instantánea desde cache
                    await this.page.uploadManager.loadCachedResults(data);
                } else {
                    // Sin cache - ejecutar análisis completo
                    await this.page.uploadManager.runAnalysisAfterLoad(data.summary);
                }
            }
        }

        return data;
    }

    /**
     * Carga proyecto y cierra modal.
     */
    async loadProjectAndClose(projectId) {
        this.closeProjectsModal();
        try {
            const result = await this.loadProject(projectId);
            if (!result.success) {
                this.page.showNotification(result.error || 'Error al cargar proyecto', 'error');
            }
        } catch (error) {
            console.error('Error cargando proyecto:', error);
            this.page.showNotification('Error al cargar proyecto: ' + error.message, 'error');
        }
    }

    /**
     * Elimina un proyecto.
     */
    async deleteProject(projectId) {
        const data = await this.api.delete(projectId);

        if (data.success && projectId === this.currentProjectId) {
            this.clearCurrentProject();
        }

        return data;
    }

    // =========================================================================
    // Estado
    // =========================================================================

    markAsModified() {
        if (!this.currentProjectId) return;

        this.hasUnsavedChanges = true;
        this.updateSaveIndicator();

        if (this.autoSaveEnabled) {
            this._scheduleAutoSave();
        }
    }

    _scheduleAutoSave() {
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }

        this.autoSaveTimer = setTimeout(async () => {
            if (this.hasUnsavedChanges && this.currentProjectId) {
                await this.saveProject();
            }
        }, this.autoSaveDelay);
    }

    clearCurrentProject() {
        this.currentProjectId = null;
        this.currentProjectName = null;
        this.hasUnsavedChanges = false;
        this.storage.clearSession();
        this.updateProjectUI();
    }

    // =========================================================================
    // UI - Actualización de Estado Visual
    // =========================================================================

    updateProjectUI() {
        const projectNameEl = document.getElementById('project-name');
        if (projectNameEl) {
            if (this.currentProjectName) {
                projectNameEl.textContent = this.currentProjectName;
                projectNameEl.classList.remove('no-project');
            } else if (this.page.sessionId) {
                projectNameEl.textContent = 'Sesion activa (sin guardar)';
                projectNameEl.classList.add('no-project');
            } else {
                projectNameEl.textContent = 'Sin proyecto';
                projectNameEl.classList.add('no-project');
            }
        }

        this.updateSaveIndicator();

        const saveBtn = document.getElementById('save-project-btn');
        if (saveBtn) {
            saveBtn.style.display = (this.currentProjectId || this.page.sessionId) ? 'inline-flex' : 'none';
            saveBtn.title = this.currentProjectId ? 'Guardar cambios' : 'Guardar como proyecto';
        }
    }

    updateSaveIndicator() {
        const indicator = document.getElementById('save-indicator');
        if (!indicator) return;

        if (!this.currentProjectId) {
            indicator.style.display = 'none';
            return;
        }

        indicator.style.display = 'inline-flex';
        indicator.classList.toggle('unsaved', this.hasUnsavedChanges);
        indicator.title = this.hasUnsavedChanges
            ? 'Cambios sin guardar'
            : 'Todos los cambios guardados';
    }

    // =========================================================================
    // Modal de Proyectos
    // =========================================================================

    async openProjectsModal() {
        const modal = document.getElementById('projects-modal');
        if (!modal) return;

        const projects = await this.api.list();
        this._renderProjectsList(projects);

        modal.classList.add('active');
    }

    closeProjectsModal() {
        const modal = document.getElementById('projects-modal');
        if (modal) {
            modal.classList.remove('active');
        }
        if (this._projectListController) {
            this._projectListController.abort();
            this._projectListController = null;
        }
    }

    _renderProjectsList(projects) {
        const container = document.getElementById('projects-list');
        if (!container) return;

        if (projects.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No hay proyectos guardados</p>
                    <p class="hint">Crea un proyecto para guardar tus modificaciones</p>
                </div>
            `;
            return;
        }

        container.innerHTML = projects.map(project => `
            <div class="project-item ${project.id === this.currentProjectId ? 'active' : ''}"
                 data-project-id="${project.id}"
                 data-project-name="${this._escapeHtml(project.name)}">
                <div class="project-info">
                    <span class="project-name">${this._escapeHtml(project.name)}</span>
                    <span class="project-meta">
                        ${project.source_file || 'Excel'} -
                        ${this._formatDate(project.updated_at)}
                    </span>
                </div>
                <div class="project-actions">
                    <button class="btn btn-primary btn-sm btn-load-project" title="Abrir proyecto">
                        Abrir
                    </button>
                    <button class="btn btn-danger btn-sm btn-delete-project" title="Eliminar proyecto">
                        Eliminar
                    </button>
                </div>
            </div>
        `).join('');

        this._bindProjectListEvents(container);
    }

    _bindProjectListEvents(container) {
        if (this._projectListController) {
            this._projectListController.abort();
        }
        this._projectListController = new AbortController();

        container.addEventListener('click', async (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;

            const projectItem = btn.closest('.project-item');
            if (!projectItem) return;

            const projectId = projectItem.dataset.projectId;
            const projectName = projectItem.dataset.projectName;

            if (btn.classList.contains('btn-load-project')) {
                e.preventDefault();
                e.stopPropagation();
                await this.loadProjectAndClose(projectId);
            } else if (btn.classList.contains('btn-delete-project')) {
                e.preventDefault();
                e.stopPropagation();
                await this._confirmDeleteProject(projectId, projectName);
            }
        }, { signal: this._projectListController.signal });
    }

    async _confirmDeleteProject(projectId, projectName) {
        if (!confirm(`¿Eliminar el proyecto "${projectName}"?\nEsta accion no se puede deshacer.`)) {
            return;
        }

        const result = await this.deleteProject(projectId);

        if (result.success) {
            this.page.showNotification(`Proyecto "${projectName}" eliminado`, 'info');
            const projects = await this.api.list();
            this._renderProjectsList(projects);
        } else {
            this.page.showNotification(result.error || 'Error al eliminar', 'error');
        }
    }

    // =========================================================================
    // Modal de Guardar Como
    // =========================================================================

    openSaveAsModal() {
        const modal = document.getElementById('save-project-modal');
        if (!modal) return;

        const nameInput = document.getElementById('new-project-name');
        const descInput = document.getElementById('new-project-description');

        if (nameInput) nameInput.value = this.currentProjectName || '';
        if (descInput) descInput.value = '';

        modal.classList.add('active');
        setTimeout(() => nameInput?.focus(), 100);
    }

    closeSaveAsModal() {
        const modal = document.getElementById('save-project-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    async saveAsNewProject() {
        const nameInput = document.getElementById('new-project-name');
        const descInput = document.getElementById('new-project-description');

        const name = nameInput?.value?.trim();
        const description = descInput?.value?.trim();

        if (!name) {
            this.page.showNotification('Ingresa un nombre para el proyecto', 'error');
            nameInput?.focus();
            return;
        }

        const file = this.page.uploadManager?.lastUploadedFile;
        if (!file) {
            this.page.showNotification(
                'No se encontro el archivo original. Por favor, carga el archivo nuevamente.',
                'error'
            );
            this.closeSaveAsModal();
            return;
        }

        try {
            const result = await this.createProject(name, description, file);

            if (result.success) {
                this.page.showNotification(`Proyecto "${name}" creado exitosamente`, 'success');
                this.closeSaveAsModal();
                await this.saveProject();
            } else {
                this.page.showNotification(result.error || 'Error al crear proyecto', 'error');
            }
        } catch (error) {
            console.error('Error creando proyecto:', error);
            this.page.showNotification('Error al crear proyecto: ' + error.message, 'error');
        }
    }

    // =========================================================================
    // Utilidades
    // =========================================================================

    _escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    _formatDate(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleDateString('es-CL', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}
