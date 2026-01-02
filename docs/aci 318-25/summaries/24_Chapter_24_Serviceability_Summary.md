# ACI 318-25 - CAPITULO 24: SERVICIABILIDAD
## Deflexiones, Agrietamiento y Requisitos de Servicio

---

## INDICE

- [24.1 Alcance](#241-alcance)
- [24.2 Deflexiones](#242-deflexiones)
- [24.3 Control de Fisuras](#243-control-de-fisuras)
- [24.4 Refuerzo por Contraccion y Temperatura](#244-refuerzo-por-contraccion-y-temperatura)
- [24.5 Fatiga](#245-fatiga)
- [24.6 Pretensado - Serviciabilidad](#246-pretensado---serviciabilidad)
- [24.7 Vibracion](#247-vibracion)
- [Formulas de Referencia Rapida](#formulas-de-referencia-rapida)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 24.1 ALCANCE

### 24.1.1 Aplicabilidad
Este capitulo aplica a requisitos de serviciabilidad para:
- (a) Deflexiones
- (b) Distribucion de refuerzo para control de fisuras
- (c) Refuerzo por contraccion y temperatura
- (d) Fatiga (cuando aplique)

---

## 24.2 DEFLEXIONES

### 24.2.1 General

**24.2.1.1** Verificar que deflexiones no excedan limites funcionales o estructurales

**24.2.1.2** Metodos de calculo:
- Analisis elastico con Ie efectivo
- Analisis no lineal (cuando se justifique)

### 24.2.2 Espesores Minimos (Sin Calculo de Deflexiones)

**Tabla 24.2.2 - Espesor Minimo de Vigas y Losas en Una Direccion**

| Condicion de Apoyo | Losa Maciza | Viga o Losa Nervada |
|--------------------|-------------|---------------------|
| Simplemente apoyada | l/20 | l/16 |
| Un extremo continuo | l/24 | l/18.5 |
| Ambos extremos continuos | l/28 | l/21 |
| Cantilever | l/10 | l/8 |

*Para fy distinto de 60,000 psi: multiplicar por (0.4 + fy/100,000)*
*Para concreto liviano: multiplicar por (1.65 - 0.005*wc) >= 1.09*

**Tabla 24.2.2.1 - Espesor Minimo de Losas en Dos Direcciones**

| Sistema | Espesor Minimo |
|---------|----------------|
| Sin vigas interiores | Mayor de: ln/33, 5 in |
| Con vigas (alpha_fm >= 0.2) | Mayor de: ln/36, 5 in |
| Con vigas (alpha_fm >= 2.0) | Mayor de: ln/36*(0.8 + fy/200,000), 3.5 in |
| Con drop panels | 90% de los valores anteriores |

### 24.2.3 Momento de Inercia Efectivo (Ie)

**Ecuacion de Branson:**
```
Ie = (Mcr/Ma)³ * Ig + [1 - (Mcr/Ma)³] * Icr <= Ig     [Ec. 24.2.3.5a]
```

**Ecuacion alternativa (Bischoff):**
```
Ie = Icr / [1 - (Mcr/Ma)² * (1 - Icr/Ig)]     [Ec. 24.2.3.5b]
```

Donde:
```
Mcr = fr * Ig / yt     (momento de agrietamiento)
fr = 7.5 * lambda * sqrt(f'c)
```

### 24.2.4 Calculo de Deflexiones

**24.2.4.1** Deflexion inmediata:
- Usar Ie en analisis elastico
- Para cargas uniformes: delta = 5*w*l⁴ / (384*Ec*Ie)

**24.2.4.2** Deflexion a largo plazo:
```
delta_LT = delta_i * lambda_delta
lambda_delta = xi / (1 + 50*rho')     [Ec. 24.2.4.1.1]
```

**Tabla 24.2.4.1 - Factor xi por Duracion de Carga**

| Duracion | xi |
|----------|-----|
| 5 anos o mas | 2.0 |
| 12 meses | 1.4 |
| 6 meses | 1.2 |
| 3 meses | 1.0 |

**24.2.4.3** Deflexion total:
```
delta_total = delta_i(D) * (1 + lambda_delta) + delta_i(L)
```

### 24.2.5 Limites de Deflexion

**Tabla 24.2.5.1 - Deflexiones Permisibles**

| Tipo de Miembro | Condicion | Limite |
|-----------------|-----------|--------|
| Techos planos | Sin danar elementos no estructurales | l/180 |
| Pisos | Sin danar elementos no estructurales | l/360 |
| Techos/pisos | Que soportan elementos fragiles | l/480 |
| Techos/pisos | Que soportan elementos no fragiles | l/240 |

---

## 24.3 CONTROL DE FISURAS

### 24.3.1 General

**24.3.1.1** El refuerzo debe distribuirse para controlar ancho de fisuras bajo cargas de servicio

### 24.3.2 Distribucion de Refuerzo en Vigas y Losas

**24.3.2.1** Espaciamiento maximo del refuerzo de flexion:
```
s <= 15 * (40,000 / fs) - 2.5*cc     [Ec. 24.3.2]
s <= 12 * (40,000 / fs)
```

Donde:
- fs = 2/3 * fy (se permite usar)
- cc = recubrimiento libre desde cara de tension

**Tabla 24.3.2.1 - Espaciamiento Maximo por fs**

| fs (psi) | s max con cc = 2 in |
|----------|---------------------|
| 24,000 | 22 in |
| 40,000 | 10 in |
| 60,000 | 5 in |

### 24.3.3 Distribucion en Vigas T

**24.3.3.1** Parte del refuerzo de flexion debe distribuirse en el ala efectivo

**24.3.3.2** Ancho efectivo de ala para distribucion:
```
beff = bw + menor de: ln/10, 6*hf (a cada lado)
```

### 24.3.4 Refuerzo en Caras Laterales de Vigas Altas

**24.3.4.1** Para vigas con h > 36 in:
- Proveer refuerzo en caras laterales
- Ask = 0.012 * (d - 30) por cara
- Espaciamiento <= menor de: d/6, 12 in

---

## 24.4 REFUERZO POR CONTRACCION Y TEMPERATURA

### 24.4.1 General

**24.4.1.1** Proveer refuerzo perpendicular al refuerzo de flexion para:
- Controlar fisuras por contraccion
- Controlar fisuras por temperatura

### 24.4.2 Cuantia Minima

**Tabla 24.4.2.1 - Cuantia Minima de Refuerzo T&S**

| Tipo de Refuerzo | Cuantia (rho) |
|------------------|---------------|
| Barras corrugadas Grado 40 o 50 | 0.0020 |
| Barras corrugadas Grado 60 | 0.0018 |
| Barras corrugadas Grado 80 | 0.0014 |
| Malla soldada (fy >= 60,000 psi) | 0.0018 |

**Para barras con fy > 80,000 psi:**
```
rho = 0.0014 * (80,000 / fy) >= 0.0010
```

### 24.4.3 Espaciamiento Maximo

```
s <= menor de: 5*h, 18 in
```

### 24.4.4 Metodo Alternativo (Analisis)

**24.4.4.1** Se permite reducir refuerzo T&S si se demuestra mediante analisis que:
- Fisuras estan controladas
- Considerar restricciones
- Considerar gradientes de temperatura

---

## 24.5 FATIGA

### 24.5.1 Alcance

**24.5.1.1** Aplica a estructuras sujetas a cargas ciclicas significativas:
- Puentes grua
- Estructuras sometidas a vibraciones
- Otros casos con > 500,000 ciclos

### 24.5.2 Limites de Esfuerzo

**24.5.2.1** Rango de esfuerzo en refuerzo:
```
ff <= 24 - 0.33*fmin     (para barras rectas)
ff <= 16 - 0.33*fmin     (para barras dobladas)
```

Donde:
- ff = rango de esfuerzo (ksi)
- fmin = esfuerzo minimo (ksi), positivo si tension

**24.5.2.2** Esfuerzo maximo en concreto:
```
fc,max <= 0.40*f'c     (compresion)
```

---

## 24.6 PRETENSADO - SERVICIABILIDAD

### 24.6.1 Esfuerzos Permisibles en Concreto

**Tabla 24.6.1.1 - Inmediatamente Despues de Transferencia**

| Ubicacion | Limite |
|-----------|--------|
| Compresion | 0.60*f'ci |
| Tension (extremos de elementos simplemente apoyados) | 6*sqrt(f'ci) |
| Tension (otros) | 3*sqrt(f'ci) |

**Tabla 24.6.1.2 - En Servicio (Despues de Perdidas)**

| Carga | Ubicacion | Limite |
|-------|-----------|--------|
| Sostenida | Compresion | 0.45*f'c |
| Total | Compresion | 0.60*f'c |
| Total | Tension (Clase U) | 0 |
| Total | Tension (Clase T) | 7.5*sqrt(f'c) |
| Total | Tension (Clase C) | 12*sqrt(f'c) |

### 24.6.2 Clases de Miembros Pretensados

**Tabla 24.6.2.1 - Clasificacion de Miembros**

| Clase | Esfuerzo de Tension en Servicio | Requisitos |
|-------|--------------------------------|------------|
| U (Uncracked) | ft <= 7.5*sqrt(f'c) | No fisurado |
| T (Transition) | 7.5*sqrt(f'c) < ft <= 12*sqrt(f'c) | Verificar ancho fisura |
| C (Cracked) | ft > 12*sqrt(f'c) | Comportamiento como reforzado |

### 24.6.3 Deflexiones en Pretensado

**24.6.3.1** Para Clase U: usar Ig

**24.6.3.2** Para Clase T y C: usar Ie efectivo

**24.6.3.3** Considerar contraflecha inicial y cambios a largo plazo

---

## 24.7 VIBRACION

### 24.7.1 General

**24.7.1.1** Verificar que vibraciones no excedan limites de confort o funcionalidad

### 24.7.2 Criterios

**Tabla 24.7.2.1 - Limites de Aceleracion (Tipicos)**

| Uso | Limite |
|-----|--------|
| Residencial | 0.5% g |
| Oficinas | 1.0% g |
| Centros comerciales | 1.5% g |

*Referencia: AISC Design Guide 11*

### 24.7.3 Frecuencia Natural

```
fn = (pi/2) * sqrt(g*E*I / (w*L⁴))
```

**Objetivo:** fn > frecuencia de la actividad humana (tipico 3-8 Hz)

---

## FORMULAS DE REFERENCIA RAPIDA

### Momento de Agrietamiento
```
Mcr = fr * Ig / yt = 7.5*lambda*sqrt(f'c) * Ig / yt
```

### Momento de Inercia Fisurada (Seccion Rectangular)
```
Icr = (b*c³)/3 + n*As*(d-c)²
```
Donde c se obtiene de: b*c²/2 = n*As*(d-c)

### Deflexion Largo Plazo
```
delta_total = delta_D*(1 + lambda_delta) + delta_L
lambda_delta = 2.0 / (1 + 50*rho')     (para 5+ anos)
```

### Espaciamiento Maximo (Control de Fisuras)
```
s = 15*(40,000/fs) - 2.5*cc <= 12*(40,000/fs)
```

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Espesor minimo losas una direccion | 7.3.1 |
| Espesor minimo losas dos direcciones | 8.3.1 |
| Espesor minimo vigas | 9.3.1 |
| Propiedades del concreto (fr, Ec) | 19.2 |
| Recubrimiento | 20.5 |
| Combinaciones de carga de servicio | 5.3 |

---

*Resumen del ACI 318-25 Capitulo 24 para serviciabilidad.*
*Fecha: 2025*
