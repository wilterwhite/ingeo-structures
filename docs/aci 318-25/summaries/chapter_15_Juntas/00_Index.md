# ACI 318-25 - CAPITULO 15: JUNTAS COLADAS EN SITIO

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [15_01_03_Alcance_General.md](15_01_03_Alcance_General.md) | 15.1-15.3 | Alcance, general y limites |
| [15_04_05_Resistencia.md](15_04_05_Resistencia.md) | 15.4-15.5 | Resistencia requerida y de diseno |
| [15_06_08_Refuerzo_Transferencia.md](15_06_08_Refuerzo_Transferencia.md) | 15.6-15.8 | Refuerzo y transferencia de fuerzas |

---

## Resumen del Capitulo

El Capitulo 15 cubre juntas y conexiones coladas en sitio:

- **15.1-15.3**: Alcance, materiales, dimensiones
- **15.4-15.5**: Resistencia al cortante en juntas
- **15.6-15.7**: Refuerzo minimo y detallado
- **15.8**: Transferencia de fuerza axial (compresion, tension, cortante)

---

## Tipos de Juntas

- Nudo viga-columna
- Conexion losa-columna
- Muro-cimentacion
- Columna-cimentacion

---

## Requisitos Principales

### Resistencia del Concreto en Junta

```
fc'(junta) >= 0.7 * fc'(columna)
```

### Cortante en Juntas Viga-Columna

| Confinamiento | Vn |
|---------------|-----|
| 4 caras (vigas) | **20*√fc'*Aj** |
| 3 caras u opuestas | **15*√fc'*Aj** |
| Otras | **12*√fc'*Aj** |

Donde: **Aj = bj * hc**

### Area Efectiva de Junta

```
bj = menor de:
  - bc (ancho columna)
  - bc/2 + Σ(menor de hv/2, extension columna)
  - bc/2 + Σ(extension viga)
```

### Factores φ

| Solicitacion | φ |
|--------------|---|
| Cortante en juntas | **0.85** |
| Aplastamiento | **0.65** |

### Transferencia de Fuerzas en Columnas

| Parametro | Requisito |
|-----------|-----------|
| As,dowel minimo | **0.005*Ag** |
| Numero minimo dowels | **4 barras** |

### Aplastamiento

```
Bn = 0.85*fc'*A1*√(A2/A1) <= 1.7*fc'*A1
```

### Friccion de Cortante

```
Vn = μ * Avf * fy
```

| Superficie | μ |
|------------|---|
| Monolitico | 1.4λ |
| Contra concreto rugoso | 1.0λ |

### Espaciamiento Transversal en Junta

```
s <= menor de (d/4, 6 in.)
```

---

*ACI 318-25 Capitulo 15 - Indice*
