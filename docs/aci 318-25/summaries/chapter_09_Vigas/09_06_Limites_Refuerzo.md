# ACI 318-25 - Seccion 9.6: LIMITES DE REFUERZO

---

## 9.6.1 Refuerzo Minimo a Flexion en Vigas No Presforzadas

### 9.6.1.1 Requisito General

Area minima As,min en toda seccion donde se requiere refuerzo a tension.

### 9.6.1.2 Calculo de As,min

As,min = **mayor de (a) y (b)**:

| Formula | Expresion |
|---------|-----------|
| (a) | 3 sqrt(f'c) x bw x d / fy |
| (b) | 200 x bw x d / fy |

> **NOTA**: Para vigas estaticamente determinadas con ala en tension, bw = menor de bf y 2bw. fy limitado a 80,000 psi max.

### 9.6.1.3 Excepcion

Si As proporcionado >= **1.33 x As requerido**, no se requiere cumplir 9.6.1.1 y 9.6.1.2.

---

## 9.6.2 Refuerzo Minimo a Flexion en Vigas Presforzadas

| Seccion | Requisito |
|---------|-----------|
| 9.6.2.1 | Con refuerzo presforzado adherido: As + Aps debe desarrollar carga >= 1.2 x carga de agrietamiento |
| 9.6.2.2 | Si phi Mn >= 2Mu y phi Vn >= 2Vu, no se requiere satisfacer 9.6.2.1 |
| 9.6.2.3 | Con tendones no adheridos: **As,min = 0.004 Act** |

---

## 9.6.3 Refuerzo Minimo a Cortante

### Tabla 9.6.3.1 - Casos Donde Av,min No Se Requiere (si Vu <= phi Vc)

| Tipo de Viga | Condiciones |
|--------------|-------------|
| Peralte pequeno | h <= 10 in. |
| Integral con losa | h <= mayor de 2.5 tf y 0.5 bw, y h <= 24 in. |
| Con fibras de acero (peso normal) | f'c < 10,000 psi, Grado 60/80, h <= 40 in. |
| Con fibras de acero (liviano) | f'c <= 6,000 psi, Grado 60, h <= 24 in. |
| Sistema de viguetas | Segun 9.8 |

### 9.6.3.1 Vigas No Presforzadas

Av,min donde Vu > phi lambda sqrt(f'c) bw d

### 9.6.3.2 Vigas Presforzadas

Av,min donde Vu > 0.5 phi Vc

### Tabla 9.6.3.4 - Av,min Requerido

| Tipo de Viga | Av,min/s |
|--------------|----------|
| No presforzada y presforzada con Aps fse < 0.4(Aps fpu + As fy) | Mayor de: 0.75 sqrt(f'c) (bw/fyt) y 50 (bw/fyt) |
| Presforzada con Aps fse >= 0.4(Aps fpu + As fy) | Menor de: [Mayor de 0.75 sqrt(f'c) (bw/fyt) y 50 (bw/fyt)] y [Aps fpu / (80 fyt d)] sqrt(d/bw) |

---

## 9.6.4 Refuerzo Minimo por Torsion

### 9.6.4.1 Cuando Se Requiere

Requerido donde Tu >= phi Tth segun 22.7.

### 9.6.4.2 Refuerzo Transversal Minimo

(Av + 2At)min/s = **mayor de**:

- **(a)** 0.75 sqrt(f'c) x bw / fyt
- **(b)** 50 x bw / fyt

### 9.6.4.3 Refuerzo Longitudinal Minimo

Al,min = **menor de (a) y (b)**:

- **(a)** [5 sqrt(f'c) x Acp / fy] - (At/s) x ph x (fyt/fy)
- **(b)** [5 sqrt(f'c) x Acp / fy] - (25 bw / fyt) x ph x (fyt/fy)

---

## Resumen de Refuerzos Minimos

### Flexion

| Tipo | Formula |
|------|---------|
| No presforzada | As,min = max(3 sqrt(f'c) bw d / fy, 200 bw d / fy) |
| Presforzada adherida | >= 1.2 Mcr |
| Presforzada no adherida | As,min = 0.004 Act |

### Cortante

| Tipo | Av,min/s |
|------|----------|
| General | max(0.75 sqrt(f'c) bw/fyt, 50 bw/fyt) |

### Torsion

| Tipo | Minimo |
|------|--------|
| Transversal | (Av + 2At)/s >= max(0.75 sqrt(f'c) bw/fyt, 50 bw/fyt) |
| Longitudinal | Al,min segun 9.6.4.3 |

---

## Referencias

| Tema | Seccion |
|------|---------|
| Torsion umbral | 22.7 |
| Sistemas de viguetas | 9.8 |

---

*ACI 318-25 Seccion 9.6 - Limites de Refuerzo*
