# ACI 318-25 - 10.6 LIMITES DE REFUERZO

---

## 10.6.1 Refuerzo Longitudinal Minimo y Maximo

### 10.6.1.1 Limites Generales
Para columnas no pretensadas y pretensadas con esfuerzo < 225 psi:
```
As,min = 0.01 * Ag
As,max = 0.08 * Ag
```

| Parametro | Valor | Justificacion |
|-----------|-------|---------------|
| Minimo 1% | 0.01*Ag | Resistir creep, retraccion, flexion |
| Maximo 8% | 0.08*Ag | Consolidacion del hormigon, similitud con ensayos |

> **RECOMENDACION**: Si hay empalmes por traslape, limitar a **4%** (zona de empalme tendria 8%).

### 10.6.1.2 Columnas Sobredimensionadas
```
As,min >= 0.005 * Ag (del area real)
```

---

## 10.6.2 Refuerzo de Cortante Minimo

### 10.6.2.1 Condicion
Proporcionar Av minimo donde:
```
Vu > 0.5 * phi * Vc
```

### 10.6.2.2 Av,min
El mayor de (a) y (b):
```
(a) Av,min = 0.75 * sqrt(f'c) * bw * s / fyt

(b) Av,min = 50 * bw * s / fyt
```

---

*ACI 318-25 Seccion 10.6*
