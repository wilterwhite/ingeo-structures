// app/static/js/managers/UploadManager.js
/**
 * Gestor de carga de archivos y análisis.
 * Maneja upload, progreso, y coordinación del análisis.
 */

class UploadManager {
    constructor(page) {
        this.page = page;
    }

    /**
     * Configura los eventos de drag & drop y file input.
     */
    bindEvents() {
        const { uploadArea, fileInput } = this.page.elements;

        uploadArea?.addEventListener('click', () => {
            fileInput?.click();
        });

        uploadArea?.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea?.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea?.addEventListener('drop', (e) => {
            e.preventDefault();
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
     * Maneja la carga de un archivo.
     */
    async handleFile(file) {
        if (!this.validateFile(file)) return;

        this.page.elements.uploadArea?.classList.add('hidden');
        this.page.elements.uploadLoading?.classList.add('active');

        try {
            // Upload
            const uploadData = await structuralAPI.uploadFile(file);
            if (!uploadData.success) throw new Error(uploadData.error);

            // Almacenar datos en page
            this.page.sessionId = uploadData.session_id;
            this.page.piersData = uploadData.summary.piers_list || [];
            this.page.columnsData = uploadData.summary.columns_list || [];
            this.page.beamsData = uploadData.summary.beams_list || [];
            this.page.slabsData = uploadData.summary.slabs_list || [];
            this.page.dropBeamsData = uploadData.summary.drop_beams_list || [];
            this.page.uniqueGrillas = uploadData.summary.grillas || [];
            this.page.uniqueStories = uploadData.summary.stories || [];
            this.page.uniqueAxes = uploadData.summary.axes || [];

            console.log('[Upload] Parsed data:', {
                piers: this.page.piersData.length,
                columns: this.page.columnsData.length,
                beams: this.page.beamsData.length,
                slabs: this.page.slabsData.length,
                dropBeams: this.page.dropBeamsData.length
            });

            // Extraer materiales
            this.page.materialsManager.extractFromData(
                this.page.piersData,
                this.page.columnsData
            );

            // Mostrar progreso y ejecutar análisis
            this.showProgressModal();
            await this.runAnalysisWithProgress({
                session_id: this.page.sessionId,
                pier_updates: [],
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0,
                materials_config: this.page.materialsManager.getConfig()
            });

        } catch (error) {
            console.error('Error:', error);
            this.page.showNotification('Error: ' + error.message, 'error');
            this.hideProgressModal();
            this.resetUploadArea();
        }
    }

    /**
     * Valida el archivo antes de procesarlo.
     */
    validateFile(file) {
        if (!file.name.toLowerCase().endsWith('.xlsx')) {
            this.page.showNotification('Por favor selecciona un archivo Excel (.xlsx)', 'error');
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
     * Ejecuta el análisis con callbacks de progreso.
     */
    runAnalysisWithProgress(params) {
        return new Promise((resolve, reject) => {
            structuralAPI.analyzeWithProgress(
                params,
                // onProgress
                (current, total, pier) => {
                    this.updateProgress(current, total, pier);
                },
                // onComplete
                (data) => {
                    this.hideProgressModal();
                    if (data.success) {
                        this.onAnalysisComplete(data);
                        resolve(data);
                    } else {
                        reject(new Error(data.error || 'Error en análisis'));
                    }
                },
                // onError
                (error) => {
                    this.hideProgressModal();
                    reject(error);
                }
            );
        });
    }

    /**
     * Procesa los resultados del análisis.
     */
    onAnalysisComplete(data) {
        const page = this.page;

        page.results = data.results;
        page.columnResults = data.column_results || [];
        page.beamResults = data.beam_results || [];
        page.slabResults = data.slab_results || [];
        page.dropBeamResults = data.drop_beam_results || [];

        // Log para debug
        if (page.columnResults.length > 0) {
            console.log('[Analysis] Column results:', page.columnResults.length);
        }
        if (page.beamResults.length > 0) {
            console.log('[Analysis] Beam results:', page.beamResults.length);
        }
        if (page.slabResults.length > 0) {
            console.log('[Analysis] Slab results:', page.slabResults.length);
        }
        if (page.dropBeamResults.length > 0) {
            console.log('[Analysis] Drop beam results:', page.dropBeamResults.length);
        }

        // Renderizar resultados
        page.resultsTable.populateFilters();
        page.resultsTable.render(data);
        page.beamsModule.renderBeamsTable();
        page.slabsTable.renderTable(page.slabResults);
        page.renderDropBeamsTable();
        page.showSection('results');
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
    }

    /**
     * Re-ejecuta el análisis con la configuración actual.
     */
    async reanalyze() {
        this.showProgressModal();
        try {
            await this.runAnalysisWithProgress({
                session_id: this.page.sessionId,
                pier_updates: [],
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0,
                materials_config: this.page.materialsManager.getConfig()
            });
        } catch (error) {
            this.page.showNotification('Error: ' + error.message, 'error');
        }
    }
}
