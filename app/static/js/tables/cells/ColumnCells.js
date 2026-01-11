// app/static/js/tables/cells/ColumnCells.js
/**
 * Celdas específicas para elementos Column (columnas).
 * Incluye: altura, armadura longitudinal, estribos.
 */

const ColumnCells = {
    /**
     * Celda de altura de columna.
     */
    createHeightCell(result) {
        const td = document.createElement('td');
        td.className = 'height-cell';
        td.innerHTML = `
            <span class="height-value">${result.geometry?.height_m?.toFixed(2) || 0}m</span>
            <span class="height-label">altura</span>
        `;
        return td;
    },

    /**
     * Celda de armadura longitudinal.
     */
    createLongitudinalCell(result, colKey) {
        const reinf = result.reinforcement || {};
        const td = document.createElement('td');
        td.className = 'longitudinal-cell';
        td.dataset.colKey = colKey;

        td.innerHTML = `
            <div class="long-row">
                <span class="long-label">Long:</span>
                <select class="edit-n-bars" title="Barras por cara">
                    ${StructuralConstants.generateOptions('column_bars_per_face', reinf.n_bars_depth)}
                </select>
                <span>×</span>
                <select class="edit-n-bars-w" title="Barras por cara (ancho)">
                    ${StructuralConstants.generateOptions('column_bars_per_face', reinf.n_bars_width)}
                </select>
            </div>
            <div class="long-row">
                <select class="edit-diam-long" title="φ Longitudinal">
                    ${StructuralConstants.generateDiameterOptions('longitudinal', reinf.diameter_long)}
                </select>
                <span class="as-info">${reinf.n_total_bars || 0}φ = ${(reinf.As_longitudinal_mm2/100).toFixed(0)}cm²</span>
            </div>
        `;
        return td;
    },

    /**
     * Celda de estribos.
     */
    createStirrupsCell(result, colKey) {
        const reinf = result.reinforcement || {};
        const td = document.createElement('td');
        td.className = 'stirrups-cell';
        td.dataset.colKey = colKey;

        td.innerHTML = `
            <div class="stirrup-row">
                <span class="stirrup-label">Estribo:</span>
                <select class="edit-stirrup-d" title="φ Estribo">
                    ${StructuralConstants.generateDiameterOptions('estribos', reinf.stirrup_diameter, 'E')}
                </select>
            </div>
            <div class="stirrup-row">
                <select class="edit-stirrup-s" title="@ Estribo">
                    ${StructuralConstants.generateSpacingOptions('columnas', reinf.stirrup_spacing)}
                </select>
            </div>
        `;
        return td;
    }
};
