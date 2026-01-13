# app/domain/constants/seismic.py
"""
Constantes y enums para diseño sísmico según ACI 318-25.
"""
from enum import Enum


class SeismicDesignCategory(Enum):
    """Categoría de Diseño Sísmico (SDC)."""
    A = "A"  # No requiere capítulo 18
    B = "B"  # Requiere 18.3 (pórticos ordinarios)
    C = "C"  # Requiere 18.4-18.5, 18.12.1.2, 18.13
    D = "D"  # Requiere capítulo 18 completo
    E = "E"  # Requiere capítulo 18 completo
    F = "F"  # Requiere capítulo 18 completo
