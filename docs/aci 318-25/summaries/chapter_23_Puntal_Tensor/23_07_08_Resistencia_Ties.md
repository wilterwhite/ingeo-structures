# ACI 318-25 - Secciones 23.7-23.8: RESISTENCIA DE TIES

---

## 23.7 RESISTENCIA DE TIES

### 23.7.1 Requisito General

El refuerzo del tie debe satisfacer:

```
phi * Fnt >= Fut
```

Donde:
- **phi = 0.75** (factor de reduccion)
- **Fnt** = Resistencia nominal del tie
- **Fut** = Fuerza factorizada del tie

### 23.7.2 Resistencia Nominal del Tie

```
Fnt = Ats * fy + Atp * Delta_fp     [Ec. 23.7.2]
```

Donde:
- **Ats** = Area de refuerzo no-pretensado (in²)
- **Atp** = Area de refuerzo pretensado (in²)
- **fy** = Esfuerzo de fluencia del acero no-pretensado (psi)
- **Delta_fp** = Incremento de esfuerzo en pretensado (psi)

---

### 23.7.3 Incremento de Esfuerzo en Pretensado

| Tipo de Pretensado | Delta_fp Tipico | Limite |
|--------------------|-----------------|--------|
| **Bonded** (adherido) | 60,000 psi | (fpy - fse) |
| **Unbonded** (no adherido) | 10,000 psi | (fpy - fse) |

Donde:
- **fpy** = Esfuerzo de fluencia del acero de pretensado
- **fse** = Esfuerzo efectivo en pretensado (despues de perdidas)

**Nota:** Para acero de pretensado tipico (270 ksi):
- fpy ≈ 243 ksi (0.9 x fpu)
- fse ≈ 160-180 ksi (tipico despues de perdidas)

---

## 23.8 DETALLES DE REFUERZO EN TIES

### 23.8.1 Ancho Efectivo del Tie

**Para una capa de barras:**

```
wt = db + 2 * c     [Ec. 23.8.1]
```

Donde:
- **db** = Diametro de la barra (in)
- **c** = Recubrimiento al acero (in)

**Limite superior (condicion hidrostatica):**

```
wt,max = Fnt / (fce * bs)
```

Donde:
- **bs** = Ancho del nodal zone perpendicular al tie (in)

---

### 23.8.2 Distribucion del Refuerzo

| Requisito | Especificacion |
|-----------|----------------|
| Concentracion | Centrado en el eje del tie |
| Ancho maximo | wt <= ancho de la extended nodal zone |
| Capas multiples | Incluir todas las barras dentro de wt |

---

### 23.8.3 Desarrollo del Refuerzo

**Punto critico para desarrollo:**

```
Donde el centroide del tie SALE de la extended nodal zone
```

**Longitud de ancaje disponible (lanc):**

Se mide desde el punto critico hacia el interior del nodal zone.

### 23.8.4 Metodos de Ancaje

| Metodo | Referencia | Aplicacion |
|--------|------------|------------|
| Desarrollo recto | 25.4 | Longitud suficiente disponible |
| Gancho estandar (90°, 180°) | 25.4.3 | Espacio limitado |
| Dispositivo mecanico | Per. fabricante | Alta fuerza en poco espacio |
| Anclaje de post-tensado | Per. fabricante | Cables de pretensado |

---

### 23.8.5 Longitud de Desarrollo

**Para barras rectas (segun 25.4):**

```
ld = (fy * psi_t * psi_e * psi_s * psi_g) / (25 * lambda * sqrt(fc')) * db
```

**Para ganchos estandar (segun 25.4.3):**

```
ldh = (0.02 * psi_e * fy) / (lambda * sqrt(fc')) * db
```

**Factores de modificacion:**
- **psi_t** = Factor de ubicacion (1.0 o 1.3)
- **psi_e** = Factor de epoxi (1.0 o 1.2)
- **psi_s** = Factor de tamano (1.0 o 0.8)
- **psi_g** = Factor de grado (1.0 a 1.15)
- **lambda** = Factor de concreto liviano (0.75 a 1.0)

---

### 23.8.6 Confinamiento de Ganchos

**Requisito (23.8.5):**

```
Los ganchos deben estar confinados por refuerzo
para evitar splitting del concreto
```

Tipicamente se logra con:
- Estribos cerrados alrededor de los ganchos
- Refuerzo transversal en la zona del gancho

---

### 23.8.7 Ancaje en Corbels y Mensulas

**Atencion especial requerida en:**
- Nodal zones de corbels
- Nodal zones adyacentes a apoyos exteriores de deep beams

**Usar longitud de ancaje (lanc):**
- Medida dentro de la extended nodal zone
- Desde el punto critico de desarrollo

---

## EJEMPLO DE DISENO DE TIE

**Datos:**
- Fut = 200 kips (fuerza factorizada)
- fy = 60 ksi
- fc' = 4000 psi
- Recubrimiento c = 2 in
- phi = 0.75

**Calculo:**

1. **Area de acero requerida:**
   ```
   Ats,req = Fut / (phi * fy)
           = 200 / (0.75 * 60)
           = 4.44 in²
   ```

2. **Seleccion de barras:**
   ```
   Usar: 6 - #8 (As = 6 x 0.79 = 4.74 in²)  OK
   ```

3. **Ancho efectivo del tie:**
   ```
   wt = db + 2*c = 1.0 + 2*2.0 = 5.0 in
   ```

4. **Verificar desarrollo:**
   ```
   Longitud disponible vs. ld requerida
   Si lanc < ld: usar ganchos o dispositivos mecanicos
   ```

---

## RESUMEN DE REQUISITOS

| Parametro | Requisito |
|-----------|-----------|
| phi | **0.75** |
| Resistencia | Fnt = Ats*fy + Atp*Delta_fp |
| Ancho efectivo | wt = db + 2c |
| Desarrollo | Desde salida de extended nodal zone |
| Ancaje | Per. Cap. 25.4 o dispositivos mecanicos |
| Confinamiento | Ganchos deben estar confinados |

---

*ACI 318-25 Secciones 23.7-23.8*
