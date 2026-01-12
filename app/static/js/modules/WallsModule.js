// app/static/js/modules/WallsModule.js
/**
 * Módulo para gestión de muros/columnas (Pier Details y Section Diagrams).
 * Extraído de StructuralPage.js para mejorar la organización del código.
 */
class WallsModule {
    constructor(page) {
        this.page = page;
        this._currentPierKey = null;
        this._currentPierLabel = null;
        this._currentPierData = null;
        this._currentElementType = 'pier';  // pier, column, beam, drop_beam
    }

    // =========================================================================
    // Helpers de Renderizado de Tablas
    // =========================================================================

    /**
     * Renderiza una tabla de diseño genérica.
     * @param {string} tbodyId - ID del tbody
     * @param {Object} designData - Datos de diseño con has_data y rows
     * @param {Function} rowRenderer - Función que genera HTML para cada fila
     * @param {number} colspan - Número de columnas para mensaje vacío
     */
    _renderDesignTable(tbodyId, designData, rowRenderer, colspan = 8) {
        const tbody = document.getElementById(tbodyId);
        if (!tbody) return;

        if (designData && designData.has_data && designData.rows.length > 0) {
            tbody.innerHTML = designData.rows.map(rowRenderer).join('');
        } else {
            tbody.innerHTML = `<tr><td colspan="${colspan}" class="no-data">Sin datos de carga</td></tr>`;
        }
    }

    // =========================================================================
    // Pier Details Modal
    // =========================================================================

    async showPierDetails(pierKey, pierLabel) {
        // Delegar al método unificado
        return this.showElementDetails(pierKey, pierLabel, 'pier');
    }

    /**
     * Muestra el modal de detalles unificado para cualquier tipo de elemento.
     * @param {string} elementKey - Clave del elemento (Story_Label)
     * @param {string} elementLabel - Etiqueta para mostrar
     * @param {string} elementType - 'pier', 'column', 'beam', 'drop_beam'
     */
    async showElementDetails(elementKey, elementLabel, elementType = 'pier') {
        const { pierDetailsModal, pierDetailsTitle, pierDetailsLoading } = this.page.elements;

        if (!pierDetailsModal) return;

        // Guardar referencia del elemento actual
        this._currentPierKey = elementKey;
        this._currentPierLabel = elementLabel;
        this._currentElementType = elementType;

        // Abrir modal y mostrar loading
        pierDetailsModal.classList.add('active');
        pierDetailsModal.dataset.elementType = elementType;  // Para CSS condicional
        pierDetailsTitle.textContent = elementLabel;
        pierDetailsLoading.classList.add('active');

        // Mostrar/ocultar secciones según tipo
        this._toggleSectionsForType(elementType);

        try {
            const data = await structuralAPI.getElementCapacities(
                this.page.sessionId, elementKey, elementType
            );

            if (data.success) {
                this._currentPierData = data;
                this.updateElementDetailsContent(data, elementType);
                this.populateComboSelector(data.combinations_list || []);

                // Cargar datos de la primera combinación (la más crítica)
                const combinations = data.combinations_list || [];
                if (combinations.length > 0) {
                    const firstComboIndex = combinations[0].index;
                    const comboDetails = await structuralAPI.getCombinationDetails(
                        this.page.sessionId,
                        elementKey,
                        firstComboIndex
                    );
                    if (comboDetails.success) {
                        this.updateDesignTablesForCombo(comboDetails);
                    }
                }
            } else {
                this.page.showNotification('Error: ' + data.error, 'error');
                this.closePierDetailsModal();
            }
        } catch (error) {
            console.error('Error getting element capacities:', error);
            this.page.showNotification('Error: ' + error.message, 'error');
            this.closePierDetailsModal();
        } finally {
            pierDetailsLoading.classList.remove('active');
        }
    }

    /**
     * Muestra/oculta secciones del modal según el tipo de elemento.
     */
    _toggleSectionsForType(elementType) {
        // Boundary check: solo pier y drop_beam
        const boundarySection = document.getElementById('boundary-check-section');
        if (boundarySection) {
            const showBoundary = elementType === 'pier' || elementType === 'drop_beam';
            boundarySection.style.display = showBoundary ? '' : 'none';
        }

        // Slenderness: solo pier, column (beams con axial alta se maneja en updateContent)
        const slendernessSection = document.getElementById('slenderness-section');
        if (slendernessSection) {
            const showSlenderness = elementType === 'pier' || elementType === 'column';
            slendernessSection.style.display = showSlenderness ? '' : 'none';
        }

        // Pure capacities: todos excepto beams sin carga axial (se maneja en updateContent)
        const capacitiesSection = document.getElementById('pure-capacities-section');
        if (capacitiesSection) {
            capacitiesSection.style.display = '';  // Visible por defecto, se oculta en updateContent si no hay datos
        }

        // Actualizar título según tipo
        const typeLabels = {
            'pier': 'Pier Details',
            'column': 'Column Details',
            'beam': 'Beam Details',
            'drop_beam': 'Drop Beam Details'
        };
        const typeTitle = document.getElementById('element-type-title');
        if (typeTitle) {
            typeTitle.textContent = typeLabels[elementType] || 'Element Details';
        }
    }

    populateComboSelector(combinations) {
        const selector = document.getElementById('pier-combo-selector');
        const badge = document.getElementById('combo-critical-badge');

        if (!selector) return;

        selector.innerHTML = '';

        if (!combinations || combinations.length === 0) {
            selector.innerHTML = '<option value="-1">Sin combinaciones</option>';
            badge?.classList.add('hidden');
            return;
        }

        const criticalCombo = combinations.find(c => c.is_critical) || combinations[0];
        selector.innerHTML = combinations.map((combo, idx) => {
            const isCritical = combo.is_critical_flexure || combo.is_critical_shear;
            const criticalMark = isCritical ? ' ★' : '';
            const criticalType = combo.is_critical_flexure && combo.is_critical_shear
                ? ' (crit. flexión y corte)'
                : combo.is_critical_flexure
                    ? ' (crit. flexión)'
                    : combo.is_critical_shear
                        ? ' (crit. corte)'
                        : '';
            return `<option value="${combo.index}" ${idx === 0 ? 'selected' : ''}>
                ${combo.full_name}${criticalMark}${criticalType}
            </option>`;
        }).join('');

        if (criticalCombo && (criticalCombo.is_critical_flexure || criticalCombo.is_critical_shear)) {
            badge?.classList.remove('hidden');
        } else {
            badge?.classList.add('hidden');
        }

        this.updateComboForcesDisplay(criticalCombo);
        selector.onchange = () => this.onComboSelectorChange();
    }

    updateComboForcesDisplay(combo) {
        if (!combo) return;

        document.getElementById('combo-P').textContent = combo.P ?? '-';
        document.getElementById('combo-M2').textContent = combo.M2 ?? '-';
        document.getElementById('combo-M3').textContent = combo.M3 ?? '-';
        document.getElementById('combo-V2').textContent = combo.V2 ?? '-';
        document.getElementById('combo-V3').textContent = combo.V3 ?? '-';
    }

    async onComboSelectorChange() {
        const selector = document.getElementById('pier-combo-selector');
        const badge = document.getElementById('combo-critical-badge');
        const comboIndex = parseInt(selector.value);

        if (comboIndex < 0 || !this._currentPierKey) return;

        const combinations = this._currentPierData?.combinations_list || [];
        const selectedCombo = combinations.find(c => c.index === comboIndex);

        this.updateComboForcesDisplay(selectedCombo);

        if (selectedCombo && (selectedCombo.is_critical_flexure || selectedCombo.is_critical_shear)) {
            badge?.classList.remove('hidden');
        } else {
            badge?.classList.add('hidden');
        }

        try {
            const loadingEl = document.getElementById('pier-details-loading');
            loadingEl?.classList.add('active');

            const data = await structuralAPI.getCombinationDetails(
                this.page.sessionId,
                this._currentPierKey,
                comboIndex
            );

            if (data.success) {
                this.updateDesignTablesForCombo(data);
            } else {
                console.error('Error:', data.error);
            }
        } catch (error) {
            console.error('Error getting combo details:', error);
        } finally {
            document.getElementById('pier-details-loading')?.classList.remove('active');
        }
    }

    async openPmDiagram() {
        const selector = document.getElementById('pier-combo-selector');
        const comboIndex = parseInt(selector?.value ?? 0);

        if (!this._currentPierKey) return;

        try {
            const data = await structuralAPI.analyzeCombination({
                session_id: this.page.sessionId,
                pier_key: this._currentPierKey,
                combination_index: comboIndex,
                generate_plot: true
            });

            if (data.success && data.pm_plot) {
                this.page.plotModal.open(
                    this._currentPierKey,
                    this._currentPierLabel,
                    data.pm_plot
                );
                setTimeout(() => this.page.plotModal.selectCombination(comboIndex), 100);
            }
        } catch (error) {
            console.error('Error opening PM diagram:', error);
        }
    }

    updateDesignTablesForCombo(data) {
        const { flexure, shear, boundary, combo_name } = data;

        const flexureBody = document.getElementById('det-flexure-body');
        if (flexure) {
            flexureBody.innerHTML = `
                <tr>
                    <td>${flexure.location}</td>
                    <td class="${getDcrClass(flexure.dcr)}">${flexure.dcr}</td>
                    <td class="combo-cell">${combo_name}</td>
                    <td>${flexure.Pu_tonf}</td>
                    <td>${flexure.Mu2_tonf_m}</td>
                    <td>${flexure.Mu3_tonf_m}</td>
                    <td>${flexure.phi_Mn_tonf_m}</td>
                    <td>${flexure.c_mm}</td>
                </tr>
            `;
        }

        const shearBody = document.getElementById('det-shear-body');
        if (shear && shear.rows) {
            shearBody.innerHTML = shear.rows.map(row => `
                <tr>
                    <td>${row.direction}</td>
                    <td class="${getDcrClass(row.dcr)}">${row.dcr}</td>
                    <td class="combo-cell">${combo_name}</td>
                    <td>${row.Pu_tonf}</td>
                    <td>${row.Mu_tonf_m}</td>
                    <td>${row.Vu_tonf}</td>
                    <td>${row.phi_Vc_tonf}</td>
                    <td>${row.phi_Vn_tonf}</td>
                </tr>
            `).join('');
        }

        const boundaryBody = document.getElementById('det-boundary-body');
        if (boundary && boundary.rows) {
            boundaryBody.innerHTML = boundary.rows.map(row => `
                <tr>
                    <td>${row.location}</td>
                    <td class="combo-cell">${combo_name}</td>
                    <td>${row.Pu_tonf}</td>
                    <td>${row.Mu_tonf_m}</td>
                    <td>${row.sigma_comp_MPa}</td>
                    <td>${row.sigma_limit_MPa}</td>
                    <td>${row.c_mm}</td>
                    <td class="${row.required === 'Yes' ? 'status-fail' : 'status-ok'}">${row.required}</td>
                </tr>
            `).join('');
        }
    }

    updatePierDetailsContent(data) {
        // Compatibilidad: delegar al método unificado
        this.updateElementDetailsContent(data, 'pier');
    }

    /**
     * Actualiza el contenido del modal para cualquier tipo de elemento.
     */
    updateElementDetailsContent(data, elementType = 'pier') {
        const { element_info, reinforcement, slenderness, capacities,
                flexure_design, shear_design, boundary_check } = data;

        // Para compatibilidad con piers antiguos
        const info = element_info || data.pier_info;
        const reinf = reinforcement || data.reinforcement;

        // Sección 1: Element Details (adaptado según tipo)
        document.getElementById('det-story').textContent = info.story;
        document.getElementById('det-pier').textContent = info.label;

        // Dimensiones varían según tipo
        if (elementType === 'pier') {
            document.getElementById('det-length').textContent = info.width_m;
            document.getElementById('det-thickness').textContent = info.thickness_m;
            document.getElementById('det-height').textContent = info.height_m;
        } else if (elementType === 'column') {
            document.getElementById('det-length').textContent = info.depth_m;
            document.getElementById('det-thickness').textContent = info.width_m;
            document.getElementById('det-height').textContent = info.height_m;
        } else if (elementType === 'beam' || elementType === 'drop_beam') {
            document.getElementById('det-length').textContent = info.depth_m;
            document.getElementById('det-thickness').textContent = info.width_m;
            document.getElementById('det-height').textContent = info.length_m;
        }

        document.getElementById('det-ag').textContent = info.Ag_m2 ||
            (info.width_m * info.thickness_m).toFixed(4);

        // Sección 2: Material Properties
        document.getElementById('det-fc').textContent = info.fc_MPa;
        document.getElementById('det-fy').textContent = info.fy_MPa;
        document.getElementById('det-lambda').textContent = info.lambda || '1.0';

        // Sección 4: Reinforcement (adaptado según tipo)
        this._updateReinforcementSection(reinf, elementType);

        // Sección 5: Flexural Design
        this._renderDesignTable('det-flexure-body', flexure_design, row => `
            <tr>
                <td>${row.location}</td>
                <td class="${getDcrClass(row.dcr)}">${row.dcr}</td>
                <td class="combo-cell">${row.combo}</td>
                <td>${row.Pu_tonf}</td>
                <td>${row.Mu2_tonf_m}</td>
                <td>${row.Mu3_tonf_m}</td>
                <td>${row.phi_Mn_tonf_m}</td>
                <td>${row.c_mm}</td>
            </tr>
        `);

        // Sección 6: Shear Design
        const phiVElement = document.getElementById('det-phi-v');
        const phiVParamElement = document.getElementById('det-phi-v-param');
        if (shear_design) {
            const phi_v = shear_design.phi_v || 0.60;
            if (phiVElement) {
                phiVElement.textContent = `(φv = ${phi_v.toFixed(2)})`;
            }
            if (phiVParamElement) {
                phiVParamElement.textContent = phi_v.toFixed(2);
            }
        }

        this._renderDesignTable('det-shear-body', shear_design, row => `
            <tr>
                <td>${row.direction}</td>
                <td class="${getDcrClass(row.dcr)}">${row.dcr}</td>
                <td class="combo-cell">${row.combo}</td>
                <td>${row.Pu_tonf}</td>
                <td>${row.Mu_tonf_m}</td>
                <td>${row.Vu_tonf}</td>
                <td>${row.phi_Vc_tonf}</td>
                <td>${row.phi_Vn_tonf}</td>
            </tr>
        `);

        // Sección 7: Boundary Element Check (solo si hay datos)
        if (boundary_check) {
            this._renderDesignTable('det-boundary-body', boundary_check, row => `
                <tr>
                    <td>${row.location}</td>
                    <td class="combo-cell">${row.combo}</td>
                    <td>${row.Pu_tonf}</td>
                    <td>${row.Mu_tonf_m}</td>
                    <td>${row.sigma_comp_MPa}</td>
                    <td>${row.sigma_limit_MPa}</td>
                    <td>${row.c_mm}</td>
                    <td class="${row.required === 'Yes' ? 'status-fail' : 'status-ok'}">${row.required}</td>
                </tr>
            `);
        }

        // Sección 8: Pure Capacities (ocultar si no hay datos)
        const capacitiesSection = document.getElementById('pure-capacities-section');
        if (capacities) {
            if (capacitiesSection) capacitiesSection.style.display = '';

            if (slenderness && slenderness.is_slender) {
                document.getElementById('det-phi-pn').innerHTML =
                    `<span class="strikethrough">${capacities.phi_Pn_max_tonf}</span>` +
                    ` → ${capacities.phi_Pn_reduced_tonf || capacities.phi_Pn_max_tonf}`;
            } else {
                document.getElementById('det-phi-pn').textContent = capacities.phi_Pn_max_tonf;
            }
            document.getElementById('det-phi-mn3').textContent = capacities.phi_Mn3_tonf_m;
            document.getElementById('det-phi-mn2').textContent = capacities.phi_Mn2_tonf_m;
            document.getElementById('det-phi-vn2').textContent = capacities.phi_Vn2_tonf;
            document.getElementById('det-phi-vn3').textContent = capacities.phi_Vn3_tonf;
        } else {
            // Ocultar sección de capacidades para beams sin carga axial alta
            if (capacitiesSection) capacitiesSection.style.display = 'none';
        }

        // Sección 3: Slenderness (ocultar si no hay datos)
        const slendernessSection = document.getElementById('slenderness-section');
        if (slenderness) {
            if (slendernessSection) slendernessSection.style.display = '';
            // Los datos de slenderness se actualizan en otro lugar si existen
        } else {
            if (slendernessSection) slendernessSection.style.display = 'none';
        }
    }

    /**
     * Actualiza la sección de refuerzo según el tipo de elemento.
     */
    _updateReinforcementSection(reinf, elementType) {
        document.getElementById('det-reinf-desc').textContent = reinf.description || '';

        // Adaptar según tipo de refuerzo
        if (reinf.type === 'mesh_edge') {
            // Pier o drop_beam: malla + borde
            document.getElementById('det-as-vertical').textContent = reinf.As_vertical_mm2 || '—';
            document.getElementById('det-as-edge').textContent = reinf.As_edge_mm2 || '—';
            document.getElementById('det-as-total').textContent = reinf.As_flexure_total_mm2 || '—';

            const rhoVEl = document.getElementById('det-rho-actual');
            const rhoVValue = reinf.rho_vertical?.toFixed(5) || '—';
            if (reinf.rho_v_ok === false) {
                rhoVEl.innerHTML = `<span class="warning-text">${rhoVValue}</span>`;
            } else {
                rhoVEl.textContent = rhoVValue;
            }
        } else if (reinf.type === 'bars_stirrups') {
            // Columna: barras longitudinales
            document.getElementById('det-as-vertical').textContent = reinf.As_long_mm2 || '—';
            document.getElementById('det-as-edge').textContent = '—';
            document.getElementById('det-as-total').textContent = reinf.As_long_mm2 || '—';
            document.getElementById('det-rho-actual').textContent = reinf.rho_long?.toFixed(5) || '—';
        } else if (reinf.type === 'bars_top_bottom') {
            // Viga: barras top/bottom
            document.getElementById('det-as-vertical').textContent = reinf.As_top_mm2 || '—';
            document.getElementById('det-as-edge').textContent = reinf.As_bottom_mm2 || '—';
            document.getElementById('det-as-total').textContent = reinf.As_total_mm2 || '—';
            document.getElementById('det-rho-actual').textContent = '—';  // Vigas no muestran cuantía igual
        }

        // Warnings (solo para piers)
        const warningsContainer = document.getElementById('det-reinf-warnings');
        if (warningsContainer) {
            if (reinf.warnings && reinf.warnings.length > 0) {
                warningsContainer.innerHTML = reinf.warnings.map(w =>
                    `<div class="warning-message">${w}</div>`
                ).join('');
                warningsContainer.style.display = 'block';
            } else {
                warningsContainer.innerHTML = '';
                warningsContainer.style.display = 'none';
            }
        }
    }

    closePierDetailsModal() {
        const { pierDetailsModal } = this.page.elements;
        pierDetailsModal?.classList.remove('active');
    }

    // =========================================================================
    // Section Diagram Modal
    // =========================================================================

    initSectionModal() {
        const modal = this.page.elements.sectionModal;
        if (!modal) return;
        setupModalClose(modal, () => this.closeSectionModal());
    }

    async showSectionDiagram(pierKey, pierLabel) {
        const { sectionModal, sectionModalTitle, sectionModalLoading, sectionModalImg } = this.page.elements;

        if (!sectionModal) return;

        sectionModal.classList.add('active');
        sectionModalTitle.textContent = `Sección - ${pierLabel}`;
        sectionModalLoading.classList.add('active');
        sectionModalImg.style.display = 'none';

        try {
            const data = await structuralAPI.getSectionDiagram(this.page.sessionId, pierKey);

            if (data.success && data.section_diagram) {
                sectionModalImg.src = `data:image/png;base64,${data.section_diagram}`;
                sectionModalImg.style.display = 'block';
            } else {
                this.page.showNotification('Error: ' + (data.error || 'No se pudo generar el diagrama'), 'error');
                this.closeSectionModal();
            }
        } catch (error) {
            console.error('Error getting section diagram:', error);
            this.page.showNotification('Error: ' + error.message, 'error');
            this.closeSectionModal();
        } finally {
            sectionModalLoading.classList.remove('active');
        }
    }

    async showProposedSectionDiagram(pierKey, pierLabel, proposedConfig) {
        const { sectionModal, sectionModalTitle, sectionModalLoading, sectionModalImg } = this.page.elements;

        if (!sectionModal) return;

        sectionModal.classList.add('active');
        sectionModalTitle.textContent = `Sección Propuesta - ${pierLabel}`;
        sectionModalLoading.classList.add('active');
        sectionModalImg.style.display = 'none';

        try {
            const data = await structuralAPI.getSectionDiagram(
                this.page.sessionId,
                pierKey,
                proposedConfig
            );

            if (data.success && data.section_diagram) {
                sectionModalImg.src = `data:image/png;base64,${data.section_diagram}`;
                sectionModalImg.style.display = 'block';
            } else {
                this.page.showNotification('Error: ' + (data.error || 'No se pudo generar el diagrama'), 'error');
                this.closeSectionModal();
            }
        } catch (error) {
            console.error('Error getting proposed section diagram:', error);
            this.page.showNotification('Error: ' + error.message, 'error');
            this.closeSectionModal();
        } finally {
            sectionModalLoading.classList.remove('active');
        }
    }

    closeSectionModal() {
        const { sectionModal } = this.page.elements;
        sectionModal?.classList.remove('active');
    }
}
