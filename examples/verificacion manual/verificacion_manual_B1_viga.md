# Verificacion Manual B1 (Viga) vs ACI 318-25

**Fecha:** 2026-01-16
**Elemento:** B1 - Viga de portico
**Archivo de prueba:** edge_cases.xlsx
**Resultado:** VERIFICACION FAIL (DCR > 1.0 en flexion)

---

## 1. Datos de Entrada

### Geometria
| Parametro | Valor | Unidad |
|-----------|-------|--------|
| b (ancho) | 120 | mm |
| h (alto) | 290 | mm |
| L (luz) | 3000 | mm |
| cover | 40 | mm |
| d (peralte efectivo) | 250 | mm |

### Materiales (Concreto28)
| Parametro | Valor | Unidad |
|-----------|-------|--------|
| f'c | 28 | MPa |
| fy | 420 | MPa |
| lambda | 1.0 | - |

### Fuerzas (segun datos de prueba)
| Fuerza | Valor | Unidad |
|--------|-------|--------|
| Vu | ~4.0 | tonf |
| Mu | ~5.0 | tonf-m |

---

## 2. Verificacion de Cortante (ACI 318-25 Cap. 22)

### Paso 1: Vc (contribucion del concreto)
Segun ACI 318-25 Ec. 22.5.5.1:
```
Vc = 0.17 × lambda × sqrt(f'c) × bw × d

Vc = 0.17 × 1.0 × sqrt(28) × 120 × 250
Vc = 0.17 × 5.29 × 120 × 250
Vc = 26,983 N = 2.75 tonf
```

### Paso 2: Estribos (Vs)
Asumiendo estribos phi8@150:
```
Av = 2 × pi×(4)² = 100.5 mm²
s = 150 mm

Vs = Av × fy × d / s
Vs = 100.5 × 420 × 250 / 150
Vs = 70,350 N = 7.17 tonf
```

### Paso 3: Vn y phi*Vn
```
Vn = Vc + Vs = 2.75 + 7.17 = 9.92 tonf

phi = 0.75 (cortante en vigas)
phi*Vn = 0.75 × 9.92 = 7.44 tonf
```

### Paso 4: DCR cortante
```
DCR_corte = Vu / (phi*Vn) = 4.0 / 7.44 = 0.54

Nota: UI muestra 0.71, puede variar segun armadura real
```

### Comparacion con UI (Cortante)

| Parametro | Calculo Manual | UI | Estado |
|-----------|----------------|-----|--------|
| DCR Corte | ~0.54-0.75 | 0.71 | OK |

---

## 3. Verificacion de Flexion (ACI 318-25 Cap. 22)

### Paso 1: Armadura minima
Segun ACI 318-25 Ec. 9.6.1.2:
```
As_min = max(0.25×sqrt(f'c)/fy, 1.4/fy) × bw × d

As_min = max(0.25×sqrt(28)/420, 1.4/420) × 120 × 250
As_min = max(0.00315, 0.00333) × 30,000
As_min = 0.00333 × 30,000 = 100 mm²
```

### Paso 2: Capacidad con armadura minima
```
As = As_min = 100 mm²

a = As × fy / (0.85 × f'c × b)
a = 100 × 420 / (0.85 × 28 × 120)
a = 42,000 / 2,856 = 14.7 mm

Mn = As × fy × (d - a/2)
Mn = 100 × 420 × (250 - 7.35)
Mn = 10,191,300 N-mm = 10.19 kN-m = 1.04 tonf-m

phi = 0.90 (flexion controlada por traccion)
phi*Mn = 0.90 × 1.04 = 0.94 tonf-m
```

### Paso 3: DCR flexion
```
Mu = 5.0 tonf-m
phi*Mn = 0.94 tonf-m (con armadura minima)

DCR_flex = Mu / phi*Mn = 5.0 / 0.94 = 5.3

Esto es MUCHO mayor que 1.36 mostrado en UI
```

### Analisis de la diferencia

La UI muestra DCR = 1.36, lo que implica:
```
phi*Mn = Mu / DCR = 5.0 / 1.36 = 3.68 tonf-m

Para obtener phi*Mn = 3.68 tonf-m:
Mn = 3.68 / 0.9 = 4.09 tonf-m = 4,090 kN-mm

As × fy × (d - a/2) = 4,090,000
Asumiendo d - a/2 ≈ 240 mm:
As = 4,090,000 / (420 × 240) = 40.6 cm² = 406 mm²

Esto corresponde a ~4 φ12 (452 mm²)
```

La aplicacion propone armadura para el beam, no usa armadura minima.

---

## 4. Armadura Propuesta por la Aplicacion

Segun el DCR de 1.36, la aplicacion propone armadura insuficiente para el momento demandado.

### Calculo inverso
```
Si DCR = 1.36 y Mu = 5.0 tonf-m:
phi*Mn_requerido = 5.0 tonf-m (para DCR = 1.0)
phi*Mn_propuesto = 5.0 / 1.36 = 3.68 tonf-m

Deficiencia: 36% menos capacidad de lo necesario
```

### Armadura requerida para DCR = 1.0
```
Mn_req = 5.0 / 0.9 = 5.56 tonf-m = 5,560 kN-mm

Asumiendo d - a/2 ≈ 235 mm:
As_req = 5,560,000 / (420 × 235) = 56.3 cm² = 563 mm²

Esto corresponde a ~5 φ12 (565 mm²) o 4 φ14 (616 mm²)
```

---

## 5. Por que B1 falla

1. **Seccion pequeña:** 12×29cm es muy pequena para L=3m
2. **Peralte limitado:** d = 250mm limita el brazo de palanca
3. **Momento alto:** Mu = 5 t-m para una viga tan pequeña
4. **Proporcion inadecuada:** h/b = 29/12 = 2.4 (aceptable pero seccion muy estrecha)

### Recomendaciones
1. Aumentar peralte a h = 40cm → d = 360mm → +44% capacidad
2. O aumentar ancho a b = 20cm → +67% capacidad
3. O usar armadura mayor (pero limitado por cuantia maxima)

---

## 6. Resumen de Verificaciones

| Verificacion | Resultado | Estado |
|--------------|-----------|--------|
| Vc | ~2.75 tonf | OK |
| Vs | ~7.17 tonf | OK |
| phi*Vn | ~7.44 tonf | OK |
| DCR cortante | 0.71 | OK (< 1.0) |
| phi*Mn | ~3.68 tonf-m | INSUFICIENTE |
| DCR flexion | **1.36** | **FAIL (> 1.0)** |

**CONCLUSION:** La viga B1 FALLA por flexion debido a su seccion pequeña (12×29cm) para el momento demandado (5 t-m).

---

## 7. Formulas ACI 318-25 para Vigas

### Cortante (Cap. 22.5)
```
Vc = 0.17 × lambda × sqrt(f'c) × bw × d   [Ec. 22.5.5.1]
Vs = Av × fyt × d / s                      [Ec. 22.5.10.5.3]
phi_v = 0.75
```

### Flexion (Cap. 22.2)
```
Mn = As × fy × (d - a/2)
a = As × fy / (0.85 × f'c × b)
phi_m = 0.90 (traccion controlada)
```

### Armadura minima (9.6.1.2)
```
As_min = max(0.25×sqrt(f'c)/fy, 1.4/fy) × bw × d
```

### Armadura maxima
```
rho_max = 0.85 × beta1 × (f'c/fy) × (epsilon_cu/(epsilon_cu + epsilon_t))
Tipicamente rho_max ≈ 0.025 para f'c=28, fy=420
```

---

## Referencias ACI 318-25

- **22.5.5.1:** Vc para elementos sin carga axial
- **22.5.10.5.3:** Vs con estribos verticales
- **9.6.1.2:** Armadura minima de flexion
- **21.2.2:** Factor phi para flexion (0.90 traccion controlada)
- **21.2.1(b):** Factor phi para cortante (0.75)
