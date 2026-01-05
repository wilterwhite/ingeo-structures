# ACI 318-25 - CAPITULO 16: CONEXIONES ENTRE MIEMBROS

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [16_01_03_Alcance_Cimentaciones.md](16_01_03_Alcance_Cimentaciones.md) | 16.1-16.3 | Alcance, prefabricados, conexiones a cimentaciones |
| [16_04_Cortante_Horizontal.md](16_04_Cortante_Horizontal.md) | 16.4 | Cortante horizontal en miembros compuestos |
| [16_05_Mensulas_Corbeles.md](16_05_Mensulas_Corbeles.md) | 16.5 | Mensulas y corbeles |

---

## Resumen del Capitulo

El Capitulo 16 cubre conexiones entre miembros:

- **16.1**: Alcance general
- **16.2**: Conexiones de miembros prefabricados
- **16.3**: Conexiones a cimentaciones
- **16.4**: Cortante horizontal en miembros compuestos
- **16.5**: Mensulas y corbeles

---

## Formulas Principales

### Transferencia a Cimentaciones (16.3)

**Aplastamiento:**
```
Bn = 0.85*f'c*A1*√(A2/A1) <= 1.7*f'c*A1
```

**Dowels minimos:**
```
As,dowel >= 0.005*Ag
Numero minimo: 4 barras
```

### Cortante Horizontal en Compuestos (16.4)

| Condicion | Vnh | Limite |
|-----------|-----|--------|
| Rugosa sin conectores | 80*bv*d | 500*bv*d |
| Rugosa con conectores | (260+0.6*ρv*fy)*bv*d | 500*bv*d |
| Lisa | μ*Avf*fy | - |

**Conectores minimos:**
```
Av >= 50*bv*s/fy
s <= menor de (4*t, 24 in.)
```

### Mensulas y Corbeles (16.5)

**Limites geometricos:**
```
a/d <= 1.0
Nuc <= Vu
d(borde) >= 0.5*d(cara)
```

**Refuerzo principal:**
```
As = mayor de:
  - Af + An
  - (2/3)*Avf + An

As,min = 0.04*(f'c/fy)*b*d
```

**Refuerzo horizontal:**
```
Ah >= 0.5*(As - An)
```

**Resistencia maxima al cortante:**
```
Vn <= menor de:
  - 0.2*f'c*b*d
  - (480 + 0.08*f'c)*b*d
  - 1600*b*d   (psi)
```

### Coeficientes de Friccion μ

| Superficie | μ |
|------------|---|
| Monolitico | 1.4λ |
| Rugoso (1/4 in.) | 1.0λ |
| Liso | 0.6λ |

### Factores φ

| Solicitacion | φ |
|--------------|---|
| Cortante (friccion) | 0.75 |
| Aplastamiento | 0.65 |

---

*ACI 318-25 Capitulo 16 - Indice*
