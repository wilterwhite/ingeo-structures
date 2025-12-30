// app/structural/static/js/PiersTable.js
/**
 * Módulo para manejo de la tabla de piers y configuración de armaduras.
 */

// Áreas de barras estándar (mm²)
const BAR_AREAS = {
    6: 28.3, 8: 50.3, 10: 78.5, 12: 113.1,
    16: 201.1, 18: 254.5, 20: 314.2, 22: 380.1,
    25: 490.9, 28: 615.8, 32: 804.2, 36: 1017.9
};

class PiersTable {
    constructor(page) {
        this.page = page;
    }

    // =========================================================================
    // Elementos DOM
    // =========================================================================

    get elements() {
        return this.page.elements;
    }

    get piersData() {
        return this.page.piersData;
    }

    // =========================================================================
    // Filtros
    // =========================================================================

    populateFilters() {
        const { piersStoryFilter, piersAxisFilter } = this.elements;

        if (piersStoryFilter) {
            piersStoryFilter.innerHTML = '<option value="">Todos los pisos</option>';
            this.page.uniqueStories.forEach(story => {
                const option = document.createElement('option');
                option.value = story;
                option.textContent = story;
                piersStoryFilter.appendChild(option);
            });
        }

        if (piersAxisFilter) {
            piersAxisFilter.innerHTML = '<option value="">Todos los ejes</option>';
            this.page.uniqueAxes.forEach(axis => {
                const option = document.createElement('option');
                option.value = axis;
                option.textContent = axis;
                piersAxisFilter.appendChild(option);
            });
        }
    }

    filter() {
        this.render();
    }

    // =========================================================================
    // Renderizado
    // =========================================================================

    render() {
        const { piersTable, piersStoryFilter, piersAxisFilter, pierCount } = this.elements;
        if (!piersTable) return;

        piersTable.innerHTML = '';

        const storyFilter = piersStoryFilter?.value || '';
        const axisFilter = piersAxisFilter?.value || '';

        const filteredPiers = this.piersData.filter(pier => {
            if (storyFilter && pier.story !== storyFilter) return false;
            if (axisFilter && pier.eje !== axisFilter) return false;
            return true;
        });

        filteredPiers.forEach(pier => {
            const row = this.createPierRow(pier);
            piersTable.appendChild(row);
        });

        if (pierCount) {
            pierCount.textContent = this.piersData.length;
        }
    }

    createPierRow(pier) {
        const row = document.createElement('tr');
        row.dataset.key = pier.key;

        const asVertPerM = this.calculateAs(pier.n_meshes, pier.diameter_v, pier.spacing_v);
        const edgeDiameter = pier.diameter_edge || 10;
        const cover = pier.cover || 25;

        row.innerHTML = `
            <td>${pier.story}</td>
            <td>${pier.label}</td>
            <td>${pier.width_m.toFixed(2)}</td>
            <td>${pier.thickness_m.toFixed(2)}</td>
            <td>${pier.fc_MPa.toFixed(1)}</td>
            <td>
                <select data-field="n_meshes">
                    <option value="1" ${pier.n_meshes === 1 ? 'selected' : ''}>1</option>
                    <option value="2" ${pier.n_meshes === 2 ? 'selected' : ''}>2</option>
                </select>
            </td>
            <td>
                <select data-field="diameter_v">
                    ${this.getDiameterOptions(pier.diameter_v)}
                </select>
            </td>
            <td>
                <select data-field="spacing_v">
                    ${this.getSpacingOptions(pier.spacing_v)}
                </select>
            </td>
            <td>
                <select data-field="diameter_h">
                    ${this.getDiameterOptions(pier.diameter_h)}
                </select>
            </td>
            <td>
                <select data-field="spacing_h">
                    ${this.getSpacingOptions(pier.spacing_h)}
                </select>
            </td>
            <td>
                <select data-field="diameter_edge">
                    ${this.getEdgeDiameterOptions(edgeDiameter)}
                </select>
            </td>
            <td>
                <select data-field="cover">
                    ${this.getCoverOptions(cover)}
                </select>
            </td>
            <td class="as-display">${Math.round(asVertPerM)}</td>
        `;

        row.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', () => this.updateAsDisplay(row));
        });

        return row;
    }

    // =========================================================================
    // Opciones de Select
    // =========================================================================

    getDiameterOptions(selected) {
        const diameters = [6, 8, 10, 12, 16, 20, 22, 25];
        return diameters.map(d =>
            `<option value="${d}" ${d === selected ? 'selected' : ''}>φ${d}</option>`
        ).join('');
    }

    getEdgeDiameterOptions(selected) {
        // Diámetros típicos para barras de borde (fierros de extremo)
        const diameters = [10, 12, 16, 20, 22, 25];
        return diameters.map(d =>
            `<option value="${d}" ${d === selected ? 'selected' : ''}>φ${d}</option>`
        ).join('');
    }

    getSpacingOptions(selected) {
        const spacings = [100, 150, 200, 250, 300];
        return spacings.map(s =>
            `<option value="${s}" ${s === selected ? 'selected' : ''}>@${s}</option>`
        ).join('');
    }

    getCoverOptions(selected) {
        const covers = [20, 25, 30, 40, 50];
        return covers.map(c =>
            `<option value="${c}" ${c === selected ? 'selected' : ''}>${c}</option>`
        ).join('');
    }

    // =========================================================================
    // Cálculos
    // =========================================================================

    calculateAs(nMeshes, diameter, spacing) {
        const barArea = BAR_AREAS[diameter] || 50.3;
        return nMeshes * (barArea / spacing) * 1000;
    }

    updateAsDisplay(row) {
        const nMeshes = parseInt(row.querySelector('[data-field="n_meshes"]').value);
        const diameterV = parseInt(row.querySelector('[data-field="diameter_v"]').value);
        const spacingV = parseInt(row.querySelector('[data-field="spacing_v"]').value);
        const asDisplay = row.querySelector('.as-display');

        if (asDisplay) {
            asDisplay.textContent = Math.round(this.calculateAs(nMeshes, diameterV, spacingV));
        }
    }

    // =========================================================================
    // Configuración Global
    // =========================================================================

    applyGlobalConfig() {
        const { globalMeshes, globalDiameter, globalSpacing, globalEdgeDiameter, globalCover, piersTable } = this.elements;

        const meshes = globalMeshes?.value || '2';
        const diameter = globalDiameter?.value || '8';
        const spacing = globalSpacing?.value || '200';
        const edgeDiameter = globalEdgeDiameter?.value || '10';
        const cover = globalCover?.value || '25';

        const rows = piersTable?.querySelectorAll('tr') || [];
        rows.forEach(row => {
            const meshSelect = row.querySelector('[data-field="n_meshes"]');
            const diamVSelect = row.querySelector('[data-field="diameter_v"]');
            const spacVSelect = row.querySelector('[data-field="spacing_v"]');
            const diamHSelect = row.querySelector('[data-field="diameter_h"]');
            const spacHSelect = row.querySelector('[data-field="spacing_h"]');
            const diamEdgeSelect = row.querySelector('[data-field="diameter_edge"]');
            const coverSelect = row.querySelector('[data-field="cover"]');

            if (meshSelect) meshSelect.value = meshes;
            if (diamVSelect) diamVSelect.value = diameter;
            if (spacVSelect) spacVSelect.value = spacing;
            if (diamHSelect) diamHSelect.value = diameter;
            if (spacHSelect) spacHSelect.value = spacing;
            if (diamEdgeSelect) diamEdgeSelect.value = edgeDiameter;
            if (coverSelect) coverSelect.value = cover;

            this.updateAsDisplay(row);
        });

        // Actualizar datos en memoria incluyendo cover
        this.piersData.forEach(pier => {
            pier.n_meshes = parseInt(meshes);
            pier.diameter_v = parseInt(diameter);
            pier.spacing_v = parseInt(spacing);
            pier.diameter_h = parseInt(diameter);
            pier.spacing_h = parseInt(spacing);
            pier.diameter_edge = parseInt(edgeDiameter);
            pier.cover = parseFloat(cover);
        });
    }

    // =========================================================================
    // Obtener Actualizaciones
    // =========================================================================

    getUpdates() {
        const updates = [];
        const { piersTable } = this.elements;
        if (!piersTable) return updates;

        piersTable.querySelectorAll('tr').forEach(row => {
            const key = row.dataset.key;
            if (!key) return;

            updates.push({
                key,
                n_meshes: parseInt(row.querySelector('[data-field="n_meshes"]')?.value || 2),
                diameter_v: parseInt(row.querySelector('[data-field="diameter_v"]')?.value || 8),
                spacing_v: parseInt(row.querySelector('[data-field="spacing_v"]')?.value || 200),
                diameter_h: parseInt(row.querySelector('[data-field="diameter_h"]')?.value || 8),
                spacing_h: parseInt(row.querySelector('[data-field="spacing_h"]')?.value || 200),
                diameter_edge: parseInt(row.querySelector('[data-field="diameter_edge"]')?.value || 10),
                cover: parseFloat(row.querySelector('[data-field="cover"]')?.value || 25)
            });
        });

        return updates;
    }

    // =========================================================================
    // Navegación a Pier
    // =========================================================================

    scrollToPier(pierKey) {
        const { piersTable } = this.elements;
        const row = piersTable?.querySelector(`tr[data-key="${pierKey}"]`);

        if (row) {
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            row.classList.add('highlight');
            setTimeout(() => row.classList.remove('highlight'), 2000);
        }
    }
}
