# 18.10 MUROS ESTRUCTURALES ESPECIALES

## 18.10.1 Alcance

### 18.10.1.1 Aplicabilidad
Aplica a muros especiales, **muros acoplados ductiles**, y todos sus componentes incluyendo **vigas de acople y pilares de muro** del SFRS.

### 18.10.1.2 Muros Prefabricados
Muros prefabricados deben cumplir **18.11** ademas de **18.10**.

### Tabla R18.10.1 - Clasificacion de Segmentos Verticales

| hw/ℓw | ℓw/bw ≤ 2.5 | 2.5 < ℓw/bw ≤ 6.0 | ℓw/bw > 6.0 |
|-------|-------------|-------------------|-------------|
| < 2.0 | Muro | Muro | Muro |
| ≥ 2.0 | Pilar (req. columna 18.10.8.1) | Pilar (columna o alternativo) | Muro |

---

## 18.10.2 Refuerzo

### 18.10.2.1 Refuerzo Distribuido Minimo

| Parametro | Requisito |
|-----------|-----------|
| ρℓ (vertical) | ≥ **0.0025** |
| ρt (horizontal) | ≥ **0.0025** |
| Espaciamiento maximo | **18"** cada direccion |

**Excepcion:** Si Vu ≤ λ√f'c Acv, ρt puede reducirse a valores de **11.6**.

Refuerzo que contribuye a Vn debe ser **continuo** y **distribuido** a traves del plano de cortante.

### 18.10.2.2 Dos Cortinas de Refuerzo
Requeridas si:
- **Vu > 2λ√f'c Acv**, O
- **hw/ℓw ≥ 2.0** (para muro completo)

### 18.10.2.3 Desarrollo y Empalmes
Refuerzo desarrollado o empalmado para **fy en tension** segun 25.4, 25.5 y (a)-(d):

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Excepto en tope: refuerzo longitudinal se extiende ≥ **12 ft** (pero no mas de ℓd) sobre el siguiente nivel |
| (b) | En zonas de fluencia: desarrollo para **1.25fy** (sustituir en 25.4) |
| (c) | Empalmes de traslape en regiones de borde: **PROHIBIDOS** sobre hsx (max 20 ft) y ℓd debajo de secciones criticas |
| (d) | Empalmes mecanicos segun **18.2.7**; soldados segun **18.2.8** |

### 18.10.2.4 Muros con Seccion Critica Unica
Muros o pilares con **hw/ℓw ≥ 2.0**, continuos desde base hasta tope, diseñados para sección crítica única:

| Requisito | Descripcion |
|-----------|-------------|
| **(a) Refuerzo en extremos** | ρ ≥ **6√f'c/fy** dentro de **0.15ℓw** del extremo, ancho = espesor del muro |
| **(b) Extension vertical** | ≥ max(ℓw, Mu/3Vu) arriba y abajo de seccion critica |
| **(c) Terminacion** | No mas del **50%** del refuerzo puede terminar en una seccion |

### 18.10.2.5 Refuerzo en Vigas de Acople
| Tipo de Refuerzo | Desarrollo |
|------------------|------------|
| Longitudinal (segun 18.6.3.1) | **1.25fy** en tension |
| Diagonal (segun 18.10.7.4) | **1.25fy** en tension |

---

## 18.10.3 Fuerzas de Diseno

### 18.10.3.3 Amplificacion de Cortante
```
Ve = Ωv * ωv * Vu,Eh
```

### Tabla 18.10.3.3.3 - Factores de Amplificacion

| Condicion | Ωv | ωv |
|-----------|-----|-----|
| hwcs/ℓw ≤ 1.0 | 1.0 | 1.0 |
| 1.0 < hwcs/ℓw < 2.0 | Interpolacion 1.0-1.5 | 1.0 |
| hwcs/ℓw ≥ 2.0 | 1.5 | 0.8 + 0.09*hn^(1/3) ≥ 1.0 |

Donde:
- hwcs = Altura del muro desde seccion critica
- hn = Altura total del edificio (pies)

**Alternativa**: Se permite tomar **Ωv * ωv = Ωo**

---

## 18.10.4 Resistencia al Cortante

### 18.10.4.1 Ecuacion de Resistencia Nominal
```
Vn = (αc * λ * √f'c + ρt * fyt) * Acv     [Ec. 18.10.4.1]
```

### Coeficiente αc

| hw/ℓw | αc |
|-------|-----|
| ≤ 1.5 | **3** |
| ≥ 2.0 | **2** |
| 1.5 < hw/ℓw < 2.0 | Interpolacion lineal |

**Limite**: f'c ≤ **12,000 psi** para calculo de Vn.

### 18.10.4.3 Muros Bajos
Si **hw/ℓw ≤ 2.0**: **ρℓ ≥ ρt**

### 18.10.4.4 Limites de Resistencia
- Todos los segmentos: **Vn ≤ Σ(αsh * 8√f'c * Acv)**
- Segmento individual: **Vn ≤ αsh * 10√f'c * Acw**

Factor αsh:
```
αsh = 0.7 * [1 + (bw + bcf) * tcf / Acx]²     [Ec. 18.10.4.4]
```
- **1.0 ≤ αsh ≤ 1.2**
- Se permite tomar **αsh = 1.0**

---

## 18.10.5 Diseno por Flexion y Carga Axial

### 18.10.5.2 Ancho Efectivo del Ala
```
bf = menor de:
    - 0.5 * distancia a alma adyacente
    - 0.25 * altura total sobre la seccion
```

---

## 18.10.6 Elementos de Borde

### 18.10.6.1 Dos Enfoques de Diseno

| Enfoque | Seccion | Aplicacion |
|---------|---------|------------|
| Basado en desplazamiento | 18.10.6.2 | hwcs/ℓw ≥ 2.0, continuos desde base |
| Basado en esfuerzos | 18.10.6.3 | Metodo tradicional |

### 18.10.6.2 Enfoque Basado en Desplazamiento

**(a) Requiere elementos de borde especiales cuando:**
```
1.5 * δu/hwcs ≥ ℓw/(600*c)     [Ec. 18.10.6.2a]
```
- δu/hwcs no debe tomarse menor que **0.005**

**(b) Extension vertical:** ≥ max(ℓw, Mu/(4Vu))

**(c) Ancho minimo:** b ≥ √(c * ℓw)/40

**(d) Capacidad de deriva:**
```
δc/hwcs = (1/100) * [4 - 1/50 - (ℓw/b)(c/b) - Ve/(8√f'c*Acv)]
```
- Minimo: **δc/hwcs ≥ 0.015**
- Requisito: **δc/hwcs ≥ 1.5 * δu/hwcs**

### 18.10.6.3 Enfoque Basado en Esfuerzos

| Condicion | Accion |
|-----------|--------|
| σmax ≥ **0.2f'c** | Requiere elementos de borde |
| σ < **0.15f'c** | Permite discontinuar |

### 18.10.6.4 Requisitos para Elementos de Borde Especiales

| Parametro | Requisito |
|-----------|-----------|
| **(a) Extension horizontal** | ≥ max(c - 0.1ℓw, c/2) |
| **(b) Ancho minimo** | b ≥ hu/16 |
| **(c) Si c/ℓw ≥ 3/8** | b ≥ 12" |
| **(e) Refuerzo transversal** | Segun 18.7.5.2(a)-(d), 18.7.5.3 |
| **(f) Espaciamiento hx** | ≤ min(14", (2/3)b) |

### Tabla 18.10.6.4(g) - Refuerzo Transversal

| Tipo | Expresiones |
|------|-------------|
| Ash/sbc (rectangular) | ≥ max[0.3(Ag/Ach - 1)(f'c/fyt), 0.09(f'c/fyt)] |
| ρs (espiral) | ≥ max[0.45(Ag/Ach - 1)(f'c/fyt), 0.12(f'c/fyt)] |

### Tabla 18.10.6.5(b) - Espaciamiento Maximo sin Elementos de Borde Especiales

| Grado | Cerca de seccion critica | Otras ubicaciones |
|-------|-------------------------|-------------------|
| 60 | ≤ min(6db, 6") | ≤ min(8db, 8") |
| 80 | ≤ min(5db, 6") | ≤ min(6db, 6") |
| 100 | ≤ min(4db, 6") | ≤ min(6db, 6") |

---

## 18.10.7 Vigas de Acoplamiento

### Clasificacion por Relacion de Aspecto

| ℓn/h | Tipo de Refuerzo |
|------|------------------|
| ≥ 4 | Longitudinal + transversal (como 18.6) |
| < 2 con Vu ≥ 4λ√f'c Acw | **Diagonal obligatorio** |
| 2 ≤ ℓn/h < 4 | Diagonal o longitudinal |

### 18.10.7.4 Resistencia con Refuerzo Diagonal
```
Vn = 2 * Avd * fy * sin(α) ≤ 10√f'c*Acw     [Ec. 18.10.7.4]
```

**Requisitos:**
- Minimo **4 barras** por grupo diagonal, en **2+ capas**
- Confinamiento individual (c) o de seccion completa (d)

### Tabla 18.10.7.4 - Espaciamiento de Confinamiento

| Grado | Espaciamiento Maximo |
|-------|---------------------|
| 60 | ≤ min(6db, 6") |
| 80 | ≤ min(5db, 6") |
| 100 | ≤ min(4db, 6") |

### 18.10.7.5 Redistribucion de Cortante
- Permitida para vigas con **ℓn/h ≥ 2**
- Maximo **20%** del valor de analisis
- **Σ(φVn) ≥ Σ(Ve)**
- Vigas deben estar **alineadas verticalmente** en el muro

### 18.10.7.6 Penetraciones en Vigas Diagonales
Penetraciones en vigas diseñadas segun 18.10.7.4:

| Requisito | Limite |
|-----------|--------|
| **(a) Cantidad maxima** | **2 penetraciones** |
| **(b) Tipo y diametro** | Cilindrica horizontal, ≤ max(**h/6**, 6") |
| **(c) Separaciones minimas** | 2" de barras diagonales, h/4 de extremos, 4" de losa superior/inferior |
| **(d) Refuerzo transversal** | No debe violar requisitos de 18.10.7.4(d) |

---

## 18.10.8 Pilares de Muro (Wall Piers)

### 18.10.8.1 Requisitos Generales
Satisfacer requisitos de **columnas especiales** (18.7.4, 18.7.5, 18.7.6).

**Alternativa para ℓw/bw > 2.5:**

| Requisito | Especificacion |
|-----------|----------------|
| (a) Cortante de diseno | Segun 18.7.6.1, o ≤ Ωo * Vu |
| (b) Vn y refuerzo | Segun 18.10.4 |
| (c) Refuerzo transversal | Estribos cerrados |
| (d) Espaciamiento vertical | ≤ 6" |
| (e) Extension | ≥ 12" arriba y abajo |
| (f) Elementos de borde | Si se requiere por 18.10.6.3 |

### 18.10.8.2 Pilares en Borde de Muro
Para pilares en el borde de un muro:
- Refuerzo horizontal en segmentos adyacentes **arriba y abajo** del pilar
- Diseñado para transferir **cortante de diseño** del pilar a segmentos adyacentes

---

## 18.10.9 Muros Acoplados Ductiles

| Elemento | Requisito |
|----------|-----------|
| Muros individuales | hwcs/ℓw ≥ 2, satisfacer 18.10 |
| Vigas de acoplamiento | **ℓn/h ≥ 2** en todos los niveles |
| 90% de los niveles | **ℓn/h ≤ 5** |

---

## 18.10.10 Juntas de Construccion
- Especificar segun **26.5.6**
- Superficies rugosas segun **Tabla 22.9.4.2**

---

## 18.10.11 Muros Discontinuos
Columnas que soportan muros estructurales discontinuos deben reforzarse segun **18.7.5.6**.

---

*ACI 318-25 Seccion 18.10*
