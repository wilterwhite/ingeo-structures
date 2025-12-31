// app/structural/static/js/StructuralPage.js
/**
 * Coordinador principal del módulo de análisis estructural.
 * Orquesta los componentes: PiersTable, ResultsTable, PlotModal.
 */

class StructuralPage {
    constructor() {
        // Estado
        this.sessionId = null;
        this.piersData = [];
        this.results = [];
        this.filters = { grilla: '', story: '', axis: '', status: '' };
        this.uniqueGrillas = [];
        this.uniqueStories = [];
        this.uniqueAxes = [];

        // Elementos DOM
        this.elements = {};

        // Componentes (se inicializan en init())
        this.piersTable = null;
        this.resultsTable = null;
        this.plotModal = null;
        this.reportModal = null;
    }

    // =========================================================================
    // Inicialización
    // =========================================================================

    init() {
        this.cacheElements();
        this.initComponents();
        this.bindEvents();
    }

    cacheElements() {
        this.elements = {
            // Secciones
            uploadSection: document.getElementById('upload-section'),
            piersSection: document.getElementById('piers-section'),
            resultsSection: document.getElementById('results-section'),

            // Upload
            uploadArea: document.getElementById('upload-area'),
            fileInput: document.getElementById('file-input'),
            uploadLoading: document.getElementById('upload-loading'),

            // Piers
            piersTable: document.getElementById('piers-table')?.querySelector('tbody'),
            pierCount: document.getElementById('pier-count'),
            piersGrillaFilter: document.getElementById('piers-grilla-filter'),
            piersStoryFilter: document.getElementById('piers-story-filter'),
            piersAxisFilter: document.getElementById('piers-axis-filter'),

            // Configuración global
            globalMeshes: document.getElementById('global-meshes'),
            globalDiameter: document.getElementById('global-diameter'),
            globalSpacing: document.getElementById('global-spacing'),
            globalEdgeDiameter: document.getElementById('global-edge-diameter'),
            globalCover: document.getElementById('global-cover'),
            applyGlobalBtn: document.getElementById('apply-global-btn'),
            reanalyzeBtn: document.getElementById('reanalyze-btn'),

            // Resultados
            resultsTable: document.getElementById('results-table')?.querySelector('tbody'),
            summaryPlotContainer: document.getElementById('summary-plot-container'),
            grillaFilter: document.getElementById('grilla-filter'),
            storyFilter: document.getElementById('story-filter'),
            axisFilter: document.getElementById('axis-filter'),
            statusFilter: document.getElementById('status-filter'),
            toggleAllCombosBtn: document.getElementById('toggle-all-combos-btn'),
            toggleCombosIcon: document.getElementById('toggle-combos-icon'),

            // Stats
            statTotal: document.getElementById('stat-total'),
            statOk: document.getElementById('stat-ok'),
            statFail: document.getElementById('stat-fail'),
            statRate: document.getElementById('stat-rate'),

            // Pier Details Modal
            pierDetailsModal: document.getElementById('pier-details-modal'),
            pierDetailsTitle: document.getElementById('pier-details-title'),
            pierDetailsLoading: document.getElementById('pier-details-loading'),
            pierDetailsBody: document.getElementById('pier-details-body'),

            // Section Diagram Modal
            sectionModal: document.getElementById('section-modal'),
            sectionModalTitle: document.getElementById('section-modal-title'),
            sectionModalLoading: document.getElementById('section-modal-loading'),
            sectionModalImg: document.getElementById('section-modal-img'),

            // Report
            generateReportBtn: document.getElementById('generate-report-btn')
        };
    }

    initComponents() {
        this.piersTable = new PiersTable(this);
        this.resultsTable = new ResultsTable(this);
        this.plotModal = new PlotModal(this);
        this.plotModal.init();
        this.reportModal = new ReportModal(this);
        this.reportModal.init();
        this.initPierDetailsModal();
        this.initSectionModal();
    }

    initPierDetailsModal() {
        const modal = this.elements.pierDetailsModal;
        if (!modal) return;

        // Cerrar al hacer clic en el botón X
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn?.addEventListener('click', () => this.closePierDetailsModal());

        // Cerrar al hacer clic fuera del contenido
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closePierDetailsModal();
            }
        });

        // Cerrar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                this.closePierDetailsModal();
            }
        });
    }

    bindEvents() {
        // Upload area
        this.elements.uploadArea?.addEventListener('click', () => {
            this.elements.fileInput?.click();
        });

        this.elements.uploadArea?.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.elements.uploadArea.classList.add('dragover');
        });

        this.elements.uploadArea?.addEventListener('dragleave', () => {
            this.elements.uploadArea.classList.remove('dragover');
        });

        this.elements.uploadArea?.addEventListener('drop', (e) => {
            e.preventDefault();
            this.elements.uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                this.handleFile(e.dataTransfer.files[0]);
            }
        });

        this.elements.fileInput?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0]);
            }
        });

        // Delegación a componentes
        this.elements.piersGrillaFilter?.addEventListener('change', () => this.piersTable.onGrillaChange());
        this.elements.piersStoryFilter?.addEventListener('change', () => this.piersTable.filter());
        this.elements.piersAxisFilter?.addEventListener('change', () => this.piersTable.filter());
        this.elements.applyGlobalBtn?.addEventListener('click', () => this.piersTable.applyGlobalConfig());
        this.elements.reanalyzeBtn?.addEventListener('click', () => this.reanalyze());
        this.elements.grillaFilter?.addEventListener('change', () => this.resultsTable.onGrillaChange());
        this.elements.storyFilter?.addEventListener('change', () => this.resultsTable.applyFilters());
        this.elements.axisFilter?.addEventListener('change', () => this.resultsTable.applyFilters());
        this.elements.statusFilter?.addEventListener('change', () => this.resultsTable.applyFilters());
        this.elements.toggleAllCombosBtn?.addEventListener('click', () => this.toggleAllCombinations());
        this.elements.generateReportBtn?.addEventListener('click', () => this.openReportModal());

        // Botones de navegación
        document.getElementById('new-file-btn')?.addEventListener('click', () => {
            this.showSection('upload');
        });

        document.getElementById('new-analysis-btn')?.addEventListener('click', () => {
            this.reset();
            this.showSection('upload');
        });
    }

    // =========================================================================
    // Navegación
    // =========================================================================

    showSection(section) {
        this.elements.uploadSection?.classList.toggle('hidden', section !== 'upload');
        this.elements.piersSection?.classList.toggle('hidden', section !== 'piers');
        this.elements.resultsSection?.classList.toggle('hidden', section !== 'results');

        if (section === 'upload') {
            this.resetUploadArea();
        }
    }

    resetUploadArea() {
        this.elements.uploadArea?.classList.remove('hidden');
        this.elements.uploadLoading?.classList.remove('active');
        if (this.elements.fileInput) {
            this.elements.fileInput.value = '';
        }
    }

    reset() {
        this.sessionId = null;
        this.piersData = [];
        this.results = [];
        this.filters = { grilla: '', story: '', axis: '', status: '' };
        this.uniqueGrillas = [];
        this.uniqueStories = [];
        this.uniqueAxes = [];
        this.resultsTable.reset();
    }

    // =========================================================================
    // Upload y Análisis
    // =========================================================================

    async handleFile(file) {
        if (!file.name.toLowerCase().endsWith('.xlsx')) {
            alert('Por favor selecciona un archivo Excel (.xlsx)');
            return;
        }

        if (file.size > 50 * 1024 * 1024) {
            alert('El archivo es demasiado grande. Máximo 50MB.');
            return;
        }

        // Verificar que el archivo no esté bloqueado
        try {
            const testReader = new FileReader();
            await new Promise((resolve, reject) => {
                testReader.onload = resolve;
                testReader.onerror = () => reject(new Error('locked'));
                testReader.readAsArrayBuffer(file.slice(0, 100));
            });
        } catch (e) {
            alert('No se puede acceder al archivo.\n¿Está abierto en Excel?\nCiérralo e intenta de nuevo.');
            return;
        }

        this.elements.uploadArea?.classList.add('hidden');
        this.elements.uploadLoading?.classList.add('active');

        try {
            // Upload
            const uploadData = await structuralAPI.uploadFile(file);
            if (!uploadData.success) throw new Error(uploadData.error);

            this.sessionId = uploadData.session_id;
            this.piersData = uploadData.summary.piers_list;
            this.uniqueGrillas = uploadData.summary.grillas || [];
            this.uniqueStories = uploadData.summary.stories || [];
            this.uniqueAxes = uploadData.summary.axes || [];

            // Mostrar progreso
            this.showProgressModal();

            // Análisis con progreso
            await this.runAnalysisWithProgress({
                session_id: this.sessionId,
                pier_updates: [],
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0
            });

        } catch (error) {
            console.error('Error:', error);
            alert('Error: ' + error.message);
            this.hideProgressModal();
            this.resetUploadArea();
        }
    }

    showProgressModal() {
        const modal = document.getElementById('progress-modal');
        if (modal) {
            modal.classList.add('active');
            this.updateProgress(0, 0, 'Iniciando análisis...');
        }
    }

    hideProgressModal() {
        const modal = document.getElementById('progress-modal');
        if (modal) modal.classList.remove('active');
    }

    updateProgress(current, total, pier) {
        const progressText = document.getElementById('progress-text');
        const progressBar = document.getElementById('progress-bar');
        const progressPier = document.getElementById('progress-pier');

        if (progressText) {
            progressText.textContent = total > 0 ? `Procesando pier ${current} de ${total}` : pier;
        }
        if (progressBar && total > 0) {
            progressBar.style.width = `${(current / total) * 100}%`;
        }
        if (progressPier) {
            progressPier.textContent = pier;
        }
    }

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
                        this.results = data.results;
                        this.resultsTable.populateFilters();
                        this.resultsTable.render(data);
                        this.showSection('results');
                        this.piersTable.populateFilters();
                        this.piersTable.render();
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

    async reanalyze() {
        const btn = this.elements.reanalyzeBtn;
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Analizando...';
        }

        const updates = this.piersTable.getUpdates();
        this.showProgressModal();

        try {
            await this.runAnalysisWithProgress({
                session_id: this.sessionId,
                pier_updates: updates,
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0
            });
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = 'Reanalizar';
            }
        }
    }

    // =========================================================================
    // Acciones de Pier
    // =========================================================================

    async toggleAllCombinations() {
        const { toggleCombosIcon, toggleAllCombosBtn } = this.elements;

        // Deshabilitar botón mientras carga
        if (toggleAllCombosBtn) {
            toggleAllCombosBtn.disabled = true;
            toggleAllCombosBtn.innerHTML = '<span id="toggle-combos-icon">⏳</span> Cargando...';
        }

        try {
            const allExpanded = await this.resultsTable.toggleAllExpand();

            // Actualizar ícono y texto
            if (toggleAllCombosBtn) {
                toggleAllCombosBtn.innerHTML = `<span id="toggle-combos-icon">${allExpanded ? '▼' : '▶'}</span> ${allExpanded ? 'Colapsar todo' : 'Expandir todo'}`;
            }
        } finally {
            if (toggleAllCombosBtn) {
                toggleAllCombosBtn.disabled = false;
            }
        }
    }

    // =========================================================================
    // Pier Details Modal
    // =========================================================================

    async showPierDetails(pierKey, pierLabel) {
        const { pierDetailsModal, pierDetailsTitle, pierDetailsLoading } = this.elements;

        if (!pierDetailsModal) return;

        // Abrir modal y mostrar loading
        pierDetailsModal.classList.add('active');
        pierDetailsTitle.textContent = pierLabel;
        pierDetailsLoading.classList.add('active');

        try {
            const data = await structuralAPI.getPierCapacities(this.sessionId, pierKey);

            if (data.success) {
                this.updatePierDetailsContent(data);
            } else {
                alert('Error: ' + data.error);
                this.closePierDetailsModal();
            }
        } catch (error) {
            console.error('Error getting pier capacities:', error);
            alert('Error: ' + error.message);
            this.closePierDetailsModal();
        } finally {
            pierDetailsLoading.classList.remove('active');
        }
    }

    updatePierDetailsContent(data) {
        const { pier_info, reinforcement, slenderness, capacities } = data;

        // Geometría
        document.getElementById('detail-width').textContent = `${pier_info.width_m} m`;
        document.getElementById('detail-thickness').textContent = `${pier_info.thickness_m} m`;
        document.getElementById('detail-height').textContent = `${pier_info.height_m} m`;
        document.getElementById('detail-fc').textContent = `${pier_info.fc_MPa} MPa`;
        document.getElementById('detail-fy').textContent = `${pier_info.fy_MPa} MPa`;

        // Armadura
        document.getElementById('detail-reinf-desc').textContent = reinforcement.description;
        document.getElementById('detail-as-vertical').textContent = `${reinforcement.As_vertical_mm2} mm²`;
        document.getElementById('detail-as-edge').textContent = `${reinforcement.As_edge_mm2} mm²`;
        document.getElementById('detail-as-total').textContent = `${reinforcement.As_flexure_total_mm2} mm²`;

        // Esbeltez
        if (slenderness) {
            document.getElementById('detail-lambda').textContent = slenderness.lambda;
            document.getElementById('detail-lambda-limit').textContent = slenderness.limit;

            const statusEl = document.getElementById('detail-slender-status');
            if (slenderness.is_slender) {
                statusEl.textContent = 'ESBELTO';
                statusEl.style.color = 'var(--warning-color)';
            } else {
                statusEl.textContent = 'NO ESBELTO';
                statusEl.style.color = 'var(--success-color)';
            }

            const reductionEl = document.getElementById('detail-slender-reduction');
            if (slenderness.is_slender && slenderness.reduction_pct > 0) {
                reductionEl.textContent = `-${slenderness.reduction_pct}%`;
                reductionEl.style.color = 'var(--warning-color)';
            } else {
                reductionEl.textContent = 'Sin reducción';
                reductionEl.style.color = 'inherit';
            }
        }

        // Capacidades
        // Si hay reducción por esbeltez, mostrar ambos valores
        if (slenderness && slenderness.is_slender) {
            document.getElementById('detail-phi-pn').innerHTML =
                `<span style="text-decoration: line-through; color: var(--text-muted);">${capacities.phi_Pn_max_tonf}</span>` +
                ` → ${capacities.phi_Pn_reduced_tonf}`;
        } else {
            document.getElementById('detail-phi-pn').textContent = capacities.phi_Pn_max_tonf;
        }
        document.getElementById('detail-phi-mn3').textContent = capacities.phi_Mn3_tonf_m;
        document.getElementById('detail-phi-mn2').textContent = capacities.phi_Mn2_tonf_m;
        document.getElementById('detail-phi-vn2').textContent = capacities.phi_Vn2_tonf;
        document.getElementById('detail-phi-vn3').textContent = capacities.phi_Vn3_tonf;
    }

    closePierDetailsModal() {
        const { pierDetailsModal } = this.elements;
        pierDetailsModal?.classList.remove('active');
    }

    // =========================================================================
    // Section Diagram Modal
    // =========================================================================

    initSectionModal() {
        const modal = this.elements.sectionModal;
        if (!modal) return;

        // Cerrar al hacer clic en el botón X
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn?.addEventListener('click', () => this.closeSectionModal());

        // Cerrar al hacer clic fuera del contenido
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeSectionModal();
            }
        });

        // Cerrar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                this.closeSectionModal();
            }
        });
    }

    async showSectionDiagram(pierKey, pierLabel) {
        const { sectionModal, sectionModalTitle, sectionModalLoading, sectionModalImg } = this.elements;

        if (!sectionModal) return;

        // Abrir modal y mostrar loading
        sectionModal.classList.add('active');
        sectionModalTitle.textContent = `Sección - ${pierLabel}`;
        sectionModalLoading.classList.add('active');
        sectionModalImg.style.display = 'none';

        try {
            const data = await structuralAPI.getSectionDiagram(this.sessionId, pierKey);

            if (data.success && data.section_diagram) {
                sectionModalImg.src = `data:image/png;base64,${data.section_diagram}`;
                sectionModalImg.style.display = 'block';
            } else {
                alert('Error: ' + (data.error || 'No se pudo generar el diagrama'));
                this.closeSectionModal();
            }
        } catch (error) {
            console.error('Error getting section diagram:', error);
            alert('Error: ' + error.message);
            this.closeSectionModal();
        } finally {
            sectionModalLoading.classList.remove('active');
        }
    }

    closeSectionModal() {
        const { sectionModal } = this.elements;
        sectionModal?.classList.remove('active');
    }

    // =========================================================================
    // Report Modal
    // =========================================================================

    openReportModal() {
        const totalPiers = this.results?.length || 0;
        if (totalPiers === 0) {
            alert('No hay resultados de análisis para generar informe.');
            return;
        }
        this.reportModal.open(totalPiers);
    }

    async showProposedSectionDiagram(pierKey, pierLabel, proposedConfig) {
        const { sectionModal, sectionModalTitle, sectionModalLoading, sectionModalImg } = this.elements;

        if (!sectionModal) return;

        // Abrir modal y mostrar loading
        sectionModal.classList.add('active');
        sectionModalTitle.textContent = `Sección Propuesta - ${pierLabel}`;
        sectionModalLoading.classList.add('active');
        sectionModalImg.style.display = 'none';

        try {
            const data = await structuralAPI.getSectionDiagram(
                this.sessionId,
                pierKey,
                proposedConfig
            );

            if (data.success && data.section_diagram) {
                sectionModalImg.src = `data:image/png;base64,${data.section_diagram}`;
                sectionModalImg.style.display = 'block';
            } else {
                alert('Error: ' + (data.error || 'No se pudo generar el diagrama'));
                this.closeSectionModal();
            }
        } catch (error) {
            console.error('Error getting proposed section diagram:', error);
            alert('Error: ' + error.message);
            this.closeSectionModal();
        } finally {
            sectionModalLoading.classList.remove('active');
        }
    }
}

// Instancia global
const structuralPage = new StructuralPage();
