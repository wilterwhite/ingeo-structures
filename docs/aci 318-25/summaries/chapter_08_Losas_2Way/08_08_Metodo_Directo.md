# ACI 318-25 - 8.8 METODO DIRECTO DE DISENO

---

## 8.8.1 Limitaciones

### 8.8.1.1 Condiciones para Usar el Metodo Directo

| Condicion | Requisito |
|-----------|-----------|
| (a) Numero minimo de claros | **3** en cada direccion |
| (b) Paneles rectangulares | β = ln_largo/ln_corto <= **2** |
| (c) Variacion de claros | Claros adyacentes <= **1/3** de diferencia |
| (d) Desplazamiento de columnas | <= **10%** del claro en direccion del desplazamiento |
| (e) Cargas | Solo cargas de gravedad, uniformemente distribuidas |
| (f) Relacion de cargas | L/D <= **2** (para carga viva no factorada) |
| (g) Para losas con vigas | 0.2 <= αf1*l2²/(αf2*l1²) <= 5.0 |

---

## 8.8.2 Momento Estatico Total

### 8.8.2.1 Formula
```
Mo = qu*l2*ln² / 8
```

Donde:
- **qu** = carga factorada por unidad de area
- **l2** = ancho del panel perpendicular a la direccion del analisis
- **ln** = luz libre en direccion del analisis

### 8.8.2.2 Luz Libre (ln)
```
ln = l1 - c1 (entre caras de apoyos)
```

**Nota:** ln no debe ser menor que **0.65*l1**.

### 8.8.2.3 Para Claros Irregulares
Si claros adyacentes son diferentes, Mo puede promediarse en el apoyo comun.

---

## 8.8.3 Distribucion de Momento Estatico Total

### 8.8.3.1 Panel Interior

| Momento | Porcentaje de Mo |
|---------|------------------|
| Negativo en apoyo | **65%** |
| Positivo en el claro | **35%** |

### 8.8.3.2 Panel de Borde

| Ubicacion | Apoyo Exterior | Claro | Apoyo Interior |
|-----------|----------------|-------|----------------|
| Con viga de borde | 16% | 57% | 70% |
| Sin viga de borde | 26% | 52% | 70% |
| Borde empotrado | 65% | 35% | 65% |

**Tabla Detallada - Panel de Borde:**

| Condicion de Borde | M- exterior | M+ | M- interior |
|--------------------|-------------|-----|-------------|
| Losa con viga de borde (αf*l2/l1 >= 1) | 0.16 | 0.57 | 0.70 |
| Losa sin viga de borde | 0.26 | 0.52 | 0.70 |
| Losa con borde empotrado | 0.65 | 0.35 | 0.65 |
| Exterior sin restriccion | 0 | 0.63 | 0.75 |

---

## 8.8.4 Distribucion de Momentos en Bandas

### 8.8.4.1 Banda de Columna - Momento Negativo

| αf1*l2/l1 | bt/bs = 0 | bt/bs >= 2.5 |
|-----------|-----------|--------------|
| 0 | 100% | 75% |
| >= 1.0 | 90% | 45% |

Interpolar para valores intermedios.

**Donde:**
- bt = ancho de viga de borde
- bs = ancho de banda de columna

### 8.8.4.2 Banda de Columna - Momento Positivo

| αf1*l2/l1 | % en banda de columna |
|-----------|-----------------------|
| 0 | 60% |
| >= 1.0 | 90% |

### 8.8.4.3 Banda Central
Recibe el resto del momento no asignado a la banda de columna.

### 8.8.4.4 Vigas entre Apoyos
Si αf1*l2/l1 >= 1.0, las vigas en la banda de columna deben resistir **85%** del momento de la banda de columna.

---

## 8.8.5 Ajustes de Momento

### 8.8.5.1 Redistribucion
Se permite redistribuir momentos hasta **10%** si se cumple:
- εt >= 0.0075 en la seccion de maximo momento

### 8.8.5.2 Momento Minimo
El momento de diseno en cualquier seccion no debe ser menor que el momento calculado considerando cargas no uniformes.

---

## Resumen de Distribucion de Mo

| Ubicacion | Panel Interior | Panel Borde (sin viga) |
|-----------|----------------|------------------------|
| M- apoyo exterior | - | 26% |
| M+ claro | 35% | 52% |
| M- apoyo interior | 65% | 70% |

---

*ACI 318-25 Seccion 8.8*
