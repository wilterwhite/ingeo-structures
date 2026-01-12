// app/static/js/tables/RowFactory.js
/**
 * Factory para crear filas de la tabla de resultados.
 * Delega la creación de celdas a módulos especializados:
 * - SharedCells: celdas compartidas (info, story, flexure, shear, actions)
 * - PierCells: celdas específicas de pier
 * - ColumnCells: celdas específicas de columna
 * - BeamCells: celdas de beam y drop_beam
 */

class RowFactory {
    constructor(resultsTable) {
        this.table = resultsTable;
    }

    // =========================================================================
    // Creación de Fila Principal
    // =========================================================================

    createRow(result, elementKey) {
        const elementType = result.element_type || 'pier';
        const isExpanded = this.table.expandedPiers.has(elementKey);

        const row = document.createElement('tr');
        row.className = `pier-row ${elementType}-type ${isExpanded ? 'expanded' : ''}`;
        row.dataset.elementType = elementType;

        // Usar data-attribute específico por tipo de elemento
        if (elementType === 'beam') {
            row.dataset.beamKey = elementKey;
        } else if (elementType === 'drop_beam') {
            row.dataset.dropBeamKey = elementKey;
        } else {
            row.dataset.pierKey = elementKey;
        }

        if (elementType === 'column') {
            this._createColumnRow(row, result, elementKey, isExpanded);
        } else if (elementType === 'drop_beam') {
            this._createDropBeamRow(row, result, elementKey, isExpanded);
        } else if (elementType === 'beam') {
            this._createBeamRow(row, result, elementKey, isExpanded);
        } else {
            this._createPierRow(row, result, elementKey, isExpanded);
        }

        return row;
    }

    // =========================================================================
    // Creación de Filas por Tipo
    // =========================================================================

    _createPierRow(row, result, pierKey, isExpanded) {
        const pier = this.table.piersData.find(p => p.key === pierKey);

        row.appendChild(SharedCells.createInfoCell(result, 'pier'));
        row.appendChild(SharedCells.createStoryCell(result));
        row.appendChild(PierCells.createGeometryCell(result));
        row.appendChild(PierCells.createMallaCell(pier, pierKey, result));
        row.appendChild(PierCells.createBordeCell(pier, pierKey, result));
        row.appendChild(this.table.createVigaCell(pierKey, 'izq'));
        row.appendChild(this.table.createVigaCell(pierKey, 'der'));
        row.appendChild(SharedCells.createFlexureSfCell(result));
        row.appendChild(SharedCells.createFlexureCapCell(result));
        row.appendChild(SharedCells.createShearSfCell(result));
        row.appendChild(SharedCells.createShearCapCell(result));
        row.appendChild(PierCells.createProposalCell(result, pierKey));
        row.appendChild(SharedCells.createActionsCell(result, pierKey, isExpanded));

        this.attachRowEventHandlers(row, pierKey, result, 'pier');
    }

    _createColumnRow(row, result, colKey, isExpanded) {
        row.appendChild(SharedCells.createInfoCell(result, 'column'));
        row.appendChild(SharedCells.createStoryCell(result));
        row.appendChild(ColumnCells.createGeometryCell(result));
        row.appendChild(ColumnCells.createLongitudinalCell(result, colKey));
        row.appendChild(ColumnCells.createStirrupsCell(result, colKey));
        row.appendChild(SharedCells.createEmptyCell());
        row.appendChild(SharedCells.createEmptyCell());
        row.appendChild(SharedCells.createFlexureSfCell(result));
        row.appendChild(SharedCells.createFlexureCapCell(result));
        row.appendChild(SharedCells.createShearSfCell(result));
        row.appendChild(SharedCells.createShearCapCell(result));
        row.appendChild(SharedCells.createEmptyCell());
        row.appendChild(SharedCells.createActionsCell(result, colKey, isExpanded, true));

        this.attachRowEventHandlers(row, colKey, result, 'column');
    }

    _createDropBeamRow(row, result, dropBeamKey, isExpanded) {
        row.appendChild(BeamCells.createDropBeamInfoCell(result));
        row.appendChild(BeamCells.createDropBeamSectionCell(result));
        row.appendChild(BeamCells.createDropBeamLengthCell(result));
        row.appendChild(BeamCells.createDropBeamMallaVCell(result, dropBeamKey));
        row.appendChild(BeamCells.createDropBeamMallaHCell(result, dropBeamKey));
        row.appendChild(BeamCells.createDropBeamBordeCell(result, dropBeamKey));
        row.appendChild(SharedCells.createFlexureSfCell(result));
        row.appendChild(SharedCells.createFlexureCapCell(result));
        row.appendChild(SharedCells.createShearSfCell(result));
        row.appendChild(SharedCells.createShearCapCell(result));
        row.appendChild(SharedCells.createActionsCell(result, dropBeamKey, isExpanded));

        this.attachRowEventHandlers(row, dropBeamKey, result, 'drop_beam');
    }

    _createBeamRow(row, result, beamKey, isExpanded) {
        row.appendChild(BeamCells.createBeamInfoCell(result));
        row.appendChild(BeamCells.createBeamSectionCell(result));
        row.appendChild(BeamCells.createBeamLengthCell(result));
        row.appendChild(BeamCells.createBeamTopReinfCell(result, beamKey));
        row.appendChild(BeamCells.createBeamBottomReinfCell(result, beamKey));
        row.appendChild(BeamCells.createBeamStirrupsCell(result, beamKey));
        row.appendChild(SharedCells.createFlexureSfCell(result));
        row.appendChild(SharedCells.createFlexureCapCell(result));
        row.appendChild(SharedCells.createShearSfCell(result));
        row.appendChild(SharedCells.createShearCapCell(result));
        row.appendChild(SharedCells.createActionsCell(result, beamKey, isExpanded));

        this.attachRowEventHandlers(row, beamKey, result, 'beam');
    }

    // =========================================================================
    // Configuración de Event Handlers
    // =========================================================================

    /**
     * Configuración de selectores por tipo de elemento.
     */
    static SELECTOR_CONFIGS = {
        pier: {
            n_meshes: ['.malla-cell .edit-meshes', 2],
            diameter_v: ['.malla-cell .edit-diameter-v', 8],
            spacing_v: ['.malla-cell .edit-spacing-v', 200],
            diameter_h: ['.malla-cell .edit-diameter-h', 8],
            spacing_h: ['.malla-cell .edit-spacing-h', 200],
            n_edge_bars: ['.borde-cell .edit-n-edge', 2],
            diameter_edge: ['.borde-cell .edit-edge', 12],
            stirrup_diameter: ['.borde-cell .edit-stirrup-d', 10],
            stirrup_spacing: ['.borde-cell .edit-stirrup-s', 150]
        },
        column: {
            n_bars_depth: ['.longitudinal-cell .edit-n-bars', 3],
            n_bars_width: ['.longitudinal-cell .edit-n-bars-w', 3],
            diameter_long: ['.longitudinal-cell .edit-diam-long', 20],
            stirrup_diameter: ['.stirrups-cell .edit-stirrup-d', 10],
            stirrup_spacing: ['.stirrups-cell .edit-stirrup-s', 150]
        },
        beam: {
            n_bars_top: ['.edit-beam-n-top', 3],
            diameter_top: ['.edit-beam-diam-top', 16],
            n_bars_bottom: ['.edit-beam-n-bot', 3],
            diameter_bottom: ['.edit-beam-diam-bot', 16],
            n_stirrup_legs: ['.edit-beam-stirrup-legs', 2],
            stirrup_diameter: ['.edit-beam-stirrup-d', 10],
            stirrup_spacing: ['.edit-beam-stirrup-s', 150]
        },
        drop_beam: {
            n_meshes: ['.malla-v-cell .edit-meshes', 2],
            diameter_v: ['.malla-v-cell .edit-diameter-v', 12],
            spacing_v: ['.malla-v-cell .edit-spacing-v', 200],
            diameter_h: ['.malla-h-cell .edit-diameter-h', 10],
            spacing_h: ['.malla-h-cell .edit-spacing-h', 200],
            n_edge_bars: ['.borde-cell .edit-n-edge', 4],
            diameter_edge: ['.borde-cell .edit-edge', 16],
            stirrup_diameter: ['.borde-cell .edit-stirrup-d', 10],
            stirrup_spacing: ['.borde-cell .edit-stirrup-s', 150]
        }
    };

    /**
     * Recolecta valores de armadura de una fila usando configuración por tipo.
     */
    _collectReinforcementChanges(row, elementType = 'pier') {
        const config = RowFactory.SELECTOR_CONFIGS[elementType];
        if (!config) {
            console.warn(`[RowFactory] No hay configuración para tipo: ${elementType}`);
            return {};
        }

        const result = {};
        for (const [field, [selector, defaultVal]] of Object.entries(config)) {
            result[field] = parseInt(row.querySelector(selector)?.value) || defaultVal;
        }
        return result;
    }

    attachRowEventHandlers(row, elementKey, result, elementType) {
        const elementLabel = `${result.story} - ${result.pier_label}`;

        // Botones de acción
        row.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                if (action === 'section') {
                    this.table.page.wallsModule.showSectionDiagram(elementKey, elementLabel);
                } else if (action === 'info') {
                    // Modal de detalles unificado para todos los tipos
                    this.table.page.wallsModule.showElementDetails(elementKey, elementLabel, elementType);
                } else if (action === 'diagram') {
                    this.table.page.plotModal.open(elementKey, elementLabel, this.table.plotsCache[elementKey]);
                }
            });
        });

        // Configuración de selectores para event listeners
        // Nota: los selectores deben coincidir con los definidos en BeamCells.js
        const selectorsByType = {
            pier: ['.malla-cell select', '.borde-cell select'],
            column: ['.longitudinal-cell select', '.stirrups-cell select'],
            beam: ['select[class^="edit-beam-"]'],  // Todos los selects de beam
            drop_beam: ['.malla-v-cell select', '.malla-h-cell select', '.borde-cell select']
        };

        // Event listeners para cambios de armadura
        const selectors = selectorsByType[elementType] || [];
        selectors.forEach(selector => {
            row.querySelectorAll(selector).forEach(select => {
                select.addEventListener('change', () => {
                    if (elementType === 'pier' && select.classList.contains('edit-n-edge')) {
                        this.table.updateStirrupsState(row);
                    }
                    const changes = this._collectReinforcementChanges(row, elementType);
                    this.table.editManager.onReinforcementChange(elementKey, elementType, changes);
                });
            });
        });

        // Eventos específicos de pier
        if (elementType === 'pier') {
            row.querySelectorAll('.viga-cell .beam-selector').forEach(select => {
                select.addEventListener('change', () => {
                    const side = select.dataset.side;
                    this.table.editManager.onBeamAssignmentChange(elementKey, side, select.value);
                });
            });

            const viewProposalBtn = row.querySelector('.view-proposal-btn');
            if (viewProposalBtn) {
                viewProposalBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const proposedConfig = this.table.getProposedConfig(result.design_proposal);
                    this.table.page.wallsModule.showProposedSectionDiagram(elementKey, elementLabel, proposedConfig);
                });
            }

            const applyBtn = row.querySelector('.apply-proposal-btn');
            if (applyBtn) {
                applyBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.table.applyProposal(elementKey, result.design_proposal);
                });
            }
        }
    }
}
