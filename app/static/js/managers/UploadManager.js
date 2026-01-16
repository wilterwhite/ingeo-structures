// app/static/js/managers/UploadManager.js
/**
 * Gestor de carga de archivos y análisis.
 * Maneja upload, progreso, y coordinación del análisis.
 */

class UploadManager {
    constructor(page) {
        this.page = page;
        this.lastUploadedFile = null;  // Guardar referencia al ultimo archivo
    }

    /**
     * Configura los eventos de drag & drop y file input.
     */
    bindEvents() {
        const { uploadArea, fileInput } = this.page.elements;

        // Prevenir que el navegador abra archivos soltados en cualquier parte
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        document.addEventListener('drop', (e) => {
            e.preventDefault();
        });

        uploadArea?.addEventListener('click', () => {
            fileInput?.click();
        });

        uploadArea?.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.add('dragover');
        });

        uploadArea?.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea?.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                this.handleFile(e.dataTransfer.files[0]);
            }
        });

        fileInput?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0]);
            }
        });
    }

    /**
     * Actualiza el estado del upload en el UI.
     */
    updateUploadStatus(status, detail = '') {
        const statusEl = document.getElementById('upload-status');
        const detailEl = document.getElementById('upload-detail');
        if (statusEl) statusEl.textContent = status;
        if (detailEl) detailEl.textContent = detail;
    }

    /**
     * Maneja la carga de un archivo.
     */
    async handleFile(file) {
        if (!this.validateFile(file)) return;

        // Si es archivo E2K, procesarlo para generar Section Cuts
        if (file.name.toLowerCase().endsWith('.e2k')) {
            return this.handleE2KFile(file);
        }

        // Guardar referencia al archivo para poder crear proyecto despues
        this.lastUploadedFile = file;

        this.page.elements.uploadArea?.classList.add('hidden');
        this.page.elements.uploadLoading?.classList.add('active');

        try {
            // Fase 1: Upload con progreso
            const uploadData = await structuralAPI.uploadWithProgress(
                file,
                (current, total, element) => {
                    this.updateUploadStatus(`Parseando ${current} de ${total}`, element);
                }
            );

            if (!uploadData.success) throw new Error(uploadData.error);
            this.storeUploadData(uploadData);

            // Delay necesario: el navegador limita conexiones simultáneas al mismo host.
            // Sin esto, el fetch del análisis puede quedar bloqueado esperando que
            // la conexión del upload-stream se libere completamente.
            await new Promise(r => setTimeout(r, 100));

            // Fase 2: Análisis con progreso (usa método unificado)
            await this._executeAnalysis();

        } catch (error) {
            console.error('Error en análisis:', error);
            this.page.showNotification('Error: ' + error.message, 'error');
            this.hideProgressModal();
            this.resetUploadArea();
        }
    }

    /**
     * Almacena los datos del upload en la página.
     */
    storeUploadData(uploadData) {
        const summary = uploadData.summary || {};

        // Mostrar resumen del parsing
        const counts = [];
        if (summary.total_piers > 0) counts.push(`${summary.total_piers} muros`);
        if (summary.total_columns > 0) counts.push(`${summary.total_columns} columnas`);
        if (summary.total_beams > 0) counts.push(`${summary.total_beams} vigas`);
        if (summary.total_drop_beams > 0) counts.push(`${summary.total_drop_beams} vigas capitel`);
        this.updateUploadStatus('Archivo procesado', counts.join(', '));

        // Almacenar datos en page
        this.page.sessionId = uploadData.session_id;
        this.page.piersData = summary.piers_list || [];
        this.page.columnsData = summary.columns_list || [];
        this.page.beamsData = summary.beams_list || [];
        this.page.dropBeamsData = summary.drop_beams_list || [];
        this.page.uniqueGrillas = summary.grillas || [];
        this.page.uniqueStories = summary.stories || [];
        this.page.uniqueAxes = summary.axes || [];

        // Extraer materiales
        this.page.materialsManager.extractFromData(
            this.page.piersData,
            this.page.columnsData
        );
    }

    /**
     * Maneja archivos E2K para generar Section Cuts.
     */
    async handleE2KFile(file) {
        this.page.elements.uploadArea?.classList.add('hidden');
        this.page.elements.uploadLoading?.classList.add('active');

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/structural/process-e2k', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error procesando archivo E2K');
            }

            // Obtener información de los headers
            const scutsGenerated = response.headers.get('X-Section-Cuts-Generated') || '?';
            const totalGroups = response.headers.get('X-Total-Groups') || '?';

            // Descargar el archivo
            const blob = await response.blob();
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'output_with_scuts.e2k';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^"]+)"?/);
                if (match) filename = match[1];
            }

            // Crear enlace de descarga
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.page.showNotification(
                `Section Cuts generados: ${scutsGenerated} (de ${totalGroups} grupos). Archivo descargado.`,
                'success'
            );

        } catch (error) {
            console.error('Error procesando E2K:', error);
            this.page.showNotification('Error: ' + error.message, 'error');
        } finally {
            this.resetUploadArea();
        }
    }

    /**
     * Valida el archivo antes de procesarlo.
     */
    validateFile(file) {
        const fileName = file.name.toLowerCase();
        const isExcel = fileName.endsWith('.xlsx');
        const isE2K = fileName.endsWith('.e2k');

        if (!isExcel && !isE2K) {
            this.page.showNotification('Por favor selecciona un archivo Excel (.xlsx) o E2K (.e2k)', 'error');
            return false;
        }

        if (file.size > 50 * 1024 * 1024) {
            this.page.showNotification('El archivo es demasiado grande. Máximo 50MB.', 'error');
            return false;
        }

        return true;
    }

    /**
     * Muestra el modal de progreso.
     */
    showProgressModal() {
        const modal = document.getElementById('progress-modal');
        if (modal) {
            modal.classList.add('active');
            this.updateProgress(0, 0, 'Iniciando análisis...');
        }
    }

    /**
     * Oculta el modal de progreso.
     */
    hideProgressModal() {
        const modal = document.getElementById('progress-modal');
        if (modal) modal.classList.remove('active');
    }

    /**
     * Actualiza el progreso en el modal.
     */
    updateProgress(current, total, element) {
        const progressText = document.getElementById('progress-text');
        const progressBar = document.getElementById('progress-bar');
        const progressPier = document.getElementById('progress-pier');

        if (progressText) {
            progressText.textContent = total > 0 ? `Procesando ${current} de ${total}` : element;
        }
        if (progressBar && total > 0) {
            progressBar.style.width = `${(current / total) * 100}%`;
        }
        if (progressPier) {
            progressPier.textContent = element;
        }
    }

    /**
     * Procesa los resultados del análisis.
     */
    onAnalysisComplete(data) {
        const page = this.page;

        page.results = data.results;
        page.columnResults = data.column_results || [];
        page.beamResults = data.beam_results || [];
        page.dropBeamResults = data.drop_beam_results || [];

        // Limpiar cache de filteredResults para asegurar datos frescos
        page.resultsTable.filteredResults = [];

        // Renderizar resultados
        page.resultsTable.populateFilters();
        page.resultsTable.render(data);
        page.beamsModule.renderBeamsTable();  // Incluye BEAM y DROP_BEAM
        page.showSection('results');

        // Actualizar UI de proyecto (mostrar boton de guardar si hay sesion)
        if (page.projectManager) {
            page.projectManager.updateProjectUI();
        }
    }

    /**
     * Resetea el área de upload.
     */
    resetUploadArea() {
        this.page.elements.uploadArea?.classList.remove('hidden');
        this.page.elements.uploadLoading?.classList.remove('active');
        if (this.page.elements.fileInput) {
            this.page.elements.fileInput.value = '';
        }
        // Resetear estado del upload
        this.updateUploadStatus('Procesando archivo...', '');
    }

    /**
     * Ejecuta el análisis estructural.
     * Método unificado usado por handleFile, reanalyze y runAnalysisAfterLoad.
     *
     * @param {Object} options - Opciones de ejecución
     * @param {boolean} options.showModal - Mostrar modal de progreso (default: true)
     * @returns {Promise<Object>} Resultado del análisis
     */
    async _executeAnalysis(options = {}) {
        const { showModal = true } = options;

        if (showModal) {
            this.showProgressModal();
        }

        try {
            const params = {
                session_id: this.page.sessionId,
                pier_updates: [],
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0,
                materials_config: this.page.materialsManager.getConfig(),
                seismic_category: this.page.getSeismicCategory()
            };

            const result = await structuralAPI.analyzeWithProgress(
                params,
                (current, total, pier) => {
                    this.updateProgress(current, total, pier);
                }
            );

            this.hideProgressModal();

            if (result.success) {
                this.onAnalysisComplete(result);
            } else {
                throw new Error(result.error || 'Error en análisis');
            }

            return result;

        } catch (error) {
            console.error('Error en análisis:', error);
            this.page.showNotification('Error: ' + error.message, 'error');
            this.hideProgressModal();
            throw error;
        }
    }

    /**
     * Re-ejecuta el análisis con la configuración actual.
     */
    async reanalyze() {
        return this._executeAnalysis();
    }

    /**
     * Ejecuta análisis después de cargar un proyecto.
     * @param {Object} summary - Summary del proyecto cargado
     */
    async runAnalysisAfterLoad(summary) {
        // Almacenar datos del summary en la página
        this._storeSummaryData(summary);

        // Extraer materiales
        this.page.materialsManager.extractFromData(
            this.page.piersData,
            this.page.columnsData
        );

        // Transición de UI: ocultar upload, mostrar config
        this.page.elements.uploadSection?.classList.add('hidden');
        this.page.elements.configCard?.classList.remove('hidden');

        // Ejecutar análisis
        return this._executeAnalysis();
    }

    /**
     * Carga resultados desde cache sin re-analizar.
     * Se usa cuando el proyecto tiene results.json guardado.
     * @param {Object} data - Respuesta del load con results y summary
     */
    async loadCachedResults(data) {
        // Almacenar datos del summary
        this._storeSummaryData(data.summary);

        // Extraer materiales
        this.page.materialsManager.extractFromData(
            this.page.piersData,
            this.page.columnsData
        );

        // Transición de UI: ocultar upload, mostrar config
        this.page.elements.uploadSection?.classList.add('hidden');
        this.page.elements.configCard?.classList.remove('hidden');

        // Restaurar resultados desde cache
        const results = data.results;
        this.page.results = results.piers || [];
        this.page.columnResults = results.columns || [];
        this.page.beamResults = results.beams || [];
        this.page.dropBeamResults = results.drop_beams || [];

        // Renderizar usando el flujo existente
        this.onAnalysisComplete({
            success: true,
            results: this.page.results,
            column_results: this.page.columnResults,
            beam_results: this.page.beamResults,
            drop_beam_results: this.page.dropBeamResults
        });
    }

    /**
     * Almacena los datos del summary en la página.
     * @param {Object} summary - Summary con listas de elementos
     */
    _storeSummaryData(summary) {
        const page = this.page;
        page.piersData = summary.piers_list || [];
        page.columnsData = summary.columns_list || [];
        page.beamsData = summary.beams_list || [];
        page.dropBeamsData = summary.drop_beams_list || [];
        page.uniqueGrillas = summary.grillas || [];
        page.uniqueStories = summary.stories || [];
        page.uniqueAxes = summary.axes || [];
    }
}
