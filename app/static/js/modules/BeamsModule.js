// app/static/js/modules/BeamsModule.js
/**
 * Módulo para gestión de vigas (Beams).
 * Incluye viga estándar, vigas custom y renderizado de tabla de vigas.
 * Extraído de StructuralPage.js para mejorar la organización del código.
 */
class BeamsModule {
    constructor(page) {
        this.page = page;
    }

    // =========================================================================
    // Viga Estándar
    // =========================================================================

    onStandardBeamChange() {
        const beam = {
            width: parseInt(this.page.elements.stdBeamWidth?.value) || 200,
            height: parseInt(this.page.elements.stdBeamHeight?.value) || 500,
            ln: parseInt(this.page.elements.stdBeamLn?.value) || 1500,
            nbars: parseInt(this.page.elements.stdBeamNbars?.value) || 2,
            diam: parseInt(this.page.elements.stdBeamDiam?.value) || 12
        };

        this.page.resultsTable.updateStandardBeam(beam);
    }

    // =========================================================================
    // Custom Beam Modal
    // =========================================================================

    initCustomBeamModal() {
        const modal = document.getElementById('custom-beam-modal');
        const form = document.getElementById('custom-beam-form');
        const createBtn = document.getElementById('create-custom-beam-btn');
        const cancelBtn = document.getElementById('cancel-custom-beam');

        if (!modal || !form) return;

        createBtn?.addEventListener('click', () => this.openCustomBeamModal());
        cancelBtn?.addEventListener('click', () => this.closeCustomBeamModal());
        setupModalClose(modal, () => this.closeCustomBeamModal());

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCreateCustomBeam();
        });
    }

    openCustomBeamModal() {
        const modal = document.getElementById('custom-beam-modal');
        const storySelect = document.getElementById('custom-beam-story');

        if (!modal) return;

        if (storySelect && this.page.uniqueStories.length > 0) {
            storySelect.innerHTML = this.page.uniqueStories.map(story =>
                `<option value="${story}">${story}</option>`
            ).join('');
        }

        document.getElementById('custom-beam-form')?.reset();
        modal.classList.add('active');
    }

    closeCustomBeamModal() {
        const modal = document.getElementById('custom-beam-modal');
        modal?.classList.remove('active');
    }

    async handleCreateCustomBeam() {
        const beamData = {
            label: document.getElementById('custom-beam-label')?.value || 'VC1',
            story: document.getElementById('custom-beam-story')?.value || 'Story1',
            width: parseInt(document.getElementById('custom-beam-width')?.value) || 200,
            depth: parseInt(document.getElementById('custom-beam-depth')?.value) || 500,
            length: parseInt(document.getElementById('custom-beam-length')?.value) || 3000,
            fc: parseInt(document.getElementById('custom-beam-fc')?.value) || 28,
            n_bars_top: parseInt(document.getElementById('custom-beam-nbars-top')?.value) || 3,
            diameter_top: parseInt(document.getElementById('custom-beam-diam-top')?.value) || 16,
            n_bars_bottom: parseInt(document.getElementById('custom-beam-nbars-bot')?.value) || 3,
            diameter_bottom: parseInt(document.getElementById('custom-beam-diam-bot')?.value) || 16,
            stirrup_diameter: parseInt(document.getElementById('custom-beam-stirrup-diam')?.value) || 10,
            stirrup_spacing: parseInt(document.getElementById('custom-beam-stirrup-spacing')?.value) || 150,
            n_stirrup_legs: parseInt(document.getElementById('custom-beam-stirrup-legs')?.value) || 2
        };

        try {
            const result = await structuralAPI.createCustomBeam(this.page.sessionId, beamData);

            if (result.success) {
                this.closeCustomBeamModal();
                this.page.showNotification(`Viga ${beamData.label} creada`, 'success');

                this.page.beamsData.push({
                    label: beamData.label,
                    story: beamData.story,
                    width: beamData.width,
                    depth: beamData.depth,
                    is_custom: true
                });

                this.page.resultsTable.refreshBeamSelectors();
                await this.reanalyzeBeam(result.beam_key);
            } else {
                this.page.showNotification(result.error || 'Error al crear viga', 'error');
            }
        } catch (error) {
            console.error('Error creating custom beam:', error);
            this.page.showNotification('Error al crear viga: ' + error.message, 'error');
        }
    }

    // =========================================================================
    // Análisis de Vigas
    // =========================================================================

    async reanalyzeBeam(beamKey) {
        try {
            const data = await structuralAPI.analyze({
                session_id: this.page.sessionId,
                pier_updates: [],
                generate_plots: false,
                moment_axis: 'M3',
                angle_deg: 0,
                materials_config: this.page.materials
            });

            if (data.success) {
                this.page.beamResults = data.beam_results || [];
                this.renderBeamsTable();
                this.page.showNotification('Viga actualizada', 'success');
            }
        } catch (error) {
            console.error('Error reanalyzing beam:', error);
            this.page.showNotification('Error al recalcular viga', 'error');
        }
    }

    // =========================================================================
    // Renderizado de Tabla
    // =========================================================================

    renderBeamsTable() {
        this.page.renderElementTable(
            this.page.beamResults,
            this.page.elements.beamsTableBody,
            'beam', 11, 'No hay vigas para analizar', 'Beams'
        );
    }

    clearBeamsTable() {
        if (this.page.elements.beamsTableBody) {
            this.page.elements.beamsTableBody.innerHTML = '';
        }
        this.page.updateElementStats([], 'beam');
    }
}
