// app/static/js/tables/cells/SharedCells.js
/**
 * Celdas compartidas usadas por múltiples tipos de elementos.
 * Incluye: info, story, flexure, shear, actions.
 */

const SharedCells = {
    /**
     * Celda de información del elemento (tipo + nombre).
     */
    createInfoCell(result, elementType) {
        const td = document.createElement('td');
        td.className = 'pier-info-cell';
        let typeLabel, typeClass;
        if (elementType === 'column') {
            typeLabel = 'COL';
            typeClass = 'type-column';
        } else if (elementType === 'strut') {
            typeLabel = 'STRUT';
            typeClass = 'type-strut';
        } else if (elementType === 'drop_beam') {
            typeLabel = 'VCAP';
            typeClass = 'type-drop_beam';
        } else if (elementType === 'beam') {
            typeLabel = 'VIGA';
            typeClass = 'type-beam';
        } else {
            typeLabel = 'PIER';
            typeClass = 'type-pier';
        }
        td.innerHTML = `
            <span class="element-type-badge ${typeClass}">${typeLabel}</span>
            <span class="pier-name">${result.pier_label || result.label || ''}</span>
        `;
        return td;
    },

    /**
     * Celda de piso/story.
     */
    createStoryCell(result) {
        const td = document.createElement('td');
        td.className = 'story-cell';
        td.textContent = result.story || '';
        return td;
    },

    /**
     * Celda de factor de seguridad a flexión (DCR).
     */
    createFlexureSfCell(result) {
        const hasTension = result.flexure?.has_tension || false;
        const tensionCombos = result.flexure?.tension_combos || 0;
        // DCR siempre viene del backend (domain/constants/phi_chapter21.py)
        const dcr = result.flexure?.dcr ?? 0;
        const dcrDisplay = formatDcr(dcr);
        // Usar dcr_class específico de flexure (no el general del result)
        const dcrClass = result.flexure?.dcr_class || getDcrClass(dcr);

        const sl = result.slenderness || {};
        const slenderInfo = sl.is_slender
            ? `Esbeltez: λ=${sl.lambda} (Mu×${sl.delta_ns?.toFixed(2) || '1.00'})`
            : `Esbeltez: λ=${sl.lambda || 0}`;

        const td = document.createElement('td');
        td.className = `fs-value ${dcrClass}`;
        td.title = `Combo: ${result.flexure?.critical_combo || '-'}\n${slenderInfo}`;

        const elementType = result.element_type || '';
        const designBehavior = result.design_behavior || '';
        let warningHtml = '';

        if (elementType === 'beam' && designBehavior === 'SEISMIC_BEAM_COLUMN') {
            // Vigas con axial significativo → se diseñan como columna (§18.6.4.6)
            warningHtml = `<span class="tension-warning" title="Viga con carga axial significativa - diseño como columna (§18.6.4.6)">📊</span>`;
        } else if (hasTension && elementType !== 'beam') {
            // Tracción solo relevante para muros/columnas, no para vigas
            warningHtml = `<span class="tension-warning" title="${tensionCombos} combinación(es) con tracción">⚡${tensionCombos}</span>`;
        }

        td.innerHTML = `<span class="fs-number">${dcrDisplay}</span>${warningHtml}`;
        return td;
    },

    /**
     * Celda de capacidad a flexión.
     */
    createFlexureCapCell(result) {
        const exceedsAxial = result.flexure?.exceeds_axial || false;
        const exceedsTension = result.flexure?.exceeds_tension || false;
        const Pu = result.flexure?.Pu || 0;
        const Mu = result.flexure?.Mu || 0;
        const phiMnPu = result.flexure?.phi_Mn_at_Pu || 0;

        const td = document.createElement('td');
        td.className = 'capacity-cell';

        if (exceedsAxial) {
            td.title = `Pu=${Pu}t > φPn_max=${result.flexure.phi_Pn_max}t`;
            td.innerHTML = `<span class="capacity-main axial-exceeded">⚠️ Pu>φPn</span>`;
        } else if (exceedsTension) {
            const phiPtMin = result.flexure?.phi_Pt_min || 0;
            td.title = `Pu=${Pu}t < φPt_min=${phiPtMin}t (excede capacidad de tracción)`;
            td.innerHTML = `Pu=${Pu}t, Mu=${Mu}t-m<br><span class="tension-exceeded">⚠️ Pu&lt;φPt</span>`;
        } else {
            const phiMn0 = result.flexure?.phi_Mn_0 || 0;
            td.title = `φMn₀=${phiMn0}t-m (P=0)`;
            td.innerHTML = `Pu=${Pu}t, Mu=${Mu}t-m<br>φMn=${phiMnPu}t-m`;
        }
        return td;
    },

    /**
     * Celda de factor de seguridad a cortante (DCR).
     */
    createShearSfCell(result) {
        const formulaType = result.shear?.formula_type || 'wall';
        // Mapear formula_type a etiqueta y título
        let shearType, shearTitle;
        if (formulaType === 'column') {
            shearType = 'COL';
            shearTitle = 'Fórmula COLUMNA (ACI 22.5)';
        } else if (formulaType === 'beam') {
            shearType = 'VIGA';
            shearTitle = 'Fórmula VIGA (ACI §18.6.5)';
        } else {
            shearType = 'MURO';
            shearTitle = 'Fórmula MURO (ACI 18.10.4)';
        }
        // DCR siempre viene del backend (domain/constants/phi_chapter21.py)
        const dcr = result.shear?.dcr ?? 0;
        const dcrDisplay = formatDcr(dcr);
        // Usar dcr_class del backend (centralizado)
        const dcrClass = result.shear?.dcr_class || getDcrClass(dcr);
        // Factor φv usado (§21.2.4.1: 0.60 SPECIAL, 0.75 otros)
        const phi_v = result.shear?.phi_v || 0.60;

        const td = document.createElement('td');
        td.className = `fs-value ${dcrClass}`;
        td.title = `Combo: ${result.shear?.critical_combo || '-'}\n${shearTitle}\nφv = ${phi_v.toFixed(2)} (§21.2.4)`;
        td.innerHTML = `
            <span class="fs-number">${dcrDisplay}</span>
            <span class="formula-tag formula-${formulaType}">${shearType}</span>
        `;
        return td;
    },

    /**
     * Celda de capacidad a cortante.
     * Muestra Vu original y Ve amplificado si hay amplificación.
     * La info de amplificación viene del backend (shear.amplification).
     */
    createShearCapCell(result) {
        const phiVn = result.shear?.phi_Vn_2 || 0;
        const VuOriginal = result.shear?.Vu_original || result.shear?.Vu_2 || 0;
        const Ve = result.shear?.Ve || result.shear?.Vu_2 || 0;
        const Vc = result.shear?.Vc || 0;
        const Vs = result.shear?.Vs || 0;

        // Usar info de amplificación del backend
        const amp = result.shear?.amplification || {};
        const hasAmplification = amp.has_amplification || false;

        const td = document.createElement('td');
        td.className = 'capacity-cell';

        if (hasAmplification) {
            const veSource = amp.reason || 'Ωv×Vu';
            const veRef = amp.aci_reference || '§18.10.3.3';
            td.title = `Vu análisis=${VuOriginal}t → Ve diseño=${Ve}t (${veRef})\nVc=${Vc}t + Vs=${Vs}t`;
            td.innerHTML = `φVn=${phiVn}t, Vu=${VuOriginal}t<br>Ve=${Ve}t (${veSource})`;
        } else {
            td.title = `Vc=${Vc}t + Vs=${Vs}t`;
            td.innerHTML = `φVn=${phiVn}t, Vu=${VuOriginal}t<br>Vc=${Vc}t + Vs=${Vs}t`;
        }
        return td;
    },

    /**
     * Celda de acciones (botones).
     */
    createActionsCell(result, elementKey, isExpanded, isColumn = false) {
        const td = document.createElement('td');
        td.className = 'actions-cell';
        td.innerHTML = `
            <div class="action-buttons-grid">
                <button class="action-btn" data-action="section" title="Ver sección">🔲</button>
                <button class="action-btn" data-action="info" title="Ver capacidades y combinaciones">ℹ️</button>
            </div>
        `;
        return td;
    },

    /**
     * Celda vacía.
     */
    createEmptyCell() {
        const td = document.createElement('td');
        td.className = 'empty-cell';
        td.innerHTML = '<span class="na-value">-</span>';
        return td;
    },

    // =========================================================================
    // Helpers para creación de selectores de refuerzo
    // =========================================================================

    /**
     * Crea un select de diámetro estándar.
     * @param {string} type - Tipo de diámetro ('malla', 'borde', 'estribos', etc.)
     * @param {number} value - Valor seleccionado
     * @param {string} className - Clase CSS del select
     * @param {string} title - Título/tooltip
     * @returns {string} HTML del select
     */
    createDiameterSelect(type, value, className, title) {
        return `<select class="${className}" title="${title}">
            ${StructuralConstants.generateDiameterOptions(type, value)}
        </select>`;
    },

    /**
     * Crea un select de espaciamiento estándar.
     * @param {string} type - Tipo de espaciamiento ('malla', 'estribos', etc.)
     * @param {number} value - Valor seleccionado
     * @param {string} className - Clase CSS del select
     * @param {string} title - Título/tooltip
     * @returns {string} HTML del select
     */
    createSpacingSelect(type, value, className, title) {
        return `<select class="${className}" title="${title}">
            ${StructuralConstants.generateSpacingOptions(type, value)}
        </select>`;
    },

    /**
     * Genera clase CSS de warning basada en condiciones booleanas.
     * @param {Object} conditions - Objeto con condiciones {nombre: boolean}
     * @returns {string} 'rho-warning' si alguna condición es false, '' si todas son true
     */
    getWarningClass(conditions) {
        return Object.values(conditions).some(v => v === false) ? 'rho-warning' : '';
    },

    /**
     * Construye título de warning desde checks fallidos.
     * @param {Object} checks - Objeto con {mensaje: boolean}
     * @returns {string} Mensajes de checks fallidos separados por coma
     */
    buildWarningTitle(checks) {
        return Object.entries(checks)
            .filter(([_, ok]) => !ok)
            .map(([msg]) => msg)
            .join(', ');
    }
};
