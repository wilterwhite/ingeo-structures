# ACI 318-25 - CAPITULO 12: DIAFRAGMAS

---

## INDICE

- [12.1 Alcance](#121-alcance)
- [12.2 Generalidades](#122-generalidades)
- [12.3 Limites de Diseno](#123-limites-de-diseno)
- [12.4 Resistencia Requerida](#124-resistencia-requerida)
- [12.5 Resistencia de Diseno](#125-resistencia-de-diseno)
- [12.6 Limites de Refuerzo](#126-limites-de-refuerzo)
- [12.7 Detallado del Refuerzo](#127-detallado-del-refuerzo)
- [Resumen de Requisitos Principales](#resumen-de-requisitos-principales)
- [Referencias a Otros Capitulos](#referencias-a-otros-capitulos)
- [Notas Importantes](#notas-importantes)

---

## 12.1 ALCANCE

### 12.1.1 Aplicacion
Este capitulo aplica al diseno de diafragmas no presforzados y presforzados, incluyendo:

| Tipo | Descripcion |
|------|-------------|
| (a) | Diafragmas que son losas coladas en sitio |
| (b) | Diafragmas que comprenden losa de recubrimiento colada en sitio sobre elementos precolados |
| (c) | Diafragmas que comprenden elementos precolados con franjas de borde formadas por losa de recubrimiento colada en sitio o vigas de borde |
| (d) | Diafragmas de elementos precolados interconectados sin losa de recubrimiento colada en sitio |

> **NOTA**: Los diafragmas tipicamente son elementos planares horizontales o casi horizontales que transfieren fuerzas laterales a elementos verticales del sistema resistente a fuerzas laterales.

### 12.1.2 Diafragmas Sismicos
Los tipos de diafragmas definidos en 12.1.1 que forman parte del sistema resistente a fuerzas sismicas deben satisfacer los requisitos de **18.12** donde aplique.

---

## 12.2 GENERALIDADES

### 12.2.1 Fuerzas de Diseno
El diseno debe considerar las fuerzas (a) a (e):

| Fuerza | Descripcion |
|--------|-------------|
| (a) | Fuerzas en el plano del diafragma debido a cargas laterales actuando sobre el edificio |
| (b) | Fuerzas de transferencia del diafragma |
| (c) | Fuerzas de conexion entre el diafragma y elementos verticales del marco o elementos no estructurales |
| (d) | Fuerzas resultantes de arriostrar elementos verticales o inclinados del edificio |
| (e) | Fuerzas fuera del plano del diafragma debido a gravedad y otras cargas aplicadas a la superficie del diafragma |

### Tipos de Acciones del Diafragma

| Accion | Descripcion |
|--------|-------------|
| **Fuerzas en el plano** | Cargas laterales (viento, sismo, presion de suelo) generan cortante, axial y flexion en el plano |
| **Fuerzas de transferencia** | Cambios en propiedades de elementos verticales o cambio de planos de resistencia entre pisos |
| **Fuerzas de conexion** | Presion de viento o fuerzas inerciales sismicas en elementos verticales y no estructurales |
| **Fuerzas de arriostramiento** | Columnas inclinadas generan empujes horizontales significativos |
| **Fuerzas fuera del plano** | Cargas de gravedad, presion de viento en techos, aceleracion vertical sismica |

### 12.2.2 Aberturas y Vacios
Los efectos de aberturas y vacios en la losa deben considerarse en el diseno.

### 12.2.3 Materiales

| Seccion | Requisito | Referencia |
|---------|-----------|------------|
| 12.2.3.1 | Propiedades de diseno del concreto | Capitulo 19 |
| 12.2.3.2 | Propiedades de diseno del refuerzo | Capitulo 20 |

---

## 12.3 LIMITES DE DISENO

### 12.3.1 Espesor Minimo del Diafragma

| Seccion | Requisito |
|---------|-----------|
| 12.3.1.1 | Espesor requerido para estabilidad, resistencia y rigidez bajo combinaciones de carga factorizadas |
| 12.3.1.2 | Diafragmas de piso y techo: espesor no menor que el requerido para elementos de piso y techo en otras partes del Codigo |

> **NOTA**: Para diafragmas en SDC D, E y F, ver Seccion 18.12 para requisitos especificos.

---

## 12.4 RESISTENCIA REQUERIDA

### 12.4.1 General

| Seccion | Requisito |
|---------|-----------|
| 12.4.1.1 | Calcular resistencia requerida de diafragmas, colectores y conexiones segun combinaciones de carga factorizadas del Capitulo 5 |
| 12.4.1.2 | Incluir efectos de cargas fuera del plano simultaneas con otras cargas aplicables |

### 12.4.2 Modelado y Analisis del Diafragma

**12.4.2.1** Los requisitos de modelado y analisis del codigo general de edificacion gobiernan donde aplique. De lo contrario, usar 12.4.2.2 a 12.4.2.4.

**12.4.2.2** Los procedimientos de modelado y analisis deben satisfacer los requisitos del Capitulo 6.

**12.4.2.3** Se permite cualquier conjunto de suposiciones razonables y consistentes para la rigidez del diafragma.

### 12.4.2.4 Metodos de Calculo Permitidos

Se permite calcular momentos, cortantes y fuerzas axiales de diseno segun uno de los siguientes:

| Metodo | Descripcion |
|--------|-------------|
| (a) | Modelo de diafragma rigido si el diafragma puede idealizarse como rigido |
| (b) | Modelo de diafragma flexible si el diafragma puede idealizarse como flexible |
| (c) | Analisis de envolvente usando limites superior e inferior de rigidez en el plano |
| (d) | Modelo de elementos finitos considerando flexibilidad del diafragma |
| (e) | Modelo puntal-tensor segun 23.2 |

### Consideraciones de Rigidez del Diafragma

| Condicion | Modelo Recomendado |
|-----------|-------------------|
| Diafragma muy rigido vs elementos verticales | Elemento completamente rigido |
| Diafragma flexible vs elementos verticales | Viga flexible entre apoyos rigidos |
| Rigidez comparable diafragma/elementos verticales | Modelo analitico detallado |
| Grandes transferencias de fuerza | Modelo con rigidez en el plano |
| Estructuras de estacionamiento con rampas | Considerar rampas como elementos de arriostramiento |

---

## 12.5 RESISTENCIA DE DISENO

### 12.5.1 General

**12.5.1.1** Para cada combinacion de carga factorizada aplicable:

**ϕSn ≥ U**

Considerar interaccion entre efectos de carga.

**12.5.1.2** ϕ segun 21.2

### 12.5.1.3 Metodos de Resistencia de Diseno

| Metodo | Requisitos |
|--------|------------|
| (a) Diafragma como viga de profundidad completa | Resistencias segun 12.5.2 a 12.5.4 |
| (b) Modelo puntal-tensor | Resistencias segun 23.3 |
| (c) Modelo de elementos finitos | Resistencias segun Capitulo 22, considerar distribuciones de cortante no uniformes |
| (d) Metodos alternativos | Satisfacer equilibrio y proporcionar resistencias ≥ requeridas |

**12.5.1.4** Se permite usar precompresion de refuerzo presforzado para resistir fuerzas del diafragma.

**12.5.1.5** Si se usa refuerzo de presfuerzo adherido no presforzado, el esfuerzo del acero usado para calcular resistencia no debe exceder el menor de fy especificado y **60,000 psi**.

### 12.5.2 Momento y Fuerza Axial

**12.5.2.1** Se permite disenar el diafragma para momento en el plano y fuerza axial segun 22.3 y 22.4.

**12.5.2.2** Se permite resistir tension por momento mediante:
- (a) Barras deformadas segun 20.2.1
- (b) Torones o barras segun 20.3.1, presforzados o no presforzados
- (c) Conectores mecanicos cruzando juntas entre elementos precolados
- (d) Precompresion de refuerzo presforzado

**12.5.2.3** Refuerzo no presforzado y conectores mecanicos resistiendo tension por momento deben ubicarse dentro de **h/4** del borde en tension, donde h es la profundidad del diafragma.

**12.5.2.4** Conectores mecanicos deben disenarse para resistir tension requerida bajo la apertura de junta anticipada.

### 12.5.3 Cortante

**12.5.3.1** Esta seccion aplica a la resistencia al cortante en el plano del diafragma.

**12.5.3.2** ϕ = **0.75**, a menos que se requiera un valor menor por 21.2.4.

#### 12.5.3.3 Diafragma Completamente Colado en Sitio

**Resistencia nominal al cortante:**
```
Vn = Acv(2λ√fc' + ρt×fy)     (12.5.3.3)
```

Donde:
- Acv = area bruta de concreto limitada por espesor y profundidad del alma del diafragma
- √fc' ≤ 100 psi
- ρt = refuerzo distribuido paralelo al cortante en el plano

#### 12.5.3.4 Limite de Cortante

```
Vu ≤ ϕ8Acv√fc'     (12.5.3.4)
```

Donde √fc' ≤ 100 psi

#### 12.5.3.5 Diafragma con Losa de Recubrimiento sobre Precolados

| Requisito | Especificacion |
|-----------|----------------|
| (a) | Vn segun Ec. 12.5.3.3, Vu ≤ ϕ8Acv√fc'. Acv usa espesor de recubrimiento (no compuesto) o combinado (compuesto). fc' = menor de precolado y recubrimiento |
| (b) | Vn ≤ resistencia por friccion de cortante (22.9) considerando espesor del recubrimiento sobre juntas entre elementos precolados |

#### 12.5.3.6 Diafragma de Precolados Interconectados (Sin Recubrimiento)

| Metodo | Requisito |
|--------|-----------|
| (a) Juntas inyectadas | Resistencia nominal ≤ **80 psi**. Disenar refuerzo por friccion de cortante (22.9). Este refuerzo es adicional al requerido para tension por momento y fuerza axial |
| (b) Conectores mecanicos | Disenar para resistir cortante requerido bajo apertura de junta anticipada |

#### 12.5.3.7 Transferencia de Cortante

Donde el cortante se transfiere del diafragma a un colector, o del diafragma/colector a un elemento vertical:

| Transferencia | Requisito |
|---------------|-----------|
| (a) A traves de concreto | Satisfacer provisiones de friccion de cortante de 22.9 |
| (b) A traves de conectores mecanicos o pasadores | Considerar efectos de levantamiento y rotacion del elemento vertical |

### 12.5.4 Colectores

> **Definicion**: Un colector es una region del diafragma que transfiere fuerzas entre el diafragma y un elemento vertical del sistema resistente a fuerzas laterales.

**12.5.4.1** Los colectores deben extenderse desde los elementos verticales a traves de todo o parte de la profundidad del diafragma segun se requiera para transferir cortante. Se permite discontinuar a lo largo de elementos verticales donde no se requiere transferencia.

**12.5.4.2** Los colectores deben disenarse como miembros a tension, compresion, o ambos, segun 22.4.

**12.5.4.3** El refuerzo del colector debe extenderse a lo largo del elemento vertical al menos el mayor de:
- (a) Longitud requerida para desarrollar el refuerzo en tension
- (b) Longitud requerida para transmitir fuerzas de diseno al elemento vertical por friccion de cortante (22.9), conectores mecanicos, u otros mecanismos

---

## 12.6 LIMITES DE REFUERZO

| Seccion | Requisito |
|---------|-----------|
| 12.6.1 | Excepto losas sobre terreno: satisfacer limites de refuerzo para losas en una direccion (7.6) o dos direcciones (8.6), segun aplique |
| 12.6.2 | Diafragmas con losa de recubrimiento sobre precolados: recubrimiento reforzado segun 24.4 en cada direccion |
| 12.6.3 | Refuerzo para fuerzas en el plano se suma al requerido para otros efectos, excepto que el refuerzo por contraccion y temperatura puede tambien resistir fuerzas en el plano |

---

## 12.7 DETALLADO DEL REFUERZO

### 12.7.1 General

| Seccion | Requisito | Referencia |
|---------|-----------|------------|
| 12.7.1.1 | Recubrimiento de concreto | 20.5.1 |
| 12.7.1.2 | Longitudes de desarrollo | 25.4 (excepto si Capitulo 18 requiere mayor) |
| 12.7.1.3 | Empalmes de refuerzo deformado | 25.5 |
| 12.7.1.4 | Barras en paquete | 25.6 |

### 12.7.2 Espaciamiento del Refuerzo

| Seccion | Requisito |
|---------|-----------|
| 12.7.2.1 | Espaciamiento minimo segun 25.2 |
| 12.7.2.2 | Espaciamiento maximo de refuerzo deformado ≤ menor de **5 veces el espesor del diafragma** y **18 in.** |

### 12.7.3 Refuerzo del Diafragma y Colector

| Seccion | Requisito |
|---------|-----------|
| 12.7.3.1 | Excepto losas sobre terreno: satisfacer detallado de losas en una direccion (7.7) o dos direcciones (8.7), segun aplique |
| 12.7.3.2 | Fuerza de tension o compresion calculada en el refuerzo debe desarrollarse a cada lado de cada seccion |
| 12.7.3.3 | Refuerzo para tension debe extenderse ≥ ℓd mas alla del punto donde ya no se requiere para tension (excepto en bordes y juntas de expansion) |

---

## RESUMEN DE REQUISITOS PRINCIPALES

### Fuerzas de Diseno

| Tipo de Fuerza | Descripcion |
|----------------|-------------|
| En el plano | Cortante, momento, fuerza axial por cargas laterales |
| Transferencia | Entre elementos verticales cuando cambian propiedades o planos |
| Conexion | De elementos verticales y no estructurales al diafragma |
| Arriostramiento | Por columnas inclinadas |
| Fuera del plano | Gravedad y otras cargas en la superficie |

### Resistencia al Cortante

| Tipo de Diafragma | Resistencia Nominal |
|-------------------|---------------------|
| Colado en sitio | Vn = Acv(2λ√fc' + ρt×fy), √fc' ≤ 100 psi |
| Con recubrimiento sobre precolados | Menor de: Ec. 12.5.3.3 y friccion de cortante sobre juntas |
| Precolados sin recubrimiento | Juntas inyectadas ≤ 80 psi + friccion de cortante, o conectores mecanicos |

### Limites Dimensionales

| Parametro | Limite |
|-----------|--------|
| Cortante maximo | Vu ≤ ϕ8Acv√fc' |
| Factor de reduccion | ϕ = 0.75 |
| √fc' maximo | 100 psi |

### Detallado del Refuerzo

| Parametro | Requisito |
|-----------|-----------|
| Espaciamiento maximo | Menor de 5t y 18 in. |
| Ubicacion del refuerzo a tension | Dentro de h/4 del borde en tension |
| Extension del refuerzo a tension | ≥ ℓd mas alla donde ya no es necesario |

### Colectores

| Requisito | Especificacion |
|-----------|----------------|
| Diseno | Como miembros a tension, compresion, o ambos |
| Extension del refuerzo | Mayor de: longitud de desarrollo y longitud para transferir fuerza |
| Transferencia de fuerza | Por friccion de cortante (22.9) o conectores mecanicos |

---

## REFERENCIAS A OTROS CAPITULOS

| Tema | Capitulo/Seccion |
|------|------------------|
| Propiedades del concreto | 19 |
| Propiedades del refuerzo | 20 |
| Factores de reduccion | 21.2 |
| Resistencia a flexion | 22.3, 22.4 |
| Friccion de cortante | 22.9 |
| Metodo puntal-tensor | 23 |
| Control de agrietamiento | 24.3 |
| Contraccion y temperatura | 24.4 |
| Desarrollo y empalmes | 25.4, 25.5 |
| Diafragmas sismicos (SDC D, E, F) | 18.12 |
| Losas en una direccion | 7.6, 7.7 |
| Losas en dos direcciones | 8.6, 8.7 |

---

## NOTAS IMPORTANTES

1. **Diafragma como viga horizontal**: El diafragma actua esencialmente como una viga que conecta horizontalmente entre elementos verticales del sistema resistente a fuerzas laterales.

2. **Colectores y distribuidores**: Los colectores transfieren cortante del diafragma a los elementos verticales. Un "distribuidor" es un colector que transfiere fuerza desde un elemento vertical al diafragma.

3. **Rigidez del diafragma**: La rigidez en el plano afecta la distribucion de fuerzas y desplazamientos entre elementos verticales. El modelo debe ser consistente con las caracteristicas del edificio.

4. **Diafragmas precolados**: Para diafragmas sin recubrimiento que resisten fuerzas en el plano, se debe anticipar cierta apertura de junta (del orden de 0.1 in. o menos).

5. **SDC D, E, F**: Los requisitos especificos para estas categorias de diseno sismico estan en el Capitulo 18.

---

*Resumen del ACI 318-25 Capitulo 12 - Diafragmas.*
*Fecha: 2025*
