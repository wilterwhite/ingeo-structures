# 18.14 MIEMBROS NO PARTE DEL SFRS

## 18.14.1 Alcance

Aplica a miembros **no designados** como parte del SFRS en estructuras asignadas a **SDC D, E, F**.

---

## 18.14.2 Acciones de Diseno

Evaluar para combinaciones de gravedad de **5.3** incluyendo efecto de movimiento vertical del suelo actuando simultaneamente con desplazamiento de diseno **δu**.

---

## 18.14.3 Vigas, Columnas y Nudos Vaciados en Sitio

### 18.14.3.1 Seleccion de Requisitos
- Si efectos de δu **no se calculan**: usar 18.14.3.3
- Si se calculan: usar 18.14.3.2 o 18.14.3.3 segun magnitud de momentos/cortantes inducidos

### 18.14.3.2 Cuando Momentos/Cortantes NO Exceden Resistencia

| Elemento | Requisitos |
|----------|------------|
| **(a) Vigas** | Satisfacer **18.6.3.1**; transversal segun 25.7 @ ≤ **d/2** |
| Vigas con Pu > Ag*f'c/10 | Estribos cerrados segun **18.7.5.2** @ ≤ menor de **6db** y **6"** |
| **(b) Columnas** | Satisfacer **18.7.4.1** y **18.7.6** |
| | Espirales (25.7.3) o estribos (25.7.4) en toda altura @ ≤ menor de **6db** y **6"** |
| | Transversal segun **18.7.5.2(a)-(e)** en longitud ℓo desde cada cara de nudo |
| **(c) Columnas Pu > 0.35Po** | Satisfacer (b) y **18.7.5.7** |
| | Transversal ≥ **0.5 * mayor de Tabla 18.7.5.4 (a) y (b)** para rectangulares |
| | Transversal ≥ **0.5 * mayor de Tabla 18.7.5.4 (d) y (e)** para espirales |
| | En longitud ℓo desde cada cara de nudo |
| **(d) Nudos** | Satisfacer **Capitulo 15** |

### 18.14.3.3 Cuando Momentos/Cortantes EXCEDEN Resistencia (o no se calculan)

| Elemento | Requisitos |
|----------|------------|
| **(a) Materiales/empalmes** | Segun **18.2.5 - 18.2.8** (requisitos SMF) |
| **(b) Vigas** | Satisfacer **18.14.3.2(a)** y **18.6.5** |
| **(c) Columnas** | Satisfacer **18.7.4, 18.7.5, 18.7.6** (excepto 18.7.4.3) |
| **(d) Nudos** | Satisfacer **18.4.4.1** |

---

## 18.14.4 Vigas y Columnas Prefabricadas

### 18.14.4.1 Requisitos
Miembros prefabricados que no contribuyen a resistencia lateral, incluyendo conexiones:

| Requisito | Descripcion |
|-----------|-------------|
| **(a)** | Satisfacer **18.14.3** |
| **(b)** | Estribos de 18.14.3.2(b) en **toda la altura** de columna, incluyendo profundidad de vigas |
| **(c)** | Refuerzo de integridad estructural segun **4.10** |
| **(d)** | Longitud de apoyo de viga ≥ **2"** mas que lo determinado por **16.2.6** |

---

## 18.14.5 Conexiones Losa-Columna

### 18.14.5.1 Criterio de Deriva para Refuerzo de Cortante

**Refuerzo de cortante requerido en seccion critica (22.6.4.1) cuando:**

| Tipo de Losa | Condicion |
|--------------|-----------|
| No pretensada | Δx/hsx ≥ **0.035 - (1/20)(vuv/φvc)** |
| Postensada (fpc segun 8.6.2.1) | Δx/hsx ≥ **0.040 - (1/20)(vuv/φvc)** |

**Donde:**
- vuv = esfuerzo cortante por gravedad + componente vertical de sismo (sin transferencia de momento)
- vc = calculado segun **22.6.5**
- Para postensado: **Vp = 0** al calcular vc
- Δx/hsx = mayor de valores de pisos adyacentes arriba y abajo
- Combinaciones de carga: solo las que incluyen **E**

### 18.14.5.2 Exenciones

| Tipo de Losa | Exento si |
|--------------|-----------|
| No pretensada | Δx/hsx ≤ **0.005** |
| Postensada (fpc segun 8.6.2.1) | Δx/hsx ≤ **0.01** |

### 18.14.5.3 Refuerzo de Cortante Requerido

| Parametro | Requisito |
|-----------|-----------|
| Resistencia | vs ≥ **3.5√f'c** en seccion critica |
| Extension | ≥ **4 * espesor de losa** desde cara del soporte |
| Tipo | Segun **8.7.6** o **8.7.7** |

---

## 18.14.6 Pilares de Muro (Wall Piers)

### 18.14.6.1 Requisitos
- Pilares de muro no parte del SFRS deben satisfacer **18.10.8**
- Si codigo general incluye factor de sobrerresistencia Ωo:
  - Cortante de diseno permitido = **Ωo * cortante inducido bajo δu**

---

## Figura R18.14.5.1 - Criterio de Refuerzo de Cortante

```
Deriva de diseno (Δx/hsx)
    ^
0.04|         Postensada
    |        /
0.03|-------/-------- Refuerzo requerido
    |      /  No pretensada
0.02|     /
    |    /
0.01|---/------------ Refuerzo NO requerido
    |  /
0.00+-------------------> vuv/φvc
    0   0.2  0.4  0.6  0.7
```

**Limites sin refuerzo:**
- No pretensada: Δx/hsx ≤ 0.005
- Postensada: Δx/hsx ≤ 0.01

---

*ACI 318-25 Seccion 18.14*
