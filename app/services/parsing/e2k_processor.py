# app/services/parsing/e2k_processor.py
"""
Procesador de archivos E2K de ETABS.

Genera Section Cuts automáticamente para todos los grupos definidos en el archivo.
También genera secciones agrietadas con Property Modifiers aplicados.
"""
import re
from dataclasses import dataclass
from typing import List, Set, Tuple, Dict, Any


@dataclass
class E2KProcessResult:
    """Resultado del procesamiento de un archivo E2K."""
    content: str
    n_section_cuts: int
    n_groups: int


@dataclass
class E2KCrackedResult:
    """Resultado de la exportación E2K con secciones agrietadas."""
    content: str
    n_sections_modified: int
    n_elements_updated: int


class E2KProcessor:
    """
    Procesa archivos E2K de ETABS para generar Section Cuts automáticamente.

    Usage:
        processor = E2KProcessor()
        result = processor.process(file_content)
    """

    # Patrones regex para extracción
    GROUP_PATTERN = re.compile(r'^\s*GROUP\s+"([^"]+)"\s*$')
    SCUT_PATTERN = re.compile(r'SECTIONCUT\s+"([^"]+)"')

    def process(self, content: bytes) -> E2KProcessResult:
        """
        Procesa un archivo E2K y agrega Section Cuts para todos los grupos.

        Args:
            content: Contenido del archivo E2K en bytes

        Returns:
            E2KProcessResult con el contenido modificado y estadísticas

        Raises:
            ValueError: Si no hay nuevos section cuts para generar
        """
        # Decodificar contenido
        text = self._decode_content(content)
        lines = text.splitlines()

        # Extraer grupos y section cuts existentes
        groups = self._extract_groups(lines)
        existing_scuts = self._extract_existing_scuts(lines)

        # Generar nuevos section cuts
        new_scuts = self._generate_scuts(groups, existing_scuts)

        if not new_scuts:
            raise ValueError(
                'No hay nuevos section cuts para generar. '
                'Todos los grupos ya tienen section cuts.'
            )

        # Insertar section cuts en el archivo
        output = self._insert_scuts(lines, new_scuts)

        return E2KProcessResult(
            content='\n'.join(output),
            n_section_cuts=len(new_scuts),
            n_groups=len(groups)
        )

    def _decode_content(self, content: bytes) -> str:
        """Decodifica el contenido del archivo, probando UTF-8 y Latin-1."""
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            return content.decode('latin-1')

    def _extract_groups(self, lines: List[str]) -> List[str]:
        """Extrae nombres de grupos del archivo E2K."""
        groups: Set[str] = set()
        for line in lines:
            match = self.GROUP_PATTERN.match(line)
            if match:
                groups.add(match.group(1))
        return sorted(groups)

    def _extract_existing_scuts(self, lines: List[str]) -> Set[str]:
        """Extrae nombres de section cuts existentes."""
        existing: Set[str] = set()
        for line in lines:
            match = self.SCUT_PATTERN.search(line)
            if match:
                existing.add(match.group(1))
        return existing

    def _generate_scuts(
        self,
        groups: List[str],
        existing: Set[str]
    ) -> List[str]:
        """Genera líneas de section cut para grupos sin ellos."""
        new_scuts = []
        for group_name in groups:
            scut_name = f"SCut-{group_name}"
            if scut_name not in existing:
                scut_line = (
                    f'  SECTIONCUT "{scut_name}"  DEFINEDBY "Group"  '
                    f'GROUP "{group_name}"  CUTFOR "Analysis"  '
                    f'ROTABOUTZ 0 ROTABOUTYY 0 ROTABOUTXXX 0'
                )
                new_scuts.append(scut_line)
        return new_scuts

    def _insert_scuts(
        self,
        lines: List[str],
        new_scuts: List[str]
    ) -> List[str]:
        """Inserta section cuts en el lugar correcto del archivo."""
        output = []
        section_cuts_found = False

        for line in lines:
            # Si encontramos la sección de SECTION CUTS, insertamos después
            if line.strip() == '$ SECTION CUTS':
                section_cuts_found = True
                output.append(line)
                output.extend(new_scuts)
                continue

            # Si no hay sección SECTION CUTS, la creamos antes de DIMENSION LINES
            if not section_cuts_found and line.strip() == '$ DIMENSION LINES':
                output.append('')
                output.append('$ SECTION CUTS')
                output.extend(new_scuts)
                output.append('')

            output.append(line)

        return output

    # =========================================================================
    # Exportación de secciones agrietadas
    # =========================================================================

    def export_cracked_sections(
        self,
        content: bytes,
        cracked_elements: List[Dict[str, Any]]
    ) -> E2KCrackedResult:
        """
        Exporta un E2K con secciones agrietadas (Property Modifiers aplicados).

        Los Property Modifiers se aplican a las secciones de frame mediante:
        - AMOD: Rigidez axial (pm_axial)
        - I2MOD: Rigidez a flexión eje 2 (pm_m2)
        - I3MOD: Rigidez a flexión eje 3 (pm_m3)
        - A2MOD: Rigidez a cortante eje 2 (pm_v2)
        - A3MOD: Rigidez a cortante eje 3 (pm_v3)
        - JMOD: Rigidez torsional (pm_torsion)
        - WMOD: Peso propio (pm_weight)

        Args:
            content: Contenido del archivo E2K en bytes
            cracked_elements: Lista de elementos agrietados, cada uno con:
                - section_name: Nombre de sección original
                - new_section_name: Nombre con sufijo PM
                - pm_axial, pm_m2, pm_m3, pm_v2, pm_v3, pm_torsion, pm_weight

        Returns:
            E2KCrackedResult con el contenido modificado y estadísticas
        """
        text = self._decode_content(content)
        lines = text.splitlines()

        # Crear mapa de secciones a agrietar
        section_map = {}  # old_name -> new_section_data
        for elem in cracked_elements:
            old_name = elem.get('base_section_name', elem.get('section_name', ''))
            new_name = elem.get('new_section_name', '')
            if old_name and new_name and old_name != new_name:
                section_map[old_name] = {
                    'new_name': new_name,
                    'pm_axial': elem.get('pm_axial', 1.0),
                    'pm_m2': elem.get('pm_m2', 1.0),
                    'pm_m3': elem.get('pm_m3', 1.0),
                    'pm_v2': elem.get('pm_v2', 1.0),
                    'pm_v3': elem.get('pm_v3', 1.0),
                    'pm_torsion': elem.get('pm_torsion', 1.0),
                    'pm_weight': elem.get('pm_weight', 1.0),
                }

        if not section_map:
            return E2KCrackedResult(
                content=text,
                n_sections_modified=0,
                n_elements_updated=0
            )

        # Procesar líneas
        output = []
        n_sections = 0
        n_elements = 0
        in_frame_sections = False
        new_sections_to_add = []

        for line in lines:
            stripped = line.strip()

            # Detectar sección FRAME SECTIONS
            if stripped == '$ FRAME SECTIONS':
                in_frame_sections = True
                output.append(line)
                continue

            # Detectar fin de FRAME SECTIONS
            if in_frame_sections and stripped.startswith('$') and stripped != '$ FRAME SECTIONS':
                # Agregar las nuevas secciones antes de la siguiente sección
                for new_sec in new_sections_to_add:
                    output.append(new_sec)
                new_sections_to_add = []
                in_frame_sections = False

            # Procesar definición de sección de frame
            if in_frame_sections and stripped.startswith('FRAMESECTION'):
                # Buscar si esta sección necesita ser clonada
                for old_name, pm_data in section_map.items():
                    if f'"{old_name}"' in line:
                        # Crear nueva sección con PM aplicados
                        new_section = self._create_cracked_section(
                            line, old_name, pm_data
                        )
                        new_sections_to_add.append(new_section)
                        n_sections += 1
                        break

            # Procesar asignaciones de línea (LINE ASSIGNS)
            if stripped.startswith('LINEASSIGN'):
                for old_name, pm_data in section_map.items():
                    if f'SECTION "{old_name}"' in line:
                        line = line.replace(
                            f'SECTION "{old_name}"',
                            f'SECTION "{pm_data["new_name"]}"'
                        )
                        n_elements += 1
                        break

            output.append(line)

        # Si quedaron secciones por agregar (archivo sin siguiente sección $)
        if new_sections_to_add:
            for new_sec in new_sections_to_add:
                output.append(new_sec)

        return E2KCrackedResult(
            content='\n'.join(output),
            n_sections_modified=n_sections,
            n_elements_updated=n_elements
        )

    def _create_cracked_section(
        self,
        original_line: str,
        old_name: str,
        pm_data: Dict[str, Any]
    ) -> str:
        """
        Crea una nueva línea de FRAMESECTION con Property Modifiers.

        Formato E2K para Property Modifiers de Frame:
        - AMOD: Rigidez axial
        - A2MOD, A3MOD: Rigidez cortante
        - JMOD: Torsión
        - I2MOD, I3MOD: Inercia (flexión)
        - WMOD: Peso
        """
        new_name = pm_data['new_name']

        # Reemplazar nombre de sección
        new_line = original_line.replace(f'"{old_name}"', f'"{new_name}"')

        # Construir string de modifiers
        mods = []
        if pm_data['pm_axial'] != 1.0:
            mods.append(f"AMOD {pm_data['pm_axial']:.4f}")
        if pm_data['pm_v2'] != 1.0:
            mods.append(f"A2MOD {pm_data['pm_v2']:.4f}")
        if pm_data['pm_v3'] != 1.0:
            mods.append(f"A3MOD {pm_data['pm_v3']:.4f}")
        if pm_data['pm_torsion'] != 1.0:
            mods.append(f"JMOD {pm_data['pm_torsion']:.4f}")
        if pm_data['pm_m2'] != 1.0:
            mods.append(f"I2MOD {pm_data['pm_m2']:.4f}")
        if pm_data['pm_m3'] != 1.0:
            mods.append(f"I3MOD {pm_data['pm_m3']:.4f}")
        if pm_data['pm_weight'] != 1.0:
            mods.append(f"WMOD {pm_data['pm_weight']:.4f}")

        if mods:
            # Agregar modifiers al final de la línea
            mod_string = ' '.join(mods)
            new_line = f"{new_line.rstrip()} {mod_string}"

        return new_line
