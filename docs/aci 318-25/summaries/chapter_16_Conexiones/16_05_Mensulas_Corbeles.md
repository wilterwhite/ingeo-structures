# ACI 318-25 - 16.5 MENSULAS Y CORBELES

---

## 16.5.1 Alcance

Aplica al diseño de ménsulas y corbeles con:
- **a/d <= 1.0**
- Carga vertical Vu aplicada en la cara exterior

Donde:
- **a** = luz de cortante (distancia de la carga a la cara del apoyo)
- **d** = peralte efectivo

---

## 16.5.2 Dimensionamiento

### 16.5.2.1 Relación a/d

```
a/d <= 1.0
```

### 16.5.2.2 Peralte en Borde Exterior

```
d(borde) >= 0.5 * d(cara de columna)
```

### 16.5.2.3 Fuerza Horizontal

**16.5.2.4** Si no se especifica, asumir:
```
Nuc >= 0.2 * Vu
```

**16.5.2.5** Fuerza horizontal máxima:
```
Nuc <= Vu
```

---

## 16.5.3 Resistencia Requerida

### 16.5.3.1 Combinaciones de Carga

Diseñar para las combinaciones del Capítulo 5.

### 16.5.3.2 Fuerzas de Diseño

| Fuerza | Descripción |
|--------|-------------|
| **Vu** | Cortante vertical factorizado |
| **Nuc** | Fuerza horizontal (tensión) factorizada |
| **Mu** | Momento = Vu*a + Nuc*(h-d) |

---

## 16.5.4 Resistencia de Diseño

### 16.5.4.1 Método de Diseño

Usar modelo puntal-tensor (Capítulo 23) o método simplificado.

### 16.5.4.2 Método Simplificado - Refuerzo Principal

**Área de acero por flexión:**
```
Af = Mu / (φ * fy * (d - a/2))
```

**Área de acero por tensión directa:**
```
An = Nuc / (φ * fy)
```

**Área de acero por fricción de cortante:**
```
Avf = Vu / (φ * μ * fy)
```

### 16.5.4.3 Área Total Requerida

```
As = mayor de:
  (a) Af + An
  (b) (2/3)*Avf + An
```

### 16.5.4.4 Coeficientes de Fricción μ

| Condición | μ |
|-----------|---|
| Monolítico | 1.4λ |
| Contra concreto rugoso | 1.0λ |
| Contra concreto liso | 0.6λ |

Donde λ = factor de concreto liviano (1.0 para normal)

---

## 16.5.5 Límites de Refuerzo

### 16.5.5.1 Refuerzo Principal Mínimo

```
As >= 0.04 * (f'c/fy) * b * d
```

### 16.5.5.2 Refuerzo Horizontal Cerrado (Ah)

```
Ah >= 0.5 * (As - An)
```

Distribuir uniformemente en (2/3)*d adyacente a As.

### 16.5.5.3 Área Total de Cortante

```
As + Ah >= (Avf/3) + An
```

---

## 16.5.6 Detallado del Refuerzo

### 16.5.6.1 Refuerzo Principal As

- Anclar en la cara exterior mediante:
  - Soldadura a barra transversal, o
  - Gancho con doblez hacia abajo

### 16.5.6.2 Desarrollo

| Ubicación | Requisito |
|-----------|-----------|
| Cara exterior | Desarrollar fy antes del punto de carga |
| Cara interior | Desarrollar fy más allá de la sección crítica |

### 16.5.6.3 Refuerzo Horizontal Ah

- Barras cerradas (estribos)
- Espaciamiento uniforme en (2/3)*d
- Anclar en ambos extremos

### 16.5.6.4 Barra de Apoyo

Proporcionar barra transversal en la cara exterior:
- Diámetro >= diámetro de As
- Soldada o con ganchos

---

## 16.5.7 Resistencia Máxima al Cortante

```
Vn <= menor de:
  - 0.2 * f'c * b * d
  - (480 + 0.08*f'c) * b * d
  - 1600 * b * d     (psi)
```

En unidades SI:
```
Vn <= menor de:
  - 0.2 * f'c * b * d
  - (3.3 + 0.08*f'c) * b * d
  - 11 * b * d       (MPa)
```

---

## Resumen de Fórmulas

| Parámetro | Fórmula |
|-----------|---------|
| As (flexión) | Af = Mu/(φ*fy*jd) |
| As (tensión) | An = Nuc/(φ*fy) |
| As (fricción) | Avf = Vu/(φ*μ*fy) |
| As total | max(Af+An, 2Avf/3+An) |
| As,min | 0.04*(f'c/fy)*b*d |
| Ah | >= 0.5*(As-An) |

### Límites Geométricos

| Parámetro | Límite |
|-----------|--------|
| a/d | <= 1.0 |
| Nuc/Vu | <= 1.0 |
| d(borde)/d(cara) | >= 0.5 |

### Factores φ

| Solicitación | φ |
|--------------|---|
| Flexión | 0.90 |
| Cortante (fricción) | 0.75 |

---

*ACI 318-25 Sección 16.5*
