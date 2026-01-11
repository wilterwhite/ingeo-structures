// app/static/js/tables/cells/PierCells.js
/**
 * Celdas específicas para elementos Pier (muros).
 * Incluye: geometría, malla, borde, propuesta.
 */

const PierCells = {
    /**
     * Celda de geometría del pier.
     */
    createGeometryCell(result) {
        const geom = result.geometry || {};
        const cont = result.wall_continuity || {};

        const sectionCm = formatSectionDimensions(geom.width_m, geom.thickness_m, 'cm');

        const hwcsM = cont.hwcs_m || geom.height_m || 0;
        const hwcsLw = cont.hwcs_lw || 0;
        const nStories = cont.n_stories || 1;
        const storiesText = nStories > 1 ? `${nStories} pisos` : '1 piso';

        const td = document.createElement('td');
        td.className = 'geometry-cell';
        td.title = `hwcs/lw = ${hwcsLw.toFixed(2)}\n${storiesText}`;
        td.innerHTML = `
            <span class="geom-dims">${sectionCm} cm</span>
            <span class="geom-hwcs">hwcs=${hwcsM.toFixed(1)}m</span>
        `;
        return td;
    },

    /**
     * Celda de armadura de malla.
     */
    createMallaCell(pier, pierKey, result) {
        const td = document.createElement('td');
        td.className = 'malla-cell';
        td.dataset.pierKey = pierKey;

        const reinf = result.reinforcement || {};
        const rhoMeshVok = reinf.rho_mesh_v_ok !== false;
        const rhoHok = reinf.rho_h_ok !== false;
        const spacingVok = reinf.spacing_v_ok !== false;
        const spacingHok = reinf.spacing_h_ok !== false;

        // Advertencias fila V
        const vHasWarning = !rhoMeshVok || !spacingVok;
        const vWarningClass = vHasWarning ? 'rho-warning' : '';
        let vWarnings = [];
        if (!rhoMeshVok) vWarnings.push(`ρ_malla < ${(reinf.rho_min || 0.0025) * 100}%`);
        if (!spacingVok) vWarnings.push(`s > ${reinf.max_spacing || 457}mm`);
        const vWarningTitle = vWarnings.length ? `${vWarnings.join(', ')} (§18.10.2.1)` : '';

        // Advertencias fila H
        const hHasWarning = !rhoHok || !spacingHok;
        const hWarningClass = hHasWarning ? 'rho-warning' : '';
        let hWarnings = [];
        if (!rhoHok) hWarnings.push(`ρ < ${(reinf.rho_min || 0.0025) * 100}%`);
        if (!spacingHok) hWarnings.push(`s > ${reinf.max_spacing || 457}mm`);
        const hWarningTitle = hWarnings.length ? `${hWarnings.join(', ')} (§18.10.2.1)` : '';

        td.innerHTML = `
            <div class="malla-row ${vWarningClass}" ${vHasWarning ? `title="${vWarningTitle}"` : ''}>
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
                ${vHasWarning ? '<span class="rho-warn-icon" title="' + vWarningTitle + '">⚠</span>' : ''}
            </div>
            <div class="malla-row ${hWarningClass}" ${hHasWarning ? `title="${hWarningTitle}"` : ''}>
                <span class="malla-spacer"></span>
                <span class="malla-label">H</span>
                <select class="edit-diameter-h" title="φ Horizontal">
                    ${generateDiameterOptions(DIAMETERS.malla, pier?.diameter_h)}
                </select>
                <select class="edit-spacing-h" title="@ Horizontal">
                    ${generateSpacingOptions(SPACINGS.malla, pier?.spacing_h)}
                </select>
                ${hHasWarning ? '<span class="rho-warn-icon" title="' + hWarningTitle + '">⚠</span>' : ''}
            </div>
        `;
        return td;
    },

    /**
     * Celda de armadura de borde.
     */
    createBordeCell(pier, pierKey, result) {
        const nEdgeBars = pier?.n_edge_bars || 2;
        const stirrupsDisabled = nEdgeBars <= 2;

        const reinf = result?.reinforcement || {};
        const rhoVok = reinf.rho_v_ok !== false;
        const warningClass = !rhoVok ? 'rho-warning' : '';
        const warningTitle = !rhoVok ? `Cuantía vertical < ${(reinf.rho_min || 0.0025) * 100}% mínimo (§11.6.2)` : '';

        const td = document.createElement('td');
        td.className = 'borde-cell';
        td.dataset.pierKey = pierKey;

        td.innerHTML = `
            <div class="borde-row ${warningClass}" ${!rhoVok ? `title="${warningTitle}"` : ''}>
                <select class="edit-n-edge" title="Nº barras borde">
                    ${generateOptions(EDGE_BAR_COUNTS, pier?.n_edge_bars, 'φ')}
                </select>
                <select class="edit-edge" title="φ Borde">
                    ${generateDiameterOptions(DIAMETERS.borde, pier?.diameter_edge)}
                </select>
                ${!rhoVok ? '<span class="rho-warn-icon" title="ρ_v < mínimo">⚠</span>' : ''}
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
    },

    /**
     * Celda de propuesta de diseño.
     */
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
};
