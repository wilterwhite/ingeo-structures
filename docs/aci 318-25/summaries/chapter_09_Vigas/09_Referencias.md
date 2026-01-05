# ACI 318-25 - Capitulo 9: RESUMEN Y REFERENCIAS

---

## Resumen de Requisitos Principales

### Peraltes Minimos (Concreto Normal, fy = 60 ksi)

| Condicion | h minimo |
|-----------|----------|
| Simplemente apoyada | l/16 |
| Un extremo continuo | l/18.5 |
| Ambos extremos continuos | l/21 |
| Cantilever | l/8 |

### Refuerzo Minimo a Flexion

| Tipo | Requisito |
|------|-----------|
| No presforzado | As,min = mayor de [3 sqrt(f'c) bw d / fy] y [200 bw d / fy] |
| Presforzado (tendones adheridos) | Carga >= 1.2 x carga de agrietamiento |
| Presforzado (tendones no adheridos) | As,min = 0.004 Act |

### Espaciamiento Maximo de Estribos

| Condicion | No Presforzada | Presforzada |
|-----------|----------------|-------------|
| Vs <= 4 sqrt(f'c) bw d | d/2 o 24 in. | 3h/4 o 24 in. |
| Vs > 4 sqrt(f'c) bw d | d/4 o 12 in. | 3h/8 o 12 in. |

### Vigas Profundas

| Parametro | Requisito |
|-----------|-----------|
| Definicion | ln <= 4h o carga concentrada dentro de 2h |
| Cortante maximo | Vu <= phi 10 sqrt(f'c) bw d |
| Refuerzo distribuido minimo | 0.0025 en ambas direcciones |
| Espaciamiento maximo | Menor de d/5 y 12 in. |

---

## Referencias a Otros Capitulos

| Tema | Capitulo/Seccion |
|------|------------------|
| Propiedades del concreto | 19 |
| Propiedades del refuerzo | 20 |
| Factores de reduccion | 21.2 |
| Resistencia a flexion | 22.3, 22.4 |
| Resistencia a cortante | 22.5 |
| Resistencia a torsion | 22.7 |
| Metodo puntal-tensor | 23 |
| Deflexiones | 24.2 |
| Clasificacion de vigas presforzadas | 24.5.2 |
| Desarrollo y empalmes | 25.4, 25.5 |
| Detalles de refuerzo transversal | 25.7 |
| Zonas de anclaje post-tensado | 25.9 |

---

## Variables Principales

| Variable | Descripcion |
|----------|-------------|
| As | Area de refuerzo longitudinal a tension |
| As,min | Area minima de refuerzo a flexion |
| Av | Area de refuerzo a cortante |
| At | Area de una pierna de estribo cerrado para torsion |
| Al | Area de refuerzo longitudinal para torsion |
| Acp | Area encerrada por perimetro exterior de seccion |
| Aoh | Area encerrada por linea central de estribos cerrados |
| Act | Area de concreto en la zona de tension |
| bw | Ancho del alma |
| d | Peralte efectivo |
| h | Peralte total |
| l | Longitud del claro |
| ln | Claro libre |
| ph | Perimetro de linea central de estribos cerrados |
| s | Espaciamiento de estribos |

---

## Factores de Reduccion de Resistencia

| Tipo de Solicitacion | phi |
|---------------------|-----|
| Flexion (controlado por tension) | 0.90 |
| Flexion (zona de transicion) | 0.65 a 0.90 |
| Flexion (controlado por compresion) | 0.65 |
| Cortante | 0.75 |
| Torsion | 0.75 |

---

## Ecuaciones Clave

### Refuerzo Minimo a Flexion

```
As,min = max(3 sqrt(f'c) bw d / fy, 200 bw d / fy)
```

**Nota:** fy limitado a 80,000 psi max para As,min.

### Refuerzo Minimo a Cortante

```
Av,min/s = max(0.75 sqrt(f'c) bw / fyt, 50 bw / fyt)
```

### Factor de Efecto de Tamano (λs) - ACI 318-25

```
λs = sqrt(2 / (1 + 0.004*d)) <= 1.0
```

| d (in.) | λs |
|---------|-----|
| 10 | 0.98 |
| 20 | 0.87 |
| 30 | 0.79 |
| 40 | 0.73 |

**Nota:** λs aplica a Vc en vigas sin Av,min. Ver 22.5 para detalles.

### Combinacion de Refuerzo Transversal (Cortante + Torsion)

```
Total = Av/s + 2 At/s
```

### Cortante Maximo en Vigas Profundas

```
Vu <= phi 10 sqrt(f'c) bw d
```

---

*ACI 318-25 Capitulo 9 - Resumen y Referencias*
