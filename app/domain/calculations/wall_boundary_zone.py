# app/domain/calculations/wall_boundary_zone.py
"""
Servicio para cálculo de zona de borde de muros según ACI 318-25 §18.10.2.4.

La zona de extremo se define como 0.15 × lw (longitud del muro).
Este servicio calcula el acero dentro de esa zona.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.pier import Pier


class WallBoundaryZoneService:
    """
    Servicio de cálculo para zonas de borde de muros.

    Según ACI 318-25 §18.10.2.4, la zona de extremo es 0.15 × lw.
    Este servicio centraliza el cálculo de acero en esa zona.
    """

    @staticmethod
    def calculate_boundary_zone_length(wall_length: float) -> float:
        """
        Calcula la longitud de la zona de borde.

        Args:
            wall_length: Longitud del muro lw (mm)

        Returns:
            Longitud de zona de borde = 0.15 × lw (mm)
        """
        return 0.15 * wall_length

    @staticmethod
    def calculate_steel_in_zone(
        pier: 'Pier',
        is_left: bool = True
    ) -> float:
        """
        Calcula el área de acero dentro de la zona de extremo (0.15×lw).

        Args:
            pier: Entidad Pier con propiedades de geometría y refuerzo
            is_left: True para extremo izquierdo, False para derecho

        Returns:
            Área de acero en mm² dentro de la zona de extremo
        """
        boundary_length = WallBoundaryZoneService.calculate_boundary_zone_length(
            pier.width
        )

        # 1. Barras de borde: todas están dentro de la zona de extremo
        As_edge = pier.As_edge_per_end

        # 2. Barras de malla dentro de la zona
        As_mesh = WallBoundaryZoneService._calculate_mesh_steel_in_zone(
            pier=pier,
            boundary_length=boundary_length,
            is_left=is_left
        )

        return As_edge + As_mesh

    @staticmethod
    def _calculate_mesh_steel_in_zone(
        pier: 'Pier',
        boundary_length: float,
        is_left: bool
    ) -> float:
        """
        Calcula el área de acero de malla dentro de la zona de borde.

        Las barras de malla empiezan en x=cover y se repiten cada spacing_v.
        Primera barra intermedia en x = cover + spacing_v.

        Args:
            pier: Entidad Pier
            boundary_length: Longitud de la zona de borde (mm)
            is_left: True para extremo izquierdo

        Returns:
            Área de acero de malla en la zona (mm²)
        """
        if pier.spacing_v <= 0:
            return 0.0

        As_mesh = 0.0
        bar_area = pier._bar_area_v

        if is_left:
            # Zona izquierda: desde 0 hasta boundary_length
            # Primera barra de malla en cover, luego cada spacing_v
            x = pier.cover
            while x < boundary_length and x < (pier.width - pier.cover):
                As_mesh += pier.n_meshes * bar_area
                x += pier.spacing_v
        else:
            # Zona derecha: desde (width - boundary_length) hasta width
            start_zone = pier.width - boundary_length
            # Última barra en width - cover, y hacia atrás cada spacing_v
            x = pier.width - pier.cover
            while x > start_zone and x > pier.cover:
                As_mesh += pier.n_meshes * bar_area
                x -= pier.spacing_v

        return As_mesh

    @staticmethod
    def get_boundary_zone_summary(pier: 'Pier') -> dict:
        """
        Obtiene un resumen del acero en ambas zonas de borde.

        Args:
            pier: Entidad Pier

        Returns:
            Diccionario con información de zonas de borde
        """
        boundary_length = WallBoundaryZoneService.calculate_boundary_zone_length(
            pier.width
        )
        As_left = WallBoundaryZoneService.calculate_steel_in_zone(pier, is_left=True)
        As_right = WallBoundaryZoneService.calculate_steel_in_zone(pier, is_left=False)

        return {
            'boundary_length_mm': boundary_length,
            'boundary_length_ratio': 0.15,
            'As_left_mm2': As_left,
            'As_right_mm2': As_right,
            'As_edge_per_end_mm2': pier.As_edge_per_end,
        }
