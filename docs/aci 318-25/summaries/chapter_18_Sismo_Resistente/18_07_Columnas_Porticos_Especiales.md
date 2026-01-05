# 18.7 COLUMNAS DE PORTICOS ESPECIALES

## 18.7.1 Alcance

### 18.7.1.1 Aplicabilidad
Aplica a columnas de porticos momento especiales del SFRS, proporcionadas para resistir **flexion, cortante y carga axial**.

---

## 18.7.2 Limites Dimensionales

### 18.7.2.1 Requisitos Geometricos

| Parametro | Requisito |
|-----------|-----------|
| (a) Dimension minima | ≥ **12"** (medida en linea recta por centroide) |
| (b) Relacion de aspecto | ≥ **0.4** |

---

## 18.7.3 Resistencia Minima a Flexion de Columnas

### 18.7.3.1 Requisito General
Columnas deben satisfacer 18.7.3.2 o 18.7.3.3, **excepto** en conexiones donde:
- Columna es discontinua arriba del nudo, Y
- **Pu < Agf'c/10** (combinaciones con E)

### 18.7.3.2 Columna Fuerte - Viga Debil
```
ΣMnc ≥ (6/5) ΣMnb                    [Eq. 18.7.3.2]
```

Donde:
- **ΣMnc** = Suma de Mn de columnas en caras del nudo (usar Pu que resulte en **menor** Mn)
- **ΣMnb** = Suma de Mn de vigas en caras del nudo (incluir refuerzo de losa en ancho efectivo segun 6.3.2 si desarrollado)

Debe satisfacerse para momentos de viga en **ambas direcciones** (horario y antihorario).

### 18.7.3.3 Columnas que No Satisfacen 18.7.3.2
- Ignorar su aporte a **resistencia y rigidez lateral** del edificio
- Disenar segun **18.14** (miembros no parte del SFRS)

---

## 18.7.4 Refuerzo Longitudinal

### 18.7.4.1 Area de Refuerzo
```
0.01Ag ≤ Ast ≤ 0.06Ag
```

### 18.7.4.2 Columnas con Hoops Circulares
Minimo **6 barras longitudinales**.

### 18.7.4.3 Control de Adherencia
Sobre la altura libre de columna, satisfacer **(a) o (b)**:

| Opcion | Requisito |
|--------|-----------|
| (a) | **1.25ℓd ≤ ℓu/2** (seleccionar refuerzo longitudinal) |
| (b) | **Ktr ≥ 1.2db** (seleccionar refuerzo transversal) |

### 18.7.4.4 Empalmes
- Mecanicos: segun **18.2.7**
- Soldados: segun **18.2.8**
- **Empalmes de traslape:** solo en **mitad central** de la altura, disenados como empalmes de tension, con refuerzo transversal segun 18.7.5.2 y 18.7.5.3

---

## 18.7.5 Refuerzo Transversal

### 18.7.5.1 Longitud ℓo
Refuerzo de 18.7.5.2-18.7.5.4 sobre longitud **ℓo** desde cada cara del nudo y en ambos lados de secciones de fluencia:

```
ℓo ≥ max(h, ℓu/6, 18")
```

### 18.7.5.2 Configuracion del Refuerzo Transversal

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Espirales simples/traslapadas, hoops circulares, o hoops rectangulares simples/traslapados con/sin crossties |
| (b) | Dobleces de hoops y crossties deben **enganchar barras longitudinales perimetrales** |
| (c) | Crossties del mismo tamano o menor que hoops (segun 25.7.2.2). Crossties consecutivos **alternados extremo por extremo** |
| (d) | Hoops/crossties rectangulares: soporte lateral segun **25.7.2.2 y 25.7.2.3** |
| (e) | Espaciamiento **hx ≤ 14"** entre barras soportadas por esquina de crosstie o hoop |
| (f) | Si **Pu > 0.3Agf'c** o **f'c > 10,000 psi**: cada barra con soporte de esquina de hoop o gancho sismico; **hx ≤ 8"** |

### 18.7.5.3 Espaciamiento del Refuerzo Transversal

```
s ≤ min(h/4, 6db G60, 5db G80, so)
```

Donde:
```
so = 4 + (14 - hx)/3                 [Eq. 18.7.5.3]
```
- **4" ≤ so ≤ 6"**

### 18.7.5.4 Cantidad de Refuerzo Transversal

**Tabla 18.7.5.4 - Refuerzo Transversal para Columnas de Porticos Especiales**

| Tipo | Condiciones | Expresiones |
|------|-------------|-------------|
| **Ash/sbc** (rectangular) | Pu ≤ 0.3Agf'c Y f'c ≤ 10,000 psi | Mayor de (a) y (b) |
| | Pu > 0.3Agf'c O f'c > 10,000 psi | Mayor de (a), (b) y (c) |
| **ρs** (espiral/circular) | Pu ≤ 0.3Agf'c Y f'c ≤ 10,000 psi | Mayor de (d) y (e) |
| | Pu > 0.3Agf'c O f'c > 10,000 psi | Mayor de (d), (e) y (f) |

**Expresiones:**
```
(a) 0.3 * (Ag/Ach - 1) * (f'c/fyt)
(b) 0.09 * (f'c/fyt)
(c) 0.2 * kf * kn * Pu/(fyt*Ach)

(d) 0.45 * (Ag/Ach - 1) * (f'c/fyt)
(e) 0.12 * (f'c/fyt)
(f) 0.35 * kf * Pu/(fyt*Ach)
```

**Factores:**
```
kf = f'c/25,000 + 0.6 ≥ 1.0          [Eq. 18.7.5.4a]
kn = nl/(nl - 2)                      [Eq. 18.7.5.4b]
```
Donde nl = numero de barras longitudinales soportadas alrededor del perimetro.

### 18.7.5.5 Fuera de ℓo
- Espirales segun **25.7.3**, o
- Hoops/crossties segun **25.7.2 y 25.7.4** con **s ≤ min(6", 6db G60, 5db G80)**

(A menos que se requiera mas por 18.7.4.4 o 18.7.6)

### 18.7.5.6 Columnas Bajo Miembros Discontinuos
Si Pu relacionado con sismo **> Agf'c/10** (o Agf'c/4 si se uso Ωo):

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Refuerzo de 18.7.5.2-18.7.5.4 en **toda la altura** bajo la discontinuidad |
| (b) | Refuerzo se extiende dentro del miembro discontinuo al menos **ℓd** de la barra de columna mas grande (segun 18.8.5). Si termina en zapata/losa mat: al menos **12"** |

### 18.7.5.7 Recubrimiento Excesivo
Si recubrimiento sobre refuerzo de confinamiento **> 4"**: refuerzo transversal adicional con recubrimiento ≤ 4" y s ≤ 12".

---

## 18.7.6 Resistencia al Cortante

### 18.7.6.1 Fuerzas de Diseno

**18.7.6.1.1** Ve se calcula de las **maximas fuerzas** en las caras del nudo:
- Usar **Mpr** en cada extremo para el rango de **Pu** factorado
- Cortante de columna no necesita exceder el basado en **Mpr de vigas** en el nudo
- Ve **no menor que** cortante factorado del analisis

```
Ve = (Mpr,sup + Mpr,inf)/ℓu
```

### 18.7.6.2 Refuerzo Transversal

**18.7.6.2.1** En longitudes ℓo, disenar para cortante con **Vc = 0** cuando **(a) Y (b)**:

| Condicion | Criterio |
|-----------|----------|
| (a) | Cortante sismico (de 18.7.6.1) ≥ **0.5 Vu,max** en ℓo |
| (b) | **Pu < Agf'c/20** (incluyendo sismo) |

---

*ACI 318-25 Seccion 18.7*
