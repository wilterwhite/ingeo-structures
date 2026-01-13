# VERIFICACIÓN DE CLASIFICACIÓN: PIER PFel-A5-1

## Dimensiones del Elemento

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| **lw**    | 640 mm | Largo del muro (dimensión mayor) |
| **tw**    | 260 mm | Espesor del muro (dimensión menor) |
| **hw**    | 3350 mm | Altura del elemento |

---

## PASO 1: Cálculo de Relaciones Geométricas

### 1.1 Relación lw/tw (Clasificación muro vs columna)

```
lw/tw = 640 / 260 = 2.46
```

**Criterio ACI 318-25:**
- lw/tw >= 4 → MURO (usar Sección 18.10)
- lw/tw < 4 → COLUMNA (usar Sección 22.5)

**Resultado:** 2.46 < 4 → **Geométricamente sería COLUMNA** ✓

---

### 1.2 Relación b/h (Requisito §18.7.2.1(b) para columnas especiales)

```
b/h = tw / lw = 260 / 640 = 0.406 ≈ 0.41
```

**Criterio ACI 318-25 §18.7.2.1(b):**
> Para ser columna de pórtico especial, la relación entre la dimensión menor y mayor debe cumplir:
> **b/h >= 0.4**

**Resultado:** 0.41 >= 0.4 → **CUMPLE §18.7.2.1(b)** ✓

**Implicaciones:**
- ✓ El elemento **SÍ puede** ser clasificado como columna de pórtico especial
- ✓ Diseñar según **Capítulo 22** (Sección 22.5)
- ✓ Aplicar requisitos de **§18.7** para detallado sísmico

---

### 1.3 Relación hw/lw (Muro esbelto vs rechoncho)

```
hw/lw = 3350 / 640 = 5.23
```

**Criterio ACI 318-25:**
- hw/lw >= 2.0 → Muro esbelto (comportamiento controlado por flexión)
- hw/lw < 2.0 → Muro rechoncho o wall pier

**Resultado:** 5.23 >= 2.0 → Muro esbelto (no aplica porque ya es columna)

**Nota:** Esta verificación es secundaria porque el elemento ya fue clasificado como COLUMNA por cumplir §18.7.2.1(b).

---

## PASO 2: Lógica de Decisión del Código

Según `app/domain/shear/classification.py`, líneas 94-136:

```python
# Primero verificar si GEOMÉTRICAMENTE sería columna (lw/tw < 4)
if lw_tw < ASPECT_RATIO_WALL_LIMIT:  # ¿2.46 < 4? → SÍ
    # Verificar si cumple §18.7.2.1(b) para ser columna de pórtico especial
    # b = dimensión menor (tw), h = dimensión mayor (lw)
    aspect_ratio = tw / lw  # 260/640 = 0.41

    if aspect_ratio < COLUMN_MIN_ASPECT_RATIO:  # ¿0.41 < 0.4? → NO
        # No cumple §18.7.2.1(b) → reclasificar como MURO
        [...]

    # Sí cumple b/h >= 0.4 → es columna de pórtico especial
    return WallClassification(
        element_type=ElementType.COLUMN,
        aci_section="22.5",
        design_method="column",
        special_requirements="Disenar como columna segun Capitulo 22"
    )
```

**Flujo de decisión:**
1. ¿lw/tw < 4? → **SÍ** (2.46 < 4)
2. ¿b/h >= 0.4? → **SÍ** (0.41 >= 0.4)
3. **Clasificación final:** COLUMNA de pórtico especial

---

## PASO 3: Resultado de la Clasificación

### Clasificación obtenida por `WallClassificationService`

```python
element_type: ElementType.COLUMN
lw:           640 mm
tw:           260 mm
hw:           3350 mm
lw_tw:        2.46
hw_lw:        5.23
aci_section:  "22.5"
design_method: "column"
special_requirements: "Disenar como columna segun Capitulo 22"
```

---

## VERIFICACIÓN FINAL

### Resultado: ✓ **CLASIFICACIÓN CORRECTA**

| Criterio | Valor | Cumple | Implicación |
|----------|-------|--------|-------------|
| lw/tw < 4 | 2.46 | ✓ SÍ | Geométricamente columna |
| b/h >= 0.4 | 0.41 | ✓ SÍ | Cumple §18.7.2.1(b) |
| Clasificación | COLUMN | ✓ SÍ | Correcta según ACI 318-25 |

---

## Interpretación ACI 318-25

El pier **PFel-A5-1** con dimensiones 640×260×3350 mm:

### ✓ CUMPLE los requisitos para ser COLUMNA de pórtico especial

**Justificación:**

1. **§18.7.2.1(b) - Relación de aspecto:**
   - La relación b/h = 0.41 **cumple** el requisito mínimo de 0.4
   - Esto asegura que el elemento tiene suficiente rigidez en ambas direcciones

2. **Diseño según Capítulo 22:**
   - Usar Sección 22.5 para resistencia a cortante
   - Aplicar ecuaciones de columnas para capacidad axial y flexión
   - Vc = 0.17 λ √f'c bw d (para elementos con carga axial)

3. **Detallado sísmico según §18.7:**
   - Confinamiento de núcleo (§18.7.5)
   - Espaciamiento de refuerzo transversal (§18.7.5.3)
   - Requisitos de longitud de desarrollo (§18.7.5.4)
   - Empalmes (§18.7.5.5)

4. **Verificación de dimensión mínima (§18.7.2.1(a)):**
   - tw = 260 mm **< 300 mm** → ⚠️ NO cumple dimensión mínima
   - Requiere análisis adicional o redimensionamiento

---

## Conclusión

La clasificación del sistema como **"COL" (COLUMN)** es **CORRECTA** según:

- ✓ Criterio geométrico lw/tw = 2.46 < 4
- ✓ Criterio de aspecto b/h = 0.41 >= 0.4 (§18.7.2.1(b))
- ✓ Código implementado en `classification.py` líneas 94-136

**Recomendación adicional:**
- Verificar dimensión mínima tw = 260 mm vs requisito de 300 mm (§18.7.2.1(a))
- Evaluar si se requiere aumentar el espesor a 300 mm para cumplir plenamente §18.7.2.1

---

## Referencias de Código

### Archivos revisados:
- `C:\Users\willi\Github\ingeo-structures\app\domain\shear\classification.py`
- `C:\Users\willi\Github\ingeo-structures\app\domain\constants\shear.py`
- `C:\Users\willi\Github\ingeo-structures\app\domain\constants\geometry.py`

### Constantes utilizadas:
```python
ASPECT_RATIO_WALL_LIMIT = 4           # shear.py, línea 173
COLUMN_MIN_ASPECT_RATIO = 0.4         # geometry.py, línea 26
WALL_PIER_HW_LW_LIMIT = 2.0           # shear.py, línea 189
```

### Función de clasificación:
```python
WallClassificationService.classify(lw, tw, hw)
# Ubicación: classification.py, líneas 74-192
```

---

**Fecha de verificación:** 2026-01-13
**Modelo revisado:** ACI 318-25
**Estado:** VERIFICADO ✓
