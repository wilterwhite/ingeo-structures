// app/static/js/tables/cells/BeamCells.js
/**
 * Celdas específicas para elementos Beam (VIGA y VCAP).
 *
 * Tanto BEAM como DROP_BEAM usan el mismo formato de armadura:
 * barras top/bottom + estribos.
 * Se diferencian por el badge: "VIGA" vs "VCAP".
 */

const BeamCells = {
    // =========================================================================
    // Beam (Viga) - Usado por BEAM y DROP_BEAM
    // =========================================================================

    createBeamInfoCell(result) {
        const td = document.createElement('td');
        td.className = 'pier-info-cell';

        // DROP_BEAM usa badge "VCAP", BEAM usa "VIGA"
        const isDropBeam = result.element_type === 'drop_beam';
        const badge = isDropBeam ? 'VCAP' : 'VIGA';
        const badgeClass = isDropBeam ? 'type-drop_beam' : 'type-beam';

        td.innerHTML = `
            <span class="element-type-badge ${badgeClass}">${badge}</span>
            <span class="pier-name">${result.label || result.pier_label || ''}</span>
            <span class="story-badge">${result.story || ''}</span>
        `;
        return td;
    },

    createBeamSectionCell(result) {
        const td = document.createElement('td');
        td.className = 'geometry-cell';
        const geom = result.geometry || {};
        // Usar dimensiones pre-formateadas del backend si están disponibles
        if (result.dimensions_display) {
            td.innerHTML = result.dimensions_display;
            td.title = `Sección: ${result.dimensions_display}`;
        } else {
            // Fallback: usar metersToCm de Utils.js
            const width = metersToCm(geom.width_m);
            const thickness = metersToCm(geom.thickness_m);
            td.innerHTML = `${width}×${thickness} cm`;
            td.title = `Sección: ${width}×${thickness} cm`;
        }
        return td;
    },

    createBeamLengthCell(result) {
        const td = document.createElement('td');
        td.className = 'length-cell';
        const length_m = (result.geometry?.length_m || 0).toFixed(2);
        td.textContent = `${length_m} m`;
        return td;
    },

    createBeamTopReinfCell(result, beamKey) {
        const td = document.createElement('td');
        td.className = 'beam-reinf-cell top-reinf-cell';
        td.dataset.beamKey = beamKey;
        const reinf = result.reinforcement || {};

        td.innerHTML = `
            <div class="reinf-row">
                <span class="reinf-label">Sup:</span>
                <select class="edit-beam-n-top" title="Nº barras superiores">
                    ${StructuralConstants.generateOptions('beam_bar_counts', reinf.n_bars_top || 3)}
                </select>
                <select class="edit-beam-diam-top" title="φ Superior">
                    ${StructuralConstants.generateDiameterOptions('vigas', reinf.diameter_top || 16)}
                </select>
            </div>
        `;
        td.title = `As top = ${reinf.As_top_mm2 || 0} mm²`;
        return td;
    },

    createBeamBottomReinfCell(result, beamKey) {
        const td = document.createElement('td');
        td.className = 'beam-reinf-cell bottom-reinf-cell';
        td.dataset.beamKey = beamKey;
        const reinf = result.reinforcement || {};

        td.innerHTML = `
            <div class="reinf-row">
                <span class="reinf-label">Inf:</span>
                <select class="edit-beam-n-bot" title="Nº barras inferiores">
                    ${StructuralConstants.generateOptions('beam_bar_counts', reinf.n_bars_bottom || 3)}
                </select>
                <select class="edit-beam-diam-bot" title="φ Inferior">
                    ${StructuralConstants.generateDiameterOptions('vigas', reinf.diameter_bottom || 16)}
                </select>
            </div>
        `;
        td.title = `As bottom = ${reinf.As_bottom_mm2 || 0} mm²`;
        return td;
    },

    createBeamStirrupsCell(result, beamKey) {
        const td = document.createElement('td');
        td.className = 'beam-stirrups-cell';
        td.dataset.beamKey = beamKey;
        const reinf = result.reinforcement || {};

        td.innerHTML = `
            <div class="stirrup-row">
                <select class="edit-beam-stirrup-legs" title="Ramas">
                    ${StructuralConstants.generateOptions('stirrup_legs', reinf.n_stirrup_legs || 2, 'R')}
                </select>
                <select class="edit-beam-stirrup-d" title="φ Estribo">
                    ${StructuralConstants.generateDiameterOptions('estribos', reinf.stirrup_diameter || 10, 'E')}
                </select>
                <select class="edit-beam-stirrup-s" title="@ Estribo">
                    ${StructuralConstants.generateSpacingOptions('estribos', reinf.stirrup_spacing || 150)}
                </select>
            </div>
        `;
        td.title = `Av = ${reinf.Av_mm2 || 0} mm²`;
        return td;
    },

    createBeamLateralCell(result, beamKey) {
        const td = document.createElement('td');
        td.className = 'beam-lateral-cell';
        td.dataset.beamKey = beamKey;
        const reinf = result.reinforcement || {};

        // 0 = sin laterales
        const diamLateral = reinf.diameter_lateral || 0;
        const spacingLateral = reinf.spacing_lateral || 200;

        td.innerHTML = `
            <div class="lateral-row">
                <select class="edit-beam-diam-lateral" title="φ Laterales (0=sin)">
                    ${StructuralConstants.generateDiameterOptions('laterales', diamLateral)}
                </select>
                <select class="edit-beam-spacing-lateral" title="@ Laterales">
                    ${StructuralConstants.generateSpacingOptions('laterales', spacingLateral)}
                </select>
            </div>
        `;
        td.title = diamLateral > 0
            ? `Laterales: φ${diamLateral}@${spacingLateral}`
            : 'Sin armadura lateral';
        return td;
    }
};
