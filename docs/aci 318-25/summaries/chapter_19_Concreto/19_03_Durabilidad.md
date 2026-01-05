# 19.3 REQUISITOS DE DURABILIDAD DEL CONCRETO

## 19.3.1 Categorias y Clases de Exposicion

### Tabla 19.3.1.1 - Categorias y Clases de Exposicion

#### Categoria F - Congelamiento y Deshielo

| Clase | Condicion |
|-------|-----------|
| **F0** | No expuesto a ciclos de congelamiento-deshielo |
| **F1** | Expuesto con **exposicion limitada** al agua |
| **F2** | Expuesto con **exposicion frecuente** al agua |

**Nota:** Clase F3 eliminada en ACI 318-25 (redundante con F2+C2)

#### Categoria S - Sulfatos

| Clase | SO₄²⁻ en Suelo (% masa) | SO₄²⁻ en Agua (ppm) |
|-------|-------------------------|---------------------|
| **S0** | < 0.10 | < 150 |
| **S1** | 0.10 - 0.20 | 150 - 1500 o agua de mar |
| **S2** | 0.20 - 2.00 | 1500 - 10,000 |
| **S3** | > 2.00 | > 10,000 |

- Sulfatos en suelo: **ASTM C1580**
- Sulfatos en agua: **ASTM D516**

#### Categoria W - Contacto con Agua

| Clase | Condicion |
|-------|-----------|
| **W0** | Concreto seco en servicio |
| **W1** | En contacto con agua, **baja permeabilidad NO requerida** |
| **W2** | En contacto con agua, **baja permeabilidad requerida** |

#### Categoria C - Proteccion Contra Corrosion

| Clase | Condicion |
|-------|-----------|
| **C0** | Seco o protegido de humedad |
| **C1** | Expuesto a humedad pero **NO a cloruros externos** |
| **C2** | Expuesto a humedad **Y cloruros externos** (deshielo, sal, agua de mar) |

---

## 19.3.2 Requisitos para Mezclas de Concreto

### Tabla 19.3.2.1 - Requisitos por Clase de Exposicion

#### Exposicion a Congelamiento-Deshielo (F)

| Clase | w/cm Max | f'c Min (psi) | Aire |
|-------|----------|---------------|------|
| F0 | N/A | 2500 | N/A |
| F1 | **0.55** | **3500** | Tabla 19.3.3.1 |
| F2 | **0.45** | **4500** | Tabla 19.3.3.1 |

#### Exposicion a Sulfatos (S)

| Clase | w/cm Max | f'c Min | Cemento ASTM C150 | Cemento ASTM C595 | Cemento ASTM C1157 |
|-------|----------|---------|-------------------|-------------------|---------------------|
| S0 | N/A | 2500 | Sin restriccion | Sin restriccion | Sin restriccion |
| S1 | **0.50** | **4000** | Tipo II | (MS) | MS |
| S2 | **0.45** | **4500** | Tipo V | (HS) | HS |
| S3 Op.1 | **0.45** | **4500** | V + puzolana/escoria | (HS) + puz/esc | HS + puz/esc |
| S3 Op.2 | **0.40** | **5000** | V (0.040% max exp) | (HS) | HS |

**Notas:**
- Para agua de mar: cemento con C₃A ≤ 10% permitido si w/cm ≤ 0.40
- Cloruro de calcio: **No permitido** en S2 y S3

#### Exposicion a Agua (W)

| Clase | w/cm Max | f'c Min (psi) | Requisitos Adicionales |
|-------|----------|---------------|------------------------|
| W0 | N/A | 2500 | Ninguno |
| W1 | N/A | 2500 | 26.4.2.2(d) - reactividad alcali |
| W2 | **0.50** | **4000** | 26.4.2.2(d) - reactividad alcali |

#### Exposicion a Corrosion (C)

| Clase | w/cm Max | f'c Min (psi) | Cl⁻ Max (No Pret.) | Cl⁻ Max (Pret.) |
|-------|----------|---------------|--------------------|--------------------|
| C0 | N/A | 2500 | **1.00%** | **0.06%** |
| C1 | N/A | 2500 | **0.30%** | **0.06%** |
| C2 | **0.40** | **5000** | **0.15%** | **0.06%** |

**Notas:**
- Cloruros como % de masa de materiales cementantes
- C2 requiere recubrimiento segun **20.5.1.4**
- Concreto simple en C2: puede usar w/cm ≤ 0.45, f'c ≥ 4500 psi

---

## 19.3.3 Requisitos Adicionales para Congelamiento-Deshielo

### Tabla 19.3.3.1 - Contenido de Aire para Concreto

| Tamano Max. Agregado (in) | F1 (%) | F2 (%) |
|---------------------------|--------|--------|
| 3/8 | 6.0 | 7.5 |
| 1/2 | 5.5 | 7.0 |
| 3/4 | 5.0 | 6.0 |
| 1 | 4.5 | 6.0 |
| 1-1/2 | 4.5 | 5.5 |
| 2 | 4.0 | 5.0 |
| 3 | 3.5 | 4.5 |

### Tabla 19.3.3.3 - Contenido de Aire para Shotcrete

| Tipo | Muestreo | F1 (%) | F2 (%) | F2+C2 (%) |
|------|----------|--------|--------|-----------|
| Shotcrete mezcla humeda | Antes de colocacion | 5.0 | 6.0 | 6.0 |
| Shotcrete mezcla seca | En sitio | N/A | N/A | 4.5 |

### 19.3.3.6 Reduccion de Aire
- Para **f'c ≥ 5000 psi**: se permite reducir **1.0%** del contenido de aire

### Metodos de Muestreo y Ensayo
- Muestreo: **ASTM C172**
- Contenido de aire: **ASTM C231** (peso normal) o **ASTM C173** (todos)

---

## 19.3.4 Requisitos de Cloruros

### 19.3.4.1 Formas Galvanizadas
- Concreto no presforzado contra formas galvanizadas: usar limite C1 (**0.30%**)
- O limite mas estricto si otras condiciones lo requieren

---

## 19.4 Requisitos de Durabilidad de Lechada

### 19.4.1 Lechada para Tendones Adheridos
- Cloruro soluble en agua ≤ **0.06%** (por masa de cementantes)
- Ensayo: **ASTM C1218**

---

## Ejemplos de Miembros por Clase F

| Clase | Ejemplos |
|-------|----------|
| F0 | Interiores, cimentaciones bajo linea de helada, climas sin heladas |
| F1 | Muros exteriores, vigas, losas no en contacto con suelo |
| F2 | Losas elevadas exteriores, muros con acumulacion de nieve/hielo |

---

## Tipos de Cemento para Resistencia a Sulfatos

| Resistencia | ASTM C150 | C₃A Max |
|-------------|-----------|---------|
| Moderada | Tipo II | 8% |
| Alta | Tipo V | 5% |
| Muy alta | Tipo V + 0.040% max exp | < 5% |

---

*ACI 318-25 Seccion 19.3-19.4*
