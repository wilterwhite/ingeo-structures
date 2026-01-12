# app/services/structural_analysis.py
"""
Servicio principal de analisis estructural.
Orquesta el parsing, calculo y generacion de resultados para todos los elementos.

Este servicio actua como orquestador, delegando a servicios especializados:
- FlexocompressionService: analisis de flexocompresion
- ShearService: verificacion de corte
- StatisticsService: estadisticas y graficos resumen
- ElementOrchestrator: verificacion unificada de elementos (Pier, Column, Beam, DropBeam)

Referencias ACI 318-25:
- Capitulo 9: Vigas (Beams)
- Capitulo 10: Columnas (Columns)
- Capitulo 11: Muros (Walls)
- Capitulo 18: Estructuras resistentes a sismos
"""
from typing import Dict, List, Any, Optional
import uuid

from .parsing.session_manager import SessionManager
from .presentation.plot_generator import PlotGenerator
from .presentation.result_formatter import ResultFormatter
from .analysis.flexocompression_service import FlexocompressionService
from .analysis.shear_service import ShearService
from .analysis.statistics_service import StatisticsService
from .analysis.proposal_service import ProposalService
from .analysis.reinforcement_update_service import ReinforcementUpdateService
from .analysis.element_details_service import ElementDetailsService
from .analysis.element_orchestrator import ElementOrchestrator
from .analysis.slab_service import SlabService
from .analysis.punching_service import PunchingService
from ..domain.entities import Pier, PierForces
from ..domain.flexure import InteractionDiagramService, SlendernessService, FlexureChecker
from ..domain.chapter18 import SeismicCategory


class StructuralAnalysisService:
    """
    Servicio principal de análisis estructural.

    Orquesta el análisis de todos los elementos estructurales:
    - Piers (muros)
    - Columns (columnas)
    - Beams (vigas)
    - Slabs (losas)

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
        statistics_service: Optional[StatisticsService] = None,
        slenderness_service: Optional[SlendernessService] = None,
        interaction_service: Optional[InteractionDiagramService] = None,
        plot_generator: Optional[PlotGenerator] = None,
        proposal_service: Optional[ProposalService] = None,
        details_formatter: Optional[ElementDetailsService] = None,
        element_orchestrator: Optional[ElementOrchestrator] = None,
        slab_service: Optional[SlabService] = None,
        punching_service: Optional[PunchingService] = None
    ):
        """
        Inicializa el servicio de análisis.

        Args:
            session_manager: Gestor de sesiones (opcional)
            flexocompression_service: Servicio de flexocompresión (opcional)
            shear_service: Servicio de corte (opcional)
            statistics_service: Servicio de estadisticas (opcional)
            slenderness_service: Servicio de esbeltez (opcional)
            interaction_service: Servicio de diagrama interaccion (opcional)
            plot_generator: Generador de graficos (opcional)
            proposal_service: Servicio de propuestas de diseño (opcional)
            details_formatter: Formateador de detalles de piers (opcional)
            element_orchestrator: Orquestador unificado de elementos (opcional)
            slab_service: Servicio de losas (opcional)
            punching_service: Servicio de punzonamiento (opcional)

        Nota: Los servicios se crean por defecto si no se pasan.
              Pasar None explícito permite inyectar mocks para testing.
        """
        self._session_manager = session_manager or SessionManager()
        self._flexo_service = flexocompression_service or FlexocompressionService()
        self._shear_service = shear_service or ShearService()
        self._statistics_service = statistics_service or StatisticsService()
        self._slenderness_service = slenderness_service or SlendernessService()
        self._interaction_service = interaction_service or InteractionDiagramService()
        self._plot_generator = plot_generator or PlotGenerator()
        self._slab_service = slab_service or SlabService()
        self._punching_service = punching_service or PunchingService()

        # Orquestador unificado de elementos: clasifica y delega al servicio apropiado
        # Verifica todos los elementos: Pier, Column, Beam, DropBeam
        self._orchestrator = element_orchestrator or ElementOrchestrator()

        # Servicios que dependen del orquestador
        self._proposal_service = proposal_service or ProposalService(
            orchestrator=self._orchestrator
        )
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
        pier: Pier,
        apply_slenderness: bool = False
    ) -> tuple:
        """
        Genera steel_layers, interaction_points y phi_Mn_0.

        Returns:
            (steel_layers, interaction_points, phi_Mn_0)
        """
        steel_layers = pier.get_steel_layers()
        interaction_points, _ = self._flexo_service.generate_interaction_curve(
            pier, direction='primary', apply_slenderness=apply_slenderness, k=0.8
        )

        # Obtener phi_Mn_0 directamente del FlexureChecker
        phi_Mn_0 = FlexureChecker.get_phi_Mn_at_P0(interaction_points)

        return steel_layers, interaction_points, phi_Mn_0

    def _analyze_piers_batch(
        self,
        piers: Dict[str, Pier],
        parsed_data: Any
    ) -> List[Dict[str, Any]]:
        """
        Analiza un lote de piers usando _analyze_element.

        Clasifica automáticamente cada pier y lo verifica con el servicio
        apropiado según ACI 318-25:
        - §18.7 (SeismicColumnService) para piers tipo columna
        - §18.10 (SeismicWallService) para muros esbeltos y rechonchos

        Args:
            piers: Diccionario de piers a analizar {key: Pier}
            parsed_data: Datos parseados de la sesión

        Returns:
            Lista de dicts formateados para la UI
        """
        hn_ft = parsed_data.building_info.hn_ft if parsed_data.building_info else None

        results = []
        for key, pier in piers.items():
            continuity_info = None
            if parsed_data.continuity_info and key in parsed_data.continuity_info:
                continuity_info = parsed_data.continuity_info[key]

            formatted = self._analyze_element(
                key, pier, parsed_data.pier_forces.get(key),
                continuity_info=continuity_info,
                hn_ft=hn_ft
            )
            results.append(formatted)

        return results

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

    def parse_excel_with_progress(self, file_content: bytes, session_id: str, hn_ft: Optional[float] = None):
        """Parsea Excel de ETABS con progreso SSE."""
        yield from self._session_manager.create_session_with_progress(file_content, session_id, hn_ft=hn_ft)

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
        seismic_category: SeismicCategory = SeismicCategory.SPECIAL
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
        result = self._orchestrator.verify(
            element=element,
            forces=forces,
            lambda_factor=lambda_factor,
            category=seismic_category,
            hwcs=hwcs,
            hn_ft=hn_ft,
        )

        # Formatear resultado
        return ResultFormatter.format_any_element(
            element, result, key, continuity_info=continuity_info
        )

    def _analyze_slab(self, key: str, slab, slab_forces) -> Dict[str, Any]:
        """
        Analiza una losa individual.

        Las losas usan servicios especializados (no el orquestador genérico).
        """
        slab_result = self._slab_service.verify_slab(slab, slab_forces)
        punching_result = self._punching_service.check_punching(slab, slab_forces)
        return ResultFormatter.format_slab_result(slab, slab_result, punching_result, key)

    def _calculate_statistics(
        self,
        pier_results: List,
        column_results: List,
        beam_results: List,
        slab_results: List,
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
            statistics['columns'] = self._statistics_service.calculate_dict_statistics(column_results)

        if beam_results:
            statistics['beams'] = self._statistics_service.calculate_dict_statistics(beam_results)

        if slab_results:
            statistics['slabs'] = self._statistics_service.calculate_dict_statistics(slab_results)

        if drop_beam_results:
            statistics['drop_beams'] = self._statistics_service.calculate_dict_statistics(drop_beam_results)

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

        # Contar elementos para barra de progreso
        piers = parsed_data.piers
        columns = parsed_data.columns or {}
        beams = parsed_data.beams or {}
        slabs = parsed_data.slabs or {}
        drop_beams = parsed_data.drop_beams or {}

        total_piers = len(piers)
        total_columns = len(columns)
        total_beams = len(beams)
        total_slabs = len(slabs)
        total_drop_beams = len(drop_beams)
        total_elements = total_piers + total_columns + total_beams + total_slabs + total_drop_beams

        # Obtener hn_ft del edificio
        hn_ft = parsed_data.building_info.hn_ft if parsed_data.building_info else None

        # =====================================================================
        # FASE 1: Analizar PIERS (usando _analyze_element)
        # =====================================================================
        pier_results = []
        for i, (key, pier) in enumerate(piers.items(), 1):
            yield {
                "type": "progress",
                "current": i,
                "total": total_elements,
                "pier": f"Pier: {pier.story} - {pier.label}"
            }
            continuity_info = None
            if parsed_data.continuity_info and key in parsed_data.continuity_info:
                continuity_info = parsed_data.continuity_info[key]

            formatted = self._analyze_element(
                key, pier, parsed_data.pier_forces.get(key),
                materials_config=materials_config,
                continuity_info=continuity_info,
                hn_ft=hn_ft,
                seismic_category=category_enum
            )
            pier_results.append(formatted)

            # Guardar en cache para que el modal no recalcule
            self._session_manager.store_analysis_result(session_id, key, formatted)

        # =====================================================================
        # FASE 2: Analizar COLUMNAS (usando _analyze_element)
        # =====================================================================
        column_results = []
        column_forces_dict = parsed_data.column_forces or {}
        for i, (key, column) in enumerate(columns.items(), 1):
            yield {
                "type": "progress",
                "current": total_piers + i,
                "total": total_elements,
                "pier": f"Columna: {column.story} - {column.label}"
            }
            formatted = self._analyze_element(
                key, column, column_forces_dict.get(key),
                seismic_category=category_enum
            )
            column_results.append(formatted)

            # Guardar en cache para que el modal no recalcule
            self._session_manager.store_analysis_result(session_id, key, formatted)

        # =====================================================================
        # FASE 3: Analizar VIGAS (usando _analyze_element)
        # =====================================================================
        beam_results = []
        beam_forces_dict = parsed_data.beam_forces or {}
        for i, (key, beam) in enumerate(beams.items(), 1):
            yield {
                "type": "progress",
                "current": total_piers + total_columns + i,
                "total": total_elements,
                "pier": f"Viga: {beam.story} - {beam.label}"
            }
            formatted = self._analyze_element(
                key, beam, beam_forces_dict.get(key),
                seismic_category=category_enum
            )
            beam_results.append(formatted)

        # =====================================================================
        # FASE 4: Analizar LOSAS (usando _analyze_slab)
        # =====================================================================
        slab_results = []
        slab_forces_dict = parsed_data.slab_forces or {}
        for i, (key, slab) in enumerate(slabs.items(), 1):
            yield {
                "type": "progress",
                "current": total_piers + total_columns + total_beams + i,
                "total": total_elements,
                "pier": f"Losa: {slab.story} - {slab.label}"
            }
            formatted = self._analyze_slab(key, slab, slab_forces_dict.get(key))
            slab_results.append(formatted)

        # =====================================================================
        # FASE 5: Analizar VIGAS CAPITEL (usando _analyze_element)
        # =====================================================================
        drop_beam_results = []
        drop_beam_forces_dict = parsed_data.drop_beam_forces or {}
        for i, (key, drop_beam) in enumerate(drop_beams.items(), 1):
            yield {
                "type": "progress",
                "current": total_piers + total_columns + total_beams + total_slabs + i,
                "total": total_elements,
                "pier": f"V. Capitel: {drop_beam.story} - {drop_beam.label}"
            }
            formatted = self._analyze_element(
                key, drop_beam, drop_beam_forces_dict.get(key),
                seismic_category=category_enum
            )
            drop_beam_results.append(formatted)

        # Calcular estadísticas
        statistics = self._calculate_statistics(
            pier_results, column_results, beam_results, slab_results, drop_beam_results
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
                'slab_results': slab_results,
                'drop_beam_results': drop_beam_results,
                'summary_plot': None
            }
        }

    def analyze_direct(
        self,
        file_content: bytes,
        generate_plots: bool = True
    ) -> Dict[str, Any]:
        """Análisis directo sin sesión previa (para pruebas)."""
        session_id = str(uuid.uuid4())
        self.parse_excel(file_content, session_id)
        return self.analyze(session_id, generate_plots=generate_plots)

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

        # Generar datos de interacción para reutilizar
        _, interaction_points, _ = self._generate_interaction_data(pier)
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

        # Generar gráfico
        pm_plot = ""
        if generate_plot:
            all_points = pier_forces.get_critical_pm_points(
                moment_axis='combined',
                angle_deg=angle_deg
            )
            pm_plot = self._plot_generator.generate_pm_diagram(
                capacity_curve=design_curve,
                demand_points=all_points,
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
    # Métodos Públicos - Gráficos Filtrados
    # =========================================================================

    def generate_filtered_summary_plot(
        self,
        session_id: str,
        pier_keys: Optional[List[str]] = None,
        story_filter: str = '',
        axis_filter: str = ''
    ) -> Dict[str, Any]:
        """
        Genera un gráfico resumen filtrado por pier_keys o filtros.

        Args:
            session_id: ID de sesión
            pier_keys: Lista específica de pier keys a incluir
            story_filter: Filtro por piso
            axis_filter: Filtro por eje

        Returns:
            Dict con success y summary_plot en base64
        """
        error = self._validate_session(session_id)
        if error:
            return error

        parsed_data = self._session_manager.get_session(session_id)

        # Filtrar piers
        filtered_piers = {}
        for key, pier in parsed_data.piers.items():
            # Si hay pier_keys, usar esos
            if pier_keys is not None:
                if key not in pier_keys:
                    continue
            else:
                # Aplicar filtros
                if story_filter and pier.story != story_filter:
                    continue
                if axis_filter and pier.eje != axis_filter:
                    continue
            filtered_piers[key] = pier

        if not filtered_piers:
            return {'success': True, 'summary_plot': None, 'count': 0}

        # Analizar piers filtrados
        results = self._analyze_piers_batch(
            piers=filtered_piers,
            parsed_data=parsed_data
        )

        # Convertir resultados a formato para gráfico resumen
        summary_data = [
            {
                'pier_label': r.get('pier_label', ''),
                'flexure_sf': r.get('flexure', {}).get('sf', 0),
                'shear_sf': r.get('shear', {}).get('sf', 0)
            }
            for r in results
        ]
        summary_plot = self._statistics_service.generate_summary_from_dict(summary_data)

        return {
            'success': True,
            'summary_plot': summary_plot,
            'count': len(results)
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

    def get_pier_capacities(self, session_id: str, pier_key: str) -> Dict[str, Any]:
        """Calcula las capacidades puras del pier (sin interacción)."""
        return self._details_formatter.get_pier_capacities(session_id, pier_key)

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
        pier = parsed_data.piers.get(pier_key)
        pier_forces = parsed_data.pier_forces.get(pier_key)

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

        drop_beam = parsed_data.drop_beams.get(drop_beam_key)
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

