# app/services/analysis/shear/facade.py
"""
Fachada principal para servicios de cortante.

ShearService orquesta todos los servicios especializados:
- WallShearService: Verificacion de cortante de muros
- ColumnShearService: Verificacion de cortante de columnas
- WallClassificationService: Clasificacion §18.10.8
- ShearAmplificationService: Amplificacion §18.10.3.3
- BoundaryElementService: Elementos de borde §18.10.6
- CouplingBeamService: Vigas de acoplamiento §18.10.7
"""
from typing import Dict, Any, Optional, List, Tuple

from ....domain.entities import Pier, PierForces, Column, ColumnForces
from ....domain.shear import WallClassification, WallGroupShearResult
from ....domain.chapter18 import BoundaryElementResult, CouplingBeamDesignResult
from ....domain.chapter18.design_forces import ShearAmplificationResult

from .column_shear import ColumnShearService
from .wall_shear import WallShearService
from .wall_special_elements import (
    WallClassificationService,
    ShearAmplificationService,
    BoundaryElementService,
    CouplingBeamService,
)
from ..formatting import format_safety_factor


class ShearService:
    """
    Fachada principal - orquesta todos los servicios de cortante.

    Responsabilidades:
    - Verificar corte con interaccion V2-V3
    - Clasificar muros y pilares de muro §18.10.8
    - Amplificar cortante para muros especiales §18.10.3.3
    - Verificar elementos de borde §18.10.6
    - Verificar vigas de acoplamiento §18.10.7
    - Verificar cortante de columnas §22.5 y §18.7.6
    """

    def __init__(self):
        self._wall = WallShearService()
        self._column = ColumnShearService()
        self._classification = WallClassificationService()
        self._amplification = ShearAmplificationService()
        self._boundary = BoundaryElementService()
        self._coupling = CouplingBeamService()

    # =========================================================================
    # VERIFICACION DE MUROS
    # =========================================================================

    def check_shear(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        Mpr_total: float = 0,
        lu: float = 0,
        lambda_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Verifica corte con interaccion V2-V3 y retorna el caso critico.

        Args:
            pier: Pier a verificar
            pier_forces: Fuerzas del pier (combinaciones)
            Mpr_total: Momento probable total de vigas de acople (kN-m)
            lu: Altura libre del pier (mm)
            lambda_factor: Factor de concreto liviano

        Returns:
            Dict con resultados de la verificacion de corte
        """
        classification = self._classification.classify_wall(pier)
        return self._wall.check_shear(
            pier, pier_forces, Mpr_total, lu, lambda_factor, classification
        )

    def get_shear_capacity(self, pier: Pier, Nu: float = 0) -> Dict[str, Any]:
        """Calcula las capacidades de corte puro del pier."""
        return self._wall.get_shear_capacity(pier, Nu)

    def verify_bidirectional_shear(
        self,
        lw: float,
        tw: float,
        hw: float,
        fc: float,
        fy: float,
        rho_h: float,
        Vu2_max: float,
        Vu3_max: float,
        Nu: float = 0,
        rho_v: Optional[float] = None
    ):
        """Expone el metodo de verificacion bidireccional."""
        return self._wall.verify_bidirectional_shear(
            lw, tw, hw, fc, fy, rho_h, Vu2_max, Vu3_max, Nu, rho_v
        )

    def verify_wall_group(
        self,
        segments: List[Tuple[float, float, float]],
        fc: float,
        fy: float,
        rho_h: float,
        Vu_total: float,
        Nu: float = 0,
        rho_v: Optional[float] = None
    ) -> WallGroupShearResult:
        """Verifica un grupo de segmentos de muro segun §18.10.4.4."""
        return self._wall.verify_wall_group(
            segments, fc, fy, rho_h, Vu_total, Nu, rho_v
        )

    # =========================================================================
    # CLASIFICACION DE MUROS (§18.10.8)
    # =========================================================================

    def classify_wall(self, pier: Pier) -> WallClassification:
        """Clasifica un pier segun ACI 318-25 §18.10.8."""
        return self._classification.classify_wall(pier)

    def get_classification_dict(self, pier: Pier) -> Dict[str, Any]:
        """Obtiene la clasificacion del pier como diccionario."""
        return self._classification.get_classification_dict(pier)

    # =========================================================================
    # AMPLIFICACION DE CORTANTE (§18.10.3.3)
    # =========================================================================

    def amplify_shear(
        self,
        pier: Pier,
        Vu: float,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        use_omega_0: bool = False,
        omega_0: float = 2.5
    ) -> ShearAmplificationResult:
        """Amplifica el cortante sismico segun ACI 318-25 §18.10.3.3."""
        return self._amplification.amplify_shear(
            pier, Vu, hwcs, hn_ft, use_omega_0, omega_0
        )

    def get_amplification_dict(
        self,
        pier: Pier,
        Vu: float,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """Obtiene la amplificacion de cortante como diccionario."""
        return self._amplification.get_amplification_dict(pier, Vu, hwcs, hn_ft)

    # =========================================================================
    # ELEMENTOS DE BORDE (§18.10.6)
    # =========================================================================

    def check_boundary_element(
        self,
        pier: Pier,
        Pu: float,
        Mu: float,
        c: Optional[float] = None,
        delta_u: Optional[float] = None,
        Vu: float = 0,
        method: str = 'auto'
    ) -> BoundaryElementResult:
        """Verifica si se requiere elemento de borde segun §18.10.6."""
        return self._boundary.check_boundary_element(
            pier, Pu, Mu, c, delta_u, Vu, method
        )

    def get_boundary_element_dict(
        self,
        pier: Pier,
        Pu: float,
        Mu: float
    ) -> Dict[str, Any]:
        """Obtiene la verificacion de elemento de borde como diccionario."""
        return self._boundary.get_boundary_element_dict(pier, Pu, Mu)

    # =========================================================================
    # VERIFICACION COMPLETA
    # =========================================================================

    def check_complete(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Realiza verificacion completa del pier incluyendo todas las mejoras ACI 318-25.

        Incluye:
        - Clasificacion del elemento (§18.10.8)
        - Verificacion de cortante con interaccion V2-V3
        - Amplificacion de cortante (§18.10.3.3)
        - Verificacion de elementos de borde (§18.10.6)

        Args:
            pier: Pier a verificar
            pier_forces: Fuerzas del pier
            hwcs: Altura desde seccion critica (mm), opcional
            hn_ft: Altura total del edificio (pies), opcional

        Returns:
            Dict con verificacion completa
        """
        # 1. Clasificacion
        classification = self.get_classification_dict(pier)

        # 2. Verificacion de cortante basica
        shear_result = self.check_shear(pier, pier_forces)

        # 3. Amplificacion de cortante (si aplica)
        Vu_max = shear_result.get('Vu_2', 0)
        amplification = self.get_amplification_dict(pier, Vu_max, hwcs=hwcs, hn_ft=hn_ft)

        # 4. Verificacion de elementos de borde (si hay fuerzas)
        boundary = None
        if pier_forces and pier_forces.combinations:
            critical_combo = None
            for combo in pier_forces.combinations:
                if combo.name == shear_result.get('critical_combo'):
                    critical_combo = combo
                    break

            if critical_combo:
                Pu = -critical_combo.P
                Mu = abs(critical_combo.M3)
                boundary = self.get_boundary_element_dict(pier, Pu, Mu)

        return {
            'classification': classification,
            'shear': shear_result,
            'amplification': amplification,
            'boundary_element': boundary
        }

    # =========================================================================
    # VIGAS DE ACOPLAMIENTO (§18.10.7)
    # =========================================================================

    def check_coupling_beam(
        self,
        ln: float,
        h: float,
        bw: float,
        Vu: float,
        fc: float,
        fy_diagonal: float,
        fyt: float,
        lambda_factor: float = 1.0
    ) -> CouplingBeamDesignResult:
        """Verifica viga de acoplamiento segun ACI 318-25 §18.10.7."""
        return self._coupling.check_coupling_beam(
            ln, h, bw, Vu, fc, fy_diagonal, fyt, lambda_factor
        )

    def get_coupling_beam_dict(
        self,
        ln: float,
        h: float,
        bw: float,
        Vu: float,
        fc: float,
        fy_diagonal: float,
        fyt: float
    ) -> Dict[str, Any]:
        """Obtiene la verificacion de viga de acople como diccionario."""
        return self._coupling.get_coupling_beam_dict(
            ln, h, bw, Vu, fc, fy_diagonal, fyt
        )

    # =========================================================================
    # CORTANTE DE COLUMNAS (§22.5 y §18.7.6)
    # =========================================================================

    def check_column_shear(
        self,
        column: Column,
        column_forces: Optional[ColumnForces],
        Mpr_top: float = 0,
        Mpr_bottom: float = 0,
        lambda_factor: float = 1.0
    ) -> Dict[str, Any]:
        """Verifica cortante de una columna segun ACI 318-25."""
        return self._column.check_column_shear(
            column, column_forces, Mpr_top, Mpr_bottom, lambda_factor
        )

    def check_column_shear_from_pier(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        lambda_factor: float = 1.0
    ) -> Dict[str, Any]:
        """Verifica cortante de un Pier tratado como columna."""
        return self._column.check_column_shear_from_pier(
            pier, pier_forces, lambda_factor
        )

    def _format_sf(self, value: float) -> Any:
        """Formatea SF para JSON. Convierte inf a '>100'."""
        return format_safety_factor(value, as_string=True)
