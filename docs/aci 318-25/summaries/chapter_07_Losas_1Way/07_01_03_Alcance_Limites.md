# ACI 318-25 - 7.1-7.3 ALCANCE Y LIMITES DE DISENO

---

## 7.1 ALCANCE

Aplica al diseño de losas no presforzadas y presforzadas reforzadas para flexión en una dirección:
- (a) Losas sólidas
- (b) Losas sobre deck de acero no compuesto
- (c) Losas compuestas de elementos de concreto
- (d) Losas prefabricadas huecas (hollow-core)

**Nota:** Sistemas de viguetas unidireccionales se cubren en Capítulo 9.

---

## 7.2 GENERAL

### 7.2.1 Consideraciones de Diseño
Considerar efectos de:
- Cargas concentradas
- Aberturas en la losa
- Vacíos dentro de la losa

**Nota:** Losas 1-way con cargas concentradas pueden ser susceptibles a falla por punzonamiento y fluencia localizada.

---

## 7.3 LIMITES DE DISENO

### 7.3.1 Espesor Minimo de Losa

#### Tabla 7.3.1.1 - Espesor Minimo (Losas Solidas No Presforzadas)

| Condicion de Apoyo | h minimo |
|--------------------|----------|
| Simplemente apoyada | **ln/20** |
| Un extremo continuo | **ln/24** |
| Ambos extremos continuos | **ln/28** |
| En voladizo | **ln/10** |

**Nota:** Valores para concreto de peso normal y fy = 60,000 psi.

#### 7.3.1.1.1 Modificacion por fy

Para fy diferente de 60,000 psi, multiplicar por:
```
Factor = (0.4 + fy/100,000)
```

#### 7.3.1.1.2 Modificacion por Concreto Liviano

Para concreto liviano (wc = 90 a 115 lb/ft³), multiplicar por el **mayor** de:
- (a) **1.65 - 0.005*wc**
- (b) **1.09**

#### 7.3.1.2 Acabado de Piso
El espesor de acabado de concreto se puede incluir en h si:
- Se coloca monolíticamente, O
- Se diseña como compuesto según 16.4

---

### 7.3.2 Limites de Deflexion Calculada

| Condicion | Requisito |
|-----------|-----------|
| Losas no presforzadas que no cumplen 7.3.1 | Calcular deflexiones según 24.2 |
| Losas presforzadas | Calcular deflexiones según 24.2 |
| Losas compuestas que cumplen 7.3.1 | No calcular deflexiones post-compuesto |

---

### 7.3.3 Limite de Deformacion del Refuerzo

**7.3.3.1:** Losas no presforzadas deben ser **controladas por tension** según Tabla 21.2.2.

---

### 7.3.4 Limites de Esfuerzo en Losas Presforzadas

| Etapa | Referencia |
|-------|------------|
| Clasificacion (U, T, C) | 24.5.2 |
| Esfuerzos inmediatamente después de transferencia | 24.5.3 |
| Esfuerzos en cargas de servicio | 24.5.4 |

---

*ACI 318-25 Secciones 7.1-7.3*
