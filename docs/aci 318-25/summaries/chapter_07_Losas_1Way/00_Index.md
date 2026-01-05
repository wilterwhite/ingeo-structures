# ACI 318-25 - CAPITULO 7: LOSAS EN UNA DIRECCION

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [07_01_03_Alcance_Limites.md](07_01_03_Alcance_Limites.md) | 7.1-7.3 | Alcance, general y limites de diseno |
| [07_04_05_Resistencia.md](07_04_05_Resistencia.md) | 7.4-7.5 | Resistencia requerida y de diseno |
| [07_06_Limites_Refuerzo.md](07_06_Limites_Refuerzo.md) | 7.6 | Limites de refuerzo (minimos) |
| [07_07_Detallado_Refuerzo.md](07_07_Detallado_Refuerzo.md) | 7.7 | Detallado del refuerzo |

---

## Resumen del Capitulo

El Capitulo 7 cubre el diseno de losas en una direccion:

- **7.1**: Alcance (losas solidas, sobre deck, compuestas, hollow-core)
- **7.2**: General (cargas concentradas, aberturas, vacios)
- **7.3**: Limites de diseno (espesor minimo, deflexiones)
- **7.4-7.5**: Resistencia requerida y de diseno
- **7.6**: Limites de refuerzo (minimos de flexion, cortante, T&S)
- **7.7**: Detallado del refuerzo (espaciamiento, terminacion, integridad)

---

## Requisitos Principales

### Espesor Minimo (Tabla 7.3.1.1)

| Condicion de Apoyo | h minimo | Modificador fy | Modificador Liviano |
|--------------------|----------|----------------|---------------------|
| Simplemente apoyada | ln/20 | (0.4 + fy/100,000) | mayor de (1.65-0.005wc, 1.09) |
| Un extremo continuo | ln/24 | (0.4 + fy/100,000) | mayor de (1.65-0.005wc, 1.09) |
| Ambos extremos continuos | ln/28 | (0.4 + fy/100,000) | mayor de (1.65-0.005wc, 1.09) |
| En voladizo | ln/10 | (0.4 + fy/100,000) | mayor de (1.65-0.005wc, 1.09) |

**Nota:** Valores base para concreto normal y fy = 60,000 psi.

### Refuerzo Minimo

| Tipo de Losa | As,min |
|--------------|--------|
| No presforzada | **0.0018*Ag** |
| Presforzada (tendones adheridos) | Para φMn >= 1.2*Mcr |
| Presforzada (tendones no adheridos) | **0.004*Act** |

### Espaciamientos Maximos

| Refuerzo | s_max |
|----------|-------|
| Flexion (tendones no adheridos) | menor de (3h, 18 in.) |
| T&S no presforzado | menor de (5h, 18 in.) |
| Tendones T&S | 6 ft |

### Seccion Critica para Cortante

| Tipo | Seccion Critica |
|------|-----------------|
| No presforzada | d desde cara de apoyo |
| Presforzada | h/2 desde cara de apoyo |

### Integridad Estructural
- Al menos **1/4** del As de momento positivo maximo debe ser continuo
- Desarrollar para **1.25*fy** en apoyos no continuos

---

*ACI 318-25 Capitulo 7 - Indice*
