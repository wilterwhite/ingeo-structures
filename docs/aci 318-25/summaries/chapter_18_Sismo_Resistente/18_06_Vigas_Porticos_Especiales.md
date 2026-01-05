# 18.6 VIGAS DE PORTICOS ESPECIALES

## 18.6.1 Alcance

### 18.6.1.1 Aplicabilidad
Aplica a vigas de porticos momento especiales del SFRS, proporcionadas principalmente para resistir **flexion y cortante**.

### 18.6.1.2 Conexion a Columnas
Las vigas deben conectar a columnas que satisfagan **18.7**.

---

## 18.6.2 Limites Dimensionales

### 18.6.2.1 Requisitos Geometricos

| Parametro | Requisito |
|-----------|-----------|
| (a) Luz libre | ℓn ≥ **4d** |
| (b) Ancho | bw ≥ **max(0.3h, 10")** |
| (c) Proyeccion mas alla de columna | ≤ **min(c2, 0.75c1)** en cada lado |

---

## 18.6.3 Refuerzo Longitudinal

### 18.6.3.1 Refuerzo Minimo y Maximo
- Minimo **2 barras continuas** superior e inferior
- En cualquier seccion: **As ≥ As,min** (segun 9.6.1.2)

| Grado | ρmax |
|-------|------|
| Grade 60 | **0.025** |
| Grade 80 | **0.020** |

### 18.6.3.2 Resistencia a Flexion
- **M+ en cara del nudo ≥ (1/2) M-** en esa cara
- **M+ o M- en cualquier seccion ≥ (1/4) Mmax** en cara de cualquier nudo

### 18.6.3.3 Empalmes de Traslape
Se permiten si hay refuerzo de hoops/espirales sobre la longitud de empalme:
- Espaciamiento transversal ≤ **min(d/4, 4")**

**PROHIBIDOS en:**
- (a) Dentro de nudos
- (b) Dentro de **2h** de la cara del nudo
- (c) Dentro de **2h** de secciones criticas donde se espera fluencia

### 18.6.3.4 Empalmes Mecanicos y Soldados
- Mecanicos: segun **18.2.7**
- Soldados: segun **18.2.8**

### 18.6.3.5 Pretensado (excepto 18.9.2.3)
Si se usa pretensado, debe satisfacer (a)-(d):

| Requisito | Limite |
|-----------|--------|
| (a) fpc promedio | ≤ **min(500 psi, f'c/10)** |
| (b) Deformacion del tendon | Desadherido en zonas de rotula; ε < **0.01** bajo desplazamiento de diseno |
| (c) Contribucion a flexion | ≤ **25%** de M+ o M- en seccion critica |
| (d) Fatiga de anclajes | 50 ciclos entre **40-85%** de fpu |

---

## 18.6.4 Refuerzo Transversal

### 18.6.4.1 Zonas de Hoops/Estribos Cerrados
Requeridos en:
- (a) **2h desde cara de columna** en ambos extremos
- (b) **2h a cada lado** de secciones donde se espera fluencia

### 18.6.4.2 Soporte Lateral de Barras
En zonas de 18.6.4.1:
- Barras longitudinales principales (tension y compresion) con soporte lateral segun **25.7.2.3 y 25.7.2.4**
- Espaciamiento transversal de barras soportadas ≤ **14"**
- Refuerzo de piel (9.7.2.3) no requiere soporte lateral

### 18.6.4.3 Estribos Cerrados
Pueden formarse con uno o mas U-stirrups con ganchos sismicos + crosstie:
- Crossties consecutivos en la misma barra: ganchos de 90° en **lados opuestos**
- Si losa solo en un lado: ganchos de 90° hacia ese lado

### 18.6.4.4 Espaciamiento de Hoops

| Parametro | Requisito |
|-----------|-----------|
| Primer hoop | ≤ **2"** de cara de columna |
| Espaciamiento s | ≤ **min(d/4, 6", 6db G60, 5db G80)** |

**Nota:** db es de la barra de flexion mas pequena (excluyendo piel).

### 18.6.4.5 Fuera de Zonas de Hoops
Estribos con ganchos sismicos en ambos extremos con **s ≤ d/2**.

### 18.6.4.6 Vigas con Carga Axial Significativa
Si **Pu > Agf'c/10**:
- En zonas de 18.6.4.1: hoops segun **18.7.5.2-18.7.5.4**
- Resto de longitud: hoops segun 18.7.5.2 con **s ≤ min(6", 6db G60, 5db G80)**
- Si recubrimiento > 4": refuerzo transversal adicional con recubrimiento ≤ 4" y s ≤ 12"

---

## 18.6.5 Resistencia al Cortante

### 18.6.5.1 Fuerzas de Diseno
Ve se calcula considerando:
- Momentos **Mpr** (resistencia probable con 1.25fy) actuando en caras del nudo en **curvatura reversa**
- Cargas de gravedad y sismo vertical factoradas

```
Ve = (Mpr1 + Mpr2)/ℓn ± wu*ℓn/2
```

Donde: wu = (1.2 + 0.2SDS)D + 1.0L + 0.2S

### 18.6.5.2 Refuerzo Transversal
En zonas de 18.6.4.1, disenar para cortante asumiendo **Vc = 0** cuando se cumplan **(a) Y (b)**:

| Condicion | Criterio |
|-----------|----------|
| (a) | Cortante sismico ≥ **0.5 Vu,max** en esa zona |
| (b) | **Pu < Agf'c/20** (incluyendo sismo) |

---

*ACI 318-25 Seccion 18.6*
