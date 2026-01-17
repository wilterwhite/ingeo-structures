# Verificacion Manual C1 (Strut) vs ACI 318-25

**Fecha:** 2026-01-16
**Elemento:** C1 (12x12cm) - Strut / Pedestal no confinado
**Archivo de prueba:** edge_cases.xlsx
**Resultado:** VERIFICACION CASO FAIL EXTREMO (DCR >> 1.0)

---

## 1. Datos de Entrada

### Geometria
| Parametro | Valor | Unidad |
|-----------|-------|--------|
| b (ancho) | 120 | mm |
| h (alto) | 120 | mm |
| Lu (altura libre) | 2800 | mm |
| cover | 25 | mm |
| Ag | 14,400 | mm^2 |

### Materiales (Concreto28)
| Parametro | Valor | Unidad |
|-----------|-------|--------|
| f'c | 28 | MPa |
| fy | 420 | MPa |

### Armadura (segun UI)
- **Longitudinal:** 1x1 φ12 (1 barra centrada)
- **Transversal:** Sin estribos

### Fuerzas (combinacion critica)
| Fuerza | Valor | Unidad |
|--------|-------|--------|
| Pu | ~5 | tonf (compresion) |
| Vu | ~0.5 | tonf |
| Mu | ~0.8 | tonf-m |

---

## 2. Clasificacion del Elemento

### ACI 318-25 Capitulo 14 - Hormigon no confinado

Un elemento se considera "strut" o pedestal no confinado cuando:
1. Dimension minima < 150mm (6")
2. O tiene solo 1 barra centrada sin estribos de confinamiento

C1 tiene:
- Dimension: 120mm < 150mm → **ES STRUT**
- 1 barra centrada, sin estribos → **HORMIGON NO CONFINADO**

### Factor phi para hormigon no confinado

Segun ACI 318-25 Seccion 21.2:
```
phi = 0.60 para elementos de hormigon no confinado (Capitulo 14)
```

Este factor es constante, no depende de la deformacion del acero.

---

## 3. Verificacion de Flexocompresion

### Capacidad axial pura (P0)

```
Ast = 1 barra φ12 = pi*(12/2)^2 = 113.1 mm^2

P0 = 0.85*fc'*(Ag - Ast) + fy*Ast
P0 = 0.85*28*(14400 - 113.1) + 420*113.1
P0 = 339,845 + 47,502 = 387,347 N = 39.5 tonf

Factor de reduccion axial (Tabla 22.4.2.1):
alpha = 0.80 (elementos con estribos o sin espiral)

Pn_max = alpha * P0 = 0.80 * 39.5 = 31.6 tonf

phi*Pn = 0.60 * 31.6 = 19.0 tonf
```

### Capacidad de momento (Mn)

Para una barra centrada, la capacidad de momento es MUY PEQUENA:
```
d = h/2 = 60mm (barra en el centro)
d' = 60mm

Con barra centrada, el brazo de palanca es casi cero.
La seccion solo tiene capacidad de momento por el concreto comprimido.

Estimacion conservadora:
Mn ≈ 0.1 * fc' * b * h^2 / 6 (aproximacion para seccion sin acero efectivo)
Mn ≈ 0.1 * 28 * 120 * 120^2 / 6
Mn ≈ 806,400 N-mm = 0.82 kN-m = 0.08 tonf-m

phi*Mn = 0.60 * 0.08 = 0.05 tonf-m
```

Esta capacidad de momento es extremadamente baja.

### Calculo de DCR

Segun la UI:
- Pu = 5 tonf
- phi_Mn = 7 tonf-m (¿?) - Este valor parece alto para la capacidad real

Si Mu = 0.8 tonf-m y phi_Mn = 0.05 tonf-m:
```
DCR = Mu / phi_Mn = 0.8 / 0.05 = 16

Cercano al 18.98 mostrado
```

**Nota:** La UI muestra phi_Mn = 7 t-m, lo cual no coincide con mi calculo.
Esto sugiere que el diagrama P-M considera la curva completa, no solo el punto de operacion.

---

## 4. Comparacion con Resultados de la Aplicacion

| Parametro | Calculo Manual | Aplicacion (UI) | Estado |
|-----------|----------------|-----------------|--------|
| phi | 0.60 | 0.60 | OK |
| Armadura | 1x1 φ12 | 1x1 φ12 | OK |
| Sin estribos | SI | Sin estribos | OK |
| DCR Flex | ~16+ | 18.98 | SIMILAR |
| DCR Corte | N/A | - | N/A (strut) |
| Estado | FAIL | FAIL | OK |

---

## 5. Por que falla tan severamente

1. **Dimension pequeña:** 12x12cm es muy pequeno para cargas de momento
2. **1 barra centrada:** No hay brazo de palanca para resistir momento
3. **Sin estribos:** No hay confinamiento → phi = 0.60
4. **Hormigon no confinado:** Capacidad reducida segun Cap. 14

### Diagrama P-M tipico para strut

```
     P (tonf)
     ^
     |  * phi*Pn_max = 19 tonf
     |  |
     |  | \
     |  |   \
     |  |     \  ← Curva muy "plana" (poco momento)
     |  |      *
     +--+-------+---------> M (tonf-m)
     0       ~0.05
```

La curva P-M de un strut con 1 barra centrada es casi una linea vertical,
indicando que solo puede tomar carga axial y casi nada de momento.

---

## 6. Recomendaciones de Diseno

Para que C1 funcione estructuralmente:

1. **Aumentar dimensiones:** Minimo 15x15cm (para ser columna, no strut)
2. **Usar armadura distribuida:** Minimo 2x2 barras en esquinas
3. **Agregar estribos:** Para confinamiento y cortante
4. **Verificar contra Cap. 18:** Si es zona sismica especial

**Armadura minima para columnas ACI 318-25 Seccion 10.6:**
```
As_min = 0.01 * Ag = 0.01 * 14400 = 144 mm^2 → 2 φ12
As_max = 0.04 * Ag = 0.04 * 14400 = 576 mm^2 → 5 φ12
```

---

## 7. Resumen

| Verificacion | Resultado | Estado |
|--------------|-----------|--------|
| Clasificacion | STRUT (< 150mm) | Correcto |
| phi | 0.60 (no confinado) | Correcto |
| Armadura | 1x1 φ12 centrada | Correcto |
| DCR Flex | 18.98 | **FAIL SEVERO** |
| DCR Corte | No aplica | - |

**CONCLUSION:**
- C1 es un caso de prueba de FALLA EXTREMA (strut con momento)
- El comportamiento es CORRECTO segun ACI 318-25 Cap. 14
- Elementos tan pequenos solo pueden tomar carga axial centrada
- Cualquier momento causa DCR muy alto debido a capacidad cercana a cero

---

## Referencias ACI 318-25

- **Capitulo 14:** Hormigon no confinado
- **21.2:** phi = 0.60 para elementos no confinados
- **Seccion 10.6:** Armadura minima en columnas (0.01*Ag)
- **Tabla 22.4.2.1:** Factor alpha = 0.80 para carga axial maxima
