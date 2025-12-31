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

# Archivos a ignorar
IGNORE_FILES = {'nul', '.DS_Store', 'Thumbs.db'}

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
    'pier_analysis.py': 'Servicio principal de análisis de piers',
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
    '__init__.py': 'Inicialización del módulo',

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


def count_lines(filepath: Path) -> int:
    """Cuenta las líneas de un archivo de texto."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def get_comment(filename: str) -> str:
    """Obtiene un comentario corto para el archivo."""
    if filename in FILE_COMMENTS:
        return FILE_COMMENTS[filename]

    # Comentarios genéricos por extensión
    ext = os.path.splitext(filename)[1]
    if ext == '.py':
        if filename.startswith('test_'):
            base = filename[5:-3]  # Remove test_ and .py
            return f'Tests para {base}'
        return 'Módulo Python'
    elif ext == '.js':
        return 'Módulo JavaScript'
    elif ext == '.css':
        return 'Hoja de estilos'
    elif ext == '.html':
        return 'Template HTML'
    elif ext == '.json':
        return 'Configuración JSON'
    elif ext == '.md':
        return 'Documentación Markdown'
    elif ext == '.xlsx':
        return 'Archivo Excel'
    elif ext in ('.yml', '.yaml'):
        return 'Configuración YAML'
    elif ext == '.txt':
        return 'Archivo de texto'
    elif ext == '.ini':
        return 'Archivo de configuración'

    return ''


def generate_tree(root_path: Path, output_path: Path):
    """Genera el árbol de archivos con comentarios y líneas."""
    total_lines = 0
    total_files = 0
    lines_by_type = {}

    output = []
    output.append("=" * 70)
    output.append("  INGEO STRUCTURES - Estructura del Proyecto")
    output.append(f"  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 70)
    output.append("")

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filtrar directorios ignorados
        dirnames[:] = [d for d in dirnames if not should_ignore(d, is_dir=True)]
        dirnames.sort()

        # Calcular nivel de indentación
        rel_path = Path(dirpath).relative_to(root_path)
        level = len(rel_path.parts)
        indent = "│   " * level

        # Nombre del directorio
        if level > 0:
            dir_name = Path(dirpath).name
            output.append(f"{indent[:-4]}├── {dir_name}/")

        # Archivos en este directorio
        valid_files = [f for f in sorted(filenames) if not should_ignore(f)]

        for i, filename in enumerate(valid_files):
            filepath = Path(dirpath) / filename
            lines = count_lines(filepath)
            comment = get_comment(filename)

            # Acumular estadísticas
            total_lines += lines
            total_files += 1
            ext = os.path.splitext(filename)[1] or 'other'
            lines_by_type[ext] = lines_by_type.get(ext, 0) + lines

            # Formatear línea
            is_last = (i == len(valid_files) - 1)
            prefix = "└── " if is_last else "├── "
            line_info = f"({lines:>4} líneas)"

            if comment:
                output.append(f"{indent}{prefix}{filename:<30} {line_info}  # {comment}")
            else:
                output.append(f"{indent}{prefix}{filename:<30} {line_info}")

    # Resumen final
    output.append("")
    output.append("=" * 70)
    output.append("  RESUMEN")
    output.append("=" * 70)
    output.append(f"  Total de archivos: {total_files}")
    output.append(f"  Total de líneas:   {total_lines:,}")
    output.append("")
    output.append("  Líneas por tipo de archivo:")
    for ext, lines in sorted(lines_by_type.items(), key=lambda x: -x[1]):
        pct = lines / total_lines * 100 if total_lines > 0 else 0
        output.append(f"    {ext:<10} {lines:>6,} líneas ({pct:>5.1f}%)")
    output.append("=" * 70)

    # Escribir archivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    return total_files, total_lines


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
