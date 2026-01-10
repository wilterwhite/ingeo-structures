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

        // Materiales y configuración
        this.materials = {};  // { materialName: { fc, type: 'normal'|'sand_lightweight'|'all_lightweight', lambda } }
        this.currentPage = 'config-page';

        // Elementos DOM
        this.elements = {};

        // Componentes (se inicializan en init())
        this.resultsTable = null;
        // beamsTable eliminado - vigas se renderizan con RowFactory
        this.slabsTable = null;
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
        this.resultsTable = new ResultsTable(this);
        // beamsTable ya no se usa - vigas se renderizan con RowFactory
        this.slabsTable = new SlabsTable(this);
        this.slabsTable.bindFilterEvents();
        this.plotModal = new PlotModal(this);
        this.plotModal.init();
        this.reportModal = new ReportModal(this);
        this.reportModal.init();

        // Módulos extraídos
        this.wallsModule = new WallsModule(this);
        this.beamsModule = new BeamsModule(this);
        this.dropBeamsModule = new DropBeamsModule(this);

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
        this.materials = {};
        this.resultsTable.reset();
        this.beamsModule.clearBeamsTable();
        this.slabsTable.clear();
        this.dropBeamsModule.clearDropBeamsTable();
        this.updateMaterialsTable();
    }

    // =========================================================================
    // Gestión de Materiales
    // =========================================================================

    /**
     * Extrae los materiales únicos de los datos cargados y actualiza la tabla.
     */
    extractMaterials() {
        const materialsMap = {};

        // Extraer de piers
        this.piersData.forEach(pier => {
            const fc = pier.fc || pier.fc_mpa || 28;  // Default 28 MPa
            const matName = pier.material || `C${Math.round(fc)}`;
            if (!materialsMap[matName]) {
                materialsMap[matName] = { fc, count: 0, type: 'normal', lambda: 1.0 };
            }
            materialsMap[matName].count++;
        });

        // Extraer de columnas
        this.columnsData.forEach(col => {
            const fc = col.fc || col.fc_mpa || 28;
            const matName = col.material || `C${Math.round(fc)}`;
            if (!materialsMap[matName]) {
                materialsMap[matName] = { fc, count: 0, type: 'normal', lambda: 1.0 };
            }
            materialsMap[matName].count++;
        });

        // Preservar configuración existente si ya estaba definida
        Object.keys(materialsMap).forEach(name => {
            if (this.materials[name]) {
                materialsMap[name].type = this.materials[name].type;
                materialsMap[name].lambda = this.materials[name].lambda;
            }
        });

        this.materials = materialsMap;
        this.updateMaterialsTable();
    }

    /**
     * Actualiza la tabla de materiales en la página de configuración.
     */
    updateMaterialsTable() {
        const tbody = this.elements.materialsTbody;
        if (!tbody) return;

        const materialNames = Object.keys(this.materials);

        if (materialNames.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="no-data-msg">No hay materiales cargados</td></tr>';
            return;
        }

        tbody.innerHTML = materialNames.map(name => {
            const mat = this.materials[name];
            const fcDisplay = mat.fc ? mat.fc.toFixed(1) : '—';
            return `
                <tr data-material="${name}">
                    <td><strong>${name}</strong></td>
                    <td>${fcDisplay} MPa</td>
                    <td>
                        <select class="material-type-select" data-material="${name}">
                            <option value="normal" ${mat.type === 'normal' ? 'selected' : ''}>Normal</option>
                            <option value="sand_lightweight" ${mat.type === 'sand_lightweight' ? 'selected' : ''}>Arena liviana (λ=0.85)</option>
                            <option value="all_lightweight" ${mat.type === 'all_lightweight' ? 'selected' : ''}>Todo liviano (λ=0.75)</option>
                        </select>
                    </td>
                    <td class="lambda-value">${mat.lambda.toFixed(2)}</td>
                    <td class="element-count">${mat.count} elementos</td>
                </tr>
            `;
        }).join('');

        // Bind eventos para cambios de tipo
        tbody.querySelectorAll('.material-type-select').forEach(select => {
            select.addEventListener('change', (e) => this.onMaterialTypeChange(e));
        });
    }

    /**
     * Maneja el cambio de tipo de concreto para un material.
     */
    onMaterialTypeChange(event) {
        const select = event.target;
        const materialName = select.dataset.material;
        const newType = select.value;

        // Calcular lambda según el tipo
        const lambdaValues = {
            'normal': 1.0,
            'sand_lightweight': 0.85,
            'all_lightweight': 0.75
        };

        this.materials[materialName].type = newType;
        this.materials[materialName].lambda = lambdaValues[newType];

        // Actualizar celda de lambda
        const row = select.closest('tr');
        const lambdaCell = row.querySelector('.lambda-value');
        if (lambdaCell) {
            lambdaCell.textContent = this.materials[materialName].lambda.toFixed(2);
        }

        console.log(`[Config] Material ${materialName} cambiado a ${newType}, λ=${lambdaValues[newType]}`);
    }

    /**
     * Obtiene el lambda para un material específico.
     */
    getLambdaForMaterial(materialName, fc) {
        // Buscar por nombre
        if (this.materials[materialName]) {
            return this.materials[materialName].lambda;
        }
        // Buscar por fc aproximado
        const approxName = `C${Math.round(fc)}`;
        if (this.materials[approxName]) {
            return this.materials[approxName].lambda;
        }
        // Default
        return 1.0;
    }

    updateElementCounts() {
        console.log('[Upload] Elementos cargados:', {
            piers: this.piersData.length,
            columns: this.columnsData.length,
            beams: this.beamsData.length,
            slabs: this.slabsData.length
        });
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
            this.piersData = uploadData.summary.piers_list || [];
            this.columnsData = uploadData.summary.columns_list || [];
            this.beamsData = uploadData.summary.beams_list || [];
            this.slabsData = uploadData.summary.slabs_list || [];
            this.dropBeamsData = uploadData.summary.drop_beams_list || [];
            this.uniqueGrillas = uploadData.summary.grillas || [];
            this.uniqueStories = uploadData.summary.stories || [];
            this.uniqueAxes = uploadData.summary.axes || [];

            // Debug: log counts
            console.log('[Upload] Parsed data:', {
                piers: this.piersData.length,
                columns: this.columnsData.length,
                beams: this.beamsData.length,
                slabs: this.slabsData.length,
                dropBeams: this.dropBeamsData.length
            });

            // Actualizar conteos en la UI
            this.updateElementCounts();

            // Extraer materiales para la página de configuración
            this.extractMaterials();

            // Mostrar progreso
            this.showProgressModal();

            // Análisis con progreso
            await this.runAnalysisWithProgress({
                session_id: this.sessionId,
                pier_updates: [],
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0,
                materials_config: this.materials
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
                        this.columnResults = data.column_results || [];
                        this.beamResults = data.beam_results || [];
                        this.slabResults = data.slab_results || [];
                        this.dropBeamResults = data.drop_beam_results || [];

                        // Log results para debug
                        if (this.columnResults.length > 0) {
                            console.log('[Analysis] Column results:', this.columnResults.length);
                        }
                        if (this.beamResults.length > 0) {
                            console.log('[Analysis] Beam results:', this.beamResults.length);
                        }
                        if (this.slabResults.length > 0) {
                            console.log('[Analysis] Slab results:', this.slabResults.length);
                        }
                        if (this.dropBeamResults.length > 0) {
                            console.log('[Analysis] Drop beam results:', this.dropBeamResults.length);
                        }

                        this.resultsTable.populateFilters();
                        this.resultsTable.render(data);
                        this.beamsModule.renderBeamsTable();
                        this.slabsTable.renderTable(this.slabResults);
                        this.dropBeamsModule.renderDropBeamsTable();
                        this.showSection('results');
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
        this.showProgressModal();
        try {
            await this.runAnalysisWithProgress({
                session_id: this.sessionId,
                pier_updates: [],
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0,
                materials_config: this.materials
            });
        } catch (error) {
            alert('Error: ' + error.message);
        }
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
}

// Instancia global
const structuralPage = new StructuralPage();
