#!/usr/bin/env python3
"""
Script para generar Section Cuts en ETABS desde grupos.

Lee un archivo .e2k, identifica todos los grupos definidos,
y genera automáticamente los Section Cuts correspondientes.

Uso:
    python scripts/e2k_section_cuts_generator.py input.e2k [-o output.e2k]
"""
import re
import argparse
from pathlib import Path


def extract_groups(lines: list[str]) -> list[str]:
    """Extrae nombres únicos de TODOS los grupos definidos."""
    # Patrón: línea de definición de grupo (sin POINT ni AREA)
    pattern = r'^\s*GROUP\s+"([^"]+)"\s*$'
    groups = set()
    for line in lines:
        match = re.match(pattern, line)
        if match:
            groups.add(match.group(1))
    return sorted(groups)


def extract_existing_section_cuts(lines: list[str]) -> set[str]:
    """Extrae nombres de section cuts existentes."""
    pattern = r'SECTIONCUT\s+"([^"]+)"'
    existing = set()
    for line in lines:
        match = re.search(pattern, line)
        if match:
            existing.add(match.group(1))
    return existing


def generate_section_cut_line(group_name: str) -> str:
    """Genera una línea SECTIONCUT para un grupo."""
    scut_name = f"SCut-{group_name}"
    return f'  SECTIONCUT "{scut_name}"  DEFINEDBY "Group"  GROUP "{group_name}"  CUTFOR "Analysis"  ROTABOUTZ 0 ROTABOUTYY 0 ROTABOUTXXX 0'


def insert_section_cuts(lines: list[str], new_scuts: list[str]) -> list[str]:
    """
    Inserta section cuts en el archivo.

    Si existe '$ SECTION CUTS', inserta después del header.
    Si NO existe, crea la sección antes de '$ DIMENSION LINES'.
    """
    output = []
    section_cuts_found = False

    for line in lines:
        # Caso 1: La sección existe
        if line.strip() == '$ SECTION CUTS':
            section_cuts_found = True
            output.append(line)
            for scut in new_scuts:
                output.append(scut)
            continue

        # Caso 2: La sección NO existe, crearla antes de DIMENSION LINES
        if not section_cuts_found and line.strip() == '$ DIMENSION LINES':
            output.append('')
            output.append('$ SECTION CUTS')
            for scut in new_scuts:
                output.append(scut)
            output.append('')

        output.append(line)

    return output


def generate_section_cuts(input_file: str, output_file: str = None) -> int:
    """
    Lee archivo e2k, genera section cuts para todos los grupos.

    Args:
        input_file: Ruta al archivo .e2k original
        output_file: Ruta de salida (opcional, default: input_with_scuts.e2k)

    Returns:
        Número de section cuts generados
    """
    input_path = Path(input_file)

    if output_file is None:
        output_file = input_path.parent / (input_path.stem + "_with_scuts" + input_path.suffix)
    else:
        output_file = Path(output_file)

    # Leer archivo (detectar encoding)
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_path, 'r', encoding='latin-1') as f:
            content = f.read()

    lines = content.splitlines()

    # Extraer grupos y section cuts existentes
    groups = extract_groups(lines)
    existing_scuts = extract_existing_section_cuts(lines)

    print(f"Grupos encontrados: {len(groups)}")
    print(f"Section cuts existentes: {len(existing_scuts)}")

    # Generar nuevos section cuts
    new_scuts = []
    for group_name in groups:
        scut_name = f"SCut-{group_name}"
        if scut_name not in existing_scuts:
            new_scuts.append(generate_section_cut_line(group_name))

    if not new_scuts:
        print("No hay nuevos section cuts para generar.")
        return 0

    # Insertar en el archivo
    output_lines = insert_section_cuts(lines, new_scuts)

    # Escribir archivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"Generados {len(new_scuts)} section cuts")
    print(f"Archivo guardado en: {output_file}")

    return len(new_scuts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genera Section Cuts en ETABS desde grupos"
    )
    parser.add_argument("input", help="Archivo e2k de entrada")
    parser.add_argument(
        "-o", "--output",
        help="Archivo de salida (default: input_with_scuts.e2k)"
    )
    args = parser.parse_args()

    generate_section_cuts(args.input, args.output)
