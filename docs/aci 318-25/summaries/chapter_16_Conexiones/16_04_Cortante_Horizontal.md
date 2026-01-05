# ACI 318-25 - 16.4 CORTANTE HORIZONTAL EN MIEMBROS COMPUESTOS

---

## 16.4.1 Alcance

Aplica al diseno del cortante horizontal en la interface entre:
- Losa colada en sitio y viga prefabricada
- Losa colada en sitio y deck metalico
- Elementos compuestos de concreto

---

## 16.4.2 Resistencia Requerida

### 16.4.2.1 Distribucion de Cortante
El cortante horizontal Vuh puede calcularse:
- **Elasticamente** basado en seccion transformada
- **Plasticamente** basado en fuerzas de compresion/tension en la losa

### 16.4.2.2 Formula Elastica
```
Vuh = Vu * Q / I
```

Donde:
- **Q** = primer momento del area de la losa respecto al eje neutro
- **I** = momento de inercia de la seccion compuesta

### 16.4.2.3 Formula Plastica (Simplificada)
```
Vuh = (C o T) / lv
```

Donde:
- **C o T** = fuerza de compresion o tension en la losa
- **lv** = longitud de cortante

---

## 16.4.3 Resistencia de Diseno

### 16.4.3.1 Requisito General
```
φVnh >= Vuh
```

Donde φ = **0.75**

### 16.4.3.2 Superficie de Contacto

**Sin conectores de cortante** (superficie intencionalmente rugosa a 1/4 in.):
```
Vnh = 80 * bv * d   (psi)
```
Limite: **Vnh <= 500*bv*d**

**Con conectores de cortante minimos** (Av >= 50*bv*s/fy):
```
Vnh = (260 + 0.6*ρv*fy) * bv * d   (psi)
```
Limite: **Vnh <= 500*bv*d**

### 16.4.3.3 Superficie Lisa o sin Conectores Adecuados

Usar friccion de cortante segun **22.9**:
```
Vnh = μ * Avf * fy
```

---

## 16.4.4 Refuerzo de Cortante Horizontal

### 16.4.4.1 Conectores Minimos
Cuando se requiere:
```
Av >= 50 * bv * s / fy
```

### 16.4.4.2 Espaciamiento Maximo
```
s <= menor de:
  - 4 veces el espesor del elemento compuesto mas delgado
  - 24 in.
```

### 16.4.4.3 Anclaje
Los conectores deben:
- Extenderse al menos **ld** dentro de cada elemento
- Ser completamente desarrollados en ambos lados

---

## 16.4.5 Tipos de Superficie de Contacto

| Tipo | Descripcion | Vnh permitido |
|------|-------------|---------------|
| **Rugosa** | Amplitud >= 1/4 in. | 80*bv*d (sin conectores) |
| **Rugosa + conectores** | Con Av minimo | (260 + 0.6*ρv*fy)*bv*d |
| **Lisa** | Sin rugosidad | Usar friccion cortante |

---

## Resumen de Formulas

| Condicion | Vnh | Limite |
|-----------|-----|--------|
| Rugosa sin conectores | 80*bv*d | 500*bv*d |
| Rugosa con conectores | (260+0.6*ρv*fy)*bv*d | 500*bv*d |
| Lisa | μ*Avf*fy | - |

### Coeficientes de Friccion μ (22.9)

| Superficie | μ |
|------------|---|
| Monolitico | 1.4λ |
| Rugoso (1/4 in.) | 1.0λ |
| Liso | 0.6λ |

---

*ACI 318-25 Seccion 16.4*
