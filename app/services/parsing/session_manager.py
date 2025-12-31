# app/structural/services/parsing/session_manager.py
"""
Gestión de sesiones para el análisis estructural.
Maneja el cache de datos parseados y actualizaciones de armadura.
"""
from typing import Dict, Optional, Any

from .excel_parser import EtabsExcelParser, ParsedData
from ...domain.calculations import WallContinuityService


class SessionManager:
    """
    Gestiona las sesiones de análisis estructural.

    Responsabilidades:
    - Almacenar datos parseados por session_id
    - Aplicar actualizaciones de armadura a piers
    - Limpiar sesiones expiradas
    """

    def __init__(self):
        self._cache: Dict[str, ParsedData] = {}
        self._excel_parser = EtabsExcelParser()
        self._continuity_service = WallContinuityService()

    def create_session(
        self,
        file_content: bytes,
        session_id: str,
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva sesión parseando el archivo Excel.

        Args:
            file_content: Contenido binario del Excel
            session_id: ID de sesión único
            hn_ft: Altura del edificio en pies (opcional, se estima si no se provee)

        Returns:
            Diccionario con resumen de piers encontrados
        """
        parsed_data = self._excel_parser.parse_excel(file_content)

        # Calcular continuidad de muros y hwcs para cada pier
        if parsed_data.piers and parsed_data.stories:
            continuity_info = self._continuity_service.analyze_continuity(
                piers=parsed_data.piers,
                stories=parsed_data.stories,
                hn_ft=hn_ft
            )
            parsed_data.continuity_info = continuity_info
            parsed_data.building_info = self._continuity_service.get_building_info()

        self._cache[session_id] = parsed_data
        summary = self._excel_parser.get_summary(parsed_data)

        # Agregar info del edificio al resumen
        if parsed_data.building_info:
            summary['building'] = {
                'n_stories': parsed_data.building_info.n_stories,
                'hn_ft': round(parsed_data.building_info.hn_ft, 1),
                'hn_m': round(parsed_data.building_info.hn_m, 2),
                'total_height_mm': round(parsed_data.building_info.total_height_mm, 0)
            }

        return {
            'success': True,
            'session_id': session_id,
            'summary': summary
        }

    def get_session(self, session_id: str) -> Optional[ParsedData]:
        """Obtiene los datos de una sesión."""
        return self._cache.get(session_id)

    def has_session(self, session_id: str) -> bool:
        """Verifica si existe una sesión."""
        return session_id in self._cache

    def clear_session(self, session_id: str) -> bool:
        """Elimina una sesión del cache."""
        if session_id in self._cache:
            del self._cache[session_id]
            return True
        return False

    def apply_reinforcement_updates(
        self,
        session_id: str,
        updates: list
    ) -> bool:
        """
        Aplica actualizaciones de armadura a los piers de una sesión.

        Args:
            session_id: ID de sesión
            updates: Lista de actualizaciones con configuración de malla
                     [{'key': 'Story_Pier', 'n_meshes': 2, 'diameter_v': 10,
                       'spacing_v': 150, 'diameter_h': 8, 'spacing_h': 200,
                       'diameter_edge': 10, 'n_edge_bars': 4,
                       'stirrup_diameter': 10, 'stirrup_spacing': 150,
                       'fy': 420}]

        Returns:
            True si se aplicaron las actualizaciones
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data or not updates:
            return False

        for update in updates:
            key = update.get('key')
            if key not in parsed_data.piers:
                continue

            pier = parsed_data.piers[key]

            # Aplicar configuración de armadura (incluye elemento de borde)
            pier.update_reinforcement(
                n_meshes=update.get('n_meshes'),
                diameter_v=update.get('diameter_v'),
                spacing_v=update.get('spacing_v'),
                diameter_h=update.get('diameter_h'),
                spacing_h=update.get('spacing_h'),
                diameter_edge=update.get('diameter_edge'),
                n_edge_bars=update.get('n_edge_bars'),
                stirrup_diameter=update.get('stirrup_diameter'),
                stirrup_spacing=update.get('stirrup_spacing'),
                fy=update.get('fy'),
                cover=update.get('cover')
            )

        return True

    def get_pier(self, session_id: str, pier_key: str):
        """Obtiene un pier específico de una sesión."""
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None
        return parsed_data.piers.get(pier_key)

    def get_pier_forces(self, session_id: str, pier_key: str):
        """Obtiene las fuerzas de un pier específico."""
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None
        return parsed_data.pier_forces.get(pier_key)

    def get_hwcs(self, session_id: str, pier_key: str) -> float:
        """
        Obtiene hwcs para un pier específico.

        hwcs es la altura desde la sección crítica (base del muro continuo)
        hasta el tope del pier actual.

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier (Story_Label)

        Returns:
            hwcs en mm, o la altura del pier si no hay info de continuidad
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return 0

        # Si hay info de continuidad, usar hwcs calculado
        if parsed_data.continuity_info and pier_key in parsed_data.continuity_info:
            return parsed_data.continuity_info[pier_key].hwcs

        # Fallback: usar altura del pier
        pier = parsed_data.piers.get(pier_key)
        return pier.height if pier else 0

    def get_hn_ft(self, session_id: str) -> float:
        """
        Obtiene la altura del edificio en pies.

        Args:
            session_id: ID de sesión

        Returns:
            hn en pies, o 0 si no hay info del edificio
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data or not parsed_data.building_info:
            return 0
        return parsed_data.building_info.hn_ft

    def get_building_info(self, session_id: str):
        """
        Obtiene información del edificio.

        Args:
            session_id: ID de sesión

        Returns:
            BuildingInfo o None
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None
        return parsed_data.building_info
