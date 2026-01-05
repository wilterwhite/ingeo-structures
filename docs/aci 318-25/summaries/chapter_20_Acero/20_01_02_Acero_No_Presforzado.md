# 20.1-20.2 ALCANCE Y ACERO NO PRESFORZADO

## 20.1 Alcance

| Seccion | Aplicabilidad |
|---------|---------------|
| 20.1.1 | Propiedades de materiales, propiedades de diseno, requisitos de durabilidad |
| 20.1.2 | Embedments (20.6) |

---

## 20.2 Barras y Alambres No Presforzados

### 20.2.1 Propiedades de Material

#### 20.2.1.1 Barras Deformadas
- Deben ser **deformadas**, excepto barras lisas permitidas en espirales

#### 20.2.1.2 Determinacion de fy
- **(a)** Metodo offset: **0.2%** segun ASTM A370
- **(b)** Metodo halt-of-force (punto de fluencia bien definido)

#### 20.2.1.3 Especificaciones ASTM para Barras Deformadas

| ASTM | Tipo | Notas |
|------|------|-------|
| **A615** | Acero al carbono | Uso general |
| **A706** | Acero de baja aleacion | Requiere Supplementary Requirements S1 |
| **A996** | Acero de eje y riel | Barras de riel deben ser Tipo R |
| **A955** | Acero inoxidable | Alta resistencia a corrosion |
| **A1035** | Acero bajo carbono-cromo | Alta resistencia (Grado 100, 120) |

**Nota:** Barras mayores a **No. 18 NO permitidas**

#### 20.2.1.4 Barras Lisas para Espirales
- ASTM A615, A706, A955, o A1035

#### 20.2.1.5 Mallas de Barras Soldadas
- ASTM A184 (barras A615 o A706)

#### 20.2.1.6 Barras con Cabeza (Headed Bars)
- ASTM A970, incluyendo **Clase HA** de Anexo A1

#### 20.2.1.7 Alambre y Malla Soldada

| ASTM | Tipo |
|------|------|
| **A1064** | Acero al carbono |
| **A1022** | Acero inoxidable |

**Tamanos de alambre deformado:**
- Permitidos: **D4 a D31**
- D31+: permitido si se trata como liso para desarrollo

**Espaciamiento maximo de intersecciones soldadas:**
- Malla deformada: **16"**
- Malla lisa: **12"**

---

### 20.2.2 Propiedades de Diseno

#### 20.2.2.1 Relacion Esfuerzo-Deformacion
```
Si εs < εy:  fs = Es * εs
Si εs ≥ εy:  fs = fy
```

#### 20.2.2.2 Modulo de Elasticidad
```
Es = 29,000,000 psi
```

#### 20.2.2.3-4 Resistencia de Fluencia para Diseno
- Basada en grado especificado
- No exceder valores de Tabla 20.2.2.4(a) y (b)

---

## Tabla 20.2.2.4(a) - Refuerzo Deformado No Presforzado

### Flexion, Fuerza Axial, Contraccion y Temperatura

| Aplicacion | fy/fyt Max (psi) | Barras ASTM |
|------------|------------------|-------------|
| **SMF** (porticos especiales) | 80,000 | A706 unicamente |
| **Muros especiales** | 100,000 | A706 unicamente |
| **Otros** | 100,000 | A615, A706, A955, A996, A1035 |

**Notas importantes:**
- [2] Refuerzo debe cumplir **20.2.2.5**
- [3] Barras en losas/vigas que pasan por muros especiales: cumplir 20.2.2.5
- [4] fy > 80,000 psi NO permitido para IMF y OMF resistiendo E

### Soporte Lateral de Barras Longitudinales / Confinamiento

| Aplicacion | fy/fyt Max (psi) | Barras ASTM |
|------------|------------------|-------------|
| Sistemas sismicos especiales | 100,000 | A615, A706, A955, A996, A1035 |
| Espirales | 100,000 | A615, A706, A955, A996, A1035 |
| Otros | 80,000 | A615, A706, A955, A996 |

### Cortante

| Aplicacion | fy/fyt Max (psi) | Barras ASTM |
|------------|------------------|-------------|
| **SMF** (porticos especiales) | 80,000 | A615, A706, A955, A996 |
| **Muros especiales** | 100,000 | A615, A706, A955, A996 |
| Espirales | 60,000 | A615, A706, A955, A996 |
| Friccion por cortante | 60,000 | A615, A706, A955, A996 |
| Estribos, ganchos, aros | 60,000 | A615, A706, A955, A996, A1035 |
| Malla soldada deformada | 80,000 | A1064, A1022 |

### Torsion

| Aplicacion | fy/fyt Max (psi) |
|------------|------------------|
| Longitudinal y transversal | **60,000** |

### Refuerzo de Anclaje

| Aplicacion | fy Max (psi) | ASTM |
|------------|--------------|------|
| SDC C, D, E, F | 80,000 | **A706 unicamente** |
| Otros | 80,000 | A615, A706, A955, A996 |

### Regiones con Metodo Puntal-Tensor

| Aplicacion | fy Max (psi) |
|------------|--------------|
| Tensores longitudinales | **80,000** |
| Otros | **60,000** |

---

## Tabla 20.2.2.4(b) - Refuerzo Espiral Liso No Presforzado

| Uso | Aplicacion | fy/fyt Max (psi) |
|-----|------------|------------------|
| Soporte lateral/confinamiento | Espirales sismicos especiales | **100,000** |
| Soporte lateral/confinamiento | Espirales | **100,000** |
| Cortante | Espirales | **60,000** |
| Torsion (vigas no presforzadas) | Espirales | **60,000** |

---

## 20.2.2.5 Refuerzo Longitudinal en Sistemas Sismicos Especiales

**Acero longitudinal resistiendo momento/axial por sismo:**

| Sistema | Grados Permitidos |
|---------|-------------------|
| **Muros especiales** | A706 Grado 60, 80, o **100** |
| **Porticos especiales (SMF)** | A706 Grado 60 o 80 |

---

## 20.2.2.6 Refuerzo de Anclaje en SDC C, D, E, F

- Debe cumplir **ASTM A706 Grado 60 o 80**

---

## Notas Importantes sobre Tabla 20.2.2.4(a)

| Nota | Descripcion |
|------|-------------|
| [1] | Incluye todos los componentes de muros especiales (vigas de acople, pilares) |
| [5] | Mallas de barras soldadas: solo A615 o A706 Grado 60 u 80 |
| [6] | A1064/A1022 NO permitidos en sistemas sismicos si la soldadura resiste esfuerzos |
| [7] | Fibras de acero para cortante: ASTM A820 segun 26.4.1.6.1 |
| [8] | Incluye diafragmas y cimentaciones con E en sistemas sismicos especiales |
| [9] | Cortante en SMF incluye estribos, ganchos, aros y espirales |
| [10] | Barras diagonales en vigas de acople: cumplir 20.2.2.5 |
| [11] | Refuerzo de anclaje: cumplir 20.2.2.6 |

---

*ACI 318-25 Secciones 20.1-20.2*
