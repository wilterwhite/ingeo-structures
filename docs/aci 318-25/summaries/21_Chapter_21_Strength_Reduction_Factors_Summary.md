# ACI 318-25 - CAPITULO 21: FACTORES DE REDUCCION DE RESISTENCIA
## Resumen para Diseno de Muros Estructurales

---

## INDICE

- [21.1 Alcance](#211-alcance)
- [21.2 Factores de Reduccion](#212-factores-de-reduccion)
  - [21.2.2 Factor phi para Momento y Carga Axial](#2122-factor-phi-para-momento-y-carga-axial)
  - [21.2.4 Modificaciones para Efectos Sismicos](#2124-modificaciones-para-efectos-sismicos)
- [Tabla Resumen para Muros](#tabla-resumen-para-muros)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 21.1 ALCANCE

### 21.1.1 Aplicabilidad
Aplica a la seleccion de factores de reduccion de resistencia (phi) usados en diseno.

### Propositos de los Factores phi (R21.1.1)
1. Considerar probabilidad de elementos sub-resistentes por variaciones en materiales y dimensiones
2. Considerar imprecisiones en las ecuaciones de diseno
3. Reflejar la ductilidad disponible y confiabilidad requerida
4. Reflejar la importancia del elemento en la estructura

---

## 21.2 FACTORES DE REDUCCION

### Tabla 21.2.1 - Factores de Reduccion phi

| Accion | phi | Excepciones |
|--------|-----|-------------|
| **(a)** Momento, axial, o combinacion | 0.65 a 0.90 segun 21.2.2 | Extremos pretensados: 21.2.3 |
| **(b)** Cortante | **0.75** | Requisitos sismicos: 21.2.4 |
| **(c)** Torsion | **0.75** | — |
| **(d)** Aplastamiento | **0.65** | — |

#### Elementos Estructurales

| Elemento | phi |
|----------|-----|
| **(e)** Mensulas y corbels | **0.75** |
| **(f)** Concreto simple | **0.60** |
| **(g)** Strut-and-tie (Cap. 23) | **0.75** |

#### Condiciones de Anclaje

| Condicion | phi |
|-----------|-----|
| **(h)** Zonas anclaje post-tensado | **0.85** |
| **(i)** Conexiones prefabricadas (fluencia acero) | **0.90** |
| **(j)** Anclaje barras (breakout) | **0.75** |
| **(k)** Refuerzo de anclaje (17.5.2.1) | **0.90** |
| **(l)** Falla concreto anclajes tension, no redundante | **0.65** |
| **(m)** Falla concreto anclajes tension, redundante | **0.75** |
| **(n)** Falla concreto anclajes cortante | **0.75** |
| **(o)** Acero anclaje, tension, ductil | **0.75** |
| **(p)** Acero anclaje, tension, no ductil | **0.65** |
| **(q)** Acero anclaje, cortante, ductil | **0.65** |
| **(r)** Acero anclaje, cortante, no ductil | **0.60** |

---

## 21.2.2 FACTOR PHI PARA MOMENTO Y CARGA AXIAL

### Deformacion Neta a Tension (epsilon_t)
Deformacion en el refuerzo extremo a tension cuando epsilon_cu = 0.003 en fibra de compresion.

### 21.2.2.1 Deformacion de Fluencia - Refuerzo Corrugado
```
epsilon_ty = fy / Es
```
Para Grado 60: se permite **epsilon_ty = 0.002**

### 21.2.2.2 Deformacion de Fluencia - Refuerzo Pretensado
```
epsilon_ty = 0.002
```

### Tabla 21.2.2 - Factor phi segun Deformacion Neta

| epsilon_t | Clasificacion | phi (Espirales) | phi (Otros) |
|-----------|---------------|-----------------|-------------|
| <= epsilon_ty | Controlado por compresion | **0.75** | **0.65** |
| epsilon_ty < epsilon_t < epsilon_ty + 0.003 | Transicion | Ec. (c) | Ec. (d) |
| >= epsilon_ty + 0.003 | Controlado por tension | **0.90** | **0.90** |

#### Formulas de Transicion
```
(c) phi = 0.75 + 0.15 * (epsilon_t - epsilon_ty) / 0.003     [Espirales]
(d) phi = 0.65 + 0.25 * (epsilon_t - epsilon_ty) / 0.003     [Otros]
```

### Diagrama de Variacion de phi

```
phi
 ^
0.90 +----------------------------------*========  Controlado por tension
     |                              *  /
0.75 +---*========================*   /           Espiral
     |   |                       /   |
0.65 +---+======================/    |            Otros
     |   |     Transicion      |     |
     +---+----------+----------+-----+---------> epsilon_t
         |          |          |
    epsilon_ty      |     epsilon_ty + 0.003
              (Compresion)        (Tension)
```

### 21.2.2.3 Limitacion para Momento y Compresion Axial

Para miembros no pretensados cuando **0.1*f'c*Ag <= Pn <= Pn,bal**:

phi no debe exceder la interpolacion lineal entre:
- phi = 0.9 en Pn = 0.1*f'c*Ag
- phi = phi_cc en Pn = Pn,bal

---

## 21.2.4 MODIFICACIONES PARA EFECTOS SISMICOS

### 21.2.4 Aplica a:
- (a) Porticos de momento especiales
- (b) Muros estructurales especiales
- (c) Muros prefabricados intermedios (SDC D, E, F)

### 21.2.4.1 Miembros Controlados por Cortante
Para miembros donde Vn < V correspondiente a Mn:
```
phi_cortante = 0.60
```

**Excepcion**: No aplica si Omega_v >= 1.5 o si omega_v*Omega_v = Omega_o

### 21.2.4.2 Diafragmas
```
phi_cortante (diafragma) <= min(phi_cortante de elementos verticales del SFRS)
```

### 21.2.4.3 Elementos de Cimentacion
```
phi_cortante (cimentacion) <= min(phi_cortante de elementos verticales del SFRS)
```

### 21.2.4.4 Juntas y Vigas de Acople Diagonales
Para juntas de porticos especiales y vigas de acople con refuerzo diagonal:
```
phi_cortante = 0.85
```

### 21.2.5 Grupos de Barras (Breakout Sismico)
```
phi_tension = 0.65
```

---

## TABLA RESUMEN PARA MUROS

| Condicion | phi | Seccion |
|-----------|-----|---------|
| Flexion (controlado por tension) | **0.90** | 21.2.2 |
| Compresion (sin espiral) | **0.65** | 21.2.2 |
| Compresion (con espiral) | **0.75** | 21.2.2 |
| Cortante (general) | **0.75** | 21.2.1(b) |
| Cortante (muros controlados por cortante) | **0.60** | 21.2.4.1 |
| Cortante (vigas acople diagonales) | **0.85** | 21.2.4.4 |
| Aplastamiento | **0.65** | 21.2.1(d) |

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Combinaciones de carga | Capitulo 5 |
| Resistencia axial Pn,max | 22.4.2.1 |
| Resistencia a flexion Mn | 22.3 |
| Resistencia a cortante Vn | 22.5 |
| Refuerzo en espiral | 25.7.3 |
| Anclajes al concreto | Capitulo 17 |
| Muros estructurales especiales | Capitulo 18 |

---

*Resumen del ACI 318-25 Capitulo 21 para factores de reduccion de resistencia.*
*Fecha: 2025*
