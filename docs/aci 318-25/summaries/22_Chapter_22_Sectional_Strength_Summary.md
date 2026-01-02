# ACI 318-25 - CAPITULO 22: RESISTENCIA SECCIONAL
## Resumen Completo para Diseno de Muros Estructurales

---

## INDICE

- [22.1 Alcance](#221-alcance)
- [22.2 Supuestos de Diseno para Momento y Carga Axial](#222-supuestos-de-diseno-para-momento-y-carga-axial)
- [22.3 Resistencia a Flexion](#223-resistencia-a-flexion)
- [22.4 Resistencia Axial o Combinada Flexion-Axial](#224-resistencia-axial-o-combinada-flexion-axial)
- [22.5 Resistencia a Cortante Unidireccional](#225-resistencia-a-cortante-unidireccional)
- [22.6 Resistencia a Cortante Bidireccional](#226-resistencia-a-cortante-bidireccional)
- [22.7 Resistencia a Torsion](#227-resistencia-a-torsion)
- [22.8 Aplastamiento (Bearing)](#228-aplastamiento-bearing)
- [22.9 Friccion por Cortante (Shear Friction)](#229-friccion-por-cortante-shear-friction)
- [Tablas Resumen](#tablas-resumen)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 22.1 ALCANCE

### 22.1.1 Aplicabilidad
Este capitulo aplica al calculo de la resistencia nominal en secciones de miembros, incluyendo:

| Item | Tipo de Resistencia |
|------|---------------------|
| (a) | Resistencia a flexion |
| (b) | Resistencia axial o combinada flexion-axial |
| (c) | Resistencia a cortante unidireccional |
| (d) | Resistencia a cortante bidireccional |
| (e) | Resistencia a torsion |
| (f) | Aplastamiento |
| (g) | Friccion por cortante |

### 22.1.2 Excepcion
No aplica si el miembro o region se disena segun **Capitulo 23** (Strut-and-Tie).

### 22.1.3 Resistencia de Diseno
```
phi_Rn = phi * Rn
```
Donde phi se obtiene del **Capitulo 21**.

---

## 22.2 SUPUESTOS DE DISENO PARA MOMENTO Y CARGA AXIAL

### 22.2.1 Equilibrio y Compatibilidad de Deformaciones

| Seccion | Requisito |
|---------|-----------|
| 22.2.1.1 | El equilibrio debe satisfacerse en cada seccion |
| 22.2.1.2 | Deformacion en concreto y refuerzo no pretensado proporcional a la distancia del eje neutro |
| 22.2.1.3 | Deformacion en concreto pretensado incluye deformacion por preesfuerzo efectivo |
| 22.2.1.4 | Cambios de deformacion en refuerzo pretensado adherido proporcionales a distancia del eje neutro |

### 22.2.2 Supuestos de Diseno para Concreto

#### 22.2.2.1 Deformacion Maxima del Concreto
```
epsilon_cu = 0.003
```
**Nota (R22.2.2.1):** En ensayos se han observado valores de 0.003 a 0.008, pero para miembros de proporciones normales se usa 0.003 a 0.004.

#### 22.2.2.2 Resistencia a Tension del Concreto
**Se desprecia** en calculos de resistencia a flexion y axial.

#### 22.2.2.3 Relacion Esfuerzo-Deformacion
Puede representarse por forma rectangular, trapezoidal, parabolica u otra que prediga resistencia en acuerdo con ensayos.

### 22.2.2.4 Bloque de Esfuerzos Rectangular Equivalente

#### 22.2.2.4.1 Esfuerzo Uniforme
```
f = 0.85 * f'c
```
Distribuido sobre zona de compresion equivalente de profundidad **a**.

#### Profundidad del Bloque
```
a = beta_1 * c                    (Ec. 22.2.2.4.1)
```
Donde **c** = distancia de fibra de compresion maxima al eje neutro.

#### Tabla 22.2.2.4.3 - Valores de beta_1

| f'c (psi) | beta_1 |
|-----------|--------|
| 2500 <= f'c <= 4000 | **0.85** |
| 4000 < f'c < 8000 | 0.85 - 0.05*(f'c - 4000)/1000 |
| f'c >= 8000 | **0.65** |

### 22.2.3 Supuestos para Refuerzo No Pretensado

| Seccion | Requisito |
|---------|-----------|
| 22.2.3.1 | Refuerzo corrugado debe cumplir 20.2.1 |
| 22.2.3.2 | Relacion esfuerzo-deformacion y Es segun 20.2.2.1 y 20.2.2.2 |

### 22.2.4 Supuestos para Refuerzo Pretensado

| Seccion | Condicion | Referencia |
|---------|-----------|------------|
| 22.2.4.1 | Pretensado adherido | fps segun 20.3.2.3 |
| 22.2.4.2 | Pretensado no adherido | fps segun 20.3.2.4 |
| 22.2.4.3 | Longitud embebida < ld | Esfuerzo segun 25.4.8.3 |

---

## 22.3 RESISTENCIA A FLEXION

### 22.3.1 General
```
Mn = calculado segun supuestos de 22.2
```

### 22.3.2 Miembros de Concreto Pretensado

| Seccion | Consideracion |
|---------|---------------|
| 22.3.2.1 | Refuerzo corrugado con pretensado puede contribuir a fs = fy |
| 22.3.2.2 | Otro refuerzo puede contribuir si se hace analisis de compatibilidad de deformaciones |

### 22.3.3 Miembros Compuestos de Concreto

| Seccion | Requisito |
|---------|-----------|
| 22.3.3.1 | Aplica a miembros construidos en colocaciones separadas pero conectados |
| 22.3.3.2 | Permitido usar seccion compuesta completa para Mn |
| 22.3.3.3 | No distinguir entre apuntalados y no apuntalados para Mn |
| 22.3.3.4 | Si f'c varia, usar propiedades individuales o f'c mas critico |

---

## 22.4 RESISTENCIA AXIAL O COMBINADA FLEXION-AXIAL

### 22.4.1 General
```
Pn, Mn = calculados segun supuestos de 22.2
```

### 22.4.2 Resistencia Axial Maxima a Compresion

#### Tabla 22.4.2.1 - Resistencia Axial Maxima

| Miembro | Refuerzo Transversal | Pn,max |
|---------|----------------------|--------|
| No pretensado | Estribos (22.4.2.4) | **0.80 Po** |
| No pretensado | Espirales (22.4.2.5) | **0.85 Po** |
| Pretensado | Estribos | **0.80 Po** |
| Pretensado | Espirales | **0.85 Po** |
| Cimentacion profunda | Estribos (Cap. 13) | **0.80 Po** |

**Nota:** fy limitado a maximo **80,000 psi**.

#### 22.4.2.2 Po para Miembros No Pretensados
```
Po = 0.85*f'c*(Ag - Ast) + fy*Ast       (Ec. 22.4.2.2)
```

#### 22.4.2.3 Po para Miembros Pretensados
```
Po = 0.85*f'c*(Ag - Ast - Apd) + fy*Ast - (fse - 0.003*Ep)*Apt    (Ec. 22.4.2.3)
```
Donde:
- Apt = area total de refuerzo pretensado
- Apd = area ocupada por ducto, vaina y refuerzo pretensado
- fse >= 0.003*Ep

### 22.4.3 Resistencia Axial Maxima a Tension

#### 22.4.3.1 Resistencia Maxima
```
Pnt,max = fy*Ast + (fse + delta_fp)*Apt     (Ec. 22.4.3.1)
```
Donde (fse + delta_fp) no debe exceder fpy, y Apt = 0 para no pretensados.

---

## 22.5 RESISTENCIA A CORTANTE UNIDIRECCIONAL

### 22.5.1 General

#### 22.5.1.1 Resistencia Nominal
```
Vn = Vc + Vs                              (Ec. 22.5.1.1)
```

#### 22.5.1.2 Limite de Dimensiones
```
Vu <= phi*(Vc + 8*sqrt(f'c)*bw*d)         (Ec. 22.5.1.2)
```
**Proposito:** Controlar agrietamiento en servicio y minimizar falla por compresion diagonal.

#### Referencias para Calculo de Vc

| Miembro | Seccion |
|---------|---------|
| No pretensado | 22.5.5 |
| Pretensado | 22.5.6 o 22.5.7 |

#### 22.5.1.5 Factor Lambda
Para Vc, Vci, Vcw: lambda segun **19.2.4** (concreto liviano).

#### 22.5.1.7-8 Consideraciones Adicionales
- Debe considerarse el efecto de **aberturas** en Vn
- Debe considerarse el efecto de **tension axial** por flujo plastico y retraccion en Vc

### 22.5.1.10-11 Interaccion de Cortante Biaxial

Se puede ignorar la interaccion si:
```
(a) Vu,x / (phi*Vn,x) <= 0.5
(b) Vu,y / (phi*Vn,y) <= 0.5
```

Si ambas relaciones > 0.5:
```
Vu,x/(phi*Vn,x) + Vu,y/(phi*Vn,y) <= 1.5    (Ec. 22.5.1.11)
```

### 22.5.2 Supuestos Geometricos

| Condicion | d | bw |
|-----------|---|----|
| Columnas rectangulares | 0.8h | - |
| Secciones circulares | 0.8*diametro | diametro (solidas) |
| Secciones circulares huecas | 0.8*diametro | 2*espesor |
| Pretensados | >= 0.8h | - |

### 22.5.3 Limites de Materiales

| Parametro | Limite | Excepcion |
|-----------|--------|-----------|
| sqrt(f'c) para Vc | **100 psi** | 22.5.3.2 |
| sqrt(f'c) > 100 psi | Permitido | Si Av,min cumple 9.6.3.4 o 9.6.4.2 |
| fy, fyt para Vs | Limites de 20.2.2.4 | fy <= 60,000 psi |

### 22.5.5 Vc para Miembros No Pretensados

#### Tabla 22.5.5.1 - Vc para Miembros No Pretensados

| Criterio | Vc |
|----------|-----|
| **Av >= Av,min** | Cualquiera de: |
| | (a) [2*lambda*sqrt(f'c) + Nu/(6Ag)] * bw*d |
| | (b) [8*lambda*(rho_w)^(1/3)*sqrt(f'c) + Nu/(6Ag)] * bw*d |
| **Av < Av,min** | (c) [8*lambda_s*lambda*(rho_w)^(1/3)*sqrt(f'c) + Nu/(6Ag)] * bw*d |

**Notas:**
- Nu positivo para compresion, negativo para tension
- Vc no debe ser menor que cero
- Nu/(6Ag) no debe exceder 0.05*f'c

#### 22.5.5.1.1 Limites de Vc
```
Vc,max = 5*lambda*sqrt(f'c)*bw*d
Vc,min = lambda*sqrt(f'c)*bw*d     (excepto tension axial neta o 18.6.5.2/18.7.6.2.1)
```

#### 22.5.5.1.3 Factor de Efecto de Tamano (Size Effect)
```
lambda_s = 2 / (1 + d/10) <= 1.0     (Ec. 22.5.5.1.3)
```
**Nota:** d en pulgadas.

### 22.5.6 Vc para Miembros Pretensados

#### 22.5.6.2 Vc como menor de Vci y Vcw

##### Vci - Resistencia a Agrietamiento Flexion-Cortante
```
Vci = 0.6*lambda*sqrt(f'c)*bw*dp + Vd + (Vi*Mcre)/Mmax    (Ec. 22.5.6.2.1a)
```

Minimo de Vci:
- Si Aps*fse < 0.4*(Aps*fpu + As*fy): Vci >= 1.7*lambda*sqrt(f'c)*bw*d
- Si Aps*fse >= 0.4*(Aps*fpu + As*fy): Vci >= 2*lambda*sqrt(f'c)*bw*d

Momento de agrietamiento:
```
Mcre = (I/yt)*(6*lambda*sqrt(f'c) + fpe - fd)    (Ec. 22.5.6.2.1d)
```

##### Vcw - Resistencia a Agrietamiento Web-Cortante
```
Vcw = (3.5*lambda*sqrt(f'c) + 0.3*fpc)*bw*dp + Vp    (Ec. 22.5.6.2.2)
```
Donde dp >= 0.8h y Vp = componente vertical del preesfuerzo efectivo.

### 22.5.8 Refuerzo a Cortante Unidireccional

#### 22.5.8.1 Requisito
```
Vs >= Vu/phi - Vc                        (Ec. 22.5.8.1)
```

#### 22.5.8.5.3 Vs para Estribos Perpendiculares
```
Vs = Av*fyt*d / s                        (Ec. 22.5.8.5.3)
```

#### 22.5.8.5.4 Vs para Estribos Inclinados
```
Vs = Av*fyt*(sin(alpha) + cos(alpha))*d / s    (Ec. 22.5.8.5.4)
```
Donde alpha >= 45 grados.

---

## 22.6 RESISTENCIA A CORTANTE BIDIRECCIONAL

### 22.6.1 General

#### 22.6.1.2 Sin Refuerzo de Cortante
```
vn = vc                                  (Ec. 22.6.1.2)
```

#### 22.6.1.3 Con Refuerzo de Cortante
```
vn = vc + vs                             (Ec. 22.6.1.3)
```

### 22.6.2 Peralte Efectivo

| Condicion | d |
|-----------|---|
| General | Promedio de d en dos direcciones ortogonales |
| Pretensados | >= 0.8h |

### 22.6.3 Limites de Materiales

| Parametro | Limite |
|-----------|--------|
| sqrt(f'c) para vc | **100 psi** |
| fyt para vs | Limites de 20.2.2.4 |

### 22.6.4 Secciones Criticas

#### 22.6.4.1 Ubicacion
Perimetro bo minimo, no mas cerca que **d/2** de:
- (a) Bordes o esquinas de columnas, cargas concentradas o areas de reaccion
- (b) Cambios de espesor (capiteles, drop panels, shear caps)

#### 22.6.4.1.1-2 Simplificaciones
- Columnas cuadradas/rectangulares: permitido asumir lados rectos
- Columnas circulares/poligonales: permitido asumir columna cuadrada de area equivalente

#### 22.6.4.3 Aberturas
Si abertura esta a menos de **4h** de la columna:
- Porcion de bo entre lineas tangentes desde centroide de columna a limites de abertura es **inefectiva**

### 22.6.5 vc para Miembros sin Refuerzo de Cortante

#### Tabla 22.6.5.2 - Cortante Bidireccional vc

| vc | Formula |
|----|---------|
| **(a)** | 4*lambda_s*lambda*sqrt(f'c) |
| **(b)** | (2 + 4/beta)*lambda_s*lambda*sqrt(f'c) |
| **(c)** | (2 + alpha_s*d/bo)*lambda_s*lambda*sqrt(f'c) |

**vc = menor de (a), (b) y (c)**

Donde:
- lambda_s = factor de tamano (22.5.5.1.3)
- beta = relacion lado largo / lado corto de columna
- alpha_s = 40 (interior), 30 (borde), 20 (esquina)

### 22.6.5.5 vc para Miembros Pretensados (si cumple 22.6.5.4)

Condiciones:
- (a) Refuerzo adherido segun 8.6.2.3 y 8.7.5.3
- (b) Columna a >= 4h de borde discontinuo
- (c) fpc >= 125 psi en cada direccion

```
vc = menor de:
(a) 3.5*lambda*sqrt(f'c) + 0.3*fpc + Vp/(bo*d)    (Ec. 22.6.5.5a)
(b) (1.5 + alpha_s*d/bo)*lambda*sqrt(f'c) + 0.3*fpc + Vp/(bo*d)    (Ec. 22.6.5.5b)
```

Limites: fpc <= 500 psi; sqrt(f'c) <= 70 psi

### 22.6.6 vc para Miembros con Refuerzo de Cortante

#### Tabla 22.6.6.1 - vc para Miembros con Refuerzo de Cortante

| Tipo de Refuerzo | Seccion Critica | vc |
|------------------|-----------------|-----|
| **Estribos** | Todas | 2*lambda_s*lambda*sqrt(f'c) |
| **Studs** | Segun 22.6.4.1 | Menor de: 3*lambda_s*lambda*sqrt(f'c), (2+4/beta)*lambda_s*lambda*sqrt(f'c), (2+alpha_s*d/bo)*lambda_s*lambda*sqrt(f'c) |
| **Studs** | Segun 22.6.4.2 | 2*lambda_s*lambda*sqrt(f'c) |

#### 22.6.6.2 Factor de Tamano lambda_s = 1.0

Se permite tomar lambda_s = 1.0 si:
- **(a) Estribos:** Disenados segun 8.7.6 y Av/s >= 2*sqrt(f'c)*bo/fyt
- **(b) Studs lisos:** Longitud de vastago <= 10 in., segun 8.7.7 y Av/s >= 2*sqrt(f'c)*bo/fyt

#### Tabla 22.6.6.3 - Esfuerzo Maximo vu

| Tipo de Refuerzo | vu Maximo (seccion 22.6.4.1) |
|------------------|------------------------------|
| Estribos | **phi*6*sqrt(f'c)** |
| Studs con cabeza | **phi*8*sqrt(f'c)** |

### 22.6.7 vs por Estribos

#### 22.6.7.1 Requisitos
Estribos permitidos en losas y zapatas si: d >= **6 in.** y d >= **16*db**

#### 22.6.7.2 Calculo de vs
```
vs = Av * fyt / (bo * s)                (Ec. 22.6.7.2)
```

### 22.6.8 vs por Studs con Cabeza

#### 22.6.8.2 Calculo de vs
```
vs = Av * fyt / (bo * s)                (Ec. 22.6.8.2)
```

#### 22.6.8.3 Refuerzo Minimo
```
Av/s >= 2*sqrt(f'c) * bo / fyt          (Ec. 22.6.8.3)
```

---

## 22.7 RESISTENCIA A TORSION

### Analogia del Tubo de Pared Delgada (R22.7)

El diseno por torsion se basa en la **analogia de armadura espacial de tubo de pared delgada**:
- Viga sometida a torsion se idealiza como tubo de pared delgada
- Nucleo de concreto se desprecia (seccion solida)
- Resistencia proporcionada por estribos cerrados y refuerzo longitudinal cerca de la superficie
- Flujo de cortante: **q = tau * t** (constante en el perimetro)
- Esfuerzo de torsion: **tau = T / (2*Ao*t)**

**Nota:** La contribucion del concreto a la resistencia torsional se ignora, pero Vc para cortante no se reduce por presencia de torsion.

### 22.7.1 General

#### 22.7.1.1 Aplicabilidad
```
Aplica si: Tu >= phi*Tth
Si Tu < phi*Tth: permitido ignorar efectos de torsion
```

### 22.7.2 Limites de Materiales

| Parametro | Limite |
|-----------|--------|
| sqrt(f'c) para Tth, Tcr | **100 psi** |
| fy, fyt para refuerzo torsional | Limites de 20.2.2.4 (60,000 psi) |

### 22.7.3 Torsion de Diseno Factorizada

#### Tipos de Torsion

| Tipo | Descripcion | Seccion |
|------|-------------|---------|
| **Torsion de equilibrio** | No puede redistribuirse; requerida para equilibrio | 22.7.3.1 |
| **Torsion de compatibilidad** | Puede redistribuirse despues de agrietamiento | 22.7.3.2 |

#### 22.7.3.1 Torsion de Equilibrio
Si Tu >= phi*Tcr y Tu es requerido para equilibrio: **Disenar para resistir Tu completo**

#### 22.7.3.2 Torsion de Compatibilidad
En estructura estaticamente indeterminada donde Tu >= phi*Tcr y puede redistribuirse: **Permitido reducir Tu a phi*Tcr**

### 22.7.4 Torsion Umbral (Threshold Torsion)

**Definicion:** Tth = Tcr / 4

#### Tabla 22.7.4.1(a) - Torsion Umbral para Secciones Solidas

| Tipo de Miembro | Tth |
|-----------------|-----|
| No pretensado | lambda*sqrt(f'c) * (Acp^2 / pcp) |
| Pretensado | lambda*sqrt(f'c) * (Acp^2/pcp) * sqrt(1 + fpc/(4*lambda*sqrt(f'c))) |
| No pretensado con carga axial | lambda*sqrt(f'c) * (Acp^2/pcp) * sqrt(1 + Nu/(4*Ag*lambda*sqrt(f'c))) |

#### Tabla 22.7.4.1(b) - Torsion Umbral para Secciones Huecas

| Tipo de Miembro | Tth |
|-----------------|-----|
| No pretensado | lambda*sqrt(f'c) * (Ag^2 / pcp) |
| Pretensado | lambda*sqrt(f'c) * (Ag^2/pcp) * sqrt(1 + fpc/(4*lambda*sqrt(f'c))) |
| No pretensado con carga axial | lambda*sqrt(f'c) * (Ag^2/pcp) * sqrt(1 + Nu/(4*Ag*lambda*sqrt(f'c))) |

**Nota:** Nu positivo para compresion, negativo para tension.

### 22.7.5 Torsion de Agrietamiento (Cracking Torsion)

#### Tabla 22.7.5.1 - Torsion de Agrietamiento

| Tipo de Miembro | Tcr |
|-----------------|-----|
| **(a)** No pretensado | 4*lambda*sqrt(f'c) * (Acp^2 / pcp) |
| **(b)** Pretensado | 4*lambda*sqrt(f'c) * (Acp^2/pcp) * sqrt(1 + fpc/(4*lambda*sqrt(f'c))) |
| **(c)** No pretensado con carga axial | 4*lambda*sqrt(f'c) * (Acp^2/pcp) * sqrt(1 + Nu/(4*Ag*lambda*sqrt(f'c))) |

### 22.7.6 Resistencia Nominal a Torsion

#### 22.7.6.1 Calculo de Tn

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

#### 22.7.6.1.1 Area Ao Simplificada
```
Ao = 0.85 * Aoh
```

#### 22.7.6.1.2 Angulo theta Simplificado

| Condicion | theta |
|-----------|-------|
| **(a)** No pretensados o Aps*fse < 0.4*(Aps*fpu + As*fy) | **45°** |
| **(b)** Pretensados con Aps*fse >= 0.4*(Aps*fpu + As*fy) | **37.5°** |

### 22.7.7 Limites de Dimensiones de Seccion

#### 22.7.7.1 Verificacion de Dimensiones

##### (a) Secciones Solidas
```
sqrt[(Vu/(bw*d))^2 + (Tu*ph/(1.7*Aoh^2))^2] <= phi*(Vc/(bw*d) + 8*sqrt(f'c))
                                                                (Ec. 22.7.7.1a)
```

##### (b) Secciones Huecas
```
Vu/(bw*d) + Tu*ph/(1.7*Aoh^2) <= phi*(Vc/(bw*d) + 8*sqrt(f'c))
                                                                (Ec. 22.7.7.1b)
```

#### Combinacion de Esfuerzos (R22.7.7.1)

| Tipo de Seccion | Combinacion de Esfuerzos |
|-----------------|--------------------------|
| **Hueca** | Suma directa (esfuerzos actuan en paredes del cajon) |
| **Solida** | Raiz cuadrada de suma de cuadrados |

#### 22.7.7.2 Secciones Huecas con Pared Delgada
Si espesor de pared **t < Aoh/ph**, reemplazar:
```
Tu*ph/(1.7*Aoh^2)  -->  Tu/(1.7*Aoh*t)
```

---

## 22.8 APLASTAMIENTO (BEARING)

### 22.8.1 General

#### 22.8.1.1 Aplicabilidad
Aplica al calculo de resistencia al aplastamiento de miembros de concreto.

#### 22.8.1.2 Excepcion
**No aplica** a zonas de anclaje post-tensado (usar 25.9).

### 22.8.3 Resistencia de Diseno

#### 22.8.3.1 Verificacion
```
phi*Bn >= Bu                            (Ec. 22.8.3.1)
```

#### Tabla 22.8.3.2 - Resistencia Nominal al Aplastamiento

| Geometria | Bn |
|-----------|-----|
| **Superficie de apoyo mas ancha que area cargada en todos los lados** | Menor de (a) y (b): |
| | (a) sqrt(A2/A1) * (0.85*f'c*A1) |
| | (b) 2 * (0.85*f'c*A1) |
| **Otros casos** | (c) 0.85*f'c*A1 |

#### Definiciones

| Parametro | Definicion |
|-----------|------------|
| **A1** | Area cargada (no mayor que area de placa de apoyo) |
| **A2** | Area de la base inferior del mayor tronco de piramide, cono o cuna contenido dentro del soporte |

#### Geometria del Tronco (Frustum)
- Base superior = area cargada A1
- Lados inclinados: **1 vertical : 2 horizontal** (45°)
- A2 se mide en el plano inferior del soporte

---

## 22.9 FRICCION POR CORTANTE (SHEAR FRICTION)

### 22.9.1 General

#### 22.9.1.1 Aplicabilidad
Aplica donde es apropiado considerar transferencia de cortante a traves de un plano dado:
- Grieta existente o potencial
- Interfaz entre materiales diferentes
- Interfaz entre concretos colocados en diferentes tiempos

#### Concepto de Friccion por Cortante (R22.9.1.1)

1. Se asume que una grieta se formara en el plano de cortante
2. Se proporciona refuerzo a traves de la grieta para resistir deslizamiento
3. Al deslizarse, las caras rugosas se separan, tensionando el refuerzo
4. El refuerzo en tension proporciona fuerza de sujecion **Avf*fy**
5. El cortante se resiste por friccion entre caras, resistencia al corte de protuberancias, y accion de pasador

**Advertencia:** Requisitos de 22.9 basados en ensayos monotonicos. Pueden ser no conservadores para interfaces sismicas con degradacion por reversiones.

### 22.9.3 Resistencia de Diseno

```
phi*Vn >= Vu                            (Ec. 22.9.3.1)
```

### 22.9.4 Resistencia Nominal

#### 22.9.4.2 Refuerzo Perpendicular al Plano de Cortante

```
Vn = mu * (Avf*fy + Nu)                 (Ec. 22.9.4.2)
```

#### Tabla 22.9.4.2 - Coeficientes de Friccion

| Condicion de Superficie de Contacto | mu |
|-------------------------------------|-----|
| **(a)** Concreto colocado monoliticamente | **1.4*lambda** |
| **(b)** Concreto contra concreto endurecido, limpio, rugosidad intencional ~1/4 in. | **1.0*lambda** |
| **(c)** Concreto contra concreto endurecido, limpio, **sin** rugosidad intencional | **0.6** |
| **(d)** Concreto contra acero estructural laminado, limpio, cortante por studs o barras soldadas | **0.7*lambda** |

**Notas:**
- lambda = 1.0 para concreto de peso normal
- Para concreto liviano: lambda segun 19.2.4, pero <= 0.85
- **Cambio ACI 318-25:** Se elimino lambda de caso (c)

#### 22.9.4.3 Refuerzo Inclinado al Plano de Cortante

Si el cortante induce **tension** en el refuerzo:
```
Vn = Avf*fy*(mu*sin(alpha) + cos(alpha)) + mu*Nu    (Ec. 22.9.4.3)
```

**Nota:** Si el cortante induce **compresion** en el refuerzo, friccion por cortante **no aplica** (Vn = 0).

#### Tabla 22.9.4.4 - Vn Maximo

| Condicion | Vn Maximo |
|-----------|-----------|
| **Concreto de peso normal, monolitico o rugoso ~1/4 in.** | Menor de: 0.2*f'c*Ac, (480 + 0.08*f'c)*Ac, 1600*Ac |
| **Otros casos** | Menor de: 0.2*f'c*Ac, 800*Ac |

#### 22.9.4.5 Tension a Traves del Plano
El area de refuerzo para resistir tension factorizada neta debe **sumarse** al area requerida para friccion por cortante.

### 22.9.5 Detallado del Refuerzo de Friccion

#### 22.9.5.1 Desarrollo del Refuerzo
El refuerzo que cruza el plano de cortante debe desarrollar **fy en tension** a ambos lados del plano.

#### 22.9.5.2 Barras U Invertidas en Losas Compuestas

| Requisito | Especificacion |
|-----------|----------------|
| (a) Tamano de barra U | <= **No. 7** |
| (b) Extension de rama transversal | >= **5*db** sobre la interfaz |
| (c) Esquinas superiores | Encierran una barra o toron |
| (d) Espaciamiento entre ramas | >= **8*db** en ambas direcciones |
| (e) Ramas verticales debajo de interfaz | Desarrollan fy segun 25.4.2 |

---

## TABLAS RESUMEN

### Resistencias Nominales

| Tipo | Formula Principal | Seccion |
|------|-------------------|---------|
| Flexion | Mn segun supuestos de 22.2 | 22.3 |
| Axial compresion | Pn,max = 0.80*Po (estribos) o 0.85*Po (espirales) | 22.4.2 |
| Cortante unidireccional | Vn = Vc + Vs | 22.5.1.1 |
| Cortante bidireccional | vn = vc + vs | 22.6.1.3 |
| Torsion | Tn = 2*Ao*At*fyt/s * cot(theta) | 22.7.6.1 |
| Aplastamiento | Bn = 0.85*f'c*A1 * sqrt(A2/A1) <= 2*(0.85*f'c*A1) | 22.8.3.2 |
| Friccion por cortante | Vn = mu*(Avf*fy + Nu) | 22.9.4.2 |

### Parametros Clave

| Parametro | Formula/Valor | Seccion |
|-----------|---------------|---------|
| epsilon_cu (concreto) | **0.003** | 22.2.2.1 |
| Bloque de esfuerzos | 0.85*f'c | 22.2.2.4.1 |
| a (profundidad bloque) | beta_1 * c | 22.2.2.4.1 |
| beta_1 (f'c <= 4000 psi) | **0.85** | 22.2.2.4.3 |
| beta_1 (f'c >= 8000 psi) | **0.65** | 22.2.2.4.3 |
| lambda_s (size effect) | 2/(1 + d/10) <= 1 | 22.5.5.1.3 |
| Ao (torsion simplificada) | 0.85 * Aoh | 22.7.6.1.1 |
| theta (no pretensado) | **45°** | 22.7.6.1.2 |

### Limites de Materiales

| Parametro | Limite | Aplicacion |
|-----------|--------|------------|
| sqrt(f'c) | 100 psi | Cortante, torsion |
| fy, fyt | 60,000 psi | Cortante, torsion, friccion |
| fy | 80,000 psi | Resistencia axial Po |

### Coeficientes de Friccion

| Condicion | mu |
|-----------|-----|
| Monolitico | 1.4*lambda |
| Rugoso (~1/4 in.) | 1.0*lambda |
| No rugoso | 0.6 |
| Contra acero | 0.7*lambda |

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Factores de reduccion phi | Capitulo 21 |
| Strut-and-Tie | Capitulo 23 |
| Propiedades del refuerzo | 20.2 |
| Propiedades del pretensado | 20.3 |
| Concreto liviano (lambda) | 19.2.4 |
| Limites de fy, fyt | 20.2.2.4 |
| Refuerzo minimo a cortante | 9.6.3, 9.6.4 |
| Losas bidireccionales | Capitulo 8 |
| Detallado de estribos bidireccionales | 8.7.6 |
| Detallado de studs con cabeza | 8.7.7 |
| Anclaje de refuerzo | 25.4 |
| Zonas de anclaje post-tensado | 25.9 |
| Combinaciones de carga | Capitulo 5 |
| Procedimientos de analisis | Capitulo 6 |
| Rugosidad intencional | 26.5.6.2(e) |

---

*Resumen completo del ACI 318-25 Capitulo 22 para resistencia seccional.*
*Fecha: 2025*
