# app/domain/constants/chapter23.py
"""
Constantes Strut-and-Tie ACI 318-25 Capitulo 23.

Aplicacion especifica: Columnas pequenas (<15x15 cm) tratadas como
struts no confinados sin refuerzo longitudinal de compresion.

Referencias:
- ACI 318-25 23.4.1(a): Fns = fce x Acs
- ACI 318-25 23.4.3: fce = 0.85 x beta_c x beta_s x fc'
- ACI 318-25 23.3.1: phi = 0.75 para struts
"""

# =============================================================================
# FACTOR PHI PARA STRUTS (Tabla 21.2.1)
# =============================================================================
# phi = 0.75 para strut-and-tie general (23.3.1)
# phi = 0.60 para struts en diseño sísmico (Tabla 21.2.1, SDC D/E/F)
PHI_STRUT = 0.60  # Factor de reduccion para struts en diseño sísmico

# =============================================================================
# COEFICIENTES BETA_S (23.4.3a) - TIPO DE STRUT
# =============================================================================
# beta_s depende del tipo de strut y refuerzo transversal

BETA_S_BOUNDARY = 1.0       # Strut en frontera/apoyo (sin tension transversal)
BETA_S_INTERIOR_REINFORCED = 0.75  # Interior con refuerzo Tab. 23.5.1
BETA_S_INTERIOR_UNREINFORCED = 0.4  # Interior sin refuerzo adecuado
BETA_S_TENSION_ZONE = 0.4   # Strut en zona de tension

# Para columnas pequenas sin estribos, usar valor conservador:
BETA_S_SMALL_COLUMN = 0.4   # Sin refuerzo transversal distribuido

# =============================================================================
# COEFICIENTES BETA_C (23.4.3b) - CONFINAMIENTO
# =============================================================================
BETA_C_UNCONFINED = 1.0     # Sin confinamiento especial
BETA_C_CONFINED_MAX = 2.0   # Maximo con confinamiento sqrt(A2/A1)

# Para columnas pequenas: no hay confinamiento
BETA_C_SMALL_COLUMN = 1.0

# =============================================================================
# RESISTENCIA EFECTIVA DEL CONCRETO (23.4.3)
# =============================================================================
# fce = 0.85 x beta_c x beta_s x fc'
# Para strut sin confinamiento y sin refuerzo transversal:
# fce = 0.85 x 1.0 x 0.4 x fc' = 0.34 x fc'

WHITNEY_FACTOR = 0.85       # Factor 0.85 del bloque de Whitney
FCE_FACTOR_SMALL_COLUMN = WHITNEY_FACTOR * BETA_C_SMALL_COLUMN * BETA_S_SMALL_COLUMN
# FCE_FACTOR_SMALL_COLUMN = 0.85 x 1.0 x 0.4 = 0.34

# =============================================================================
# LIMITES GEOMETRICOS
# =============================================================================
# Umbral para clasificar como "columna pequena" (strut no confinado)
SMALL_COLUMN_MAX_DIM_MM = 150.0  # Ambas dimensiones deben ser < 150mm

# =============================================================================
# EXPORTACIONES
# =============================================================================
__all__ = [
    'PHI_STRUT',
    'BETA_S_BOUNDARY',
    'BETA_S_INTERIOR_REINFORCED',
    'BETA_S_INTERIOR_UNREINFORCED',
    'BETA_S_TENSION_ZONE',
    'BETA_S_SMALL_COLUMN',
    'BETA_C_UNCONFINED',
    'BETA_C_CONFINED_MAX',
    'BETA_C_SMALL_COLUMN',
    'WHITNEY_FACTOR',
    'FCE_FACTOR_SMALL_COLUMN',
    'SMALL_COLUMN_MAX_DIM_MM',
]
