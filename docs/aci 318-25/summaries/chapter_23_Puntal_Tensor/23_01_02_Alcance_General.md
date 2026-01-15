# ACI 318-25 - Secciones 23.1-23.2: ALCANCE Y GENERALIDADES

---

## 23.1 ALCANCE

### 23.1.1 Aplicabilidad

El metodo de puntal y tensor (strut-and-tie) aplica para:

- **D-Regions (Discontinuity Regions)**: Regiones donde la distribucion de deformaciones NO es lineal
- Zonas cerca de cargas concentradas
- Zonas cerca de discontinuidades geometricas
- Zonas cerca de aberturas y cambios de seccion

### 23.1.2 Uso General

El metodo puede usarse para disenar cualquier miembro estructural o region, incluyendo:

| Aplicacion | Descripcion |
|------------|-------------|
| Vigas de gran peralte (deep beams) | L/d < 4 |
| Mensulas y corbels | av/d < 2.0 |
| Cabezales de pilotes | Transferencia de cargas |
| Nudos viga-columna | Zonas de conexion |
| Apoyos de vigas | Transferencia a soportes |
| Zonas de anclaje | Post-tensado |

### 23.1.3 Principio de St. Venant

La distribucion de esfuerzos alcanza una distribucion lineal (B-region) a una distancia aproximada de **h** desde el punto de discontinuidad.

```
Extension de D-region = h (peralte del miembro)
```

---

## 23.2 GENERALIDADES

### 23.2.1 Proceso de Diseno (4 Pasos)

| Paso | Descripcion |
|------|-------------|
| 1 | Definir y aislar D-regions |
| 2 | Calcular fuerzas resultantes en limites |
| 3 | Seleccionar modelo y calcular fuerzas internas |
| 4 | Disenar struts, ties y nodal zones |

### 23.2.2 Componentes del Modelo

**Strut (Puntal):**
- Miembro en **compresion**
- Representa campo de compresion en el concreto
- Tipos: boundary strut, interior strut

**Tie (Tensor):**
- Miembro en **tension**
- Representa refuerzo de acero
- Tipicamente horizontal o vertical

**Nodal Zone (Zona Nodal):**
- Region donde se conectan struts y ties
- Volumen de concreto que transfiere fuerzas

### 23.2.3 Tipos de Nodos

| Tipo | Descripcion | Coeficiente βn |
|------|-------------|----------------|
| **C-C-C** | 3 fuerzas de compresion | **1.0** |
| **C-C-T** | 2 compresiones + 1 tension | **0.80** |
| **C-T-T** | 1 compresion + 2 tensiones | **0.60** |

### 23.2.4 Tipos de Struts

| Tipo | Ubicacion | Tension Transversal |
|------|-----------|---------------------|
| **Boundary strut** | En frontera/apoyo | Sin tension transversal |
| **Interior strut** | En interior | Con tension transversal |
| **Strut en zona tension** | Miembro en tension | Esfuerzos perpendiculares |

### 23.2.5 Extended Nodal Zone

Zona extendida delimitada por:
- Interseccion del ancho del strut (ws)
- Interseccion del ancho del tie (wt)

Permite mayor area para anclaje y desarrollo del refuerzo.

---

## 23.2.6 REQUISITOS GEOMETRICOS

### Angulo Minimo Strut-Tie (23.2.7)

```
theta >= 25 grados (entre strut y tie)
```

**IMPORTANTE:** Si el angulo es menor a 25°, el modelo NO es valido.

### 23.2.8 Equilibrio

- Las fuerzas internas deben estar en **equilibrio** con las cargas factorizadas
- El modelo debe transferir todas las cargas a los apoyos

### 23.2.9 Intersecciones

| Elemento | Regla |
|----------|-------|
| Struts | Solo intersectan en **nodal zones** |
| Ties | Pueden cruzar struts |
| Modelo | Geometria debe ser consistente |

---

## 23.2.10 REQUISITOS POR TIPO DE MIEMBRO

### Vigas de Gran Peralte (23.2.9)

Deben satisfacer adicionalmente:
- **9.9.2.1**: Requisitos de resistencia
- **9.9.3.1**: Refuerzo minimo
- **9.9.4**: Detallado de refuerzo

### Muros (23.2.10)

Deben satisfacer:
- **11.6**: Diseno por cortante
- **11.7.2-11.7.3**: Refuerzo distribuido

### Mensulas/Corbels (23.2.11)

Requisitos adicionales:
- av/d < **2.0** (relacion corte a profundidad)
- Asc >= **0.04(fc'/fy)(bw·d)**
- Satisfacer **16.5.2** y **16.5.6**

### Friccion por Cortante (23.2.12)

Aplican requisitos del **Capitulo 22.9** para interfaces de cortante.

---

## 23.2.13 DISENO SISMICO

Para categorias sismicas **SDC D, E, F**:

| Requisito | Referencia |
|-----------|------------|
| Reduccion de resistencia | 23.11.2, 23.11.5 |
| Desarrollo de ties | 23.11.4 |
| Refuerzo transversal | 23.11.3 |
| Factor de sobreresistencia | Ωo >= 2.5 |

Ver seccion **23.11** para requisitos completos.

---

## REFERENCIAS A OTROS CAPITULOS

| Capitulo | Tema | Aplicacion en Cap. 23 |
|----------|------|----------------------|
| 5 | Combinaciones de carga | Fuerzas factorizadas |
| 9 | Vigas | Deep beams 9.9 |
| 11 | Muros | Refuerzo distribuido |
| 15 | Juntas | Nudos viga-columna |
| 16 | Conexiones | Mensulas y corbels |
| 18 | Sismo | Detallado especial |
| 21 | Factores phi | Reduccion de resistencia |
| 22 | Resistencia seccional | Cortante y friccion |
| 25 | Detalles refuerzo | Desarrollo y anclaje |

---

*ACI 318-25 Secciones 23.1-23.2*
