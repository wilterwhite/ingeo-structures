# app/services/parsing/excel_parser.py
"""
Parser de archivos Excel exportados de ETABS.

Orquesta la lectura de las tablas de ETABS usando los módulos:
- material_mapper: Conversión de nombres de materiales a f'c
- table_extractor: Búsqueda de tablas dentro de hojas Excel
"""
from io import BytesIO
from typing import Dict, List, Any
import pandas as pd

from ...domain.entities import Pier, LoadCombination, PierForces, ParsedData
from .material_mapper import parse_material_to_fc
from .table_extractor import (
    normalize_columns,
    find_table_in_sheet,
    find_table_by_sheet_name
)


# =============================================================================
# Parser Principal
# =============================================================================

class EtabsExcelParser:
    """
    Parser para archivos Excel de ETABS con tablas de muros.

    Espera encontrar las siguientes tablas (hojas o secciones):
    1. Wall Property Definitions - Propiedades de materiales
    2. Pier Section Properties - Geometría de piers
    3. Pier Forces - Fuerzas por combinación de carga
    """

    def parse_excel(self, file_content: bytes) -> ParsedData:
        """
        Parsea el archivo Excel de ETABS.

        Args:
            file_content: Contenido binario del archivo Excel

        Returns:
            ParsedData con todos los datos parseados
        """
        excel_file = pd.ExcelFile(BytesIO(file_content))

        # Almacenamiento
        raw_data: Dict[str, pd.DataFrame] = {}
        materials: Dict[str, float] = {}

        # Buscar tablas en todas las hojas
        wall_props_df = None
        pier_props_df = None
        pier_forces_df = None

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            raw_data[sheet_name] = df

            # Buscar tablas con marcadores "TABLE:"
            if wall_props_df is None:
                wall_props_df = find_table_in_sheet(df, "Wall Property Definitions")

            if pier_props_df is None:
                pier_props_df = find_table_in_sheet(df, "Pier Section Properties")

            if pier_forces_df is None:
                pier_forces_df = find_table_in_sheet(df, "Pier Forces")

        # Fallback: buscar por nombre de hoja
        if wall_props_df is None:
            wall_props_df = find_table_by_sheet_name(excel_file, ['wall', 'prop'])

        if pier_props_df is None:
            pier_props_df = find_table_by_sheet_name(excel_file, ['pier', 'section'])

        if pier_forces_df is None:
            pier_forces_df = find_table_by_sheet_name(excel_file, ['pier', 'force'])

        # Procesar materiales
        if wall_props_df is not None:
            materials = self._parse_materials(wall_props_df)

        # Procesar piers
        piers, stories = self._parse_piers(pier_props_df, materials)

        # Procesar fuerzas
        pier_forces = self._parse_forces(pier_forces_df)

        return ParsedData(
            piers=piers,
            pier_forces=pier_forces,
            materials=materials,
            stories=stories,
            raw_data=raw_data
        )

    def _parse_materials(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extrae el mapeo de nombres de materiales a f'c."""
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

    def _parse_piers(
        self,
        df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> tuple[Dict[str, Pier], List[str]]:
        """Extrae los piers con su geometría."""
        piers: Dict[str, Pier] = {}
        stories: List[str] = []

        if df is None:
            return piers, stories

        df = normalize_columns(df)

        for _, row in df.iterrows():
            story = str(row.get('story', ''))
            pier_label = str(row.get('pier', ''))

            if not pier_label or pier_label == 'nan':
                continue

            # Geometría (m -> mm)
            width = self._get_average(row, 'width bottom', 'width top') * 1000
            thickness = self._get_average(row, 'thickness bottom', 'thickness top') * 1000

            # Altura
            cg_bottom = float(row.get('cg bottom z', 0))
            cg_top = float(row.get('cg top z', cg_bottom + 3))
            height = (cg_top - cg_bottom) * 1000

            # Material -> f'c
            material_name = str(row.get('material', '4000Psi'))
            fc = materials.get(material_name, parse_material_to_fc(material_name))

            # Ángulo del eje
            axis_angle = float(row.get('axisangle', row.get('axis angle', 0)))

            # Crear Pier
            pier_key = f"{story}_{pier_label}"
            piers[pier_key] = Pier(
                label=pier_label,
                story=story,
                width=width,
                thickness=thickness,
                height=height,
                fc=fc,
                fy=420.0,
                axis_angle=axis_angle
            )

            if story not in stories:
                stories.append(story)

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

    def get_summary(self, data: ParsedData) -> Dict[str, Any]:
        """Genera un resumen de los datos parseados."""
        # Extraer ejes únicos
        axes = set()
        for pier in data.piers.values():
            if pier.eje:
                axes.add(pier.eje)

        return {
            'total_piers': len(data.piers),
            'total_stories': len(data.stories),
            'stories': data.stories,
            'axes': sorted(list(axes)),
            'total_combinations': sum(
                len(pf.combinations) for pf in data.pier_forces.values()
            ),
            'materials': list(data.materials.keys()),
            'piers_list': [
                {
                    'key': key,
                    'label': pier.label,
                    'story': pier.story,
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
