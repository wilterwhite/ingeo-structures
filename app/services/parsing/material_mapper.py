# app/structural/services/parsing/material_mapper.py
"""
Mapeo de nombres de materiales de ETABS a resistencia f'c.

Este módulo contiene la lógica para convertir los nombres de materiales
usados en ETABS (ej: "4000Psi", "H30") a valores de f'c en MPa.

Para agregar un nuevo material, simplemente añádelo al diccionario MATERIAL_FC_MAP.
"""
import re
from typing import Optional


# =============================================================================
# Mapeo de Materiales
# =============================================================================

MATERIAL_FC_MAP = {
    # -------------------------------------------------------------------------
    # Hormigón - Nomenclatura PSI (común en ETABS)
    # -------------------------------------------------------------------------
    '3000psi': 20.7,
    '4000psi': 27.6,
    '5000psi': 34.5,
    '6000psi': 41.4,
    '7000psi': 48.3,
    '8000psi': 55.2,

    # -------------------------------------------------------------------------
    # Hormigón - Nomenclatura Chilena/Sudamericana (H + MPa)
    # -------------------------------------------------------------------------
    'h20': 20.0,
    'h25': 25.0,
    'h30': 30.0,
    'h35': 35.0,
    'h40': 40.0,
    'h45': 45.0,
    'h50': 50.0,
    'h55': 55.0,
    'h60': 60.0,

    # -------------------------------------------------------------------------
    # Hormigón - Nomenclatura con guión (H-25, H-30, etc.)
    # -------------------------------------------------------------------------
    'h-20': 20.0,
    'h-25': 25.0,
    'h-30': 30.0,
    'h-35': 35.0,
    'h-40': 40.0,
    'h-45': 45.0,

    # -------------------------------------------------------------------------
    # Albañilería
    # -------------------------------------------------------------------------
    'm1500psi': 10.3,
    'm2000psi': 13.8,
    'm2500psi': 17.2,

    # -------------------------------------------------------------------------
    # Nombres descriptivos comunes
    # -------------------------------------------------------------------------
    'concrete': 25.0,
    'concreto': 25.0,
    'hormigon': 25.0,
}

# Valor por defecto cuando no se puede determinar f'c
DEFAULT_FC_MPA = 25.0


# =============================================================================
# Función de Conversión
# =============================================================================

def parse_material_to_fc(material_name: str) -> float:
    """
    Convierte el nombre del material a f'c en MPa.

    Estrategia de búsqueda:
    1. Buscar coincidencia exacta en MATERIAL_FC_MAP
    2. Buscar coincidencia parcial en MATERIAL_FC_MAP
    3. Extraer número del nombre y convertir (psi si > 100, MPa si <= 100)
    4. Retornar valor por defecto

    Args:
        material_name: Nombre del material (ej: "4000Psi", "H30", "Concrete 5000")

    Returns:
        f'c en MPa

    Examples:
        >>> parse_material_to_fc("4000Psi")
        27.6
        >>> parse_material_to_fc("H30")
        30.0
        >>> parse_material_to_fc("Concrete 5000psi")
        34.5
        >>> parse_material_to_fc("Unknown")
        25.0
    """
    if not material_name:
        return DEFAULT_FC_MPA

    # Normalizar: minúsculas, sin espacios extra
    name_normalized = material_name.lower().strip()

    # 1. Coincidencia exacta
    if name_normalized in MATERIAL_FC_MAP:
        return MATERIAL_FC_MAP[name_normalized]

    # 2. Coincidencia parcial (buscar si alguna clave está contenida)
    for key, fc in MATERIAL_FC_MAP.items():
        if key in name_normalized:
            return fc

    # 3. Extraer número del nombre
    match = re.search(r'(\d+)', material_name)
    if match:
        value = int(match.group(1))
        if value > 100:
            # Probablemente es psi (ej: 4000, 5000)
            return value * 0.00689476  # psi a MPa
        else:
            # Probablemente ya es MPa (ej: 25, 30)
            return float(value)

    # 4. Valor por defecto
    return DEFAULT_FC_MPA


def get_available_materials() -> dict:
    """
    Retorna el diccionario de materiales disponibles.

    Útil para mostrar opciones al usuario o para debugging.

    Returns:
        Copia del diccionario MATERIAL_FC_MAP
    """
    return MATERIAL_FC_MAP.copy()
