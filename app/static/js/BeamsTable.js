// app/static/js/BeamsTable.js
/**
 * Módulo para manejo de la tabla de vigas.
 * Muestra resultados de verificación de cortante para vigas.
 * Permite editar la enfierradura de cada viga.
 * Usa Utils.js para funciones compartidas.
 */

// Opciones de diámetros de barras disponibles
const BEAM_DIAMETERS = [8, 10, 12, 16, 18, 20, 22, 25, 28, 32];
const BEAM_N_BARS = [2, 3, 4, 5, 6, 8];
const STIRRUP_SPACINGS = [100, 125, 150, 175, 200, 250, 300];
const STIRRUP_LEGS = [2, 3, 4];

class BeamsTable {
    constructor(page) {
        this.page = page;
        this.beamResults = [];
    }

    // =========================================================================
    // Renderizado
    // =========================================================================

    renderTable(beamResults) {
        this.beamResults = beamResults || [];
        const tbody = document.querySelector('#beams-table tbody');

        if (!tbody) return;

        tbody.innerHTML = '';
        this.updateStats();

        this.beamResults.forEach(result => {
            const row = this.createRow(result);
            tbody.appendChild(row);
        });
    }

    updateStats() {
        const total = this.beamResults.length;
        const ok = this.beamResults.filter(r => r.overall_status === 'OK').length;
        const fail = total - ok;
        const rate = total > 0 ? Math.round(ok / total * 100) : 100;

        const totalEl = document.getElementById('beam-stat-total');
        const okEl = document.getElementById('beam-stat-ok');
        const failEl = document.getElementById('beam-stat-fail');
        const rateEl = document.getElementById('beam-stat-rate');

        if (totalEl) totalEl.textContent = total;
        if (okEl) okEl.textContent = ok;
        if (failEl) failEl.textContent = fail;
        if (rateEl) rateEl.textContent = rate + '%';
    }

    createRow(result) {
        const row = document.createElement('tr');
        row.className = `beam-row ${result.overall_status === 'OK' ? 'status-ok' : 'status-fail'}`;
        row.dataset.beamKey = result.key;

        row.appendChild(this.createInfoCell(result));
        row.appendChild(this.createSectionCell(result));
        row.appendChild(this.createLongitudinalCell(result));
        row.appendChild(this.createStirrupsCell(result));
        row.appendChild(this.createCapacityCell(result));
        row.appendChild(this.createDemandCell(result));
        row.appendChild(this.createDcrCell(result));
        row.appendChild(this.createComboCell(result));

        return row;
    }

    // =========================================================================
    // Celdas
    // =========================================================================

    createInfoCell(result) {
        const td = document.createElement('td');
        td.className = 'beam-info-cell';

        let sourceLabel, sourceClass;
        if (result.is_custom) {
            sourceLabel = 'CUSTOM';
            sourceClass = 'type-custom';
        } else if (result.source === 'spandrel') {
            sourceLabel = 'SPANDREL';
            sourceClass = 'type-spandrel';
        } else {
            sourceLabel = 'FRAME';
            sourceClass = 'type-frame';
        }

        td.innerHTML = `
            <span class="element-type-badge ${sourceClass}">${sourceLabel}</span>
            <span class="beam-name">${result.label}</span>
            <span class="beam-story">${result.story}</span>
        `;
        return td;
    }

    createSectionCell(result) {
        const td = document.createElement('td');
        td.className = 'section-cell';
        const geom = result.geometry || {};

        td.innerHTML = `
            <span class="section-dims">${(geom.width_m * 100).toFixed(0)}×${(geom.depth_m * 100).toFixed(0)} cm</span>
            <span class="section-length">L=${(geom.length_m || 0).toFixed(2)}m</span>
        `;
        return td;
    }

    createLongitudinalCell(result) {
        const td = document.createElement('td');
        td.className = 'longitudinal-cell editable-cell';
        const reinf = result.reinforcement || {};
        const beamKey = result.key;

        // Fila superior
        const topRow = document.createElement('div');
        topRow.className = 'reinf-row';
        topRow.innerHTML = `
            <span class="reinf-label">Sup:</span>
            ${this.createSelect(beamKey, 'n_bars_top', BEAM_N_BARS, reinf.n_bars_top || 3)}
            <span class="reinf-sep">φ</span>
            ${this.createSelect(beamKey, 'diameter_top', BEAM_DIAMETERS, reinf.diameter_top || 16)}
        `;

        // Fila inferior
        const botRow = document.createElement('div');
        botRow.className = 'reinf-row';
        botRow.innerHTML = `
            <span class="reinf-label">Inf:</span>
            ${this.createSelect(beamKey, 'n_bars_bottom', BEAM_N_BARS, reinf.n_bars_bottom || 3)}
            <span class="reinf-sep">φ</span>
            ${this.createSelect(beamKey, 'diameter_bottom', BEAM_DIAMETERS, reinf.diameter_bottom || 16)}
        `;

        td.appendChild(topRow);
        td.appendChild(botRow);

        // Agregar eventos después de insertar en DOM
        setTimeout(() => this.attachSelectListeners(td, beamKey), 0);

        return td;
    }

    createStirrupsCell(result) {
        const td = document.createElement('td');
        td.className = 'stirrups-cell editable-cell';
        const reinf = result.reinforcement || {};
        const beamKey = result.key;

        // Fila de configuración: ramas E diámetro @ espaciamiento
        const configRow = document.createElement('div');
        configRow.className = 'reinf-row';
        configRow.innerHTML = `
            ${this.createSelect(beamKey, 'n_stirrup_legs', STIRRUP_LEGS, reinf.n_stirrup_legs || 2)}
            <span class="reinf-sep">E</span>
            ${this.createSelect(beamKey, 'stirrup_diameter', BEAM_DIAMETERS.slice(0, 5), reinf.stirrup_diameter || 10)}
            <span class="reinf-sep">@</span>
            ${this.createSelect(beamKey, 'stirrup_spacing', STIRRUP_SPACINGS, reinf.stirrup_spacing || 150)}
        `;

        // Info de Av
        const avInfo = document.createElement('div');
        avInfo.className = 'av-info';
        avInfo.textContent = `Av=${reinf.Av || 0}mm²`;

        td.appendChild(configRow);
        td.appendChild(avInfo);

        // Agregar eventos
        setTimeout(() => this.attachSelectListeners(td, beamKey), 0);

        return td;
    }

    // =========================================================================
    // Helpers para selectores editables
    // =========================================================================

    createSelect(beamKey, field, options, currentValue) {
        const optionsHtml = options.map(opt =>
            `<option value="${opt}" ${opt == currentValue ? 'selected' : ''}>${opt}</option>`
        ).join('');
        return `<select class="reinf-select" data-beam="${beamKey}" data-field="${field}">${optionsHtml}</select>`;
    }

    attachSelectListeners(cell, beamKey) {
        const selects = cell.querySelectorAll('.reinf-select');
        selects.forEach(select => {
            select.addEventListener('change', (e) => this.handleReinforcementChange(beamKey, e.target));
        });
    }

    async handleReinforcementChange(beamKey, selectEl) {
        const field = selectEl.dataset.field;
        const value = parseInt(selectEl.value, 10);

        // Recopilar todos los valores actuales de la fila
        const row = selectEl.closest('tr');
        const reinforcement = this.collectReinforcementFromRow(row);
        reinforcement[field] = value;

        try {
            selectEl.classList.add('updating');
            await structuralAPI.updateBeamReinforcement(
                this.page.sessionId,
                beamKey,
                reinforcement
            );

            // Re-analizar para actualizar DCR y capacidad
            await this.page.reanalyzeBeam(beamKey);

        } catch (error) {
            console.error('Error updating reinforcement:', error);
            this.page.showNotification('Error al actualizar enfierradura', 'error');
        } finally {
            selectEl.classList.remove('updating');
        }
    }

    collectReinforcementFromRow(row) {
        const data = {};
        const selects = row.querySelectorAll('.reinf-select');
        selects.forEach(select => {
            data[select.dataset.field] = parseInt(select.value, 10);
        });
        return data;
    }

    createCapacityCell(result) {
        const td = document.createElement('td');
        td.className = 'capacity-value';
        const shear = result.shear || {};

        td.innerHTML = `<span class="phi-vn">${shear.phi_Vn || 0}</span>`;
        return td;
    }

    createDemandCell(result) {
        const td = document.createElement('td');
        td.className = 'demand-value';
        const shear = result.shear || {};

        td.innerHTML = `<span class="vu">${shear.Vu || 0}</span>`;
        return td;
    }

    createDcrCell(result) {
        const td = document.createElement('td');
        td.className = 'dcr-value';
        const shear = result.shear || {};
        const dcr = shear.dcr || 0;

        const dcrClass = dcr > 1 ? 'dcr-fail' : dcr > 0.8 ? 'dcr-warn' : 'dcr-ok';
        td.innerHTML = `<span class="${dcrClass}">${dcr.toFixed(3)}</span>`;
        return td;
    }

    createComboCell(result) {
        const td = document.createElement('td');
        td.className = 'combo-cell';
        const shear = result.shear || {};

        const combo = shear.critical_combo || 'N/A';
        td.innerHTML = `<span class="combo-name" title="${combo}">${truncateCombo(combo, 15)}</span>`;
        return td;
    }

    clear() {
        const tbody = document.querySelector('#beams-table tbody');
        if (tbody) tbody.innerHTML = '';
        this.beamResults = [];
    }
}
