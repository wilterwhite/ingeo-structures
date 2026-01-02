# ACI 318-25 - CAPITULO 19: CONCRETO - DISENO Y DURABILIDAD
## Resumen de Propiedades de Diseno y Requisitos de Durabilidad

---

## INDICE

- [19.1 Alcance](#191-alcance)
- [19.2 Propiedades de Diseno del Concreto](#192-propiedades-de-diseno-del-concreto)
- [19.3 Requisitos de Durabilidad del Concreto](#193-requisitos-de-durabilidad-del-concreto)
- [19.4 Requisitos de Durabilidad de Lechada](#194-requisitos-de-durabilidad-de-lechada)
- [Tipos de Cemento para Exposicion a Sulfatos](#tipos-de-cemento-para-exposicion-a-sulfatos)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 19.1 ALCANCE

### 19.1.1 Aplicabilidad
Este capitulo aplica al concreto, incluyendo:
- (a) Propiedades para diseno
- (b) Requisitos de durabilidad

### 19.1.2 Lechada para Tendones Adheridos
Requisitos de durabilidad para lechada segun **19.4**

---

## 19.2 PROPIEDADES DE DISENO DEL CONCRETO

### 19.2.1 Resistencia a Compresion Especificada

### Tabla 19.2.1.1 - Limites para f'c

| Aplicacion | f'c minimo (psi) |
|------------|------------------|
| General | 2500 |
| Cimentaciones SDC A, B, C | 2500 |
| Cimentaciones residenciales <= 2 pisos, SDC D, E, F | 2500 |
| Cimentaciones SDC D, E, F (otros) | 3000 |
| Marcos especiales a momento | 3000 |
| Muros estructurales especiales (refuerzo Grado 60 u 80) | 3000 |
| Muros estructurales especiales (refuerzo Grado 100) | 5000 |
| Pilotes prefabricados no pretensados, pozos excavados | 4000 |
| Pilotes prefabricados pretensados | 5000 |

**19.2.1.1(d)** Concreto liviano en marcos y muros especiales: **f'c <= 5000 psi** (a menos que se demuestre equivalencia experimental)

**19.2.1.3** f'c basado en ensayos a **28 dias** (a menos que se especifique otra edad)

**19.2.1.4** Para miembros pretensados: **f'ci >= 3000 psi**

### 19.2.2 Modulo de Elasticidad

**(a)** Para wc entre 90 y 160 lb/ft³:
```
Ec = wc^1.5 * 33 * sqrt(f'c)     [Ec. 19.2.2.1.a] (psi)
```

**(b)** Para concreto de peso normal:
```
Ec = 57,000 * sqrt(f'c)          [Ec. 19.2.2.1.b] (psi)
```

**19.2.2.2** Se permite especificar Ec basado en ensayos de mezclas a usar en obra

### 19.2.3 Modulo de Ruptura
```
fr = 7.5 * lambda * sqrt(f'c)    [Ec. 19.2.3.1]
```

### 19.2.4 Concreto Liviano - Factor lambda

### Tabla 19.2.4.1(a) - Valores de lambda Basados en Densidad de Equilibrio

| wc (lb/ft³) | lambda |
|-------------|--------|
| <= 100 | 0.75 |
| 100 < wc <= 135 | 0.0075*wc <= 1.0 |
| > 135 | 1.0 |

### Tabla 19.2.4.1(b) - Valores de lambda Basados en Composicion de Agregados

| Tipo de Concreto | Composicion | lambda |
|------------------|-------------|--------|
| Todo liviano | Fino: ASTM C330, Grueso: ASTM C330 | 0.75 |
| Liviano, mezcla fina | Fino: ASTM C330+C33, Grueso: ASTM C330 | 0.75 a 0.85 |
| Arena-liviano | Fino: ASTM C33, Grueso: ASTM C330 | 0.85 |
| Arena-liviano, mezcla gruesa | Fino: ASTM C33, Grueso: ASTM C330+C33 | 0.85 a 1.0 |

**19.2.4.2** Se permite usar **lambda = 0.75** para concreto liviano

**19.2.4.3** Para concreto de peso normal: **lambda = 1.0**

---

## 19.3 REQUISITOS DE DURABILIDAD DEL CONCRETO

### Tabla 19.3.1.1 - Categorias y Clases de Exposicion

| Categoria | Clase | Condicion |
|-----------|-------|-----------|
| **Congelamiento-Deshielo (F)** | F0 | No expuesto a ciclos de congelamiento-deshielo |
| | F1 | Expuesto con exposicion limitada al agua |
| | F2 | Expuesto con exposicion frecuente al agua |
| **Sulfatos (S)** | S0 | SO4²⁻ < 0.10% (suelo), < 150 ppm (agua) |
| | S1 | 0.10 <= SO4²⁻ < 0.20%, 150-1500 ppm o agua de mar |
| | S2 | 0.20 <= SO4²⁻ <= 2.00%, 1500-10,000 ppm |
| | S3 | SO4²⁻ > 2.00%, > 10,000 ppm |
| **Contacto con Agua (W)** | W0 | Seco en servicio |
| | W1 | Contacto con agua, baja permeabilidad no requerida |
| | W2 | Contacto con agua, baja permeabilidad requerida |
| **Corrosion (C)** | C0 | Seco o protegido de humedad |
| | C1 | Expuesto a humedad, sin cloruros externos |
| | C2 | Expuesto a humedad y cloruros externos |

### Tabla 19.3.2.1 - Requisitos por Clase de Exposicion

| Clase | w/cm max | f'c min (psi) | Requisitos Adicionales |
|-------|----------|---------------|------------------------|
| **F0** | N/A | 2500 | N/A |
| **F1** | 0.55 | 3500 | Aire incluido (Tabla 19.3.3.1) |
| **F2** | 0.45 | 4500 | Aire incluido (Tabla 19.3.3.1) |
| **S0** | N/A | 2500 | Sin restriccion de cemento |
| **S1** | 0.50 | 4000 | Cemento Tipo II, MS |
| **S2** | 0.45 | 4500 | Cemento Tipo V, HS |
| **S3 Opcion 1** | 0.45 | 4500 | Tipo V + puzolana/escoria |
| **S3 Opcion 2** | 0.40 | 5000 | Tipo V (expansion <= 0.040%) |
| **W0** | N/A | 2500 | Ninguno |
| **W1** | N/A | 2500 | 26.4.2.2(d) |
| **W2** | 0.50 | 4000 | 26.4.2.2(d) |
| **C0** | N/A | 2500 | Cl⁻ max: 1.00% (no pret.), 0.06% (pret.) |
| **C1** | N/A | 2500 | Cl⁻ max: 0.30% (no pret.), 0.06% (pret.) |
| **C2** | 0.40 | 5000 | Cl⁻ max: 0.15% (no pret.), 0.06% (pret.) |

*Cl⁻ = ion cloruro soluble en agua, % por masa de materiales cementicios*

### 19.3.3 Requisitos Adicionales - Congelamiento-Deshielo

### Tabla 19.3.3.1 - Contenido de Aire Total

| Tamano Maximo Nominal (in) | F1 (%) | F2 (%) |
|----------------------------|--------|--------|
| 3/8 | 6.0 | 7.5 |
| 1/2 | 5.5 | 7.0 |
| 3/4 | 5.0 | 6.0 |
| 1 | 4.5 | 6.0 |
| 1-1/2 | 4.5 | 5.5 |
| 2 | 4.0 | 5.0 |
| 3 | 3.5 | 4.5 |

**19.3.3.2** Muestreo segun ASTM C172, contenido de aire segun ASTM C231 o C173

### Tabla 19.3.3.3 - Contenido de Aire para Shotcrete

| Tipo | Ubicacion Muestreo | F1 (%) | F2 (%) | F2 y C2 (%) |
|------|-------------------|--------|--------|-------------|
| Mezcla humeda | Antes de colocacion | 5.0 | 6.0 | 6.0 |
| Mezcla seca | En sitio | N/A | N/A | 4.5 |

**19.3.3.6** Para f'c >= 5000 psi: se permite reducir contenido de aire en **1.0%**

### 19.3.4 Requisitos Adicionales - Cloruros

**19.3.4.1** Concreto no pretensado colado contra encofrado de acero galvanizado permanente: cumplir limites de Clase C1 (a menos que se requiera limite mas estricto)

---

## 19.4 REQUISITOS DE DURABILIDAD DE LECHADA

### 19.4.1 Contenido de Ion Cloruro
Lechada para tendones adheridos:
```
Cl⁻ <= 0.06% (por masa de materiales cementicios)
```
Ensayar segun ASTM C1218

---

## TIPOS DE CEMENTO PARA EXPOSICION A SULFATOS

| Clase | ASTM C150 | ASTM C595 | ASTM C1157 |
|-------|-----------|-----------|------------|
| S1 | Tipo II | (MS) | MS |
| S2 | Tipo V | (HS) | HS |
| S3 | Tipo V + puzolana/escoria | (HS) + puzolana/escoria | HS + puzolana/escoria |

**Notas:**
- Para agua de mar, se permite C3A hasta 10% si w/cm <= 0.40
- Tipo I o III permitido si C3A < 8% (S1) o < 5% (S2)

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Proporcionamiento de mezclas | 26.4.3 |
| Ensayos y aceptacion | 26.12.3 |
| Recubrimiento (Clase C2) | 20.5.1.4 |
| Propiedades del refuerzo | Capitulo 20 |
| Factores phi | 21.2 |
| Evaluacion reactividad alcali | ASTM C1778 |

---

*Resumen del ACI 318-25 Capitulo 19 para propiedades de diseno y durabilidad del concreto.*
*Fecha: 2025*
