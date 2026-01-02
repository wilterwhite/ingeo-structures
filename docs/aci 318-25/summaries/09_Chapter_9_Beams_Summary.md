# ACI 318-25 - CAPITULO 9: VIGAS

---

## INDICE

- [9.1 Alcance](#91-alcance)
- [9.2 Generalidades](#92-generalidades)
- [9.3 Limites de Diseno](#93-limites-de-diseno)
- [9.4 Resistencia Requerida](#94-resistencia-requerida)
- [9.5 Resistencia de Diseno](#95-resistencia-de-diseno)
- [9.6 Limites de Refuerzo](#96-limites-de-refuerzo)
- [9.7 Detallado del Refuerzo](#97-detallado-del-refuerzo)
- [9.8 Sistemas de Viguetas en Una Direccion](#98-sistemas-de-viguetas-en-una-direccion-no-presforzados)
- [9.9 Vigas Profundas (Deep Beams)](#99-vigas-profundas-deep-beams)
- [Resumen de Requisitos Principales](#resumen-de-requisitos-principales)
- [Referencias a Otros Capitulos](#referencias-a-otros-capitulos)

---

## 9.1 ALCANCE

### 9.1.1 Aplicacion
Este capitulo aplica al diseno de vigas no presforzadas y presforzadas, incluyendo:

| Tipo | Descripcion |
|------|-------------|
| (a) | Vigas compuestas de elementos de concreto construidos en colocaciones separadas pero conectados para resistir cargas como unidad |
| (b) | Sistemas de viguetas en una direccion segun 9.8 |
| (c) | Vigas profundas (deep beams) segun 9.9 |

> **NOTA**: Vigas compuestas de acero estructural-concreto no estan cubiertas. Ver ANSI/AISC 360.

---

## 9.2 GENERALIDADES

### 9.2.1 Materiales

| Seccion | Requisito | Referencia |
|---------|-----------|------------|
| 9.2.1.1 | Propiedades de diseno del concreto | Capitulo 19 |
| 9.2.1.2 | Propiedades de diseno del refuerzo | Capitulo 20 |
| 9.2.1.3 | Empotramientos en concreto | 20.6 |

### 9.2.2 Conexion a Otros Miembros

| Tipo de Construccion | Requisito |
|---------------------|-----------|
| Colada en sitio | Juntas segun Capitulo 15 |
| Precolada | Conexiones segun 16.2 |

### 9.2.3 Estabilidad

**9.2.3.1** Si la viga no esta arriostrada lateralmente de forma continua:
- (a) Espaciamiento de arriostramiento lateral ≤ **50 veces** el menor ancho del ala o cara de compresion
- (b) Considerar efectos de cargas excentricas

**9.2.3.2** En vigas presforzadas: considerar pandeo de almas y alas delgadas, y pandeo del miembro entre puntos de contacto con ductos sobredimensionados.

### 9.2.4 Construccion de Vigas T

| Seccion | Requisito |
|---------|-----------|
| 9.2.4.1 | Ala y alma coladas monoliticamente o compuestas segun 16.4 |
| 9.2.4.2 | Ancho efectivo del ala segun 6.3.2 |
| 9.2.4.3 | Refuerzo perpendicular al eje de la viga segun 7.5.2.3 |

#### 9.2.4.4 Ala Volada para Diseno por Torsion
- (a) Incluir porcion de losa a cada lado de la viga que se extiende igual a la proyeccion de la viga, pero no mayor que **4 veces el espesor de losa**
- (b) Ignorar alas si Acp²/pcp (seccion solida) o Ag²/pcp (seccion hueca) es menor sin las alas

---

## 9.3 LIMITES DE DISENO

### 9.3.1 Peralte Minimo de Viga

#### Tabla 9.3.1.1 - Peralte Minimo de Vigas No Presforzadas

| Condicion de Apoyo | Peralte Minimo h |
|-------------------|------------------|
| Simplemente apoyada | ℓ/16 |
| Un extremo continuo | ℓ/18.5 |
| Ambos extremos continuos | ℓ/21 |
| Cantilever | ℓ/8 |

> **NOTA**: Expresiones aplicables para concreto de peso normal y fy = 60,000 psi.

#### 9.3.1.1.1 Modificacion por fy
Para fy diferente de 60,000 psi, multiplicar por:
```
(0.4 + fy/100,000)
```

#### 9.3.1.1.2 Modificacion por Concreto Liviano
Para vigas de concreto liviano con wc entre 90 y 115 lb/ft³, multiplicar por el mayor de:
- (a) 1.65 - 0.005wc
- (b) 1.09

#### 9.3.1.2 Acabado de Piso
El espesor de acabado de piso puede incluirse en h si:
- Se coloca monoliticamente, o
- Se disena compuesto segun 16.4

### 9.3.2 Limites de Deflexion Calculada

| Seccion | Requisito |
|---------|-----------|
| 9.3.2.1 | Para vigas no presforzadas que no satisfacen 9.3.1 y vigas presforzadas: calcular deflexiones segun 24.2 |
| 9.3.2.2 | Para vigas compuestas apuntaladas que satisfacen 9.3.1: no se requiere calcular deflexiones post-composicion |

### 9.3.3 Limite de Deformacion del Refuerzo
**9.3.3.1** Vigas no presforzadas con Pu < 0.10fc'Ag deben ser **controladas por tension** segun Tabla 21.2.2.

### 9.3.4 Limites de Esfuerzo en Vigas Presforzadas

| Seccion | Requisito |
|---------|-----------|
| 9.3.4.1 | Clasificar como Clase U, T o C segun 24.5.2 |
| 9.3.4.2 | Esfuerzos despues de transferencia y en servicio no deben exceder 24.5.3 y 24.5.4 |

---

## 9.4 RESISTENCIA REQUERIDA

### 9.4.1 General

| Seccion | Requisito |
|---------|-----------|
| 9.4.1.1 | Calcular segun combinaciones de carga factorizadas del Capitulo 5 |
| 9.4.1.2 | Calcular segun procedimientos de analisis del Capitulo 6 |
| 9.4.1.3 | Para vigas presforzadas, considerar efectos de presfuerzo segun 5.3.14 |

### 9.4.2 Momento Factorizado
**9.4.2.1** Para vigas construidas integralmente con apoyos, Mu puede calcularse en la cara del apoyo.

### 9.4.3 Cortante Factorizado

**9.4.3.1** Para vigas construidas integralmente con apoyos, Vu puede calcularse en la cara del apoyo.

**9.4.3.2** Seccion critica reducida permitida si se cumplen (a), (b) y (c):
- (a) Reaccion del apoyo introduce compresion en la region del extremo
- (b) Cargas aplicadas en o cerca de la superficie superior
- (c) No hay carga concentrada entre cara del apoyo y seccion critica

| Tipo de Viga | Seccion Critica |
|--------------|-----------------|
| No presforzada | **d** desde la cara del apoyo |
| Presforzada | **h/2** desde la cara del apoyo |

### 9.4.4 Torsion Factorizada

| Seccion | Requisito |
|---------|-----------|
| 9.4.4.1 | Se permite tomar carga torsional de losa como uniforme |
| 9.4.4.2 | Tu puede calcularse en la cara del apoyo |
| 9.4.4.3 | Seccion critica a d (no presforzada) o h/2 (presforzada), excepto si hay momento torsional concentrado |
| 9.4.4.4 | Se permite reducir Tu segun 22.7.3 |

---

## 9.5 RESISTENCIA DE DISENO

### 9.5.1 General

**9.5.1.1** Para cada combinacion de carga factorizada aplicable:

**ϕSn ≥ U**

Incluyendo:
- (a) **ϕMn ≥ Mu**
- (b) **ϕVn ≥ Vu**
- (c) **ϕTn ≥ Tu**
- (d) **ϕPn ≥ Pu**

**9.5.1.2** ϕ segun 21.2

### 9.5.2 Momento

| Condicion | Calculo de Mn |
|-----------|---------------|
| Pu < 0.10fc'Ag | Segun 22.3 |
| Pu ≥ 0.10fc'Ag | Segun 22.4 |

**9.5.2.3** Para vigas presforzadas, tendones externos se consideran como no adheridos.

### 9.5.3 Cortante

| Seccion | Requisito |
|---------|-----------|
| 9.5.3.1 | Vn segun 22.5 |
| 9.5.3.2 | Para vigas compuestas, Vnh segun 16.4 |

### 9.5.4 Torsion

**9.5.4.1** Si Tu < ϕTth (segun 22.7), se permite despreciar efectos torsionales. No se requieren los minimos de 9.6.4 ni detallado de 9.7.5 y 9.7.6.3.

**9.5.4.2** Tn segun 22.7

**9.5.4.3** Refuerzo longitudinal y transversal para torsion se suma al requerido para Vu, Mu y Pu.

**Adicion de refuerzo transversal:**
```
Total(Av+t/s) = Av/s + 2At/s
```

**9.5.4.5** Se permite reducir refuerzo longitudinal torsional en zona de compresion por flexion:
```
Reduccion = Mu/(0.9dfy)
```

#### Procedimientos Alternativos de Diseno por Torsion

| Seccion | Condicion | Requisito |
|---------|-----------|-----------|
| 9.5.4.6 | h/bt ≥ 3, secciones solidas | Procedimiento alternativo verificado por ensayos |
| 9.5.4.7 | h/bt ≥ 4.5, secciones precoladas solidas | Procedimiento alternativo con refuerzo de alma abierta |

---

## 9.6 LIMITES DE REFUERZO

### 9.6.1 Refuerzo Minimo a Flexion en Vigas No Presforzadas

**9.6.1.1** Area minima As,min en toda seccion donde se requiere refuerzo a tension.

**9.6.1.2** As,min = mayor de (a) y (b):

| Formula | Expresion |
|---------|-----------|
| (a) | 3√fc' × bw × d / fy |
| (b) | 200 × bw × d / fy |

> **NOTA**: Para vigas estaticamente determinadas con ala en tension, bw = menor de bf y 2bw. fy limitado a 80,000 psi max.

**9.6.1.3** Si As proporcionado ≥ 1.33 × As requerido, no se requiere cumplir 9.6.1.1 y 9.6.1.2.

### 9.6.2 Refuerzo Minimo a Flexion en Vigas Presforzadas

| Seccion | Requisito |
|---------|-----------|
| 9.6.2.1 | Con refuerzo presforzado adherido: As + Aps debe desarrollar carga ≥ 1.2 × carga de agrietamiento |
| 9.6.2.2 | Si ϕMn ≥ 2Mu y ϕVn ≥ 2Vu, no se requiere satisfacer 9.6.2.1 |
| 9.6.2.3 | Con tendones no adheridos: **As,min = 0.004Act** |

### 9.6.3 Refuerzo Minimo a Cortante

#### Tabla 9.6.3.1 - Casos Donde Av,min No Se Requiere si Vu ≤ ϕVc

| Tipo de Viga | Condiciones |
|--------------|-------------|
| Peralte pequeno | h ≤ 10 in. |
| Integral con losa | h ≤ mayor de 2.5tf y 0.5bw, y h ≤ 24 in. |
| Con fibras de acero (peso normal) | fc' < 10,000 psi, Grado 60/80, h ≤ 40 in. |
| Con fibras de acero (liviano) | fc' ≤ 6,000 psi, Grado 60, h ≤ 24 in. |
| Sistema de viguetas | Segun 9.8 |

**9.6.3.1** Para vigas no presforzadas: Av,min donde Vu > ϕλ√fc'bwd

**9.6.3.2** Para vigas presforzadas: Av,min donde Vu > 0.5ϕVc

#### Tabla 9.6.3.4 - Av,min Requerido

| Tipo de Viga | Av,min/s |
|--------------|----------|
| No presforzada y presforzada con Apsfse < 0.4(Apsfpu + Asfy) | Mayor de: 0.75√fc'(bw/fyt) y 50(bw/fyt) |
| Presforzada con Apsfse ≥ 0.4(Apsfpu + Asfy) | Menor de: [Mayor de 0.75√fc'(bw/fyt) y 50(bw/fyt)] y [Apsfpu/(80fytd)]√(d/bw) |

### 9.6.4 Refuerzo Minimo por Torsion

**9.6.4.1** Requerido donde Tu ≥ ϕTth segun 22.7.

**9.6.4.2** Refuerzo transversal minimo (Av + 2At)min/s = mayor de:
- (a) 0.75√fc' × bw/fyt
- (b) 50 × bw/fyt

**9.6.4.3** Refuerzo longitudinal minimo Aℓ,min = menor de (a) y (b):
- (a) [5√fc'×Acp/fy] - (At/s)×ph×(fyt/fy)
- (b) [5√fc'×Acp/fy] - (25bw/fyt)×ph×(fyt/fy)

---

## 9.7 DETALLADO DEL REFUERZO

### 9.7.1 General

| Seccion | Requisito | Referencia |
|---------|-----------|------------|
| 9.7.1.1 | Recubrimiento de concreto | 20.5.1 |
| 9.7.1.2 | Longitudes de desarrollo | 25.4 |
| 9.7.1.3 | Empalmes de refuerzo deformado | 25.5 |
| 9.7.1.4 | Para fy ≥ 80,000 psi: Ktr ≥ 0.5db a lo largo de desarrollo y empalmes | - |
| 9.7.1.5 | Barras en paquete | 25.6 |

### 9.7.2 Espaciamiento del Refuerzo

| Seccion | Requisito |
|---------|-----------|
| 9.7.2.1 | Espaciamientos minimos segun 25.2 |
| 9.7.2.2 | Para vigas no presforzadas y Clase C presforzadas: s segun 24.3 |
| 9.7.2.3 | Para vigas con h > 36 in.: refuerzo de piel distribuido en h/2 desde cara en tension, s segun 24.3.2 |

### 9.7.3 Refuerzo a Flexion en Vigas No Presforzadas

#### 9.7.3.1-9.7.3.4 Desarrollo del Refuerzo

| Seccion | Requisito |
|---------|-----------|
| 9.7.3.1 | Desarrollar fuerza calculada a cada lado de la seccion |
| 9.7.3.2 | Ubicaciones criticas: puntos de maximo esfuerzo y donde el refuerzo ya no es necesario |
| 9.7.3.3 | Extender mas alla del punto donde no es necesario: ≥ mayor de d y 12db |
| 9.7.3.4 | Refuerzo continuo: embedment ≥ ℓd mas alla del punto de corte |

#### 9.7.3.5 Terminacion en Zona de Tension
No terminar refuerzo en zona de tension a menos que:
- (a) Vu ≤ (2/3)ϕVn en el punto de corte
- (b) Para barras No. 11 y menores: refuerzo continuo = 2× requerido y Vu ≤ (3/4)ϕVn
- (c) Estribos adicionales: area ≥ 60bws/fyt, s ≤ d/(8βb), sobre distancia 3d/4

#### 9.7.3.8 Terminacion del Refuerzo

| Ubicacion | Requisito |
|-----------|-----------|
| Apoyos simples | ≥ 1/3 del refuerzo de momento positivo maximo se extiende ≥ 6 in. al apoyo |
| Otros apoyos | ≥ 1/4 del refuerzo de momento positivo maximo se extiende ≥ 6 in. al apoyo |
| Sistema resistente lateral | Desarrollar fy en tension en cara del apoyo |
| Apoyos simples y P.I. | ℓd ≤ 1.3Mn/Vu + ℓa (confinado) o ℓd ≤ Mn/Vu + ℓa (no confinado) |
| Momento negativo | ≥ 1/3 con embedment ≥ mayor de d, 12db y ℓn/16 mas alla de P.I. |

### 9.7.4 Refuerzo a Flexion en Vigas Presforzadas

| Seccion | Requisito |
|---------|-----------|
| 9.7.4.1 | Tendones externos: mantener excentricidad especificada |
| 9.7.4.3.1 | Zonas de anclaje post-tensado segun 25.9 |
| 9.7.4.3.2 | Anclajes y acopladores segun 25.8 |

#### 9.7.4.4 Terminacion de Refuerzo con Tendones No Adheridos
- (a) ≥ ℓn/3 en areas de momento positivo, centrado
- (b) ≥ ℓn/6 a cada lado de la cara del apoyo

### 9.7.5 Refuerzo Longitudinal por Torsion

| Seccion | Requisito |
|---------|-----------|
| 9.7.5.1 | Distribuir alrededor del perimetro de estribos cerrados, s ≤ 12 in., al menos una barra en cada esquina |
| 9.7.5.2 | Diametro ≥ 0.042 × espaciamiento transversal, pero no menor que 3/8 in. |
| 9.7.5.3 | Extender ≥ (bt + d) mas alla del punto requerido por analisis |
| 9.7.5.4 | Desarrollar en la cara del apoyo en ambos extremos |

### 9.7.6 Refuerzo Transversal

#### 9.7.6.2 Cortante

**Tabla 9.7.6.2.2 - Espaciamiento Maximo de Piernas de Refuerzo de Cortante**

| Vs Requerido | Viga No Presforzada | Viga Presforzada |
|--------------|---------------------|------------------|
| | A lo largo | A traves | A lo largo | A traves |
| ≤ 4√fc'bwd | Menor de d/2 y 24 in. | d | Menor de 3h/4 y 24 in. | 3h/2 |
| > 4√fc'bwd | Menor de d/4 y 12 in. | d/2 | Menor de 3h/8 y 12 in. | 3h/4 |

#### 9.7.6.3 Torsion

| Seccion | Requisito |
|---------|-----------|
| 9.7.6.3.1 | Estribos cerrados segun 25.7.1.6 o aros |
| 9.7.6.3.2 | Extender ≥ (bt + d) mas alla del punto requerido |
| 9.7.6.3.3 | s ≤ menor de ph/8 y 12 in. |
| 9.7.6.3.4 | Secciones huecas: distancia al centro del refuerzo desde cara interior ≥ 0.5Aoh/ph |

#### 9.7.6.4 Soporte Lateral del Refuerzo de Compresion

| Seccion | Requisito |
|---------|-----------|
| 9.7.6.4.2 | Tamano minimo: No. 3 para barras ≤ No. 10; No. 4 para barras ≥ No. 11 y paquetes |
| 9.7.6.4.3 | Espaciamiento ≤ menor de 16db (long.), 48db (transv.) y dimension menor de la viga |
| 9.7.6.4.4 | Toda barra de compresion a ≤ 6 in. de una esquina de estribo con angulo ≤ 135° |

### 9.7.7 Refuerzo de Integridad Estructural (Vigas Coladas en Sitio)

#### 9.7.7.1 Vigas Perimetrales
- (a) ≥ 1/4 del refuerzo de momento positivo maximo continuo (min. 2 barras)
- (b) ≥ 1/6 del refuerzo de momento negativo continuo (min. 2 barras)
- (c) Estribos cerrados con s ≤ d/2 (no presforzada) o 3h/4 (presforzada)
- En extremos apoyados sobre longitud ≥ 2h: s ≤ menor de d/4 (o 3h/8), 8db, 24db de estribo, 12 in.

#### 9.7.7.2 Otras Vigas
- (a) ≥ 1/4 del refuerzo de momento positivo maximo continuo (min. 2 barras), o
- (b) Refuerzo longitudinal encerrado por estribos cerrados

| Seccion | Requisito |
|---------|-----------|
| 9.7.7.3 | Refuerzo de integridad pasa a traves de la region de la columna |
| 9.7.7.4 | Desarrollar en tension con 1.25fy en apoyos no continuos |
| 9.7.7.5 | Empalmes: momento positivo cerca del apoyo, momento negativo cerca de midspan |
| 9.7.7.6 | Empalmes mecanicos, soldados o Clase B |

---

## 9.8 SISTEMAS DE VIGUETAS EN UNA DIRECCION (NO PRESFORZADOS)

### 9.8.1 Requisitos Generales

| Requisito | Limite |
|-----------|--------|
| Ancho minimo de nervaduras | 4 in. |
| Profundidad maxima (excluyendo losa) | 3.5 × ancho minimo |
| Espaciamiento libre maximo entre nervaduras | 30 in. |
| Aumento permitido de Vc | 1.1 × valores de 22.5 |

**9.8.1.6 Integridad Estructural:** Al menos una barra inferior en cada vigueta continua, desarrollada con 1.25fy en la cara del apoyo.

**9.8.1.7** Refuerzo perpendicular a las nervaduras segun 24.4.

**9.8.1.8** Sistemas que no satisfacen 9.8.1.1-9.8.1.4 deben disenarse como losas y vigas.

### 9.8.2 Sistemas con Rellenos Estructurales

| Requisito | Valor |
|-----------|-------|
| Espesor de losa sobre rellenos | ≥ mayor de (claro libre/12) y 1.5 in. |
| Calculo de resistencia | Se permite incluir cascarones verticales de rellenos |

### 9.8.3 Sistemas con Otros Rellenos

| Requisito | Valor |
|-----------|-------|
| Espesor de losa | ≥ mayor de (claro libre/12) y 2 in. |

---

## 9.9 VIGAS PROFUNDAS (DEEP BEAMS)

### 9.9.1 General

**9.9.1.1** Definicion de viga profunda - una de las siguientes condiciones:
- (a) Claro libre ≤ **4h**
- (b) Cargas concentradas dentro de **2h** de la cara del apoyo

**9.9.1.2** Disenar considerando distribucion no lineal de deformacion longitudinal.

**9.9.1.3** El metodo puntal-tensor (Capitulo 23) satisface 9.9.1.2.

### 9.9.2 Limites Dimensionales

**9.9.2.1** Excepto segun 23.4.4:
```
Vu ≤ ϕ10√fc' bw d
```

### 9.9.3 Limites de Refuerzo

**9.9.3.1** Refuerzo distribuido minimo:
- (a) Transversal: **Atd ≥ 0.0025 bw std**
- (b) Longitudinal: **Aℓd ≥ 0.0025 bw sℓd**

**9.9.3.2** Refuerzo minimo a flexion segun 9.6.1.

### 9.9.4 Detallado del Refuerzo

| Seccion | Requisito |
|---------|-----------|
| 9.9.4.1 | Recubrimiento segun 20.5.1 |
| 9.9.4.2 | Espaciamiento minimo segun 25.2 |
| 9.9.4.3 | Espaciamiento de refuerzo distribuido ≤ menor de d/5 y 12 in. |
| 9.9.4.4 | Para bw > 8 in.: al menos 2 cortinas, swd ≤ 24 in. |
| 9.9.4.5 | Desarrollo considerando distribucion de esfuerzo no proporcional al momento |
| 9.9.4.6 | Apoyos simples: desarrollar fy en la cara del apoyo |
| 9.9.4.7 | Apoyos interiores: refuerzo negativo continuo; refuerzo positivo continuo o empalmado |

---

## RESUMEN DE REQUISITOS PRINCIPALES

### Peraltes Minimos (Concreto Normal, fy = 60 ksi)

| Condicion | h minimo |
|-----------|----------|
| Simplemente apoyada | ℓ/16 |
| Un extremo continuo | ℓ/18.5 |
| Ambos extremos continuos | ℓ/21 |
| Cantilever | ℓ/8 |

### Refuerzo Minimo a Flexion

| Tipo | Requisito |
|------|-----------|
| No presforzado | As,min = mayor de [3√fc'bwd/fy] y [200bwd/fy] |
| Presforzado (tendones adheridos) | Carga ≥ 1.2 × carga de agrietamiento |
| Presforzado (tendones no adheridos) | As,min = 0.004Act |

### Espaciamiento Maximo de Estribos

| Condicion | No Presforzada | Presforzada |
|-----------|----------------|-------------|
| Vs ≤ 4√fc'bwd | d/2 o 24 in. | 3h/4 o 24 in. |
| Vs > 4√fc'bwd | d/4 o 12 in. | 3h/8 o 12 in. |

### Vigas Profundas

| Parametro | Requisito |
|-----------|-----------|
| Definicion | ℓn ≤ 4h o carga concentrada dentro de 2h |
| Cortante maximo | Vu ≤ ϕ10√fc'bwd |
| Refuerzo distribuido minimo | 0.0025 en ambas direcciones |
| Espaciamiento maximo | Menor de d/5 y 12 in. |

---

## REFERENCIAS A OTROS CAPITULOS

| Tema | Capitulo/Seccion |
|------|------------------|
| Propiedades del concreto | 19 |
| Propiedades del refuerzo | 20 |
| Factores de reduccion | 21.2 |
| Resistencia a flexion | 22.3, 22.4 |
| Resistencia a cortante | 22.5 |
| Resistencia a torsion | 22.7 |
| Metodo puntal-tensor | 23 |
| Deflexiones | 24.2 |
| Clasificacion de vigas presforzadas | 24.5.2 |
| Desarrollo y empalmes | 25.4, 25.5 |
| Detalles de refuerzo transversal | 25.7 |
| Zonas de anclaje post-tensado | 25.9 |

---

*Resumen del ACI 318-25 Capitulo 9 - Vigas.*
*Fecha: 2025*
