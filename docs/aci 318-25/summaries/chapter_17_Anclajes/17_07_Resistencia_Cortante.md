# 17.7 RESISTENCIA A CORTANTE DE ANCLAJES

## 17.7.1 Resistencia del Acero en Cortante

**17.7.1.1 Anclaje Individual o Grupo (acero gobierna):**
```
Vsa = Ase,V * futa     [Ec. 17.7.1.2a] (anclajes colados con manga)
Vsa = 0.6 * Ase,V * futa     [Ec. 17.7.1.2b] (anclajes colados sin manga)
Vsa = 0.6 * Ase,V * futa     [Ec. 17.7.1.2c] (anclajes post-instalados)
```

**Limites:**
- futa <= menor de: 1.9*fya, 125,000 psi

**17.7.1.3** Efecto de brazo de palanca:
Si el cortante actua con brazo de palanca (ej: grout bajo placa):
```
Vsa = (Ase,V * futa) / (1 + l_g / (2*hef))
```
donde l_g = espesor del grout

### Tabla 17.7.1.2 - Area de Seccion Efectiva en Cortante (Ase,V)

| Tipo de Anclaje | Ase,V |
|-----------------|-------|
| Perno con cabeza | Area de la parte roscada |
| Barra roscada | 0.7854*(d - 0.9743/n)^2 |
| Conectores AWS Tipo B | Area del vastago |

---

## 17.7.2 Resistencia al Desprendimiento del Concreto (Breakout) en Cortante

**17.7.2.1 Anclaje Individual:**
```
Vcb = (AVc / AVco) * psi_ed,V * psi_c,V * psi_h,V * Vb     [Ec. 17.7.2.1a]
```

**17.7.2.2 Grupo de Anclajes:**
```
Vcbg = (AVc / AVco) * psi_ec,V * psi_ed,V * psi_c,V * psi_h,V * Vb     [Ec. 17.7.2.1b]
```

### 17.7.2.2 Areas Proyectadas de Falla en Cortante

**AVco** (area de un anclaje sin efectos de borde, esquina o espesor):
```
AVco = 4.5 * ca1^2     [Ec. 17.7.2.2.1]
```

**AVc**: Area real proyectada, limitada por:
- Bordes perpendiculares (1.5*ca1 a cada lado)
- Espesor del miembro (1.5*ca1)
- Espaciamiento entre anclajes

### 17.7.2.3 Resistencia Basica al Desprendimiento en Cortante

**Ecuacion General:**
```
Vb = (7 * (le/da)^0.2 * sqrt(da)) * lambda_a * sqrt(f'c) * ca1^1.5     [Ec. 17.7.2.3.1a]
```

**Ecuacion Simplificada (cuando le >= 8*da):**
```
Vb = 9 * lambda_a * sqrt(f'c) * ca1^1.5     [Ec. 17.7.2.3.1b]
```

**Limites:**
- le <= hef (anclajes de expansion y undercut)
- le <= 8*da

### Tabla 17.7.2.4 - Factores de Modificacion para Breakout en Cortante

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_ec,V** (excentricidad) | Carga excentrica en grupo | 1 / (1 + 2*e'V / (3*ca1)) <= 1.0 |
| | Carga concentrica | 1.0 |
| **psi_ed,V** (borde) | ca2 >= 1.5*ca1 | 1.0 |
| | ca2 < 1.5*ca1 | 0.7 + 0.3*(ca2 / (1.5*ca1)) |
| **psi_c,V** (fisuracion) | Concreto fisurado, sin refuerzo de borde | 1.0 |
| | Concreto fisurado, con refuerzo No. 4+ | 1.2 |
| | Concreto fisurado, con refuerzo y estribos s <= 4 in | 1.4 |
| | Concreto no fisurado | 1.4 |
| **psi_h,V** (espesor) | ha >= 1.5*ca1 | 1.0 |
| | ha < 1.5*ca1 | sqrt(1.5*ca1 / ha) |

### 17.7.2.5 Cortante Paralelo al Borde

Si cortante actua paralelo al borde:
```
Vcb,parallel = 2 * Vcb     [Ec. 17.7.2.5.1]
```

Para cortante en angulo con el borde, resolver componentes.

### 17.7.2.6 Anclajes en Esquinas

Para anclajes cerca de dos bordes perpendiculares:
- Calcular Vcb para cada borde
- Usar el **menor** de los dos valores

---

## 17.7.3 Resistencia al Desprendimiento Posterior (Pryout) en Cortante

**17.7.3.1** Aplica a anclajes alejados del borde donde pryout puede gobernar

**Anclaje Individual:**
```
Vcp = kcp * Ncp     [Ec. 17.7.3.1a]
```

**Grupo de Anclajes:**
```
Vcpg = kcp * Ncpg     [Ec. 17.7.3.1b]
```

### Tabla 17.7.3.1 - Factor kcp

| Profundidad Efectiva | kcp |
|---------------------|-----|
| hef < 2.5 in | 1.0 |
| hef >= 2.5 in | 2.0 |

**Donde:**
- Ncp = Ncb para anclaje individual (desprendimiento en tension)
- Ncpg = Ncbg para grupo de anclajes

---

*ACI 318-25 Seccion 17.7*
