# app/services/persistence/project_manager.py
"""
Gestor de proyectos con persistencia.

Estructura de proyecto:
    ~/.ingeo-structures/projects/{project_id}/
        project.json         # Metadata del proyecto
        parsed_data.json     # Estado completo parseado
        results.json         # Resultados de análisis (carga instantánea)
        source.xlsx          # Copia del Excel original (backup)
"""
import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .parsed_data_serializer import (
    serialize_parsed_data,
    deserialize_parsed_data,
)

if TYPE_CHECKING:
    from ...domain.entities.parsed_data import ParsedData


def _get_projects_base_dir() -> Path:
    """Obtiene el directorio base para proyectos."""
    base = os.environ.get('INGEO_PROJECTS_DIR')
    if base:
        return Path(base)
    return Path.home() / '.ingeo-structures' / 'projects'


class ProjectManager:
    """
    Gestor de proyectos con persistencia.

    Responsabilidades:
    - Crear nuevos proyectos
    - Guardar estado parseado y resultados de análisis
    - Cargar proyectos existentes (instantáneo)
    - Listar y eliminar proyectos
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self._base_dir = base_dir or _get_projects_base_dir()
        self._ensure_base_dir()

    def _ensure_base_dir(self):
        """Crea el directorio base si no existe."""
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _get_project_dir(self, project_id: str) -> Path:
        """Obtiene el directorio de un proyecto."""
        return self._base_dir / project_id

    # =========================================================================
    # CREAR PROYECTO
    # =========================================================================

    def create_project(
        self,
        name: str,
        excel_content: bytes,
        excel_filename: str,
        description: str = "",
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo proyecto desde un archivo Excel.
        """
        project_id = str(uuid.uuid4())[:8]
        project_dir = self._get_project_dir(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)

        # Guardar Excel original
        excel_path = project_dir / 'source.xlsx'
        with open(excel_path, 'wb') as f:
            f.write(excel_content)

        # Crear metadata
        metadata = {
            'id': project_id,
            'name': name,
            'description': description,
            'source_file': excel_filename,
            'hn_ft': hn_ft,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': '2.0',
        }

        with open(project_dir / 'project.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return {
            'success': True,
            'project_id': project_id,
            'metadata': metadata
        }

    # =========================================================================
    # GUARDAR
    # =========================================================================

    def save_parsed_data(
        self,
        project_id: str,
        parsed_data: 'ParsedData',
    ) -> Dict[str, Any]:
        """
        Guarda el ParsedData completo.
        """
        project_dir = self._get_project_dir(project_id)
        if not project_dir.exists():
            return {'success': False, 'error': 'Proyecto no encontrado'}

        serialized = serialize_parsed_data(parsed_data)

        parsed_data_path = project_dir / 'parsed_data.json'
        with open(parsed_data_path, 'w', encoding='utf-8') as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)

        self._update_project_timestamp(project_id)

        return {
            'success': True,
            'saved': {
                'vertical_elements': len(parsed_data.vertical_elements),
                'horizontal_elements': len(parsed_data.horizontal_elements),
            }
        }

    def save_results(
        self,
        project_id: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Guarda los resultados del análisis en results.json.
        Permite cargar proyectos sin re-ejecutar el análisis.
        """
        project_dir = self._get_project_dir(project_id)
        if not project_dir.exists():
            return {'success': False, 'error': 'Proyecto no encontrado'}

        results_path = project_dir / 'results.json'
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False)

        return {'success': True}

    # =========================================================================
    # CARGAR
    # =========================================================================

    def load_project(self, project_id: str) -> Dict[str, Any]:
        """
        Carga un proyecto existente.

        Returns:
            Dict con parsed_data, results (si existe), y metadata
        """
        project_dir = self._get_project_dir(project_id)
        if not project_dir.exists():
            return {'success': False, 'error': 'Proyecto no encontrado'}

        # Leer metadata
        with open(project_dir / 'project.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Cargar parsed_data
        parsed_data_path = project_dir / 'parsed_data.json'
        if not parsed_data_path.exists():
            return {'success': False, 'error': 'Proyecto sin datos parseados'}

        with open(parsed_data_path, 'r', encoding='utf-8') as f:
            parsed_data_dict = json.load(f)

        parsed_data = deserialize_parsed_data(parsed_data_dict)

        # Cargar resultados de análisis si existen
        results = self.load_results(project_id)

        return {
            'success': True,
            'project_id': project_id,
            'metadata': metadata,
            'parsed_data': parsed_data,
            'hn_ft': metadata.get('hn_ft'),
            'results': results,
            'has_results': results is not None,
        }

    def load_results(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Carga los resultados del análisis desde results.json.
        """
        results_path = self._get_project_dir(project_id) / 'results.json'
        if not results_path.exists():
            return None

        with open(results_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # =========================================================================
    # LISTAR Y ELIMINAR
    # =========================================================================

    def list_projects(self) -> List[Dict[str, Any]]:
        """Lista todos los proyectos disponibles."""
        projects = []

        if not self._base_dir.exists():
            return projects

        for item in self._base_dir.iterdir():
            if item.is_dir():
                metadata_path = item / 'project.json'
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            projects.append(metadata)
                    except (json.JSONDecodeError, IOError):
                        continue

        projects.sort(key=lambda p: p.get('updated_at', ''), reverse=True)
        return projects

    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Elimina un proyecto."""
        project_dir = self._get_project_dir(project_id)
        if not project_dir.exists():
            return {'success': False, 'error': 'Proyecto no encontrado'}

        try:
            shutil.rmtree(project_dir)
            return {'success': True}
        except OSError as e:
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # UTILIDADES
    # =========================================================================

    def _update_project_timestamp(self, project_id: str) -> None:
        """Actualiza el timestamp de modificación."""
        project_dir = self._get_project_dir(project_id)
        metadata_path = project_dir / 'project.json'

        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            metadata['updated_at'] = datetime.now().isoformat()

            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

    def get_project_metadata(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene solo la metadata de un proyecto."""
        project_dir = self._get_project_dir(project_id)
        metadata_path = project_dir / 'project.json'

        if not metadata_path.exists():
            return None

        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_project_name(
        self,
        project_id: str,
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Actualiza nombre y descripción de un proyecto."""
        project_dir = self._get_project_dir(project_id)
        metadata_path = project_dir / 'project.json'

        if not metadata_path.exists():
            return {'success': False, 'error': 'Proyecto no encontrado'}

        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        metadata['name'] = name
        if description is not None:
            metadata['description'] = description
        metadata['updated_at'] = datetime.now().isoformat()

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return {'success': True, 'metadata': metadata}

    def project_exists(self, project_id: str) -> bool:
        """Verifica si un proyecto existe."""
        return (self._get_project_dir(project_id) / 'project.json').exists()
