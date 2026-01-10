// app/static/js/RecalcButton.js
/**
 * Clase para manejar el botón flotante de recálculo.
 * Encapsula toda la lógica de UI del botón en un solo lugar.
 */
class RecalcButton {
    constructor(onRecalculate) {
        this.pendingItems = new Set();
        this.onRecalculate = onRecalculate;
        this.button = null;
        this.isLoading = false;
        this._create();
    }

    /**
     * Crea el botón en el DOM (solo una vez).
     */
    _create() {
        // Evitar duplicados
        const existing = document.getElementById('recalc-floating-btn');
        if (existing) {
            existing.remove();
        }

        this.button = document.createElement('button');
        this.button.id = 'recalc-floating-btn';
        this.button.className = 'btn btn-primary floating-recalc-btn hidden';
        this.button.title = 'Recalcular elementos con cambios pendientes';
        this.button.addEventListener('click', () => {
            if (!this.isLoading && this.onRecalculate) {
                this.onRecalculate();
            }
        });

        document.body.appendChild(this.button);
        this._render();
    }

    /**
     * Renderiza el contenido del botón según el estado actual.
     */
    _render() {
        if (!this.button) return;

        const count = this.pendingItems.size;

        if (this.isLoading) {
            this.button.innerHTML = `<span class="spinner"></span> Calculando...`;
            this.button.disabled = true;
            this.button.classList.remove('hidden');
        } else if (count > 0) {
            this.button.innerHTML = `Recalcular (${count})`;
            this.button.disabled = false;
            this.button.classList.remove('hidden');
        } else {
            this.button.classList.add('hidden');
            this.button.disabled = false;
        }
    }

    /**
     * Agrega un elemento a la lista de pendientes.
     */
    addPending(key) {
        this.pendingItems.add(key);
        this._render();
    }

    /**
     * Remueve un elemento de la lista de pendientes.
     */
    removePending(key) {
        this.pendingItems.delete(key);
        this._render();
    }

    /**
     * Limpia todos los pendientes.
     */
    clearPending() {
        this.pendingItems.clear();
        this._render();
    }

    /**
     * Cambia a estado de carga.
     */
    setLoading(show = true) {
        this.isLoading = show;
        this._render();
    }

    /**
     * Retorna los keys pendientes como array.
     */
    getPendingKeys() {
        return [...this.pendingItems];
    }

    /**
     * Verifica si hay cambios pendientes.
     */
    hasPending() {
        return this.pendingItems.size > 0;
    }

    /**
     * Destruye el botón del DOM.
     */
    destroy() {
        if (this.button) {
            this.button.remove();
            this.button = null;
        }
        this.pendingItems.clear();
    }
}
