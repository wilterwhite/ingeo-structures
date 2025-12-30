# app/structural/domain/constants/shear.py
"""
Constantes y referencias ACI 318-25 para verificacion de corte en muros.

Referencias ACI 318-25:
=======================

CAPITULO 11 - MUROS (Walls):
----------------------------
- 11.5.4.3: Resistencia nominal al corte en el plano
            Vn = (alpha_c x lambda x sqrt(f'c) + rho_t x fyt) x Acv

- 11.5.4.3: Coeficiente alpha_c segun relacion hw/lw
            Unidades US (psi):
            - alpha_c = 3 si hw/lw <= 1.5 (muros rechonchos)
            - alpha_c = 2 si hw/lw >= 2.0 (muros esbeltos)
            Unidades SI (MPa): dividir por 12
            - alpha_c = 0.25 si hw/lw <= 1.5
            - alpha_c = 0.17 si hw/lw >= 2.0
            - Interpolacion lineal entre 1.5 y 2.0

- 11.5.4.2: Limite maximo de Vn
            Vn <= 8 x sqrt(f'c) x Acv (US)
            Vn <= 0.66 x sqrt(f'c) x Acv (SI, para grupo)
            Vn <= 0.83 x sqrt(f'c) x Acv (SI, individual)

- 11.6.2: Cuantia minima para cortante alto
          Si hw/lw <= 2.0, entonces rho_v >= rho_h

CAPITULO 18 - MUROS ESTRUCTURALES ESPECIALES:
---------------------------------------------
- 18.10.4.1: Misma ecuacion que 11.5.4.3
- 18.10.4.3: Requisito rho_v >= rho_h
- 18.10.4.4: Limites maximos por segmento y grupo

CAPITULO 22 - RESISTENCIA AL CORTE GENERAL:
-------------------------------------------
- 22.5.5.1:  Vc = 0.17 x lambda x sqrt(f'c) x bw x d (SI)
- 22.5.1.2:  Limite: Vs <= 0.66 x sqrt(f'c) x bw x d (SI)

FACTORES DE REDUCCION (Seccion 21.2):
-------------------------------------
- 21.2.1: phi = 0.75 para corte y torsion
"""

# =============================================================================
# FACTORES DE REDUCCION DE RESISTENCIA (ACI 318-25 Tabla 21.2.1)
# =============================================================================

PHI_SHEAR = 0.75  # Factor phi para corte y torsion


# =============================================================================
# PROPIEDADES DEL HORMIGON (ACI 318-14 Seccion 19.2)
# =============================================================================

LAMBDA_NORMAL = 1.0  # lambda = 1.0 para hormigon de peso normal


# =============================================================================
# COEFICIENTES PARA MUROS (ACI 318-14 Tabla 18.10.4.1)
# =============================================================================

# Coeficiente alpha_c para resistencia al corte de muros
ALPHA_C_SQUAT = 0.25    # alpha_c para muros rechonchos (hw/lw <= 1.5)
ALPHA_C_SLENDER = 0.17  # alpha_c para muros esbeltos (hw/lw >= 2.0)

# Limites de interpolacion para alpha_c
HW_LW_SQUAT_LIMIT = 1.5    # Limite inferior (muros rechonchos)
HW_LW_SLENDER_LIMIT = 2.0  # Limite superior (muros esbeltos)

# Ecuacion 11.5.4.4 - Tension axial neta
# alpha_c = 2 * (1 + Nu/(500*Ag)) >= 0  [US: psi]
# alpha_c = 2 * (1 + Nu/(3.45*Ag)) >= 0 [SI: MPa]
# 500 psi = 3.45 MPa (constante de conversion)
ALPHA_C_TENSION_STRESS_MPA = 3.45  # 500 psi en MPa


# =============================================================================
# LIMITES MAXIMOS DE Vn (ACI 318-14 Seccion 18.10.4.4)
# =============================================================================

# Para segmento individual: Vn <= 0.83 x sqrt(f'c) x Acw
VN_MAX_INDIVIDUAL_COEF = 0.83

# Para grupo de segmentos: Vn <= 0.66 x sqrt(f'c) x Acv_total
VN_MAX_GROUP_COEF = 0.66


# =============================================================================
# COEFICIENTES PARA COLUMNAS/VIGAS (ACI 318-14 Seccion 22.5)
# =============================================================================

# Coeficiente para Vc (Ec. 22.5.5.1): Vc = 0.17 x lambda x sqrt(f'c) x bw x d
VC_COEF_COLUMN = 0.17

# Limite del aporte del acero (Seccion 22.5.1.2): Vs <= 0.66 x sqrt(f'c) x bw x d
VS_MAX_COEF = 0.66


# =============================================================================
# CLASIFICACION DE SECCION
# =============================================================================

# Limite de relacion de aspecto para clasificar muro vs columna
# lw/tw >= 4 -> MURO (usar Seccion 18.10.4)
# lw/tw < 4  -> COLUMNA (usar Seccion 22.5)
ASPECT_RATIO_WALL_LIMIT = 4


# =============================================================================
# VALORES POR DEFECTO
# =============================================================================

DEFAULT_COVER_MM = 40  # Recubrimiento por defecto (mm)


# =============================================================================
# CONVERSION DE UNIDADES
# =============================================================================

# Factor de conversion: 1 tonf = 9806.65 N (g x 1000 kg)
N_TO_TONF = 9806.65


# =============================================================================
# CLASIFICACION WALL PIERS (ACI 318-25 Seccion 18.10.8, Tabla R18.10.1)
# =============================================================================

# Limites para clasificacion de pilares de muro (wall piers)
# Un "wall pier" es un segmento vertical de muro con hw/lw < 2.0
WALL_PIER_HW_LW_LIMIT = 2.0

# Clasificacion segun lw/bw cuando hw/lw < 2.0:
# - lw/bw <= 2.5: Pilar con requisitos de columna (S18.7)
# - 2.5 < lw/bw <= 6.0: Pilar con metodo alternativo (S18.10.8.1)
# - lw/bw > 6.0: Se considera muro
WALL_PIER_COLUMN_LIMIT = 2.5    # lw/bw <= 2.5 -> requisitos de columna
WALL_PIER_ALTERNATE_LIMIT = 6.0  # lw/bw <= 6.0 -> metodo alternativo


# =============================================================================
# AMPLIFICACION DE CORTANTE (ACI 318-25 Seccion 18.10.3.3)
# =============================================================================

# Ve = Omega_v x omega_v x VuEh
# Donde:
# - Omega_v: Factor de sobrerresistencia a flexion
# - omega_v: Factor de amplificacion dinamica

# Tabla 18.10.3.3.3 - Factor Omega_v segun hwcs/lw
OMEGA_V_MIN = 1.0   # Para hwcs/lw <= 1.0
OMEGA_V_MAX = 1.5   # Para hwcs/lw >= 2.0

# Tabla 18.10.3.3.3 - Factor omega_v (amplificacion dinamica)
# omega_v = 0.8 + 0.09 * hn^(1/3) >= 1.0  (para hwcs/lw >= 2.0)
# omega_v = 1.0 (para hwcs/lw < 2.0)
OMEGA_V_DYN_COEF = 0.09
OMEGA_V_DYN_BASE = 0.8
OMEGA_V_DYN_MIN = 1.0

# Factor de sobrerresistencia del sistema (ASCE 7)
# Se puede usar Omega_v x omega_v = Omega_o si el codigo lo incluye
OMEGA_0_DEFAULT = 2.5  # Valor tipico para muros especiales


# =============================================================================
# ELEMENTOS DE BORDE (ACI 318-25 Seccion 18.10.6)
# =============================================================================

# Metodo basado en esfuerzos (S18.10.6.3)
BOUNDARY_STRESS_REQUIRED = 0.2   # sigma >= 0.2*f'c requiere elemento de borde
BOUNDARY_STRESS_DISCONTINUE = 0.15  # sigma < 0.15*f'c puede discontinuar

# Metodo basado en desplazamiento (S18.10.6.2)
BOUNDARY_DRIFT_MIN = 0.005  # delta_u/hwcs minimo a considerar
BOUNDARY_DRIFT_CAPACITY_MIN = 0.015  # delta_c/hwcs minimo

# Requisitos dimensionales de elementos de borde (S18.10.6.4)
BOUNDARY_MIN_WIDTH_RATIO = 1/16  # b >= hu/16
BOUNDARY_MIN_WIDTH_INCHES = 12   # b >= 12" cuando c/lw >= 3/8
BOUNDARY_C_LW_THRESHOLD = 3/8    # Umbral para ancho minimo de 12"

# Espaciamiento maximo de refuerzo transversal (Tabla 18.10.6.5(b))
# Segun grado del acero y ubicacion
BOUNDARY_SPACING = {
    60: {'critical': (6, 6), 'other': (8, 8)},    # (n*db, inches)
    80: {'critical': (5, 6), 'other': (6, 6)},
    100: {'critical': (4, 6), 'other': (6, 6)},
}
