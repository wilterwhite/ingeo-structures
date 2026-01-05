# ACI 318-25 - 6.5 METODO SIMPLIFICADO

---

## 6.5.1 Condiciones de Aplicabilidad

| Requisito | Condicion |
|-----------|-----------|
| (a) | Miembros prismaticos |
| (b) | Cargas uniformemente distribuidas |
| (c) | L <= 3D |
| (d) | Al menos dos tramos |
| (e) | Tramo mayor <= 1.20 x tramo menor |

---

## Tabla 6.5.2 - Momentos Aproximados

| Momento | Ubicacion | Condicion | Mu |
|---------|-----------|-----------|-----|
| **Positivo** | Tramo extremo | Extremo integral con soporte | wu*ln²/14 |
| | | Extremo no restringido | wu*ln²/11 |
| | Tramos interiores | Todos | wu*ln²/16 |
| **Negativo** | Cara interior apoyo exterior | Con viga de borde | wu*ln²/24 |
| | | Con columna | wu*ln²/16 |
| | Cara exterior 1er apoyo interior | Dos tramos | wu*ln²/9 |
| | | Mas de dos tramos | wu*ln²/10 |
| | Cara de otros apoyos | Todos | wu*ln²/11 |
| | Todos los apoyos | Losas ln <= 10 ft o rigidez col/viga > 8 | wu*ln²/12 |

**Nota:** Para momentos negativos, ln = promedio de luces claras adyacentes.

---

## Tabla 6.5.4 - Cortantes Aproximados

| Ubicacion | Vu |
|-----------|-----|
| Cara exterior del primer apoyo interior | **1.15 * wu*ln/2** |
| Cara de todos los otros apoyos | wu*ln/2 |

---

## 6.5.3 Redistribucion
**NO se permite** redistribuir momentos calculados con el metodo simplificado.

---

*ACI 318-25 Seccion 6.5*
