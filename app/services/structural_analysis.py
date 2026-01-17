# app/services/structural_analysis.py
"""
Servicio principal de analisis estructural.
Orquesta el parsing, calculo y generacion de resultados para todos los elementos.

Este servicio actua como orquestador, delegando a servicios especializados:
- FlexocompressionService: analisis de flexocompresion
- ShearService: verificacion de corte
- ElementOrchestrator: verificacion unificada de elementos (Pier, Column, Beam, DropBeam)

Referencias ACI 318-25:
- Capitulo 9: Vigas (Beams)
- Capitulo 10: Columnas (Columns)
- Capitulo 11: Muros (Walls)
- Capitulo 18: Estructuras resistentes a sismos
"""
from typing import Dict, List, Any, Optional
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import uuid
import math

from .parsing.session_manager import SessionManager
from .presentation.plot_generator import PlotGenerator
from .presentation.result_formatter import ResultFormatter
from .analysis.statistics_service import calculate_statistics
from .analysis.flexocompression_service import FlexocompressionService
from .analysis.shear_service import ShearService
from .analysis.reinforcement_update_service import ReinforcementUpdateService
from .presentation.modal_data_service import ElementDetailsService
from .analysis.element_orchestrator import ElementOrchestrator
from ..domain.entities import VerticalElement, ElementForces
from ..domain.flexure import InteractionDiagramService, SlendernessService, FlexureChecker, InteractionPoint
from ..domain.chapter18 import SeismicCategory


class StructuralAnalysisService:
    """
    Servicio principal de análisis estructural.

    Orquesta el análisis de todos los elementos estructurales:
    - Piers (muros)
    - Columns (columnas)
    - Beams (vigas)
    - DropBeams (vigas capitel)

    Responsabilidades:
    - Orquestar el flujo de análisis
    - Coordinar servicios de cálculo
    - Generar resultados y gráficos
    """

    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        flexocompression_service: Optional[FlexocompressionService] = None,
        shear_service: Optional[ShearService] = None,
        slenderness_service: Optional[SlendernessService] = None,
        interaction_service: Optional[InteractionDiagramService] = None,
        plot_generator: Optional[PlotGenerator] = None,
        details_formatter: Optional[ElementDetailsService] = None,
        element_orchestrator: Optional[ElementOrchestrator] = None
    ):
        """
        Inicializa el servicio de análisis.

        Args:
            session_manager: Gestor de sesiones (opcional)
            flexocompression_service: Servicio de flexocompresión (opcional)
            shear_service: Servicio de corte (opcional)
            slenderness_service: Servicio de esbeltez (opcional)
            interaction_service: Servicio de diagrama interaccion (opcional)
            plot_generator: Generador de graficos (opcional)
            details_formatter: Formateador de detalles de piers (opcional)
            element_orchestrator: Orquestador unificado de elementos (opcional)

        Nota: Los servicios se crean por defecto si no se pasan.
              Pasar None explícito permite inyectar mocks para testing.
        """
        self._session_manager = session_manager or SessionManager()
        self._flexo_service = flexocompression_service or FlexocompressionService()
        self._shear_service = shear_service or ShearService()
        self._slenderness_service = slenderness_service or SlendernessService()
        self._interaction_service = interaction_service or InteractionDiagramService()
        self._plot_generator = plot_generator or PlotGenerator()

        # Orquestador unificado de elementos: clasifica y delega al servicio apropiado
        # Verifica todos los elementos: Pier, Column, Beam, DropBeam
        self._orchestrator = element_orchestrator or ElementOrchestrator()

        self._details_formatter = details_formatter or ElementDetailsService(
            session_manager=self._session_manager,
            orchestrator=self._orchestrator,
            flexocompression_service=self._flexo_service,
            shear_service=self._shear_service,
            slenderness_service=self._slenderness_service,
            plot_generator=self._plot_generator
        )

    # =========================================================================
    # Helpers - Generación de Datos de Interacción
    # =========================================================================

    def _generate_interaction_data(
        self,
        pier: VerticalElement,
        apply_slenderness: bool = False,
        direction: str = 'primary'
    ) -> tuple:
        """
        Genera steel_layers, interaction_points y phi_Mn_0.

        Args:
            pier: Elemento vertical a analizar
            apply_slenderness: Si aplicar efectos de esbeltez
            direction: 'primary' (M3, eje fuerte) o 'secondary' (M2, eje debil)

        Returns:
            (steel_layers, interaction_points, phi_Mn_0)
        """
        steel_layers = pier.get_steel_layers(direction)
        interaction_points, _ = self._flexo_service.generate_interaction_curve(
            pier, direction=direction, apply_slenderness=apply_slenderness, k=0.8
        )

        # Obtener phi_Mn_0 directamente del FlexureChecker
        phi_Mn_0 = FlexureChecker.get_phi_Mn_at_P0(interaction_points)

        return steel_layers, interaction_points, phi_Mn_0

    # =========================================================================
    # Validación (delegada a SessionManager)
    # =========================================================================

    def _validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Valida que la sesión existe."""
        return self._session_manager.validate_session(session_id)

    def _validate_pier(self, session_id: str, pier_key: str) -> Optional[Dict[str, Any]]:
        """Valida que el pier existe en la sesión."""
        return self._session_manager.validate_pier(session_id, pier_key)

    # =========================================================================
    # API Pública - Gestión de Sesiones
    # =========================================================================

    def parse_excel(self, file_content: bytes, session_id: str, hn_ft: Optional[float] = None) -> Dict[str, Any]:
        """Parsea Excel de ETABS y crea una sesión."""
        return self._session_manager.create_session(file_content, session_id, hn_ft=hn_ft)

    def parse_excel_with_progress(
        self,
        file_content: bytes,
        session_id: str,
        hn_ft: Optional[float] = None,
        merge: bool = False,
        filename: str = "unknown.xlsx"
    ):
        """
        Parsea Excel de ETABS con progreso SSE.

        Nuevo flujo multi-archivo:
        1. Acumular tablas del archivo
        2. Fusionar tablas acumuladas
        3. Procesar elementos desde tablas fusionadas

        Args:
            file_content: Contenido binario del Excel
            session_id: ID de sesión
            hn_ft: Altura del edificio en pies (opcional)
            merge: Si True y la sesión existe, combina datos en vez de sobrescribir
            filename: Nombre del archivo para logging
        """
        # Fase 1: Acumular tablas del archivo
        yield {
            'type': 'progress',
            'phase': 'extracting',
            'current': 0,
            'total': 1,
            'element': 'Extrayendo tablas del Excel...'
        }

        accum_result = self._session_manager.accumulate_tables(file_content, session_id, filename=filename)
        if not accum_result.get('success'):
            yield {'type': 'error', 'message': accum_result.get('error', 'Error acumulando tablas')}
            return

        tables_found = accum_result.get('tables_found', [])
        yield {
            'type': 'progress',
            'phase': 'extracted',
            'current': 1,
            'total': 1,
            'element': f'Encontradas {len(tables_found)} tablas'
        }

        # Fase 2: Procesar sesión (fusionar tablas y parsear elementos)
        yield {
            'type': 'progress',
            'phase': 'processing',
            'current': 0,
            'total': 1,
            'element': 'Procesando elementos...'
        }

        process_result = self._session_manager.process_session(session_id, hn_ft=hn_ft)
        if not process_result.get('success'):
            yield {'type': 'error', 'message': process_result.get('error', 'Error procesando sesión')}
            return

        yield {
            'type': 'complete',
            'result': {
                'success': True,
                'session_id': session_id,
                'summary': process_result.get('summary', {}),
                'merged': merge
            }
        }

    def clear_session(self, session_id: str) -> bool:
        """Limpia una sesión del cache."""
        return self._session_manager.clear_session(session_id)

    # =========================================================================
    # API Pública - Análisis Completo
    # =========================================================================

    def analyze(
        self,
        session_id: str,
        pier_updates: Optional[List[Dict]] = None,
        column_updates: Optional[List[Dict]] = None,
        beam_updates: Optional[List[Dict]] = None,
        drop_beam_updates: Optional[List[Dict]] = None,
        generate_plots: bool = True,
        moment_axis: str = 'M3',
        angle_deg: float = 0,
        materials_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el análisis estructural completo.

        Este método es un wrapper que consume analyze_with_progress() y retorna
        el resultado final. Usa analyze_with_progress() directamente para SSE.

        Args:
            session_id: ID de sesión
            pier_updates: Actualizaciones de armadura de piers opcionales
            column_updates: Actualizaciones de armadura de columnas opcionales
            beam_updates: Actualizaciones de armadura de vigas opcionales
            drop_beam_updates: Actualizaciones de armadura de vigas capitel opcionales
            generate_plots: Generar gráficos P-M
            moment_axis: Plano de momento ('M2', 'M3', 'combined', 'SRSS')
            angle_deg: Ángulo para vista combinada
            materials_config: Configuración de materiales con lambda por tipo

        Returns:
            Diccionario con estadísticas y resultados
        """
        # Consumir el generador y retornar el resultado final
        result = None
        for event in self.analyze_with_progress(
            session_id=session_id,
            pier_updates=pier_updates,
            column_updates=column_updates,
            beam_updates=beam_updates,
            drop_beam_updates=drop_beam_updates,
            generate_plots=generate_plots,
            moment_axis=moment_axis,
            angle_deg=angle_deg,
            materials_config=materials_config
        ):
            if event.get('type') == 'complete':
                result = event.get('result')
            elif event.get('type') == 'error':
                return {'success': False, 'error': event.get('message')}

        return result or {'success': False, 'error': 'No result generated'}

    def _get_lambda_for_element(
        self,
        element,
        materials_config: Dict[str, Any]
    ) -> float:
        """
        Obtiene el factor lambda para un elemento basado en su material.

        Args:
            element: Pier, Column u otro elemento con atributos 'material' y 'fc'
            materials_config: Config de materiales {name: {fc, type, lambda}}

        Returns:
            Factor lambda (1.0 para concreto normal)
        """
        # Buscar por nombre de material si está definido
        material_name = getattr(element, 'material', None)
        fc = element.fc

        # Intentar buscar por nombre exacto
        if material_name and material_name in materials_config:
            mat_info = materials_config[material_name]
            return mat_info.get('lambda', 1.0)

        # Intentar buscar por nombre aproximado basado en f'c
        approx_name = f"C{int(round(fc))}"
        if approx_name in materials_config:
            mat_info = materials_config[approx_name]
            return mat_info.get('lambda', 1.0)

        # Default: concreto normal
        return 1.0

    def _analyze_element(
        self,
        key: str,
        element,
        forces,
        materials_config: Optional[Dict] = None,
        continuity_info=None,
        hn_ft: Optional[float] = None,
        seismic_category: SeismicCategory = SeismicCategory.SPECIAL,
        coupling_config=None,
        interaction_curve=None
    ) -> Dict[str, Any]:
        """
        Analiza un elemento individual usando ElementOrchestrator.

        Método genérico que funciona con Pier, Column, Beam, DropBeam.
        Centraliza la lógica de verificación para evitar duplicación.

        Args:
            key: Clave del elemento (Story_Label)
            element: Elemento estructural
            forces: Fuerzas del elemento
            materials_config: Config de materiales para lambda (opcional)
            continuity_info: Info de continuidad para piers (opcional)
            hn_ft: Altura del edificio en pies (opcional)
            seismic_category: Categoría sísmica (SPECIAL, INTERMEDIATE, ORDINARY)
            coupling_config: Configuración de vigas de acople (PierCouplingConfig)
            interaction_curve: Curva P-M pre-calculada (optimización)

        Returns:
            Diccionario formateado para la UI
        """
        # Determinar lambda_factor solo si hay materials_config
        lambda_factor = 1.0
        if materials_config:
            lambda_factor = self._get_lambda_for_element(element, materials_config)

        # Obtener hwcs de continuity_info si existe
        hwcs = continuity_info.hwcs if continuity_info else None

        # Verificar usando el orquestador unificado
        # Pasar curva pre-calculada si está disponible
        result = self._orchestrator.verify(
            element=element,
            forces=forces,
            lambda_factor=lambda_factor,
            category=seismic_category,
            hwcs=hwcs,
            hn_ft=hn_ft,
            interaction_curve=interaction_curve,
        )

        # Formatear resultado
        return ResultFormatter.format_any_element(
            element, result, key,
            continuity_info=continuity_info,
            coupling_config=coupling_config
        )

    def _calculate_statistics(
        self,
        pier_results: List,
        column_results: List,
        beam_results: List,
        drop_beam_results: List
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas de todos los tipos de elementos.

        Returns:
            Diccionario con estadísticas por tipo de elemento
        """
        total = len(pier_results)
        ok = sum(1 for r in pier_results if r.get('overall_status') == 'OK')
        statistics = {
            'total': total,
            'ok': ok,
            'fail': total - ok,
            'pass_rate': round(ok / total * 100, 1) if total > 0 else 0,
        }

        if column_results:
            statistics['columns'] = calculate_statistics(column_results)

        if beam_results:
            statistics['beams'] = calculate_statistics(beam_results)

        if drop_beam_results:
            statistics['drop_beams'] = calculate_statistics(drop_beam_results)

        return statistics

    def analyze_with_progress(
        self,
        session_id: str,
        pier_updates: Optional[List[Dict]] = None,
        column_updates: Optional[List[Dict]] = None,
        beam_updates: Optional[List[Dict]] = None,
        drop_beam_updates: Optional[List[Dict]] = None,
        generate_plots: bool = True,
        moment_axis: str = 'M3',
        angle_deg: float = 0,
        materials_config: Optional[Dict] = None,
        seismic_category: str = 'SPECIAL'
    ):
        """
        Ejecuta el análisis estructural con progreso (generador para SSE).

        Args:
            pier_updates: Actualizaciones de armadura de piers/muros
            column_updates: Actualizaciones de armadura de columnas
            beam_updates: Actualizaciones de armadura de vigas
            drop_beam_updates: Actualizaciones de armadura de vigas capitel
            materials_config: Configuración de materiales con lambda por tipo de concreto.
                Format: {material_name: {fc, type, lambda}, ...}
            seismic_category: Categoría sísmica ('SPECIAL', 'INTERMEDIATE', 'ORDINARY')

        Yields:
            Dict con eventos de progreso:
            - {"type": "progress", "current": 1, "total": 100, "element": "P1-A1"}
            - {"type": "complete", "result": {...}}
            - {"type": "error", "message": "..."}
        """
        materials_config = materials_config or {}

        # Convertir string a enum de categoría sísmica
        # El frontend envía 'SPECIAL', 'INTERMEDIATE', 'ORDINARY'
        category_map = {
            'SPECIAL': SeismicCategory.SPECIAL,
            'INTERMEDIATE': SeismicCategory.INTERMEDIATE,
            'ORDINARY': SeismicCategory.ORDINARY,
        }
        category_enum = category_map.get(seismic_category.upper(), SeismicCategory.SPECIAL)

        # Validar sesión
        error = self._validate_session(session_id)
        if error:
            yield {"type": "error", "message": error.get('error', 'Error de sesión')}
            return

        # Obtener datos de la sesión
        parsed_data = self._session_manager.get_session(session_id)

        # Aplicar todas las actualizaciones de armadura
        ReinforcementUpdateService.apply_all_updates(
            parsed_data,
            pier_updates=pier_updates,
            column_updates=column_updates,
            beam_updates=beam_updates,
            drop_beam_updates=drop_beam_updates,
        )

        # Limpiar cache de análisis previo (se recalculará todo)
        self._session_manager.clear_analysis_cache(session_id)

        # Separar elementos por tipo usando la nueva arquitectura unificada
        from ..domain.entities import VerticalElementSource, HorizontalElementSource

        vertical_elements = parsed_data.vertical_elements or {}
        horizontal_elements = parsed_data.horizontal_elements or {}

        # Separar verticales por source
        piers = {k: v for k, v in vertical_elements.items() if v.source == VerticalElementSource.PIER}
        columns = {k: v for k, v in vertical_elements.items() if v.source == VerticalElementSource.FRAME}

        # Separar horizontales por source
        beams = {k: v for k, v in horizontal_elements.items() if v.source != HorizontalElementSource.DROP_BEAM}
        drop_beams = {k: v for k, v in horizontal_elements.items() if v.source == HorizontalElementSource.DROP_BEAM}

        total_piers = len(piers)
        total_columns = len(columns)
        total_beams = len(beams)
        total_drop_beams = len(drop_beams)
        total_elements = total_piers + total_columns + total_beams + total_drop_beams

        # Obtener hn_ft del edificio
        hn_ft = parsed_data.building_info.hn_ft if parsed_data.building_info else None

        # =====================================================================
        # PRE-GENERACIÓN DE CURVAS P-M (OPTIMIZACIÓN)
        # Las curvas P-M son determinísticas por elemento. Se generan UNA VEZ
        # y se reutilizan en todo el análisis.
        # =====================================================================
        yield {
            "type": "progress",
            "current": 0,
            "total": total_elements,
            "pier": "Generando curvas de interacción P-M..."
        }

        # Pre-generar curvas para elementos verticales (piers y columnas)
        for key, element in vertical_elements.items():
            # Solo generar si no existe en cache
            if not self._session_manager.get_interaction_curve(session_id, key, 'primary'):
                try:
                    curve_primary, _ = self._flexo_service.generate_interaction_curve(
                        element, direction='primary', use_cache=False
                    )
                    self._session_manager.store_interaction_curve(
                        session_id, key, 'primary', curve_primary
                    )
                except Exception:
                    pass  # Continuar si falla un elemento

            if not self._session_manager.get_interaction_curve(session_id, key, 'secondary'):
                try:
                    curve_secondary, _ = self._flexo_service.generate_interaction_curve(
                        element, direction='secondary', use_cache=False
                    )
                    self._session_manager.store_interaction_curve(
                        session_id, key, 'secondary', curve_secondary
                    )
                except Exception:
                    pass

        # Pre-generar curvas para vigas (solo primary)
        for key, element in horizontal_elements.items():
            if not self._session_manager.get_interaction_curve(session_id, key, 'primary'):
                try:
                    curve_primary, _ = self._flexo_service.generate_interaction_curve(
                        element, direction='primary', use_cache=False
                    )
                    self._session_manager.store_interaction_curve(
                        session_id, key, 'primary', curve_primary
                    )
                except Exception:
                    pass

        # =====================================================================
        # ANÁLISIS PARALELO - Usa curvas pre-generadas
        # =====================================================================
        import os
        vertical_forces = parsed_data.vertical_forces or {}
        horizontal_forces = parsed_data.horizontal_forces or {}

        # Configuración de paralelización AGRESIVA
        MAX_WORKERS = (os.cpu_count() or 8) * 4  # 96 workers - compensar GIL
        PROGRESS_INTERVAL = 200  # Solo para progreso, sin batching real

        # Preparar todas las tareas de análisis (con curvas P-M pre-calculadas)
        all_tasks = []

        # Tareas de PIERS (incluir curva P-M pre-calculada)
        for key, pier in piers.items():
            continuity_info = None
            if parsed_data.continuity_info and key in parsed_data.continuity_info:
                continuity_info = parsed_data.continuity_info[key]
            coupling_config = parsed_data.pier_coupling_configs.get(key)
            # Obtener curva pre-calculada del cache
            interaction_curve = self._session_manager.get_interaction_curve(
                session_id, key, 'primary'
            )

            all_tasks.append({
                'type': 'pier',
                'key': key,
                'element': pier,
                'forces': vertical_forces.get(key),
                'materials_config': materials_config,
                'continuity_info': continuity_info,
                'hn_ft': hn_ft,
                'seismic_category': category_enum,
                'coupling_config': coupling_config,
                'interaction_curve': interaction_curve,
                'label': f"Pier: {pier.story} - {pier.label}"
            })

        # Tareas de COLUMNAS (incluir curva P-M pre-calculada)
        for key, column in columns.items():
            interaction_curve = self._session_manager.get_interaction_curve(
                session_id, key, 'primary'
            )
            all_tasks.append({
                'type': 'column',
                'key': key,
                'element': column,
                'forces': vertical_forces.get(key),
                'seismic_category': category_enum,
                'interaction_curve': interaction_curve,
                'label': f"Columna: {column.story} - {column.label}"
            })

        # Tareas de VIGAS (incluir curva P-M pre-calculada)
        for key, beam in beams.items():
            interaction_curve = self._session_manager.get_interaction_curve(
                session_id, key, 'primary'
            )
            all_tasks.append({
                'type': 'beam',
                'key': key,
                'element': beam,
                'forces': horizontal_forces.get(key),
                'seismic_category': category_enum,
                'interaction_curve': interaction_curve,
                'label': f"Viga: {beam.story} - {beam.label}"
            })

        # Tareas de VIGAS CAPITEL (incluir curva P-M pre-calculada)
        for key, drop_beam in drop_beams.items():
            interaction_curve = self._session_manager.get_interaction_curve(
                session_id, key, 'primary'
            )
            all_tasks.append({
                'type': 'drop_beam',
                'key': key,
                'element': drop_beam,
                'forces': horizontal_forces.get(key),
                'seismic_category': category_enum,
                'interaction_curve': interaction_curve,
                'label': f"V. Capitel: {drop_beam.story} - {drop_beam.label}"
            })

        # Función worker para ejecutar en threads
        def analyze_task(task):
            """Analiza un elemento y retorna resultado con metadata."""
            formatted = self._analyze_element(
                task['key'],
                task['element'],
                task['forces'],
                materials_config=task.get('materials_config'),
                continuity_info=task.get('continuity_info'),
                hn_ft=task.get('hn_ft'),
                seismic_category=task.get('seismic_category'),
                coupling_config=task.get('coupling_config'),
                interaction_curve=task.get('interaction_curve')
            )
            return {
                'type': task['type'],
                'key': task['key'],
                'result': formatted,
                'label': task['label']
            }

        # Resultados por tipo
        pier_results = []
        column_results = []
        beam_results = []
        drop_beam_results = []

        # ULTRA-AGRESIVO: Lanzar TODOS los elementos en paralelo sin batching
        completed = 0
        last_progress = 0
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Enviar TODAS las tareas de una vez
            futures = {executor.submit(analyze_task, task): task for task in all_tasks}

            # Recoger resultados a medida que terminan
            for future in as_completed(futures):
                result = future.result()
                completed += 1

                # Clasificar resultado
                if result['type'] == 'pier':
                    pier_results.append(result['result'])
                elif result['type'] == 'column':
                    column_results.append(result['result'])
                elif result['type'] == 'beam':
                    beam_results.append(result['result'])
                elif result['type'] == 'drop_beam':
                    drop_beam_results.append(result['result'])

                # Guardar en cache
                self._session_manager.store_analysis_result(
                    session_id, result['key'], result['result']
                )

                # Emitir progreso cada PROGRESS_INTERVAL elementos
                if completed - last_progress >= PROGRESS_INTERVAL or completed == total_elements:
                    last_progress = completed
                    yield {
                        "type": "progress",
                        "current": completed,
                        "total": total_elements,
                        "pier": f"Procesando {completed} de {total_elements}"
                    }

        # Calcular estadísticas
        statistics = self._calculate_statistics(
            pier_results, column_results, beam_results, drop_beam_results
        )

        # Unificar resultados
        all_results = pier_results + column_results

        # Enviar resultado completo
        yield {
            "type": "complete",
            "result": {
                'success': True,
                'statistics': statistics,
                'results': all_results,
                'beam_results': beam_results,
                'drop_beam_results': drop_beam_results,
                'summary_plot': None
            }
        }

    # =========================================================================
    # API Pública - Análisis por Combinación
    # =========================================================================

    def get_pier_combinations(
        self,
        session_id: str,
        pier_key: str
    ) -> Dict[str, Any]:
        """
        Obtiene las combinaciones de carga de un pier con sus FS calculados.

        Usa ElementOrchestrator.verify_all_combinations() para centralizar
        la lógica de verificación.
        """
        # Validar pier
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        if pier_forces is None:
            return {'success': False, 'error': f'Forces not found for pier: {pier_key}'}

        # Usar orquestador para verificar todas las combinaciones
        combination_results = self._orchestrator.verify_all_combinations(
            element=pier,
            forces=pier_forces,
            lambda_factor=1.0,
            apply_slenderness=True,
        )

        # Convertir a formato de diccionario para la UI
        combinations_with_fs = [result.to_dict() for result in combination_results]

        # Obtener phi_Mn_0 para verificación de capacidad
        _, interaction_points, phi_Mn_0 = self._generate_interaction_data(
            pier, apply_slenderness=True
        )

        # Verificación de capacidad (muro fuerte - viga débil)
        # phi_Mn_muro >= 1.2 × Mpr_vigas
        capacity_check = None
        Mpr_total = self._session_manager.get_pier_Mpr_total(session_id, pier_key)
        if Mpr_total > 0:
            # Convertir phi_Mn_0 de tonf-m a kN-m para comparar (1 tonf-m ≈ 9.81 kN-m)
            phi_Mn_kNm = phi_Mn_0 * 9.80665
            Mpr_required = 1.2 * Mpr_total
            capacity_ratio = phi_Mn_kNm / Mpr_required if Mpr_required > 0 else float('inf')
            capacity_check = {
                'phi_Mn_wall_kNm': round(phi_Mn_kNm, 1),
                'Mpr_beams_kNm': round(Mpr_total, 1),
                'required_kNm': round(Mpr_required, 1),
                'ratio': round(capacity_ratio, 2),
                'is_ok': capacity_ratio >= 1.0,
                'status': 'OK' if capacity_ratio >= 1.0 else 'NO OK'
            }

        return {
            'success': True,
            'pier_key': pier_key,
            'combinations': combinations_with_fs,
            'unique_angles': pier_forces.get_unique_angles(),
            'total_combinations': len(pier_forces.combinations),
            'capacity_check': capacity_check
        }

    def analyze_single_combination(
        self,
        session_id: str,
        pier_key: str,
        combination_index: int,
        generate_plot: bool = True
    ) -> Dict[str, Any]:
        """
        Analiza un pier para una combinación específica.

        Usa ElementOrchestrator.verify_combination() para la verificación.
        """
        # Validar pier
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        if not pier_forces or combination_index >= len(pier_forces.combinations):
            return {'success': False, 'error': 'Invalid combination index'}

        # Obtener la combinación
        combo = pier_forces.combinations[combination_index]
        angle_deg = combo.moment_angle_deg

        # Generar curvas de interacción para M3 (primary) y M2 (secondary)
        _, points_M3, _ = self._generate_interaction_data(pier, direction='primary')
        _, points_M2, _ = self._generate_interaction_data(pier, direction='secondary')

        # Interpolar la curva al ángulo específico de la combinación
        # Fórmula: Mn(θ) = Mn3 * cos(θ) + Mn2 * sin(θ)
        angle_rad = math.radians(abs(angle_deg))
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)

        # Crear funciones de interpolación para obtener Mn dado Pn
        # Ordenar por phi_Pn para interpolar correctamente
        points_M3_sorted = sorted(points_M3, key=lambda p: p.phi_Pn, reverse=True)
        points_M2_sorted = sorted(points_M2, key=lambda p: p.phi_Pn, reverse=True)

        def interpolate_Mn_at_Pn(points: list, target_Pn: float) -> tuple:
            """Interpola Mn, phi, c, epsilon_t para un Pn dado."""
            # Buscar el segmento donde cae target_Pn
            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i + 1]
                if p1.phi_Pn >= target_Pn >= p2.phi_Pn:
                    # Interpolación lineal
                    if abs(p1.phi_Pn - p2.phi_Pn) < 0.001:
                        ratio = 0.5
                    else:
                        ratio = (p1.phi_Pn - target_Pn) / (p1.phi_Pn - p2.phi_Pn)
                    Mn = p1.phi_Mn + ratio * (p2.phi_Mn - p1.phi_Mn)
                    phi = p1.phi + ratio * (p2.phi - p1.phi)
                    c = p1.c + ratio * (p2.c - p1.c) if p1.c != float('inf') and p2.c != float('inf') else p1.c
                    eps = p1.epsilon_t + ratio * (p2.epsilon_t - p1.epsilon_t) if p1.epsilon_t != float('inf') and p2.epsilon_t != float('inf') else p1.epsilon_t
                    return Mn, phi, c, eps
            # Si está fuera del rango, usar el extremo más cercano
            if target_Pn > points[0].phi_Pn:
                return points[0].phi_Mn, points[0].phi, points[0].c, points[0].epsilon_t
            return points[-1].phi_Mn, points[-1].phi, points[-1].c, points[-1].epsilon_t

        # Usar los valores de phi_Pn de la curva M3 como referencia
        interpolated_points = []
        for p3 in points_M3_sorted:
            target_Pn = p3.phi_Pn

            # Obtener Mn de M3 (ya lo tenemos)
            Mn3 = p3.phi_Mn
            phi3 = p3.phi

            # Interpolar Mn de M2 al mismo Pn
            Mn2, phi2, c2, eps2 = interpolate_Mn_at_Pn(points_M2_sorted, target_Pn)

            # Interpolar según ángulo
            phi_Mn_interp = Mn3 * cos_angle + Mn2 * sin_angle
            phi_interp = min(phi3, phi2)

            # Calcular Mn nominal (sin phi)
            Mn_interp = phi_Mn_interp / phi_interp if phi_interp > 0 else 0

            # c y epsilon_t del punto M3 (aproximación razonable)
            c_interp = p3.c
            epsilon_t_interp = p3.epsilon_t

            interpolated_points.append(InteractionPoint(
                Pn=p3.Pn,
                Mn=Mn_interp,
                phi=phi_interp,
                phi_Pn=target_Pn,
                phi_Mn=phi_Mn_interp,
                c=c_interp,
                epsilon_t=epsilon_t_interp
            ))

        # Usar la curva interpolada para el ángulo de esta combinación
        interaction_points = interpolated_points
        design_curve = self._interaction_service.get_design_curve(interaction_points)

        # Usar orquestador para verificar la combinación
        result = self._orchestrator.verify_combination(
            element=pier,
            combination=combo,
            index=combination_index,
            interaction_points=interaction_points,
        )
        flexure_sf = result.flexure_sf
        flexure_status = result.flexure_status

        # Generar gráfico - solo mostrar el punto de ESTA combinación
        pm_plot = ""
        if generate_plot:
            # Solo el punto de la combinación actual (no todos los puntos)
            # El punto está en el plano del ángulo de esta combinación
            # Formato: (Pu, Mu, combo_name)
            combo_label = f"{combo.name} ({combo.location})"
            combo_point = [(result.P, combo.moment_resultant, combo_label)]
            pm_plot = self._plot_generator.generate_pm_diagram(
                capacity_curve=design_curve,
                demand_points=combo_point,
                pier_label=f"{pier.story} - {pier.label}",
                safety_factor=flexure_sf,
                moment_axis='combined',
                angle_deg=angle_deg
            )

        return {
            'success': True,
            'pier_key': pier_key,
            'combination': {
                'index': combination_index,
                'name': combo.name,
                'location': combo.location,
                'step_type': combo.step_type,
                'P': result.P,
                'M2': combo.M2,
                'M3': combo.M3,
                'M_resultant': combo.moment_resultant,
                'angle_deg': angle_deg
            },
            'safety_factor': round(flexure_sf, 3) if flexure_sf < 100 else '>100',
            'status': flexure_status,
            'pm_plot': pm_plot
        }

    # =========================================================================
    # Capacidades (delegado a PierDetailsFormatter)
    # =========================================================================

    def get_section_diagram(
        self,
        session_id: str,
        pier_key: str,
        proposed_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Genera un diagrama de la sección transversal del pier."""
        return self._details_formatter.get_section_diagram(
            session_id, pier_key, proposed_config
        )

    def get_element_capacities(
        self,
        session_id: str,
        element_key: str,
        element_type: str = 'pier'
    ) -> Dict[str, Any]:
        """
        Obtiene capacidades de cualquier tipo de elemento estructural.

        Args:
            session_id: ID de sesión
            element_key: Clave del elemento (Story_Label)
            element_type: 'pier', 'column', 'beam', 'drop_beam'

        Returns:
            Dict con información completa del elemento estilo ETABS
        """
        return self._details_formatter.get_element_capacities(
            session_id, element_key, element_type
        )

    def get_combination_details(
        self,
        session_id: str,
        pier_key: str,
        combo_index: int
    ) -> Dict[str, Any]:
        """Obtiene los detalles de diseño para una combinación específica."""
        return self._details_formatter.get_combination_details(
            session_id, pier_key, combo_index
        )

    # =========================================================================
    # API Publica - Configuracion de Sesion
    # =========================================================================

    def set_default_coupling_beam(
        self,
        session_id: str,
        width: float,
        height: float,
        ln: float,
        n_bars_top: int,
        diameter_top: int,
        n_bars_bottom: int,
        diameter_bottom: int
    ) -> None:
        """Configura la viga de acople por defecto para una sesion."""
        self._session_manager.set_default_coupling_beam(
            session_id=session_id,
            width=width,
            height=height,
            ln=ln,
            n_bars_top=n_bars_top,
            diameter_top=diameter_top,
            n_bars_bottom=n_bars_bottom,
            diameter_bottom=diameter_bottom
        )

    def set_pier_coupling_config(
        self,
        session_id: str,
        pier_key: str,
        has_beam_left: bool = True,
        has_beam_right: bool = True,
        beam_left_config: Optional[Dict] = None,
        beam_right_config: Optional[Dict] = None
    ) -> None:
        """Configura las vigas de acople para un pier específico."""
        self._session_manager.set_pier_coupling_config(
            session_id=session_id,
            pier_key=pier_key,
            has_beam_left=has_beam_left,
            has_beam_right=has_beam_right,
            beam_left_config=beam_left_config,
            beam_right_config=beam_right_config
        )

    def resolve_beam_config(
        self,
        session_id: str,
        beam_key: str
    ) -> Optional[Dict[str, Any]]:
        """Delega a SessionManager.resolve_beam_config()."""
        return self._session_manager.resolve_beam_config(session_id, beam_key)

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
        """Delega a SessionManager.create_custom_beam()."""
        return self._session_manager.create_custom_beam(
            session_id=session_id,
            label=label,
            story=story,
            length=length,
            depth=depth,
            width=width,
            fc=fc,
            n_bars_top=n_bars_top,
            n_bars_bottom=n_bars_bottom,
            diameter_top=diameter_top,
            diameter_bottom=diameter_bottom,
            stirrup_diameter=stirrup_diameter,
            stirrup_spacing=stirrup_spacing,
            n_stirrup_legs=n_stirrup_legs
        )

    def analyze_single_pier(
        self,
        session_id: str,
        pier_key: str,
        generate_plot: bool = True
    ) -> Dict[str, Any]:
        """
        Re-analiza un pier individual y retorna su resultado.

        Args:
            session_id: ID de sesión
            pier_key: Clave del pier
            generate_plot: Generar gráfico P-M

        Returns:
            Diccionario con el resultado del pier (formato VerificationResult.to_dict())
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        parsed_data = self._session_manager.get_session(session_id)
        pier = parsed_data.vertical_elements.get(pier_key)
        pier_forces = parsed_data.vertical_forces.get(pier_key)

        # Obtener hwcs y hn_ft
        hwcs = None
        hn_ft = None
        continuity_info = None
        if parsed_data.continuity_info and pier_key in parsed_data.continuity_info:
            continuity_info = parsed_data.continuity_info[pier_key]
            hwcs = continuity_info.hwcs
        if parsed_data.building_info:
            hn_ft = parsed_data.building_info.hn_ft

        result = self._orchestrator.verify(
            pier,
            pier_forces,
            hwcs=hwcs,
            hn_ft=hn_ft
        )

        return ResultFormatter.format_any_element(
            pier, result, pier_key, continuity_info
        )

    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de una sesion."""
        return self._session_manager.get_session(session_id)

    # =========================================================================
    # API Pública - Vigas Capitel (Drop Beams)
    # =========================================================================

    def generate_drop_beam_section_diagram(
        self,
        session_id: str,
        drop_beam_key: str
    ) -> Dict[str, Any]:
        """
        Genera un diagrama de la sección transversal de una viga capitel.

        Args:
            session_id: ID de sesión
            drop_beam_key: Clave de la viga capitel

        Returns:
            Diccionario con success y plot (imagen en base64)
        """
        parsed_data = self._session_manager.get_session(session_id)
        if not parsed_data:
            return {
                'success': False,
                'error': f'Sesión no encontrada: {session_id}'
            }

        drop_beam = parsed_data.horizontal_elements.get(drop_beam_key)
        if not drop_beam:
            return {
                'success': False,
                'error': f'Viga capitel no encontrada: {drop_beam_key}'
            }

        plot = self._plot_generator.generate_drop_beam_section_diagram(drop_beam)
        return {
            'success': True,
            'plot': plot
        }

    # =========================================================================
    # API Pública - Tablas ETABS (Vista de verificación)
    # =========================================================================

    def get_raw_tables(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene las tablas crudas de ETABS de una sesión.

        Retorna las tablas extraídas del Excel para que el usuario pueda
        verificar que los datos se leyeron correctamente.

        Args:
            session_id: ID de sesión

        Returns:
            Dict con tablas en formato JSON-serializable, o None si no existe
        """
        return self._session_manager.get_raw_tables(session_id)

