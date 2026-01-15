# ACI 318-25 - Sección 23.11: DISEÑO SÍSMICO

---

## 23.11 REQUISITOS SÍSMICOS ESPECIALES

### 23.11.1 Aplicabilidad

Aplica para elementos diseñados con strut-and-tie en:
- **SDC D, E, F** (Categorías de Diseño Sísmico altas)
- Sistemas resistentes a fuerzas sísmicas

**Referencias cruzadas:**
- Capítulo 18: Requisitos sísmicos generales
- Capítulo 15: Juntas viga-columna

---

## 23.11.2 REDUCCIÓN DE RESISTENCIA EN STRUTS

### Resistencia Efectiva Reducida

Para struts en zonas sísmicas críticas:

```
fce(sísmico) = 0.8 × fce     [Ec. 23.11.2]
```

Donde:
- **fce** = Resistencia efectiva según 23.4.3
- **Factor 0.8** = Reducción por degradación cíclica

**Aplicación:**

| Elemento | fce Base | fce Sísmico |
|----------|----------|-------------|
| Boundary strut | 0.85×βc×1.0×fc' | **0.68×βc×fc'** |
| Interior strut | 0.85×βc×0.75×fc' | **0.51×βc×fc'** |
| Zona tensión | 0.85×βc×0.40×fc' | **0.27×βc×fc'** |

---

## 23.11.3 REFUERZO TRANSVERSAL

### 23.11.3.1 Requisito General

El refuerzo transversal debe satisfacer:

```
Ash / (s × bc) >= 0.09 × fc' / fyt     [Ec. 23.11.3.1]
```

Donde:
- **Ash** = Área de refuerzo transversal (in²)
- **s** = Espaciamiento de estribos (in)
- **bc** = Dimensión del núcleo confinado (in)
- **fyt** = Esfuerzo de fluencia del refuerzo transversal (psi)

### 23.11.3.2 Espaciamiento Máximo

**Tabla 23.11.3.2 - Espaciamiento por Grado de Acero:**

| Grado de Acero (fyt) | Espaciamiento Máximo |
|---------------------|---------------------|
| Grado 40 (280 MPa) | **d/4** |
| Grado 60 (420 MPa) | **d/4** |
| Grado 80 (550 MPa) | **6 × db longitudinal** |
| Grado 100 (690 MPa) | **5 × db longitudinal** |

**Límites adicionales:**

```
s <= menor de:
  (a) d/4
  (b) 6 in (150 mm) para Grado 40/60
  (c) 5 in (125 mm) para Grado 80/100
  (d) Tabla 23.11.3.2
```

### 23.11.3.3 Extensión del Confinamiento

```
Longitud de confinamiento = Mayor de:
  (a) Longitud del strut dentro de la junta
  (b) Longitud de desarrollo del tie
  (c) Profundidad del miembro (h)
```

---

## 23.11.4 DESARROLLO DE TIES

### 23.11.4.1 Esfuerzo de Diseño Incrementado

Para desarrollo del refuerzo de ties:

```
Desarrollo basado en: 1.25 × fy     [Ec. 23.11.4.1]
```

**Nota:** Este factor 1.25 es similar al usado en marcos especiales (Cap. 18).

### 23.11.4.2 Longitud de Desarrollo Modificada

```
ld(sísmico) = 1.25 × ld(estándar)
```

**Para ganchos estándar:**

```
ldh(sísmico) = 1.25 × ldh(estándar)
```

### 23.11.4.3 Anclaje en Nodal Zones

| Requisito | Especificación |
|-----------|----------------|
| Longitud mínima | 1.25 × ld desde cara de columna |
| Ganchos | Deben estar confinados con estribos |
| Dispositivos mecánicos | Permitidos si cumplen 1.25 × Ats × fy |

---

## 23.11.5 REDUCCIÓN DE RESISTENCIA EN NODAL ZONES

### Resistencia Reducida

Para nodal zones en zonas sísmicas:

```
Fnn(sísmico) = 0.8 × Fnn     [Ec. 23.11.5]
```

**Valores de fce reducidos:**

Para fc' = 4000 psi, sin confinamiento:

| Tipo de Nodo | βn | fce Base (psi) | fce Sísmico (psi) |
|--------------|-----|----------------|-------------------|
| C-C-C | 1.0 | 3,400 | **2,720** |
| C-C-T | 0.80 | 2,720 | **2,176** |
| C-T-T | 0.60 | 2,040 | **1,632** |

---

## 23.11.6 FACTOR DE SOBRERRESISTENCIA

### Aplicación del Factor Ωo

Para elementos críticos del sistema resistente a sismos:

```
Diseño para: Ωo × E
```

Donde:
- **Ωo** = Factor de sobrerresistencia (típico 2.5 a 3.0)
- **E** = Fuerza sísmica de diseño

**Aplicación en strut-and-tie:**

| Sistema | Ωo Típico |
|---------|-----------|
| Marcos especiales | **3.0** |
| Muros especiales | **2.5** |
| Sistemas duales | **2.5** |

---

## RESUMEN DE REQUISITOS SÍSMICOS

### Factores de Reducción

| Elemento | Factor Sísmico | Aplicación |
|----------|----------------|------------|
| Struts | **0.8** | Resistencia efectiva fce |
| Nodal zones | **0.8** | Resistencia nominal Fnn |
| Desarrollo ties | **1.25** | Multiplicador de fy |

### Refuerzo Transversal

| Parámetro | Requisito |
|-----------|-----------|
| Cuantía mínima | Ash/(s×bc) >= 0.09×fc'/fyt |
| Espaciamiento | <= d/4, <= 6" (Gr.60), <= 5" (Gr.80+) |
| Extensión | >= h, >= ld del tie |

### Comparación con Diseño No-Sísmico

| Aspecto | No-Sísmico | Sísmico SDC D/E/F |
|---------|------------|-------------------|
| fce struts | 0.85×βc×βs×fc' | **0.68×βc×βs×fc'** |
| Fnn nodos | fce×Anz | **0.8×fce×Anz** |
| Desarrollo | fy | **1.25×fy** |
| Refuerzo transversal | Per. 23.5-23.6 | Per. 23.11.3 (más estricto) |

---

## EJEMPLO DE DISEÑO SÍSMICO

**Datos:**
- Junta viga-columna en marco especial
- SDC D
- fc' = 5000 psi
- fy = 60 ksi (Grado 60)
- Nodo C-C-T

**Cálculo de resistencia del nodo:**

1. **Resistencia efectiva base:**
   ```
   fce = 0.85 × 1.0 × 0.80 × 5000 = 3,400 psi
   ```

2. **Reducción sísmica:**
   ```
   fce(sísmico) = 0.8 × 3,400 = 2,720 psi
   ```

3. **Para área de nodo Anz = 200 in²:**
   ```
   Fnn(sísmico) = 2,720 × 200 = 544,000 lb = 544 kips
   phi × Fnn = 0.75 × 544 = 408 kips (capacidad de diseño)
   ```

**Desarrollo del tie:**

1. **Longitud de desarrollo base (ld):**
   ```
   ld = (fy × ψt × ψe × ψs × ψg) / (25 × λ × √fc') × db
   ```

2. **Longitud sísmica:**
   ```
   ld(sísmico) = 1.25 × ld
   ```

**Refuerzo transversal:**

1. **Cuantía requerida:**
   ```
   Ash/(s×bc) >= 0.09 × 5000 / 60000 = 0.0075
   ```

2. **Espaciamiento máximo (Grado 60):**
   ```
   s <= menor de: d/4, 6 in
   ```

---

## REFERENCIAS CRUZADAS

| Sección | Tema | Aplicación |
|---------|------|------------|
| 18.8 | Juntas especiales | Detallado en marcos |
| 18.10 | Muros especiales | Boundary elements |
| 15.4 | Resistencia de juntas | Cortante en conexiones |
| 25.4 | Desarrollo de refuerzo | Longitudes de anclaje |
| 21.2.4 | Factor φ sísmico | Reducción 0.75 |

---

*ACI 318-25 Sección 23.11*
