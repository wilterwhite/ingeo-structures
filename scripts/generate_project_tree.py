#!/usr/bin/env python
"""
Genera un archivo con la estructura de carpetas y archivos del proyecto.
Incluye comentarios cortos y conteo de líneas para cada archivo.
"""
import os
from pathlib import Path
from datetime import datetime

# Directorios a ignorar
IGNORE_DIRS = {
    '__pycache__', '.git', 'venv', 'node_modules', '.pytest_cache',
    '.mypy_cache', '.tox', 'dist', 'build', '*.egg-info', '.idea',
    '.vscode', 'htmlcov', '.coverage', 'docs', 'examples', 'tests',
    'scripts'
}

# Extensiones a ignorar
IGNORE_EXTENSIONS = {'.pyc', '.pyo', '.exe', '.dll', '.so', '.dylib'}

# Extensiones binarias (no cuentan líneas de código)
BINARY_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.bmp', '.svg',
                     '.pdf', '.zip', '.tar', '.gz', '.woff', '.woff2', '.ttf',
                     '.eot', '.mp3', '.mp4', '.wav', '.avi', '.mov'}

# Archivos a ignorar
IGNORE_FILES = {'nul', '.DS_Store', 'Thumbs.db', '__init__.py'}

# Comentarios por patrón de nombre de archivo
FILE_COMMENTS = {
    # App domain
    'pier.py': 'Entidad Pier: muro de hormigón armado',
    'design_proposal.py': 'Propuestas de diseño para piers que fallan',
    'verification_result.py': 'Resultados de verificación estructural',
    'coupling_beam.py': 'Configuración de vigas de acople',
    'reinforcement_calculator.py': 'Cálculo de áreas de refuerzo',
    'steel_layer_calculator.py': 'Cálculo de capas de acero para P-M',
    'wall_continuity.py': 'Cálculo de altura efectiva hwcs',
    'materials.py': 'Constantes de materiales (barras, hormigón)',
    'units.py': 'Factores de conversión de unidades',

    # Services
    'structural_analysis.py': 'Servicio principal de análisis estructural',
    'flexure_service.py': 'Verificación de flexión con diagrama P-M',
    'shear_service.py': 'Verificación de corte según ACI 318',
    'slenderness_service.py': 'Verificación de esbeltez según ACI 318',
    'proposal_service.py': 'Generación de propuestas de diseño',
    'pm_diagram.py': 'Generación de diagrama de interacción P-M',
    'section_diagram.py': 'Generación de diagrama de sección',
    'session_manager.py': 'Gestión de sesiones de análisis',
    'excel_parser.py': 'Parser de archivos Excel de ETABS',
    'reinforcement_config.py': 'Configuración de armadura',

    # Routes
    'routes.py': 'Rutas Flask de la API',
    'run.py': 'Punto de entrada de la aplicación',

    # Frontend
    'StructuralAPI.js': 'API client para comunicación con backend',
    'StructuralPage.js': 'Controlador principal de la página',
    'ResultsTable.js': 'Renderizado de tabla de resultados',
    'PiersTable.js': 'Renderizado de tabla de piers',
    'PlotModal.js': 'Modal para diagrama P-M interactivo',
    'structural.css': 'Estilos principales de la aplicación',
    'tables.css': 'Estilos de tablas de piers y resultados',
    'modals.css': 'Estilos de ventanas modales',
    'structural_standalone.html': 'Template HTML principal',

    # Tests
    'conftest.py': 'Fixtures compartidos para pytest',

    # Config
    'requirements.txt': 'Dependencias Python del proyecto',
    'pytest.ini': 'Configuración de pytest',
    '.gitignore': 'Archivos ignorados por git',
    'README.md': 'Documentación del proyecto',
}


def should_ignore(name: str, is_dir: bool = False) -> bool:
    """Determina si un archivo o directorio debe ser ignorado."""
    if name in IGNORE_FILES:
        return True
    if is_dir:
        return name in IGNORE_DIRS or name.startswith('.')
    ext = os.path.splitext(name)[1]
    return ext in IGNORE_EXTENSIONS


def is_binary_file(filepath: Path) -> bool:
    """Determina si un archivo es binario (imagen, etc.)."""
    ext = filepath.suffix.lower()
    return ext in BINARY_EXTENSIONS


def count_lines(filepath: Path) -> int:
    """Cuenta las líneas de un archivo de texto.

    Retorna 0 para archivos binarios (imágenes, etc.).
    """
    if is_binary_file(filepath):
        return 0

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def get_comment(filename: str) -> str:
    """Obtiene un comentario corto para el archivo.

    Solo retorna comentarios específicos definidos en FILE_COMMENTS.
    NO genera comentarios genéricos como "Módulo Python" que son obvios.
    """
    if filename in FILE_COMMENTS:
        return FILE_COMMENTS[filename]

    # Solo comentarios específicos para tests
    ext = os.path.splitext(filename)[1]
    if ext == '.py' and filename.startswith('test_'):
        base = filename[5:-3]  # Remove test_ and .py
        return f'Tests para {base}'

    # No generar comentarios genéricos obvios
    return ''


class TreeStats:
    """Acumula estadísticas durante la generación del árbol."""
    def __init__(self):
        self.total_lines = 0
        self.total_files = 0
        self.lines_by_type = {}

    def add_file(self, filepath: Path, lines: int):
        self.total_lines += lines
        self.total_files += 1
        ext = filepath.suffix or 'other'
        self.lines_by_type[ext] = self.lines_by_type.get(ext, 0) + lines


def build_tree_recursive(
    dir_path: Path,
    prefix: str,
    output: list,
    stats: TreeStats
):
    """Construye el árbol recursivamente con prefijos correctos.

    Args:
        dir_path: Directorio a procesar
        prefix: Prefijo de indentación actual (ej: "│   │   ")
        output: Lista donde agregar líneas de salida
        stats: Objeto para acumular estadísticas
    """
    # Obtener contenido del directorio
    try:
        entries = list(dir_path.iterdir())
    except PermissionError:
        return

    # Separar y filtrar directorios y archivos
    subdirs = sorted([e for e in entries if e.is_dir() and not should_ignore(e.name, is_dir=True)])
    files = sorted([e for e in entries if e.is_file() and not should_ignore(e.name)])

    # Combinar: primero archivos, luego directorios
    all_entries = files + subdirs
    total = len(all_entries)

    for i, entry in enumerate(all_entries):
        is_last = (i == total - 1)
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "

        if entry.is_file():
            # Archivo
            lines = count_lines(entry)
            comment = get_comment(entry.name)
            stats.add_file(entry, lines)

            # Formato: para binarios mostrar (binario) en vez de líneas
            if is_binary_file(entry):
                line_info = "(binario)"
            else:
                line_info = f"({lines:>4} líneas)"

            if comment:
                output.append(f"{prefix}{connector}{entry.name:<35} {line_info}  # {comment}")
            else:
                output.append(f"{prefix}{connector}{entry.name:<35} {line_info}")
        else:
            # Directorio
            output.append(f"{prefix}{connector}{entry.name}/")
            build_tree_recursive(entry, prefix + extension, output, stats)


def generate_tree(root_path: Path, output_path: Path):
    """Genera el árbol de archivos con comentarios y líneas."""
    stats = TreeStats()
    output = []

    output.append("=" * 70)
    output.append("  INGEO STRUCTURES - Estructura del Proyecto")
    output.append(f"  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 70)
    output.append("")
    output.append(f"{root_path.name}/")

    # Construir árbol recursivamente
    build_tree_recursive(root_path, "", output, stats)

    # Resumen final
    output.append("")
    output.append("=" * 70)
    output.append("  RESUMEN")
    output.append("=" * 70)
    output.append(f"  Total de archivos: {stats.total_files}")
    output.append(f"  Total de líneas de código: {stats.total_lines:,}")
    output.append("")
    output.append("  Líneas por tipo de archivo:")
    for ext, lines in sorted(stats.lines_by_type.items(), key=lambda x: -x[1]):
        if lines > 0:  # Solo mostrar tipos con líneas de código
            pct = lines / stats.total_lines * 100 if stats.total_lines > 0 else 0
            output.append(f"    {ext:<10} {lines:>6,} líneas ({pct:>5.1f}%)")
    output.append("=" * 70)

    # Escribir archivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    return stats.total_files, stats.total_lines


def main():
    # Obtener raíz del proyecto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Archivo de salida
    output_file = project_root / 'PROJECT_STRUCTURE.txt'

    print(f"Generando estructura del proyecto...")
    print(f"Raíz: {project_root}")

    total_files, total_lines = generate_tree(project_root, output_file)

    print(f"\nEstructura generada en: {output_file}")
    print(f"Total: {total_files} archivos, {total_lines:,} líneas")


if __name__ == '__main__':
    main()
