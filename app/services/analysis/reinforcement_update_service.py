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
                n_stirrup_legs_depth=update.get('n_stirrup_legs_depth'),
                n_stirrup_legs_width=update.get('n_stirrup_legs_width'),
                fy=update.get('fy'),
                fyt=update.get('fyt'),
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

        Args:
            drop_beams: Diccionario {drop_beam_key: DropBeam}
            updates: Lista de actualizaciones [{key, n_meshes, diameter_v, ...}]

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
            drop_beam.update_reinforcement(
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
            )
            count += 1

        logger.debug(f"Actualizadas {count} vigas capitel")
        return count

    @staticmethod
    def apply_slab_updates(
        slabs: Dict[str, Any],
        updates: Optional[List[Dict[str, Any]]]
    ) -> int:
        """
        Aplica actualizaciones de armadura a losas.

        Args:
            slabs: Diccionario {slab_key: Slab}
            updates: Lista de actualizaciones [{key, n_meshes, diameter_v, ...}]

        Returns:
            Número de losas actualizadas
        """
        if not updates:
            return 0

        count = 0
        for update in updates:
            key = update.get('key')
            if not key or key not in slabs:
                continue

            slab = slabs[key]
            if hasattr(slab, 'update_reinforcement'):
                slab.update_reinforcement(
                    n_meshes=update.get('n_meshes'),
                    diameter_v=update.get('diameter_v'),
                    spacing_v=update.get('spacing_v'),
                    diameter_h=update.get('diameter_h'),
                    spacing_h=update.get('spacing_h'),
                    diameter_edge=update.get('diameter_edge'),
                    n_edge_bars=update.get('n_edge_bars'),
                    fy=update.get('fy'),
                    cover=update.get('cover'),
                )
                count += 1

        logger.debug(f"Actualizadas {count} losas")
        return count

    @classmethod
    def apply_all_updates(
        cls,
        parsed_data,
        pier_updates: Optional[List[Dict]] = None,
        column_updates: Optional[List[Dict]] = None,
        beam_updates: Optional[List[Dict]] = None,
        drop_beam_updates: Optional[List[Dict]] = None,
        slab_updates: Optional[List[Dict]] = None,
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

        if pier_updates and parsed_data.piers:
            counts['piers'] = cls.apply_pier_updates(parsed_data.piers, pier_updates)

        if column_updates and parsed_data.columns:
            counts['columns'] = cls.apply_column_updates(parsed_data.columns, column_updates)

        if beam_updates and parsed_data.beams:
            counts['beams'] = cls.apply_beam_updates(parsed_data.beams, beam_updates)

        if drop_beam_updates and parsed_data.drop_beams:
            counts['drop_beams'] = cls.apply_drop_beam_updates(parsed_data.drop_beams, drop_beam_updates)

        if slab_updates and parsed_data.slabs:
            counts['slabs'] = cls.apply_slab_updates(parsed_data.slabs, slab_updates)

        return counts

    # =========================================================================
    # Métodos especializados para losas (incluyen tipo y columna)
    # =========================================================================

    @staticmethod
    def update_slab_properties(
        slab,
        slab_type: str = None,
        diameter_main: int = None,
        spacing_main: int = None,
        diameter_temp: int = None,
        spacing_temp: int = None,
        column_width: float = None,
        column_depth: float = None
    ) -> bool:
        """
        Actualiza propiedades de una losa (tipo, refuerzo y columna).

        Args:
            slab: Objeto Slab a actualizar
            slab_type: 'one_way' o 'two_way'
            diameter_main: Diámetro armadura principal (mm)
            spacing_main: Espaciamiento armadura principal (mm)
            diameter_temp: Diámetro armadura temperatura (mm)
            spacing_temp: Espaciamiento armadura temperatura (mm)
            column_width: Ancho columna para punzonamiento (mm)
            column_depth: Profundidad columna para punzonamiento (mm)

        Returns:
            True si se actualizó correctamente
        """
        from ...domain.entities.slab import SlabType

        # Actualizar tipo de losa
        if slab_type:
            slab.slab_type = (
                SlabType.TWO_WAY if slab_type == 'two_way'
                else SlabType.ONE_WAY
            )

        # Actualizar refuerzo
        if diameter_main is not None:
            slab.update_reinforcement(diameter_main=diameter_main)
        if spacing_main is not None:
            slab.update_reinforcement(spacing_main=spacing_main)
        if diameter_temp is not None:
            slab.update_reinforcement(diameter_temp=diameter_temp)
        if spacing_temp is not None:
            slab.update_reinforcement(spacing_temp=spacing_temp)

        # Actualizar columna
        if column_width is not None:
            slab.update_column_info(column_width=column_width)
        if column_depth is not None:
            slab.update_column_info(column_depth=column_depth)

        return True

    @classmethod
    def apply_slab_property_updates(
        cls,
        slabs: Dict[str, Any],
        updates: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Aplica actualizaciones de propiedades a múltiples losas.

        Args:
            slabs: Diccionario {slab_key: Slab}
            updates: Lista de actualizaciones [{key, slab_type, diameter_main, ...}]

        Returns:
            Dict con 'updated_count' y 'errors'
        """
        if not updates:
            return {'updated_count': 0, 'errors': None}

        updated_count = 0
        errors = []

        for update in updates:
            slab_key = update.get('key')
            if not slab_key or slab_key not in slabs:
                continue

            slab = slabs[slab_key]
            try:
                cls.update_slab_properties(
                    slab,
                    slab_type=update.get('slab_type'),
                    diameter_main=update.get('diameter_main'),
                    spacing_main=update.get('spacing_main'),
                    diameter_temp=update.get('diameter_temp'),
                    spacing_temp=update.get('spacing_temp'),
                    column_width=update.get('column_width'),
                    column_depth=update.get('column_depth')
                )
                updated_count += 1
            except Exception as e:
                errors.append(f'{slab_key}: {str(e)}')

        logger.debug(f"Actualizadas {updated_count} losas")
        return {
            'success': len(errors) == 0,
            'updated_count': updated_count,
            'errors': errors if errors else None
        }
