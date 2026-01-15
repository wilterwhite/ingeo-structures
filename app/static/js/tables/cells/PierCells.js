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
        const boundary = result.boundary_element || {};

        const sectionCm = formatSectionDimensions(geom.width_m, geom.thickness_m, 'cm');

        const hwcsM = cont.hwcs_m || geom.height_m || 0;
        const hwcsLw = cont.hwcs_lw || 0;
        const nStories = cont.n_stories || 1;
        const storiesText = nStories > 1 ? `${nStories} pisos` : '1 piso';

        // Verificar si hay warnings de geometría de elementos de borde
        const geoWarnings = boundary.geometry_warnings || [];
        const hasGeoWarning = geoWarnings.length > 0;
        const warningClass = hasGeoWarning ? 'geo-warning' : '';
        const warningIcon = hasGeoWarning
            ? `<span class="geo-warn-icon" title="${geoWarnings.join('\n')}">⚠</span>`
            : '';

        const td = document.createElement('td');
        td.className = `geometry-cell ${warningClass}`;
        td.title = `hwcs/lw = ${hwcsLw.toFixed(2)}\n${storiesText}${hasGeoWarning ? '\n⚠ ' + geoWarnings.join('\n') : ''}`;
        td.innerHTML = `
            <span class="geom-dims">${sectionCm} cm</span>
            <span class="geom-hwcs">hwcs=${hwcsM.toFixed(1)}m ${warningIcon}</span>
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
        const modifiedFields = reinf.modified_fields || [];

        // Usar warnings pre-calculados del backend
        const vWarnings = reinf.warnings_v || [];
        const hWarnings = reinf.warnings_h || [];

        // Determinar si hay warnings
        const vHasWarning = vWarnings.length > 0;
        const hHasWarning = hWarnings.length > 0;
        const vWarningClass = vHasWarning ? 'rho-warning' : '';
        const hWarningClass = hHasWarning ? 'rho-warning' : '';
        const vWarningTitle = vHasWarning ? `${vWarnings.join(', ')} (§18.10.2.1)` : '';
        const hWarningTitle = hHasWarning ? `${hWarnings.join(', ')} (§18.10.2.1)` : '';

        // Clases para campos modificados
        const meshesModified = modifiedFields.includes('n_meshes') ? 'field-modified' : '';
        const diamVModified = modifiedFields.includes('diameter_v') ? 'field-modified' : '';
        const spacingVModified = modifiedFields.includes('spacing_v') ? 'field-modified' : '';
        const diamHModified = modifiedFields.includes('diameter_h') ? 'field-modified' : '';
        const spacingHModified = modifiedFields.includes('spacing_h') ? 'field-modified' : '';

        td.innerHTML = `
            <div class="malla-row ${vWarningClass}" ${vHasWarning ? `title="${vWarningTitle}"` : ''}>
                <select class="edit-meshes ${meshesModified}" title="Mallas">
                    ${StructuralConstants.generateOptions('mesh_counts', pier?.n_meshes, 'M')}
                </select>
                <span class="malla-label">V</span>
                <select class="edit-diameter-v ${diamVModified}" title="φ Vertical">
                    ${StructuralConstants.generateDiameterOptions('malla', pier?.diameter_v)}
                </select>
                <select class="edit-spacing-v ${spacingVModified}" title="@ Vertical">
                    ${StructuralConstants.generateSpacingOptions('malla', pier?.spacing_v)}
                </select>
                ${vHasWarning ? '<span class="rho-warn-icon" title="' + vWarningTitle + '">⚠</span>' : ''}
            </div>
            <div class="malla-row ${hWarningClass}" ${hHasWarning ? `title="${hWarningTitle}"` : ''}>
                <span class="malla-spacer"></span>
                <span class="malla-label">H</span>
                <select class="edit-diameter-h ${diamHModified}" title="φ Horizontal">
                    ${StructuralConstants.generateDiameterOptions('malla', pier?.diameter_h)}
                </select>
                <select class="edit-spacing-h ${spacingHModified}" title="@ Horizontal">
                    ${StructuralConstants.generateSpacingOptions('malla', pier?.spacing_h)}
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
        const rhoVexceedsMax = reinf.rho_v_exceeds_max === true;
        const modifiedFields = reinf.modified_fields || [];

        // Determinar clase de advertencia
        let warningClass = '';
        let warningTitle = '';
        let warningIcon = '';

        if (rhoVexceedsMax) {
            warningClass = 'rho-error';
            warningTitle = `Cuantía vertical > ${(reinf.rho_max || 0.04) * 100}% máximo (§18.10.2.1)`;
            warningIcon = '<span class="rho-warn-icon rho-error-icon" title="ρ_v > máximo">⚠</span>';
        } else if (!rhoVok) {
            warningClass = 'rho-warning';
            warningTitle = `Cuantía vertical < ${(reinf.rho_min || 0.0025) * 100}% mínimo (§11.6.2)`;
            warningIcon = '<span class="rho-warn-icon" title="ρ_v < mínimo">⚠</span>';
        }

        // Clases para campos modificados
        const nEdgeModified = modifiedFields.includes('n_edge_bars') ? 'field-modified' : '';
        const diamEdgeModified = modifiedFields.includes('diameter_edge') ? 'field-modified' : '';
        const stirrupDModified = modifiedFields.includes('stirrup_diameter') ? 'field-modified' : '';
        const stirrupSModified = modifiedFields.includes('stirrup_spacing') ? 'field-modified' : '';

        const td = document.createElement('td');
        td.className = 'borde-cell';
        td.dataset.pierKey = pierKey;

        td.innerHTML = `
            <div class="borde-row ${warningClass}" ${warningTitle ? `title="${warningTitle}"` : ''}>
                <select class="edit-n-edge ${nEdgeModified}" title="Nº barras borde">
                    ${StructuralConstants.generateOptions('edge_bar_counts', pier?.n_edge_bars, 'φ')}
                </select>
                <select class="edit-edge ${diamEdgeModified}" title="φ Borde">
                    ${StructuralConstants.generateDiameterOptions('borde', pier?.diameter_edge)}
                </select>
                ${warningIcon}
            </div>
            <div class="borde-row borde-estribos">
                <span class="borde-label">E</span>
                <select class="edit-stirrup-d ${stirrupDModified}" title="φ Estribo" ${stirrupsDisabled ? 'disabled' : ''}>
                    ${StructuralConstants.generateDiameterOptions('estribos', pier?.stirrup_diameter, 'E')}
                </select>
                <select class="edit-stirrup-s ${stirrupSModified}" title="@ Estribo" ${stirrupsDisabled ? 'disabled' : ''}>
                    ${StructuralConstants.generateSpacingOptions('estribos', pier?.stirrup_spacing)}
                </select>
            </div>
        `;
        return td;
    },

    /**
     * Labels para modos de falla (inline para evitar dependencia externa).
     */
    _failureModeLabels: {
        flexure: 'Flexión',
        shear: 'Corte',
        confinement: 'Confin.',
        slenderness: 'Esbeltez',
        combined: 'Combinado',
        overdesigned: 'Sobred.',
        column_min_thickness: 'Espesor',
        none: '-'
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
            const modeLabel = this._failureModeLabels[proposal.failure_mode] || proposal.failure_mode;
            td.innerHTML = `
                <div class="proposal-info">
                    <span class="proposal-mode proposal-mode-${proposal.failure_mode}">${modeLabel}</span>
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
    },

    /**
     * Celda de categoría sísmica del elemento.
     * Permite cambiar entre SPECIAL, INTERMEDIATE, ORDINARY, NON_SFRS.
     */
    createSeismicCategoryCell(result, pierKey) {
        const td = document.createElement('td');
        td.className = 'seismic-category-cell';
        td.dataset.pierKey = pierKey;

        // Obtener categoría actual (null/'' = usar categoría global)
        const currentCategory = result.seismic_category || '';

        // Obtener categoría global para mostrar en la opción por defecto
        const globalCategory = document.getElementById('seismic-category')?.value || 'SPECIAL';
        const globalLabel = `(${globalCategory})`;

        td.innerHTML = `
            <select class="edit-seismic-category" title="Categoría sísmica (actual: ${globalCategory})">
                <option value="" ${currentCategory === '' ? 'selected' : ''}>${globalLabel}</option>
                <option value="SPECIAL" ${currentCategory === 'SPECIAL' ? 'selected' : ''}>Special</option>
                <option value="INTERMEDIATE" ${currentCategory === 'INTERMEDIATE' ? 'selected' : ''}>Intermediate</option>
                <option value="ORDINARY" ${currentCategory === 'ORDINARY' ? 'selected' : ''}>Ordinary</option>
                <option value="NON_SFRS" ${currentCategory === 'NON_SFRS' ? 'selected' : ''}>Non-SFRS</option>
            </select>
        `;
        return td;
    }
};
