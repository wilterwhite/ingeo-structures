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

        // Managers especializados
        this.combinationsManager = new CombinationsManager(this);
        this.couplingBeamManager = new CouplingBeamManager(this);
        this.editManager = new PierEditManager(this);
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
     * Obtiene valores de filtros desde el DOM.
     * @returns {Object}
     */
    getFilterValues() {
        return {
            grilla: this.elements.grillaFilter?.value || '',
            story: this.elements.storyFilter?.value || '',
            axis: this.elements.axisFilter?.value || '',
            status: this.elements.statusFilter?.value || '',
            elementType: this.elements.elementTypeFilter?.value || ''
        };
    }

    /**
     * Verifica si un resultado cumple con los filtros.
     * @param {Object} result
     * @returns {boolean}
     */
    matchesFilters(result) {
        const filters = this.filters;

        if (filters.grilla) {
            const parts = result.pier_label.split('-');
            const grilla = parts.length > 0 ? parts[0] : '';
            if (grilla !== filters.grilla) return false;
        }
        if (filters.story && result.story !== filters.story) return false;
        if (filters.axis) {
            const parts = result.pier_label.split('-');
            const axis = parts.length > 1 ? parts[1] : '';
            if (axis !== filters.axis) return false;
        }
        if (filters.elementType) {
            const elementType = result.element_type || 'pier';
            if (elementType !== filters.elementType) return false;
        }
        // Filtrar por estado (usa helper de FilterableTable)
        return this.matchesStatusFilter(result, filters.status);
    }

    // =========================================================================
    // Acceso a datos
    // =========================================================================

    get elements() { return this.page.elements; }
    get filters() { return this.page.filters; }
    get piersData() { return this.page.piersData; }
    get sessionId() { return this.page.sessionId; }

    // =========================================================================
    // Filtros
    // =========================================================================

    populateFilters() {
        const { grillaFilter, storyFilter } = this.elements;

        if (grillaFilter) {
            grillaFilter.innerHTML = '<option value="">Todas</option>';
            this.page.uniqueGrillas.forEach(grilla => {
                const option = document.createElement('option');
                option.value = grilla;
                option.textContent = grilla;
                grillaFilter.appendChild(option);
            });
        }

        if (storyFilter) {
            storyFilter.innerHTML = '<option value="">Todos</option>';
            this.page.uniqueStories.forEach(story => {
                const option = document.createElement('option');
                option.value = story;
                option.textContent = story;
                storyFilter.appendChild(option);
            });
        }

        this.updateAxisFilter();
    }

    updateAxisFilter() {
        const { grillaFilter, axisFilter } = this.elements;
        if (!axisFilter) return;

        const selectedGrilla = grillaFilter?.value || '';
        const currentAxis = axisFilter.value;

        let axes;
        if (selectedGrilla) {
            const axesSet = new Set();
            this.page.results.forEach(result => {
                const parts = result.pier_label.split('-');
                const grilla = parts[0] || '';
                const axis = parts[1] || '';
                if (grilla === selectedGrilla && axis) axesSet.add(axis);
            });
            axes = [...axesSet].sort();
        } else {
            axes = this.page.uniqueAxes;
        }

        axisFilter.innerHTML = '<option value="">Todos</option>';
        axes.forEach(axis => {
            const option = document.createElement('option');
            option.value = axis;
            option.textContent = axis;
            axisFilter.appendChild(option);
        });

        if (axes.includes(currentAxis)) axisFilter.value = currentAxis;
    }

    onGrillaChange() {
        this.updateAxisFilter();
        this.applyFilters();
    }

    /**
     * Aplica filtros y actualiza la tabla.
     * Sobrescribe FilterableTable.applyFilters() para agregar lógica específica.
     */
    applyFilters() {
        // Obtener filtros y aplicar a page.filters para compatibilidad
        this.filters = this.getFilterValues();
        Object.assign(this.page.filters, this.filters);

        // Filtrar resultados usando método heredado matchesFilters
        this.filteredResults = this.page.results.filter(r => this.matchesFilters(r));

        // Renderizar y actualizar stats
        this.renderTable(this.filteredResults);
        this.updateStats();
        this.updateSummaryPlot();
    }

    /**
     * Obtiene resultados filtrados (alias para compatibilidad).
     * @returns {Array}
     */
    getFilteredResults() {
        return this.filteredResults.length > 0
            ? this.filteredResults
            : this.page.results.filter(r => this.matchesFilters(r));
    }

    /**
     * Actualiza estadísticas en el DOM.
     * Implementa método abstracto de FilterableTable.
     */
    updateStats() {
        const stats = this.calculateStats();
        // Convertir rate a pass_rate para compatibilidad
        stats.pass_rate = stats.rate;
        this.updateStatistics(stats);
    }


    // =========================================================================
    // Renderizado Principal
    // =========================================================================

    render(data) {
        this.updateStatistics(data.statistics);
        this.renderSummaryPlot(data.summary_plot);
        this.renderTable(data.results);
    }

    updateStatistics(stats) {
        const { statTotal, statOk, statFail, statRate } = this.elements;
        if (statTotal) statTotal.textContent = stats.total;
        if (statOk) statOk.textContent = stats.ok;
        if (statFail) statFail.textContent = stats.fail;
        if (statRate) statRate.textContent = stats.pass_rate.toFixed(1) + '%';
    }

    renderSummaryPlot(plotBase64) {
        const { summaryPlotContainer } = this.elements;
        if (summaryPlotContainer && plotBase64) {
            summaryPlotContainer.innerHTML = `<img src="data:image/png;base64,${plotBase64}" alt="Resumen">`;
        }
    }

    async updateSummaryPlot() {
        if (!this.sessionId) return;
        try {
            const { summaryPlotContainer } = this.elements;
            if (summaryPlotContainer) summaryPlotContainer.classList.add('loading');

            const data = await structuralAPI.getSummaryPlot({
                session_id: this.sessionId,
                story_filter: this.filters.story,
                axis_filter: this.filters.axis
            });

            if (data.success && data.summary_plot) {
                this.renderSummaryPlot(data.summary_plot);
            } else if (data.count === 0 && summaryPlotContainer) {
                summaryPlotContainer.innerHTML = '<p class="no-data">No hay datos para los filtros seleccionados</p>';
            }
        } catch (error) {
            console.error('Error updating summary plot:', error);
        } finally {
            const { summaryPlotContainer } = this.elements;
            if (summaryPlotContainer) summaryPlotContainer.classList.remove('loading');
        }
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
                this.updateSummaryPlot();
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

        const config = this.parseProposalConfig(proposal);
        // Aplicar cambios usando el editManager
        const changes = {};
        if (config.n_edge_bars) changes.n_edge_bars = config.n_edge_bars;
        if (config.diameter_edge) changes.diameter_edge = config.diameter_edge;
        if (config.n_meshes) changes.n_meshes = config.n_meshes;
        if (config.diameter_v) {
            changes.diameter_v = config.diameter_v;
            changes.diameter_h = config.diameter_v;
        }
        if (config.spacing_v) {
            changes.spacing_v = config.spacing_v;
            changes.spacing_h = config.spacing_v;
        }

        this.editManager.onReinforcementChange(pierKey, changes);
    }

    parseProposalConfig(proposal) {
        const config = {};
        const desc = proposal.description || '';
        const borderMatch = desc.match(/(\d+)φ(\d+)/);
        if (borderMatch) { config.n_edge_bars = parseInt(borderMatch[1]); config.diameter_edge = parseInt(borderMatch[2]); }
        const meshMatch = desc.match(/(\d)M\s*φ(\d+)@(\d+)/);
        if (meshMatch) { config.n_meshes = parseInt(meshMatch[1]); config.diameter_v = parseInt(meshMatch[2]); config.spacing_v = parseInt(meshMatch[3]); }
        return config;
    }

    reset() {
        this.combinationsManager.clear();
        this.plotsCache = {};
        this.customBeamPiers.clear();
        this.pierBeamConfigs = {};
        this.pierBeamAssignments = {};
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
