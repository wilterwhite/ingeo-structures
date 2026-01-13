# app/structural/scripts/split_aci_pdf.py
"""
Script para dividir el PDF de ACI 318-25 en archivos por capítulos.

Usa la tabla de contenidos (bookmarks) del PDF para identificar los capítulos
y crear archivos separados para cada uno.

Uso:
    python app/structural/scripts/split_aci_pdf.py

Salida:
    app/structural/aci 318-25/chapters/
    ├── 00_Index.pdf              <- Índice alfabético (al inicio)
    ├── 01_Chapter_1_General.pdf
    ├── 02_Chapter_2_Notation.pdf
    ├── ...
    ├── 27_Chapter_27_...pdf
    ├── 28_Appendix_A_...pdf
    └── 33_Commentary_References.pdf
"""
import os
import re
from pathlib import Path
from typing import List, Dict

from pypdf import PdfReader, PdfWriter


def extract_bookmarks(reader: PdfReader) -> List[Dict]:
    """
    Extrae los bookmarks (tabla de contenidos) del PDF.

    Returns:
        Lista de dicts con {title, page_number, level}
    """
    bookmarks = []

    def traverse_outline(outline_items, level=0):
        """Traversa el outline completo."""
        for item in outline_items:
            if isinstance(item, list):
                # Sub-lista = nivel anidado
                traverse_outline(item, level + 1)
            else:
                # Bookmark individual
                try:
                    title = item.title
                    page_num = None
                    if hasattr(item, 'page') and item.page is not None:
                        try:
                            page_num = reader.get_destination_page_number(item)
                        except:
                            pass

                    bookmarks.append({
                        'title': title,
                        'page': page_num,
                        'level': level
                    })
                except Exception as e:
                    pass

    if reader.outline:
        traverse_outline(reader.outline, 0)

    return bookmarks


def identify_chapters(bookmarks: List[Dict]) -> List[Dict]:
    """
    Identifica los capítulos principales de ACI 318.

    ACI 318-25 tiene capítulos numerados del 1 al 27 (aproximadamente).
    También incluye secciones como "Foreword", "Preface", etc.
    """
    chapters = []

    # Patrones para identificar capítulos
    chapter_patterns = [
        r'^CHAPTER\s+(\d+)',           # "CHAPTER 1"
        r'^(\d+)\s*[-—–]\s*(.+)',      # "1 - General" o "1—General"
        r'^(\d+)\.\s*(.+)',            # "1. General"
        r'^Part\s+(\d+)',              # "Part 1"
        r'^PART\s+(\d+)',              # "PART 1"
        r'^(Foreword|Preface|Introduction|Contents|Notation)',  # Secciones especiales
        r'^(FOREWORD|PREFACE|INTRODUCTION|CONTENTS|NOTATION)',
        r'^(Commentary|COMMENTARY)',   # Comentario
        r'^(Appendix|APPENDIX)\s*([A-Z])?',  # Apéndices
    ]

    for bm in bookmarks:
        title = bm['title'].strip()
        page = bm['page']
        level = bm['level']

        # Solo procesar bookmarks de nivel 0 (principales)
        if level > 0:
            continue

        if page is None:
            continue

        is_chapter = False
        chapter_num = None
        chapter_title = title

        for pattern in chapter_patterns:
            match = re.match(pattern, title, re.IGNORECASE)
            if match:
                is_chapter = True
                groups = match.groups()
                if groups and groups[0].isdigit():
                    chapter_num = int(groups[0])
                break

        # Bookmarks de nivel 0 son capítulos
        if level == 0:
            is_chapter = True

        if is_chapter:
            chapters.append({
                'title': chapter_title,
                'page': page,
                'number': chapter_num
            })

    # Ordenar por página
    chapters.sort(key=lambda x: x['page'])

    return chapters


def sanitize_filename(title: str, max_length: int = 50) -> str:
    """Convierte un título en un nombre de archivo válido."""
    # Remover caracteres no válidos
    clean = re.sub(r'[<>:"/\\|?*]', '', title)
    # Reemplazar espacios y guiones por underscore
    clean = re.sub(r'[\s\-—–]+', '_', clean)
    # Remover underscores múltiples
    clean = re.sub(r'_+', '_', clean)
    # Truncar si es muy largo
    if len(clean) > max_length:
        clean = clean[:max_length]
    # Remover underscore final
    clean = clean.rstrip('_')
    return clean


def clean_output_directory(output_dir: str):
    """
    Limpia los archivos generados anteriormente en el directorio de salida.
    Solo elimina archivos PDF y de índice generados por este script.
    """
    if not os.path.exists(output_dir):
        return

    patterns = ['*.pdf', '00_INDEX.*', '_00_INDEX.*', '00_index.*']
    deleted = 0

    for pattern in patterns:
        import glob
        for filepath in glob.glob(os.path.join(output_dir, pattern)):
            try:
                os.remove(filepath)
                deleted += 1
            except Exception as e:
                print(f"  Warning: Could not delete {filepath}: {e}")

    if deleted > 0:
        print(f"  Cleaned {deleted} old files from output directory")


def split_pdf_by_chapters(
    input_path: str,
    output_dir: str,
    chapters: List[Dict],
    total_pages: int,
    clean_first: bool = True
) -> List[str]:
    """
    Divide el PDF en archivos separados por capítulo.

    Args:
        input_path: Ruta al PDF original
        output_dir: Directorio de salida
        chapters: Lista de capítulos con {title, page, number}
        total_pages: Total de páginas del PDF
        clean_first: Si True, limpia archivos anteriores antes de crear nuevos

    Returns:
        Lista de archivos creados
    """
    created_files = []

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    # Limpiar archivos anteriores si se solicita
    if clean_first:
        clean_output_directory(output_dir)

    # Abrir el PDF original
    reader = PdfReader(input_path)

    # Encontrar el número máximo de capítulo y el mínimo
    max_chapter_num = 0
    min_chapter_num = float('inf')
    first_numbered_chapter_page = float('inf')

    for ch in chapters:
        if ch['number'] is not None:
            if ch['number'] > max_chapter_num:
                max_chapter_num = ch['number']
            if ch['number'] < min_chapter_num:
                min_chapter_num = ch['number']
                first_numbered_chapter_page = ch['page']

    # Contador para front matter (antes del capítulo 1)
    front_matter_counter = 0
    # Contador para apéndices (después del último capítulo numerado)
    appendix_counter = max_chapter_num + 1

    for i, chapter in enumerate(chapters):
        # Determinar rango de páginas
        start_page = chapter['page']

        if i < len(chapters) - 1:
            end_page = chapters[i + 1]['page'] - 1
        else:
            end_page = total_pages - 1

        # Saltar si no hay páginas
        if start_page > end_page:
            continue

        # Crear nombre de archivo con numeración apropiada
        title_lower = chapter['title'].lower()

        # El índice alfabético va al inicio como 00_
        if title_lower.startswith('index') or title_lower == 'índice':
            prefix = "00"
        elif chapter['number'] is not None:
            # Capítulo numerado explícitamente
            prefix = f"{chapter['number']:02d}"
        elif chapter['page'] < first_numbered_chapter_page:
            # Front matter (antes del primer capítulo numerado)
            front_matter_counter += 1
            prefix = f"00{chr(96 + front_matter_counter)}"  # 00a, 00b, 00c, etc.
        else:
            # Apéndices y otros (después de los capítulos numerados)
            prefix = f"{appendix_counter:02d}"
            appendix_counter += 1

        filename = f"{prefix}_{sanitize_filename(chapter['title'])}.pdf"
        output_path = os.path.join(output_dir, filename)

        # Crear PDF del capítulo
        writer = PdfWriter()

        for page_num in range(start_page, end_page + 1):
            if page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])

        # Guardar
        with open(output_path, 'wb') as f:
            writer.write(f)

        n_pages = end_page - start_page + 1
        print(f"  Created: {filename} ({n_pages} pages)")
        created_files.append(output_path)

    return created_files


def main():
    """Función principal."""
    # Rutas - detectar directorio base
    script_path = Path(__file__).resolve()

    # Buscar el directorio raíz del proyecto (donde está app/)
    project_root = script_path.parent.parent.parent.parent
    if not (project_root / "app").exists():
        # Alternativa: buscar hacia arriba
        project_root = script_path.parent
        while project_root.parent != project_root:
            if (project_root / "app").exists():
                break
            project_root = project_root.parent

    pdf_path = project_root / "app" / "structural" / "aci 318-25" / "ACI 318-25.pdf"
    output_dir = project_root / "app" / "structural" / "aci 318-25" / "chapters"

    print(f"Project root: {project_root}")
    print(f"Input PDF: {pdf_path}")
    print(f"Output dir: {output_dir}")
    print()

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        return

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    # Abrir PDF y extraer bookmarks
    print("Opening PDF and extracting bookmarks...")
    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    print(f"  Total pages: {total_pages}")

    # Extraer bookmarks
    bookmarks = extract_bookmarks(reader)
    print(f"  Found {len(bookmarks)} bookmarks")

    if not bookmarks:
        print("\nNo bookmarks found. Using fallback (split every 50 pages)...")
        chapters = []
        for i in range(0, total_pages, 50):
            chapters.append({
                'title': f'Pages_{i+1}_to_{min(i+50, total_pages)}',
                'page': i,
                'number': i // 50
            })
    else:
        # Mostrar bookmarks encontrados
        print("\nBookmarks found (first 30):")
        for bm in bookmarks[:30]:
            indent = "  " * bm['level']
            page_str = f"p.{bm['page']+1}" if bm['page'] is not None else "no page"
            print(f"  {indent}{bm['title'][:55]:<55} [{page_str}]")

        if len(bookmarks) > 30:
            print(f"  ... and {len(bookmarks) - 30} more")

        # Identificar capítulos
        print("\nIdentifying main chapters...")
        chapters = identify_chapters(bookmarks)

    print(f"\nFound {len(chapters)} chapters to extract:")
    for ch in chapters[:20]:
        num_str = f"Ch.{ch['number']}" if ch['number'] else "---"
        print(f"  {num_str:>6} | p.{ch['page']+1:>4} | {ch['title'][:50]}")
    if len(chapters) > 20:
        print(f"  ... and {len(chapters) - 20} more")

    # Dividir PDF (sobreescribe archivos con el mismo nombre)
    print(f"\nSplitting PDF into {len(chapters)} files...")
    created = split_pdf_by_chapters(
        str(pdf_path),
        str(output_dir),
        chapters,
        total_pages,
        clean_first=False  # No borrar archivos existentes
    )

    print(f"\n{'='*60}")
    print(f"Done! Created {len(created)} PDF files.")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
