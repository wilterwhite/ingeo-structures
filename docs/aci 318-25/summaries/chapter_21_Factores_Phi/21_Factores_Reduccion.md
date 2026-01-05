# 21 FACTORES DE REDUCCION DE RESISTENCIA (φ)

## 21.1 Alcance

Los factores de reduccion φ tienen como proposito:
1. Contabilizar probabilidad de miembros sub-resistentes (variaciones en materiales y dimensiones)
2. Contabilizar inexactitudes en ecuaciones de diseno
3. Reflejar ductilidad disponible y confiabilidad requerida
4. Reflejar importancia del miembro en la estructura

---

## 21.2.1 Tabla 21.2.1 - Factores de Reduccion φ

### Acciones Basicas

| Accion | φ | Excepciones |
|--------|---|-------------|
| **(a) Momento, axial, o combinado** | 0.65 - 0.90 | Segun 21.2.2; cerca de extremos pretensados: 21.2.3 |
| **(b) Cortante** | **0.75** | Requisitos adicionales en 21.2.4 para sismo |
| **(c) Torsion** | **0.75** | — |
| **(d) Aplastamiento** | **0.65** | — |

### Elementos Estructurales

| Elemento | φ |
|----------|---|
| **(e) Mensulas y corbels** | **0.75** |
| **(f) Concreto simple** | **0.60** |
| **(g) Puntal-tensor (puntales, tensores, nodos, aplastamiento)** | **0.75** |

### Condiciones de Anclaje

| Condicion | φ |
|-----------|---|
| **(h) Zonas de anclaje post-tensado** | **0.85** |
| **(i) Conexiones prefabricado (fluencia acero en tension)** | **0.90** |
| **(j) Anclaje barras - resistencia breakout grupos** | **0.75** |
| **(k) Refuerzo de anclaje (17.5.2.1)** | **0.90** |

### Falla de Concreto en Anclajes

| Tipo | φ |
|------|---|
| **(l) Tension, no redundante** | **0.65** |
| **(m) Tension, redundante** | **0.75** |
| **(n) Cortante** | **0.75** |

### Acero de Anclajes

| Tipo | Ductil | No Ductil |
|------|--------|-----------|
| **(o)/(p) Tension** | **0.75** | **0.65** |
| **(q)/(r) Cortante** | **0.65** | **0.60** |

**Notas:**
- [1] Componentes de anclaje: perno o manguito
- [2] Ductilidad segun ACI CODE-355.2 o ACI CODE-355.4

---

## 21.2.2 Factor φ para Momento y/o Axial

### Deformacion Unitaria de Fluencia (εty)

| Tipo de Refuerzo | εty |
|------------------|-----|
| Deformado Grado 60 | **0.002** (permitido) |
| Deformado (general) | **fy / Es** |
| Presforzado (todos) | **0.002** |

### Tabla 21.2.2 - Factor φ Segun Deformacion Neta εt

| Deformacion εt | Clasificacion | φ (Espirales) | φ (Otros) |
|----------------|---------------|---------------|-----------|
| εt ≤ εty | **Controlado por compresion** | **0.75** | **0.65** |
| εty < εt < εty + 0.003 | **Transicion** | 0.75 + 0.15*(εt - εty)/0.003 | 0.65 + 0.25*(εt - εty)/0.003 |
| εt ≥ εty + 0.003 | **Controlado por tension** | **0.90** | **0.90** |

**Nota:** Para secciones en transicion, se permite usar φ de compresion controlada.

### Formulas de Transicion

**Con espirales (25.7.3):**
```
φ = 0.75 + 0.15 * (εt - εty) / 0.003
```

**Con otros (estribos):**
```
φ = 0.65 + 0.25 * (εt - εty) / 0.003
```

### 21.2.2.3 Miembros No Presforzados con M + P

Para **0.1 f'c Ag ≤ Pn ≤ Pn,bal**:
- φ de Tabla 21.2.2 **no debe exceder** interpolacion lineal entre:
  - 0.90 en 0.1 f'c Ag
  - φcc en Pn,bal

---

## 21.2.3 Extremos de Miembros Pretensados

### Longitud de Transferencia
```
ℓtr = (fse / 3000) * db     [Ec. 21.2.3]
```

### Tabla 21.2.3 - Factor φ Cerca de Extremos Pretensados

#### Todos los Torones Adheridos

| Distancia desde Extremo | φ |
|-------------------------|---|
| ≤ ℓtr | **0.75** |
| ℓtr a ℓd | Interpolacion lineal: 0.75 a φp |

#### Uno o Mas Torones Desadheridos

| Esfuerzo en Servicio | Distancia | φ |
|----------------------|-----------|---|
| **Sin tension** | ≤ (ℓdb + ℓtr) | **0.75** |
| | (ℓdb + ℓtr) a (ℓdb + ℓd) | Interpolacion: 0.75 a φp |
| **Con tension** | ≤ (ℓdb + ℓtr) | **0.75** |
| | (ℓdb + ℓtr) a (ℓdb + 2ℓd) | Interpolacion: 0.75 a φp |

**Donde:**
- ℓdb = longitud desadherida
- ℓd = longitud de desarrollo (25.4.8.1)
- φp = φ donde todos los torones estan desarrollados

---

## 21.2.4 Modificaciones para Efectos Sismicos

### Aplica a estructuras con:
- (a) Porticos especiales de momento (SMF)
- (b) Muros especiales estructurales
- (c) Muros intermedios prefabricados en SDC D, E, F

### 21.2.4.1 Miembros Controlados por Cortante
**φ = 0.60** si:
- Resistencia nominal a cortante < cortante correspondiente al desarrollo de Mn
- **Excepcion:** No aplica si Ωv ≥ 1.5 o si ωvΩv = Ωo

### 21.2.4.2 Diafragmas
- φ para cortante ≤ **menor φ de componentes verticales** del SFRS

### 21.2.4.3 Elementos de Cimentacion
- φ para cortante ≤ **menor φ de componentes verticales** del SFRS

### 21.2.4.4 Nudos SMF y Vigas de Acople Diagonales
- **φ = 0.85** para cortante

---

## 21.2.5 Grupos de Barras en SFRS

Para grupos de barras gobernados por **breakout del concreto** en sistemas sismo-resistentes:
- **φ = 0.65** para tension

---

## Resumen Rapido de Factores φ

| Accion | φ Normal | φ Sismico |
|--------|----------|-----------|
| Flexion (tension controlada) | 0.90 | 0.90 |
| Flexion (compresion, espirales) | 0.75 | 0.75 |
| Flexion (compresion, estribos) | 0.65 | 0.65 |
| Cortante | 0.75 | 0.60-0.85 |
| Torsion | 0.75 | 0.75 |
| Aplastamiento | 0.65 | 0.65 |
| Puntal-tensor | 0.75 | 0.75 |
| Concreto simple | 0.60 | 0.60 |

---

## Valores de εty por Grado

| Grado | fy (psi) | εty = fy/Es |
|-------|----------|-------------|
| 40 | 40,000 | 0.00138 |
| 60 | 60,000 | **0.00207** |
| 80 | 80,000 | 0.00276 |
| 100 | 100,000 | 0.00345 |

**Limite tension controlada:** εt ≥ εty + 0.003

| Grado | εt min (tension controlada) |
|-------|----------------------------|
| 60 | 0.00507 |
| 80 | 0.00576 |
| 100 | 0.00645 |

---

*ACI 318-25 Capitulo 21*
