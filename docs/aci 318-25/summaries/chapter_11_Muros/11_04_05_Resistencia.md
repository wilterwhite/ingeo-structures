# ACI 318-25 - 11.4-11.5 RESISTENCIA

---

## 11.4 RESISTENCIA REQUERIDA

### 11.4.1.3 Efectos de Esbeltez
Calcular segun:
- 6.6.4 (Magnificacion de momentos)
- 6.7 (Analisis de segundo orden)
- **11.8** (Metodo alternativo para muros esbeltos)

---

## 11.5 RESISTENCIA DE DISENO

### 11.5.1 General
Para cada combinacion de carga:
```
phi*Pn >= Pu
phi*Mn >= Mu
phi*Vn >= Vu
```

---

## 11.5.3 METODO SIMPLIFICADO (Carga Axial + Flexion Fuera del Plano)

### 11.5.3.1 Condicion de Aplicabilidad
Resultante de cargas factoradas dentro del **tercio medio** del espesor (e <= h/6).

### Ecuacion de Resistencia Nominal
```
Pn = 0.55 * f'c * Ag * [1 - (k*lc / 32h)^2]
```

### Tabla 11.5.3.2 - Factor de Longitud Efectiva k

| Condiciones de Borde | k |
|---------------------|---|
| Arriostrado, restringido rotacion | **0.8** |
| Arriostrado, sin restriccion rotacion | **1.0** |
| No arriostrado | **2.0** |

---

## 11.5.4 CORTANTE EN EL PLANO

### 11.5.4.2 Limite Maximo
```
Vn <= 8 * sqrt(f'c) * Acv
```

Donde:
- **Acv** = lw * h (area de corte en el plano)

### 11.5.4.3 Resistencia Nominal
```
Vn = (αc * λ * √fc' + ρt * fyt) * Acv
```

### Coeficiente αc (Tabla 11.5.4.3)

| hw/lw | αc |
|-------|-----|
| <= 1.5 | **3** |
| >= 2.0 | **2** |
| 1.5 < hw/lw < 2.0 | **6 - 2*(hw/lw)** (interpolacion) |

### 11.5.4.4 Muros con Tension Axial Neta
```
αc = 2 * (1 + Nu / (500 * Ag)) >= 0
```
Nu es negativo para tension.

### 11.5.5 Cortante Fuera del Plano
Vn segun 22.5 (como losa unidireccional).

---

## Factores de Reduccion (φ) para Muros

| Solicitacion | φ |
|--------------|---|
| Flexion (controlada por tension) | 0.90 |
| Cortante | **0.75** |
| Carga axial (compresion) | 0.65 |

---

## Resumen de Formulas

| Parametro | Formula |
|-----------|---------|
| Pn simplificado | 0.55*fc'*Ag*[1-(k*lc/32h)²] |
| Vn (cortante plano) | (αc*λ*√fc' + ρt*fyt)*Acv |
| Vn,max | 8*√fc'*Acv |
| Acv | lw * h |

---

*ACI 318-25 Secciones 11.4-11.5*
