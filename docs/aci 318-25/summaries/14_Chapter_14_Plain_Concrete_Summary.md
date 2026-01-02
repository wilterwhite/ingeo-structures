# ACI 318-25 - CAPITULO 14: CONCRETO SIMPLE (PLAIN CONCRETE)
## Resumen para Diseno de Miembros de Concreto Simple

---

## INDICE

- [14.1 Alcance](#141-alcance)
- [14.2 General](#142-general)
- [14.3 Limites de Diseno](#143-limites-de-diseno)
- [14.4 Resistencia Requerida](#144-resistencia-requerida)
- [14.5 Resistencia de Diseno](#145-resistencia-de-diseno)
- [14.6 Detallado del Refuerzo](#146-detallado-del-refuerzo)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 14.1 ALCANCE

### 14.1.1 Aplicabilidad
Aplica al diseno de miembros de concreto simple, incluyendo:
- (a) Miembros en estructuras de edificios
- (b) Miembros en estructuras no edificatorias (arcos, estructuras subterraneas, muros de gravedad, muros de blindaje)

### 14.1.2 Casos Permitidos
El concreto simple solo se permite en:
- (a) Miembros continuamente soportados por suelo u otros miembros estructurales
- (b) Miembros donde la accion de arco provee compresion bajo todas las condiciones de carga
- (c) Muros
- (d) Pedestales
- (e) Cimentaciones profundas coladas en sitio (altura no soportada <= 3 veces la menor dimension horizontal)

### 14.1.3 Restricciones Sismicas (SDC D, E, F)
Solo se permite concreto simple en:
- (a) Zapatas que soporten muros de concreto reforzado o mamposteria (con refuerzo longitudinal minimo)
- (b) Elementos de cimentacion para viviendas unifamiliares/bifamiliares <= 3 pisos

### 14.1.4 Prohibiciones
**No se permite** concreto simple para columnas y cabezales de pilotes.

---

## 14.2 GENERAL

### 14.2.1 Materiales
- Propiedades del concreto segun Capitulo 19
- Refuerzo de acero (si se requiere) segun Capitulo 20
- Embebidos segun 20.6

### 14.2.2 Conexion a Otros Miembros
- **14.2.2.1**: No se transmitira tension a traves de juntas de construccion, contraccion o aislamiento
- **14.2.2.2**: Los muros deben estar arriostrados contra traslacion lateral

### 14.2.3 Prefabricados
- Considerar todas las condiciones de carga desde fabricacion hasta estructura terminada
- Conectar para transferir fuerzas laterales al sistema resistente

---

## 14.3 LIMITES DE DISENO

### Tabla 14.3.1.1 - Espesor Minimo de Muros de Carga

| Tipo de Muro | Espesor Minimo |
|--------------|----------------|
| General | Mayor de: 5.5 in, 1/24*(menor de lu o lw) |
| Sotano exterior | 7.5 in |
| Cimentacion | 7.5 in |

### 14.3.2 Zapatas
- **Espesor minimo**: 8 in
- Area de base determinada por fuerzas sin factorar y presion admisible del suelo

### 14.3.3 Pedestales
- Relacion altura no soportada / dimension lateral minima promedio **<= 3**

### 14.3.4 Juntas de Contraccion y Aislamiento
Deben proporcionarse para:
- Dividir miembros en elementos flexuralmente discontinuos
- Limitar esfuerzos por restriccion de movimientos (creep, contraccion, temperatura)

---

## 14.4 RESISTENCIA REQUERIDA

### 14.4.1 General
- Calcular segun combinaciones de carga factoradas (Capitulo 5)
- Procedimientos de analisis segun Capitulo 6
- **No asumir continuidad flexural** por tension entre elementos adyacentes

### 14.4.2 Muros
Disenar para excentricidad correspondiente al momento maximo, pero **no menor que 0.10h**

### Tabla 14.4.3.2.1 - Ubicacion de Seccion Critica para Mu

| Miembro Soportado | Ubicacion de Seccion Critica |
|-------------------|------------------------------|
| Columna o pedestal | Cara de columna o pedestal |
| Columna con placa base de acero | Mitad entre cara de columna y borde de placa |
| Muro de concreto | Cara del muro |
| Muro de mamposteria | Mitad entre centro y cara del muro |

### 14.4.3.3 Cortante Unidireccional
Secciones criticas ubicadas a distancia **h** desde:
- (a) Ubicacion definida en Tabla 14.4.3.2.1
- (b) Cara de cargas concentradas o areas de reaccion

### 14.4.3.4 Cortante Bidireccional
Perimetro bo minimo, pero no mas cerca de **h/2** de:
- (a) Ubicacion segun Tabla 14.4.3.2.1
- (b) Cara de cargas concentradas
- (c) Cambios de espesor de zapata

---

## 14.5 RESISTENCIA DE DISENO

### 14.5.1 General
Para cada combinacion de carga:
```
phi*Mn >= Mu
phi*Pn >= Pu
phi*Vn >= Vu
phi*Bn >= Bu
```

### Consideraciones Clave:
- **14.5.1.3**: Se permite considerar resistencia a tension del concreto
- **14.5.1.4**: Calculos basados en relacion lineal esfuerzo-deformacion
- **14.5.1.6**: No se asigna resistencia al refuerzo de acero
- **14.5.1.7**: Para concreto colado contra suelo, usar **h = espesor especificado - 2 in**

### 14.5.2 Flexion
```
Mn = 5*lambda*sqrt(f'c)*Sm     [Ec. 14.5.2.1a] (cara de tension)
Mn = 0.85*f'c*Sm               [Ec. 14.5.2.1b] (cara de compresion)
```
Usar el **menor** de ambos valores. Sm = modulo de seccion elastico.

### 14.5.3 Compresion Axial
```
Pn = 0.60*f'c*Ag*[1 - (lc / 32h)^2]     [Ec. 14.5.3.1]
```
Para cimentaciones profundas con soporte lateral del suelo: usar lc = 0

### Tabla 14.5.4.1 - Flexion y Compresion Axial Combinadas

| Ubicacion | Ecuacion de Interaccion |
|-----------|------------------------|
| Cara de tension | Mu/Sm - Pu/Ag <= phi*5*lambda*sqrt(f'c) |
| Cara de compresion | Mu/(phi*Mn) + Pu/(phi*Pn) <= 1.0 |

### 14.5.4.2 Metodo Simplificado para Muros
Si Mu <= Pu*(h/6), no se requiere considerar Mu:
```
Pn = 0.45*f'c*Ag*[1 - (lc / 32h)^2]     [Ec. 14.5.4.2]
```

### Tabla 14.5.5.1 - Resistencia Nominal a Cortante

| Accion de Cortante | Vn |
|--------------------|----|
| Unidireccional | (4/3)*lambda*sqrt(f'c)*bw*h |
| Bidireccional | Menor de: (1 + 2/beta)*(4/3)*lambda*sqrt(f'c)*bo*h |
|                | 2*(4/3)*lambda*sqrt(f'c)*bo*h |

*beta = relacion lado largo / lado corto del area de carga*

### Tabla 14.5.6.1 - Resistencia Nominal al Aplastamiento

| Condicion | Bn |
|-----------|-----|
| Superficie de apoyo mas ancha que area cargada | Menor de: sqrt(A2/A1)*(0.85*f'c*A1), 2*(0.85*f'c*A1) |
| Otros casos | 0.85*f'c*A1 |

---

## 14.6 DETALLADO DEL REFUERZO

### 14.6.1 Aberturas
- Proporcionar al menos **2 barras No. 5** alrededor de ventanas, puertas y aberturas similares
- Las barras deben extenderse al menos **24 in** mas alla de las esquinas de las aberturas
- O desarrollar fy en tension en las esquinas

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Propiedades del concreto | Capitulo 19 |
| Propiedades del acero | Capitulo 20 |
| Factores phi | 21.2 |
| Embebidos | 20.6 |
| Combinaciones de carga | Capitulo 5 |
| Procedimientos de analisis | Capitulo 6 |

---

*Resumen del ACI 318-25 Capitulo 14 para diseno de concreto simple.*
*Fecha: 2025*
