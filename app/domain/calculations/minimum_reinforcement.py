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

    # Límites de espaciamiento (mm)
    MIN_SPACING = 100
    MAX_SPACING = 300

    # Múltiplo para redondeo de espaciamiento (mm)
    SPACING_ROUND_MULTIPLE = 5

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
        Redondea hacia abajo a múltiplo de 5mm para asegurar ρ ≥ ρmin.
        """
        # As mínimo por metro
        As_min_per_m = rho_min * thickness * 1000  # mm²/m

        # Espaciamiento exacto (proteger división por cero)
        if As_min_per_m > 0:
            spacing_exact = n_meshes * bar_area * 1000 / As_min_per_m
        else:
            spacing_exact = cls.MAX_SPACING

        # Redondear hacia abajo a múltiplo de 5mm
        spacing = int(spacing_exact // cls.SPACING_ROUND_MULTIPLE) * cls.SPACING_ROUND_MULTIPLE

        # Limitar a rango típico
        spacing = max(cls.MIN_SPACING, min(cls.MAX_SPACING, spacing))

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
