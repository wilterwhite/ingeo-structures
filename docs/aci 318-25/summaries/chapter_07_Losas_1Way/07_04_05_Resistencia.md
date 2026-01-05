# ACI 318-25 - 7.4-7.5 RESISTENCIA REQUERIDA Y DE DISENO

---

## 7.4 RESISTENCIA REQUERIDA

### 7.4.1 General

| Requisito | Referencia |
|-----------|------------|
| Combinaciones de carga | Capítulo 5 |
| Procedimientos de análisis | Capítulo 6 |
| Efectos de presfuerzo | 5.3.14 |

### 7.4.2 Momento Factorado

**7.4.2.1:** Para losas construidas integralmente con apoyos, Mu se permite calcular **en la cara del apoyo**.

### 7.4.3 Cortante Factorado

**7.4.3.1:** Para losas construidas integralmente con apoyos, Vu se permite calcular **en la cara del apoyo**.

**7.4.3.2:** Se permite diseñar para Vu en la **sección crítica** si se cumplen (a), (b) y (c):

| Condicion | Requisito |
|-----------|-----------|
| (a) | Reacción de apoyo introduce compresión en la losa |
| (b) | Cargas aplicadas en o cerca de la superficie superior |
| (c) | Sin carga concentrada entre cara de apoyo y sección crítica |

#### Seccion Critica para Cortante

| Tipo de Losa | Seccion Critica |
|--------------|-----------------|
| No presforzada | **d** desde la cara del apoyo |
| Presforzada | **h/2** desde la cara del apoyo |

---

## 7.5 RESISTENCIA DE DISENO

### 7.5.1 General

**7.5.1.1:** Para cada combinación de carga, en todas las secciones:
```
φSn >= U
```

Incluyendo:
- (a) **φMn >= Mu**
- (b) **φVn >= Vu**

**7.5.1.2:** Factores φ según **21.2**.

### 7.5.2 Momento

**7.5.2.1:** Calcular Mn según **22.3**.

**7.5.2.2:** Para losas presforzadas, tendones externos se consideran **no adheridos** para calcular resistencia a flexión (a menos que estén efectivamente adheridos).

**7.5.2.3:** Si refuerzo principal de flexión es paralelo al eje de viga T, proporcionar refuerzo perpendicular en la parte superior de la losa:
- (a) Diseñar para carga factorada en ancho de ala actuando como voladizo
- (b) Solo considerar ancho de ala efectivo según 6.3.2

**No aplica a construcción de viguetas.**

### 7.5.3 Cortante

**7.5.3.1:** Calcular Vn según **22.5**.

**7.5.3.2:** Para losas compuestas, calcular resistencia a cortante horizontal Vnh según **16.4**.

---

## Referencias para Calculo

| Parametro | Referencia |
|-----------|------------|
| Mn (momento nominal) | 22.3 |
| Vn (cortante nominal) | 22.5 |
| Vnh (cortante horizontal) | 16.4 |
| Factores φ | 21.2 |
| Ancho efectivo de ala | 6.3.2 |

---

*ACI 318-25 Secciones 7.4-7.5*
