# app/domain/chapter23/__init__.py
"""
Modulo para Strut-and-Tie ACI 318-25 Capitulo 23.

Aplicacion principal: Columnas pequenas (<15x15 cm) tratadas como
struts no confinados sin refuerzo longitudinal de compresion.

Conceptos clave:
- Struts: elementos en compresion (puntales)
- Ties: elementos en tension (tensores)
- Nodal zones: zonas de conexion

Para columnas pequenas:
- fce = 0.34 x fc' (beta_s=0.4, beta_c=1.0)
- Fns = fce x Acs (la barra NO cuenta como As')
- phi = 0.75
"""

from .strut_capacity import StrutCapacityService, StrutCapacityResult

__all__ = [
    'StrutCapacityService',
    'StrutCapacityResult',
]
