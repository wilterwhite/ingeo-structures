# app/domain/constants/geometry.py
"""
Constantes geométricas ACI 318-25.

Centraliza todos los límites dimensionales para verificación de geometría:
- Columnas especiales (§18.7.2)
- Vigas especiales (§18.6.2)
- Elementos de borde (§18.10.6.4)
- Zonas de extremo (§18.10.2.4)

Todas las dimensiones están en mm salvo indicación contraria.

Referencias: ACI 318-25 Capítulo 18
"""

# =============================================================================
# COLUMNAS ESPECIALES (§18.7.2)
# =============================================================================

# §18.7.2.1(a): Dimensión mínima de la sección transversal
# ACI usa 12" = 304.8mm. El valor SI redondeado es 300mm.
# Usamos 300mm como valor SI estándar (ver Commentary R18.7.2.1)
COLUMN_MIN_DIMENSION_MM = 300.0

# §18.7.2.1(b): Relación de aspecto mínima b/h >= 0.4
COLUMN_MIN_ASPECT_RATIO = 0.4


# =============================================================================
# VIGAS ESPECIALES (§18.6.2)
# =============================================================================

# §18.6.2.1(a): bw >= 0.3h
BEAM_MIN_WIDTH_RATIO = 0.3

# §18.6.2.1(b): bw >= 10" = 254mm
BEAM_MIN_WIDTH_MM = 254.0

# §18.6.2.1(c): bw no debe exceder ancho del elemento de apoyo + 0.75h
BEAM_WIDTH_SUPPORT_FACTOR = 0.75

# ln >= 4d (práctica común para evitar vigas profundas)
BEAM_MIN_LN_TO_D = 4.0


# =============================================================================
# ELEMENTOS DE BORDE (§18.10.6.4)
# =============================================================================

# §18.10.6.4(b): Ancho mínimo b >= hu/16
BE_WIDTH_TO_HU_RATIO = 1 / 16

# §18.10.6.4(c): Para c/lw >= 3/8, ancho mínimo 12" = 305mm
# Nota: Usamos 305mm (valor imperial exacto) porque es el umbral de verificación
# de elementos de borde que requieren confinamiento especial
BE_MIN_WIDTH_SPECIAL_MM = 305.0

# Umbral c/lw para requerir ancho mínimo de 305mm
BE_C_LW_THRESHOLD = 0.375  # 3/8

# §18.10.6.4(a): Extensión horizontal
# length >= max(c - 0.1*lw, c/2)
BE_LENGTH_C_FACTOR = 0.5
BE_LENGTH_LW_FACTOR = 0.1


# =============================================================================
# ZONAS DE EXTREMO DE MUROS (§18.10.2.4)
# =============================================================================

# Límite hw/lw para zona de extremo
ZONE_HW_LW_LIMIT = 2.0

# Longitud de zona de extremo como fracción de lw
ZONE_LENGTH_RATIO = 0.15


# =============================================================================
# CLASIFICACIÓN MURO/COLUMNA
# =============================================================================

# Relación lw/tw para clasificar como muro vs columna
# lw/tw >= 4 → muro; lw/tw < 4 → columna
WALL_COLUMN_ASPECT_THRESHOLD = 4.0


# =============================================================================
# EXPORTACIONES
# =============================================================================

__all__ = [
    # Columnas
    'COLUMN_MIN_DIMENSION_MM',
    'COLUMN_MIN_ASPECT_RATIO',
    # Vigas
    'BEAM_MIN_WIDTH_RATIO',
    'BEAM_MIN_WIDTH_MM',
    'BEAM_WIDTH_SUPPORT_FACTOR',
    'BEAM_MIN_LN_TO_D',
    # Boundary Elements
    'BE_WIDTH_TO_HU_RATIO',
    'BE_MIN_WIDTH_SPECIAL_MM',
    'BE_C_LW_THRESHOLD',
    'BE_LENGTH_C_FACTOR',
    'BE_LENGTH_LW_FACTOR',
    # Zonas de extremo
    'ZONE_HW_LW_LIMIT',
    'ZONE_LENGTH_RATIO',
    # Clasificación
    'WALL_COLUMN_ASPECT_THRESHOLD',
]
