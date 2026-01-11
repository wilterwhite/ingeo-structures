// app/static/js/editing/ElementEditManager.js
/**
 * Clase para gestionar la edición de todos los elementos estructurales.
 * Centraliza la lógica de cambios de armadura para piers, columnas, vigas y vigas capitel.
 * Extiende la funcionalidad original de PierEditManager para soportar múltiples tipos.
 */
class ElementEditManager {
    constructor(resultsTable) {
        this.table = resultsTable;
        // elementKey -> { type: 'pier'|'column'|'beam'|'drop_beam', reinforcement: {...}, beams: {...} }
        this.localChanges = new Map();
        this.recalcButton = new RecalcButton(() => this.recalculateAll());
    }

    // =========================================================================
    // API Pública
    // =========================================================================

    /**
     * Registra un cambio en la armadura de un elemento.
     * @param {string} elementKey - Key del elemento
     * @param {string} elementType - Tipo: 'pier', 'column', 'beam', 'drop_beam'
     * @param {Object} changes - Objeto con los campos cambiados {field: value}
     */
    onReinforcementChange(elementKey, elementType, changes) {
        this._ensureChangeEntry(elementKey, elementType);
        Object.assign(this.localChanges.get(elementKey).reinforcement, changes);
        this._markRowPending(elementKey, elementType);
        this.recalcButton.addPending(elementKey);
    }

    /**
     * Registra un cambio en la asignación de viga de acople (solo para piers).
     * @param {string} pierKey - Key del pier
     * @param {string} side - 'izq' o 'der'
     * @param {string} beamKey - Key de la viga asignada
     */
    onBeamAssignmentChange(pierKey, side, beamKey) {
        this._ensureChangeEntry(pierKey, 'pier');
        this.localChanges.get(pierKey).beams[side] = beamKey;
        this._markRowPending(pierKey, 'pier');
        this.recalcButton.addPending(pierKey);
    }

    /**
     * Recalcula todos los elementos con cambios pendientes.
     */
    async recalculateAll() {
        const pendingKeys = this.recalcButton.getPendingKeys();
        if (pendingKeys.length === 0) return;

        this.recalcButton.setLoading(true);
        this._setRowsLoading(pendingKeys, true);

        try {
            // Separar por tipo de elemento
            const { pierKeys, columnKeys, beamKeys, dropBeamKeys } = this._separateElementTypes(pendingKeys);

            const pierUpdates = this._buildPierUpdates(pierKeys);
            const columnUpdates = this._buildColumnUpdates(columnKeys);
            const beamUpdates = this._buildBeamUpdates(beamKeys);
            const dropBeamUpdates = this._buildDropBeamUpdates(dropBeamKeys);

            const data = await structuralAPI.analyze({
                session_id: this.table.sessionId,
                pier_updates: pierUpdates,
                column_updates: columnUpdates,
                beam_updates: beamUpdates,
                drop_beam_updates: dropBeamUpdates,
                generate_plots: true,
                moment_axis: 'M3',
                angle_deg: 0
            });

            if (data.success) {
                // Éxito: aplicar resultados y limpiar
                this._applyResults(data, pierKeys, columnKeys, beamKeys, dropBeamKeys);
                this._clearPendingChanges(pendingKeys);
            } else {
                this._showError('Error en el análisis: ' + (data.error || 'Error desconocido'));
            }
        } catch (error) {
            // Error de red: NO limpiar pendientes para permitir reintento
            console.error('Error recalculando elementos:', error);
            this._showError('Error de conexión. Los cambios pendientes se mantienen.');
        } finally {
            this.recalcButton.setLoading(false);
            this._setRowsLoading(pendingKeys, false);
        }
    }

    /**
     * Limpia todos los cambios pendientes (usado al reset).
     */
    reset() {
        this.localChanges.clear();
        this.recalcButton.clearPending();
    }

    /**
     * Destruye el manager y limpia recursos.
     */
    destroy() {
        this.localChanges.clear();
        this.recalcButton.destroy();
    }

    // =========================================================================
    // Métodos Privados - Gestión de Cambios
    // =========================================================================

    /**
     * Asegura que existe una entrada para el elemento en localChanges.
     */
    _ensureChangeEntry(elementKey, elementType) {
        if (!this.localChanges.has(elementKey)) {
            this.localChanges.set(elementKey, {
                type: elementType,
                reinforcement: {},
                beams: {}
            });
        }
    }

    /**
     * Separa las keys pendientes por tipo de elemento.
     */
    _separateElementTypes(keys) {
        const result = {
            pierKeys: [],
            columnKeys: [],
            beamKeys: [],
            dropBeamKeys: []
        };

        keys.forEach(key => {
            const entry = this.localChanges.get(key);
            if (!entry) return;

            switch (entry.type) {
                case 'pier':
                    result.pierKeys.push(key);
                    break;
                case 'column':
                    result.columnKeys.push(key);
                    break;
                case 'beam':
                    result.beamKeys.push(key);
                    break;
                case 'drop_beam':
                    result.dropBeamKeys.push(key);
                    break;
            }
        });

        return result;
    }

    // =========================================================================
    // Métodos Privados - UI
    // =========================================================================

    /**
     * Marca una fila como pendiente de recálculo (visual).
     */
    _markRowPending(elementKey, elementType) {
        const selector = this._getRowSelector(elementKey, elementType);
        const row = document.querySelector(selector);
        if (row) {
            row.classList.add('pending-recalc');
        }
    }

    /**
     * Quita la marca de pendiente de una fila.
     */
    _unmarkRowPending(elementKey, elementType) {
        const selector = this._getRowSelector(elementKey, elementType);
        const row = document.querySelector(selector);
        if (row) {
            row.classList.remove('pending-recalc');
        }
    }

    /**
     * Obtiene el selector CSS para una fila según el tipo de elemento.
     */
    _getRowSelector(elementKey, elementType) {
        switch (elementType) {
            case 'pier':
            case 'column':
                return `tr[data-pier-key="${elementKey}"]`;
            case 'beam':
                return `tr[data-beam-key="${elementKey}"]`;
            case 'drop_beam':
                return `tr[data-drop-beam-key="${elementKey}"]`;
            default:
                return `tr[data-pier-key="${elementKey}"]`;
        }
    }

    /**
     * Aplica estado de carga a las filas.
     */
    _setRowsLoading(elementKeys, loading) {
        elementKeys.forEach(key => {
            const entry = this.localChanges.get(key);
            if (!entry) return;

            const selector = this._getRowSelector(key, entry.type);
            const row = document.querySelector(selector);
            if (row) {
                row.style.opacity = loading ? '0.5' : '1';
            }
        });
    }

    // =========================================================================
    // Métodos Privados - Build Updates
    // =========================================================================

    /**
     * Schemas de campos por tipo de elemento.
     * Cada campo mapea a [valorDefault, usarReinforcementNested]
     */
    static UPDATE_SCHEMAS = {
        pier: {
            n_meshes: 2, diameter_v: 8, diameter_h: 8, spacing_v: 200, spacing_h: 200,
            n_edge_bars: 2, diameter_edge: 12, stirrup_diameter: 10, stirrup_spacing: 150
        },
        column: {
            n_bars_depth: 3, n_bars_width: 3, diameter_long: 20,
            stirrup_diameter: 10, stirrup_spacing: 150
        },
        beam: {
            n_bars_top: 3, diameter_top: 16, n_bars_bottom: 3, diameter_bottom: 16,
            n_stirrup_legs: 2, stirrup_diameter: 10, stirrup_spacing: 150
        },
        drop_beam: {
            n_meshes: 2, diameter_v: 12, diameter_h: 10, spacing_v: 200, spacing_h: 200,
            n_edge_bars: 4, diameter_edge: 16, stirrup_diameter: 10, stirrup_spacing: 150
        }
    };

    /**
     * Obtiene la fuente de datos para un tipo de elemento.
     */
    _getDataSource(elementType) {
        switch (elementType) {
            case 'pier': return this.table.piersData;
            case 'column': return this.table.page.columnsData;
            case 'beam': return this.table.page.beamResults;
            case 'drop_beam': return this.table.page.dropBeamResults;
            default: return null;
        }
    }

    /**
     * Construye updates genérico para cualquier tipo de elemento.
     */
    _buildElementUpdates(keys, elementType) {
        const schema = ElementEditManager.UPDATE_SCHEMAS[elementType];
        const dataSource = this._getDataSource(elementType);
        const useReinfNested = (elementType === 'beam');

        return keys.map(key => {
            const element = dataSource?.find(e => e.key === key);
            if (!element) return null;

            const changes = this.localChanges.get(key) || { reinforcement: {}, beams: {} };
            const reinfChanges = changes.reinforcement || {};
            const elementReinf = useReinfNested ? (element.reinforcement || {}) : element;

            const update = { key };
            for (const [field, defaultVal] of Object.entries(schema)) {
                update[field] = reinfChanges[field] ?? elementReinf[field] ?? defaultVal;
            }

            // Campos especiales por tipo
            if (elementType === 'pier') {
                update.cover = element.cover ?? 25;
                update.beam_left = changes.beams.izq;
                update.beam_right = changes.beams.der;
            } else if (elementType === 'column') {
                update.cover = element.cover ?? 40;
            }

            return update;
        }).filter(Boolean);
    }

    /**
     * Construye pier_updates (wrapper para compatibilidad).
     */
    _buildPierUpdates(pierKeys) {
        return this._buildElementUpdates(pierKeys, 'pier');
    }

    /**
     * Construye column_updates (wrapper para compatibilidad).
     */
    _buildColumnUpdates(columnKeys) {
        return this._buildElementUpdates(columnKeys, 'column');
    }

    /**
     * Construye beam_updates (wrapper para compatibilidad).
     */
    _buildBeamUpdates(beamKeys) {
        return this._buildElementUpdates(beamKeys, 'beam');
    }

    /**
     * Construye drop_beam_updates (wrapper para compatibilidad).
     */
    _buildDropBeamUpdates(dropBeamKeys) {
        return this._buildElementUpdates(dropBeamKeys, 'drop_beam');
    }

    // =========================================================================
    // Métodos Privados - Apply Results
    // =========================================================================

    /**
     * Aplica los resultados del servidor a la UI.
     */
    _applyResults(data, pierKeys, columnKeys, beamKeys, dropBeamKeys) {
        // Actualizar resultados de piers/columns en page
        if (data.results) {
            this.table.page.results = data.results;
        }

        // Actualizar piersData con los cambios de armadura aplicados
        pierKeys.forEach(key => {
            const changes = this.localChanges.get(key);
            if (changes?.reinforcement) {
                const pier = this.table.piersData?.find(p => p.key === key);
                if (pier) {
                    Object.assign(pier, changes.reinforcement);
                }
            }
            delete this.table.combinationsCache[key];
            this._unmarkRowPending(key, 'pier');
        });

        // Actualizar columnsData
        columnKeys.forEach(key => {
            const changes = this.localChanges.get(key);
            if (changes?.reinforcement) {
                const column = this.table.page.columnsData?.find(c => c.key === key);
                if (column) {
                    Object.assign(column, changes.reinforcement);
                }
            }
            delete this.table.combinationsCache[key];
            this._unmarkRowPending(key, 'column');
        });

        // Re-renderizar tabla de piers/columns si hubo cambios
        if (pierKeys.length > 0 || columnKeys.length > 0) {
            const filtered = this.table.getFilteredResults();
            this.table.renderTable(filtered);
            const stats = this.table.calculateStats();
            stats.pass_rate = stats.rate;  // Compatibilidad
            this.table.updateStatistics(stats);
            this.table.updateSummaryPlot();
        }

        // Actualizar beamResults y re-renderizar
        if (data.beam_results && beamKeys.length > 0) {
            this.table.page.beamResults = data.beam_results;
            this.table.page.beamsModule.renderBeamsTable();
            beamKeys.forEach(key => this._unmarkRowPending(key, 'beam'));
        }

        // Actualizar dropBeamResults y re-renderizar
        if (data.drop_beam_results && dropBeamKeys.length > 0) {
            this.table.page.dropBeamResults = data.drop_beam_results;
            this.table.page.renderDropBeamsTable();
            dropBeamKeys.forEach(key => this._unmarkRowPending(key, 'drop_beam'));
        }
    }

    /**
     * Limpia los cambios pendientes después de éxito.
     */
    _clearPendingChanges(elementKeys) {
        elementKeys.forEach(key => {
            this.localChanges.delete(key);
            this.recalcButton.removePending(key);
        });
    }

    /**
     * Muestra un error al usuario.
     */
    _showError(message) {
        console.error(message);
        if (this.table.page?.showNotification) {
            this.table.page.showNotification(message, 'error');
        } else {
            alert(message);
        }
    }
}

// Alias para compatibilidad con código existente
const PierEditManager = ElementEditManager;
