# app/domain/constants/phi_chapter21.py
"""
Factores de reducción de resistencia según ACI 318-25 Capítulo 21.

Este módulo centraliza todos los factores phi usados en verificaciones
de resistencia según la Tabla 21.2.1 y secciones relacionadas.

Referencias ACI 318-25:
=======================

TABLA 21.2.1 - Factores de reducción phi:
-----------------------------------------
(a) Momento, axial, o combinación: 0.65 a 0.90 según §21.2.2
(b) Cortante: 0.75
(c) Torsión: 0.75
(d) Aplastamiento: 0.65

§21.2.2 - Factor phi según deformación neta:
--------------------------------------------
- epsilon_t <= epsilon_ty: phi = 0.65 (compresión controlada)
- epsilon_t >= epsilon_ty + 0.003: phi = 0.90 (tracción controlada)
- Transición: interpolación lineal

§21.2.4 - Modificaciones sísmicas:
----------------------------------
- §21.2.4.1: phi = 0.60 para miembros controlados por cortante
- §21.2.4.4: phi = 0.85 para vigas de acople con refuerzo diagonal
"""

# =============================================================================
# FACTORES PHI PARA FLEXIÓN Y CARGA AXIAL (§21.2.2)
# =============================================================================

PHI_COMPRESSION = 0.65      # Sección controlada por compresión (sin espiral)
PHI_COMPRESSION_SPIRAL = 0.75  # Sección controlada por compresión (con espiral)
PHI_TENSION = 0.90          # Sección controlada por tracción

# Deformaciones para cálculo de phi en zona de transición
EPSILON_TY = 0.002          # Deformación de fluencia típica (fy ≈ 400 MPa)
EPSILON_T_LIMIT = 0.005     # Límite para tracción controlada (epsilon_ty + 0.003)

# Cuantía máxima para asegurar falla dúctil (ρmax = 4%)
# Si se excede, la sección es controlada por compresión (φ = 0.65)
# y se debe aumentar espesor en lugar de agregar más acero
RHO_MAX = 0.04


# =============================================================================
# FACTORES PHI PARA CORTANTE Y TORSIÓN (§21.2.1)
# =============================================================================

PHI_SHEAR = 0.75            # Cortante general
PHI_TORSION = 0.75          # Torsión


# =============================================================================
# FACTORES PHI PARA ELEMENTOS ESPECIALES (§21.2.1)
# =============================================================================

PHI_BEARING = 0.65          # Aplastamiento
PHI_STRUT_TIE = 0.75        # Modelos puntal-tensor (Cap. 23)
PHI_PLAIN_CONCRETE = 0.60   # Concreto simple


# =============================================================================
# MODIFICACIONES SÍSMICAS (§21.2.4)
# =============================================================================

PHI_SHEAR_SEISMIC = 0.60    # Miembros controlados por cortante (§21.2.4.1)
PHI_SHEAR_DIAGONAL = 0.85   # Vigas de acople diagonales (§21.2.4.4)


# =============================================================================
# FUNCIONES DE CÁLCULO DE PHI
# =============================================================================

def calculate_phi_flexure(
    epsilon_t: float,
    is_spiral: bool = False
) -> float:
    """
    Calcula el factor de reducción φ según la deformación del acero (§21.2.2).

    Args:
        epsilon_t: Deformación neta del acero en tracción (valor absoluto)
        is_spiral: True si el elemento tiene refuerzo en espiral

    Returns:
        φ: Factor de reducción de resistencia

    Tabla 21.2.2:
    - epsilon_t <= epsilon_ty: Compresión controlada (0.65 o 0.75)
    - epsilon_t >= epsilon_ty + 0.003: Tracción controlada (0.90)
    - Entre ambos: Interpolación lineal (zona de transición)
    """
    epsilon_t = abs(epsilon_t)
    phi_c = PHI_COMPRESSION_SPIRAL if is_spiral else PHI_COMPRESSION

    if epsilon_t >= EPSILON_T_LIMIT:
        # Sección controlada por tracción
        return PHI_TENSION
    elif epsilon_t <= EPSILON_TY:
        # Sección controlada por compresión
        return phi_c
    else:
        # Zona de transición - interpolación lineal
        return phi_c + (PHI_TENSION - phi_c) * \
               (epsilon_t - EPSILON_TY) / (EPSILON_T_LIMIT - EPSILON_TY)
