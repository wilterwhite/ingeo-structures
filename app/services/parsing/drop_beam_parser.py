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
from ...domain.entities.load_combination import LoadCombination
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

        if section_cut_df is None or section_cut_df.empty:
            return drop_beams, drop_beam_forces, stories

        # Normalizar columnas
        df = normalize_columns(section_cut_df)

        # Agrupar combinaciones por corte de sección
        for _, row in df.iterrows():
            # Obtener nombre del corte
            section_cut_name = str(row.get('sectioncut', ''))

            # Intentar extraer datos del nombre
            section_cut = self._parse_section_cut_name(section_cut_name)
            if section_cut is None:
                continue

            drop_beam_key = section_cut.element_key

            # Crear ElementForces si no existe
            if drop_beam_key not in drop_beam_forces:
                drop_beam_forces[drop_beam_key] = ElementForces(
                    label=section_cut.display_name,
                    story=section_cut.story,
                    element_type=ElementForceType.DROP_BEAM,
                    section_cut=section_cut,
                    combinations=[]
                )

            # Parsear combinación de carga
            combo = self._parse_combination(row)
            if combo is not None:
                drop_beam_forces[drop_beam_key].combinations.append(combo)

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

    def _parse_combination(self, row: pd.Series) -> Optional[LoadCombination]:
        """
        Parsea una combinación de carga desde una fila.

        Las columnas de Section Cut Forces - Analysis son:
        - F1, F2, F3: Fuerzas en ejes globales (tonf)
        - M1, M2, M3: Momentos en ejes globales (tonf-m)

        Se mapean a P, V2, V3, T, M2, M3 para compatibilidad con LoadCombination.
        """
        try:
            combo_name = str(row.get('output case', ''))
            if not combo_name or combo_name == 'nan':
                return None

            case_type = str(row.get('case type', ''))
            if case_type == 'nan':
                case_type = ''

            step_type = str(row.get('step type', ''))
            if step_type == 'nan':
                step_type = ''

            # Mapear columnas de Analysis a LoadCombination
            # F1 -> P (axial)
            # F2 -> V3 (cortante en dir 2)
            # F3 -> V2 (cortante en dir 3)
            # M1 -> T (torsión)
            # M2 -> M3
            # M3 -> M2
            return LoadCombination(
                name=combo_name,
                location='Section Cut',
                step_type=step_type,
                P=float(row.get('f1', 0)),
                V2=float(row.get('f3', 0)),   # F3 -> V2
                V3=float(row.get('f2', 0)),   # F2 -> V3
                T=float(row.get('m1', 0)),
                M2=float(row.get('m3', 0)),   # M3 -> M2
                M3=float(row.get('m2', 0))    # M2 -> M3
            )

        except (ValueError, TypeError) as e:
            logger.warning("Combinación inválida para drop_beam '%s', omitiendo: %s", combo_name, e)
            return None

    def set_default_fc(self, fc: float):
        """Establece el f'c por defecto para las vigas capitel."""
        self._default_fc = fc

    def set_default_length(self, length_mm: float):
        """Establece la luz libre por defecto para las vigas capitel."""
        self._default_length = length_mm
