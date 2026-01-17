// app/static/js/tables/cells/ColumnCells.js
/**
 * Celdas específicas para elementos Column (columnas).
 * Incluye: altura, armadura longitudinal, estribos.
 */

const ColumnCells = {
    /**
     * Celda de geometría de columna (similar a pier).
     * Muestra: dimensiones de sección + altura
     * Backend envía: width_mm (depth), thickness_mm (width), height_mm
     */
    createGeometryCell(result) {
        const geom = result.geometry || {};

        // Usar dimensiones pre-formateadas del backend si están disponibles
        let sectionCm;
        if (result.dimensions_display) {
            sectionCm = result.dimensions_display;
        } else {
            // Fallback: usar metersToCm de Utils.js
            const depthCm = metersToCm(geom.width_m);
            const widthCm = metersToCm(geom.thickness_m);
            sectionCm = `${depthCm} × ${widthCm} cm`;
        }

        // Altura en metros
        const heightM = geom.height_m || 0;

        const td = document.createElement('td');
        td.className = 'geometry-cell';
        td.title = `Sección: ${sectionCm}\nAltura: ${heightM.toFixed(2)}m`;
        td.innerHTML = `
            <span class="geom-dims">${sectionCm}</span>
            <span class="geom-hwcs">altura=${heightM.toFixed(1)}m</span>
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
     * Celda de estribos o trabas.
     * @param {Object} result - Resultado del elemento
     * @param {string} colKey - Key del elemento
     * @param {boolean} disabled - Si true, muestra estribos deshabilitados (para STRUT 1x1)
     */
    createStirrupsCell(result, colKey, disabled = false) {
        const reinf = result.reinforcement || {};
        const hasCrossties = reinf.has_crossties || false;
        const td = document.createElement('td');
        td.className = 'stirrups-cell' + (disabled ? ' strut-disabled' : '') + (hasCrossties ? ' crossties' : '');
        td.dataset.colKey = colKey;

        if (disabled) {
            // STRUT 1x1: sin estribos (no confinado)
            td.innerHTML = `
                <div class="stirrup-row">
                    <span class="disabled-label">Sin estribos</span>
                </div>
                <div class="stirrup-row">
                    <span class="disabled-note">(no confinado)</span>
                </div>
            `;
        } else if (hasCrossties) {
            // Trabas: 1 rama en alguna dirección (no confinado)
            // Formato compacto: Tr + T10 en fila 1, @150 + (no conf) en fila 2
            td.innerHTML = `
                <div class="stirrup-row">
                    <span class="stirrup-label">Tr</span>
                    <select class="edit-stirrup-d" title="φ Traba">
                        ${StructuralConstants.generateDiameterOptions('estribos', reinf.stirrup_diameter, 'T')}
                    </select>
                    <select class="edit-stirrup-s" title="@ Traba">
                        ${StructuralConstants.generateSpacingOptions('columnas', reinf.stirrup_spacing)}
                    </select>
                </div>
                <div class="stirrup-row">
                    <span class="disabled-note">(no confinado)</span>
                </div>
            `;
        } else {
            // Estribos normales (confinado)
            // Formato compacto: E + E10 en fila 1, @150 en fila 2
            td.innerHTML = `
                <div class="stirrup-row">
                    <span class="stirrup-label">E</span>
                    <select class="edit-stirrup-d" title="φ Estribo">
                        ${StructuralConstants.generateDiameterOptions('estribos', reinf.stirrup_diameter, 'E')}
                    </select>
                    <select class="edit-stirrup-s" title="@ Estribo">
                        ${StructuralConstants.generateSpacingOptions('columnas', reinf.stirrup_spacing)}
                    </select>
                </div>
            `;
        }
        return td;
    }
};
