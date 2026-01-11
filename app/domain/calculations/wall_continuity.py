# app/domain/calculations/wall_continuity.py
"""
Cálculo de continuidad de muros y altura hwcs según ACI 318-25.

Este módulo analiza los piers de ETABS para determinar:
- Qué muros son continuos a través de varios pisos
- La altura total del muro continuo (hwcs) para cada pier
- La posición del pier dentro del muro continuo

hwcs es necesario para:
- §18.10.3.3: Factor Omega_v (amplificación de cortante)
- §18.10.6: Verificación de elementos de borde (drift ratio)
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, TYPE_CHECKING

from ..constants.units import MM_TO_M, MM_TO_FT

if TYPE_CHECKING:
    from ..entities.pier import Pier
    from ..entities.parsed_data import ParsedData


@dataclass
class WallContinuityInfo:
    """Información de continuidad para un pier."""
    pier_key: str              # Clave del pier (Story_Label)
    label: str                 # Label del muro (sin story)
    story: str                 # Piso del pier

    # Continuidad
    is_continuous: bool        # True si el muro continúa a otros pisos
    n_stories: int             # Número de pisos que abarca el muro
    stories_list: List[str]    # Lista de pisos (de abajo a arriba)

    # Alturas
    pier_height: float         # Altura de este pier (mm)
    hwcs: float                # Altura desde sección crítica (mm)
    height_above: float        # Altura de muro sobre este pier (mm)
    height_below: float        # Altura de muro bajo este pier (mm)

    # Posición
    is_base: bool              # True si es el pier más bajo del muro
    is_top: bool               # True si es el pier más alto del muro
    story_index: int           # Índice del piso (0 = base)

    @property
    def hwcs_m(self) -> float:
        """Altura desde sección crítica en metros."""
        return self.hwcs * MM_TO_M

    def get_hwcs_lw(self, lw_mm: float) -> float:
        """
        Calcula relación hwcs/lw para clasificación de muros.

        Args:
            lw_mm: Longitud del muro en mm (pier.width)

        Returns:
            Relación hwcs/lw (adimensional)
        """
        return self.hwcs / lw_mm if lw_mm > 0 else 0


@dataclass
class BuildingInfo:
    """Información global del edificio."""
    n_stories: int             # Número total de pisos
    stories: List[str]         # Lista de pisos ordenados (de abajo a arriba)
    total_height_mm: float     # Altura total del edificio (mm)
    hn_ft: float               # Altura total en pies (para omega_v)
    hn_m: float                # Altura total en metros


class WallContinuityService:
    """
    Servicio para calcular continuidad de muros y hwcs.

    Analiza los piers parseados de ETABS para determinar qué muros
    son continuos a través de varios pisos y calcular hwcs para cada uno.
    """

    def __init__(self):
        self._continuity_cache: Dict[str, WallContinuityInfo] = {}
        self._building_info: Optional[BuildingInfo] = None

    def analyze_continuity(
        self,
        piers: Dict[str, 'Pier'],
        stories: List[str],
        hn_ft: Optional[float] = None
    ) -> Dict[str, WallContinuityInfo]:
        """
        Analiza la continuidad de todos los muros.

        Args:
            piers: Diccionario de piers indexados por "Story_Label"
            stories: Lista de pisos ordenados (de abajo a arriba)
            hn_ft: Altura del edificio en pies (opcional, se calcula si no se provee)

        Returns:
            Diccionario de WallContinuityInfo por pier_key
        """
        # Agrupar piers por label (ignorando story)
        piers_by_label: Dict[str, List[tuple]] = {}

        for pier_key, pier in piers.items():
            label = pier.label
            if label not in piers_by_label:
                piers_by_label[label] = []
            piers_by_label[label].append((pier_key, pier))

        # Calcular altura total del edificio
        total_height = sum(p.height for p in piers.values()) / len(piers_by_label) if piers_by_label else 0

        # Si no se provee hn_ft, calcularlo de los datos
        if hn_ft is None or hn_ft <= 0:
            # Estimar altura del edificio sumando alturas únicas por piso
            story_heights = {}
            for pier in piers.values():
                if pier.story not in story_heights:
                    story_heights[pier.story] = pier.height
            total_height = sum(story_heights.values())
            hn_ft = total_height * MM_TO_FT

        # Guardar info del edificio
        self._building_info = BuildingInfo(
            n_stories=len(stories),
            stories=stories,
            total_height_mm=total_height,
            hn_ft=hn_ft,
            hn_m=total_height * MM_TO_M
        )

        # Crear mapa de índice de piso
        story_index_map = {story: i for i, story in enumerate(stories)}

        # Calcular continuidad para cada grupo de muros
        continuity_info: Dict[str, WallContinuityInfo] = {}

        for label, pier_list in piers_by_label.items():
            # Ordenar piers por índice de piso (de abajo a arriba)
            pier_list_sorted = sorted(
                pier_list,
                key=lambda x: story_index_map.get(x[1].story, 0)
            )

            n_stories = len(pier_list_sorted)
            is_continuous = n_stories > 1
            stories_list = [p[1].story for p in pier_list_sorted]

            # Calcular hwcs acumulado para cada pier
            cumulative_height = 0.0
            heights = [p[1].height for p in pier_list_sorted]
            total_wall_height = sum(heights)

            for i, (pier_key, pier) in enumerate(pier_list_sorted):
                cumulative_height += pier.height
                height_below = sum(heights[:i])
                height_above = sum(heights[i+1:])

                # hwcs = altura desde la base del muro hasta el tope del pier actual
                hwcs = cumulative_height

                info = WallContinuityInfo(
                    pier_key=pier_key,
                    label=label,
                    story=pier.story,
                    is_continuous=is_continuous,
                    n_stories=n_stories,
                    stories_list=stories_list,
                    pier_height=pier.height,
                    hwcs=hwcs,
                    height_above=height_above,
                    height_below=height_below,
                    is_base=(i == 0),
                    is_top=(i == n_stories - 1),
                    story_index=i
                )

                continuity_info[pier_key] = info

        self._continuity_cache = continuity_info
        return continuity_info

    def get_hwcs(self, pier_key: str) -> float:
        """
        Obtiene hwcs para un pier específico.

        Args:
            pier_key: Clave del pier (Story_Label)

        Returns:
            hwcs en mm, o 0 si no se encuentra
        """
        info = self._continuity_cache.get(pier_key)
        return info.hwcs if info else 0

    def get_building_info(self) -> Optional[BuildingInfo]:
        """Obtiene información del edificio."""
        return self._building_info

    def get_hn_ft(self) -> float:
        """Obtiene la altura del edificio en pies."""
        return self._building_info.hn_ft if self._building_info else 0
