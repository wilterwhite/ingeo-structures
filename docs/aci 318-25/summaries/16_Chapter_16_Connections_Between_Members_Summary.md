# ACI 318-25 - CAPITULO 16: CONEXIONES ENTRE MIEMBROS
## Resumen para Diseno de Conexiones y Transferencia de Carga

---

## INDICE

- [16.1 Alcance](#161-alcance)
- [16.2 Conexiones de Miembros Prefabricados](#162-conexiones-de-miembros-prefabricados)
- [16.3 Conexiones a Cimentaciones](#163-conexiones-a-cimentaciones)
- [16.4 Cortante Horizontal en Miembros Compuestos](#164-cortante-horizontal-en-miembros-compuestos)
- [16.5 Mensulas y Corbeles](#165-mensulas-y-corbeles)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 16.1 ALCANCE

### 16.1.1 Aplicabilidad
Este capitulo aplica al diseno de juntas y conexiones, incluyendo:
- (a) Conexiones de miembros prefabricados
- (b) Conexiones entre cimentaciones y miembros colados en sitio o prefabricados
- (c) Resistencia a cortante horizontal de miembros flexurales compuestos
- (d) Mensulas y corbeles

---

## 16.2 CONEXIONES DE MIEMBROS PREFABRICADOS

### 16.2.1 General

**16.2.1.1** Transferencia de fuerzas permitida mediante:
- Juntas lechadas
- Llaves de cortante
- Apoyo
- Anclajes
- Conectores mecanicos
- Refuerzo de acero
- Losa de refuerzo superior
- Combinacion de los anteriores

**16.2.1.2** Adecuacion de conexiones verificada por analisis o ensayo

**16.2.1.3** **No se permiten** detalles de conexion que dependan unicamente de friccion por cargas gravitacionales

**16.2.1.4** Disenar conexiones para resistir fuerzas y acomodar deformaciones del sistema estructural prefabricado

**16.2.1.5** Considerar efectos de restriccion de cambio volumetrico (5.3.6)

**16.2.1.6** Considerar efectos de tolerancias de fabricacion y montaje

### 16.2.2 Resistencia Requerida

**16.2.2.3** Para conexiones de apoyo, Nuc debe ser (a) o (b), pero no exceder Nuc,max:

**(a)** Conexiones sin almohadillas de apoyo:
- Calcular Nuc simultaneamente con Vu usando combinaciones de carga factoradas
- Tratar fuerza de restriccion como carga viva

**(b)** Conexiones sobre almohadillas de apoyo:
```
Nuc = 0.20 * reaccion vertical sostenida sin factorar * 1.6
```

**16.2.2.4** Si se determina coeficiente de friccion por ensayo:
```
Nuc = reaccion vertical sostenida sin factorar * coeficiente de friccion * 1.6
```

### 16.2.3 Resistencia de Diseno
```
phi*Sn >= U     [Ec. 16.2.3.1]
```

**16.2.3.3** Resistencia nominal al aplastamiento Bn segun **22.8**

**16.2.3.4** Si cortante es resultado primario, calcular Vn segun cortante-friccion (**22.9**)

### 16.2.4 Requisitos Minimos de Conexion y Amarres de Integridad

**16.2.4.1** Proveer amarres de integridad en direcciones vertical, longitudinal y transversal

**16.2.4.2** Conexiones diafragma-miembro: resistencia a tension nominal >= **300 lb/ft**

**16.2.4.3** Amarres verticales de integridad:

| Conexion | Requisito |
|----------|-----------|
| Entre columnas prefabricadas | Resistencia a tension >= 200*Ag lb |
| Entre paneles de muro prefabricados | Al menos 2 amarres, >= 10,000 lb/amarre |

### 16.2.5 Amarres para Muros de Carga Prefabricados >= 3 Pisos

**16.2.5.1** Amarres en sistemas de piso/techo:
- (a) Longitudinal y transversal: **>= 1500 lb/ft** de ancho o largo
- (b) Sobre apoyos de muro interior y entre piso/techo y muros exteriores
- (c) Dentro de 2 ft del plano del sistema de piso/techo
- (d) Longitudinal: paralelo a luces, espaciamiento <= 10 ft
- (e) Transversal: perpendicular a luces, espaciamiento <= separacion de muros
- (f) Perimetro (dentro de 4 ft del borde): **>= 16,000 lb**

**16.2.5.2** Amarres verticales:
- (a) En todos los paneles de muro, continuos en toda la altura
- (b) Resistencia a tension >= **3000 lb/ft** horizontal de muro
- (c) Al menos **2 amarres** en cada panel

### Tabla 16.2.6.2 - Dimensiones Minimas de Apoyo

| Tipo de Miembro | Distancia Minima (cara de apoyo a extremo) |
|-----------------|-------------------------------------------|
| Losa solida o hueca | Mayor de: ln/180, 2 in |
| Viga o miembro con alma | Mayor de: ln/180, 3 in |

**16.2.6.3** Almohadillas de apoyo: retroceso minimo de **0.5 in** o dimension del chaflan desde caras no armadas

---

## 16.3 CONEXIONES A CIMENTACIONES

### 16.3.1 General

**16.3.1.1** Fuerzas y momentos factorados transferidos mediante:
- Apoyo sobre concreto
- Refuerzo
- Pasadores
- Pernos de anclaje
- Conectores mecanicos

**16.3.1.2** Refuerzo/pasadores/conectores disenar para transferir:
- (a) Fuerzas de compresion que excedan resistencia al aplastamiento (22.8)
- (b) Cualquier fuerza de tension calculada

### 16.3.3 Resistencia de Diseno
```
phi*Sn >= U     [Ec. 16.3.3.1]
```

**16.3.3.5** Vn calculado segun cortante-friccion (**22.9**)

**16.3.3.6** Pernos de anclaje segun **Capitulo 17**

### 16.3.4 Refuerzo Minimo (Colado en Sitio)

| Conexion | As minimo |
|----------|-----------|
| Columna/pedestal a cimentacion | 0.005*Ag |
| Muro a cimentacion | Segun 11.6.1 |

---

## 16.4 CORTANTE HORIZONTAL EN MIEMBROS COMPUESTOS

### 16.4.1 General
Proveer transferencia completa de fuerzas de cortante horizontal en superficies de contacto.

**16.4.1.2** Si existe tension a traves de interfaz: refuerzo transversal requerido (16.4.6, 16.4.7)

### 16.4.3 Resistencia de Diseno
```
phi*Vnh >= Vu     [Ec. 16.4.3.1]
```

### Tabla 16.4.4.1 - Resistencia Nominal a Cortante Horizontal

| Mecanismo | Preparacion de Superficie | Avf,min | Vnh |
|-----------|---------------------------|---------|-----|
| Adherencia cementicia | Limpia, libre de lechada, textura ligera | No requerido | 80*bv*d |
| Cortante-friccion | Limpia, libre de lechada | Segun 16.4.6.1 | Segun 22.9 |
| Cortante-friccion | Limpia, rugosidad intencional 1/4 in | Segun 16.4.6.1 | lambda*(260 + 0.6*Avf*fyt/(bv*s))*bv*d <= 500*bv*d |

### 16.4.5 Metodo Alternativo
Entre puntos de momento cero y maximo:
```
Vuh = menor de:
  - Fuerza de compresion nominal (concreto + refuerzo)
  - As*fy + Aps*fps
```

### 16.4.6 Refuerzo Minimo
```
Avf,min = 50*bv*s/fy
```

### 16.4.7 Detallado
- **Espaciamiento longitudinal**: <= menor de 24 in, 4*(dimension minima del elemento soportado)
- Desarrollar en elementos interconectados segun 25.7.1

---

## 16.5 MENSULAS Y CORBELES

### 16.5.1 General
Aplicable para **av/d <= 1.0** y **Nuc <= Vu**

### 16.5.2 Limites Dimensionales

**16.5.2.1** Profundidad efectiva d calculada en la cara del apoyo

**16.5.2.2** Profundidad total en borde exterior del area de apoyo >= **0.5d**

**16.5.2.3** Area de apoyo no proyectar mas alla de:
- (a) Extremo de la porcion recta del refuerzo principal de tension
- (b) Cara interior de la barra de anclaje transversal

### Limites de Cortante (Concreto Peso Normal)

| Condicion | Vu/phi <= |
|-----------|-----------|
| (a) | 0.2*f'c*bw*d |
| (b) | (480 + 0.08*f'c)*bw*d |
| (c) | 1600*bw*d |

### Limites de Cortante (Concreto Liviano)

| Condicion | Vu/phi <= |
|-----------|-----------|
| (a) | (0.2 - 0.07*av/d)*f'c*bw*d |
| (b) | (800 - 280*av/d)*bw*d |

### 16.5.4 Resistencia de Diseno
```
phi*Nn >= Nuc
phi*Vn >= Vu
phi*Mn >= Mu
```

**16.5.4.3** Resistencia a tension:
```
Nn = An*fy
```

**16.5.4.4** Resistencia a cortante Vn segun cortante-friccion (**22.9**)

### 16.5.5 Limites de Refuerzo

**16.5.5.1** Area de refuerzo principal de tension Asc >= mayor de:
- (a) Af + An
- (b) (2/3)*Avf + An
- (c) 0.04*(f'c/fy)*(bw*d)

**16.5.5.2** Area total de estribos cerrados o amarres paralelos a Asc:
```
Ah = 0.5*(Asc - An)
```

### 16.5.6 Detallado

**16.5.6.3** Anclaje del refuerzo principal en cara frontal:
- (a) Soldadura a barra transversal de igual tamano
- (b) Doblez horizontal formando lazo
- (c) Otros medios para desarrollar fy

**16.5.6.6** Estribos cerrados distribuidos uniformemente dentro de **(2/3)d** medido desde el refuerzo principal de tension

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Resistencia al aplastamiento | 22.8 |
| Cortante-friccion | 22.9 |
| Anclajes | Capitulo 17 |
| Desarrollo de refuerzo | 25.4 |
| Refuerzo transversal | 25.7 |
| Integridad estructural prefabricados | PCI MNL 120 |

---

*Resumen del ACI 318-25 Capitulo 16 para diseno de conexiones entre miembros.*
*Fecha: 2025*
