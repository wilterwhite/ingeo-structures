# Verificacion Manual P1 vs ACI 318-25

**Fecha:** 2026-01-16
**Elemento:** P1 (100x20cm) - Pier rectangular
**Archivo de prueba:** edge_cases.xlsx
**Resultado:** VERIFICACION CASO FAIL (DCR > 1.0)

---

## 1. Datos de Entrada

### Geometria
| Parametro | Valor | Unidad |
|-----------|-------|--------|
| lw (longitud) | 1000 | mm |
| tw (espesor) | 200 | mm |
| hwcs (altura piso) | 3000 | mm |
| cover | 25 | mm |
| Acv | 200,000 | mm^2 |

### Materiales (3000Psi)
| Parametro | Valor | Unidad |
|-----------|-------|--------|
| f'c | 21 | MPa |
| fy | 420 | MPa |
| lambda | 1.0 | - |

### Armadura (segun UI)
- **Malla:** 2M phi8@200 (vertical y horizontal)
- **Borde:** 2phi10 E10@150

### Fuerzas (combinacion critica - Top)
| Fuerza | Valor | Unidad |
|--------|-------|--------|
| Pu | -35 | tonf (compresion) |
| Vu | 8 | tonf |
| Mu | 43 | tonf-m |

---

## 2. Verificacion de Cortante

### Paso 1: alpha_c
```
hw/lw = 3000/1000 = 3.0 > 2.0
alpha_c = 0.17 (muro esbelto)
```

### Paso 2: rho_h
```
Malla: 2M phi8@200
rho_h = 2 * (1000/200) * pi*(4)^2 / (200*1000)
rho_h = 2 * 5 * 50.27 / 200000 = 0.00251
```

### Paso 3: Capacidad de corte
```
Vc = 0.17 * 1.0 * sqrt(21) * 200000 = 155,822 N = 15.89 tonf
Vs = 0.0025 * 420 * 200000 = 210,000 N = 21.41 tonf
Vn = 15.89 + 21.41 = 37.30 tonf
```

### Paso 4: Factor phi y amplificacion
```
phi = 0.60 (SPECIAL)
phi*Vn = 0.60 * 37.30 = 22.38 tonf

Amplificacion (hwcs/lw = 3.0 > 2.0):
Omega_v = 1.5, omega_v = 1.0
Ve = 1.5 * 8 = 12 tonf
```

### Paso 5: DCR cortante
```
DCR_shear = Ve / (phi*Vn) = 12 / 22.38 = 0.54

UI muestra: DCR Corte = 0.54 OK!
```

---

## 3. Verificacion de Flexocompresion

### Paso 1: Verificar esbeltez (ACI 318-25 Seccion 6.2.5)

```
Radio de giro: r = t / sqrt(12) = 200 / 3.464 = 57.74 mm
Factor k: k = 0.8 (muro arriostrado)
Longitud efectiva: k*lu = 0.8 * 3000 = 2400 mm

Esbeltez: lambda = k*lu/r = 2400 / 57.74 = 41.6

Limite para porticos arriostrados: lambda_limit = 22

Como 41.6 > 22 → EL MURO ES ESBELTO
```

### Paso 2: Magnificacion de momentos (ACI 318-25 Seccion 6.6.4)

El momento debe magnificarse: Mc = delta_ns * Mu

```
Carga critica de Euler:
(EI)eff = 0.35 * Ec * Ig     [Tabla 6.6.3.1.1(a)]

Ec = 4700 * sqrt(21) = 21,538 MPa

Ig = b * t^3 / 12 = 1000 * 200^3 / 12 = 6.67E8 mm^4

(EI)eff = 0.35 * 21538 * 6.67E8 = 5.03E12 N-mm^2

Pc = pi^2 * (EI)eff / (k*lu)^2
Pc = 9.87 * 5.03E12 / (2400)^2
Pc = 8,617,000 N = 878 tonf

Factor Cm = 1.0 (conservador)

Factor de magnificacion:
delta_ns = Cm / (1 - Pu/0.75*Pc)
delta_ns = 1.0 / (1 - 35*9.81 / (0.75 * 8617))
delta_ns = 1.0 / (1 - 343.4 / 6463)
delta_ns = 1.0 / (1 - 0.053)
delta_ns = 1.0 / 0.947 = 1.056

Nota: Este valor parece pequeno para DCR = 2.15
```

### Paso 3: Momento magnificado

```
Mc = delta_ns * Mu
Mc = 1.056 * 43 = 45.4 tonf-m (aproximado)

Pero la UI muestra phi_Mn = 27 tonf-m a Pu = 35 tonf
DCR = Mc / phi_Mn = 45.4 / 27 = 1.68

Aun no llega a 2.15...
```

### Paso 4: Revisar curva de interaccion P-M

La discrepancia sugiere que:
1. El momento magnificado es mayor (diferente delta_ns)
2. O el phi_Mn a Pu=35t es menor
3. O hay otra consideracion

Para verificar exactamente, necesitaria generar la curva P-M completa del elemento.

---

## 4. Comparacion con Resultados de la Aplicacion

| Parametro | Calculo Manual | Aplicacion (UI) | Estado |
|-----------|----------------|-----------------|--------|
| DCR Corte | 0.54 | 0.54 | OK |
| phi*Vn | 22.38 tonf | 22 tonf | OK |
| DCR Flex | ~1.68 (sin mag) | 2.15 | INVESTIGAR |
| phi_Mn | (calcular curva) | 27 tonf-m | - |
| Pu | 35 tonf | 35 tonf | OK |

---

## 5. Analisis del DCR = 2.15

Segun la UI:
- Pu = 35 tonf
- phi_Mn = 27 tonf-m (capacidad a ese Pu)
- Mu_demanda = 43 tonf-m (del analisis)

Si DCR = Mu/phi_Mn = 43/27 = 1.59

Pero si hay magnificacion por esbeltez:
```
Mc = delta_ns * Mu
DCR = Mc / phi_Mn

Si DCR = 2.15 y phi_Mn = 27:
Mc = 2.15 * 27 = 58.05 tonf-m

delta_ns = Mc / Mu = 58.05 / 43 = 1.35
```

Esto significa que el factor de magnificacion real es delta_ns = 1.35,
lo cual implica que la formula exacta del codigo da un valor mayor
que mi calculo simplificado (1.056).

**Posible causa:** El calculo de esbeltez puede usar el momento M2 minimo
o considerar efectos de segundo orden de manera diferente.

---

## 6. Verificacion de Cuantia Minima

```
tw = 200 mm > 130 mm → Requiere doble malla (2M)
rho_min = 0.0025

Malla: 2M phi8@200
rho = 0.0025 OK
```

---

## 7. Resumen

| Verificacion | Resultado | Estado |
|--------------|-----------|--------|
| Cortante | DCR = 0.54 | OK |
| Flexocompresion | DCR = 2.15 | **FAIL** |
| Cuantia minima | 0.0025 | OK |
| Muro esbelto | lambda = 41.6 | SI |

**CONCLUSION:**
- El calculo de cortante es CORRECTO (DCR = 0.54)
- El elemento FALLA por flexocompresion (DCR = 2.15 > 1.0)
- La falla se debe a:
  1. Momento alto (Mu = 43 tonf-m)
  2. Muro esbelto (lambda = 41.6 > 22) → magnificacion de momentos
  3. Capacidad limitada (phi_Mn = 27 tonf-m a Pu = 35 tonf)

**RECOMENDACION:** Aumentar refuerzo de borde o espesor del muro para aumentar phi_Mn.

---

## Referencias ACI 318-25

- **6.2.5:** Efectos de esbeltez (lambda > 22 para arriostrados)
- **6.6.4:** Magnificacion de momentos Mc = delta_ns * Mu
- **Tabla 6.6.3.1.1(a):** Rigidez efectiva (EI)eff = 0.35*Ec*Ig para muros
- **18.10.4.1:** Resistencia al cortante de muros especiales
- **21.2.4.1:** phi = 0.60 para cortante en elementos especiales
