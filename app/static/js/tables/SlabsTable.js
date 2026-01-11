// app/static/js/tables/SlabsTable.js
/**
 * Módulo para manejo de la tabla de losas.
 * Muestra resultados de verificación para losas 1-Way y 2-Way.
 * Extiende FilterableTable para reutilizar lógica de filtrado.
 */

class SlabsTable extends FilterableTable {
    constructor(page) {
        super(page);
    }

    // =========================================================================
    // Métodos requeridos por FilterableTable
    // =========================================================================

    /**
     * Obtiene valores de filtros desde el DOM.
     * @returns {Object} { type, status }
     */
    getFilterValues() {
        return {
            type: document.getElementById('slab-type-filter')?.value || '',
            status: document.getElementById('slab-status-filter')?.value || ''
        };
    }

    /**
     * Verifica si un resultado cumple con los filtros.
     * @param {Object} result - Resultado de losa
     * @returns {boolean}
     */
    matchesFilters(result) {
        // Filtrar por tipo de losa
        if (this.filters.type && result.slab_type !== this.filters.type) {
            return false;
        }
        // Filtrar por estado (usa helper de FilterableTable)
        return this.matchesStatusFilter(result, this.filters.status);
    }

    // =========================================================================
    // Renderizado
    // =========================================================================

    /**
     * Punto de entrada para renderizar la tabla.
     * @param {Array} slabResults - Resultados de losas
     */
    renderTable(slabResults) {
        this.results = slabResults || [];
        this.applyFilters();
    }

    /**
     * Renderiza la tabla con los resultados filtrados.
     */
    render() {
        const tbody = document.querySelector('#slabs-table tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        this.filteredResults.forEach(result => {
            const row = this.createRow(result);
            tbody.appendChild(row);
        });
    }

    /**
     * Actualiza las estadísticas en el DOM.
     */
    updateStats() {
        const stats = this.calculateStats();

        const totalEl = document.getElementById('slab-stat-total');
        const okEl = document.getElementById('slab-stat-ok');
        const failEl = document.getElementById('slab-stat-fail');
        const rateEl = document.getElementById('slab-stat-rate');

        if (totalEl) totalEl.textContent = stats.total;
        if (okEl) okEl.textContent = stats.ok;
        if (failEl) failEl.textContent = stats.fail;
        if (rateEl) rateEl.textContent = stats.rate + '%';
    }

    // =========================================================================
    // Creación de filas
    // =========================================================================

    createRow(result) {
        const row = document.createElement('tr');
        row.className = `slab-row ${getStatusClass(result)}`;
        row.dataset.slabKey = result.slab_key;

        row.appendChild(this.createInfoCell(result));
        row.appendChild(this.createThicknessCell(result));
        row.appendChild(this.createWidthCell(result));
        row.appendChild(this.createThicknessCheckCell(result));
        row.appendChild(this.createFlexureCapacityCell(result));
        row.appendChild(this.createFlexureDemandCell(result));
        row.appendChild(this.createFlexureDcrCell(result));
        row.appendChild(this.createShearCapacityCell(result));
        row.appendChild(this.createShearDemandCell(result));
        row.appendChild(this.createShearDcrCell(result));
        row.appendChild(this.createPunchingCell(result));

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

    createFlexureDcrCell(result) {
        const flex = result.flexure || {};
        const dcr = flex.dcr || 0;
        // Usar clase CSS del backend (consistente con otros elementos)
        const dcrClass = flex.dcr_class || 'fs-ok';

        const td = document.createElement('td');
        td.className = 'dcr-value';
        td.innerHTML = `<span class="${dcrClass}">${dcr.toFixed(3)}</span>`;
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

    createShearDcrCell(result) {
        const shear = result.shear || {};
        const dcr = shear.dcr || 0;
        // Usar clase CSS del backend (consistente con otros elementos)
        const dcrClass = shear.dcr_class || 'fs-ok';

        const td = document.createElement('td');
        td.className = 'dcr-value';
        td.innerHTML = `<span class="${dcrClass}">${dcr.toFixed(3)}</span>`;
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

    // =========================================================================
    // Helpers
    // =========================================================================

    clear() {
        const tbody = document.querySelector('#slabs-table tbody');
        if (tbody) tbody.innerHTML = '';
        this.results = [];
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
