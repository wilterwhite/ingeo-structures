// app/static/js/ModalUtils.js
/**
 * Utilidades para manejo de modales.
 * Centraliza la lógica de cierre (ESC, click fuera, botón X).
 */

/**
 * Configura eventos de cierre estándar para un modal.
 * @param {HTMLElement} modal - Elemento del modal
 * @param {Function} closeCallback - Función para cerrar el modal
 * @returns {Function} Función para remover los event listeners (cleanup)
 */
function setupModalClose(modal, closeCallback) {
    if (!modal) return () => {};

    // Cerrar al hacer clic fuera del contenido
    const clickOutsideHandler = (e) => {
        if (e.target === modal) {
            closeCallback();
        }
    };
    modal.addEventListener('click', clickOutsideHandler);

    // Cerrar con botón X
    const closeBtn = modal.querySelector('.modal-close');
    const closeBtnHandler = () => closeCallback();
    closeBtn?.addEventListener('click', closeBtnHandler);

    // Cerrar con Escape
    const escapeHandler = (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeCallback();
        }
    };
    document.addEventListener('keydown', escapeHandler);

    // Retornar cleanup function
    return () => {
        modal.removeEventListener('click', clickOutsideHandler);
        closeBtn?.removeEventListener('click', closeBtnHandler);
        document.removeEventListener('keydown', escapeHandler);
    };
}

/**
 * Verifica si un modal está abierto.
 * @param {HTMLElement} modal - Elemento del modal
 * @returns {boolean} true si está abierto
 */
function isModalOpen(modal) {
    return modal?.classList.contains('active') || false;
}
