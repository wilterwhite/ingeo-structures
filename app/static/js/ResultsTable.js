// app/structural/static/js/ResultsTable.js
/**
 * Módulo para manejo de la tabla de resultados.
 * Usa RowFactory para crear filas de piers y columnas.
 */

class ResultsTable {
    constructor(page) {
        this.page = page;
        this.rowFactory = new RowFactory(this);
        this.expandedPiers = new Set();
        this.combinationsCache = {};
        this.plotsCache = {};

        // Estado de vigas estándar
        this.standardBeam = { width: 200, height: 500, ln: 1500, nbars: 2, diam: 12 };
        this.customBeamPiers = new Set();
        this.pierBeamConfigs = {};
        this.pendingRecalcPiers = new Set();  // Piers con cambios pendientes de recalcular

        // Crear botón flotante de recalcular
        this.createRecalcButton();
    }

    createRecalcButton() {
        const btn = document.createElement('button');
        btn.id = 'recalc-floating-btn';
        btn.className = 'btn btn-primary floating-recalc-btn hidden';
        btn.innerHTML = '🔄 Recalcular (<span class="pending-count">0</span>)';
        btn.title = 'Recalcular piers con cambios pendientes';
        btn.addEventListener('click', () => this.recalculatePendingPiers());
        document.body.appendChild(btn);
        this.recalcButton = btn;
    }

    updateRecalcButton() {
        const count = this.pendingRecalcPiers.size;
        if (this.recalcButton) {
            this.recalcButton.querySelector('.pending-count').textContent = count;
            this.recalcButton.classList.toggle('hidden', count === 0);
        }
    }

    async recalculatePendingPiers() {
        if (this.pendingRecalcPiers.size === 0) return;

        const piersToRecalc = [...this.pendingRecalcPiers];
        this.pendingRecalcPiers.clear();
        this.updateRecalcButton();

        // Remover clase pending-recalc de todas las filas
        piersToRecalc.forEach(pierKey => {
            const row = document.querySelector(`tr[data-pier-key="${pierKey}"]`);
            if (row) row.classList.remove('pending-recalc');
        });

        // Mostrar loading
        if (this.recalcButton) {
            this.recalcButton.disabled = true;
            this.recalcButton.innerHTML = `⏳ Calculando (${piersToRecalc.length})...`;
        }

        try {
            // Recalcular cada pier secuencialmente
            for (const pierKey of piersToRecalc) {
                await this.savePierBeamConfig(pierKey);
            }
        } finally {
            if (this.recalcButton) {
                this.recalcButton.disabled = false;
                this.recalcButton.innerHTML = '🔄 Recalcular (<span class="pending-count">0</span>)';
            }
        }
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

    applyFilters() {
        this.page.filters.grilla = this.elements.grillaFilter?.value || '';
        this.page.filters.story = this.elements.storyFilter?.value || '';
        this.page.filters.axis = this.elements.axisFilter?.value || '';
        this.page.filters.status = this.elements.statusFilter?.value || '';
        this.page.filters.elementType = this.elements.elementTypeFilter?.value || '';

        const filtered = this.getFilteredResults();
        this.renderTable(filtered);
        this.updateStatistics(this.calculateStatistics(filtered));
        this.updateSummaryPlot();
    }

    getFilteredResults() {
        return this.page.results.filter(result => {
            if (this.filters.grilla) {
                const parts = result.pier_label.split('-');
                const grilla = parts.length > 0 ? parts[0] : '';
                if (grilla !== this.filters.grilla) return false;
            }
            if (this.filters.story && result.story !== this.filters.story) return false;
            if (this.filters.axis) {
                const parts = result.pier_label.split('-');
                const axis = parts.length > 1 ? parts[1] : '';
                if (axis !== this.filters.axis) return false;
            }
            if (this.filters.status) {
                const isOk = result.overall_status === 'OK';
                if (this.filters.status === 'OK' && !isOk) return false;
                if (this.filters.status === 'FAIL' && isOk) return false;
            }
            if (this.filters.elementType) {
                const elementType = result.element_type || 'pier';
                if (elementType !== this.filters.elementType) return false;
            }
            return true;
        });
    }

    calculateStatistics(results) {
        const total = results.length;
        const ok = results.filter(r => r.overall_status === 'OK').length;
        return { total, ok, fail: total - ok, pass_rate: total > 0 ? (ok / total * 100) : 0 };
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
    // Vigas de Acople (para piers)
    // =========================================================================

    createVigaCell(pierKey, side) {
        const isCustom = this.customBeamPiers.has(pierKey);
        const beam = this.getBeamConfig(pierKey, side);

        const td = document.createElement('td');
        td.className = `viga-cell ${isCustom ? 'using-custom' : 'using-default'}`;
        td.dataset.pierKey = pierKey;
        td.dataset.side = side;

        td.innerHTML = `
            <div class="viga-row">
                <select class="edit-viga-width-${side}" title="Ancho (mm)">
                    <option value="0">-</option>
                    ${BEAM_OPTIONS.widths.map(w => `<option value="${w}" ${w === beam.width ? 'selected' : ''}>${w}</option>`).join('')}
                </select>
                <span>×</span>
                <select class="edit-viga-height-${side}" title="Alto (mm)">
                    <option value="0">-</option>
                    ${BEAM_OPTIONS.heights.map(h => `<option value="${h}" ${h === beam.height ? 'selected' : ''}>${h}</option>`).join('')}
                </select>
            </div>
            <div class="viga-row">
                <select class="edit-viga-nbars-${side}" title="Nº barras">
                    ${BEAM_OPTIONS.nBars.map(n => `<option value="${n}" ${n === beam.nbars ? 'selected' : ''}>${n}</option>`).join('')}
                </select>
                <select class="edit-viga-diam-${side}" title="φ barras">
                    ${generateDiameterOptions(DIAMETERS.vigas, beam.diam)}
                </select>
            </div>
            <div class="viga-row">
                <span>L=</span>
                <select class="edit-viga-ln-${side}" title="Largo libre (mm)">
                    ${BEAM_OPTIONS.lengths.map(l => `<option value="${l}" ${l === beam.ln ? 'selected' : ''}>${l}</option>`).join('')}
                </select>
            </div>
        `;

        // Siempre permitir edición - al cambiar, marcar como custom y pendiente de recálculo
        td.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', () => {
                // Marcar como custom inmediatamente (feedback visual)
                if (!this.customBeamPiers.has(pierKey)) {
                    this.customBeamPiers.add(pierKey);
                    this.pierBeamConfigs[pierKey] = {
                        izq: { ...this.standardBeam },
                        der: { ...this.standardBeam }
                    };
                    // Actualizar ambas celdas para mostrar naranja
                    this.updatePierBeamCells(pierKey);
                }

                // Guardar config localmente
                this.onBeamChange(pierKey, side, false);  // false = no guardar en servidor

                // Agregar a pendientes y mostrar botón
                this.pendingRecalcPiers.add(pierKey);
                this.updateRecalcButton();

                // Marcar fila como pendiente
                const row = document.querySelector(`tr[data-pier-key="${pierKey}"]`);
                if (row) row.classList.add('pending-recalc');
            });
        });

        return td;
    }

    getBeamConfig(pierKey, side) {
        if (this.customBeamPiers.has(pierKey) && this.pierBeamConfigs[pierKey]?.[side]) {
            return this.pierBeamConfigs[pierKey][side];
        }
        return this.standardBeam;
    }

    togglePierBeamLock(pierKey) {
        if (this.customBeamPiers.has(pierKey)) {
            this.customBeamPiers.delete(pierKey);
            delete this.pierBeamConfigs[pierKey];
        } else {
            this.customBeamPiers.add(pierKey);
            this.pierBeamConfigs[pierKey] = {
                izq: { ...this.standardBeam },
                der: { ...this.standardBeam }
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
            this.pierBeamConfigs[pierKey] = { izq: { ...this.standardBeam }, der: { ...this.standardBeam } };
        }
        this.pierBeamConfigs[pierKey][side] = { width, height, ln, nbars, diam };

        // Solo guardar en servidor si se solicita (botón recalcular)
        if (saveToServer) {
            this.savePierBeamConfig(pierKey);
        }
    }

    async savePierBeamConfig(pierKey) {
        const config = this.pierBeamConfigs[pierKey];
        if (!config) return;

        const row = this.elements.resultsTable?.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
        if (row) row.style.opacity = '0.5';

        try {
            // El endpoint guarda config Y retorna resultado actualizado
            const response = await structuralAPI.setPierBeam(this.sessionId, pierKey, config);

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
                this.updateStatistics(this.calculateStatistics(filtered));
                this.updateSummaryPlot();
            }
        } catch (error) {
            console.error('Error guardando config de viga:', error);
        } finally {
            if (row) row.style.opacity = '1';
        }
    }

    updateStandardBeam(beam) {
        this.standardBeam = { ...beam };
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
            await structuralAPI.setDefaultBeam(this.sessionId, this.standardBeam);
        } catch (error) {
            console.error('Error guardando viga estándar:', error);
        }
    }

    // =========================================================================
    // Combinaciones
    // =========================================================================

    appendComboRows(container, pierKey) {
        const isExpanded = this.expandedPiers.has(pierKey);
        const displayStyle = isExpanded ? '' : 'display: none;';

        if (isExpanded && this.combinationsCache[pierKey]) {
            this.combinationsCache[pierKey].forEach(combo => {
                container.appendChild(this.createComboRow(combo, pierKey, displayStyle));
            });
        } else {
            const loadingRow = document.createElement('tr');
            loadingRow.className = 'combo-row';
            loadingRow.dataset.pierKey = pierKey;
            loadingRow.style.cssText = displayStyle;
            loadingRow.innerHTML = '<td colspan="12" style="text-align:center; color: #6b7280;">Cargando...</td>';
            container.appendChild(loadingRow);
        }
    }

    createComboRow(combo, pierKey, displayStyle = '') {
        const tr = document.createElement('tr');
        tr.className = 'combo-row';
        tr.dataset.pierKey = pierKey;
        tr.dataset.comboIndex = combo.index;
        if (displayStyle) tr.style.cssText = displayStyle;

        const shearSf2 = parseFloat(combo.shear_sf_2) || 100;
        const shearSf3 = parseFloat(combo.shear_sf_3) || 100;
        const dcrCombined = Math.sqrt(Math.pow(1/shearSf2, 2) + Math.pow(1/shearSf3, 2));
        const comboShearSf = 1.0 / dcrCombined;
        const comboShearDisplay = comboShearSf >= 100 ? '>100' : comboShearSf.toFixed(2);

        tr.innerHTML = `
            <td class="combo-indent" colspan="2"><span class="combo-name">${combo.full_name || combo.name}</span></td>
            <td class="combo-forces-cell" colspan="4">P=${combo.P} | M2=${combo.M2} | M3=${combo.M3}</td>
            <td class="fs-value ${getFsClass(combo.flexure_sf)}">${combo.flexure_sf}</td>
            <td></td>
            <td class="fs-value ${getFsClass(comboShearDisplay)}">${comboShearDisplay}</td>
            <td class="combo-forces-cell">V2=${combo.V2} | V3=${combo.V3} | DCR: ${formatDcr(dcrCombined)}</td>
            <td></td>
            <td class="actions-cell"><button class="action-btn" data-action="diagram-combo">📊</button></td>
        `;

        tr.querySelector('[data-action="diagram-combo"]')?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showCombinationDiagram(pierKey, combo.index);
        });

        return tr;
    }

    async toggleExpand(pierKey) {
        const { resultsTable } = this.elements;
        const pierRow = resultsTable?.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
        const comboRows = resultsTable?.querySelectorAll(`.combo-row[data-pier-key="${pierKey}"]`);
        if (!pierRow) return;

        if (this.expandedPiers.has(pierKey)) {
            this.expandedPiers.delete(pierKey);
            pierRow.classList.remove('expanded');
            comboRows?.forEach(row => row.style.display = 'none');
        } else {
            this.expandedPiers.add(pierKey);
            pierRow.classList.add('expanded');
            if (!this.combinationsCache[pierKey]) {
                await this.loadCombinations(pierKey);
            } else {
                comboRows?.forEach(row => row.style.display = '');
            }
        }
    }

    async loadCombinations(pierKey) {
        try {
            const data = await structuralAPI.getPierCombinations(this.sessionId, pierKey);
            if (data.success) {
                this.combinationsCache[pierKey] = data.combinations;
                const { resultsTable } = this.elements;
                resultsTable?.querySelectorAll(`.combo-row[data-pier-key="${pierKey}"]`).forEach(r => r.remove());

                const pierRow = resultsTable?.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
                if (!pierRow) return;

                let insertAfter = pierRow;
                data.combinations.forEach(combo => {
                    const tr = this.createComboRow(combo, pierKey);
                    insertAfter.insertAdjacentElement('afterend', tr);
                    insertAfter = tr;
                });
            }
        } catch (error) {
            console.error('Error loading combinations:', error);
        }
    }

    async showCombinationDiagram(pierKey, comboIndex) {
        const combo = this.combinationsCache[pierKey]?.[comboIndex];
        if (!combo) return;
        try {
            const data = await structuralAPI.analyzeCombination({
                session_id: this.sessionId, pier_key: pierKey,
                combination_index: comboIndex, generate_plot: true
            });
            if (data.success && data.pm_plot) {
                this.page.plotModal.open(pierKey, pierKey.replace('_', ' - '), data.pm_plot, combo);
            }
        } catch (error) {
            console.error('Error getting combination diagram:', error);
        }
    }

    async toggleAllExpand() {
        const { resultsTable } = this.elements;
        if (!resultsTable) return false;

        const pierKeys = Array.from(resultsTable.querySelectorAll('.pier-row:not(.column-type)')).map(r => r.dataset.pierKey);
        if (pierKeys.length === 0) return false;

        const hasExpanded = pierKeys.some(key => this.expandedPiers.has(key));

        if (hasExpanded) {
            this.collapseAll();
            return false;
        } else {
            await this.expandAll(pierKeys);
            return true;
        }
    }

    collapseAll() {
        const { resultsTable } = this.elements;
        if (!resultsTable) return;
        this.expandedPiers.clear();
        resultsTable.querySelectorAll('.combo-row').forEach(r => r.style.display = 'none');
        resultsTable.querySelectorAll('.pier-row').forEach(r => r.classList.remove('expanded'));
    }

    async expandAll(pierKeys) {
        const { resultsTable } = this.elements;
        if (!resultsTable) return;

        pierKeys.forEach(key => this.expandedPiers.add(key));
        resultsTable.querySelectorAll('.pier-row').forEach(r => r.classList.add('expanded'));

        await Promise.all(pierKeys.filter(k => !this.combinationsCache[k]).map(k => this.loadCombinations(k)));
        resultsTable.querySelectorAll('.combo-row').forEach(r => r.style.display = '');
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
        if (config.n_edge_bars) pier.n_edge_bars = config.n_edge_bars;
        if (config.diameter_edge) pier.diameter_edge = config.diameter_edge;
        if (config.n_meshes) pier.n_meshes = config.n_meshes;
        if (config.diameter_v) { pier.diameter_v = config.diameter_v; pier.diameter_h = config.diameter_v; }
        if (config.spacing_v) { pier.spacing_v = config.spacing_v; pier.spacing_h = config.spacing_v; }

        await this.reanalyzeSinglePier(pierKey);
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

    async saveInlineEdit(row, pierKey) {
        const malla = row.querySelector('.malla-cell');
        const borde = row.querySelector('.borde-cell');

        const pier = this.piersData.find(p => p.key === pierKey);
        if (pier) {
            pier.n_meshes = parseInt(malla?.querySelector('.edit-meshes')?.value) || 2;
            pier.diameter_v = parseInt(malla?.querySelector('.edit-diameter-v')?.value) || 8;
            pier.spacing_v = parseInt(malla?.querySelector('.edit-spacing-v')?.value) || 200;
            pier.diameter_h = parseInt(malla?.querySelector('.edit-diameter-h')?.value) || 8;
            pier.spacing_h = parseInt(malla?.querySelector('.edit-spacing-h')?.value) || 200;
            pier.n_edge_bars = parseInt(borde?.querySelector('.edit-n-edge')?.value) || 2;
            pier.diameter_edge = parseInt(borde?.querySelector('.edit-edge')?.value) || 12;
            pier.stirrup_diameter = parseInt(borde?.querySelector('.edit-stirrup-d')?.value) || 10;
            pier.stirrup_spacing = parseInt(borde?.querySelector('.edit-stirrup-s')?.value) || 150;
        }

        await this.reanalyzeSinglePier(pierKey);
    }

    async reanalyzeSinglePier(pierKey) {
        const pier = this.piersData.find(p => p.key === pierKey);
        if (!pier || !this.sessionId) return;

        const row = this.elements.resultsTable?.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
        if (row) row.style.opacity = '0.5';

        try {
            const data = await structuralAPI.analyze({
                session_id: this.sessionId,
                pier_updates: [{
                    key: pierKey,
                    n_meshes: pier.n_meshes, diameter_v: pier.diameter_v, diameter_h: pier.diameter_h,
                    spacing_v: pier.spacing_v, spacing_h: pier.spacing_h,
                    n_edge_bars: pier.n_edge_bars || 2, diameter_edge: pier.diameter_edge,
                    stirrup_diameter: pier.stirrup_diameter || 10, stirrup_spacing: pier.stirrup_spacing || 150,
                    cover: pier.cover || 25
                }],
                generate_plots: true, moment_axis: 'M3', angle_deg: 0
            });

            if (data.success) {
                this.page.results = data.results;
                delete this.combinationsCache[pierKey];
                const filtered = this.getFilteredResults();
                this.renderTable(filtered);
                this.updateStatistics(this.calculateStatistics(filtered));
                this.updateSummaryPlot();
            }
        } catch (error) {
            console.error('Error re-analyzing pier:', error);
            alert('Error al re-analizar: ' + error.message);
        } finally {
            if (row) row.style.opacity = '1';
        }
    }

    reset() {
        this.expandedPiers.clear();
        this.combinationsCache = {};
        this.plotsCache = {};
    }
}
