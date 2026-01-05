# ACI 318-25 - CAPITULO 8: LOSAS EN DOS DIRECCIONES

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [08_01_03_Alcance_Limites.md](08_01_03_Alcance_Limites.md) | 8.1-8.3 | Alcance, general y limites de diseno |
| [08_04_05_Resistencia.md](08_04_05_Resistencia.md) | 8.4-8.5 | Resistencia requerida y de diseno |
| [08_06_07_Refuerzo.md](08_06_07_Refuerzo.md) | 8.6-8.7 | Limites y detallado del refuerzo |
| [08_08_Metodo_Directo.md](08_08_Metodo_Directo.md) | 8.8 | Metodo directo de diseno |
| [08_09_Marco_Equivalente.md](08_09_Marco_Equivalente.md) | 8.9 | Metodo del marco equivalente |
| [08_10_Cortante_Bidireccional.md](08_10_Cortante_Bidireccional.md) | 8.10 | Refuerzo de cortante bidireccional |

---

## Resumen del Capitulo

El Capitulo 8 cubre el diseno de losas en dos direcciones:

- **8.1**: Alcance (losas planas, placas planas, losas con vigas)
- **8.2**: General (aberturas, vigas de borde)
- **8.3**: Limites de diseno (espesor minimo, drop panels)
- **8.4-8.5**: Resistencia requerida y de diseno
- **8.6-8.7**: Limites y detallado del refuerzo
- **8.8**: Metodo directo de diseno
- **8.9**: Metodo del marco equivalente
- **8.10**: Refuerzo de cortante bidireccional (punzonamiento)

---

## Requisitos Principales

### Espesor Minimo (Tabla 8.3.1.1)

| Sistema | Sin drop panel | Con drop panel |
|---------|----------------|----------------|
| Sin vigas de borde | ln/33 >= 5 in. | ln/36 >= 4 in. |
| Con vigas de borde | ln/33 >= 5 in. | ln/36 >= 4 in. |
| Con vigas interiores (αfm >= 2) | 3.5 in. minimo | - |

### Refuerzo Minimo

| Tipo de Losa | As,min |
|--------------|--------|
| No presforzada | **0.0018*Ag** (cada direccion) |
| Presforzada (tendones no adheridos) | **0.004*Act** |

### Espaciamiento Maximo

| Refuerzo | s_max |
|----------|-------|
| Principal | menor de (2h, 18 in.) |
| En banda de columna | <= 2h |

### Metodo Directo - Distribucion de Mo

| Ubicacion | Panel Interior | Panel Borde |
|-----------|----------------|-------------|
| M- exterior | - | 26% |
| M+ claro | 35% | 52% |
| M- interior | 65% | 70% |

### Cortante Bidireccional

| Parametro | Formula |
|-----------|---------|
| Seccion critica | Perimetro a d/2 de columna |
| Vc (control) | 4*λ*λs*√fc' * bo * d |
| λs (efecto tamano) | √(2/(1 + 0.004*d)) <= 1.0 |
| αs | 40 (interior), 30 (borde), 20 (esquina) |

### Transferencia de Momento

| Factor | Formula |
|--------|---------|
| γf (por flexion) | 1 / (1 + (2/3)*√(b1/b2)) |
| γv (por cortante) | 1 - γf |

---

## Formulas Clave

### Momento Estatico Total (Metodo Directo)
```
Mo = qu*l2*ln² / 8
```

### Columna Equivalente (Marco Equivalente)
```
1/Kec = 1/ΣKc + 1/Kt
Kt = Σ(9*Ecs*C) / [l2*(1 - c2/l2)³]
C = Σ[(1 - 0.63*x/y)*(x³*y/3)]
```

### Cortante con Refuerzo
| Tipo | Vn maximo |
|------|-----------|
| Barras/Mallas | 6*λ*√fc' * bo * d |
| Studs | 8*λ*√fc' * bo * d |

---

*ACI 318-25 Capitulo 8 - Indice*
