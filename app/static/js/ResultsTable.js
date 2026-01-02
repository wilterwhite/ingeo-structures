// app/structural/static/js/ResultsTable.js
/**
 * Módulo para manejo de la tabla de resultados y combinaciones.
 * Refactorizado para mejor mantenibilidad.
 */

class ResultsTable {
    constructor(page) {
        this.page = page;
        this.expandedPiers = new Set();
        this.combinationsCache = {};
        this.plotsCache = {};

        // Estado de vigas
        this.standardBeam = { width: 200, height: 500, ln: 1500, nbars: 2, diam: 12 };
        this.customBeamPiers = new Set();  // Piers con vigas personalizadas
        this.pierBeamConfigs = {};  // Configuración de vigas por pier
    }

    // =========================================================================
    // Acceso a elementos y datos
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

        // Poblar ejes (inicialmente todos)
        this.updateAxisFilter();
    }

    /**
     * Actualiza el filtro de ejes según la grilla seleccionada.
     */
    updateAxisFilter() {
        const { grillaFilter, axisFilter } = this.elements;
        if (!axisFilter) return;

        const selectedGrilla = grillaFilter?.value || '';
        const currentAxis = axisFilter.value;

        // Obtener ejes únicos de la grilla seleccionada (desde resultados)
        let axes;
        if (selectedGrilla) {
            const axesSet = new Set();
            this.page.results.forEach(result => {
                const parts = result.pier_label.split('-');
                const grilla = parts[0] || '';
                const axis = parts[1] || '';
                if (grilla === selectedGrilla && axis) {
                    axesSet.add(axis);
                }
            });
            axes = [...axesSet].sort();
        } else {
            axes = this.page.uniqueAxes;
        }

        // Repoblar dropdown
        axisFilter.innerHTML = '<option value="">Todos</option>';
        axes.forEach(axis => {
            const option = document.createElement('option');
            option.value = axis;
            option.textContent = axis;
            axisFilter.appendChild(option);
        });

        // Mantener selección si sigue siendo válida
        if (axes.includes(currentAxis)) {
            axisFilter.value = currentAxis;
        }
    }

    /**
     * Llamado cuando cambia la grilla - actualiza ejes y aplica filtros.
     */
    onGrillaChange() {
        this.updateAxisFilter();
        this.applyFilters();
    }

    applyFilters() {
        this.page.filters.grilla = this.elements.grillaFilter?.value || '';
        this.page.filters.story = this.elements.storyFilter?.value || '';
        this.page.filters.axis = this.elements.axisFilter?.value || '';
        this.page.filters.status = this.elements.statusFilter?.value || '';

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
            const pierKey = `${result.story}_${result.pier_label}`;
            if (result.pm_plot) this.plotsCache[pierKey] = result.pm_plot;

            const row = this.createPierRow(result, pierKey);
            resultsTable.appendChild(row);
            this.appendComboRows(resultsTable, pierKey);

            if (this.expandedPiers.has(pierKey) && !this.combinationsCache[pierKey]) {
                this.loadCombinations(pierKey);
            }
        });
    }

    // =========================================================================
    // Creación de Fila Principal (Refactorizado)
    // =========================================================================

    createPierRow(result, pierKey) {
        const pier = this.piersData.find(p => p.key === pierKey);
        const isExpanded = this.expandedPiers.has(pierKey);

        const row = document.createElement('tr');
        row.className = `pier-row ${isExpanded ? 'expanded' : ''}`;
        row.dataset.pierKey = pierKey;

        // Crear cada celda por separado
        row.appendChild(this.createPierInfoCell(result));
        row.appendChild(this.createHwcsCell(result));
        row.appendChild(this.createMallaCell(pier, pierKey, result));
        row.appendChild(this.createBordeCell(pier, pierKey));
        row.appendChild(this.createVigaCell(pierKey, 'izq'));
        row.appendChild(this.createVigaCell(pierKey, 'der'));
        row.appendChild(this.createFlexureSfCell(result));
        row.appendChild(this.createFlexureCapCell(result));
        row.appendChild(this.createShearSfCell(result));
        row.appendChild(this.createShearCapCell(result));
        row.appendChild(this.createProposalCell(result, pierKey));
        row.appendChild(this.createActionsCell(result, pierKey, isExpanded));

        // Event handlers
        this.attachRowEventHandlers(row, pierKey, result);

        return row;
    }

    // =========================================================================
    // Celdas Individuales
    // =========================================================================

    createPierInfoCell(result) {
        const td = document.createElement('td');
        td.className = 'pier-info-cell';
        td.innerHTML = `
            <span class="pier-name">${result.pier_label}</span>
            <span class="pier-story">${result.story}</span>
            <span class="pier-dims">lw=${result.geometry.width_m.toFixed(2)} e=${result.geometry.thickness_m.toFixed(2)}</span>
        `;
        return td;
    }

    createHwcsCell(result) {
        const cont = result.wall_continuity || {};
        const hwcsM = cont.hwcs_m || result.geometry.height_m || 0;
        const hwcsLw = cont.hwcs_lw || 0;
        const nStories = cont.n_stories || 1;
        const storiesText = cont.is_continuous ? `${nStories} pisos` : '1 piso';

        const td = document.createElement('td');
        td.className = 'hwcs-cell';
        td.title = `hwcs/lw = ${hwcsLw.toFixed(2)}`;
        td.innerHTML = `
            <span class="hwcs-value">${hwcsM.toFixed(1)}m</span>
            <span class="hwcs-ratio">hwcs/lw=${hwcsLw.toFixed(1)}</span>
            <span class="hwcs-stories">${storiesText}</span>
        `;
        return td;
    }

    createMallaCell(pier, pierKey, result) {
        const td = document.createElement('td');
        td.className = 'malla-cell';
        td.dataset.pierKey = pierKey;

        td.innerHTML = `
            <div class="malla-row">
                <select class="edit-meshes" title="Mallas">
                    <option value="1" ${pier?.n_meshes === 1 ? 'selected' : ''}>1M</option>
                    <option value="2" ${pier?.n_meshes === 2 ? 'selected' : ''}>2M</option>
                </select>
                <span class="malla-label">V</span>
                <select class="edit-diameter-v" title="φ Vertical">
                    ${[6,8,10,12,16].map(d => `<option value="${d}" ${pier?.diameter_v === d ? 'selected' : ''}>φ${d}</option>`).join('')}
                </select>
                <select class="edit-spacing-v" title="@ Vertical">
                    ${[100,125,150,175,200,250,300].map(s => `<option value="${s}" ${pier?.spacing_v === s ? 'selected' : ''}>@${s}</option>`).join('')}
                </select>
            </div>
            <div class="malla-row">
                <span class="malla-spacer"></span>
                <span class="malla-label">H</span>
                <select class="edit-diameter-h" title="φ Horizontal">
                    ${[6,8,10,12,16].map(d => `<option value="${d}" ${pier?.diameter_h === d ? 'selected' : ''}>φ${d}</option>`).join('')}
                </select>
                <select class="edit-spacing-h" title="@ Horizontal">
                    ${[100,125,150,175,200,250,300].map(s => `<option value="${s}" ${pier?.spacing_h === s ? 'selected' : ''}>@${s}</option>`).join('')}
                </select>
            </div>
        `;
        return td;
    }

    createBordeCell(pier, pierKey) {
        const nEdgeBars = pier?.n_edge_bars || 2;
        const stirrupsDisabled = nEdgeBars <= 2;

        const td = document.createElement('td');
        td.className = 'borde-cell';
        td.dataset.pierKey = pierKey;

        td.innerHTML = `
            <div class="borde-row">
                <select class="edit-n-edge" title="Nº barras borde">
                    ${[2,4,6,8,10,12].map(n => `<option value="${n}" ${pier?.n_edge_bars === n ? 'selected' : ''}>${n}φ</option>`).join('')}
                </select>
                <select class="edit-edge" title="φ Borde">
                    ${[12,16,18,20,22,25,28,32].map(d => `<option value="${d}" ${pier?.diameter_edge === d ? 'selected' : ''}>φ${d}</option>`).join('')}
                </select>
            </div>
            <div class="borde-row borde-estribos">
                <span class="borde-label">E</span>
                <select class="edit-stirrup-d" title="φ Estribo" ${stirrupsDisabled ? 'disabled' : ''}>
                    ${[8,10,12].map(d => `<option value="${d}" ${pier?.stirrup_diameter === d ? 'selected' : ''}>E${d}</option>`).join('')}
                </select>
                <select class="edit-stirrup-s" title="@ Estribo" ${stirrupsDisabled ? 'disabled' : ''}>
                    ${[75,100,125,150,200].map(s => `<option value="${s}" ${pier?.stirrup_spacing === s ? 'selected' : ''}>@${s}</option>`).join('')}
                </select>
            </div>
        `;
        return td;
    }

    createVigaCell(pierKey, side) {
        const isCustom = this.customBeamPiers.has(pierKey);
        const beam = this.getBeamConfig(pierKey, side);

        const td = document.createElement('td');
        td.className = `viga-cell ${isCustom ? '' : 'locked'}`;
        td.dataset.pierKey = pierKey;
        td.dataset.side = side;

        td.innerHTML = `
            <div class="viga-row">
                <select class="edit-viga-width-${side}" title="Ancho (mm)">
                    <option value="0">-</option>
                    ${[150,200,250,300].map(w => `<option value="${w}" ${w === beam.width ? 'selected' : ''}>${w}</option>`).join('')}
                </select>
                <span>×</span>
                <select class="edit-viga-height-${side}" title="Alto (mm)">
                    <option value="0">-</option>
                    ${[400,500,600,700,800].map(h => `<option value="${h}" ${h === beam.height ? 'selected' : ''}>${h}</option>`).join('')}
                </select>
            </div>
            <div class="viga-row">
                <select class="edit-viga-nbars-${side}" title="Nº barras">
                    ${[2,3,4,5,6].map(n => `<option value="${n}" ${n === beam.nbars ? 'selected' : ''}>${n}</option>`).join('')}
                </select>
                <select class="edit-viga-diam-${side}" title="φ barras">
                    ${[12,16,18,20,22,25].map(d => `<option value="${d}" ${d === beam.diam ? 'selected' : ''}>φ${d}</option>`).join('')}
                </select>
            </div>
            <div class="viga-row">
                <span>L=</span>
                <select class="edit-viga-ln-${side}" title="Largo libre (mm)">
                    ${[1000,1200,1500,1800,2000,2500].map(l => `<option value="${l}" ${l === beam.ln ? 'selected' : ''}>${l}</option>`).join('')}
                </select>
            </div>
            ${side === 'der' ? `<button class="btn-toggle-beam ${isCustom ? 'unlocked' : ''}" data-pier="${pierKey}" title="${isCustom ? 'Volver a estándar' : 'Especificar vigas'}">${isCustom ? '✓' : '⚙'}</button>` : ''}
        `;

        // Agregar event listener al botón de toggle (solo en lado derecho)
        if (side === 'der') {
            const btn = td.querySelector('.btn-toggle-beam');
            btn?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.togglePierBeamLock(pierKey);
            });
        }

        // Agregar event listeners para guardar cambios si está desbloqueado
        if (isCustom) {
            td.querySelectorAll('select').forEach(select => {
                select.addEventListener('change', () => this.onBeamChange(pierKey, side));
            });
        }

        return td;
    }

    /**
     * Obtiene la configuración de viga para un pier/lado.
     */
    getBeamConfig(pierKey, side) {
        // Si tiene config personalizada, usarla
        if (this.customBeamPiers.has(pierKey) && this.pierBeamConfigs[pierKey]?.[side]) {
            return this.pierBeamConfigs[pierKey][side];
        }
        // Si no, usar la estándar
        return this.standardBeam;
    }

    /**
     * Alterna el estado bloqueado/desbloqueado de vigas de un pier.
     */
    togglePierBeamLock(pierKey) {
        if (this.customBeamPiers.has(pierKey)) {
            // Volver a estándar
            this.customBeamPiers.delete(pierKey);
            delete this.pierBeamConfigs[pierKey];
        } else {
            // Desbloquear - inicializar con valores actuales (estándar)
            this.customBeamPiers.add(pierKey);
            this.pierBeamConfigs[pierKey] = {
                izq: { ...this.standardBeam },
                der: { ...this.standardBeam }
            };
        }

        // Re-renderizar las celdas de viga de este pier
        this.updatePierBeamCells(pierKey);
    }

    /**
     * Actualiza las celdas de viga de un pier específico.
     */
    updatePierBeamCells(pierKey) {
        const row = document.querySelector(`tr[data-pier-key="${pierKey}"]`);
        if (!row) return;

        // Encontrar las celdas de viga (posiciones 4 y 5)
        const cells = row.querySelectorAll('.viga-cell');
        if (cells.length >= 2) {
            const newIzq = this.createVigaCell(pierKey, 'izq');
            const newDer = this.createVigaCell(pierKey, 'der');
            cells[0].replaceWith(newIzq);
            cells[1].replaceWith(newDer);
        }
    }

    /**
     * Maneja cambios en los selects de viga.
     */
    onBeamChange(pierKey, side) {
        const row = document.querySelector(`tr[data-pier-key="${pierKey}"]`);
        if (!row) return;

        const cell = row.querySelector(`.viga-cell[data-side="${side}"]`);
        if (!cell) return;

        // Leer valores actuales
        const width = parseInt(cell.querySelector(`.edit-viga-width-${side}`)?.value) || 0;
        const height = parseInt(cell.querySelector(`.edit-viga-height-${side}`)?.value) || 0;
        const ln = parseInt(cell.querySelector(`.edit-viga-ln-${side}`)?.value) || 1500;
        const nbars = parseInt(cell.querySelector(`.edit-viga-nbars-${side}`)?.value) || 2;
        const diam = parseInt(cell.querySelector(`.edit-viga-diam-${side}`)?.value) || 12;

        // Guardar en config local
        if (!this.pierBeamConfigs[pierKey]) {
            this.pierBeamConfigs[pierKey] = { izq: { ...this.standardBeam }, der: { ...this.standardBeam } };
        }
        this.pierBeamConfigs[pierKey][side] = { width, height, ln, nbars, diam };

        // Enviar al backend
        this.savePierBeamConfig(pierKey);
    }

    /**
     * Guarda la configuración de viga de un pier en el backend.
     */
    async savePierBeamConfig(pierKey) {
        const config = this.pierBeamConfigs[pierKey];
        if (!config) return;

        try {
            await this.page.api.setPierBeam(this.sessionId, pierKey, config);
        } catch (error) {
            console.error('Error guardando config de viga:', error);
        }
    }

    /**
     * Actualiza la viga estándar y propaga a piers bloqueados.
     */
    updateStandardBeam(beam) {
        this.standardBeam = { ...beam };

        // Actualizar todas las celdas de viga bloqueadas
        document.querySelectorAll('.viga-cell.locked').forEach(cell => {
            const pierKey = cell.dataset.pierKey;
            const side = cell.dataset.side;
            const newCell = this.createVigaCell(pierKey, side);
            cell.replaceWith(newCell);
        });

        // Guardar en backend
        this.saveStandardBeam();
    }

    /**
     * Guarda la viga estándar en el backend.
     */
    async saveStandardBeam() {
        try {
            await this.page.api.setDefaultBeam(this.sessionId, this.standardBeam);
        } catch (error) {
            console.error('Error guardando viga estándar:', error);
        }
    }

    createFlexureSfCell(result) {
        const hasTension = result.flexure.has_tension || false;
        const tensionCombos = result.flexure.tension_combos || 0;

        const td = document.createElement('td');
        td.className = `fs-value ${this.getFsClass(result.flexure.sf)}`;

        let tensionWarning = '';
        if (hasTension) {
            tensionWarning = `<span class="tension-warning" title="${tensionCombos} combinación(es) con tracción (Pu<0)">⚡${tensionCombos}</span>`;
        }

        td.innerHTML = `
            <span class="fs-number">${result.flexure.sf}</span>${tensionWarning}
            <span class="critical-combo">${this.truncateCombo(result.flexure.critical_combo)}</span>
        `;
        return td;
    }

    createFlexureCapCell(result) {
        const sl = result.slenderness || {};
        const slenderClass = sl.is_slender ? 'slender-warn' : '';
        const slenderInfo = sl.is_slender ? `λ=${sl.lambda} (-${sl.reduction_pct}%)` : `λ=${sl.lambda || 0}`;
        const exceedsAxial = result.flexure.exceeds_axial || false;

        const td = document.createElement('td');
        td.className = 'capacity-cell';

        if (exceedsAxial) {
            // Pu excede φPn,max - mostrar advertencia clara
            td.innerHTML = `
                <span class="capacity-line axial-exceeded">⚠️ Pu=${result.flexure.Pu}t > φPn=${result.flexure.phi_Pn_max}t</span>
                <span class="capacity-line">Mu=${result.flexure.Mu}t-m</span>
                <span class="capacity-line capacity-ref">φMn₀=${result.flexure.phi_Mn_0}t-m</span>
                <span class="slenderness-info ${slenderClass}">${slenderInfo}</span>
            `;
        } else {
            td.innerHTML = `
                <span class="capacity-line">φMn(Pu)=${result.flexure.phi_Mn_at_Pu}t-m</span>
                <span class="capacity-line">Mu=${result.flexure.Mu}t-m</span>
                <span class="capacity-line capacity-ref">φMn₀=${result.flexure.phi_Mn_0}t-m</span>
                <span class="slenderness-info ${slenderClass}">${slenderInfo}</span>
            `;
        }
        return td;
    }

    createShearSfCell(result) {
        const shearType = result.shear.formula_type === 'column' ? 'COL' : 'MURO';
        const shearTitle = result.shear.formula_type === 'column'
            ? 'Fórmula COLUMNA (ACI 22.5)'
            : 'Fórmula MURO (ACI 18.10.4)';

        const td = document.createElement('td');
        td.className = `fs-value ${this.getFsClass(result.shear.sf)}`;
        td.innerHTML = `
            <span class="fs-number">${result.shear.sf}</span>
            <span class="critical-combo">${this.truncateCombo(result.shear.critical_combo)}</span>
            <span class="formula-tag formula-${result.shear.formula_type}" title="${shearTitle}">${shearType}</span>
        `;
        return td;
    }

    createShearCapCell(result) {
        const td = document.createElement('td');
        td.className = 'capacity-cell';
        td.innerHTML = `
            <span class="capacity-line">Vc=${result.shear.Vc}t + Vs=${result.shear.Vs}t</span>
            <span class="capacity-line">φVn=${result.shear.phi_Vn_2}t</span>
            <span class="dcr-info">DCR: ${this.formatDcr(result.shear.dcr_combined)} (Vu=${result.shear.Vu_2}t)</span>
        `;
        return td;
    }

    createProposalCell(result, pierKey) {
        const proposal = result.design_proposal;
        const hasProposal = proposal && proposal.has_proposal;

        const td = document.createElement('td');
        td.className = `proposal-cell ${hasProposal ? 'has-proposal' : ''}`;
        td.dataset.pierKey = pierKey;

        if (hasProposal) {
            td.innerHTML = `
                <div class="proposal-info">
                    <span class="proposal-mode proposal-mode-${proposal.failure_mode}">${this.getFailureModeLabel(proposal.failure_mode)}</span>
                    <span class="proposal-desc">${proposal.description}</span>
                    <span class="proposal-sf ${proposal.success ? 'proposal-success' : 'proposal-fail'}">
                        SF: ${proposal.sf_original.toFixed(2)} → ${proposal.sf_proposed.toFixed(2)}
                    </span>
                </div>
                <div class="proposal-actions">
                    <button class="view-proposal-btn" data-pier-key="${pierKey}" title="Ver sección propuesta">🔲</button>
                    <button class="apply-proposal-btn" data-pier-key="${pierKey}" title="Aplicar propuesta">✓</button>
                </div>
            `;
        } else {
            td.innerHTML = '<span class="no-proposal">-</span>';
        }
        return td;
    }

    createActionsCell(result, pierKey, isExpanded) {
        const td = document.createElement('td');
        td.className = 'actions-cell';
        td.innerHTML = `
            <div class="action-buttons-grid">
                <button class="action-btn ${isExpanded ? 'active' : ''}" data-action="expand" title="Ver combinaciones">
                    <span class="expand-icon">▶</span>
                </button>
                <button class="action-btn" data-action="section" title="Ver sección">🔲</button>
                <button class="action-btn" data-action="info" title="Ver capacidades">ℹ️</button>
                ${result.pm_plot
                    ? `<button class="action-btn" data-action="diagram" title="Diagrama P-M">📊</button>`
                    : `<button class="action-btn" disabled style="visibility:hidden">-</button>`}
            </div>
        `;
        return td;
    }

    // =========================================================================
    // Event Handlers
    // =========================================================================

    attachRowEventHandlers(row, pierKey, result) {
        const pierLabel = `${result.story} - ${result.pier_label}`;

        // Botones de acción
        row.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                if (action === 'expand') this.toggleExpand(pierKey);
                else if (action === 'section') this.page.showSectionDiagram(pierKey, pierLabel);
                else if (action === 'info') this.page.showPierDetails(pierKey, pierLabel);
                else if (action === 'diagram') this.page.plotModal.open(pierKey, pierLabel, this.plotsCache[pierKey]);
            });
        });

        // Edición de malla
        row.querySelectorAll('.malla-cell select').forEach(select => {
            select.addEventListener('change', () => this.saveInlineEdit(row, pierKey));
        });

        // Edición de borde
        row.querySelectorAll('.borde-cell select').forEach(select => {
            select.addEventListener('change', () => {
                if (select.classList.contains('edit-n-edge')) this.updateStirrupsState(row);
                this.saveInlineEdit(row, pierKey);
            });
        });

        // Edición de vigas
        row.querySelectorAll('.viga-cell select').forEach(select => {
            select.addEventListener('change', () => this.saveInlineEdit(row, pierKey));
        });

        // Ver sección propuesta
        const viewProposalBtn = row.querySelector('.view-proposal-btn');
        if (viewProposalBtn) {
            viewProposalBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const pierLabel = `${result.story} - ${result.pier_label}`;
                const proposedConfig = this.getProposedConfig(result.design_proposal);
                this.page.showProposedSectionDiagram(pierKey, pierLabel, proposedConfig);
            });
        }

        // Aplicar propuesta
        const applyBtn = row.querySelector('.apply-proposal-btn');
        if (applyBtn) {
            applyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.applyProposal(pierKey, result.design_proposal);
            });
        }
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

    // =========================================================================
    // Filas de Combinaciones
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
            <td class="fs-value ${this.getFsClass(combo.flexure_sf)}">${combo.flexure_sf}</td>
            <td></td>
            <td class="fs-value ${this.getFsClass(comboShearDisplay)}">${comboShearDisplay}</td>
            <td class="combo-forces-cell">V2=${combo.V2} | V3=${combo.V3} | DCR: ${this.formatDcr(dcrCombined)}</td>
            <td></td>
            <td class="actions-cell"><button class="action-btn" data-action="diagram-combo">📊</button></td>
        `;

        tr.querySelector('[data-action="diagram-combo"]')?.addEventListener('click', (e) => {
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
            this.expandedPiers.delete(pierKey);
            pierRow.classList.remove('expanded');
            comboRows.forEach(row => row.style.display = 'none');
        } else {
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
                resultsTable.querySelectorAll(`.combo-row[data-pier-key="${pierKey}"]`).forEach(r => r.remove());

                const pierRow = resultsTable.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
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

        const pierKeys = Array.from(resultsTable.querySelectorAll('.pier-row')).map(r => r.dataset.pierKey);
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

    getFailureModeLabel(mode) {
        return {
            flexure: 'Flexión',
            shear: 'Corte',
            combined: 'Combinado',
            slenderness: 'Esbeltez',
            confinement: 'Confinamiento',
            overdesigned: 'Optimizar'
        }[mode] || mode;
    }

    // =========================================================================
    // Edición y Propuestas
    // =========================================================================

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
