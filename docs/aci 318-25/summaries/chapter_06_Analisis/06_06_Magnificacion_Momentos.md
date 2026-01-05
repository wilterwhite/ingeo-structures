# ACI 318-25 - 6.6 ANALISIS 1ER ORDEN Y MAGNIFICACION

---

## 6.6.3 Propiedades de Seccion

### Tabla 6.6.3.1.1(a) - Momentos de Inercia para Cargas Factoradas

| Miembro | Momento de Inercia | Area Axial | Area Cortante |
|---------|-------------------|------------|---------------|
| Columnas | **0.70*Ig** | 1.0*Ag | 1.0*Ashear |
| Muros (no fisurados) | **0.70*Ig** | 1.0*Ag | 1.0*Ashear |
| Muros (fisurados) | **0.35*Ig** | 1.0*Ag | 1.0*Ashear |
| Vigas | **0.35*Ig** | 1.0*Ag | 1.0*Ashear |
| Losas planas | **0.25*Ig** | 1.0*Ag | 1.0*Ashear |

**Notas:**
- Si hay cargas laterales sostenidas, dividir I de columnas y muros por (1 + beta_ds).
- Para secciones rectangulares: **Ashear <= 5/6*Ag**
- Modulo de corte: **G = 0.4*Ec**

### Tabla 6.6.3.1.1(b) - Momentos de Inercia Alternativos

| Miembro | Minimo | Formula | Maximo |
|---------|--------|---------|--------|
| Columnas y muros | 0.35*Ig | (0.80 + 25*Ast/Ag)*(1 - Mu/(Pu*h) - 0.5*Pu/Po)*Ig | 0.875*Ig |
| Vigas, losas | 0.25*Ig | (0.10 + 25*rho)*(1.2 - 0.2*bw/d)*Ig | 0.5*Ig |

### 6.6.3.1.2 Deflexiones bajo Cargas Laterales Factoradas

Si se espera respuesta inelastica, calcular rigidez efectiva segun:

| Opcion | Metodo |
|--------|--------|
| **(a)** | Propiedades de Tabla 6.6.3.1.1(a) |
| **(b)** | **I = 0.5*Ig** para todos los miembros |
| **(c)** | Analisis mas detallado considerando condiciones de carga |

**Nota:** Para losas 2-way sin vigas en SFRS, usar modelo validado con ensayos.

### 6.6.3.2.2 Analisis en Servicio
```
I_servicio = 1.4 * I_factorado    (pero <= Ig)
```

---

## 6.6.4 METODO DE MAGNIFICACION DE MOMENTOS

### 6.6.4.3 Clasificacion Nonsway/Sway

| Criterio | Condicion para Nonsway |
|----------|------------------------|
| **(a)** Incremento de momentos | Efectos 2do orden <= 5% de momentos 1er orden |
| **(b)** Indice de estabilidad | Q <= 0.05 |

### 6.6.4.4 Propiedades de Estabilidad

#### 6.6.4.4.1 Indice de Estabilidad Q
```
Q = (Sum Pu * Delta_o) / (Vus * lc)
```

Donde:
- Sum Pu = carga vertical factorada total del piso
- Vus = cortante horizontal del piso
- Delta_o = deriva de 1er orden
- lc = altura de piso

#### 6.6.4.4.2 Carga Critica de Pandeo
```
Pc = pi² * (EI)eff / (k*lu)²
```

#### 6.6.4.4.4 Rigidez Efectiva (EI)eff

| Ecuacion | Formula | Uso |
|----------|---------|-----|
| **(a)** | (EI)eff = 0.4*Ec*Ig / (1 + beta_dns) | Simplificada |
| **(b)** | (EI)eff = (0.2*Ec*Ig + Es*Ise) / (1 + beta_dns) | Con refuerzo |
| **(c)** | (EI)eff = Ec*I / (1 + beta_dns) | Usando Tabla 6.6.3.1.1(b) |

**Nota:** beta_dns = carga axial sostenida maxima / carga axial maxima (misma combinacion).

**Simplificacion:** Si beta_dns = 0.6, entonces (EI)eff = 0.25*Ec*Ig

---

## 6.6.4.5 Marcos Nonsway (Arriostrados)

### 6.6.4.5.1 Momento de Diseno
```
Mc = delta * M2
```

### 6.6.4.5.2 Factor de Magnificacion
```
delta = Cm / (1 - Pu/(0.75*Pc)) >= 1.0
```

### 6.6.4.5.3 Factor Cm

| Condicion | Cm |
|-----------|-----|
| Sin cargas transversales entre apoyos | Cm = 0.6 - 0.4*(M1/M2) |
| Con cargas transversales entre apoyos | Cm = 1.0 |

**Convencion:** M1/M2 negativo (curvatura simple), positivo (curvatura doble).

### 6.6.4.5.4 Momento Minimo
```
M2,min = Pu * (0.6 + 0.03*h)
```
Donde h esta en pulgadas y M2,min en lb-in.

---

## 6.6.4.6 Marcos Sway (No Arriostrados)

### 6.6.4.6.1 Momentos en Extremos de Columna
```
M1 = M1ns + delta_s * M1s
M2 = M2ns + delta_s * M2s
```

Donde:
- M1ns, M2ns = momentos de cargas que no causan desplazamiento lateral
- M1s, M2s = momentos de cargas que causan desplazamiento lateral

### 6.6.4.6.2 Factor de Magnificacion delta_s

| Metodo | Formula | Limite |
|--------|---------|--------|
| **(a)** Metodo Q | delta_s = 1/(1-Q) >= 1 | Solo si delta_s <= 1.5 |
| **(b)** Suma de P | delta_s = 1/(1 - Sum Pu/(0.75*Sum Pc)) >= 1 | Siempre permitido |
| **(c)** Analisis 2do orden | Por analisis | Siempre permitido |

**Nota:** Si delta_s > 1.5, solo se permiten metodos (b) o (c).

---

## 6.6.5 REDISTRIBUCION DE MOMENTOS

### 6.6.5.1 Condiciones
Se permite reducir momentos en secciones de momento maximo si:
- (a) Miembros a flexion son continuos
- (b) epsilon_t >= **0.0075** en la seccion donde se reduce el momento

### 6.6.5.3 Limite de Redistribucion
```
Redistribucion maxima = menor de (1000*epsilon_t)% y 20%
```

### Excepciones (NO se permite redistribucion)
- Momentos aproximados (6.5)
- Analisis inelastico (6.8)
- Patrones de carga de losas 2-way (6.4.3.3)

---

*ACI 318-25 Seccion 6.6*
