# ACI 318-25 - CAPITULO 11: MUROS (WALLS)
## Resumen Funcional para Implementacion en App

---

## 11.1 ALCANCE

### 11.1.1 Aplicabilidad
Este capitulo aplica al diseno de muros **no pretensados y pretensados**, incluyendo:
- (a) Colados en sitio (Cast-in-place)
- (b) Prefabricados en planta (Precast in-plant)
- (c) Prefabricados en sitio incluyendo tilt-up

### 11.1.2-11.1.6 Referencias a otros capitulos
| Tipo de Muro | Capitulo de Referencia |
|--------------|------------------------|
| Muros estructurales especiales | Capitulo 18 |
| Muros de concreto simple | Capitulo 14 |
| Muros de retencion en voladizo | Capitulo 13 |
| Muros como vigas de cimentacion | 13.3.5 |
| Muros con formas aislantes (ICF) | Permitido (ver ACI PRC-560) |

### Definiciones Clave (ASCE/SEI 7)
- **Muro estructural**: Muro que cumple definicion de muro de carga o muro de cortante
- **Muro de carga (Bearing wall)**: Soporta carga vertical mas alla de un umbral
- **Muro de cortante (Shear wall)**: Disenado para resistir fuerzas laterales en su plano

---

## 11.2 GENERAL

### 11.2.1 Materiales
- **11.2.1.1**: Propiedades del concreto segun Capitulo 19
- **11.2.1.2**: Propiedades del acero segun Capitulo 20
- **11.2.1.3**: Embedments segun 20.6

### 11.2.2 Conexion a otros elementos
- **11.2.2.1**: Conexiones de muros prefabricados segun 16.2
- **11.2.2.2**: Conexiones muro-cimentacion segun 16.3

### 11.2.3 Distribucion de Cargas
**Longitud efectiva horizontal** para cargas concentradas (la menor de):
- Distancia centro a centro entre cargas
- Ancho de apoyo + 4 veces el espesor del muro

> **Nota**: No extender mas alla de juntas verticales a menos que el diseno provea transferencia de fuerzas.

### 11.2.4 Elementos Intersectantes

**11.2.4.1**: Los muros deben anclarse a:
- Pisos y techos
- Columnas, pilastras, contrafuertes
- Muros intersectantes
- Zapatas

**11.2.4.2**: Para muros colados en sitio con **Pu > 0.2 f'c Ag**:
```
La porcion del muro dentro del espesor del sistema de piso
debe tener f'c especificado >= 0.8 f'c del muro
```
> **Razon**: Factor 0.8 refleja menor confinamiento en juntas piso-muro vs piso-columna.

---

## 11.3 LIMITES DE DISENO

### 11.3.1 Espesor Minimo de Muros Solidos

#### Tabla 11.3.1.1 - Espesor minimo h

| Tipo de Muro | Espesor Minimo h |
|--------------|------------------|
| **De carga (Bearing)** [1] | Mayor de: (a) 4 in (100 mm), (b) 1/25 del menor entre longitud y altura no soportadas |
| **Sin carga (Nonbearing)** | Mayor de: (c) 4 in (100 mm), (d) 1/30 del menor entre longitud y altura no soportadas |
| **Sotano exterior y cimentacion** [1] | (e) 7.5 in (190 mm) |

> [1] Solo aplica a muros disenados con el metodo simplificado de 11.5.3

**Excepcion**: Muros mas delgados permitidos si se demuestra resistencia y estabilidad adecuadas mediante analisis estructural.

---

## 11.4 RESISTENCIA REQUERIDA

### 11.4.1 General
- **11.4.1.1**: Calcular segun combinaciones de carga factoradas (Capitulo 5)
- **11.4.1.2**: Calcular segun procedimientos de analisis (Capitulo 6)

### 11.4.1.3 Efectos de Esbeltez
Calcular segun:
- 6.6.4 (Magnificacion de momentos)
- 6.7 (Analisis de segundo orden elastico)
- 6.8 (Analisis inelastico de segundo orden)
- **11.8** (Metodo alternativo para muros esbeltos fuera del plano)

### 11.4.1.4 Consideraciones de Carga
Los muros deben disenarse para:
- Cargas axiales excentricas
- Cargas laterales
- Cualquier otra carga aplicable

### 11.4.1.5 Muros de Sotano
Diseno para presion lateral de tierra fuera del plano segun Seccion 13.3.7

### Fuerzas Tipicas en un Muro
```
+------------------+
|   CARGA AXIAL    |  (vertical hacia abajo)
|        |         |
|        v         |
|  +-----------+   |
|  |           |   |  <- CORTANTE EN EL PLANO (In-plane shear)
|  |   MURO    |   |  <- MOMENTO EN EL PLANO (In-plane moment)
|  |           |   |
|  +-----------+   |
|        |         |
|  CORTANTE FUERA  |  (perpendicular al plano)
|   DEL PLANO      |
|  MOMENTO FUERA   |
|   DEL PLANO      |
+------------------+
```

### 11.4.2 Carga Axial y Momento Factorados
**11.4.2.1**: Disenar para el maximo momento factorado Mu que acompana la carga axial Pu:
- Pu no debe exceder **phi * Pn,max** (ver 22.4.2.1)
- phi = factor de reduccion para secciones controladas por compresion (21.2.2)
- Mu debe magnificarse por efectos de esbeltez

### 11.4.3 Cortante Factorado
**11.4.3.1**: Disenar para el maximo Vu en el plano y fuera del plano.

---

## 11.5 RESISTENCIA DE DISENO

### 11.5.1 General
**11.5.1.1**: Para cada combinacion de carga, la resistencia de diseno debe satisfacer:
```
(a) phi*Pn >= Pu
(b) phi*Mn >= Mu
(c) phi*Vn >= Vu
```
> Debe considerarse la interaccion carga axial-momento.

**11.5.1.2**: phi segun 21.2

### 11.5.2 Carga Axial y Flexion (En el plano o fuera del plano)
- **11.5.2.1 (Muros de carga)**: Pn y Mn segun 22.4, o alternativamente usar 11.5.3
- **11.5.2.2 (Muros sin carga)**: Mn segun 22.3

---

### 11.5.3 METODO SIMPLIFICADO (Carga Axial + Flexion Fuera del Plano)

#### 11.5.3.1 Condicion de Aplicabilidad
Aplica cuando la **resultante de todas las cargas factoradas** esta ubicada dentro del **tercio medio del espesor** del muro (excentricidad <= h/6).

#### Ecuacion de Resistencia Nominal

```
Pn = 0.55 * f'c * Ag * [1 - (k*lc / 32h)^2]     (Ec. 11.5.3.1)
```

Donde:
- f'c = resistencia especificada del concreto (psi o MPa)
- Ag = area bruta de la seccion del muro
- k = factor de longitud efectiva (Tabla 11.5.3.2)
- lc = longitud no soportada del muro
- h = espesor del muro

#### Tabla 11.5.3.2 - Factor de Longitud Efectiva k

| Condiciones de Borde | k |
|---------------------|---|
| Muro arriostrado arriba y abajo contra traslacion lateral Y: | |
| (a) Restringido contra rotacion en uno o ambos extremos | **0.8** |
| (b) Sin restriccion contra rotacion en ambos extremos | **1.0** |
| Muro NO arriostrado contra traslacion lateral | **2.0** |

#### 11.5.3.3 Factor de Reduccion
Pn de Ec. 11.5.3.1 debe reducirse por **phi para secciones controladas por compresion** (21.2.2)

#### 11.5.3.4 Refuerzo
El refuerzo del muro debe ser al menos el requerido por 11.6

---

### 11.5.4 CORTANTE EN EL PLANO (In-Plane Shear)

> **Importancia**: Critico para muros con relacion altura/longitud pequena (hw/lw < 2)

#### 11.5.4.1 Metodos de Calculo
- Calcular Vn segun 11.5.4.2 a 11.5.4.4
- **Alternativa**: Para muros con hw/lw < 2, permitido usar metodo de puntal y tensor (Capitulo 23)

#### 11.5.4.2 Limite Maximo de Cortante
```
Vn <= 8 * sqrt(f'c) * Acv     (en cualquier seccion horizontal)
```
> **Razon**: Prevenir falla por compresion diagonal.

#### 11.5.4.3 Resistencia Nominal al Cortante

```
Vn = (alpha_c * lambda * sqrt(f'c) + rho_t * fyt) * Acv     (Ec. 11.5.4.3)
```

Donde:
- **Acv** = area bruta de la seccion de concreto limitada por espesor y longitud del muro
- **lambda** = factor de concreto liviano
- **rho_t** = cuantia de refuerzo transversal (horizontal)
- **fyt** = resistencia a la fluencia del refuerzo transversal

**Valores de alpha_c:**
| Relacion hw/lw | alpha_c |
|----------------|---------|
| hw/lw <= 1.5 | **3** |
| hw/lw >= 2.0 | **2** |
| 1.5 < hw/lw < 2.0 | Interpolar linealmente entre 3 y 2 |

**Formula de interpolacion:**
```
alpha_c = 3 - (hw/lw - 1.5) * 2    para 1.5 < hw/lw < 2.0
```

#### 11.5.4.4 Muros Sujetos a Tension Axial Neta
Cuando existe tension axial neta en toda la seccion del muro:

```
alpha_c = 2 * (1 + Nu / (500 * Ag)) >= 0.0     (Ec. 11.5.4.4)
```
Donde **Nu es negativo para tension**.

> **Nota**: La contribucion del concreto al cortante se reduce o puede ser despreciable. El refuerzo transversal debe resistir la mayoria o toda la fuerza cortante.

### 11.5.5 Cortante Fuera del Plano
**11.5.5.1**: Vn segun 22.5 (como losa unidireccional)

---

## 11.6 LIMITES DE REFUERZO

### 11.6.1 Refuerzo Minimo (Cortante en plano bajo)

**Condicion**: Si Vu en el plano <= 0.5 * phi * alpha_c * lambda * sqrt(f'c) * Acv

#### Tabla 11.6.1 - Refuerzo Minimo

| Tipo de Muro | Tipo de Refuerzo | Tamano Barra | fy (psi) | rho_l min (longitudinal) | rho_t min (transversal) |
|--------------|------------------|--------------|----------|--------------------------|-------------------------|
| **Colado en sitio** | Barras corrugadas | <= No. 5 | >= 60,000 | 0.0012 | 0.0020 |
| | | <= No. 5 | < 60,000 | 0.0015 | 0.0025 |
| | | > No. 5 | Cualquiera | 0.0015 | 0.0025 |
| | Malla electrosoldada | <= W31 o D31 | Cualquiera | 0.0012 | 0.0020 |
| **Prefabricado** | Barras o malla | Cualquiera | Cualquiera | 0.0010 | 0.0010 |

**Notas:**
- [1] Muros con esfuerzo compresivo promedio por pretensado >= 225 psi no necesitan cumplir rho_l minimo
- [2] Muros prefabricados pretensados de un solo sentido, no mas anchos que 12 ft y sin conexion mecanica transversal, no necesitan refuerzo minimo perpendicular al refuerzo de flexion

> **Excepcion**: Estos limites no necesitan satisfacerse si se demuestra resistencia y estabilidad adecuadas mediante analisis estructural.

### 11.6.2 Refuerzo Minimo (Cortante en plano alto)

**Condicion**: Si Vu en el plano > 0.5 * phi * alpha_c * lambda * sqrt(f'c) * Acv

**(a) Refuerzo Longitudinal (vertical) rho_l:**
```
rho_l >= 0.0025 + 0.5 * (2.5 - hw/lw) * (rho_t - 0.0025)     (Ec. 11.6.2)
```
- Minimo: **0.0025**
- No necesita exceder rho_t requerido por resistencia (11.5.4.3)

**(b) Refuerzo Transversal (horizontal) rho_t:**
- Minimo: **0.0025**

> **Nota tecnica**: Para muros con hw/lw < 0.5, el refuerzo vertical es igual al horizontal. Para hw/lw > 2.5, solo se requiere el minimo vertical (0.0025*s*h).

---

## 11.7 DETALLADO DE REFUERZO

### 11.7.1 General
- **11.7.1.1**: Recubrimiento segun 20.5.1
- **11.7.1.2**: Longitudes de desarrollo segun 25.4
- **11.7.1.3**: Longitudes de empalme segun 25.5

### 11.7.2 Espaciamiento de Refuerzo Longitudinal

#### 11.7.2.1 Muros Colados en Sitio
| Condicion | Espaciamiento Maximo s |
|-----------|------------------------|
| General | Menor de: **3h** y **18 in** |
| Si se requiere refuerzo de cortante en plano | No exceder **lw/3** |

#### 11.7.2.2 Muros Prefabricados
| Condicion | Espaciamiento Maximo s |
|-----------|------------------------|
| General | Menor de: (a) **5h**, (b) **18 in** (exterior) o **30 in** (interior) |
| Si se requiere refuerzo de cortante en plano | Menor de: **3h**, **18 in**, **lw/3** |

#### 11.7.2.3 Doble Cortina de Refuerzo
Para muros con **espesor > 10 in** (excepto muros de sotano de un piso y muros de retencion en voladizo):
- **Refuerzo distribuido en cada direccion debe colocarse en al menos DOS CORTINAS**, una cerca de cada cara.

#### 11.7.2.4 Refuerzo a Tension por Flexion
Debe estar bien distribuido y colocado lo mas cerca posible de la cara en tension.

### 11.7.3 Espaciamiento de Refuerzo Transversal

#### 11.7.3.1 Muros Colados en Sitio
| Condicion | Espaciamiento Maximo s |
|-----------|------------------------|
| General | Menor de: **3h** y **18 in** |
| Si se requiere refuerzo de cortante en plano | No exceder **lw/5** |

#### 11.7.3.2 Muros Prefabricados
| Condicion | Espaciamiento Maximo s |
|-----------|------------------------|
| General | Menor de: (a) **5h**, (b) **18 in** (exterior) o **30 in** (interior) |
| Si se requiere refuerzo de cortante en plano | Menor de: **3h**, **18 in**, **lw/5** |

### 11.7.4 Refuerzo de Cortante a Traves del Espesor
**11.7.4.1**: El refuerzo de cortante requerido para resistencia fuera del plano debe extenderse lo mas cerca posible de las superficies de compresion y tension extremas, y satisfacer 25.7.1.3 o 25.7.1.8.

### 11.7.5 Soporte Lateral del Refuerzo Longitudinal
**11.7.5.1**: Si el refuerzo longitudinal se requiere para compresion Y **Ast > 0.01 Ag**:
- El refuerzo longitudinal debe tener soporte lateral mediante **estribos transversales**.

### 11.7.6 Refuerzo Alrededor de Aberturas
**11.7.6.1**: Ademas del refuerzo minimo de 11.6, se requiere:

| Tipo de Muro | Refuerzo Adicional |
|--------------|-------------------|
| Dos cortinas de refuerzo en ambas direcciones | Al menos **dos barras No. 5** alrededor de ventanas, puertas y aberturas similares |
| Una cortina de refuerzo en ambas direcciones | Al menos **una barra No. 5** |

> Las barras deben desarrollar **fy en tension** en las esquinas de las aberturas.

---

## 11.8 METODO ALTERNATIVO PARA MUROS ESBELTOS (Analisis Fuera del Plano)

### 11.8.1 Condiciones de Aplicabilidad

**11.8.1.1**: Este metodo es permitido para muros que satisfacen TODAS las siguientes condiciones:

| Condicion | Requisito |
|-----------|-----------|
| (a) Seccion transversal | Constante en toda la altura del muro |
| (b) Comportamiento | Controlado por tension para efecto de momento fuera del plano |
| (c) Resistencia minima | phi*Mn >= Mcr (donde Mcr usa fr de 19.2.3) |
| (d) Carga axial maxima | Pu en seccion de media altura <= **0.06 f'c Ag** |
| (e) Deflexion maxima | Deflexion fuera del plano por cargas de servicio (incluyendo P-Delta) <= **lc/150** |

> **Nota**: Muros con ventanas u otras aberturas grandes NO se consideran con seccion constante.

### 11.8.2 Modelado

**11.8.2.1**: El muro se analiza como:
- Miembro simplemente apoyado
- Cargado axialmente
- Sujeto a carga lateral uniformemente distribuida fuera del plano
- Momentos y deflexiones maximos ocurren a **media altura**

**11.8.2.2**: Distribucion de cargas gravitacionales concentradas:
```
Ancho efectivo = Ancho de apoyo + distribucion a pendiente 2V:1H hacia abajo
```
Limitado por:
- (a) Espaciamiento de cargas concentradas
- (b) Bordes del panel

### 11.8.3 Momento Factorado

**11.8.3.1**: Mu a media altura debe incluir efectos de deflexion del muro:

#### Metodo (a) - Calculo Iterativo

```
Mu = Mua + Pu * Delta_u     (Ec. 11.8.3.1a)
```

Donde:
- **Mua** = momento factorado maximo a media altura debido a cargas laterales y verticales excentricas, SIN incluir efectos P-Delta

**Deflexion Delta_u:**
```
Delta_u = (5 * Mu * lc^2) / (0.75 * 48 * Ec * Icr)     (Ec. 11.8.3.1b)
```

**Inercia agrietada Icr:**
```
Icr = (Es/Ec) * (As + Pu/fy * h/(2d)) * (d - c)^2 + (lw * c^3) / 3     (Ec. 11.8.3.1c)
```

> **Importante**: El valor de **Es/Ec debe ser al menos 6**

#### Metodo (b) - Calculo Directo

```
Mu = Mua / (1 - (5 * Pu * lc^2) / (0.75 * 48 * Ec * Icr))     (Ec. 11.8.3.1d)
```

**Area de acero efectiva (para calcular c):**
```
Ase,w = As + (Pu / fy) * (h/2 / d)
```

### 11.8.4 Deflexion Fuera del Plano - Cargas de Servicio

**11.8.4.1**: La deflexion de servicio Delta_s se calcula segun:

#### Tabla 11.8.4.1 - Calculo de Delta_s

| Condicion | Formula de Delta_s |
|-----------|-------------------|
| Ma <= (2/3)Mcr | Delta_s = (Ma / Mcr) * Delta_cr |
| Ma > (2/3)Mcr | Delta_s = (2/3)*Delta_cr + [(Ma - (2/3)Mcr) / (Mn - (2/3)Mcr)] * (Delta_n - (2/3)Delta_cr) |

**11.8.4.2**: Momento de servicio Ma:
```
Ma = Msa + Ps * Delta_s     (Ec. 11.8.4.2)

(Requiere iteracion de deflexiones)
```

**11.8.4.3**: Deflexiones de referencia:
```
Delta_cr = (5 * Mcr * lc^2) / (48 * Ec * Ig)     (Ec. 11.8.4.3a)

Delta_n = (5 * Mn * lc^2) / (48 * Ec * Icr)      (Ec. 11.8.4.3b)
```

**11.8.4.4**: Icr segun Ec. 11.8.3.1c

### Combinaciones de Carga de Servicio Recomendadas

| Tipo de Carga | Combinacion |
|---------------|-------------|
| Viento | D + 0.5L + Wa |
| Sismo | D + 0.5L + 0.7E |

---

## RESUMEN DE FORMULAS CLAVE PARA IMPLEMENTACION

### Resistencia a Compresion (Metodo Simplificado)
```python
def Pn_simplified(fc, Ag, k, lc, h):
    """
    Ec. 11.5.3.1: Resistencia axial nominal simplificada
    fc: f'c en psi
    Ag: Area bruta (in^2)
    k: Factor de longitud efectiva (0.8, 1.0, o 2.0)
    lc: Longitud no soportada (in)
    h: Espesor del muro (in)
    """
    return 0.55 * fc * Ag * (1 - (k * lc / (32 * h))**2)
```

### Resistencia a Cortante en el Plano
```python
def alpha_c(hw, lw):
    """Calcula coeficiente alpha_c basado en relacion de aspecto"""
    ratio = hw / lw
    if ratio <= 1.5:
        return 3.0
    elif ratio >= 2.0:
        return 2.0
    else:
        return 3.0 - (ratio - 1.5) * 2.0  # Interpolacion lineal

def Vn_inplane(alpha_c, lambda_factor, fc, rho_t, fyt, Acv):
    """
    Ec. 11.5.4.3: Resistencia nominal al cortante en el plano
    """
    import math
    return (alpha_c * lambda_factor * math.sqrt(fc) + rho_t * fyt) * Acv

def Vn_max(fc, Acv):
    """Ec. 11.5.4.2: Cortante maximo permitido"""
    import math
    return 8 * math.sqrt(fc) * Acv
```

### Refuerzo Minimo (Cortante Alto)
```python
def rho_l_min_high_shear(hw, lw, rho_t):
    """
    Ec. 11.6.2: Cuantia longitudinal minima cuando Vu > 0.5*phi*Vc
    """
    ratio = hw / lw
    rho_l = 0.0025 + 0.5 * (2.5 - ratio) * (rho_t - 0.0025)
    return max(rho_l, 0.0025)
```

### Inercia Agrietada para Muros Esbeltos
```python
def Icr_slender_wall(Es, Ec, As, Pu, fy, h, d, c, lw):
    """
    Ec. 11.8.3.1c: Momento de inercia agrietado
    """
    n = max(Es / Ec, 6)  # Es/Ec debe ser al menos 6
    Ase_w = As + (Pu / fy) * (h / 2) / d
    return n * Ase_w * (d - c)**2 + (lw * c**3) / 3
```

---

## REFERENCIAS CRUZADAS IMPORTANTES

| Tema | Seccion de Referencia |
|------|----------------------|
| Propiedades del concreto | Capitulo 19 |
| Propiedades del acero | Capitulo 20 |
| Factores de reduccion phi | 21.2 |
| Resistencia Pn,max | 22.4.2.1 |
| Flexion Mn | 22.3, 22.4 |
| Cortante Vn (fuera del plano) | 22.5 |
| Metodo puntal-tensor | Capitulo 23 |
| Longitudes de desarrollo | 25.4 |
| Longitudes de empalme | 25.5 |
| Estribos y ganchos | 25.7.1.3, 25.7.1.8 |
| Muros estructurales especiales | Capitulo 18 |
| Muros de concreto simple | Capitulo 14 |
| Muros de retencion | Capitulo 13 |
| Conexiones prefabricados | 16.2 |
| Conexiones a cimentaciones | 16.3 |

---

## NOTAS PARA IMPLEMENTACION EN APP

### Verificaciones Obligatorias
1. **Espesor minimo** segun tipo de muro (Tabla 11.3.1.1)
2. **Esbeltez**: klc/32h < 1.0 para que Pn > 0 en metodo simplificado
3. **Cortante maximo**: Vn <= 8*sqrt(f'c)*Acv
4. **Refuerzo minimo**: Segun nivel de cortante (bajo vs alto)
5. **Espaciamiento maximo**: Depende de tipo (colado vs prefabricado) y si hay cortante

### Flujo de Diseno Sugerido
1. Definir geometria (h, lw, hw, lc)
2. Verificar espesor minimo
3. Calcular cargas factoradas (Pu, Mu, Vu)
4. Verificar si aplica metodo simplificado (e <= h/6)
5. Calcular resistencia axial (11.5.3.1 o 22.4)
6. Verificar cortante en plano (11.5.4)
7. Verificar cortante fuera del plano (22.5)
8. Determinar refuerzo requerido
9. Verificar limites de espaciamiento
10. Detallar refuerzo en aberturas

### Factores de Reduccion phi Tipicos (21.2.2)
- Seccion controlada por compresion: phi = 0.65 (sin espiral) o 0.75 (con espiral)
- Seccion controlada por tension: phi = 0.90
- Cortante: phi = 0.75

---

*Resumen generado del ACI 318-25 Capitulo 11 para uso en desarrollo de aplicacion estructural.*
*Fecha: 2025*
