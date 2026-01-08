# app/domain/flexure/interaction_diagram.py
"""
Cálculo del diagrama de interacción P-M para muros rectangulares de hormigón armado.
Implementa el método de compatibilidad de deformaciones según ACI 318.
"""
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

from ..calculations.steel_layer_calculator import SteelLayer, SteelLayerCalculator
from ..constants.units import N_TO_TONF, NMM_TO_TONFM
from ..constants.phi_chapter21 import (
    PHI_COMPRESSION,
    PHI_TENSION,
    EPSILON_TY,
    EPSILON_T_LIMIT,
    calculate_phi_flexure,
)
from ..constants.materials import calculate_beta1 as _calculate_beta1
from .checker import FlexureChecker


@dataclass
class InteractionPoint:
    """Un punto en el diagrama de interacción."""
    Pn: float       # Resistencia nominal axial (tonf)
    Mn: float       # Resistencia nominal a flexión (tonf-m)
    phi: float      # Factor de reducción
    phi_Pn: float   # Resistencia de diseño axial (tonf)
    phi_Mn: float   # Resistencia de diseño a flexión (tonf-m)
    c: float        # Profundidad del eje neutro (mm)
    epsilon_t: float  # Deformación del acero en tracción


class InteractionDiagramService:
    """
    Servicio para generar el diagrama de interacción P-M de muros rectangulares.

    Hipótesis ACI 318:
    - Deformación máxima del hormigón: εcu = 0.003
    - Bloque de compresión equivalente de Whitney
    - Acero elasto-plástico perfecto

    Unidades de salida: tonf y tonf-m (compatibles con ETABS)
    """

    # Constantes de deformación
    EPSILON_CU = 0.003      # Deformación última del hormigón
    ES = 200000             # Módulo de elasticidad del acero (MPa)

    def __init__(self):
        pass

    def calculate_beta1(self, fc: float) -> float:
        """
        Calcula β1 según ACI 318-25 §22.2.2.4.3.

        Delega a la función centralizada en constants/materials.py.

        Args:
            fc: Resistencia del hormigón (MPa)

        Returns:
            β1: Factor del bloque de compresión equivalente (0.65-0.85)
        """
        return _calculate_beta1(fc)

    def calculate_phi(self, epsilon_t: float) -> float:
        """
        Calcula el factor de reducción φ según la deformación del acero.

        Delega a calculate_phi_flexure() de constants/phi.py (§21.2.2).

        Args:
            epsilon_t: Deformación del acero en tracción

        Returns:
            φ: Factor de reducción
        """
        return calculate_phi_flexure(epsilon_t)

    def generate_steel_layers(
        self,
        width: float,           # Largo del muro (mm)
        cover: float,           # Recubrimiento (mm)
        n_meshes: int,          # Número de mallas (1 o 2)
        bar_area_edge: float,   # Área de barra de borde (mm²)
        bar_area_v: float,      # Área de barra de malla (mm²)
        spacing_v: float        # Espaciamiento vertical (mm)
    ) -> List[SteelLayer]:
        """
        Genera las capas de acero con sus posiciones reales.

        Delega a SteelLayerCalculator para evitar duplicación de código.

        Args:
            width: Largo del muro (mm)
            cover: Recubrimiento al centro de la barra (mm)
            n_meshes: Número de mallas (1 o 2)
            bar_area_edge: Área de cada barra de borde (mm²)
            bar_area_v: Área de cada barra de malla (mm²)
            spacing_v: Espaciamiento de la malla (mm)

        Returns:
            Lista de SteelLayer ordenadas por posición
        """
        return SteelLayerCalculator.calculate(
            width=width,
            cover=cover,
            n_meshes=n_meshes,
            bar_area_edge=bar_area_edge,
            bar_area_v=bar_area_v,
            spacing_v=spacing_v
        )

    def generate_interaction_curve(
        self,
        width: float,       # Largo del muro (mm)
        thickness: float,   # Espesor del muro (mm)
        fc: float,          # f'c (MPa)
        fy: float,          # fy (MPa)
        As_total: float,    # Área de acero total vertical (mm²) - para compatibilidad
        cover: float = 25,  # Recubrimiento (mm) - 2.5cm default
        n_points: int = 50, # Número de puntos en la curva
        steel_layers: Optional[List[SteelLayer]] = None  # Capas de acero (opcional)
    ) -> List[InteractionPoint]:
        """
        Genera los puntos del diagrama de interacción P-M.

        Si se proporcionan steel_layers, usa las posiciones reales de las barras.
        Si no, usa el modelo simplificado (As/2 en cada extremo).

        Args:
            width: Largo del muro en la dirección del momento (mm)
            thickness: Espesor del muro (mm)
            fc: Resistencia del hormigón (MPa)
            fy: Fluencia del acero (MPa)
            As_total: Área total de acero vertical (mm²)
            cover: Recubrimiento (mm)
            n_points: Número de puntos a generar
            steel_layers: Lista de capas de acero con posiciones reales

        Returns:
            Lista de InteractionPoint ordenados de compresión pura a tracción pura
        """
        # Parámetros geométricos
        b = thickness                    # Ancho de la sección
        h = width                        # Altura de la sección (dirección del momento)

        # Si no se proporcionan capas, crear modelo simplificado (2 capas)
        if steel_layers is None or len(steel_layers) == 0:
            steel_layers = [
                SteelLayer(position=cover, area=As_total / 2),
                SteelLayer(position=h - cover, area=As_total / 2)
            ]

        # Calcular As_total desde las capas (para P0)
        As_total_calc = sum(layer.area for layer in steel_layers)

        # Profundidad efectiva = posición de la capa más alejada
        d = max(layer.position for layer in steel_layers)

        # Propiedades del material
        beta1 = self.calculate_beta1(fc)
        epsilon_y = fy / self.ES

        points = []

        # 1. Punto de compresión pura (P0)
        Ag = b * h
        P0 = 0.85 * fc * (Ag - As_total_calc) + fy * As_total_calc
        P0_max = 0.80 * P0  # Límite ACI 318

        phi_P0 = PHI_COMPRESSION
        points.append(InteractionPoint(
            Pn=P0_max / N_TO_TONF,
            Mn=0,
            phi=phi_P0,
            phi_Pn=phi_P0 * P0_max / N_TO_TONF,
            phi_Mn=0,
            c=float('inf'),
            epsilon_t=0
        ))

        # 2. Generar valores de c para la curva
        c_balanced = d * self.EPSILON_CU / (self.EPSILON_CU + epsilon_y)
        c_values = []

        # Zona 1: Compresión alta (c > d)
        n_zone1 = n_points // 4
        for i in range(n_zone1):
            ratio = i / n_zone1
            c = d * (10 - 9 * ratio)
            c_values.append(c)

        # Zona 2: Transición (d > c > c_balanced)
        n_zone2 = n_points // 3
        for i in range(n_zone2 + 1):
            ratio = i / n_zone2
            c = d - (d - c_balanced) * ratio
            c_values.append(c)

        # Zona 3: Tracción controlada (c < c_balanced)
        n_zone3 = n_points // 3
        c_min = 0.05 * d
        for i in range(n_zone3 + 1):
            ratio = i / n_zone3
            c = c_balanced - (c_balanced - c_min) * ratio
            if c > 0:
                c_values.append(c)

        c_values = sorted(set(c_values), reverse=True)

        # Centro de la sección para calcular momentos
        y_centroid = h / 2

        # Valor minimo de c para evitar division por numeros muy pequenos
        c_tolerance = 1.0  # mm - minimo 1mm para estabilidad numerica

        for c in c_values:
            if c <= c_tolerance:
                continue

            # Bloque de compresion de Whitney
            a = beta1 * c
            if a > h:
                a = h

            # Compresión del hormigón
            Cc = 0.85 * fc * a * b  # N
            Mc = Cc * (y_centroid - a / 2)  # N-mm

            # Sumar contribución de cada capa de acero
            Pn_steel = 0.0
            Mn_steel = 0.0
            epsilon_t_max = 0.0  # Para calcular phi

            for layer in steel_layers:
                di = layer.position
                Asi = layer.area

                # Deformación en esta capa
                # εi = εcu × (di - c) / c
                # Positivo = tracción, Negativo = compresión
                epsilon_i = self.EPSILON_CU * (di - c) / c

                # Esfuerzo (limitado por fy)
                fs_i = min(abs(epsilon_i) * self.ES, fy)
                if epsilon_i < 0:
                    fs_i = -fs_i  # Compresión

                # Descontar hormigón si la barra está en zona comprimida
                if di <= a:
                    # La barra está dentro del bloque de compresión
                    # Fuerza neta = As × (fs - 0.85×fc) si está comprimida
                    if fs_i < 0:  # Compresión
                        Fi = Asi * (fs_i + 0.85 * fc)  # +0.85fc porque fs_i es negativo
                    else:
                        Fi = Asi * fs_i
                else:
                    # La barra está en zona de tracción
                    Fi = Asi * fs_i

                # Contribución a P (positivo = compresión)
                Pn_steel += -Fi  # Negativo porque tracción resta a P

                # Contribución a M respecto al centroide
                Mn_steel += Fi * (di - y_centroid)

                # Guardar deformación máxima en tracción (para phi)
                if epsilon_i > epsilon_t_max:
                    epsilon_t_max = epsilon_i

            # Fuerzas totales
            Pn = Cc + Pn_steel  # N
            Mn = abs(Mc + Mn_steel)  # N-mm (siempre positivo)

            # Factor phi basado en deformación máxima del acero en tracción
            phi = self.calculate_phi(epsilon_t_max)

            # Verificar límite de compresión
            if Pn > P0_max:
                Pn = P0_max

            points.append(InteractionPoint(
                Pn=Pn / N_TO_TONF,
                Mn=Mn / NMM_TO_TONFM,
                phi=phi,
                phi_Pn=phi * Pn / N_TO_TONF,
                phi_Mn=phi * Mn / NMM_TO_TONFM,
                c=c,
                epsilon_t=epsilon_t_max
            ))

        # 3. Punto de tracción pura
        Pt = -As_total_calc * fy  # N (negativo)
        phi_Pt = PHI_TENSION

        points.append(InteractionPoint(
            Pn=Pt / N_TO_TONF,
            Mn=0,
            phi=phi_Pt,
            phi_Pn=phi_Pt * Pt / N_TO_TONF,
            phi_Mn=0,
            c=0,
            epsilon_t=float('inf')
        ))

        # Ordenar por Pn de mayor a menor
        points.sort(key=lambda p: p.phi_Pn, reverse=True)

        return points

    def get_design_curve(
        self,
        points: List[InteractionPoint]
    ) -> List[Tuple[float, float]]:
        """
        Extrae la curva de diseño (φPn, φMn) del diagrama.

        Returns:
            Lista de tuplas (φMn, φPn) para graficar
        """
        curve = [(p.phi_Mn, p.phi_Pn) for p in points]
        return curve

    def calculate_safety_factor(
        self,
        points: List[InteractionPoint],
        Pu: float,
        Mu: float
    ) -> Tuple[float, bool]:
        """
        Calcula el factor de seguridad para un punto de demanda.

        Delega a FlexureChecker para evitar duplicación de código.

        Args:
            points: Puntos del diagrama de interacción
            Pu: Carga axial de demanda (tonf), positivo = compresión
            Mu: Momento de demanda (tonf-m), siempre positivo

        Returns:
            Tuple (factor_seguridad, is_inside)
        """
        return FlexureChecker.calculate_safety_factor(points, Pu, Mu)

    def check_flexure(
        self,
        points: List[InteractionPoint],
        demand_points: List[Tuple[float, float, str]]
    ) -> Tuple[float, str, str, float, float, float, float, bool, float, bool, int]:
        """
        DEPRECATED: Usar FlexureChecker.check_flexure() directamente.

        Este metodo se mantiene solo por compatibilidad. Prefiere llamar a:
            from app.domain.flexure import FlexureChecker
            result = FlexureChecker.check_flexure(points, demand_points)

        Args:
            points: Puntos del diagrama de interaccion
            demand_points: Lista de (Pu, Mu, combo_name)

        Returns:
            Tuple de 11 elementos (usar FlexureCheckResult directamente es mas claro)
        """
        result = FlexureChecker.check_flexure(points, demand_points)
        return (
            result.safety_factor,
            result.status,
            result.critical_combo,
            result.phi_Mn_0,
            result.phi_Mn_at_Pu,
            result.critical_Pu,
            result.critical_Mu,
            result.exceeds_axial_capacity,
            result.phi_Pn_max,
            result.has_tension,
            result.tension_combos
        )
