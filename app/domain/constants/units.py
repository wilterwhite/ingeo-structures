# app/domain/constants/units.py
"""
Constantes de conversion de unidades.

Sistema de unidades del proyecto:
- Longitudes: mm
- Esfuerzos: MPa
- Fuerzas: tonf (salida), N (calculos internos)
- Momentos: tonf-m (salida), N-mm (calculos internos)

Referencias: ACI 318-25 Appendix E
"""

# =============================================================================
# CONVERSION DE FUERZA
# =============================================================================
# Basado en gravedad estandar: g = 9.80665 m/s²
# 1 tonf (metric ton-force) = 1000 kg × g = 9806.65 N

# Conversiones de fuerza tonf <-> N
# 1 tonf (metric ton-force) = 1000 kg × g = 9806.65 N
TONF_TO_N = 9806.65        # tonf → N: multiplicar (ej: 1 tonf * TONF_TO_N = 9806.65 N)
N_TO_TONF = TONF_TO_N      # Alias: para N → tonf usar DIVIDIR (ej: 9806.65 N / N_TO_TONF = 1 tonf)

# Otras conversiones de fuerza
KGF_TO_N = 9.80665         # 1 kgf = 9.80665 N (exacto)
N_TO_KGF = 1 / KGF_TO_N
LBF_TO_N = 4.4482          # 1 lbf = 4.4482 N
N_TO_LBF = 1 / LBF_TO_N
KIP_TO_KN = 4.4482         # 1 kip = 4.4482 kN
KN_TO_KIP = 1 / KIP_TO_KN

# =============================================================================
# CONVERSION DE MOMENTO
# =============================================================================

# NOTA: Por compatibilidad historica, NMM_TO_TONFM tiene el valor 9806650
# Uso: tonfm_to_Nmm = value_tonfm * NMM_TO_TONFM
#      Nmm_to_tonfm = value_Nmm / NMM_TO_TONFM
TONFM_TO_NMM = 9806650.0   # 1 tonf-m = 9806650 N-mm (multiplicar tonf-m × esto = N-mm)
NMM_TO_TONFM = TONFM_TO_NMM  # Alias por compatibilidad (dividir N-mm por esto para obtener tonf-m)

# Otras conversiones de momento
KIPFT_TO_KNM = 1.356       # 1 kip-ft = 1.356 kN-m
KNM_TO_KIPFT = 1 / KIPFT_TO_KNM
KIPIN_TO_KNM = 0.1130      # 1 kip-in = 0.1130 kN-m

# =============================================================================
# CONVERSION DE LONGITUD
# =============================================================================

MM_TO_M = 0.001
M_TO_MM = 1000.0

# Pulgadas
INCH_TO_MM = 25.4          # Exacto por definicion
MM_TO_INCH = 1 / INCH_TO_MM  # 0.03937

# Pies
FT_TO_M = 0.3048           # Exacto por definicion
M_TO_FT = 1 / FT_TO_M      # 3.2808
FT_TO_MM = FT_TO_M * 1000  # 304.8
MM_TO_FT = 1 / FT_TO_MM    # 0.00328084

# Pulgadas especificas usadas en ACI 318-25
SIX_INCH_MM = 152.4        # 6" en mm
EIGHT_INCH_MM = 203.2      # 8" en mm
TWELVE_INCH_MM = 304.8     # 12" en mm
FOURTEEN_INCH_MM = 355.6   # 14" en mm
EIGHTEEN_INCH_MM = 457.2   # 18" en mm

# Dimensión mínima para columnas sísmicas especiales (§18.7.2.1)
# ACI usa 300mm como valor SI redondeado (12" = 304.8mm)
MIN_COLUMN_DIMENSION_MM = 300.0

# =============================================================================
# CONVERSION DE AREA
# =============================================================================

IN2_TO_MM2 = 645.16        # 1 in² = 645.16 mm²
MM2_TO_IN2 = 1 / IN2_TO_MM2  # 0.00155
FT2_TO_M2 = 0.0929         # 1 ft² = 0.0929 m²

# =============================================================================
# CONVERSION DE ESFUERZO / PRESION
# =============================================================================

PSI_TO_MPA = 0.006895      # 1 psi = 0.006895 MPa
MPA_TO_PSI = 1 / PSI_TO_MPA  # 145.04
KSI_TO_MPA = 6.895         # 1 ksi = 6.895 MPa
MPA_TO_KSI = 1 / KSI_TO_MPA  # 0.1450

# kgf/cm² (sistema MKS)
KGFCM2_TO_MPA = 0.0981     # 1 kgf/cm² = 0.0981 MPa
MPA_TO_KGFCM2 = 1 / KGFCM2_TO_MPA  # 10.19

# Presion de area
PSF_TO_KPA = 0.04788       # 1 psf = 0.04788 kPa
KSF_TO_KPA = 47.88         # 1 ksf = 47.88 kPa

# =============================================================================
# CONVERSION DE DENSIDAD / PESO UNITARIO
# =============================================================================

PCF_TO_KGM3 = 16.02        # 1 lb/ft³ = 16.02 kg/m³
PCF_TO_KNM3 = 0.1571       # 1 lb/ft³ = 0.1571 kN/m³
KNM3_TO_PCF = 1 / PCF_TO_KNM3  # 6.366

# =============================================================================
# FACTOR DE CONVERSION PARA ECUACIONES ACI (sqrt(fc'))
# =============================================================================
# Coeficientes US (con fc' en psi) dividir por 12 para SI (fc' en MPa)
# Ejemplo: Vc = 2√fc' (psi) → Vc = 0.17√fc' (MPa)

SQRT_FC_FACTOR = 12.0      # Factor de conversion para √fc' (psi → MPa)
