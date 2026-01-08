# app/structural/services/pier_analysis.py
"""
Servicio principal de analisis estructural de piers.
Orquesta el parsing, calculo y generacion de resultados.

Este servicio actua como orquestador, delegando a servicios especializados:
- FlexureService: analisis de flexocompresion
- ShearService: verificacion de corte
- StatisticsService: estadisticas y graficos resumen
- PierVerificationService: verificacion de conformidad ACI 318-25

Referencias ACI 318-25:
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
from .analysis.pier_verification_service import PierVerificationService
from .analysis.pier_capacity_service import PierCapacityService
from .analysis.element_verification_service import ElementService
from .analysis.slab_service import SlabService
from .analysis.punching_service import PunchingService
from ..domain.entities import Pier, PierForces
from .analysis.verification_result import ElementVerificationResult
from ..domain.flexure import InteractionDiagramService, SlendernessService
from ..domain.chapter11 import WallType
from ..domain.constants import SeismicDesignCategory


class PierAnalysisService:
    """
    Servicio de análisis estructural para piers de hormigón armado.

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
        verification_service: Optional[PierVerificationService] = None,
        capacity_service: Optional[PierCapacityService] = None,
        element_service: Optional[ElementService] = None,
        slab_service: Optional[SlabService] = None,
        punching_service: Optional[PunchingService] = None
    ):
        """
        Inicializa el servicio de analisis.

        Args:
            session_manager: Gestor de sesiones (opcional, crea uno nuevo si no se pasa)
            flexocompression_service: Servicio de flexocompresión (opcional)
            shear_service: Servicio de corte (opcional)
            statistics_service: Servicio de estadisticas (opcional)
            slenderness_service: Servicio de esbeltez (opcional)
            interaction_service: Servicio de diagrama interaccion (opcional)
            plot_generator: Generador de graficos (opcional)
            proposal_service: Servicio de propuestas de diseño (opcional)
            verification_service: Servicio de verificacion de piers (opcional)
            capacity_service: Servicio de capacidades de piers (opcional)
            element_service: Servicio unificado de elementos (opcional)

        Nota: Los servicios se crean por defecto si no se pasan.
              Pasar None explicito permite inyectar mocks para testing.
        """
        self._session_manager = session_manager or SessionManager()
        self._flexo_service = flexocompression_service or FlexocompressionService()
        self._shear_service = shear_service or ShearService()
        self._statistics_service = statistics_service or StatisticsService()
        self._slenderness_service = slenderness_service or SlendernessService()
        self._interaction_service = interaction_service or InteractionDiagramService()
        self._plot_generator = plot_generator or PlotGenerator()
        self._proposal_service = proposal_service or ProposalService(
            flexocompression_service=self._flexo_service,
            shear_service=self._shear_service
        )
        self._verification_service = verification_service or PierVerificationService(
            session_manager=self._session_manager
        )
        self._capacity_service = capacity_service or PierCapacityService(
            session_manager=self._session_manager,
            flexocompression_service=self._flexo_service,
            shear_service=self._shear_service,
            slenderness_service=self._slenderness_service,
            plot_generator=self._plot_generator
        )
        self._slab_service = slab_service or SlabService()
        self._punching_service = punching_service or PunchingService()

        # Servicio unificado de elementos (reemplaza ElementAnalyzer, ColumnService, BeamService)
        self._element_service = element_service or ElementService(
            flexocompression_service=self._flexo_service,
            shear_service=self._shear_service,
            proposal_service=self._proposal_service,
            plot_generator=self._plot_generator,
            session_manager=self._session_manager
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

        # Obtener phi_Mn_0
        _, _, _, phi_Mn_0, _, _, _, _, _ = self._interaction_service.check_flexure(
            interaction_points, [(0, 1, "dummy")]
        )

        return steel_layers, interaction_points, phi_Mn_0

    def _analyze_piers_batch(
        self,
        piers: Dict[str, Pier],
        parsed_data: Any,
        session_id: str,
        generate_plots: bool = False,
        moment_axis: str = 'M3',
        angle_deg: float = 0
    ) -> List[ElementVerificationResult]:
        """
        Analiza un lote de piers y retorna los resultados.

        Args:
            piers: Diccionario de piers a analizar {key: Pier}
            parsed_data: Datos parseados de la sesión
            session_id: ID de sesión para obtener configuración de vigas
            generate_plots: Generar gráficos P-M individuales
            moment_axis: Eje de momento
            angle_deg: Ángulo para vista combinada

        Returns:
            Lista de ElementVerificationResult
        """
        # Obtener hn_ft del edificio
        hn_ft = None
        if parsed_data.building_info:
            hn_ft = parsed_data.building_info.hn_ft

        results: List[ElementVerificationResult] = []
        for key, pier in piers.items():
            pier_forces = parsed_data.pier_forces.get(key)

            # Obtener hwcs y continuity_info para este pier
            hwcs = None
            continuity_info = None
            if parsed_data.continuity_info and key in parsed_data.continuity_info:
                continuity_info = parsed_data.continuity_info[key]
                hwcs = continuity_info.hwcs

            result = self._element_service.verify(
                pier,
                pier_forces,
                generate_plot=generate_plots,
                moment_axis=moment_axis,
                angle_deg=angle_deg,
                hwcs=hwcs,
                hn_ft=hn_ft
            )
            results.append(result)

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
        generate_plots: bool = True,
        moment_axis: str = 'M3',
        angle_deg: float = 0
    ) -> Dict[str, Any]:
        """
        Ejecuta el análisis estructural completo.

        Args:
            session_id: ID de sesión
            pier_updates: Actualizaciones de armadura opcionales
            generate_plots: Generar gráficos P-M
            moment_axis: Plano de momento ('M2', 'M3', 'combined', 'SRSS')
            angle_deg: Ángulo para vista combinada

        Returns:
            Diccionario con estadísticas y resultados
        """
        # Validar sesión
        error = self._validate_session(session_id)
        if error:
            return error

        # Aplicar actualizaciones de armadura
        if pier_updates:
            self._session_manager.apply_reinforcement_updates(session_id, pier_updates)

        # Obtener datos de la sesión
        parsed_data = self._session_manager.get_session(session_id)

        # Analizar todos los piers
        results = self._analyze_piers_batch(
            piers=parsed_data.piers,
            parsed_data=parsed_data,
            session_id=session_id,
            generate_plots=generate_plots,
            moment_axis=moment_axis,
            angle_deg=angle_deg
        )

        # Calcular estadísticas (delegado a StatisticsService)
        statistics = self._statistics_service.calculate_statistics(results)

        # Generar gráfico resumen (delegado a StatisticsService)
        summary_plot = None
        if generate_plots and results:
            summary_plot = self._statistics_service.generate_summary_plot(results)

        # Formatear resultados de piers para la UI
        pier_results = []
        for i, r in enumerate(results):
            key = list(parsed_data.piers.keys())[i]
            pier = parsed_data.piers[key]
            formatted = ResultFormatter.format_element_result(pier, r, key)
            pier_results.append(formatted)

        return {
            'success': True,
            'statistics': statistics,
            'results': pier_results,
            'summary_plot': summary_plot
        }

    def analyze_with_progress(
        self,
        session_id: str,
        pier_updates: Optional[List[Dict]] = None,
        generate_plots: bool = True,
        moment_axis: str = 'M3',
        angle_deg: float = 0,
        materials_config: Optional[Dict] = None
    ):
        """
        Ejecuta el análisis estructural con progreso (generador para SSE).

        Args:
            materials_config: Configuración de materiales con lambda por tipo de concreto.
                Format: {material_name: {fc, type, lambda}, ...}

        Yields:
            Dict con eventos de progreso:
            - {"type": "progress", "current": 1, "total": 100, "element": "P1-A1"}
            - {"type": "complete", "result": {...}}
            - {"type": "error", "message": "..."}
        """
        materials_config = materials_config or {}

        def get_lambda_for_pier(pier) -> float:
            """Obtiene el factor lambda para un pier basado en su material."""
            # Buscar por nombre de material si está definido
            material_name = getattr(pier, 'material', None)
            fc = pier.fc

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

        # Validar sesión
        error = self._validate_session(session_id)
        if error:
            yield {"type": "error", "message": error.get('error', 'Error de sesión')}
            return

        # Aplicar actualizaciones de armadura
        if pier_updates:
            self._session_manager.apply_reinforcement_updates(session_id, pier_updates)

        # Obtener datos de la sesión
        parsed_data = self._session_manager.get_session(session_id)

        # Contar elementos totales (piers + columnas)
        piers = parsed_data.piers
        columns = parsed_data.columns or {}
        total_piers = len(piers)
        total_columns = len(columns)
        total_elements = total_piers + total_columns

        results = []
        column_results = []

        # Obtener hn_ft del edificio
        hn_ft = None
        if parsed_data.building_info:
            hn_ft = parsed_data.building_info.hn_ft

        # =====================================================================
        # FASE 1: Analizar PIERS
        # =====================================================================
        for i, (key, pier) in enumerate(piers.items(), 1):
            # Enviar progreso
            yield {
                "type": "progress",
                "current": i,
                "total": total_elements,
                "pier": f"Pier: {pier.story} - {pier.label}"
            }

            # Obtener datos del pier
            pier_forces = parsed_data.pier_forces.get(key)

            # Obtener hwcs y continuity_info
            hwcs = None
            continuity_info = None
            if parsed_data.continuity_info and key in parsed_data.continuity_info:
                continuity_info = parsed_data.continuity_info[key]
                hwcs = continuity_info.hwcs

            # Obtener lambda para este pier
            lambda_factor = get_lambda_for_pier(pier)

            # Analizar pier
            result = self._element_service.verify(
                pier,
                pier_forces,
                generate_plot=generate_plots,
                moment_axis=moment_axis,
                angle_deg=angle_deg,
                hwcs=hwcs,
                hn_ft=hn_ft,
                lambda_factor=lambda_factor
            )
            results.append(result)

        # =====================================================================
        # FASE 2: Analizar COLUMNAS
        # =====================================================================
        column_forces_dict = parsed_data.column_forces or {}
        for i, (key, column) in enumerate(columns.items(), 1):
            # Enviar progreso
            yield {
                "type": "progress",
                "current": total_piers + i,
                "total": total_elements,
                "pier": f"Columna: {column.story} - {column.label}"
            }

            # Obtener fuerzas de la columna
            col_forces = column_forces_dict.get(key)

            # Verificar columna usando ElementService
            col_result = self._element_service.verify(column, col_forces)

            # Convertir a formato compatible con la tabla
            unified_result = ResultFormatter.format_element_result(
                column, col_result, key
            )
            column_results.append(unified_result)

        # =====================================================================
        # FASE 3: Procesar Vigas
        # =====================================================================
        beam_results = []
        beams = parsed_data.beams or {}
        beam_forces_dict = parsed_data.beam_forces or {}
        total_beams = len(beams)

        for i, (key, beam) in enumerate(beams.items(), 1):
            # Enviar progreso
            yield {
                "type": "progress",
                "current": total_piers + total_columns + i,
                "total": total_elements + total_beams,
                "pier": f"Viga: {beam.story} - {beam.label}"
            }

            # Obtener fuerzas de la viga
            beam_forces = beam_forces_dict.get(key)

            # Verificar viga usando ElementService
            beam_result = self._element_service.verify(beam, beam_forces)

            # Convertir a formato para UI
            unified_result = ResultFormatter.format_element_result(
                beam, beam_result, key
            )
            beam_results.append(unified_result)

        # =====================================================================
        # FASE 4: Analizar LOSAS
        # =====================================================================
        slab_results = []
        slabs = parsed_data.slabs or {}
        slab_forces_dict = parsed_data.slab_forces or {}
        total_slabs = len(slabs)

        if total_slabs > 0:
            for i, (key, slab) in enumerate(slabs.items(), 1):
                # Enviar progreso
                yield {
                    "type": "progress",
                    "current": total_piers + total_columns + total_beams + i,
                    "total": total_elements + total_beams + total_slabs,
                    "pier": f"Losa: {slab.story} - {slab.label}"
                }

                # Obtener fuerzas de la losa
                slab_forces = slab_forces_dict.get(key)

                # Verificar losa (flexion, cortante, espesor)
                slab_result = self._slab_service.verify_slab(slab, slab_forces)

                # Verificar punzonamiento si es 2-Way
                punching_result = self._punching_service.check_punching(
                    slab, slab_forces
                )

                # Combinar resultados
                unified_result = ResultFormatter.format_slab_result(
                    slab, slab_result, punching_result, key
                )
                slab_results.append(unified_result)

        # Calcular estadisticas de piers
        statistics = self._statistics_service.calculate_statistics(results)

        # Agregar estadísticas de columnas
        if column_results:
            col_ok = sum(1 for r in column_results if r['overall_status'] == 'OK')
            col_fail = len(column_results) - col_ok
            statistics['columns'] = {
                'total': len(column_results),
                'ok': col_ok,
                'fail': col_fail,
                'pass_rate': round(col_ok / len(column_results) * 100, 1) if column_results else 100
            }

        # Agregar estadisticas de vigas
        if beam_results:
            beam_ok = sum(1 for r in beam_results if r['overall_status'] == 'OK')
            beam_fail = len(beam_results) - beam_ok
            statistics['beams'] = {
                'total': len(beam_results),
                'ok': beam_ok,
                'fail': beam_fail,
                'pass_rate': round(beam_ok / len(beam_results) * 100, 1) if beam_results else 100
            }

        # Agregar estadisticas de losas
        if slab_results:
            slab_ok = sum(1 for r in slab_results if r['overall_status'] == 'OK')
            slab_fail = len(slab_results) - slab_ok
            statistics['slabs'] = {
                'total': len(slab_results),
                'ok': slab_ok,
                'fail': slab_fail,
                'pass_rate': round(slab_ok / len(slab_results) * 100, 1) if slab_results else 100
            }

        # Generar grafico resumen (solo para piers por ahora)
        summary_plot = None
        if generate_plots and results:
            yield {
                "type": "progress",
                "current": total_elements,
                "total": total_elements,
                "pier": "Generando resumen..."
            }
            summary_plot = self._statistics_service.generate_summary_plot(results)

        # Formatear resultados de piers para la UI
        pier_results_dicts = []
        piers_list = list(piers.items())
        for i, r in enumerate(results):
            key, pier = piers_list[i]
            formatted = ResultFormatter.format_element_result(pier, r, key)
            pier_results_dicts.append(formatted)

        # Unificar todos los resultados
        all_results = pier_results_dicts + column_results

        # Enviar resultado completo
        yield {
            "type": "complete",
            "result": {
                'success': True,
                'statistics': statistics,
                'results': all_results,
                'beam_results': beam_results,  # Vigas separadas (tabla diferente)
                'slab_results': slab_results,  # Losas separadas (tabla diferente)
                'summary_plot': summary_plot
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
        """Obtiene las combinaciones de carga de un pier con sus FS calculados."""
        # Validar pier
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        if pier_forces is None:
            return {'success': False, 'error': f'Forces not found for pier: {pier_key}'}

        # Generar datos de interacción (con reducción por esbeltez)
        _, interaction_points, phi_Mn_0 = self._generate_interaction_data(
            pier, apply_slenderness=True
        )

        # Calcular FS para cada combinación
        combinations_with_fs = []
        for i, combo in enumerate(pier_forces.combinations):
            # FS Flexión
            P = -combo.P  # Convertir a positivo = compresión
            M = combo.moment_resultant
            demand_point = [(P, M, combo.name)]
            flexure_sf, flexure_status, _, _, _, _, _, _, _ = self._interaction_service.check_flexure(
                interaction_points, demand_point
            )

            # FS Corte V2 y V3 (usa verify_bidirectional_shear para consistencia)
            shear_v2, shear_v3 = self._shear_service.verify_bidirectional_shear(
                lw=pier.width,
                tw=pier.thickness,
                hw=pier.height,
                fc=pier.fc,
                fy=pier.fy,
                rho_h=pier.rho_horizontal,
                Vu2_max=abs(combo.V2),
                Vu3_max=abs(combo.V3),
                Nu=P
            )

            # Estado general de esta combinación
            fs_min = min(
                flexure_sf if flexure_sf < 100 else 100,
                shear_v2.sf if shear_v2.sf < 100 else 100,
                shear_v3.sf if shear_v3.sf < 100 else 100
            )
            status = 'OK' if fs_min >= 1.0 else 'NO OK'

            combinations_with_fs.append({
                'index': i,
                'name': combo.name,
                'location': combo.location,
                'step_type': combo.step_type,
                'full_name': f"{combo.name} ({combo.location})" if combo.location else combo.name,
                'P': round(-combo.P, 2),  # tonf (positivo = compresión)
                'M2': round(combo.M2, 2),
                'M3': round(combo.M3, 2),
                'V2': round(combo.V2, 2),
                'V3': round(combo.V3, 2),
                'M_resultant': round(combo.moment_resultant, 2),
                'angle_deg': round(combo.moment_angle_deg, 1),
                'flexure_sf': round(flexure_sf, 2) if flexure_sf < 100 else '>100',
                'flexure_status': flexure_status,
                'shear_sf_2': round(shear_v2.sf, 2) if shear_v2.sf < 100 else '>100',
                'shear_sf_3': round(shear_v3.sf, 2) if shear_v3.sf < 100 else '>100',
                'overall_status': status
            })

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
        """Analiza un pier para una combinación específica."""
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

        # Generar datos de interacción
        _, interaction_points, _ = self._generate_interaction_data(pier)
        design_curve = self._interaction_service.get_design_curve(interaction_points)

        # Calcular SF para esta combinación
        P = -combo.P
        M = combo.moment_resultant
        demand_points = [(P, M, f"{combo.name} ({combo.location})")]
        flexure_sf, flexure_status, _, _, _, _, _, _, _ = self._interaction_service.check_flexure(
            interaction_points, demand_points
        )

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
                'P': P,
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

        # Analizar piers filtrados (sin generar plots individuales)
        results = self._analyze_piers_batch(
            piers=filtered_piers,
            parsed_data=parsed_data,
            session_id=session_id,
            generate_plots=False,
            moment_axis='M3',
            angle_deg=0
        )

        # Generar gráfico resumen (delegado a StatisticsService)
        summary_plot = self._statistics_service.generate_summary_plot(results)

        return {
            'success': True,
            'summary_plot': summary_plot,
            'count': len(results)
        }

    # =========================================================================
    # Capacidades (delegado a PierCapacityService)
    # =========================================================================

    def get_section_diagram(
        self,
        session_id: str,
        pier_key: str,
        proposed_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Genera un diagrama de la sección transversal del pier."""
        return self._capacity_service.get_section_diagram(
            session_id, pier_key, proposed_config
        )

    def get_pier_capacities(self, session_id: str, pier_key: str) -> Dict[str, Any]:
        """Calcula las capacidades puras del pier (sin interacción)."""
        return self._capacity_service.get_pier_capacities(session_id, pier_key)

    def get_combination_details(
        self,
        session_id: str,
        pier_key: str,
        combo_index: int
    ) -> Dict[str, Any]:
        """Obtiene los detalles de diseño para una combinación específica."""
        return self._capacity_service.get_combination_details(
            session_id, pier_key, combo_index
        )

    # =========================================================================
    # Verificacion ACI 318-25 (delegado a PierVerificationService)
    # =========================================================================

    def verify_aci_318_25(
        self,
        session_id: str,
        pier_key: str,
        wall_type: str = 'bearing',
        cast_type: str = 'cast_in_place'
    ) -> Dict[str, Any]:
        """Verifica conformidad ACI 318-25 Capitulo 11 para un pier."""
        return self._verification_service.verify_aci_318_25(
            session_id, pier_key, wall_type, cast_type
        )

    def verify_all_piers_aci_318_25(
        self,
        session_id: str,
        wall_type: str = 'bearing'
    ) -> Dict[str, Any]:
        """Verifica conformidad ACI 318-25 para todos los piers."""
        return self._verification_service.verify_all_piers_aci_318_25(
            session_id, wall_type
        )

    def verify_seismic(
        self,
        session_id: str,
        pier_key: str,
        sdc: str = 'D',
        delta_u: float = 0,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        sigma_max: float = 0,
        is_wall_pier: bool = False
    ) -> Dict[str, Any]:
        """Verifica conformidad ACI 318-25 Capitulo 18 para un pier."""
        return self._verification_service.verify_seismic(
            session_id, pier_key, sdc, delta_u, hwcs, hn_ft, sigma_max, is_wall_pier
        )

    def verify_combined_aci(
        self,
        session_id: str,
        pier_key: str,
        wall_type: str = 'bearing',
        sdc: str = 'D',
        delta_u: float = 0,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        sigma_max: float = 0,
        is_wall_pier: bool = False
    ) -> Dict[str, Any]:
        """Verificacion combinada de Capitulos 11 y 18 para un pier."""
        return self._verification_service.verify_combined_aci(
            session_id, pier_key, wall_type, sdc, delta_u, hwcs, hn_ft,
            sigma_max, is_wall_pier
        )

    def verify_all_piers_seismic(
        self,
        session_id: str,
        sdc: str = 'D',
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """Verifica conformidad sismica para todos los piers."""
        return self._verification_service.verify_all_piers_seismic(
            session_id, sdc, hn_ft
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

        result = self._element_service.verify(
            pier,
            pier_forces,
            generate_plot=generate_plot,
            moment_axis='M3',
            angle_deg=0,
            hwcs=hwcs,
            hn_ft=hn_ft
        )

        return ResultFormatter.format_element_result(pier, result, pier_key)

    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de una sesion."""
        return self._session_manager.get_session(session_id)

    # =========================================================================
    # API Publica - Actualizacion de Losas
    # =========================================================================

    def update_slab(
        self,
        session_id: str,
        slab_key: str,
        slab_type: Optional[str] = None,
        diameter_main: Optional[int] = None,
        spacing_main: Optional[int] = None,
        diameter_temp: Optional[int] = None,
        spacing_temp: Optional[int] = None,
        column_width: Optional[float] = None,
        column_depth: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Actualiza propiedades de una losa.

        Args:
            session_id: ID de sesion
            slab_key: Clave de la losa
            slab_type: 'one_way' o 'two_way'
            diameter_main: Diametro armadura principal (mm)
            spacing_main: Espaciamiento armadura principal (mm)
            diameter_temp: Diametro armadura temperatura (mm)
            spacing_temp: Espaciamiento armadura temperatura (mm)
            column_width: Ancho columna para punzonamiento (mm)
            column_depth: Profundidad columna para punzonamiento (mm)

        Returns:
            Dict con success y mensaje
        """
        from ..domain.entities.slab import SlabType

        parsed_data = self._session_manager.get_session(session_id)
        if not parsed_data:
            return {'success': False, 'error': 'Sesion no encontrada'}

        if slab_key not in parsed_data.slabs:
            return {'success': False, 'error': f'Losa {slab_key} no encontrada'}

        slab = parsed_data.slabs[slab_key]

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

        return {'success': True, 'message': f'Losa {slab_key} actualizada'}

    def update_slabs_batch(
        self,
        session_id: str,
        slab_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Actualiza multiples losas en batch.

        Args:
            session_id: ID de sesion
            slab_updates: Lista de dicts con 'key' y propiedades a actualizar

        Returns:
            Dict con success y conteo de actualizaciones
        """
        updated_count = 0
        errors = []

        for update in slab_updates:
            slab_key = update.get('key')
            if not slab_key:
                continue

            result = self.update_slab(
                session_id=session_id,
                slab_key=slab_key,
                slab_type=update.get('slab_type'),
                diameter_main=update.get('diameter_main'),
                spacing_main=update.get('spacing_main'),
                diameter_temp=update.get('diameter_temp'),
                spacing_temp=update.get('spacing_temp'),
                column_width=update.get('column_width'),
                column_depth=update.get('column_depth')
            )

            if result.get('success'):
                updated_count += 1
            else:
                errors.append(result.get('error', 'Error desconocido'))

        return {
            'success': len(errors) == 0,
            'updated_count': updated_count,
            'errors': errors if errors else None
        }

