# ACI 318-25 - CAPITULO 23: METODO PUNTAL-TENSOR (STRUT-AND-TIE)
## Resumen para Diseno de Regiones de Discontinuidad

---

## INDICE

- [23.1 Alcance](#231-alcance)
- [23.2 General](#232-general)
- [23.3 Resistencia de Diseno](#233-resistencia-de-diseno)
- [23.4 Resistencia de Puntales](#234-resistencia-de-puntales)
- [23.5 Refuerzo Distribuido Minimo](#235-refuerzo-distribuido-minimo)
- [23.6 Detallado de Refuerzo en Puntales](#236-detallado-de-refuerzo-en-puntales)
- [23.7 Resistencia de Tensores](#237-resistencia-de-tensores)
- [23.8 Detallado de Refuerzo en Tensores](#238-detallado-de-refuerzo-en-tensores)
- [23.9 Resistencia de Zonas Nodales](#239-resistencia-de-zonas-nodales)
- [23.10 Nodos de Barra Curva](#2310-nodos-de-barra-curva)
- [23.11 Diseno Sismo-Resistente](#2311-diseno-sismo-resistente)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 23.1 ALCANCE

### 23.1.1 Aplicabilidad
Aplica al diseno de miembros de concreto estructural, o regiones de miembros, donde discontinuidades de carga o geometricas causan distribucion no lineal de deformaciones longitudinales.

### 23.1.2 Permiso General
Cualquier miembro o region de discontinuidad puede disenarse modelando como armadura idealizada.

---

## 23.2 GENERAL

### 23.2.1 Modelo Puntal-Tensor
Consiste en puntales y tensores conectados en nodos para formar armadura idealizada en 2D o 3D.

### 23.2.2 Geometria
La geometria de la armadura debe ser consistente con las dimensiones de:
- Puntales
- Tensores
- Zonas nodales
- Areas de apoyo
- Soportes

### 23.2.3 Transferencia de Cargas
El modelo debe ser capaz de transferir todas las cargas factoradas a los apoyos o regiones B adyacentes.

### 23.2.4 Equilibrio
Las fuerzas internas deben estar en equilibrio con las cargas aplicadas y reacciones.

### 23.2.5 Cruces Permitidos
- Tensores **pueden** cruzar puntales y otros tensores
- Puntales **solo intersectan o solapan en nodos**

### 23.2.7 Angulo Minimo
El angulo entre los ejes de cualquier puntal y tensor que actuan en un nodo debe ser **>= 25 grados**

### 23.2.8 Pretensado
Incluir efectos del pretensado como cargas externas con factores de carga segun **5.3.16**

### Requisitos Adicionales por Tipo de Miembro

| Miembro | Requisitos |
|---------|------------|
| Vigas profundas | 9.9.2.1, 9.9.3.1, 9.9.4 |
| Muros | 11.6, 11.7.2, 11.7.3 |
| Mensulas/corbeles (av/d < 2.0) | 16.5.2, 16.5.6, Asc >= 0.04*(f'c/fy)*(bw*d) |

### 23.2.12 Cortante-Friccion
Aplicar requisitos de **22.9** donde sea apropiado considerar transferencia de cortante a traves de un plano.

---

## 23.3 RESISTENCIA DE DISENO

### 23.3.1 Verificacion de Resistencia
Para cada combinacion de carga factorada:
```
Puntales:      phi*Fns >= Fus
Tensores:      phi*Fnt >= Fut
Zonas nodales: phi*Fnn >= Fun
```

### 23.3.2 Factor phi
Segun **21.2**

---

## 23.4 RESISTENCIA DE PUNTALES

### 23.4.1 Resistencia Nominal a Compresion

**(a)** Puntal sin refuerzo longitudinal:
```
Fns = fce * Acs     [Ec. 23.4.1a]
```

**(b)** Puntal con refuerzo longitudinal:
```
Fns = fce * Acs + As' * fs'     [Ec. 23.4.1b]
```
- Se permite tomar fs' = fy para refuerzo Grado 40 o 60
- Evaluar Fns en cada extremo, usar el menor valor

### 23.4.3 Resistencia Efectiva del Concreto en Puntal
```
fce = 0.85 * beta_c * beta_s * f'c     [Ec. 23.4.3]
```

### Tabla 23.4.3(a) - Coeficiente de Puntal beta_s

| Ubicacion | Tipo | Refuerzo | Dimensiones | beta_s |
|-----------|------|----------|-------------|--------|
| Miembros en tension | Cualquiera | Cualquiera | Cualquiera | 0.4 |
| Juntas viga-columna | Interior | Cumple Cap. 15 y 18 | - | 0.75 |
| Otros casos | Borde | Cualquiera | Cualquiera | 1.0 |
| | Interior | Cumple Tabla 23.5.1 | Cualquiera | 0.75 |
| | Interior | No cumple 23.5.1 | Cumple 23.4.4 | 0.75 |
| | Interior | No cumple 23.5.1 | No cumple 23.4.4 | 0.4 |

### Tabla 23.4.3(b) - Factor de Confinamiento beta_c

| Ubicacion | beta_c |
|-----------|--------|
| Extremo de puntal conectado a nodo con superficie de apoyo | Menor de: sqrt(A2/A1), 2.0 |
| Nodo con superficie de apoyo | Menor de: sqrt(A2/A1), 2.0 |
| Otros casos | 1.0 |

### 23.4.4 Verificacion de Tension Diagonal
Si beta_s = 0.75 basado en linea (e):
```
Vu <= phi * 5 * tan(theta) * lambda * lambda_s * sqrt(f'c) * bw * d
```

### 23.4.4.1 Factor de Efecto de Tamano lambda_s

| Condicion | lambda_s |
|-----------|----------|
| Refuerzo distribuido segun 23.5 | 1.0 |
| Sin refuerzo distribuido | sqrt(2 / (1 + d/10)) <= 1 |

---

## 23.5 REFUERZO DISTRIBUIDO MINIMO

### Tabla 23.5.1 - Refuerzo Distribuido Minimo

| Restriccion Lateral | Configuracion | Cuantia Minima |
|---------------------|---------------|----------------|
| No restringido | Malla ortogonal | 0.0025 en cada direccion |
| No restringido | Una direccion (angulo alpha) | 0.0025 / sin²(alpha_1) |
| Restringido (segun 23.5.3) | - | No requerido |

### 23.5.2 Requisitos de Detallado

- (a) Desarrollar refuerzo mas alla del puntal segun **25.4**
- (b) Espaciamiento sld y std <= **12 in** (en plano del modelo)
- (c) Angulo alpha_1 >= **40 grados**
- (d) Miembros > 10 in perpendicular al plano: refuerzo en **2 planos** minimo
- (e) Espaciamiento entre planos swd <= **24 in**
- (f) Si concreto se extiende > 12 in mas alla del nodo: refuerzo de conexion

### 23.5.3 Puntales Lateralmente Restringidos
Se consideran restringidos si:
- (a) Region de discontinuidad es continua perpendicular al plano del modelo
- (b) Concreto se extiende >= 0.5*(ancho del puntal) mas alla de cada cara
- (c) Puntal en junta restringida segun 15.5.2.5

---

## 23.6 DETALLADO DE REFUERZO EN PUNTALES

### 23.6.1 Refuerzo de Compresion
Debe ser paralelo al eje del puntal y confinado por:
- Amarres cerrados (23.6.3)
- Espirales (23.6.4)

### 23.6.3 Amarres Cerrados

**Espaciamiento s** <= menor de:
- (a) Menor dimension de seccion transversal del puntal
- (b) 48*db del alambre o barra de amarre
- (c) 16*db del refuerzo de compresion

**Primer amarre**: a no mas de **0.5s** de la cara de la zona nodal

---

## 23.7 RESISTENCIA DE TENSORES

### 23.7.2 Resistencia Nominal a Tension
```
Fnt = Ats * fy + Atp * delta_fp     [Ec. 23.7.2]
```
- Atp = 0 para miembros no pretensados
- delta_fp = 60,000 psi (pretensado adherido), 10,000 psi (no adherido)
- delta_fp <= (fpy - fse)

---

## 23.8 DETALLADO DE REFUERZO EN TENSORES

### 23.8.1 Eje Centroidal
Eje del refuerzo del tensor debe coincidir con el eje del tensor en el modelo.

### 23.8.3 Espaciamiento Transversal
Espaciamiento transversal del refuerzo del tensor <= menor de:
- (a) 24 in
- (b) Espaciamiento maximo del capitulo respectivo

### 23.8.4 Anclaje
Refuerzo del tensor anclado por:
- Dispositivos mecanicos
- Anclajes de postensado
- Ganchos estandar
- Desarrollo de barra recta (23.8.5)

### 23.8.5 Desarrollo de Fuerza
Desarrollar fuerza del tensor en cada direccion donde el centroide del refuerzo sale de la zona nodal extendida.

---

## 23.9 RESISTENCIA DE ZONAS NODALES

### 23.9.1 Resistencia Nominal a Compresion
```
Fnn = fce * Anz     [Ec. 23.9.1]
```

### 23.9.2 Resistencia Efectiva del Concreto
```
fce = 0.85 * beta_c * beta_n * f'c     [Ec. 23.9.2]
```

### Tabla 23.9.2 - Coeficiente de Zona Nodal beta_n

| Configuracion de Zona Nodal | beta_n |
|-----------------------------|--------|
| C-C-C: Acotada por puntales y/o areas de apoyo | 1.0 |
| C-C-T: Anclando un tensor | 0.80 |
| C-T-T o T-T-T: Anclando dos o mas tensores | 0.60 |

### 23.9.4 Area de Cara Nodal (Anz)
Menor de:
- (a) Area de cara perpendicular a linea de accion de Fus
- (b) Area de seccion perpendicular a linea de accion de fuerza resultante

---

## 23.10 NODOS DE BARRA CURVA

### 23.10.2 Radio de Curvatura (recubrimiento >= 1.5*db)

**(a)** Dobleces < 180 grados:
```
rb >= (2 * Ats * fy) / (bs * f'c)     [Ec. 23.10.2a]
```

**(b)** Tensores anclados por dobleces de 180 grados:
```
rb >= (Ats * fy) / (wt * f'c)     [Ec. 23.10.2b]
```

### 23.10.3 Recubrimiento Limitado
Si recubrimiento < 1.5*db, multiplicar rb por **(1.5*db / cc)**

### 23.10.5 Esquinas de Marco
Centro de curvatura debe ubicarse dentro de la junta.

---

## 23.11 DISENO SISMO-RESISTENTE

### 23.11.1 Aplicabilidad (SDC D, E, F)
Regiones del sistema sismo-resistente disenadas con puntal-tensor deben cumplir:
- (a) Capitulo 18
- (b) 23.11.2 a 23.11.5, a menos que E se multiplique por **omega_o >= 2.5**

### 23.11.2 Resistencia de Puntales
Multiplicar fce (segun 23.4) por **0.8**

### 23.11.3 Detallado de Puntales
Refuerzo transversal segun **23.11.3.2** o **23.11.3.3**

### Tabla 23.11.3.2(a) - Refuerzo Transversal para Puntales

| Refuerzo | Expresion |
|----------|-----------|
| Ash/(s*bc) para estribos rectangulares | Mayor de: 0.3*(Acs/Ach - 1)*(f'c/fyt), 0.09*(f'c/fyt) |

### Tabla 23.11.3.2(b) - Espaciamiento Maximo

| Grado de Refuerzo | Espaciamiento Maximo |
|-------------------|---------------------|
| Grado 60 | Menor de: 6*db, 6 in |
| Grado 80 | Menor de: 5*db, 6 in |
| Grado 100 | Menor de: 4*db, 6 in |

### 23.11.4 Resistencia de Tensores
Desarrollar refuerzo del tensor para **1.25*fy** en tension segun **25.4**

### 23.11.5 Resistencia de Nodos
Multiplicar Fnn (segun 23.9) por **0.8**

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Factores de carga | Capitulo 5 |
| Procedimientos de analisis | Capitulo 6 |
| Vigas profundas | 9.9 |
| Muros | Capitulo 11 |
| Juntas viga-columna | Capitulo 15 |
| Mensulas y corbeles | 16.5 |
| Requisitos sismicos | Capitulo 18 |
| Factores phi | 21.2 |
| Cortante-friccion | 22.9 |
| Desarrollo de refuerzo | 25.4 |
| Amarres | 25.7.2 |
| Espirales | 25.7.3 |

---

*Resumen del ACI 318-25 Capitulo 23 para metodo puntal-tensor.*
*Fecha: 2025*
