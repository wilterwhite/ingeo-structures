# app/services/parsing/column_parser.py
"""
Parser para columnas desde archivos Excel de ETABS.

Tablas requeridas:
- Frame Section Property Definitions - Concrete Rectangular: geometria
- Element Forces - Columns: fuerzas por combinacion de carga
"""
from typing import Dict, List, Tuple
import pandas as pd

from ...domain.entities.column import Column
from ...domain.entities.column_forces import ColumnForces
from ...domain.entities.load_combination import LoadCombination
from .material_mapper import parse_material_to_fc
from .table_extractor import normalize_columns


class ColumnParser:
    """
    Parser para columnas de ETABS.

    Extrae columnas desde:
    - Frame Section Property Definitions - Concrete Rectangular
    - Element Forces - Columns
    """

    def parse_columns(
        self,
        section_df: pd.DataFrame,
        forces_df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, Column], Dict[str, ColumnForces], List[str]]:
        """
        Parsea columnas y sus fuerzas.

        Args:
            section_df: DataFrame con definiciones de secciones (Frame Sec Def)
            forces_df: DataFrame con fuerzas (Element Forces - Columns)
            materials: Diccionario de materiales ya parseados

        Returns:
            Tupla (columns, column_forces, stories)
        """
        # Parsear definiciones de secciones
        section_defs = self._parse_section_definitions(section_df, materials)

        # Parsear fuerzas y crear columnas
        columns, column_forces, stories = self._parse_forces_and_columns(
            forces_df, section_defs, materials
        )

        return columns, column_forces, stories

    def _parse_section_definitions(
        self,
        df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Dict[str, dict]:
        """
        Parsea las definiciones de secciones de columnas.

        Retorna diccionario con nombre de seccion -> propiedades
        """
        sections = {}

        if df is None:
            return sections

        df = normalize_columns(df)

        for _, row in df.iterrows():
            name = str(row.get('name', ''))
            design_type = str(row.get('design type', '')).lower()

            # Solo procesar columnas
            if 'column' not in design_type:
                continue

            if not name or name == 'nan':
                continue

            # Geometria (m -> mm)
            depth = float(row.get('depth', 0)) * 1000  # eje 2
            width = float(row.get('width', 0)) * 1000  # eje 3

            # Material
            material_name = str(row.get('material', '4000Psi'))
            fc = materials.get(material_name, parse_material_to_fc(material_name))

            sections[name] = {
                'depth': depth,
                'width': width,
                'fc': fc,
                'material': material_name
            }

        return sections

    def _parse_forces_and_columns(
        self,
        df: pd.DataFrame,
        section_defs: Dict[str, dict],
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, Column], Dict[str, ColumnForces], List[str]]:
        """
        Parsea las fuerzas de columnas y crea las entidades Column.
        """
        columns: Dict[str, Column] = {}
        column_forces: Dict[str, ColumnForces] = {}
        stories: List[str] = []
        column_heights: Dict[str, Tuple[float, float]] = {}  # min, max station

        if df is None:
            return columns, column_forces, stories

        df = normalize_columns(df)

        for _, row in df.iterrows():
            story = str(row.get('story', ''))
            column_label = str(row.get('column', ''))

            if not column_label or column_label == 'nan':
                continue

            column_key = f"{story}_{column_label}"

            # Tracking de stations para calcular altura
            try:
                station = float(row.get('station', 0))
            except (ValueError, TypeError):
                station = 0

            if column_key not in column_heights:
                column_heights[column_key] = (station, station)
            else:
                min_s, max_s = column_heights[column_key]
                column_heights[column_key] = (min(min_s, station), max(max_s, station))

            # Crear ColumnForces si no existe
            if column_key not in column_forces:
                column_forces[column_key] = ColumnForces(
                    column_label=column_label,
                    story=story,
                    combinations=[]
                )

            # Determinar location basado en station
            # La station mas baja es "Bottom", la mas alta es "Top"
            location = str(row.get('location', ''))
            if not location or location == 'nan':
                location = 'Middle'

            # Parsear combinacion
            try:
                combo = LoadCombination(
                    name=str(row.get('output case', '')),
                    location=location,
                    step_type=self._clean_step_type(row.get('step type', '')),
                    P=float(row.get('p', 0)),
                    V2=float(row.get('v2', 0)),
                    V3=float(row.get('v3', 0)),
                    T=float(row.get('t', 0)),
                    M2=float(row.get('m2', 0)),
                    M3=float(row.get('m3', 0))
                )
                column_forces[column_key].combinations.append(combo)
            except (ValueError, TypeError):
                continue

            if story not in stories:
                stories.append(story)

        # Crear columnas con altura calculada
        for column_key, forces in column_forces.items():
            story, column_label = column_key.split('_', 1)

            # Buscar seccion (por ahora usamos la primera definicion disponible)
            # En una implementacion mas completa, habria que mapear columna -> seccion
            section = None
            for sec_name, sec_props in section_defs.items():
                section = sec_props
                break  # Usar la primera por ahora

            if section is None:
                # Valores por defecto si no hay seccion
                section = {'depth': 450, 'width': 450, 'fc': 28}

            # Calcular altura desde stations
            if column_key in column_heights:
                min_s, max_s = column_heights[column_key]
                height = (max_s - min_s) * 1000  # m -> mm
                if height < 100:  # Si es muy pequeno, usar 3m por defecto
                    height = 3000
            else:
                height = 3000

            # Actualizar altura en forces
            forces.height = height

            columns[column_key] = Column(
                label=column_label,
                story=story,
                depth=section['depth'],
                width=section['width'],
                height=height,
                fc=section['fc'],
                fy=420.0
            )

        return columns, column_forces, stories

    def _clean_step_type(self, value) -> str:
        """Limpia el step_type de valores nan."""
        step_type = str(value) if value else ''
        return '' if step_type == 'nan' else step_type
