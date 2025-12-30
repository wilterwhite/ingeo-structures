# ACI 318-25 - CAPITULO 8: LOSAS EN DOS DIRECCIONES
## Two-Way Slabs

---

## 8.1 ALCANCE

### 8.1.1 Aplicacion
Este capitulo aplica al diseno de losas no presforzadas y presforzadas reforzadas para flexion en dos direcciones, con o sin vigas entre apoyos, incluyendo:

| Tipo | Descripcion |
|------|-------------|
| (a) | Losas solidas |
| (b) | Losas coladas sobre deck de acero no compuesto |
| (c) | Losas compuestas de elementos de concreto |
| (d) | Sistemas de viguetas en dos direcciones (waffle slabs) segun 8.8 |

> **Sistemas incluidos**: Flat slabs, flat plates, losas con vigas en ambas direcciones, waffle slabs.

---

## 8.2 GENERALIDADES

### 8.2.1 Metodos de Diseno Permitidos
Se permite disenar por cualquier procedimiento que satisfaga equilibrio y compatibilidad geometrica, incluyendo:
- **Metodo de diseno directo**
- **Metodo del marco equivalente**

### 8.2.2 Consideraciones de Diseno
Los efectos de cargas concentradas, aberturas y vacios en la losa deben considerarse.

### 8.2.3 Losas Presforzadas como No Presforzadas
Losas presforzadas con esfuerzo compresivo efectivo promedio < **125 psi** deben disenarse como no presforzadas.

### 8.2.4 Panel de Caida (Drop Panel)
Para reducir espesor minimo o refuerzo negativo:

| Requisito | Valor |
|-----------|-------|
| Proyeccion minima bajo la losa | ≥ h/4 de la losa adyacente |
| Extension desde linea central del apoyo | ≥ L/6 en cada direccion |

### 8.2.5 Capitel de Cortante (Shear Cap)
Para aumentar seccion critica de cortante:
- Proyectar bajo el sofito de la losa
- Extender horizontalmente desde la cara de columna ≥ espesor de la proyeccion

### 8.2.6 Materiales

| Seccion | Referencia |
|---------|------------|
| 8.2.6.1 Propiedades del concreto | Capitulo 19 |
| 8.2.6.2 Propiedades del refuerzo | Capitulo 20 |
| 8.2.6.3 Empotramientos | 20.6 |

---

## 8.3 LIMITES DE DISENO

### 8.3.1 Espesor Minimo de Losa

#### Tabla 8.3.1.1 - Losas Sin Vigas Interiores (pulgadas)

| fy (psi) | Sin drop panels | Con drop panels |
|----------|----------------|-----------------|
| | Exterior sin viga | Exterior con viga | Interior | Exterior sin viga | Exterior con viga | Interior |
| 40,000 | ℓn/33 | ℓn/36 | ℓn/36 | ℓn/36 | ℓn/40 | ℓn/40 |
| 60,000 | ℓn/30 | ℓn/33 | ℓn/33 | ℓn/33 | ℓn/36 | ℓn/36 |
| 80,000 | ℓn/27 | ℓn/30 | ℓn/30 | ℓn/30 | ℓn/33 | ℓn/33 |

**Espesores minimos absolutos:**
- Sin drop panels: **5 in.**
- Con drop panels: **4 in.**

> **NOTA**: Para fy > 80,000 psi, las deflexiones deben calcularse (8.3.2).

#### Tabla 8.3.1.2 - Losas Con Vigas en Todos los Lados

| αfm | Espesor Minimo h |
|-----|------------------|
| αfm ≤ 0.2 | Usar Tabla 8.3.1.1 |
| 0.2 < αfm ≤ 2.0 | Mayor de: ℓn(0.8 + fy/200,000) / [36 + 5β(αfm - 0.2)] y 5.0 in. |
| αfm > 2.0 | Mayor de: ℓn(0.8 + fy/200,000) / (36 + 9β) y 3.5 in. |

Donde:
- αfm = valor promedio de αf para todas las vigas en los bordes del panel
- β = relacion de luces libres (largo/corto)

### 8.3.2 Limites de Deflexion Calculada
Calcular deflexiones segun 24.2 para:
- Losas no presforzadas que no satisfacen 8.3.1
- Losas sin vigas interiores con relacion largo/corto > 2.0
- Losas presforzadas

### 8.3.3 Limite de Deformacion del Refuerzo
**8.3.3.1** Las losas no presforzadas deben ser **controladas por tension** segun Tabla 21.2.2.

### 8.3.4 Limites de Esfuerzo en Losas Presforzadas
**8.3.4.1** Disenar como Clase U con ft ≤ 6√fc'.

---

## 8.4 RESISTENCIA REQUERIDA

### 8.4.1 Definiciones de Franjas

| Termino | Definicion |
|---------|------------|
| **Franja de columna** | Ancho a cada lado del eje de columna = menor de 0.25ℓ2 y 0.25ℓ1 |
| **Franja central** | Limitada por dos franjas de columna |
| **Panel** | Limitado por ejes de columnas, vigas o muros |

### 8.4.2 Momento Factorizado

#### 8.4.2.2 Momento de Losa Resistido por la Columna (Msc)

**Fraccion transferida por flexion:**
```
γf = 1 / [1 + (2/3)√(b1/b2)]
```

**Ancho efectivo de losa (bslab):**
- Ancho de columna/capitel/shear cap + 1.5h a cada lado

#### Tabla 8.4.2.2.4 - Valores Modificados de γf

| Ubicacion Columna | Direccion del Claro | vuv | εt (dentro de bslab) | γf Maximo Modificado |
|-------------------|---------------------|-----|----------------------|---------------------|
| Esquina | Cualquiera | ≤ 0.5ϕvc | ≥ εty + 0.003 | 1.0 |
| Borde | Perpendicular al borde | ≤ 0.75ϕvc | ≥ εty + 0.003 | 1.0 |
| Borde | Paralelo al borde | ≤ 0.4ϕvc | ≥ εty + 0.008 | 1.25/[1+(2/3)√(b1/b2)] ≤ 1.0 |
| Interior | Cualquiera | ≤ 0.4ϕvc | ≥ εty + 0.008 | 1.25/[1+(2/3)√(b1/b2)] ≤ 1.0 |

### 8.4.3 Cortante en Una Direccion
Seccion critica a **d** (no presforzadas) o **h/2** (presforzadas) de la cara del apoyo.

### 8.4.4 Cortante en Dos Direcciones (Punzonado)

**Seccion critica:** Segun 22.6.4

**Fraccion de momento transferida por excentricidad de cortante:**
```
γv = 1 - γf
```

**Esfuerzo cortante maximo:**
```
vu,max = vuv + γvMsc×c / Jc
```

---

## 8.5 RESISTENCIA DE DISENO

### 8.5.1 General
**ϕSn ≥ U**, incluyendo:
- (a) ϕMn ≥ Mu en todas las secciones
- (b) ϕMn ≥ γfMsc dentro de bslab
- (c) ϕVn ≥ Vu para cortante en una direccion
- (d) ϕvn ≥ vu para cortante en dos direcciones

### 8.5.3 Cortante
- **Una direccion:** Vn segun 22.5
- **Dos direcciones:** vn segun 22.6

### 8.5.4 Aberturas en Sistemas de Losas

| Ubicacion | Requisito |
|-----------|-----------|
| Franjas centrales intersectantes | Cualquier tamano permitido; mantener refuerzo total |
| Franjas de columna intersectantes | Max. 1/8 del ancho; agregar refuerzo interrumpido |
| Franja de columna + franja central | Max. 1/4 del refuerzo interrumpido |
| Cerca de columna (< 4h) | Satisfacer 22.6.4.3 |

---

## 8.6 LIMITES DE REFUERZO

### 8.6.1 Refuerzo Minimo a Flexion (No Presforzadas)

**8.6.1.1** Area minima: **As,min = 0.0018Ag**

**8.6.1.2** Si vuv > ϕ2√fc'λsλ en seccion critica:
```
As,min = 5vuv×bslab×bo / (ϕαsfy)
```

### 8.6.2 Refuerzo Minimo a Flexion (Presforzadas)

**8.6.2.1** Esfuerzo compresivo efectivo minimo: **125 psi** en toda seccion tributaria

#### Tabla 8.6.2.3 - Refuerzo Adherido Minimo (As,min)

| Region | ft Calculado | As,min |
|--------|--------------|--------|
| Momento positivo | ft ≤ 2√fc' | No requerido |
| Momento positivo | 2√fc' < ft ≤ 6√fc' | Nc / (0.5fy) |
| Momento negativo en columnas | ft ≤ 6√fc' | 0.00075Acf |

---

## 8.7 DETALLADO DEL REFUERZO

### 8.7.2 Espaciamiento del Refuerzo

| Tipo | Espaciamiento Maximo |
|------|---------------------|
| Losas solidas no presforzadas (secciones criticas) | Menor de 2h y 18 in. |
| Losas solidas no presforzadas (otras secciones) | Menor de 3h y 18 in. |
| Tendones presforzados | Menor de 8h y 5 ft |

### 8.7.3 Restriccion en Esquinas
Donde αf > 1.0 en vigas de borde:
- Refuerzo superior e inferior para Mu = Mu positivo maximo del panel
- Extension: 1/5 del claro largo desde la esquina
- Colocar paralelo a diagonal (superior) y perpendicular (inferior)

### 8.7.4 Refuerzo a Flexion (No Presforzadas)

#### 8.7.4.1.3 Extensiones de Refuerzo (Fig. 8.7.4.1.3)

**Franja de Columna - Superior:**
| Porcion | Extension desde cara apoyo |
|---------|---------------------------|
| 50% (mitad de barras) | 0.30ℓn (sin drop panel) o 0.33ℓn (con drop panel) |
| 50% restante | 0.20ℓn |
| Al menos 50% | ≥ 5d desde cara de apoyo |

**Franja de Columna - Inferior:**
- 100%: Continuas o empalmadas en region central
- Al menos 2 barras pasan dentro de columna

**Franja Central:**
| Ubicacion | Extension |
|-----------|-----------|
| Superior | 0.22ℓn desde cara de apoyo |
| Inferior | 6 in. en apoyos, max. 0.15ℓn entre apoyos |

### 8.7.4.2 Integridad Estructural

| Requisito | Descripcion |
|-----------|-------------|
| 8.7.4.2.1 | Todas las barras inferiores de franja de columna: continuas o empalmadas |
| 8.7.4.2.2 | Al menos 2 barras inferiores pasan dentro de columna, desarrolladas con 1.25fy |

### 8.7.5 Refuerzo a Flexion (Presforzadas)

**8.7.5.3** Refuerzo adherido en momento negativo:
- Distribuir entre lineas a 1.5h de caras de columna
- Minimo 4 barras/alambres/torones en cada direccion
- Espaciamiento maximo: 12 in.

### 8.7.5.6 Integridad Estructural (Presforzadas)

| Requisito | Descripcion |
|-----------|-------------|
| 8.7.5.6.1 | Al menos 2 tendones (≥ 1/2 in. diametro) en cada direccion pasando por columna |
| 8.7.5.6.2 | Fuera de columna, tendones de integridad pasan bajo tendones ortogonales |
| 8.7.5.6.3 | Alternativa: Refuerzo deformado inferior con As = mayor de 4.5√fc'c2d/fy y 300c2d/fy |

### 8.7.6 Refuerzo de Cortante - Estribos

#### Tabla 8.7.6.3 - Ubicacion y Espaciamiento de Estribos

| Direccion | Descripcion | Maximo |
|-----------|-------------|--------|
| Perpendicular a columna | Distancia de cara a primer estribo | d/2 |
| Perpendicular a columna | Espaciamiento entre estribos | d/2 |
| Paralelo a columna | Espaciamiento entre piernas | 2d |

### 8.7.7 Refuerzo de Cortante - Studs con Cabeza

#### Tabla 8.7.7.1.2 - Ubicacion y Espaciamiento de Studs

| Direccion | Descripcion | Condicion | Maximo |
|-----------|-------------|-----------|--------|
| Perpendicular | Distancia a primera linea | Todas | d/2 |
| Perpendicular | Espaciamiento entre lineas | vu ≤ ϕ6√fc' | 3d/4 |
| Perpendicular | Espaciamiento entre lineas | vu > ϕ6√fc' | d/2 |
| Paralelo | Espaciamiento entre studs adyacentes | Todas | 2d |

---

## 8.8 SISTEMAS DE VIGUETAS EN DOS DIRECCIONES (NO PRESFORZADOS)

### 8.8.1 Requisitos Generales

| Requisito | Limite |
|-----------|--------|
| Ancho minimo de nervaduras | 4 in. |
| Profundidad maxima (excluyendo losa) | 3.5 × ancho minimo |
| Espaciamiento libre maximo entre nervaduras | 30 in. |
| Aumento permitido de Vc | 1.1 × valores de 22.5 |

### 8.8.2 Sistemas con Rellenos Estructurales
- Espesor de losa sobre rellenos: ≥ mayor de (claro libre/12) y 1.5 in.
- Se permite incluir cascarones verticales de rellenos en calculo de resistencia

### 8.8.3 Sistemas con Otros Rellenos
- Espesor de losa: ≥ mayor de (claro libre/12) y 2 in.

---

## 8.9 CONSTRUCCION LIFT-SLAB

**8.9.1** Donde es impracticable pasar tendones o barras a traves de la columna:
- Al menos 2 tendones post-tensados o 2 barras inferiores adheridas en cada direccion
- Pasar a traves del collar de levantamiento
- Continuos o empalmados (mecanicos, soldados o Clase B)

---

## RESUMEN DE ESPESORES MINIMOS

### Losas Planas Sin Vigas (fy = 60 ksi)

| Tipo | Exterior sin viga borde | Exterior con viga borde | Interior |
|------|------------------------|------------------------|----------|
| Sin drop panel | ℓn/30 | ℓn/33 | ℓn/33 |
| Con drop panel | ℓn/33 | ℓn/36 | ℓn/36 |

### Minimos Absolutos
- Sin drop panel: 5 in.
- Con drop panel: 4 in.

---

## REFERENCIAS A OTROS CAPITULOS

| Tema | Capitulo/Seccion |
|------|------------------|
| Propiedades del concreto | 19 |
| Propiedades del refuerzo | 20 |
| Factores de reduccion | 21.2 |
| Resistencia a flexion | 22.3 |
| Cortante en una direccion | 22.5 |
| Cortante en dos direcciones | 22.6 |
| Deflexiones | 24.2 |
| Desarrollo y empalmes | 25.4, 25.5 |
| Anclaje de estribos | 25.7.1 |
| Zonas de anclaje post-tensado | 25.9 |

---

*Resumen del ACI 318-25 Capitulo 8 - Losas en Dos Direcciones.*
*Fecha: 2025*
