# app/domain/constants/units.py
"""
Constantes de conversion de unidades.

Sistema de unidades del proyecto:
- Longitudes: mm
- Esfuerzos: MPa
- Fuerzas: tonf (salida), N (calculos internos)
- Momentos: tonf-m (salida), N-mm (calculos internos)
"""

# Conversion de fuerza
N_TO_TONF = 9806.65        # 1 tonf = 9806.65 N
TONF_TO_N = 1 / N_TO_TONF  # Para convertir tonf a N

# Conversion de momento
NMM_TO_TONFM = 9806650.0   # 1 tonf-m = 9806650 N-mm
TONFM_TO_NMM = 1 / NMM_TO_TONFM

# Conversion de longitud
MM_TO_M = 0.001
M_TO_MM = 1000.0

# Conversion de pulgadas a mm
INCH_TO_MM = 25.4
MM_TO_INCH = 1 / INCH_TO_MM
