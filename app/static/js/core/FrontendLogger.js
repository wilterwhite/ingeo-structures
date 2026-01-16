// app/static/js/core/FrontendLogger.js
/**
 * Logger del frontend para debugging.
 * Captura el estado de las tablas y lo envía al backend para escribir
 * en un archivo de log que se sobreescribe (no acumula).
 *
 * Uso: Permite a Claude Code ver el estado del frontend sin acceso al navegador.
 */

class FrontendLogger {
    constructor(page) {
        this.page = page;
        this.enabled = true;
        this.debounceTimer = null;
        this.debounceDelay = 500; // ms
    }

    /**
     * Habilita/deshabilita el logger.
     */
    setEnabled(enabled) {
        this.enabled = enabled;
    }

    /**
     * Captura el estado actual y lo envía al backend (con debounce).
     */
    log() {
        if (!this.enabled) return;

        // Debounce para no saturar con llamadas
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this._doLog(), this.debounceDelay);
    }

    /**
     * Envía el log inmediatamente (sin debounce).
     */
    logNow() {
        if (!this.enabled) return;
        clearTimeout(this.debounceTimer);
        this._doLog();
    }

    async _doLog() {
        try {
            const content = this._buildLogContent();
            await fetch('/api/frontend-log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
        } catch (e) {
            // Silenciar errores - el log es opcional
            console.debug('[FrontendLogger] Error:', e.message);
        }
    }

    _buildLogContent() {
        const lines = [];
        const now = new Date().toLocaleString('es-CL');

        lines.push('='.repeat(70));
        lines.push(`FRONTEND STATE LOG - ${now}`);
        lines.push('='.repeat(70));
        lines.push('');

        // Página actual
        lines.push(`Pagina activa: ${this.page.currentPage || 'config-page'}`);
        lines.push(`Session ID: ${this.page.sessionId || 'ninguna'}`);
        lines.push('');

        // Estadísticas generales
        lines.push('-'.repeat(40));
        lines.push('ESTADISTICAS GENERALES');
        lines.push('-'.repeat(40));
        lines.push(`Piers: ${this.page.results?.length || 0}`);
        lines.push(`Columnas: ${this.page.columnResults?.length || 0}`);
        lines.push(`Vigas: ${this.page.beamResults?.length || 0}`);
        lines.push(`Drop Beams: ${this.page.dropBeamResults?.length || 0}`);
        lines.push('');

        // Tabla de elementos verticales (piers + columnas)
        if (this.page.results?.length > 0 || this.page.columnResults?.length > 0) {
            lines.push(this._buildVerticalElementsTable());
        }

        // Tabla de vigas
        if (this.page.beamResults?.length > 0 || this.page.dropBeamResults?.length > 0) {
            lines.push(this._buildBeamsTable());
        }

        // Errores de consola (últimos)
        lines.push(this._buildConsoleErrors());

        return lines.join('\n');
    }

    _buildVerticalElementsTable() {
        const lines = [];
        lines.push('-'.repeat(160));
        lines.push('TABLA: ELEMENTOS VERTICALES');
        lines.push('-'.repeat(160));

        // Header línea 1
        const header1 = this._padColumns([
            'Elemento', 'Story', 'Cat', 'Geometria', 'Enfierradura', 'Borde', 'V.Izq', 'V.Der', 'DCR Flex', 'Flexocompresion', 'DCR Corte', 'Corte', 'Estado'
        ], [10, 7, 5, 12, 18, 12, 6, 6, 8, 24, 8, 20, 6]);
        lines.push(header1);
        lines.push('-'.repeat(160));

        // Combinar piers y columnas
        const allVertical = [
            ...(this.page.results || []),
            ...(this.page.columnResults || [])
        ];

        allVertical.forEach(r => {
            const label = r.pier_label || r.label || r.key || '-';
            const story = r.story || '-';

            // Categoría sísmica
            const cat = r.seismic_category || 'SPEC';

            // Geometría
            let geom = r.dimensions_display || '-';

            // Enfierradura (malla): nM φV@sV / φH@sH
            let enfierr = '-';
            const reinf = r.reinforcement || {};
            if (reinf.n_meshes !== undefined) {
                const warnV = reinf.warnings_v?.length > 0 ? '⚠' : '';
                const warnH = reinf.warnings_h?.length > 0 ? '⚠' : '';
                enfierr = `${reinf.n_meshes}M φ${reinf.diameter_v || 8}@${reinf.spacing_v || 200}${warnV}`;
            }

            // Borde: nφ φdb + estribos
            let borde = '-';
            if (reinf.n_edge_bars !== undefined) {
                const warnRho = !reinf.rho_v_ok ? '⚠' : '';
                borde = `${reinf.n_edge_bars}φ${reinf.diameter_edge || 12}${warnRho}`;
                if (reinf.stirrup_diameter) {
                    borde += ` E${reinf.stirrup_diameter}@${reinf.stirrup_spacing || 150}`;
                }
            }

            // Vigas de acople (izq/der) - ahora vienen directamente del resultado
            const beamIzq = r.coupling_beam_left || 'generic';
            const beamDer = r.coupling_beam_right || 'generic';
            const vIzq = beamIzq === 'generic' ? 'Gen' : (beamIzq === 'none' ? '-' : beamIzq.substring(0, 6));
            const vDer = beamDer === 'generic' ? 'Gen' : (beamDer === 'none' ? '-' : beamDer.substring(0, 6));

            // DCRs
            const dcrFlexVal = r.flexure?.dcr;
            const dcrShearVal = r.shear?.dcr;
            const dcrFlex = dcrFlexVal !== undefined ? dcrFlexVal.toFixed(2) : '-';
            const dcrShear = dcrShearVal !== undefined ? dcrShearVal.toFixed(2) : '-';

            // Flexocompresión
            let flexInfo = '-';
            const flex = r.flexure || {};
            if (flex.exceeds_tension) {
                flexInfo = `Pu=${flex.Pu}t<φPt TRACC`;
            } else if (flex.exceeds_axial) {
                flexInfo = `Pu=${flex.Pu}t>φPn`;
            } else if (flex.Pu !== undefined) {
                const phiMn = flex.phi_Mn_at_Pu || 0;
                flexInfo = `Pu=${flex.Pu}t φMn=${phiMn.toFixed(0)}t-m`;
            }

            // Corte
            let shearInfo = '-';
            const sh = r.shear || {};
            if (sh.phi_Vn_2 !== undefined) {
                const Vu = sh.Vu_original || sh.Vu_2 || 0;
                shearInfo = `φVn=${sh.phi_Vn_2.toFixed(0)}t Vu=${Vu.toFixed(0)}t`;
            }

            // Estado
            const maxDcr = Math.max(dcrFlexVal || 0, dcrShearVal || 0);
            let estado = maxDcr > 1.0 ? 'FAIL' : 'OK';
            if (r.overall_status === 'NO OK' && maxDcr <= 1.0) {
                estado = 'WARN';
            }

            const row = this._padColumns([
                label.substring(0, 10),
                story.substring(0, 7),
                cat.substring(0, 5),
                geom.substring(0, 12),
                enfierr.substring(0, 18),
                borde.substring(0, 12),
                vIzq,
                vDer,
                dcrFlex,
                flexInfo.substring(0, 24),
                dcrShear,
                shearInfo.substring(0, 20),
                estado
            ], [10, 7, 5, 12, 18, 12, 6, 6, 8, 24, 8, 20, 6]);
            lines.push(row);
        });

        lines.push('');
        return lines.join('\n');
    }

    _buildBeamsTable() {
        const lines = [];
        lines.push('-'.repeat(80));
        lines.push('TABLA: VIGAS');
        lines.push('-'.repeat(80));

        const header = this._padColumns([
            'Viga', 'Story', 'Tipo', 'Seccion', 'DCR Flex', 'DCR Corte', 'Estado'
        ], [15, 10, 8, 15, 10, 10, 8]);
        lines.push(header);
        lines.push('-'.repeat(80));

        // Combinar beams y drop beams
        const allBeams = [
            ...(this.page.beamResults || []),
            ...(this.page.dropBeamResults || [])
        ];

        allBeams.forEach(r => {
            const tipo = r.element_type === 'drop_beam' ? 'DROP' : 'BEAM';
            const label = r.label || r.key || '-';
            const story = r.story || '-';

            // Sección - usar dimensions_display (pre-formateado) o geometry.width_m/thickness_m
            let seccion = r.dimensions_display || (
                r.geometry?.width_m && r.geometry?.thickness_m
                    ? `${(r.geometry.width_m * 100).toFixed(0)}x${(r.geometry.thickness_m * 100).toFixed(0)}cm`
                    : '-'
            );

            // DCRs - buscar en flexure/shear objects
            const dcrFlexVal = r.flexure?.dcr;
            const dcrShearVal = r.shear?.dcr;
            const dcrFlex = dcrFlexVal !== undefined ? dcrFlexVal.toFixed(2) : '-';
            const dcrShear = dcrShearVal !== undefined ? dcrShearVal.toFixed(2) : '-';

            // Estado basado en DCR
            const maxDcr = Math.max(dcrFlexVal || 0, dcrShearVal || 0);
            let estado = maxDcr > 1.0 ? 'FAIL' : 'OK';
            if (r.overall_status === 'NO OK' && maxDcr <= 1.0) {
                estado = 'WARN';
            }

            const row = this._padColumns([
                label.substring(0, 15),
                story.substring(0, 10),
                tipo,
                seccion,
                dcrFlex,
                dcrShear,
                estado
            ], [15, 10, 8, 15, 10, 10, 8]);
            lines.push(row);
        });

        lines.push('');
        return lines.join('\n');
    }

    _buildConsoleErrors() {
        const lines = [];
        lines.push('-'.repeat(40));
        lines.push('ERRORES RECIENTES (si hay)');
        lines.push('-'.repeat(40));

        // Verificar si hay errores capturados
        if (window._frontendErrors && window._frontendErrors.length > 0) {
            window._frontendErrors.slice(-5).forEach(err => {
                lines.push(`[${err.time}] ${err.message}`);
            });
        } else {
            lines.push('(sin errores)');
        }
        lines.push('');
        return lines.join('\n');
    }

    _padColumns(values, widths) {
        return values.map((v, i) => {
            const s = String(v || '-');
            return s.padEnd(widths[i] || 10);
        }).join(' ');
    }

    /**
     * Inicializa captura de errores de consola.
     */
    initErrorCapture() {
        window._frontendErrors = [];
        const originalError = console.error;
        console.error = (...args) => {
            const msg = args.map(a => String(a)).join(' ');
            window._frontendErrors.push({
                time: new Date().toLocaleTimeString('es-CL'),
                message: msg.substring(0, 200)
            });
            // Mantener solo los últimos 10
            if (window._frontendErrors.length > 10) {
                window._frontendErrors.shift();
            }
            originalError.apply(console, args);
        };
    }
}

// Singleton global
window.frontendLogger = null;
