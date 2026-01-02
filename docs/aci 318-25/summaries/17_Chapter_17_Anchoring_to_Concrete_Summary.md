# ACI 318-25 - CAPITULO 17: ANCLAJES AL CONCRETO

---

## INDICE

- [17.1 Alcance](#171-alcance)
- [17.2 General](#172-general)
- [17.3 Requisitos Generales de Diseno](#173-requisitos-generales-de-diseno)
- [17.4 Resistencia de Diseno](#174-resistencia-de-diseno)
- [17.5 Requisitos de Analisis](#175-requisitos-de-analisis)
- [17.6 Resistencia a Tension de Anclajes](#176-resistencia-a-tension-de-anclajes)
  - [17.6.1 Resistencia del Acero en Tension](#1761-resistencia-del-acero-en-tension)
  - [17.6.2 Resistencia al Desprendimiento (Breakout)](#1762-resistencia-al-desprendimiento-del-concreto-breakout-en-tension)
  - [17.6.3 Resistencia al Arrancamiento (Pullout)](#1763-resistencia-al-arrancamiento-pullout-en-tension)
  - [17.6.4 Resistencia al Desprendimiento Lateral (Side-Face Blowout)](#1764-resistencia-al-desprendimiento-lateral-side-face-blowout)
  - [17.6.5 Resistencia de Adherencia (Adhesivos)](#1765-resistencia-de-adherencia-para-anclajes-adhesivos)
- [17.7 Resistencia a Cortante de Anclajes](#177-resistencia-a-cortante-de-anclajes)
  - [17.7.1 Resistencia del Acero en Cortante](#1771-resistencia-del-acero-en-cortante)
  - [17.7.2 Resistencia al Desprendimiento (Breakout) en Cortante](#1772-resistencia-al-desprendimiento-del-concreto-breakout-en-cortante)
  - [17.7.3 Resistencia al Desprendimiento Posterior (Pryout)](#1773-resistencia-al-desprendimiento-posterior-pryout-en-cortante)
- [17.8 Interaccion Tension-Cortante](#178-interaccion-tension-cortante)
- [17.9 Splitting (Hendimiento)](#179-splitting-hendimiento)
- [17.10 Requisitos Sismicos para Anclajes](#1710-requisitos-sismicos-para-anclajes)
- [17.11 Anclajes Adhesivos - Requisitos Detallados](#1711-anclajes-adhesivos---requisitos-detallados)
- [17.12 Instalacion de Anclajes](#1712-instalacion-de-anclajes)
- [17.13 Requisitos Especiales](#1713-requisitos-especiales)
- [Variables Clave](#variables-clave)
- [Resumen de Factores](#resumen-de-factores)
- [Lista de Verificacion](#lista-de-verificacion---diseno-de-anclajes)
- [Referencias Normativas](#referencias-normativas)

---

## 17.1 ALCANCE

### 17.1.1 Aplicabilidad
Este capitulo aplica al diseno de anclajes en concreto usados para transmitir cargas mediante:
- (a) Tension
- (b) Cortante
- (c) Combinacion de tension y cortante

### 17.1.2 Tipos de Anclajes Cubiertos
- Anclajes colados en sitio (cast-in anchors)
- Anclajes post-instalados (post-installed anchors)
  - Expansion (torque-controlled, displacement-controlled)
  - Undercut
  - Adhesivos

### 17.1.3 Exclusiones
Este capitulo NO aplica a:
- (a) Pasadores o barras de refuerzo usados como parte del sistema de refuerzo
- (b) Conectores instalados horizontalmente en juntas de mamposteria

---

## 17.2 GENERAL

### 17.2.1 Requisitos de Calificacion

**17.2.1.1** Anclajes post-instalados: evaluar segun ACI 355.2 o ACI 355.4

**17.2.1.2** Anclajes adhesivos: calificados para:
- (a) Uso en concreto fisurado y no fisurado
- (b) Categoria de sensibilidad segun ACI 355.4

### 17.2.2 Informacion de Instalacion
Documentos de construccion deben especificar:
- (a) Tipo y material del anclaje
- (b) Profundidad efectiva de empotramiento hef
- (c) Tamano y ubicacion
- (d) Para adhesivos: tiempo de curado, temperatura de instalacion

### 17.2.3 Materiales de Anclajes

**Tabla 17.2.3 - Materiales Permitidos**

| Tipo de Anclaje | Norma |
|-----------------|-------|
| Pernos con cabeza | ASTM F1554 (Grado 36, 55, 105) |
| Barras roscadas | ASTM A354 (Grado BC, BD) |
| | ASTM A449 |
| | ASTM F1554 |
| Conectores de cabeza | ASTM A29 (Grado 1015-1030) |
| | AWS D1.1 Tipo B |
| Anclajes post-instalados | Segun informe de calificacion |

### 17.2.4 Requisitos de Ductilidad

**17.2.4.1** Anclaje ductil:
- Elongacion >= 14% en 2 in
- Reduccion de area >= 30%

**17.2.4.2** Elemento de acero ductil:
- Resistencia nominal >= 1.2*carga de fluencia

---

## 17.3 REQUISITOS GENERALES DE DISENO

### 17.3.1 Resistencia de Diseno
```
phi*Nn >= Nua     (tension)
phi*Vn >= Vua     (cortante)
```

### 17.3.2 Distribucion de Cargas en Grupos

**17.3.2.1** Placa de base rigida (tension): distribucion elastica de fuerzas a anclajes

**17.3.2.2** Placa de base rigida (cortante):
- Cargas dentro del plano del grupo: distribucion elastica
- Cargas excentricas: considerar rigidez rotacional

### 17.3.3 Modos de Falla

**Tension:**
| Modo | Simbolo | Seccion |
|------|---------|---------|
| Acero del anclaje | Nsa | 17.6.1 |
| Desprendimiento del concreto (breakout) | Ncb, Ncbg | 17.6.2 |
| Arrancamiento (pullout) | Npn | 17.6.3 |
| Falla lateral del concreto (side-face blowout) | Nsb, Nsbg | 17.6.4 |
| Falla de adherencia (adhesivos) | Na, Nag | 17.6.5 |

**Cortante:**
| Modo | Simbolo | Seccion |
|------|---------|---------|
| Acero del anclaje | Vsa | 17.7.1 |
| Desprendimiento del concreto | Vcb, Vcbg | 17.7.2 |
| Desprendimiento de borde (pryout) | Vcp, Vcpg | 17.7.3 |

---

## 17.4 RESISTENCIA DE DISENO

### Tabla 17.4.1 - Factores de Reduccion de Resistencia (phi)

| Tipo de Carga | Elemento Ductil | Elemento No Ductil |
|---------------|-----------------|-------------------|
| **Tension - Acero** | 0.75 | 0.65 |
| **Tension - Concreto** | | |
| - Refuerzo suplementario | 0.75 | 0.75 |
| - Sin refuerzo suplementario | 0.70 | 0.70 |
| **Cortante - Acero** | 0.65 | 0.60 |
| **Cortante - Concreto** | | |
| - Refuerzo suplementario | 0.75 | 0.75 |
| - Sin refuerzo suplementario | 0.70 | 0.70 |

### 17.4.2 Condiciones para Refuerzo Suplementario
- Desarrollado a ambos lados del plano de falla
- Dimensionado para resistir la carga total del anclaje

---

## 17.5 REQUISITOS DE ANALISIS

### 17.5.1 Suposiciones de Diseno

**17.5.1.1** Rigidez de placa base:
- (a) Determinar por analisis, o
- (b) Asumir rigida si espesor >= mayor dimension entre anclajes / 10

**17.5.1.2** Excentricidad:
- Considerar excentricidad de carga respecto al centroide del grupo

### 17.5.2 Concreto Fisurado vs No Fisurado

**17.5.2.1** Asumir concreto fisurado a menos que se demuestre que:
- (a) Zona de compresion bajo cargas sostenidas
- (b) Pretensado suficiente para prevenir fisuracion

**17.5.2.2** Concreto no fisurado: usar factores psi_c,N y psi_c,V = 1.0 (o valores del informe de calificacion)

---

## 17.6 RESISTENCIA A TENSION DE ANCLAJES

### 17.6.1 Resistencia del Acero en Tension

**Ecuacion:**
```
Nsa = Ase,N * futa     [Ec. 17.6.1.2]
```

**Limites:**
- futa <= menor de: 1.9*fya, 125,000 psi

**Tabla 17.6.1.2 - Area de Seccion Efectiva (Ase,N)**

| Tipo de Anclaje | Ase,N |
|-----------------|-------|
| Perno con cabeza | Area de la parte roscada |
| Barra roscada | 0.7854*(d - 0.9743/n)^2 |
| Conectores AWS Tipo B | Area del vastago |

---

### 17.6.2 Resistencia al Desprendimiento del Concreto (Breakout) en Tension

**17.6.2.1 Anclaje Individual:**
```
Ncb = (ANc / ANco) * psi_ed,N * psi_c,N * psi_cp,N * Nb     [Ec. 17.6.2.1a]
```

**17.6.2.2 Grupo de Anclajes:**
```
Ncbg = (ANc / ANco) * psi_ec,N * psi_ed,N * psi_c,N * psi_cp,N * Nb     [Ec. 17.6.2.1b]
```

### 17.6.2.2 Area Proyectada de Falla

**ANco** (area de un anclaje sin efectos de borde o espaciamiento):
```
ANco = 9 * hef^2     [Ec. 17.6.2.2.1]
```

**ANc**: Area real proyectada, limitada por:
- Bordes
- Espaciamiento
- Espesor del miembro

### 17.6.2.3 Resistencia Basica al Desprendimiento

**Anclajes colados y post-instalados (Categoria 1):**
```
Nb = kc * lambda_a * sqrt(f'c) * hef^1.5     [Ec. 17.6.2.3.1]
```

| Tipo | kc |
|------|-----|
| Colados en sitio | 24 |
| Post-instalados | Segun informe de calificacion |

**Para hef > 11 in (Categoria 2):**
```
Nb = 16 * lambda_a * sqrt(f'c) * hef^(5/3)     [Ec. 17.6.2.3.2]
```

### Tabla 17.6.2.4 - Factores de Modificacion para Breakout en Tension

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_ec,N** (excentricidad) | Carga excentrica en grupo | 1 / (1 + 2*e'N / (3*hef)) <= 1.0 |
| | Carga concentrica | 1.0 |
| **psi_ed,N** (borde) | ca,min >= 1.5*hef | 1.0 |
| | ca,min < 1.5*hef | 0.7 + 0.3*(ca,min / (1.5*hef)) |
| **psi_c,N** (fisuracion) | Concreto fisurado | 1.0 |
| | Concreto no fisurado | 1.25 (colados), segun informe (post-instalados) |
| **psi_cp,N** (splitting post-instalados) | ca,min >= cac | 1.0 |
| | ca,min < cac | ca,min / cac >= (1.5*hef / cac) |

---

### 17.6.3 Resistencia al Arrancamiento (Pullout) en Tension

**17.6.3.1 Anclaje Individual:**
```
Npn = psi_c,P * Np     [Ec. 17.6.3.1]
```

### Tabla 17.6.3.2.2 - Resistencia Basica al Arrancamiento

| Tipo de Anclaje | Np |
|-----------------|-----|
| Perno con cabeza | 8 * Abrg * f'c |
| Perno con tuerca | 8 * Abrg * f'c |
| Gancho en J o L | 0.9 * f'c * eh * da |
| Post-instalado | Segun informe de calificacion |

**Limites para ganchos:**
- 3*da <= eh <= 4.5*da

### Tabla 17.6.3.3 - Factor de Modificacion psi_c,P

| Condicion | psi_c,P |
|-----------|---------|
| Concreto fisurado | 1.0 |
| Concreto no fisurado | 1.4 |

---

### 17.6.4 Resistencia al Desprendimiento Lateral (Side-Face Blowout)

**Aplica cuando:** hef > 2.5*ca1

**17.6.4.1 Anclaje Individual:**
```
Nsb = 160 * ca1 * sqrt(Abrg) * lambda_a * sqrt(f'c)     [Ec. 17.6.4.1]
```

**Si ca2 < 3*ca1:**
```
Nsb = (1 + ca2 / ca1) / 4 * 160 * ca1 * sqrt(Abrg) * lambda_a * sqrt(f'c)
```

**17.6.4.2 Grupo de Anclajes:**
```
Nsbg = (1 + s / (6*ca1)) * Nsb     [Ec. 17.6.4.2]
```
donde s = espaciamiento del anclaje externo al borde

---

### 17.6.5 Resistencia de Adherencia para Anclajes Adhesivos

**17.6.5.1 Anclaje Individual:**
```
Na = (ANa / ANao) * psi_ed,Na * psi_cp,Na * Nba     [Ec. 17.6.5.1a]
```

**17.6.5.2 Grupo de Anclajes:**
```
Nag = (ANa / ANao) * psi_ec,Na * psi_ed,Na * psi_cp,Na * Nba     [Ec. 17.6.5.1b]
```

### 17.6.5.2 Areas Proyectadas

**ANao:**
```
ANao = (2*cNa)^2     [Ec. 17.6.5.2.1]
```

**Radio de influencia critico:**
```
cNa = 10*da * (tau_uncr / 1100)^0.5     [Ec. 17.6.5.2.2]
```

### 17.6.5.3 Resistencia Basica de Adherencia

```
Nba = lambda_a * tau_cr * pi * da * hef     [Ec. 17.6.5.3.1]
```

**tau_cr**: Esfuerzo de adherencia caracteristico (del informe de calificacion)

### Tabla 17.6.5.4 - Factores de Modificacion para Adhesivos

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_ec,Na** | Carga excentrica | 1 / (1 + e'N / cNa) <= 1.0 |
| **psi_ed,Na** | ca,min >= cNa | 1.0 |
| | ca,min < cNa | 0.7 + 0.3*(ca,min / cNa) |
| **psi_cp,Na** | ca,min >= cac | 1.0 |
| | ca,min < cac | ca,min / cac |

---

## 17.7 RESISTENCIA A CORTANTE DE ANCLAJES

### 17.7.1 Resistencia del Acero en Cortante

**17.7.1.1 Anclaje Individual o Grupo (acero gobierna):**
```
Vsa = Ase,V * futa     [Ec. 17.7.1.2a] (anclajes colados con manga)
Vsa = 0.6 * Ase,V * futa     [Ec. 17.7.1.2b] (anclajes colados sin manga)
Vsa = 0.6 * Ase,V * futa     [Ec. 17.7.1.2c] (anclajes post-instalados)
```

**Limites:**
- futa <= menor de: 1.9*fya, 125,000 psi

**17.7.1.3** Efecto de brazo de palanca:
Si el cortante actua con brazo de palanca (ej: grout bajo placa):
```
Vsa = (Ase,V * futa) / (1 + l_g / (2*hef))
```
donde l_g = espesor del grout

### Tabla 17.7.1.2 - Area de Seccion Efectiva en Cortante (Ase,V)

| Tipo de Anclaje | Ase,V |
|-----------------|-------|
| Perno con cabeza | Area de la parte roscada |
| Barra roscada | 0.7854*(d - 0.9743/n)^2 |
| Conectores AWS Tipo B | Area del vastago |

---

### 17.7.2 Resistencia al Desprendimiento del Concreto (Breakout) en Cortante

**17.7.2.1 Anclaje Individual:**
```
Vcb = (AVc / AVco) * psi_ed,V * psi_c,V * psi_h,V * Vb     [Ec. 17.7.2.1a]
```

**17.7.2.2 Grupo de Anclajes:**
```
Vcbg = (AVc / AVco) * psi_ec,V * psi_ed,V * psi_c,V * psi_h,V * Vb     [Ec. 17.7.2.1b]
```

### 17.7.2.2 Areas Proyectadas de Falla en Cortante

**AVco** (area de un anclaje sin efectos de borde, esquina o espesor):
```
AVco = 4.5 * ca1^2     [Ec. 17.7.2.2.1]
```

**AVc**: Area real proyectada, limitada por:
- Bordes perpendiculares (1.5*ca1 a cada lado)
- Espesor del miembro (1.5*ca1)
- Espaciamiento entre anclajes

### 17.7.2.3 Resistencia Basica al Desprendimiento en Cortante

**Ecuacion General:**
```
Vb = (7 * (le/da)^0.2 * sqrt(da)) * lambda_a * sqrt(f'c) * ca1^1.5     [Ec. 17.7.2.3.1a]
```

**Ecuacion Simplificada (cuando le >= 8*da):**
```
Vb = 9 * lambda_a * sqrt(f'c) * ca1^1.5     [Ec. 17.7.2.3.1b]
```

**Limites:**
- le <= hef (anclajes de expansion y undercut)
- le <= 8*da

### Tabla 17.7.2.4 - Factores de Modificacion para Breakout en Cortante

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_ec,V** (excentricidad) | Carga excentrica en grupo | 1 / (1 + 2*e'V / (3*ca1)) <= 1.0 |
| | Carga concentrica | 1.0 |
| **psi_ed,V** (borde) | ca2 >= 1.5*ca1 | 1.0 |
| | ca2 < 1.5*ca1 | 0.7 + 0.3*(ca2 / (1.5*ca1)) |
| **psi_c,V** (fisuracion) | Concreto fisurado, sin refuerzo de borde | 1.0 |
| | Concreto fisurado, con refuerzo No. 4+ | 1.2 |
| | Concreto fisurado, con refuerzo y estribos s <= 4 in | 1.4 |
| | Concreto no fisurado | 1.4 |
| **psi_h,V** (espesor) | ha >= 1.5*ca1 | 1.0 |
| | ha < 1.5*ca1 | sqrt(1.5*ca1 / ha) |

### 17.7.2.5 Cortante Paralelo al Borde

Si cortante actua paralelo al borde:
```
Vcb,parallel = 2 * Vcb     [Ec. 17.7.2.5.1]
```

Para cortante en angulo con el borde, resolver componentes.

### 17.7.2.6 Anclajes en Esquinas

Para anclajes cerca de dos bordes perpendiculares:
- Calcular Vcb para cada borde
- Usar el **menor** de los dos valores

---

### 17.7.3 Resistencia al Desprendimiento Posterior (Pryout) en Cortante

**17.7.3.1** Aplica a anclajes alejados del borde donde pryout puede gobernar

**Anclaje Individual:**
```
Vcp = kcp * Ncp     [Ec. 17.7.3.1a]
```

**Grupo de Anclajes:**
```
Vcpg = kcp * Ncpg     [Ec. 17.7.3.1b]
```

### Tabla 17.7.3.1 - Factor kcp

| Profundidad Efectiva | kcp |
|---------------------|-----|
| hef < 2.5 in | 1.0 |
| hef >= 2.5 in | 2.0 |

**Donde:**
- Ncp = Ncb para anclaje individual (desprendimiento en tension)
- Ncpg = Ncbg para grupo de anclajes

---

## 17.8 INTERACCION TENSION-CORTANTE

### 17.8.1 Cuando Verificar Interaccion

**No se requiere verificar si:**
- (a) Vua <= 0.2*phi*Vn, o
- (b) Nua <= 0.2*phi*Nn

**Se requiere verificar si:**
- Vua > 0.2*phi*Vn Y Nua > 0.2*phi*Nn

### 17.8.2 Ecuacion de Interaccion Trilineal

```
Nua / (phi*Nn) + Vua / (phi*Vn) <= 1.2     [Ec. 17.8.2]
```

### 17.8.3 Metodo Alternativo - Interaccion Eliptica

Se permite usar:
```
(Nua / (phi*Nn))^(5/3) + (Vua / (phi*Vn))^(5/3) <= 1.0     [Ec. 17.8.3]
```

### Diagrama de Interaccion

```
     Nua/(phi*Nn)
          |
     1.0  +--------+
          |        |\
          |        | \  Lineal (1.2)
          |        |  \
     0.2  +........+...+
          |        |   |
          +--------+---+---- Vua/(phi*Vn)
               0.2   1.0
```

---

## 17.9 SPLITTING (HENDIMIENTO)

### 17.9.1 General
Verificar que las fuerzas de splitting inducidas por la instalacion y carga no causen falla prematura.

### 17.9.2 Requisitos de Distancia Minima

### Tabla 17.9.2.1 - Distancias Minimas al Borde y Espaciamiento

| Tipo de Anclaje | ca,min | s,min |
|-----------------|--------|-------|
| Colados en sitio | Segun recubrimiento (Cap. 20) | Segun 17.9.3 |
| Post-instalados (sin torque) | 6*da | 6*da |
| Post-instalados (torque-controlled) | Segun informe ACI 355.2 | Segun informe |
| Adhesivos | Segun informe ACI 355.4 | Segun informe |

### 17.9.3 Espaciamiento Minimo

**Anclajes colados en sitio:**
```
s,min >= 4*da     [para tension]
s,min >= 4*da     [para cortante]
```

**Anclajes post-instalados:**
- Segun informe de calificacion
- Minimo 6*da si no se especifica

### 17.9.4 Distancia Critica al Borde (cac)

Para anclajes post-instalados, verificar splitting usando:
```
cac = valor del informe de calificacion
```

**Si ca,min < cac:**
- Aplicar factor psi_cp,N (ver 17.6.2.4)
- Verificar resistencia reducida al desprendimiento

### 17.9.5 Control de Splitting en Bordes Delgados

**17.9.5.1** Si ha < 1.5*hef:
- Limitar carga o
- Proveer refuerzo de confinamiento

**17.9.5.2** Refuerzo de confinamiento:
- Estribos o amarres que encierren los anclajes
- Espaciamiento <= 3 in desde la superficie de carga

---

## 17.10 REQUISITOS SISMICOS PARA ANCLAJES

### 17.10.1 Alcance

**17.10.1.1** Aplica a anclajes en estructuras asignadas a SDC C, D, E o F que:
- (a) Resisten cargas sismicas, o
- (b) Soporten componentes que requieren proteccion sismica

**17.10.1.2** Excepciones - No aplica a:
- Anclajes en miembros de concreto simple (Cap. 14)
- Anclajes disenados para E multiplicado por omega_o

### 17.10.2 Categorias de Diseno Sismico C, D, E, F

### Tabla 17.10.2 - Requisitos por SDC

| SDC | Requisitos |
|-----|------------|
| C | 17.10.3, 17.10.4, 17.10.6, 17.10.7 |
| D, E, F | Todos los requisitos de 17.10 |

### 17.10.3 Anclajes en Zonas de Rotulas Plasticas

**17.10.3.1** Anclajes NO deben ubicarse en:
- Zonas de rotulas plasticas de elementos del sistema sismo-resistente

**17.10.3.2** Excepcion:
- Anclajes usados para conectar elementos de concreto prefabricado
- Anclajes usados para conexiones que desarrollan la resistencia probable del miembro

### 17.10.4 Requisitos de Ductilidad

**17.10.4.1** Anclajes deben disenarse para comportamiento ductil:

**(a)** El elemento de acero debe ser ductil (17.2.4) Y gobernar la falla:
```
phi*Nn,acero <= phi*Nn,concreto * 1.0
phi*Vn,acero <= phi*Vn,concreto * 1.0
```

**(b)** O disenar para resistencia del mecanismo de fluencia del accesorio:
```
Nua = 1.4 * Sy     [tension]
Vua = 1.4 * Sy     [cortante]
```
donde Sy = fuerza de fluencia del accesorio conectado

### 17.10.5 Requisitos Adicionales para SDC D, E, F

**17.10.5.1** Anclajes de un solo anclaje:
- Disenar para comportamiento ductil (17.10.4), o
- Proveer refuerzo de anclaje (17.10.5.3)

**17.10.5.2** Grupos de anclajes:
- Minimo 4 anclajes
- Minimo 2 anclajes en cada direccion
- Disenar para redistribucion de carga

**17.10.5.3** Refuerzo de anclaje:
- Desarrollado a ambos lados del plano de falla
- Encerrado por estribos o amarres
- phi = 0.75

### 17.10.6 Factores de Reduccion Sismicos

**Tabla 17.10.6.1 - Factores phi para Cargas Sismicas**

| Modo de Falla | Sin Refuerzo Suplementario | Con Refuerzo Suplementario |
|---------------|---------------------------|---------------------------|
| Acero - tension (ductil) | 0.75 | 0.75 |
| Acero - tension (no ductil) | 0.65 | 0.65 |
| Concreto - tension | 0.70 | 0.75 |
| Acero - cortante (ductil) | 0.65 | 0.65 |
| Acero - cortante (no ductil) | 0.60 | 0.60 |
| Concreto - cortante | 0.70 | 0.75 |

### 17.10.7 Anclajes Post-Instalados en Aplicaciones Sismicas

**17.10.7.1** Anclajes de expansion:
- Solo tipo torque-controlled calificados para sismo
- Informe de calificacion debe indicar uso sismico

**17.10.7.2** Anclajes undercut:
- Permitidos si calificados para sismo segun ACI 355.2

**17.10.7.3** Anclajes adhesivos:
- Calificados segun ACI 355.4 para uso sismico
- Categoria 1 o 2 segun carga sostenida

---

## 17.11 ANCLAJES ADHESIVOS - REQUISITOS DETALLADOS

### 17.11.1 General

**17.11.1.1** Anclajes adhesivos calificados segun ACI 355.4

**17.11.1.2** Categorias de anclajes adhesivos:

| Categoria | Descripcion | Aplicacion |
|-----------|-------------|------------|
| 1 | Baja sensibilidad a condiciones de instalacion | General |
| 2 | Sensibilidad moderada | Instalacion controlada |
| 3 | Alta sensibilidad | No permitido en ACI 318 |

### 17.11.2 Resistencia de Adherencia

**17.11.2.1** Esfuerzo de adherencia caracteristico (tau_cr):
- Obtenido del informe de calificacion ACI 355.4
- Valores para concreto fisurado y no fisurado

**Tabla 17.11.2.1 - Valores Tipicos de tau_cr**

| Tipo de Adhesivo | tau_cr,fisurado (psi) | tau_cr,no fisurado (psi) |
|------------------|----------------------|-------------------------|
| Epoxico | 800 - 1400 | 1200 - 2000 |
| Vinilester | 700 - 1200 | 1000 - 1800 |
| Hibrido | 750 - 1300 | 1100 - 1900 |

*Valores tipicos - usar valores del informe de calificacion especifico*

### 17.11.3 Cargas Sostenidas en Anclajes Adhesivos

**17.11.3.1** Factor de reduccion por carga sostenida:
```
alpha_N,seis = factor del informe de calificacion
```

**17.11.3.2** Para cargas sostenidas >= 55% de la carga total:
- Usar tau_cr reducido
- Verificar creep (fluencia lenta)

### 17.11.4 Temperatura de Instalacion y Servicio

**Tabla 17.11.4.1 - Rangos de Temperatura**

| Parametro | Rango Permitido |
|-----------|-----------------|
| Temperatura de instalacion | Segun informe (tipico: 40°F a 110°F) |
| Temperatura de servicio | Segun informe (tipico: -40°F a 175°F) |
| Temperatura maxima a corto plazo | Segun informe |

### 17.11.5 Humedad y Condiciones de Instalacion

**17.11.5.1** Preparacion del orificio:
- Perforar con broca de carburo
- Limpiar con cepillo y soplado (ciclos especificados)
- Superficie seca o segun informe

**17.11.5.2** Condiciones de humedad:
- Seco: instalacion estandar
- Humedo: solo si adhesivo calificado para humedo
- Sumergido: solo si adhesivo calificado especificamente

### 17.11.6 Inspeccion de Anclajes Adhesivos

**17.11.6.1** Inspeccion requerida para:
- Anclajes horizontales o hacia arriba
- Anclajes en aplicaciones sismicas (SDC C-F)
- Anclajes con cargas sostenidas

**17.11.6.2** Verificacion de instalacion:
- Diametro y profundidad del orificio
- Limpieza del orificio
- Llenado completo con adhesivo
- Tiempo de curado

---

## 17.12 INSTALACION DE ANCLAJES

### 17.12.1 Anclajes Colados en Sitio

**17.12.1.1** Colocacion:
- Asegurar posicion antes del colado
- Verificar profundidad de empotramiento
- Mantener verticalidad

**17.12.1.2** Tolerancias:
- Ubicacion: ± 1/2 in (a menos que se especifique otra)
- Verticalidad: 1:40
- Profundidad: -0, +1/2 in

### 17.12.2 Anclajes Post-Instalados

### Tabla 17.12.2.1 - Requisitos de Instalacion por Tipo

| Tipo | Requisitos de Instalacion |
|------|--------------------------|
| **Expansion (torque-controlled)** | Torque especificado, verificar expansion |
| **Expansion (displacement-controlled)** | Desplazamiento especificado, verificar asentamiento |
| **Undercut** | Verificar perfil de corte, torque |
| **Adhesivo** | Limpieza, llenado, tiempo de curado |

### 17.12.3 Refuerzo de Anclaje

**17.12.3.1** Detallado:
- Desarrollar para fy a ambos lados del plano de falla potencial
- Espaciamiento <= 0.5*hef desde el anclaje

**17.12.3.2** Para tension:
- Horquillas (hairpins) o estribos que encierren el cono de falla
- As >= Nua / (phi * fy)

**17.12.3.3** Para cortante:
- Estribos perpendiculares al borde
- As >= Vua / (phi * fy)
- Primer estribo a <= 0.5*ca1 del anclaje

---

## 17.13 REQUISITOS ESPECIALES

### 17.13.1 Anclajes en Concreto Liviano

**17.13.1.1** Factor lambda_a:
- Usar valores de 19.2.4
- Aplicar a todas las ecuaciones de resistencia del concreto

**Tabla 17.13.1.1 - Factor lambda_a**

| Tipo de Concreto | lambda_a |
|------------------|----------|
| Peso normal | 1.0 |
| Arena-liviano | 0.85 |
| Todo liviano | 0.75 |

### 17.13.2 Anclajes en Concreto de Alta Resistencia

**17.13.2.1** Para f'c > 10,000 psi:
- Limitar sqrt(f'c) a 100 psi en ecuaciones de desprendimiento
- Verificar splitting con mayor cuidado

### 17.13.3 Anclajes Cerca de Juntas de Expansion

**17.13.3.1** Considerar movimiento de junta:
- Reducir capacidad si movimiento puede afectar anclaje
- Proveer holgura si se espera movimiento significativo

### 17.13.4 Anclajes en Elementos Pretensados

**17.13.4.1** Verificar:
- Interaccion con tendones
- Perdida de pretensado por orificios
- Transferencia de carga

---

## VARIABLES CLAVE

### Tension

| Variable | Descripcion |
|----------|-------------|
| Ase,N | Area efectiva del anclaje en tension |
| futa | Resistencia a tension especificada del acero |
| fya | Resistencia a fluencia especificada del acero |
| hef | Profundidad efectiva de empotramiento |
| ANc, ANco | Areas proyectadas de falla por breakout |
| ca1, ca2 | Distancias al borde |
| Abrg | Area de apoyo de la cabeza |
| da | Diametro del anclaje |
| eh | Distancia del borde interior del vastago a la punta del gancho |
| tau_cr | Esfuerzo de adherencia caracteristico |
| cNa | Radio de influencia critico para adherencia |
| lambda_a | Factor de concreto liviano |

### Cortante

| Variable | Descripcion |
|----------|-------------|
| Ase,V | Area efectiva del anclaje en cortante |
| ca1 | Distancia al borde en direccion de la carga |
| ca2 | Distancia al borde perpendicular a ca1 |
| AVc, AVco | Areas proyectadas de falla por breakout en cortante |
| le | Longitud efectiva de carga del anclaje |
| da | Diametro del anclaje |
| ha | Espesor del miembro donde esta el anclaje |
| e'V | Excentricidad de cortante en grupo |
| kcp | Factor de pryout |
| lambda_a | Factor de concreto liviano |

---

## RESUMEN DE FACTORES

### Factores de Reduccion phi

| Modo | Estatico | Sismico |
|------|----------|---------|
| Tension - acero ductil | 0.75 | 0.75 |
| Tension - acero no ductil | 0.65 | 0.65 |
| Tension - concreto | 0.70/0.75 | 0.70/0.75 |
| Cortante - acero ductil | 0.65 | 0.65 |
| Cortante - acero no ductil | 0.60 | 0.60 |
| Cortante - concreto | 0.70/0.75 | 0.70/0.75 |

### Ecuaciones Principales

**Tension:**
```
Nn = min(Nsa, Ncb o Ncbg, Npn, Nsb o Nsbg, Na o Nag)
```

**Cortante:**
```
Vn = min(Vsa, Vcb o Vcbg, Vcp o Vcpg)
```

**Interaccion:**
```
Nua/(phi*Nn) + Vua/(phi*Vn) <= 1.2
```

---

## LISTA DE VERIFICACION - DISENO DE ANCLAJES

### Paso 1: Determinar Cargas
- [ ] Nua (tension factorada)
- [ ] Vua (cortante factorado)
- [ ] Excentricidades
- [ ] Combinaciones de carga (incluyendo sismo si aplica)

### Paso 2: Seleccionar Anclaje
- [ ] Tipo (colado, post-instalado, adhesivo)
- [ ] Material y grado
- [ ] Diametro da
- [ ] Profundidad efectiva hef

### Paso 3: Verificar Geometria
- [ ] Distancias al borde (ca1, ca2)
- [ ] Espaciamiento (s)
- [ ] Espesor del miembro (ha)
- [ ] Requisitos de splitting

### Paso 4: Calcular Resistencias
- [ ] Tension: Nsa, Ncb, Npn, Nsb (Na si adhesivo)
- [ ] Cortante: Vsa, Vcb, Vcp
- [ ] Aplicar factores phi

### Paso 5: Verificar
- [ ] phi*Nn >= Nua
- [ ] phi*Vn >= Vua
- [ ] Interaccion si aplica

### Paso 6: Requisitos Sismicos (si SDC C-F)
- [ ] Verificar ductilidad o refuerzo de anclaje
- [ ] Verificar ubicacion respecto a rotulas plasticas

---

## REFERENCIAS NORMATIVAS

| Norma | Descripcion |
|-------|-------------|
| ACI 355.2 | Calificacion de anclajes mecanicos post-instalados |
| ACI 355.4 | Calificacion de anclajes adhesivos |
| ASTM F1554 | Pernos de anclaje (Grado 36, 55, 105) |
| ASTM A354 | Pernos de alta resistencia |
| ASTM A449 | Pernos de acero templado |
| AWS D1.1 | Conectores de cabeza |

---

## REFERENCIAS CRUZADAS INTERNAS

| Tema | Seccion |
|------|---------|
| Factores phi | 21.2 |
| Requisitos sismicos generales | Capitulo 18 |
| Propiedades del concreto | Capitulo 19 |
| Recubrimiento | 20.5 |

---

*Resumen del ACI 318-25 Capitulo 17 - Anclajes al Concreto.*
*Fecha: 2025*
