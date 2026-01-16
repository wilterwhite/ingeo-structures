# app/services/analysis/reinforcement_update_service.py
"""
Servicio centralizado para actualización de armadura de elementos estructurales.

Este servicio es la ÚNICA ubicación para aplicar actualizaciones de armadura.
Las rutas y otros servicios deben delegar a este servicio en lugar de
iterar y aplicar updates directamente.
"""
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ReinforcementUpdateService:
    """
    Servicio para aplicar actualizaciones de armadura a elementos estructurales.

    Centraliza la lógica de actualización que antes estaba duplicada en:
    - routes/piers.py
    - routes/drop_beams.py
    - routes/beams.py
    - routes/columns.py
    - services/structural_analysis.py
    - services/parsing/session_manager.py
    """

    @staticmethod
    def apply_pier_updates(
        piers: Dict[str, Any],
        updates: Optional[List[Dict[str, Any]]]
    ) -> int:
        """
        Aplica actualizaciones de armadura a piers.

        Args:
            piers: Diccionario {pier_key: Pier}
            updates: Lista de actualizaciones [{key, n_meshes, diameter_v, ...}]

        Returns:
            Número de piers actualizados
        """
        if not updates:
            return 0

        count = 0
        for update in updates:
            key = update.get('key')
            if not key or key not in piers:
                continue

            pier = piers[key]
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
                cover=update.get('cover'),
                seismic_category=update.get('seismic_category'),
            )
            count += 1

        logger.debug(f"Actualizados {count} piers")
        return count

    @staticmethod
    def apply_column_updates(
        columns: Dict[str, Any],
        updates: Optional[List[Dict[str, Any]]]
    ) -> int:
        """
        Aplica actualizaciones de armadura a columnas.

        Args:
            columns: Diccionario {column_key: Column}
            updates: Lista de actualizaciones [{key, n_bars_depth, diameter_long, ...}]

        Returns:
            Número de columnas actualizadas
        """
        if not updates:
            return 0

        count = 0
        for update in updates:
            key = update.get('key')
            if not key or key not in columns:
                continue

            column = columns[key]
            column.update_reinforcement(
                n_bars_depth=update.get('n_bars_depth'),
                n_bars_width=update.get('n_bars_width'),
                diameter_long=update.get('diameter_long'),
                stirrup_diameter=update.get('stirrup_diameter'),
                stirrup_spacing=update.get('stirrup_spacing'),
                n_shear_legs=update.get('n_shear_legs'),
                n_shear_legs_secondary=update.get('n_shear_legs_secondary'),
                fy=update.get('fy'),
                cover=update.get('cover'),
            )
            count += 1

        logger.debug(f"Actualizadas {count} columnas")
        return count

    @staticmethod
    def apply_beam_updates(
        beams: Dict[str, Any],
        updates: Optional[List[Dict[str, Any]]]
    ) -> int:
        """
        Aplica actualizaciones de armadura a vigas.

        Args:
            beams: Diccionario {beam_key: Beam}
            updates: Lista de actualizaciones [{key, n_bars_top, diameter_top, ...}]

        Returns:
            Número de vigas actualizadas
        """
        if not updates:
            return 0

        count = 0
        for update in updates:
            key = update.get('key')
            if not key or key not in beams:
                continue

            beam = beams[key]
            beam.update_reinforcement(
                n_bars_top=update.get('n_bars_top'),
                n_bars_bottom=update.get('n_bars_bottom'),
                diameter_top=update.get('diameter_top'),
                diameter_bottom=update.get('diameter_bottom'),
                diameter_lateral=update.get('diameter_lateral'),
                spacing_lateral=update.get('spacing_lateral'),
                stirrup_diameter=update.get('stirrup_diameter'),
                stirrup_spacing=update.get('stirrup_spacing'),
                n_stirrup_legs=update.get('n_stirrup_legs'),
            )
            count += 1

        logger.debug(f"Actualizadas {count} vigas")
        return count

    @staticmethod
    def apply_drop_beam_updates(
        drop_beams: Dict[str, Any],
        updates: Optional[List[Dict[str, Any]]]
    ) -> int:
        """
        Aplica actualizaciones de armadura a vigas capitel.

        DROP_BEAM ahora usa el mismo formato que BEAM (barras top/bottom).

        Args:
            drop_beams: Diccionario {drop_beam_key: DropBeam}
            updates: Lista de actualizaciones [{key, n_bars_top, diameter_top, ...}]

        Returns:
            Número de vigas capitel actualizadas
        """
        if not updates:
            return 0

        count = 0
        for update in updates:
            key = update.get('key')
            if not key or key not in drop_beams:
                continue

            drop_beam = drop_beams[key]
            # DROP_BEAM ahora usa el mismo formato que BEAM
            drop_beam.update_reinforcement(
                n_bars_top=update.get('n_bars_top'),
                n_bars_bottom=update.get('n_bars_bottom'),
                diameter_top=update.get('diameter_top'),
                diameter_bottom=update.get('diameter_bottom'),
                diameter_lateral=update.get('diameter_lateral'),
                spacing_lateral=update.get('spacing_lateral'),
                stirrup_diameter=update.get('stirrup_diameter'),
                stirrup_spacing=update.get('stirrup_spacing'),
                n_stirrup_legs=update.get('n_stirrup_legs'),
                fy=update.get('fy'),
                cover=update.get('cover'),
            )
            count += 1

        logger.debug(f"Actualizadas {count} vigas capitel")
        return count

    @classmethod
    def apply_all_updates(
        cls,
        parsed_data,
        pier_updates: Optional[List[Dict]] = None,
        column_updates: Optional[List[Dict]] = None,
        beam_updates: Optional[List[Dict]] = None,
        drop_beam_updates: Optional[List[Dict]] = None,
    ) -> Dict[str, int]:
        """
        Aplica todas las actualizaciones de armadura a parsed_data.

        Args:
            parsed_data: Objeto ParsedData con todos los elementos
            *_updates: Listas de actualizaciones por tipo

        Returns:
            Diccionario con conteo de actualizaciones por tipo
        """
        counts = {}

        # Elementos verticales contienen tanto piers como columnas
        vertical_elements = parsed_data.vertical_elements or {}

        if pier_updates and vertical_elements:
            counts['piers'] = cls.apply_pier_updates(vertical_elements, pier_updates)

        if column_updates and vertical_elements:
            counts['columns'] = cls.apply_column_updates(vertical_elements, column_updates)

        # Elementos horizontales contienen tanto vigas como vigas capitel
        horizontal_elements = parsed_data.horizontal_elements or {}

        if beam_updates and horizontal_elements:
            counts['beams'] = cls.apply_beam_updates(horizontal_elements, beam_updates)

        if drop_beam_updates and horizontal_elements:
            counts['drop_beams'] = cls.apply_drop_beam_updates(horizontal_elements, drop_beam_updates)

        return counts
