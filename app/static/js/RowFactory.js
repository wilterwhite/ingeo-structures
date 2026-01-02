// app/static/js/RowFactory.js
/**
 * Factory para crear filas de la tabla de resultados.
 * Soporta piers y columnas con celdas diferenciadas.
 * Usa Constants.js y Utils.js para valores y funciones compartidas.
 */

class RowFactory {
    constructor(resultsTable) {
        this.table = resultsTable;
    }

    // =========================================================================
    // Creación de Fila Principal
    // =========================================================================

    createRow(result, elementKey) {
        const elementType = result.element_type || 'pier';
        const isExpanded = this.table.expandedPiers.has(elementKey);

        const row = document.createElement('tr');
        row.className = `pier-row ${elementType}-type ${isExpanded ? 'expanded' : ''}`;
        row.dataset.pierKey = elementKey;
        row.dataset.elementType = elementType;

        if (elementType === 'column') {
            this._createColumnRow(row, result, elementKey, isExpanded);
        } else {
            this._createPierRow(row, result, elementKey, isExpanded);
        }

        return row;
    }

    _createPierRow(row, result, pierKey, isExpanded) {
        const pier = this.table.piersData.find(p => p.key === pierKey);

        row.appendChild(this.createInfoCell(result, 'pier'));
        row.appendChild(this.createHwcsCell(result));
        row.appendChild(this.createMallaCell(pier, pierKey, result));
        row.appendChild(this.createBordeCell(pier, pierKey));
        row.appendChild(this.table.createVigaCell(pierKey, 'izq'));
        row.appendChild(this.table.createVigaCell(pierKey, 'der'));
        row.appendChild(this.createFlexureSfCell(result));
        row.appendChild(this.createFlexureCapCell(result));
        row.appendChild(this.createShearSfCell(result));
        row.appendChild(this.createShearCapCell(result));
        row.appendChild(this.createProposalCell(result, pierKey));
        row.appendChild(this.createActionsCell(result, pierKey, isExpanded));

        this.attachRowEventHandlers(row, pierKey, result, 'pier');
    }

    _createColumnRow(row, result, colKey, isExpanded) {
        row.appendChild(this.createInfoCell(result, 'column'));
        row.appendChild(this.createColumnHeightCell(result));
        row.appendChild(this.createLongitudinalCell(result, colKey));
        row.appendChild(this.createStirrupsCell(result, colKey));
        row.appendChild(this.createEmptyCell());
        row.appendChild(this.createEmptyCell());
        row.appendChild(this.createFlexureSfCell(result));
        row.appendChild(this.createFlexureCapCell(result));
        row.appendChild(this.createShearSfCell(result));
        row.appendChild(this.createShearCapCell(result));
        row.appendChild(this.createEmptyCell());
        row.appendChild(this.createActionsCell(result, colKey, isExpanded, true));

        this.attachRowEventHandlers(row, colKey, result, 'column');
    }

    // =========================================================================
    // Celdas Comunes
    // =========================================================================

    createInfoCell(result, elementType) {
        const td = document.createElement('td');
        td.className = 'pier-info-cell';
        const typeLabel = elementType === 'column' ? 'COL' : 'PIER';
        const typeClass = elementType === 'column' ? 'type-column' : 'type-pier';
        td.innerHTML = `
            <span class="element-type-badge ${typeClass}">${typeLabel}</span>
            <span class="pier-name">${result.pier_label}</span>
            <span class="pier-story">${result.story}</span>
            <span class="pier-dims">${result.geometry.width_m.toFixed(2)}×${result.geometry.thickness_m.toFixed(2)}</span>
        `;
        return td;
    }

    createFlexureSfCell(result) {
        const hasTension = result.flexure?.has_tension || false;
        const tensionCombos = result.flexure?.tension_combos || 0;
        const sf = result.flexure?.sf ?? 0;

        const td = document.createElement('td');
        td.className = `fs-value ${getFsClass(sf)}`;

        let tensionWarning = '';
        if (hasTension) {
            tensionWarning = `<span class="tension-warning" title="${tensionCombos} combinación(es) con tracción">⚡${tensionCombos}</span>`;
        }

        td.innerHTML = `
            <span class="fs-number">${sf}</span>${tensionWarning}
            <span class="critical-combo">${truncateCombo(result.flexure?.critical_combo)}</span>
        `;
        return td;
    }

    createFlexureCapCell(result) {
        const sl = result.slenderness || {};
        const slenderClass = sl.is_slender ? 'slender-warn' : '';
        const slenderInfo = sl.is_slender ? `λ=${sl.lambda} (-${sl.reduction_pct}%)` : `λ=${sl.lambda || 0}`;
        const exceedsAxial = result.flexure?.exceeds_axial || false;

        const td = document.createElement('td');
        td.className = 'capacity-cell';

        if (exceedsAxial) {
            td.innerHTML = `
                <span class="capacity-line axial-exceeded">⚠️ Pu=${result.flexure.Pu}t > φPn=${result.flexure.phi_Pn_max}t</span>
                <span class="capacity-line">Mu=${result.flexure.Mu}t-m</span>
                <span class="capacity-line capacity-ref">φMn₀=${result.flexure.phi_Mn_0}t-m</span>
                <span class="slenderness-info ${slenderClass}">${slenderInfo}</span>
            `;
        } else {
            td.innerHTML = `
                <span class="capacity-line">φMn(Pu)=${result.flexure?.phi_Mn_at_Pu || 0}t-m</span>
                <span class="capacity-line">Mu=${result.flexure?.Mu || 0}t-m</span>
                <span class="capacity-line capacity-ref">φMn₀=${result.flexure?.phi_Mn_0 || 0}t-m</span>
                <span class="slenderness-info ${slenderClass}">${slenderInfo}</span>
            `;
        }
        return td;
    }

    createShearSfCell(result) {
        const formulaType = result.shear?.formula_type || 'wall';
        const shearType = formulaType === 'column' ? 'COL' : 'MURO';
        const shearTitle = formulaType === 'column' ? 'Fórmula COLUMNA (ACI 22.5)' : 'Fórmula MURO (ACI 18.10.4)';

        const td = document.createElement('td');
        td.className = `fs-value ${getFsClass(result.shear?.sf)}`;
        td.innerHTML = `
            <span class="fs-number">${result.shear?.sf || 0}</span>
            <span class="critical-combo">${truncateCombo(result.shear?.critical_combo)}</span>
            <span class="formula-tag formula-${formulaType}" title="${shearTitle}">${shearType}</span>
        `;
        return td;
    }

    createShearCapCell(result) {
        const td = document.createElement('td');
        td.className = 'capacity-cell';
        td.innerHTML = `
            <span class="capacity-line">Vc=${result.shear?.Vc || 0}t + Vs=${result.shear?.Vs || 0}t</span>
            <span class="capacity-line">φVn=${result.shear?.phi_Vn_2 || 0}t</span>
            <span class="dcr-info">DCR: ${formatDcr(result.shear?.dcr_combined)} (Vu=${result.shear?.Vu_2 || 0}t)</span>
        `;
        return td;
    }

    createActionsCell(result, elementKey, isExpanded, isColumn = false) {
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

    createEmptyCell() {
        const td = document.createElement('td');
        td.className = 'empty-cell';
        td.innerHTML = '<span class="na-value">-</span>';
        return td;
    }

    // =========================================================================
    // Celdas Específicas de Pier
    // =========================================================================

    createHwcsCell(result) {
        const cont = result.wall_continuity || {};
        const hwcsM = cont.hwcs_m || result.geometry?.height_m || 0;
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
                    ${generateOptions(MESH_OPTIONS, pier?.n_meshes, 'M')}
                </select>
                <span class="malla-label">V</span>
                <select class="edit-diameter-v" title="φ Vertical">
                    ${generateDiameterOptions(DIAMETERS.malla, pier?.diameter_v)}
                </select>
                <select class="edit-spacing-v" title="@ Vertical">
                    ${generateSpacingOptions(SPACINGS.malla, pier?.spacing_v)}
                </select>
            </div>
            <div class="malla-row">
                <span class="malla-spacer"></span>
                <span class="malla-label">H</span>
                <select class="edit-diameter-h" title="φ Horizontal">
                    ${generateDiameterOptions(DIAMETERS.malla, pier?.diameter_h)}
                </select>
                <select class="edit-spacing-h" title="@ Horizontal">
                    ${generateSpacingOptions(SPACINGS.malla, pier?.spacing_h)}
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
                    ${generateOptions(EDGE_BAR_COUNTS, pier?.n_edge_bars, 'φ')}
                </select>
                <select class="edit-edge" title="φ Borde">
                    ${generateDiameterOptions(DIAMETERS.borde, pier?.diameter_edge)}
                </select>
            </div>
            <div class="borde-row borde-estribos">
                <span class="borde-label">E</span>
                <select class="edit-stirrup-d" title="φ Estribo" ${stirrupsDisabled ? 'disabled' : ''}>
                    ${generateDiameterOptions(DIAMETERS.estribos, pier?.stirrup_diameter, 'E')}
                </select>
                <select class="edit-stirrup-s" title="@ Estribo" ${stirrupsDisabled ? 'disabled' : ''}>
                    ${generateSpacingOptions(SPACINGS.estribos, pier?.stirrup_spacing)}
                </select>
            </div>
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
                    <span class="proposal-mode proposal-mode-${proposal.failure_mode}">${getFailureModeLabel(proposal.failure_mode)}</span>
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

    // =========================================================================
    // Celdas Específicas de Columna
    // =========================================================================

    createColumnHeightCell(result) {
        const td = document.createElement('td');
        td.className = 'height-cell';
        td.innerHTML = `
            <span class="height-value">${result.geometry?.height_m?.toFixed(2) || 0}m</span>
            <span class="height-label">altura</span>
        `;
        return td;
    }

    createLongitudinalCell(result, colKey) {
        const reinf = result.reinforcement || {};
        const td = document.createElement('td');
        td.className = 'longitudinal-cell';
        td.dataset.colKey = colKey;

        td.innerHTML = `
            <div class="long-row">
                <span class="long-label">Long:</span>
                <select class="edit-n-bars" title="Barras por cara">
                    ${generateOptions(COLUMN_BARS_PER_FACE, reinf.n_bars_depth)}
                </select>
                <span>×</span>
                <select class="edit-n-bars-w" title="Barras por cara (ancho)">
                    ${generateOptions(COLUMN_BARS_PER_FACE, reinf.n_bars_width)}
                </select>
            </div>
            <div class="long-row">
                <select class="edit-diam-long" title="φ Longitudinal">
                    ${generateDiameterOptions(DIAMETERS.longitudinal, reinf.diameter_long)}
                </select>
                <span class="as-info">${reinf.n_total_bars || 0}φ = ${(reinf.As_longitudinal_mm2/100).toFixed(0)}cm²</span>
            </div>
        `;
        return td;
    }

    createStirrupsCell(result, colKey) {
        const reinf = result.reinforcement || {};
        const td = document.createElement('td');
        td.className = 'stirrups-cell';
        td.dataset.colKey = colKey;

        td.innerHTML = `
            <div class="stirrup-row">
                <span class="stirrup-label">Estribo:</span>
                <select class="edit-stirrup-d" title="φ Estribo">
                    ${generateDiameterOptions(DIAMETERS.estribos, reinf.stirrup_diameter, 'E')}
                </select>
            </div>
            <div class="stirrup-row">
                <select class="edit-stirrup-s" title="@ Estribo">
                    ${generateSpacingOptions(SPACINGS.columnas, reinf.stirrup_spacing)}
                </select>
            </div>
        `;
        return td;
    }

    // =========================================================================
    // Event Handlers
    // =========================================================================

    attachRowEventHandlers(row, elementKey, result, elementType) {
        const elementLabel = `${result.story} - ${result.pier_label}`;

        row.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                if (action === 'expand') this.table.toggleExpand(elementKey);
                else if (action === 'section') this.table.page.showSectionDiagram(elementKey, elementLabel);
                else if (action === 'info') this.table.page.showPierDetails(elementKey, elementLabel);
                else if (action === 'diagram') this.table.page.plotModal.open(elementKey, elementLabel, this.table.plotsCache[elementKey]);
            });
        });

        if (elementType === 'pier') {
            row.querySelectorAll('.malla-cell select').forEach(select => {
                select.addEventListener('change', () => this.table.saveInlineEdit(row, elementKey));
            });

            row.querySelectorAll('.borde-cell select').forEach(select => {
                select.addEventListener('change', () => {
                    if (select.classList.contains('edit-n-edge')) this.table.updateStirrupsState(row);
                    this.table.saveInlineEdit(row, elementKey);
                });
            });

            row.querySelectorAll('.viga-cell select').forEach(select => {
                select.addEventListener('change', () => this.table.saveInlineEdit(row, elementKey));
            });

            const viewProposalBtn = row.querySelector('.view-proposal-btn');
            if (viewProposalBtn) {
                viewProposalBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const proposedConfig = this.table.getProposedConfig(result.design_proposal);
                    this.table.page.showProposedSectionDiagram(elementKey, elementLabel, proposedConfig);
                });
            }

            const applyBtn = row.querySelector('.apply-proposal-btn');
            if (applyBtn) {
                applyBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.table.applyProposal(elementKey, result.design_proposal);
                });
            }
        }
    }
}
