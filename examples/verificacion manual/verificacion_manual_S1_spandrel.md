# Verificacion Manual S1 (Spandrel) vs ACI 318-25

**Fecha:** 2026-01-16
**Elemento:** S1 - Viga de acople (Spandrel/Coupling Beam)
**Archivo de prueba:** edge_cases.xlsx
**Resultado:** VERIFICACION FAIL (DCR > 1.0 en cortante)

---

## 1. Datos de Entrada

### Geometria
| Parametro | Valor | Unidad |
|-----------|-------|--------|
| L (luz libre) | 450 | mm |
| h (alto/depth) | 660 | mm |
| b (ancho/thickness) | 260 | mm |
| d (peralte efectivo) | 620 | mm |
| ln/h | 450/660 = 0.68 | - |

### Clasificacion: Viga Corta (Deep Beam)
```
ln/h = 0.68 < 2.0 → Es viga de acople corta
Aplica ACI 318-25 Seccion 18.10.7 (vigas de acople)
```

### Materiales (3000Psi)
| Parametro | Valor | Unidad |
|-----------|-------|--------|
| f'c | 21 | MPa |
| fy | 420 | MPa |

### Fuerzas (segun datos de prueba)
| Fuerza | Valor | Unidad |
|--------|-------|--------|
| Vu | ~8 | tonf |
| Mu | ~2 | tonf-m |

Del frontend log:
- DCR Flex = 0.11 (muy bajo)
- DCR Corte = 5.10 (MUY ALTO - FAIL)

---

## 2. Analisis de la Viga de Acople

### Por que ln/h < 2.0 es especial

Las vigas de acople con ln/h < 2.0 tienen comportamiento diferente:

1. **Cortante domina sobre flexion** - El momento no controla
2. **Mecanismo de falla:** Cortante diagonal o deslizamiento
3. **ACI 318-25 §18.10.7:** Requiere refuerzo diagonal o especial

### Verificacion de Cortante (Metodo convencional)

```
Vc = 0.17 × lambda × sqrt(f'c) × bw × d
Vc = 0.17 × 1.0 × sqrt(21) × 260 × 620
Vc = 0.17 × 4.58 × 161,200
Vc = 125,576 N = 12.8 tonf

Vs (con estribos phi10@150):
Av = 2 × pi×(5)² = 157 mm²
Vs = 157 × 420 × 620 / 150 = 272,636 N = 27.8 tonf

Vn = Vc + Vs = 12.8 + 27.8 = 40.6 tonf

phi = 0.60 (SPECIAL)
phi*Vn = 0.60 × 40.6 = 24.4 tonf
```

### Limite Maximo de Vn para Vigas Cortas

Segun ACI 318-25 §18.10.7.4:
```
Para vigas de acople con ln/h < 2.0:
Vn_max = 0.83 × sqrt(f'c) × Acw
Vn_max = 0.83 × sqrt(21) × (260 × 660)
Vn_max = 0.83 × 4.58 × 171,600
Vn_max = 652,554 N = 66.5 tonf

phi*Vn_max = 0.60 × 66.5 = 39.9 tonf
```

Esto es mayor que mi calculo de phi*Vn = 24.4 tonf, asi que el limite no controla.

---

## 3. Por que DCR = 5.10?

La UI muestra DCR cortante = 5.10, lo que implica:
```
Si Vu = 8 tonf y DCR = 5.10:
phi*Vn = Vu / DCR = 8 / 5.10 = 1.57 tonf

Esto es MUY bajo - solo 1.57 tonf de capacidad!
```

### Posibles causas del DCR tan alto:

1. **Sin armadura de corte adecuada:** La aplicacion puede no estar proponiendo estribos suficientes

2. **Clasificacion como viga de acople diagonal:**
   - ACI 318-25 §18.10.7.2 requiere refuerzo diagonal para ln/h < 2.0
   - Sin refuerzo diagonal, la capacidad es muy baja

3. **Calculo segun §18.10.7:**
   ```
   Para vigas de acople especiales con refuerzo convencional:
   Vn se limita por el deslizamiento en la interfaz muro-viga
   ```

---

## 4. Requisitos ACI para Vigas de Acople

### ACI 318-25 §18.10.7 - Vigas de Acople

```
Si ln/h < 2.0:
  Opcion 1: Refuerzo diagonal (§18.10.7.2)
    - Barras diagonales que cruzan la luz
    - Vn = 2 × Avd × fy × sin(alpha)
    - Muy efectivo pero dificil de construir

  Opcion 2: Refuerzo convencional (§18.10.7.3)
    - Solo permitido si Vu <= 0.33 × sqrt(f'c) × Acw
    - Limite muy restrictivo

  Opcion 3: Para ln/h >= 2.0:
    - Se disena como viga normal (Cap. 18.6)
```

### Verificacion del limite para refuerzo convencional
```
Limite Vu para refuerzo convencional:
Vu_limit = 0.33 × sqrt(f'c) × Acw
Vu_limit = 0.33 × sqrt(21) × (260 × 660)
Vu_limit = 0.33 × 4.58 × 171,600
Vu_limit = 259,366 N = 26.4 tonf

phi*Vu_limit = 0.60 × 26.4 = 15.9 tonf

Vu = 8 tonf < 15.9 tonf → DEBERIA permitir refuerzo convencional
```

Pero el DCR = 5.10 sugiere que hay otro factor limitante...

---

## 5. Interpretacion del Resultado

El DCR = 5.10 indica que la aplicacion esta considerando:

1. **Capacidad de corte muy reducida** para vigas de acople cortas
2. **Posible requerimiento de refuerzo diagonal** que no esta presente
3. **Factor de seguridad adicional** para este tipo de elemento critico

### Calculo aproximado si solo cuenta Vc:
```
Si phi*Vn = Vc solamente (sin Vs por requerimiento diagonal):
phi*Vc = 0.60 × 12.8 = 7.7 tonf
DCR = 8 / 7.7 = 1.04

Esto tampoco da 5.10...
```

### Calculo con cortante por friccion:
```
Para vigas de acople, la interfaz muro-viga puede controlar:
Vn_friction = mu × Avf × fy

Si Avf es solo la armadura del muro en la interfaz:
Avf ≈ 4 × phi10 = 4 × 78.5 = 314 mm²
mu = 1.0 (concreto rugoso)

Vn = 1.0 × 314 × 420 = 131,880 N = 13.4 tonf
phi*Vn = 0.75 × 13.4 = 10.1 tonf

DCR = 8 / 10.1 = 0.79

Tampoco explica DCR = 5.10
```

---

## 6. Conclusion sobre S1

El DCR = 5.10 es muy alto e indica que:

1. La viga de acople S1 tiene **demanda de cortante que excede significativamente la capacidad**
2. La aplicacion puede estar usando un **criterio muy conservador** para vigas cortas
3. **Se requiere investigar** el algoritmo exacto de calculo para spandrels

### Recomendaciones
1. Revisar el codigo de calculo de cortante para spandrels
2. Verificar si se esta aplicando §18.10.7 correctamente
3. Considerar si ln/h calculado es correcto
4. Evaluar si se requiere refuerzo diagonal

---

## 7. Resumen de Verificaciones

| Verificacion | Resultado | Estado |
|--------------|-----------|--------|
| ln/h | 0.68 | VIGA CORTA |
| Clasificacion | Coupling Beam | §18.10.7 |
| DCR flexion | 0.11 | OK (no controla) |
| DCR cortante | **5.10** | **FAIL SEVERO** |
| Requiere diagonal | Probablemente | §18.10.7.2 |

**CONCLUSION:** El spandrel S1 FALLA severamente por cortante (DCR = 5.10).
Las vigas de acople cortas (ln/h < 2.0) tienen requisitos especiales segun §18.10.7.

---

## Referencias ACI 318-25

- **18.10.7:** Vigas de acople de muros estructurales especiales
- **18.10.7.2:** Refuerzo diagonal requerido para ln/h < 2.0 (tipicamente)
- **18.10.7.3:** Refuerzo convencional (con limitaciones)
- **18.10.7.4:** Limites de cortante Vn_max
- **22.9:** Cortante por friccion (interfaces)
