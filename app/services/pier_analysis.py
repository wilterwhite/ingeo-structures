# app/structural/services/pier_analysis.py
"""
Servicio principal de analisis estructural de piers.
Orquesta el parsing, calculo y generacion de resultados.

Este servicio actua como orquestador, delegando a servicios especializados:
- FlexureService: analisis de flexocompresion
- ShearService: verificacion de corte
- StatisticsService: estadisticas y graficos resumen
- ACI318_25_Service: verificacion de conformidad ACI 318-25

Referencias ACI 318-25:
- Capitulo 11: Muros (Walls)
- Capitulo 18: Estructuras resistentes a sismos
"""
from typing import Dict, List, Any, Optional
import uuid

from .parsing.session_manager import SessionManager
from .presentation.plot_generator import PlotGenerator
from .analysis.flexure_service import FlexureService
from .analysis.shear_service import ShearService
from .analysis.statistics_service import StatisticsService
from .analysis.proposal_service import ProposalService
from .analysis.aci_318_25_service import (
    ACI318_25_Service,
    Chapter18_VerificationResult
)
from .analysis.pier_verification_service import PierVerificationService
from .analysis.pier_capacity_service import PierCapacityService
from ..domain.entities import Pier, VerificationResult, PierForces
from ..domain.flexure import InteractionDiagramService, SlendernessService, SteelLayer
from ..domain.chapter11 import WallType, WallCastType
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
        flexure_service: Optional[FlexureService] = None,
        shear_service: Optional[ShearService] = None,
        statistics_service: Optional[StatisticsService] = None,
        slenderness_service: Optional[SlendernessService] = None,
        interaction_service: Optional[InteractionDiagramService] = None,
        plot_generator: Optional[PlotGenerator] = None,
        aci_318_25_service: Optional[ACI318_25_Service] = None,
        proposal_service: Optional[ProposalService] = None,
        verification_service: Optional[PierVerificationService] = None,
        capacity_service: Optional[PierCapacityService] = None
    ):
        """
        Inicializa el servicio de analisis.

        Args:
            session_manager: Gestor de sesiones (opcional, crea uno nuevo si no se pasa)
            flexure_service: Servicio de flexion (opcional)
            shear_service: Servicio de corte (opcional)
            statistics_service: Servicio de estadisticas (opcional)
            slenderness_service: Servicio de esbeltez (opcional)
            interaction_service: Servicio de diagrama interaccion (opcional)
            plot_generator: Generador de graficos (opcional)
            aci_318_25_service: Servicio de verificacion ACI 318-25 (opcional)
            proposal_service: Servicio de propuestas de diseño (opcional)
            verification_service: Servicio de verificacion de piers (opcional)
            capacity_service: Servicio de capacidades de piers (opcional)

        Nota: Los servicios se crean por defecto si no se pasan.
              Pasar None explicito permite inyectar mocks para testing.
        """
        self._session_manager = session_manager or SessionManager()
        self._flexure_service = flexure_service or FlexureService()
        self._shear_service = shear_service or ShearService()
        self._statistics_service = statistics_service or StatisticsService()
        self._slenderness_service = slenderness_service or SlendernessService()
        self._interaction_service = interaction_service or InteractionDiagramService()
        self._plot_generator = plot_generator or PlotGenerator()
        self._aci_318_25_service = aci_318_25_service or ACI318_25_Service()
        self._proposal_service = proposal_service or ProposalService(
            flexure_service=self._flexure_service,
            shear_service=self._shear_service
        )
        self._verification_service = verification_service or PierVerificationService(
            session_manager=self._session_manager,
            aci_318_25_service=self._aci_318_25_service
        )
        self._capacity_service = capacity_service or PierCapacityService(
            session_manager=self._session_manager,
            flexure_service=self._flexure_service,
            shear_service=self._shear_service,
            slenderness_service=self._slenderness_service,
            plot_generator=self._plot_generator
        )

    # =========================================================================
    # Helpers - Conversión de Enums
    # =========================================================================

    def _get_sdc_enum(self, sdc: str) -> SeismicDesignCategory:
        """Convierte string SDC a enum."""
        return {
            'A': SeismicDesignCategory.A,
            'B': SeismicDesignCategory.B,
            'C': SeismicDesignCategory.C,
            'D': SeismicDesignCategory.D,
            'E': SeismicDesignCategory.E,
            'F': SeismicDesignCategory.F
        }.get(sdc.upper(), SeismicDesignCategory.D)

    def _get_wall_type_enum(self, wall_type: str) -> WallType:
        """Convierte string wall_type a enum."""
        return {
            'bearing': WallType.BEARING,
            'nonbearing': WallType.NONBEARING,
            'basement': WallType.BASEMENT,
            'foundation': WallType.FOUNDATION
        }.get(wall_type, WallType.BEARING)

    # =========================================================================
    # Helpers - Extracción de Datos
    # =========================================================================

    def _get_max_Vu(self, pier_forces: Optional[PierForces]) -> tuple:
        """Obtiene el cortante máximo de las combinaciones."""
        Vu = 0.0
        Vu_Eh = 0.0
        if pier_forces and pier_forces.combinations:
            for combo in pier_forces.combinations:
                Vu_combo = max(abs(combo.V2), abs(combo.V3))
                if Vu_combo > Vu:
                    Vu = Vu_combo
                    Vu_Eh = Vu_combo
        return Vu, Vu_Eh

    def _get_hwcs_hn(
        self,
        session_id: str,
        pier_key: str,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> tuple:
        """Obtiene hwcs y hn_ft, usando valores calculados si no se proporcionan."""
        if hwcs is None or hwcs <= 0:
            hwcs = self._session_manager.get_hwcs(session_id, pier_key)
        if hn_ft is None or hn_ft <= 0:
            hn_ft = self._session_manager.get_hn_ft(session_id)
        return hwcs, hn_ft

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
        steel_layers = self._flexure_service.pier_to_steel_layers(pier)
        interaction_points = self._interaction_service.generate_interaction_curve(
            width=pier.width,
            thickness=pier.thickness,
            fc=pier.fc,
            fy=pier.fy,
            As_total=pier.As_flexure_total,
            cover=pier.cover,
            steel_layers=steel_layers
        )

        # Aplicar reducción por esbeltez si se requiere
        if apply_slenderness:
            slenderness = self._slenderness_service.analyze(pier, k=0.8, braced=True)
            if slenderness.is_slender:
                reduction = slenderness.buckling_factor
                for point in interaction_points:
                    point.phi_Pn *= reduction
                    point.Pn *= reduction

        # Obtener phi_Mn_0
        _, _, _, phi_Mn_0, _, _, _ = self._interaction_service.check_flexure(
            interaction_points, [(0, 1, "dummy")]
        )

        return steel_layers, interaction_points, phi_Mn_0

    def _analyze_piers_batch(
        self,
        piers: Dict[str, Pier],
        parsed_data: Any,
        generate_plots: bool = False,
        moment_axis: str = 'M3',
        angle_deg: float = 0
    ) -> List[VerificationResult]:
        """
        Analiza un lote de piers y retorna los resultados.

        Args:
            piers: Diccionario de piers a analizar {key: Pier}
            parsed_data: Datos parseados de la sesión
            generate_plots: Generar gráficos P-M individuales
            moment_axis: Eje de momento
            angle_deg: Ángulo para vista combinada

        Returns:
            Lista de VerificationResult
        """
        # Obtener hn_ft del edificio
        hn_ft = None
        if parsed_data.building_info:
            hn_ft = parsed_data.building_info.hn_ft

        results: List[VerificationResult] = []
        for key, pier in piers.items():
            pier_forces = parsed_data.pier_forces.get(key)

            # Obtener hwcs y continuity_info para este pier
            hwcs = None
            continuity_info = None
            if parsed_data.continuity_info and key in parsed_data.continuity_info:
                continuity_info = parsed_data.continuity_info[key]
                hwcs = continuity_info.hwcs

            result = self._analyze_pier(
                pier=pier,
                pier_forces=pier_forces,
                generate_plot=generate_plots,
                moment_axis=moment_axis,
                angle_deg=angle_deg,
                hwcs=hwcs,
                hn_ft=hn_ft,
                continuity_info=continuity_info
            )
            results.append(result)

        return results

    # =========================================================================
    # Validación Centralizada
    # =========================================================================

    def _validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Valida que la sesión existe.

        Returns:
            None si la sesión es válida, o dict con error si no existe.
        """
        if not self._session_manager.has_session(session_id):
            return {
                'success': False,
                'error': 'Session not found. Please upload the file again.'
            }
        return None

    def _validate_pier(
        self,
        session_id: str,
        pier_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Valida que el pier existe en la sesión.

        Returns:
            None si el pier es válido, o dict con error si no existe.
        """
        session_error = self._validate_session(session_id)
        if session_error:
            return session_error

        pier = self._session_manager.get_pier(session_id, pier_key)
        if pier is None:
            return {'success': False, 'error': f'Pier not found: {pier_key}'}
        return None

    # =========================================================================
    # API Pública - Gestión de Sesiones
    # =========================================================================

    def parse_excel(self, file_content: bytes, session_id: str) -> Dict[str, Any]:
        """Parsea Excel de ETABS y crea una sesión."""
        return self._session_manager.create_session(file_content, session_id)

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

        return {
            'success': True,
            'statistics': statistics,
            'results': [r.to_dict() for r in results],
            'summary_plot': summary_plot
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
            flexure_sf, flexure_status, _, _, _, _, _ = self._interaction_service.check_flexure(
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
        flexure_sf, flexure_status, _, _, _, _, _ = self._interaction_service.check_flexure(
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
    # Métodos Privados - Análisis
    # =========================================================================

    def _analyze_pier(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        generate_plot: bool,
        moment_axis: str,
        angle_deg: float,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        continuity_info: Optional[Any] = None
    ) -> VerificationResult:
        """
        Ejecuta el análisis estructural de un pier individual.

        Incluye verificaciones ACI 318-25:
        - Flexocompresión
        - Cortante con interacción V2-V3
        - Clasificación de muros (§18.10.8)
        - Amplificación de cortante (§18.10.3.3)
        - Elementos de borde (§18.10.6)

        Args:
            pier: Pier a analizar
            pier_forces: Fuerzas del pier
            generate_plot: Generar gráfico P-M
            moment_axis: Eje de momento
            angle_deg: Ángulo para vista combinada
            hwcs: Altura desde sección crítica (mm), opcional
            hn_ft: Altura total del edificio (pies), opcional
            continuity_info: WallContinuityInfo para este pier, opcional
        """

        # 1. Flexocompresión (delegado a FlexureService)
        flexure_result = self._flexure_service.check_flexure(
            pier, pier_forces, moment_axis, angle_deg
        )

        # 2. Corte (delegado a ShearService)
        shear_result = self._shear_service.check_shear(pier, pier_forces)

        # 3. Clasificación del muro (ACI 318-25 §18.10.8)
        classification = self._shear_service.get_classification_dict(pier)

        # 4. Amplificación de cortante (ACI 318-25 §18.10.3.3)
        Vu_max = shear_result.get('Vu_2', 0)
        amplification = self._shear_service.get_amplification_dict(
            pier, Vu_max, hwcs=hwcs, hn_ft=hn_ft
        )

        # 5. Elementos de borde (ACI 318-25 §18.10.6)
        boundary = {'required': False, 'method': '', 'aci_reference': ''}
        boundary_sigma_max = 0.0
        boundary_limit = 0.0
        boundary_length = 0.0
        if pier_forces and pier_forces.combinations:
            # Obtener cargas críticas
            critical_combo = None
            for combo in pier_forces.combinations:
                if combo.name == shear_result.get('critical_combo'):
                    critical_combo = combo
                    break

            if critical_combo:
                Pu = -critical_combo.P  # Positivo = compresión
                Mu = abs(critical_combo.M3)
                boundary = self._shear_service.get_boundary_element_dict(pier, Pu, Mu)
                if 'stress_check' in boundary:
                    boundary_sigma_max = boundary['stress_check'].get('sigma_max', 0)
                    boundary_limit = boundary['stress_check'].get('limit', 0)
                if 'dimensions' in boundary:
                    boundary_length = boundary['dimensions'].get('length_horizontal_mm', 0)

        # 6. Estado general
        overall_status = "OK"
        if flexure_result['status'] != "OK" or shear_result['status'] != "OK":
            overall_status = "NO OK"

        # 7. Obtener datos de esbeltez (antes de propuesta)
        slenderness_data = flexure_result.get('slenderness', {})

        # 8. Propuesta de diseño (si falla)
        proposal = None
        if overall_status != "OK":
            proposal = self._proposal_service.generate_proposal(
                pier=pier,
                pier_forces=pier_forces,
                flexure_sf=flexure_result['sf'],
                shear_dcr=shear_result['dcr_combined'],
                boundary_required=boundary.get('required', False),
                slenderness_reduction=slenderness_data.get('reduction', 1.0)
            )

        # 9. Gráfico P-M
        pm_plot = ""
        if generate_plot:
            pm_plot = self._plot_generator.generate_pm_diagram(
                capacity_curve=flexure_result['design_curve'],
                demand_points=flexure_result['demand_points'],
                pier_label=f"{pier.story} - {pier.label}",
                safety_factor=flexure_result['sf'],
                moment_axis=moment_axis,
                angle_deg=angle_deg
            )

        # Preparar datos de propuesta (solo si hay propuesta exitosa)
        has_proposal = proposal is not None and proposal.success
        if has_proposal:
            original_thickness = proposal.original_config.thickness
            proposal_failure_mode = proposal.failure_mode.value
            proposal_type = proposal.proposal_type.value
            proposal_description = proposal.proposed_config.description(original_thickness)
            proposal_sf_original = proposal.original_sf_flexure
            proposal_sf_proposed = proposal.proposed_sf_flexure
            proposal_dcr_original = proposal.original_dcr_shear
            proposal_dcr_proposed = proposal.proposed_dcr_shear
            proposal_success = True
            proposal_changes = ", ".join(proposal.changes)
        else:
            proposal_failure_mode = ""
            proposal_type = ""
            proposal_description = ""
            proposal_sf_original = 0.0
            proposal_sf_proposed = 0.0
            proposal_dcr_original = 0.0
            proposal_dcr_proposed = 0.0
            proposal_success = False
            proposal_changes = ""

        return VerificationResult(
            pier_label=pier.label,
            story=pier.story,
            width_m=pier.width / 1000,
            thickness_m=pier.thickness / 1000,
            height_m=pier.height / 1000,
            fc_MPa=pier.fc,
            fy_MPa=pier.fy,
            As_vertical_mm2=pier.As_vertical,
            As_horizontal_mm2=pier.As_horizontal,
            rho_vertical=pier.rho_vertical,
            rho_horizontal=pier.rho_horizontal,
            flexure_sf=flexure_result['sf'],
            flexure_status=flexure_result['status'],
            critical_combo_flexure=flexure_result['critical_combo'],
            flexure_phi_Mn_0=flexure_result['phi_Mn_0'],
            flexure_phi_Mn_at_Pu=flexure_result['phi_Mn_at_Pu'],
            flexure_Pu=flexure_result['Pu'],
            flexure_Mu=flexure_result['Mu'],
            flexure_exceeds_axial=flexure_result.get('exceeds_axial_capacity', False),
            flexure_phi_Pn_max=flexure_result.get('phi_Pn_max', 0.0),
            shear_sf=shear_result['sf'],
            shear_status=shear_result['status'],
            critical_combo_shear=shear_result['critical_combo'],
            shear_dcr_2=shear_result['dcr_2'],
            shear_dcr_3=shear_result['dcr_3'],
            shear_dcr_combined=shear_result['dcr_combined'],
            shear_phi_Vn_2=shear_result['phi_Vn_2'],
            shear_phi_Vn_3=shear_result['phi_Vn_3'],
            shear_Vu_2=shear_result['Vu_2'],
            shear_Vu_3=shear_result['Vu_3'],
            shear_Vc=shear_result.get('Vc', 0),
            shear_Vs=shear_result.get('Vs', 0),
            shear_alpha_c=shear_result.get('alpha_c', 0),
            shear_formula_type=shear_result.get('formula_type', 'wall'),
            overall_status=overall_status,
            slenderness_lambda=slenderness_data.get('lambda', 0.0),
            slenderness_is_slender=slenderness_data.get('is_slender', False),
            slenderness_reduction=slenderness_data.get('reduction', 1.0),
            pm_plot_base64=pm_plot,
            # Clasificación ACI 318-25 §18.10.8
            classification_type=classification.get('type', ''),
            classification_lw_tw=classification.get('lw_tw', 0),
            classification_hw_lw=classification.get('hw_lw', 0),
            classification_aci_section=classification.get('aci_section', ''),
            classification_is_wall_pier=classification.get('is_wall_pier', False),
            # Amplificación de cortante ACI 318-25 §18.10.3.3
            amplification_omega_v=amplification.get('omega_v', 1.0),
            amplification_omega_v_dyn=amplification.get('omega_v_dyn', 1.0),
            amplification_factor=amplification.get('amplification', 1.0),
            amplification_Ve=amplification.get('Ve', 0),
            amplification_applies=amplification.get('applies', False),
            # Elementos de borde ACI 318-25 §18.10.6
            boundary_required=boundary.get('required', False),
            boundary_method=boundary.get('method', ''),
            boundary_sigma_max=boundary_sigma_max,
            boundary_limit=boundary_limit,
            boundary_length_mm=boundary_length,
            boundary_aci_reference=boundary.get('aci_reference', ''),
            # Continuidad del muro
            continuity_hwcs_m=(hwcs / 1000) if hwcs else pier.height / 1000,
            continuity_n_stories=continuity_info.n_stories if continuity_info else 1,
            continuity_is_continuous=continuity_info.is_continuous if continuity_info else False,
            continuity_is_base=continuity_info.is_base if continuity_info else True,
            continuity_hwcs_lw=(hwcs / pier.width) if hwcs and pier.width > 0 else (pier.height / pier.width if pier.width > 0 else 0),
            # Propuesta de diseño
            has_proposal=has_proposal,
            proposal_failure_mode=proposal_failure_mode,
            proposal_type=proposal_type,
            proposal_description=proposal_description,
            proposal_sf_original=proposal_sf_original,
            proposal_sf_proposed=proposal_sf_proposed,
            proposal_dcr_original=proposal_dcr_original,
            proposal_dcr_proposed=proposal_dcr_proposed,
            proposal_success=proposal_success,
            proposal_changes=proposal_changes
        )

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

    def get_section_diagram(self, session_id: str, pier_key: str) -> Dict[str, Any]:
        """Genera un diagrama de la sección transversal del pier."""
        return self._capacity_service.get_section_diagram(session_id, pier_key)

    def get_pier_capacities(self, session_id: str, pier_key: str) -> Dict[str, Any]:
        """Calcula las capacidades puras del pier (sin interacción)."""
        return self._capacity_service.get_pier_capacities(session_id, pier_key)

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
