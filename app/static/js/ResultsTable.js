// app/structural/static/js/ResultsTable.js
/**
 * Módulo para manejo de la tabla de resultados y combinaciones.
 */

class ResultsTable {
    constructor(page) {
        this.page = page;
        this.expandedPiers = new Set();
        this.combinationsCache = {};
        this.plotsCache = {};
    }

    // =========================================================================
    // Acceso a elementos y datos
    // =========================================================================

    get elements() {
        return this.page.elements;
    }

    get filters() {
        return this.page.filters;
    }

    get piersData() {
        return this.page.piersData;
    }

    get sessionId() {
        return this.page.sessionId;
    }

    // =========================================================================
    // Filtros
    // =========================================================================

    populateFilters() {
        const { storyFilter, axisFilter } = this.elements;

        if (storyFilter) {
            storyFilter.innerHTML = '<option value="">Todos los pisos</option>';
            this.page.uniqueStories.forEach(story => {
                const option = document.createElement('option');
                option.value = story;
                option.textContent = story;
                storyFilter.appendChild(option);
            });
        }

        if (axisFilter) {
            axisFilter.innerHTML = '<option value="">Todos los ejes</option>';
            this.page.uniqueAxes.forEach(axis => {
                const option = document.createElement('option');
                option.value = axis;
                option.textContent = axis;
                axisFilter.appendChild(option);
            });
        }
    }

    applyFilters() {
        this.page.filters.story = this.elements.storyFilter?.value || '';
        this.page.filters.axis = this.elements.axisFilter?.value || '';

        const filtered = this.getFilteredResults();
        this.renderTable(filtered);
        this.updateStatistics(this.calculateStatistics(filtered));
        this.updateSummaryPlot();
    }

    getFilteredResults() {
        return this.page.results.filter(result => {
            if (this.filters.story && result.story !== this.filters.story) {
                return false;
            }
            if (this.filters.axis) {
                const parts = result.pier_label.split('-');
                const axis = parts.length > 1 ? parts[1] : '';
                if (axis !== this.filters.axis) return false;
            }
            return true;
        });
    }

    calculateStatistics(results) {
        const total = results.length;
        const ok = results.filter(r => r.overall_status === 'OK').length;

        return {
            total,
            ok,
            fail: total - ok,
            pass_rate: total > 0 ? (ok / total * 100) : 0
        };
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
            summaryPlotContainer.innerHTML =
                `<img src="data:image/png;base64,${plotBase64}" alt="Resumen de Factores de Seguridad">`;
        }
    }

    async updateSummaryPlot() {
        if (!this.sessionId) return;

        try {
            const { summaryPlotContainer } = this.elements;
            if (summaryPlotContainer) {
                summaryPlotContainer.classList.add('loading');
            }

            const data = await structuralAPI.getSummaryPlot({
                session_id: this.sessionId,
                story_filter: this.filters.story,
                axis_filter: this.filters.axis
            });

            if (data.success && data.summary_plot) {
                this.renderSummaryPlot(data.summary_plot);
            } else if (data.count === 0) {
                if (summaryPlotContainer) {
                    summaryPlotContainer.innerHTML =
                        '<p class="no-data">No hay datos para los filtros seleccionados</p>';
                }
            }
        } catch (error) {
            console.error('Error updating summary plot:', error);
        } finally {
            const { summaryPlotContainer } = this.elements;
            if (summaryPlotContainer) {
                summaryPlotContainer.classList.remove('loading');
            }
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
            const pierKey = `${result.story}_${result.pier_label}`;
            const pierLabel = `${result.story} - ${result.pier_label}`;

            if (result.pm_plot) {
                this.plotsCache[pierKey] = result.pm_plot;
            }

            // Fila principal del pier
            const row = this.createPierRow(result, pierKey, pierLabel);
            resultsTable.appendChild(row);

            // Filas de combinaciones (como <tr> directamente, no <tbody>)
            this.appendComboRows(resultsTable, pierKey);

            // Si está expandido, cargar combinaciones
            if (this.expandedPiers.has(pierKey) && !this.combinationsCache[pierKey]) {
                this.loadCombinations(pierKey);
            }
        });
    }

    createPierRow(result, pierKey, pierLabel) {
        const statusClass = result.overall_status === 'OK' ? 'status-ok' : 'status-fail';
        const isExpanded = this.expandedPiers.has(pierKey);

        const pier = this.piersData.find(p => p.key === pierKey);
        const armaduraText = pier
            ? `${pier.n_meshes}M φ${pier.diameter_v}@${pier.spacing_v} +${pier.n_meshes}φ${pier.diameter_edge || 10}`
            : '-';

        // Esbeltez info
        const slenderness = result.slenderness || {};
        const lambdaVal = slenderness.lambda || 0;
        const isSlender = slenderness.is_slender || false;
        const reductionPct = slenderness.reduction_pct || 0;
        const slenderClass = isSlender ? 'slender-warn' : '';
        const slenderInfo = isSlender
            ? `λ=${lambdaVal} (-${reductionPct}%)`
            : `λ=${lambdaVal}`;

        const row = document.createElement('tr');
        row.className = `pier-row ${isExpanded ? 'expanded' : ''}`;
        row.dataset.pierKey = pierKey;

        // Tipo de fórmula de corte
        const shearType = result.shear.formula_type === 'column' ? 'COL' : 'MURO';
        const shearTypeTitle = result.shear.formula_type === 'column'
            ? 'Fórmula COLUMNA (ACI 22.5): Vc=0.17√fc·bw·d'
            : 'Fórmula MURO (ACI 18.10.4): Vc=αc√fc·Acv';

        // Wall continuity info
        const continuity = result.wall_continuity || {};
        const hwcsM = continuity.hwcs_m || result.geometry.height_m || 0;
        const hwcsLw = continuity.hwcs_lw || 0;
        const nStories = continuity.n_stories || 1;
        const isContinuous = continuity.is_continuous || false;
        const storiesText = isContinuous ? `${nStories} pisos` : '1 piso';

        row.innerHTML = `
            <td>${result.story}</td>
            <td>${result.pier_label}</td>
            <td>${result.geometry.width_m.toFixed(2)}×${result.geometry.thickness_m.toFixed(2)}</td>
            <td class="hwcs-cell" title="hwcs/lw = ${hwcsLw.toFixed(2)}">
                <span class="hwcs-value">${hwcsM.toFixed(1)}m</span>
                <span class="hwcs-ratio">hwcs/lw=${hwcsLw.toFixed(1)}</span>
                <span class="hwcs-stories">${storiesText}</span>
            </td>
            <td class="armadura-cell" data-pier-key="${pierKey}">
                <div class="armadura-row">
                    <select class="edit-meshes" title="Mallas">
                        <option value="1" ${pier?.n_meshes === 1 ? 'selected' : ''}>1M</option>
                        <option value="2" ${pier?.n_meshes === 2 ? 'selected' : ''}>2M</option>
                    </select>
                    <select class="edit-diameter" title="φ Vertical">
                        ${[6,8,10,12,16,20,22,25].map(d => `<option value="${d}" ${pier?.diameter_v === d ? 'selected' : ''}>φ${d}</option>`).join('')}
                    </select>
                    <select class="edit-spacing" title="Espaciamiento">
                        ${[100,150,200,250,300].map(s => `<option value="${s}" ${pier?.spacing_v === s ? 'selected' : ''}>@${s}</option>`).join('')}
                    </select>
                </div>
                <div class="armadura-row borde-row">
                    <select class="edit-n-edge" title="Nº barras borde (por lado)">
                        ${[2,4,6,8,10,12].map(n => `<option value="${n}" ${pier?.n_edge_bars === n ? 'selected' : ''}>${n}φ</option>`).join('')}
                    </select>
                    <select class="edit-edge" title="φ Borde">
                        ${[12,16,18,20,22,25,28,32].map(d => `<option value="${d}" ${pier?.diameter_edge === d ? 'selected' : ''}>φ${d}</option>`).join('')}
                    </select>
                    <select class="edit-stirrup-d" title="φ Estribo">
                        ${[8,10,12].map(d => `<option value="${d}" ${pier?.stirrup_diameter === d ? 'selected' : ''}>E${d}</option>`).join('')}
                    </select>
                    <select class="edit-stirrup-s" title="@ Estribo">
                        ${[75,100,125,150,200].map(s => `<option value="${s}" ${pier?.stirrup_spacing === s ? 'selected' : ''}>@${s}</option>`).join('')}
                    </select>
                </div>
            </td>
            <td class="fs-value ${this.getFsClass(result.flexure.sf)}">
                <span class="fs-number">${result.flexure.sf}</span>
                <span class="critical-combo">${this.truncateCombo(result.flexure.critical_combo)}</span>
            </td>
            <td class="capacity-cell">
                <span class="capacity-line">φMn=${result.flexure.phi_Mn}t-m</span>
                <span class="capacity-line">Mu=${result.flexure.Mu}t-m</span>
                <span class="slenderness-info ${slenderClass}" title="Esbeltez">${slenderInfo}</span>
            </td>
            <td class="fs-value ${this.getFsClass(result.shear.sf)}">
                <span class="fs-number">${result.shear.sf}</span>
                <span class="critical-combo">${this.truncateCombo(result.shear.critical_combo)}</span>
                <span class="formula-tag formula-${result.shear.formula_type}" title="${shearTypeTitle}">${shearType}</span>
            </td>
            <td class="capacity-cell">
                <span class="capacity-line">Vc=${result.shear.Vc}t + Vs=${result.shear.Vs}t</span>
                <span class="capacity-line">φVn=${result.shear.phi_Vn_2}t</span>
                <span class="dcr-info" title="DCR = Vu/φVn">DCR: ${this.formatDcr(result.shear.dcr_combined)} (Vu=${result.shear.Vu_2}t)</span>
            </td>
            <td class="${statusClass}">${result.overall_status}</td>
            <td class="actions-cell">
                <div class="action-buttons">
                    <button class="action-btn ${isExpanded ? 'active' : ''}" data-action="expand" title="Ver combinaciones">
                        <span class="expand-icon">▶</span>
                    </button>
                    <button class="action-btn" data-action="section" title="Ver sección transversal">🔲</button>
                    <button class="action-btn" data-action="info" title="Ver capacidades">ℹ️</button>
                    ${result.pm_plot ?
                        `<button class="action-btn" data-action="diagram" title="Ver diagrama P-M">📊</button>` : ''}
                </div>
            </td>
        `;

        // Event handlers para botones de acción
        row.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;

                if (action === 'expand') {
                    this.toggleExpand(pierKey);
                } else if (action === 'section') {
                    this.page.showSectionDiagram(pierKey, pierLabel);
                } else if (action === 'info') {
                    this.page.showPierDetails(pierKey, pierLabel);
                } else if (action === 'diagram') {
                    this.page.plotModal.open(pierKey, pierLabel, this.plotsCache[pierKey]);
                }
            });
        });

        // Event handlers para edición inline de armadura
        row.querySelectorAll('.armadura-cell select').forEach(select => {
            select.addEventListener('change', () => {
                this.saveInlineEdit(row, pierKey);
            });
        });

        return row;
    }

    appendComboRows(container, pierKey) {
        const isExpanded = this.expandedPiers.has(pierKey);
        const displayStyle = isExpanded ? '' : 'display: none;';

        if (isExpanded && this.combinationsCache[pierKey]) {
            // Agregar filas de combinaciones existentes
            this.combinationsCache[pierKey].forEach(combo => {
                const tr = this.createComboRow(combo, pierKey, displayStyle);
                container.appendChild(tr);
            });
        } else {
            // Fila de cargando
            const loadingRow = document.createElement('tr');
            loadingRow.className = 'combo-row';
            loadingRow.dataset.pierKey = pierKey;
            loadingRow.style.cssText = displayStyle;
            loadingRow.innerHTML = '<td colspan="11" style="text-align:center; color: #6b7280;">Cargando combinaciones...</td>';
            container.appendChild(loadingRow);
        }
    }

    createComboRow(combo, pierKey, displayStyle = '') {
        const statusClass = combo.overall_status === 'OK' ? 'status-ok' : 'status-fail';

        const tr = document.createElement('tr');
        tr.className = 'combo-row';
        tr.dataset.pierKey = pierKey;
        tr.dataset.comboIndex = combo.index;
        if (displayStyle) {
            tr.style.cssText = displayStyle;
        }

        // Calcular DCR combinado SRSS: DCR = √[(Vu2/φVn2)² + (Vu3/φVn3)²]
        const shearSf2 = parseFloat(combo.shear_sf_2) || 100;
        const shearSf3 = parseFloat(combo.shear_sf_3) || 100;
        const dcr2 = 1.0 / shearSf2;
        const dcr3 = 1.0 / shearSf3;
        const dcrCombined = Math.sqrt(dcr2 * dcr2 + dcr3 * dcr3);
        const comboShearSf = 1.0 / dcrCombined;
        const comboShearDisplay = comboShearSf >= 100 ? '>100' : comboShearSf.toFixed(2);

        tr.innerHTML = `
            <td class="combo-indent"></td>
            <td class="combo-name" colspan="3">
                ${combo.full_name || combo.name}
            </td>
            <td class="combo-forces-cell">P=${combo.P} | M2=${combo.M2} | M3=${combo.M3}</td>
            <td class="fs-value ${this.getFsClass(combo.flexure_sf)}">${combo.flexure_sf}</td>
            <td></td>
            <td class="fs-value ${this.getFsClass(comboShearDisplay)}">${comboShearDisplay}</td>
            <td class="combo-forces-cell">V2=${combo.V2} | V3=${combo.V3} | DCR: ${this.formatDcr(dcrCombined)}</td>
            <td class="${statusClass}">${combo.overall_status}</td>
            <td class="actions-cell">
                <button class="action-btn" data-action="diagram-combo" title="Ver diagrama P-M">📊</button>
            </td>
        `;

        // Event handler para el botón de diagrama
        const btn = tr.querySelector('[data-action="diagram-combo"]');
        btn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showCombinationDiagram(pierKey, combo.index);
        });

        return tr;
    }

    // =========================================================================
    // Expandir/Contraer
    // =========================================================================

    async toggleExpand(pierKey) {
        const { resultsTable } = this.elements;
        const pierRow = resultsTable.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
        const comboRows = resultsTable.querySelectorAll(`.combo-row[data-pier-key="${pierKey}"]`);

        if (!pierRow) return;

        if (this.expandedPiers.has(pierKey)) {
            // Contraer
            this.expandedPiers.delete(pierKey);
            pierRow.classList.remove('expanded');
            comboRows.forEach(row => row.style.display = 'none');
        } else {
            // Expandir
            this.expandedPiers.add(pierKey);
            pierRow.classList.add('expanded');

            if (!this.combinationsCache[pierKey]) {
                await this.loadCombinations(pierKey);
            } else {
                comboRows.forEach(row => row.style.display = '');
            }
        }
    }

    async loadCombinations(pierKey) {
        try {
            const data = await structuralAPI.getPierCombinations(this.sessionId, pierKey);

            if (data.success) {
                this.combinationsCache[pierKey] = data.combinations;

                const { resultsTable } = this.elements;

                // Eliminar filas de "cargando" existentes
                const oldRows = resultsTable.querySelectorAll(`.combo-row[data-pier-key="${pierKey}"]`);
                oldRows.forEach(row => row.remove());

                // Encontrar la fila del pier para insertar después
                const pierRow = resultsTable.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
                if (!pierRow) return;

                // Insertar nuevas filas de combinaciones después del pier row
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

    // =========================================================================
    // Diagrama de Combinación
    // =========================================================================

    async showCombinationDiagram(pierKey, comboIndex) {
        const combo = this.combinationsCache[pierKey]?.[comboIndex];
        if (!combo) return;

        const pierLabel = pierKey.replace('_', ' - ');

        try {
            const data = await structuralAPI.analyzeCombination({
                session_id: this.sessionId,
                pier_key: pierKey,
                combination_index: comboIndex,
                generate_plot: true
            });

            if (data.success && data.pm_plot) {
                this.page.plotModal.open(pierKey, pierLabel, data.pm_plot, combo);
            }
        } catch (error) {
            console.error('Error getting combination diagram:', error);
        }
    }

    // =========================================================================
    // Utilidades
    // =========================================================================

    truncateCombo(name) {
        if (!name) return '';
        return name.length > 20 ? name.substring(0, 18) + '...' : name;
    }

    getFsClass(fs) {
        if (fs === '>100') return 'fs-ok';
        const val = parseFloat(fs);
        if (val >= 1.5) return 'fs-ok';
        if (val >= 1.0) return 'fs-warn';
        return 'fs-fail';
    }

    formatDcr(dcr) {
        if (dcr === undefined || dcr === null) return '-';
        if (dcr < 0.001) return '≈0';
        return dcr.toFixed(2);
    }

    // =========================================================================
    // Edición Inline de Armadura
    // =========================================================================

    async saveInlineEdit(row, pierKey) {
        const armaduraCell = row.querySelector('.armadura-cell');

        // Armadura distribuida
        const meshes = parseInt(armaduraCell.querySelector('.edit-meshes').value);
        const diameter = parseInt(armaduraCell.querySelector('.edit-diameter').value);
        const spacing = parseInt(armaduraCell.querySelector('.edit-spacing').value);

        // Elemento de borde
        const nEdgeBars = parseInt(armaduraCell.querySelector('.edit-n-edge').value);
        const edgeDiameter = parseInt(armaduraCell.querySelector('.edit-edge').value);
        const stirrupDiameter = parseInt(armaduraCell.querySelector('.edit-stirrup-d').value);
        const stirrupSpacing = parseInt(armaduraCell.querySelector('.edit-stirrup-s').value);

        // Actualizar piersData local
        const pier = this.piersData.find(p => p.key === pierKey);
        if (pier) {
            pier.n_meshes = meshes;
            pier.diameter_v = diameter;
            pier.diameter_h = diameter;
            pier.spacing_v = spacing;
            pier.spacing_h = spacing;
            pier.n_edge_bars = nEdgeBars;
            pier.diameter_edge = edgeDiameter;
            pier.stirrup_diameter = stirrupDiameter;
            pier.stirrup_spacing = stirrupSpacing;
        }

        // Re-analizar este pier
        await this.reanalyzeSinglePier(pierKey);
    }

    async reanalyzeSinglePier(pierKey) {
        const pier = this.piersData.find(p => p.key === pierKey);
        if (!pier || !this.sessionId) return;

        // Mostrar indicador de carga en la fila
        const row = this.elements.resultsTable?.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
        if (row) {
            row.style.opacity = '0.5';
        }

        try {
            const updates = [{
                key: pierKey,
                n_meshes: pier.n_meshes,
                diameter_v: pier.diameter_v,
                diameter_h: pier.diameter_h,
                spacing_v: pier.spacing_v,
                spacing_h: pier.spacing_h,
                n_edge_bars: pier.n_edge_bars || 2,
                diameter_edge: pier.diameter_edge,
                stirrup_diameter: pier.stirrup_diameter || 10,
                stirrup_spacing: pier.stirrup_spacing || 150,
                cover: pier.cover || 25
            }];

            const data = await structuralAPI.analyze({
                session_id: this.sessionId,
                pier_updates: updates,
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0
            });

            if (data.success) {
                // Actualizar resultados
                this.page.results = data.results;

                // Limpiar caché de combinaciones para este pier
                delete this.combinationsCache[pierKey];

                // Re-renderizar tabla manteniendo expansiones
                const filtered = this.getFilteredResults();
                this.renderTable(filtered);
                this.updateStatistics(this.calculateStatistics(filtered));
                this.updateSummaryPlot();
            }
        } catch (error) {
            console.error('Error re-analyzing pier:', error);
            alert('Error al re-analizar: ' + error.message);
        } finally {
            if (row) {
                row.style.opacity = '1';
            }
        }
    }

    // =========================================================================
    // Expandir/Colapsar Todos
    // =========================================================================

    toggleAllExpand() {
        const { resultsTable } = this.elements;
        if (!resultsTable) return false;

        // Obtener todas las pierKeys de las filas visibles
        const pierRows = resultsTable.querySelectorAll('.pier-row');
        const pierKeys = Array.from(pierRows).map(row => row.dataset.pierKey);

        // Determinar si expandir o colapsar (si hay alguno expandido, colapsar todos)
        const hasExpanded = pierKeys.some(key => this.expandedPiers.has(key));

        if (hasExpanded) {
            // Colapsar todos
            this.collapseAll();
            return false;
        } else {
            // Expandir todos
            this.expandAll(pierKeys);
            return true;
        }
    }

    collapseAll() {
        const { resultsTable } = this.elements;
        if (!resultsTable) return;

        // Colapsar todas las filas
        this.expandedPiers.clear();

        // Ocultar todas las filas de combinaciones
        const comboRows = resultsTable.querySelectorAll('.combo-row');
        comboRows.forEach(row => row.style.display = 'none');

        // Remover clase expanded de todas las pier rows
        const pierRows = resultsTable.querySelectorAll('.pier-row');
        pierRows.forEach(row => row.classList.remove('expanded'));
    }

    async expandAll(pierKeys) {
        const { resultsTable } = this.elements;
        if (!resultsTable) return;

        // Marcar todos como expandidos
        pierKeys.forEach(key => this.expandedPiers.add(key));

        // Actualizar UI
        const pierRows = resultsTable.querySelectorAll('.pier-row');
        pierRows.forEach(row => row.classList.add('expanded'));

        // Cargar combinaciones para los que no tienen caché
        const loadPromises = pierKeys
            .filter(key => !this.combinationsCache[key])
            .map(key => this.loadCombinations(key));

        await Promise.all(loadPromises);

        // Mostrar todas las filas de combinaciones
        const comboRows = resultsTable.querySelectorAll('.combo-row');
        comboRows.forEach(row => row.style.display = '');
    }

    // =========================================================================
    // Reset
    // =========================================================================

    reset() {
        this.expandedPiers.clear();
        this.combinationsCache = {};
        this.plotsCache = {};
    }
}
