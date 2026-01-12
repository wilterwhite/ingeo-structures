// app/static/js/tables/cells/BeamCells.js
/**
 * Celdas específicas para elementos Beam y DropBeam.
 * Incluye: info, sección, longitud, armaduras.
 */

const BeamCells = {
    // =========================================================================
    // Drop Beam (Viga Capitel)
    // =========================================================================

    createDropBeamInfoCell(result) {
        const td = document.createElement('td');
        td.className = 'pier-info-cell';
        td.innerHTML = `
            <span class="element-type-badge type-drop_beam">VCAP</span>
            <span class="pier-name">${result.label || result.pier_label || ''}</span>
            <span class="story-badge">${result.story || ''}</span>
        `;
        return td;
    },

    createDropBeamSectionCell(result) {
        const td = document.createElement('td');
        td.className = 'geometry-cell';
        // Usar dimensiones del backend
        const sectionText = getDimensionsDisplay(result);
        td.innerHTML = sectionText;
        td.title = `Sección: ${sectionText}`;
        return td;
    },

    createDropBeamLengthCell(result) {
        const td = document.createElement('td');
        td.className = 'length-cell';
        const length_m = (result.geometry?.length_m || 0).toFixed(2);
        td.textContent = `${length_m}`;
        return td;
    },

    createDropBeamMallaVCell(result, dropBeamKey) {
        const td = document.createElement('td');
        td.className = 'malla-cell malla-v-cell';
        td.dataset.dropBeamKey = dropBeamKey;
        const reinf = result.reinforcement || {};

        td.innerHTML = `
            <div class="malla-row">
                <select class="edit-meshes" title="Mallas">
                    ${StructuralConstants.generateOptions('mesh_counts', reinf.n_meshes || 2, 'M')}
                </select>
                <span class="malla-label">V</span>
                <select class="edit-diameter-v" title="φ Vertical">
                    ${StructuralConstants.generateDiameterOptions('malla', reinf.diameter_v || 12)}
                </select>
                <select class="edit-spacing-v" title="@ Vertical">
                    ${StructuralConstants.generateSpacingOptions('malla', reinf.spacing_v || 200)}
                </select>
            </div>
        `;
        td.title = `ρv=${(reinf.rho_vertical || 0).toFixed(4)}`;
        return td;
    },

    createDropBeamMallaHCell(result, dropBeamKey) {
        const td = document.createElement('td');
        td.className = 'malla-cell malla-h-cell';
        td.dataset.dropBeamKey = dropBeamKey;
        const reinf = result.reinforcement || {};

        td.innerHTML = `
            <div class="malla-row">
                <span class="malla-spacer"></span>
                <span class="malla-label">H</span>
                <select class="edit-diameter-h" title="φ Horizontal">
                    ${StructuralConstants.generateDiameterOptions('malla', reinf.diameter_h || 10)}
                </select>
                <select class="edit-spacing-h" title="@ Horizontal">
                    ${StructuralConstants.generateSpacingOptions('malla', reinf.spacing_h || 200)}
                </select>
            </div>
        `;
        td.title = `ρh=${(reinf.rho_horizontal || 0).toFixed(4)}`;
        return td;
    },

    createDropBeamBordeCell(result, dropBeamKey) {
        const td = document.createElement('td');
        td.className = 'borde-cell';
        td.dataset.dropBeamKey = dropBeamKey;
        const reinf = result.reinforcement || {};

        td.innerHTML = `
            <div class="borde-row">
                <select class="edit-n-edge" title="Nº barras borde">
                    ${StructuralConstants.generateOptions('edge_bar_counts', reinf.n_edge_bars || 4, 'φ')}
                </select>
                <select class="edit-edge" title="φ Borde">
                    ${StructuralConstants.generateDiameterOptions('borde', reinf.diameter_edge || 16)}
                </select>
            </div>
            <div class="borde-row borde-estribos">
                <span class="borde-label">E</span>
                <select class="edit-stirrup-d" title="φ Estribo">
                    ${StructuralConstants.generateDiameterOptions('estribos', reinf.stirrup_diameter || 10, 'E')}
                </select>
                <select class="edit-stirrup-s" title="@ Estribo">
                    ${StructuralConstants.generateSpacingOptions('estribos', reinf.stirrup_spacing || 150)}
                </select>
            </div>
        `;
        td.title = `As borde=${reinf.As_edge_mm2 || 0}mm²`;
        return td;
    },

    // =========================================================================
    // Beam (Viga)
    // =========================================================================

    createBeamInfoCell(result) {
        const td = document.createElement('td');
        td.className = 'pier-info-cell';
        td.innerHTML = `
            <span class="element-type-badge type-beam">VIGA</span>
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
    }
};
