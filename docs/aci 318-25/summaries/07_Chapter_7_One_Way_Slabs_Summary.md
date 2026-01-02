# ACI 318-25 - CAPITULO 7: LOSAS EN UNA DIRECCION

---

## INDICE

- [7.1 Alcance](#71-alcance)
- [7.2 Generalidades](#72-generalidades)
- [7.3 Limites de Diseno](#73-limites-de-diseno)
- [7.4 Resistencia Requerida](#74-resistencia-requerida)
- [7.5 Resistencia de Diseno](#75-resistencia-de-diseno)
- [7.6 Limites de Refuerzo](#76-limites-de-refuerzo)
- [7.7 Detallado del Refuerzo](#77-detallado-del-refuerzo)
- [Resumen de Requisitos Principales](#resumen-de-requisitos-principales)
- [Referencias a Otros Capitulos](#referencias-a-otros-capitulos)

---

## 7.1 ALCANCE

### 7.1.1 Aplicacion
Este capitulo aplica al diseno de losas no presforzadas y presforzadas reforzadas para flexion en una direccion, incluyendo:

| Tipo | Descripcion |
|------|-------------|
| (a) | Losas solidas |
| (b) | Losas coladas sobre deck de acero no compuesto (stay-in-place) |
| (c) | Losas compuestas de elementos de concreto construidos en colocaciones separadas pero conectados para resistir cargas como unidad |
| (d) | Losas precoladas, presforzadas de nucleo hueco (hollow-core) |

> **NOTA**: Las provisiones para sistemas de viguetas en una direccion estan en el Capitulo 9.

---

## 7.2 GENERALIDADES

### 7.2.1 Consideraciones de Diseno
Los efectos de cargas concentradas, aberturas en la losa y vacios dentro de la losa deben considerarse en el diseno.

> **NOTA**: Las cargas concentradas pueden causar comportamiento en dos direcciones, falla por punzonado y fluencia flexural localizada.

### 7.2.2 Materiales

| Seccion | Requisito | Referencia |
|---------|-----------|------------|
| 7.2.2.1 | Propiedades de diseno del concreto | Capitulo 19 |
| 7.2.2.2 | Propiedades de diseno del refuerzo de acero | Capitulo 20 |
| 7.2.2.3 | Empotramiento en concreto | 20.6 |

### 7.2.3 Conexion a Otros Miembros

| Tipo de Construccion | Requisito |
|---------------------|-----------|
| Colada en sitio | Juntas segun Capitulo 15 |
| Precolada | Conexiones segun 16.2 |

---

## 7.3 LIMITES DE DISENO

### 7.3.1 Espesor Minimo de Losa

#### Tabla 7.3.1.1 - Espesor Minimo de Losas Solidas No Presforzadas en Una Direccion

| Condicion de Apoyo | Espesor Minimo h |
|-------------------|------------------|
| Simplemente apoyada | ℓ/20 |
| Un extremo continuo | ℓ/24 |
| Ambos extremos continuos | ℓ/28 |
| Cantilever | ℓ/10 |

> **NOTA**: Expresiones aplicables para concreto de peso normal y fy = 60,000 psi.

#### 7.3.1.1.1 Modificacion por fy
Para fy diferente de 60,000 psi, multiplicar las expresiones por:
```
(0.4 + fy/100,000)
```

#### 7.3.1.1.2 Modificacion por Concreto Liviano
Para losas de concreto liviano con wc entre 90 y 115 lb/ft³, multiplicar por el mayor de:
- (a) 1.65 - 0.005wc
- (b) 1.09

#### 7.3.1.2 Acabado de Piso
El espesor de acabado de piso de concreto puede incluirse en h si:
- Se coloca monoliticamente con la losa, o
- Se disena para ser compuesto segun 16.4

### 7.3.2 Limites de Deflexion Calculada

| Seccion | Requisito |
|---------|-----------|
| 7.3.2.1 | Para losas no presforzadas que no satisfacen 7.3.1 y losas presforzadas: calcular deflexiones segun 24.2, no exceder limites de 24.2.2 |
| 7.3.2.2 | Para losas compuestas: investigar deflexiones antes de que el miembro sea compuesto |

### 7.3.3 Limite de Deformacion del Refuerzo
**7.3.3.1** Las losas no presforzadas deben ser **controladas por tension** segun Tabla 21.2.2.

### 7.3.4 Limites de Esfuerzo en Losas Presforzadas

| Seccion | Requisito |
|---------|-----------|
| 7.3.4.1 | Clasificar losas como Clase U, T o C segun 24.5.2 |
| 7.3.4.2 | Esfuerzos inmediatamente despues de transferencia y en cargas de servicio no deben exceder 24.5.3 y 24.5.4 |

---

## 7.4 RESISTENCIA REQUERIDA

### 7.4.1 General

| Seccion | Requisito |
|---------|-----------|
| 7.4.1.1 | Calcular segun combinaciones de carga factorizadas del Capitulo 5 |
| 7.4.1.2 | Calcular segun procedimientos de analisis del Capitulo 6 |
| 7.4.1.3 | Para losas presforzadas, considerar efectos de reacciones inducidas por presfuerzo segun 5.3.14 |

### 7.4.2 Momento Factorizado
**7.4.2.1** Para losas construidas integralmente con apoyos, Mu en el apoyo puede calcularse en la cara del apoyo.

### 7.4.3 Cortante Factorizado

| Seccion | Requisito |
|---------|-----------|
| 7.4.3.1 | Vu en el apoyo puede calcularse en la cara del apoyo |
| 7.4.3.2 | Seccion critica a distancia **d** (no presforzadas) o **h/2** (presforzadas) de la cara del apoyo |

**Condiciones para usar seccion critica reducida (7.4.3.2):**
- (a) Reaccion del apoyo introduce compresion en la region del extremo
- (b) Cargas aplicadas en o cerca de la superficie superior
- (c) No hay carga concentrada entre cara del apoyo y seccion critica

---

## 7.5 RESISTENCIA DE DISENO

### 7.5.1 General
**7.5.1.1** Para cada combinacion de carga factorizada aplicable:

**ϕSn ≥ U**

Incluyendo:
- (a) **ϕMn ≥ Mu**
- (b) **ϕVn ≥ Vu**

**7.5.1.2** ϕ segun 21.2

### 7.5.2 Momento

| Seccion | Requisito |
|---------|-----------|
| 7.5.2.1 | Mn segun 22.3 |
| 7.5.2.2 | Tendones externos: considerar como no adheridos |
| 7.5.2.3 | Refuerzo perpendicular a vigas T si el refuerzo principal es paralelo al eje de la viga |

### 7.5.3 Cortante

| Seccion | Requisito |
|---------|-----------|
| 7.5.3.1 | Vn segun 22.5 |
| 7.5.3.2 | Para losas compuestas, Vnh segun 16.4 |

---

## 7.6 LIMITES DE REFUERZO

### 7.6.1 Refuerzo Minimo a Flexion en Losas No Presforzadas

**7.6.1.1** Area minima de refuerzo a flexion:

**As,min = 0.0018Ag**

> **NOTA**: Es el mismo valor que para refuerzo por contraccion y temperatura (24.4.3.2).

### 7.6.2 Refuerzo Minimo a Flexion en Losas Presforzadas

| Seccion | Requisito |
|---------|-----------|
| 7.6.2.1 | Con refuerzo presforzado adherido: As + Aps debe desarrollar carga ≥ 1.2 × carga de agrietamiento |
| 7.6.2.2 | Si ϕMn ≥ 2Mu y ϕVn ≥ 2Vu, no se requiere satisfacer 7.6.2.1 |
| 7.6.2.3 | Con tendones no adheridos: **As,min ≥ 0.004Act** |

Donde Act = area de la seccion entre la cara en tension y el centroide de la seccion bruta.

### 7.6.3 Refuerzo Minimo a Cortante

| Seccion | Requisito |
|---------|-----------|
| 7.6.3.1 | Av,min requerido donde Vu > ϕVc |
| 7.6.3.1 | Para losas hollow-core con h > 12.5 in.: Av,min donde Vu > 0.5ϕVcw |
| 7.6.3.2 | No se requiere si ensayos demuestran Mn y Vn requeridos |
| 7.6.3.3 | Si se requiere refuerzo de cortante, Av,min segun 9.6.3.4 |

### 7.6.4 Refuerzo Minimo por Contraccion y Temperatura

| Seccion | Requisito |
|---------|-----------|
| 7.6.4.1 | Refuerzo segun 24.4 |
| 7.6.4.2 | Si se usa refuerzo presforzado segun 24.4.4, aplicar 7.6.4.2.1 a 7.6.4.2.3 |
| 7.6.4.2.3 | Al menos un tendon requerido entre vigas o muros adyacentes |

---

## 7.7 DETALLADO DEL REFUERZO

### 7.7.1 General

| Seccion | Requisito | Referencia |
|---------|-----------|------------|
| 7.7.1.1 | Recubrimiento de concreto | 20.5.1 |
| 7.7.1.2 | Longitudes de desarrollo | 25.4 |
| 7.7.1.3 | Empalmes de refuerzo deformado | 25.5 |
| 7.7.1.4 | Barras en paquete | 25.6 |

### 7.7.2 Espaciamiento del Refuerzo

| Seccion | Requisito |
|---------|-----------|
| 7.7.2.1 | Espaciamientos minimos segun 25.2 |
| 7.7.2.2 | Para losas no presforzadas y Clase C presforzadas: s ≤ valor de 24.3 |
| 7.7.2.3 | Con tendones no adheridos: s ≤ menor de 3h y 18 in. |
| 7.7.2.4 | Refuerzo por 7.5.2.3: s ≤ menor de 5h y 18 in. |

### 7.7.3 Refuerzo a Flexion en Losas No Presforzadas

#### Desarrollo del Refuerzo
| Seccion | Requisito |
|---------|-----------|
| 7.7.3.1 | Desarrollar fuerza calculada a cada lado de la seccion |
| 7.7.3.2 | Ubicaciones criticas: puntos de maximo esfuerzo y donde el refuerzo ya no es necesario |
| 7.7.3.3 | Extender refuerzo mas alla del punto donde no es necesario: ≥ mayor de d y 12db |
| 7.7.3.4 | Refuerzo continuo: embedment ≥ ℓd mas alla del punto de corte |

#### Terminacion en Zona de Tension (7.7.3.5)
No terminar refuerzo en zona de tension a menos que:
- (a) Vu ≤ (2/3)ϕVn en el punto de corte
- (b) Para barras No. 11 y menores: refuerzo continuo = 2× requerido y Vu ≤ (3/4)ϕVn
- (c) Estribos adicionales proporcionados

#### Terminacion del Refuerzo (7.7.3.8)

| Ubicacion | Requisito |
|-----------|-----------|
| Apoyos simples | ≥ 1/3 del refuerzo de momento positivo maximo debe extenderse al apoyo |
| Otros apoyos | ≥ 1/4 del refuerzo de momento positivo maximo debe extenderse 6 in. al apoyo |
| Momento negativo | ≥ 1/3 debe tener embedment ≥ mayor de d, 12db y ℓn/16 mas alla del punto de inflexion |

### 7.7.4 Refuerzo a Flexion en Losas Presforzadas

| Seccion | Requisito |
|---------|-----------|
| 7.7.4.1 | Tendones externos: mantener excentricidad especificada |
| 7.7.4.2 | Si se requiere refuerzo no presforzado, satisfacer 7.7.3 |
| 7.7.4.3.1 | Zonas de anclaje post-tensado segun 25.9 |
| 7.7.4.3.2 | Anclajes y acopladores segun 25.8 |

#### Terminacion de Refuerzo Deformado con Tendones No Adheridos (7.7.4.4.1)
- (a) ≥ ℓn/3 en areas de momento positivo, centrado
- (b) ≥ ℓn/6 a cada lado de la cara del apoyo

### 7.7.5 Refuerzo de Cortante
**7.7.5.1** Si se requiere, detallar segun 9.7.6.2

### 7.7.6 Refuerzo por Contraccion y Temperatura

#### 7.7.6.1 Colocacion
Perpendicular al refuerzo a flexion

#### 7.7.6.2 Refuerzo No Presforzado
Espaciamiento ≤ menor de **5h** y **18 in.**

#### 7.7.6.3 Refuerzo Presforzado
| Requisito | Valor |
|-----------|-------|
| Espaciamiento maximo de tendones | 6 ft |
| Distancia de cara de viga/muro al tendon mas cercano | ≤ 6 ft |
| Si espaciamiento > 4.5 ft | Refuerzo adicional segun 24.4.3 |

### 7.7.7 Refuerzo de Integridad Estructural (Losas Coladas en Sitio)

| Seccion | Requisito |
|---------|-----------|
| 7.7.7.1 | ≥ 1/4 del refuerzo de momento positivo maximo debe ser **continuo** |
| 7.7.7.2 | En apoyos no continuos: desarrollar en tension usando 1.25fy |
| 7.7.7.3 | Empalmes cerca de apoyos: mecanicos, soldados o Clase B |

---

## RESUMEN DE REQUISITOS PRINCIPALES

### Espesores Minimos (Concreto Normal, fy = 60 ksi)

| Condicion | h minimo |
|-----------|----------|
| Simplemente apoyada | L/20 |
| Un extremo continuo | L/24 |
| Ambos extremos continuos | L/28 |
| Cantilever | L/10 |

### Refuerzo Minimo

| Tipo | Requisito |
|------|-----------|
| Flexion (no presforzado) | As,min = 0.0018Ag |
| Flexion (presforzado, tendones no adheridos) | As,min = 0.004Act |
| Contraccion/Temperatura | Segun 24.4 |

### Espaciamiento Maximo

| Tipo de Refuerzo | Espaciamiento Maximo |
|------------------|---------------------|
| Longitudinal (no presforzado, Clase C) | Segun 24.3 |
| Longitudinal (tendones no adheridos) | Menor de 3h y 18 in. |
| Contraccion/Temperatura (no presforzado) | Menor de 5h y 18 in. |
| Tendones de contraccion/temperatura | 6 ft |

---

## REFERENCIAS A OTROS CAPITULOS

| Tema | Capitulo/Seccion |
|------|------------------|
| Propiedades del concreto | 19 |
| Propiedades del refuerzo | 20 |
| Factores de reduccion de resistencia | 21.2 |
| Resistencia a flexion | 22.3 |
| Resistencia a cortante | 22.5 |
| Deflexiones | 24.2 |
| Clasificacion de losas presforzadas | 24.5.2 |
| Desarrollo y empalmes | 25.4, 25.5 |
| Sistemas de viguetas | Capitulo 9 |
| Construccion compuesta | 16.4 |

---

*Resumen del ACI 318-25 Capitulo 7 - Losas en Una Direccion.*
*Fecha: 2025*
