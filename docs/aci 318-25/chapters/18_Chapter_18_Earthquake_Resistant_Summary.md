# ACI 318-25 - CAPITULO 18: ESTRUCTURAS RESISTENTES A SISMOS
## Resumen para Diseno de Muros Estructurales

---

## 18.1 ALCANCE

### 18.1.1 Aplicabilidad
Aplica al diseno de estructuras asignadas a SDC B a F, incluyendo:
- (a) Sistemas designados como parte del SFRS
- (b) Miembros no designados como parte del SFRS

### Tabla R18.2 - Secciones a Satisfacer por SDC

| Componente | SDC B | SDC C | SDC D, E, F |
|------------|-------|-------|-------------|
| Analisis y diseno | 18.2.2 | 18.2.2 | 18.2.2, 18.2.4 |
| Materiales | — | — | 18.2.5 - 18.2.8 |
| Muros y vigas de acople | — | — | 18.10 |
| Muros prefabricados | — | 18.5 | 18.5, 18.11 |
| Diafragmas | — | 18.12.1.2 | 18.12 |
| Cimentaciones | — | 18.13 | 18.13 |
| Miembros no parte del SFRS | — | — | 18.14 |

---

## 18.2 GENERAL

### 18.2.5 Concreto en Muros Especiales
- Resistencia segun 19.2.1
- Concreto liviano: f'c max = **5000 psi** para calculos de diseno

### 18.2.6 Refuerzo en Muros Especiales
Grados ASTM A706 permitidos: **60, 80 y 100**

| Aplicacion | fyt Maximo |
|------------|-----------|
| Refuerzo de confinamiento | 100,000 psi |
| Resistencia nominal al cortante | 60,000 psi |

### 18.2.7 Empalmes Mecanicos
| Clase | Ubicacion Permitida |
|-------|---------------------|
| Clase S | Cualquier ubicacion |
| Clase G | Prohibida donde empalmes de traslape estan prohibidos, en vigas de acople, y dentro de 2h de secciones criticas |
| Clase L | NO permitida en sistemas especiales |

### 18.2.8 Empalmes Soldados
**NO permitidos** en muros estructurales especiales ni vigas de acople.

---

## 18.10 MUROS ESTRUCTURALES ESPECIALES

### 18.10.1 Alcance
Aplica a muros especiales, muros acoplados ductiles, vigas de acople y pilares de muro del SFRS.

### Tabla R18.10.1 - Clasificacion de Segmentos

| hw/lw | lw/bw <= 2.5 | 2.5 < lw/bw <= 6.0 | lw/bw > 6.0 |
|-------|--------------|--------------------|-------------|
| < 2.0 | Muro | Muro | Muro |
| >= 2.0 | Pilar (18.10.8.1) | Pilar (columna o alternativo) | Muro |

---

### 18.10.2 Refuerzo

#### 18.10.2.1 Refuerzo Distribuido Minimo

| Parametro | Requisito |
|-----------|-----------|
| rho_l (vertical) | >= **0.0025** |
| rho_t (horizontal) | >= **0.0025** |
| Espaciamiento maximo | **18 in** |

#### 18.10.2.2 Dos Cortinas de Refuerzo
Requeridas si:
- Vu > 2*lambda*sqrt(f'c)*Acv, O
- hw/lw >= 2.0

#### 18.10.2.3 Desarrollo y Empalmes
| Requisito | Descripcion |
|-----------|-------------|
| (a) | Refuerzo longitudinal se extiende >= 12 ft arriba donde no se requiere |
| (b) | En zonas de fluencia: desarrollar para **1.25fy** |
| (c) | Empalmes de traslape en regiones de borde: **PROHIBIDOS** sobre hsx y ld debajo de secciones criticas |

---

### 18.10.3 Fuerzas de Diseno

#### 18.10.3.3 Amplificacion de Cortante
```
Ve = Omega_v * omega_v * Vu,Eh
```

#### Tabla 18.10.3.3.3 - Factores de Amplificacion

| Condicion | Omega_v | omega_v |
|-----------|---------|---------|
| hwcs/lw <= 1.0 | 1.0 | 1.0 |
| 1.0 < hwcs/lw < 2.0 | Interpolacion 1.0-1.5 | 1.0 |
| hwcs/lw >= 2.0 | 1.5 | 0.8 + 0.09*hn^(1/3) >= 1.0 |

Donde:
- hwcs = Altura del muro desde seccion critica
- hn = Altura total del edificio (pies)

**Alternativa**: Se permite tomar Omega_v * omega_v = Omega_o

---

### 18.10.4 Resistencia al Cortante

#### 18.10.4.1 Ecuacion de Resistencia Nominal
```
Vn = (alpha_c * lambda * sqrt(f'c) + rho_t * fyt) * Acv     [Ec. 18.10.4.1]
```

#### Coeficiente alpha_c

| hw/lw | alpha_c |
|-------|---------|
| <= 1.5 | 3 |
| >= 2.0 | 2 |
| 1.5 < hw/lw < 2.0 | Interpolacion lineal |

**Limite**: f'c <= 12,000 psi

#### 18.10.4.3 Requisito para Muros Bajos
Si hw/lw <= 2.0: **rho_l >= rho_t**

#### 18.10.4.4 Limites de Resistencia
- Todos los segmentos: Vn <= Sum(alpha_sh * 8 * sqrt(f'c) * Acv)
- Segmento individual: Vn <= alpha_sh * 10 * sqrt(f'c) * Acw

Factor alpha_sh:
```
alpha_sh = 0.7 * (1 + (bw + bcf) * tcf / Acx)^2     [Ec. 18.10.4.4]
```
- 1.0 <= alpha_sh <= 1.2
- Se permite tomar alpha_sh = 1.0

---

### 18.10.5 Diseno por Flexion y Carga Axial

#### 18.10.5.2 Ancho Efectivo del Ala
```
bf = menor de:
    - 0.5 * distancia a alma adyacente
    - 0.25 * altura total sobre la seccion
```

---

### 18.10.6 Elementos de Borde

#### 18.10.6.1 Dos Enfoques de Diseno

| Enfoque | Seccion | Aplicacion |
|---------|---------|------------|
| Basado en desplazamiento | 18.10.6.2 | hwcs/lw >= 2.0, continuos desde base |
| Basado en esfuerzos | 18.10.6.3 | Metodo tradicional |

#### 18.10.6.2 Enfoque Basado en Desplazamiento

**(a) Requiere elementos de borde especiales cuando:**
```
1.5 * delta_u/hwcs >= lw/(600*c)     [Ec. 18.10.6.2a]
```
- delta_u/hwcs no debe tomarse menor que 0.005

**(b) Extension vertical:** Mayor de lw y Mu/(4Vu)

**(c) Ancho minimo:** b >= sqrt(c * lw)/40

**(d) Capacidad de deriva:**
```
delta_c/hwcs = (1/100) * [4 - 1/50 - (lw/b)(c/b) - Ve/(8*sqrt(f'c)*Acv)]
```
- Minimo: delta_c/hwcs >= 0.015
- Requisito: delta_c/hwcs >= 1.5 * delta_u/hwcs

#### 18.10.6.3 Enfoque Basado en Esfuerzos

| Condicion | Accion |
|-----------|--------|
| sigma_max >= 0.2*f'c | Requiere elementos de borde |
| sigma < 0.15*f'c | Permite discontinuar |

#### 18.10.6.4 Requisitos para Elementos de Borde Especiales

| Parametro | Requisito |
|-----------|-----------|
| **(a) Extension horizontal** | Mayor de: c - 0.1*lw y c/2 |
| **(b) Ancho minimo** | b >= hu/16 |
| **(c) Si c/lw >= 3/8** | b >= 12 in |
| **(e) Refuerzo transversal** | Segun 18.7.5.2(a)-(d), 18.7.5.3 |
| **(f) Espaciamiento hx** | <= menor de 14" y (2/3)b |

#### Tabla 18.10.6.4(g) - Refuerzo Transversal

| Tipo | Expresiones |
|------|-------------|
| Ash/sbc (rectangular) | Mayor de: 0.3*(Ag/Ach - 1)*(f'c/fyt) y 0.09*(f'c/fyt) |
| rho_s (espiral) | Mayor de: 0.45*(Ag/Ach - 1)*(f'c/fyt) y 0.12*(f'c/fyt) |

#### Tabla 18.10.6.5(b) - Espaciamiento Maximo sin Elementos de Borde Especiales

| Grado | Cerca de seccion critica | Otras ubicaciones |
|-------|-------------------------|-------------------|
| 60 | Menor de: 6db, 6" | Menor de: 8db, 8" |
| 80 | Menor de: 5db, 6" | Menor de: 6db, 6" |
| 100 | Menor de: 4db, 6" | Menor de: 6db, 6" |

---

### 18.10.7 Vigas de Acoplamiento

#### Clasificacion por Relacion de Aspecto

| ln/h | Tipo de Refuerzo |
|------|------------------|
| >= 4 | Longitudinal + transversal (como 18.6) |
| < 2 con Vu >= 4*lambda*sqrt(f'c)*Acw | Diagonal obligatorio |
| 2 <= ln/h < 4 | Diagonal o longitudinal |

#### 18.10.7.4 Resistencia con Refuerzo Diagonal
```
Vn = 2 * Avd * fy * sin(alpha) <= 10*sqrt(f'c)*Acw     [Ec. 18.10.7.4]
```

**Requisitos:**
- Minimo 4 barras por grupo diagonal, en 2+ capas
- Confinamiento individual (c) o de seccion completa (d)

#### Tabla 18.10.7.4 - Espaciamiento de Confinamiento

| Grado | Espaciamiento Maximo |
|-------|---------------------|
| 60 | Menor de: 6db, 6" |
| 80 | Menor de: 5db, 6" |
| 100 | Menor de: 4db, 6" |

#### 18.10.7.5 Redistribucion de Cortante
- Permitida para vigas con ln/h >= 2
- Maximo 20% del valor de analisis
- Sum(phi*Vn) >= Sum(Ve)

---

### 18.10.8 Pilares de Muro (Wall Piers)

#### 18.10.8.1 Requisitos Generales
Satisfacer requisitos de columnas especiales (18.7.4, 18.7.5, 18.7.6).

**Alternativa para lw/bw > 2.5:**

| Requisito | Especificacion |
|-----------|----------------|
| (a) Cortante de diseno | Segun 18.7.6.1, o <= Omega_o * Vu |
| (b) Vn y refuerzo | Segun 18.10.4 |
| (c) Refuerzo transversal | Estribos cerrados |
| (d) Espaciamiento vertical | <= 6" |
| (e) Extension | >= 12" arriba y abajo |
| (f) Elementos de borde | Si se requiere por 18.10.6.3 |

---

### 18.10.9 Muros Acoplados Ductiles

| Elemento | Requisito |
|----------|-----------|
| Muros individuales | hwcs/lw >= 2, satisfacer 18.10 |
| Vigas de acoplamiento | ln/h >= 2 en todos los niveles |
| 90% de los niveles | ln/h <= 5 |

---

### 18.10.10 Juntas de Construccion
- Especificar segun 26.5.6
- Superficies rugosas segun Tabla 22.9.4.2

---

## 18.12 DIAFRAGMAS Y CERCHAS

### 18.12.6 Espesor Minimo

| Tipo | Espesor Minimo |
|------|----------------|
| Losas de concreto | 2" |
| Compuestas sobre prefabricado | 2" |
| No compuestas sobre prefabricado | 2-1/2" |

### 18.12.7 Refuerzo
- Espaciamiento maximo: **18"**
- Todo el refuerzo para fy en tension
- Colectores: Esfuerzo promedio <= phi*fy con fy <= 60,000 psi

### 18.12.9 Resistencia al Cortante
```
Vn = Acv * (2*lambda*sqrt(f'c) + rho_t*fy)     [Ec. 18.12.9.1]
Vn <= 8*sqrt(f'c) * Acv
```

---

## 18.13 CIMENTACIONES

### 18.13.2 Zapatas y Cabezales (SDC D, E, F)

| Seccion | Requisito |
|---------|-----------|
| 18.13.2.2 | Refuerzo longitudinal debe desarrollar fy en tension |
| 18.13.2.3 | Columnas empotradas: ganchos 90 hacia el centro |
| 18.13.2.4 | Cerca del borde (<= 0.5*profundidad): transversal segun 18.7.5.2-18.7.5.4 |

### 18.13.4 Amarres Sismicos
- SDC C, D, E, F: Interconectar cabezales
- Resistencia >= 0.1*SDS * (mayor carga D+L factorada)
- Vigas de amarre: dimension min >= L/20, max 18"

---

## 18.14 MIEMBROS NO PARTE DEL SFRS

### 18.14.2 Acciones de Diseno
Evaluar para combinaciones de gravedad actuando con desplazamiento de diseno delta_u.

### 18.14.3 Vigas, Columnas y Nudos

**Cuando momentos/cortantes inducidos NO exceden resistencia:**

| Elemento | Requisitos |
|----------|------------|
| Vigas | Transversal @ <= d/2 |
| Columnas | Espirales/estribos @ <= menor de 6db, 6" en toda altura |
| Columnas Pu > 0.35Po | Transversal >= 0.5 * Tabla 18.7.5.4 en lo |

**Cuando momentos/cortantes inducidos EXCEDEN resistencia:**
- Vigas: 18.6.5
- Columnas: 18.7.4, 18.7.5, 18.7.6

### 18.14.5 Conexiones Losa-Columna

**Requiere refuerzo de cortante cuando:**
- No pretensada: Delta_x/hsx >= 0.035 - (1/20)*(vuv/phi*vc)
- Postensada: Delta_x/hsx >= 0.040 - (1/20)*(vuv/phi*vc)

**Exento si:**
- No pretensada: Delta_x/hsx <= 0.005
- Postensada: Delta_x/hsx <= 0.01

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Combinaciones de carga | Capitulo 5 |
| Analisis estructural | Capitulo 6 |
| Muros (general) | Capitulo 11 |
| Juntas viga-columna | Capitulo 15 |
| Anclajes sismicos | 17.10 |
| Propiedades del concreto | Capitulo 19 |
| Propiedades del refuerzo | Capitulo 20 |
| Factores phi | Capitulo 21, 21.2.4 |
| Resistencia seccional | Capitulo 22 |
| Desarrollo y empalmes | Capitulo 25 |

---

*Resumen del ACI 318-25 Capitulo 18 para diseno de muros estructurales especiales.*
*Fecha: 2025*
