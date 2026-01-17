// app/static/js/modules/EtabsTablesModule.js
/**
 * Módulo para visualizar las tablas crudas de ETABS.
 *
 * Permite al usuario verificar que los datos se leyeron correctamente
 * antes de ejecutar el análisis estructural.
 */

class EtabsTablesModule {
    constructor(page) {
        this.page = page;
        this.tables = {};
        this.currentTable = null;

        // Nombres descriptivos para las tablas
        this.tableNames = {
            'wall_props': 'Wall Property Definitions',
            'pier_props': 'Pier Section Properties',
            'pier_forces': 'Pier Forces',
            'frame_section': 'Frame Section Definitions (Rectangular)',
            'frame_circular': 'Frame Section Definitions (Circular)',
            'frame_assigns': 'Frame Assignments - Section Properties',
            'column_forces': 'Element Forces - Columns',
            'beam_forces': 'Element Forces - Beams',
            'spandrel_props': 'Spandrel Section Properties',
            'spandrel_forces': 'Spandrel Forces',
            'section_cut': 'Section Cut Forces - Analysis',
            'walls_connectivity': 'Wall Object Connectivity',
            'points_connectivity': 'Point Object Connectivity',
            'pier_assigns': 'Area Assignments - Pier Labels',
        };
    }

    init() {
        this.cacheElements();
        this.bindEvents();
    }

    cacheElements() {
        this.elements = {
            page: document.getElementById('etabs-tables-page'),
            placeholder: document.getElementById('etabs-tables-placeholder'),
            content: document.getElementById('etabs-tables-content'),
            tableSelector: document.getElementById('etabs-table-selector'),
            tableContainer: document.getElementById('etabs-table-container'),
            tableInfo: document.getElementById('etabs-table-info'),
        };
    }

    bindEvents() {
        this.elements.tableSelector?.addEventListener('change', (e) => {
            this.selectTable(e.target.value);
        });
    }

    /**
     * Carga las tablas desde el backend.
     */
    async loadTables() {
        if (!this.page.sessionId) {
            console.warn('[EtabsTablesModule] No hay session_id');
            return false;
        }

        try {
            const response = await fetch(`/structural/session/${this.page.sessionId}/tables`);
            const data = await response.json();

            if (data.success && data.tables) {
                this.tables = data.tables;
                this.populateSelector();
                this.showContent();
                return true;
            } else {
                console.warn('[EtabsTablesModule] No se encontraron tablas');
                return false;
            }
        } catch (error) {
            console.error('[EtabsTablesModule] Error cargando tablas:', error);
            return false;
        }
    }

    /**
     * Llena el selector de tablas.
     */
    populateSelector() {
        const selector = this.elements.tableSelector;
        if (!selector) return;

        selector.innerHTML = '<option value="">Selecciona una tabla...</option>';

        // Ordenar tablas por nombre descriptivo
        const sortedKeys = Object.keys(this.tables).sort((a, b) => {
            const nameA = this.tableNames[a] || a;
            const nameB = this.tableNames[b] || b;
            return nameA.localeCompare(nameB);
        });

        for (const key of sortedKeys) {
            const table = this.tables[key];
            const name = this.tableNames[key] || key;
            const rows = table.total_rows || table.rows?.length || 0;

            const option = document.createElement('option');
            option.value = key;
            option.textContent = `${name} (${rows} filas)`;
            selector.appendChild(option);
        }

        // Seleccionar la primera tabla automáticamente
        if (sortedKeys.length > 0) {
            selector.value = sortedKeys[0];
            this.selectTable(sortedKeys[0]);
        }
    }

    /**
     * Selecciona y muestra una tabla.
     */
    selectTable(tableKey) {
        if (!tableKey || !this.tables[tableKey]) {
            this.elements.tableContainer.innerHTML = '<p class="no-data-msg">Selecciona una tabla para ver su contenido.</p>';
            this.elements.tableInfo.textContent = '';
            return;
        }

        const table = this.tables[tableKey];
        this.currentTable = tableKey;

        // Mostrar info
        const totalRows = table.total_rows || table.rows?.length || 0;
        const shownRows = table.rows?.length || 0;
        this.elements.tableInfo.textContent = totalRows > shownRows
            ? `Mostrando ${shownRows} de ${totalRows} filas`
            : `${totalRows} filas`;

        // Renderizar tabla
        this.renderTable(table);
    }

    /**
     * Renderiza una tabla en el contenedor.
     */
    renderTable(tableData) {
        const container = this.elements.tableContainer;
        if (!container) return;

        const { columns, rows } = tableData;

        if (!columns || !rows || rows.length === 0) {
            container.innerHTML = '<p class="no-data-msg">La tabla está vacía.</p>';
            return;
        }

        // Crear tabla HTML
        const table = document.createElement('table');
        table.className = 'etabs-raw-table';

        // Header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            th.title = col;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Body
        const tbody = document.createElement('tbody');
        rows.forEach((row, rowIndex) => {
            const tr = document.createElement('tr');
            tr.className = rowIndex % 2 === 0 ? 'even' : 'odd';

            row.forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell;
                td.title = cell;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        container.innerHTML = '';
        container.appendChild(table);
    }

    /**
     * Muestra el contenido de tablas (oculta placeholder).
     */
    showContent() {
        this.elements.placeholder?.classList.add('hidden');
        this.elements.content?.classList.remove('hidden');
    }

    /**
     * Muestra el placeholder (oculta contenido).
     */
    showPlaceholder() {
        this.elements.placeholder?.classList.remove('hidden');
        this.elements.content?.classList.add('hidden');
    }

    /**
     * Resetea el módulo.
     */
    reset() {
        this.tables = {};
        this.currentTable = null;

        if (this.elements.tableSelector) {
            this.elements.tableSelector.innerHTML = '<option value="">Selecciona una tabla...</option>';
        }
        if (this.elements.tableContainer) {
            this.elements.tableContainer.innerHTML = '';
        }
        if (this.elements.tableInfo) {
            this.elements.tableInfo.textContent = '';
        }

        this.showPlaceholder();
    }

    /**
     * Retorna el número de tablas cargadas.
     */
    getTableCount() {
        return Object.keys(this.tables).length;
    }
}
