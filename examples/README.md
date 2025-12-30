# Archivos de Ejemplo

## Pier results.xlsx

Archivo de ejemplo exportado desde ETABS con las tablas necesarias para el análisis estructural.

### Tablas requeridas:
1. **Pier Section Properties** - Propiedades geométricas de los piers
2. **Pier Forces** - Fuerzas y momentos por combinación de carga

### Formato esperado:

#### Pier Section Properties
| Story | Pier | Width Bottom | Thickness Bottom | Material |
|-------|------|--------------|------------------|----------|
| Cielo P2 | PMar-C4-1 | 0.6 | 0.1 | 4000Psi |

#### Pier Forces
| Story | Pier | Output Case | Location | Step Type | P | V2 | V3 | T | M2 | M3 |
|-------|------|-------------|----------|-----------|---|----|----|---|----|----|
| Cielo P2 | PMar-C4-1 | 1.2D+1.6L | Top | | -0.58 | 0.57 | 0 | 0 | 0 | -0.73 |

### Unidades
- Dimensiones: metros (m)
- Fuerzas: tonf
- Momentos: tonf-m
