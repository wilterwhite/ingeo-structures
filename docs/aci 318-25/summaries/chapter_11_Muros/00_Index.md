# ACI 318-25 - CAPITULO 11: MUROS

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [11_01_03_Alcance_Limites.md](11_01_03_Alcance_Limites.md) | 11.1-11.3 | Alcance y espesor minimo |
| [11_04_05_Resistencia.md](11_04_05_Resistencia.md) | 11.4-11.5 | Resistencia y metodo simplificado |
| [11_06_07_Refuerzo.md](11_06_07_Refuerzo.md) | 11.6-11.7 | Limites y detallado de refuerzo |
| [11_08_Muros_Esbeltos.md](11_08_Muros_Esbeltos.md) | 11.8 | Metodo alternativo para muros esbeltos |

---

## Resumen del Capitulo

El Capitulo 11 cubre el diseno de muros:

- **11.1-11.3**: Alcance y limites dimensionales
- **11.4-11.5**: Resistencia (axial, momento, cortante)
- **11.5.3**: Metodo simplificado (P-e <= h/6)
- **11.5.4**: Cortante en el plano
- **11.6-11.7**: Refuerzo minimo y detallado
- **11.8**: Metodo alternativo para muros esbeltos

---

## Requisitos Principales

### Espesor Minimo (Tabla 11.3.1.1)

| Tipo de Muro | h minimo |
|--------------|----------|
| De carga | Mayor de: **4 in**, **lu/25** |
| Sin carga | Mayor de: **4 in**, **lu/30** |
| Sotano/cimentacion | **7.5 in** |

### Metodo Simplificado (11.5.3)

**Condicion:** e <= h/6 (resultante en tercio medio)
```
Pn = 0.55 * fc' * Ag * [1 - (k*lc/32h)²]
```

| Condicion de Borde | k |
|-------------------|---|
| Arriostrado, restringido | 0.8 |
| Arriostrado, sin restriccion | 1.0 |
| No arriostrado | 2.0 |

### Cortante en el Plano (11.5.4)

```
Vn = (αc*λ*√fc' + ρt*fyt) * Acv <= 8*√fc'*Acv
```

| hw/lw | αc |
|-------|-----|
| <= 1.5 | 3 |
| >= 2.0 | 2 |

### Cuantias Minimas (Tabla 11.6.1)

| Condicion | ρl,min | ρt,min |
|-----------|--------|--------|
| Cortante bajo, barras <= No.5, fy >= 60 ksi | 0.0012 | 0.0020 |
| Cortante bajo, barras > No.5 | 0.0015 | 0.0025 |
| **Cortante alto** | **0.0025** | **0.0025** |

### Espaciamiento Maximo

| Tipo | s_max |
|------|-------|
| General | menor de (3h, 18 in.) |
| Cortante (longitudinal) | lw/3 |
| Cortante (transversal) | lw/5 |

### Doble Cortina
Muros con **h > 10 in.** requieren refuerzo en dos cortinas.

---

*ACI 318-25 Capitulo 11 - Indice*
