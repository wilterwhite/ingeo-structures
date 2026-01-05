# app/services/parsing/slab_parser.py
"""
Parser para losas desde archivos Excel de ETABS.

Extrae datos de la tabla "Section Cut Forces - Analysis".
Formato esperado del nombre del corte:
"Scut Losa S02-29x150 eje CL - Eje C3"
"""
import re
from typing import Dict, List, Tuple, Optional
import pandas as pd

from ...domain.entities.slab import Slab, SlabType, SupportCondition
from ...domain.entities.slab_forces import SlabForces, SlabSectionCut
from ...domain.entities.load_combination import LoadCombination
from ...domain.constants.reinforcement import FY_DEFAULT_MPA
from .table_extractor import normalize_columns


class SlabParser:
    """
    Parser para losas de ETABS.

    Extrae losas desde Section Cut Forces - Analysis.
    El nombre del corte contiene la geometria de la losa.
    """

    # Patron regex para extraer datos del nombre del corte
    # Formato: "Scut Losa S02-29x150 eje CL - Eje C3"
    # o variantes como: "Scut Losa S02-29x150 eje CL - C3"
    SLAB_PATTERN = re.compile(
        r'Scut\s+Losa\s+'           # Prefijo fijo
        r'(\w+)-'                    # Story (S02, etc.)
        r'(\d+)x(\d+)\s+'           # Espesor x Ancho en cm
        r'eje\s+(\w+)\s*'           # Eje de la losa (CL, etc.)
        r'-\s*'                      # Separador
        r'(?:Eje\s+)?'              # "Eje " opcional
        r'(\w+)',                    # Ubicacion (C3, etc.)
        re.IGNORECASE
    )

    def __init__(self):
        """Inicializa el parser."""
        self._default_fc = 28.0  # MPa
        self._default_span = 5000.0  # mm (5m por defecto)

    def parse_slabs(
        self,
        section_cut_df: pd.DataFrame,
        materials: Dict[str, float]
    ) -> Tuple[Dict[str, Slab], Dict[str, SlabForces], List[str]]:
        """
        Parsea losas desde Section Cut Forces - Analysis.

        Args:
            section_cut_df: DataFrame con datos de Section Cut Forces
            materials: Diccionario de materiales {nombre: fc}

        Returns:
            Tupla (slabs, slab_forces, stories)
        """
        slabs: Dict[str, Slab] = {}
        slab_forces: Dict[str, SlabForces] = {}
        stories: List[str] = []

        if section_cut_df is None or section_cut_df.empty:
            return slabs, slab_forces, stories

        # Normalizar columnas
        df = normalize_columns(section_cut_df)

        # Agrupar combinaciones por corte de seccion
        for _, row in df.iterrows():
            # Obtener nombre del corte
            section_cut_name = str(row.get('sectioncut', ''))

            # Intentar extraer datos del nombre
            section_cut = self._parse_section_cut_name(section_cut_name)
            if section_cut is None:
                continue

            slab_key = section_cut.slab_key

            # Crear SlabForces si no existe
            if slab_key not in slab_forces:
                slab_forces[slab_key] = SlabForces(
                    slab_label=section_cut.display_name,
                    story=section_cut.story,
                    section_cut=section_cut,
                    combinations=[]
                )

            # Parsear combinacion de carga
            combo = self._parse_combination(row)
            if combo is not None:
                slab_forces[slab_key].combinations.append(combo)

            # Agregar story a la lista
            if section_cut.story not in stories:
                stories.append(section_cut.story)

        # Crear entidades Slab
        for slab_key, forces in slab_forces.items():
            sc = forces.section_cut
            slabs[slab_key] = Slab(
                label=forces.slab_label,
                story=sc.story,
                slab_type=SlabType.ONE_WAY,  # Por defecto, el usuario puede cambiar
                thickness=sc.thickness_mm,
                width=sc.width_mm,
                span_length=self._default_span,
                axis_slab=sc.axis_slab,
                location=sc.location,
                fc=self._default_fc,
                fy=FY_DEFAULT_MPA,
                support_condition=SupportCondition.ONE_END_CONTINUOUS
            )

        return slabs, slab_forces, stories

    def _parse_section_cut_name(self, name: str) -> Optional[SlabSectionCut]:
        """
        Extrae datos del nombre del corte de seccion.

        Formato esperado: "Scut Losa S02-29x150 eje CL - Eje C3"

        Returns:
            SlabSectionCut o None si no es un corte de losa valido
        """
        if not name or 'nan' in name.lower():
            return None

        # Verificar si es un corte de losa
        if 'scut losa' not in name.lower():
            return None

        match = self.SLAB_PATTERN.match(name.strip())
        if not match:
            # Log para debug
            return None

        story, thickness_cm, width_cm, axis_slab, location = match.groups()

        return SlabSectionCut(
            name=name,
            story=story.upper(),
            thickness_mm=float(thickness_cm) * 10,  # cm -> mm
            width_mm=float(width_cm) * 10,          # cm -> mm
            axis_slab=axis_slab.upper(),
            location=location.upper()
        )

    def _parse_combination(self, row: pd.Series) -> Optional[LoadCombination]:
        """
        Parsea una combinacion de carga desde una fila.

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
            # M1 -> T (torsion)
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
            return None

    def set_default_fc(self, fc: float):
        """Establece el f'c por defecto para las losas."""
        self._default_fc = fc

    def set_default_span(self, span_mm: float):
        """Establece la luz por defecto para las losas."""
        self._default_span = span_mm
