// app/static/js/tables/CouplingBeamManager.js
/**
 * Gestor de vigas de acople para la tabla de resultados.
 *
 * Responsabilidades:
 * - Crear celdas de selección de vigas de acople
 * - Construir opciones del dropdown
 * - Manejar asignaciones de vigas a piers
 * - Comunicar cambios al EditManager
 */

class CouplingBeamManager {
    /**
     * @param {ResultsTable} resultsTable - Referencia a la tabla de resultados
     */
    constructor(resultsTable) {
        this.table = resultsTable;

        // Estado de vigas estándar (para "Genérica")
        this.standardBeam = { width: 200, height: 500, ln: 1500, nbars: 2, diam: 12 };

        // Asignaciones de vigas por pier
        this.pierBeamAssignments = {};  // { pierKey: { izq: 'beamKey', der: 'beamKey' } }
    }

    // =========================================================================
    // Acceso a datos
    // =========================================================================

    get page() { return this.table.page; }
    get beamsData() { return this.page.beamsData || []; }
    get editManager() { return this.table.editManager; }

    // =========================================================================
    // Creación de celdas
    // =========================================================================

    /**
     * Crea una celda de selección de viga de acople.
     * @param {string} pierKey - Clave del pier
     * @param {string} side - 'izq' o 'der'
     * @returns {HTMLTableCellElement}
     */
    createVigaCell(pierKey, side) {
        const td = document.createElement('td');
        td.className = 'viga-cell';
        td.dataset.pierKey = pierKey;
        td.dataset.side = side;

        // Obtener la viga actualmente asignada (si hay)
        const assignedBeamKey = this.getAssignedBeamKey(pierKey, side);

        // Construir opciones del dropdown
        const options = this.buildBeamOptions(assignedBeamKey, pierKey, side);

        td.innerHTML = `
            <select class="beam-selector" data-pier="${pierKey}" data-side="${side}" title="Seleccionar viga de acople">
                ${options}
            </select>
            <span class="assigned-beam-info">${this.getBeamInfoText(assignedBeamKey)}</span>
        `;

        // Evento de cambio
        const select = td.querySelector('.beam-selector');
        select.addEventListener('change', () => {
            this._handleBeamChange(pierKey, side, select.value, td);
        });

        return td;
    }

    /**
     * Maneja el cambio de selección de viga.
     * @private
     */
    _handleBeamChange(pierKey, side, newValue, cell) {
        // Guardar asignación localmente
        if (!this.pierBeamAssignments[pierKey]) {
            this.pierBeamAssignments[pierKey] = { izq: 'generic', der: 'generic' };
        }
        this.pierBeamAssignments[pierKey][side] = newValue;

        // Actualizar info text
        const infoSpan = cell.querySelector('.assigned-beam-info');
        if (infoSpan) {
            infoSpan.textContent = this.getBeamInfoText(newValue);
        }

        // Notificar al editManager para recálculo pendiente
        if (this.editManager) {
            this.editManager.onBeamAssignmentChange(pierKey, side, newValue);
        }
    }

    // =========================================================================
    // Construcción de opciones
    // =========================================================================

    /**
     * Construye las opciones del dropdown de vigas.
     * @param {string} currentValue - Valor actualmente seleccionado
     * @param {string} pierKey - Clave del pier
     * @param {string} side - 'izq' o 'der'
     * @returns {string} HTML de las opciones
     */
    buildBeamOptions(currentValue, pierKey, side) {
        const otherSide = side === 'izq' ? 'der' : 'izq';
        const otherBeamKey = this.getAssignedBeamKey(pierKey, otherSide);

        let html = `
            <option value="generic" ${currentValue === 'generic' ? 'selected' : ''}>Genérica</option>
            <option value="none" ${currentValue === 'none' ? 'selected' : ''}>Sin viga</option>
        `;

        // Agregar vigas disponibles (ETABS + custom)
        if (this.beamsData.length > 0) {
            html += '<optgroup label="Vigas disponibles">';
            this.beamsData.forEach(beam => {
                const beamKey = `${beam.story}_${beam.label}`;
                const isDisabled = beamKey === otherBeamKey;  // No permitir la misma viga en ambos lados
                const isSelected = currentValue === beamKey;
                const customBadge = beam.is_custom ? ' [CUSTOM]' : '';
                html += `<option value="${beamKey}" ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}>${beam.label} - ${beam.story}${customBadge}</option>`;
            });
            html += '</optgroup>';
        }

        return html;
    }

    // =========================================================================
    // Consultas de estado
    // =========================================================================

    /**
     * Obtiene la key de la viga asignada a un pier/lado.
     * @param {string} pierKey
     * @param {string} side - 'izq' o 'der'
     * @returns {string} Key de la viga ('generic', 'none', o beamKey)
     */
    getAssignedBeamKey(pierKey, side) {
        const config = this.pierBeamAssignments?.[pierKey]?.[side];
        return config || 'generic';  // default: genérica
    }

    /**
     * Obtiene texto informativo de la viga asignada.
     * @param {string} beamKey
     * @returns {string}
     */
    getBeamInfoText(beamKey) {
        if (beamKey === 'generic') return '';
        if (beamKey === 'none') return 'No calc';

        // Buscar en beamsData
        const beam = this.beamsData.find(b => `${b.story}_${b.label}` === beamKey);
        if (beam) {
            return `${beam.width}×${beam.depth}`;
        }
        return '';
    }

    /**
     * Obtiene todas las asignaciones de vigas.
     * @returns {Object}
     */
    getAssignments() {
        return { ...this.pierBeamAssignments };
    }

    /**
     * Limpia todas las asignaciones.
     */
    clearAssignments() {
        this.pierBeamAssignments = {};
    }

    /**
     * Sincroniza las asignaciones de vigas desde los resultados del backend.
     * Esto permite que el frontend refleje el estado real almacenado en el servidor.
     * @param {Array} results - Resultados de piers con coupling_beam_left/right
     */
    syncFromResults(results) {
        if (!results || !Array.isArray(results)) return;

        results.forEach(r => {
            // Solo sincronizar piers (no columnas)
            if (r.element_type === 'pier' && r.key) {
                const left = r.coupling_beam_left || 'generic';
                const right = r.coupling_beam_right || 'generic';

                // Solo guardar si hay asignación (evitar crear entradas vacías)
                if (left !== 'generic' || right !== 'generic') {
                    this.pierBeamAssignments[r.key] = { izq: left, der: right };
                } else if (!this.pierBeamAssignments[r.key]) {
                    // Si no hay asignación previa, crear con genérica
                    this.pierBeamAssignments[r.key] = { izq: 'generic', der: 'generic' };
                }
            }
        });
    }
}
