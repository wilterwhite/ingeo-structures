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
from io import BytesIO
from typing import Dict, List, Any
import pandas as pd

logger = logging.getLogger(__name__)

from ...domain.entities import Pier, LoadCombination, PierForces, ParsedData
from ...domain.constants.reinforcement import FY_DEFAULT_MPA
from .material_mapper import parse_material_to_fc
from .table_extractor import (
    normalize_columns,
    find_table_in_sheet,
    find_table_by_sheet_name,
    extract_units_from_df,
)
from .column_parser import ColumnParser
from .beam_parser import BeamParser
from .drop_beam_parser import DropBeamParser


# Nombres de tablas soportadas (para mostrar al usuario)
SUPPORTED_TABLES = {
    'piers': [
        'Wall Property Definitions',
        'Pier Section Properties',
        'Pier Forces'
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

    def parse_excel(self, file_content: bytes) -> ParsedData:
        """
        Parsea el archivo Excel de ETABS.

        Detecta automaticamente que tablas estan presentes y las procesa.

        Args:
            file_content: Contenido binario del archivo Excel

        Returns:
            ParsedData con todos los datos parseados
        """
        excel_file = pd.ExcelFile(BytesIO(file_content))

        # Almacenamiento
        raw_data: Dict[str, pd.DataFrame] = {}
        materials: Dict[str, float] = {}

        # DataFrames para cada tabla
        # Piers
        wall_props_df = None
        pier_props_df = None
        pier_forces_df = None
        # Columnas y Vigas
        frame_section_df = None
        frame_circular_df = None  # Frame Section Property Definitions - Concrete Circle
        frame_assigns_df = None  # Frame Assignments - Section Properties
        column_forces_df = None
        beam_forces_df = None
        # Spandrels
        spandrel_props_df = None
        spandrel_forces_df = None
        # Vigas capitel (Section Cuts)
        section_cut_df = None

        # Buscar tablas en todas las hojas
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            raw_data[sheet_name] = df

            # Piers
            if wall_props_df is None:
                wall_props_df = find_table_in_sheet(df, "Wall Property Definitions")

            if pier_props_df is None:
                pier_props_df = find_table_in_sheet(df, "Pier Section Properties")

            if pier_forces_df is None:
                pier_forces_df = find_table_in_sheet(df, "Pier Forces")

            # Frame sections (columnas y vigas)
            if frame_section_df is None:
                frame_section_df = find_table_in_sheet(
                    df, "Frame Section Property Definitions - Concrete Rectangular"
                )

            # Frame sections circulares
            if frame_circular_df is None:
                frame_circular_df = find_table_in_sheet(
                    df, "Frame Section Property Definitions - Concrete Circle"
                )

            # Frame assignments (asignación de secciones a elementos)
            if frame_assigns_df is None:
                frame_assigns_df = find_table_in_sheet(
                    df, "Frame Assignments - Section Properties"
                )

            # Columnas
            if column_forces_df is None:
                column_forces_df = find_table_in_sheet(df, "Element Forces - Columns")

            # Vigas
            if beam_forces_df is None:
                beam_forces_df = find_table_in_sheet(df, "Element Forces - Beams")

            # Spandrels
            if spandrel_props_df is None:
                spandrel_props_df = find_table_in_sheet(df, "Spandrel Section Properties")

            if spandrel_forces_df is None:
                spandrel_forces_df = find_table_in_sheet(df, "Spandrel Forces")

            # Vigas capitel (Section Cut Forces)
            if section_cut_df is None:
                section_cut_df = find_table_in_sheet(df, "Section Cut Forces - Analysis")

        # Fallback: buscar por nombre de hoja (piers)
        if wall_props_df is None:
            wall_props_df = find_table_by_sheet_name(excel_file, ['wall', 'prop'])

        if pier_props_df is None:
            pier_props_df = find_table_by_sheet_name(excel_file, ['pier', 'section'])

        if pier_forces_df is None:
            pier_forces_df = find_table_by_sheet_name(excel_file, ['pier', 'force'])

        # Procesar materiales
        if wall_props_df is not None:
            materials = self._parse_materials(wall_props_df)

        # Tambien obtener materiales de frame sections si existen
        if frame_section_df is not None:
            frame_materials = self._parse_frame_materials(frame_section_df)
            materials.update(frame_materials)

        # Procesar piers
        piers, pier_stories = self._parse_piers(pier_props_df, materials)
        pier_forces = self._parse_forces(pier_forces_df)

        # Procesar columnas
        columns = {}
        column_forces = {}
        column_stories = []
        if column_forces_df is not None:
            columns, column_forces, column_stories = self.column_parser.parse_columns(
                frame_section_df, column_forces_df, materials
            )

        # Procesar vigas
        beams = {}
        beam_forces = {}
        beam_stories = []
        if beam_forces_df is not None or spandrel_forces_df is not None:
            beams, beam_forces, beam_stories = self.beam_parser.parse_beams(
                frame_section_df, frame_assigns_df, beam_forces_df,
                spandrel_props_df, spandrel_forces_df,
                materials, frame_circular_df
            )

        # Procesar vigas capitel (Section Cut Forces)
        drop_beams = {}
        drop_beam_forces = {}
        drop_beam_stories = []
        if section_cut_df is not None:
            drop_beams, drop_beam_forces, drop_beam_stories = self.drop_beam_parser.parse_drop_beams(
                section_cut_df, materials
            )

        # Combinar stories
        all_stories = pier_stories.copy()
        for s in column_stories + beam_stories + drop_beam_stories:
            if s not in all_stories:
                all_stories.append(s)

        return ParsedData(
            piers=piers,
            pier_forces=pier_forces,
            columns=columns,
            column_forces=column_forces,
            beams=beams,
            beam_forces=beam_forces,
            drop_beams=drop_beams,
            drop_beam_forces=drop_beam_forces,
            materials=materials,
            stories=all_stories,
            raw_data=raw_data
        )

    def _parse_materials(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extrae el mapeo de nombres de materiales a f'c desde Wall Property Definitions."""
        materials = {}
        df = normalize_columns(df)

        for _, row in df.iterrows():
            name = str(row.get('name', ''))
            material = str(row.get('material', name))
            if name:
                fc = parse_material_to_fc(material)
                materials[name] = fc
                materials[material] = fc

        return materials

    def _parse_frame_materials(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extrae materiales desde Frame Section Definitions."""
        materials = {}

        if df is None:
            return materials

        df = normalize_columns(df)

        for _, row in df.iterrows():
            material = str(row.get('material', ''))
            if material and material != 'nan':
                fc = parse_material_to_fc(material)
                materials[material] = fc

        return materials

    def _parse_piers(
        self,
        df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> tuple[Dict[str, Pier], List[str]]:
        """Extrae los piers con su geometría."""
        piers: Dict[str, Pier] = {}
        stories: List[str] = []

        if df is None:
            logger.info("Piers: No se encontró tabla Pier Section Properties")
            return piers, stories

        df = normalize_columns(df)

        # Extraer factores de conversión de unidades de la primera fila
        units = extract_units_from_df(df)
        logger.info(f"Piers: Unidades detectadas - width: {units.get('width bottom', 1.0)}, cg: {units.get('cg bottom z', 1.0)}")

        # Saltar la fila de unidades (primera fila del DataFrame normalizado)
        df = df.iloc[1:]

        # Contadores para logging
        total_rows = len(df)
        skipped_empty = 0
        skipped_invalid_geometry = 0
        imported_ok = 0

        for _, row in df.iterrows():
            story = str(row.get('story', ''))
            pier_label = str(row.get('pier', ''))

            if not pier_label or pier_label == 'nan':
                skipped_empty += 1
                continue

            # Geometría - aplicar factor de conversión según unidades del Excel
            width = self._get_average(row, 'width bottom', 'width top') * units.get('width bottom', 1.0)
            thickness = self._get_average(row, 'thickness bottom', 'thickness top') * units.get('thickness bottom', 1.0)

            # Altura - CG viene en la unidad especificada en el Excel
            cg_bottom = float(row.get('cg bottom z', 0)) * units.get('cg bottom z', 1.0)
            cg_top = float(row.get('cg top z', cg_bottom + 3000)) * units.get('cg top z', 1.0)
            height = cg_top - cg_bottom

            # Material -> f'c
            material_name = str(row.get('material', '4000Psi'))
            fc = materials.get(material_name, parse_material_to_fc(material_name))

            # Ángulo del eje
            axis_angle = float(row.get('axisangle', row.get('axis angle', 0)))

            # Validar geometría antes de crear Pier (evitar divisiones por cero)
            if width <= 0 or thickness <= 0 or height <= 0:
                skipped_invalid_geometry += 1
                logger.warning(
                    f"Pier {pier_label}@{story}: geometría inválida "
                    f"(width={width}, thickness={thickness}, height={height})"
                )
                continue

            # Crear Pier
            pier_key = f"{story}_{pier_label}"
            piers[pier_key] = Pier(
                label=pier_label,
                story=story,
                width=width,
                thickness=thickness,
                height=height,
                fc=fc,
                fy=FY_DEFAULT_MPA,
                axis_angle=axis_angle
            )
            imported_ok += 1

            if story not in stories:
                stories.append(story)

        # Log resumen
        logger.info(
            f"Piers: {imported_ok} importados OK, "
            f"{skipped_invalid_geometry} con geometría inválida, "
            f"{skipped_empty} filas vacías (de {total_rows} filas)"
        )

        return piers, stories

    def _parse_forces(self, df: pd.DataFrame) -> Dict[str, PierForces]:
        """Extrae las fuerzas por combinación de carga."""
        pier_forces: Dict[str, PierForces] = {}

        if df is None:
            return pier_forces

        df = normalize_columns(df)

        for _, row in df.iterrows():
            story = str(row.get('story', ''))
            pier_label = str(row.get('pier', ''))

            if not pier_label or pier_label == 'nan':
                continue

            pier_key = f"{story}_{pier_label}"

            # Crear PierForces si no existe
            if pier_key not in pier_forces:
                pier_forces[pier_key] = PierForces(
                    pier_label=pier_label,
                    story=story,
                    combinations=[]
                )

            # Parsear combinación
            try:
                combo = LoadCombination(
                    name=str(row.get('output case', '')),
                    location=str(row.get('location', '')),
                    step_type=self._clean_step_type(row.get('step type', '')),
                    P=float(row.get('p', 0)),
                    V2=float(row.get('v2', 0)),
                    V3=float(row.get('v3', 0)),
                    T=float(row.get('t', 0)),
                    M2=float(row.get('m2', 0)),
                    M3=float(row.get('m3', 0))
                )
                pier_forces[pier_key].combinations.append(combo)
            except (ValueError, TypeError):
                continue

        return pier_forces

    def _get_average(self, row: pd.Series, col1: str, col2: str) -> float:
        """Obtiene el promedio de dos columnas (bottom/top)."""
        val1 = float(row.get(col1, 0))
        val2 = float(row.get(col2, val1))
        return (val1 + val2) / 2

    def _clean_step_type(self, value) -> str:
        """Limpia el step_type de valores nan."""
        step_type = str(value) if value else ''
        return '' if step_type == 'nan' else step_type

    def parse_excel_with_progress(self, file_content: bytes):
        """
        Parsea el archivo Excel de ETABS con eventos de progreso.

        Generador que emite eventos de progreso durante el parsing.

        Args:
            file_content: Contenido binario del archivo Excel

        Yields:
            dict: Eventos de progreso con type='progress', current, total, element
                  o type='complete' con result al finalizar
        """
        excel_file = pd.ExcelFile(BytesIO(file_content))
        total_sheets = len(excel_file.sheet_names)

        # Fase 1: Leer hojas (progreso 0-50%)
        raw_data: Dict[str, pd.DataFrame] = {}
        materials: Dict[str, float] = {}

        # DataFrames para cada tabla
        wall_props_df = None
        pier_props_df = None
        pier_forces_df = None
        frame_section_df = None
        frame_circular_df = None
        frame_assigns_df = None
        column_forces_df = None
        beam_forces_df = None
        spandrel_props_df = None
        spandrel_forces_df = None
        section_cut_df = None

        # Buscar tablas en todas las hojas con progreso
        for i, sheet_name in enumerate(excel_file.sheet_names):
            # Emitir progreso de lectura de hojas
            yield {
                'type': 'progress',
                'phase': 'reading',
                'current': i + 1,
                'total': total_sheets,
                'element': f'Leyendo hoja: {sheet_name}'
            }

            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            raw_data[sheet_name] = df

            # Piers
            if wall_props_df is None:
                wall_props_df = find_table_in_sheet(df, "Wall Property Definitions")
            if pier_props_df is None:
                pier_props_df = find_table_in_sheet(df, "Pier Section Properties")
            if pier_forces_df is None:
                pier_forces_df = find_table_in_sheet(df, "Pier Forces")

            # Frame sections
            if frame_section_df is None:
                frame_section_df = find_table_in_sheet(
                    df, "Frame Section Property Definitions - Concrete Rectangular"
                )
            if frame_circular_df is None:
                frame_circular_df = find_table_in_sheet(
                    df, "Frame Section Property Definitions - Concrete Circle"
                )
            if frame_assigns_df is None:
                frame_assigns_df = find_table_in_sheet(
                    df, "Frame Assignments - Section Properties"
                )

            # Columnas y Vigas
            if column_forces_df is None:
                column_forces_df = find_table_in_sheet(df, "Element Forces - Columns")
            if beam_forces_df is None:
                beam_forces_df = find_table_in_sheet(df, "Element Forces - Beams")

            # Spandrels
            if spandrel_props_df is None:
                spandrel_props_df = find_table_in_sheet(df, "Spandrel Section Properties")
            if spandrel_forces_df is None:
                spandrel_forces_df = find_table_in_sheet(df, "Spandrel Forces")

            # Vigas capitel
            if section_cut_df is None:
                section_cut_df = find_table_in_sheet(df, "Section Cut Forces - Analysis")

        # Fallback: buscar por nombre de hoja
        if wall_props_df is None:
            wall_props_df = find_table_by_sheet_name(excel_file, ['wall', 'prop'])
        if pier_props_df is None:
            pier_props_df = find_table_by_sheet_name(excel_file, ['pier', 'section'])
        if pier_forces_df is None:
            pier_forces_df = find_table_by_sheet_name(excel_file, ['pier', 'force'])

        # Fase 2: Procesar tablas (progreso 50-100%)
        yield {'type': 'progress', 'phase': 'parsing', 'current': 1, 'total': 6, 'element': 'Procesando materiales'}
        if wall_props_df is not None:
            materials = self._parse_materials(wall_props_df)
        if frame_section_df is not None:
            frame_materials = self._parse_frame_materials(frame_section_df)
            materials.update(frame_materials)

        yield {'type': 'progress', 'phase': 'parsing', 'current': 2, 'total': 6, 'element': 'Procesando muros'}
        piers, pier_stories = self._parse_piers(pier_props_df, materials)
        pier_forces = self._parse_forces(pier_forces_df)

        yield {'type': 'progress', 'phase': 'parsing', 'current': 3, 'total': 6, 'element': 'Procesando columnas'}
        columns = {}
        column_forces = {}
        column_stories = []
        if column_forces_df is not None:
            columns, column_forces, column_stories = self.column_parser.parse_columns(
                frame_section_df, column_forces_df, materials
            )

        yield {'type': 'progress', 'phase': 'parsing', 'current': 4, 'total': 6, 'element': 'Procesando vigas'}
        beams = {}
        beam_forces = {}
        beam_stories = []
        if beam_forces_df is not None or spandrel_forces_df is not None:
            beams, beam_forces, beam_stories = self.beam_parser.parse_beams(
                frame_section_df, frame_assigns_df, beam_forces_df,
                spandrel_props_df, spandrel_forces_df,
                materials, frame_circular_df
            )

        yield {'type': 'progress', 'phase': 'parsing', 'current': 5, 'total': 6, 'element': 'Procesando vigas capitel'}
        drop_beams = {}
        drop_beam_forces = {}
        drop_beam_stories = []
        if section_cut_df is not None:
            drop_beams, drop_beam_forces, drop_beam_stories = self.drop_beam_parser.parse_drop_beams(
                section_cut_df, materials
            )

        yield {'type': 'progress', 'phase': 'parsing', 'current': 6, 'total': 6, 'element': 'Finalizando'}

        # Combinar stories
        all_stories = pier_stories.copy()
        for s in column_stories + beam_stories + drop_beam_stories:
            if s not in all_stories:
                all_stories.append(s)

        # Emitir resultado final
        result = ParsedData(
            piers=piers,
            pier_forces=pier_forces,
            columns=columns,
            column_forces=column_forces,
            beams=beams,
            beam_forces=beam_forces,
            drop_beams=drop_beams,
            drop_beam_forces=drop_beam_forces,
            materials=materials,
            stories=all_stories,
            raw_data=raw_data
        )

        yield {'type': 'complete', 'result': result}

    def get_summary(self, data: ParsedData) -> Dict[str, Any]:
        """Genera un resumen de los datos parseados."""
        # Extraer ejes y grillas únicos de piers
        axes = set()
        grillas = set()
        for pier in data.piers.values():
            if pier.eje:
                axes.add(pier.eje)
            if pier.grilla:
                grillas.add(pier.grilla)

        # Construir resumen base
        summary = {
            'total_piers': len(data.piers),
            'total_columns': len(data.columns) if data.columns else 0,
            'total_beams': len(data.beams) if data.beams else 0,
            'total_drop_beams': len(data.drop_beams) if data.drop_beams else 0,
            'total_stories': len(data.stories),
            'stories': data.stories,
            'axes': sorted(list(axes)),
            'grillas': sorted(list(grillas)),
            'total_combinations': sum(
                len(pf.combinations) for pf in data.pier_forces.values()
            ),
            'materials': list(data.materials.keys()),
            'piers_list': [
                {
                    'key': key,
                    'label': pier.label,
                    'story': pier.story,
                    'grilla': pier.grilla,
                    'eje': pier.eje,
                    'width_m': pier.width / 1000,
                    'thickness_m': pier.thickness / 1000,
                    'height_m': pier.height / 1000,
                    'fc_MPa': pier.fc,
                    'fy_MPa': pier.fy,
                    # Configuración de armadura
                    'n_meshes': pier.n_meshes,
                    'diameter_v': pier.diameter_v,
                    'spacing_v': pier.spacing_v,
                    'diameter_h': pier.diameter_h,
                    'spacing_h': pier.spacing_h,
                    'diameter_edge': pier.diameter_edge,
                    # Elemento de borde
                    'n_edge_bars': pier.n_edge_bars,
                    'stirrup_diameter': pier.stirrup_diameter,
                    'stirrup_spacing': pier.stirrup_spacing,
                    'cover': pier.cover,
                    # Valores calculados
                    'As_vertical_mm2': pier.As_vertical,
                    'As_horizontal_mm2': pier.As_horizontal,
                    'As_edge_mm2': pier.As_edge_total,
                    'rho_vertical': pier.rho_vertical,
                    'rho_horizontal': pier.rho_horizontal,
                    'reinforcement_desc': pier.reinforcement_description
                }
                for key, pier in data.piers.items()
            ]
        }

        # Agregar columnas si existen
        if data.columns:
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
                for key, col in data.columns.items()
            ]

        # Agregar vigas si existen
        if data.beams:
            summary['beams_list'] = [
                {
                    'key': key,
                    'label': beam.label,
                    'story': beam.story,
                    'source': beam.source.value,  # 'frame' o 'spandrel'
                    'is_custom': getattr(beam, 'is_custom', False),
                    'section': beam.section_name,
                    'length_m': beam.length / 1000,
                    'depth': beam.depth,  # mm (para mostrar en dropdown)
                    'width': beam.width,  # mm (para mostrar en dropdown)
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
                for key, beam in data.beams.items()
            ]

        # Agregar vigas capitel si existen
        if data.drop_beams:
            summary['drop_beams_list'] = [
                {
                    'key': key,
                    'label': db.label,
                    'story': db.story,
                    'axis_slab': db.axis_slab,
                    'location': db.location,
                    'width_m': db.width / 1000,       # Espesor de losa
                    'thickness_m': db.thickness / 1000,  # Ancho tributario
                    'length_m': db.length / 1000,
                    'fc_MPa': db.fc,
                    'fy_MPa': db.fy,
                    # Configuración de armadura (igual que pier)
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
                    # Valores calculados
                    'As_vertical_mm2': db.As_vertical,
                    'As_horizontal_mm2': db.As_horizontal,
                    'As_edge_mm2': db.As_edge_total,
                    'rho_vertical': db.rho_vertical,
                    'rho_horizontal': db.rho_horizontal,
                    'reinforcement_desc': db.reinforcement_description
                }
                for key, db in data.drop_beams.items()
            ]

        return summary
