# ACI 318-25 - 10.7 DETALLADO DE REFUERZO

---

## 10.7.1 General

| Requisito | Referencia |
|-----------|------------|
| Recubrimiento | 20.5.1 |
| Desarrollo de barras | 25.4 |
| Barras en paquete | 25.6 |

### 10.7.1.3 Barras con fy >= 80,000 psi
A lo largo de longitudes de desarrollo y empalme, proporcionar refuerzo transversal tal que:
```
Ktr >= 0.5 * db
```

---

## 10.7.2 Espaciamiento
Espaciamiento minimo segun **25.2**.

---

## 10.7.3 Numero Minimo de Barras

| Tipo de Confinamiento | Barras Minimas |
|-----------------------|----------------|
| Estribos triangulares | 3 |
| Estribos rectangulares o circulares | 4 |
| Espirales o zunchos circulares (marcos especiales) | 6 |

> **NOTA**: Con menos de 8 barras en arreglo circular, la orientacion afecta significativamente la resistencia a momento.

---

## 10.7.4 Barras Longitudinales con Codo

### 10.7.4.1 Pendiente Maxima
Pendiente del codo respecto al eje longitudinal: **no exceder 1 en 6**.
Porciones arriba y abajo del codo deben ser paralelas al eje.

### 10.7.4.2 Desfase >= 3 in
Si la cara de la columna tiene desfase >= 3 in:
- No usar barras dobladas
- Usar dowels separados empalmados con barras adyacentes

---

## 10.7.5 EMPALMES DE REFUERZO LONGITUDINAL

### 10.7.5.1 General
**Tipos permitidos:**
- Empalmes por traslape
- Empalmes mecanicos
- Empalmes soldados a tope
- Empalmes de apoyo directo

### 10.7.5.2 Empalmes por Traslape

#### 10.7.5.2.1 Barras en Compresion
Se permiten empalmes por traslape a compresion.

**Reduccion de longitud permitida:**

| Tipo | Factor | Condicion |
|------|--------|-----------|
| Con estribos | 0.83 | Area efectiva >= 0.0015*h*s en ambas direcciones |
| Con espirales | 0.75 | Espirales cumplen 25.7.3 |

**Longitud minima de empalme: 12 in**

#### 10.7.5.2.2 Barras en Tension
Empalmes segun Tabla 10.7.5.2.2:

| Tension en Barra | Detalles | Clase |
|------------------|----------|-------|
| <= 0.5*fy | <= 50% barras empalmadas, escalonados >= ld | Clase A |
| <= 0.5*fy | Otros casos | Clase B |
| > 0.5*fy | Todos los casos | Clase B |

### 10.7.5.3 Empalmes de Apoyo Directo

#### 10.7.5.3.1 Condiciones
- Barras en compresion
- Empalmes escalonados o barras adicionales en ubicaciones de empalme
- Barras continuas con resistencia a traccion >= 0.25*fy*As de cada cara

---

## 10.7.6 REFUERZO TRANSVERSAL

### 10.7.6.1 General

| Tipo | Referencia |
|------|------------|
| Estribos | 25.7.2 |
| Espirales | 25.7.3 |
| Zunchos | 25.7.4 |

### Espaciamiento Maximo de Estribos (25.7.2.1)

```
s <= menor de:
  (a) 16*db (longitudinal)
  (b) 48*db (transversal)
  (c) Dimension menor de columna
```

### Refuerzo de Espiral Minimo (25.7.3.3)

```
ρs >= 0.45 * (Ag/Ach - 1) * (fc'/fyt)
```

Y no menos que:
```
ρs >= 0.12 * fc'/fyt
```

Donde:
- **ρs** = volumen de espiral / volumen del nucleo
- **Ach** = area del nucleo (centro a centro de espiral)

### Paso de Espiral (25.7.3.2)

```
1 in. <= s <= 3 in.
```

#### 10.7.6.1.5 Pernos de Anclaje en Parte Superior
Encerrar pernos con refuerzo transversal que rodee al menos 4 barras longitudinales:
- Distribuir dentro de **5 in** de la parte superior
- Minimo: **2 No. 4** o **3 No. 3** estribos

#### 10.7.6.1.6 Acopladores Mecanicos en Extremos
Encerrar con refuerzo transversal:
- Distribuir dentro de **5 in** de los extremos
- Minimo: **2 No. 4** o **3 No. 3** estribos

### 10.7.6.2 Soporte Lateral con Estribos

#### 10.7.6.2.1 Ubicacion Inferior
Primer estribo: no mas de **s/2** sobre la parte superior de zapata o losa.

#### 10.7.6.2.2 Ubicacion Superior

| Condicion | Ubicacion del Ultimo Estribo |
|-----------|------------------------------|
| Sin vigas en todas las caras | <= s/2 bajo refuerzo de losa |
| Vigas en todas las caras | <= 3 in bajo refuerzo de viga mas baja |

### 10.7.6.5 Cortante

#### Tabla 10.7.6.5.2 - Espaciamiento Maximo de Refuerzo de Cortante

| Condicion | Columna No Pretensada | Columna Pretensada |
|-----------|----------------------|-------------------|
| Vs <= 4*sqrt(f'c)*bw*d | Menor de: d/2, 24 in | Menor de: 3h/4, 24 in |
| Vs > 4*sqrt(f'c)*bw*d | Menor de: d/4, 12 in | Menor de: 3h/8, 12 in |

---

*ACI 318-25 Seccion 10.7*
