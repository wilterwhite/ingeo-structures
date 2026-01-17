# app/services/parsing/column_parser.py
"""
Parser para columnas desde archivos Excel de ETABS.

Tablas requeridas:
- Frame Section Property Definitions - Concrete Rectangular: geometria
- Frame Assignments - Section Properties: mapeo columna -> seccion
- Element Forces - Columns: fuerzas por combinacion de carga

OPTIMIZADO: Usa operaciones vectorizadas de pandas en lugar de iterrows()
para procesar tablas grandes (180k+ filas) eficientemente.
"""
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor

from ...domain.entities import (
    VerticalElement,
    VerticalElementSource,
    ElementForces,
    ElementForceType,
)
from ...domain.entities.element_forces import COMBO_COLUMNS
from ...domain.constants.reinforcement import FY_DEFAULT_MPA
from .material_mapper import parse_material_to_fc
from .table_extractor import normalize_columns, extract_units_from_df
from ..logging import claude_logger
import logging

logger = logging.getLogger(__name__)


class ColumnParser:
    """
    Parser para columnas de ETABS.

    Extrae columnas desde:
    - Frame Section Property Definitions - Concrete Rectangular
    - Frame Assignments - Section Properties
    - Element Forces - Columns
    """

    def parse_columns(
        self,
        section_df: pd.DataFrame,
        assigns_df: Optional[pd.DataFrame],
        forces_df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, VerticalElement], Dict[str, ElementForces], List[str]]:
        """
        Parsea columnas y sus fuerzas.

        Args:
            section_df: DataFrame con definiciones de secciones (Frame Sec Def)
            assigns_df: DataFrame con asignaciones columna->seccion (Frame Assigns)
            forces_df: DataFrame con fuerzas (Element Forces - Columns)
            materials: Diccionario de materiales ya parseados

        Returns:
            Tupla (columns, column_forces, stories)
            donde columns son VerticalElement con source=FRAME
        """
        # Parsear definiciones de secciones
        section_defs = self._parse_section_definitions(section_df, materials)

        # Parsear asignaciones columna -> seccion
        column_sections = self._parse_section_assignments(assigns_df)

        # Parsear fuerzas y crear columnas (VECTORIZADO)
        columns, column_forces, stories = self._parse_forces_and_columns_vectorized(
            forces_df, section_defs, column_sections, materials
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

        # Extraer factores de conversion de unidades de la primera fila
        units = extract_units_from_df(df)

        # Saltar la fila de unidades
        df = df.iloc[1:]

        # Filtrar solo columnas y filas validas
        df = df[df['name'].notna() & (df['name'] != 'nan')]
        if 'design type' in df.columns:
            mask = df['design type'].astype(str).str.lower().str.contains('column', na=False)
            df = df[mask]

        if len(df) == 0:
            return sections

        # Vectorizado: extraer todas las secciones de una vez
        depth_factor = units.get('depth', 1.0)
        width_factor = units.get('width', 1.0)

        # Convertir columnas numéricas
        df['depth'] = pd.to_numeric(df['depth'], errors='coerce').fillna(0) * depth_factor
        df['width'] = pd.to_numeric(df['width'], errors='coerce').fillna(0) * width_factor
        df['_material'] = df.get('material', pd.Series(['4000Psi'] * len(df))).astype(str).fillna('4000Psi')

        # OPTIMIZADO: Usar to_dict('records') en lugar de iterrows
        records = df[['name', 'depth', 'width', '_material']].to_dict('records')

        for r in records:
            name = str(r.get('name', ''))
            if not name or name == 'nan':
                continue

            depth = float(r.get('depth', 0))
            width = float(r.get('width', 0))
            material_name = r['_material']
            fc = materials.get(material_name, parse_material_to_fc(material_name))

            sections[name] = {
                'depth': depth,
                'width': width,
                'fc': fc,
                'material': material_name
            }

        return sections

    def _parse_section_assignments(
        self,
        df: Optional[pd.DataFrame]
    ) -> Dict[str, str]:
        """
        Parsea las asignaciones de secciones a columnas.
        Retorna diccionario con (story, label) -> nombre_seccion
        """
        if df is None:
            return {}

        df = normalize_columns(df)

        # Filtrar filas validas
        df = df[
            df['story'].notna() & (df['story'] != 'nan') &
            df['label'].notna() & (df['label'] != 'nan') &
            df['section property'].notna() & (df['section property'] != 'nan')
        ]

        if len(df) == 0:
            return {}

        # Vectorizado: crear keys y valores
        keys = df['story'].astype(str) + '_' + df['label'].astype(str)
        values = df['section property'].astype(str)

        assignments = dict(zip(keys, values))
        logger.info(f"Column assignments: {len(assignments)} asignaciones parseadas")
        return assignments

    def _parse_forces_and_columns_vectorized(
        self,
        df: pd.DataFrame,
        section_defs: Dict[str, dict],
        column_sections: Dict[str, str],
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, VerticalElement], Dict[str, ElementForces], List[str]]:
        """
        Parsea las fuerzas de columnas usando operaciones VECTORIZADAS.
        Mucho mas rapido que iterrows() para 180k+ filas.
        """
        columns: Dict[str, VerticalElement] = {}
        column_forces: Dict[str, ElementForces] = {}
        stories: List[str] = []

        if df is None or len(df) == 0:
            return columns, column_forces, stories

        df = normalize_columns(df)

        # Filtrar filas validas
        df = df[df['column'].notna() & (df['column'].astype(str) != 'nan')].copy()

        if len(df) == 0:
            return columns, column_forces, stories

        # Crear column_key vectorizado
        df['column_key'] = df['story'].astype(str) + '_' + df['column'].astype(str)

        # Convertir columnas numericas de una vez (vectorizado)
        numeric_cols = ['station', 'p', 'v2', 'v3', 't', 'm2', 'm3']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Calcular min/max station por columna (vectorizado con groupby)
        station_stats = df.groupby('column_key')['station'].agg(['min', 'max'])
        column_heights = {
            key: (row['min'], row['max'])
            for key, row in station_stats.iterrows()
        }

        # Obtener stories unicos (vectorizado)
        stories = df['story'].astype(str).unique().tolist()

        # OPTIMIZADO: Preparar columnas antes de agrupar
        # Derivar location desde station (ETABS da Station numérico para columnas)
        # Nota: ETABS puede tener columna 'location' pero vacía para columnas
        # Validar que existan valores de ubicación reales (Top/Bottom/Middle)
        valid_locations = {'Top', 'Bottom', 'Middle', 'top', 'bottom', 'middle'}
        has_valid_location = (
            'location' in df.columns and
            df['location'].astype(str).str.strip().isin(valid_locations).any()
        )
        if has_valid_location:
            df['_location'] = df['location'].astype(str).replace('nan', 'Middle').replace('None', 'Middle').fillna('Middle')
        elif 'station' in df.columns:
            # Convertir station numérico a Top/Bottom/Middle
            # station=0 o min → Bottom, station=max → Top, otros → Middle
            def station_to_location(row):
                station = row['station']
                col_key = row['column_key']
                if col_key not in column_heights:
                    return 'Middle'
                min_st, max_st = column_heights[col_key]
                # Tolerancia para comparación de floats
                tol = 0.001
                if abs(station - min_st) < tol:
                    return 'Bottom'
                elif abs(station - max_st) < tol:
                    return 'Top'
                else:
                    return 'Middle'
            df['_location'] = df.apply(station_to_location, axis=1)
        else:
            df['_location'] = 'Middle'

        if 'output case' in df.columns:
            df['_output_case'] = df['output case'].astype(str).fillna('')
        else:
            df['_output_case'] = ''

        if 'step type' in df.columns:
            df['_step_type'] = df['step type'].astype(str).replace('nan', '').fillna('')
        else:
            df['_step_type'] = ''

        # OPTIMIZADO: Renombrar columnas para match con COMBO_COLUMNS antes de agrupar
        df_combos = df[['column_key', '_output_case', '_location', '_step_type', 'p', 'v2', 'v3', 't', 'm2', 'm3']].copy()
        df_combos.columns = ['column_key', 'name', 'location', 'step_type', 'P', 'V2', 'V3', 'T', 'M2', 'M3']

        # AGRESIVO: Procesar grupos en PARALELO con todos los cores
        grouped = df_combos.groupby('column_key')
        group_items = list(grouped)
        
        # Función worker para procesar un chunk de grupos
        def process_chunk(chunk_items):
            chunk_forces = {}
            for column_key, group in chunk_items:
                parts = column_key.split('_', 1)
                if len(parts) != 2 or len(group) == 0:
                    continue
                story, column_label = parts
                forces = ElementForces(
                    label=column_label,
                    story=story,
                    element_type=ElementForceType.COLUMN
                )
                forces.set_combinations_from_df(group[COMBO_COLUMNS])
                chunk_forces[column_key] = forces
            return chunk_forces
        
        # Dividir en chunks y procesar en paralelo
        n_workers = min(os.cpu_count() or 8, len(group_items))
        if n_workers > 1 and len(group_items) > 100:
            chunk_size = max(1, len(group_items) // n_workers)
            chunks = [group_items[i:i+chunk_size] for i in range(0, len(group_items), chunk_size)]
            
            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                results = list(executor.map(process_chunk, chunks))
                for chunk_result in results:
                    column_forces.update(chunk_result)
        else:
            # Secuencial para datasets pequeños
            column_forces = process_chunk(group_items)

        # Crear columnas con altura calculada
        skipped_columns = []
        for column_key, forces in column_forces.items():
            story, column_label = column_key.split('_', 1)

            # Buscar seccion usando el mapeo de asignaciones
            section = None

            # 1. Buscar en asignaciones (Frame Assigns - Sect Prop)
            if column_key in column_sections:
                section_name = column_sections[column_key]
                section = section_defs.get(section_name)

            # 2. Buscar por label directo en secciones
            if section is None:
                section = section_defs.get(column_label)

            # 3. Si no hay seccion, saltar esta columna y registrar error
            if section is None:
                skipped_columns.append(f"{column_label} ({story})")
                continue

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

            # Crear VerticalElement con source=FRAME (columna)
            depth = section['depth']
            width = section['width']

            # Obtener nombre de seccion para PM
            section_name = column_sections.get(column_key, column_label)

            column = VerticalElement(
                label=column_label,
                story=story,
                length=depth,
                thickness=width,
                height=height,
                fc=section['fc'],
                fy=FY_DEFAULT_MPA,
                source=VerticalElementSource.FRAME,
                section_name=section_name,
            )

            # Aplicar property modifiers si estan en el nombre de seccion
            column.apply_pm_from_section_name()

            columns[column_key] = column

        # Log para Claude
        claude_logger.log_elements_created("Columns", len(columns))

        # Registrar columnas sin seccion como errores
        if skipped_columns:
            logger.warning(f"Column parser: {len(skipped_columns)} columnas sin seccion definida (no creadas)")
            for col in skipped_columns[:20]:
                claude_logger.log_parsing_warning(f"Columna sin seccion: {col}")
            if len(skipped_columns) > 20:
                claude_logger.log_parsing_warning(f"... y {len(skipped_columns) - 20} columnas mas sin seccion")

        return columns, column_forces, stories
