# 13.4 FUNDACIONES PROFUNDAS

## 13.4.1 General

### 13.4.1.1 Numero y Arreglo
El numero y arreglo de miembros de fundacion profunda debe determinarse de modo que las fuerzas y momentos aplicados no excedan la resistencia permisible de la fundacion profunda.

### 13.4.1.2 Miembros sin Soporte Lateral Adecuado
Porciones de miembros de fundacion profunda en aire, agua o suelos incapaces de proporcionar restriccion lateral adecuada para prevenir pandeo:
- Disenar como columna o pedestal segun provisiones aplicables del **Capitulo 10** y **Capitulo 14**
- phi determinado segun 13.4.3.2

### 13.4.1.3 Dimensiones Minimas

| Tipo de Miembro | Dimension Minima |
|-----------------|------------------|
| Precolados | Lado minimo >= **10 in.** |
| Colados en sitio | Diametro >= **12 in.** |
| Colados en sitio (residencial/utilidades, <=2 pisos, muros de carga) | Diametro >= **10 in.** |

### 13.4.1.4 Efectos de Mala Ubicacion
- El diseno debe considerar efectos de mala ubicacion potencial de cualquier miembro de fundacion profunda por al menos **3 in.**
- Se permite aumentar la resistencia axial a compresion de los miembros en **10%** al considerar efectos de mala ubicacion

### 13.4.1.5 Metodos de Diseno
Diseno de miembros de fundacion profunda segun **13.4.2** o **13.4.3**.

---

## 13.4.2 Resistencia Axial Admisible

### 13.4.2.1 Condiciones para Usar Resistencia Admisible
Se permite disenar miembros de fundacion profunda usando combinaciones de carga para diseno por esfuerzos admisibles en ASCE/SEI 7, Seccion 2.4, si:

**(a)** El miembro esta lateralmente soportado en toda su altura

**(b)** Las fuerzas aplicadas causan momentos flectores menores que el momento debido a una excentricidad accidental del **5%** del diametro o ancho del miembro

### Tabla 13.4.2.1 - Resistencia Maxima Admisible a Compresion

| Tipo de Miembro de Fundacion Profunda | Resistencia Maxima Admisible |
|---------------------------------------|------------------------------|
| Pilote perforado o augered colado en sitio sin camisa | Pa = 0.3*fc'*Ag + 0.4*fy*As |
| Pilote de concreto colado en sitio en roca o dentro de tubo/camisa metalica permanente (no satisface 13.4.2.3) | Pa = 0.33*fc'*Ag + 0.4*fy*As [1] |
| Pilote de concreto con camisa metalica confinado segun 13.4.2.3 | Pa = 0.4*fc'*Ag |
| Pilote de concreto precolado no presforzado | Pa = 0.33*fc'*Ag + 0.4*fy*As |
| Pilote de concreto precolado presforzado | Pa = (0.33*fc' - 0.27*fpc)*Ag |

**Notas:**
- Ag aplica al area bruta de la seccion transversal
- Si se usa camisa temporal o permanente, la cara interior de la camisa se considera la superficie del concreto
- [1] As no incluye la camisa, tubo o pipe de acero

### 13.4.2.2 Cuando No se Cumplen Condiciones
Si 13.4.2.1(a) o 13.4.2.1(b) no se satisface, disenar usando **diseno por resistencia** segun 13.4.3.

### 13.4.2.3 Pilotes con Camisa Metalica Confinados
Pilotes colados en sitio con camisa metalica se consideran confinados si:

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Diseno no usa la camisa para resistir ninguna porcion de la carga axial |
| (b) | Camisa con punta sellada e hincada con mandril |
| (c) | Espesor de camisa >= calibre estandar No. 14 (0.068 in.) |
| (d) | Camisa sin costura o con costuras de resistencia igual al material base |
| (e) | Relacion fy de camisa / fc' >= 6, y fy >= 30,000 psi |
| (f) | Diametro nominal del miembro <= **16 in.** |

### 13.4.2.4 Resistencias Admisibles Mayores
Se permiten resistencias admisibles mayores que las de Tabla 13.4.2.1 si son aceptadas por el funcionario de edificacion segun 1.10 y justificadas por **ensayos de carga**.

---

## 13.4.3 Diseno por Resistencia

**13.4.3.1** Diseno por resistencia permitido para todos los miembros de fundacion profunda.

**13.4.3.2** Diseno por resistencia segun **10.5** usando:
- Factores de reduccion de resistencia a compresion de Tabla 13.4.3.2 para carga axial sin momento
- Factores de reduccion de resistencia de Tabla 21.2.1 para tension, cortante y carga axial combinada con momento

> **NOTA**: Las provisiones de 22.4.2.4 y 22.4.2.5 no aplican a fundaciones profundas.

### Tabla 13.4.3.2 - Factores de Reduccion de Resistencia a Compresion phi

| Tipo de Miembro de Fundacion Profunda | Factor phi |
|---------------------------------------|------------|
| Pilote perforado o augered colado en sitio sin camisa [1] | **0.55** |
| Pilote de concreto colado en sitio en roca o dentro de tubo/camisa [2] (no satisface 13.4.2.3) | **0.60** |
| Pilote de concreto colado en sitio en tubo de acero [3] | **0.70** |
| Pilote de concreto con camisa metalica confinado segun 13.4.2.3 | **0.65** |
| Pilote de concreto precolado no presforzado | **0.65** |
| Pilote de concreto precolado presforzado | **0.65** |

**Notas:**
- [1] Factor de 0.55 representa un limite superior para condiciones de suelo bien entendidas con buena mano de obra
- [2] Para espesor de pared del tubo de acero < 0.25 in.
- [3] Espesor de pared del tubo de acero >= 0.25 in.

---

## 13.4.4 Fundaciones Profundas Coladas en Sitio

### 13.4.4.1 Requisitos de Refuerzo
Miembros de fundacion profunda colados en sitio sujetos a levantamiento o **Mu >= 0.4*Mcr** deben reforzarse, a menos que esten encerrados por tubo o pipe de acero estructural.

### 13.4.4.1.1 Refuerzo Minimo para SDC A o B

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Numero minimo de barras longitudinales segun 10.7.3.1 |
| (b) | Area de refuerzo longitudinal >= **0.0025*Ag** (excepto si resistencia de diseno >= 4/3 de resistencia requerida y Mu <= 0.4*Mcr) |
| (c) | Refuerzo longitudinal extendido desde la parte superior hasta **10 ft** o **3 diametros** del miembro (no exceder longitud del miembro) |
| (d) | Refuerzo transversal sobre la longitud minima de refuerzo longitudinal |
| (e) | Refuerzo transversal: estribos o espirales con diametro minimo de **3/8 in.** |
| (f) | Si refuerzo longitudinal requerido para compresion y Ast > 0.01*Ag: espaciamiento transversal segun 25.7.2.1 |

### 13.4.4.1.2 Alternativa para Miembros Pequenos
Para miembros de **24 in.** de diametro nominal o menor, si Pu < 0.75*phi*Pn o si se disena segun 13.4.2 y la carga axial de combinaciones admisibles < 0.75*Pa:

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Una o mas barras longitudinales en el centro del miembro con Ast >= 0.0025*Ag |
| (b) | Refuerzo longitudinal extendido desde la parte superior al menos **10 ft** (no exceder longitud del miembro) |

### 13.4.4.2 Colocacion de Refuerzo
Segun **26.5.8**.

---

## 13.4.5 Pilotes de Concreto Precolado

**13.4.5.1** Pilotes precolados que soportan edificios asignados a **SDC A o B** deben satisfacer 13.4.5.2 a 13.4.5.6.

**13.4.5.2** Refuerzo longitudinal en patron simetrico.

**13.4.5.3** Para pilotes precolados **no presforzados**:

| Requisito | Valor |
|-----------|-------|
| Numero minimo de barras | 4 |
| Area minima | **0.008*Ag** |

**13.4.5.4** Para pilotes precolados **presforzados**:
Esfuerzo compresivo efectivo promedio minimo segun Tabla 13.4.5.4.

### Tabla 13.4.5.4 - Esfuerzo Compresivo Minimo en Pilotes Presforzados

| Longitud del Pilote (ft) | Esfuerzo Compresivo Minimo (psi) |
|--------------------------|----------------------------------|
| <= 30 | 400 |
| 30 < L <= 50 | 550 |
| > 50 | 700 |

**13.4.5.5** Presfuerzo efectivo calculado basado en perdida total asumida de **30,000 psi** en el refuerzo presforzado.

**13.4.5.6** Refuerzo transversal segun Tablas 13.4.5.6(a) y 13.4.5.6(b):

### Tabla 13.4.5.6(a) - Tamano Minimo de Refuerzo Transversal

| Dimension Horizontal Minima h (in.) | Refuerzo Transversal Minimo (alambre) |
|------------------------------------|---------------------------------------|
| h <= 16 | W4, D4 |
| 16 < h < 20 | W4.5, D5 |
| h >= 20 | W5.5, D6 |

> **NOTA**: Si se usan barras, minimo No. 3 para todos los valores de h.

### Tabla 13.4.5.6(b) - Espaciamiento Maximo de Refuerzo Transversal

| Ubicacion en el Pilote | Espaciamiento Maximo c/c (in.) |
|------------------------|--------------------------------|
| Primeros 5 estribos/espirales en cada extremo | **1** |
| 24 in. desde cada extremo | **4** |
| Resto del pilote | **6** |

---

## 13.4.6 Cabezales de Pilotes (Pile Caps)

**13.4.6.1** Los cabezales deben cumplir 13.4.6.2 a 13.4.6.7. Requisitos aplican a todos los elementos de fundacion a los que se conectan miembros de fundacion profunda, incluyendo vigas de fundacion y losas de fundacion, excepto lo permitido en 13.4.6.3.1.

**13.4.6.2** Profundidad total del cabezal seleccionada tal que la profundidad efectiva del refuerzo inferior sea **al menos 12 in.**

**13.4.6.3** Miembros de fundacion profunda deben embeberse en el cabezal **al menos 3 in.** El cabezal debe extenderse mas alla del borde del miembro de fundacion profunda por **al menos 4 in.**

**13.4.6.3.1** Excepcion de 13.4.6.3 si el analisis demuestra que fuerzas y momentos (incluyendo diseno por mala ubicacion segun 13.4.1.4) pueden transferirse adecuadamente.

**13.4.6.4** Momentos y cortantes factorizados se permiten calcular con la reaccion de cualquier pilote asumida concentrada en el centroide de la seccion del pilote.

**13.4.6.5** Excepto para cabezales disenados segun 13.2.6.5 (puntal-tensor):

| Tipo | Requisito |
|------|-----------|
| Una direccion | phi*Vn >= Vu, donde Vn segun 22.5 |
| Dos direcciones | phi*vn >= vu, donde vn segun 22.6 |

**13.4.6.6** Si se disena con metodo puntal-tensor (13.2.6.5):
- Resistencia efectiva a compresion del concreto en puntales, fce, segun **23.4.3**

**13.4.6.7** Calculo de cortante factorizado en cualquier seccion a traves del cabezal:

| Posicion del Centro del Pilote | Contribucion al Cortante |
|--------------------------------|--------------------------|
| Centro a **dpile/2 o mas fuera** de la seccion | Reaccion completa del pilote |
| Centro a **dpile/2 o mas dentro** de la seccion | Cero cortante |
| Posiciones intermedias | Interpolacion lineal entre valor completo y cero |

**13.4.6.8** Para cabezales con pilotes espaciados a **<=4 diametros de pilote**, y para losas de fundacion con pilotes espaciados a **<=5 diametros de pilote**:

**(a) Cortante en una direccion:**
```
Vc = 2*lambda*sqrt(fc') * bw * d
```

**(b) Cortante en dos direcciones:**
Calcular vc segun 22.6, con factor de efecto de tamano **lambda_s = 1.0**

> **NOTA**: Cabezales y losas de fundacion con pilotes espaciados cercanamente exhiben mayor resistencia a cortante debido a accion de arco.

---

*ACI 318-25 Seccion 13.4*
