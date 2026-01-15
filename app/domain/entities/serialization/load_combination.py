# app/domain/entities/serialization/load_combination.py
"""
Helper centralizado para parsing de LoadCombination desde Excel.

Evita duplicación del mismo código en 4 parsers diferentes.
"""
from typing import Dict, Any

from ..load_combination import LoadCombination


def parse_load_combination(row: Dict[str, Any], location: str = 'Bottom') -> LoadCombination:
    """
    Parsea una fila de Excel a LoadCombination.

    Usado por: pier_parser, column_parser, beam_parser, drop_beam_parser.

    Args:
        row: Diccionario con claves lowercase del Excel
        location: 'Top' o 'Bottom' (default 'Bottom')

    Returns:
        LoadCombination con los valores parseados

    Campos esperados en row (case-insensitive, ya normalizado):
        - output case: nombre de la combinación
        - step type: '' o 'Max' o 'Min'
        - p: carga axial (tonf)
        - v2: corte dirección 2 (tonf)
        - v3: corte dirección 3 (tonf)
        - t: torsión (tonf-m)
        - m2: momento dirección 2 (tonf-m)
        - m3: momento dirección 3 (tonf-m)
    """
    return LoadCombination(
        name=str(row.get('output case', '')),
        location=location,
        step_type=str(row.get('step type', '')),
        P=float(row.get('p', 0)),
        V2=float(row.get('v2', 0)),
        V3=float(row.get('v3', 0)),
        T=float(row.get('t', 0)),
        M2=float(row.get('m2', 0)),
        M3=float(row.get('m3', 0)),
    )
