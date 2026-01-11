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
        // Usar dcr_class del backend (centralizado)
        const dcrClass = result.dcr_class || result.flexure?.dcr_class || getDcrClass(dcr);

        const sl = result.slenderness || {};
        const slenderInfo = sl.is_slender
            ? `Esbeltez: λ=${sl.lambda} (Mu×${sl.delta_ns?.toFixed(2) || '1.00'})`
            : `Esbeltez: λ=${sl.lambda || 0}`;

        const td = document.createElement('td');
        td.className = `fs-value ${dcrClass}`;
        td.title = `Combo: ${result.flexure?.critical_combo || '-'}\n${slenderInfo}`;

        let tensionWarning = '';
        if (hasTension) {
            tensionWarning = `<span class="tension-warning" title="${tensionCombos} combinación(es) con tracción">⚡${tensionCombos}</span>`;
        }

        td.innerHTML = `<span class="fs-number">${dcrDisplay}</span>${tensionWarning}`;
        return td;
    },

    /**
     * Celda de capacidad a flexión.
     */
    createFlexureCapCell(result) {
        const exceedsAxial = result.flexure?.exceeds_axial || false;
        const Mu = result.flexure?.Mu || 0;
        const phiMnPu = result.flexure?.phi_Mn_at_Pu || 0;

        const td = document.createElement('td');
        td.className = 'capacity-cell';

        if (exceedsAxial) {
            td.title = `Pu=${result.flexure.Pu}t > φPn_max=${result.flexure.phi_Pn_max}t`;
            td.innerHTML = `<span class="capacity-main axial-exceeded">⚠️ Pu>φPn</span>`;
        } else {
            const phiMn0 = result.flexure?.phi_Mn_0 || 0;
            td.title = `φMn₀=${phiMn0}t-m (P=0)`;
            td.innerHTML = `Mu=${Mu}t-m<br>φMn=${phiMnPu}t-m`;
        }
        return td;
    },

    /**
     * Celda de factor de seguridad a cortante (DCR).
     */
    createShearSfCell(result) {
        const formulaType = result.shear?.formula_type || 'wall';
        const shearType = formulaType === 'column' ? 'COL' : 'MURO';
        const shearTitle = formulaType === 'column' ? 'Fórmula COLUMNA (ACI 22.5)' : 'Fórmula MURO (ACI 18.10.4)';
        // DCR siempre viene del backend (domain/constants/phi_chapter21.py)
        const dcr = result.shear?.dcr ?? 0;
        const dcrDisplay = formatDcr(dcr);
        // Usar dcr_class del backend (centralizado)
        const dcrClass = result.shear?.dcr_class || getDcrClass(dcr);

        const td = document.createElement('td');
        td.className = `fs-value ${dcrClass}`;
        td.title = `Combo: ${result.shear?.critical_combo || '-'}\n${shearTitle}`;
        td.innerHTML = `
            <span class="fs-number">${dcrDisplay}</span>
            <span class="formula-tag formula-${formulaType}">${shearType}</span>
        `;
        return td;
    },

    /**
     * Celda de capacidad a cortante.
     */
    createShearCapCell(result) {
        const phiVn = result.shear?.phi_Vn_2 || 0;
        const Vu = result.shear?.Vu_2 || 0;
        const Vc = result.shear?.Vc || 0;
        const Vs = result.shear?.Vs || 0;

        const td = document.createElement('td');
        td.className = 'capacity-cell';
        td.innerHTML = `φVn=${phiVn}t, Vu=${Vu}t<br>Vc=${Vc}t + Vs=${Vs}t`;
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
