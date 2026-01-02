# ACI 318-25 - CAPITULO 15: JUNTAS COLADAS EN SITIO (CAST-IN-PLACE JOINTS)
## Resumen para Diseno de Juntas Viga-Columna y Losa-Columna

---

## INDICE

- [15.1 Alcance](#151-alcance)
- [15.2 General](#152-general)
- [15.3 Limites de Diseno](#153-limites-de-diseno)
- [15.4 Resistencia Requerida](#154-resistencia-requerida)
- [15.5 Resistencia de Diseno](#155-resistencia-de-diseno)
- [15.6 Limites de Refuerzo](#156-limites-de-refuerzo)
- [15.7 Detallado del Refuerzo](#157-detallado-del-refuerzo)
- [15.8 Transferencia de Fuerza Axial](#158-transferencia-de-fuerza-axial-a-traves-del-sistema-de-piso)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 15.1 ALCANCE

### 15.1.1 Aplicabilidad
Este capitulo aplica al diseno y detallado de juntas coladas en sitio, incluyendo:
- (a) Juntas viga-columna
- (b) Juntas losa-columna

### 15.1.2 Transferencia de Fuerza Axial
La transferencia de fuerza axial a traves del sistema de piso debe cumplir con **15.8**.

---

## 15.2 GENERAL

### 15.2.1 Cortante en Juntas Viga-Columna
El cortante resultante de la transferencia de momento debe considerarse en el diseno de la junta.

### 15.2.2 Juntas de Esquina
Deben considerarse los efectos de momentos de cierre y apertura dentro de la junta.

### 15.2.3 Materiales
- Propiedades del concreto segun Capitulo 19
- Propiedades del refuerzo segun Capitulo 20

---

## 15.3 LIMITES DE DISENO

### 15.3.1 Vigas Profundas
Si la profundidad de viga > 2 veces la profundidad de columna (en direccion del cortante):
- Disenar usando metodo puntal-tensor (Capitulo 23)
- Resistencia a cortante no debe exceder phi*Vn segun 15.5
- Cumplir requisitos de detallado de 15.7

---

## 15.4 RESISTENCIA REQUERIDA

### 15.4.1 General
- Calcular segun combinaciones de carga factoradas (Capitulo 5) y 15.4.2
- Procedimientos de analisis segun Capitulo 6

### 15.4.2 Cortante Factorado en Junta Viga-Columna
Vu se calcula en un plano a media altura de la junta usando:
- (a) Momento maximo transferido (analisis de carga factorada) para vigas continuas
- (b) Momento nominal de la viga Mn

---

## 15.5 RESISTENCIA DE DISENO

### 15.5.1 General
```
phi*Vn >= Vu
```
phi segun 21.2.1 para cortante.

### Tabla 15.5.2.1 - Resistencia Nominal a Cortante de Junta Viga-Columna

| Columna | Viga (direccion Vu) | Confinamiento | Vn (lb) |
|---------|---------------------|---------------|---------|
| Continua o cumple 15.5.2.3 | Continua o cumple 15.5.2.4 | Confinada | 24*lambda*sqrt(f'c)*Aj |
| | | No confinada | 20*lambda*sqrt(f'c)*Aj |
| | Otra | Confinada | 20*lambda*sqrt(f'c)*Aj |
| | | No confinada | 15*lambda*sqrt(f'c)*Aj |
| Otra | Continua o cumple 15.5.2.4 | Confinada | 20*lambda*sqrt(f'c)*Aj |
| | | No confinada | 15*lambda*sqrt(f'c)*Aj |
| | Otra | Confinada | 15*lambda*sqrt(f'c)*Aj |
| | | No confinada | 12*lambda*sqrt(f'c)*Aj |

*lambda = 0.75 para concreto liviano, 1.0 para concreto de peso normal*

### 15.5.2.2 Area Efectiva de la Junta (Aj)
```
Aj = profundidad de junta * ancho efectivo de junta
```
- **Profundidad de junta**: h de la columna en direccion del cortante
- **Ancho efectivo**:
  - Si viga mas ancha que columna: ancho total de columna
  - Si columna mas ancha que viga: menor de (b + h) o (b + 2x)

donde x = distancia perpendicular del eje de viga a la cara mas cercana de columna

### 15.5.2.3 Extension de Columna (Continuidad)
Una extension de columna provee continuidad si:
- (a) La columna se extiende sobre la junta al menos una profundidad h
- (b) El refuerzo longitudinal y transversal de la columna inferior continua a traves de la extension

### 15.5.2.4 Extension de Viga (Continuidad)
Una extension de viga provee continuidad si:
- (a) La viga se extiende al menos una profundidad h mas alla de la cara de la junta
- (b) El refuerzo longitudinal y transversal de la viga opuesta continua a traves de la extension

### 15.5.2.5 Junta Confinada
Una junta se considera confinada si dos vigas transversales satisfacen:
- (a) Cubren al menos 3/4 del ancho de la cara de la columna
- (b) Cubren un area >= 3/4 del producto (ancho de columna * profundidad de viga mas profunda)
- (c) Se extienden al menos una profundidad h mas alla de las caras de la junta
- (d) Contienen al menos 2 barras continuas superior e inferior (cumpliendo 9.6.1.2) y estribos No. 3 o mayores

---

## 15.6 LIMITES DE REFUERZO

### 15.6.1 Refuerzo Longitudinal de Columna
El refuerzo longitudinal de columna en juntas debe satisfacer **10.6.1.1**.
Si incluye pasadores, el area de pasadores se incluye en el calculo.

---

## 15.7 DETALLADO DEL REFUERZO

### 15.7.1 Refuerzo Transversal en Juntas Viga-Columna

**15.7.1.1** Las juntas deben satisfacer 15.7.1.2 a 15.7.1.4 a menos que:
- (a) La junta este confinada por vigas transversales segun 15.5.2.5
- (b) La junta no sea parte del sistema sismo-resistente
- (c) La junta no sea parte de estructura SDC D, E o F

**15.7.1.2** Refuerzo transversal debe consistir en:
- Amarres (25.7.2)
- Espirales (25.7.3)
- Ganchos (25.7.4)

**15.7.1.3** Al menos **dos capas** de refuerzo transversal horizontal dentro de la profundidad de la viga menos profunda

**15.7.1.4** Espaciamiento **s <= 8 in** dentro de la profundidad de la viga mas profunda

### 15.7.2 Refuerzo Transversal en Juntas Losa-Columna
Excepto donde este lateralmente soportado en cuatro lados por losa:
- Continuar refuerzo transversal de columna a traves de la junta losa-columna
- Incluye capitel, abaco y capuchon de cortante

### 15.7.3 Refuerzo Longitudinal en Juntas

**15.7.3.1** Desarrollo del refuerzo terminado en la junta segun **25.4**

**15.7.3.2** Refuerzo terminado con gancho o cabeza debe extenderse lo mas cerca posible de la cara lejana del nucleo de la junta

**15.7.3.3** Ganchos estandar deben girarse hacia la mitad de la profundidad de la viga o columna

---

## 15.8 TRANSFERENCIA DE FUERZA AXIAL A TRAVES DEL SISTEMA DE PISO

### 15.8.1 Condicion
Si f'c del sistema de piso < 0.7*f'c de la columna, usar (a), (b) o (c):

**(a)** Colocar concreto de la resistencia especificada para la columna:
- Extender al menos 2 ft dentro del sistema de piso desde la cara de la columna
- Integrar con el concreto del piso

**(b)** Disenar resistencia axial usando la resistencia menor de concreto con:
- Pasadores verticales que satisfagan 15.6.1
- Refuerzo transversal requerido

**(c)** Para juntas confinadas lateralmente en cuatro lados:
```
f'c (en junta) = 0.75*f'c(columna) + 0.35*f'c(piso)
```
**Limite**: f'c de columna usado en calculo <= 2.5*f'c del piso

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Transferencia momento losa-columna | Capitulo 8, 22.6 |
| Requisitos sismicos adicionales | Capitulo 18 |
| Metodo puntal-tensor | Capitulo 23 |
| Amarres | 25.7.2 |
| Espirales | 25.7.3 |
| Ganchos | 25.7.4 |
| Desarrollo de refuerzo | 25.4 |

---

*Resumen del ACI 318-25 Capitulo 15 para diseno de juntas coladas en sitio.*
*Fecha: 2025*
