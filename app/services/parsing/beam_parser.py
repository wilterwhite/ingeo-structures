# app/services/parsing/beam_parser.py
"""
Parser para vigas desde archivos Excel de ETABS.

Soporta dos tipos de vigas:
1. Frame beams: Element Forces - Beams + Frame Section Definitions
2. Spandrels: Spandrel Section Properties + Spandrel Forces
"""
from typing import Dict, List, Tuple
import logging
import pandas as pd

from ...domain.entities.beam import Beam, BeamSource, BeamShape

logger = logging.getLogger(__name__)
from ...domain.entities.beam_forces import BeamForces
from ...domain.entities.load_combination import LoadCombination
from ...domain.constants.reinforcement import FY_DEFAULT_MPA
from .material_mapper import parse_material_to_fc
from .table_extractor import normalize_columns


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
    ) -> Tuple[Dict[str, Beam], Dict[str, BeamForces], List[str]]:
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
        """
        beams: Dict[str, Beam] = {}
        beam_forces: Dict[str, BeamForces] = {}
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
        """
        sections = {}

        if df is None:
            return sections

        df = normalize_columns(df)

        for _, row in df.iterrows():
            name = str(row.get('name', ''))

            if not name or name == 'nan':
                continue

            # Geometria (m -> mm)
            try:
                depth = float(row.get('depth', 0)) * 1000  # altura
                width = float(row.get('width', 0)) * 1000  # ancho
            except (ValueError, TypeError) as e:
                logger.warning("Sección '%s' con geometría inválida, omitiendo: %s", name, e)
                continue

            if depth <= 0 or width <= 0:
                continue

            # Material
            material_name = str(row.get('material', '4000Psi'))
            fc = materials.get(material_name, parse_material_to_fc(material_name))

            sections[name] = {
                'depth': depth,
                'width': width,
                'fc': fc,
                'material': material_name,
                'shape': BeamShape.RECTANGULAR
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
        """
        sections = {}

        if df is None:
            return sections

        df = normalize_columns(df)

        for _, row in df.iterrows():
            name = str(row.get('name', ''))

            if not name or name == 'nan':
                continue

            # Geometria circular (m -> mm)
            # La columna puede ser 'diameter' o 't3' según la versión de ETABS
            try:
                diameter = float(row.get('diameter', 0) or row.get('t3', 0)) * 1000
            except (ValueError, TypeError) as e:
                logger.warning("Sección circular '%s' con diámetro inválido, omitiendo: %s", name, e)
                continue

            if diameter <= 0:
                continue

            # Material
            material_name = str(row.get('material', '4000Psi'))
            fc = materials.get(material_name, parse_material_to_fc(material_name))

            # Para secciones circulares, depth = width = diameter
            sections[name] = {
                'depth': diameter,
                'width': diameter,
                'fc': fc,
                'material': material_name,
                'shape': BeamShape.CIRCULAR
            }

        return sections

    def _parse_section_assignments(
        self,
        df: pd.DataFrame
    ) -> Tuple[Dict[str, str], set]:
        """
        Parsea las asignaciones de secciones a elementos (Frame Assignments).

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

        for _, row in df.iterrows():
            story = str(row.get('story', ''))
            label = str(row.get('label', ''))
            section_prop = str(row.get('section property', '') or
                               row.get('analytic section', '') or '')
            shape = str(row.get('shape', '')).lower()

            if not story or story == 'nan' or not label or label == 'nan':
                continue

            key = f"{story}_{label}"

            # Solo incluir elementos de hormigón (rectangular o circular)
            if 'concrete' in shape:
                concrete_beams.add(key)

            if section_prop and section_prop != 'nan':
                assigns[key] = section_prop

        return assigns, concrete_beams

    def _parse_frame_beams(
        self,
        df: pd.DataFrame,
        section_defs: Dict[str, dict],
        section_assigns: Dict[str, str],
        concrete_beams: set,
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, Beam], Dict[str, BeamForces], List[str]]:
        """
        Parsea vigas tipo frame (solo hormigón).
        """
        beams: Dict[str, Beam] = {}
        beam_forces: Dict[str, BeamForces] = {}
        stories: List[str] = []
        beam_lengths: Dict[str, Tuple[float, float]] = {}  # min, max station
        beam_sections: Dict[str, str] = {}  # beam_key -> section_name

        if df is None:
            return beams, beam_forces, stories

        df = normalize_columns(df)

        for _, row in df.iterrows():
            story = str(row.get('story', ''))
            beam_label = str(row.get('beam', ''))

            if not beam_label or beam_label == 'nan':
                continue

            beam_key = f"{story}_{beam_label}"

            # Filtrar vigas que no son de hormigón (si tenemos info de asignaciones)
            if concrete_beams and beam_key not in concrete_beams:
                continue

            # Capturar nombre de sección (puede estar en varias columnas)
            section_name = str(row.get('section', '') or
                               row.get('analytic section', '') or
                               row.get('section property', '') or '')
            if section_name and section_name != 'nan' and beam_key not in beam_sections:
                beam_sections[beam_key] = section_name

            # Tracking de stations para calcular longitud
            try:
                station = float(row.get('station', 0))
            except (ValueError, TypeError) as e:
                logger.warning("Station inválida para viga '%s', usando 0: %s", beam_key, e)
                station = 0  # Station 0 es válido como fallback

            if beam_key not in beam_lengths:
                beam_lengths[beam_key] = (station, station)
            else:
                min_s, max_s = beam_lengths[beam_key]
                beam_lengths[beam_key] = (min(min_s, station), max(max_s, station))

            # Crear BeamForces si no existe
            if beam_key not in beam_forces:
                beam_forces[beam_key] = BeamForces(
                    beam_label=beam_label,
                    story=story,
                    combinations=[]
                )

            # Location basado en station relativa
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
                beam_forces[beam_key].combinations.append(combo)
            except (ValueError, TypeError) as e:
                logger.warning("Combinación inválida para viga '%s', omitiendo: %s", beam_key, e)
                continue

            if story not in stories:
                stories.append(story)

        # Crear vigas con longitud calculada
        for beam_key, forces in beam_forces.items():
            story, beam_label = beam_key.split('_', 1)

            # Buscar sección específica de esta viga
            section = None
            section_name = None

            # 1. Primero intentar desde tabla de asignaciones
            if beam_key in section_assigns:
                section_name = section_assigns[beam_key]
                if section_name in section_defs:
                    section = section_defs[section_name]

            # 2. Fallback: desde datos de Element Forces - Beams
            if section is None and beam_key in beam_sections:
                section_name = beam_sections[beam_key]
                if section_name in section_defs:
                    section = section_defs[section_name]

            # 3. Fallback: matchear por nombre
            if section is None:
                for sec_name, sec_props in section_defs.items():
                    if beam_label in sec_name or sec_name in beam_label:
                        section = sec_props
                        section_name = sec_name
                        break

            if section is None:
                section = {
                    'depth': 600,
                    'width': 300,
                    'fc': 28,
                    'shape': BeamShape.RECTANGULAR
                }
                section_name = 'Default'

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
            beam_shape = section.get('shape', BeamShape.RECTANGULAR)

            beams[beam_key] = Beam(
                label=beam_label,
                story=story,
                length=length,
                depth=section['depth'],
                width=section['width'],
                shape=beam_shape,
                fc=section['fc'],
                fy=FY_DEFAULT_MPA,
                source=BeamSource.FRAME,
                section_name=section_name
            )

        return beams, beam_forces, stories

    def _parse_spandrels(
        self,
        props_df: pd.DataFrame,
        forces_df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, Beam], Dict[str, BeamForces], List[str]]:
        """
        Parsea spandrels (vigas de acople tipo shell).
        """
        beams: Dict[str, Beam] = {}
        beam_forces: Dict[str, BeamForces] = {}
        stories: List[str] = []
        spandrel_props: Dict[str, dict] = {}

        # 1. Parsear propiedades de spandrels
        if props_df is not None:
            props_df = normalize_columns(props_df)

            for _, row in props_df.iterrows():
                story = str(row.get('story', ''))
                spandrel_label = str(row.get('spandrel', ''))

                if not spandrel_label or spandrel_label == 'nan':
                    continue

                spandrel_key = f"{story}_{spandrel_label}"

                # Geometria (m -> mm)
                length = float(row.get('length', 0)) * 1000
                depth_left = float(row.get('depth left', 0)) * 1000
                depth_right = float(row.get('depth right', 0)) * 1000
                depth = (depth_left + depth_right) / 2

                thickness_left = float(row.get('thickness left', 0)) * 1000
                thickness_right = float(row.get('thickness right', 0)) * 1000
                width = (thickness_left + thickness_right) / 2

                # Material
                material_name = str(row.get('material', '4000Psi'))
                fc = materials.get(material_name, parse_material_to_fc(material_name))

                spandrel_props[spandrel_key] = {
                    'length': length,
                    'depth': depth,
                    'width': width,
                    'fc': fc
                }

                if story not in stories:
                    stories.append(story)

        # 2. Parsear fuerzas de spandrels
        if forces_df is not None:
            forces_df = normalize_columns(forces_df)

            for _, row in forces_df.iterrows():
                story = str(row.get('story', ''))
                spandrel_label = str(row.get('spandrel', ''))

                if not spandrel_label or spandrel_label == 'nan':
                    continue

                spandrel_key = f"{story}_{spandrel_label}"

                if spandrel_key not in beam_forces:
                    beam_forces[spandrel_key] = BeamForces(
                        beam_label=spandrel_label,
                        story=story,
                        combinations=[]
                    )

                location = str(row.get('location', 'Middle'))
                if location == 'nan':
                    location = 'Middle'

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
                    beam_forces[spandrel_key].combinations.append(combo)
                except (ValueError, TypeError) as e:
                    logger.warning("Combinación inválida para spandrel '%s', omitiendo: %s", spandrel_key, e)
                    continue

        # 3. Crear vigas spandrel
        for spandrel_key in set(spandrel_props.keys()) | set(beam_forces.keys()):
            if spandrel_key not in spandrel_props:
                continue

            props = spandrel_props[spandrel_key]
            story, spandrel_label = spandrel_key.split('_', 1)

            if spandrel_key in beam_forces:
                beam_forces[spandrel_key].length = props['length']

            beams[spandrel_key] = Beam(
                label=spandrel_label,
                story=story,
                length=props['length'],
                depth=props['depth'],
                width=props['width'],
                fc=props['fc'],
                fy=FY_DEFAULT_MPA,
                source=BeamSource.SPANDREL
            )

            if story not in stories:
                stories.append(story)

        return beams, beam_forces, stories

    def _clean_step_type(self, value) -> str:
        """Limpia el step_type de valores nan."""
        step_type = str(value) if value else ''
        return '' if step_type == 'nan' else step_type
