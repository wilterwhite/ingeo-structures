# app/domain/constants/tolerances.py
"""
Tolerancias numéricas para cálculos estructurales.

Centraliza las constantes de tolerancia usadas en verificaciones
de flexocompresión, geometría, y otros cálculos numéricos.
"""

# ============================================================================
# Tolerancias geométricas/numéricas generales
# ============================================================================

# División por cero / valores pequeños
ZERO_TOLERANCE = 1e-6  # Para evitar división por cero

# Determinantes de matrices (paralelismo de líneas)
PARALLEL_TOLERANCE = 1e-10  # Para detectar líneas paralelas en intersección

# ============================================================================
# Tolerancias para ray-casting en diagramas P-M
# ============================================================================

# Parámetro de interpolación en segmentos (0 a 1)
# Permite pequeño margen para errores de precisión numérica
SEGMENT_PARAM_TOLERANCE = 0.001  # -0.001 <= s <= 1.001

# Umbral para considerar SF "dentro" de la curva
INSIDE_SF_THRESHOLD = 0.999  # SF >= 0.999 significa dentro

# ============================================================================
# Tolerancias para capacidades axiales
# ============================================================================

# Margen para detectar exceso de capacidad axial/tensión
# 1.001 = 0.1% de tolerancia para evitar falsos positivos por redondeo
AXIAL_CAPACITY_TOLERANCE = 1.001
