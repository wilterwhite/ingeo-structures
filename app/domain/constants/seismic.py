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


class WallCategory(Enum):
    """Categoría de muro estructural."""
    ORDINARY = "ordinary"          # Muro ordinario - no requiere Cap. 18
    INTERMEDIATE = "intermediate"  # Muro intermedio prefabricado - 18.5
    SPECIAL = "special"           # Muro especial - 18.10


# Secciones requeridas según SDC (basado en Tabla R18.2)
SDC_REQUIREMENTS = {
    SeismicDesignCategory.A: {},
    SeismicDesignCategory.B: {
        "analysis": "18.2.2",
        "frames": "18.3",
    },
    SeismicDesignCategory.C: {
        "analysis": "18.2.2",
        "frames": "18.4",
        "walls": "18.5 (prefabricados)",
        "diaphragms": "18.12.1.2",
        "foundations": "18.13",
    },
    # SDC D, E, F requieren capítulo 18 completo
    SeismicDesignCategory.D: {
        "analysis": "18.2.2, 18.2.4",
        "materials": "18.2.5-18.2.8",
        "frames": "18.6-18.9",
        "walls": "18.10, 18.11",
        "diaphragms": "18.12",
        "foundations": "18.13",
        "non_sfrs": "18.14",
    },
    SeismicDesignCategory.E: {
        "analysis": "18.2.2, 18.2.4",
        "materials": "18.2.5-18.2.8",
        "frames": "18.6-18.9",
        "walls": "18.10, 18.11",
        "diaphragms": "18.12",
        "foundations": "18.13",
        "non_sfrs": "18.14",
    },
    SeismicDesignCategory.F: {
        "analysis": "18.2.2, 18.2.4",
        "materials": "18.2.5-18.2.8",
        "frames": "18.6-18.9",
        "walls": "18.10, 18.11",
        "diaphragms": "18.12",
        "foundations": "18.13",
        "non_sfrs": "18.14",
    },
}
