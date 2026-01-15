# ACI 318-25 - Secciones 23.9-23.10: NODAL ZONES

---

## 23.9 RESISTENCIA DE NODAL ZONES

### 23.9.1 Resistencia Nominal

```
Fnn = fce * Anz     [Ec. 23.9.1]
```

Donde:
- **Fnn** = Resistencia nominal del nodal zone
- **fce** = Resistencia efectiva del concreto
- **Anz** = Area efectiva del nodal zone

**Criterio de aceptacion:**

```
phi * Fnn >= Fun

Donde phi = 0.75
```

---

### 23.9.2 Resistencia Efectiva del Concreto

```
fce = 0.85 * beta_c * beta_n * fc'     [Ec. 23.9.2]
```

Donde:
- **fc'** = Resistencia a compresion del concreto (psi)
- **beta_c** = Factor de confinamiento (1.0 a 2.0)
- **beta_n** = Coeficiente del nodal zone (0.6 a 1.0)

---

### 23.9.2 Coeficiente del Nodal Zone (beta_n)

**Tabla 23.9.2:**

| Tipo de Nodo | Configuracion | beta_n |
|--------------|---------------|--------|
| **C-C-C** | Zone bounded por struts y/o bearing surfaces | **1.0** |
| **C-C-T** | Zone anclando **1 tie** | **0.80** |
| **C-T-T** | Zone anclando **2 o mas ties** | **0.60** |

**Ilustracion:**

```
C-C-C (beta_n = 1.0):       C-C-T (beta_n = 0.80):      C-T-T (beta_n = 0.60):

    Strut                       Strut                       Strut
      \                           \                           |
       \                           \                          |
        o----Strut                  o----Tie                  o----Tie
       /                           /                          |
      /                           /                           |
    Strut                       Strut                       Tie
```

---

### 23.9.3 Factor de Confinamiento (beta_c)

Mismo que para struts (Tabla 23.4.3(b)):

| Ubicacion | beta_c |
|-----------|--------|
| Superficie de bearing | sqrt(A2/A1) <= **2.0** |
| Sin confinamiento especial | **1.0** |

---

### 23.9.4 Area del Nodal Zone

El area **Anz** es el menor de:

| Opcion | Definicion |
|--------|------------|
| (a) | Area perpendicular a la linea de accion de Fus |
| (b) | Area de seccion perpendicular a la resultante de fuerzas |

**Extended Nodal Zone:**

```
Delimitada por:
- Ancho del strut (ws)
- Ancho del tie (wt)
- Geometria del apoyo/bearing
```

---

### 23.9.5 Nodos Hidrostaticos

Para nodos **hidrostaticos**, las proporciones de los lados son proporcionales a las fuerzas:

```
ws1 / Fs1 = ws2 / Fs2 = ws3 / Fs3
```

**Ventaja:** Esfuerzo uniforme en todas las caras.

---

## 23.10 CURVED-BAR NODES

### 23.10.1 Aplicabilidad

Aplica cuando el tie se ancla mediante curvas (bends) en lugar de desarrollo recto.

Usos tipicos:
- Esquinas de marcos
- Conexiones viga-columna
- Zonas de anclaje

---

### 23.10.2 Radio Minimo de Curvatura

**Para clear cover >= 1.5*db (23.10.2a, 23.10.2b):**

**Bends menores de 180°:**

```
rb >= (2 * Ats * fy) / (bs * fc')     [Ec. 23.10.2a]
```

**Bends de 180° (U-bends):**

```
rb >= (Ats * fy) / (wt * fc')     [Ec. 23.10.2b]
```

**Limite inferior (segun 25.3):**

```
rb >= db(min) / 2
```

Donde:
- **rb** = Radio de curvatura interior (in)
- **Ats** = Area del tie (in²)
- **fy** = Esfuerzo de fluencia (psi)
- **bs** = Ancho del strut o nodal zone (in)
- **wt** = Ancho efectivo del tie (in)
- **fc'** = Resistencia del concreto (psi)

---

### 23.10.3 Correccion por Recubrimiento Reducido

**Para clear cover < 1.5*db:**

```
rb(corregido) = rb(calculado) * (1.5 * db / cc)     [Ec. 23.10.3]
```

Donde:
- **cc** = Clear cover al lado normal al plano del bend (in)

---

### 23.10.4 Radios Minimos por Tabla 25.3

| Diametro de Barra | Radio Minimo Interior |
|-------------------|----------------------|
| No. 3 a No. 8 | **3 * db** |
| No. 9, 10, 11 | **4 * db** |
| No. 14, 18 | **5 * db** |

---

### 23.10.5 Ubicacion del Centro de Curvatura

**Requisito critico:**

```
El centro de curvatura DEBE estar DENTRO
del nodal zone (zona sombreada permitida)
```

**En esquinas de marcos:**

```
      |      |
      |  rb  |
      |  o<--|-- Centro de curvatura debe estar
      |______|   dentro de la junta (shaded area)
     /
    / Diagonal strut
   /
```

---

## RESUMEN DE COEFICIENTES NODAL ZONES

### Valores Tipicos de fce para Nodal Zones

Para fc' = 4000 psi, sin confinamiento (beta_c = 1.0):

| Tipo de Nodo | beta_n | fce (psi) |
|--------------|--------|-----------|
| C-C-C | 1.0 | **3,400** |
| C-C-T | 0.80 | **2,720** |
| C-T-T | 0.60 | **2,040** |

```
fce = 0.85 * 1.0 * beta_n * 4000
```

### Comparacion de Resistencias

| Elemento | beta | fce (fc'=4000 psi) |
|----------|------|-------------------|
| Nodo C-C-C | 1.0 | 3,400 psi |
| Nodo C-C-T | 0.80 | 2,720 psi |
| Strut boundary | 1.0 | 3,400 psi |
| Strut interior | 0.75 | 2,550 psi |
| Nodo C-T-T | 0.60 | 2,040 psi |
| Strut en tension zone | 0.40 | 1,360 psi |

---

## EJEMPLO DE VERIFICACION DE NODO

**Datos:**
- Nodo C-C-T (anclando 1 tie)
- fc' = 4000 psi
- Sin confinamiento (beta_c = 1.0)
- Area del nodo Anz = 150 in²
- Fuerza factorizada Fun = 300 kips

**Calculo:**

1. **Resistencia efectiva:**
   ```
   fce = 0.85 * 1.0 * 0.80 * 4000 = 2,720 psi
   ```

2. **Resistencia nominal:**
   ```
   Fnn = fce * Anz = 2,720 * 150 = 408,000 lb = 408 kips
   ```

3. **Resistencia de diseno:**
   ```
   phi * Fnn = 0.75 * 408 = 306 kips
   ```

4. **Verificacion:**
   ```
   phi * Fnn = 306 kips >= Fun = 300 kips  OK
   ```

---

*ACI 318-25 Secciones 23.9-23.10*
