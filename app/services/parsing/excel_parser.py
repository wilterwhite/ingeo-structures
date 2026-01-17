# app/services/parsing/excel_parser.py
"""
Parser de archivos Excel exportados de ETABS.

Orquesta la lectura de las tablas de ETABS usando los modulos:
- material_mapper: Conversion de nombres de materiales a f'c
- table_extractor: Busqueda de tablas dentro de hojas Excel
- column_parser: Parser de columnas
- beam_parser: Parser de vigas (frame y spandrels)

Tablas soportadas:
- Piers: Wall Property Definitions, Pier Section Properties, Pier Forces
- Columnas: Frame Section Property Definitions - Concrete Rectangular, Element Forces - Columns
- Vigas: Frame Section Property Definitions - Concrete Rectangular, Element Forces - Beams
- Spandrels: Spandrel Section Properties, Spandrel Forces
"""
import logging
import time
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

logger = logging.getLogger(__name__)
_perf_logger = logging.getLogger('perf')

from ...domain.entities import (
    VerticalElement,
    VerticalElementSource,
    ElementForces,
    ElementForceType,
    ParsedData,
)
from ...domain.entities.element_forces import COMBO_COLUMNS
from ...domain.constants.reinforcement import FY_DEFAULT_MPA
from .material_mapper import parse_material_to_fc
from .table_extractor import (
    normalize_columns,
    extract_units_from_df,
    extract_tables_fast,
    TABLE_NAME_MAPPINGS,
)
from .column_parser import ColumnParser
from .beam_parser import BeamParser
from .drop_beam_parser import DropBeamParser
from .composite_pier_parser import CompositePierParser
from ..logging import claude_logger


# Nombres de tablas soportadas (para mostrar al usuario en UI)
SUPPORTED_TABLES = {
    'piers': [
        'Wall Property Definitions',
        'Pier Section Properties',
        'Pier Forces'
    ],
    'piers_composite': [
        'Wall Object Connectivity',
        'Point Object Connectivity',
        'Area Assigns - Pier Labels'
    ],
    'columns': [
        'Frame Section Property Definitions - Concrete Rectangular',
        'Element Forces - Columns'
    ],
    'beams': [
        'Frame Section Property Definitions - Concrete Rectangular',
        'Frame Section Property Definitions - Concrete Circle',
        'Element Forces - Beams',
        'Spandrel Section Properties',
        'Spandrel Forces'
    ],
    'drop_beams': [
        'Section Cut Forces - Analysis'
    ]
}

# Claves internas de tablas (derivadas del mapeo en table_extractor)
TABLE_KEYS = {key for _, key in TABLE_NAME_MAPPINGS}


# =============================================================================
# Parser Principal
# =============================================================================

class EtabsExcelParser:
    """
    Parser para archivos Excel de ETABS.

    Detecta automaticamente las tablas presentes y parsea:
    - Piers: Wall Property Definitions, Pier Section Properties, Pier Forces
    - Columnas: Frame Sec Def - Conc Rect, Element Forces - Columns
    - Vigas: Frame Sec Def - Conc Rect, Element Forces - Beams, Spandrels
    """

    def __init__(self):
        self.column_parser = ColumnParser()
        self.beam_parser = BeamParser()
        self.drop_beam_parser = DropBeamParser()
        self.composite_pier_parser = CompositePierParser()

    # =========================================================================
    # FASE 1: Extraccion de Tablas (sin procesar elementos)
    # =========================================================================

    def extract_tables_only(self, file_content: bytes) -> Dict[str, pd.DataFrame]:
        """
        Extrae las tablas de un archivo Excel SIN procesar elementos.

        Usado para el flujo de acumulacion multi-archivo:
        1. Se llama extract_tables_only() para cada archivo
        2. Se acumulan las tablas
        3. Se llama parse_from_tables() con tablas fusionadas

        Args:
            file_content: Contenido binario del archivo Excel

        Returns:
            Dict con tablas encontradas: {
                'pier_props': DataFrame,
                'frame_section': DataFrame,
                ...
            }
        """
        # Usar openpyxl read_only mode (mucho mas rapido)
        tables = extract_tables_fast(file_content)

        # Log de tablas encontradas y faltantes
        missing_tables = [k for k in TABLE_KEYS if k not in tables]

        # Log para Claude
        for table_name, df in tables.items():
            claude_logger.log_table_found(table_name, len(df))
        for missing in missing_tables:
            claude_logger.log_table_missing(missing)

        return tables

    # =========================================================================
    # FASE 2: Procesamiento desde Tablas Fusionadas
    # =========================================================================

    def parse_from_tables(self, tables: Dict[str, pd.DataFrame]) -> ParsedData:
        """
        Procesa elementos desde tablas ya fusionadas.

        Args:
            tables: Dict con tablas fusionadas de multiples archivos

        Returns:
            ParsedData con elementos parseados
        """
        t0 = time.perf_counter()

        # Extraer tablas del dict
        wall_props_df = tables.get('wall_props')
        pier_props_df = tables.get('pier_props')
        pier_forces_df = tables.get('pier_forces')
        frame_section_df = tables.get('frame_section')
        frame_circular_df = tables.get('frame_circular')
        frame_assigns_df = tables.get('frame_assigns')
        column_forces_df = tables.get('column_forces')
        beam_forces_df = tables.get('beam_forces')
        spandrel_props_df = tables.get('spandrel_props')
        spandrel_forces_df = tables.get('spandrel_forces')
        section_cut_df = tables.get('section_cut')
        walls_connectivity_df = tables.get('walls_connectivity')
        points_connectivity_df = tables.get('points_connectivity')
        pier_assigns_df = tables.get('pier_assigns')

        # Procesar materiales
        t1 = time.perf_counter()
        materials: Dict[str, float] = {}
        if wall_props_df is not None:
            materials = self._parse_materials(wall_props_df)
        if frame_section_df is not None:
            frame_materials = self._parse_frame_materials(frame_section_df)
            materials.update(frame_materials)
        _perf_logger.info(f"[PERF] parse_materials: {time.perf_counter()-t1:.2f}s")

        # Procesar piers
        t1 = time.perf_counter()
        piers, pier_stories = self._parse_piers(pier_props_df, materials)
        _perf_logger.info(f"[PERF] parse_piers: {time.perf_counter()-t1:.2f}s ({len(piers)} piers)")

        t1 = time.perf_counter()
        pier_forces = self._parse_forces(pier_forces_df)
        _perf_logger.info(f"[PERF] parse_pier_forces: {time.perf_counter()-t1:.2f}s ({len(pier_forces)} forces)")

        # Geometria compuesta de piers (L, T, C)
        t1 = time.perf_counter()
        if walls_connectivity_df is not None and points_connectivity_df is not None:
            # Extraer espesores de piers para usar como fallback
            # (ETABS no incluye espesor en Area/Perimeter de Wall Object Connectivity)
            pier_thicknesses: Dict[str, float] = {}
            for key, pier in piers.items():
                pier_thicknesses[key] = pier.thickness  # Ya está en mm desde _parse_piers
            composite_sections = self.composite_pier_parser.parse_composite_piers(
                walls_connectivity_df, points_connectivity_df, pier_assigns_df,
                pier_thicknesses=pier_thicknesses
            )
            for key, pier in piers.items():
                if key in composite_sections:
                    pier.composite_section = composite_sections[key]
        _perf_logger.info(f"[PERF] parse_composite: {time.perf_counter()-t1:.2f}s")

        # OPTIMIZADO: Procesar columnas y vigas EN PARALELO
        t1 = time.perf_counter()
        columns = {}
        column_forces = {}
        column_stories = []
        beams = {}
        beam_forces = {}
        beam_stories = []

        def parse_columns_task():
            if column_forces_df is not None:
                return self.column_parser.parse_columns(
                    frame_section_df, frame_assigns_df, column_forces_df, materials
                )
            return {}, {}, []

        def parse_beams_task():
            if beam_forces_df is not None or spandrel_forces_df is not None:
                return self.beam_parser.parse_beams(
                    frame_section_df, frame_assigns_df, beam_forces_df,
                    spandrel_props_df, spandrel_forces_df,
                    materials, frame_circular_df
                )
            return {}, {}, []

        # Ejecutar ambos parsers en paralelo
        with ThreadPoolExecutor(max_workers=2) as executor:
            col_future = executor.submit(parse_columns_task)
            beam_future = executor.submit(parse_beams_task)

            columns, column_forces, column_stories = col_future.result()
            beams, beam_forces, beam_stories = beam_future.result()

        _perf_logger.info(f"[PERF] parse_columns+beams (parallel): {time.perf_counter()-t1:.2f}s ({len(columns)} columns, {len(beams)} beams)")

        # Procesar vigas capitel (Section Cut Forces)
        t1 = time.perf_counter()
        drop_beams = {}
        drop_beam_forces = {}
        drop_beam_stories = []
        if section_cut_df is not None:
            drop_beams, drop_beam_forces, drop_beam_stories = self.drop_beam_parser.parse_drop_beams(
                section_cut_df, materials
            )
        _perf_logger.info(f"[PERF] parse_drop_beams: {time.perf_counter()-t1:.2f}s ({len(drop_beams)} drop_beams)")

        # Combinar stories sin duplicados
        all_stories = pier_stories.copy()
        for s in column_stories + beam_stories + drop_beam_stories:
            if s not in all_stories:
                all_stories.append(s)

        # Combinar elementos
        vertical_elements = {**piers, **columns}
        horizontal_elements = {**beams, **drop_beams}
        vertical_forces = {**pier_forces, **column_forces}
        horizontal_forces = {**beam_forces, **drop_beam_forces}

        _perf_logger.info(f"[PERF] parse_from_tables TOTAL: {time.perf_counter()-t0:.2f}s")

        return ParsedData(
            vertical_elements=vertical_elements,
            horizontal_elements=horizontal_elements,
            vertical_forces=vertical_forces,
            horizontal_forces=horizontal_forces,
            materials=materials,
            stories=all_stories,
            raw_tables=tables,
        )

    # =========================================================================
    # Metodos de Parsing Internos
    # =========================================================================

    def _parse_materials(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Extrae el mapeo de nombres de materiales a f'c desde Wall Property Definitions.

        OPTIMIZADO: Usa operaciones vectorizadas.
        """
        materials = {}
        df = normalize_columns(df)

        # Filtrar filas con name válido
        df = df[df['name'].notna() & (df['name'].astype(str) != 'nan') & (df['name'].astype(str) != '')]

        if len(df) == 0:
            return materials

        # OPTIMIZADO: Usar to_dict('records') en lugar de iterrows
        df['_material'] = df.get('material', df['name']).astype(str)
        records = df[['name', '_material']].to_dict('records')

        for r in records:
            name = str(r.get('name', ''))
            material = r['_material']
            if name:
                fc = parse_material_to_fc(material)
                materials[name] = fc
                materials[material] = fc

        return materials

    def _parse_frame_materials(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Extrae materiales desde Frame Section Definitions.

        OPTIMIZADO: Usa operaciones vectorizadas.
        """
        materials = {}

        if df is None:
            return materials

        df = normalize_columns(df)

        # Filtrar materiales válidos
        if 'material' not in df.columns:
            return materials

        df = df[df['material'].notna() & (df['material'].astype(str) != 'nan') & (df['material'].astype(str) != '')]

        if len(df) == 0:
            return materials

        # Obtener materiales únicos (más eficiente)
        unique_materials = df['material'].astype(str).unique()
        for material in unique_materials:
            fc = parse_material_to_fc(material)
            materials[material] = fc

        return materials

    def _parse_piers(
        self,
        df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> tuple[Dict[str, VerticalElement], List[str]]:
        """
        Extrae los piers con su geometria como VerticalElement.

        OPTIMIZADO: Usa operaciones vectorizadas para filtrado y conversión.
        """
        piers: Dict[str, VerticalElement] = {}
        stories: List[str] = []

        if df is None:
            logger.info("Piers: No se encontro tabla Pier Section Properties")
            return piers, stories

        df = normalize_columns(df)

        # Extraer factores de conversion de unidades de la primera fila
        units = extract_units_from_df(df)
        logger.info(f"Piers: Unidades detectadas - width: {units.get('width bottom', 1.0)}, cg: {units.get('cg bottom z', 1.0)}")

        # Saltar la fila de unidades
        df = df.iloc[1:].copy()
        total_rows = len(df)

        # Filtrar filas válidas (vectorizado)
        df = df[df['pier'].notna() & (df['pier'].astype(str) != 'nan')]
        skipped_empty = total_rows - len(df)

        if len(df) == 0:
            logger.info(f"Piers: 0 importados OK, 0 con geometria invalida, {skipped_empty} filas vacias")
            return piers, stories

        # Convertir columnas numéricas de una vez (vectorizado)
        numeric_cols = ['width bottom', 'width top', 'thickness bottom', 'thickness top',
                        'cg bottom z', 'cg top z', 'axisangle', 'axis angle']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Calcular geometría vectorizada
        width_factor = units.get('width bottom', 1.0)
        thickness_factor = units.get('thickness bottom', 1.0)
        cg_factor = units.get('cg bottom z', 1.0)

        df['_width'] = ((df.get('width bottom', 0) + df.get('width top', df.get('width bottom', 0))) / 2) * width_factor
        df['_thickness'] = ((df.get('thickness bottom', 0) + df.get('thickness top', df.get('thickness bottom', 0))) / 2) * thickness_factor
        df['_cg_bottom'] = df.get('cg bottom z', 0) * cg_factor
        df['_cg_top'] = df.get('cg top z', df['_cg_bottom'] + 3000) * units.get('cg top z', 1.0)
        df['_height'] = df['_cg_top'] - df['_cg_bottom']

        # Filtrar geometría válida
        valid_geom = (df['_width'] > 0) & (df['_thickness'] > 0) & (df['_height'] > 0)
        skipped_invalid_geometry = (~valid_geom).sum()
        df = df[valid_geom]

        if len(df) == 0:
            logger.info(f"Piers: 0 importados OK, {skipped_invalid_geometry} con geometria invalida, {skipped_empty} filas vacias")
            return piers, stories

        # OPTIMIZADO: Usar to_dict('records') en lugar de iterrows
        df['_material'] = df.get('material', pd.Series(['4000Psi'] * len(df))).astype(str).fillna('4000Psi')
        if 'axisangle' in df.columns:
            df['_angle'] = pd.to_numeric(df['axisangle'], errors='coerce').fillna(0)
        elif 'axis angle' in df.columns:
            df['_angle'] = pd.to_numeric(df['axis angle'], errors='coerce').fillna(0)
        else:
            df['_angle'] = 0

        records = df[['story', 'pier', '_material', '_angle', '_width', '_thickness', '_height']].to_dict('records')

        for r in records:
            story = str(r.get('story', ''))
            pier_label = str(r.get('pier', ''))

            # Material -> f'c
            material_name = r['_material']
            fc = materials.get(material_name, parse_material_to_fc(material_name))

            # Crear VerticalElement con source=PIER
            pier_key = f"{story}_{pier_label}"
            piers[pier_key] = VerticalElement(
                label=pier_label,
                story=story,
                length=float(r['_width']),
                thickness=float(r['_thickness']),
                height=float(r['_height']),
                fc=fc,
                fy=FY_DEFAULT_MPA,
                source=VerticalElementSource.PIER,
                axis_angle=float(r['_angle']),
            )

            if story not in stories:
                stories.append(story)

        # Log resumen
        logger.info(
            f"Piers: {len(piers)} importados OK, "
            f"{skipped_invalid_geometry} con geometria invalida, "
            f"{skipped_empty} filas vacias (de {total_rows} filas)"
        )

        return piers, stories

    def _parse_forces(self, df: pd.DataFrame) -> Dict[str, ElementForces]:
        """
        Extrae las fuerzas por combinacion de carga.

        OPTIMIZADO: Usa operaciones vectorizadas y groupby() para procesar
        tablas grandes eficientemente.
        """
        pier_forces: Dict[str, ElementForces] = {}

        if df is None or len(df) == 0:
            return pier_forces

        df = normalize_columns(df)

        # Filtrar filas válidas (vectorizado)
        df = df[df['pier'].notna() & (df['pier'].astype(str) != 'nan')].copy()

        if len(df) == 0:
            return pier_forces

        # Crear pier_key vectorizado
        df['_key'] = df['story'].astype(str) + '_' + df['pier'].astype(str)

        # Convertir columnas numéricas de una vez (vectorizado)
        numeric_cols = ['p', 'v2', 'v3', 't', 'm2', 'm3']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # OPTIMIZADO: Preparar columnas antes de agrupar
        if 'location' in df.columns:
            df['_location'] = df['location'].astype(str).fillna('')
        else:
            df['_location'] = ''

        if 'output case' in df.columns:
            df['_output_case'] = df['output case'].astype(str).fillna('')
        else:
            df['_output_case'] = ''

        if 'step type' in df.columns:
            df['_step_type'] = df['step type'].astype(str).replace('nan', '').fillna('')
        else:
            df['_step_type'] = ''

        # OPTIMIZADO: Renombrar columnas para match con COMBO_COLUMNS antes de agrupar
        df_combos = df[['_key', '_output_case', '_location', '_step_type', 'p', 'v2', 'v3', 't', 'm2', 'm3']].copy()
        df_combos.columns = ['pier_key', 'name', 'location', 'step_type', 'P', 'V2', 'V3', 'T', 'M2', 'M3']

        # Procesar por grupos usando set_combinations_from_df (SIN crear objetos)
        grouped = df_combos.groupby('pier_key')

        for pier_key, group in grouped:
            parts = pier_key.split('_', 1)
            if len(parts) != 2:
                continue
            story, pier_label = parts

            if len(group) == 0:
                continue

            # OPTIMIZADO: Usar DataFrame directamente sin crear LoadCombination objects
            forces = ElementForces(
                label=pier_label,
                story=story,
                element_type=ElementForceType.PIER
            )
            forces.set_combinations_from_df(group[COMBO_COLUMNS])
            pier_forces[pier_key] = forces

        return pier_forces

    def _get_average(self, row: pd.Series, col1: str, col2: str) -> float:
        """Obtiene el promedio de dos columnas (bottom/top)."""
        val1 = float(row.get(col1, 0))
        val2 = float(row.get(col2, val1))
        return (val1 + val2) / 2

    # =========================================================================
    # Resumen de Datos
    # =========================================================================

    def get_summary(self, data: ParsedData) -> Dict[str, Any]:
        """Genera un resumen de los datos parseados."""
        # Usar metodos helper de ParsedData para filtrar por tipo
        piers = data.get_piers()
        columns = data.get_columns()
        beams = data.get_beams()
        drop_beams = data.get_drop_beams()

        # Extraer ejes y grillas unicos de piers
        axes = set()
        grillas = set()
        for pier in piers.values():
            if pier.eje:
                axes.add(pier.eje)
            if pier.grilla:
                grillas.add(pier.grilla)

        # Construir resumen base
        summary = {
            'total_piers': len(piers),
            'total_columns': len(columns),
            'total_beams': len(beams),
            'total_drop_beams': len(drop_beams),
            'total_stories': len(data.stories),
            'stories': data.stories,
            'axes': sorted(list(axes)),
            'grillas': sorted(list(grillas)),
            'total_combinations': sum(
                len(f.combinations) for f in data.vertical_forces.values()
            ),
            'materials': list(data.materials.keys()),
            'piers_list': [
                {
                    'key': key,
                    'label': pier.label,
                    'story': pier.story,
                    'grilla': pier.grilla,
                    'eje': pier.eje,
                    'width_m': pier.lw / 1000,
                    'thickness_m': pier.thickness / 1000,
                    'height_m': pier.height / 1000,
                    'fc_MPa': pier.fc,
                    'fy_MPa': pier.fy,
                    'n_meshes': pier.n_meshes,
                    'diameter_v': pier.diameter_v,
                    'spacing_v': pier.spacing_v,
                    'diameter_h': pier.diameter_h,
                    'spacing_h': pier.spacing_h,
                    'diameter_edge': pier.diameter_edge,
                    'n_edge_bars': pier.n_edge_bars,
                    'stirrup_diameter': pier.stirrup_diameter,
                    'stirrup_spacing': pier.stirrup_spacing,
                    'cover': pier.cover,
                    'As_vertical_mm2': pier.As_vertical,
                    'As_horizontal_mm2': pier.As_horizontal,
                    'As_edge_mm2': pier.As_edge_total,
                    'rho_vertical': pier.rho_vertical,
                    'rho_horizontal': pier.rho_horizontal,
                    'reinforcement_desc': pier.reinforcement_description
                }
                for key, pier in piers.items()
            ]
        }

        # Agregar columnas si existen
        if columns:
            summary['columns_list'] = [
                {
                    'key': key,
                    'label': col.label,
                    'story': col.story,
                    'section': col.section_name,
                    'depth_m': col.depth / 1000,
                    'width_m': col.width / 1000,
                    'height_m': col.height / 1000,
                    'fc_MPa': col.fc,
                    'fy_MPa': col.fy,
                    'n_bars_depth': col.n_bars_depth,
                    'n_bars_width': col.n_bars_width,
                    'diameter_long': col.diameter_long,
                    'stirrup_diameter': col.stirrup_diameter,
                    'stirrup_spacing': col.stirrup_spacing,
                    'As_longitudinal_mm2': col.As_longitudinal,
                    'rho_longitudinal': col.rho_longitudinal,
                    'reinforcement_desc': col.reinforcement_description
                }
                for key, col in columns.items()
            ]

        # Agregar vigas si existen
        if beams:
            summary['beams_list'] = [
                {
                    'key': key,
                    'label': beam.label,
                    'story': beam.story,
                    'source': beam.source.value,
                    'is_custom': getattr(beam, 'is_custom', False),
                    'section': beam.section_name,
                    'length_m': beam.length / 1000,
                    'depth': beam.depth,
                    'width': beam.width,
                    'depth_m': beam.depth / 1000,
                    'width_m': beam.width / 1000,
                    'fc_MPa': beam.fc,
                    'fy_MPa': beam.fy,
                    'stirrup_diameter': beam.stirrup_diameter,
                    'stirrup_spacing': beam.stirrup_spacing,
                    'n_stirrup_legs': beam.n_stirrup_legs,
                    'Av_mm2': beam.Av,
                    'reinforcement_desc': beam.reinforcement_description
                }
                for key, beam in beams.items()
            ]

        # Agregar vigas capitel si existen
        if drop_beams:
            summary['drop_beams_list'] = [
                {
                    'key': key,
                    'label': db.label,
                    'story': db.story,
                    'axis_slab': db.axis_slab,
                    'location': db.location,
                    'width_m': db.width / 1000,
                    'depth_m': db.depth / 1000,
                    'length_m': db.length / 1000,
                    'fc_MPa': db.fc,
                    'fy_MPa': db.fy,
                    'n_meshes': db.n_meshes,
                    'diameter_v': db.diameter_v,
                    'spacing_v': db.spacing_v,
                    'diameter_h': db.diameter_h,
                    'spacing_h': db.spacing_h,
                    'diameter_edge': db.diameter_edge,
                    'n_edge_bars': db.n_edge_bars,
                    'stirrup_diameter': db.stirrup_diameter,
                    'stirrup_spacing': db.stirrup_spacing,
                    'cover': db.cover,
                    'As_vertical_mm2': db.As_vertical,
                    'As_horizontal_mm2': db.As_horizontal,
                    'As_edge_mm2': db.As_edge_total,
                    'rho_vertical': db.rho_vertical,
                    'rho_horizontal': db.rho_horizontal,
                    'reinforcement_desc': db.reinforcement_description
                }
                for key, db in drop_beams.items()
            ]

        return summary
