# ACI 318-25 - 8.4-8.5 RESISTENCIA REQUERIDA Y DE DISENO

---

## 8.4 RESISTENCIA REQUERIDA

### 8.4.1 General

| Requisito | Referencia |
|-----------|------------|
| Combinaciones de carga | Capitulo 5 |
| Procedimientos de analisis | Capitulo 6 |
| Efectos de presfuerzo | 5.3.14 |

### 8.4.2 Metodos de Analisis

| Metodo | Condiciones de Uso |
|--------|-------------------|
| Metodo Directo (8.8) | Cumple limitaciones 8.8.1.1 |
| Marco Equivalente (8.9) | Cualquier sistema |
| Analisis elastico | Segun Capitulo 6 |
| Analisis no lineal | Segun Apendice A |

### 8.4.3 Momento Factorado

**8.4.3.1:** Para losas construidas integralmente con apoyos:
```
Mu se permite calcular en la cara del apoyo
```

### 8.4.4 Cortante Factorado

**8.4.4.1:** Disenar para el **mayor** de:
- (a) Cortante unidireccional (viga ancha)
- (b) Cortante bidireccional (punzonamiento)

**8.4.4.2:** Secciones criticas:

| Tipo | Seccion Critica |
|------|-----------------|
| Unidireccional | **d** desde cara de apoyo |
| Bidireccional | Perimetro a **d/2** de columna/carga |

---

## 8.5 RESISTENCIA DE DISENO

### 8.5.1 General

**8.5.1.1:** Para cada combinacion de carga:
```
φSn >= U
```

Incluyendo:
- (a) **φMn >= Mu**
- (b) **φVn >= Vu**

**8.5.1.2:** Factores φ segun **21.2**.

### 8.5.2 Momento

**8.5.2.1:** Calcular Mn segun **22.3**.

**8.5.2.2:** Ancho efectivo para ala en tension:
- Ancho de viga + espesor de losa a cada lado
- No exceder 1/10 del claro

**8.5.2.3:** Para losas presforzadas, tendones externos se consideran **no adheridos**.

### 8.5.3 Cortante

**8.5.3.1:** Cortante unidireccional segun **22.5**.

**8.5.3.2:** Cortante bidireccional segun **22.6**.

### 8.5.4 Cortante y Momento Combinados

**8.5.4.1:** Transferencia de momento en conexiones losa-columna:

| Parametro | Formula |
|-----------|---------|
| Fraccion por flexion | γf = 1 / (1 + (2/3)*√(b1/b2)) |
| Fraccion por cortante | γv = 1 - γf |

**8.5.4.2:** Ancho efectivo para momento:
- El menor de:
  - (a) c2 + 3h (columnas interiores)
  - (b) c2 + 1.5h + cT (columnas de borde)
  - (c) Ancho de banda de columna

### 8.5.4.3 Esfuerzo de Cortante

```
vu = Vu/(bo*d) ± γv*Mu*c/(Jc)
```

Donde:
- **bo** = perimetro de seccion critica
- **Jc** = propiedad de seccion critica analogia a momento polar de inercia

---

## Resumen de Referencias

| Parametro | Seccion |
|-----------|---------|
| Mn (momento nominal) | 22.3 |
| Vn unidireccional | 22.5 |
| Vn bidireccional | 22.6 |
| Factores φ | 21.2 |
| Metodo directo | 8.8 |
| Marco equivalente | 8.9 |

---

*ACI 318-25 Secciones 8.4-8.5*
