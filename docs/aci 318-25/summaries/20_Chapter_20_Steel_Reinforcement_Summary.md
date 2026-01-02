# ACI 318-25 - CAPITULO 20: ACERO DE REFUERZO
## Propiedades, Durabilidad y Embebidos

---

## INDICE

- [20.1 Alcance](#201-alcance)
- [20.2 Propiedades del Refuerzo No Pretensado](#202-propiedades-del-refuerzo-no-pretensado)
- [20.3 Propiedades del Refuerzo Pretensado](#203-propiedades-del-refuerzo-pretensado)
- [20.4 Requisitos de Ductilidad](#204-requisitos-de-ductilidad)
- [20.5 Recubrimiento de Concreto](#205-recubrimiento-de-concreto)
- [20.6 Proteccion Contra Corrosion](#206-proteccion-contra-corrosion)
- [20.7 Embebidos y Conexiones](#207-embebidos-y-conexiones)
- [20.8 Requisitos Especiales](#208-requisitos-especiales)
- [20.9 Identificacion y Almacenamiento](#209-identificacion-y-almacenamiento)
- [Tablas de Barras](#tablas-de-barras)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 20.1 ALCANCE

### 20.1.1 Aplicabilidad
Este capitulo aplica a:
- (a) Propiedades del acero de refuerzo para diseno
- (b) Requisitos de durabilidad del acero
- (c) Embebidos en el concreto

---

## 20.2 PROPIEDADES DEL REFUERZO NO PRETENSADO

### 20.2.1 Barras Corrugadas

**Tabla 20.2.1.1 - Normas ASTM para Barras Corrugadas**

| Norma | Descripcion | Grados |
|-------|-------------|--------|
| ASTM A615 | Acero al carbono | 40, 60, 80, 100 |
| ASTM A706 | Baja aleacion (soldable, sismico) | 60, 80, 100 |
| ASTM A996 | Riel y eje | 40, 50, 60 |
| ASTM A1035 | Baja aleacion alta resistencia | 100, 120 |

### 20.2.2 Propiedades de Diseno

**Tabla 20.2.2.1 - Propiedades de Diseno del Refuerzo**

| Propiedad | Simbolo | Valor |
|-----------|---------|-------|
| Modulo de elasticidad | Es | 29,000,000 psi |
| Resistencia a fluencia | fy | Segun grado |
| Deformacion de fluencia | epsilon_y | fy / Es |

### Tabla 20.2.2.2 - Resistencia a Fluencia por Grado

| Grado | fy (psi) | fy (MPa) |
|-------|----------|----------|
| 40 | 40,000 | 280 |
| 60 | 60,000 | 420 |
| 80 | 80,000 | 550 |
| 100 | 100,000 | 690 |
| 120 | 120,000 | 830 |

### 20.2.3 Limites de fy para Diseno

**Tabla 20.2.3.1 - Limites de fy**

| Aplicacion | fy max (psi) |
|------------|--------------|
| Flexion y carga axial | 80,000 (general), 100,000 (sismico con restricciones) |
| Cortante (estribos) | 60,000 (general), 80,000 (con restricciones) |
| Torsion | 60,000 |
| Anclajes | 60,000 |
| Refuerzo de cortante-friccion | 60,000 |
| Sismico - marcos especiales | 60,000 o 80,000 (18.2.6) |
| Sismico - muros especiales | 60,000, 80,000 o 100,000 (18.2.7) |

### 20.2.4 Malla Soldada de Alambre

**Tabla 20.2.4.1 - Normas para Malla Soldada**

| Norma | Tipo |
|-------|------|
| ASTM A185 | Lisa |
| ASTM A497 | Corrugada |

**Limites:**
- fy <= 80,000 psi
- Espaciamiento de alambres <= 16 in (losas) o 12 in (otros)

---

## 20.3 PROPIEDADES DEL REFUERZO PRETENSADO

### 20.3.1 Tipos de Tendones

**Tabla 20.3.1.1 - Normas para Tendones**

| Norma | Tipo | fpu (psi) |
|-------|------|-----------|
| ASTM A416 | Toron de 7 alambres | 250,000 - 270,000 |
| ASTM A421 | Alambre | 235,000 - 250,000 |
| ASTM A722 | Barra de alta resistencia | 150,000 |

### 20.3.2 Propiedades de Diseno

**Tabla 20.3.2.1 - Propiedades del Acero de Pretensado**

| Propiedad | Toron | Alambre | Barra |
|-----------|-------|---------|-------|
| Ep (psi) | 28,500,000 | 29,000,000 | 29,000,000 |
| fpy/fpu | 0.85 (bajo relax), 0.90 (relevado) | 0.85 | 0.80 |

### 20.3.3 Limites de Esfuerzo

**Tabla 20.3.3.1 - Esfuerzos Permisibles en Tendones**

| Etapa | Limite |
|-------|--------|
| Durante tensado | 0.80*fpu (general), 0.94*fpy |
| Inmediatamente despues de transferencia | 0.74*fpu |
| Anclajes post-tensados | 0.70*fpu |
| Servicio (despues de perdidas) | 0.80*fpy |

---

## 20.4 REQUISITOS DE DUCTILIDAD

### 20.4.1 Refuerzo Sismico

**Tabla 20.4.1.1 - Requisitos para ASTM A706**

| Propiedad | Requisito |
|-----------|-----------|
| Relacion fu/fy real | >= 1.25 |
| Relacion fy real / fy nominal | <= 1.25 |
| Elongacion en 8 in | >= 12% (Grado 60), >= 10% (Grado 80) |

### 20.4.2 Soldabilidad

**20.4.2.1** Barras ASTM A706: soldables sin precalentamiento especial

**20.4.2.2** Barras ASTM A615: requieren procedimiento segun AWS D1.4:
- Precalentamiento basado en carbono equivalente
- Electrodo compatible

---

## 20.5 RECUBRIMIENTO DE CONCRETO

### 20.5.1 Recubrimiento Minimo

**Tabla 20.5.1.1 - Concreto Colado en Sitio (No Expuesto)**

| Miembro | Recubrimiento (in) |
|---------|-------------------|
| Losas, muros, viguetas (No. 11 o menor) | 3/4 |
| Losas, muros, viguetas (No. 14, 18) | 1-1/2 |
| Vigas, columnas (refuerzo principal) | 1-1/2 |
| Vigas, columnas (estribos, amarres) | 1-1/2 |
| Cascarones, laminas plegadas | 3/4 |

**Tabla 20.5.1.2 - Concreto Expuesto a Suelo o Intemperie**

| Barra | Recubrimiento (in) |
|-------|-------------------|
| No. 5 o menor | 1-1/2 |
| No. 6 a No. 18 | 2 |

**Tabla 20.5.1.3 - Casos Especiales**

| Condicion | Recubrimiento (in) |
|-----------|-------------------|
| Colado contra suelo | 3 |
| Expuesto a cloruros (C2) | 2 (vigas/col), 1-1/2 (losas) |
| Prefabricados (no expuestos) | Ver 20.5.1.3.2 |

### 20.5.2 Recubrimiento para Postensado

**Tabla 20.5.2.1 - Recubrimiento de Ductos/Tendones**

| Condicion | Recubrimiento (in) |
|-----------|-------------------|
| Losas (interiores) | 3/4 |
| Losas (expuestas) | 1 |
| Vigas y columnas | 1-1/2 |
| Colado contra suelo | 2 |

### 20.5.3 Recubrimiento para Paquetes

Recubrimiento medido desde la superficie exterior del paquete.

---

## 20.6 PROTECCION CONTRA CORROSION

### 20.6.1 Tipos de Proteccion

**Tabla 20.6.1.1 - Metodos de Proteccion**

| Metodo | Norma | Aplicacion |
|--------|-------|------------|
| Recubrimiento epoxico | ASTM A775, A934 | Puentes, estacionamientos |
| Galvanizado | ASTM A767 | Exposicion moderada |
| Acero inoxidable | ASTM A955 | Alta corrosion |
| Doble recubrimiento | ASTM A1055 | Epoxico + galvanizado |

### 20.6.2 Requisitos por Clase de Exposicion

**Tabla 20.6.2.1 - Proteccion Requerida**

| Clase | Requisito |
|-------|-----------|
| C0 | Sin requisito especial |
| C1 | Recubrimiento adecuado |
| C2 | Epoxico, galvanizado, inoxidable, o recubrimiento aumentado |

### 20.6.3 Contenido de Cloruros

**Tabla 20.6.3.1 - Limites de Ion Cloruro (% por peso de cemite)**

| Condicion | No Pretensado | Pretensado |
|-----------|---------------|------------|
| C0 | 1.00 | 0.06 |
| C1 | 0.30 | 0.06 |
| C2 | 0.15 | 0.06 |

---

## 20.7 EMBEBIDOS Y CONEXIONES

### 20.7.1 Embebidos Metalicos

**20.7.1.1** Materiales permitidos:
- Acero estructural ASTM A36, A992
- Acero inoxidable ASTM A240, A276
- Fundicion gris ASTM A48

**20.7.1.2** Recubrimiento minimo: 2 in (expuesto), 1-1/2 in (no expuesto)

### 20.7.2 Ductos para Postensado

**Tabla 20.7.2.1 - Requisitos de Ductos**

| Tipo | Material | Espesor min |
|------|----------|-------------|
| Rigido | Acero galvanizado | 26 gage |
| Semi-rigido | Acero corrugado | 28 gage |
| Plastico | HDPE | Segun fabricante |

### 20.7.3 Anclajes de Postensado

- Cumplir PTI M50.3
- Desarrollar 95% de fpu del tendon
- Proteccion contra corrosion permanente

---

## 20.8 REQUISITOS ESPECIALES

### 20.8.1 Refuerzo de Bajo Carbono

Para soldadura sin precalentamiento:
- Carbono equivalente CE <= 0.45%
- O usar ASTM A706

### 20.8.2 Refuerzo de Alta Resistencia (Grado 100+)

**20.8.2.1** Limitaciones:
- No usar en cortante-friccion
- Verificar anclaje y desarrollo
- Considerar control de fisuras

**20.8.2.2** Aplicaciones sismicas:
- Muros especiales: permitido con f'c >= 5000 psi
- Marcos especiales: no permitido (usar Grado 60 u 80)

### 20.8.3 Empalmes Mecanicos

**Tabla 20.8.3.1 - Tipos de Empalmes Mecanicos**

| Tipo | Requisito |
|------|-----------|
| Tipo 1 | Desarrollar 1.25*fy |
| Tipo 2 | Desarrollar resistencia a tension de la barra |

---

## 20.9 IDENTIFICACION Y ALMACENAMIENTO

### 20.9.1 Marcas de Identificacion

Barras deben tener marcas que indiquen:
- Fabricante
- Tamano de barra
- Grado (linea continua o numero)
- Tipo de acero (S = sismico A706)

### 20.9.2 Almacenamiento

- Proteger de intemperie
- Almacenar elevado sobre el suelo
- Separar por tamano y grado
- Evitar contaminacion con aceite, grasa

---

## TABLAS DE BARRAS

### Tabla 20.9.1 - Propiedades de Barras

| No. | db (in) | Ab (in²) | Peso (lb/ft) |
|-----|---------|----------|--------------|
| 3 | 0.375 | 0.11 | 0.376 |
| 4 | 0.500 | 0.20 | 0.668 |
| 5 | 0.625 | 0.31 | 1.043 |
| 6 | 0.750 | 0.44 | 1.502 |
| 7 | 0.875 | 0.60 | 2.044 |
| 8 | 1.000 | 0.79 | 2.670 |
| 9 | 1.128 | 1.00 | 3.400 |
| 10 | 1.270 | 1.27 | 4.303 |
| 11 | 1.410 | 1.56 | 5.313 |
| 14 | 1.693 | 2.25 | 7.650 |
| 18 | 2.257 | 4.00 | 13.600 |

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Longitud de desarrollo | 25.4 |
| Empalmes | 25.5 |
| Recubrimiento para proteccion sismica | 18.12.7.6 |
| Durabilidad del concreto | 19.3 |
| Requisitos sismicos de refuerzo | 18.2.5-18.2.8 |
| Anclajes | Capitulo 17 |

---

*Resumen del ACI 318-25 Capitulo 20 para propiedades del acero de refuerzo.*
*Fecha: 2025*
