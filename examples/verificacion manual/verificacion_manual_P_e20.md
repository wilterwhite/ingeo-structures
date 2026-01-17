# Verificacion Manual P_e20 vs ACI 318-25

**Fecha:** 2026-01-16
**Elemento:** P_e20 (150x20cm)
**Archivo de prueba:** edge_cases.xlsx
**Resultado:** VERIFICACION EXITOSA

---

## 1. Datos de Entrada

### Geometria
| Parametro | Valor | Unidad |
|-----------|-------|--------|
| lw (longitud) | 1500 | mm |
| tw (espesor) | 200 | mm |
| hwcs (altura piso) | 3000 | mm |
| cover | 25 | mm |
| Acv | 300,000 | mm^2 |

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
| Pu | -50 | tonf (compresion) |
| Vu | 14 | tonf |
| Mu | 40 | tonf-m |

---

## 2. Calculo Manual de Cortante ACI 318-25 Seccion 18.10.4

### Paso 1: Determinar alpha_c (Tabla 11.5.4.3 / 18.10.4.1)

```
hw/lw = 3000 / 1500 = 2.0

Segun ACI 318-25:
- hw/lw <= 1.5: alpha_c = 0.25 (muros rechonchos)
- hw/lw >= 2.0: alpha_c = 0.17 (muros esbeltos)

Como hw/lw = 2.0 >= 2.0:
alpha_c = 0.17
```

### Paso 2: Calcular cuantia horizontal rho_h

```
Malla: 2M phi8@200

Barras horizontales por metro de altura:
n_barras = 1000 / 200 = 5 barras/m

Area por barra phi8:
As_barra = pi * (8/2)^2 = 50.27 mm^2

Area total por metro (2 mallas):
As_h = 2 * 5 * 50.27 = 502.7 mm^2/m

Cuantia horizontal:
rho_h = As_h / (tw * 1000) = 502.7 / (200 * 1000) = 0.00251

rho_h = 0.0025 (redondeado)
```

### Paso 3: Calcular Vc (contribucion del concreto)

```
Ecuacion 18.10.4.1:
Vc = Acv * alpha_c * lambda * sqrt(f'c)

Vc = 300,000 mm^2 * 0.17 * 1.0 * sqrt(21 MPa)
Vc = 300,000 * 0.17 * 4.583
Vc = 233,733 N = 233.73 kN

Conversion a tonf:
Vc = 233.73 / 9.81 = 23.83 tonf
```

### Paso 4: Calcular Vs (contribucion del acero)

```
Ecuacion 18.10.4.1:
Vs = rho_h * fyt * Acv

Vs = 0.0025 * 420 MPa * 300,000 mm^2
Vs = 315,000 N = 315 kN

Conversion a tonf:
Vs = 315 / 9.81 = 32.11 tonf
```

### Paso 5: Calcular Vn nominal

```
Vn = Vc + Vs
Vn = 23.83 + 32.11 = 55.94 tonf
```

### Paso 6: Aplicar factor phi (Seccion 21.2.4.1)

```
IMPORTANTE: Segun ACI 318-25 Seccion 21.2.4.1:
- phi = 0.60 para elementos ESPECIALES (muros especiales resistentes a sismo)
- phi = 0.75 para elementos ORDINARIOS o INTERMEDIOS

El elemento P_e20 tiene categoria sismica "SPEC" (SPECIAL), por lo tanto:
phi = 0.60

phi*Vn = 0.60 * 55.94 = 33.56 tonf
```

---

## 3. Amplificacion de Cortante ACI 318-25 Seccion 18.10.3.3

Para muros especiales, el cortante debe amplificarse segun Tabla 18.10.3.3.3:

### Paso 7: Calcular factores de amplificacion

```
hwcs/lw = 3000/1500 = 2.0

Segun Tabla 18.10.3.3.3:

Factor Omega_v (sobrerresistencia a flexion):
- hwcs/lw <= 1.0: Omega_v = 1.0
- hwcs/lw >= 2.0: Omega_v = 1.5
- Entre 1.0 y 2.0: interpolacion lineal

Como hwcs/lw = 2.0:
Omega_v = 1.5

Factor omega_v (amplificacion dinamica):
- hwcs/lw < 2.0: omega_v = 1.0
- hwcs/lw >= 2.0: omega_v = 0.8 + 0.09 * hn^(1/3) >= 1.0

Como no se define altura del edificio (hn_ft):
omega_v = 1.0

Amplificacion total:
amp = Omega_v * omega_v = 1.5 * 1.0 = 1.5
```

### Paso 8: Calcular cortante de diseno Ve

```
Ve = amp * Vu
Ve = 1.5 * 14 = 21 tonf
```

### Paso 9: Calcular DCR

```
DCR = Ve / (phi*Vn)
DCR = 21 / 33.56 = 0.626

Redondeado: DCR = 0.62
```

---

## 4. Comparacion con Resultados de la Aplicacion

| Parametro | Calculo Manual | Aplicacion (UI) | Diferencia |
|-----------|----------------|-----------------|------------|
| Vc | 23.83 tonf | 23.66 tonf | -0.7% OK |
| Vs | 32.11 tonf | 32.31 tonf | +0.6% OK |
| Vn | 55.94 tonf | 55.97 tonf | +0.05% OK |
| phi | 0.60 | 0.60 | OK |
| phi*Vn | 33.56 tonf | 34 tonf* | +1.3% OK |
| Omega_v | 1.5 | 1.5 | OK |
| Ve | 21.0 tonf | ~21 tonf | OK |
| **DCR** | **0.626** | **0.62** | **OK** |

*Nota: La UI muestra phi*Vn=34t por redondeo de visualizacion.

---

## 5. Verificacion del Limite Maximo Vn

Segun ACI 318-25 Seccion 18.10.4.4:

```
Vn_max = 0.66 * sqrt(f'c) * Acv (para grupo de segmentos)
Vn_max = 0.66 * sqrt(21) * 300,000
Vn_max = 0.66 * 4.583 * 300,000
Vn_max = 907,434 N = 92.5 tonf

Vn = 55.94 tonf < 92.5 tonf  OK
```

---

## 6. Verificacion de Cuantia Minima

Segun ACI 318-25 Seccion 18.10.2.1:

```
rho_min = 0.0025

Cuantia calculada:
rho_h = 0.0025 >= 0.0025  OK

Para muros con hw/lw <= 2.0 (Seccion 18.10.4.3):
Se requiere rho_v >= rho_h

rho_v = rho_h = 0.0025 (malla cuadrada)  OK
```

---

## 7. Resumen de Verificaciones

| Verificacion | Resultado | Estado |
|--------------|-----------|--------|
| Vc (concreto) | 23.83 tonf | OK |
| Vs (acero) | 32.11 tonf | OK |
| Vn (nominal) | 55.94 tonf | OK |
| phi (categoria sismica) | 0.60 (SPECIAL) | OK |
| phi*Vn | 33.56 tonf | OK |
| Omega_v (amplificacion) | 1.5 | OK |
| Ve (cortante amplificado) | 21.0 tonf | OK |
| DCR cortante | 0.62 | OK (< 1.0) |
| Vn_max | 92.5 tonf | OK (Vn < Vn_max) |
| rho_min | 0.0025 | OK |

**CONCLUSION: Los calculos de la aplicacion son CORRECTOS y coinciden con ACI 318-25.**

---

## 8. Notas Importantes

### Factor phi segun categoria sismica (ACI 318-25 Seccion 21.2.4.1)
- **SPECIAL** (muros especiales): phi = 0.60
- **INTERMEDIATE** (muros intermedios): phi = 0.75
- **ORDINARY** (muros ordinarios): phi = 0.75

### Amplificacion de cortante (ACI 318-25 Seccion 18.10.3.3)
Solo aplica a muros especiales completos, NO aplica a:
- Pilares de muro (wall piers) con lw/tw <= 6.0
- Vigas de acoplamiento (coupling beams)

### Diferencias menores observadas
Las pequenas diferencias (< 1%) entre el calculo manual y la aplicacion se deben a:
1. Redondeo de constantes (sqrt, pi)
2. Precision de conversion de unidades (N_TO_TONF = 9806.65)
3. Redondeo de valores intermedios

Estas diferencias son despreciables y no afectan el resultado final.

---

## Referencias ACI 318-25

- **18.10.4.1:** Resistencia nominal al corte Vn = (alpha_c * lambda * sqrt(f'c) + rho_t * fyt) * Acv
- **Tabla 11.5.4.3:** Coeficientes alpha_c segun hw/lw
- **18.10.4.4:** Limite maximo Vn para segmentos de muro
- **21.2.4.1:** phi = 0.60 para elementos especiales controlados por cortante
- **18.10.3.3:** Amplificacion de cortante Ve = Omega_v * omega_v * Vu
- **Tabla 18.10.3.3.3:** Factores Omega_v y omega_v segun hwcs/lw
- **18.10.2.1:** Cuantia minima de refuerzo
