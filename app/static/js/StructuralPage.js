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
        this.results = [];
        this.columnResults = [];
        this.beamResults = [];
        this.slabResults = [];
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
        this.beamsTable = null;
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

            // Paginas principales
            configPage: document.getElementById('config-page'),
            wallsPage: document.getElementById('walls-page'),
            beamsPage: document.getElementById('beams-page'),
            slabsPage: document.getElementById('slabs-page'),

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
        this.beamsTable = new BeamsTable(this);
        this.slabsTable = new SlabsTable(this);
        this.slabsTable.bindFilterEvents();
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
        setupModalClose(modal, () => this.closePierDetailsModal());
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
        this.elements.stdBeamWidth?.addEventListener('change', () => this.onStandardBeamChange());
        this.elements.stdBeamHeight?.addEventListener('change', () => this.onStandardBeamChange());
        this.elements.stdBeamLn?.addEventListener('change', () => this.onStandardBeamChange());
        this.elements.stdBeamNbars?.addEventListener('change', () => this.onStandardBeamChange());
        this.elements.stdBeamDiam?.addEventListener('change', () => this.onStandardBeamChange());

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
        this.results = [];
        this.columnResults = [];
        this.beamResults = [];
        this.slabResults = [];
        this.filters = { grilla: '', story: '', axis: '', status: '', elementType: '' };
        this.uniqueGrillas = [];
        this.uniqueStories = [];
        this.uniqueAxes = [];
        this.materials = {};
        this.resultsTable.reset();
        this.beamsTable.clear();
        this.slabsTable.clear();
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
            this.uniqueGrillas = uploadData.summary.grillas || [];
            this.uniqueStories = uploadData.summary.stories || [];
            this.uniqueAxes = uploadData.summary.axes || [];

            // Debug: log counts
            console.log('[Upload] Parsed data:', {
                piers: this.piersData.length,
                columns: this.columnsData.length,
                beams: this.beamsData.length,
                slabs: this.slabsData.length
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

                        this.resultsTable.populateFilters();
                        this.resultsTable.render(data);
                        this.beamsTable.renderTable(this.beamResults);
                        this.slabsTable.renderTable(this.slabResults);
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
    // Pier Details Modal
    // =========================================================================

    async showPierDetails(pierKey, pierLabel) {
        const { pierDetailsModal, pierDetailsTitle, pierDetailsLoading } = this.elements;

        if (!pierDetailsModal) return;

        // Guardar referencia del pier actual para el selector de combos
        this._currentPierKey = pierKey;
        this._currentPierLabel = pierLabel;

        // Abrir modal y mostrar loading
        pierDetailsModal.classList.add('active');
        pierDetailsTitle.textContent = pierLabel;
        pierDetailsLoading.classList.add('active');

        try {
            const data = await structuralAPI.getPierCapacities(this.sessionId, pierKey);

            if (data.success) {
                this._currentPierData = data;
                this.updatePierDetailsContent(data);
                this.populateComboSelector(data.combinations_list || []);

                // Cargar datos de la primera combinación (la más crítica)
                // para asegurar que las tablas muestren la misma combinación
                const combinations = data.combinations_list || [];
                if (combinations.length > 0) {
                    const firstComboIndex = combinations[0].index;
                    const comboDetails = await structuralAPI.getCombinationDetails(
                        this.sessionId,
                        pierKey,
                        firstComboIndex
                    );
                    if (comboDetails.success) {
                        this.updateDesignTablesForCombo(comboDetails);
                    }
                }
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

    /**
     * Llena el selector de combinaciones.
     */
    populateComboSelector(combinations) {
        const selector = document.getElementById('pier-combo-selector');
        const badge = document.getElementById('combo-critical-badge');

        if (!selector) return;

        // Limpiar opciones anteriores
        selector.innerHTML = '';

        if (!combinations || combinations.length === 0) {
            selector.innerHTML = '<option value="-1">Sin combinaciones</option>';
            badge?.classList.add('hidden');
            return;
        }

        // Agregar opción por defecto (crítica)
        const criticalCombo = combinations.find(c => c.is_critical) || combinations[0];
        selector.innerHTML = combinations.map((combo, idx) => {
            const isCritical = combo.is_critical_flexure || combo.is_critical_shear;
            const criticalMark = isCritical ? ' ★' : '';
            const criticalType = combo.is_critical_flexure && combo.is_critical_shear
                ? ' (crit. flexión y corte)'
                : combo.is_critical_flexure
                    ? ' (crit. flexión)'
                    : combo.is_critical_shear
                        ? ' (crit. corte)'
                        : '';
            return `<option value="${combo.index}" ${idx === 0 ? 'selected' : ''}>
                ${combo.full_name}${criticalMark}${criticalType}
            </option>`;
        }).join('');

        // Mostrar badge si la primera es crítica
        if (criticalCombo && (criticalCombo.is_critical_flexure || criticalCombo.is_critical_shear)) {
            badge?.classList.remove('hidden');
        } else {
            badge?.classList.add('hidden');
        }

        // Actualizar fuerzas mostradas
        this.updateComboForcesDisplay(criticalCombo);

        // Agregar evento change
        selector.onchange = () => this.onComboSelectorChange();
    }

    /**
     * Actualiza el display de fuerzas de la combinación seleccionada.
     */
    updateComboForcesDisplay(combo) {
        if (!combo) return;

        document.getElementById('combo-P').textContent = combo.P ?? '-';
        document.getElementById('combo-M2').textContent = combo.M2 ?? '-';
        document.getElementById('combo-M3').textContent = combo.M3 ?? '-';
        document.getElementById('combo-V2').textContent = combo.V2 ?? '-';
        document.getElementById('combo-V3').textContent = combo.V3 ?? '-';
    }

    /**
     * Maneja el cambio en el selector de combinaciones.
     */
    async onComboSelectorChange() {
        const selector = document.getElementById('pier-combo-selector');
        const badge = document.getElementById('combo-critical-badge');
        const comboIndex = parseInt(selector.value);

        if (comboIndex < 0 || !this._currentPierKey) return;

        // Buscar la combinación en la lista
        const combinations = this._currentPierData?.combinations_list || [];
        const selectedCombo = combinations.find(c => c.index === comboIndex);

        // Actualizar fuerzas
        this.updateComboForcesDisplay(selectedCombo);

        // Actualizar badge
        if (selectedCombo && (selectedCombo.is_critical_flexure || selectedCombo.is_critical_shear)) {
            badge?.classList.remove('hidden');
        } else {
            badge?.classList.add('hidden');
        }

        // Obtener detalles de la combinación seleccionada
        try {
            const loadingEl = document.getElementById('pier-details-loading');
            loadingEl?.classList.add('active');

            const data = await structuralAPI.getCombinationDetails(
                this.sessionId,
                this._currentPierKey,
                comboIndex
            );

            if (data.success) {
                this.updateDesignTablesForCombo(data);
            } else {
                console.error('Error:', data.error);
            }
        } catch (error) {
            console.error('Error getting combo details:', error);
        } finally {
            document.getElementById('pier-details-loading')?.classList.remove('active');
        }
    }

    /**
     * Actualiza solo las tablas de diseño (flexión, corte, boundary) para una combinación.
     */
    updateDesignTablesForCombo(data) {
        const { flexure, shear, boundary, combo_name, combo_location } = data;

        // Actualizar Flexural Design
        const flexureBody = document.getElementById('det-flexure-body');
        if (flexure) {
            flexureBody.innerHTML = `
                <tr>
                    <td>${flexure.location}</td>
                    <td class="${this._getDcrClass(flexure.dcr)}">${flexure.dcr}</td>
                    <td class="combo-cell">${combo_name}</td>
                    <td>${flexure.Pu_tonf}</td>
                    <td>${flexure.Mu2_tonf_m}</td>
                    <td>${flexure.Mu3_tonf_m}</td>
                    <td>${flexure.phi_Mn_tonf_m}</td>
                    <td>${flexure.c_mm}</td>
                </tr>
            `;
        }

        // Actualizar Shear Design
        const shearBody = document.getElementById('det-shear-body');
        if (shear && shear.rows) {
            shearBody.innerHTML = shear.rows.map(row => `
                <tr>
                    <td>${row.direction}</td>
                    <td class="${this._getDcrClass(row.dcr)}">${row.dcr}</td>
                    <td class="combo-cell">${combo_name}</td>
                    <td>${row.Pu_tonf}</td>
                    <td>${row.Mu_tonf_m}</td>
                    <td>${row.Vu_tonf}</td>
                    <td>${row.phi_Vc_tonf}</td>
                    <td>${row.phi_Vn_tonf}</td>
                </tr>
            `).join('');
        }

        // Actualizar Boundary Element Check
        const boundaryBody = document.getElementById('det-boundary-body');
        if (boundary && boundary.rows) {
            boundaryBody.innerHTML = boundary.rows.map(row => `
                <tr>
                    <td>${row.location}</td>
                    <td class="combo-cell">${combo_name}</td>
                    <td>${row.Pu_tonf}</td>
                    <td>${row.Mu_tonf_m}</td>
                    <td>${row.sigma_comp_MPa}</td>
                    <td>${row.sigma_limit_MPa}</td>
                    <td>${row.c_mm}</td>
                    <td class="${row.required === 'Yes' ? 'status-fail' : 'status-ok'}">${row.required}</td>
                </tr>
            `).join('');
        }
    }

    updatePierDetailsContent(data) {
        const { pier_info, reinforcement, slenderness, capacities,
                flexure_design, shear_design, boundary_check } = data;

        // Sección 1: Pier Details
        document.getElementById('det-story').textContent = pier_info.story;
        document.getElementById('det-pier').textContent = pier_info.label;
        document.getElementById('det-length').textContent = pier_info.width_m;
        document.getElementById('det-thickness').textContent = pier_info.thickness_m;
        document.getElementById('det-height').textContent = pier_info.height_m;
        document.getElementById('det-ag').textContent = pier_info.Ag_m2 ||
            (pier_info.width_m * pier_info.thickness_m).toFixed(4);

        // Sección 2: Material Properties
        document.getElementById('det-fc').textContent = pier_info.fc_MPa;
        document.getElementById('det-fy').textContent = pier_info.fy_MPa;
        document.getElementById('det-lambda').textContent = pier_info.lambda || '1.0';

        // Sección 4: Reinforcement
        document.getElementById('det-reinf-desc').textContent = reinforcement.description;
        document.getElementById('det-as-vertical').textContent = reinforcement.As_vertical_mm2;
        document.getElementById('det-as-edge').textContent = reinforcement.As_edge_mm2;
        document.getElementById('det-as-total').textContent = reinforcement.As_flexure_total_mm2;

        // Mostrar cuantías con estado (OK o warning)
        const rhoVEl = document.getElementById('det-rho-actual');
        const rhoVValue = reinforcement.rho_vertical?.toFixed(5) || '—';
        if (reinforcement.rho_v_ok === false) {
            rhoVEl.innerHTML = `<span class="warning-text">${rhoVValue}</span>`;
        } else {
            rhoVEl.textContent = rhoVValue;
        }

        // Mostrar advertencias de cuantía mínima si existen
        const warningsContainer = document.getElementById('det-reinf-warnings');
        if (warningsContainer) {
            if (reinforcement.warnings && reinforcement.warnings.length > 0) {
                warningsContainer.innerHTML = reinforcement.warnings.map(w =>
                    `<div class="warning-message">${w}</div>`
                ).join('');
                warningsContainer.style.display = 'block';
            } else {
                warningsContainer.innerHTML = '';
                warningsContainer.style.display = 'none';
            }
        }

        // Sección 5: Flexural Design
        const flexureBody = document.getElementById('det-flexure-body');
        if (flexure_design && flexure_design.has_data && flexure_design.rows.length > 0) {
            flexureBody.innerHTML = flexure_design.rows.map(row => `
                <tr>
                    <td>${row.location}</td>
                    <td class="${this._getDcrClass(row.dcr)}">${row.dcr}</td>
                    <td class="combo-cell">${row.combo}</td>
                    <td>${row.Pu_tonf}</td>
                    <td>${row.Mu2_tonf_m}</td>
                    <td>${row.Mu3_tonf_m}</td>
                    <td>${row.phi_Mn_tonf_m}</td>
                    <td>${row.c_mm}</td>
                </tr>
            `).join('');
        } else {
            flexureBody.innerHTML = '<tr><td colspan="8" class="no-data">Sin datos de carga</td></tr>';
        }

        // Sección 6: Shear Design
        const shearBody = document.getElementById('det-shear-body');
        if (shear_design && shear_design.has_data && shear_design.rows.length > 0) {
            shearBody.innerHTML = shear_design.rows.map(row => `
                <tr>
                    <td>${row.direction}</td>
                    <td class="${this._getDcrClass(row.dcr)}">${row.dcr}</td>
                    <td class="combo-cell">${row.combo}</td>
                    <td>${row.Pu_tonf}</td>
                    <td>${row.Mu_tonf_m}</td>
                    <td>${row.Vu_tonf}</td>
                    <td>${row.phi_Vc_tonf}</td>
                    <td>${row.phi_Vn_tonf}</td>
                </tr>
            `).join('');
        } else {
            shearBody.innerHTML = '<tr><td colspan="8" class="no-data">Sin datos de carga</td></tr>';
        }

        // Sección 7: Boundary Element Check
        const boundaryBody = document.getElementById('det-boundary-body');
        if (boundary_check && boundary_check.has_data && boundary_check.rows.length > 0) {
            boundaryBody.innerHTML = boundary_check.rows.map(row => `
                <tr>
                    <td>${row.location}</td>
                    <td class="combo-cell">${row.combo}</td>
                    <td>${row.Pu_tonf}</td>
                    <td>${row.Mu_tonf_m}</td>
                    <td>${row.sigma_comp_MPa}</td>
                    <td>${row.sigma_limit_MPa}</td>
                    <td>${row.c_mm}</td>
                    <td class="${row.required === 'Yes' ? 'status-fail' : 'status-ok'}">${row.required}</td>
                </tr>
            `).join('');
        } else {
            boundaryBody.innerHTML = '<tr><td colspan="8" class="no-data">Sin datos de carga</td></tr>';
        }

        // Sección 8: Pure Capacities
        if (slenderness && slenderness.is_slender) {
            document.getElementById('det-phi-pn').innerHTML =
                `<span class="strikethrough">${capacities.phi_Pn_max_tonf}</span>` +
                ` → ${capacities.phi_Pn_reduced_tonf}`;
        } else {
            document.getElementById('det-phi-pn').textContent = capacities.phi_Pn_max_tonf;
        }
        document.getElementById('det-phi-mn3').textContent = capacities.phi_Mn3_tonf_m;
        document.getElementById('det-phi-mn2').textContent = capacities.phi_Mn2_tonf_m;
        document.getElementById('det-phi-vn2').textContent = capacities.phi_Vn2_tonf;
        document.getElementById('det-phi-vn3').textContent = capacities.phi_Vn3_tonf;
    }

    /**
     * Retorna la clase CSS para colorear el D/C (Demand/Capacity) según su valor.
     * D/C <= 1.0 es OK, D/C > 1.0 significa que falla.
     */
    _getDcrClass(dcr) {
        if (dcr === '<0.01' || (typeof dcr === 'number' && dcr <= 1.0)) {
            return 'status-ok';
        }
        return 'status-fail';
    }

    /**
     * Retorna la clase CSS para colorear el SF según su valor.
     */
    _getSfClass(sf) {
        if (sf === '>100' || (typeof sf === 'number' && sf >= 1)) {
            return 'status-ok';
        }
        return 'status-fail';
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
        setupModalClose(modal, () => this.closeSectionModal());
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

    // =========================================================================
    // Viga Estándar
    // =========================================================================

    /**
     * Maneja cambios en la viga estándar.
     */
    onStandardBeamChange() {
        const beam = {
            width: parseInt(this.elements.stdBeamWidth?.value) || 200,
            height: parseInt(this.elements.stdBeamHeight?.value) || 500,
            ln: parseInt(this.elements.stdBeamLn?.value) || 1500,
            nbars: parseInt(this.elements.stdBeamNbars?.value) || 2,
            diam: parseInt(this.elements.stdBeamDiam?.value) || 12
        };

        // Actualizar en ResultsTable (propaga a celdas bloqueadas y guarda en backend)
        this.resultsTable.updateStandardBeam(beam);
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
