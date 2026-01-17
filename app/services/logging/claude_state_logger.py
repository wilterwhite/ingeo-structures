# app/services/logging/claude_state_logger.py
"""
Logger centralizado para visibilidad Claude-App.

Genera un archivo claude_state.log con secciones estructuradas:
- [PARSING]: tablas encontradas/faltantes, elementos creados
- [ANALYSIS]: resultados de verificacion, DCRs
- [FRONTEND]: estado actual de la UI
"""
from dataclasses import dataclass, field
from typing import Dict, List
from pathlib import Path

# Usar directorio del proyecto como base
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CLAUDE_LOG_PATH = _PROJECT_ROOT / "claude_state.log"


@dataclass
class ParsingState:
    session_id: str = ""
    files: List[str] = field(default_factory=list)
    tables_found: Dict[str, int] = field(default_factory=dict)
    tables_missing: List[str] = field(default_factory=list)
    elements_created: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


@dataclass
class AnalysisState:
    elements_analyzed: int = 0
    results: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class FrontendState:
    current_page: str = ""
    tables_visible: Dict[str, str] = field(default_factory=dict)
    warnings_shown: int = 0
    last_action: str = ""


class ClaudeStateLogger:
    """Singleton que centraliza el estado de la aplicacion para Claude."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self.parsing = ParsingState()
        self.analysis = AnalysisState()
        self.frontend = FrontendState()

    def reset(self):
        """Reinicia el estado (nueva sesion)."""
        self._init_state()
        self._write()

    # --- Parsing methods ---
    def set_session(self, session_id: str):
        # Nueva sesión = limpiar todo
        self._init_state()
        self.parsing.session_id = session_id
        self._write()

    def log_file_received(self, filename: str):
        if filename not in self.parsing.files:
            self.parsing.files.append(filename)
        self._write()

    def log_table_found(self, table_name: str, row_count: int):
        self.parsing.tables_found[table_name] = row_count
        self._write()

    def log_table_missing(self, table_name: str):
        if table_name not in self.parsing.tables_missing:
            self.parsing.tables_missing.append(table_name)
        self._write()

    def log_elements_created(self, element_type: str, count: int, fallback_count: int = 0):
        self.parsing.elements_created[element_type] = count
        if fallback_count > 0:
            warning = f"{element_type}: {fallback_count} usando fallback"
            if warning not in self.parsing.warnings:
                self.parsing.warnings.append(warning)
        self._write()

    def log_parsing_warning(self, msg: str):
        if msg not in self.parsing.warnings:
            self.parsing.warnings.append(msg)
        self._write()

    # --- Analysis methods ---
    def log_analysis_start(self, element_count: int):
        self.analysis.elements_analyzed = 0
        self.analysis.results = []
        self._write()

    def log_element_result(self, label: str, story: str, dcr: float, pu: float = 0, mn: float = 0):
        self.analysis.elements_analyzed += 1
        result_str = f"{label} ({story}): DCR={dcr:.2f}"
        if pu != 0:
            result_str += f", Pu={pu:.0f}kN"
        if mn != 0:
            result_str += f", Mn={mn:.0f}kN-m"
        self.analysis.results.append(result_str)
        self._write()

    def log_analysis_warning(self, msg: str):
        if msg not in self.analysis.warnings:
            self.analysis.warnings.append(msg)
        self._write()

    def log_analysis_error(self, msg: str):
        if msg not in self.analysis.errors:
            self.analysis.errors.append(msg)
        self._write()

    # --- Frontend methods ---
    def update_frontend_state(self, page: str, tables: Dict[str, str], warnings: int, action: str):
        self.frontend.current_page = page
        self.frontend.tables_visible = tables
        self.frontend.warnings_shown = warnings
        self.frontend.last_action = action
        self._write()

    def _write(self):
        """Escribe el estado actual al archivo."""
        try:
            content = self._format()
            CLAUDE_LOG_PATH.write_text(content, encoding='utf-8')
        except Exception:
            pass  # No fallar si hay error de escritura

    def _format(self) -> str:
        lines = []

        # PARSING section
        lines.append("[PARSING]")
        lines.append(f"  Session: {self.parsing.session_id or '(none)'}")
        lines.append(f"  Files: {', '.join(self.parsing.files) if self.parsing.files else '(none)'}")

        if self.parsing.tables_found:
            lines.append("  Tables Found:")
            for name, count in self.parsing.tables_found.items():
                lines.append(f"    - {name}: {count} rows")
        else:
            lines.append("  Tables Found: (none)")

        if self.parsing.tables_missing:
            lines.append("  Tables Missing:")
            for name in self.parsing.tables_missing:
                lines.append(f"    - {name}")

        if self.parsing.elements_created:
            lines.append("  Elements Created:")
            for etype, count in self.parsing.elements_created.items():
                lines.append(f"    - {etype}: {count}")
        else:
            lines.append("  Elements Created: (none)")

        if self.parsing.warnings:
            lines.append("  Warnings:")
            for w in self.parsing.warnings:
                lines.append(f"    - {w}")

        lines.append("")

        # ANALYSIS section
        lines.append("[ANALYSIS]")
        lines.append(f"  Elements Analyzed: {self.analysis.elements_analyzed}")

        if self.analysis.results:
            lines.append("  Results (last 10):")
            for r in self.analysis.results[-10:]:
                lines.append(f"    - {r}")

        if self.analysis.warnings:
            lines.append("  Warnings:")
            for w in self.analysis.warnings:
                lines.append(f"    - {w}")

        if self.analysis.errors:
            lines.append("  Errors:")
            for e in self.analysis.errors:
                lines.append(f"    - {e}")

        lines.append("")

        # FRONTEND section
        lines.append("[FRONTEND]")
        lines.append(f"  Current Page: {self.frontend.current_page or '(none)'}")

        if self.frontend.tables_visible:
            lines.append("  Tables Visible:")
            for name, info in self.frontend.tables_visible.items():
                lines.append(f"    - {name}: {info}")

        lines.append(f"  Warnings Shown: {self.frontend.warnings_shown}")
        lines.append(f"  Last Action: {self.frontend.last_action or '(none)'}")

        return '\n'.join(lines)


# Singleton instance
claude_logger = ClaudeStateLogger()
