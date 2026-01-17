# app/services/parsing/drop_beam_parser.py
"""
Parser para vigas capitel desde archivos Excel de ETABS.

Las vigas capitel son losas diseñadas como vigas a flexocompresión.
Extrae datos de la tabla "Section Cut Forces - Analysis".
Formato esperado del nombre del corte:
"Scut Losa S02-29x150 eje CL - Eje C3"
"""
import re
import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd

from ...domain.entities import (
    HorizontalElement,
    HorizontalElementSource,
    ElementForces,
    ElementForceType,
)
from ...domain.entities.reinforcement import BeamReinforcement
from ...domain.entities.section_cut import SectionCutInfo
from ...domain.entities.element_forces import COMBO_COLUMNS
from ...domain.constants.reinforcement import FY_DEFAULT_MPA
from .table_extractor import normalize_columns

logger = logging.getLogger(__name__)


class DropBeamParser:
    """
    Parser para vigas capitel de ETABS.

    Extrae vigas capitel desde Section Cut Forces - Analysis.
    El nombre del corte contiene la geometría de la sección.

    Nota: Crea instancias de HorizontalElement con source=DROP_BEAM.
    """

    # Patrones regex para extraer datos del nombre del corte
    # Formato 1: "Scut Losa S02-29x150 eje CL - Eje C3" (formato antiguo)
    # Formato 2: "SCut-Losa S01-29x100 Borde losa-2" (formato del script e2k)
    SECTION_CUT_PATTERN_OLD = re.compile(
        r'Scut\s+Losa\s+'           # Prefijo con espacio
        r'(\w+)-'                    # Story (S02, etc.)
        r'(\d+)x(\d+)\s+'           # Espesor x Ancho en cm
        r'eje\s+(\w+)\s*'           # Eje de la losa (CL, etc.)
        r'-\s*'                      # Separador
        r'(?:Eje\s+)?'              # "Eje " opcional
        r'(\w+)',                    # Ubicación (C3, etc.)
        re.IGNORECASE
    )

    # Formato nuevo: "SCut-Losa S01-29x100 Borde losa-2"
    SECTION_CUT_PATTERN_NEW = re.compile(
        r'SCut-Losa\s+'             # Prefijo con guión
        r'(\w+)-'                    # Story (S01, etc.)
        r'(\d+)x(\d+)\s+'           # Espesor x Ancho en cm
        r'(.+)',                     # Resto es la ubicación (Borde losa-2, etc.)
        re.IGNORECASE
    )

    def __init__(self):
        """Inicializa el parser."""
        self._default_fc = 28.0  # MPa
        self._default_length = 5000.0  # mm (5m luz libre por defecto)

    def parse_drop_beams(
        self,
        section_cut_df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, HorizontalElement], Dict[str, ElementForces], List[str]]:
        """
        Parsea vigas capitel desde Section Cut Forces - Analysis.

        OPTIMIZADO: Usa operaciones vectorizadas y set_combinations_from_df.

        Args:
            section_cut_df: DataFrame con datos de Section Cut Forces
            materials: Diccionario de materiales {nombre: fc}

        Returns:
            Tupla (drop_beams, drop_beam_forces, stories)
            drop_beams contiene HorizontalElement con source=DROP_BEAM
        """
        drop_beams: Dict[str, HorizontalElement] = {}
        drop_beam_forces: Dict[str, ElementForces] = {}
        stories: List[str] = []
        section_cut_cache: Dict[str, SectionCutInfo] = {}

        if section_cut_df is None or section_cut_df.empty:
            return drop_beams, drop_beam_forces, stories

        # Normalizar columnas
        df = normalize_columns(section_cut_df)

        # Filtrar filas válidas
        df = df[df['sectioncut'].notna() & (df['sectioncut'].astype(str) != 'nan')].copy()

        if len(df) == 0:
            return drop_beams, drop_beam_forces, stories

        # Parsear nombres de section cut y obtener element_key para cada fila
        def get_element_key(name: str) -> str:
            if name not in section_cut_cache:
                sc = self._parse_section_cut_name(name)
                if sc:
                    section_cut_cache[name] = sc
                    return sc.element_key
                return ''
            return section_cut_cache[name].element_key

        df['_element_key'] = df['sectioncut'].astype(str).apply(get_element_key)

        # Filtrar filas con element_key válido
        df = df[df['_element_key'] != '']

        if len(df) == 0:
            return drop_beams, drop_beam_forces, stories

        # OPTIMIZADO: Preparar columnas para combinaciones
        # Mapear columnas de Analysis a LoadCombination
        # F1 -> P, F2 -> V3, F3 -> V2, M1 -> T, M2 -> M3, M3 -> M2
        for col in ['f1', 'f2', 'f3', 'm1', 'm2', 'm3']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0

        if 'output case' in df.columns:
            df['_output_case'] = df['output case'].astype(str).fillna('')
        else:
            df['_output_case'] = ''

        if 'step type' in df.columns:
            df['_step_type'] = df['step type'].astype(str).replace('nan', '').fillna('')
        else:
            df['_step_type'] = ''

        # Crear DataFrame de combinaciones con mapeo correcto de columnas
        df_combos = pd.DataFrame({
            'element_key': df['_element_key'],
            'name': df['_output_case'],
            'location': 'Section Cut',
            'step_type': df['_step_type'],
            'P': df['f1'],
            'V2': df['f3'],   # F3 -> V2
            'V3': df['f2'],   # F2 -> V3
            'T': df['m1'],
            'M2': df['m3'],   # M3 -> M2
            'M3': df['m2']    # M2 -> M3
        })

        # Agrupar por element_key
        grouped = df_combos.groupby('element_key')

        for element_key, group in grouped:
            if len(group) == 0:
                continue

            # Obtener SectionCutInfo del cache (ya parseado)
            scut_name = df[df['_element_key'] == element_key]['sectioncut'].iloc[0]
            section_cut = section_cut_cache.get(scut_name)
            if section_cut is None:
                continue

            # Crear ElementForces usando set_combinations_from_df
            forces = ElementForces(
                label=section_cut.display_name,
                story=section_cut.story,
                element_type=ElementForceType.DROP_BEAM,
                section_cut=section_cut
            )
            forces.set_combinations_from_df(group[COMBO_COLUMNS])
            drop_beam_forces[element_key] = forces

            # Agregar story a la lista
            if section_cut.story not in stories:
                stories.append(section_cut.story)

        # Crear entidades HorizontalElement con source=DROP_BEAM
        for key, forces in drop_beam_forces.items():
            sc = forces.section_cut
            label = f"{sc.axis_slab} - {sc.location}"

            # Crear BeamReinforcement con valores por defecto para vigas capitel
            discrete_reinforcement = BeamReinforcement(
                n_bars_top=4,
                n_bars_bottom=4,
                diameter_top=16,
                diameter_bottom=16,
            )

            drop_beams[key] = HorizontalElement(
                label=label,
                story=sc.story,
                # Para DROP_BEAM:
                # - depth = thickness (espesor de losa, dimensión menor)
                # - width = width (ancho tributario, dimensión mayor)
                length=self._default_length,
                depth=sc.thickness_mm,   # Espesor de losa
                width=sc.width_mm,       # Ancho tributario
                fc=self._default_fc,
                fy=FY_DEFAULT_MPA,
                source=HorizontalElementSource.DROP_BEAM,
                discrete_reinforcement=discrete_reinforcement,
                cover=25.0,  # Cover típico para losas
                axis_slab=sc.axis_slab,
                location=sc.location,
            )

        return drop_beams, drop_beam_forces, stories

    def _parse_section_cut_name(self, name: str) -> Optional[SectionCutInfo]:
        """
        Extrae datos del nombre del corte de sección.

        Formatos soportados:
        - "Scut Losa S02-29x150 eje CL - Eje C3" (formato antiguo)
        - "SCut-Losa S01-29x100 Borde losa-2" (formato del script e2k)

        Returns:
            SectionCutInfo o None si no es un corte válido
        """
        if not name or 'nan' in name.lower():
            return None

        # Verificar si es un corte de losa (con espacio o guión)
        name_lower = name.lower()
        if 'scut losa' not in name_lower and 'scut-losa' not in name_lower:
            return None

        # Intentar formato antiguo primero
        match = self.SECTION_CUT_PATTERN_OLD.match(name.strip())
        if match:
            story, thickness_cm, width_cm, axis_slab, location = match.groups()
            return SectionCutInfo(
                name=name,
                story=story.upper(),
                thickness_mm=float(thickness_cm) * 10,  # cm -> mm
                width_mm=float(width_cm) * 10,          # cm -> mm
                axis_slab=axis_slab.upper(),
                location=location.upper()
            )

        # Intentar formato nuevo (del script e2k)
        match = self.SECTION_CUT_PATTERN_NEW.match(name.strip())
        if match:
            story, thickness_cm, width_cm, location = match.groups()
            # En formato nuevo, no hay eje explícito, usamos la ubicación completa
            return SectionCutInfo(
                name=name,
                story=story.upper(),
                thickness_mm=float(thickness_cm) * 10,  # cm -> mm
                width_mm=float(width_cm) * 10,          # cm -> mm
                axis_slab='',  # No hay eje en formato nuevo
                location=location.strip()
            )

        return None

    def set_default_fc(self, fc: float):
        """Establece el f'c por defecto para las vigas capitel."""
        self._default_fc = fc

    def set_default_length(self, length_mm: float):
        """Establece la luz libre por defecto para las vigas capitel."""
        self._default_length = length_mm
