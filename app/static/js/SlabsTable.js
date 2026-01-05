// app/static/js/SlabsTable.js
/**
 * Modulo para manejo de la tabla de losas.
 * Muestra resultados de verificacion para losas 1-Way y 2-Way.
 * Usa Utils.js para funciones compartidas.
 */

class SlabsTable {
    constructor(page) {
        this.page = page;
        this.slabResults = [];
        this.filteredResults = [];
        this.filters = { type: '', status: '' };
    }

    // =========================================================================
    // Renderizado
    // =========================================================================

    renderTable(slabResults) {
        this.slabResults = slabResults || [];
        this.applyFilters();
    }

    applyFilters() {
        const typeFilter = document.getElementById('slab-type-filter')?.value || '';
        const statusFilter = document.getElementById('slab-status-filter')?.value || '';

        this.filters = { type: typeFilter, status: statusFilter };

        this.filteredResults = this.slabResults.filter(result => {
            // Filtrar por tipo
            if (typeFilter && result.slab_type !== typeFilter) {
                return false;
            }
            // Filtrar por estado
            if (statusFilter) {
                const isOk = result.overall_status === 'OK';
                if (statusFilter === 'OK' && !isOk) return false;
                if (statusFilter === 'FAIL' && isOk) return false;
            }
            return true;
        });

        this.render();
    }

    render() {
        const tbody = document.querySelector('#slabs-table tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        this.updateStats();

        this.filteredResults.forEach(result => {
            const row = this.createRow(result);
            tbody.appendChild(row);
        });
    }

    updateStats() {
        const total = this.filteredResults.length;
        const ok = this.filteredResults.filter(r => r.overall_status === 'OK').length;
        const fail = total - ok;
        const rate = total > 0 ? Math.round(ok / total * 100) : 100;

        const totalEl = document.getElementById('slab-stat-total');
        const okEl = document.getElementById('slab-stat-ok');
        const failEl = document.getElementById('slab-stat-fail');
        const rateEl = document.getElementById('slab-stat-rate');

        if (totalEl) totalEl.textContent = total;
        if (okEl) okEl.textContent = ok;
        if (failEl) failEl.textContent = fail;
        if (rateEl) rateEl.textContent = rate + '%';
    }

    createRow(result) {
        const row = document.createElement('tr');
        row.className = `slab-row ${result.overall_status === 'OK' ? 'status-ok' : 'status-fail'}`;
        row.dataset.slabKey = result.slab_key;

        row.appendChild(this.createInfoCell(result));
        row.appendChild(this.createThicknessCell(result));
        row.appendChild(this.createWidthCell(result));
        row.appendChild(this.createThicknessCheckCell(result));
        row.appendChild(this.createFlexureCapacityCell(result));
        row.appendChild(this.createFlexureDemandCell(result));
        row.appendChild(this.createFlexureSfCell(result));
        row.appendChild(this.createShearCapacityCell(result));
        row.appendChild(this.createShearDemandCell(result));
        row.appendChild(this.createShearSfCell(result));
        row.appendChild(this.createPunchingCell(result));
        row.appendChild(this.createStatusCell(result));

        return row;
    }

    // =========================================================================
    // Celdas
    // =========================================================================

    createInfoCell(result) {
        const td = document.createElement('td');
        td.className = 'slab-info-cell';

        const typeLabel = result.slab_type === 'TWO_WAY' ? '2-WAY' : '1-WAY';
        const typeClass = result.slab_type === 'TWO_WAY' ? 'type-2way' : 'type-1way';

        td.innerHTML = `
            <span class="element-type-badge ${typeClass}">${typeLabel}</span>
            <span class="slab-name">${result.label || result.slab_key}</span>
            <span class="slab-story">${result.story || ''}</span>
        `;
        return td;
    }

    createThicknessCell(result) {
        const td = document.createElement('td');
        td.className = 'thickness-cell';
        const h_cm = (result.thickness || 0) / 10; // mm a cm
        td.textContent = h_cm.toFixed(0);
        return td;
    }

    createWidthCell(result) {
        const td = document.createElement('td');
        td.className = 'width-cell';
        const b_cm = (result.width || 0) / 10; // mm a cm
        td.textContent = b_cm.toFixed(0);
        return td;
    }

    createThicknessCheckCell(result) {
        const td = document.createElement('td');
        td.className = 'thickness-check-cell';

        const thk = result.thickness_check || {};
        const isOk = thk.is_ok === true;
        const h_min_cm = (thk.h_min || 0) / 10;

        const statusClass = isOk ? 'check-ok' : 'check-fail';
        td.innerHTML = `
            <span class="${statusClass}" title="h min = ${h_min_cm.toFixed(0)} cm">
                ${h_min_cm.toFixed(0)} cm
            </span>
        `;
        return td;
    }

    createFlexureCapacityCell(result) {
        const td = document.createElement('td');
        td.className = 'capacity-value';
        const flex = result.flexure || {};

        const phiMn = flex.phi_Mn || 0;
        td.innerHTML = `<span class="phi-mn">${phiMn.toFixed(2)}</span>`;
        return td;
    }

    createFlexureDemandCell(result) {
        const td = document.createElement('td');
        td.className = 'demand-value';
        const flex = result.flexure || {};

        const Mu = flex.Mu || 0;
        td.innerHTML = `<span class="mu">${Mu.toFixed(2)}</span>`;
        return td;
    }

    createFlexureSfCell(result) {
        const flex = result.flexure || {};
        const sf = flex.sf || 0;

        const td = document.createElement('td');
        td.className = `fs-value ${this.getFsClass(sf)}`;
        td.innerHTML = `<span class="fs-number">${sf.toFixed(2)}</span>`;
        return td;
    }

    createShearCapacityCell(result) {
        const td = document.createElement('td');
        td.className = 'capacity-value';
        const shear = result.shear || {};

        const phiVn = shear.phi_Vn || 0;
        td.innerHTML = `<span class="phi-vn">${phiVn.toFixed(2)}</span>`;
        return td;
    }

    createShearDemandCell(result) {
        const td = document.createElement('td');
        td.className = 'demand-value';
        const shear = result.shear || {};

        const Vu = shear.Vu || 0;
        td.innerHTML = `<span class="vu">${Vu.toFixed(2)}</span>`;
        return td;
    }

    createShearSfCell(result) {
        const shear = result.shear || {};
        const sf = shear.sf || 0;

        const td = document.createElement('td');
        td.className = `fs-value ${this.getFsClass(sf)}`;
        td.innerHTML = `<span class="fs-number">${sf.toFixed(2)}</span>`;
        return td;
    }

    createPunchingCell(result) {
        const td = document.createElement('td');
        td.className = 'punching-cell';

        const punching = result.punching || {};

        if (!punching.applicable) {
            td.innerHTML = '<span class="na">N/A</span>';
            return td;
        }

        const isOk = punching.status === 'OK';
        const sf = punching.sf || 0;
        const statusClass = isOk ? 'check-ok' : 'check-fail';
        const sfDisplay = sf === '>100' ? '>100' : sf.toFixed(2);

        td.innerHTML = `
            <span class="${statusClass}" title="SF=${sfDisplay}, bo=${punching.bo}mm">
                SF=${sfDisplay}
            </span>
        `;
        return td;
    }

    createStatusCell(result) {
        const td = document.createElement('td');
        const status = result.overall_status || 'N/A';
        const statusClass = status === 'OK' ? 'status-ok' : 'status-fail';

        td.innerHTML = `<span class="status-badge ${statusClass}">${status}</span>`;
        return td;
    }

    // =========================================================================
    // Helpers
    // =========================================================================

    getFsClass(sf) {
        if (sf >= 1.5) return 'fs-excellent';
        if (sf >= 1.2) return 'fs-good';
        if (sf >= 1.0) return 'fs-ok';
        return 'fs-fail';
    }

    clear() {
        const tbody = document.querySelector('#slabs-table tbody');
        if (tbody) tbody.innerHTML = '';
        this.slabResults = [];
        this.filteredResults = [];
    }

    // =========================================================================
    // Bind Events
    // =========================================================================

    bindFilterEvents() {
        document.getElementById('slab-type-filter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('slab-status-filter')?.addEventListener('change', () => this.applyFilters());
    }
}
