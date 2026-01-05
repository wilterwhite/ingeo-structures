# 22.7 RESISTENCIA A TORSION

## Analogia del Tubo de Pared Delgada (R22.7)

El diseno por torsion se basa en la **analogia de armadura espacial de tubo de pared delgada**:
- Viga sometida a torsion se idealiza como tubo de pared delgada
- Nucleo de concreto se desprecia (seccion solida)
- Resistencia proporcionada por estribos cerrados y refuerzo longitudinal cerca de la superficie
- Flujo de cortante: **q = tau * t** (constante en el perimetro)
- Esfuerzo de torsion: **tau = T / (2*Ao*t)**

**Nota:** La contribucion del concreto a la resistencia torsional se ignora, pero Vc para cortante no se reduce por presencia de torsion.

## 22.7.1 General

### 22.7.1.1 Aplicabilidad
```
Aplica si: Tu >= phi*Tth
Si Tu < phi*Tth: permitido ignorar efectos de torsion
```

## 22.7.2 Limites de Materiales

| Parametro | Limite |
|-----------|--------|
| sqrt(f'c) para Tth, Tcr | **100 psi** |
| fy, fyt para refuerzo torsional | Limites de 20.2.2.4 (60,000 psi) |

## 22.7.3 Torsion de Diseno Factorizada

### Tipos de Torsion

| Tipo | Descripcion | Seccion |
|------|-------------|---------|
| **Torsion de equilibrio** | No puede redistribuirse; requerida para equilibrio | 22.7.3.1 |
| **Torsion de compatibilidad** | Puede redistribuirse despues de agrietamiento | 22.7.3.2 |

### 22.7.3.1 Torsion de Equilibrio
Si Tu >= phi*Tcr y Tu es requerido para equilibrio: **Disenar para resistir Tu completo**

### 22.7.3.2 Torsion de Compatibilidad
En estructura estaticamente indeterminada donde Tu >= phi*Tcr y puede redistribuirse: **Permitido reducir Tu a phi*Tcr**

## 22.7.4 Torsion Umbral (Threshold Torsion)

**Definicion:** Tth = Tcr / 4

### Tabla 22.7.4.1(a) - Torsion Umbral para Secciones Solidas

| Tipo de Miembro | Tth |
|-----------------|-----|
| No pretensado | lambda*sqrt(f'c) * (Acp^2 / pcp) |
| Pretensado | lambda*sqrt(f'c) * (Acp^2/pcp) * sqrt(1 + fpc/(4*lambda*sqrt(f'c))) |
| No pretensado con carga axial | lambda*sqrt(f'c) * (Acp^2/pcp) * sqrt(1 + Nu/(4*Ag*lambda*sqrt(f'c))) |

### Tabla 22.7.4.1(b) - Torsion Umbral para Secciones Huecas

| Tipo de Miembro | Tth |
|-----------------|-----|
| No pretensado | lambda*sqrt(f'c) * (Ag^2 / pcp) |
| Pretensado | lambda*sqrt(f'c) * (Ag^2/pcp) * sqrt(1 + fpc/(4*lambda*sqrt(f'c))) |
| No pretensado con carga axial | lambda*sqrt(f'c) * (Ag^2/pcp) * sqrt(1 + Nu/(4*Ag*lambda*sqrt(f'c))) |

**Nota:** Nu positivo para compresion, negativo para tension.

## 22.7.5 Torsion de Agrietamiento (Cracking Torsion)

### Tabla 22.7.5.1 - Torsion de Agrietamiento

| Tipo de Miembro | Tcr |
|-----------------|-----|
| **(a)** No pretensado | 4*lambda*sqrt(f'c) * (Acp^2 / pcp) |
| **(b)** Pretensado | 4*lambda*sqrt(f'c) * (Acp^2/pcp) * sqrt(1 + fpc/(4*lambda*sqrt(f'c))) |
| **(c)** No pretensado con carga axial | 4*lambda*sqrt(f'c) * (Acp^2/pcp) * sqrt(1 + Nu/(4*Ag*lambda*sqrt(f'c))) |

## 22.7.6 Resistencia Nominal a Torsion

### 22.7.6.1 Calculo de Tn

Para miembros no pretensados y pretensados, **Tn = menor de (a) y (b)**:

```
(a) Tn = 2*Ao*At*fyt/s * cot(theta)     (Ec. 22.7.6.1a) - Estribos
(b) Tn = 2*Ao*Al*fy/ph * tan(theta)     (Ec. 22.7.6.1b) - Longitudinal
```

Donde:
- Ao = area encerrada por trayectoria de flujo de cortante (por analisis)
- theta = angulo de diagonales de compresion (30° <= theta <= 60°)
- At = area de una rama de estribo cerrado
- Al = area de refuerzo longitudinal torsional
- ph = perimetro de linea central del estribo cerrado mas externo

### 22.7.6.1.1 Area Ao Simplificada
```
Ao = 0.85 * Aoh
```

### 22.7.6.1.2 Angulo theta Simplificado

| Condicion | theta |
|-----------|-------|
| **(a)** No pretensados o Aps*fse < 0.4*(Aps*fpu + As*fy) | **45°** |
| **(b)** Pretensados con Aps*fse >= 0.4*(Aps*fpu + As*fy) | **37.5°** |

## 22.7.7 Limites de Dimensiones de Seccion

### 22.7.7.1 Verificacion de Dimensiones

#### (a) Secciones Solidas
```
sqrt[(Vu/(bw*d))^2 + (Tu*ph/(1.7*Aoh^2))^2] <= phi*(Vc/(bw*d) + 8*sqrt(f'c))
                                                                (Ec. 22.7.7.1a)
```

#### (b) Secciones Huecas
```
Vu/(bw*d) + Tu*ph/(1.7*Aoh^2) <= phi*(Vc/(bw*d) + 8*sqrt(f'c))
                                                                (Ec. 22.7.7.1b)
```

### Combinacion de Esfuerzos (R22.7.7.1)

| Tipo de Seccion | Combinacion de Esfuerzos |
|-----------------|--------------------------|
| **Hueca** | Suma directa (esfuerzos actuan en paredes del cajon) |
| **Solida** | Raiz cuadrada de suma de cuadrados |

### 22.7.7.1.1 Miembros Pretensados
Para miembros pretensados, el valor de **d** usado en 22.7.7.1 **no necesita ser menor que 0.8h**.

### 22.7.7.1.2 Secciones Huecas con Espesor Variable
Para secciones huecas donde el espesor de pared varia alrededor del perimetro, evaluar Ec. (22.7.7.1b) en la ubicacion donde el termino:
```
(Vu/(bw*d)) + (Tu*ph/(1.7*Aoh^2))
```
es **maximo**.

### 22.7.7.2 Secciones Huecas con Pared Delgada
Si espesor de pared **t < Aoh/ph**, reemplazar:
```
Tu*ph/(1.7*Aoh^2)  -->  Tu/(1.7*Aoh*t)
```

---

*ACI 318-25 Seccion 22.7*
