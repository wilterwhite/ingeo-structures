# ACI 318-25 - 8.10 REFUERZO DE CORTANTE BIDIRECCIONAL

---

## 8.10.1 Tipos de Refuerzo de Cortante

| Tipo | Descripcion |
|------|-------------|
| (a) Barras individuales o mallas de alambre | Segun 22.6.8 |
| (b) Conectores de cortante tipo perno (studs) | Segun 22.6.9 |
| (c) Cabezales de cortante (shearheads) | Segun 22.6.10 |

---

## 8.10.2 Seccion Critica

### 8.10.2.1 Sin Refuerzo de Cortante
Perimetro a **d/2** de la cara del area cargada o columna.

### 8.10.2.2 Con Barras o Mallas
Perimetro a **d/2** del refuerzo mas externo.

### 8.10.2.3 Con Studs
Perimetro a **d/2** del ultimo perno.

### 8.10.2.4 Geometria de la Seccion Critica

| Tipo de Columna | Forma del Perimetro |
|-----------------|---------------------|
| Rectangular | Rectangular |
| Circular | Circular |
| Poligonal | Poligonal con esquinas a d/2 |

---

## 8.10.3 Resistencia al Cortante del Concreto (Vc)

### 8.10.3.1 Columnas Interiores

```
Vc = menor de:
  (a) 4*λ*λs*√fc' * bo * d
  (b) (2 + 4/β)*λ*λs*√fc' * bo * d
  (c) (2 + αs*d/bo)*λ*λs*√fc' * bo * d
```

Donde:
- **β** = relacion lado largo/lado corto de columna
- **αs** = 40 (interior), 30 (borde), 20 (esquina)
- **λs** = √(2/(1 + 0.004*d)) <= 1.0 (efecto de tamano)
- **bo** = perimetro de seccion critica

### 8.10.3.2 Columnas de Borde y Esquina
Usar las mismas formulas con αs apropiado.

### 8.10.3.3 Limite Superior
```
Vc <= 4*λ*λs*√fc' * bo * d
```

---

## 8.10.4 Resistencia con Refuerzo de Cortante (Vn)

### 8.10.4.1 Con Barras o Mallas

| Parametro | Valor |
|-----------|-------|
| Vn maximo | 6*λ*√fc' * bo * d |
| Vc reducido | 2*λ*λs*√fc' * bo * d |
| Vs | Av*fyt*d/s |

```
Vn = Vc + Vs <= 6*λ*√fc' * bo * d
```

### 8.10.4.2 Con Studs (Conectores Tipo Perno)

| Parametro | Valor |
|-----------|-------|
| Vn maximo | 8*λ*√fc' * bo * d |
| Vc en seccion con studs | 3*λ*λs*√fc' * bo * d |

```
Vn = Vc + Vs <= 8*λ*√fc' * bo * d
```

---

## 8.10.5 Espaciamiento del Refuerzo

### 8.10.5.1 Barras o Mallas

| Direccion | s_max |
|-----------|-------|
| Perpendicular a columna | **d/2** |
| Paralela a columna | **2d** |

### 8.10.5.2 Studs

| Direccion | s_max |
|-----------|-------|
| Primera fila desde columna | <= **d/2** |
| Entre filas | <= **3d/4** (si Vu > 6*√fc'*bo*d), **d** (si menor) |

---

## 8.10.6 Desarrollo del Refuerzo

### 8.10.6.1 Barras y Mallas
Desarrollar fy en ambos lados de la seccion critica.

### 8.10.6.2 Studs
- Placa de cabeza y base deben tener area >= 10*Ase
- Altura de stud >= distancia entre centroide de cabeza y base

---

## 8.10.7 Extension del Refuerzo

### 8.10.7.1 Perimetro Exterior
El refuerzo de cortante debe extenderse hasta donde:
```
Vu <= φ*Vc (concreto solo)
```

A una distancia >= **d/2** desde la ultima linea de refuerzo.

---

## Resumen de Limites

| Tipo de Refuerzo | Vn maximo | Vc en zona reforzada |
|------------------|-----------|----------------------|
| Sin refuerzo | 4*λ*λs*√fc' * bo * d | - |
| Barras/Mallas | 6*λ*√fc' * bo * d | 2*λ*λs*√fc' * bo * d |
| Studs | 8*λ*√fc' * bo * d | 3*λ*λs*√fc' * bo * d |

### Factor de Tamano (λs)

```
λs = √(2/(1 + 0.004*d)) <= 1.0
```

| d (in.) | λs |
|---------|-----|
| 10 | 0.98 |
| 20 | 0.87 |
| 30 | 0.79 |
| 40 | 0.73 |

---

*ACI 318-25 Seccion 8.10*
