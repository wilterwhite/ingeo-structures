// app/static/js/ReportModal.js
/**
 * Modal para configurar y generar informes PDF.
 */
class ReportModal {
    constructor(page) {
        this.page = page;
        this.elements = {};
        this.totalPiers = 0;
    }

    init() {
        this.cacheElements();
        this.bindEvents();
    }

    cacheElements() {
        this.elements = {
            modal: document.getElementById('report-modal'),
            projectName: document.getElementById('report-project-name'),
            topLoad: document.getElementById('report-top-load'),
            topCuantia: document.getElementById('report-top-cuantia'),
            includeFailing: document.getElementById('report-include-failing'),
            includeProposals: document.getElementById('report-include-proposals'),
            includePM: document.getElementById('report-include-pm'),
            includeSections: document.getElementById('report-include-sections'),
            includeFullTable: document.getElementById('report-include-full-table'),
            errorDiv: document.getElementById('report-error'),
            cancelBtn: document.getElementById('report-cancel-btn'),
            generateBtn: document.getElementById('report-generate-btn'),
            btnText: document.querySelector('#report-generate-btn .btn-text'),
            btnLoading: document.querySelector('#report-generate-btn .btn-loading')
        };
    }

    bindEvents() {
        // Cerrar modal al hacer clic fuera
        this.elements.modal?.addEventListener('click', (e) => {
            if (e.target === this.elements.modal) {
                this.close();
            }
        });

        // Boton cerrar en modal
        const closeBtn = this.elements.modal?.querySelector('.modal-close');
        closeBtn?.addEventListener('click', () => this.close());

        // Boton cancelar
        this.elements.cancelBtn?.addEventListener('click', () => this.close());

        // Boton generar
        this.elements.generateBtn?.addEventListener('click', () => this.generate());

        // Validar inputs numericos
        [this.elements.topLoad, this.elements.topCuantia].forEach(input => {
            input?.addEventListener('input', () => this.validateInputs());
        });

        // Tecla Escape para cerrar
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
    }

    isOpen() {
        return this.elements.modal?.classList.contains('active');
    }

    open(totalPiers) {
        this.totalPiers = totalPiers;

        // Actualizar limites de los inputs
        if (this.elements.topLoad) {
            this.elements.topLoad.max = totalPiers;
            if (parseInt(this.elements.topLoad.value) > totalPiers) {
                this.elements.topLoad.value = Math.min(5, totalPiers);
            }
        }
        if (this.elements.topCuantia) {
            this.elements.topCuantia.max = totalPiers;
            if (parseInt(this.elements.topCuantia.value) > totalPiers) {
                this.elements.topCuantia.value = Math.min(5, totalPiers);
            }
        }

        // Limpiar errores
        this.hideError();

        // Mostrar modal
        this.elements.modal?.classList.add('active');
    }

    close() {
        this.elements.modal?.classList.remove('active');
    }

    validateInputs() {
        const topLoad = parseInt(this.elements.topLoad?.value) || 0;
        const topCuantia = parseInt(this.elements.topCuantia?.value) || 0;

        const errors = [];

        if (topLoad < 1) {
            errors.push('Top por carga debe ser al menos 1');
        } else if (topLoad > this.totalPiers) {
            errors.push(`Top por carga (${topLoad}) excede el total de piers (${this.totalPiers})`);
        }

        if (topCuantia < 1) {
            errors.push('Top por cuantia debe ser al menos 1');
        } else if (topCuantia > this.totalPiers) {
            errors.push(`Top por cuantia (${topCuantia}) excede el total de piers (${this.totalPiers})`);
        }

        if (errors.length > 0) {
            this.showError(errors.join('. '));
            return false;
        }

        this.hideError();
        return true;
    }

    showError(message) {
        if (this.elements.errorDiv) {
            this.elements.errorDiv.textContent = message;
            this.elements.errorDiv.style.display = 'block';
        }
    }

    hideError() {
        if (this.elements.errorDiv) {
            this.elements.errorDiv.style.display = 'none';
        }
    }

    setLoading(loading) {
        if (this.elements.btnText) {
            this.elements.btnText.style.display = loading ? 'none' : 'inline';
        }
        if (this.elements.btnLoading) {
            this.elements.btnLoading.style.display = loading ? 'inline' : 'none';
        }
        if (this.elements.generateBtn) {
            this.elements.generateBtn.disabled = loading;
        }
        if (this.elements.cancelBtn) {
            this.elements.cancelBtn.disabled = loading;
        }
    }

    getConfig() {
        return {
            session_id: this.page.sessionId,
            project_name: this.elements.projectName?.value || 'Proyecto Sin Nombre',
            top_by_load: parseInt(this.elements.topLoad?.value) || 5,
            top_by_cuantia: parseInt(this.elements.topCuantia?.value) || 5,
            include_failing: this.elements.includeFailing?.checked ?? true,
            include_proposals: this.elements.includeProposals?.checked ?? true,
            include_pm_diagrams: this.elements.includePM?.checked ?? true,
            include_sections: this.elements.includeSections?.checked ?? true,
            include_full_table: this.elements.includeFullTable?.checked ?? true
        };
    }

    async generate() {
        if (!this.validateInputs()) {
            return;
        }

        this.setLoading(true);
        this.hideError();

        try {
            const config = this.getConfig();
            const blob = await structuralAPI.generateReport(config);

            // Descargar el archivo
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Informe_${config.project_name.replace(/\s+/g, '_')}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            // Cerrar modal
            this.close();

        } catch (error) {
            console.error('Error generating report:', error);
            this.showError(error.message || 'Error al generar el informe');
        } finally {
            this.setLoading(false);
        }
    }
}
