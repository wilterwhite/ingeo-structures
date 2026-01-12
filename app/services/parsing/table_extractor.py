# app/structural/services/parsing/table_extractor.py
"""
Extracción de tablas desde archivos Excel de ETABS.

ETABS exporta múltiples tablas en una sola hoja de Excel, cada una
marcada con "TABLE: NombreTabla". Este módulo contiene la lógica
para encontrar y extraer tablas específicas.

Las tablas de ETABS tienen esta estructura:
- Fila 0: "TABLE: NombreTabla"
- Fila 1: Headers (nombres de columnas)
- Fila 2: Unidades (mm, m, tonf, etc.)
- Fila 3+: Datos
"""
from typing import Optional, List, Dict, Tuple
import pandas as pd


# =============================================================================
# Factores de Conversión de Unidades a mm
# =============================================================================

UNIT_FACTORS_TO_MM: Dict[str, float] = {
    'mm': 1.0,
    'm': 1000.0,
    'cm': 10.0,
    'in': 25.4,
    'ft': 304.8,
}


def get_unit_factor(unit_str) -> float:
    """
    Retorna el factor para convertir una unidad de longitud a mm.

    Args:
        unit_str: String con la unidad (ej: 'mm', 'm', 'cm')

    Returns:
        Factor de conversión a mm. Si la unidad no es reconocida, retorna 1.0
    """
    if unit_str is None or pd.isna(unit_str):
        return 1.0
    unit = str(unit_str).lower().strip()
    return UNIT_FACTORS_TO_MM.get(unit, 1.0)


def extract_units_from_df(df: pd.DataFrame) -> Dict[str, float]:
    """
    Extrae los factores de conversión de unidades de un DataFrame de ETABS.

    ETABS pone las unidades en la primera fila de datos (después de headers).
    Esta función lee esa fila y retorna un dict con los factores de conversión.

    Args:
        df: DataFrame ya normalizado con headers

    Returns:
        Dict[column_name -> factor_to_mm]
        Ejemplo: {'width bottom': 1.0, 'cg bottom z': 1000.0}
    """
    units = {}
    if df is None or len(df) == 0:
        return units

    # La primera fila del DataFrame normalizado debería tener las unidades
    # (porque find_table_in_sheet ya extrajo headers)
    first_row = df.iloc[0]
    for col in df.columns:
        unit_value = first_row.get(col)
        units[str(col).lower()] = get_unit_factor(unit_value)

    return units


# =============================================================================
# Columnas Esperadas por Tipo de Tabla
# =============================================================================

PIER_SECTION_COLUMNS = [
    'story', 'pier', 'width bottom', 'thickness bottom',
    'width top', 'thickness top', 'material',
    'cg bottom z', 'cg top z'
]

PIER_FORCES_COLUMNS = [
    'story', 'pier', 'output case', 'case type',
    'step type', 'location', 'p', 'v2', 'v3', 't', 'm2', 'm3'
]

WALL_PROPERTY_COLUMNS = [
    'name', 'material', 'wall thickness'
]


# =============================================================================
# Funciones de Extracción
# =============================================================================

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza los nombres de columnas a minúsculas.

    Args:
        df: DataFrame con columnas a normalizar

    Returns:
        DataFrame con columnas en minúsculas
    """
    df = df.copy()
    df.columns = [str(col).lower().strip() for col in df.columns]
    return df


def find_table_in_sheet(
    df: pd.DataFrame,
    table_marker: str
) -> Optional[pd.DataFrame]:
    """
    Busca una tabla específica dentro de una hoja de Excel.

    ETABS pone múltiples tablas en una sola hoja, cada una marcada
    con "TABLE: nombre". Esta función encuentra la tabla y extrae
    solo sus datos.

    Args:
        df: DataFrame de la hoja completa (leída sin header)
        table_marker: Texto que identifica la tabla (ej: "Pier Section Properties")

    Returns:
        DataFrame con los datos de esa tabla, o None si no se encuentra

    Example:
        >>> df = pd.read_excel('etabs.xlsx', sheet_name='Sheet1', header=None)
        >>> pier_props = find_table_in_sheet(df, "Pier Section Properties")
    """
    # Buscar la fila que contiene el marcador de tabla
    start_row = None
    end_row = len(df)

    for i, row in df.iterrows():
        row_str = ' '.join([str(v) for v in row.values if pd.notna(v)])
        if table_marker.lower() in row_str.lower():
            start_row = i + 1  # La siguiente fila son los headers
            break

    if start_row is None:
        return None

    # Buscar el fin de la tabla (siguiente "TABLE:" o fin del archivo)
    for i in range(start_row + 1, len(df)):
        row_str = ' '.join([str(v) for v in df.iloc[i].values if pd.notna(v)])
        if 'table:' in row_str.lower():
            end_row = i
            break

    # Extraer subtabla
    sub_df = df.iloc[start_row:end_row].copy()

    # La primera fila son los headers
    if len(sub_df) > 0:
        sub_df.columns = sub_df.iloc[0]
        sub_df = sub_df.iloc[1:]  # Remover fila de headers

    # Eliminar filas vacías
    sub_df = sub_df.dropna(how='all')

    return sub_df if len(sub_df) > 0 else None


def find_table_by_sheet_name(
    excel_file: pd.ExcelFile,
    keywords: List[str]
) -> Optional[pd.DataFrame]:
    """
    Busca una tabla por nombre de hoja que contenga ciertas palabras clave.

    Args:
        excel_file: Archivo Excel abierto con pd.ExcelFile
        keywords: Lista de palabras que debe contener el nombre de la hoja

    Returns:
        DataFrame de la hoja encontrada, o None

    Example:
        >>> excel = pd.ExcelFile('etabs.xlsx')
        >>> forces = find_table_by_sheet_name(excel, ['pier', 'force'])
    """
    for sheet_name in excel_file.sheet_names:
        sheet_lower = sheet_name.lower()
        if all(kw in sheet_lower for kw in keywords):
            return pd.read_excel(excel_file, sheet_name=sheet_name)
    return None


def has_required_columns(df: pd.DataFrame, required: List[str]) -> bool:
    """
    Verifica si un DataFrame tiene las columnas requeridas.

    Args:
        df: DataFrame a verificar
        required: Lista de nombres de columnas requeridas (en minúsculas)

    Returns:
        True si tiene todas las columnas requeridas
    """
    if df is None:
        return False

    df_normalized = normalize_columns(df)
    return all(col in df_normalized.columns for col in required)
