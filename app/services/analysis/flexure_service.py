# app/structural/services/analysis/flexure_service.py
"""
Servicio de análisis de flexocompresión para piers.
Maneja la generación de curvas de interacción y verificación de capacidad.
"""
from typing import Dict, List, Any, Optional, Tuple

from ...domain.entities import Pier, PierForces
from ...domain.flexure import (
    InteractionDiagramService,
    SlendernessService,
    SteelLayer,
    InteractionPoint,
)


class FlexureService:
    """
    Servicio para análisis de flexocompresión de piers.

    Responsabilidades:
    - Generar curvas de interacción P-M
    - Verificar capacidad de flexocompresión
    - Calcular capacidades puras
    - Manejar efectos de esbeltez
    """

    def __init__(self):
        self._interaction_service = InteractionDiagramService()
        self._slenderness_service = SlendernessService()

    def pier_to_steel_layers(self, pier: Pier) -> List[SteelLayer]:
        """
        Convierte las capas de acero del pier a objetos SteelLayer.

        Args:
            pier: Pier con la configuración de armadura

        Returns:
            Lista de SteelLayer para usar en generate_interaction_curve
        """
        return [
            SteelLayer(position=pos, area=area)
            for pos, area in pier.get_steel_layers()
        ]

    def generate_interaction_curve(
        self,
        pier: Pier,
        apply_slenderness: bool = True
    ) -> Tuple[List[InteractionPoint], Dict[str, Any]]:
        """
        Genera la curva de interacción P-M para un pier.

        Args:
            pier: Pier a analizar
            apply_slenderness: Si aplicar reducción por esbeltez

        Returns:
            Tuple (interaction_points, slenderness_data)
        """
        # Analizar esbeltez
        slenderness = self._slenderness_service.analyze(pier, k=0.8, braced=True)
        slenderness_data = {
            'lambda': round(slenderness.lambda_ratio, 1),
            'is_slender': slenderness.is_slender,
            'reduction': round(slenderness.buckling_factor, 3) if slenderness.is_slender else 1.0
        }

        # Generar capas de acero
        steel_layers = self.pier_to_steel_layers(pier)

        # Generar curva de interacción
        interaction_points = self._interaction_service.generate_interaction_curve(
            width=pier.width,
            thickness=pier.thickness,
            fc=pier.fc,
            fy=pier.fy,
            As_total=pier.As_flexure_total,
            cover=pier.cover,
            steel_layers=steel_layers
        )

        # Aplicar reducción por esbeltez si corresponde
        if apply_slenderness and slenderness.is_slender:
            reduction = slenderness.buckling_factor
            for point in interaction_points:
                point.phi_Pn *= reduction
                point.Pn *= reduction

        return interaction_points, slenderness_data

    def check_flexure(
        self,
        pier: Pier,
        pier_forces: Optional[PierForces],
        moment_axis: str = 'M3',
        angle_deg: float = 0
    ) -> Dict[str, Any]:
        """
        Verifica flexocompresión con efectos de esbeltez.

        Args:
            pier: Pier a verificar
            pier_forces: Fuerzas del pier (combinaciones)
            moment_axis: Eje del momento ('M2' o 'M3')
            angle_deg: Ángulo del momento resultante

        Returns:
            Dict con resultados de la verificación
        """
        # Generar curva con esbeltez
        interaction_points, slenderness_data = self.generate_interaction_curve(pier)
        design_curve = self._interaction_service.get_design_curve(interaction_points)

        # Obtener puntos de demanda
        demand_points = []
        if pier_forces and pier_forces.combinations:
            demand_points = pier_forces.get_critical_pm_points(
                moment_axis=moment_axis,
                angle_deg=angle_deg
            )

        # Verificar
        if demand_points:
            sf, status, critical, phi_Mn_0, phi_Mn_at_Pu, critical_Pu, critical_Mu = \
                self._interaction_service.check_flexure(interaction_points, demand_points)
        else:
            sf, status, critical = float('inf'), "OK", "N/A"
            phi_Mn_0, phi_Mn_at_Pu, critical_Pu, critical_Mu = 0.0, 0.0, 0.0, 0.0

        return {
            'sf': sf,
            'status': status,
            'critical_combo': critical,
            'phi_Mn_0': phi_Mn_0,           # Capacidad a P=0 (flexión pura)
            'phi_Mn_at_Pu': phi_Mn_at_Pu,   # Capacidad a Pu crítico
            'Pu': critical_Pu,
            'Mu': critical_Mu,
            'design_curve': design_curve,
            'demand_points': demand_points,
            'slenderness': slenderness_data
        }

    def get_capacities(self, pier: Pier) -> Dict[str, Any]:
        """
        Calcula las capacidades puras del pier (sin demanda).

        Args:
            pier: Pier a analizar

        Returns:
            Dict con capacidades de compresión, momentos y corte
        """
        # Esbeltez
        slenderness = self._slenderness_service.analyze(pier, k=0.8, braced=True)

        # 1. Compresión pura
        phi_compression = 0.65
        Ag = pier.width * pier.thickness
        As_total = pier.As_flexure_total
        Pn_max = 0.80 * (0.85 * pier.fc * (Ag - As_total) + pier.fy * As_total)
        phi_Pn_max = phi_compression * Pn_max / 9806.65  # tonf

        # 2. Momento M3 (eje fuerte)
        steel_layers_M3 = self.pier_to_steel_layers(pier)
        interaction_points_M3 = self._interaction_service.generate_interaction_curve(
            width=pier.width,
            thickness=pier.thickness,
            fc=pier.fc,
            fy=pier.fy,
            As_total=pier.As_flexure_total,
            cover=pier.cover,
            n_points=30,
            steel_layers=steel_layers_M3
        )
        phi_Mn3 = self._interaction_service._get_phi_Mn_at_P0(interaction_points_M3)

        # 3. Momento M2 (eje débil)
        steel_layers_M2 = [
            SteelLayer(position=pier.cover, area=pier.As_flexure_total / 2),
            SteelLayer(position=pier.thickness - pier.cover, area=pier.As_flexure_total / 2)
        ]
        interaction_points_M2 = self._interaction_service.generate_interaction_curve(
            width=pier.thickness,
            thickness=pier.width,
            fc=pier.fc,
            fy=pier.fy,
            As_total=pier.As_flexure_total,
            cover=pier.cover,
            n_points=30,
            steel_layers=steel_layers_M2
        )
        phi_Mn2 = self._interaction_service._get_phi_Mn_at_P0(interaction_points_M2)

        return {
            'phi_Pn_max': round(phi_Pn_max, 1),
            'phi_Mn3': round(phi_Mn3, 2),
            'phi_Mn2': round(phi_Mn2, 2),
            'slenderness': {
                'lambda': round(slenderness.lambda_ratio, 1),
                'is_slender': slenderness.is_slender,
                'reduction': round(slenderness.buckling_factor, 3) if slenderness.is_slender else 1.0
            }
        }
