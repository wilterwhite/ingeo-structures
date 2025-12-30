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
        this.filters = { story: '', axis: '' };
        this.uniqueStories = [];
        this.uniqueAxes = [];

        // Elementos DOM
        this.elements = {};

        // Componentes (se inicializan en init())
        this.piersTable = null;
        this.resultsTable = null;
        this.plotModal = null;
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
            storyFilter: document.getElementById('story-filter'),
            axisFilter: document.getElementById('axis-filter'),

            // Stats
            statTotal: document.getElementById('stat-total'),
            statOk: document.getElementById('stat-ok'),
            statFail: document.getElementById('stat-fail'),
            statRate: document.getElementById('stat-rate'),

            // Pier Details Modal
            pierDetailsModal: document.getElementById('pier-details-modal'),
            pierDetailsTitle: document.getElementById('pier-details-title'),
            pierDetailsLoading: document.getElementById('pier-details-loading'),
            pierDetailsBody: document.getElementById('pier-details-body')
        };
    }

    initComponents() {
        this.piersTable = new PiersTable(this);
        this.resultsTable = new ResultsTable(this);
        this.plotModal = new PlotModal(this);
        this.plotModal.init();
        this.initPierDetailsModal();
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
        this.elements.piersStoryFilter?.addEventListener('change', () => this.piersTable.filter());
        this.elements.piersAxisFilter?.addEventListener('change', () => this.piersTable.filter());
        this.elements.applyGlobalBtn?.addEventListener('click', () => this.piersTable.applyGlobalConfig());
        this.elements.reanalyzeBtn?.addEventListener('click', () => this.reanalyze());
        this.elements.storyFilter?.addEventListener('change', () => this.resultsTable.applyFilters());
        this.elements.axisFilter?.addEventListener('change', () => this.resultsTable.applyFilters());

        // Botones de navegación
        document.getElementById('new-file-btn')?.addEventListener('click', () => {
            this.showSection('upload');
        });

        document.getElementById('back-to-piers-btn')?.addEventListener('click', () => {
            this.showSection('piers');
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
        this.filters = { story: '', axis: '' };
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
            this.uniqueStories = uploadData.summary.stories || [];
            this.uniqueAxes = uploadData.summary.axes || [];

            // Análisis automático
            const analyzeData = await structuralAPI.analyze({
                session_id: this.sessionId,
                pier_updates: [],
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0
            });

            if (!analyzeData.success) throw new Error(analyzeData.error);

            this.results = analyzeData.results;

            // Renderizar
            this.resultsTable.populateFilters();
            this.resultsTable.render(analyzeData);
            this.showSection('results');

            this.piersTable.populateFilters();
            this.piersTable.render();

        } catch (error) {
            console.error('Error:', error);
            alert('Error: ' + error.message);
            this.resetUploadArea();
        }
    }

    async reanalyze() {
        const btn = this.elements.reanalyzeBtn;
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Analizando...';
        }

        const updates = this.piersTable.getUpdates();

        try {
            const data = await structuralAPI.analyze({
                session_id: this.sessionId,
                pier_updates: updates,
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0
            });

            if (data.success) {
                this.results = data.results;
                this.resultsTable.reset();
                this.resultsTable.render(data);
                this.showSection('results');
            } else {
                alert('Error: ' + data.error);
            }
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

    editPierArmadura(pierKey) {
        this.showSection('piers');
        setTimeout(() => {
            this.piersTable.scrollToPier(pierKey);
        }, 100);
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
}

// Instancia global
const structuralPage = new StructuralPage();
