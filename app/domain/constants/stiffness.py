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
# NOTAS DE APLICACION
# =============================================================================
# - Para analisis a nivel de carga factorada
# - Si hay cargas laterales sostenidas, dividir I por (1 + beta_ds)
# - Para analisis en servicio: I_servicio = 1.4 × I_factorado (pero <= Ig)
