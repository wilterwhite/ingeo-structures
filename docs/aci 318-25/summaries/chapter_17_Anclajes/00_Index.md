# ACI 318-25 - CAPITULO 17: ANCLAJES AL CONCRETO

## Indice de Subcapitulos

| Archivo | Subcapitulo | Descripcion |
|---------|-------------|-------------|
| [17_01_Alcance.md](17_01_Alcance.md) | 17.1 | Alcance y tipos de anclajes |
| [17_02_General.md](17_02_General.md) | 17.2 | Requisitos de calificacion y materiales |
| [17_03_Requisitos_Diseno.md](17_03_Requisitos_Diseno.md) | 17.3 | Requisitos generales de diseno |
| [17_04_Resistencia_Diseno.md](17_04_Resistencia_Diseno.md) | 17.4 | Factores de reduccion de resistencia |
| [17_05_Requisitos_Analisis.md](17_05_Requisitos_Analisis.md) | 17.5 | Suposiciones de diseno y analisis |
| [17_06_Resistencia_Tension.md](17_06_Resistencia_Tension.md) | 17.6 | Resistencia a tension de anclajes |
| [17_07_Resistencia_Cortante.md](17_07_Resistencia_Cortante.md) | 17.7 | Resistencia a cortante de anclajes |
| [17_08_Interaccion.md](17_08_Interaccion.md) | 17.8 | Interaccion tension-cortante |
| [17_09_Splitting.md](17_09_Splitting.md) | 17.9 | Splitting (hendimiento) |
| [17_10_Sismico.md](17_10_Sismico.md) | 17.10 | Requisitos sismicos para anclajes |
| [17_11_Adhesivos.md](17_11_Adhesivos.md) | 17.11 | Anclajes adhesivos - detallado |
| [17_12_Instalacion.md](17_12_Instalacion.md) | 17.12 | Instalacion de anclajes |
| [17_13_Especiales.md](17_13_Especiales.md) | 17.13 | Requisitos especiales |
| [17_Referencias.md](17_Referencias.md) | Refs | Variables, factores y referencias |

---

## Resumen del Capitulo

El Capitulo 17 cubre el diseno de anclajes al concreto:

- **17.1-17.5**: Alcance, materiales, requisitos generales
- **17.6**: Resistencia a tension
- **17.7**: Resistencia a cortante
- **17.8**: Interaccion tension-cortante
- **17.9**: Splitting
- **17.10**: Requisitos sismicos
- **17.11-17.13**: Adhesivos, instalacion, especiales

---

## Modos de Falla

### Tension

| Modo | Formula | Seccion |
|------|---------|---------|
| Acero | Nsa = Ase,N * futa | 17.6.1 |
| Breakout | Ncb = (ANc/ANco) * ψed,N * ψc,N * ψcp,N * Nb | 17.6.2 |
| Pullout | Npn = ψc,P * Np | 17.6.3 |
| Side-face blowout | Nsb = 160 * ca1 * √Abrg * λa * √f'c | 17.6.4 |
| Adherencia | Na = (ANa/ANao) * ψed,Na * ψcp,Na * Nba | 17.6.5 |

### Cortante

| Modo | Formula | Seccion |
|------|---------|---------|
| Acero | Vsa = 0.6 * Ase,V * futa | 17.7.1 |
| Breakout | Vcb = (AVc/AVco) * ψed,V * ψc,V * ψh,V * Vb | 17.7.2 |
| Pryout | Vcp = kcp * Ncp | 17.7.3 |

---

## Formulas Principales

### Breakout en Tension (17.6.2)

**Resistencia basica:**
```
Nb = kc * λa * √f'c * hef^1.5     (hef <= 11 in)
Nb = 16 * λa * √f'c * hef^(5/3)   (hef > 11 in)
```

**Areas proyectadas:**
```
ANco = 9 * hef²
```

| Factor | Condicion | Valor |
|--------|-----------|-------|
| kc | Colados | 24 |
| ψed,N | ca,min >= 1.5*hef | 1.0 |
| ψed,N | ca,min < 1.5*hef | 0.7 + 0.3*(ca,min/(1.5*hef)) |
| ψc,N | Fisurado | 1.0 |
| ψc,N | No fisurado | 1.25 |

### Pullout (17.6.3)

```
Np = 8 * Abrg * f'c    (cabeza/tuerca)
Np = 0.9 * f'c * eh * da  (gancho J/L)
```

### Breakout en Cortante (17.7.2)

**Resistencia basica:**
```
Vb = 7 * (le/da)^0.2 * √da * λa * √f'c * ca1^1.5
Vb = 9 * λa * √f'c * ca1^1.5   (simplificada, le >= 8*da)
```

**Areas proyectadas:**
```
AVco = 4.5 * ca1²
```

| Factor | Condicion | Valor |
|--------|-----------|-------|
| ψed,V | ca2 >= 1.5*ca1 | 1.0 |
| ψed,V | ca2 < 1.5*ca1 | 0.7 + 0.3*(ca2/(1.5*ca1)) |
| ψc,V | Fisurado sin refuerzo | 1.0 |
| ψc,V | Fisurado con refuerzo | 1.2 |
| ψc,V | No fisurado | 1.4 |
| ψh,V | ha >= 1.5*ca1 | 1.0 |
| ψh,V | ha < 1.5*ca1 | √(1.5*ca1/ha) |
| kcp | hef < 2.5 in | 1.0 |
| kcp | hef >= 2.5 in | 2.0 |

### Interaccion (17.8)

```
Si Vua > 0.2*φVn Y Nua > 0.2*φNn:
  Nua/(φNn) + Vua/(φVn) <= 1.2   (trilineal)
  (Nua/(φNn))^(5/3) + (Vua/(φVn))^(5/3) <= 1.0   (eliptica)
```

---

## Factores de Reduccion φ

### Cargas Estaticas (17.4)

| Modo | Ductil | No Ductil |
|------|--------|-----------|
| Tension - acero | 0.75 | 0.65 |
| Tension - concreto (sin ref.) | 0.70 | 0.70 |
| Tension - concreto (con ref.) | 0.75 | 0.75 |
| Cortante - acero | 0.65 | 0.60 |
| Cortante - concreto (sin ref.) | 0.70 | 0.70 |
| Cortante - concreto (con ref.) | 0.75 | 0.75 |

### Cargas Sismicas - SDC C, D, E, F (17.10.6)

| Modo | Sin Ref. Suplementario | Con Ref. Suplementario |
|------|------------------------|------------------------|
| Tension - concreto | 0.70 | 0.75 |
| Cortante - concreto | 0.70 | 0.75 |

---

## Requisitos Sismicos (17.10)

### Aplicabilidad
- SDC C, D, E, F
- Anclajes que resisten cargas sismicas

### Ductilidad
```
φNn,acero <= φNn,concreto
φVn,acero <= φVn,concreto
```

### Grupos (SDC D, E, F)
- Minimo 4 anclajes
- Minimo 2 en cada direccion

---

## Distancias Minimas (17.9)

| Tipo | ca,min | s,min |
|------|--------|-------|
| Colados | Segun recubrimiento | 4*da |
| Post-instalados | 6*da | 6*da |
| Adhesivos | Segun informe | Segun informe |

---

*ACI 318-25 Capitulo 17 - Indice*
