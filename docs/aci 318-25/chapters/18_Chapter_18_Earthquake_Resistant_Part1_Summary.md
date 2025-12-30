# ACI 318-25 - CAPITULO 18: ESTRUCTURAS RESISTENTES A SISMOS (PARTE 1)
## Resumen Funcional para Implementacion en App

---

## 18.1 ALCANCE

### 18.1.1 Aplicabilidad
Este capitulo aplica al diseno de estructuras de concreto **no pretensadas y pretensadas** asignadas a Categorias de Diseno Sismico (SDC) **B a F**, incluyendo:

| Componente | Descripcion |
|------------|-------------|
| (a) Sistemas estructurales designados como parte del sistema resistente a fuerzas sismicas | Diafragmas, porticos de momento, muros estructurales y cimentaciones |
| (b) Miembros no designados como parte del SFRS | Requeridos para soportar otras cargas mientras experimentan deformaciones asociadas con efectos sismicos |

### 18.1.2 Filosofia de Diseno
Las estructuras disenadas segun este capitulo estan destinadas a resistir movimientos sismicos a traves de **respuesta inelastica ductil** de miembros seleccionados.

> **Concepto Clave**: El diseno admite respuesta no lineal con rigidez reducida y mayor disipacion de energia, pero sin deterioro critico de resistencia.

### Aplicabilidad por SDC

| SDC | Aplicacion del Capitulo 18 |
|-----|---------------------------|
| **A** | NO aplica |
| **B, C** | Aplica a sistemas designados como parte del SFRS |
| **D, E, F** | Aplica a sistemas del SFRS Y sistemas no designados como parte del SFRS |

---

## 18.2 GENERAL

### 18.2.1 Sistemas Estructurales

**18.2.1.1**: Todas las estructuras deben asignarse a un SDC segun 4.4.6.1

**18.2.1.2**: Todos los miembros deben satisfacer Capitulos 1-17 y 19-26. Donde el Capitulo 18 entre en conflicto con otros capitulos, **el Capitulo 18 gobierna**.

#### Tabla R18.2 - Secciones del Capitulo 18 a Satisfacer por SDC

| Componente | SDC A | SDC B | SDC C | SDC D, E, F |
|------------|-------|-------|-------|-------------|
| Analisis y diseno | Ninguno | 18.2.2 | 18.2.2 | 18.2.2, 18.2.4 |
| Materiales | Ninguno | Ninguno | Ninguno | 18.2.5 - 18.2.8 |
| Miembros de portico | Ninguno | 18.3 | 18.4 | 18.6 - 18.9 |
| Muros y vigas de acople | Ninguno | Ninguno | Ninguno | 18.10 |
| Muros prefabricados | Ninguno | Ninguno | 18.5 | 18.5[1], 18.11 |
| Diafragmas y cerchas | Ninguno | Ninguno | 18.12.1.2 | 18.12 |
| Cimentaciones | Ninguno | Ninguno | 18.13 | 18.13 |
| Miembros no parte del SFRS | Ninguno | Ninguno | Ninguno | 18.14 |
| Anclajes | Ninguno | Ninguno | 18.2.3 | 18.2.3 |

> [1] Segun lo permita el codigo de construccion general

#### 18.2.1.6 Requisitos por Tipo de Sistema

| Sistema Estructural | Seccion Aplicable |
|--------------------|-------------------|
| (a) Porticos de momento ordinarios | 18.3 |
| (b) Muros estructurales ordinarios | No requiere detallado del Cap. 18 |
| (c) Porticos de momento intermedios | 18.4 |
| (d) Muros prefabricados intermedios | 18.5 |
| (e) Porticos de momento especiales | 18.2.3-18.2.8 y 18.6-18.8 |
| (f) Porticos especiales con prefabricado | 18.2.3-18.2.8 y 18.9 |
| (g) Muros estructurales especiales | 18.2.3-18.2.8 y 18.10 |
| (h) Muros especiales con prefabricado | 18.2.3-18.2.8 y 18.11 |

**18.2.1.7**: Sistemas alternativos permitidos si se demuestra por evidencia experimental y analisis que tendran resistencia y tenacidad igual o superior a sistemas comparables que satisfagan este capitulo.

---

### 18.2.2 Analisis y Proporcionamiento

**18.2.2.1**: Debe considerarse la interaccion de todos los miembros estructurales y no estructurales que afecten la respuesta lineal y no lineal.

**18.2.2.2**: Miembros rigidos no parte del SFRS son permitidos si su efecto en la respuesta se considera en el diseno. Deben considerarse las consecuencias de falla de miembros no parte del SFRS.

**18.2.2.3**: Miembros que se extienden debajo de la base de la estructura y transmiten fuerzas sismicas a la cimentacion deben cumplir requisitos del Capitulo 18 consistentes con el SFRS sobre la base.

> **Recomendacion para Calculo de Deriva**: Asumir todos los miembros completamente agrietados proporciona mejores estimaciones que usar rigidez no agrietada.

---

### 18.2.3 Anclaje al Concreto
**18.2.3.1**: Anclajes que resisten fuerzas inducidas por sismo en estructuras SDC C, D, E o F deben estar de acuerdo con **17.10**.

---

### 18.2.4 Factores de Reduccion de Resistencia
**18.2.4.1**: Factores de reduccion segun **Capitulo 21**, incluyendo provisiones especificas en **21.2.4** para porticos especiales, muros especiales y muros prefabricados intermedios.

---

### 18.2.5 Concreto en Porticos y Muros Especiales

**18.2.5.1**: Resistencia especificada del concreto segun requisitos de sistemas sismicos especiales de **19.2.1**.

| Tipo de Concreto | Limitacion |
|------------------|------------|
| Concreto liviano | f'c maximo = **5000 psi** para calculos de diseno |
| Concreto normal | Sin limite especifico adicional |

> **Razon**: Limitacion del concreto liviano debido a escasez de datos sobre comportamiento bajo reversiones de desplazamiento en rango inelastico.

---

### 18.2.6 Refuerzo en Porticos y Muros Especiales

**18.2.6.1**: Refuerzo segun requisitos de sistemas sismicos especiales de **20.2.2**.

#### Grados de Refuerzo Permitidos

| Sistema | Grados ASTM A706 Permitidos |
|---------|---------------------------|
| Muros estructurales especiales (todos los componentes) | **60, 80 y 100** |
| Porticos de momento especiales | **60 y 80** solamente |

> **Nota**: Grado 100 NO permitido en porticos especiales por datos insuficientes.

#### Limites de fyt para Refuerzo Transversal

| Aplicacion | fyt Maximo |
|------------|-----------|
| Refuerzo de confinamiento (18.7.5.4) | 100,000 psi |
| Diseno de cortante (algunos miembros especiales) | 80,000 u 100,000 psi |
| Resistencia nominal al cortante (20.2.2.4) | 60,000 psi |

---

### 18.2.7 Empalmes Mecanicos en Sistemas Especiales

**18.2.7.1**: Empalmes mecanicos segun **25.5.7** y esta seccion.

**18.2.7.2**: Requisitos:

| Requisito | Descripcion |
|-----------|-------------|
| (a) Clases permitidas | **Clase G** o **Clase S** |
| (b) Clase S | Permitida en cualquier ubicacion (excepto 18.9.2.1(c)) |
| (c) Clase G en porticos especiales | **PROHIBIDA** en juntas, dentro de 2h de la cara de columna/viga, y dentro de 2h de secciones criticas de fluencia |
| (d) Clase G en muros especiales | **PROHIBIDA** donde empalmes de traslape estan prohibidos, en vigas de acople, y dentro de 2h de secciones criticas |

> **Nota Importante**: Empalmes Clase L NO estan permitidos en sistemas sismicos especiales.

---

### 18.2.8 Empalmes Soldados en Sistemas Especiales

**18.2.8.1**: Empalmes soldados **NO estan permitidos** en porticos de momento especiales ni en muros estructurales especiales, incluyendo vigas de acople.

**18.2.8.2**: Soldar estribos, amarres, insertos u otros elementos similares al refuerzo longitudinal requerido por diseno **NO esta permitido**.

> **Razon**: La soldadura de barras cruzadas puede causar fragilizacion local del acero.

---

## 18.3 PORTICOS DE MOMENTO ORDINARIOS

### 18.3.1 Alcance
**18.3.1.1**: Aplica a porticos de momento ordinarios que forman parte del SFRS.

> **Nota**: Solo aplica a estructuras SDC B.

### 18.3.2 Vigas
Las vigas deben tener al menos **dos barras continuas** en ambas caras (superior e inferior):
- Barras inferiores continuas con area >= **1/4 del area maxima de barras inferiores** a lo largo del claro
- Desarrollo en tension segun 25.4 sustituyendo **1.25fy** por fy en la cara del apoyo

### 18.3.3 Columnas con lu <= 5c1

Columnas con longitud no soportada lu <= 5c1 deben tener phiVn al menos el **menor** de:

| Opcion | Descripcion |
|--------|-------------|
| (a) | Cortante asociado con desarrollo de Mn en cada extremo restringido por curvatura reversa. Calcular para Pu que resulte en la mayor resistencia a flexion |
| (b) | Cortante maximo de combinaciones con E, usando **Omega_o * E** en lugar de E |

### 18.3.4 Juntas Viga-Columna
Satisfacer Capitulo 15 con cortante de junta Vu calculado en un plano a media altura de la junta usando fuerzas de viga en tension/compresion y cortante de columna consistente con **Mn de las vigas**.

---

## 18.4 PORTICOS DE MOMENTO INTERMEDIOS

### 18.4.1 Alcance
**18.4.1.1**: Aplica a porticos intermedios incluyendo **losas en dos direcciones sin vigas** que forman parte del SFRS.

### 18.4.2 Vigas

#### 18.4.2.1 Refuerzo Longitudinal
- Al menos **dos barras continuas** en caras superior e inferior
- Barras inferiores continuas >= **1/4 del area maxima de barras inferiores**
- Desarrollo para **1.25fy** en la cara del apoyo

#### 18.4.2.2 Requisitos de Momento
| Ubicacion | Requisito |
|-----------|-----------|
| Momento positivo en cara de junta | >= **1/3** del momento negativo en esa cara |
| Momento en cualquier seccion | >= **1/5** del momento maximo en cara de cualquier junta |

#### 18.4.2.3 Resistencia al Cortante
phiVn debe ser al menos el **menor** de:

**(a)** Suma de:
- Cortante por desarrollo de Mn en cada extremo (curvatura reversa)
- Cortante por cargas gravitacionales y sismo vertical factoradas

**(b)** Cortante maximo de combinaciones con **2E** (E duplicado)

```
Combinacion ejemplo: U = 1.2D + 2.0E + 1.0L + 0.2S
```

#### 18.4.2.4 Refuerzo Transversal en Extremos
En ambos extremos de la viga, sobre longitud >= **2h** desde la cara del apoyo:

| Parametro | Requisito |
|-----------|-----------|
| Tipo | Estribos cerrados segun 18.6.4.3 |
| Primer estribo | A no mas de **2 in** de la cara del apoyo |
| Espaciamiento maximo | El menor de: (a) d/4, (b) 8db longitudinal, (c) 24db transversal, (d) 12 in |

#### 18.4.2.5 Espaciamiento Fuera de Extremos
Espaciamiento transversal <= **d/2** a lo largo de toda la viga.

#### 18.4.2.6 Vigas con Alta Carga Axial
Si Pu > Ag*f'c/10: Refuerzo transversal segun 25.7.2.2 y 25.7.2.3 o 25.7.2.4.

---

### 18.4.3 Columnas

#### 18.4.3.1 Resistencia al Cortante
phiVn debe ser al menos el **menor** de:

| Opcion | Descripcion |
|--------|-------------|
| (a) | Cortante por desarrollo de Mn en cada extremo (curvatura reversa), usando Pu que resulte en mayor resistencia |
| (b) | Cortante maximo con **Omega_o * E** (Omega_o = 3.0 para porticos intermedios) |

#### 18.4.3.2 Tipo de Refuerzo
Columnas reforzadas con espirales segun Capitulo 10 O cumplir 18.4.3.3-18.4.3.5.

#### 18.4.3.3 Estribos en Extremos
En ambos extremos, estribos a espaciamiento so sobre longitud lo:

**Espaciamiento so** (el menor de):
| Grado | Requisito |
|-------|-----------|
| (a) Grado 60 | Menor de: 8db barra longitudinal y 8 in |
| (b) Grado 80 | Menor de: 6db barra longitudinal y 6 in |
| (c) Siempre | 1/2 de la dimension minima de la columna |

**Longitud lo** (el mayor de):
| Condicion | Valor |
|-----------|-------|
| (d) | 1/6 del claro libre |
| (e) | Dimension maxima de la columna |
| (f) | 18 in |

#### 18.4.3.4 Ubicacion del Primer Estribo
A no mas de **so/2** de la cara de la junta.

#### 18.4.3.5 Fuera de lo
Espaciamiento segun **10.7.6.5.2**.

#### 18.4.3.6 Columnas bajo Miembros Discontinuos
Columnas que soportan reacciones de miembros rigidos discontinuos (muros):
- Refuerzo transversal a espaciamiento so sobre **toda la altura** debajo del nivel de discontinuidad
- **Condicion**: Pu relacionada con sismo > Ag*f'c/10
- Si se uso Omega_o: Limite aumenta a Ag*f'c/4
- Refuerzo debe extenderse arriba y abajo segun 18.7.5.6(b)

---

### 18.4.4 Juntas

#### 18.4.4.1 Requisitos de Detallado
Juntas viga-columna deben satisfacer 15.7.1.2, 15.7.1.3 y 18.4.4.2-18.4.4.5.

#### 18.4.4.2 Vigas Profundas
Si la profundidad de viga > 2 veces la profundidad de columna:
- Analisis y diseno por **metodo puntal-tensor (Capitulo 23)**
- Resistencia de diseno <= phiVn segun 15.5
- Cumplir requisitos de detallado 18.4.4.3-18.4.4.5

#### 18.4.4.3 Desarrollo de Refuerzo
Refuerzo terminado en junta debe:
- Extenderse a la cara lejana del nucleo de la junta
- Desarrollarse en tension segun **18.8.5**

#### 18.4.4.4 Espaciamiento de Refuerzo Transversal
Dentro de la altura de la viga mas profunda: s <= menor de 18.4.3.3(a)-(c)

#### 18.4.4.5 Barras con Cabeza
Si el refuerzo superior de viga consiste en barras con cabeza que terminan en la junta:
- La columna debe extenderse sobre la junta al menos la profundidad **h** de la junta
- Alternativa: Refuerzo vertical adicional que proporcione confinamiento equivalente

#### 18.4.4.6 Juntas Losa-Columna
- Refuerzo transversal segun 15.7.2
- Al menos una capa de refuerzo transversal entre refuerzo superior e inferior de losa

#### 18.4.4.7 Resistencia al Cortante de Juntas

**18.4.4.7.1**: phiVn >= Vu

**18.4.4.7.2**: Vu segun 18.3.4

**18.4.4.7.3**: phi segun 21.2.1 para cortante

**18.4.4.7.4**: Vn segun **18.8.4.3**

---

### 18.4.5 Losas en Dos Direcciones sin Vigas

#### 18.4.5.1 Momento Factorado
Calcular Msc para combinaciones de carga (5.3.1e) y (5.3.1g). Refuerzo para Msc dentro de la franja de columna (8.4.1.5).

#### 18.4.5.2 Ancho Efectivo
Refuerzo dentro del ancho efectivo (8.4.2.2.3) debe resistir gamma_f * Msc.

Para conexiones de borde y esquina: Ancho no excede ct perpendicular al claro.

#### 18.4.5.3-18.4.5.7 Distribucion de Refuerzo

| Seccion | Requisito |
|---------|-----------|
| 18.4.5.3 | >= 1/2 del refuerzo de franja de columna en apoyo dentro de ancho efectivo |
| 18.4.5.4 | >= 1/4 del refuerzo superior en apoyo continuo a traves del claro |
| 18.4.5.5 | Refuerzo inferior continuo >= 1/3 del refuerzo superior en apoyo |
| 18.4.5.6 | >= 1/2 refuerzo inferior de franja media y todo el inferior de franja de columna a medio claro debe ser continuo y desarrollar fy en cara de columna |
| 18.4.5.7 | En bordes discontinuos: Todo el refuerzo superior e inferior desarrollado en cara de soporte |

#### 18.4.5.8 Esfuerzo Cortante Maximo
En seccion critica (22.6.4.1), cortante en dos direcciones por cargas gravitacionales sin transferencia de momento:

| Tipo de Conexion | Limite |
|------------------|--------|
| No pretensada | <= **0.4 phi vc** |
| Postensada no adherida (fpc cumple 8.6.2.1) | <= **0.5 phi vc** |

> **Excepcion**: No aplica si la conexion satisface 18.14.5

---

## 18.5 MUROS PREFABRICADOS INTERMEDIOS

### 18.5.1 Alcance
**18.5.1.1**: Aplica a muros prefabricados estructurales intermedios del SFRS.

### 18.5.2 General

#### 18.5.2.1 Fluencia en Conexiones
En conexiones entre paneles o panel-cimentacion:
- Fluencia restringida a **elementos de acero o refuerzo**
- Empalmes mecanicos usados como componentes de conexion: **Clase S**

#### 18.5.2.2 Resistencia de Conexion
Para elementos de conexion no disenados para fluir:
```
Resistencia requerida = 1.5 * Sy (de la porcion que fluye)
```
Pero no exceder resistencia de combinaciones con **Emh**.

#### 18.5.2.3 SDC D, E o F
Pilares de muro (wall piers) segun **18.10.8** o **18.14**.

---

## 18.6 VIGAS DE PORTICOS DE MOMENTO ESPECIALES

### 18.6.1 Alcance

**18.6.1.1**: Aplica a vigas de porticos especiales que resisten principalmente flexion y cortante.

**18.6.1.2**: Vigas deben conectarse a columnas que satisfagan **18.7**.

> **Nota**: No aplica a porticos losa-columna.

### 18.6.2 Limites Dimensionales

**18.6.2.1**: Las vigas deben satisfacer:

| Parametro | Requisito |
|-----------|-----------|
| (a) Claro libre ln | >= **4d** |
| (b) Ancho bw | >= mayor de **0.3h** y **10 in** |
| (c) Proyeccion mas alla de columna | <= menor de c2 y **0.7c1** (cada lado) |

> **Razon de (a)**: Miembros con ln/d < 4 tienen comportamiento significativamente diferente, especialmente respecto a resistencia al cortante.

---

### 18.6.3 Refuerzo Longitudinal

#### 18.6.3.1 Requisitos Basicos

| Parametro | Requisito |
|-----------|-----------|
| Barras continuas | Al menos **2** en caras superior e inferior |
| Refuerzo minimo | Segun 9.6.1.2 |
| Cuantia maxima (Grado 60) | rho <= **0.025** |
| Cuantia maxima (Grado 80) | rho <= **0.02** |

#### 18.6.3.2 Requisitos de Momento

| Ubicacion | Requisito |
|-----------|-----------|
| Momento positivo en cara de junta | >= **1/2** del momento negativo |
| Momento en cualquier seccion | >= **1/4** del momento maximo en cualquier junta |

#### 18.6.3.3 Empalmes de Traslape

**Permitidos** solo si:
- Refuerzo de confinamiento (estribos/espiral) sobre toda la longitud del empalme
- Espaciamiento transversal <= menor de **d/4** y **4 in**

**PROHIBIDOS** en:
| Ubicacion | Razon |
|-----------|-------|
| (a) Dentro de juntas | Fluencia esperada |
| (b) Dentro de 2h de cara de junta | Zona de articulacion plastica |
| (c) Dentro de 2h de secciones criticas de fluencia | Comportamiento ciclico |

#### 18.6.3.4 Empalmes Mecanicos y Soldados
- Mecanicos: segun 18.2.7
- Soldados: segun 18.2.8

#### 18.6.3.5 Pretensado (si no es segun 18.9.2.3)

| Requisito | Limite |
|-----------|--------|
| (a) Preesfuerzo promedio fpc | <= menor de **500 psi** y **f'c/10** |
| (b) Deformacion en tendones | < **0.01** bajo desplazamiento de diseno (tendones no adheridos en zonas plasticas) |
| (c) Resistencia por tendones en zona plastica | <= **1/4** de resistencia positiva o negativa |
| (d) Fatiga de anclajes | 50 ciclos entre 40% y 85% de fpu |

---

### 18.6.4 Refuerzo Transversal

#### 18.6.4.1 Regiones que Requieren Estribos/Cercos

| Region | Extension |
|--------|-----------|
| (a) Extremos de viga | 2h desde cara de columna hacia medio claro |
| (b) Zonas de fluencia | 2h a ambos lados de secciones donde se espera fluencia |

#### 18.6.4.2 Soporte Lateral
En regiones de 18.6.4.1:
- Barras longitudinales principales mas cercanas a caras de tension y compresion deben tener soporte segun 25.7.2.3 y 25.7.2.4
- Espaciamiento transversal de barras soportadas <= **14 in**
- Refuerzo de piel (9.7.2.3) no requiere soporte lateral

#### 18.6.4.3 Configuracion de Estribos Cerrados
Permitido formar con:
- Uno o mas U-stirrups con ganchos sismicos en ambos extremos
- Cerrados con grapa (crosstie)
- Grapas consecutivas que sujetan la misma barra deben tener ganchos de 90° en **lados opuestos**
- Si la losa confina de un solo lado: ganchos de 90° deben estar en ese lado

#### 18.6.4.4 Espaciamiento de Estribos

| Parametro | Limite |
|-----------|--------|
| Primer estribo | A no mas de **2 in** de cara de columna |
| Espaciamiento (Grado 60) | El menor de: d/4, 6 in, **6db** flexion principal |
| Espaciamiento (Grado 80) | El menor de: d/4, 6 in, **5db** flexion principal |

#### 18.6.4.5 Fuera de Zonas de Confinamiento
Estribos con ganchos sismicos a espaciamiento <= **d/2**.

#### 18.6.4.6 Vigas con Alta Carga Axial (Pu > Ag*f'c/10)
En longitudes de 18.6.4.1:
- Estribos segun 18.7.5.2-18.7.5.4

En resto de viga:
- Estribos segun 18.7.5.2
- Espaciamiento <= menor de 6 in, 6db (G60), 5db (G80)

Si recubrimiento > 4 in: Refuerzo transversal adicional con recubrimiento <= 4 in y espaciamiento <= 12 in.

---

### 18.6.5 Resistencia al Cortante

#### 18.6.5.1 Fuerzas de Diseno

Cortante de diseno Ve calculado considerando:
- Momentos de **resistencia probable Mpr** (signo opuesto) en caras de juntas
- Cargas gravitacionales factoradas y sismo vertical a lo largo del claro

```
Ve = (Mpr1 + Mpr2) / ln +/- (wu * ln) / 2

Donde:
- Mpr calculado con 1.25fy y phi = 1.0
- wu = (1.2 + 0.2*SDS)*D + 1.0L + 0.2S
```

#### 18.6.5.2 Refuerzo Transversal

En longitudes de 18.6.4.1, disenar para cortante asumiendo **Vc = 0** cuando AMBAS condiciones ocurren:

| Condicion | Descripcion |
|-----------|-------------|
| (a) | Cortante inducido por sismo >= 1/2 del cortante maximo requerido |
| (b) | Pu (incluyendo sismo) < Ag*f'c/20 |

---

## 18.7 COLUMNAS DE PORTICOS DE MOMENTO ESPECIALES

### 18.7.1 Alcance
**18.7.1.1**: Aplica a columnas que resisten flexion, cortante y fuerzas axiales.

### 18.7.2 Limites Dimensionales

**18.7.2.1**: Las columnas deben satisfacer:

| Parametro | Requisito |
|-----------|-----------|
| (a) Dimension minima | >= **12 in** (medida en linea recta a traves del centroide) |
| (b) Relacion de dimensiones | >= **0.4** (dimension menor / dimension perpendicular) |

---

### 18.7.3 Resistencia Minima a Flexion de Columnas

#### 18.7.3.1 Aplicabilidad
Columnas deben satisfacer 18.7.3.2 o 18.7.3.3, **excepto** en conexiones donde:
- La columna es discontinua arriba
- Pu < Ag*f'c/10

#### 18.7.3.2 Columna Fuerte - Viga Debil

```
Sum(Mnc) >= (6/5) * Sum(Mnb)     (Ec. 18.7.3.2)
```

Donde:
- **Sum(Mnc)** = Suma de Mn de columnas en la junta (caras de junta), calculado para Pu consistente con direccion de fuerzas que resulte en **menor** resistencia
- **Sum(Mnb)** = Suma de Mn de vigas en la junta (caras de junta)
  - En construccion T, incluir refuerzo de losa dentro del ancho efectivo (6.3.2) si esta desarrollado
- Momentos deben sumarse de modo que columnas se opongan a vigas
- Verificar para momentos de viga en **ambas direcciones**

#### 18.7.3.3 Si No Se Cumple 18.7.3.2
- Ignorar resistencia y rigidez lateral de las columnas involucradas
- Esas columnas deben cumplir **18.14**

> **Advertencia**: Columnas debiles pueden formar mecanismo de piso que lleve al colapso.

---

### 18.7.4 Refuerzo Longitudinal

#### 18.7.4.1 Area de Refuerzo
```
0.01*Ag <= Ast <= 0.06*Ag
```

#### 18.7.4.2 Columnas Circulares
Al menos **6 barras longitudinales**.

#### 18.7.4.3 Control de Agrietamiento por Adherencia
Sobre la altura libre, satisfacer **(a)** o **(b)**:

| Opcion | Requisito |
|--------|-----------|
| (a) | 1.25*ld <= lu/2 (seleccionar refuerzo longitudinal) |
| (b) | Ktr >= 1.2*db (seleccionar refuerzo transversal) |

#### 18.7.4.4 Empalmes
- Mecanicos: segun 18.2.7
- Soldados: segun 18.2.8
- **Traslape**: Solo en **mitad central** de la altura, disenados como empalmes de tension, con transversal segun 18.7.5.2 y 18.7.5.3

---

### 18.7.5 Refuerzo Transversal

#### 18.7.5.1 Longitud de Confinamiento lo

Refuerzo segun 18.7.5.2-18.7.5.4 sobre longitud lo desde cada cara de junta y a ambos lados de secciones de fluencia.

**lo** >= el mayor de:
| Condicion | Valor |
|-----------|-------|
| (a) | Profundidad de columna en cara de junta |
| (b) | 1/6 del claro libre |
| (c) | 18 in |

#### 18.7.5.2 Configuracion del Refuerzo Transversal

| Requisito | Descripcion |
|-----------|-------------|
| (a) Tipo | Espirales simples/superpuestas, aros circulares, o estribos rectangulares con/sin grapas |
| (b) Dobleces | Deben abrazar barras longitudinales perimetrales |
| (c) Grapas | Mismo tamano o menor que estribos, segun 25.7.2.2. Alternar extremos |
| (d) Soporte lateral | Segun 25.7.2.2 y 25.7.2.3 |
| (e) Espaciamiento hx | <= **14 in** entre barras soportadas |
| (f) Si Pu > 0.3Ag*f'c o f'c > 10,000 psi | Cada barra soportada por esquina de estribo o gancho sismico, hx <= **8 in** |

#### 18.7.5.3 Espaciamiento del Refuerzo Transversal

Espaciamiento s <= el menor de:
| Parametro | Limite |
|-----------|--------|
| (a) | 1/4 de dimension minima de columna |
| (b) Grado 60 | 6db de la barra longitudinal mas pequena |
| (c) Grado 80 | 5db de la barra longitudinal mas pequena |
| (d) so | Calculado por Ec. 18.7.5.3 |

```
so = 4 + (14 - hx) / 3     (Ec. 18.7.5.3)

Donde:
- so <= 6 in
- so no necesita ser < 4 in
```

#### 18.7.5.4 Cantidad de Refuerzo Transversal

**Tabla 18.7.5.4 - Refuerzo Transversal para Columnas Especiales**

| Tipo | Condiciones | Expresiones |
|------|-------------|-------------|
| **Ash/(s*bc) rectangular** | Pu <= 0.3Ag*f'c Y f'c <= 10,000 psi | Mayor de (a) y (b) |
| | Pu > 0.3Ag*f'c O f'c > 10,000 psi | Mayor de (a), (b) y (c) |
| **rho_s espiral/circular** | Pu <= 0.3Ag*f'c Y f'c <= 10,000 psi | Mayor de (d) y (e) |
| | Pu > 0.3Ag*f'c O f'c > 10,000 psi | Mayor de (d), (e) y (f) |

**Expresiones:**
```
(a) Ash/(s*bc) = 0.3 * (Ag/Ach - 1) * f'c/fyt

(b) Ash/(s*bc) = 0.09 * f'c/fyt

(c) Ash/(s*bc) = 0.2 * kf * kn * Pu/(fyt*Ach)

(d) rho_s = 0.45 * (Ag/Ach - 1) * f'c/fyt

(e) rho_s = 0.12 * f'c/fyt

(f) rho_s = 0.35 * kf * Pu/(fyt*Ach)
```

**Factores:**
```
kf = f'c/25000 + 0.6 >= 1.0     (Ec. 18.7.5.4a)

kn = nl / (nl - 2)              (Ec. 18.7.5.4b)
```
Donde nl = numero de barras longitudinales soportadas en el perimetro.

#### 18.7.5.5 Fuera de Longitud lo
- Espirales segun 25.7.3 O
- Estribos/grapas segun 25.7.2 y 25.7.4
- Espaciamiento s <= menor de: 6 in, 6db (G60), 5db (G80)

#### 18.7.5.6 Columnas bajo Miembros Discontinuos

**(a)** Refuerzo de 18.7.5.2-18.7.5.4 sobre **toda la altura** si Pu (sismo) > Ag*f'c/10
- Si se uso Omega_o: Limite = Ag*f'c/4

**(b)** Refuerzo transversal debe extenderse hacia:
- Miembro discontinuo: >= ld de la barra de columna mas grande (segun 18.8.5)
- Muro: >= ld de la barra mas grande en punto de terminacion
- Zapata/losa de cimentacion: >= 12 in

#### 18.7.5.7 Recubrimiento Excesivo
Si recubrimiento > 4 in: Refuerzo transversal adicional con recubrimiento <= 4 in y s <= 12 in.

---

### 18.7.6 Resistencia al Cortante

#### 18.7.6.1 Fuerzas de Diseno

**18.7.6.1.1**: Cortante Ve calculado de:
- Mpr maximo en cada cara de junta (rango de Pu factorado)
- Limitado por resistencia de junta basada en Mpr de vigas
- En ningun caso menor que Vu del analisis

```
Ve = (Mpr_top + Mpr_bottom) / lu
```

#### 18.7.6.2 Refuerzo Transversal

**18.7.6.2.1**: En longitudes lo, disenar asumiendo **Vc = 0** cuando AMBAS ocurren:

| Condicion | Descripcion |
|-----------|-------------|
| (a) | Cortante sismico >= 1/2 del cortante maximo en lo |
| (b) | Pu < Ag*f'c/20 |

---

## 18.8 JUNTAS DE PORTICOS DE MOMENTO ESPECIALES

### 18.8.1 Alcance
**18.8.1.1**: Aplica a juntas viga-columna de porticos especiales del SFRS.

### 18.8.2 General

#### 18.8.2.1 Fuerzas en Refuerzo
Fuerzas en refuerzo longitudinal de viga calculadas asumiendo esfuerzo de tension de **1.25fy**.

#### 18.8.2.2 Desarrollo de Refuerzo
Refuerzo terminado en junta:
- Extender a la **cara lejana** del nucleo de junta
- Desarrollar en tension segun **18.8.5**

#### 18.8.2.3 Profundidad de Junta

Profundidad h de junta (paralela al refuerzo de viga) >= el **mayor** de:

| Condicion | Requisito |
|-----------|-----------|
| (a) Grado 60 | (20/lambda)*db de la barra mas grande (lambda = 0.75 liviano, 1.0 normal) |
| (b) Grado 80 | **26db** de la barra mas grande |
| (c) Relacion de aspecto | h/2 de cualquier viga que genere cortante de junta |

> **Nota**: Para Grado 80, la junta debe ser de concreto normal (18.8.2.3.1).

---

### 18.8.3 Refuerzo Transversal

#### 18.8.3.1 Requisitos Generales
Segun 18.7.5.2, 18.7.5.3, 18.7.5.4 y 18.7.5.7, excepto 18.8.3.2.

#### 18.8.3.2 Reduccion Permitida
Donde vigas conectan en los **cuatro lados** y ancho de viga >= **3/4** del ancho de columna:
- Cantidad de refuerzo (18.7.5.4) puede reducirse a **la mitad**
- Espaciamiento (18.7.5.3) puede aumentarse a **6 in** dentro de h de la viga mas poco profunda

#### 18.8.3.3 Refuerzo de Viga Fuera del Nucleo
Refuerzo de viga fuera del nucleo de columna debe confinarse con transversal que:
- Pase a traves de la columna
- Satisfaga espaciamiento de 18.6.4.4
- Satisfaga 18.6.4.2 y 18.6.4.3

---

### 18.8.4 Resistencia al Cortante

#### 18.8.4.1 Fuerza Cortante de Junta
Vu calculado en plano a media altura de junta usando:
- Fuerzas de viga en tension/compresion (segun 18.8.2.1)
- Cortante de columna consistente con Mpr de vigas

#### 18.8.4.2 Factor phi
Segun **21.2.4.4**.

#### 18.8.4.3 Resistencia Nominal Vn

**Tabla 18.8.4.3 - Resistencia Nominal al Cortante de Junta**

| Columna | Viga | Confinamiento por Vigas Transversales (15.5.2.5) | Vn (lb) |
|---------|------|--------------------------------------------------|---------|
| Continua o cumple 15.5.2.3 | Continua o cumple 15.5.2.4 | Confinada | 20*lambda*sqrt(f'c)*Aj |
| | | No confinada | 15*lambda*sqrt(f'c)*Aj |
| | Otra | Confinada | 15*lambda*sqrt(f'c)*Aj |
| | | No confinada | 12*lambda*sqrt(f'c)*Aj |
| Otra | Continua o cumple 15.5.2.4 | Confinada | 15*lambda*sqrt(f'c)*Aj |
| | | No confinada | 12*lambda*sqrt(f'c)*Aj |
| | Otra | Confinada | 12*lambda*sqrt(f'c)*Aj |
| | | No confinada | 8*lambda*sqrt(f'c)*Aj |

Donde:
- lambda = 0.75 (concreto liviano), 1.0 (normal)
- Aj segun 15.5.2.2

---

### 18.8.5 Longitud de Desarrollo de Barras en Tension

#### 18.8.5.1 Barras con Gancho Estandar (No. 3 - No. 11)

```
ldh = fy * db / (65 * lambda * sqrt(f'c))     (Ec. 18.8.5.1)
```

**Limites minimos:**
| Concreto | ldh Minimo |
|----------|-----------|
| Normal | Mayor de: **8db** y **6 in** |
| Liviano | Mayor de: **10db** y **7.5 in** |

**Requisitos adicionales:**
- lambda = 0.75 (liviano), 1.0 (otros)
- Gancho dentro del nucleo confinado de columna o elemento de borde
- Gancho doblado hacia la junta

#### 18.8.5.2 Barras con Cabeza
Desarrollar **1.25fy** segun 25.4.4 sustituyendo 1.25fy por fy.

#### 18.8.5.3 Barras Rectas (No. 3 - No. 11)

ld >= el mayor de:

| Condicion | Factor |
|-----------|--------|
| (a) Concreto debajo de barra <= 12 in | **2.5** veces ldh (18.8.5.1) |
| (b) Concreto debajo de barra > 12 in | **3.25** veces ldh (18.8.5.1) |

#### 18.8.5.4 Barras Fuera del Nucleo Confinado
Barras rectas deben pasar a traves del nucleo confinado.
Porcion de ld fuera del nucleo confinado: aumentar por factor de **1.6**.

```
ldm = 1.6*ld - 0.6*ldc

Donde ldc = longitud dentro del nucleo confinado
```

#### 18.8.5.5 Barras con Epoxico
Multiplicar longitudes de 18.8.5.1, 18.8.5.3 y 18.8.5.4 por factores de 25.4.2.5 o 25.4.3.2.

---

## 18.9 PORTICOS ESPECIALES CON CONCRETO PREFABRICADO

### 18.9.1 Alcance
**18.9.1.1**: Aplica a porticos especiales construidos con prefabricado del SFRS.

### 18.9.2 General

#### 18.9.2.1 Conexiones Ductiles

Porticos con conexiones ductiles deben satisfacer:

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Requisitos de 18.6-18.8 para porticos colados en sitio |
| (b) | Vn de conexiones (22.9) >= **2Ve** (Ve segun 18.6.5.1 o 18.7.6.1) |
| (c) | Empalmes mecanicos de viga a >= **h/2** de cara de junta, Clase S |

#### 18.9.2.2 Conexiones Fuertes

Porticos con conexiones fuertes deben satisfacer:

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Requisitos de 18.6-18.8 |
| (b) | 18.6.2.1(a) aplica entre ubicaciones de fluencia intencionada |
| (c) | phi*Sn >= Se |
| (d) | Refuerzo principal continuo a traves de conexiones, desarrollado fuera de conexion fuerte y zona plastica |
| (e) Columna-columna | phi*Sn >= 1.4Se, phi*Mn >= 0.4Mpr, phi*Vn >= Ve |

#### 18.9.2.3 Sistemas Alternativos

Porticos que no satisfacen 18.9.2.1 o 18.9.2.2 deben satisfacer:

| Requisito | Descripcion |
|-----------|-------------|
| (a) | **ACI CODE-374.1** |
| (b) | Detalles y materiales representativos de los usados en estructura |
| (c) | Procedimiento de diseno define mecanismo, valores de aceptacion establecidos por ensayos |

---

## 18.10 MUROS ESTRUCTURALES ESPECIALES (INICIO)

### 18.10.1 Alcance

**18.10.1.1**: Aplica a muros especiales, muros acoplados ductiles, y todos los componentes incluyendo vigas de acople y pilares de muro del SFRS.

**18.10.1.2**: Muros especiales prefabricados segun 18.11 ademas de 18.10.

#### Tabla R18.10.1 - Provisiones de Diseno por Tipo de Segmento

| hw/lw | lw/bw <= 2.5 | 2.5 < lw/bw <= 6.0 | lw/bw > 6.0 |
|-------|--------------|--------------------|-----------|
| < 2.0 | Muro | Muro | Muro |
| >= 2.0 | Pilar (requisitos de columna - 18.10.8.1) | Pilar (columna o alternativo - 18.10.8.1) | Muro |

---

### 18.10.2 Refuerzo

#### 18.10.2.1 Refuerzo Distribuido Minimo

| Parametro | Requisito |
|-----------|-----------|
| rho_l (vertical) | >= **0.0025** |
| rho_t (horizontal) | >= **0.0025** (reducible a 11.6 si Vu <= lambda*sqrt(f'c)*Acv) |
| Espaciamiento maximo | **18 in** cada direccion |
| Refuerzo para Vn | Continuo, distribuido a traves del plano de corte |

#### 18.10.2.2 Dos Cortinas de Refuerzo
Requeridas si:
- Vu > 2*lambda*sqrt(f'c)*Acv, O
- hw/lw >= 2.0 (altura/longitud del muro completo)

#### 18.10.2.3 Desarrollo y Empalmes

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Refuerzo longitudinal se extiende >= 12 ft arriba donde no se requiere (pero no mas de ld sobre siguiente piso) |
| (b) | En zonas de fluencia: desarrollar para **1.25fy** |
| (c) | Empalmes de traslape en regiones de borde: **PROHIBIDOS** sobre hsx arriba y ld debajo de secciones criticas. hsx <= 20 ft |
| (d) | Empalmes mecanicos segun 18.2.7, soldados segun 18.2.8 |

> **Regiones de borde**: Incluyen longitudes de 18.10.6.4(a) y espesor de muro mas alla de intersecciones.

#### 18.10.2.4 Refuerzo Concentrado en Extremos
Para muros con hw/lw >= 2.0, continuos desde base hasta tope, con seccion critica unica:
- **Continuacion en Parte 2 del resumen**

---

## FORMULAS CLAVE PARA IMPLEMENTACION

### Resistencia Columna Fuerte - Viga Debil
```python
def strong_column_weak_beam(Mnc_list, Mnb_list):
    """
    Ec. 18.7.3.2: Verificacion columna fuerte - viga debil
    Mnc_list: Lista de Mn de columnas en junta
    Mnb_list: Lista de Mn de vigas en junta
    """
    sum_Mnc = sum(Mnc_list)
    sum_Mnb = sum(Mnb_list)
    return sum_Mnc >= 1.2 * sum_Mnb
```

### Espaciamiento de Confinamiento
```python
def spacing_so(hx):
    """
    Ec. 18.7.5.3: Espaciamiento maximo de confinamiento
    hx: Espaciamiento entre barras soportadas (in)
    """
    so = 4 + (14 - hx) / 3
    return max(4.0, min(so, 6.0))
```

### Factores de Confinamiento
```python
def factor_kf(fc):
    """
    Ec. 18.7.5.4a: Factor de resistencia del concreto
    fc: f'c en psi
    """
    return max(1.0, fc / 25000 + 0.6)

def factor_kn(nl):
    """
    Ec. 18.7.5.4b: Factor de efectividad de confinamiento
    nl: Numero de barras longitudinales soportadas
    """
    return nl / (nl - 2)
```

### Refuerzo Transversal de Columna
```python
import math

def Ash_required(fc, fyt, Ag, Ach, bc, s, Pu, nl, case='low'):
    """
    Tabla 18.7.5.4: Refuerzo transversal requerido
    case: 'low' si Pu <= 0.3Ag*fc y fc <= 10000 psi
          'high' en caso contrario
    """
    # Expresiones basicas
    expr_a = 0.3 * (Ag/Ach - 1) * fc/fyt
    expr_b = 0.09 * fc/fyt

    if case == 'low':
        Ash_sbc = max(expr_a, expr_b)
    else:
        kf = max(1.0, fc/25000 + 0.6)
        kn = nl / (nl - 2)
        expr_c = 0.2 * kf * kn * Pu / (fyt * Ach)
        Ash_sbc = max(expr_a, expr_b, expr_c)

    return Ash_sbc * s * bc
```

### Longitud de Desarrollo con Gancho
```python
def ldh_seismic(fy, db, fc, concrete_type='normal'):
    """
    Ec. 18.8.5.1: Longitud de desarrollo con gancho estandar
    """
    lambda_factor = 0.75 if concrete_type == 'lightweight' else 1.0
    ldh = fy * db / (65 * lambda_factor * math.sqrt(fc))

    if concrete_type == 'lightweight':
        ldh_min = max(10 * db, 7.5)
    else:
        ldh_min = max(8 * db, 6.0)

    return max(ldh, ldh_min)
```

### Resistencia al Cortante de Junta
```python
def joint_shear_strength(fc, Aj, column_type, beam_type, confined, concrete='normal'):
    """
    Tabla 18.8.4.3: Resistencia nominal al cortante de junta
    column_type: 'continuous' o 'other'
    beam_type: 'continuous' o 'other'
    confined: True/False
    """
    lambda_factor = 0.75 if concrete == 'lightweight' else 1.0

    if column_type == 'continuous':
        if beam_type == 'continuous':
            coef = 20 if confined else 15
        else:
            coef = 15 if confined else 12
    else:
        if beam_type == 'continuous':
            coef = 15 if confined else 12
        else:
            coef = 12 if confined else 8

    return coef * lambda_factor * math.sqrt(fc) * Aj
```

---

## REFERENCIAS CRUZADAS IMPORTANTES

| Tema | Seccion |
|------|---------|
| Combinaciones de carga | Capitulo 5 |
| Analisis | Capitulo 6 |
| Juntas viga-columna (general) | Capitulo 15 |
| Anclajes sismicos | 17.10 |
| Propiedades del concreto | Capitulo 19 |
| Propiedades del refuerzo | Capitulo 20 |
| Factores de reduccion phi | Capitulo 21, 21.2.4 |
| Resistencia al cortante | 22.5, 22.9 |
| Metodo puntal-tensor | Capitulo 23 |
| Desarrollo y empalmes | Capitulo 25 |
| Ganchos y configuracion transversal | 25.7 |

---

## NOTAS PARA IMPLEMENTACION EN APP

### Verificaciones Obligatorias por SDC

**SDC B:**
- Porticos ordinarios (18.3)
- Vigas: 2 barras continuas, 1/4 de area maxima inferior
- Columnas cortas: Verificar cortante

**SDC C:**
- Porticos intermedios (18.4)
- Cortante de diseno con 2E o Mpr
- Estribos cerrados en extremos de viga
- Cortante de columna con Omega_o*E

**SDC D, E, F:**
- Porticos especiales (18.6-18.8)
- Columna fuerte - viga debil
- Longitudes de desarrollo incrementadas
- Confinamiento extensivo
- Vc = 0 en zonas plasticas

### Flujo de Diseno Sugerido - Porticos Especiales

1. Verificar dimensiones minimas (18.6.2, 18.7.2)
2. Verificar columna fuerte - viga debil (18.7.3.2)
3. Disenar refuerzo longitudinal (limites de cuantia)
4. Calcular Ve por capacidad (Mpr)
5. Disenar refuerzo transversal de confinamiento
6. Verificar cortante de junta
7. Verificar longitudes de desarrollo
8. Detallar empalmes (ubicacion, tipo)

### Factores phi Tipicos (Capitulo 21)

| Condicion | phi |
|-----------|-----|
| Flexion (controlado por tension) | 0.90 |
| Cortante | 0.75 |
| Cortante de junta (especial) | 0.85 |
| Compresion (sin espiral) | 0.65 |
| Compresion (con espiral) | 0.75 |

---

*Resumen generado del ACI 318-25 Capitulo 18 (Parte 1: Secciones 18.1-18.10.2) para uso en desarrollo de aplicacion estructural.*

*Este resumen cubre: Alcance, requisitos generales, porticos ordinarios, intermedios y especiales (vigas, columnas, juntas), prefabricados, e inicio de muros especiales.*

*Continua en Parte 2: Secciones 18.10.3 en adelante (Muros especiales completo, diafragmas, cimentaciones, miembros no SFRS)*

*Fecha: 2025*
