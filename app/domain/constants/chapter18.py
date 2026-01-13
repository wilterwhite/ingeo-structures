# app/domain/constants/chapter18.py
"""
Constantes ACI 318-25 Capítulo 18 - Estructuras Sismo-Resistentes.

Centraliza constantes de detallamiento sísmico usadas en:
- §18.6: Vigas de pórticos especiales
- §18.7: Columnas de pórticos especiales
- §18.10: Muros estructurales especiales

Todas las dimensiones están en mm salvo indicación contraria.
"""

# =============================================================================
# Dimensiones Mínimas (§18.6.2, §18.7.2)
# =============================================================================

# Vigas especiales §18.6.2.1
MIN_WIDTH_BEAM_MM = 254         # 10" = 254mm (§18.6.2.1(b))
MIN_WIDTH_BEAM_RATIO = 0.3      # bw >= 0.3h (§18.6.2.1(a))
MIN_DEPTH_BEAM_MM = 254         # Práctica común

# Columnas especiales §18.7.2.1
# NOTA: MIN_COLUMN_DIM_MM movido a geometry.py como COLUMN_MIN_DIMENSION_MM
MIN_COLUMN_RATIO = 0.4          # b >= 0.4h (§18.7.2.1(b))


# =============================================================================
# Zona de Confinamiento lo (§18.7.5.1)
# =============================================================================

LO_MIN_MM = 457                 # 18" mínimo para lo
LO_MIN_RATIO = 1/6              # lo >= lu/6


# =============================================================================
# Espaciamiento Transversal (§18.6.4, §18.7.5)
# =============================================================================

# Espaciamiento hx máximo
HX_MAX_MM = 356                 # 14" = 356mm para condiciones normales
HX_MAX_HIGH_AXIAL_MM = 203      # 8" = 203mm para Pu > 0.3Ag·f'c o f'c > 70MPa

# Espaciamiento so (Ec. 18.7.5.3)
SO_MIN_MM = 102                 # 4" mínimo
SO_MAX_MM = 152                 # 6" máximo

# Primer estribo
FIRST_HOOP_MAX_MM = 51          # 2" = 51mm desde cara del nudo


# =============================================================================
# Límites de Materiales para Sísmico (§18.2)
# =============================================================================

FC_LIMIT_HIGH_AXIAL_MPA = 70    # f'c > 70 MPa activa condición especial
FY_MAX_SEISMIC_MPA = 550        # fy máximo para refuerzo sísmico Grade 80


# =============================================================================
# Factores de Grado de Acero (§18.7.5.3)
# =============================================================================

DB_FACTOR_GRADE_60 = 6          # s_max <= 6*db para Grado 60
DB_FACTOR_GRADE_80 = 5          # s_max <= 5*db para Grado 80


# =============================================================================
# Vigas de Acoplamiento (§18.10.7)
# =============================================================================

COUPLING_BEAM_LN_H_LIMIT = 4.0  # ln/h límite para diagonal vs convencional
COUPLING_BEAM_LN_H_DIAGONAL = 2.0  # ln/h < 2 requiere refuerzo diagonal


# =============================================================================
# Exportaciones
# =============================================================================

__all__ = [
    # Dimensiones mínimas
    'MIN_WIDTH_BEAM_MM',
    'MIN_WIDTH_BEAM_RATIO',
    'MIN_DEPTH_BEAM_MM',
    'MIN_COLUMN_RATIO',
    # Zona de confinamiento
    'LO_MIN_MM',
    'LO_MIN_RATIO',
    # Espaciamiento transversal
    'HX_MAX_MM',
    'HX_MAX_HIGH_AXIAL_MM',
    'SO_MIN_MM',
    'SO_MAX_MM',
    'FIRST_HOOP_MAX_MM',
    # Materiales
    'FC_LIMIT_HIGH_AXIAL_MPA',
    'FY_MAX_SEISMIC_MPA',
    # Grado de acero
    'DB_FACTOR_GRADE_60',
    'DB_FACTOR_GRADE_80',
    # Vigas de acoplamiento
    'COUPLING_BEAM_LN_H_LIMIT',
    'COUPLING_BEAM_LN_H_DIAGONAL',
]
