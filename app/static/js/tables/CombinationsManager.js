// app/static/js/tables/CombinationsManager.js
/**
 * Gestor de combinaciones de carga para la tabla de resultados.
 *
 * Responsabilidades:
 * - Cargar combinaciones desde el backend
 * - Crear filas de combinaciones
 * - Manejar expansión/colapso de filas
 * - Mostrar diagramas P-M de combinaciones específicas
 */

class CombinationsManager {
    /**
     * @param {ResultsTable} resultsTable - Referencia a la tabla de resultados
     */
    constructor(resultsTable) {
        this.table = resultsTable;

        // Estado de expansión
        this.expandedPiers = new Set();

        // Cache de combinaciones por pier
        this.combinationsCache = {};
    }

    // =========================================================================
    // Acceso a datos
    // =========================================================================

    get page() { return this.table.page; }
    get elements() { return this.page.elements; }
    get sessionId() { return this.page.sessionId; }
    get resultsTable() { return this.elements.resultsTable; }

    // =========================================================================
    // Creación de filas
    // =========================================================================

    /**
     * Agrega filas de combinaciones para un pier.
     * @param {HTMLElement} container - Contenedor donde agregar las filas
     * @param {string} pierKey - Clave del pier
     */
    appendComboRows(container, pierKey) {
        const isExpanded = this.expandedPiers.has(pierKey);
        const displayStyle = isExpanded ? '' : 'display: none;';

        if (isExpanded && this.combinationsCache[pierKey]) {
            this.combinationsCache[pierKey].forEach(combo => {
                container.appendChild(this.createComboRow(combo, pierKey, displayStyle));
            });
        } else {
            const loadingRow = document.createElement('tr');
            loadingRow.className = 'combo-row';
            loadingRow.dataset.pierKey = pierKey;
            loadingRow.style.cssText = displayStyle;
            loadingRow.innerHTML = '<td colspan="12" style="text-align:center; color: #6b7280;">Cargando...</td>';
            container.appendChild(loadingRow);
        }
    }

    /**
     * Crea una fila de combinación.
     * @param {Object} combo - Datos de la combinación
     * @param {string} pierKey - Clave del pier
     * @param {string} displayStyle - Estilo de display CSS
     * @returns {HTMLTableRowElement}
     */
    createComboRow(combo, pierKey, displayStyle = '') {
        const tr = document.createElement('tr');
        tr.className = 'combo-row';
        tr.dataset.pierKey = pierKey;
        tr.dataset.comboIndex = combo.index;
        if (displayStyle) tr.style.cssText = displayStyle;

        // Usar SF y DCR combinados calculados por backend
        const comboShearSf = combo.shear_sf_combined;
        const dcrCombined = combo.shear_dcr_combined;

        tr.innerHTML = `
            <td class="combo-indent" colspan="2"><span class="combo-name">${combo.full_name || combo.name}</span></td>
            <td class="combo-forces-cell" colspan="4">P=${combo.P} | M2=${combo.M2} | M3=${combo.M3}</td>
            <td class="fs-value ${getFsClass(combo.flexure_sf)}">${combo.flexure_sf}</td>
            <td></td>
            <td class="fs-value ${getFsClass(comboShearSf)}">${comboShearSf}</td>
            <td class="combo-forces-cell">V2=${combo.V2} | V3=${combo.V3} | DCR: ${formatDcr(dcrCombined)}</td>
            <td></td>
            <td class="actions-cell"><button class="action-btn" data-action="diagram-combo">📊</button></td>
        `;

        // Evento para mostrar diagrama
        tr.querySelector('[data-action="diagram-combo"]')?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showCombinationDiagram(pierKey, combo.index);
        });

        return tr;
    }

    // =========================================================================
    // Expansión / Colapso
    // =========================================================================

    /**
     * Alterna la expansión de un pier.
     * @param {string} pierKey
     */
    async toggleExpand(pierKey) {
        const pierRow = this.resultsTable?.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
        const comboRows = this.resultsTable?.querySelectorAll(`.combo-row[data-pier-key="${pierKey}"]`);
        if (!pierRow) return;

        if (this.expandedPiers.has(pierKey)) {
            this.expandedPiers.delete(pierKey);
            pierRow.classList.remove('expanded');
            comboRows?.forEach(row => row.style.display = 'none');
        } else {
            this.expandedPiers.add(pierKey);
            pierRow.classList.add('expanded');
            if (!this.combinationsCache[pierKey]) {
                await this.loadCombinations(pierKey);
            } else {
                comboRows?.forEach(row => row.style.display = '');
            }
        }
    }

    /**
     * Alterna expansión de todos los piers.
     * @returns {boolean} true si expandió, false si colapsó
     */
    async toggleAllExpand() {
        if (!this.resultsTable) return false;

        const pierKeys = Array.from(
            this.resultsTable.querySelectorAll('.pier-row:not(.column-type)')
        ).map(r => r.dataset.pierKey);

        if (pierKeys.length === 0) return false;

        const hasExpanded = pierKeys.some(key => this.expandedPiers.has(key));

        if (hasExpanded) {
            this.collapseAll();
            return false;
        } else {
            await this.expandAll(pierKeys);
            return true;
        }
    }

    /**
     * Colapsa todos los piers.
     */
    collapseAll() {
        if (!this.resultsTable) return;
        this.expandedPiers.clear();
        this.resultsTable.querySelectorAll('.combo-row').forEach(r => r.style.display = 'none');
        this.resultsTable.querySelectorAll('.pier-row').forEach(r => r.classList.remove('expanded'));
    }

    /**
     * Expande todos los piers especificados.
     * @param {string[]} pierKeys
     */
    async expandAll(pierKeys) {
        if (!this.resultsTable) return;

        pierKeys.forEach(key => this.expandedPiers.add(key));
        this.resultsTable.querySelectorAll('.pier-row').forEach(r => r.classList.add('expanded'));

        // Cargar combinaciones en paralelo para piers que no tienen cache
        await Promise.all(
            pierKeys
                .filter(k => !this.combinationsCache[k])
                .map(k => this.loadCombinations(k))
        );

        this.resultsTable.querySelectorAll('.combo-row').forEach(r => r.style.display = '');
    }

    // =========================================================================
    // Carga de datos
    // =========================================================================

    /**
     * Carga las combinaciones de un pier desde el backend.
     * @param {string} pierKey
     */
    async loadCombinations(pierKey) {
        try {
            const data = await structuralAPI.getPierCombinations(this.sessionId, pierKey);
            if (data.success) {
                this.combinationsCache[pierKey] = data.combinations;

                // Remover filas de "Cargando..."
                this.resultsTable?.querySelectorAll(`.combo-row[data-pier-key="${pierKey}"]`).forEach(r => r.remove());

                // Insertar filas de combinaciones
                const pierRow = this.resultsTable?.querySelector(`.pier-row[data-pier-key="${pierKey}"]`);
                if (!pierRow) return;

                let insertAfter = pierRow;
                data.combinations.forEach(combo => {
                    const tr = this.createComboRow(combo, pierKey);
                    insertAfter.insertAdjacentElement('afterend', tr);
                    insertAfter = tr;
                });
            }
        } catch (error) {
            console.error('Error loading combinations:', error);
        }
    }

    /**
     * Muestra el diagrama P-M para una combinación específica.
     * @param {string} pierKey
     * @param {number} comboIndex
     */
    async showCombinationDiagram(pierKey, comboIndex) {
        const combo = this.combinationsCache[pierKey]?.[comboIndex];
        if (!combo) return;

        try {
            const data = await structuralAPI.analyzeCombination({
                session_id: this.sessionId,
                pier_key: pierKey,
                combination_index: comboIndex,
                generate_plot: true
            });

            if (data.success && data.pm_plot) {
                this.page.plotModal.open(
                    pierKey,
                    pierKey.replace('_', ' - '),
                    data.pm_plot,
                    combo
                );
            }
        } catch (error) {
            console.error('Error getting combination diagram:', error);
        }
    }

    // =========================================================================
    // Utilidades
    // =========================================================================

    /**
     * Verifica si un pier está expandido.
     * @param {string} pierKey
     * @returns {boolean}
     */
    isExpanded(pierKey) {
        return this.expandedPiers.has(pierKey);
    }

    /**
     * Obtiene las combinaciones cacheadas de un pier.
     * @param {string} pierKey
     * @returns {Array|null}
     */
    getCachedCombinations(pierKey) {
        return this.combinationsCache[pierKey] || null;
    }

    /**
     * Limpia todo el cache y estado.
     */
    clear() {
        this.expandedPiers.clear();
        this.combinationsCache = {};
    }
}
