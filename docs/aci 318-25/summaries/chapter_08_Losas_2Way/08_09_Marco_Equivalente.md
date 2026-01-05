# ACI 318-25 - 8.9 METODO DEL MARCO EQUIVALENTE

---

## 8.9.1 Alcance

El metodo del marco equivalente puede usarse para:
- Cualquier sistema de losas en dos direcciones
- Cargas laterales y de gravedad

---

## 8.9.2 Modelado del Marco

### 8.9.2.1 Marco en Cada Direccion
El marco equivalente consiste en:
- Franjas horizontales de losa limitadas lateralmente por lineas centrales de paneles adyacentes
- Columnas o muros que soportan la losa

### 8.9.2.2 Ancho de Marco

| Direccion | Ancho |
|-----------|-------|
| Analisis | l2 = ancho perpendicular a direccion del analisis |

---

## 8.9.3 Propiedades de la Losa-Viga

### 8.9.3.1 Momento de Inercia
Calcular usando seccion bruta de concreto.

### 8.9.3.2 Rigidez en Apoyos
La rigidez varia desde la cara del apoyo hasta el centro:
- Considerar columna de ancho finito
- O usar factor de rigidez modificado

### 8.9.3.3 Con Vigas
Si hay vigas entre apoyos:
- Incluir porcion de losa que actua como ala
- Ancho de ala efectivo segun 6.3.2

### 8.9.3.4 Inercia para Deflexiones
Usar Ie segun 24.2 para calculo de deflexiones.

---

## 8.9.4 Propiedades de Columna

### 8.9.4.1 Rigidez de Columna
Calcular Kc considerando:
- Seccion bruta de concreto
- Longitud de columna arriba y abajo de la losa

### 8.9.4.2 Columna Equivalente
La columna equivalente combina:
- Rigidez de columnas reales (Kc)
- Rigidez torsional del elemento transversal (Kt)

```
1/Kec = 1/ΣKc + 1/Kt
```

### 8.9.4.3 Rigidez Torsional

```
Kt = Σ(9*Ecs*C) / [l2*(1 - c2/l2)³]
```

Donde **C** es la constante de seccion torsional:
```
C = Σ[(1 - 0.63*x/y)*(x³*y/3)]
```

Con x = dimension corta, y = dimension larga de cada rectangulo.

---

## 8.9.5 Distribucion de Momentos

### 8.9.5.1 Factores de Distribucion
Usar analisis elastico o factores de momento modificados.

### 8.9.5.2 Redistribucion
Se permite hasta **10%** de redistribucion si εt >= 0.0075.

### 8.9.5.3 Distribucion a Bandas
Distribuir momentos en la seccion transversal segun **8.8.4**.

---

## 8.9.6 Cargas de Patron

### 8.9.6.1 Cuando Aplicar
Si L/D > 0.5:
- Carga total factorada en todos los claros + (3/4)*L factorada en claros alternos

### 8.9.6.2 Simplificacion
Si L/D <= 0.5:
- Permitido usar carga total en todos los claros

---

## Resumen de Formulas

| Parametro | Formula |
|-----------|---------|
| Columna equivalente | 1/Kec = 1/ΣKc + 1/Kt |
| Rigidez torsional | Kt = Σ(9*Ecs*C) / [l2*(1 - c2/l2)³] |
| Constante C | C = Σ[(1 - 0.63*x/y)*(x³*y/3)] |

---

*ACI 318-25 Seccion 8.9*
