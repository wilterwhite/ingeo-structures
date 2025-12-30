# app/domain/constants/stiffness.py
"""
Constantes de rigidez efectiva segun ACI 318-25 Tabla 6.6.3.1.1(a).

Para diseno sismico, muros siempre se consideran agrietados.
Esto es apropiado para Chile donde casi todo es sismico.
"""

# =============================================================================
# FACTORES DE RIGIDEZ EFECTIVA - ACI 318-25 Tabla 6.6.3.1.1(a)
# =============================================================================

# Factor de rigidez para muros (siempre agrietado para diseno sismico)
# I_eff = factor × Ig
WALL_STIFFNESS_FACTOR = 0.35  # Muros fisurados

# Otros factores (referencia, para uso futuro)
WALL_UNCRACKED_STIFFNESS_FACTOR = 0.70  # Muros no fisurados
COLUMN_STIFFNESS_FACTOR = 0.70          # Columnas
BEAM_STIFFNESS_FACTOR = 0.35            # Vigas
FLAT_SLAB_STIFFNESS_FACTOR = 0.25       # Losas planas

# =============================================================================
# MOMENTO MINIMO M2,min - ACI 318-25 Seccion 6.6.4.5.4
# =============================================================================
# M2,min = Pu * e_min
# e_min = 15 + 0.03*h (mm)  [equivalente SI de 0.6 + 0.03*h en pulgadas]
#
# Donde:
# - Pu = carga axial factorada (N o kN)
# - h = dimension de la seccion en direccion de estabilidad (mm)
# - e_min = excentricidad minima (mm)

M2_MIN_ECCENTRICITY_BASE = 15.0    # mm (equivale a 0.6 in)
M2_MIN_ECCENTRICITY_FACTOR = 0.03  # mm/mm (adimensional)

# =============================================================================
# NOTAS DE APLICACION
# =============================================================================
# - Para analisis a nivel de carga factorada
# - Si hay cargas laterales sostenidas, dividir I por (1 + beta_ds)
# - Para analisis en servicio: I_servicio = 1.4 × I_factorado (pero <= Ig)
