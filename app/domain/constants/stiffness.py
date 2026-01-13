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

# Otros factores de rigidez (Tabla 6.6.3.1.1(a))
COLUMN_STIFFNESS_FACTOR = 0.70          # Columnas
BEAM_STIFFNESS_FACTOR = 0.35            # Vigas

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
# LIMITE DE EFECTOS DE SEGUNDO ORDEN - ACI 318-25 Seccion 6.2.5.3
# =============================================================================
# Mu (con efectos 2do orden) <= 1.4 * Mu (1er orden)
# Si se excede este limite, revisar el sistema estructural.

SECOND_ORDER_LIMIT = 1.4  # Factor maximo permitido de amplificacion

# =============================================================================
# FACTOR Cm - ACI 318-25 Seccion 6.6.4.5.3
# =============================================================================
# Cm = 0.6 - 0.4*(M1/M2) para miembros sin cargas transversales
# Cm = 1.0 para miembros con cargas transversales
#
# Convencion de signos:
# - M1 = momento menor en extremo (puede ser + o -)
# - M2 = momento mayor en extremo (siempre positivo por convencion)
# - M1/M2 positivo = curvatura doble (Cm bajo, ~0.4)
# - M1/M2 negativo = curvatura simple (Cm alto, ~1.0)

CM_BASE = 0.6        # Termino constante en formula Cm
CM_FACTOR = 0.4      # Factor multiplicador de M1/M2
CM_MIN = 0.4         # Valor minimo practico de Cm (ACI no especifica, pero es razonable)
CM_TRANSVERSE = 1.0  # Cm cuando hay cargas transversales

# =============================================================================
# NOTAS DE APLICACION
# =============================================================================
# - Para analisis a nivel de carga factorada
# - Si hay cargas laterales sostenidas, dividir I por (1 + beta_ds)
# - Para analisis en servicio: I_servicio = 1.4 × I_factorado (pero <= Ig)
