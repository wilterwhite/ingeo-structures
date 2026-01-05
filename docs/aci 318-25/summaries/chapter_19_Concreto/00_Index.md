# ACI 318-25 - CAPITULO 19: CONCRETO - Diseño y Durabilidad

## Contenido del Capitulo

| Archivo | Secciones | Contenido |
|---------|-----------|-----------|
| [19_01_02_Alcance_Propiedades.md](19_01_02_Alcance_Propiedades.md) | 19.1-19.2 | f'c, Ec, fr, factor λ |
| [19_03_Durabilidad.md](19_03_Durabilidad.md) | 19.3-19.4 | Exposicion, durabilidad, lechada |

---

## Formulas Rapidas

### Modulo de Elasticidad (Ec)
```
Ec = 57,000 * √f'c          [psi, peso normal]
Ec = wc^1.5 * 33 * √f'c     [psi, liviano]
```

### Modulo de Ruptura (fr)
```
fr = 7.5 * λ * √f'c         [Ec. 19.2.3.1]
```

### Factor β₁
```
β₁ = 0.85 - 0.05*(f'c - 4000)/1000
0.65 ≤ β₁ ≤ 0.85
```

---

## Tablas Principales

| Tabla | Contenido |
|-------|-----------|
| 19.2.1.1 | f'c minimo por aplicacion |
| 19.2.4.1(a) | Factor λ por densidad |
| 19.2.4.1(b) | Factor λ por composicion |
| 19.3.1.1 | Categorias de exposicion (F, S, W, C) |
| 19.3.2.1 | Requisitos por clase de exposicion |
| 19.3.3.1 | Contenido de aire (congelamiento) |

---

## Factor λ - Concreto Liviano

| wc (lb/ft³) | λ |
|-------------|---|
| ≤ 100 | 0.75 |
| 100-135 | 0.0075*wc |
| > 135 | 1.0 |

---

## f'c Minimo por Aplicacion

| Aplicacion | f'c Min (psi) |
|------------|---------------|
| General | 2500 |
| Porticos especiales | 3000 |
| Muros especiales Grado 60/80 | 3000 |
| Muros especiales Grado 100 | 5000 |
| Pilotes presforzados | 5000 |

---

*ACI 318-25 Capitulo 19 - Indice*
