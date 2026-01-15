# ACI 318-25 - Secciones 23.3-23.4: RESISTENCIA DE STRUTS

---

## 23.3 RESISTENCIA DE DISENO

### 23.3.1 Criterio de Aceptacion

Para CADA combinacion de carga, verificar:

```
phi * Fns >= Fus     (Struts)
phi * Fnt >= Fut     (Ties)
phi * Fnn >= Fun     (Nodal zones)
```

Donde:
- **phi = 0.75** (factor de reduccion, segun 21.2)
- **Fns, Fnt, Fnn** = Resistencias nominales
- **Fus, Fut, Fun** = Fuerzas factorizadas

---

## 23.4 RESISTENCIA DE STRUTS

### 23.4.1 Resistencia Nominal

**Sin refuerzo longitudinal de compresion (23.4.1a):**

```
Fns = fce * Acs     [Ec. 23.4.1a]
```

**Con refuerzo longitudinal de compresion (23.4.1b):**

```
Fns = fce * Acs + As' * fs'     [Ec. 23.4.1b]
```

Donde:
- **fce** = Resistencia efectiva del concreto (psi)
- **Acs** = Area de seccion transversal del strut (in²)
- **As'** = Area de refuerzo longitudinal en compresion (in²)
- **fs'** = Esfuerzo en refuerzo de compresion = fy (para Grado 40 o 60)

---

### 23.4.3 Resistencia Efectiva del Concreto

```
fce = 0.85 * beta_c * beta_s * fc'     [Ec. 23.4.3]
```

Donde:
- **fc'** = Resistencia a compresion del concreto (psi)
- **beta_s** = Coeficiente del strut (0.4 a 1.0)
- **beta_c** = Factor de confinamiento (1.0 a 2.0)

---

### 23.4.3(a) Coeficiente del Strut (beta_s)

| Ubicacion | Tipo | Refuerzo | beta_s |
|-----------|------|----------|--------|
| Zonas de tension | Cualquiera | Cualquiera | **0.4** |
| Juntas viga-columna | Interior | Per. Cap. 15, 18 | **0.75** |
| Otros casos | Boundary | Cualquiera | **1.0** |
| Otros casos | Interior | Per. Tab. 23.5.1 (a) o (b) | **0.75** |
| Otros casos | Interior | No per. Tab. 23.5.1, pero sat. 23.4.4 | **0.75** |
| Otros casos | Interior | No per. Tab. 23.5.1 ni 23.4.4 | **0.4** |

**Notas:**
- **Boundary strut**: En frontera/apoyo, sin tension transversal
- **Interior strut**: Diagonal interior, con tension transversal
- **Zona de tension**: Strut en miembro sometido a tension

---

### 23.4.3(b) Factor de Confinamiento (beta_c)

| Ubicacion | beta_c |
|-----------|--------|
| Extremo de strut con bearing | sqrt(A2/A1) <= **2.0** |
| Nodo con superficie de bearing | Maximo **2.0** |
| Otros casos (sin confinamiento) | **1.0** |

Donde:
- **A1** = Area de la placa de apoyo
- **A2** = Area de la piramide de distribucion

---

### 23.4.4 Verificacion de Tension Diagonal

Cuando beta_s = 0.75 por satisfacer 23.4.4:

```
Vu <= phi * 5 * tan(theta) * lambda_s * sqrt(fc') * bw * d     [Ec. 23.4.4]
```

Donde:
- **theta** = Angulo del strut respecto a la horizontal (grados)
- **lambda_s** = Factor de efecto de tamano
- **bw** = Ancho del alma (in)
- **d** = Profundidad efectiva (in)

**Factor de Efecto de Tamano (23.4.4.1):**

```
lambda_s = sqrt(2 / (1 + d/10)) <= 1.0     [Sin refuerzo distribuido]
lambda_s = 1.0                              [Con refuerzo distribuido]
```

Unidades: d en pulgadas

---

## RESUMEN DE COEFICIENTES

### Tabla Resumen beta_s

| Condicion | beta_s | Observacion |
|-----------|--------|-------------|
| Zona de tension | **0.4** | Mas conservador |
| Interior sin refuerzo adecuado | **0.4** | Requiere mas area |
| Interior con refuerzo Tab. 23.5.1 | **0.75** | Refuerzo distribuido |
| Interior satisface 23.4.4 | **0.75** | Verificacion diagonal |
| Boundary strut | **1.0** | Menos conservador |
| Junta sismica especial | **0.75** | Cap. 15, 18 |

### Valores Tipicos de fce

Para fc' = 4000 psi:

| Tipo de Strut | beta_s | beta_c | fce (psi) |
|---------------|--------|--------|-----------|
| Boundary, sin confinamiento | 1.0 | 1.0 | **3,400** |
| Boundary, con confinamiento | 1.0 | 2.0 | **6,800** |
| Interior con refuerzo | 0.75 | 1.0 | **2,550** |
| Zona de tension | 0.4 | 1.0 | **1,360** |

```
fce = 0.85 * beta_c * beta_s * fc'
```

---

## EJEMPLO DE CALCULO

**Datos:**
- fc' = 4,000 psi
- Strut interior con refuerzo distribuido (Tab. 23.5.1)
- Sin confinamiento especial
- Acs = 100 in²

**Calculo:**
```
beta_s = 0.75 (interior con refuerzo)
beta_c = 1.0 (sin confinamiento)

fce = 0.85 * 1.0 * 0.75 * 4000 = 2,550 psi

Fns = fce * Acs = 2,550 * 100 = 255,000 lb = 255 kips

phi * Fns = 0.75 * 255 = 191 kips
```

---

*ACI 318-25 Secciones 23.3-23.4*
