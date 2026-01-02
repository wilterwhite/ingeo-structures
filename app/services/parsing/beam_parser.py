# app/services/parsing/beam_parser.py
"""
Parser para vigas desde archivos Excel de ETABS.

Soporta dos tipos de vigas:
1. Frame beams: Element Forces - Beams + Frame Section Definitions
2. Spandrels: Spandrel Section Properties + Spandrel Forces
"""
from typing import Dict, List, Tuple
import pandas as pd

from ...domain.entities.beam import Beam, BeamSource
from ...domain.entities.beam_forces import BeamForces
from ...domain.entities.load_combination import LoadCombination
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
        beam_forces_df: pd.DataFrame,
        spandrel_props_df: pd.DataFrame,
        spandrel_forces_df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, Beam], Dict[str, BeamForces], List[str]]:
        """
        Parsea vigas de ambas fuentes (frame y spandrel).

        Args:
            section_df: Frame Section Property Definitions
            beam_forces_df: Element Forces - Beams
            spandrel_props_df: Spandrel Section Properties
            spandrel_forces_df: Spandrel Forces
            materials: Diccionario de materiales

        Returns:
            Tupla (beams, beam_forces, stories)
        """
        beams: Dict[str, Beam] = {}
        beam_forces: Dict[str, BeamForces] = {}
        stories: List[str] = []

        # 1. Parsear frame beams
        section_defs = self._parse_section_definitions(section_df, materials)
        frame_beams, frame_forces, frame_stories = self._parse_frame_beams(
            beam_forces_df, section_defs, materials
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
        Parsea las definiciones de secciones de vigas (frame).
        """
        sections = {}

        if df is None:
            return sections

        df = normalize_columns(df)

        for _, row in df.iterrows():
            name = str(row.get('name', ''))
            design_type = str(row.get('design type', '')).lower()

            # Solo procesar vigas
            if 'beam' not in design_type:
                continue

            if not name or name == 'nan':
                continue

            # Geometria (m -> mm)
            depth = float(row.get('depth', 0)) * 1000  # altura
            width = float(row.get('width', 0)) * 1000  # ancho

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

    def _parse_frame_beams(
        self,
        df: pd.DataFrame,
        section_defs: Dict[str, dict],
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, Beam], Dict[str, BeamForces], List[str]]:
        """
        Parsea vigas tipo frame.
        """
        beams: Dict[str, Beam] = {}
        beam_forces: Dict[str, BeamForces] = {}
        stories: List[str] = []
        beam_lengths: Dict[str, Tuple[float, float]] = {}  # min, max station

        if df is None:
            return beams, beam_forces, stories

        df = normalize_columns(df)

        for _, row in df.iterrows():
            story = str(row.get('story', ''))
            beam_label = str(row.get('beam', ''))

            if not beam_label or beam_label == 'nan':
                continue

            beam_key = f"{story}_{beam_label}"

            # Tracking de stations para calcular longitud
            try:
                station = float(row.get('station', 0))
            except (ValueError, TypeError):
                station = 0

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
            except (ValueError, TypeError):
                continue

            if story not in stories:
                stories.append(story)

        # Crear vigas con longitud calculada
        for beam_key, forces in beam_forces.items():
            story, beam_label = beam_key.split('_', 1)

            # Buscar seccion de viga
            section = None
            for sec_name, sec_props in section_defs.items():
                section = sec_props
                break

            if section is None:
                section = {'depth': 600, 'width': 300, 'fc': 28}

            # Calcular longitud desde stations
            if beam_key in beam_lengths:
                min_s, max_s = beam_lengths[beam_key]
                length = (max_s - min_s) * 1000  # m -> mm
                if length < 100:
                    length = 5000  # 5m por defecto
            else:
                length = 5000

            forces.length = length

            beams[beam_key] = Beam(
                label=beam_label,
                story=story,
                length=length,
                depth=section['depth'],
                width=section['width'],
                fc=section['fc'],
                fy=420.0,
                source=BeamSource.FRAME
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
                except (ValueError, TypeError):
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
                fy=420.0,
                source=BeamSource.SPANDREL
            )

            if story not in stories:
                stories.append(story)

        return beams, beam_forces, stories

    def _clean_step_type(self, value) -> str:
        """Limpia el step_type de valores nan."""
        step_type = str(value) if value else ''
        return '' if step_type == 'nan' else step_type
