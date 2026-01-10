// app/static/js/modules/DropBeamsModule.js
/**
 * Módulo para gestión de vigas capitel (Drop Beams).
 * Extraído de StructuralPage.js para mejorar la organización del código.
 */
class DropBeamsModule {
    constructor(page) {
        this.page = page;
    }

    // =========================================================================
    // Renderizado de Tabla
    // =========================================================================

    renderDropBeamsTable() {
        this.page.renderElementTable(
            this.page.dropBeamResults,
            this.page.elements.dropBeamsTable,
            'drop-beam', 12, 'No hay vigas capitel para analizar', 'DropBeams'
        );
    }

    clearDropBeamsTable() {
        if (this.page.elements.dropBeamsTable) {
            this.page.elements.dropBeamsTable.innerHTML = '';
        }
        this.page.updateElementStats([], 'drop-beam');
    }
}
