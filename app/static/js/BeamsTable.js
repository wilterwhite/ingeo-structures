// app/static/js/BeamsTable.js
/**
 * Módulo para manejo de la tabla de vigas.
 * Muestra resultados de verificación de cortante para vigas.
 * Usa Utils.js para funciones compartidas.
 */

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
        row.appendChild(this.createStirrupsCell(result));
        row.appendChild(this.createCapacityCell(result));
        row.appendChild(this.createDemandCell(result));
        row.appendChild(this.createSfCell(result));
        row.appendChild(this.createDcrCell(result));
        row.appendChild(this.createComboCell(result));
        row.appendChild(this.createStatusCell(result));

        return row;
    }

    // =========================================================================
    // Celdas
    // =========================================================================

    createInfoCell(result) {
        const td = document.createElement('td');
        td.className = 'beam-info-cell';

        const sourceLabel = result.source === 'spandrel' ? 'SPANDREL' : 'FRAME';
        const sourceClass = result.source === 'spandrel' ? 'type-spandrel' : 'type-frame';

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

    createStirrupsCell(result) {
        const td = document.createElement('td');
        td.className = 'stirrups-cell';
        const reinf = result.reinforcement || {};

        td.innerHTML = `
            <span class="stirrup-config">${reinf.n_stirrup_legs || 2}E${reinf.stirrup_diameter || 10}@${reinf.stirrup_spacing || 200}</span>
            <span class="av-info">Av=${reinf.Av || 0}mm²</span>
        `;
        return td;
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

    createSfCell(result) {
        const shear = result.shear || {};
        const sf = shear.sf;

        const td = document.createElement('td');
        td.className = `fs-value ${getFsClass(sf)}`;
        td.innerHTML = `<span class="fs-number">${sf}</span>`;
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

    createStatusCell(result) {
        const td = document.createElement('td');
        const status = result.overall_status || 'N/A';
        const statusClass = status === 'OK' ? 'status-ok' : 'status-fail';

        td.innerHTML = `<span class="status-badge ${statusClass}">${status}</span>`;
        return td;
    }

    clear() {
        const tbody = document.querySelector('#beams-table tbody');
        if (tbody) tbody.innerHTML = '';
        this.beamResults = [];
    }
}
