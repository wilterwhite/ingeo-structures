# app/services/parsing/e2k_processor.py
"""
Procesador de archivos E2K de ETABS.

Genera Section Cuts automáticamente para todos los grupos definidos en el archivo.
"""
import re
from dataclasses import dataclass
from typing import List, Set, Tuple


@dataclass
class E2KProcessResult:
    """Resultado del procesamiento de un archivo E2K."""
    content: str
    n_section_cuts: int
    n_groups: int


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
