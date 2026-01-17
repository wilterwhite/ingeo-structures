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
            const structuredState = this._buildStructuredState();

            await fetch('/api/frontend-log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content,
                    ...structuredState
                })
            });
        } catch (e) {
            // Silenciar errores - el log es opcional
            console.debug('[FrontendLogger] Error:', e.message);
        }
    }

    /**
     * Construye estado estructurado para ClaudeStateLogger.
     */
    _buildStructuredState() {
        const tables = {};

        // Helper para calcular resumen de tabla
        const summarizeTable = (items, name) => {
            if (items.length === 0) return;
            const dcrs = items.map(r => r.flexure?.dcr || 0).filter(d => d > 0);
            const minDcr = dcrs.length > 0 ? Math.min(...dcrs) : 0;
            const maxDcr = dcrs.length > 0 ? Math.max(...dcrs) : 0;
            tables[name] = `${items.length} rows, DCR [${minDcr.toFixed(2)}-${maxDcr.toFixed(2)}]`;
        };

        const piers = this.page.results || [];
        const columns = this.page.columnResults || [];
        const beams = this.page.beamResults || [];
        const dropBeams = this.page.dropBeamResults || [];

        summarizeTable(piers, 'Piers');
        summarizeTable(columns, 'Columns');
        summarizeTable(beams, 'Beams');
        summarizeTable(dropBeams, 'DropBeams');

        // Contar warnings
        let warningsCount = 0;
        [...piers, ...columns, ...beams, ...dropBeams].forEach(r => {
            const reinf = r.reinforcement || {};
            if (reinf.warnings_v?.length > 0) warningsCount += reinf.warnings_v.length;
            if (reinf.warnings_h?.length > 0) warningsCount += reinf.warnings_h.length;
            if (r.warnings?.length > 0) warningsCount += r.warnings.length;
        });

        return {
            page: this.page.currentPage || 'config-page',
            tables,
            warnings_count: warningsCount,
            last_action: this._lastAction || ''
        };
    }

    /**
     * Registra la última acción del usuario.
     * @param {string} action - Descripción de la acción
     */
    setLastAction(action) {
        this._lastAction = action;
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

        // Campos modificados (debug)
        lines.push(this._buildModifiedFieldsSection());

        // Warnings de elementos (espesor, cuantía, etc.)
        lines.push(this._buildWarningsSection());

        // Errores de consola (últimos)
        lines.push(this._buildConsoleErrors());

        return lines.join('\n');
    }

    _buildModifiedFieldsSection() {
        const lines = [];
        lines.push('-'.repeat(60));
        lines.push('CAMPOS MODIFICADOS (marcados en azul en UI)');
        lines.push('-'.repeat(60));

        const allVertical = [
            ...(this.page.results || []),
            ...(this.page.columnResults || [])
        ];

        let hasModified = false;
        allVertical.forEach(r => {
            const label = r.pier_label || r.label || r.key || '-';
            const reinf = r.reinforcement || {};
            const modFields = reinf.modified_fields || [];

            if (modFields.length > 0) {
                hasModified = true;
                lines.push(`${label}: ${modFields.join(', ')}`);
            }
        });

        if (!hasModified) {
            lines.push('(ninguno)');
        }

        lines.push('');
        return lines.join('\n');
    }

    _buildWarningsSection() {
        const lines = [];
        lines.push('-'.repeat(60));
        lines.push('WARNINGS (espesor, cuantía, etc.)');
        lines.push('-'.repeat(60));

        const allVertical = [
            ...(this.page.results || []),
            ...(this.page.columnResults || [])
        ];

        let hasWarnings = false;
        allVertical.forEach(r => {
            const label = r.pier_label || r.label || r.key || '-';
            const reinf = r.reinforcement || {};
            const warnings = [];

            // Warnings de armadura vertical
            if (reinf.warnings_v && reinf.warnings_v.length > 0) {
                warnings.push(...reinf.warnings_v);
            }

            // Warnings de armadura horizontal
            if (reinf.warnings_h && reinf.warnings_h.length > 0) {
                warnings.push(...reinf.warnings_h);
            }

            // Warning de cuantía
            if (reinf.rho_v_ok === false) {
                warnings.push('ρv < ρmin');
            }
            if (reinf.rho_v_exceeds_max === true) {
                warnings.push('ρv > ρmax (4%)');
            }

            // Warnings generales del resultado
            if (r.warnings && r.warnings.length > 0) {
                warnings.push(...r.warnings);
            }

            if (warnings.length > 0) {
                hasWarnings = true;
                lines.push(`${label}: ${warnings.join(', ')}`);
            }
        });

        if (!hasWarnings) {
            lines.push('(ninguno)');
        }

        lines.push('');
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

            // Enfierradura - detectar tipo: STIRRUPS (columnas) vs MESH (piers)
            let enfierr = '-';
            let borde = '-';
            const reinf = r.reinforcement || {};

            // Campos modificados por el usuario (para debug)
            const modFields = reinf.modified_fields || [];
            const modMark = modFields.length > 0 ? '*' : '';

            // Detectar si es armadura discreta (columnas) o malla (piers)
            if (reinf.n_bars_depth > 0 || reinf.n_bars_width > 0) {
                // STIRRUPS Layout (Columna): nxm φdb
                const nDepth = reinf.n_bars_depth || 0;
                const nWidth = reinf.n_bars_width || 0;
                const dLong = reinf.diameter_long || 16;
                enfierr = `${nDepth}x${nWidth} φ${dLong}${modMark}`;
                // Estribos/Trabas para columnas
                if (reinf.stirrup_diameter && reinf.stirrup_spacing) {
                    const prefix = reinf.has_crossties ? 'T' : 'E';  // T=Traba, E=Estribo
                    borde = `${prefix}${reinf.stirrup_diameter}@${reinf.stirrup_spacing}`;
                } else {
                    borde = 'Sin estribos';
                }
            } else if (reinf.n_meshes !== undefined && reinf.n_meshes > 0) {
                // MESH Layout (Pier): nM φV@sV
                const warnV = reinf.warnings_v?.length > 0 ? '⚠' : '';
                enfierr = `${reinf.n_meshes}M φ${reinf.diameter_v || 8}@${reinf.spacing_v || 200}${warnV}${modMark}`;
                // Borde: nφ φdb + estribos
                if (reinf.n_edge_bars !== undefined) {
                    const warnRho = !reinf.rho_v_ok ? '⚠' : '';
                    borde = `${reinf.n_edge_bars}φ${reinf.diameter_edge || 12}${warnRho}`;
                    if (reinf.stirrup_diameter) {
                        borde += ` E${reinf.stirrup_diameter}@${reinf.stirrup_spacing || 150}`;
                    }
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

            // Corte - manejar tanto muros/columnas (phi_Vn_2) como struts (phi_Vn)
            let shearInfo = '-';
            const sh = r.shear || {};
            if (sh.phi_Vn_2 !== undefined) {
                // Muros y columnas
                const Vu = sh.Vu_original || sh.Vu_2 || 0;
                shearInfo = `φVn=${sh.phi_Vn_2.toFixed(0)}t Vu=${Vu.toFixed(0)}t`;
            } else if (sh.phi_Vn !== undefined) {
                // Struts (phi_Vn = phi_Vcr)
                const Vu = sh.Vu || 0;
                const cracked = sh.is_cracked ? '⚠' : '';
                shearInfo = `φVc=${sh.phi_Vn.toFixed(1)}t Vu=${Vu.toFixed(1)}t${cracked}`;
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
     * Loggea el proceso de importación de archivos.
     * @param {string} phase - Fase del proceso: 'start', 'file', 'complete', 'error'
     * @param {Object} data - Datos del evento
     */
    logImport(phase, data = {}) {
        if (!this.enabled) return;

        const now = new Date().toLocaleTimeString('es-CL');
        let message = '';

        switch (phase) {
            case 'start':
                message = `[${now}] IMPORT START: ${data.fileCount} archivo(s)`;
                if (data.files) {
                    data.files.forEach((f, i) => {
                        message += `\n  - Archivo ${i + 1}: ${f.name} (${(f.size / 1024).toFixed(1)} KB)`;
                    });
                }
                break;

            case 'file':
                message = `[${now}] PROCESANDO: Archivo ${data.fileIndex + 1}/${data.totalFiles} - ${data.fileName}`;
                if (data.sessionId) {
                    message += ` (session: ${data.sessionId.substring(0, 8)}...)`;
                }
                if (data.merge) {
                    message += ' [MERGE]';
                }
                break;

            case 'progress':
                message = `[${now}] PROGRESO: ${data.current}/${data.total} - ${data.element || ''}`;
                break;

            case 'file_complete':
                message = `[${now}] ARCHIVO COMPLETADO: ${data.fileName}`;
                if (data.summary) {
                    const s = data.summary;
                    const counts = [];
                    if (s.total_piers > 0) counts.push(`${s.total_piers} piers`);
                    if (s.total_columns > 0) counts.push(`${s.total_columns} columnas`);
                    if (s.total_beams > 0) counts.push(`${s.total_beams} vigas`);
                    if (s.total_drop_beams > 0) counts.push(`${s.total_drop_beams} drop beams`);
                    message += `\n  Elementos: ${counts.join(', ') || 'ninguno'}`;
                }
                if (data.merged) {
                    message += ' [DATOS COMBINADOS]';
                }
                break;

            case 'analysis_start':
                message = `[${now}] ANALISIS START: session=${data.sessionId?.substring(0, 8) || '-'}...`;
                break;

            case 'analysis_progress':
                message = `[${now}] ANALIZANDO: ${data.current}/${data.total} - ${data.element || ''}`;
                break;

            case 'complete':
                message = `[${now}] IMPORT COMPLETE`;
                if (data.summary) {
                    const s = data.summary;
                    message += `\n  Total: ${s.total_piers || 0} piers, ${s.total_columns || 0} columnas, ${s.total_beams || 0} vigas`;
                }
                if (data.duration) {
                    message += `\n  Duracion: ${data.duration}ms`;
                }
                break;

            case 'error':
                message = `[${now}] ERROR: ${data.message || 'Error desconocido'}`;
                if (data.fileName) {
                    message += ` (archivo: ${data.fileName})`;
                }
                break;

            default:
                message = `[${now}] ${phase}: ${JSON.stringify(data)}`;
        }

        // Agregar al buffer de import log
        if (!this._importLog) {
            this._importLog = [];
        }
        this._importLog.push(message);

        // Throttle: solo enviar cada 2 segundos para eventos de progreso
        // Enviar inmediatamente para eventos importantes
        const immediateEvents = ['start', 'file', 'file_complete', 'analysis_start', 'complete', 'error'];
        if (immediateEvents.includes(phase)) {
            this._sendImportLogNow();
        } else {
            this._sendImportLogThrottled();
        }
    }

    _sendImportLogThrottled() {
        if (this._importLogTimer) return;
        this._importLogTimer = setTimeout(() => {
            this._importLogTimer = null;
            this._sendImportLogNow();
        }, 2000);
    }

    async _sendImportLogNow() {
        if (!this.enabled || !this._importLog) return;
        if (this._sendingLog) return; // Evitar requests simultáneas

        this._sendingLog = true;
        try {
            const lines = [];
            lines.push('='.repeat(70));
            lines.push('IMPORT/ANALYSIS LOG');
            lines.push('='.repeat(70));
            lines.push('');
            lines.push(...this._importLog);
            lines.push('');
            lines.push('='.repeat(70));
            lines.push('');

            // Agregar estado actual de datos
            lines.push(this._buildLogContent());

            await fetch('/api/frontend-log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: lines.join('\n') })
            });
        } catch (e) {
            console.debug('[FrontendLogger] Error sending import log:', e.message);
        } finally {
            this._sendingLog = false;
        }
    }

    /**
     * Limpia el log de importación (llamar al inicio de nuevo import).
     */
    clearImportLog() {
        this._importLog = [];
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
