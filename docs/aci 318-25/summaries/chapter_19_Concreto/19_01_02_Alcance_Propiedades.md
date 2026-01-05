# 19.1-19.2 ALCANCE Y PROPIEDADES DE DISENO

## 19.1 Alcance

| Seccion | Aplicabilidad |
|---------|---------------|
| 19.1.1 | Propiedades del concreto para diseno y requisitos de durabilidad |
| 19.1.2 | Requisitos de durabilidad para lechada de tendones adheridos (19.4) |

---

## 19.2 Propiedades de Diseno del Concreto

### 19.2.1 Resistencia a Compresion Especificada (f'c)

#### Tabla 19.2.1.1 - Limites para f'c

| Aplicacion | f'c Minimo (psi) |
|------------|------------------|
| General | **2500** |
| Cimentaciones SDC A, B, C | **2500** |
| Cimentaciones residencial/utilidad ≤ 2 pisos, SDC D, E, F | **2500** |
| Cimentaciones SDC D, E, F (otras) | **3000** |
| Porticos de momento especiales | **3000** |
| Muros especiales con Grado 60 u 80 | **3000** |
| Muros especiales con Grado 100 | **5000** |
| Pilotes hincados prefabricados no presforzados | **4000** |
| Pilas perforadas (drilled shafts) | **4000** |
| Pilotes hincados prefabricados presforzados | **5000** |

#### 19.2.1.1(d) Concreto Liviano en Sistemas Sismicos
- f'c ≤ **5000 psi** para porticos especiales y muros especiales
- Excepcion: evidencia experimental de resistencia/tenacidad equivalente

#### 19.2.1.3 Edad de Ensayo
- Por defecto: **28 dias**
- Otra edad debe indicarse en documentos de construccion

#### 19.2.1.4 Miembros Pretensados
- f'ci ≥ **3000 psi**

---

### 19.2.2 Modulo de Elasticidad (Ec)

#### Formulas de Calculo

| Tipo de Concreto | Formula |
|------------------|---------|
| General (wc = 90-160 lb/ft³) | **Ec = wc^1.5 * 33 * √f'c** (psi) |
| Peso normal | **Ec = 57,000 * √f'c** (psi) |

#### Notas:
- Ec se define como pendiente de la linea desde 0 hasta 45% de f'c
- Mayor variabilidad en: concreto de alta resistencia (f'c > 8000 psi), liviano, y SCC
- Se permite especificar Ec basado en ensayos (19.2.2.2)

---

### 19.2.3 Modulo de Ruptura (fr)

```
fr = 7.5 * λ * √f'c     [Ec. 19.2.3.1]
```

Donde λ se determina segun **19.2.4**

---

### 19.2.4 Concreto Liviano - Factor λ

#### Tabla 19.2.4.1(a) - λ Basado en Densidad de Equilibrio

| wc (lb/ft³) | λ |
|-------------|---|
| ≤ 100 | **0.75** |
| 100 < wc ≤ 135 | **0.0075 * wc** (≤ 1.0) |
| > 135 | **1.0** |

#### Tabla 19.2.4.1(b) - λ Basado en Composicion de Agregados

| Tipo | Agregado Fino | Agregado Grueso | λ |
|------|---------------|-----------------|---|
| Todo liviano | ASTM C330 | ASTM C330 | **0.75** |
| Liviano, mezcla fina | C330 + C33 | ASTM C330 | 0.75 - 0.85 |
| Arena-liviano | ASTM C33 | ASTM C330 | **0.85** |
| Arena-liviano, mezcla gruesa | ASTM C33 | C330 + C33 | 0.85 - 1.0 |

#### Valores por Defecto
- 19.2.4.2: Se permite usar **λ = 0.75** para concreto liviano
- 19.2.4.3: **λ = 1.0** para concreto de peso normal

---

## Formulas de Diseno Comunes

### Factor β₁ (Bloque de Compresion)

| f'c (psi) | β₁ |
|-----------|-----|
| ≤ 4000 | **0.85** |
| 4000 < f'c < 8000 | 0.85 - 0.05*(f'c - 4000)/1000 |
| ≥ 8000 | **0.65** |

```
β₁ = 0.85 - 0.05 * (f'c - 4000)/1000
0.65 ≤ β₁ ≤ 0.85
```

### Densidad de Equilibrio
- Concreto liviano: **90 - 135 lb/ft³**
- Concreto peso normal: **> 135 lb/ft³** (tipicamente 145-150 lb/ft³)

---

*ACI 318-25 Secciones 19.1-19.2*
