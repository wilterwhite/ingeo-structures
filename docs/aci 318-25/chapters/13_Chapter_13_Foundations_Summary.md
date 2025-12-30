# ACI 318-25 - CAPITULO 13: FUNDACIONES
## Foundations

---

## 13.1 ALCANCE

### 13.1.1 Aplicacion
Este capitulo aplica al diseno de fundaciones no presforzadas y presforzadas, incluyendo:

| Tipo | Categoria | Descripcion |
|------|-----------|-------------|
| (a) | Superficial | Zapatas corridas (Strip footings) |
| (b) | Superficial | Zapatas aisladas (Isolated footings) |
| (c) | Superficial | Zapatas combinadas (Combined footings) |
| (d) | Superficial | Losas de fundacion (Mat foundations) |
| (e) | Superficial | Vigas de fundacion (Grade beams) |
| (f) | Profunda | Cabezales de pilotes (Pile caps) |
| (g) | Profunda | Pilotes (Piles) |
| (h) | Profunda | Pilas perforadas (Drilled piers) |
| (i) | Profunda | Cajones (Caissons) |
| (j) | Muros | Muros de contencion en voladizo |
| (k) | Muros | Muros de contencion con contrafuertes |
| (l) | Muros | Muros de sotano (Basement walls) |

> **NOTA**: Las zapatas escalonadas e inclinadas se consideran subconjuntos de otros tipos de zapatas.

---

## 13.2 GENERALIDADES

### 13.2.1 Materiales

| Seccion | Requisito | Referencia |
|---------|-----------|------------|
| 13.2.1.1 | Propiedades de diseno del concreto | Capitulo 19 |
| 13.2.1.2 | Propiedades de diseno del refuerzo | Capitulo 20 |
| 13.2.1.3 | Empotramientos en concreto | 20.6 |

### 13.2.2 Conexion a Otros Miembros
**13.2.2.1** Diseno y detallado de conexiones de columnas, pedestales y muros colados en sitio y precolados a fundaciones segun **16.3**.

### 13.2.3 Efectos Sismicos

| Seccion | Requisito |
|---------|-----------|
| 13.2.3.1 | Miembros estructurales que se extienden debajo de la base de la estructura y transmiten fuerzas sismicas a la fundacion deben disenarse segun 18.2.2.3 |
| 13.2.3.2 | Para estructuras asignadas a **SDC C, D, E o F**: fundaciones que resisten o transfieren fuerzas sismicas deben disenarse segun 18.13 |

> **NOTA**: La base de una estructura, segun se define en el analisis, no necesariamente corresponde a la fundacion o nivel del suelo.

### 13.2.4 Losas sobre Terreno (Slabs-on-Ground)

| Seccion | Requisito |
|---------|-----------|
| 13.2.4.1 | Losas sobre terreno que transmiten cargas verticales o fuerzas laterales deben disenarse y detallarse segun este Codigo |
| 13.2.4.2 | Losas sobre terreno que transmiten fuerzas laterales como parte del sistema sismo-resistente deben disenarse segun 18.13 |

> **NOTA**: Las losas sobre terreno frecuentemente actuan como diafragma para mantener el edificio unido a nivel del suelo.

### 13.2.5 Concreto Simple
**13.2.5.1** Fundaciones de concreto simple deben disenarse segun **Capitulo 14**.

### 13.2.6 Criterios de Diseno

#### 13.2.6.1 Proporciones de Fundacion
Las fundaciones deben proporcionarse para:
- Efectos de apoyo (bearing)
- Estabilidad contra volteo
- Estabilidad contra deslizamiento en la interfaz suelo-fundacion

Segun el codigo general de edificacion.

#### 13.2.6.2 Resistencia a Cortante para Fundaciones Superficiales Rigidas
Para fundaciones superficiales continuamente apoyadas en suelo y disenadas asumiendo comportamiento rigido:

**(a) Cortante en una direccion:**
```
Vc = 2λ√fc' × bw × d
```

**(b) Cortante en dos direcciones:**
El factor de efecto de tamano λs (segun 22.6) puede tomarse igual a **1.0**

> **NOTA**: Esta provision se basa en el comportamiento satisfactorio historico de fundaciones superficiales sin considerar efectos de tamano.

#### 13.2.6.3 Cargas Factorizadas
Los miembros de fundacion deben disenarse para resistir cargas factorizadas y reacciones inducidas correspondientes, excepto lo permitido en 13.4.2.

#### 13.2.6.4 Metodos de Diseno Alternativos
Se permite disenar sistemas de fundacion por cualquier procedimiento que satisfaga equilibrio y compatibilidad geometrica.

#### 13.2.6.5 Metodo Puntal-Tensor
Se permite el diseno de fundaciones segun el metodo puntal-tensor del **Capitulo 23**.

#### 13.2.6.6 Momento Externo
El momento externo en cualquier seccion de zapata corrida, zapata aislada o cabezal de pilotes debe calcularse pasando un plano vertical a traves del miembro y calculando el momento de las fuerzas actuando sobre toda el area del miembro a un lado de ese plano.

---

### 13.2.7 Secciones Criticas para Fundaciones Superficiales y Cabezales

#### Tabla 13.2.7.1 - Ubicacion de Seccion Critica para Mu

| Miembro Soportado | Ubicacion de Seccion Critica |
|-------------------|------------------------------|
| Columna o pedestal | Cara de columna o pedestal |
| Columna con placa base de acero | A mitad de camino entre cara de columna y borde de placa |
| Muro de concreto | Cara del muro |
| Muro de mamposteria | A mitad de camino entre centro y cara del muro |

#### 13.2.7.2 Seccion Critica para Cortante
La ubicacion de la seccion critica para cortante factorizado:
- **Cortante en una direccion**: segun 7.4.3 y 8.4.3
- **Cortante en dos direcciones**: segun 8.4.4.1

Medida desde la ubicacion de la seccion critica para Mu en 13.2.7.1.

#### 13.2.7.3 Columnas Circulares o Poligonales
Se permite tratar como miembros cuadrados de area equivalente al ubicar secciones criticas para momento, cortante y desarrollo de refuerzo.

---

### 13.2.8 Desarrollo de Refuerzo en Fundaciones Superficiales y Cabezales

| Seccion | Requisito |
|---------|-----------|
| 13.2.8.1 | Desarrollo de refuerzo segun Capitulo 25 |
| 13.2.8.2 | Fuerza calculada en tension o compresion debe desarrollarse a cada lado de la seccion |
| 13.2.8.3 | Secciones criticas en mismas ubicaciones que 13.2.7.1 para momento maximo y donde ocurren cambios de seccion o refuerzo |
| 13.2.8.4 | Embedment adecuado para refuerzo en tension donde el esfuerzo no es directamente proporcional al momento (zapatas inclinadas, escalonadas o ahusadas) |

### 13.2.9 Recubrimiento de Concreto
**13.2.9.1** Recubrimiento para refuerzo en miembros de fundacion segun **20.5.1.3**.

---

## 13.3 FUNDACIONES SUPERFICIALES

### 13.3.1 General

| Seccion | Requisito |
|---------|-----------|
| 13.3.1.1 | Area minima de base proporcionada para no exceder la presion de apoyo permisible. Presiones permisibles determinadas por mecanica de suelos segun codigo general de edificacion |
| 13.3.1.2 | **Profundidad total** seleccionada tal que la profundidad efectiva del refuerzo inferior sea **al menos 6 in.** |
| 13.3.1.3 | En zapatas inclinadas, escalonadas o ahusadas: profundidad, ubicacion de escalones o angulo de inclinacion tal que los requisitos de diseno se satisfagan en cada seccion |

---

### 13.3.2 Fundaciones Superficiales en Una Direccion

**13.3.2.1** Diseno y detallado de fundaciones superficiales en una direccion (zapatas corridas, combinadas, vigas de fundacion) segun esta seccion y provisiones aplicables de **Capitulo 7** y **Capitulo 9**.

**13.3.2.2** El refuerzo debe distribuirse **uniformemente** a lo largo de todo el ancho de las zapatas en una direccion.

---

### 13.3.3 Zapatas Aisladas en Dos Direcciones

**13.3.3.1** Diseno y detallado segun esta seccion y provisiones aplicables de **Capitulo 7** y **Capitulo 8**.

**13.3.3.2** En zapatas cuadradas en dos direcciones:
- Refuerzo distribuido **uniformemente** a lo largo de todo el ancho de la zapata en ambas direcciones

**13.3.3.3** En zapatas rectangulares, el refuerzo debe distribuirse segun:

**(a) Direccion larga:**
- Refuerzo distribuido uniformemente a lo largo de todo el ancho de la zapata

**(b) Direccion corta:**
- Una porcion del refuerzo total, **γs × As**, distribuida uniformemente sobre una banda de ancho igual a la longitud del lado corto, centrada en el eje de columna o pedestal
- El resto del refuerzo, **(1 - γs) × As**, distribuido uniformemente fuera del ancho de banda central

**Factor de distribucion:**
```
γs = 2 / (β + 1)
```

Donde **β** = relacion de lado largo a lado corto de la zapata

> **NOTA**: Para minimizar errores de construccion, una practica comun es aumentar la cantidad de refuerzo en la direccion corta por 2β/(β + 1) y espaciarlo uniformemente.

---

### 13.3.4 Zapatas Combinadas y Losas de Fundacion en Dos Direcciones

| Seccion | Requisito |
|---------|-----------|
| 13.3.4.1 | Diseno y detallado segun esta seccion y provisiones aplicables del Capitulo 8 |
| 13.3.4.2 | El **metodo de diseno directo NO debe usarse** para disenar zapatas combinadas y losas de fundacion |
| 13.3.4.3 | Distribucion de presion de apoyo debe ser consistente con propiedades del suelo/roca y la estructura, y principios de mecanica de suelos |
| 13.3.4.4 | Refuerzo minimo en losas de fundacion no presforzadas segun **8.6.1.1** (As,min = 0.0018Ag) |

> **NOTA**: Recomendaciones detalladas en ACI PRC-336.2.

---

### 13.3.5 Muros como Vigas de Fundacion

| Seccion | Requisito |
|---------|-----------|
| 13.3.5.1 | Diseno segun provisiones aplicables del Capitulo 9 |
| 13.3.5.2 | Si el muro de viga de fundacion se considera viga profunda segun 9.9.1.1, el diseno debe satisfacer los requisitos de 9.9 |
| 13.3.5.3 | Muros de viga de fundacion deben satisfacer requisitos minimos de refuerzo de 11.6 |

---

### 13.3.6 Componentes de Muro de Muros de Contencion en Voladizo

#### 13.3.6.1 Vastago de Muro en Voladizo Simple
- Disenar como losa en una direccion segun provisiones aplicables del **Capitulo 7**

**Resistencia a cortante del concreto:**
```
Vc = 2λ√fc' × bw × d
```

> **NOTA**: Esta provision se basa en el desempeno historico satisfactorio de muros de contencion en voladizo disenados bajo ediciones anteriores del Codigo.

#### 13.3.6.2 Muros con Contrafuertes o Estribos
- Disenar el vastago como losa en dos direcciones segun provisiones aplicables del **Capitulo 8**

> **NOTA**: Muros con contrafuertes tienden a comportarse mas en accion bidireccional que unidireccional.

#### 13.3.6.3 Seccion Critica
| Tipo de Muro | Seccion Critica |
|--------------|-----------------|
| Espesor uniforme | Interfaz entre vastago y zapata |
| Espesor variable o ahusado | Investigar cortante y momento a lo largo de toda la altura |

---

### 13.3.7 Muros de Sotano

**13.3.7.1** Diseno de muros de sotano para resistir presion lateral de tierra fuera del plano:

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Disenar como losas en una direccion (Capitulo 7) o en dos direcciones (Capitulo 8) |
| (b) | Disenar para resistir presion hidrostatica, si aplica |
| (c) | Resistencia a cortante en una direccion: Vc = 2λ√fc' × bw × d |
| (d) | Para cortante en dos direcciones: factor de efecto de tamano λs = 1.0 |
| (e) | Satisfacer provisiones aplicables del Capitulo 18 |

**13.3.7.2** Para cargas distintas a presion lateral de tierra fuera del plano, satisfacer provisiones aplicables del **Capitulo 11**.

---

## 13.4 FUNDACIONES PROFUNDAS

### 13.4.1 General

#### 13.4.1.1 Numero y Arreglo
El numero y arreglo de miembros de fundacion profunda debe determinarse de modo que las fuerzas y momentos aplicados no excedan la resistencia permisible de la fundacion profunda.

#### 13.4.1.2 Miembros sin Soporte Lateral Adecuado
Porciones de miembros de fundacion profunda en aire, agua o suelos incapaces de proporcionar restriccion lateral adecuada para prevenir pandeo:
- Disenar como columna o pedestal segun provisiones aplicables del **Capitulo 10** y **Capitulo 14**
- ϕ determinado segun 13.4.3.2

#### 13.4.1.3 Dimensiones Minimas

| Tipo de Miembro | Dimension Minima |
|-----------------|------------------|
| Precolados | Lado minimo ≥ **10 in.** |
| Colados en sitio | Diametro ≥ **12 in.** |
| Colados en sitio (residencial/utilidades, ≤2 pisos, muros de carga) | Diametro ≥ **10 in.** |

#### 13.4.1.4 Efectos de Mala Ubicacion
- El diseno debe considerar efectos de mala ubicacion potencial de cualquier miembro de fundacion profunda por al menos **3 in.**
- Se permite aumentar la resistencia axial a compresion de los miembros en **10%** al considerar efectos de mala ubicacion

#### 13.4.1.5 Metodos de Diseno
Diseno de miembros de fundacion profunda segun **13.4.2** o **13.4.3**.

---

### 13.4.2 Resistencia Axial Admisible

#### 13.4.2.1 Condiciones para Usar Resistencia Admisible
Se permite disenar miembros de fundacion profunda usando combinaciones de carga para diseno por esfuerzos admisibles en ASCE/SEI 7, Seccion 2.4, si:

**(a)** El miembro esta lateralmente soportado en toda su altura

**(b)** Las fuerzas aplicadas causan momentos flectores menores que el momento debido a una excentricidad accidental del **5%** del diametro o ancho del miembro

#### Tabla 13.4.2.1 - Resistencia Maxima Admisible a Compresion

| Tipo de Miembro de Fundacion Profunda | Resistencia Maxima Admisible |
|---------------------------------------|------------------------------|
| Pilote perforado o augered colado en sitio sin camisa | Pa = 0.3fc'Ag + 0.4fyAs |
| Pilote de concreto colado en sitio en roca o dentro de tubo/camisa metalica permanente (no satisface 13.4.2.3) | Pa = 0.33fc'Ag + 0.4fyAs [1] |
| Pilote de concreto con camisa metalica confinado segun 13.4.2.3 | Pa = 0.4fc'Ag |
| Pilote de concreto precolado no presforzado | Pa = 0.33fc'Ag + 0.4fyAs |
| Pilote de concreto precolado presforzado | Pa = (0.33fc' - 0.27fpc)Ag |

**Notas:**
- Ag aplica al area bruta de la seccion transversal
- Si se usa camisa temporal o permanente, la cara interior de la camisa se considera la superficie del concreto
- [1] As no incluye la camisa, tubo o pipe de acero

#### 13.4.2.2 Cuando No se Cumplen Condiciones
Si 13.4.2.1(a) o 13.4.2.1(b) no se satisface, disenar usando **diseno por resistencia** segun 13.4.3.

#### 13.4.2.3 Pilotes con Camisa Metalica Confinados
Pilotes colados en sitio con camisa metalica se consideran confinados si:

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Diseno no usa la camisa para resistir ninguna porcion de la carga axial |
| (b) | Camisa con punta sellada e hincada con mandril |
| (c) | Espesor de camisa ≥ calibre estandar No. 14 (0.068 in.) |
| (d) | Camisa sin costura o con costuras de resistencia igual al material base |
| (e) | Relacion fy de camisa / fc' ≥ 6, y fy ≥ 30,000 psi |
| (f) | Diametro nominal del miembro ≤ **16 in.** |

#### 13.4.2.4 Resistencias Admisibles Mayores
Se permiten resistencias admisibles mayores que las de Tabla 13.4.2.1 si son aceptadas por el funcionario de edificacion segun 1.10 y justificadas por **ensayos de carga**.

---

### 13.4.3 Diseno por Resistencia

**13.4.3.1** Diseno por resistencia permitido para todos los miembros de fundacion profunda.

**13.4.3.2** Diseno por resistencia segun **10.5** usando:
- Factores de reduccion de resistencia a compresion de Tabla 13.4.3.2 para carga axial sin momento
- Factores de reduccion de resistencia de Tabla 21.2.1 para tension, cortante y carga axial combinada con momento

> **NOTA**: Las provisiones de 22.4.2.4 y 22.4.2.5 no aplican a fundaciones profundas.

#### Tabla 13.4.3.2 - Factores de Reduccion de Resistencia a Compresion ϕ

| Tipo de Miembro de Fundacion Profunda | Factor ϕ |
|---------------------------------------|----------|
| Pilote perforado o augered colado en sitio sin camisa [1] | **0.55** |
| Pilote de concreto colado en sitio en roca o dentro de tubo/camisa [2] (no satisface 13.4.2.3) | **0.60** |
| Pilote de concreto colado en sitio en tubo de acero [3] | **0.70** |
| Pilote de concreto con camisa metalica confinado segun 13.4.2.3 | **0.65** |
| Pilote de concreto precolado no presforzado | **0.65** |
| Pilote de concreto precolado presforzado | **0.65** |

**Notas:**
- [1] Factor de 0.55 representa un limite superior para condiciones de suelo bien entendidas con buena mano de obra
- [2] Para espesor de pared del tubo de acero < 0.25 in.
- [3] Espesor de pared del tubo de acero ≥ 0.25 in.

---

### 13.4.4 Fundaciones Profundas Coladas en Sitio

#### 13.4.4.1 Requisitos de Refuerzo
Miembros de fundacion profunda colados en sitio sujetos a levantamiento o **Mu ≥ 0.4Mcr** deben reforzarse, a menos que esten encerrados por tubo o pipe de acero estructural.

#### 13.4.4.1.1 Refuerzo Minimo para SDC A o B

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Numero minimo de barras longitudinales segun 10.7.3.1 |
| (b) | Area de refuerzo longitudinal ≥ **0.0025Ag** (excepto si resistencia de diseno ≥ 4/3 de resistencia requerida y Mu ≤ 0.4Mcr) |
| (c) | Refuerzo longitudinal extendido desde la parte superior hasta **10 ft** o **3 diametros** del miembro (no exceder longitud del miembro) |
| (d) | Refuerzo transversal sobre la longitud minima de refuerzo longitudinal |
| (e) | Refuerzo transversal: estribos o espirales con diametro minimo de **3/8 in.** |
| (f) | Si refuerzo longitudinal requerido para compresion y Ast > 0.01Ag: espaciamiento transversal segun 25.7.2.1 |

#### 13.4.4.1.2 Alternativa para Miembros Pequenos
Para miembros de **24 in.** de diametro nominal o menor, si Pu < 0.75ϕPn o si se disena segun 13.4.2 y la carga axial de combinaciones admisibles < 0.75Pa:

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Una o mas barras longitudinales en el centro del miembro con Ast ≥ 0.0025Ag |
| (b) | Refuerzo longitudinal extendido desde la parte superior al menos **10 ft** (no exceder longitud del miembro) |

#### 13.4.4.2 Colocacion de Refuerzo
Segun **26.5.8**.

---

### 13.4.5 Pilotes de Concreto Precolado

**13.4.5.1** Pilotes precolados que soportan edificios asignados a **SDC A o B** deben satisfacer 13.4.5.2 a 13.4.5.6.

**13.4.5.2** Refuerzo longitudinal en patron simetrico.

**13.4.5.3** Para pilotes precolados **no presforzados**:

| Requisito | Valor |
|-----------|-------|
| Numero minimo de barras | 4 |
| Area minima | **0.008Ag** |

**13.4.5.4** Para pilotes precolados **presforzados**:
Esfuerzo compresivo efectivo promedio minimo segun Tabla 13.4.5.4.

#### Tabla 13.4.5.4 - Esfuerzo Compresivo Minimo en Pilotes Presforzados

| Longitud del Pilote (ft) | Esfuerzo Compresivo Minimo (psi) |
|--------------------------|----------------------------------|
| ≤ 30 | 400 |
| 30 < L ≤ 50 | 550 |
| > 50 | 700 |

**13.4.5.5** Presfuerzo efectivo calculado basado en perdida total asumida de **30,000 psi** en el refuerzo presforzado.

**13.4.5.6** Refuerzo transversal segun Tablas 13.4.5.6(a) y 13.4.5.6(b):

#### Tabla 13.4.5.6(a) - Tamano Minimo de Refuerzo Transversal

| Dimension Horizontal Minima h (in.) | Refuerzo Transversal Minimo (alambre) |
|------------------------------------|---------------------------------------|
| h ≤ 16 | W4, D4 |
| 16 < h < 20 | W4.5, D5 |
| h ≥ 20 | W5.5, D6 |

> **NOTA**: Si se usan barras, minimo No. 3 para todos los valores de h.

#### Tabla 13.4.5.6(b) - Espaciamiento Maximo de Refuerzo Transversal

| Ubicacion en el Pilote | Espaciamiento Maximo c/c (in.) |
|------------------------|--------------------------------|
| Primeros 5 estribos/espirales en cada extremo | **1** |
| 24 in. desde cada extremo | **4** |
| Resto del pilote | **6** |

---

### 13.4.6 Cabezales de Pilotes (Pile Caps)

**13.4.6.1** Los cabezales deben cumplir 13.4.6.2 a 13.4.6.7. Requisitos aplican a todos los elementos de fundacion a los que se conectan miembros de fundacion profunda, incluyendo vigas de fundacion y losas de fundacion, excepto lo permitido en 13.4.6.3.1.

**13.4.6.2** Profundidad total del cabezal seleccionada tal que la profundidad efectiva del refuerzo inferior sea **al menos 12 in.**

**13.4.6.3** Miembros de fundacion profunda deben embeberse en el cabezal **al menos 3 in.** El cabezal debe extenderse mas alla del borde del miembro de fundacion profunda por **al menos 4 in.**

**13.4.6.3.1** Excepcion de 13.4.6.3 si el analisis demuestra que fuerzas y momentos (incluyendo diseno por mala ubicacion segun 13.4.1.4) pueden transferirse adecuadamente.

**13.4.6.4** Momentos y cortantes factorizados se permiten calcular con la reaccion de cualquier pilote asumida concentrada en el centroide de la seccion del pilote.

**13.4.6.5** Excepto para cabezales disenados segun 13.2.6.5 (puntal-tensor):

| Tipo | Requisito |
|------|-----------|
| Una direccion | ϕVn ≥ Vu, donde Vn segun 22.5 |
| Dos direcciones | ϕvn ≥ vu, donde vn segun 22.6 |

**13.4.6.6** Si se disena con metodo puntal-tensor (13.2.6.5):
- Resistencia efectiva a compresion del concreto en puntales, fce, segun **23.4.3**

**13.4.6.7** Calculo de cortante factorizado en cualquier seccion a traves del cabezal:

| Posicion del Centro del Pilote | Contribucion al Cortante |
|--------------------------------|--------------------------|
| Centro a **dpile/2 o mas fuera** de la seccion | Reaccion completa del pilote |
| Centro a **dpile/2 o mas dentro** de la seccion | Cero cortante |
| Posiciones intermedias | Interpolacion lineal entre valor completo y cero |

**13.4.6.8** Para cabezales con pilotes espaciados a **≤4 diametros de pilote**, y para losas de fundacion con pilotes espaciados a **≤5 diametros de pilote**:

**(a) Cortante en una direccion:**
```
Vc = 2λ√fc' × bw × d
```

**(b) Cortante en dos direcciones:**
Calcular vc segun 22.6, con factor de efecto de tamano **λs = 1.0**

> **NOTA**: Cabezales y losas de fundacion con pilotes espaciados cercanamente exhiben mayor resistencia a cortante debido a accion de arco.

---

## RESUMEN DE DIMENSIONES MINIMAS

### Fundaciones Superficiales

| Parametro | Valor Minimo |
|-----------|--------------|
| Profundidad efectiva refuerzo inferior | **6 in.** |

### Fundaciones Profundas

| Parametro | Valor Minimo |
|-----------|--------------|
| Lado minimo pilotes precolados | **10 in.** |
| Diametro pilotes colados en sitio | **12 in.** (10 in. para residencial ≤2 pisos) |
| Longitud refuerzo longitudinal | Mayor de 10 ft o 3 diametros |
| Refuerzo longitudinal minimo | 0.0025Ag |

### Cabezales de Pilotes

| Parametro | Valor Minimo |
|-----------|--------------|
| Profundidad efectiva refuerzo inferior | **12 in.** |
| Embedment de pilote en cabezal | **3 in.** |
| Extension de cabezal mas alla del pilote | **4 in.** |

---

## RESUMEN DE FACTORES DE REDUCCION DE RESISTENCIA

### Diseno por Resistencia Admisible (Tabla 13.4.2.1)

| Tipo | Coeficiente fc' | Coeficiente fy |
|------|-----------------|----------------|
| Sin camisa | 0.30 | 0.40 |
| En roca/camisa | 0.33 | 0.40 |
| Camisa confinada | 0.40 | - |
| Precolado no presforzado | 0.33 | 0.40 |
| Precolado presforzado | 0.33 - 0.27fpc/fc' | - |

### Diseno por Resistencia (Tabla 13.4.3.2)

| Tipo | Factor ϕ |
|------|----------|
| Sin camisa | 0.55 |
| En roca/camisa (t < 0.25 in.) | 0.60 |
| Tubo acero (t ≥ 0.25 in.) | 0.70 |
| Camisa confinada | 0.65 |
| Precolado no presforzado | 0.65 |
| Precolado presforzado | 0.65 |

---

## REFERENCIAS A OTROS CAPITULOS

| Tema | Capitulo/Seccion |
|------|------------------|
| Propiedades del concreto | 19 |
| Propiedades del refuerzo | 20 |
| Recubrimiento de concreto | 20.5.1.3 |
| Factores de reduccion | 21.2 |
| Resistencia a cortante una direccion | 22.5 |
| Resistencia a cortante dos direcciones | 22.6 |
| Metodo puntal-tensor | 23 |
| Desarrollo y empalmes | 25 |
| Losas en una direccion | Capitulo 7 |
| Losas en dos direcciones | Capitulo 8 |
| Vigas | Capitulo 9 |
| Columnas | Capitulo 10 |
| Muros | Capitulo 11 |
| Concreto simple | Capitulo 14 |
| Conexiones | 16.3 |
| Provisiones sismicas | Capitulo 18 |
| Colocacion de refuerzo | 26.5.8 |

---

## DOCUMENTOS DE REFERENCIA

| Documento | Tema |
|-----------|------|
| ACI PRC-336.2 | Recomendaciones para zapatas combinadas y losas de fundacion |
| ACI PRC-336.3 | Recomendaciones para pilas perforadas |
| ACI PRC-543 | Recomendaciones para pilotes de concreto |
| PCI 2019 | Practica recomendada para pilotes precolados presforzados |
| ASCE/SEI 7 | Combinaciones de carga para diseno por esfuerzos admisibles |
| IBC | Requisitos geotecnicos y de ensayo de carga |
| ANSI/AISC 360 | Miembros compuestos con tubo de acero |
| CRSI Handbook | Guia para zapatas rectangulares y cortante cerca de columna |

---

*Resumen del ACI 318-25 Capitulo 13 - Fundaciones.*
*Fecha: 2025*
