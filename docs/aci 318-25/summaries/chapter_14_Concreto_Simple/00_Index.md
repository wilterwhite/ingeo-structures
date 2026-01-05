# ACI 318-25 - CAPITULO 14: CONCRETO SIMPLE

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [14_01_03_Alcance_Limites.md](14_01_03_Alcance_Limites.md) | 14.1-14.3 | Alcance y limites de diseno |
| [14_04_05_Resistencia.md](14_04_05_Resistencia.md) | 14.4-14.5 | Resistencia requerida y de diseno |
| [14_06_Detallado.md](14_06_Detallado.md) | 14.6 | Juntas y detallado |

---

## Resumen del Capitulo

El Capitulo 14 cubre el diseno de concreto simple estructural:

- **14.1**: Alcance (pedestales, muros, zapatas)
- **14.2**: General (materiales, conexiones, restricciones sismicas)
- **14.3**: Limites de diseno (esbeltez, espesores)
- **14.4-14.5**: Resistencia (axial, flexion, cortante, aplastamiento)
- **14.6**: Detallado (juntas de construccion y contraccion)

---

## Restricciones Sismicas

| SDC | Permitido |
|-----|-----------|
| A, B, C | Si, con limitaciones |
| **D, E, F** | **NO** (muros sotano, fundaciones, pedestales) |

---

## Requisitos Principales

### Limites Geometricos

| Miembro | Parametro | Limite |
|---------|-----------|--------|
| Pedestal | H / dimension menor | **<= 3** |
| Muro | H o L / espesor | **<= 25** |
| Zapata | Espesor en borde | **>= 8 in.** |
| Zapata | Proyeccion | **<= d** |

### Factor de Reduccion

```
φ = 0.60   (para todo concreto simple)
```

### Formulas de Resistencia

| Solicitacion | Formula |
|--------------|---------|
| **Compresion axial** | Pn = 0.60*fc'*A1*[1-(lc/32h)²] |
| **Aplastamiento** | Bn = 0.85*fc'*A1*√(A2/A1) <= 0.85*fc'*A1*2 |
| **Flexion** | Mn = 5*λ*√fc'*Sm |
| **Cortante 1-dir** | Vn = (4/3)*λ*√fc'*bw*h |
| **Cortante 2-dir** | Vn = (4/3)*λ*√fc'*bo*h |

Donde:
- Sm = bh²/6 (modulo de seccion)
- √fc' <= 100 psi

### Factor de Longitud Efectiva k

| Condicion | k |
|-----------|---|
| Arriostrado ambos extremos | 0.8 |
| Arriostrado un extremo | 1.0 |
| No arriostrado | 2.0 |

### Juntas de Contraccion

| Parametro | Requisito |
|-----------|-----------|
| Espaciamiento | <= 25*h |
| Profundidad | >= h/4 |

---

*ACI 318-25 Capitulo 14 - Indice*
