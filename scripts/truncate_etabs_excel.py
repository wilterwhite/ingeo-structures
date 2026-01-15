#!/usr/bin/env python3
"""
Trunca un archivo Excel de ETABS manteniendo solo una muestra de elementos.

Uso:
    python scripts/truncate_etabs_excel.py input.xlsx output.xlsx [--piers N] [--cols N] [--beams N]

Por defecto:
    - 10 piers
    - 5 columnas por story
    - 5 vigas por story
    - 3 spandrels
    - 50 section cuts

El script mantiene la consistencia entre hojas:
    - Pier Section Properties ↔ Pier Forces
    - Frame Assigns ↔ Element Forces (Columns/Beams)
    - Frame Sec Def (solo secciones usadas)
"""

import argparse
import pandas as pd
from pathlib import Path


def filter_data(df: pd.DataFrame, filter_col_idx: int, values_to_keep: set, header_rows: int = 3) -> pd.DataFrame:
    """
    Filtra filas de un DataFrame manteniendo los headers.

    Args:
        df: DataFrame raw (sin header)
        filter_col_idx: índice de columna para filtrar
        values_to_keep: valores a mantener en esa columna
        header_rows: número de filas de header a mantener siempre

    Returns:
        DataFrame filtrado con headers
    """
    header = df.iloc[:header_rows]
    data = df.iloc[header_rows:]
    filtered = data[data.iloc[:, filter_col_idx].isin(values_to_keep)]
    return pd.concat([header, filtered], ignore_index=True)


def truncate_excel(input_path: str, output_path: str,
                   n_piers: int = 10,
                   n_cols_per_story: int = 5,
                   n_beams_per_story: int = 5,
                   n_spandrels: int = 3,
                   n_section_cuts: int = 50) -> dict:
    """
    Trunca un archivo Excel de ETABS.

    Args:
        input_path: Ruta al archivo Excel original
        output_path: Ruta al archivo Excel de salida
        n_piers: Número de piers a mantener
        n_cols_per_story: Número de columnas por story
        n_beams_per_story: Número de vigas por story
        n_spandrels: Número de spandrels a mantener
        n_section_cuts: Número de section cuts a mantener

    Returns:
        Diccionario con estadísticas del truncado
    """
    xlsx = pd.ExcelFile(input_path)

    # Cargar todas las hojas sin headers
    sheets_raw = {}
    for sheet in xlsx.sheet_names:
        sheets_raw[sheet] = pd.read_excel(xlsx, sheet_name=sheet, header=None)

    stats = {'original': {}, 'truncated': {}}

    # === PIERS ===
    pier_props = sheets_raw['Pier Section Properties']
    stats['original']['piers'] = len(pier_props) - 3
    pier_labels = pier_props.iloc[3:, 1].dropna().unique()[:n_piers]

    pier_props_filtered = filter_data(pier_props, 1, set(pier_labels))
    pier_forces_filtered = filter_data(sheets_raw['Pier Forces'], 1, set(pier_labels))
    stats['truncated']['piers'] = len(pier_props_filtered) - 3

    # === COLUMNAS ===
    col_forces = sheets_raw['Element Forces - Columns']
    stats['original']['columns'] = len(col_forces) - 3
    cols_to_keep = set()
    data_rows = col_forces.iloc[3:]
    for story in data_rows.iloc[:, 0].dropna().unique():
        story_data = data_rows[data_rows.iloc[:, 0] == story]
        story_cols = story_data.iloc[:, 1].unique()[:n_cols_per_story]
        cols_to_keep.update(story_cols)

    col_forces_filtered = filter_data(col_forces, 1, cols_to_keep)
    stats['truncated']['columns'] = len(col_forces_filtered) - 3

    # === VIGAS ===
    beam_forces = sheets_raw['Element Forces - Beams']
    stats['original']['beams'] = len(beam_forces) - 3
    beams_to_keep = set()
    data_rows = beam_forces.iloc[3:]
    for story in data_rows.iloc[:, 0].dropna().unique():
        story_data = data_rows[data_rows.iloc[:, 0] == story]
        story_beams = story_data.iloc[:, 1].unique()[:n_beams_per_story]
        beams_to_keep.update(story_beams)

    beam_forces_filtered = filter_data(beam_forces, 1, beams_to_keep)
    stats['truncated']['beams'] = len(beam_forces_filtered) - 3

    # === FRAME ASSIGNS ===
    all_frame_labels = cols_to_keep | beams_to_keep
    frame_assigns_filtered = filter_data(
        sheets_raw['Frame Assigns - Sect Prop'], 1, all_frame_labels
    )

    # === FRAME SEC DEF ===
    used_sections = set(frame_assigns_filtered.iloc[3:, 5].dropna().unique())
    frame_sec_filtered = filter_data(
        sheets_raw['Frame Sec Def - Conc Rect'], 0, used_sections
    )

    # === SPANDRELS ===
    spandrel_props = sheets_raw['Spandrel Section Properties']
    spandrel_labels = spandrel_props.iloc[3:, 1].dropna().unique()[:n_spandrels]
    spandrel_props_filtered = filter_data(spandrel_props, 1, set(spandrel_labels))
    spandrel_forces_filtered = filter_data(
        sheets_raw['Spandrel Forces'], 1, set(spandrel_labels)
    )

    # === SECTION CUTS ===
    section_cuts = sheets_raw['Section Cut Forces - Analysis']
    section_cuts_filtered = section_cuts.head(3 + n_section_cuts)

    # === GUARDAR ===
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        sheets_raw['Program Control'].to_excel(
            writer, sheet_name='Program Control', index=False, header=False
        )
        sheets_raw['Wall Property Def - Specified'].to_excel(
            writer, sheet_name='Wall Property Def - Specified', index=False, header=False
        )
        spandrel_props_filtered.to_excel(
            writer, sheet_name='Spandrel Section Properties', index=False, header=False
        )
        spandrel_forces_filtered.to_excel(
            writer, sheet_name='Spandrel Forces', index=False, header=False
        )
        section_cuts_filtered.to_excel(
            writer, sheet_name='Section Cut Forces - Analysis', index=False, header=False
        )
        pier_props_filtered.to_excel(
            writer, sheet_name='Pier Section Properties', index=False, header=False
        )
        pier_forces_filtered.to_excel(
            writer, sheet_name='Pier Forces', index=False, header=False
        )
        frame_sec_filtered.to_excel(
            writer, sheet_name='Frame Sec Def - Conc Rect', index=False, header=False
        )
        frame_assigns_filtered.to_excel(
            writer, sheet_name='Frame Assigns - Sect Prop', index=False, header=False
        )
        col_forces_filtered.to_excel(
            writer, sheet_name='Element Forces - Columns', index=False, header=False
        )
        beam_forces_filtered.to_excel(
            writer, sheet_name='Element Forces - Beams', index=False, header=False
        )

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Trunca un archivo Excel de ETABS manteniendo una muestra de elementos.'
    )
    parser.add_argument('input', help='Archivo Excel de entrada')
    parser.add_argument('output', help='Archivo Excel de salida')
    parser.add_argument('--piers', type=int, default=10, help='Número de piers (default: 10)')
    parser.add_argument('--cols', type=int, default=5, help='Columnas por story (default: 5)')
    parser.add_argument('--beams', type=int, default=5, help='Vigas por story (default: 5)')
    parser.add_argument('--spandrels', type=int, default=3, help='Spandrels (default: 3)')
    parser.add_argument('--cuts', type=int, default=50, help='Section cuts (default: 50)')

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: No se encuentra el archivo {args.input}")
        return 1

    print(f"Truncando {args.input} -> {args.output}")
    print(f"  Piers: {args.piers}")
    print(f"  Columnas por story: {args.cols}")
    print(f"  Vigas por story: {args.beams}")
    print(f"  Spandrels: {args.spandrels}")
    print(f"  Section cuts: {args.cuts}")
    print()

    stats = truncate_excel(
        args.input, args.output,
        n_piers=args.piers,
        n_cols_per_story=args.cols,
        n_beams_per_story=args.beams,
        n_spandrels=args.spandrels,
        n_section_cuts=args.cuts
    )

    print("=== Resultado ===")
    print(f"Piers: {stats['original']['piers']} -> {stats['truncated']['piers']}")
    print(f"Columns (filas): {stats['original']['columns']} -> {stats['truncated']['columns']}")
    print(f"Beams (filas): {stats['original']['beams']} -> {stats['truncated']['beams']}")
    print()
    print(f"Archivo creado: {args.output}")

    return 0


if __name__ == '__main__':
    exit(main())
