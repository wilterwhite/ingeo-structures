# ACI 318-25 - CAPITULO 13: FUNDACIONES

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [13_01_Alcance.md](13_01_Alcance.md) | 13.1 | Alcance y tipos de fundaciones |
| [13_02_Generalidades.md](13_02_Generalidades.md) | 13.2 | Requisitos generales, secciones criticas y desarrollo |
| [13_03_Superficiales.md](13_03_Superficiales.md) | 13.3 | Fundaciones superficiales (zapatas, losas, muros) |
| [13_04_Profundas.md](13_04_Profundas.md) | 13.4 | Fundaciones profundas (pilotes, pilas, cabezales) |
| [13_Resumenes.md](13_Resumenes.md) | Resumenes | Dimensiones minimas y factores de reduccion |
| [13_Referencias.md](13_Referencias.md) | Referencias | Referencias a otros capitulos y documentos |

---

## Tipos de Fundaciones - Resumen

**Superficiales:**
| Tipo | Seccion |
|------|---------|
| Zapatas corridas (Strip footings) | 13.3.2 |
| Zapatas aisladas (Isolated footings) | 13.3.3 |
| Zapatas combinadas (Combined footings) | 13.3.4 |
| Losas de fundacion (Mat foundations) | 13.3.4 |
| Vigas de fundacion (Grade beams) | 13.3.5 |
| Muros de contencion | 13.3.6 |
| Muros de sotano | 13.3.7 |

**Profundas:**
| Tipo | Seccion |
|------|---------|
| Pilotes colados en sitio | 13.4.4 |
| Pilotes precolados | 13.4.5 |
| Cabezales de pilotes | 13.4.6 |
| Pilas perforadas | 13.4 |
| Cajones | 13.4 |

---

## Requisitos Principales

### Secciones Criticas (Tabla 13.2.7.1)

| Miembro Soportado | Seccion Critica para Mu |
|-------------------|-------------------------|
| Columna/pedestal | Cara de columna |
| Columna con placa base | Mitad entre cara y borde placa |
| Muro concreto | Cara del muro |
| Muro mamposteria | Mitad entre centro y cara |

### Zapatas Rectangulares - Distribucion de Refuerzo

```
γs = 2 / (β + 1)
```
Donde β = lado largo / lado corto

### Cortante en Fundaciones Rigidas

```
Vc = 2*λ*√fc' * bw * d     (una direccion)
λs = 1.0                    (dos direcciones - sin efecto de tamano)
```

### Dimensiones Minimas

| Elemento | Minimo |
|----------|--------|
| Profundidad efectiva zapatas | **6 in.** |
| Profundidad efectiva cabezales | **12 in.** |
| Pilotes precolados (lado) | **10 in.** |
| Pilotes colados en sitio (Ø) | **12 in.** |
| Embedment pilote en cabezal | **3 in.** |
| Extension cabezal mas alla pilote | **4 in.** |

### Factores φ para Pilotes (Tabla 13.4.3.2)

| Tipo | φ |
|------|---|
| Sin camisa | **0.55** |
| En roca/camisa (t < 0.25") | **0.60** |
| Tubo acero (t >= 0.25") | **0.70** |
| Camisa confinada | **0.65** |
| Precolado | **0.65** |

### Refuerzo Minimo Pilotes

| Tipo | As,min |
|------|--------|
| Colados en sitio | **0.0025*Ag** |
| Precolados no presforzados | **0.008*Ag** |

---

*ACI 318-25 Capitulo 13 - Indice*
