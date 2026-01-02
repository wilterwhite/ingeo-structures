# ACI 318-25 - CAPITULO 25: DETALLES DE REFUERZO (REINFORCEMENT DETAILS)
## Resumen para Desarrollo, Empalmes y Detallado

---

## INDICE

- [25.1 Alcance](#251-alcance)
- [25.2 Espaciamiento Minimo del Refuerzo](#252-espaciamiento-minimo-del-refuerzo)
- [25.3 Ganchos Sismicos y Crossties](#253-ganchos-sismicos-y-crossties)
- [25.4 Longitud de Desarrollo](#254-longitud-de-desarrollo)
- [25.5 Empalmes de Refuerzo](#255-empalmes-de-refuerzo)
- [25.6 Paquetes de Barras](#256-paquetes-de-barras)
- [25.7 Refuerzo Transversal](#257-refuerzo-transversal)
- [25.8 Ganchos Estandar](#258-ganchos-estandar)
- [25.9 Requisitos Adicionales](#259-requisitos-adicionales)
- [Referencias Cruzadas](#referencias-cruzadas)
- [Formulas de Referencia Rapida](#formulas-de-referencia-rapida)

---

## 25.1 ALCANCE

### 25.1.1 Aplicabilidad
Este capitulo aplica al detallado del refuerzo, incluyendo:
- (a) Espaciamiento, recubrimiento y doblado del refuerzo
- (b) Longitud de desarrollo del refuerzo
- (c) Empalmes del refuerzo
- (d) Paquetes de barras
- (e) Refuerzo transversal
- (f) Requisitos de postensado

---

## 25.2 ESPACIAMIENTO MINIMO DEL REFUERZO

### 25.2.1 Refuerzo No Pretensado

**Tabla 25.2.1 - Espaciamiento Minimo Libre**

| Tipo de Miembro | Espaciamiento Minimo |
|-----------------|---------------------|
| Vigas, columnas, estribos | Mayor de: db, 1 in, (4/3)*dagg |
| Muros, losas | Mayor de: db, 1 in, (4/3)*dagg |
| Barras en capas | >= 1 in entre capas |
| Paquetes de barras | Espaciamiento basado en diametro equivalente |

*dagg = tamano maximo del agregado grueso*

### 25.2.3 Tendones Pretensados

| Tipo | Espaciamiento Minimo |
|------|---------------------|
| Torones de 1/2 in | 2 in (extremos), 1-1/3 in (centro) |
| Torones de 0.6 in | 2-1/2 in (extremos), 1.6 in (centro) |
| Barras | 3*db |

---

## 25.3 GANCHOS SISMICOS Y CROSSTIES

### 25.3.1 Gancho Sismico
- Doblez de **135 grados** o mas
- Extension de **6*db** o **3 in** (mayor)
- Extension se proyecta hacia el interior del nucleo confinado

### 25.3.2 Crosstie
- Barra continua con gancho sismico en un extremo
- Gancho de 90 grados en el otro extremo (enganchando barra longitudinal)
- **Alternar** ganchos de 90 grados en direccion opuesta a lo largo del miembro

### 25.3.3 Extension de Ganchos de 90 Grados
| Grado de Refuerzo | Extension Minima |
|-------------------|------------------|
| Grado 60 | 6*db |
| Grado 80 | 8*db |
| Grado 100 | 10*db |

---

## 25.4 LONGITUD DE DESARROLLO

### 25.4.1 General
La longitud de desarrollo debe proveerse donde sea requerido por analisis.

### 25.4.2 Desarrollo de Barras Corrugadas en Tension

**Ecuacion General:**
```
ld = (fy*psi_t*psi_e*psi_s*psi_g / (25*lambda*sqrt(f'c))) * db     [Ec. 25.4.2.4a]
```

**Ecuacion Simplificada (Si cumple condiciones de espaciamiento y recubrimiento):**
```
ld = (fy*psi_t*psi_e / (20*lambda*sqrt(f'c))) * db     [Ec. 25.4.2.4b]
```

### Tabla 25.4.2.5 - Factores de Modificacion

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_t** (ubicacion) | Mas de 12 in de concreto debajo | 1.3 |
| | Otros casos | 1.0 |
| **psi_e** (epoxico) | Recubrimiento < 3*db o espaciamiento < 6*db | 1.5 |
| | Otros casos epoxico | 1.2 |
| | Sin recubrimiento epoxico | 1.0 |
| **psi_s** (tamano) | No. 6 o menor | 0.8 |
| | No. 7 o mayor | 1.0 |
| **psi_g** (grado) | Grado 60 | 1.0 |
| | Grado 80 | 1.15 |
| | Grado 100 | 1.3 |
| **lambda** | Concreto peso normal | 1.0 |
| | Concreto liviano | Ver 19.2.4 |

**Limites:**
- psi_t * psi_e <= 1.7
- ld,min >= 12 in

### 25.4.3 Desarrollo de Ganchos Estandar en Tension

**Ecuacion:**
```
ldh = (fy*psi_e*psi_r*psi_o*psi_c*psi_g / (55*lambda*sqrt(f'c))) * db     [Ec. 25.4.3.1]
```

### Tabla 25.4.3.2 - Factores para Ganchos

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_r** (confinamiento) | Gancho en esquina interior de columna | 0.8 |
| | Otros casos | 1.0 |
| **psi_o** (confinamiento) | Refuerzo perpendicular dentro del gancho | 0.8 |
| | Otros casos | 1.0 |
| **psi_c** (recubrimiento) | Recubrimiento lateral >= 2.5 in (cola gancho) | 0.8 |
| | Recubrimiento >= 2 in (cola de gancho 180 grados) | 0.8 |
| | Otros casos | 1.0 |

**Limites:**
- ldh,min >= mayor de 8*db, 6 in

### 25.4.4 Desarrollo de Barras con Cabeza en Tension

**Ecuacion:**
```
ldt = (fy*psi_e*psi_p*psi_o*psi_g / (22*lambda*sqrt(f'c))) * db     [Ec. 25.4.4.1]
```

**Requisitos:**
- Area neta de apoyo de cabeza Abrg >= 4*Ab
- Recubrimiento libre >= db
- Espaciamiento libre >= 2*db

**Limites:**
- ldt,min >= mayor de 8*db, 6 in

### 25.4.9 Desarrollo de Barras Corrugadas en Compresion

**Ecuacion:**
```
ldc = (fy*psi_r*psi_g / (50*lambda*sqrt(f'c))) * db >= 0.0003*fy*db     [Ec. 25.4.9.1]
```

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_r** | Confinado con espirales o estribos | 0.75 |
| | Otros casos | 1.0 |

**Limite:** ldc,min >= 8 in

### 25.4.10 Desarrollo de Alambre Corrugado

```
ld = (fy*psi_e*psi_s*psi_g / (25*lambda*sqrt(f'c))) * db     [Ec. 25.4.10.1]
```
**Limite:** ld,min >= 8 in

### 25.4.11 Desarrollo de Malla Soldada de Alambre

| Tipo | Desarrollo |
|------|------------|
| Corrugada | Segun 25.4.10 + factor por barras transversales |
| Lisa | Desarrollo mecanico en intersecciones soldadas |

---

## 25.5 EMPALMES DE REFUERZO

### 25.5.1 General

**25.5.1.1** Empalmes permitidos:
- (a) Empalmes por traslape
- (b) Empalmes mecanicos
- (c) Empalmes soldados
- (d) Empalmes de extremo

### 25.5.2 Empalmes por Traslape de Barras Corrugadas en Tension

### Tabla 25.5.2.1 - Longitud de Empalme por Traslape

| Clase | As provisto / As requerido | Longitud de Traslape |
|-------|----------------------------|---------------------|
| A | >= 2.0 en toda la longitud del empalme | Mayor de: 1.0*ld, 12 in |
| B | Otros casos | Mayor de: 1.3*ld, 12 in |

**25.5.2.2** Empalmes escalonados:
- Espaciamiento centro a centro de empalmes adyacentes >= Clase A

### 25.5.3 Empalmes por Traslape de Barras Corrugadas en Compresion

```
lsc = mayor de: 0.0005*fy*db, 12 in     (f'c >= 3000 psi)
```

**Factores de modificacion:**
- Si f'c < 3000 psi: multiplicar por 1.33
- Si confinado con estribos: multiplicar por 0.83
- Si confinado con espirales: multiplicar por 0.75

### 25.5.4 Empalmes de Extremo

Para compresion unicamente:
- Barras cortadas perpendicular
- Superficies en contacto completo
- Dispositivo de soporte adecuado

### 25.5.5 Empalmes por Traslape en Columnas

**25.5.5.1** Para combinacion de compresion y tension:
- Determinar empalme basado en esfuerzos de traccion o compresion

**25.5.5.3** En zonas donde analisis indica traccion:
- Clase B si As provisto >= 2 * As requerido
- Clase B empalme completo en otros casos

### 25.5.6 Limites de Empalmes por Traslape

| Restriccion | Requisito |
|-------------|-----------|
| Barras No. 14 y No. 18 | No empalmar por traslape |
| Paquetes | Solo 2 barras empalmadas en un punto |

### 25.5.7 Empalmes Mecanicos y Soldados

**Empalmes mecanicos:**
- Tipo 1: Desarrollar 125% fy de la barra
- Tipo 2: Desarrollar resistencia a traccion especificada de la barra

**Empalmes soldados:**
- Desarrollar 125% fy de la barra

---

## 25.6 PAQUETES DE BARRAS

### 25.6.1 General
- Maximo **4 barras** por paquete
- Barras paralelas en contacto

### 25.6.2 Terminacion de Barras
- Terminar barras individuales a diferentes puntos
- Espaciamiento minimo **40*db** entre terminaciones (dentro del claro)

### 25.6.3 Desarrollo y Empalmes
- Usar diametro equivalente db,eq para calcular ld
```
db,eq = db * sqrt(n)     donde n = numero de barras
```

### 25.6.4 Barras Individuales
- Barras mayores a No. 11 no incluir en paquetes (excepto para sismo)

---

## 25.7 REFUERZO TRANSVERSAL

### 25.7.1 General
- Refuerzo transversal requerido segun capitulos de miembros
- Desarrollar en elementos interconectados segun 25.7.1.1

### 25.7.2 Amarres (Ties)

**Tamano minimo:**
| Refuerzo Longitudinal | Amarre Minimo |
|-----------------------|---------------|
| No. 10 o menor | No. 3 |
| No. 11, 14, 18 | No. 4 |
| Paquetes | No. 4 |

**Espaciamiento maximo s:**
- (a) 16*db de barra longitudinal
- (b) 48*db de amarre
- (c) Menor dimension del miembro

**Configuracion:**
- Cada barra de esquina y alternadas soportadas por esquina de amarre
- Angulo de esquina <= 135 grados
- Ninguna barra a mas de 6 in libre de soporte lateral

### 25.7.3 Espirales

**Tamano:** >= No. 3 (db >= 3/8 in)

**Espaciamiento claro:**
- Minimo: 1 in o 1-1/3*dagg
- Maximo: 3 in

**Anclaje:** 1.5 vueltas adicionales en cada extremo

### 25.7.4 Zunchos (Hoops)

**Definicion:** Amarre cerrado o amarres cerrados continuamente enrollados

**Requisitos:**
- Ganchos sismicos en ambos extremos (25.3.1)
- Crosstie con gancho sismico en un extremo permitido

**Espaciamiento:** Segun requisitos sismicos del Capitulo 18

---

## 25.8 GANCHOS ESTANDAR

### Tabla 25.8.1 - Dimensiones de Ganchos Estandar

| Tipo | Doblez | Extension |
|------|--------|-----------|
| 180 grados | Radio >= 3*db (No. 3-8), 4*db (No. 9-11), 5*db (No. 14-18) | 4*db >= 2.5 in |
| 90 grados | Mismo radio | 12*db |
| Estribos 90 grados | Radio >= 2*db (No. 3-5), 3*db (No. 6-8) | 6*db |
| Estribos 135 grados | Mismo radio | 6*db |

### 25.8.2 Ganchos para Estribos y Amarres

| Barra | Doblez | Extension |
|-------|--------|-----------|
| No. 3 a No. 5 | 90 grados | 6*db |
| No. 3 a No. 5 | 135 grados | 6*db |
| No. 6 a No. 8 | 90 grados | 12*db |
| No. 6 a No. 8 | 135 grados | 6*db |

---

## 25.9 REQUISITOS ADICIONALES

### 25.9.1 Recubrimiento de Concreto
Segun Capitulo 20 (Tabla 20.5.1.3.1 y siguientes)

### 25.9.2 Barras Dobladas

**Radio minimo de doblado:**
| Tamano de Barra | Radio Minimo |
|-----------------|--------------|
| No. 3 a No. 8 | 3*db |
| No. 9 a No. 11 | 4*db |
| No. 14 y No. 18 | 5*db |

**No doblar barras embebidas** a menos que se permita especificamente

### 25.9.3 Refuerzo de Integridad Estructural

**25.9.3.1** Requisitos para estructuras coladas en sitio:
- Vigas perimetrales: 1/6 de As(-) superior o 2 barras continuas
- Vigas no perimetrales: 1/4 de As(-) superior o 2 barras continuas
- Refuerzo inferior: Al menos 1 barra continua

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Recubrimiento minimo | 20.5 |
| Durabilidad del refuerzo | 20.6 |
| Factores de reduccion | 21.2 |
| Requisitos sismicos | 18.6-18.8, 18.10 |
| Vigas | 9.7 |
| Columnas | 10.7 |
| Muros | 11.7 |
| Conexiones | 15.7, 16.5 |
| Puntal-tensor | 23.6-23.8 |

---

## FORMULAS DE REFERENCIA RAPIDA

### Desarrollo en Tension (Simplificado, Grado 60)
```
ld = 0.05*fy*db / sqrt(f'c) = 3*db*sqrt(fy) / sqrt(f'c)
```
*Para condiciones favorables de espaciamiento y recubrimiento*

### Empalme Clase B
```
lst = 1.3*ld
```

### Longitud de Gancho (Simplificado, Grado 60)
```
ldh = 0.02*fy*db / sqrt(f'c)
```

### Desarrollo en Compresion
```
ldc = 0.02*fy*db / sqrt(f'c) >= 0.0003*fy*db
```

---

*Resumen del ACI 318-25 Capitulo 25 para detalles de refuerzo.*
*Fecha: 2025*
