# ACI 318-25 - 15.4-15.5 RESISTENCIA

---

## 15.4 RESISTENCIA REQUERIDA

### 15.4.1 General

| Requisito | Referencia |
|-----------|------------|
| Combinaciones de carga | Capitulo 5 |
| Procedimientos de analisis | Capitulo 6 |

### 15.4.2 Fuerzas en la Junta
Las juntas deben disenarse para resistir:
- Fuerzas axiales
- Cortantes
- Momentos
- Torsion (si aplica)

de los miembros que se conectan.

---

## 15.5 RESISTENCIA DE DISENO

### 15.5.1 General

**15.5.1.1** Para cada combinacion de carga:
```
φSn >= U
```

**15.5.1.2** Factor de reduccion φ segun **21.2**.

### 15.5.2 Cortante en Juntas Viga-Columna

#### 15.5.2.1 Resistencia Nominal al Cortante

Para juntas confinadas en las **cuatro caras** por vigas:
```
Vn = 20 * √fc' * Aj
```

Para juntas confinadas en **tres caras** o esquinas opuestas:
```
Vn = 15 * √fc' * Aj
```

Para **otras** juntas:
```
Vn = 12 * √fc' * Aj
```

Donde:
- **Aj** = area efectiva de la seccion transversal de la junta

#### 15.5.2.2 Area Efectiva Aj

```
Aj = bj * hc
```

Donde:
- **bj** = ancho efectivo de la junta
- **hc** = profundidad de la columna en direccion del cortante

#### 15.5.2.3 Ancho Efectivo bj

```
bj = menor de:
  (a) bc
  (b) bc/2 + Σ(menor de hv/2, c2)
  (c) bc/2 + Σ(x)
```

Donde:
- **bc** = ancho de columna perpendicular al cortante
- **hv** = peralte de la viga mas profunda
- **c2** = extension de columna mas alla de la viga
- **x** = extension de la viga mas alla de la columna

### 15.5.3 Cortante en Conexiones Losa-Columna

**15.5.3.1** Calcular cortante y momento segun **8.4.4**.

**15.5.3.2** Resistencia al cortante segun **22.6** (cortante bidireccional).

### 15.5.4 Factor de Reduccion

| Solicitacion | φ |
|--------------|---|
| Cortante en juntas | **0.85** |
| Aplastamiento | **0.65** |

---

## Resumen de Formulas - Cortante en Juntas

| Confinamiento | Vn |
|---------------|-----|
| 4 caras | **20*√fc'*Aj** |
| 3 caras u opuestas | **15*√fc'*Aj** |
| Otras | **12*√fc'*Aj** |

---

*ACI 318-25 Secciones 15.4-15.5*
