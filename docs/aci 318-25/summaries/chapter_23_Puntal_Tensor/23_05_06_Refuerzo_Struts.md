# ACI 318-25 - Secciones 23.5-23.6: REFUERZO DE STRUTS

---

## 23.5 REFUERZO DISTRIBUIDO MINIMO

### 23.5.1 Cuantias Minimas

**Tabla 23.5.1 - Refuerzo Distribuido Minimo:**

| Condicion | Direcciones | Cuantia Minima (rho) |
|-----------|-------------|----------------------|
| Strut no arriostrado | Malla ortogonal | **0.0025** en cada direccion |
| Strut no arriostrado | Una direccion a angulo alpha | **0.0025 / sin²(alpha)** |
| Strut arriostrado lateralmente | Cualquiera | **No requerido** |

**Notas:**
- **alpha** = Angulo entre refuerzo y eje del strut (>= 40°)
- El refuerzo controla agrietamiento diagonal
- Cuando alpha = 90°: sin²(90°) = 1.0, por tanto rho = 0.0025

### Angulo Minimo del Refuerzo (23.5.1)

```
alpha >= 40 grados (entre refuerzo y strut)
```

---

### 23.5.2 Espaciamiento del Refuerzo

| Parametro | Limite Maximo | Descripcion |
|-----------|---------------|-------------|
| sld, std | **12 in** (300 mm) | Espaciamiento en el plano |
| swd | **24 in** (600 mm) | Entre planos de refuerzo |

**Requisito de espesor (23.5.2.2):**

```
Si espesor perpendicular al plano >= 10 in:
  Se requieren 2 o mas planos de refuerzo
```

---

### 23.5.3 Struts Arriostrados Lateralmente

Un strut se considera **arriostrado lateralmente** si cumple TODAS:

| Condicion | Requisito |
|-----------|-----------|
| (a) | D-region es continua perpendicular al plano del modelo |
| (b) | Concreto se extiende >= **ws/2** a cada lado del strut |
| (c) | Strut esta en junta arriostrada segun **15.5.2.5** |

**Si el strut esta arriostrado:**
- Refuerzo distribuido **NO requerido**
- Pero puede ser beneficioso para control de agrietamiento

**Si el strut NO esta arriostrado:**
- Refuerzo distribuido **REQUERIDO** segun Tabla 23.5.1

---

## 23.6 DETALLES DE REFUERZO EN STRUTS

### 23.6.1 Refuerzo Longitudinal en Compresion

Cuando se usa refuerzo de compresion en struts:

- Barras **paralelas** al eje del strut
- Encerradas con **closed ties** (segun 25.7.2) O **espirales** (segun 25.7.3)

### 23.6.2 Tamano Minimo de Amarres

| Refuerzo Longitudinal | Amarre Minimo |
|-----------------------|---------------|
| No. 10 (db <= 32 mm) o menor | **No. 3** (db = 10 mm) |
| No. 11, 14, 18 | **No. 4** (db = 13 mm) |
| Paquetes de barras | **No. 4** (db = 13 mm) |

---

### 23.6.3 Espaciamiento de Closed Ties

**23.6.3.1 Espaciamiento maximo:**

```
s <= menor de:
  (a) Dimension menor del strut
  (b) 48 * db (diametro del tie)
  (c) 16 * db (diametro del refuerzo longitudinal)
```

**23.6.3.2 Primer closed tie:**

```
Distancia desde cara de nodal zone <= 0.5 * s
```

---

### 23.6.4 Configuracion de Amarres

| Requisito | Especificacion |
|-----------|----------------|
| Barras soportadas | Cada barra de esquina y alternadas |
| Angulo de esquina | <= **135°** |
| Separacion libre maxima | Ninguna barra > **6 in** (150 mm) sin soporte |

---

## RESUMEN GRAFICO

### Refuerzo Distribuido en Struts Interiores

```
        Strut
         /
        /  alpha >= 40°
       /____________________
      |    |    |    |    |   Refuerzo horizontal
      |    |    |    |    |   rho_h >= 0.0025
      |____|____|____|____|
           |    |    |
           |    |    |        Refuerzo vertical
           |    |    |        rho_v >= 0.0025
           |    |    |

  Espaciamiento s <= 12 in (en cada direccion)
```

### Detalle de Strut con Refuerzo de Compresion

```
  Closed ties @ s
       |
   ____v____
  |  o    o  |   o = Barras longitudinales
  |    __    |       (paralelas al strut)
  |   |  |   |
  |   |  |   |   Closed tie confina
  |   |__|   |   las barras
  |  o    o  |
  |__________|
       ^
       |
  Primer tie a <= 0.5*s de nodal zone
```

---

## EJEMPLO DE VERIFICACION

**Datos:**
- Strut interior, no arriostrado
- Espesor del miembro: 18 in
- fc' = 4000 psi
- Refuerzo: malla ortogonal

**Verificacion:**

1. **Cuantia requerida:**
   ```
   rho_min = 0.0025 (cada direccion, Tab. 23.5.1)
   ```

2. **Espaciamiento:**
   ```
   s <= 12 in (en plano)
   ```

3. **Planos de refuerzo:**
   ```
   Espesor = 18 in > 10 in
   Se requieren 2 planos de refuerzo
   Separacion entre planos swd <= 24 in  OK
   ```

4. **Area de refuerzo por pie:**
   ```
   As = rho * b * s = 0.0025 * 12 * 12 = 0.36 in²/ft
   Usar: #4 @ 12" c/c (As = 0.20 in²/ft x 2 planos = 0.40 in²/ft)  OK
   ```

---

*ACI 318-25 Secciones 23.5-23.6*
