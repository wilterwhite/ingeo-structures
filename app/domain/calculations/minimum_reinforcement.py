# app/domain/calculations/minimum_reinforcement.py
"""
Cálculo de armadura mínima para muros según ACI 318-25.

Referencia:
- ACI 318-25 §11.6.1: Cuantía mínima ρ = 0.0025
- ACI 318-25 §11.7.2.3: Muros con espesor ≤ 130mm pueden usar malla simple

Este módulo contiene la lógica pura de cálculo, separada de las entidades.
"""
from dataclasses import dataclass
from typing import Tuple

from ..constants.reinforcement import RHO_MIN
from ..constants.materials import get_bar_area


@dataclass
class MinimumReinforcementConfig:
    """Configuración de armadura mínima calculada."""
    n_meshes: int       # Número de mallas (1=simple, 2=doble)
    diameter: int       # Diámetro de barra (mm)
    spacing: int        # Espaciamiento (mm)
    bar_area: float     # Área de barra (mm²)
    rho_provided: float # Cuantía provista

    @property
    def As_per_meter(self) -> float:
        """Área de acero por metro lineal (mm²/m)."""
        return self.n_meshes * self.bar_area * 1000 / self.spacing


class MinimumReinforcementCalculator:
    """
    Calculador de armadura mínima para muros.

    Aplica las reglas de ACI 318-25:
    - ρmin = 0.0025 (§11.6.1)
    - Espesor ≤ 130mm: malla simple permitida (§11.7.2.3)
    - Espesor > 130mm: malla doble requerida
    """

    # Espesor límite para malla simple (mm)
    SINGLE_MESH_THICKNESS_LIMIT = 130

    # Diámetro por defecto para armadura mínima (mm)
    DEFAULT_DIAMETER = 8

    # Espaciamientos disponibles en el frontend (ordenados)
    # El cálculo redondea hacia abajo al valor disponible más cercano
    AVAILABLE_SPACINGS = [100, 125, 150, 175, 200, 250, 300]

    # Límites de espaciamiento (mm)
    MIN_SPACING = 100
    MAX_SPACING = 300

    @classmethod
    def calculate_for_pier(
        cls,
        thickness: float,
        rho_min: float = RHO_MIN,
        diameter: int = DEFAULT_DIAMETER,
    ) -> MinimumReinforcementConfig:
        """
        Calcula la armadura mínima para un muro.

        Args:
            thickness: Espesor del muro (mm)
            rho_min: Cuantía mínima (default 0.0025)
            diameter: Diámetro de barra a usar (default φ8)

        Returns:
            MinimumReinforcementConfig con la configuración calculada
        """
        # Determinar número de mallas según espesor
        n_meshes = cls._calculate_n_meshes(thickness)

        # Obtener área de barra
        bar_area = get_bar_area(diameter)

        # Calcular espaciamiento
        spacing = cls._calculate_spacing(
            thickness=thickness,
            n_meshes=n_meshes,
            bar_area=bar_area,
            rho_min=rho_min,
        )

        # Calcular cuantía real provista
        rho_provided = cls._calculate_rho(
            n_meshes=n_meshes,
            bar_area=bar_area,
            spacing=spacing,
            thickness=thickness,
        )

        return MinimumReinforcementConfig(
            n_meshes=n_meshes,
            diameter=diameter,
            spacing=spacing,
            bar_area=bar_area,
            rho_provided=rho_provided,
        )

    @classmethod
    def _calculate_n_meshes(cls, thickness: float) -> int:
        """
        Determina número de mallas según espesor.

        §11.7.2.3: Muros con t ≤ 130mm pueden usar malla central simple.
        """
        return 1 if thickness <= cls.SINGLE_MESH_THICKNESS_LIMIT else 2

    @classmethod
    def _calculate_spacing(
        cls,
        thickness: float,
        n_meshes: int,
        bar_area: float,
        rho_min: float,
    ) -> int:
        """
        Calcula espaciamiento para cumplir ρ ≥ ρmin.

        Fórmula: s = n_meshes × As_barra × 1000 / (ρmin × t × 1000)
        Redondea hacia abajo al espaciamiento disponible más cercano
        para asegurar ρ ≥ ρmin y que el valor esté en el dropdown.
        """
        # As mínimo por metro
        As_min_per_m = rho_min * thickness * 1000  # mm²/m

        # Espaciamiento exacto (proteger división por cero)
        if As_min_per_m > 0:
            spacing_exact = n_meshes * bar_area * 1000 / As_min_per_m
        else:
            spacing_exact = cls.MAX_SPACING

        # Redondear hacia abajo al espaciamiento disponible más cercano
        # (conservador: siempre cumple ρ ≥ ρmin)
        spacing = cls.MIN_SPACING  # fallback
        for s in cls.AVAILABLE_SPACINGS:
            if s <= spacing_exact:
                spacing = s
            else:
                break

        return spacing

    @classmethod
    def _calculate_rho(
        cls,
        n_meshes: int,
        bar_area: float,
        spacing: int,
        thickness: float,
    ) -> float:
        """Calcula la cuantía de refuerzo provista."""
        if spacing <= 0 or thickness <= 0:
            return 0.0
        As_per_m = n_meshes * bar_area * 1000 / spacing
        return As_per_m / (thickness * 1000)

    # Combinaciones de borde ordenadas por área creciente
    EDGE_COMBINATIONS = [
        (2, 10),   # 2φ10 = 157 mm²
        (2, 12),   # 2φ12 = 226 mm²
        (4, 10),   # 4φ10 = 314 mm²
        (2, 16),   # 2φ16 = 402 mm²
        (4, 12),   # 4φ12 = 452 mm²
        (4, 16),   # 4φ16 = 804 mm²
    ]

    @classmethod
    def calculate_edge_reinforcement(
        cls,
        thickness: float,
        cover: float = 25.0,
        rho_min: float = RHO_MIN,
    ) -> Tuple[int, int]:
        """
        Calcula enfierradura de borde mínima para cumplir ρmin.

        La zona de borde se define como cover + 50mm (espacio típico para barras).
        Se busca la combinación mínima de (n_barras, diámetro) que cumple:
            As_provisto >= ρmin × ancho_borde × espesor

        Args:
            thickness: Espesor del muro (mm)
            cover: Recubrimiento (mm)
            rho_min: Cuantía mínima (0.0025)

        Returns:
            Tuple (n_edge_bars, diameter_edge)
        """
        # Ancho de zona de borde aproximado
        edge_zone_width = cover + 50  # ~75mm típico

        # As mínimo en zona de borde
        As_min = rho_min * edge_zone_width * thickness

        # Probar combinaciones hasta encontrar la mínima que cumple
        for n_bars, diameter in cls.EDGE_COMBINATIONS:
            As_provided = n_bars * get_bar_area(diameter)
            if As_provided >= As_min:
                return n_bars, diameter

        # Fallback: última combinación (la más grande)
        return cls.EDGE_COMBINATIONS[-1]

    @classmethod
    def verify_minimum(
        cls,
        n_meshes: int,
        bar_area: float,
        spacing: int,
        thickness: float,
        rho_min: float = RHO_MIN,
    ) -> Tuple[bool, float, str]:
        """
        Verifica si una configuración de refuerzo cumple el mínimo.

        Args:
            n_meshes: Número de mallas
            bar_area: Área de barra (mm²)
            spacing: Espaciamiento (mm)
            thickness: Espesor del muro (mm)
            rho_min: Cuantía mínima requerida

        Returns:
            Tuple (is_ok, rho_provided, message)
        """
        rho_provided = cls._calculate_rho(n_meshes, bar_area, spacing, thickness)

        is_ok = rho_provided >= rho_min

        if is_ok:
            message = f"ρ={rho_provided:.4f} ≥ ρmin={rho_min}"
        else:
            message = f"ρ={rho_provided:.4f} < ρmin={rho_min} (§11.6.1)"

        return is_ok, rho_provided, message
