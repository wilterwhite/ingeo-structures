# app/services/parsing/beam_parser.py
"""
Parser para vigas desde archivos Excel de ETABS.

Soporta dos tipos de vigas:
1. Frame beams: Element Forces - Beams + Frame Section Definitions
2. Spandrels: Spandrel Section Properties + Spandrel Forces

OPTIMIZADO: Usa operaciones vectorizadas de pandas en lugar de iterrows()
para procesar tablas grandes (240k+ filas) eficientemente.
"""
from typing import Dict, List, Tuple
import logging
import os
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from ...domain.entities import (
    HorizontalElement,
    HorizontalElementSource,
    HorizontalElementShape,
    ElementForces,
    ElementForceType,
)
from ...domain.entities.element_forces import COMBO_COLUMNS
from ...domain.constants.reinforcement import FY_DEFAULT_MPA
from .material_mapper import parse_material_to_fc
from .table_extractor import normalize_columns, extract_units_from_df
from ..logging import claude_logger

logger = logging.getLogger(__name__)


class BeamParser:
    """
    Parser para vigas de ETABS.

    Extrae vigas desde:
    - Frame beams: Frame Sec Def + Element Forces - Beams
    - Spandrels: Spandrel Section Properties + Spandrel Forces
    """

    def parse_beams(
        self,
        section_df: pd.DataFrame,
        assigns_df: pd.DataFrame,
        beam_forces_df: pd.DataFrame,
        spandrel_props_df: pd.DataFrame,
        spandrel_forces_df: pd.DataFrame,
        materials: Dict[str, float],
        circular_section_df: pd.DataFrame = None
    ) -> Tuple[Dict[str, HorizontalElement], Dict[str, ElementForces], List[str]]:
        """
        Parsea vigas de ambas fuentes (frame y spandrel).

        Args:
            section_df: Frame Section Property Definitions - Concrete Rectangular
            assigns_df: Frame Assignments - Section Properties
            beam_forces_df: Element Forces - Beams
            spandrel_props_df: Spandrel Section Properties
            spandrel_forces_df: Spandrel Forces
            materials: Diccionario de materiales
            circular_section_df: Frame Section Property Definitions - Concrete Circle

        Returns:
            Tupla (beams, beam_forces, stories)
            donde beams son HorizontalElement
        """
        beams: Dict[str, HorizontalElement] = {}
        beam_forces: Dict[str, ElementForces] = {}
        stories: List[str] = []

        # 1. Parsear definiciones de secciones (rectangular y circular)
        section_defs = self._parse_section_definitions(section_df, materials)
        circular_defs = self._parse_circular_sections(circular_section_df, materials)
        section_defs.update(circular_defs)

        # 2. Parsear asignaciones
        section_assigns, concrete_beams = self._parse_section_assignments(assigns_df)

        # 2. Parsear frame beams (solo hormigón)
        frame_beams, frame_forces, frame_stories = self._parse_frame_beams(
            beam_forces_df, section_defs, section_assigns, concrete_beams, materials
        )
        beams.update(frame_beams)
        beam_forces.update(frame_forces)
        for s in frame_stories:
            if s not in stories:
                stories.append(s)

        # 2. Parsear spandrels
        spandrel_beams, spandrel_forces, spandrel_stories = self._parse_spandrels(
            spandrel_props_df, spandrel_forces_df, materials
        )
        beams.update(spandrel_beams)
        beam_forces.update(spandrel_forces)
        for s in spandrel_stories:
            if s not in stories:
                stories.append(s)

        return beams, beam_forces, stories

    def _parse_section_definitions(
        self,
        df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Dict[str, dict]:
        """
        Parsea las definiciones de secciones rectangulares de hormigón.
        Incluye todas las secciones (vigas, columnas) porque ETABS puede
        clasificarlas incorrectamente.

        OPTIMIZADO: Usa operaciones vectorizadas.
        """
        sections = {}

        if df is None:
            return sections

        df = normalize_columns(df)

        # Extraer factores de conversión de unidades de la primera fila
        units = extract_units_from_df(df)
        logger.info(f"Frame sections: Unidades detectadas - depth: {units.get('depth', 1.0)}, width: {units.get('width', 1.0)}")

        # Saltar la fila de unidades
        df = df.iloc[1:].copy()

        # Filtrar filas válidas (vectorizado)
        df = df[df['name'].notna() & (df['name'].astype(str) != 'nan')]

        if len(df) == 0:
            return sections

        # Convertir columnas numéricas (vectorizado)
        depth_factor = units.get('depth', 1.0)
        width_factor = units.get('width', 1.0)

        df['depth'] = pd.to_numeric(df['depth'], errors='coerce').fillna(0) * depth_factor
        df['width'] = pd.to_numeric(df['width'], errors='coerce').fillna(0) * width_factor

        # Filtrar geometría válida
        df = df[(df['depth'] > 0) & (df['width'] > 0)]

        # OPTIMIZADO: Usar to_dict('records') en lugar de iterrows
        df['_material'] = df.get('material', pd.Series(['4000Psi'] * len(df))).astype(str).fillna('4000Psi')
        records = df[['name', 'depth', 'width', '_material']].to_dict('records')

        for r in records:
            name = str(r['name'])
            material_name = r['_material']
            fc = materials.get(material_name, parse_material_to_fc(material_name))

            sections[name] = {
                'depth': float(r['depth']),
                'width': float(r['width']),
                'fc': fc,
                'material': material_name,
                'shape': HorizontalElementShape.RECTANGULAR
            }

        return sections

    def _parse_circular_sections(
        self,
        df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Dict[str, dict]:
        """
        Parsea las definiciones de secciones circulares de hormigón.
        Tabla: Frame Section Property Definitions - Concrete Circle

        OPTIMIZADO: Usa operaciones vectorizadas.
        """
        sections = {}

        if df is None:
            return sections

        df = normalize_columns(df)

        # Extraer factores de conversión de unidades de la primera fila
        units = extract_units_from_df(df)
        diameter_factor = units.get('diameter', units.get('t3', 1.0))
        logger.info(f"Circular sections: Unidades detectadas - diameter: {diameter_factor}")

        # Saltar la fila de unidades
        df = df.iloc[1:].copy()

        # Filtrar filas válidas (vectorizado)
        df = df[df['name'].notna() & (df['name'].astype(str) != 'nan')]

        if len(df) == 0:
            return sections

        # Calcular diámetro (puede estar en 'diameter' o 't3')
        if 'diameter' in df.columns:
            df['_diameter'] = pd.to_numeric(df['diameter'], errors='coerce').fillna(0)
        elif 't3' in df.columns:
            df['_diameter'] = pd.to_numeric(df['t3'], errors='coerce').fillna(0)
        else:
            return sections

        df['_diameter'] = df['_diameter'] * diameter_factor

        # Filtrar diámetros válidos
        df = df[df['_diameter'] > 0]

        # OPTIMIZADO: Usar to_dict('records') en lugar de iterrows
        df['_material'] = df.get('material', pd.Series(['4000Psi'] * len(df))).astype(str).fillna('4000Psi')
        records = df[['name', '_diameter', '_material']].to_dict('records')

        for r in records:
            name = str(r['name'])
            diameter = float(r['_diameter'])
            material_name = r['_material']
            fc = materials.get(material_name, parse_material_to_fc(material_name))

            sections[name] = {
                'depth': diameter,
                'width': diameter,
                'fc': fc,
                'material': material_name,
                'shape': HorizontalElementShape.CIRCULAR
            }

        return sections

    def _parse_section_assignments(
        self,
        df: pd.DataFrame
    ) -> Tuple[Dict[str, str], set]:
        """
        Parsea las asignaciones de secciones a elementos (Frame Assignments).

        OPTIMIZADO: Usa operaciones vectorizadas.

        Returns:
            Tuple of:
            - Dict mapping 'Story_Label' -> 'Section Property Name'
            - Set of beam_keys that are concrete (rectangular or circular)
        """
        assigns = {}
        concrete_beams = set()

        if df is None:
            return assigns, concrete_beams

        df = normalize_columns(df)

        # Filtrar filas válidas (vectorizado)
        df = df[
            df['story'].notna() & (df['story'].astype(str) != 'nan') &
            df['label'].notna() & (df['label'].astype(str) != 'nan')
        ].copy()

        if len(df) == 0:
            return assigns, concrete_beams

        # Crear keys vectorizado
        df['_key'] = df['story'].astype(str) + '_' + df['label'].astype(str)

        # Identificar concreto (vectorizado)
        if 'shape' in df.columns:
            concrete_mask = df['shape'].astype(str).str.lower().str.contains('concrete', na=False)
            concrete_beams = set(df.loc[concrete_mask, '_key'].tolist())

        # Obtener section property (puede estar en varias columnas)
        if 'section property' in df.columns:
            section_col = 'section property'
        elif 'analytic section' in df.columns:
            section_col = 'analytic section'
        else:
            return assigns, concrete_beams

        # Filtrar solo filas con section property válido
        valid_sections = df[
            df[section_col].notna() &
            (df[section_col].astype(str) != 'nan') &
            (df[section_col].astype(str) != '')
        ]

        # Crear diccionario vectorizado
        assigns = dict(zip(
            valid_sections['_key'],
            valid_sections[section_col].astype(str)
        ))

        return assigns, concrete_beams

    def _parse_frame_beams(
        self,
        df: pd.DataFrame,
        section_defs: Dict[str, dict],
        section_assigns: Dict[str, str],
        concrete_beams: set,
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, HorizontalElement], Dict[str, ElementForces], List[str]]:
        """
        Parsea vigas tipo frame (solo hormigón).

        OPTIMIZADO: Usa operaciones vectorizadas y groupby() para procesar
        240k+ filas eficientemente en lugar de iterrows().
        """
        beams: Dict[str, HorizontalElement] = {}
        beam_forces: Dict[str, ElementForces] = {}
        stories: List[str] = []

        if df is None or len(df) == 0:
            return beams, beam_forces, stories

        df = normalize_columns(df)

        # Filtrar filas válidas (vectorizado)
        df = df[df['beam'].notna() & (df['beam'].astype(str) != 'nan')].copy()

        if len(df) == 0:
            return beams, beam_forces, stories

        # Crear beam_key vectorizado
        df['beam_key'] = df['story'].astype(str) + '_' + df['beam'].astype(str)

        # Filtrar solo vigas de hormigón si tenemos info
        if concrete_beams:
            df = df[df['beam_key'].isin(concrete_beams)]

        if len(df) == 0:
            return beams, beam_forces, stories

        # Convertir columnas numéricas de una vez (vectorizado)
        numeric_cols = ['station', 'p', 'v2', 'v3', 't', 'm2', 'm3']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Calcular min/max station por viga (vectorizado con groupby)
        station_stats = df.groupby('beam_key')['station'].agg(['min', 'max'])
        beam_lengths = {
            key: (row['min'], row['max'])
            for key, row in station_stats.iterrows()
        }

        # Obtener stories únicos (vectorizado)
        stories = df['story'].astype(str).unique().tolist()

        # Capturar sección desde columnas de forces (primera ocurrencia por viga)
        beam_sections: Dict[str, str] = {}
        section_cols = ['section', 'analytic section', 'section property']
        for col in section_cols:
            if col in df.columns:
                # Obtener primera sección válida por beam_key
                valid_sections = df[df[col].notna() & (df[col].astype(str) != 'nan')]
                if len(valid_sections) > 0:
                    first_sections = valid_sections.groupby('beam_key')[col].first()
                    for key, val in first_sections.items():
                        if key not in beam_sections:
                            beam_sections[key] = str(val)

        # OPTIMIZADO: Preparar todas las columnas de una vez para evitar iloc repetidos
        if 'location' in df.columns:
            df['_location'] = df['location'].astype(str).replace('nan', 'Middle').fillna('Middle')
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
        df_combos = df[['beam_key', '_output_case', '_location', '_step_type', 'p', 'v2', 'v3', 't', 'm2', 'm3']].copy()
        df_combos.columns = ['beam_key', 'name', 'location', 'step_type', 'P', 'V2', 'V3', 'T', 'M2', 'M3']

        # AGRESIVO: Procesar grupos en PARALELO con todos los cores
        grouped = df_combos.groupby('beam_key')
        group_items = list(grouped)
        
        # Función worker para procesar un chunk de grupos
        def process_beam_chunk(chunk_items):
            chunk_forces = {}
            for beam_key, group in chunk_items:
                parts = beam_key.split('_', 1)
                if len(parts) != 2 or len(group) == 0:
                    continue
                story, beam_label = parts
                forces = ElementForces(
                    label=beam_label,
                    story=story,
                    element_type=ElementForceType.BEAM
                )
                forces.set_combinations_from_df(group[COMBO_COLUMNS])
                chunk_forces[beam_key] = forces
            return chunk_forces
        
        # Dividir en chunks y procesar en paralelo
        n_workers = min(os.cpu_count() or 8, len(group_items))
        if n_workers > 1 and len(group_items) > 100:
            chunk_size = max(1, len(group_items) // n_workers)
            chunks = [group_items[i:i+chunk_size] for i in range(0, len(group_items), chunk_size)]
            
            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                results = list(executor.map(process_beam_chunk, chunks))
                for chunk_result in results:
                    beam_forces.update(chunk_result)
        else:
            beam_forces = process_beam_chunk(group_items)

        # Crear vigas con longitud calculada
        skipped_beams = []
        for beam_key, forces in beam_forces.items():
            story, beam_label = beam_key.split('_', 1)

            # Buscar sección específica de esta viga
            section = None
            section_name = None

            # 1. Primero intentar desde tabla de asignaciones
            if beam_key in section_assigns:
                section_name = section_assigns[beam_key]
                section = section_defs.get(section_name)

            # 2. Desde datos de Element Forces - Beams
            if section is None and beam_key in beam_sections:
                section_name = beam_sections[beam_key]
                section = section_defs.get(section_name)

            # 3. Matchear por nombre
            if section is None:
                for sec_name, sec_props in section_defs.items():
                    if beam_label in sec_name or sec_name in beam_label:
                        section = sec_props
                        section_name = sec_name
                        break

            # Si no hay seccion, saltar esta viga
            if section is None:
                skipped_beams.append(f"{beam_label} ({story})")
                continue

            # Calcular longitud desde stations
            if beam_key in beam_lengths:
                min_s, max_s = beam_lengths[beam_key]
                length = (max_s - min_s) * 1000  # m -> mm
                if length < 100:
                    length = 5000  # 5m por defecto
            else:
                length = 5000

            forces.length = length

            # Shape de la sección (default: rectangular)
            beam_shape = section.get('shape', HorizontalElementShape.RECTANGULAR)

            # Validar geometría
            if length <= 0 or section['depth'] <= 0 or section['width'] <= 0:
                logger.warning(
                    f"Beam {beam_label}@{story}: geometría inválida "
                    f"(length={length}, depth={section['depth']}, width={section['width']})"
                )
                continue

            beam = HorizontalElement(
                label=beam_label,
                story=story,
                length=length,
                depth=section['depth'],
                width=section['width'],
                shape=beam_shape,
                fc=section['fc'],
                fy=FY_DEFAULT_MPA,
                source=HorizontalElementSource.FRAME,
                section_name=section_name
            )

            # Aplicar property modifiers si estan en el nombre de seccion
            beam.apply_pm_from_section_name()

            beams[beam_key] = beam

        # Log para Claude
        claude_logger.log_elements_created("Beams", len(beams))

        # Registrar vigas sin seccion como errores
        if skipped_beams:
            logger.warning(f"Beam parser: {len(skipped_beams)} vigas sin seccion definida (no creadas)")
            for beam in skipped_beams[:20]:
                claude_logger.log_parsing_warning(f"Viga sin seccion: {beam}")
            if len(skipped_beams) > 20:
                claude_logger.log_parsing_warning(f"... y {len(skipped_beams) - 20} vigas mas sin seccion")

        logger.info(f"Frame beams: {len(beams)} importadas OK")
        return beams, beam_forces, stories

    def _parse_spandrels(
        self,
        props_df: pd.DataFrame,
        forces_df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, HorizontalElement], Dict[str, ElementForces], List[str]]:
        """
        Parsea spandrels (vigas de acople tipo shell).

        OPTIMIZADO: Usa operaciones vectorizadas donde es posible.
        """
        beams: Dict[str, HorizontalElement] = {}
        beam_forces: Dict[str, ElementForces] = {}
        stories: List[str] = []
        spandrel_props: Dict[str, dict] = {}

        # 1. Parsear propiedades de spandrels (vectorizado)
        if props_df is not None and len(props_df) > 0:
            props_df = normalize_columns(props_df)

            # Extraer factores de conversión de unidades de la primera fila
            units = extract_units_from_df(props_df)
            logger.info(
                f"Spandrels: Unidades detectadas - length: {units.get('length', 1.0)}, "
                f"depth: {units.get('depth left', 1.0)}, thickness: {units.get('thickness left', 1.0)}"
            )

            # Saltar la fila de unidades
            props_df = props_df.iloc[1:].copy()

            # Filtrar filas válidas
            props_df = props_df[
                props_df['spandrel'].notna() &
                (props_df['spandrel'].astype(str) != 'nan')
            ]

            if len(props_df) > 0:
                # Crear key vectorizado
                props_df['_key'] = props_df['story'].astype(str) + '_' + props_df['spandrel'].astype(str)

                # Convertir columnas numéricas
                for col in ['length', 'depth left', 'depth right', 'thickness left', 'thickness right']:
                    if col in props_df.columns:
                        props_df[col] = pd.to_numeric(props_df[col], errors='coerce').fillna(0)

                # Aplicar factores de unidad
                props_df['length'] = props_df['length'] * units.get('length', 1.0)
                props_df['depth left'] = props_df.get('depth left', 0) * units.get('depth left', 1.0)
                props_df['depth right'] = props_df.get('depth right', 0) * units.get('depth right', 1.0)
                props_df['thickness left'] = props_df.get('thickness left', 0) * units.get('thickness left', 1.0)
                props_df['thickness right'] = props_df.get('thickness right', 0) * units.get('thickness right', 1.0)

                # OPTIMIZADO: Usar to_dict('records') en lugar de iterrows
                props_df['_material'] = props_df.get('material', pd.Series(['4000Psi'] * len(props_df))).astype(str).fillna('4000Psi')
                cols_needed = ['_key', 'length', 'depth left', 'depth right', 'thickness left', 'thickness right', '_material']
                # Asegurar que todas las columnas existan
                for col in cols_needed:
                    if col not in props_df.columns:
                        props_df[col] = 0 if col != '_material' else '4000Psi'
                records = props_df[cols_needed].to_dict('records')

                for r in records:
                    spandrel_key = r['_key']
                    depth = (float(r.get('depth left', 0)) + float(r.get('depth right', 0))) / 2
                    width = (float(r.get('thickness left', 0)) + float(r.get('thickness right', 0))) / 2
                    material_name = r['_material']
                    fc = materials.get(material_name, parse_material_to_fc(material_name))

                    spandrel_props[spandrel_key] = {
                        'length': float(r['length']),
                        'depth': depth,
                        'width': width,
                        'fc': fc
                    }

                stories = props_df['story'].astype(str).unique().tolist()

        # 2. Parsear fuerzas de spandrels (vectorizado con groupby)
        if forces_df is not None and len(forces_df) > 0:
            forces_df = normalize_columns(forces_df)

            # Filtrar filas válidas
            forces_df = forces_df[
                forces_df['spandrel'].notna() &
                (forces_df['spandrel'].astype(str) != 'nan')
            ].copy()

            if len(forces_df) > 0:
                # Crear key y convertir numericos
                forces_df['_key'] = forces_df['story'].astype(str) + '_' + forces_df['spandrel'].astype(str)

                for col in ['p', 'v2', 'v3', 't', 'm2', 'm3']:
                    if col in forces_df.columns:
                        forces_df[col] = pd.to_numeric(forces_df[col], errors='coerce').fillna(0)

                # OPTIMIZADO: Preparar columnas antes de agrupar
                if 'location' in forces_df.columns:
                    forces_df['_location'] = forces_df['location'].astype(str).replace('nan', 'Middle').fillna('Middle')
                else:
                    forces_df['_location'] = 'Middle'

                if 'output case' in forces_df.columns:
                    forces_df['_output_case'] = forces_df['output case'].astype(str).fillna('')
                else:
                    forces_df['_output_case'] = ''

                if 'step type' in forces_df.columns:
                    forces_df['_step_type'] = forces_df['step type'].astype(str).replace('nan', '').fillna('')
                else:
                    forces_df['_step_type'] = ''

                # OPTIMIZADO: Renombrar columnas para match con COMBO_COLUMNS
                df_combos = forces_df[['_key', '_output_case', '_location', '_step_type', 'p', 'v2', 'v3', 't', 'm2', 'm3']].copy()
                df_combos.columns = ['spandrel_key', 'name', 'location', 'step_type', 'P', 'V2', 'V3', 'T', 'M2', 'M3']

                # AGRESIVO: Procesar spandrels en paralelo
                grouped = df_combos.groupby('spandrel_key')
                group_items = list(grouped)
                
                def process_spandrel_chunk(chunk_items):
                    chunk_forces = {}
                    for spandrel_key, group in chunk_items:
                        parts = spandrel_key.split('_', 1)
                        if len(parts) != 2 or len(group) == 0:
                            continue
                        story, spandrel_label = parts
                        forces = ElementForces(
                            label=spandrel_label,
                            story=story,
                            element_type=ElementForceType.BEAM
                        )
                        forces.set_combinations_from_df(group[COMBO_COLUMNS])
                        chunk_forces[spandrel_key] = forces
                    return chunk_forces
                
                n_workers = min(os.cpu_count() or 8, len(group_items))
                if n_workers > 1 and len(group_items) > 20:
                    chunk_size = max(1, len(group_items) // n_workers)
                    chunks = [group_items[i:i+chunk_size] for i in range(0, len(group_items), chunk_size)]
                    with ThreadPoolExecutor(max_workers=n_workers) as executor:
                        results = list(executor.map(process_spandrel_chunk, chunks))
                        for chunk_result in results:
                            beam_forces.update(chunk_result)
                else:
                    beam_forces = process_spandrel_chunk(group_items)

        # 3. Crear vigas spandrel
        skipped_invalid = 0
        for spandrel_key in set(spandrel_props.keys()) | set(beam_forces.keys()):
            if spandrel_key not in spandrel_props:
                continue

            props = spandrel_props[spandrel_key]
            story, spandrel_label = spandrel_key.split('_', 1)

            # Validar geometría
            if props['length'] <= 0 or props['depth'] <= 0 or props['width'] <= 0:
                logger.warning(
                    f"Spandrel {spandrel_label}@{story}: geometría inválida "
                    f"(length={props['length']}, depth={props['depth']}, width={props['width']})"
                )
                skipped_invalid += 1
                continue

            if spandrel_key in beam_forces:
                beam_forces[spandrel_key].length = props['length']

            spandrel = HorizontalElement(
                label=spandrel_label,
                story=story,
                length=props['length'],
                depth=props['depth'],
                width=props['width'],
                fc=props['fc'],
                fy=FY_DEFAULT_MPA,
                source=HorizontalElementSource.SPANDREL,
                section_name=spandrel_label  # Usar label como nombre de seccion
            )

            # Aplicar property modifiers si estan en el nombre de seccion
            spandrel.apply_pm_from_section_name()

            beams[spandrel_key] = spandrel

            if story not in stories:
                stories.append(story)

        # Log para Claude
        claude_logger.log_elements_created("Spandrels", len(beams))
        if skipped_invalid > 0:
            claude_logger.log_parsing_warning(f"Spandrels: {skipped_invalid} con geometria invalida (omitidas)")

        logger.info(f"Spandrels: {len(beams)} importadas OK, {skipped_invalid} con geometría inválida")
        return beams, beam_forces, stories

