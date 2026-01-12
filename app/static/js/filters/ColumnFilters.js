// app/static/js/filters/ColumnFilters.js
/**
 * Filtros tipo Excel/Drive para columnas de tabla.
 * Maneja filtros multi-select y numéricos con dropdowns en headers.
 */

class ColumnFilters {
    /**
     * @param {Object} resultsTable - Tabla o módulo que contiene los datos
     * @param {string} tableId - ID del elemento table en el DOM (default: 'results-table')
     * @param {Object} config - Configuración de columnas filtrables (default: CONFIG para muros/columnas)
     */
    constructor(resultsTable, tableId = 'results-table', config = null) {
        this.table = resultsTable;
        this.tableId = tableId;
        this.config = config || ColumnFilters.CONFIG;
        this.filters = {};          // { column: { type, values/condition } }
        this.sortColumn = null;
        this.sortDirection = null;  // 'asc' | 'desc'
        this.dropdownEl = null;
        this.activeColumn = null;
    }

    // Configuración de columnas filtrables para MUROS/COLUMNAS
    static CONFIG = {
        element: {
            type: 'multiselect',
            label: 'Elemento',
            index: 0,
            getValue: (r) => r.pier_label || r.label,
            getGroup: (r) => r.element_type === 'column' ? 'COLUMNA' : 'MURO'
        },
        story: {
            type: 'multiselect',
            label: 'Story',
            index: 1,
            getValue: (r) => r.story
        },
        geometry: {
            type: 'multiselect',
            label: 'Geometría',
            index: 2,
            getValue: (r) => {
                const g = r.geometry || {};
                return `${g.thickness || '?'}×${g.length || '?'}`;
            }
        },
        dcr_flex: {
            type: 'numeric',
            label: 'D/C Flex.',
            index: 7,
            getValue: (r) => r.flexure?.dcr ?? null
        },
        dcr_shear: {
            type: 'numeric',
            label: 'D/C Corte',
            index: 9,
            getValue: (r) => r.shear?.dcr ?? null
        }
    };

    // Configuración para VIGAS (beams)
    static BEAMS_CONFIG = {
        element: {
            type: 'multiselect',
            label: 'Viga',
            index: 0,
            getValue: (r) => r.label || r.pier_label
        },
        section: {
            type: 'multiselect',
            label: 'Sección',
            index: 1,
            getValue: (r) => {
                const g = r.geometry || {};
                const w = g.width_m ? (g.width_m * 100).toFixed(0) : '?';
                const t = g.thickness_m ? (g.thickness_m * 100).toFixed(0) : '?';
                return `${w}×${t}`;
            }
        },
        dcr_flex: {
            type: 'numeric',
            label: 'D/C Flex.',
            index: 6,
            getValue: (r) => r.flexure?.dcr ?? null
        },
        dcr_shear: {
            type: 'numeric',
            label: 'D/C Corte',
            index: 8,
            getValue: (r) => r.shear?.dcr ?? null
        }
    };

    // Configuración para VIGAS CAPITEL (drop_beams)
    static DROP_BEAMS_CONFIG = {
        element: {
            type: 'multiselect',
            label: 'V. Capitel',
            index: 0,
            getValue: (r) => r.label || r.pier_label
        },
        section: {
            type: 'multiselect',
            label: 'Sección',
            index: 1,
            getValue: (r) => {
                // Usar getDimensionsDisplay si está disponible, sino calcular
                if (typeof getDimensionsDisplay === 'function') {
                    return getDimensionsDisplay(r);
                }
                const g = r.geometry || {};
                const w = g.width_m ? (g.width_m * 100).toFixed(0) : '?';
                const t = g.thickness_m ? (g.thickness_m * 100).toFixed(0) : '?';
                return `${w}×${t}`;
            }
        },
        dcr_flex: {
            type: 'numeric',
            label: 'D/C Flex.',
            index: 6,
            getValue: (r) => r.flexure?.dcr ?? null
        },
        dcr_shear: {
            type: 'numeric',
            label: 'D/C Corte',
            index: 8,
            getValue: (r) => r.shear?.dcr ?? null
        }
    };

    /**
     * Inicializa los filtros después de renderizar la tabla.
     */
    init() {
        this.createHeaderButtons();
        this.bindGlobalEvents();
    }

    /**
     * Agrega botones de filtro a los headers configurados.
     */
    createHeaderButtons() {
        // Buscar la tabla por su ID (configurable)
        const tableEl = document.getElementById(this.tableId);
        const thead = tableEl?.querySelector('thead tr');
        if (!thead) return;

        const ths = thead.querySelectorAll('th');

        Object.entries(this.config).forEach(([column, config]) => {
            const th = ths[config.index];
            if (!th) return;

            // Si ya tiene el botón de filtro, solo actualizar estado
            if (th.classList.contains('filterable')) {
                this.updateButtonState(column);
                return;
            }

            // Wrap contenido existente
            const label = th.textContent.trim();
            th.innerHTML = '';
            th.classList.add('filterable');

            const content = document.createElement('div');
            content.className = 'th-content';

            const labelSpan = document.createElement('span');
            labelSpan.className = 'th-label';
            labelSpan.textContent = label;

            const btn = document.createElement('button');
            btn.className = 'filter-btn';
            btn.dataset.column = column;
            btn.innerHTML = '▼';
            btn.title = 'Filtrar';
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown(column, btn);
            });

            content.appendChild(labelSpan);
            content.appendChild(btn);
            th.appendChild(content);
        });
    }

    /**
     * Eventos globales para cerrar dropdown al hacer click fuera.
     */
    bindGlobalEvents() {
        document.addEventListener('click', (e) => {
            if (this.dropdownEl && !this.dropdownEl.contains(e.target)) {
                this.closeDropdown();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.dropdownEl) {
                this.closeDropdown();
            }
        });
    }

    /**
     * Muestra/oculta el dropdown de filtro.
     */
    toggleDropdown(column, buttonEl) {
        // Si ya está abierto este mismo, cerrar
        if (this.activeColumn === column && this.dropdownEl) {
            this.closeDropdown();
            return;
        }

        this.closeDropdown();
        this.activeColumn = column;

        const colConfig = this.config[column];
        if (!colConfig) return;

        // Crear dropdown según tipo
        if (colConfig.type === 'multiselect') {
            this.dropdownEl = this.createMultiselectDropdown(column);
        } else if (colConfig.type === 'numeric') {
            this.dropdownEl = this.createNumericDropdown(column);
        }

        // Posicionar debajo del botón
        const rect = buttonEl.getBoundingClientRect();
        this.dropdownEl.style.top = `${rect.bottom + 2}px`;
        this.dropdownEl.style.left = `${rect.left - 150}px`; // Ajustar para que no se salga

        document.body.appendChild(this.dropdownEl);
        buttonEl.classList.add('active');
    }

    /**
     * Cierra el dropdown actual.
     */
    closeDropdown() {
        if (this.dropdownEl) {
            this.dropdownEl.remove();
            this.dropdownEl = null;
        }
        if (this.activeColumn) {
            const btn = document.querySelector(`.filter-btn[data-column="${this.activeColumn}"]`);
            if (btn && !this.filters[this.activeColumn]) {
                btn.classList.remove('active');
            }
            this.activeColumn = null;
        }
    }

    /**
     * Crea dropdown multi-select.
     */
    createMultiselectDropdown(column) {
        const config = this.config[column];
        const values = this.getUniqueValues(column);
        const currentFilter = this.filters[column]?.values || new Set(values);

        const dropdown = document.createElement('div');
        dropdown.className = 'column-filter-dropdown';
        dropdown.addEventListener('click', (e) => e.stopPropagation());

        // Búsqueda
        const searchDiv = document.createElement('div');
        searchDiv.className = 'filter-search';
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Buscar...';
        searchInput.addEventListener('input', () => {
            const term = searchInput.value.toLowerCase();
            dropdown.querySelectorAll('.filter-option').forEach(opt => {
                const text = opt.textContent.toLowerCase();
                opt.style.display = text.includes(term) ? '' : 'none';
            });
        });
        searchDiv.appendChild(searchInput);
        dropdown.appendChild(searchDiv);

        // Acciones rápidas
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'filter-actions';

        const selectAllBtn = document.createElement('button');
        selectAllBtn.textContent = 'Todos';
        selectAllBtn.addEventListener('click', () => {
            dropdown.querySelectorAll('.filter-option input').forEach(cb => cb.checked = true);
        });

        const clearAllBtn = document.createElement('button');
        clearAllBtn.textContent = 'Ninguno';
        clearAllBtn.addEventListener('click', () => {
            dropdown.querySelectorAll('.filter-option input').forEach(cb => cb.checked = false);
        });

        actionsDiv.appendChild(selectAllBtn);
        actionsDiv.appendChild(clearAllBtn);
        dropdown.appendChild(actionsDiv);

        // Opciones
        const optionsDiv = document.createElement('div');
        optionsDiv.className = 'filter-options';

        values.forEach(value => {
            const label = document.createElement('label');
            label.className = 'filter-option';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = value;
            checkbox.checked = currentFilter.has(value);

            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(` ${value}`));
            optionsDiv.appendChild(label);
        });

        dropdown.appendChild(optionsDiv);

        // Footer con Aplicar
        const footer = document.createElement('div');
        footer.className = 'filter-footer';

        const clearBtn = document.createElement('button');
        clearBtn.className = 'clear-filter';
        clearBtn.textContent = 'Limpiar';
        clearBtn.addEventListener('click', () => {
            delete this.filters[column];
            this.updateButtonState(column);
            this.applyFilters();
            this.closeDropdown();
        });

        const applyBtn = document.createElement('button');
        applyBtn.className = 'apply-filter';
        applyBtn.textContent = 'Aplicar';
        applyBtn.addEventListener('click', () => {
            const selected = new Set();
            dropdown.querySelectorAll('.filter-option input:checked').forEach(cb => {
                selected.add(cb.value);
            });

            if (selected.size === values.length) {
                // Todos seleccionados = sin filtro
                delete this.filters[column];
            } else {
                this.filters[column] = { type: 'multiselect', values: selected };
            }

            this.updateButtonState(column);
            this.applyFilters();
            this.closeDropdown();
        });

        footer.appendChild(clearBtn);
        footer.appendChild(applyBtn);
        dropdown.appendChild(footer);

        return dropdown;
    }

    /**
     * Crea dropdown numérico con ordenamiento y filtro de rango.
     */
    createNumericDropdown(column) {
        const currentFilter = this.filters[column] || {};

        const dropdown = document.createElement('div');
        dropdown.className = 'column-filter-dropdown numeric';
        dropdown.addEventListener('click', (e) => e.stopPropagation());

        // Ordenamiento
        const sortDiv = document.createElement('div');
        sortDiv.className = 'filter-sort';

        const sortAscBtn = document.createElement('button');
        sortAscBtn.innerHTML = '↑ Menor a mayor';
        sortAscBtn.className = this.sortColumn === column && this.sortDirection === 'asc' ? 'active' : '';
        sortAscBtn.addEventListener('click', () => {
            this.sortColumn = column;
            this.sortDirection = 'asc';
            this.applyFilters();
            this.closeDropdown();
        });

        const sortDescBtn = document.createElement('button');
        sortDescBtn.innerHTML = '↓ Mayor a menor';
        sortDescBtn.className = this.sortColumn === column && this.sortDirection === 'desc' ? 'active' : '';
        sortDescBtn.addEventListener('click', () => {
            this.sortColumn = column;
            this.sortDirection = 'desc';
            this.applyFilters();
            this.closeDropdown();
        });

        sortDiv.appendChild(sortAscBtn);
        sortDiv.appendChild(sortDescBtn);
        dropdown.appendChild(sortDiv);

        // Divider
        const hr = document.createElement('hr');
        dropdown.appendChild(hr);

        // Filtro de rango
        const rangeDiv = document.createElement('div');
        rangeDiv.className = 'filter-range';

        const conditionSelect = document.createElement('select');
        ['gt', 'lt', 'gte', 'lte'].forEach(op => {
            const option = document.createElement('option');
            option.value = op;
            option.textContent = { gt: '>', lt: '<', gte: '≥', lte: '≤' }[op];
            if (currentFilter.operator === op) option.selected = true;
            conditionSelect.appendChild(option);
        });

        const valueInput = document.createElement('input');
        valueInput.type = 'number';
        valueInput.step = '0.01';
        valueInput.placeholder = '0.00';
        valueInput.value = currentFilter.value ?? '';

        rangeDiv.appendChild(conditionSelect);
        rangeDiv.appendChild(valueInput);
        dropdown.appendChild(rangeDiv);

        // Footer
        const footer = document.createElement('div');
        footer.className = 'filter-footer';

        const clearBtn = document.createElement('button');
        clearBtn.className = 'clear-filter';
        clearBtn.textContent = 'Limpiar';
        clearBtn.addEventListener('click', () => {
            delete this.filters[column];
            if (this.sortColumn === column) {
                this.sortColumn = null;
                this.sortDirection = null;
            }
            this.updateButtonState(column);
            this.applyFilters();
            this.closeDropdown();
        });

        const applyBtn = document.createElement('button');
        applyBtn.className = 'apply-filter';
        applyBtn.textContent = 'Aplicar';
        applyBtn.addEventListener('click', () => {
            const value = parseFloat(valueInput.value);
            if (!isNaN(value)) {
                this.filters[column] = {
                    type: 'numeric',
                    operator: conditionSelect.value,
                    value: value
                };
            } else {
                delete this.filters[column];
            }

            this.updateButtonState(column);
            this.applyFilters();
            this.closeDropdown();
        });

        footer.appendChild(clearBtn);
        footer.appendChild(applyBtn);
        dropdown.appendChild(footer);

        return dropdown;
    }

    /**
     * Actualiza el estado visual del botón de filtro.
     */
    updateButtonState(column) {
        const btn = document.querySelector(`.filter-btn[data-column="${column}"]`);
        if (btn) {
            if (this.filters[column]) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        }
    }

    /**
     * Obtiene valores únicos de una columna.
     */
    getUniqueValues(column) {
        const config = this.config[column];
        if (!config) return [];

        // Soportar diferentes estructuras de datos
        const results = this.table.page?.results || this.results || [];
        const values = new Set();

        results.forEach(r => {
            const value = config.getValue(r);
            if (value !== null && value !== undefined) {
                values.add(String(value));
            }
        });

        return Array.from(values).sort();
    }

    /**
     * Verifica si un resultado pasa todos los filtros.
     */
    matchesFilters(result) {
        for (const [column, filter] of Object.entries(this.filters)) {
            const config = this.config[column];
            if (!config) continue;

            const value = config.getValue(result);

            if (filter.type === 'multiselect') {
                if (!filter.values.has(String(value))) {
                    return false;
                }
            } else if (filter.type === 'numeric') {
                const numValue = parseFloat(value);
                if (isNaN(numValue)) return false;

                switch (filter.operator) {
                    case 'gt': if (!(numValue > filter.value)) return false; break;
                    case 'lt': if (!(numValue < filter.value)) return false; break;
                    case 'gte': if (!(numValue >= filter.value)) return false; break;
                    case 'lte': if (!(numValue <= filter.value)) return false; break;
                }
            }
        }

        return true;
    }

    /**
     * Ordena resultados si hay ordenamiento activo.
     */
    sortResults(results) {
        if (!this.sortColumn || !this.sortDirection) return results;

        const config = this.config[this.sortColumn];
        if (!config) return results;

        return [...results].sort((a, b) => {
            const aVal = parseFloat(config.getValue(a)) || 0;
            const bVal = parseFloat(config.getValue(b)) || 0;

            if (this.sortDirection === 'asc') {
                return aVal - bVal;
            } else {
                return bVal - aVal;
            }
        });
    }

    /**
     * Aplica filtros y re-renderiza la tabla.
     * Soporta diferentes estructuras de datos según el tipo de tabla.
     */
    applyFilters() {
        // Obtener resultados según la estructura de datos
        const results = this.getResults();
        if (!results) return;

        // Filtrar
        let filtered = results.filter(r => this.matchesFilters(r));

        // Ordenar
        filtered = this.sortResults(filtered);

        // Actualizar según el tipo de callback disponible
        if (this.onFilterApply) {
            // Callback personalizado para beams/drop_beams
            this.onFilterApply(filtered);
        } else if (this.table.filteredResults !== undefined) {
            // ResultsTable estándar
            this.table.filteredResults = filtered;
            this.table.renderTable(filtered);
            this.table.updateStats();
        }

        // Re-crear botones de filtro (se pierden al re-renderizar tbody)
        this.createHeaderButtons();
    }

    /**
     * Obtiene los resultados según la estructura de datos disponible.
     */
    getResults() {
        return this.results || this.table?.page?.results || null;
    }

    /**
     * Establece los resultados para filtrar (útil para beams/drop_beams).
     */
    setResults(results) {
        this.results = results;
    }

    /**
     * Limpia todos los filtros.
     */
    clearAllFilters() {
        this.filters = {};
        this.sortColumn = null;
        this.sortDirection = null;

        // Actualizar botones
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        this.applyFilters();
    }
}
