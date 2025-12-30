# ACI 318-25 Capítulo 18: Estructuras Resistentes a Sismos - Parte 2
## Resumen Funcional para Implementación

---

## Índice
1. [18.10.3 Fuerzas de Diseño para Muros](#18103-fuerzas-de-diseño-para-muros)
2. [18.10.4 Resistencia al Cortante de Muros](#18104-resistencia-al-cortante-de-muros)
3. [18.10.5 Diseño por Flexión y Carga Axial](#18105-diseño-por-flexión-y-carga-axial)
4. [18.10.6 Elementos de Borde](#18106-elementos-de-borde-de-muros-estructurales-especiales)
5. [18.10.7 Vigas de Acoplamiento](#18107-vigas-de-acoplamiento-coupling-beams)
6. [18.10.8 Pilares de Muro (Wall Piers)](#18108-pilares-de-muro-wall-piers)
7. [18.10.9 Muros Acoplados Dúctiles](#18109-muros-acoplados-dúctiles)
8. [18.11 Muros Prefabricados Especiales](#1811-muros-estructurales-especiales-prefabricados)
9. [18.12 Diafragmas y Cerchas](#1812-diafragmas-y-cerchas)
10. [18.13 Cimentaciones](#1813-cimentaciones)
11. [18.14 Miembros No Parte del SFRS](#1814-miembros-no-designados-como-parte-del-sfrs)

---

## 18.10.3 Fuerzas de Diseño para Muros

### 18.10.3.1-18.10.3.2 Referencias a Otras Secciones
| Tipo de Elemento | Sección de Referencia |
|------------------|----------------------|
| Segmentos horizontales de muro (incluye vigas de acoplamiento) | 18.10.7 |
| Pilares de muro (wall piers) | 18.10.8 |

### 18.10.3.3 Amplificación de Cortante para Muros

Para muros no cubiertos por 18.10.3.1 o 18.10.3.2, el cortante de diseño debe amplificarse:

**Ecuación de Amplificación:**
```
Ve = Ωv × ωv × VuEh
```

Donde:
- `VuEh` = Cortante debido al efecto sísmico horizontal Eh
- `Ωv` = Factor de sobrerresistencia a flexión
- `ωv` = Factor de amplificación dinámica

### Tabla 18.10.3.3.3 - Factores Ωv y ωv

| Condición | Ωv | ωv |
|-----------|-----|-----|
| hwcs/ℓw ≤ 1.0 | 1.0 | 1.0 |
| 1.0 < hwcs/ℓw < 2.0 | Interpolación lineal entre 1.0 y 1.5 | 1.0 |
| hwcs/ℓw ≥ 2.0 | 1.5 | 0.8 + 0.09×hn^(1/3) ≥ 1.0 |

**Notas:**
- `hwcs` = Altura del muro desde la sección crítica
- `ℓw` = Longitud del muro
- `hn` = Altura total del edificio (pies)

**Alternativas (18.10.3.3.4-18.10.3.3.5):**
- Se permite tomar `Ωv × ωv = Ωo` si el código general incluye factor de sobrerresistencia
- Si `Ωv × ωv = Ωo`, se permite tomar el factor de redundancia = 1.0

```python
def amplification_factors(hwcs, lw, hn_ft):
    """
    Calcula factores de amplificación para cortante en muros.

    Args:
        hwcs: Altura del muro desde sección crítica (in)
        lw: Longitud del muro (in)
        hn_ft: Altura total del edificio (ft)

    Returns:
        tuple: (omega_v, omega_v_factor)
    """
    ratio = hwcs / lw

    # Factor Omega_v
    if ratio <= 1.0:
        omega_v = 1.0
    elif ratio >= 2.0:
        omega_v = 1.5
    else:
        omega_v = 1.0 + 0.5 * (ratio - 1.0)

    # Factor omega_v (amplificación dinámica)
    if ratio < 2.0:
        omega_v_dyn = 1.0
    else:
        omega_v_dyn = max(1.0, 0.8 + 0.09 * (hn_ft ** (1/3)))

    return omega_v, omega_v_dyn

def design_shear_wall(Vu_Eh, hwcs, lw, hn_ft):
    """Calcula cortante de diseño amplificado para muro."""
    omega_v, omega_v_dyn = amplification_factors(hwcs, lw, hn_ft)
    Ve = omega_v * omega_v_dyn * Vu_Eh
    return Ve
```

---

## 18.10.4 Resistencia al Cortante de Muros

### 18.10.4.1 Ecuación de Resistencia Nominal

```
Vn = (αc × λ × √f'c + ρt × fyt) × Acv     [Ec. 18.10.4.1]
```

**Coeficiente αc según relación hw/ℓw:**

| Relación hw/ℓw | αc |
|----------------|-----|
| ≤ 1.5 | 3 |
| ≥ 2.0 | 2 |
| 1.5 < hw/ℓw < 2.0 | Interpolación lineal |

**Límite:** f'c ≤ 12,000 psi para uso en ecuaciones de cortante

### 18.10.4.2 Relación hw/ℓw para Segmentos

Para segmentos de muro, usar el **mayor** de:
- Relación hw/ℓw del muro completo
- Relación hw/ℓw del segmento considerado

### 18.10.4.3 Refuerzo Distribuido

- Muros requieren refuerzo distribuido en dos direcciones ortogonales
- Si hw/ℓw ≤ 2.0: `ρℓ ≥ ρt` (refuerzo vertical ≥ refuerzo horizontal)

### 18.10.4.4 Límites de Resistencia - Factor αsh

**Límites de Vn:**
- Para todos los segmentos verticales: `Vn ≤ Σ(αsh × 8 × √f'c × Acv)`
- Para un segmento individual: `Vn ≤ αsh × 10 × √f'c × Acw`

**Factor αsh:**
```
αsh = 0.7 × (1 + (bw + bcf) × tcf / Acx)² ≤ 1.2     [Ec. 18.10.4.4]
```

Donde:
- `bcf` = Ancho efectivo del ala según 18.10.5.2
- `tcf` = Espesor del ala
- `Acx` = Acv o Acw según aplique
- `αsh` no necesita ser menor que 1.0
- Se permite tomar `αsh = 1.0`

### 18.10.4.5 Segmentos Horizontales y Vigas de Acoplamiento

```
Vn ≤ 10 × √f'c × Acw
```

```python
def alpha_c(hw, lw):
    """Calcula coeficiente αc para resistencia al cortante."""
    ratio = hw / lw
    if ratio <= 1.5:
        return 3.0
    elif ratio >= 2.0:
        return 2.0
    else:
        return 3.0 - (ratio - 1.5) * 2.0  # Interpolación lineal

def shear_strength_wall(fc, lam, rho_t, fyt, Acv, hw, lw):
    """
    Calcula resistencia nominal al cortante del muro.

    Args:
        fc: f'c en psi (máx 12000 para esta ecuación)
        lam: Factor lambda para concreto liviano
        rho_t: Cuantía de refuerzo transversal (horizontal)
        fyt: fy del refuerzo transversal (psi)
        Acv: Área bruta de la sección (in²)
        hw: Altura del muro (in)
        lw: Longitud del muro (in)

    Returns:
        Vn en lb
    """
    fc_limited = min(fc, 12000)
    ac = alpha_c(hw, lw)
    Vn = (ac * lam * (fc_limited ** 0.5) + rho_t * fyt) * Acv
    return Vn

def alpha_sh(bw, bcf, tcf, Acx):
    """Calcula factor αsh para límite de cortante."""
    if bcf == 0 or tcf == 0:
        return 1.0
    alpha = 0.7 * (1 + (bw + bcf) * tcf / Acx) ** 2
    return max(1.0, min(alpha, 1.2))
```

---

## 18.10.5 Diseño por Flexión y Carga Axial

### 18.10.5.1 Requisitos Generales

- Diseñar según Capítulo 22.4
- Considerar concreto y refuerzo desarrollado dentro de:
  - Anchos efectivos de alas
  - Elementos de borde
  - Alma del muro
- Considerar efectos de aberturas

### 18.10.5.2 Ancho Efectivo del Ala

A menos que se realice análisis más detallado:

```
bf = menor de:
    - 0.5 × distancia a alma de muro adyacente
    - 0.25 × altura total del muro sobre la sección
```

```python
def effective_flange_width(dist_to_adjacent_web, total_wall_height_above):
    """
    Calcula ancho efectivo del ala desde la cara del alma.

    Args:
        dist_to_adjacent_web: Distancia a alma de muro adyacente (in)
        total_wall_height_above: Altura del muro sobre la sección (in)

    Returns:
        Ancho efectivo del ala (in)
    """
    return min(0.5 * dist_to_adjacent_web, 0.25 * total_wall_height_above)
```

---

## 18.10.6 Elementos de Borde de Muros Estructurales Especiales

### 18.10.6.1 Dos Enfoques de Diseño

| Enfoque | Sección | Descripción |
|---------|---------|-------------|
| Basado en desplazamiento | 18.10.6.2 | Para muros con hwcs/ℓw ≥ 2.0, continuos desde base |
| Basado en esfuerzos | 18.10.6.3 | Método tradicional, conservador |

### 18.10.6.2 Enfoque Basado en Desplazamiento

**Aplica a:** Muros o pilares con hwcs/ℓw ≥ 2.0, continuos desde base, con sección crítica única.

**(a) Requisito para elementos de borde especiales:**

```
1.5δu/hwcs ≥ ℓw/(600c)     [Ec. 18.10.6.2a]
```

Donde:
- `δu` = Desplazamiento de diseño en la parte superior del muro
- `hwcs` = Altura del muro desde la sección crítica
- `c` = Profundidad del eje neutro (mayor valor calculado)
- `δu/hwcs` no debe tomarse menor que 0.005

**(b) Si se requieren elementos de borde especiales:**

**(i) Extensión vertical:** Mayor de `ℓw` y `Mu/(4Vu)`

**(ii) Requisito de ancho:** `b ≥ √(c × ℓw)/40`

**(iii) Verificación de capacidad de deriva:**
```
δc/hwcs ≥ 1.5 × δu/hwcs     [Ec. 18.10.6.2b]
```

**Capacidad de deriva:**
```
δc/hwcs = (1/100) × [4 - 1/50 - (ℓw/b)(c/b) - Ve/(8×√f'c×Acv)]
```
Mínimo: `δc/hwcs ≥ 0.015`

### 18.10.6.3 Enfoque Basado en Esfuerzos

**Requiere elementos de borde especiales cuando:**
```
σmax ≥ 0.2 × f'c
```

**Se permite discontinuar cuando:**
```
σ < 0.15 × f'c
```

Donde σ = esfuerzo de compresión en fibra extrema, calculado con:
- Cargas factorizadas
- Modelo elástico lineal
- Propiedades de sección bruta

### 18.10.6.4 Requisitos para Elementos de Borde Especiales

| Requisito | Especificación |
|-----------|----------------|
| **(a) Extensión horizontal** | Mayor de: `c - 0.1ℓw` y `c/2` |
| **(b) Ancho mínimo** | `b ≥ hu/16` |
| **(c) Para c/ℓw ≥ 3/8** | `b ≥ 12 in` |
| **(d) Secciones con alas** | Incluir ancho efectivo + extender ≥12" en el alma |
| **(e) Refuerzo transversal** | Según 18.7.5.2(a)-(d), 18.7.5.3, espaciamiento ≤ 1/3 dimensión menor |
| **(f) Espaciamiento hx** | ≤ menor de 14" y (2/3)b |

### Tabla 18.10.6.4(g) - Refuerzo Transversal para Elementos de Borde

| Tipo | Expresiones |
|------|-------------|
| **Ash/sbc (estribos rectangulares)** | Mayor de: (a) `0.3(Ag/Ach - 1)(f'c/fyt)` y (b) `0.09(f'c/fyt)` |
| **ρs (espiral o aro circular)** | Mayor de: (c) `0.45(Ag/Ach - 1)(f'c/fyt)` y (d) `0.12(f'c/fyt)` |

### 18.10.6.5 Cuando NO se Requieren Elementos de Borde Especiales

**(a) Terminación de refuerzo horizontal:**
- Si `ωv×Ωv×Vu < λ×√f'c×Acv`: No requiere gancho
- Caso contrario: Gancho estándar o estribos en U

**(b) Refuerzo transversal si ρ > 400/fy:**
- Satisfacer 18.7.5.2(a)-(e)
- En intersecciones alma-ala: extender ≥12" en cada dirección

### Tabla 18.10.6.5(b) - Espaciamiento Máximo de Refuerzo Transversal

| Grado del Refuerzo | Zona | Espaciamiento Máximo |
|--------------------|------|---------------------|
| **60** | Dentro de ℓw o Mu/4Vu de sección crítica | Menor de: 6db, 6" |
| **60** | Otras ubicaciones | Menor de: 8db, 8" |
| **80** | Dentro de ℓw o Mu/4Vu de sección crítica | Menor de: 5db, 6" |
| **80** | Otras ubicaciones | Menor de: 6db, 6" |
| **100** | Dentro de ℓw o Mu/4Vu de sección crítica | Menor de: 4db, 6" |
| **100** | Otras ubicaciones | Menor de: 6db, 6" |

```python
def check_boundary_element_required_displacement(delta_u, hwcs, lw, c):
    """
    Verifica si se requiere elemento de borde especial (método de desplazamiento).

    Args:
        delta_u: Desplazamiento de diseño (in)
        hwcs: Altura del muro desde sección crítica (in)
        lw: Longitud del muro (in)
        c: Profundidad del eje neutro (in)

    Returns:
        bool: True si se requiere elemento de borde especial
    """
    drift_ratio = max(delta_u / hwcs, 0.005)
    limit = lw / (600 * c)
    return (1.5 * drift_ratio) >= limit

def check_boundary_element_required_stress(sigma_max, fc):
    """
    Verifica si se requiere elemento de borde especial (método de esfuerzos).

    Returns:
        bool: True si se requiere elemento de borde especial
    """
    return sigma_max >= 0.2 * fc

def boundary_element_length(c, lw):
    """Calcula longitud horizontal del elemento de borde."""
    return max(c - 0.1 * lw, c / 2)

def boundary_element_Ash(Ag, Ach, fc, fyt):
    """Calcula Ash/sbc requerido para elemento de borde."""
    expr_a = 0.3 * (Ag / Ach - 1) * (fc / fyt)
    expr_b = 0.09 * (fc / fyt)
    return max(expr_a, expr_b)

def max_tie_spacing_boundary(fy_grade, db, near_critical=True):
    """
    Espaciamiento máximo de refuerzo transversal en borde de muro.

    Args:
        fy_grade: Grado del acero (60, 80, 100)
        db: Diámetro de barra longitudinal más pequeña (in)
        near_critical: True si está cerca de sección crítica
    """
    if fy_grade == 60:
        if near_critical:
            return min(6 * db, 6.0)
        else:
            return min(8 * db, 8.0)
    elif fy_grade == 80:
        if near_critical:
            return min(5 * db, 6.0)
        else:
            return min(6 * db, 6.0)
    else:  # Grade 100
        if near_critical:
            return min(4 * db, 6.0)
        else:
            return min(6 * db, 6.0)
```

---

## 18.10.7 Vigas de Acoplamiento (Coupling Beams)

### Clasificación por Relación de Aspecto

| Relación ℓn/h | Tipo de Refuerzo | Sección |
|---------------|------------------|---------|
| ≥ 4 | Longitudinal + transversal (como viga de pórtico) | 18.10.7.1 |
| < 2 con Vu ≥ 4λ√f'c×Acw | Diagonal obligatorio | 18.10.7.2 |
| 2 ≤ ℓn/h < 4 | Diagonal o longitudinal | 18.10.7.3 |

### 18.10.7.1 Vigas con ℓn/h ≥ 4

- Satisfacer requisitos de 18.6 (vigas de pórticos especiales)
- El borde del muro se interpreta como columna
- No requiere satisfacer 18.6.2.1(b) y (c) si se demuestra estabilidad lateral adecuada

### 18.10.7.2 Vigas con ℓn/h < 2 y Vu ≥ 4λ√f'c×Acw

**Refuerzo diagonal obligatorio**, a menos que se demuestre que:
- La pérdida de rigidez/resistencia no afecta capacidad de carga vertical
- No compromete egreso de la estructura
- No compromete integridad de componentes no estructurales

### 18.10.7.3 Vigas Intermedias (2 ≤ ℓn/h < 4)

Opciones:
- **(a)** Dos grupos de barras diagonales simétricas
- **(b)** Refuerzo longitudinal y transversal según 18.6.3, 18.6.4, 18.6.5

### 18.10.7.4 Vigas con Refuerzo Diagonal

**Resistencia nominal al cortante:**
```
Vn = 2 × Avd × fy × sin(α) ≤ 10×√f'c×Acw     [Ec. 18.10.7.4]
```

Donde:
- `Avd` = Área total de refuerzo en cada grupo diagonal
- `α` = Ángulo entre diagonales y eje longitudinal de la viga

**Requisitos:**
- Mínimo 4 barras por grupo diagonal, en 2+ capas
- Dos opciones de confinamiento: (c) individual o (d) de sección completa

### Opción (c) - Confinamiento de Diagonales Individuales

| Requisito | Especificación |
|-----------|----------------|
| Dimensión mín. del núcleo | ≥ bw/2 paralelo a bw, ≥ bw/5 en otros lados |
| Ash mínimo | Mayor de: `0.09sbc(f'c/fyt)` y `0.3sbc(Ag/Ach-1)(f'c/fyt)` |
| Espaciamiento perpendicular | ≤ 14" |
| Refuerzo perimetral adicional | ≥ 0.002bws cada dirección, espaciamiento ≤ 12" |

### Opción (d) - Confinamiento de Sección Completa

| Requisito | Especificación |
|-----------|----------------|
| Ash mínimo | Mayor de: `0.09sbc(f'c/fyt)` y `0.3sbc(Ag/Ach-1)(f'c/fyt)` |
| Espaciamiento vertical/horizontal | ≤ 8" |
| Cada barra | Soportada por esquina de estribo o gancho |

### Tabla 18.10.7.4 - Espaciamiento Máximo de Refuerzo Transversal

| Grado del Refuerzo Diagonal | Espaciamiento Máximo |
|-----------------------------|---------------------|
| 60 | Menor de: 6db, 6" |
| 80 | Menor de: 5db, 6" |
| 100 | Menor de: 4db, 6" |

### 18.10.7.5 Redistribución de Cortante

Se permite redistribuir Ve entre vigas de acoplamiento si:
- Vigas alineadas verticalmente dentro del mismo muro
- ℓn/h ≥ 2
- Redistribución máxima: 20% del valor de análisis
- `Σ(ϕVn) ≥ Σ(Ve)` de las vigas que comparten cargas

### 18.10.7.6 Penetraciones en Vigas Diagonales

| Requisito | Límite |
|-----------|--------|
| Número máximo | 2 |
| Tipo | Cilíndricas horizontales |
| Diámetro máximo | Mayor de h/6 y 6" |
| Distancia a diagonales | ≥ 2" libre |
| Distancia a extremos | ≥ h/4 libre |
| Distancia a bordes sup/inf | ≥ 4" libre |
| Distancia entre penetraciones | ≥ diámetro mayor |

```python
import math

def coupling_beam_diagonal_shear(Avd, fy, alpha_deg, fc, Acw):
    """
    Calcula resistencia al cortante de viga de acoplamiento diagonal.

    Args:
        Avd: Área de refuerzo en cada grupo diagonal (in²)
        fy: Resistencia del acero (psi)
        alpha_deg: Ángulo de diagonales con eje horizontal (grados)
        fc: f'c (psi)
        Acw: Área de la sección (in²)

    Returns:
        Vn en lb
    """
    alpha_rad = math.radians(alpha_deg)
    Vn_calc = 2 * Avd * fy * math.sin(alpha_rad)
    Vn_max = 10 * (fc ** 0.5) * Acw
    return min(Vn_calc, Vn_max)

def coupling_beam_type(ln, h, Vu, lam, fc, Acw):
    """
    Determina tipo de refuerzo requerido para viga de acoplamiento.

    Returns:
        str: Tipo de refuerzo requerido
    """
    ratio = ln / h
    threshold = 4 * lam * (fc ** 0.5) * Acw

    if ratio >= 4:
        return "longitudinal_per_18.6"
    elif ratio < 2 and Vu >= threshold:
        return "diagonal_required"
    else:
        return "diagonal_or_longitudinal"

def diagonal_confinement_Ash(s, bc, fc, fyt, Ag, Ach):
    """Calcula Ash para confinamiento de diagonales."""
    expr_i = 0.09 * s * bc * (fc / fyt)
    expr_ii = 0.3 * s * bc * (Ag / Ach - 1) * (fc / fyt)
    return max(expr_i, expr_ii)
```

---

## 18.10.8 Pilares de Muro (Wall Piers)

### Definición
Segmentos verticales estrechos de muro, creados por aberturas (puertas, ventanas).

### 18.10.8.1 Requisitos Generales

Los pilares de muro deben satisfacer requisitos de columnas de pórticos especiales (18.7.4, 18.7.5, 18.7.6), con caras de nudo en parte superior e inferior.

**Alternativa para pilares con ℓw/bw > 2.5:**

| Requisito | Especificación |
|-----------|----------------|
| **(a) Cortante de diseño** | Según 18.7.6.1, o ≤ Ωo × Vu del análisis |
| **(b) Vn y refuerzo distribuido** | Según 18.10.4 |
| **(c) Refuerzo transversal** | Estribos cerrados (ganchos 180° si una cortina) |
| **(d) Espaciamiento vertical** | ≤ 6" |
| **(e) Extensión del refuerzo** | ≥ 12" arriba y abajo de altura libre |
| **(f) Elementos de borde** | Si se requiere por 18.10.6.3 |

### 18.10.8.2 Pilares en Borde de Muro

- Proporcionar refuerzo horizontal en segmentos adyacentes arriba y abajo
- Diseñar para transferir el cortante del pilar a segmentos adyacentes

---

## 18.10.9 Muros Acoplados Dúctiles

### 18.10.9.1-18.10.9.3 Requisitos

| Elemento | Requisito |
|----------|-----------|
| **Muros individuales** | hwcs/ℓw ≥ 2, satisfacer 18.10 |
| **Vigas de acoplamiento** | ℓn/h ≥ 2 en todos los niveles |
| **90% de los niveles** | ℓn/h ≤ 5 |
| **Desarrollo del refuerzo** | Según 18.10.2.5 en ambos extremos |

---

## 18.10.10 Juntas de Construcción

### 18.10.10.1 Requisitos
- Especificar según 26.5.6
- Superficies de contacto rugosas según condición (b) de Tabla 22.9.4.2

---

## 18.10.11 Muros Discontinuos

### 18.10.11.1 Columnas de Soporte
Columnas que soportan muros discontinuos deben reforzarse según **18.7.5.6**.

---

## 18.11 Muros Estructurales Especiales Prefabricados

### 18.11.1 Alcance
Aplica a muros estructurales especiales construidos con concreto prefabricado como parte del SFRS.

### 18.11.2 General

| Tipo | Requisitos |
|------|------------|
| **18.11.2.1** | Satisfacer 18.10 y 18.5.2; 18.10.2.4 no aplica si deformaciones concentradas en juntas |
| **18.11.2.2** | Muros con postensado no adherido: Satisfacer ACI CODE-550.6 |

---

## 18.12 Diafragmas y Cerchas

### 18.12.1 Alcance

| SDC | Aplicabilidad |
|-----|---------------|
| D, E, F | Diafragmas, colectores, cerchas |
| C, D, E, F | Diafragmas de concreto prefabricado (18.12.11) |

### 18.12.2 Fuerzas de Diseño

- Obtener del código general de construcción
- Considerar combinaciones de carga aplicables
- Para colectores: Amplificar por factor Ωo

### 18.12.4-18.12.5 Losas de Recubrimiento

| Tipo | Requisitos |
|------|------------|
| **Compuesta** | Reforzada, superficie rugosa, intencional |
| **No compuesta** | Diseñar losa de recubrimiento para resistir fuerzas sísmicas sola |

### 18.12.6 Espesor Mínimo de Diafragmas

| Tipo | Espesor Mínimo |
|------|----------------|
| Losas de concreto | 2" |
| Losas compuestas sobre prefabricado | 2" |
| Losas no compuestas sobre prefabricado | 2-1/2" |

### 18.12.7 Refuerzo

| Requisito | Especificación |
|-----------|----------------|
| **18.12.7.1 Espaciamiento máx** | 18" (excepto postensadas) |
| **18.12.7.1 Malla electrosoldada** | Alambre paralelo a juntas: espaciamiento ≥ 10" |
| **18.12.7.3 Desarrollo** | Todo el refuerzo para fy en tensión |
| **18.12.7.4 Empalmes mecánicos** | Clase G o S en conexión diafragma-elemento vertical |
| **18.12.7.5 Colectores** | Esfuerzo promedio ≤ ϕfy con fy ≤ 60,000 psi |

### 18.12.7.6 Refuerzo Transversal para Colectores

**Requerido cuando:** Esfuerzo de compresión > 0.2f'c (o 0.5f'c con Ωo)

### Tabla 18.12.7.6 - Refuerzo Transversal para Colectores

| Tipo | Expresión |
|------|-----------|
| **Ash/sbc (rectangular)** | `0.09(f'c/fyt)` |
| **ρs (espiral/circular)** | Mayor de: `0.45(Ag/Ach-1)(f'c/fyt)` y `0.12(f'c/fyt)` |

### 18.12.9 Resistencia al Cortante

**18.12.9.1 Ecuación general:**
```
Vn = Acv × (2λ√f'c + ρt×fy)     [Ec. 18.12.9.1]
```

**18.12.9.2 Límite máximo:**
```
Vn ≤ 8√f'c × Acv
```

**18.12.9.3 Fricción por cortante (juntas de prefabricado):**
```
Vn = Avf × fy × μ     [Ec. 18.12.9.3]
```
- μ = 1.0λ
- ≥ 50% de Avf debe distribuirse uniformemente

### 18.12.12 Cerchas Estructurales

### Tabla 18.12.12.1 - Refuerzo Transversal para Cerchas

| Tipo | Expresiones |
|------|-------------|
| **Ash/sbc (rectangular)** | Mayor de: (a) `0.3(Ag/Ach-1)(f'c/fyt)` y (b) `0.09(f'c/fyt)` |
| **ρs (espiral/circular)** | Mayor de: (c) `0.45(Ag/Ach-1)(f'c/fyt)` y (d) `0.12(f'c/fyt)` |

```python
def diaphragm_shear_strength(Acv, lam, fc, rho_t, fy):
    """Resistencia al cortante del diafragma."""
    return Acv * (2 * lam * (fc ** 0.5) + rho_t * fy)

def diaphragm_shear_limit(fc, Acv):
    """Límite máximo de cortante del diafragma."""
    return 8 * (fc ** 0.5) * Acv

def collector_transverse_Ash(s, bc, fc, fyt):
    """Ash para colectores con compresión alta."""
    return 0.09 * s * bc * (fc / fyt)
```

---

## 18.13 Cimentaciones

### 18.13.1 Alcance
Aplica a cimentaciones que:
- Resisten fuerzas inducidas por sismo
- Transfieren fuerzas sísmicas entre estructura y suelo

### 18.13.2 Zapatas, Losas de Cimentación y Cabezales

**(Aplica a SDC D, E, F)**

| Sección | Requisito |
|---------|-----------|
| **18.13.2.2** | Refuerzo longitudinal debe desarrollar fy en tensión en la interfaz |
| **18.13.2.3** | Columnas con condición empotrada: ganchos 90° hacia el centro |
| **18.13.2.4** | Columnas/elementos de borde cerca del borde (≤ 0.5×profundidad): refuerzo transversal según 18.7.5.2-18.7.5.4 extendido ℓd en cimentación |
| **18.13.2.5** | Fuerzas de levantamiento: refuerzo en cara superior según 7.6.1 o 9.6.1 |
| **18.13.2.6** | Concreto simple según 14.1.3 |
| **18.13.2.7** | Pilotes inclinados: diseñar cabezal para resistencia completa |

### 18.13.3 Vigas de Cimentación y Losas sobre Terreno

| Sección | SDC | Requisito |
|---------|-----|-----------|
| **18.13.3.1** | D, E, F | Vigas de cimentación según 18.6 |
| **18.13.3.2** | C, D, E, F | Losas sobre terreno como diafragmas según 18.12 |

### 18.13.4 Amarres Sísmicos de Cimentación

| Sección | SDC | Requisito |
|---------|-----|-----------|
| **18.13.4.1** | C, D, E, F | Interconectar cabezales en direcciones ortogonales |
| **18.13.4.2** | D, E, F | Zapatas en Clase de Sitio E o F |
| **18.13.4.3** | - | Resistencia ≥ 0.1×SDS × (mayor carga D+L factorizada) |
| **18.13.4.4** | D, E, F | Vigas de amarre: dimensión mín ≥ L/20, máx 18"; estribos @ ≤ 0.5×dimensión menor o 12" |

### 18.13.5 Cimentaciones Profundas

**(SDC C, D, E, F)**

| Tipo | Requisitos Clave |
|------|------------------|
| **Todos (18.13.5.2)** | Refuerzo continuo para tensión |
| **Todos (18.13.5.4)** | Ganchos sísmicos para estribos |
| **SDC D, E, F (18.13.5.5)** | Refuerzo según 18.7.5.2, 18.7.5.3, Tabla 18.7.5.4(e) en 7 diámetros arriba/abajo de interfaces de estratos |

### Tabla 18.13.5.7.1 - Refuerzo Mínimo para Pilotes Vaciados en Sitio

| Parámetro | SDC C | SDC D, E, F - Sitio A, B, C, D | SDC D, E, F - Sitio E, F |
|-----------|-------|-------------------------------|-------------------------|
| **Cuantía long. mín** | 0.0025 | 0.005 | 0.005 |
| **Longitud reforzada** | Mayor de: 1/3 long., 10', 3D, long. flexural | Mayor de: 1/2 long., 10', 3D, long. flexural | Longitud completa |
| **Zona de confinamiento** | 3D desde cabezal | 3D desde cabezal | 7D desde cabezal |
| **Espaciamiento zona conf.** | ≤ menor de 6", 8db | Según 18.7.5.3, ≥ 0.5×Tabla 18.7.5.4(e) | Según 18.7.5.3, ≥ Tabla 18.7.5.4(e) |

### 18.13.5.10 Pilotes Pretensados Prefabricados

**18.13.5.10.4 SDC C - Refuerzo transversal:**
```
ρs ≥ 0.15(f'c/fyt)     [Ec. 18.13.5.10.4a]
```
o análisis más detallado:
```
ρs ≥ 0.04(f'c/fyt)(2.8 + 2.3Pu/(f'c×Ag))     [Ec. 18.13.5.10.4b]
```

**18.13.5.10.5 SDC D, E, F:**
```
ρs ≥ 0.2(f'c/fyt)     [Ec. 18.13.5.10.5a]
```
o:
```
ρs ≥ 0.06(f'c/fyt)(2.8 + 2.3Pu/(f'c×Ag))     [Ec. 18.13.5.10.5b]
```

**18.13.5.10.6 Carga axial máxima factorizada:**

| Tipo de Pilote | Límite de Pu |
|----------------|--------------|
| Cuadrado ≤ 14" | 0.2f'c×Ag |
| Cuadrado > 14" | 0.25f'c×Ag |
| Circular/Octogonal ≤ 24" | 0.4f'c×Ag |
| Circular/Octogonal > 24" | 0.45f'c×Ag |

```python
def pile_transverse_SDC_C(fc, fyt, Pu=None, Ag=None, detailed=False):
    """
    Refuerzo transversal para pilotes pretensados SDC C.

    Args:
        fc, fyt: Resistencias (psi)
        Pu, Ag: Para análisis detallado
        detailed: Si usar ecuación detallada
    """
    if detailed and Pu is not None and Ag is not None:
        return 0.04 * (fc / fyt) * (2.8 + 2.3 * Pu / (fc * Ag))
    return 0.15 * (fc / fyt)

def pile_transverse_SDC_DEF(fc, fyt, Pu=None, Ag=None, detailed=False):
    """Refuerzo transversal para pilotes pretensados SDC D, E, F."""
    if detailed and Pu is not None and Ag is not None:
        return 0.06 * (fc / fyt) * (2.8 + 2.3 * Pu / (fc * Ag))
    return 0.2 * (fc / fyt)

def max_axial_prestressed_pile(fc, Ag, pile_type, dimension):
    """
    Carga axial máxima para pilotes pretensados.

    Args:
        pile_type: 'square' o 'circular'
        dimension: Lado o diámetro (in)
    """
    if pile_type == 'square':
        factor = 0.2 if dimension <= 14 else 0.25
    else:  # circular or octagonal
        factor = 0.4 if dimension <= 24 else 0.45
    return factor * fc * Ag
```

---

## 18.14 Miembros No Designados como Parte del SFRS

### 18.14.1 Alcance
Aplica a miembros no parte del SFRS en estructuras SDC D, E, F.

### 18.14.2 Acciones de Diseño

Evaluar para combinaciones de carga de gravedad (5.3) incluyendo:
- Efecto del movimiento vertical del suelo
- Actuando simultáneamente con desplazamiento de diseño δu

### 18.14.3 Vigas, Columnas y Nudos Vaciados en Sitio

### 18.14.3.2 Cuando Momentos/Cortantes Inducidos NO Exceden Resistencia

| Elemento | Requisitos |
|----------|------------|
| **Vigas** | 18.6.3.1; refuerzo transversal @ ≤ d/2; si Pu > Agf'c/10: estribos según 18.7.5.2 @ ≤ menor de 6db, 6" |
| **Columnas** | 18.7.4.1, 18.7.6; espirales/estribos @ ≤ menor de 6db, 6" en toda altura; 18.7.5.2(a)-(e) en longitud ℓo |
| **Columnas con Pu > 0.35Po** | Además: 18.7.5.7; refuerzo transversal ≥ 0.5× Tabla 18.7.5.4 en longitud ℓo |
| **Nudos** | Capítulo 15 |

### 18.14.3.3 Cuando Momentos/Cortantes Inducidos EXCEDEN Resistencia (o no calculados)

| Elemento | Requisitos |
|----------|------------|
| **Materiales, empalmes** | Según 18.2.5-18.2.8 (pórticos especiales) |
| **Vigas** | 18.14.3.2(a) + 18.6.5 |
| **Columnas** | 18.7.4, 18.7.5, 18.7.6 (excepto 18.7.4.3) |
| **Nudos** | 18.4.4.1 |

### 18.14.5 Conexiones Losa-Columna

### 18.14.5.1 Refuerzo de Cortante Requerido

**Losas no pretensadas:**
```
Δx/hsx ≥ 0.035 - (1/20)(vuv/ϕvc)
```

**Losas postensadas no adheridas (fpc según 8.6.2.1):**
```
Δx/hsx ≥ 0.040 - (1/20)(vuv/ϕvc)
```

### 18.14.5.2 Exención de Refuerzo de Cortante

| Tipo de Losa | Límite de Deriva |
|--------------|------------------|
| No pretensada | Δx/hsx ≤ 0.005 |
| Postensada no adherida | Δx/hsx ≤ 0.01 |

### 18.14.5.3 Requisitos del Refuerzo

- `vs ≥ 3.5√f'c` en sección crítica
- Extender ≥ 4 veces espesor de losa desde cara del soporte

### 18.14.6 Pilares de Muro

Pilares no parte del SFRS: Satisfacer 18.10.8

```python
def slab_column_shear_reinforcement_required(drift_ratio, vuv, phi_vc, prestressed=False):
    """
    Verifica si se requiere refuerzo de cortante en conexión losa-columna.

    Args:
        drift_ratio: Δx/hsx
        vuv: Esfuerzo cortante por gravedad
        phi_vc: ϕVc de la conexión
        prestressed: True para losas postensadas

    Returns:
        bool: True si se requiere refuerzo
    """
    base = 0.040 if prestressed else 0.035
    threshold = base - (1/20) * (vuv / phi_vc)
    return drift_ratio >= threshold

def slab_column_exempt(drift_ratio, prestressed=False):
    """Verifica si la conexión está exenta de refuerzo de cortante."""
    limit = 0.01 if prestressed else 0.005
    return drift_ratio <= limit
```

---

## Referencias Cruzadas Importantes

| Tema | Sección de Referencia |
|------|----------------------|
| Vigas de pórticos especiales | 18.6 |
| Columnas de pórticos especiales | 18.7 |
| Nudos de pórticos especiales | 18.8 |
| Propiedades de sección bruta | 22.4 |
| Ganchos sísmicos | 25.3 |
| Desarrollo de refuerzo | 25.4, 25.5 |
| Empalmes mecánicos | 25.5.7 |
| Fricción por cortante | 22.9 |
| Diafragmas (diseño general) | Capítulo 12 |
| Integridad estructural | 4.10 |
| Concreto simple en cimentaciones | 14.1.3 |
| Requisitos de soporte prefabricado | 16.2.6 |

---

## Notas de Implementación

### Prioridades de Verificación para Muros

1. **Clasificación del muro:** hwcs/ℓw para determinar factores de amplificación
2. **Cortante de diseño:** Aplicar factores Ωv y ωv
3. **Resistencia al cortante:** Verificar Vn con límites
4. **Elementos de borde:** Método de desplazamiento o esfuerzos
5. **Detallado de elementos de borde:** Dimensiones, refuerzo transversal
6. **Vigas de acoplamiento:** Clasificar y detallar según ℓn/h

### Verificaciones para Diafragmas

1. Determinar fuerzas de diseño del código general
2. Verificar espesor mínimo
3. Calcular resistencia al cortante (incluyendo fricción en juntas)
4. Verificar colectores con factor Ωo
5. Proporcionar refuerzo transversal si compresión > 0.2f'c

### Verificaciones para Cimentaciones

1. Desarrollo de refuerzo longitudinal en interface
2. Amarres sísmicos entre elementos
3. Refuerzo transversal en zonas de confinamiento de pilotes
4. Límites de carga axial para pilotes pretensados

---

*Documento generado para implementación en app estructural - ACI 318-25 Capítulo 18 Parte 2*
*Páginas 350-392 del código original*
