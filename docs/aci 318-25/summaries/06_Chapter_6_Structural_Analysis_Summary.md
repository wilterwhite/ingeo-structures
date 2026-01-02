# ACI 318-25 - CAPITULO 6: ANALISIS ESTRUCTURAL

---

## INDICE

- [6.1 Alcance](#61-alcance)
- [6.2 General](#62-general)
  - [6.2.5 Efectos de Esbeltez](#625-efectos-de-esbeltez)
- [6.3 Supuestos de Modelado](#63-supuestos-de-modelado)
- [6.4 Disposicion de Carga Viva](#64-disposicion-de-carga-viva)
- [6.5 Metodo Simplificado](#65-metodo-simplificado-vigas-continuas-y-losas-1-way)
- [6.6 Analisis Elastico Lineal de Primer Orden](#66-analisis-elastico-lineal-de-primer-orden)
  - [6.6.4 Metodo de Magnificacion de Momentos](#664-metodo-de-magnificacion-de-momentos)
  - [6.6.5 Redistribucion de Momentos](#665-redistribucion-de-momentos)
- [6.7 Analisis Elastico Lineal de Segundo Orden](#67-analisis-elastico-lineal-de-segundo-orden)
- [6.8 Analisis Inelastico](#68-analisis-inelastico)
- [6.9 Analisis de Elementos Finitos](#69-analisis-de-elementos-finitos)
- [Tablas Resumen](#tablas-resumen)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 6.1 ALCANCE

### 6.1.1 Aplicabilidad
Aplica a metodos de analisis, modelado de miembros y sistemas estructurales, y calculo de efectos de carga.

---

## 6.2 GENERAL

### 6.2.3 Metodos de Analisis Permitidos

| Metodo | Seccion | Descripcion |
|--------|---------|-------------|
| **(a)** Simplificado | 6.5 | Vigas continuas y losas unidireccionales (cargas gravitacionales) |
| **(b)** Elastico lineal 1er orden | 6.6 | Con magnificacion de momentos para esbeltez |
| **(c)** Elastico lineal 2do orden | 6.7 | Considera geometria deformada |
| **(d)** Inelastico | 6.8 | No linealidad del material |
| **(e)** Elementos finitos | 6.9 | Metodo general |

### 6.2.4 Metodos Adicionales Permitidos

| Aplicacion | Metodo | Referencia |
|------------|--------|------------|
| Losas bidireccionales (gravedad) | Diseno directo o marco equivalente | 6.2.4.1 |
| Muros esbeltos | Efectos fuera del plano | 11.8 |
| Diafragmas | Analisis especifico | 12.4.2 |
| Regiones D | Strut-and-Tie | Capitulo 23 |

---

## 6.2.5 EFECTOS DE ESBELTEZ

### 6.2.5.1 Cuando se Pueden Ignorar

#### (a) Columnas NO arriostradas (sway)
```
k*lu/r <= 22                                    (Ec. 6.2.5.1a)
```

#### (b) Columnas arriostradas (nonsway)
```
k*lu/r <= 34 + 12*(M1/M2)                       (Ec. 6.2.5.1b)
k*lu/r <= 40                                    (Ec. 6.2.5.1c)
```

**Convencion de signos:**
- M1/M2 **negativo** = curvatura simple
- M1/M2 **positivo** = curvatura doble

**Criterio de arriostramiento:**
Si rigidez lateral de elementos de arriostre >= 12 x rigidez lateral bruta de columnas → columnas se consideran arriostradas.

### 6.2.5.2 Radio de Giro

| Metodo | Formula |
|--------|---------|
| General | r = sqrt(Ig/Ag) |
| Columnas rectangulares | r = 0.30 x dimension en direccion de estabilidad |
| Columnas circulares | r = 0.25 x diametro |

### 6.2.5.3 Limite de Efectos de Segundo Orden
```
Mu (con efectos 2do orden) <= 1.4 * Mu (1er orden)
```
Si se excede, revisar sistema estructural.

---

## 6.3 SUPUESTOS DE MODELADO

### 6.3.1 General

#### 6.3.1.1 Rigideces
Las rigideces de miembros deben basarse en un conjunto razonable de supuestos, **consistentes** en todo el analisis.

#### 6.3.1.2 Modelo Simplificado para Gravedad
Para momentos y cortantes por cargas gravitacionales:
- Usar modelo limitado al nivel considerado
- Incluir columnas arriba y abajo
- Extremos lejanos de columnas: **empotrados**

### 6.3.2 Geometria de Vigas T

#### Tabla 6.3.2.1 - Ancho Efectivo de Ala

| Ubicacion del Ala | Ancho Efectivo (mas alla de cara del alma) |
|-------------------|-------------------------------------------|
| **Ambos lados** | Menor de: 8h, sw/2, ln/8 |
| **Un lado** | Menor de: 6h, sw/2, ln/12 |

Donde:
- h = espesor de losa
- sw = distancia libre al alma adyacente
- ln = luz libre

#### 6.3.2.2 Vigas T Aisladas
- Espesor de ala >= **0.5*bw**
- Ancho efectivo de ala <= **4*bw**

---

## 6.4 DISPOSICION DE CARGA VIVA

### 6.4.1 General
Para diseno de pisos/techos: carga viva solo en el nivel considerado.

### 6.4.2 Losas Unidireccionales y Vigas

| Condicion | Ubicacion de L factorada |
|-----------|--------------------------|
| **(a)** Mu+ maximo cerca de centro de luz | En el tramo y tramos alternos |
| **(b)** Mu- maximo en apoyo | Solo en tramos adyacentes |

### 6.4.3 Losas Bidireccionales

| Condicion | Requisito |
|-----------|-----------|
| L conocida (6.4.3.1) | Analizar para esa disposicion |
| L <= 0.75D o carga simultanea (6.4.3.2) | L en todos los paneles |
| Otros casos (6.4.3.3) | 75% de L en patrones criticos |

---

## 6.5 METODO SIMPLIFICADO (Vigas Continuas y Losas 1-Way)

### 6.5.1 Condiciones de Aplicabilidad

| Requisito | Condicion |
|-----------|-----------|
| (a) | Miembros prismaticos |
| (b) | Cargas uniformemente distribuidas |
| (c) | L <= 3D |
| (d) | Al menos dos tramos |
| (e) | Tramo mayor <= 1.20 x tramo menor |

### Tabla 6.5.2 - Momentos Aproximados

| Momento | Ubicacion | Condicion | Mu |
|---------|-----------|-----------|-----|
| **Positivo** | Tramo extremo | Extremo integral con soporte | wu*ln²/14 |
| | | Extremo no restringido | wu*ln²/11 |
| | Tramos interiores | Todos | wu*ln²/16 |
| **Negativo** | Cara interior apoyo exterior | Con viga de borde | wu*ln²/24 |
| | | Con columna | wu*ln²/16 |
| | Cara exterior 1er apoyo interior | Dos tramos | wu*ln²/9 |
| | | Mas de dos tramos | wu*ln²/10 |
| | Cara de otros apoyos | Todos | wu*ln²/11 |
| | Todos los apoyos | Losas ln <= 10 ft o rigidez col/viga > 8 | wu*ln²/12 |

**Nota:** Para momentos negativos, ln = promedio de luces claras adyacentes.

### Tabla 6.5.4 - Cortantes Aproximados

| Ubicacion | Vu |
|-----------|-----|
| Cara exterior del primer apoyo interior | **1.15 * wu*ln/2** |
| Cara de todos los otros apoyos | wu*ln/2 |

### 6.5.3 Redistribucion
**NO se permite** redistribuir momentos calculados con el metodo simplificado.

---

## 6.6 ANALISIS ELASTICO LINEAL DE PRIMER ORDEN

### 6.6.3 Propiedades de Seccion

#### Tabla 6.6.3.1.1(a) - Momentos de Inercia para Analisis a Nivel de Carga Factorada

| Miembro | Momento de Inercia | Area Axial | Area Cortante |
|---------|-------------------|------------|---------------|
| Columnas | **0.70*Ig** | 1.0*Ag | 1.0*Ashear |
| Muros (no fisurados) | **0.70*Ig** | 1.0*Ag | 1.0*Ashear |
| Muros (fisurados) | **0.35*Ig** | 1.0*Ag | 1.0*Ashear |
| Vigas | **0.35*Ig** | 1.0*Ag | 1.0*Ashear |
| Losas planas | **0.25*Ig** | 1.0*Ag | 1.0*Ashear |

**Nota:** Si hay cargas laterales sostenidas, dividir I de columnas y muros por (1 + βds).

#### Tabla 6.6.3.1.1(b) - Momentos de Inercia Alternativos

| Miembro | Minimo | Formula | Maximo |
|---------|--------|---------|--------|
| Columnas y muros | 0.35*Ig | (0.80 + 25*Ast/Ag)*(1 - Mu/(Pu*h) - 0.5*Pu/Po)*Ig | 0.875*Ig |
| Vigas, losas | 0.25*Ig | (0.10 + 25*rho)*(1.2 - 0.2*bw/d)*Ig | 0.5*Ig |

#### 6.6.3.2.2 Analisis en Servicio
```
I_servicio = 1.4 * I_factorado    (pero <= Ig)
```

---

## 6.6.4 METODO DE MAGNIFICACION DE MOMENTOS

### 6.6.4.3 Clasificacion Nonsway/Sway

| Criterio | Condicion para Nonsway |
|----------|------------------------|
| **(a)** Incremento de momentos | Efectos 2do orden <= 5% de momentos 1er orden |
| **(b)** Indice de estabilidad | Q <= 0.05 |

### 6.6.4.4 Propiedades de Estabilidad

#### 6.6.4.4.1 Indice de Estabilidad Q
```
Q = (Sum Pu * Delta_o) / (Vus * lc)             (Ec. 6.6.4.4.1)
```

Donde:
- Sum Pu = carga vertical factorada total del piso
- Vus = cortante horizontal del piso
- Delta_o = deriva de 1er orden
- lc = altura de piso

#### 6.6.4.4.2 Carga Critica de Pandeo
```
Pc = pi² * (EI)eff / (k*lu)²                    (Ec. 6.6.4.4.2)
```

#### 6.6.4.4.4 Rigidez Efectiva (EI)eff

| Ecuacion | Formula | Uso |
|----------|---------|-----|
| **(a)** | (EI)eff = 0.4*Ec*Ig / (1 + βdns) | Simplificada |
| **(b)** | (EI)eff = (0.2*Ec*Ig + Es*Ise) / (1 + βdns) | Con refuerzo |
| **(c)** | (EI)eff = Ec*I / (1 + βdns) | Usando Tabla 6.6.3.1.1(b) |

**Nota:** βdns = carga axial sostenida maxima / carga axial maxima (misma combinacion).

**Simplificacion:** Si βdns = 0.6, entonces (EI)eff = 0.25*Ec*Ig

---

### 6.6.4.5 Marcos Nonsway (Arriostrados)

#### 6.6.4.5.1 Momento de Diseno
```
Mc = delta * M2                                 (Ec. 6.6.4.5.1)
```

#### 6.6.4.5.2 Factor de Magnificacion
```
delta = Cm / (1 - Pu/(0.75*Pc)) >= 1.0          (Ec. 6.6.4.5.2)
```

#### 6.6.4.5.3 Factor Cm

| Condicion | Cm |
|-----------|-----|
| Sin cargas transversales entre apoyos | Cm = 0.6 - 0.4*(M1/M2) |
| Con cargas transversales entre apoyos | Cm = 1.0 |

**Convencion:** M1/M2 negativo (curvatura simple), positivo (curvatura doble).

#### 6.6.4.5.4 Momento Minimo
```
M2,min = Pu * (0.6 + 0.03*h)                    (Ec. 6.6.4.5.4)
```
Donde h esta en pulgadas y M2,min en lb-in.

---

### 6.6.4.6 Marcos Sway (No Arriostrados)

#### 6.6.4.6.1 Momentos en Extremos de Columna
```
M1 = M1ns + delta_s * M1s                       (Ec. 6.6.4.6.1a)
M2 = M2ns + delta_s * M2s                       (Ec. 6.6.4.6.1b)
```

Donde:
- M1ns, M2ns = momentos de cargas que no causan desplazamiento lateral
- M1s, M2s = momentos de cargas que causan desplazamiento lateral

#### 6.6.4.6.2 Factor de Magnificacion delta_s

| Metodo | Formula | Limite |
|--------|---------|--------|
| **(a)** Metodo Q | delta_s = 1/(1-Q) >= 1 | Solo si delta_s <= 1.5 |
| **(b)** Suma de P | delta_s = 1/(1 - Sum Pu/(0.75*Sum Pc)) >= 1 | Siempre permitido |
| **(c)** Analisis 2do orden | Por analisis | Siempre permitido |

**Nota:** Si delta_s > 1.5, solo se permiten metodos (b) o (c).

---

## 6.6.5 REDISTRIBUCION DE MOMENTOS

### 6.6.5.1 Condiciones
Se permite reducir momentos en secciones de momento maximo si:
- (a) Miembros a flexion son continuos
- (b) εt >= **0.0075** en la seccion donde se reduce el momento

### 6.6.5.3 Limite de Redistribucion
```
Redistribucion maxima = menor de (1000*εt)% y 20%
```

### Excepciones (NO se permite redistribucion)
- Momentos aproximados (6.5)
- Analisis inelastico (6.8)
- Patrones de carga de losas 2-way (6.4.3.3)

---

## 6.7 ANALISIS ELASTICO LINEAL DE SEGUNDO ORDEN

### 6.7.1 General

#### 6.7.1.1 Requisitos
Debe considerar:
- Influencia de cargas axiales
- Presencia de regiones fisuradas
- Efectos de duracion de carga

#### 6.7.1.2 Efectos de Esbeltez
Se deben considerar a lo largo de la longitud de la columna. Se permite usar 6.6.4.5.

### 6.7.2 Propiedades de Seccion
- **Cargas factoradas:** Usar propiedades de 6.6.3.1
- **Cargas de servicio:** I = 1.4 * I_factorado (pero <= Ig)

---

## 6.8 ANALISIS INELASTICO

### 6.8.1 General

#### 6.8.1.1 Requisitos
- Debe considerar **no linealidad del material**
- 1er orden: equilibrio en configuracion no deformada
- 2do orden: equilibrio en configuracion deformada

#### 6.8.1.2 Validacion
El procedimiento debe demostrar concordancia sustancial con resultados de ensayos fisicos.

#### 6.8.1.5 Redistribucion
**NO se permite** redistribuir momentos calculados por analisis inelastico.

---

## 6.9 ANALISIS DE ELEMENTOS FINITOS

### 6.9.1 Permiso
Se permite usar analisis de elementos finitos para determinar efectos de carga.

### 6.9.2 Modelo Apropiado
El modelo debe ser apropiado para el proposito previsto:
- Tipos de elementos capaces de representar la respuesta requerida
- Malla de tamano suficiente para capturar detalle estructural

### 6.9.3 Analisis Inelastico
Se requiere un analisis **separado** para cada combinacion de carga factorada (superposicion no aplica).

### 6.9.5 Tolerancia Dimensional
Dimensiones usadas en analisis deben estar dentro del **10%** de las especificadas, o repetir el analisis.

### 6.9.6 Redistribucion
**NO se permite** redistribuir momentos de analisis inelastico.

---

## TABLAS RESUMEN

### Rigideces Efectivas para Analisis

| Elemento | I para Cargas Factoradas | I para Servicio |
|----------|--------------------------|-----------------|
| Columnas | 0.70*Ig | min(0.98*Ig, Ig) |
| Muros (no fisurados) | 0.70*Ig | min(0.98*Ig, Ig) |
| Muros (fisurados) | 0.35*Ig | min(0.49*Ig, Ig) |
| Vigas | 0.35*Ig | min(0.49*Ig, Ig) |
| Losas planas | 0.25*Ig | min(0.35*Ig, Ig) |

### Limites de Esbeltez

| Tipo de Marco | Limite k*lu/r | Referencia |
|---------------|---------------|------------|
| Sway (no arriostrado) | 22 | 6.2.5.1(a) |
| Nonsway (arriostrado) | 34 + 12*(M1/M2) y 40 | 6.2.5.1(b)(c) |

### Factores de Magnificacion

| Tipo | Formula | Seccion |
|------|---------|---------|
| Nonsway | delta = Cm/(1 - Pu/0.75Pc) | 6.6.4.5.2 |
| Sway (Q) | delta_s = 1/(1-Q) | 6.6.4.6.2(a) |
| Sway (Sum P) | delta_s = 1/(1 - Sum Pu/0.75 Sum Pc) | 6.6.4.6.2(b) |

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Combinaciones de carga | Capitulo 5 |
| Muros esbeltos (fuera del plano) | 11.8 |
| Diafragmas | 12.4.2 |
| Strut-and-Tie | Capitulo 23 |
| Deflexiones | 24.2 |
| Modulo de elasticidad Ec | 19.2.2 |
| Factor k (nomogramas Jackson-Moreland) | Fig. R6.2.5.1 |

---

## FIGURAS CLAVE

### Fig. R6.2.5.1 - Factor de Longitud Efectiva k
- **(a) Marcos Nonsway:** k = 0.5 a 1.0
- **(b) Marcos Sway:** k >= 1.0

### Fig. R6.2.5.3 - Diagrama de Flujo para Esbeltez
1. Ignorar esbeltez? (6.2.5.1) → Si: Solo analisis 1er orden
2. Columnas como nonsway? (6.6.4.3) → Si: Magnificacion nonsway (6.6.4.5)
3. Marcos sway → Magnificacion sway (6.6.4.6) o analisis 2do orden
4. Verificar Mu(2do orden) <= 1.4*Mu(1er orden)

---

*Resumen del ACI 318-25 Capitulo 6 para analisis estructural.*
*Fecha: 2025*
