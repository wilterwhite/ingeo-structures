# ACI 318-25 - CAPITULO 10: COLUMNAS

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [10_01_03_Alcance_Limites.md](10_01_03_Alcance_Limites.md) | 10.1-10.3 | Alcance y limites de diseno |
| [10_04_05_Resistencia.md](10_04_05_Resistencia.md) | 10.4-10.5 | Resistencia requerida y de diseno |
| [10_06_Limites_Refuerzo.md](10_06_Limites_Refuerzo.md) | 10.6 | Limites de refuerzo (1%-8%) |
| [10_07_Detallado.md](10_07_Detallado.md) | 10.7 | Detallado, empalmes y transversal |

---

## Resumen del Capitulo

El Capitulo 10 cubre el diseno de columnas:

- **10.1-10.3**: Alcance y limites dimensionales
- **10.4-10.5**: Resistencia (axial, momento, cortante, torsion)
- **10.6**: Limites de refuerzo (As,min = 1%, As,max = 8%)
- **10.7**: Detallado (empalmes, estribos, espirales)

---

## Requisitos Principales

### Refuerzo Longitudinal

| Parametro | Valor |
|-----------|-------|
| As,min | **0.01*Ag** |
| As,max | **0.08*Ag** |
| Barras minimas (rectangular) | 4 |
| Barras minimas (espiral) | 6 |
| Pendiente maxima de codo | 1:6 |
| Empalme minimo | 12 in |

### Resistencia Axial Maxima (Pn,max)

| Tipo | Formula |
|------|---------|
| Con estribos | **0.80 * [0.85*fc'*(Ag-Ast) + fy*Ast]** |
| Con espirales | **0.85 * [0.85*fc'*(Ag-Ast) + fy*Ast]** |

### Factores φ

| Tipo | φ (compresion) |
|------|----------------|
| Con estribos | **0.65** |
| Con espirales | **0.75** |

### Refuerzo Transversal

| Parametro | Estribos | Espirales |
|-----------|----------|-----------|
| s_max | menor de (16db, 48db_t, dimension) | 1 a 3 in. |
| ρs_min | - | 0.45*(Ag/Ach-1)*(fc'/fyt) >= 0.12*fc'/fyt |

---

*ACI 318-25 Capitulo 10 - Indice*
