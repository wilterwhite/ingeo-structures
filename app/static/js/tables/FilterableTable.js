// app/static/js/tables/FilterableTable.js
/**
 * Clase base para tablas filtrables.
 * Proporciona funcionalidad común de filtrado y estadísticas.
 * Usa Utils.js para helpers compartidos.
 */
class FilterableTable {
    constructor(page) {
        this.page = page;
        this.results = [];
        this.filteredResults = [];
        this.filters = {};
    }

    // =========================================================================
    // Filtrado
    // =========================================================================

    /**
     * Aplica filtros y re-renderiza la tabla.
     * Subclases deben implementar getFilterValues() y matchesFilters().
     */
    applyFilters() {
        this.filters = this.getFilterValues();
        this.filteredResults = this.results.filter(r => this.matchesFilters(r));
        this.render();
        this.updateStats();
    }

    /**
     * Obtiene los valores actuales de los filtros desde el DOM.
     * @returns {Object} Objeto con valores de filtros
     * @abstract
     */
    getFilterValues() {
        throw new Error('Subclase debe implementar getFilterValues()');
    }

    /**
     * Verifica si un resultado cumple con los filtros actuales.
     * @param {Object} result - Resultado a verificar
     * @returns {boolean}
     * @abstract
     */
    matchesFilters(result) {
        throw new Error('Subclase debe implementar matchesFilters()');
    }

    // =========================================================================
    // Estadísticas
    // =========================================================================

    /**
     * Calcula estadísticas de los resultados filtrados.
     * @returns {Object} { total, ok, fail, rate }
     */
    calculateStats() {
        const total = this.filteredResults.length;
        const ok = this.filteredResults.filter(r => isStatusOk(r)).length;
        const fail = total - ok;
        const rate = total > 0 ? Math.round((ok / total) * 100) : 100;
        return { total, ok, fail, rate };
    }

    // =========================================================================
    // Renderizado (abstracto)
    // =========================================================================

    /**
     * Renderiza la tabla con los resultados filtrados.
     * Subclases deben implementar este método o sobrescribir applyFilters().
     */
    render() {
        // No-op por defecto - subclases pueden sobrescribir applyFilters() en su lugar
    }

    /**
     * Actualiza las estadísticas en el DOM.
     * Subclases deben implementar este método o sobrescribir applyFilters().
     */
    updateStats() {
        // No-op por defecto - subclases pueden sobrescribir applyFilters() en su lugar
    }

    // =========================================================================
    // Helpers comunes
    // =========================================================================

    /**
     * Helper para verificar filtro de status.
     * @param {Object} result - Resultado a verificar
     * @param {string} statusFilter - Valor del filtro ('', 'OK', 'FAIL')
     * @returns {boolean}
     */
    matchesStatusFilter(result, statusFilter) {
        if (!statusFilter) return true;
        const isOk = isStatusOk(result);
        if (statusFilter === 'OK' && !isOk) return false;
        if (statusFilter === 'FAIL' && isOk) return false;
        return true;
    }
}
