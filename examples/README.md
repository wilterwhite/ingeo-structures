# Archivos de Ejemplo

## Pier results.xlsx

Archivo de ejemplo exportado desde ETABS con datos reales de un proyecto.

## test_data_comprehensive.xlsx

Archivo de prueba con casos edge para verificar todas las funcionalidades:

| Grupo | Piers | Descripción |
|-------|-------|-------------|
| **M** | M1-Cont, M2-Cont | Muros continuos (3 y 2 pisos) - prueba hwcs |
| **W** | W1-Column, W2-Wall | Clasificación wall vs column (lw/tw < 4 vs >= 4) |
| **P** | P1-WPCol, P2-WPAlt, P3-WPWall | Wall piers (hw/lw < 2) con diferentes lw/tw |
| **S** | S1-Short, S2-Slender | Esbeltez (lambda < 22 vs > 22) |
| **H** | H1-Squat, H2-Trans, H3-Tall | Relación hw/lw (rechoncho, transición, esbelto) |
| **F** | F1-FlexFail, F2-ShearFail | Casos que deben fallar en flexión y corte |
| **C** | C1-H25, C2-H40 | Diferentes resistencias de concreto |
| **T** | T1-Tension | Muro en tracción neta |

### Características:
- **20 piers** distribuidos en 3 pisos
- **3 materiales**: H25 (25 MPa), H30 (30 MPa), H40 (40 MPa)
- **4 combinaciones**: 1.4D, 1.2D+1.6L, 1.2D+1.0E, 0.9D+1.0E

---

## Tablas requeridas de ETABS

### Pier Section Properties
| Story | Pier | Width Bottom | Thickness Bottom | Material |
|-------|------|--------------|------------------|----------|
| Piso 1 | M1-Cont | 2.0 | 0.25 | H30 |

### Pier Forces
| Story | Pier | Output Case | Location | Step Type | P | V2 | V3 | T | M2 | M3 |
|-------|------|-------------|----------|-----------|---|----|----|---|----|----|
| Piso 1 | M1-Cont | 1.2D+1.6L | Top | Max | -120 | 12 | 4.5 | 0 | 3 | 22.5 |

### Unidades
- Dimensiones: metros (m)
- Fuerzas: tonf
- Momentos: tonf-m
