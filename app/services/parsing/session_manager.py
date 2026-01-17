# app/structural/services/parsing/session_manager.py
"""
Gestión de sesiones para el análisis estructural.
Maneja el cache de datos parseados y actualizaciones de armadura.
"""
from typing import Dict, Optional, Any, List
import pandas as pd
import logging

from .excel_parser import EtabsExcelParser, ParsedData
from ...domain.calculations import WallContinuityService
from ...domain.entities.coupling_beam import CouplingBeamConfig, PierCouplingConfig
from ...domain.constants.reinforcement import FY_DEFAULT_MPA
from ..logging import claude_logger

logger = logging.getLogger(__name__)


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

    # =========================================================================
    # NUEVO FLUJO: Acumular → Fusionar → Procesar
    # =========================================================================

    def accumulate_tables(
        self,
        file_content: bytes,
        session_id: str,
        filename: str = "unknown.xlsx"
    ) -> Dict[str, Any]:
        """
        Extrae y acumula tablas de un archivo Excel SIN procesar elementos.

        Flujo multi-archivo:
        1. accumulate_tables(archivo1) → acumula tablas
        2. accumulate_tables(archivo2) → acumula más tablas
        3. process_session() → fusiona y procesa

        Args:
            file_content: Contenido binario del Excel
            session_id: ID de sesión
            filename: Nombre del archivo para logging

        Returns:
            Dict con tablas encontradas en este archivo
        """
        # Log para Claude
        claude_logger.set_session(session_id)
        claude_logger.log_file_received(filename)

        # Extraer tablas del archivo
        tables = self._excel_parser.extract_tables_only(file_content)

        # Crear sesión si no existe
        if session_id not in self._cache:
            self._cache[session_id] = ParsedData()

        parsed_data = self._cache[session_id]

        # Acumular tablas
        for key, df in tables.items():
            if key not in parsed_data.accumulated_tables:
                parsed_data.accumulated_tables[key] = []
            parsed_data.accumulated_tables[key].append(df)

        # Generar resumen de tablas encontradas
        tables_found = list(tables.keys())
        total_accumulated = {
            k: len(v) for k, v in parsed_data.accumulated_tables.items()
        }

        logger.info(
            f"Session {session_id}: Acumuladas {len(tables)} tablas. "
            f"Total: {total_accumulated}"
        )

        return {
            'success': True,
            'session_id': session_id,
            'tables_found': tables_found,
            'total_accumulated': total_accumulated
        }

    def process_session(
        self,
        session_id: str,
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fusiona tablas acumuladas y procesa elementos.

        Debe llamarse DESPUÉS de accumulate_tables().

        Args:
            session_id: ID de sesión
            hn_ft: Altura del edificio en pies (opcional)

        Returns:
            Dict con resumen de elementos parseados
        """
        if session_id not in self._cache:
            return {'success': False, 'error': 'Session not found'}

        parsed_data = self._cache[session_id]

        if not parsed_data.accumulated_tables:
            return {'success': False, 'error': 'No tables accumulated'}

        # Fusionar tablas del mismo tipo
        merged_tables: Dict[str, pd.DataFrame] = {}
        logger.info(f"[process_session] Tablas acumuladas: {list(parsed_data.accumulated_tables.keys())}")
        for key, df_list in parsed_data.accumulated_tables.items():
            if len(df_list) == 1:
                merged_tables[key] = df_list[0]
                logger.info(f"[process_session] Tabla '{key}': 1 archivo, {len(df_list[0])} filas")
            else:
                # Concatenar DataFrames del mismo tipo
                merged_tables[key] = pd.concat(df_list, ignore_index=True)
                logger.info(f"[process_session] Fusionadas {len(df_list)} tablas '{key}' -> {len(merged_tables[key])} filas")

        logger.info(f"[process_session] Tablas fusionadas: {list(merged_tables.keys())}")
        if 'frame_section' in merged_tables:
            logger.info(f"[process_session] frame_section tiene {len(merged_tables['frame_section'])} filas")
        else:
            logger.warning("[process_session] NO SE ENCONTRÓ frame_section en tablas fusionadas!")

        # Procesar elementos desde tablas fusionadas
        new_parsed = self._excel_parser.parse_from_tables(merged_tables)

        # Copiar datos procesados a la sesión actual
        parsed_data.vertical_elements = new_parsed.vertical_elements
        parsed_data.horizontal_elements = new_parsed.horizontal_elements
        parsed_data.vertical_forces = new_parsed.vertical_forces
        parsed_data.horizontal_forces = new_parsed.horizontal_forces
        parsed_data.materials = new_parsed.materials
        parsed_data.stories = new_parsed.stories
        parsed_data.raw_tables = merged_tables  # Guardar tablas fusionadas

        # Calcular continuidad de muros
        from ...domain.entities import VerticalElementSource
        piers = {k: v for k, v in parsed_data.vertical_elements.items()
                 if v.source == VerticalElementSource.PIER}

        if piers and parsed_data.stories:
            continuity_info = self._continuity_service.analyze_continuity(
                piers=piers,
                stories=parsed_data.stories,
                hn_ft=hn_ft
            )
            parsed_data.continuity_info = continuity_info
            parsed_data.building_info = self._continuity_service.get_building_info()

        # Generar resumen
        summary = self._excel_parser.get_summary(parsed_data)

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

    def get_raw_tables(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna las tablas crudas de una sesión para vista de verificación.

        Args:
            session_id: ID de sesión

        Returns:
            Dict con tablas en formato serializable para JSON
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None

        result = {}

        # Usar raw_tables si ya se procesó, sino accumulated_tables
        tables = parsed_data.raw_tables or {}

        # Si no hay raw_tables, mostrar accumulated_tables fusionadas temporalmente
        if not tables and parsed_data.accumulated_tables:
            for key, df_list in parsed_data.accumulated_tables.items():
                if df_list:
                    tables[key] = df_list[0] if len(df_list) == 1 else pd.concat(df_list)

        for key, df in tables.items():
            if df is not None and not df.empty:
                # Convertir DataFrame a formato JSON-serializable
                result[key] = {
                    'columns': [str(c) for c in df.columns.tolist()],
                    'rows': df.head(100).fillna('').astype(str).values.tolist(),
                    'total_rows': len(df)
                }

        return result

    def get_session(self, session_id: str) -> Optional[ParsedData]:
        """Obtiene los datos de una sesión."""
        return self._cache.get(session_id)

    def has_session(self, session_id: str) -> bool:
        """Verifica si existe una sesión."""
        return session_id in self._cache

    # =========================================================================
    # Validación (centralizada para evitar duplicación)
    # =========================================================================

    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Valida que la sesión existe.

        Returns:
            None si la sesión es válida, o dict con error si no existe.
        """
        if not self.has_session(session_id):
            return {
                'success': False,
                'error': 'Session not found. Please upload the file again.'
            }
        return None

    def validate_pier(self, session_id: str, pier_key: str) -> Optional[Dict[str, Any]]:
        """
        Valida que el pier existe en la sesión.

        Returns:
            None si el pier es válido, o dict con error si no existe.
        """
        session_error = self.validate_session(session_id)
        if session_error:
            return session_error

        pier = self.get_pier(session_id, pier_key)
        if pier is None:
            return {'success': False, 'error': f'Pier not found: {pier_key}'}
        return None

    # =========================================================================
    # Gestión de Sesiones
    # =========================================================================

    def clear_session(self, session_id: str) -> bool:
        """Elimina una sesión del cache."""
        if session_id in self._cache:
            del self._cache[session_id]
            return True
        return False

    # =========================================================================
    # Métodos de acceso a elementos
    # =========================================================================

    def get_pier(self, session_id: str, pier_key: str):
        """Obtiene un pier específico de una sesión."""
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None
        return parsed_data.vertical_elements.get(pier_key)

    def get_column(self, session_id: str, column_key: str):
        """Obtiene una columna específica de una sesión."""
        parsed_data = self.get_session(session_id)
        if not parsed_data or not parsed_data.vertical_elements:
            return None
        return parsed_data.vertical_elements.get(column_key)

    def validate_column(self, session_id: str, column_key: str) -> Optional[Dict[str, Any]]:
        """
        Valida que la columna existe en la sesión.

        Returns:
            None si la columna es válida, o dict con error si no existe.
        """
        session_error = self.validate_session(session_id)
        if session_error:
            return session_error

        column = self.get_column(session_id, column_key)
        if column is None:
            return {'success': False, 'error': f'Column not found: {column_key}'}
        return None

    def get_pier_forces(self, session_id: str, pier_key: str):
        """Obtiene las fuerzas de un pier específico."""
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None
        return parsed_data.vertical_forces.get(pier_key)

    def get_column_forces(self, session_id: str, column_key: str):
        """Obtiene las fuerzas de una columna específica."""
        parsed_data = self.get_session(session_id)
        if not parsed_data or not parsed_data.vertical_forces:
            return None
        return parsed_data.vertical_forces.get(column_key)

    def get_beam(self, session_id: str, beam_key: str):
        """Obtiene una viga específica de una sesión."""
        parsed_data = self.get_session(session_id)
        if not parsed_data or not parsed_data.horizontal_elements:
            return None
        return parsed_data.horizontal_elements.get(beam_key)

    def get_beam_forces(self, session_id: str, beam_key: str):
        """Obtiene las fuerzas de una viga específica."""
        parsed_data = self.get_session(session_id)
        if not parsed_data or not parsed_data.horizontal_forces:
            return None
        return parsed_data.horizontal_forces.get(beam_key)

    def get_drop_beam(self, session_id: str, key: str):
        """Obtiene una viga capitel específica de una sesión."""
        parsed_data = self.get_session(session_id)
        if not parsed_data or not parsed_data.horizontal_elements:
            return None
        return parsed_data.horizontal_elements.get(key)

    def get_drop_beam_forces(self, session_id: str, key: str):
        """Obtiene las fuerzas de una viga capitel específica."""
        parsed_data = self.get_session(session_id)
        if not parsed_data or not parsed_data.horizontal_forces:
            return None
        return parsed_data.horizontal_forces.get(key)

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
        pier = parsed_data.vertical_elements.get(pier_key)
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

    # =========================================================================
    # VIGAS DE ACOPLE
    # =========================================================================

    def set_default_coupling_beam(
        self,
        session_id: str,
        **kwargs
    ) -> bool:
        """
        Configura la viga de acople generica por defecto.

        Args:
            session_id: ID de sesión
            **kwargs: Configuración de la viga:
                - width: Ancho (mm)
                - height: Altura (mm)
                - ln: Largo libre (mm)
                - n_bars_top: Número de barras superiores
                - diameter_top: Diámetro superior (mm)
                - n_bars_bottom: Número de barras inferiores
                - diameter_bottom: Diámetro inferior (mm)
                - stirrup_diameter: Diámetro estribos (mm)
                - stirrup_spacing: Espaciamiento estribos (mm)
                - n_legs: Número de ramas (default 2)
                - fy: Fluencia del acero (MPa, default 420)
                - fc: f'c del concreto (MPa, default 25)

        Returns:
            True si se aplicó la configuración
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return False

        beam = CouplingBeamConfig(
            width=kwargs.get('width', 200),
            height=kwargs.get('height', 500),
            ln=kwargs.get('ln', 1500),
            n_bars_top=kwargs.get('n_bars_top', 3),
            diameter_top=kwargs.get('diameter_top', 16),
            n_bars_bottom=kwargs.get('n_bars_bottom', 3),
            diameter_bottom=kwargs.get('diameter_bottom', 16),
            stirrup_diameter=kwargs.get('stirrup_diameter', 10),
            stirrup_spacing=kwargs.get('stirrup_spacing', 150),
            n_legs=kwargs.get('n_legs', 2),
            fy=kwargs.get('fy', FY_DEFAULT_MPA),
            fc=kwargs.get('fc', 25),
            cover=kwargs.get('cover', 40),
        )

        parsed_data.default_coupling_beam = beam
        return True

    def get_default_coupling_beam(
        self,
        session_id: str
    ) -> Optional[CouplingBeamConfig]:
        """
        Obtiene la viga de acople genérica.

        Args:
            session_id: ID de sesión

        Returns:
            CouplingBeamConfig o None
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None
        return parsed_data.default_coupling_beam

    def set_pier_coupling_config(
        self,
        session_id: str,
        pier_key: str,
        has_beam_left: bool = True,
        has_beam_right: bool = True,
        beam_left_config: Optional[dict] = None,
        beam_right_config: Optional[dict] = None
    ) -> bool:
        """
        Configura las vigas de acople para un pier específico.

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier (Story_Label)
            has_beam_left: Si tiene viga a la izquierda
            has_beam_right: Si tiene viga a la derecha
            beam_left_config: Config de viga izquierda (None = usar genérica)
            beam_right_config: Config de viga derecha (None = usar genérica)

        Returns:
            True si se aplicó la configuración
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data or pier_key not in parsed_data.vertical_elements:
            return False

        # Crear vigas específicas si se proveen configs
        beam_left = None
        if beam_left_config:
            beam_left = CouplingBeamConfig(**beam_left_config)

        beam_right = None
        if beam_right_config:
            beam_right = CouplingBeamConfig(**beam_right_config)

        config = PierCouplingConfig(
            pier_key=pier_key,
            beam_left=beam_left,
            beam_right=beam_right,
            has_beam_left=has_beam_left,
            has_beam_right=has_beam_right
        )

        parsed_data.pier_coupling_configs[pier_key] = config
        return True

    # =========================================================================
    # CACHE DE RESULTADOS DE ANÁLISIS
    # =========================================================================

    def store_analysis_result(
        self,
        session_id: str,
        element_key: str,
        result: Dict[str, Any]
    ) -> bool:
        """
        Almacena el resultado de análisis de un elemento.

        Permite que el modal use los mismos datos que la tabla sin recalcular.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento (ej: "Cielo P1_PFel-A20-2")
            result: Resultado formateado del análisis

        Returns:
            True si se almacenó correctamente
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return False

        parsed_data.analysis_cache[element_key] = result
        return True

    def get_analysis_result(
        self,
        session_id: str,
        element_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene el resultado de análisis de un elemento desde el cache.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento

        Returns:
            Resultado formateado o None si no existe
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None

        return parsed_data.analysis_cache.get(element_key)

    def clear_analysis_cache(self, session_id: str) -> bool:
        """
        Limpia el cache de resultados de análisis.

        Útil cuando se modifica la armadura y hay que recalcular.

        Args:
            session_id: ID de sesión

        Returns:
            True si se limpió correctamente
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return False

        parsed_data.analysis_cache.clear()
        # También limpiar curvas P-M (dependen de la armadura)
        parsed_data.interaction_curves.clear()
        return True

    # =========================================================================
    # CACHE DE CURVAS DE INTERACCIÓN P-M
    # =========================================================================

    def store_interaction_curve(
        self,
        session_id: str,
        element_key: str,
        direction: str,
        curve: List[Any]
    ) -> bool:
        """
        Almacena una curva de interacción P-M para un elemento.

        La curva P-M es determinística para un elemento dado (depende solo de
        geometría y armadura), por lo que se puede reutilizar en múltiples
        verificaciones sin recalcular.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento (Story_Label)
            direction: 'primary' o 'secondary'
            curve: Lista de InteractionPoint

        Returns:
            True si se guardó correctamente
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return False

        if element_key not in parsed_data.interaction_curves:
            parsed_data.interaction_curves[element_key] = {}

        parsed_data.interaction_curves[element_key][direction] = curve
        return True

    def get_interaction_curve(
        self,
        session_id: str,
        element_key: str,
        direction: str = 'primary'
    ) -> Optional[List[Any]]:
        """
        Obtiene una curva de interacción P-M previamente calculada.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento
            direction: 'primary' o 'secondary'

        Returns:
            Lista de InteractionPoint o None si no existe
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None

        element_curves = parsed_data.interaction_curves.get(element_key)
        if not element_curves:
            return None

        return element_curves.get(direction)

    def clear_interaction_curves(self, session_id: str) -> bool:
        """
        Limpia todas las curvas de interacción de una sesión.

        Útil cuando se modifica la armadura y hay que recalcular.

        Args:
            session_id: ID de sesión

        Returns:
            True si se limpió correctamente
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return False

        parsed_data.interaction_curves.clear()
        return True

    # =========================================================================
    # VIGAS DE ACOPLE
    # =========================================================================

    def get_pier_Mpr_total(
        self,
        session_id: str,
        pier_key: str
    ) -> float:
        """
        Obtiene el Mpr total de vigas de acople para un pier.

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier

        Returns:
            Mpr total en kN-m (suma de vigas izq + der)
        """
        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return 0.0

        default_beam = parsed_data.default_coupling_beam
        if not default_beam:
            return 0.0

        # Buscar config específica o usar default (vigas en ambos lados)
        pier_config = parsed_data.pier_coupling_configs.get(pier_key)

        if pier_config:
            return pier_config.get_Mpr_total(default_beam)
        else:
            # Por defecto: viga genérica en ambos lados
            return 2 * default_beam.Mpr_max

    # =========================================================================
    # VIGAS CUSTOM Y RESOLUCIÓN
    # =========================================================================

    def resolve_beam_config(
        self,
        session_id: str,
        beam_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Resuelve la configuración de una viga desde el catálogo de la sesión.

        Args:
            session_id: ID de sesión
            beam_key: Clave de la viga ('none', 'generic', o key del catálogo)

        Returns:
            Dict con configuración de la viga, o None si es 'none' o 'generic'
        """
        if beam_key == 'none':
            return None
        if beam_key == 'generic':
            return None  # El servicio usará la viga genérica

        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return None

        beam = parsed_data.horizontal_elements.get(beam_key)
        if beam:
            return {
                'width': beam.width,
                'height': beam.depth,
                'ln': beam.length,
                'n_bars_top': beam.n_bars_top,
                'diameter_top': beam.diameter_top,
                'n_bars_bottom': beam.n_bars_bottom,
                'diameter_bottom': beam.diameter_bottom
            }
        return None

    def create_custom_beam(
        self,
        session_id: str,
        label: str,
        story: str,
        length: float = 3000,
        depth: float = 500,
        width: float = 200,
        fc: float = 28,
        n_bars_top: int = 3,
        n_bars_bottom: int = 3,
        diameter_top: int = 16,
        diameter_bottom: int = 16,
        stirrup_diameter: int = 10,
        stirrup_spacing: int = 150,
        n_stirrup_legs: int = 2
    ) -> Dict[str, Any]:
        """
        Crea una viga custom y la agrega al catálogo de la sesión.

        Args:
            session_id: ID de sesión
            label: Etiqueta de la viga
            story: Piso donde se ubica
            length: Longitud en mm
            depth: Altura en mm
            width: Ancho en mm
            fc: Resistencia del concreto en MPa
            n_bars_top: Número de barras superiores
            n_bars_bottom: Número de barras inferiores
            diameter_top: Diámetro barras superiores en mm
            diameter_bottom: Diámetro barras inferiores en mm
            stirrup_diameter: Diámetro de estribos en mm
            stirrup_spacing: Espaciamiento de estribos en mm
            n_stirrup_legs: Número de ramas del estribo

        Returns:
            Dict con 'success', 'beam_key' o 'error'
        """
        from ...domain.entities import HorizontalElement, HorizontalElementSource
        from ...domain.entities import HorizontalDiscreteReinforcement

        parsed_data = self.get_session(session_id)
        if not parsed_data:
            return {'success': False, 'error': 'Sesión no encontrada'}

        beam_key = f"{story}_{label}"

        if beam_key in parsed_data.horizontal_elements:
            return {
                'success': False,
                'error': f'Ya existe una viga con el nombre {label} en {story}'
            }

        beam = HorizontalElement(
            label=label,
            story=story,
            length=float(length),
            depth=float(depth),
            width=float(width),
            fc=float(fc),
            source=HorizontalElementSource.FRAME,
            is_custom=True,
            discrete_reinforcement=HorizontalDiscreteReinforcement(
                n_bars_top=int(n_bars_top),
                n_bars_bottom=int(n_bars_bottom),
                diameter_top=int(diameter_top),
                diameter_bottom=int(diameter_bottom),
            ),
            stirrup_diameter=int(stirrup_diameter),
            stirrup_spacing=int(stirrup_spacing),
            n_shear_legs=int(n_stirrup_legs)
        )

        parsed_data.horizontal_elements[beam_key] = beam

        return {'success': True, 'beam_key': beam_key}
