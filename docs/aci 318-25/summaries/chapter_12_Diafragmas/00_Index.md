# ACI 318-25 - CAPITULO 12: DIAFRAGMAS

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [12_01_03_Alcance_Limites.md](12_01_03_Alcance_Limites.md) | 12.1-12.3 | Alcance, fuerzas y espesor |
| [12_04_Modelado.md](12_04_Modelado.md) | 12.4 | Modelado y analisis |
| [12_05_Resistencia.md](12_05_Resistencia.md) | 12.5 | Resistencia (cortante, colectores) |
| [12_06_07_Refuerzo.md](12_06_07_Refuerzo.md) | 12.6-12.7 | Limites y detallado de refuerzo |

---

## Resumen del Capitulo

El Capitulo 12 cubre el diseno de diafragmas:

- **12.1-12.3**: Alcance, fuerzas de diseno y espesor
- **12.4**: Metodos de modelado y analisis
- **12.5**: Resistencia al cortante y colectores
- **12.6-12.7**: Refuerzo minimo y detallado

---

## Requisitos Principales

### Resistencia al Cortante (12.5.3)

```
Vn = Acv * (2*λ*√fc' + ρt*fy) <= 8*√fc'*Acv
```

| Parametro | Valor |
|-----------|-------|
| φ | **0.75** |
| √fc' limite | 100 psi max |

### Fuerzas en Cuerdas (Chords)

```
Tu = Cu = Mu / (j*d)
```
Donde j ≈ 0.9

### Colectores

Disenar como miembros a tension/compresion segun 22.4.

**Friccion de cortante:**
```
Vn = μ * Avf * fy
```

| Superficie | μ |
|------------|---|
| Concreto rugoso | 1.4λ |
| Concreto liso | 1.0λ |
| Concreto-acero | 0.6λ |

### Detallado

| Parametro | Requisito |
|-----------|-----------|
| Espaciamiento maximo | menor de (5t, 18 in.) |
| Ubicacion refuerzo tension | dentro de h/4 del borde |
| Extension refuerzo | >= ld mas alla donde no se requiere |

---

*ACI 318-25 Capitulo 12 - Indice*
