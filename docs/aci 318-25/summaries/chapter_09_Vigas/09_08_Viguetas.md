# ACI 318-25 - Seccion 9.8: SISTEMAS DE VIGUETAS EN UNA DIRECCION (NO PRESFORZADOS)

---

## 9.8.1 Requisitos Generales

### Limites Dimensionales

| Requisito | Limite |
|-----------|--------|
| Ancho minimo de nervaduras | 4 in. |
| Profundidad maxima (excluyendo losa) | 3.5 x ancho minimo |
| Espaciamiento libre maximo entre nervaduras | 30 in. |
| Aumento permitido de Vc | 1.1 x valores de 22.5 |

### 9.8.1.6 Integridad Estructural

Al menos una barra inferior en cada vigueta continua, desarrollada con **1.25 fy** en la cara del apoyo.

### 9.8.1.7 Refuerzo Perpendicular

Refuerzo perpendicular a las nervaduras segun 24.4.

### 9.8.1.8 Sistemas No Conformes

Sistemas que no satisfacen 9.8.1.1-9.8.1.4 deben disenarse como **losas y vigas**.

---

## 9.8.2 Sistemas con Rellenos Estructurales

| Requisito | Valor |
|-----------|-------|
| Espesor de losa sobre rellenos | >= mayor de (claro libre/12) y 1.5 in. |
| Calculo de resistencia | Se permite incluir cascarones verticales de rellenos |

---

## 9.8.3 Sistemas con Otros Rellenos

| Requisito | Valor |
|-----------|-------|
| Espesor de losa | >= mayor de (claro libre/12) y 2 in. |

---

## Diagrama Tipico de Sistema de Viguetas

```
        Espesor de losa (tf)
        |<-->|
   _____|____|_____|____|_____|____|_____
  |                                      |
  |    |----| s  |----| s  |----|       |
  |    |    |    |    |    |    |       |
  |    |    |    |    |    |    |       |
  |____|    |____|    |____|    |_______|
       |bw  |    |bw  |    |bw  |
       |<-->|    |<-->|    |<-->|

Donde:
- bw >= 4 in. (ancho de nervadura)
- h <= 3.5 bw (profundidad sin losa)
- s <= 30 in. (espaciamiento libre)
```

---

## Resumen de Requisitos

| Parametro | Valor Minimo/Maximo |
|-----------|---------------------|
| bw (ancho nervadura) | >= 4 in. |
| h (profundidad nervadura) | <= 3.5 bw |
| Espaciamiento libre | <= 30 in. |
| tf (relleno estructural) | >= max(claro/12, 1.5 in.) |
| tf (otros rellenos) | >= max(claro/12, 2 in.) |
| Vc | 1.1 x valor normal |

---

## Referencias

| Tema | Seccion |
|------|---------|
| Resistencia a cortante | 22.5 |
| Control de fisuracion | 24.4 |

---

*ACI 318-25 Seccion 9.8 - Sistemas de Viguetas en Una Direccion*
