# 17.6 RESISTENCIA A TENSION DE ANCLAJES

## 17.6.1 Resistencia del Acero en Tension

**Ecuacion:**
```
Nsa = Ase,N * futa     [Ec. 17.6.1.2]
```

**Limites:**
- futa <= menor de: 1.9*fya, 125,000 psi

**Tabla 17.6.1.2 - Area de Seccion Efectiva (Ase,N)**

| Tipo de Anclaje | Ase,N |
|-----------------|-------|
| Perno con cabeza | Area de la parte roscada |
| Barra roscada | 0.7854*(d - 0.9743/n)^2 |
| Conectores AWS Tipo B | Area del vastago |

---

## 17.6.2 Resistencia al Desprendimiento del Concreto (Breakout) en Tension

**17.6.2.1 Anclaje Individual:**
```
Ncb = (ANc / ANco) * psi_ed,N * psi_c,N * psi_cp,N * Nb     [Ec. 17.6.2.1a]
```

**17.6.2.2 Grupo de Anclajes:**
```
Ncbg = (ANc / ANco) * psi_ec,N * psi_ed,N * psi_c,N * psi_cp,N * Nb     [Ec. 17.6.2.1b]
```

### 17.6.2.2 Area Proyectada de Falla

**ANco** (area de un anclaje sin efectos de borde o espaciamiento):
```
ANco = 9 * hef^2     [Ec. 17.6.2.2.1]
```

**ANc**: Area real proyectada, limitada por:
- Bordes
- Espaciamiento
- Espesor del miembro

### 17.6.2.3 Resistencia Basica al Desprendimiento

**Anclajes colados y post-instalados (Categoria 1):**
```
Nb = kc * lambda_a * sqrt(f'c) * hef^1.5     [Ec. 17.6.2.3.1]
```

| Tipo | kc |
|------|-----|
| Colados en sitio | 24 |
| Post-instalados | Segun informe de calificacion |

**Para hef > 11 in (Categoria 2):**
```
Nb = 16 * lambda_a * sqrt(f'c) * hef^(5/3)     [Ec. 17.6.2.3.2]
```

### Tabla 17.6.2.4 - Factores de Modificacion para Breakout en Tension

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_ec,N** (excentricidad) | Carga excentrica en grupo | 1 / (1 + 2*e'N / (3*hef)) <= 1.0 |
| | Carga concentrica | 1.0 |
| **psi_ed,N** (borde) | ca,min >= 1.5*hef | 1.0 |
| | ca,min < 1.5*hef | 0.7 + 0.3*(ca,min / (1.5*hef)) |
| **psi_c,N** (fisuracion) | Concreto fisurado | 1.0 |
| | Concreto no fisurado | 1.25 (colados), segun informe (post-instalados) |
| **psi_cp,N** (splitting post-instalados) | ca,min >= cac | 1.0 |
| | ca,min < cac | ca,min / cac >= (1.5*hef / cac) |

---

## 17.6.3 Resistencia al Arrancamiento (Pullout) en Tension

**17.6.3.1 Anclaje Individual:**
```
Npn = psi_c,P * Np     [Ec. 17.6.3.1]
```

### Tabla 17.6.3.2.2 - Resistencia Basica al Arrancamiento

| Tipo de Anclaje | Np |
|-----------------|-----|
| Perno con cabeza | 8 * Abrg * f'c |
| Perno con tuerca | 8 * Abrg * f'c |
| Gancho en J o L | 0.9 * f'c * eh * da |
| Post-instalado | Segun informe de calificacion |

**Limites para ganchos:**
- 3*da <= eh <= 4.5*da

### Tabla 17.6.3.3 - Factor de Modificacion psi_c,P

| Condicion | psi_c,P |
|-----------|---------|
| Concreto fisurado | 1.0 |
| Concreto no fisurado | 1.4 |

---

## 17.6.4 Resistencia al Desprendimiento Lateral (Side-Face Blowout)

**Aplica cuando:** hef > 2.5*ca1

**17.6.4.1 Anclaje Individual:**
```
Nsb = 160 * ca1 * sqrt(Abrg) * lambda_a * sqrt(f'c)     [Ec. 17.6.4.1]
```

**Si ca2 < 3*ca1:**
```
Nsb = (1 + ca2 / ca1) / 4 * 160 * ca1 * sqrt(Abrg) * lambda_a * sqrt(f'c)
```

**17.6.4.2 Grupo de Anclajes:**
```
Nsbg = (1 + s / (6*ca1)) * Nsb     [Ec. 17.6.4.2]
```
donde s = espaciamiento del anclaje externo al borde

---

## 17.6.5 Resistencia de Adherencia para Anclajes Adhesivos

**17.6.5.1 Anclaje Individual:**
```
Na = (ANa / ANao) * psi_ed,Na * psi_cp,Na * Nba     [Ec. 17.6.5.1a]
```

**17.6.5.2 Grupo de Anclajes:**
```
Nag = (ANa / ANao) * psi_ec,Na * psi_ed,Na * psi_cp,Na * Nba     [Ec. 17.6.5.1b]
```

### 17.6.5.2 Areas Proyectadas

**ANao:**
```
ANao = (2*cNa)^2     [Ec. 17.6.5.2.1]
```

**Radio de influencia critico:**
```
cNa = 10*da * (tau_uncr / 1100)^0.5     [Ec. 17.6.5.2.2]
```

### 17.6.5.3 Resistencia Basica de Adherencia

```
Nba = lambda_a * tau_cr * pi * da * hef     [Ec. 17.6.5.3.1]
```

**tau_cr**: Esfuerzo de adherencia caracteristico (del informe de calificacion)

### Tabla 17.6.5.4 - Factores de Modificacion para Adhesivos

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_ec,Na** | Carga excentrica | 1 / (1 + e'N / cNa) <= 1.0 |
| **psi_ed,Na** | ca,min >= cNa | 1.0 |
| | ca,min < cNa | 0.7 + 0.3*(ca,min / cNa) |
| **psi_cp,Na** | ca,min >= cac | 1.0 |
| | ca,min < cac | ca,min / cac |

---

*ACI 318-25 Seccion 17.6*
