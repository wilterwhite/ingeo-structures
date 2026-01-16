// app/static/js/tables/ResultsTable.js
/**
 * Módulo para manejo de la tabla de resultados.
 * Usa RowFactory para crear filas de piers y columnas.
 * Extiende FilterableTable para reutilizar lógica de filtrado y estadísticas.
 */

class ResultsTable extends FilterableTable {
    constructor(page) {
        super(page);
        this.rowFactory = new RowFactory(this);
        this.plotsCache = {};

        // Propiedades para vigas personalizadas por pier
        this.customBeamPiers = new Set();
        this.pierBeamConfigs = {};

        // Managers especializados
        this.combinationsManager = new CombinationsManager(this);
        this.couplingBeamManager = new CouplingBeamManager(this);
        this.editManager = new ElementEditManager(this);

        // Filtros de columna tipo Excel
        this.columnFilters = new ColumnFilters(this);
    }

    // =========================================================================
    // Propiedades para CombinationsManager (delegación)
    // =========================================================================

    /** @returns {Set} Piers expandidos - delegado a CombinationsManager */
    get expandedPiers() { return this.combinationsManager.expandedPiers; }

    /** @returns {Object} Cache de combinaciones - delegado a CombinationsManager */
    get combinationsCache() { return this.combinationsManager.combinationsCache; }

    // =========================================================================
    // Métodos requeridos por FilterableTable
    // =========================================================================

    /**
     * Verifica si un resultado cumple con los filtros.
     * Delegado a ColumnFilters.
     * @param {Object} result
     * @returns {boolean}
     */
    matchesFilters(result) {
        return this.columnFilters.matchesFilters(result);
    }

    // =========================================================================
    // Acceso a datos
    // =========================================================================

    get elements() { return this.page.elements; }
    get filters() { return this.page.filters; }
    set filters(value) { Object.assign(this.page.filters, value); }
    get piersData() { return this.page.piersData; }
    get sessionId() { return this.page.sessionId; }

    // =========================================================================
    // Filtros (delegados a ColumnFilters)
    // =========================================================================

    /**
     * Inicializa filtros (llamado después del render inicial).
     * Los filtros de columna se manejan en ColumnFilters.
     */
    populateFilters() {
        // Método vacío mantenido por compatibilidad - llamado desde UploadManager
    }

    /**
     * Obtiene resultados filtrados.
     * @returns {Array}
     */
    getFilteredResults() {
        return this.filteredResults.length > 0
            ? this.filteredResults
            : this.page.results.filter(r => this.matchesFilters(r));
    }

    /**
     * Actualiza estadísticas en el DOM.
     */
    updateStats() {
        const stats = this.calculateStats();
        stats.pass_rate = stats.rate;
        this.updateStatistics(stats);
    }


    // =========================================================================
    // Renderizado Principal
    // =========================================================================

    render(data) {
        this.updateStatistics(data.statistics);

        // Sincronizar asignaciones de vigas de acople desde los resultados del backend
        this.couplingBeamManager.syncFromResults(data.results);

        this.renderTable(data.results);

        // Inicializar filtros de columna después de renderizar
        this.columnFilters.init();

        // Log del estado del frontend (para debugging remoto)
        this.page.logState();
    }

    updateStatistics(stats) {
        if (!stats) return;
        const { statTotal, statOk, statFail, statRate } = this.elements;
        // Backend usa nomenclatura unificada: total, ok, fail, pass_rate
        if (statTotal) statTotal.textContent = stats.total ?? 0;
        if (statOk) statOk.textContent = stats.ok ?? 0;
        if (statFail) statFail.textContent = stats.fail ?? 0;
        if (statRate) statRate.textContent = (stats.pass_rate ?? 0).toFixed(1) + '%';
    }

    // =========================================================================
    // Tabla de Resultados
    // =========================================================================

    renderTable(results) {
        const { resultsTable } = this.elements;
        if (!resultsTable) return;

        resultsTable.innerHTML = '';
        this.plotsCache = {};

        results.forEach(result => {
            const elementKey = result.key || `${result.story}_${result.pier_label}`;
            if (result.pm_plot) this.plotsCache[elementKey] = result.pm_plot;

            const row = this.rowFactory.createRow(result, elementKey);
            resultsTable.appendChild(row);

            // Solo agregar combo rows para piers (columnas no tienen por ahora)
            if (result.element_type !== 'column') {
                this.appendComboRows(resultsTable, elementKey);
                if (this.expandedPiers.has(elementKey) && !this.combinationsCache[elementKey]) {
                    this.loadCombinations(elementKey);
                }
            }
        });
    }

    // =========================================================================
    // Vigas de Acople - Delegado a CouplingBeamManager
    // =========================================================================

    /** Crea celda de viga - delegado a CouplingBeamManager */
    createVigaCell(pierKey, side) {
        return this.couplingBeamManager.createVigaCell(pierKey, side);
    }

    /** Obtiene asignación de viga - delegado a CouplingBeamManager */
    getAssignedBeamKey(pierKey, side) {
        return this.couplingBeamManager.getAssignedBeamKey(pierKey, side);
    }

    /** Acceso a asignaciones para compatibilidad */
    get pierBeamAssignments() {
        return this.couplingBeamManager.getAssignments();
    }

    getBeamConfig(pierKey, side) {
        if (this.customBeamPiers?.has(pierKey) && this.pierBeamConfigs?.[pierKey]?.[side]) {
            return this.pierBeamConfigs[pierKey][side];
        }
        return this.couplingBeamManager.standardBeam;
    }

    togglePierBeamLock(pierKey) {
        if (this.customBeamPiers.has(pierKey)) {
            this.customBeamPiers.delete(pierKey);
            delete this.pierBeamConfigs[pierKey];
        } else {
            this.customBeamPiers.add(pierKey);
            const standardBeam = this.couplingBeamManager.standardBeam;
            this.pierBeamConfigs[pierKey] = {
                izq: { ...standardBeam },
                der: { ...standardBeam }
            };
        }
        this.updatePierBeamCells(pierKey);
    }

    updatePierBeamCells(pierKey) {
        const row = document.querySelector(`tr[data-pier-key="${pierKey}"]`);
        if (!row) return;

        const cells = row.querySelectorAll('.viga-cell');
        if (cells.length >= 2) {
            const newIzq = this.createVigaCell(pierKey, 'izq');
            const newDer = this.createVigaCell(pierKey, 'der');
            cells[0].replaceWith(newIzq);
            cells[1].replaceWith(newDer);
        }
    }

    onBeamChange(pierKey, side, saveToServer = true) {
        const row = document.querySelector(`tr[data-pier-key="${pierKey}"]`);
        if (!row) return;

        const cell = row.querySelector(`.viga-cell[data-side="${side}"]`);
        if (!cell) return;

        const width = parseInt(cell.querySelector(`.edit-viga-width-${side}`)?.value) || 0;
        const height = parseInt(cell.querySelector(`.edit-viga-height-${side}`)?.value) || 0;
        const ln = parseInt(cell.querySelector(`.edit-viga-ln-${side}`)?.value) || 1500;
        const nbars = parseInt(cell.querySelector(`.edit-viga-nbars-${side}`)?.value) || 2;
        const diam = parseInt(cell.querySelector(`.edit-viga-diam-${side}`)?.value) || 12;

        if (!this.pierBeamConfigs[pierKey]) {
            const standardBeam = this.couplingBeamManager.standardBeam;
            this.pierBeamConfigs[pierKey] = { izq: { ...standardBeam }, der: { ...standardBeam } };
        }
        this.pierBeamConfigs[pierKey][side] = { width, height, ln, nbars, diam };

        // Solo guardar en servidor si se solicita (botón recalcular)
        if (saveToServer) {
            this.savePierBeamConfig(pierKey);
        }
    }

    async savePierBeamConfig(pierKey) {
        // Usar la nueva asignación de vigas del catálogo
        const assignment = this.pierBeamAssignments[pierKey];
        const beamLeft = assignment?.izq || 'generic';
        const beamRight = assignment?.der || 'generic';

        const row = this.elements.resultsTable?.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
        if (row) row.style.opacity = '0.5';

        try {
            // Usar el nuevo endpoint de asignación de vigas
            const response = await structuralAPI.assignCouplingBeam(
                this.sessionId,
                pierKey,
                beamLeft,
                beamRight
            );

            if (response.success && response.result) {
                // Actualizar resultado en page.results
                const idx = this.page.results.findIndex(r => r.key === pierKey);
                if (idx >= 0) {
                    this.page.results[idx] = response.result;
                }
                // Limpiar cache y re-renderizar
                delete this.combinationsCache[pierKey];
                const filtered = this.getFilteredResults();
                this.renderTable(filtered);
                this.updateStats();  // Usar método heredado
            }
        } catch (error) {
            console.error('Error guardando config de viga:', error);
        } finally {
            if (row) row.style.opacity = '1';
        }
    }

    updateStandardBeam(beam) {
        this.couplingBeamManager.standardBeam = { ...beam };
        document.querySelectorAll('.viga-cell.locked').forEach(cell => {
            const pierKey = cell.dataset.pierKey;
            const side = cell.dataset.side;
            const newCell = this.createVigaCell(pierKey, side);
            cell.replaceWith(newCell);
        });
        this.saveStandardBeam();
    }

    async saveStandardBeam() {
        try {
            await structuralAPI.setDefaultBeam(this.sessionId, this.couplingBeamManager.standardBeam);
        } catch (error) {
            console.error('Error guardando viga estándar:', error);
        }
    }

    // =========================================================================
    // Combinaciones - Delegado a CombinationsManager
    // =========================================================================

    appendComboRows(container, pierKey) {
        this.combinationsManager.appendComboRows(container, pierKey);
    }

    async toggleExpand(pierKey) {
        await this.combinationsManager.toggleExpand(pierKey);
    }

    async loadCombinations(pierKey) {
        await this.combinationsManager.loadCombinations(pierKey);
    }

    async toggleAllExpand() {
        return await this.combinationsManager.toggleAllExpand();
    }

    collapseAll() {
        this.combinationsManager.collapseAll();
    }

    async expandAll(pierKeys) {
        await this.combinationsManager.expandAll(pierKeys);
    }

    // =========================================================================
    // Edición y Propuestas
    // =========================================================================

    updateStirrupsState(row) {
        const bordeCell = row.querySelector('.borde-cell');
        if (!bordeCell) return;

        const nEdge = parseInt(bordeCell.querySelector('.edit-n-edge')?.value) || 2;
        const shouldDisable = nEdge <= 2;

        const stirrupD = bordeCell.querySelector('.edit-stirrup-d');
        const stirrupS = bordeCell.querySelector('.edit-stirrup-s');
        if (stirrupD) stirrupD.disabled = shouldDisable;
        if (stirrupS) stirrupS.disabled = shouldDisable;
    }

    getProposedConfig(proposal) {
        if (!proposal || !proposal.proposed_config) return null;
        const config = proposal.proposed_config;
        return {
            n_edge_bars: config.n_edge_bars,
            diameter_edge: config.diameter_edge,
            n_meshes: config.n_meshes,
            diameter_v: config.diameter_v,
            spacing_v: config.spacing_v,
            diameter_h: config.diameter_h,
            spacing_h: config.spacing_h,
            stirrup_diameter: config.stirrup_diameter,
            stirrup_spacing: config.stirrup_spacing,
            n_stirrup_legs: config.n_stirrup_legs,
            thickness: config.thickness
        };
    }

    async applyProposal(pierKey, proposal) {
        if (!proposal?.has_proposal) return;
        const pier = this.piersData.find(p => p.key === pierKey);
        if (!pier) return;

        // Usar proposed_config del backend (no parsear description)
        const config = this.getProposedConfig(proposal);
        if (!config) return;

        // Aplicar cambios usando el editManager
        const changes = {};
        if (config.n_edge_bars) changes.n_edge_bars = config.n_edge_bars;
        if (config.diameter_edge) changes.diameter_edge = config.diameter_edge;
        if (config.n_meshes) changes.n_meshes = config.n_meshes;
        if (config.diameter_v) {
            changes.diameter_v = config.diameter_v;
            changes.diameter_h = config.diameter_h || config.diameter_v;
        }
        if (config.spacing_v) {
            changes.spacing_v = config.spacing_v;
            changes.spacing_h = config.spacing_h || config.spacing_v;
        }
        if (config.thickness) changes.thickness = config.thickness;
        if (config.stirrup_diameter) changes.stirrup_diameter = config.stirrup_diameter;
        if (config.stirrup_spacing) changes.stirrup_spacing = config.stirrup_spacing;
        if (config.n_stirrup_legs) changes.n_stirrup_legs = config.n_stirrup_legs;

        this.editManager.onReinforcementChange(pierKey, 'pier', changes);
    }

    reset() {
        this.combinationsManager.clear();
        this.plotsCache = {};
        this.customBeamPiers.clear();
        this.pierBeamConfigs = {};
        this.couplingBeamManager.clearAssignments();
        this.editManager.reset();
    }

    /**
     * Actualiza los dropdowns de vigas cuando se agregan vigas custom.
     */
    refreshBeamSelectors() {
        // Actualizar todos los dropdowns de vigas en la tabla
        const vigaCells = document.querySelectorAll('.viga-cell');
        vigaCells.forEach(cell => {
            const pierKey = cell.dataset.pierKey;
            const side = cell.dataset.side;
            if (!pierKey || !side) return;

            const select = cell.querySelector('.beam-selector');
            if (select) {
                const currentValue = select.value;
                select.innerHTML = this.buildBeamOptions(currentValue, pierKey, side);
            }
        });
    }
}
