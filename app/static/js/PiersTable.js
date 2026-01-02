// app/static/js/PiersTable.js
/**
 * Módulo para manejo de la tabla de piers y configuración de armaduras.
 * Usa Constants.js para valores de armadura.
 */

class PiersTable {
    constructor(page) {
        this.page = page;
    }

    get elements() { return this.page.elements; }
    get piersData() { return this.page.piersData; }

    populateFilters() {
        const { piersGrillaFilter, piersStoryFilter } = this.elements;
        if (piersGrillaFilter) {
            piersGrillaFilter.innerHTML = '<option value="">Todas</option>';
            this.page.uniqueGrillas.forEach(grilla => {
                const option = document.createElement('option');
                option.value = grilla;
                option.textContent = grilla;
                piersGrillaFilter.appendChild(option);
            });
        }
        if (piersStoryFilter) {
            piersStoryFilter.innerHTML = '<option value="">Todos</option>';
            this.page.uniqueStories.forEach(story => {
                const option = document.createElement('option');
                option.value = story;
                option.textContent = story;
                piersStoryFilter.appendChild(option);
            });
        }
        this.updateAxisFilter();
    }

    updateAxisFilter() {
        const { piersGrillaFilter, piersAxisFilter } = this.elements;
        if (!piersAxisFilter) return;
        const selectedGrilla = piersGrillaFilter?.value || '';
        const currentAxis = piersAxisFilter.value;
        let axes;
        if (selectedGrilla) {
            const axesSet = new Set();
            this.piersData.forEach(pier => {
                if (pier.grilla === selectedGrilla && pier.eje) axesSet.add(pier.eje);
            });
            axes = [...axesSet].sort();
        } else {
            axes = this.page.uniqueAxes;
        }
        piersAxisFilter.innerHTML = '<option value="">Todos</option>';
        axes.forEach(axis => {
            const option = document.createElement('option');
            option.value = axis;
            option.textContent = axis;
            piersAxisFilter.appendChild(option);
        });
        if (axes.includes(currentAxis)) piersAxisFilter.value = currentAxis;
    }

    filter() { this.render(); }
    onGrillaChange() { this.updateAxisFilter(); this.render(); }

    render() {
        const { piersTable, piersGrillaFilter, piersStoryFilter, piersAxisFilter, pierCount } = this.elements;
        if (!piersTable) return;
        piersTable.innerHTML = '';
        const grillaFilter = piersGrillaFilter?.value || '';
        const storyFilter = piersStoryFilter?.value || '';
        const axisFilter = piersAxisFilter?.value || '';
        const filteredPiers = this.piersData.filter(pier => {
            if (grillaFilter && pier.grilla !== grillaFilter) return false;
            if (storyFilter && pier.story !== storyFilter) return false;
            if (axisFilter && pier.eje !== axisFilter) return false;
            return true;
        });
        filteredPiers.forEach(pier => piersTable.appendChild(this.createPierRow(pier)));
        if (pierCount) pierCount.textContent = this.piersData.length;
    }

    createPierRow(pier) {
        const row = document.createElement('tr');
        row.dataset.key = pier.key;
        const asVertPerM = calculateAsPerMeter(pier.n_meshes, pier.diameter_v, pier.spacing_v);
        const edgeDiameter = pier.diameter_edge || 10;
        const cover = pier.cover || 25;
        row.innerHTML = `
            <td>${pier.story}</td>
            <td>${pier.label}</td>
            <td>${pier.width_m.toFixed(2)}</td>
            <td>${pier.thickness_m.toFixed(2)}</td>
            <td>${pier.fc_MPa.toFixed(1)}</td>
            <td><select data-field="n_meshes">${generateOptions(MESH_OPTIONS, pier.n_meshes)}</select></td>
            <td><select data-field="diameter_v">${generateDiameterOptions(DIAMETERS.general, pier.diameter_v)}</select></td>
            <td><select data-field="spacing_v">${generateSpacingOptions(SPACINGS.general, pier.spacing_v)}</select></td>
            <td><select data-field="diameter_h">${generateDiameterOptions(DIAMETERS.general, pier.diameter_h)}</select></td>
            <td><select data-field="spacing_h">${generateSpacingOptions(SPACINGS.general, pier.spacing_h)}</select></td>
            <td><select data-field="diameter_edge">${generateDiameterOptions(DIAMETERS.generalBorde, edgeDiameter)}</select></td>
            <td><select data-field="cover">${generateOptions(COVERS, cover)}</select></td>
            <td class="as-display">${Math.round(asVertPerM)}</td>
        `;
        row.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', () => this.updateAsDisplay(row));
        });
        return row;
    }

    updateAsDisplay(row) {
        const nMeshes = parseInt(row.querySelector('[data-field="n_meshes"]').value);
        const diameterV = parseInt(row.querySelector('[data-field="diameter_v"]').value);
        const spacingV = parseInt(row.querySelector('[data-field="spacing_v"]').value);
        const asDisplay = row.querySelector('.as-display');
        if (asDisplay) asDisplay.textContent = Math.round(calculateAsPerMeter(nMeshes, diameterV, spacingV));
    }

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
