# 18.4 PORTICOS DE MOMENTO INTERMEDIOS

## 18.4.1 Alcance
Aplica a porticos momento intermedios incluyendo **losas en dos direcciones sin vigas** que forman parte del SFRS (tipicamente **SDC C**).

---

## 18.4.2 Vigas

### 18.4.2.1 Refuerzo Longitudinal
- Minimo **2 barras continuas** superior e inferior
- Barras inferiores continuas: **As ≥ 0.25 As,max**
- Desarrollo para **1.25fy** en cara del apoyo

### 18.4.2.2 Resistencia a Flexion
- **M+ en cara del nudo ≥ (1/3) M-** en esa cara
- **M+ o M- en cualquier seccion ≥ (1/5) Mmax** en cara de cualquier nudo

### 18.4.2.3 Resistencia al Cortante
φVn debe ser al menos el **menor de (a) y (b)**:

| Opcion | Calculo de Ve |
|--------|---------------|
| (a) | Ve = (Mnl + Mnr)/ℓn + Vu,gravedad (incluyendo sismo vertical) |
| (b) | Cortante maximo de combinaciones con **2E** sustituyendo E |

**Ejemplo combinacion (b):** U = 1.2D + 2.0E + 1.0L + 0.2S

### 18.4.2.4 Refuerzo Transversal en Extremos
Hoops o estribos cerrados (segun 18.6.4.3) sobre **2h desde la cara del apoyo**:

| Parametro | Requisito |
|-----------|-----------|
| Primer hoop | ≤ 2" de la cara del apoyo |
| Espaciamiento | ≤ min(d/4, 8db,long, 24db,trans, 12") |

### 18.4.2.5 Espaciamiento General
Refuerzo transversal con **s ≤ d/2** en toda la longitud de la viga.

### 18.4.2.6 Vigas con Carga Axial
Si **Pu > Agf'c/10**: refuerzo transversal segun 25.7.2.2 y 25.7.2.3 o 25.7.2.4.

---

## 18.4.3 Columnas

### 18.4.3.1 Resistencia al Cortante
φVn debe ser al menos el **menor de (a) y (b)**:

| Opcion | Calculo de Ve |
|--------|---------------|
| (a) | Ve = (Mnt + Mnb)/ℓu con Pu que resulte en maxima Mn |
| (b) | Cortante maximo de combinaciones con **ΩoE** sustituyendo E |

**Nota:** En ASCE/SEI 7, Ωo = 3.0 para porticos intermedios.

### 18.4.3.2 Tipo de Refuerzo
Columnas deben tener refuerzo en espiral (Cap. 10) o satisfacer 18.4.3.3-18.4.3.5.

### 18.4.3.3 Hoops en Extremos
Hoops con espaciamiento **so** sobre longitud **ℓo** desde la cara del nudo:

**Espaciamiento so ≤ menor de:**

| Grado | Limite |
|-------|--------|
| Grade 60 | min(8db, 8") |
| Grade 80 | min(6db, 6") |
| Todos | (1/2) dimension minima de columna |

**Longitud ℓo ≥ mayor de:**
- (1/6) luz libre de columna
- Dimension maxima de seccion transversal
- 18"

### 18.4.3.4 Ubicacion del Primer Hoop
Primer hoop a **≤ so/2** de la cara del nudo.

### 18.4.3.5 Fuera de ℓo
Espaciamiento segun **10.7.6.5.2**.

### 18.4.3.6 Columnas Bajo Muros Discontinuos
Si la porcion de Pu relacionada con sismo **excede Agf'c/10**:
- Refuerzo transversal con espaciamiento **so** en **toda la altura** bajo el nivel de discontinuidad
- Si fuerzas fueron amplificadas por Ωo: limite aumenta a **Agf'c/4**
- Refuerzo transversal se extiende arriba y abajo segun **18.7.5.6(b)**

---

## 18.4.4 Nudos

### 18.4.4.1 Detallado
Satisfacer **15.7.1.2, 15.7.1.3** y 18.4.4.2-18.4.4.5.

### 18.4.4.2 Vigas Profundas
Si viga que genera cortante tiene **h_viga > 2h_columna**:
- Analisis y diseno por **metodo strut-and-tie (Capitulo 23)**
- φVn del nudo segun strut-and-tie **no debe exceder** φVn segun 15.5
- Requisitos de detallado 18.4.4.3-18.4.4.5 aplican

### 18.4.4.3 Desarrollo de Refuerzo
Refuerzo longitudinal terminado en nudo debe:
- Extenderse a la **cara lejana del nucleo del nudo**
- Desarrollarse en tension segun **18.8.5**

### 18.4.4.4 Espaciamiento de Refuerzo Transversal
**s ≤ menor de 18.4.3.3(a)-(c)** dentro de la altura de la viga mas profunda.

### 18.4.4.5 Barras con Cabeza en Parte Superior
Si refuerzo superior de viga son barras con cabeza que terminan en el nudo:
- Columna debe extenderse **≥ h del nudo** sobre el nudo, O
- Refuerzo de viga debe estar confinado por refuerzo vertical adicional

### 18.4.4.6 Nudos Losa-Columna
- Satisfacer requisitos de refuerzo transversal de **15.7.2**
- Al menos **una capa** de refuerzo transversal entre refuerzo superior e inferior de losa

### 18.4.4.7 Resistencia al Cortante del Nudo

**18.4.4.7.1** φVn ≥ Vu

**18.4.4.7.2** Vu del nudo segun **18.3.4** (fuerzas de viga con fy, no 1.25fy)

**18.4.4.7.3** φ segun **21.2.1** para cortante

**18.4.4.7.4** Vn del nudo segun **18.8.4.3**

---

## 18.4.5 Losas en Dos Direcciones sin Vigas

### 18.4.5.1 Momento en el Apoyo
Msc calculado para combinaciones **Eq. (5.3.1e) y (5.3.1g)**. Refuerzo para resistir Msc debe colocarse dentro del **column strip** (8.4.1.5).

### 18.4.5.2 Ancho Efectivo
Refuerzo dentro del ancho efectivo (8.4.2.2.3) debe resistir **γfMsc**. Para conexiones de borde y esquina, ancho efectivo **no excede ct** desde cara de columna.

### 18.4.5.3 Refuerzo en Column Strip
Al menos **50%** del refuerzo del column strip en el apoyo debe estar dentro del ancho efectivo.

### 18.4.5.4 Refuerzo Superior Continuo
Al menos **25%** del refuerzo superior en el column strip debe ser **continuo en todo el claro**.

### 18.4.5.5 Refuerzo Inferior Continuo
Refuerzo inferior continuo en column strip **≥ (1/3)** del refuerzo superior en el apoyo.

### 18.4.5.6 Refuerzo Inferior en Midspan
Al menos **50%** del refuerzo inferior del middle strip y **todo** el refuerzo inferior del column strip en midspan debe ser **continuo** y desarrollar **fy** en la cara de columnas/muros.

### 18.4.5.7 Bordes Discontinuos
**Todo** el refuerzo superior e inferior en el apoyo debe desarrollarse en la cara de columnas/muros.

### 18.4.5.8 Limite de Cortante por Punzonamiento
En secciones criticas (22.6.4.1), esfuerzo de cortante por gravedad (sin transferencia de momento):

| Tipo de Losa | Limite |
|--------------|--------|
| No pretensada | vuv ≤ **0.4φvc** |
| Postensada (con fpc segun 8.6.2.1) | vuv ≤ **0.5φvc** |

**Exencion:** No aplica si conexion satisface **18.14.5**.

**Limites de exencion por deriva:**

| Tipo | Limite Δx/hsx |
|------|---------------|
| No pretensada | ≤ 0.005 |
| Postensada | ≤ 0.01 |

---

*ACI 318-25 Seccion 18.4*
