# app/services/analysis/element_orchestrator.py
"""
Orquestador central para verificación de elementos estructurales.

Clasifica el elemento, resuelve su comportamiento de diseño,
y delega las verificaciones al servicio de dominio apropiado.

Este orquestador es "thin" - solo coordina, no implementa lógica de verificación.
Los servicios de dominio (SeismicColumnService, SeismicBeamService, SeismicWallService)
son "thick" y contienen la lógica real de verificación.

Usa ForceExtractor y GeometryNormalizer para evitar duplicación de código.
"""
from typing import Union, Optional, Dict, Any, List, TYPE_CHECKING
from dataclasses import dataclass, field

from .element_classifier import ElementClassifier, ElementType
from .design_behavior_resolver import DesignBehaviorResolver
from .design_behavior import DesignBehavior
from .flexocompression_service import FlexocompressionService
from .shear_service import ShearService
from .force_extractor import ForceExtractor
from .geometry_normalizer import GeometryNormalizer
from ...domain.chapter18 import (
    SeismicColumnService,
    SeismicBeamService,
    SeismicWallService,
    SeismicCategory,
)
from ...domain.flexure import FlexureChecker
from ...domain.shear.combined import calculate_combined_dcr

if TYPE_CHECKING:
    from ...domain.entities import Beam, Column, Pier, DropBeam
    from ...domain.entities import BeamForces, ColumnForces, PierForces, DropBeamForces
    from ...domain.entities import LoadCombination


@dataclass
class OrchestrationResult:
    """
    Resultado de la orquestación de verificación.

    Contiene el resultado específico del servicio de dominio usado
    y metadata sobre la clasificación y comportamiento.
    """
    element_type: ElementType
    design_behavior: DesignBehavior
    service_used: str                 # 'column', 'beam', 'wall', 'flexure'
    domain_result: Any                # SeismicColumnResult, SeismicBeamResult, etc.
    is_ok: bool
    dcr_max: float
    critical_check: str
    warnings: list


@dataclass
class CombinationResult:
    """
    Resultado de verificación para UNA combinación de carga específica.

    Usado para análisis detallado por combinación (ej: get_pier_combinations).
    Contiene factores de seguridad individuales para flexión y cortante.
    """
    # Identificación de la combinación
    index: int
    name: str
    location: str
    step_type: str

    # Fuerzas de la combinación
    P: float               # Carga axial (tonf, positivo=compresión)
    V2: float              # Cortante V2 (tonf)
    V3: float              # Cortante V3 (tonf)
    M2: float              # Momento M2 (tonf-m)
    M3: float              # Momento M3 (tonf-m)
    M_resultant: float     # Momento resultante (tonf-m)
    angle_deg: float       # Ángulo del momento (grados)

    # Resultados de verificación
    flexure_sf: float      # Factor de seguridad a flexión
    flexure_status: str    # 'OK', 'NO OK'
    shear_sf_v2: float     # Factor de seguridad cortante V2
    shear_sf_v3: float     # Factor de seguridad cortante V3
    shear_dcr_combined: float  # DCR combinado biaxial
    overall_status: str    # 'OK', 'NO OK'

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'index': self.index,
            'name': self.name,
            'location': self.location,
            'step_type': self.step_type,
            'full_name': f"{self.name} ({self.location})" if self.location else self.name,
            'P': round(self.P, 2),
            'M2': round(self.M2, 2),
            'M3': round(self.M3, 2),
            'V2': round(self.V2, 2),
            'V3': round(self.V3, 2),
            'M_resultant': round(self.M_resultant, 2),
            'angle_deg': round(self.angle_deg, 1),
            'flexure_sf': round(self.flexure_sf, 2) if self.flexure_sf < 100 else '>100',
            'flexure_status': self.flexure_status,
            'shear_sf_2': round(self.shear_sf_v2, 2) if self.shear_sf_v2 < 100 else '>100',
            'shear_sf_3': round(self.shear_sf_v3, 2) if self.shear_sf_v3 < 100 else '>100',
            'shear_dcr_combined': round(self.shear_dcr_combined, 3),
            'shear_sf_combined': f"{1/self.shear_dcr_combined:.2f}" if self.shear_dcr_combined > 0 else '>100',
            'overall_status': self.overall_status,
        }


class ElementOrchestrator:
    """
    Orquestador central para verificación de elementos.

    Flujo:
    1. Clasificar elemento → ElementType
    2. Resolver comportamiento → DesignBehavior
    3. Delegar a servicio de dominio apropiado
    4. Retornar resultado unificado

    El orquestador usa DesignBehavior.service_type para determinar
    qué servicio de dominio usar, garantizando que:
    - SEISMIC_COLUMN y WALL_PIER_COLUMN → SeismicColumnService
    - SEISMIC_BEAM → SeismicBeamService
    - SEISMIC_WALL, WALL_PIER_ALT, DROP_BEAM → SeismicWallService
    - FLEXURE_* → FlexocompressionService

    Example:
        orchestrator = ElementOrchestrator()

        # Verificar cualquier elemento
        result = orchestrator.verify(pier, forces, lambda_factor=1.0)

        # El orquestador clasifica automáticamente y delega
        print(result.design_behavior.aci_section)  # e.g., "§18.7" o "§18.10"
        print(result.service_used)                  # e.g., "column" o "wall"
    """

    def __init__(
        self,
        classifier: Optional[ElementClassifier] = None,
        resolver: Optional[DesignBehaviorResolver] = None,
        column_service: Optional[SeismicColumnService] = None,
        beam_service: Optional[SeismicBeamService] = None,
        wall_service: Optional[SeismicWallService] = None,
        flexo_service: Optional[FlexocompressionService] = None,
        shear_service: Optional[ShearService] = None,
    ):
        """
        Inicializa el orquestador con servicios de dominio.

        Todos los parámetros son opcionales y se crean por defecto
        si no se proporcionan (para facilitar pruebas).
        """
        self._classifier = classifier or ElementClassifier()
        self._resolver = resolver or DesignBehaviorResolver()
        self._column_service = column_service or SeismicColumnService()
        self._beam_service = beam_service or SeismicBeamService()
        self._wall_service = wall_service or SeismicWallService()
        self._flexo_service = flexo_service or FlexocompressionService()
        self._shear_service = shear_service or ShearService()

    def verify(
        self,
        element: Union['Beam', 'Column', 'Pier', 'DropBeam'],
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces']] = None,
        *,
        lambda_factor: float = 1.0,
        category: SeismicCategory = SeismicCategory.SPECIAL,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        moment_axis: str = 'M3',
    ) -> OrchestrationResult:
        """
        Verifica un elemento estructural delegando al servicio apropiado.

        Args:
            element: Entidad del elemento (Beam, Column, Pier, DropBeam)
            forces: Fuerzas del elemento
            lambda_factor: Factor para concreto liviano (default 1.0)
            category: Categoría sísmica (default SPECIAL)
            hwcs: Altura desde sección crítica (mm), para muros
            hn_ft: Altura del edificio (pies), para amplificación
            moment_axis: Eje de momento ('M2', 'M3'), para columnas

        Returns:
            OrchestrationResult con resultado del servicio de dominio
        """
        # 1. Clasificar elemento
        element_type = self._classifier.classify(element)

        # 2. Resolver comportamiento de diseño
        is_seismic = getattr(element, 'is_seismic', True)
        design_behavior = self._resolver.resolve(element_type, element, forces, is_seismic)

        # 3. Delegar según service_type del comportamiento
        # Esto garantiza consistencia: el comportamiento define qué servicio usar
        service_type = design_behavior.service_type

        if service_type == 'column':
            return self._verify_as_column(
                element, forces, element_type, design_behavior,
                lambda_factor, category
            )

        elif service_type == 'wall':
            return self._verify_as_wall(
                element, forces, element_type, design_behavior,
                lambda_factor, category, hwcs, hn_ft
            )

        elif service_type == 'beam':
            return self._verify_as_beam(
                element, forces, element_type, design_behavior,
                lambda_factor, category
            )

        else:  # 'flexure'
            return self._verify_flexure(
                element, forces, element_type, design_behavior, moment_axis
            )

    # =========================================================================
    # MÉTODOS DE DELEGACIÓN
    # =========================================================================

    def _verify_as_column(
        self,
        element: Union['Column', 'Pier'],
        forces: Optional[Union['ColumnForces', 'PierForces']],
        element_type: ElementType,
        design_behavior: DesignBehavior,
        lambda_factor: float,
        category: SeismicCategory,
    ) -> OrchestrationResult:
        """Delega verificación a SeismicColumnService (§18.7)."""
        # Usar servicios auxiliares para normalizar datos
        geom = GeometryNormalizer.to_column(element)
        envelope = ForceExtractor.extract_envelope(forces)

        # Llamar servicio
        result = self._column_service.verify_column(
            b=geom.b, h=geom.h, lu=geom.lu, cover=geom.cover, Ag=geom.Ag,
            fc=geom.fc, fy=geom.fy, fyt=geom.fyt,
            Ast=geom.Ast, n_bars=geom.n_bars, db_long=geom.db_long,
            s_transverse=geom.s_transverse, Ash=geom.Ash, hx=geom.hx,
            Vu_V2=envelope.V2_max, Vu_V3=envelope.V3_max, Pu=envelope.P_max,
            category=category,
            lambda_factor=lambda_factor,
        )

        return OrchestrationResult(
            element_type=element_type,
            design_behavior=design_behavior,
            service_used='column',
            domain_result=result,
            is_ok=result.is_ok,
            dcr_max=result.dcr_max,
            critical_check=result.critical_check,
            warnings=result.warnings,
        )

    def _verify_as_wall(
        self,
        element: Union['Pier', 'DropBeam'],
        forces: Optional[Union['PierForces', 'DropBeamForces']],
        element_type: ElementType,
        design_behavior: DesignBehavior,
        lambda_factor: float,
        category: SeismicCategory,
        hwcs: Optional[float],
        hn_ft: Optional[float],
    ) -> OrchestrationResult:
        """Delega verificación a SeismicWallService (§18.10)."""
        from ...domain.entities import DropBeam

        # Usar ForceExtractor para normalizar fuerzas
        envelope = ForceExtractor.extract_envelope(forces)
        Vu = envelope.V2_max
        Mu = envelope.M3_max
        Pu = envelope.P_max

        # Llamar servicio según tipo
        if isinstance(element, DropBeam):
            result = self._wall_service.verify_drop_beam(
                drop_beam=element,
                Vu=Vu, Mu=Mu, Pu=Pu,
                lambda_factor=lambda_factor,
                category=category,
            )
        else:
            result = self._wall_service.verify_wall(
                pier=element,
                Vu=Vu, Mu=Mu, Pu=Pu,
                hwcs=hwcs, hn_ft=hn_ft,
                lambda_factor=lambda_factor,
                category=category,
            )

        return OrchestrationResult(
            element_type=element_type,
            design_behavior=design_behavior,
            service_used='wall',
            domain_result=result,
            is_ok=result.is_ok,
            dcr_max=result.dcr_max,
            critical_check=result.critical_check,
            warnings=result.warnings,
        )

    def _verify_as_beam(
        self,
        element: 'Beam',
        forces: Optional['BeamForces'],
        element_type: ElementType,
        design_behavior: DesignBehavior,
        lambda_factor: float,
        category: SeismicCategory,
    ) -> OrchestrationResult:
        """Delega verificación a SeismicBeamService (§18.6)."""
        # Usar servicios auxiliares para normalizar datos
        geom = GeometryNormalizer.to_beam(element)
        envelope = ForceExtractor.extract_envelope(forces)

        # Llamar servicio
        result = self._beam_service.verify_beam(
            bw=geom.bw, h=geom.h, d=geom.d, ln=geom.ln, cover=geom.cover,
            fc=geom.fc, fy=geom.fy, fyt=geom.fyt,
            As_top=geom.As_top, As_bottom=geom.As_bottom,
            n_bars_top=geom.n_bars_top, n_bars_bottom=geom.n_bars_bottom,
            db_long=geom.db_long,
            s_in_zone=geom.s_in_zone, s_outside_zone=geom.s_outside_zone,
            Av=geom.Av,
            Vu=envelope.V2_max, Mpr_left=0, Mpr_right=0,
            category=category,
            lambda_factor=lambda_factor,
        )

        return OrchestrationResult(
            element_type=element_type,
            design_behavior=design_behavior,
            service_used='beam',
            domain_result=result,
            is_ok=result.is_ok,
            dcr_max=result.dcr_max,
            critical_check=result.critical_check,
            warnings=result.warnings,
        )

    def _verify_flexure(
        self,
        element: Union['Beam', 'Column', 'Pier'],
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces']],
        element_type: ElementType,
        design_behavior: DesignBehavior,
        moment_axis: str,
    ) -> OrchestrationResult:
        """Delega verificación a FlexocompressionService."""
        # Calcular capacidad usando flexocompression service
        result = self._flexo_service.check_flexure(element, forces, moment_axis)

        dcr = 0
        if result and 'SF' in result:
            sf = result['SF']
            dcr = 1 / sf if sf > 0 else float('inf')

        is_ok = dcr <= 1.0

        return OrchestrationResult(
            element_type=element_type,
            design_behavior=design_behavior,
            service_used='flexure',
            domain_result=result,
            is_ok=is_ok,
            dcr_max=round(dcr, 3),
            critical_check='flexure' if not is_ok else '',
            warnings=[],
        )

    # =========================================================================
    # MÉTODOS DE CONVENIENCIA
    # =========================================================================

    def classify(
        self,
        element: Union['Beam', 'Column', 'Pier', 'DropBeam'],
    ) -> ElementType:
        """Clasifica un elemento. Alias para acceso directo."""
        return self._classifier.classify(element)

    def resolve_behavior(
        self,
        element: Union['Beam', 'Column', 'Pier', 'DropBeam'],
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces']] = None,
    ) -> DesignBehavior:
        """Resuelve el comportamiento de diseño. Alias para acceso directo."""
        element_type = self._classifier.classify(element)
        is_seismic = getattr(element, 'is_seismic', True)
        return self._resolver.resolve(element_type, element, forces, is_seismic)

    def get_verification_info(
        self,
        element: Union['Beam', 'Column', 'Pier', 'DropBeam'],
        forces: Optional[Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces']] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene información sobre cómo se verificaría un elemento.

        Útil para debug o UI.
        """
        element_type = self._classifier.classify(element)
        is_seismic = getattr(element, 'is_seismic', True)
        behavior = self._resolver.resolve(element_type, element, forces, is_seismic)

        # Determinar servicio basado en service_type
        service_names = {
            'column': 'SeismicColumnService (§18.7)',
            'beam': 'SeismicBeamService (§18.6)',
            'wall': 'SeismicWallService (§18.10)',
            'flexure': 'FlexocompressionService',
        }
        service = service_names.get(behavior.service_type, 'FlexocompressionService')

        return {
            'element_type': element_type.value,
            'design_behavior': behavior.name,
            'aci_section': behavior.aci_section,
            'service': service,
            'requires_pm_diagram': behavior.requires_pm_diagram,
            'requires_seismic_checks': behavior.requires_seismic_checks,
        }

    # =========================================================================
    # VERIFICACIÓN POR COMBINACIÓN
    # =========================================================================

    def verify_combination(
        self,
        element: Union['Beam', 'Column', 'Pier', 'DropBeam'],
        combination: 'LoadCombination',
        index: int = 0,
        *,
        interaction_points: Optional[List] = None,
        lambda_factor: float = 1.0,
    ) -> CombinationResult:
        """
        Verifica un elemento para UNA combinación de carga específica.

        Este método centraliza la lógica que antes estaba en get_pier_combinations()
        de structural_analysis.py, permitiendo verificar cualquier elemento
        contra una combinación individual.

        Args:
            element: Entidad del elemento (Pier, Column, Beam, DropBeam)
            combination: Combinación de carga a verificar
            index: Índice de la combinación (para tracking)
            interaction_points: Puntos del diagrama P-M (si ya calculado, para reutilizar)
            lambda_factor: Factor para concreto liviano (default 1.0)

        Returns:
            CombinationResult con SF de flexión, cortante y estado general
        """
        # Si no tenemos interaction_points, generarlos
        if interaction_points is None:
            interaction_points, _ = self._flexo_service.generate_interaction_curve(
                element, direction='primary', apply_slenderness=True, k=0.8
            )

        # Extraer fuerzas de la combinación
        P = combination.P_compression  # Positivo = compresión
        M = combination.moment_resultant
        V2 = abs(combination.V2)
        V3 = abs(combination.V3)

        # 1. Verificar flexión usando FlexureChecker
        demand_point = [(P, M, combination.name)]
        flexure_result = FlexureChecker.check_flexure(interaction_points, demand_point)
        flexure_sf = flexure_result.safety_factor
        flexure_status = flexure_result.status

        # 2. Verificar cortante bidireccional
        # Obtener geometría para verificación de cortante
        shear_result = self._shear_service.verify_bidirectional_shear(
            lw=element.width,
            tw=element.thickness,
            hw=element.height,
            fc=element.fc,
            fy=element.fy,
            rho_h=element.rho_horizontal,
            Vu2_max=V2,
            Vu3_max=V3,
            Nu=P,
            lambda_factor=lambda_factor,
        )
        shear_sf_v2 = shear_result.result_V2.sf
        shear_sf_v3 = shear_result.result_V3.sf

        # 3. Calcular DCR combinado biaxial
        shear_dcr_combined = calculate_combined_dcr(shear_sf_v2, shear_sf_v3)

        # 4. Estado general
        fs_min = min(
            flexure_sf if flexure_sf < 100 else 100,
            shear_sf_v2 if shear_sf_v2 < 100 else 100,
            shear_sf_v3 if shear_sf_v3 < 100 else 100,
        )
        overall_status = 'OK' if fs_min >= 1.0 else 'NO OK'

        return CombinationResult(
            index=index,
            name=combination.name,
            location=combination.location,
            step_type=combination.step_type,
            P=P,
            V2=combination.V2,
            V3=combination.V3,
            M2=combination.M2,
            M3=combination.M3,
            M_resultant=M,
            angle_deg=combination.moment_angle_deg,
            flexure_sf=flexure_sf,
            flexure_status=flexure_status,
            shear_sf_v2=shear_sf_v2,
            shear_sf_v3=shear_sf_v3,
            shear_dcr_combined=shear_dcr_combined,
            overall_status=overall_status,
        )

    def verify_all_combinations(
        self,
        element: Union['Beam', 'Column', 'Pier', 'DropBeam'],
        forces: Union['BeamForces', 'ColumnForces', 'PierForces', 'DropBeamForces'],
        *,
        lambda_factor: float = 1.0,
        apply_slenderness: bool = True,
    ) -> List[CombinationResult]:
        """
        Verifica un elemento para TODAS sus combinaciones de carga.

        Optimiza generando el diagrama P-M una sola vez y reutilizándolo.

        Args:
            element: Entidad del elemento
            forces: Fuerzas con lista de combinaciones
            lambda_factor: Factor para concreto liviano
            apply_slenderness: Aplicar reducción por esbeltez al diagrama P-M

        Returns:
            Lista de CombinationResult, uno por cada combinación
        """
        # Generar diagrama P-M una sola vez
        interaction_points, _ = self._flexo_service.generate_interaction_curve(
            element, direction='primary', apply_slenderness=apply_slenderness, k=0.8
        )

        # Verificar cada combinación
        results = []
        for i, combo in enumerate(forces.combinations):
            result = self.verify_combination(
                element=element,
                combination=combo,
                index=i,
                interaction_points=interaction_points,
                lambda_factor=lambda_factor,
            )
            results.append(result)

        return results
