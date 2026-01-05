# app/domain/entities/slab_forces.py
"""
Entidades para losas: SlabSectionCut y SlabForces.
Los datos provienen de Section Cut Forces - Analysis de ETABS.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .load_combination import LoadCombination


@dataclass
class SlabSectionCut:
    """
    Representa un corte de seccion desde ETABS.

    Formato del nombre en ETABS:
    "Scut Losa S02-29x150 eje CL - Eje C3"
           |    |   |       |       |
           |    |   |       |       +-- Ubicacion del corte
           |    |   |       +-- Eje de la losa
           |    |   +-- Ancho del corte (cm)
           |    +-- Espesor (cm)
           +-- Story/Piso
    """
    name: str                   # Nombre completo del corte
    story: str                  # Piso extraido del nombre (ej: "S02")
    thickness_mm: float         # Espesor extraido del nombre (mm)
    width_mm: float             # Ancho del corte extraido del nombre (mm)
    axis_slab: str              # Eje de la losa (ej: "CL")
    location: str               # Ubicacion del corte (ej: "Eje C3", "C3")

    @property
    def slab_key(self) -> str:
        """Clave unica para identificar la losa."""
        return f"{self.story}_{self.axis_slab}_{self.location}"

    @property
    def display_name(self) -> str:
        """Nombre legible para mostrar en UI."""
        return f"{self.axis_slab} @ {self.location}"


@dataclass
class SlabForces:
    """
    Coleccion de todas las combinaciones de carga para un corte de losa.

    Las fuerzas vienen de Section Cut Forces - Analysis:
    - F1: Fuerza axial (en direccion del eje 1 global)
    - F2, F3: Cortantes (en direccion ejes 2 y 3 globales)
    - M1: Torsion
    - M2, M3: Momentos flectores

    Para diseño se usan valores absolutos ya que importa la magnitud.
    """
    slab_label: str
    story: str
    section_cut: SlabSectionCut
    combinations: List[LoadCombination] = field(default_factory=list)

    def get_envelope(self) -> Dict[str, float]:
        """
        Obtiene la envolvente de todas las combinaciones.
        Retorna los valores maximos absolutos.
        """
        if not self.combinations:
            return {}

        # Para losas, el cortante principal y momento dependen de la orientacion
        # Usamos valores absolutos para diseño
        F1_max = max(abs(c.P) for c in self.combinations)   # P = F1
        F2_max = max(abs(c.V3) for c in self.combinations)  # V3 = F2
        F3_max = max(abs(c.V2) for c in self.combinations)  # V2 = F3
        M2_max = max(abs(c.M3) for c in self.combinations)  # M3 = M2
        M3_max = max(abs(c.M2) for c in self.combinations)  # M2 = M3

        return {
            'F1_max': F1_max,  # Axial
            'F2_max': F2_max,  # Cortante
            'F3_max': F3_max,  # Cortante
            'M2_max': M2_max,  # Momento
            'M3_max': M3_max   # Momento
        }

    def get_max_shear(self) -> Dict[str, float]:
        """
        Obtiene los cortantes maximos.
        Para losas, el cortante principal suele ser V2 (o F3 en global).
        """
        if not self.combinations:
            return {'V_max': 0, 'V2_max': 0, 'V3_max': 0}

        V2_max = max(abs(c.V2) for c in self.combinations)
        V3_max = max(abs(c.V3) for c in self.combinations)

        return {
            'V_max': max(V2_max, V3_max),  # Maximo de ambas direcciones
            'V2_max': V2_max,
            'V3_max': V3_max
        }

    def get_max_moment(self) -> Dict[str, float]:
        """
        Obtiene los momentos maximos.
        Para losas, el momento principal suele ser M2 (o M3 en global).
        """
        if not self.combinations:
            return {'M_max': 0, 'M2_max': 0, 'M3_max': 0}

        M2_max = max(abs(c.M2) for c in self.combinations)
        M3_max = max(abs(c.M3) for c in self.combinations)

        return {
            'M_max': max(M2_max, M3_max),  # Maximo de ambas direcciones
            'M2_max': M2_max,
            'M3_max': M3_max
        }

    def get_critical_shear_combo(self) -> Optional[LoadCombination]:
        """
        Obtiene la combinacion con el cortante maximo.
        """
        if not self.combinations:
            return None

        # Buscar la combinacion con mayor cortante (cualquier direccion)
        return max(self.combinations, key=lambda c: max(abs(c.V2), abs(c.V3)))

    def get_critical_moment_combo(self) -> Optional[LoadCombination]:
        """
        Obtiene la combinacion con el momento maximo.
        """
        if not self.combinations:
            return None

        # Buscar la combinacion con mayor momento (cualquier direccion)
        return max(self.combinations, key=lambda c: max(abs(c.M2), abs(c.M3)))

    def get_punching_shear(self) -> Dict[str, float]:
        """
        Obtiene datos para verificacion de punzonamiento.
        Para punzonamiento se usa el cortante total en el corte.
        """
        if not self.combinations:
            return {'Vu_max': 0, 'critical_combo': ''}

        # El cortante para punzonamiento es la suma vectorial o el maximo
        Vu_max = 0
        critical_combo = ''

        for c in self.combinations:
            # Cortante combinado (aproximado como maximo)
            Vu = max(abs(c.V2), abs(c.V3))
            if Vu > Vu_max:
                Vu_max = Vu
                critical_combo = c.name

        return {
            'Vu_max': Vu_max,
            'critical_combo': critical_combo
        }
