# ACI 318-25 - CAPITULO 10: COLUMNAS (COLUMNS)
## Resumen para Diseno de Columnas

---

## 10.1 ALCANCE

### 10.1.1 Aplicabilidad
Aplica al diseno de columnas no pretensadas y pretensadas, incluyendo pedestales de hormigon armado.

### 10.1.2 Pedestales de Concreto Simple
Diseno segun Capitulo 14.

### Nota Importante
Las columnas compuestas acero-hormigon NO estan cubiertas. Ver ANSI/AISC 360.

---

## 10.2 GENERAL

### 10.2.1 Materiales
| Propiedad | Referencia |
|-----------|------------|
| Concreto | Capitulo 19 |
| Acero de refuerzo | Capitulo 20 |
| Embebidos | 20.6 |

### 10.2.2 Conexiones
| Tipo de Construccion | Referencia |
|---------------------|------------|
| Colado en sitio | Capitulo 15 |
| Prefabricado | 16.2 |
| Conexion a cimentacion | 16.3 |

---

## 10.3 LIMITES DE DISENO

### 10.3.1 Limites Dimensionales

#### 10.3.1.1 Secciones No Circulares
Para columnas cuadradas, octagonales u otras formas, se permite basar el area bruta, refuerzo requerido y resistencia en una seccion circular con diametro igual a la **menor dimension lateral**.

#### 10.3.1.2 Columnas Sobredimensionadas
Si la seccion es mayor a la requerida por cargas:
- Se permite usar un area efectiva reducida (>= 50% del area total)
- Refuerzo minimo basado en area requerida
- **NO aplica** a columnas de marcos especiales (Cap. 18)

#### 10.3.1.3 Columnas Monoliticas con Muros
Limite exterior de seccion efectiva: no mayor a **1.5 in** fuera del refuerzo transversal.

#### 10.3.1.4 Columnas con Espirales Entrelazadas
Limite exterior: a una distancia igual al recubrimiento minimo fuera de las espirales.

#### 10.3.1.5 Area Reducida
Si se usa area reducida (10.3.1.1-10.3.1.4), el analisis de otras partes de la estructura debe basarse en la seccion real.

---

## 10.4 RESISTENCIA REQUERIDA

### 10.4.1 General
| Requisito | Referencia |
|-----------|------------|
| Combinaciones de carga | Capitulo 5 |
| Analisis estructural | Capitulo 6 |

### 10.4.2 Fuerza Axial y Momento
**10.4.2.1** Considerar Pu y Mu simultaneos para cada combinacion de carga aplicable.

> **NOTA**: La combinacion critica puede no ser evidente. Verificar todas las combinaciones, no solo las de Pu,max y Mu,max.

---

## 10.5 RESISTENCIA DE DISENO

### 10.5.1 General
Para cada combinacion de carga:
```
phi*Pn >= Pu
phi*Mn >= Mu
phi*Vn >= Vu
phi*Tn >= Tu
```

Considerar interaccion entre efectos de carga.

### 10.5.1.2 Factor de Reduccion
phi segun **21.2**.

### 10.5.2 Fuerza Axial y Momento
Pn y Mn segun **22.4** (Diagrama de interaccion).

### 10.5.3 Cortante
Vn segun **22.5**.

### 10.5.4 Torsion
Si Tu >= phi*Tth (umbral de 22.7), considerar torsion segun **Capitulo 9**.

> **NOTA**: La torsion en columnas de edificios es tipicamente despreciable.

---

## 10.6 LIMITES DE REFUERZO

### 10.6.1 Refuerzo Longitudinal Minimo y Maximo

#### 10.6.1.1 Limites Generales
Para columnas no pretensadas y pretensadas con esfuerzo < 225 psi:
```
As,min = 0.01 * Ag
As,max = 0.08 * Ag
```

| Parametro | Valor | Justificacion |
|-----------|-------|---------------|
| Minimo 1% | 0.01*Ag | Resistir creep, retraccion, flexion |
| Maximo 8% | 0.08*Ag | Consolidacion del hormigon, similitud con ensayos |

> **RECOMENDACION**: Si hay empalmes por traslape, limitar a **4%** (zona de empalme tendria 8%).

#### 10.6.1.2 Columnas Sobredimensionadas
```
As,min >= 0.005 * Ag (del area real)
```

### 10.6.2 Refuerzo de Cortante Minimo

#### 10.6.2.1 Condicion
Proporcionar Av minimo donde:
```
Vu > 0.5 * phi * Vc
```

#### 10.6.2.2 Av,min
El mayor de (a) y (b):
```
(a) Av,min = 0.75 * sqrt(f'c) * bw * s / fyt

(b) Av,min = 50 * bw * s / fyt
```

---

## 10.7 DETALLADO DE REFUERZO

### 10.7.1 General

| Requisito | Referencia |
|-----------|------------|
| Recubrimiento | 20.5.1 |
| Desarrollo de barras | 25.4 |
| Barras en paquete | 25.6 |

#### 10.7.1.3 Barras con fy >= 80,000 psi
A lo largo de longitudes de desarrollo y empalme, proporcionar refuerzo transversal tal que:
```
Ktr >= 0.5 * db
```

### 10.7.2 Espaciamiento
Espaciamiento minimo segun **25.2**.

### 10.7.3 Refuerzo Longitudinal - Numero Minimo de Barras

| Tipo de Confinamiento | Barras Minimas |
|-----------------------|----------------|
| Estribos triangulares | 3 |
| Estribos rectangulares o circulares | 4 |
| Espirales o zunchos circulares (marcos especiales) | 6 |

> **NOTA**: Con menos de 8 barras en arreglo circular, la orientacion afecta significativamente la resistencia a momento.

### 10.7.4 Barras Longitudinales con Codo

#### 10.7.4.1 Pendiente Maxima
Pendiente del codo respecto al eje longitudinal: **no exceder 1 en 6**.
Porciones arriba y abajo del codo deben ser paralelas al eje.

#### 10.7.4.2 Desfase >= 3 in
Si la cara de la columna tiene desfase >= 3 in:
- No usar barras dobladas
- Usar dowels separados empalmados con barras adyacentes

---

## 10.7.5 EMPALMES DE REFUERZO LONGITUDINAL

### 10.7.5.1 General
**Tipos permitidos:**
- Empalmes por traslape
- Empalmes mecanicos
- Empalmes soldados a tope
- Empalmes de apoyo directo

### 10.7.5.2 Empalmes por Traslape

#### 10.7.5.2.1 Barras en Compresion
Se permiten empalmes por traslape a compresion.

**Reduccion de longitud permitida:**
| Tipo | Factor | Condicion |
|------|--------|-----------|
| Con estribos | 0.83 | Area efectiva >= 0.0015*h*s en ambas direcciones |
| Con espirales | 0.75 | Espirales cumplen 25.7.3 |

**Longitud minima de empalme: 12 in**

#### 10.7.5.2.2 Barras en Tension
Empalmes segun Tabla 10.7.5.2.2:

| Tension en Barra | Detalles | Clase |
|------------------|----------|-------|
| <= 0.5*fy | <= 50% barras empalmadas, escalonados >= ld | Clase A |
| <= 0.5*fy | Otros casos | Clase B |
| > 0.5*fy | Todos los casos | Clase B |

### 10.7.5.3 Empalmes de Apoyo Directo

#### 10.7.5.3.1 Condiciones
- Barras en compresion
- Empalmes escalonados o barras adicionales en ubicaciones de empalme
- Barras continuas con resistencia a traccion >= 0.25*fy*As de cada cara

---

## 10.7.6 REFUERZO TRANSVERSAL

### 10.7.6.1 General

| Tipo | Referencia |
|------|------------|
| Estribos | 25.7.2 |
| Espirales | 25.7.3 |
| Zunchos | 25.7.4 |

#### 10.7.6.1.3 Columnas Pretensadas (esfuerzo >= 225 psi)
No requieren cumplir espaciamiento de 16*db de 25.7.2.1.

#### 10.7.6.1.5 Pernos de Anclaje en Parte Superior
Encerrar pernos con refuerzo transversal que rodee al menos 4 barras longitudinales:
- Distribuir dentro de **5 in** de la parte superior
- Minimo: **2 No. 4** o **3 No. 3** estribos

#### 10.7.6.1.6 Acopladores Mecanicos en Extremos
Encerrar con refuerzo transversal:
- Distribuir dentro de **5 in** de los extremos
- Minimo: **2 No. 4** o **3 No. 3** estribos

### 10.7.6.2 Soporte Lateral con Estribos

#### 10.7.6.2.1 Ubicacion Inferior
Primer estribo: no mas de **s/2** sobre la parte superior de zapata o losa.

#### 10.7.6.2.2 Ubicacion Superior
| Condicion | Ubicacion del Ultimo Estribo |
|-----------|------------------------------|
| Sin vigas en todas las caras | <= s/2 bajo refuerzo de losa |
| Vigas en todas las caras | <= 3 in bajo refuerzo de viga mas baja |

### 10.7.6.3 Soporte Lateral con Espirales

#### 10.7.6.3.1 Ubicacion Inferior
Base de espiral: en la parte superior de zapata o losa.

#### Tabla 10.7.6.3.2 - Extension de Espirales en Parte Superior

| Condicion de Borde | Extension Requerida |
|--------------------|---------------------|
| Vigas en todas las caras | Hasta refuerzo inferior de elementos superiores |
| Sin vigas en todas las caras | Hasta refuerzo inferior + estribos adicionales hasta losa |
| Columnas con capiteles | Hasta donde diametro/ancho del capitel = 2x columna |

### 10.7.6.4 Soporte Lateral de Barras con Codo

#### 10.7.6.4.1 Fuerza Horizontal
Disenar estribos, espirales o partes de la estructura de piso para resistir:
```
Fh = 1.5 * (componente horizontal de fuerza en barra inclinada)
```

#### 10.7.6.4.2 Ubicacion
Estribos o espirales: dentro de **6 in** de los puntos de quiebre.

### 10.7.6.5 Cortante

#### 10.7.6.5.1 Refuerzo
Si se requiere: usar estribos, zunchos o espirales.

#### Tabla 10.7.6.5.2 - Espaciamiento Maximo de Refuerzo de Cortante

| Condicion | Columna No Pretensada | Columna Pretensada |
|-----------|----------------------|-------------------|
| Vs <= 4*sqrt(f'c)*bw*d | Menor de: d/2, 24 in | Menor de: 3h/4, 24 in |
| Vs > 4*sqrt(f'c)*bw*d | Menor de: d/4, 12 in | Menor de: 3h/8, 12 in |

---

## TABLA RESUMEN - REQUISITOS PRINCIPALES

| Parametro | Requisito |
|-----------|-----------|
| As,min | 0.01*Ag |
| As,max | 0.08*Ag |
| Barras minimas (rectangular) | 4 |
| Barras minimas (espiral) | 6 |
| Pendiente maxima de codo | 1:6 |
| Empalme minimo | 12 in |
| Estribos en anclajes | 2 No.4 o 3 No.3 dentro de 5 in |

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Propiedades del concreto | Capitulo 19 |
| Propiedades del acero | Capitulo 20 |
| Factores phi | 21.2 |
| Resistencia Pn, Mn | 22.4 |
| Resistencia Vn | 22.5 |
| Torsion | Capitulo 9, 22.7 |
| Estribos | 25.7.2 |
| Espirales | 25.7.3 |
| Zunchos | 25.7.4 |
| Longitudes de desarrollo | 25.4 |
| Longitudes de empalme | 25.5 |
| Columnas en marcos especiales | Capitulo 18 |
| Columnas compuestas | ANSI/AISC 360 |

---

*Resumen del ACI 318-25 Capitulo 10 para diseno de columnas.*
*Fecha: 2025*
