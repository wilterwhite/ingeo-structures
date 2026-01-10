// app/structural/static/js/PlotModal.js
/**
 * Modal de diagrama P-M con navegador de combinaciones.
 */
class PlotModal {
    constructor(page) {
        this.page = page;
        this.elements = {};

        // Estado del modal
        this.pierKey = null;
        this.pierLabel = null;
        this.combinations = [];
        this.currentIndex = 0;
    }

    init() {
        this.cacheElements();
        this.bindEvents();
    }

    cacheElements() {
        this.elements = {
            modal: document.getElementById('plot-modal'),
            title: document.getElementById('modal-pier-title'),
            plotImg: document.getElementById('modal-plot-img'),
            plotLoading: document.getElementById('modal-plot-loading'),
            comboList: document.getElementById('modal-combo-list'),
            comboName: document.getElementById('modal-combo-name'),
            comboP: document.getElementById('modal-combo-P'),
            comboM2: document.getElementById('modal-combo-M2'),
            comboM3: document.getElementById('modal-combo-M3'),
            comboM: document.getElementById('modal-combo-M'),
            comboAngle: document.getElementById('modal-combo-angle'),
            currentIndexEl: document.getElementById('combo-current-index'),
            totalCombos: document.getElementById('combo-total'),
            prevBtn: document.getElementById('combo-prev-btn'),
            nextBtn: document.getElementById('combo-next-btn')
        };
    }

    bindEvents() {
        // Eventos de cierre estándar (ESC, click fuera, botón X)
        setupModalClose(this.elements.modal, () => this.close());

        // Navegación con flechas (específico de este modal)
        document.addEventListener('keydown', (e) => {
            if (!this.isOpen()) return;
            if (e.key === 'ArrowLeft') this.navigate(-1);
            else if (e.key === 'ArrowRight') this.navigate(1);
        });

        // Botones de navegación
        this.elements.prevBtn?.addEventListener('click', () => this.navigate(-1));
        this.elements.nextBtn?.addEventListener('click', () => this.navigate(1));
    }

    isOpen() {
        return this.elements.modal?.classList.contains('active');
    }

    async open(pierKey, pierLabel, initialPlot) {
        this.pierKey = pierKey;
        this.pierLabel = pierLabel;

        // Mostrar modal con plot inicial
        if (this.elements.title) {
            this.elements.title.textContent = `Diagrama P-M - ${pierLabel}`;
        }
        if (this.elements.plotImg) {
            this.elements.plotImg.src = `data:image/png;base64,${initialPlot}`;
        }
        this.elements.modal?.classList.add('active');

        // Cargar combinaciones
        await this.loadCombinations();
    }

    close() {
        this.elements.modal?.classList.remove('active');
        this.pierKey = null;
        this.pierLabel = null;
        this.combinations = [];
        this.currentIndex = 0;
    }

    async loadCombinations() {
        try {
            const data = await structuralAPI.getPierCombinations(
                this.page.sessionId,
                this.pierKey
            );

            if (data.success) {
                this.combinations = data.combinations;
                this.renderCombinationList();

                if (this.elements.totalCombos) {
                    this.elements.totalCombos.textContent = data.combinations.length;
                }

                // Seleccionar primera combinación
                if (data.combinations.length > 0) {
                    this.selectCombination(0);
                }
            }
        } catch (error) {
            console.error('Error loading combinations:', error);
        }
    }

    renderCombinationList() {
        if (!this.elements.comboList) return;

        this.elements.comboList.innerHTML = '';

        this.combinations.forEach((combo, index) => {
            const item = document.createElement('div');
            item.className = 'combo-item';
            item.dataset.index = index;
            item.addEventListener('click', () => this.selectCombination(index));

            item.innerHTML = `
                <span class="combo-name">${combo.name} (${combo.location})</span>
                <span class="combo-moment">M=${combo.M_resultant.toFixed(1)}</span>
                <span class="combo-angle">${combo.angle_deg.toFixed(1)}°</span>
            `;

            this.elements.comboList.appendChild(item);
        });
    }

    async selectCombination(index) {
        if (index < 0 || index >= this.combinations.length) return;

        this.currentIndex = index;
        const combo = this.combinations[index];

        // Actualizar índice
        if (this.elements.currentIndexEl) {
            this.elements.currentIndexEl.textContent = index + 1;
        }

        // Actualizar estado activo en lista
        document.querySelectorAll('.combo-item').forEach((item, i) => {
            item.classList.toggle('active', i === index);
        });

        // Scroll a item activo
        const activeItem = document.querySelector('.combo-item.active');
        if (activeItem) {
            activeItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Actualizar info de combinación
        this.updateComboInfo(combo);

        // Obtener diagrama actualizado
        await this.fetchCombinationDiagram(combo);
    }

    updateComboInfo(combo) {
        if (this.elements.comboName) {
            this.elements.comboName.textContent = combo.full_name;
        }
        if (this.elements.comboP) {
            this.elements.comboP.textContent = combo.P.toFixed(2);
        }
        if (this.elements.comboM2) {
            this.elements.comboM2.textContent = combo.M2.toFixed(2);
        }
        if (this.elements.comboM3) {
            this.elements.comboM3.textContent = combo.M3.toFixed(2);
        }
        if (this.elements.comboM) {
            this.elements.comboM.textContent = combo.M_resultant.toFixed(2);
        }
        if (this.elements.comboAngle) {
            this.elements.comboAngle.textContent = combo.angle_deg.toFixed(1);
        }
    }

    async fetchCombinationDiagram(combo) {
        this.setLoading(true);

        try {
            const data = await structuralAPI.analyzeCombination({
                session_id: this.page.sessionId,
                pier_key: this.pierKey,
                combination_index: combo.index,
                generate_plot: true
            });

            if (data.success && data.pm_plot) {
                this.elements.plotImg.src = `data:image/png;base64,${data.pm_plot}`;
            }
        } catch (error) {
            console.error('Error fetching combination diagram:', error);
        } finally {
            this.setLoading(false);
        }
    }

    setLoading(loading) {
        if (this.elements.plotLoading) {
            this.elements.plotLoading.style.display = loading ? 'block' : 'none';
        }
        if (this.elements.plotImg) {
            this.elements.plotImg.style.opacity = loading ? '0.3' : '1';
        }
    }

    navigate(delta) {
        const newIndex = this.currentIndex + delta;
        if (newIndex >= 0 && newIndex < this.combinations.length) {
            this.selectCombination(newIndex);
        }
    }
}
