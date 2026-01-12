// app/static/js/managers/MaterialsManager.js
/**
 * Gestor de materiales para configuración de concreto.
 * Maneja tipos de concreto (normal, liviano) y sus factores lambda.
 */

class MaterialsManager {
    constructor(page) {
        this.page = page;
        this.materials = {};  // { materialName: { fc, type, lambda, count } }
    }

    /**
     * Extrae los materiales únicos de los datos cargados.
     */
    extractFromData(piersData, columnsData) {
        const materialsMap = {};

        // Extraer de piers
        piersData.forEach(pier => {
            const fc = pier.fc || pier.fc_mpa || 28;
            const matName = pier.material || `C${Math.round(fc)}`;
            if (!materialsMap[matName]) {
                materialsMap[matName] = { fc, count: 0, type: 'normal', lambda: 1.0 };
            }
            materialsMap[matName].count++;
        });

        // Extraer de columnas
        columnsData.forEach(col => {
            const fc = col.fc || col.fc_mpa || 28;
            const matName = col.material || `C${Math.round(fc)}`;
            if (!materialsMap[matName]) {
                materialsMap[matName] = { fc, count: 0, type: 'normal', lambda: 1.0 };
            }
            materialsMap[matName].count++;
        });

        // Preservar configuración existente
        Object.keys(materialsMap).forEach(name => {
            if (this.materials[name]) {
                materialsMap[name].type = this.materials[name].type;
                materialsMap[name].lambda = this.materials[name].lambda;
            }
        });

        this.materials = materialsMap;
        this.updateTable();
    }

    /**
     * Actualiza la tabla de materiales en la UI.
     */
    updateTable() {
        const tbody = this.page.elements.materialsTbody;
        if (!tbody) return;

        const materialNames = Object.keys(this.materials);

        if (materialNames.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="no-data-msg">No hay materiales cargados</td></tr>';
            return;
        }

        tbody.innerHTML = materialNames.map(name => {
            const mat = this.materials[name];
            const fcDisplay = mat.fc ? mat.fc.toFixed(1) : '—';
            return `
                <tr data-material="${name}">
                    <td><strong>${name}</strong></td>
                    <td>${fcDisplay} MPa</td>
                    <td>
                        <select class="material-type-select" data-material="${name}">
                            <option value="normal" ${mat.type === 'normal' ? 'selected' : ''}>Normal</option>
                            <option value="sand_lightweight" ${mat.type === 'sand_lightweight' ? 'selected' : ''}>Arena liviana (λ=0.85)</option>
                            <option value="all_lightweight" ${mat.type === 'all_lightweight' ? 'selected' : ''}>Todo liviano (λ=0.75)</option>
                        </select>
                    </td>
                    <td class="lambda-value">${mat.lambda.toFixed(2)}</td>
                    <td class="element-count">${mat.count} elementos</td>
                </tr>
            `;
        }).join('');

        // Bind eventos
        tbody.querySelectorAll('.material-type-select').forEach(select => {
            select.addEventListener('change', (e) => this.onTypeChange(e));
        });
    }

    /**
     * Maneja el cambio de tipo de concreto.
     * Usa factores lambda de StructuralConstants (cargados desde backend).
     */
    onTypeChange(event) {
        const select = event.target;
        const materialName = select.dataset.material;
        const newType = select.value;

        // Obtener lambda del backend (siempre debería estar disponible)
        const lambda = StructuralConstants.getLambda(newType);

        this.materials[materialName].type = newType;
        this.materials[materialName].lambda = lambda;

        // Actualizar celda de lambda
        const row = select.closest('tr');
        const lambdaCell = row.querySelector('.lambda-value');
        if (lambdaCell) {
            lambdaCell.textContent = lambda.toFixed(2);
        }

    }

    /**
     * Obtiene el lambda para un material específico.
     */
    getLambda(materialName, fc) {
        // Buscar por nombre
        if (this.materials[materialName]) {
            return this.materials[materialName].lambda;
        }
        // Buscar por fc aproximado
        const approxName = `C${Math.round(fc)}`;
        if (this.materials[approxName]) {
            return this.materials[approxName].lambda;
        }
        return 1.0;
    }

    /**
     * Obtiene la configuración de materiales para enviar al backend.
     */
    getConfig() {
        return this.materials;
    }

    /**
     * Resetea los materiales.
     */
    reset() {
        this.materials = {};
        this.updateTable();
    }
}
