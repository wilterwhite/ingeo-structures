// app/structural/static/js/StructuralPage.js
/**
 * Coordinador principal del módulo de análisis estructural.
 * Orquesta los componentes: ResultsTable, PlotModal, módulos y managers.
 *
 * Managers:
 * - MaterialsManager: Gestión de tipos de concreto y lambda
 * - UploadManager: Carga de archivos y análisis
 *
 * Módulos:
 * - WallsModule: Muros y columnas
 * - BeamsModule: Vigas
 */

class StructuralPage {
    constructor() {
        // Estado de datos
        this.sessionId = null;
        this.piersData = [];
        this.columnsData = [];
        this.beamsData = [];
        this.slabsData = [];
        this.dropBeamsData = [];
        this.results = [];
        this.columnResults = [];
        this.beamResults = [];
        this.slabResults = [];
        this.dropBeamResults = [];

        // Filtros y metadatos
        this.filters = { grilla: '', story: '', axis: '', status: '', elementType: '' };
        this.uniqueGrillas = [];
        this.uniqueStories = [];
        this.uniqueAxes = [];
        this.currentPage = 'config-page';

        // Elementos DOM (se cachean en init)
        this.elements = {};

        // Managers y componentes (se inicializan en init)
        this.materialsManager = null;
        this.uploadManager = null;
        this.resultsTable = null;
        this.slabsTable = null;
        this.plotModal = null;
        this.reportModal = null;
    }

    // =========================================================================
    // Inicialización
    // =========================================================================

    async init() {
        // Cargar constantes del backend primero
        if (typeof StructuralConstants !== 'undefined') {
            await StructuralConstants.load();
        }

        this.cacheElements();
        this.initComponents();
        this.bindEvents();
    }

    cacheElements() {
        this.elements = {
            // Config page
            uploadSection: document.getElementById('upload-section'),
            configCard: document.getElementById('config-card'),

            // Upload
            uploadArea: document.getElementById('upload-area'),
            fileInput: document.getElementById('file-input'),
            uploadLoading: document.getElementById('upload-loading'),

            // Walls page
            wallsPlaceholder: document.getElementById('walls-placeholder'),
            resultsSection: document.getElementById('results-section'),

            // Beams page
            beamsPlaceholder: document.getElementById('beams-placeholder'),
            beamsResultsSection: document.getElementById('beams-results-section'),

            // Slabs page
            slabsPlaceholder: document.getElementById('slabs-placeholder'),
            slabsResultsSection: document.getElementById('slabs-results-section'),

            // Vigas (Beams)
            beamsTableBody: document.getElementById('beams-table')?.querySelector('tbody'),

            // Vigas Capitel (Drop Beams)
            dropBeamsPlaceholder: document.getElementById('drop-beams-placeholder'),
            dropBeamsResultsSection: document.getElementById('drop-beams-results-section'),
            dropBeamsTable: document.getElementById('drop-beams-table')?.querySelector('tbody'),

            // Paginas principales
            configPage: document.getElementById('config-page'),
            wallsPage: document.getElementById('walls-page'),
            beamsPage: document.getElementById('beams-page'),
            slabsPage: document.getElementById('slabs-page'),
            dropBeamsPage: document.getElementById('drop-beams-page'),

            // Resultados
            resultsTable: document.getElementById('results-table')?.querySelector('tbody'),
            summaryPlotContainer: document.getElementById('summary-plot-container'),
            grillaFilter: document.getElementById('grilla-filter'),
            storyFilter: document.getElementById('story-filter'),
            axisFilter: document.getElementById('axis-filter'),
            statusFilter: document.getElementById('status-filter'),
            elementTypeFilter: document.getElementById('element-type-filter'),
            // Viga estándar
            stdBeamWidth: document.getElementById('std-beam-width'),
            stdBeamHeight: document.getElementById('std-beam-height'),
            stdBeamLn: document.getElementById('std-beam-ln'),
            stdBeamNbars: document.getElementById('std-beam-nbars'),
            stdBeamDiam: document.getElementById('std-beam-diam'),

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
            generateReportBtn: document.getElementById('generate-report-btn'),

            // Materiales (Config page)
            materialsTableWrapper: document.getElementById('materials-table-wrapper'),
            materialsTbody: document.getElementById('materials-tbody')
        };
    }

    initComponents() {
        // Managers
        this.materialsManager = new MaterialsManager(this);
        this.uploadManager = new UploadManager(this);

        // Componentes de UI
        this.resultsTable = new ResultsTable(this);
        this.slabsTable = new SlabsTable(this);
        this.slabsTable.bindFilterEvents();
        this.plotModal = new PlotModal(this);
        this.plotModal.init();
        this.reportModal = new ReportModal(this);
        this.reportModal.init();

        // Módulos de elementos
        this.wallsModule = new WallsModule(this);
        this.beamsModule = new BeamsModule(this);

        this.initPierDetailsModal();
        this.wallsModule.initSectionModal();
        this.beamsModule.initCustomBeamModal();
    }

    initPierDetailsModal() {
        const modal = this.elements.pierDetailsModal;
        if (!modal) return;
        setupModalClose(modal, () => this.wallsModule.closePierDetailsModal());
    }

    bindEvents() {
        // Navegación principal (tabs de páginas)
        document.querySelectorAll('.main-nav .nav-tab').forEach(tab => {
            tab.addEventListener('click', () => this.navigateToPage(tab.dataset.page));
        });

        // Upload (delegado a UploadManager)
        this.uploadManager.bindEvents();

        // Filtros de resultados
        this.elements.grillaFilter?.addEventListener('change', () => this.resultsTable.onGrillaChange());
        this.elements.storyFilter?.addEventListener('change', () => this.resultsTable.applyFilters());
        this.elements.axisFilter?.addEventListener('change', () => this.resultsTable.applyFilters());
        this.elements.statusFilter?.addEventListener('change', () => this.resultsTable.applyFilters());
        this.elements.elementTypeFilter?.addEventListener('change', () => this.resultsTable.applyFilters());
        this.elements.generateReportBtn?.addEventListener('click', () => this.openReportModal());

        // Viga estándar (para muros acoplados)
        this.elements.stdBeamWidth?.addEventListener('change', () => this.beamsModule.onStandardBeamChange());
        this.elements.stdBeamHeight?.addEventListener('change', () => this.beamsModule.onStandardBeamChange());
        this.elements.stdBeamLn?.addEventListener('change', () => this.beamsModule.onStandardBeamChange());
        this.elements.stdBeamNbars?.addEventListener('change', () => this.beamsModule.onStandardBeamChange());
        this.elements.stdBeamDiam?.addEventListener('change', () => this.beamsModule.onStandardBeamChange());

        // Botones de navegación
        document.getElementById('new-file-btn')?.addEventListener('click', () => {
            this.reset();
            this.showSection('upload');
            this.navigateToPage('config-page');
        });

        document.getElementById('new-analysis-btn')?.addEventListener('click', () => {
            this.reset();
            this.showSection('upload');
            this.navigateToPage('config-page');
        });

        // Botón de diagrama P-M en modal de detalles
        document.getElementById('open-pm-diagram-btn')?.addEventListener('click', () => this.wallsModule.openPmDiagram());
    }

    // =========================================================================
    // Navegación Principal (Páginas)
    // =========================================================================

    navigateToPage(pageId) {
        // Actualizar tabs
        document.querySelectorAll('.main-nav .nav-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.page === pageId);
        });

        // Mostrar/ocultar paginas
        this.elements.configPage?.classList.toggle('hidden', pageId !== 'config-page');
        this.elements.wallsPage?.classList.toggle('hidden', pageId !== 'walls-page');
        this.elements.beamsPage?.classList.toggle('hidden', pageId !== 'beams-page');
        this.elements.slabsPage?.classList.toggle('hidden', pageId !== 'slabs-page');
        this.elements.dropBeamsPage?.classList.toggle('hidden', pageId !== 'drop-beams-page');

        this.currentPage = pageId;
    }

    // =========================================================================
    // Navegación de Secciones
    // =========================================================================

    showSection(section) {
        // Config page
        this.elements.uploadSection?.classList.toggle('hidden', section !== 'upload');
        this.elements.configCard?.classList.toggle('hidden', section === 'upload');

        // Walls page
        this.elements.wallsPlaceholder?.classList.toggle('hidden', section !== 'upload');
        this.elements.resultsSection?.classList.toggle('hidden', section !== 'results');

        // Beams page
        this.elements.beamsPlaceholder?.classList.toggle('hidden', section !== 'upload');
        this.elements.beamsResultsSection?.classList.toggle('hidden', section !== 'results');

        // Slabs page
        this.elements.slabsPlaceholder?.classList.toggle('hidden', section !== 'upload');
        this.elements.slabsResultsSection?.classList.toggle('hidden', section !== 'results');

        // Drop Beams page
        this.elements.dropBeamsPlaceholder?.classList.toggle('hidden', section !== 'upload');
        this.elements.dropBeamsResultsSection?.classList.toggle('hidden', section !== 'results');

        if (section === 'upload') {
            this.resetUploadArea();
        }

        // Navegar a la página de muros después de análisis
        if (section === 'results') {
            this.navigateToPage('walls-page');
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
        this.columnsData = [];
        this.beamsData = [];
        this.slabsData = [];
        this.dropBeamsData = [];
        this.results = [];
        this.columnResults = [];
        this.beamResults = [];
        this.slabResults = [];
        this.dropBeamResults = [];
        this.filters = { grilla: '', story: '', axis: '', status: '', elementType: '' };
        this.uniqueGrillas = [];
        this.uniqueStories = [];
        this.uniqueAxes = [];

        // Reset componentes
        this.materialsManager.reset();
        this.resultsTable.reset();
        this.beamsModule.clearBeamsTable();
        this.slabsTable.clear();
        this.clearDropBeamsTable();
    }

    // =========================================================================
    // Delegación a Managers (Métodos de conveniencia)
    // =========================================================================

    /**
     * Obtiene el lambda para un material. Delega a MaterialsManager.
     */
    getLambdaForMaterial(materialName, fc) {
        return this.materialsManager.getLambda(materialName, fc);
    }

    /**
     * Re-ejecuta el análisis. Delega a UploadManager.
     */
    async reanalyze() {
        return this.uploadManager.reanalyze();
    }

    // =========================================================================
    // Report Modal
    // =========================================================================

    openReportModal() {
        const totalPiers = this.results?.length || 0;
        if (totalPiers === 0) {
            this.showNotification('No hay resultados de análisis para generar informe.', 'error');
            return;
        }
        this.reportModal.open(totalPiers);
    }

    // =========================================================================
    // Métodos Compartidos (usados por módulos)
    // =========================================================================

    /**
     * Muestra una notificación temporal al usuario.
     */
    showNotification(message, type = 'info') {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            document.body.appendChild(container);
        }

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        container.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Actualiza estadísticas de un tipo de elemento (genérico).
     */
    updateElementStats(results, prefix) {
        const statTotal = document.getElementById(`${prefix}-stat-total`);
        if (!statTotal) return;

        const stats = calculateElementStats(results);
        statTotal.textContent = stats.total;
        document.getElementById(`${prefix}-stat-ok`).textContent = stats.ok;
        document.getElementById(`${prefix}-stat-fail`).textContent = stats.fail;
        document.getElementById(`${prefix}-stat-rate`).textContent = `${stats.rate}%`;
    }

    /**
     * Renderiza una tabla de elementos genérica.
     */
    renderElementTable(results, tbody, statsPrefix, colspan, emptyMsg, logPrefix) {
        if (!tbody) {
            console.warn(`[${logPrefix}] No se encontró tbody`);
            return;
        }

        tbody.innerHTML = '';

        if (!results || results.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${colspan}" class="no-data-msg">${emptyMsg}</td></tr>`;
            this.updateElementStats([], statsPrefix);
            return;
        }

        const rowFactory = new RowFactory(this.resultsTable);
        results.forEach(result => {
            const elementKey = result.key || `${result.story}_${result.label}`;
            const row = rowFactory.createRow(result, elementKey);
            if (row) {
                tbody.appendChild(row);
            }
        });

        this.updateElementStats(results, statsPrefix);
        console.log(`[${logPrefix}] Renderizados ${results.length} elementos`);
    }

    // =========================================================================
    // Drop Beams (Vigas Capitel)
    // =========================================================================

    renderDropBeamsTable() {
        this.renderElementTable(
            this.dropBeamResults,
            this.elements.dropBeamsTable,
            'drop-beam', 12, 'No hay vigas capitel para analizar', 'DropBeams'
        );
    }

    clearDropBeamsTable() {
        if (this.elements.dropBeamsTable) {
            this.elements.dropBeamsTable.innerHTML = '';
        }
        this.updateElementStats([], 'drop-beam');
    }
}

// Instancia global
const structuralPage = new StructuralPage();
