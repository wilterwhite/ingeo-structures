# app/domain/calculations/coupling_beam_capacity.py
"""
Servicio de cálculo de capacidad para vigas de acople.

Centraliza los cálculos de Mn y Mpr que antes estaban en CouplingBeamConfig.
Usa el bloque rectangular de Whitney para flexión pura.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.coupling_beam import CouplingBeamConfig


class CouplingBeamCapacityService:
    """
    Servicio de cálculo de capacidad flexural para vigas de acople.

    Implementa el método de Whitney para vigas rectangulares
    con armadura simple (tracción en una capa).
    """

    @staticmethod
    def calculate_Mn(
        As: float,
        d: float,
        b: float,
        fy: float,
        fc: float
    ) -> float:
        """
        Calcula momento nominal usando bloque rectangular de Whitney.

        a = As * fy / (0.85 * fc * b)
        Mn = As * fy * (d - a/2)

        Args:
            As: Área de acero en tracción (mm²)
            d: Profundidad efectiva (mm)
            b: Ancho de la viga (mm)
            fy: Fluencia del acero (MPa)
            fc: Resistencia del concreto (MPa)

        Returns:
            Mn en kN-m
        """
        # Profundidad del bloque de compresión
        a = As * fy / (0.85 * fc * b)

        # Verificar que a < d (armadura en tracción)
        if a >= d:
            return 0.0

        # Momento nominal (N-mm -> kN-m)
        Mn_Nmm = As * fy * (d - a / 2)
        return Mn_Nmm / 1e6

    @staticmethod
    def calculate_Mpr(Mn: float, alpha: float = 1.25) -> float:
        """
        Calcula momento probable.

        Mpr = alpha * Mn, donde alpha = 1.25 según ACI 318-25.

        Args:
            Mn: Momento nominal (kN-m)
            alpha: Factor de sobrerresistencia (default 1.25)

        Returns:
            Mpr en kN-m
        """
        return alpha * Mn

    @staticmethod
    def calculate_from_beam(beam: 'CouplingBeamConfig') -> dict:
        """
        Calcula todas las capacidades de una viga de acople.

        Args:
            beam: Configuración de viga de acople

        Returns:
            Diccionario con Mn y Mpr positivos y negativos
        """
        # Momento positivo (armadura inferior en tracción)
        Mn_positive = CouplingBeamCapacityService.calculate_Mn(
            As=beam.As_bottom,
            d=beam.d_bottom,
            b=beam.width,
            fy=beam.fy,
            fc=beam.fc
        )

        # Momento negativo (armadura superior en tracción)
        Mn_negative = CouplingBeamCapacityService.calculate_Mn(
            As=beam.As_top,
            d=beam.d_top,
            b=beam.width,
            fy=beam.fy,
            fc=beam.fc
        )

        Mpr_positive = CouplingBeamCapacityService.calculate_Mpr(Mn_positive)
        Mpr_negative = CouplingBeamCapacityService.calculate_Mpr(Mn_negative)

        return {
            'Mn_positive_kNm': round(Mn_positive, 2),
            'Mn_negative_kNm': round(Mn_negative, 2),
            'Mpr_positive_kNm': round(Mpr_positive, 2),
            'Mpr_negative_kNm': round(Mpr_negative, 2),
            'Mpr_max_kNm': round(max(Mpr_positive, Mpr_negative), 2),
        }
