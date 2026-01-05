# 22.2 SUPUESTOS DE DISENO PARA MOMENTO Y CARGA AXIAL

## 22.2.1 Equilibrio y Compatibilidad de Deformaciones

| Seccion | Requisito |
|---------|-----------|
| 22.2.1.1 | El equilibrio debe satisfacerse en cada seccion |
| 22.2.1.2 | Deformacion en concreto y refuerzo no pretensado proporcional a la distancia del eje neutro |
| 22.2.1.3 | Deformacion en concreto pretensado incluye deformacion por preesfuerzo efectivo |
| 22.2.1.4 | Cambios de deformacion en refuerzo pretensado adherido proporcionales a distancia del eje neutro |

## 22.2.2 Supuestos de Diseno para Concreto

### 22.2.2.1 Deformacion Maxima del Concreto
```
epsilon_cu = 0.003
```
**Nota (R22.2.2.1):** En ensayos se han observado valores de 0.003 a 0.008, pero para miembros de proporciones normales se usa 0.003 a 0.004.

### 22.2.2.2 Resistencia a Tension del Concreto
**Se desprecia** en calculos de resistencia a flexion y axial.

### 22.2.2.3 Relacion Esfuerzo-Deformacion
Puede representarse por forma rectangular, trapezoidal, parabolica u otra que prediga resistencia en acuerdo con ensayos.

## 22.2.2.4 Bloque de Esfuerzos Rectangular Equivalente

### 22.2.2.4.1 Esfuerzo Uniforme
```
f = 0.85 * f'c
```
Distribuido sobre zona de compresion equivalente de profundidad **a**.

### Profundidad del Bloque
```
a = beta_1 * c                    (Ec. 22.2.2.4.1)
```
Donde **c** = distancia de fibra de compresion maxima al eje neutro.

### Tabla 22.2.2.4.3 - Valores de beta_1

| f'c (psi) | beta_1 |
|-----------|--------|
| 2500 <= f'c <= 4000 | **0.85** |
| 4000 < f'c < 8000 | 0.85 - 0.05*(f'c - 4000)/1000 |
| f'c >= 8000 | **0.65** |

## 22.2.3 Supuestos para Refuerzo No Pretensado

| Seccion | Requisito |
|---------|-----------|
| 22.2.3.1 | Refuerzo corrugado debe cumplir 20.2.1 |
| 22.2.3.2 | Relacion esfuerzo-deformacion y Es segun 20.2.2.1 y 20.2.2.2 |

## 22.2.4 Supuestos para Refuerzo Pretensado

| Seccion | Condicion | Referencia |
|---------|-----------|------------|
| 22.2.4.1 | Pretensado adherido | fps segun 20.3.2.3 |
| 22.2.4.2 | Pretensado no adherido | fps segun 20.3.2.4 |
| 22.2.4.3 | Longitud embebida < ld | Esfuerzo segun 25.4.8.3 |

---

*ACI 318-25 Seccion 22.2*
