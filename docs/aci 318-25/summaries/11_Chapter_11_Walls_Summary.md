# ACI 318-25 - CAPITULO 11: MUROS

---

## INDICE

- [11.1 Alcance](#111-alcance)
- [11.2 General](#112-general)
- [11.3 Limites de Diseno](#113-limites-de-diseno)
- [11.4 Resistencia Requerida](#114-resistencia-requerida)
- [11.5 Resistencia de Diseno](#115-resistencia-de-diseno)
  - [11.5.3 Metodo Simplificado](#1153-metodo-simplificado-carga-axial--flexion-fuera-del-plano)
  - [11.5.4 Cortante en el Plano](#1154-cortante-en-el-plano)
- [11.6 Limites de Refuerzo](#116-limites-de-refuerzo)
- [11.7 Detallado de Refuerzo](#117-detallado-de-refuerzo)
- [11.8 Metodo Alternativo para Muros Esbeltos](#118-metodo-alternativo-para-muros-esbeltos)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 11.1 ALCANCE

### 11.1.1 Aplicabilidad
Aplica al diseno de muros no pretensados y pretensados, incluyendo:
- (a) Colados en sitio
- (b) Prefabricados en planta
- (c) Prefabricados en sitio (tilt-up)

### Referencias a Otros Capitulos

| Tipo de Muro | Capitulo |
|--------------|----------|
| Muros estructurales especiales | 18 |
| Muros de concreto simple | 14 |
| Muros de retencion en voladizo | 13 |

---

## 11.2 GENERAL

### 11.2.3 Distribucion de Cargas
Longitud efectiva horizontal para cargas concentradas (la menor de):
- Distancia centro a centro entre cargas
- Ancho de apoyo + 4h

### 11.2.4.2 Muros con Pu > 0.2*f'c*Ag
La porcion del muro dentro del sistema de piso debe tener f'c >= 0.8*f'c del muro.

---

## 11.3 LIMITES DE DISENO

### Tabla 11.3.1.1 - Espesor Minimo h

| Tipo de Muro | Espesor Minimo |
|--------------|----------------|
| De carga | Mayor de: 4 in, 1/25*(menor de lu o lw) |
| Sin carga | Mayor de: 4 in, 1/30*(menor de lu o lw) |
| Sotano exterior y cimentacion | 7.5 in |

---

## 11.4 RESISTENCIA REQUERIDA

### 11.4.1.3 Efectos de Esbeltez
Calcular segun:
- 6.6.4 (Magnificacion de momentos)
- 6.7 (Analisis de segundo orden)
- **11.8** (Metodo alternativo para muros esbeltos)

---

## 11.5 RESISTENCIA DE DISENO

### 11.5.1 General
Para cada combinacion de carga:
```
phi*Pn >= Pu
phi*Mn >= Mu
phi*Vn >= Vu
```

### 11.5.3 METODO SIMPLIFICADO (Carga Axial + Flexion Fuera del Plano)

#### 11.5.3.1 Condicion de Aplicabilidad
Resultante de cargas factoradas dentro del **tercio medio** del espesor (e <= h/6).

#### Ecuacion de Resistencia Nominal
```
Pn = 0.55 * f'c * Ag * [1 - (k*lc / 32h)^2]     [Ec. 11.5.3.1]
```

#### Tabla 11.5.3.2 - Factor de Longitud Efectiva k

| Condiciones de Borde | k |
|---------------------|---|
| Arriostrado, restringido rotacion | **0.8** |
| Arriostrado, sin restriccion rotacion | **1.0** |
| No arriostrado | **2.0** |

---

### 11.5.4 CORTANTE EN EL PLANO

#### 11.5.4.2 Limite Maximo
```
Vn <= 8 * sqrt(f'c) * Acv
```

#### 11.5.4.3 Resistencia Nominal
```
Vn = (alpha_c * lambda * sqrt(f'c) + rho_t * fyt) * Acv     [Ec. 11.5.4.3]
```

#### Coeficiente alpha_c

| hw/lw | alpha_c |
|-------|---------|
| <= 1.5 | 3 |
| >= 2.0 | 2 |
| 1.5 < hw/lw < 2.0 | Interpolacion lineal |

#### 11.5.4.4 Muros con Tension Axial Neta
```
alpha_c = 2 * (1 + Nu / (500 * Ag)) >= 0     [Ec. 11.5.4.4]
```
Nu es negativo para tension.

### 11.5.5 Cortante Fuera del Plano
Vn segun 22.5 (como losa unidireccional).

---

## 11.6 LIMITES DE REFUERZO

### 11.6.1 Refuerzo Minimo (Cortante Bajo)
**Condicion**: Vu <= 0.5 * phi * alpha_c * lambda * sqrt(f'c) * Acv

#### Tabla 11.6.1 - Cuantias Minimas

| Tipo | Barra | fy (psi) | rho_l min | rho_t min |
|------|-------|----------|-----------|-----------|
| Colado en sitio | <= No. 5 | >= 60,000 | 0.0012 | 0.0020 |
| Colado en sitio | <= No. 5 | < 60,000 | 0.0015 | 0.0025 |
| Colado en sitio | > No. 5 | Cualquiera | 0.0015 | 0.0025 |
| Prefabricado | Cualquiera | Cualquiera | 0.0010 | 0.0010 |

### 11.6.2 Refuerzo Minimo (Cortante Alto)
**Condicion**: Vu > 0.5 * phi * alpha_c * lambda * sqrt(f'c) * Acv

**(a) Refuerzo Longitudinal:**
```
rho_l >= 0.0025 + 0.5 * (2.5 - hw/lw) * (rho_t - 0.0025)     [Ec. 11.6.2]
```
- Minimo: **0.0025**

**(b) Refuerzo Transversal:**
- Minimo: **0.0025**

---

## 11.7 DETALLADO DE REFUERZO

### 11.7.2 Espaciamiento de Refuerzo Longitudinal

| Tipo | Espaciamiento Maximo |
|------|---------------------|
| Colado en sitio (general) | Menor de: 3h, 18 in |
| Colado en sitio (cortante) | No exceder lw/3 |
| Prefabricado (general) | Menor de: 5h, 18 in (ext) o 30 in (int) |

### 11.7.2.3 Doble Cortina de Refuerzo
Muros con espesor > 10 in: refuerzo en **dos cortinas**.

### 11.7.3 Espaciamiento de Refuerzo Transversal

| Tipo | Espaciamiento Maximo |
|------|---------------------|
| Colado en sitio (general) | Menor de: 3h, 18 in |
| Colado en sitio (cortante) | No exceder lw/5 |
| Prefabricado (general) | Menor de: 5h, 18 in (ext) o 30 in (int) |

### 11.7.5 Soporte Lateral del Refuerzo Longitudinal
Si Ast > 0.01*Ag: refuerzo longitudinal debe tener soporte lateral con estribos.

### 11.7.6 Refuerzo Alrededor de Aberturas
| Cortinas | Refuerzo Adicional |
|----------|-------------------|
| Dos cortinas | Al menos 2 barras No. 5 |
| Una cortina | Al menos 1 barra No. 5 |

Desarrollar fy en tension en esquinas de aberturas.

---

## 11.8 METODO ALTERNATIVO PARA MUROS ESBELTOS

### 11.8.1 Condiciones de Aplicabilidad

| Condicion | Requisito |
|-----------|-----------|
| (a) Seccion | Constante en toda la altura |
| (b) Comportamiento | Controlado por tension |
| (c) Resistencia | phi*Mn >= Mcr |
| (d) Carga axial | Pu <= 0.06*f'c*Ag (a media altura) |
| (e) Deflexion | <= lc/150 (cargas de servicio) |

### 11.8.3 Momento Factorado

#### Metodo (a) - Iterativo
```
Mu = Mua + Pu * Delta_u     [Ec. 11.8.3.1a]

Delta_u = (5 * Mu * lc^2) / (0.75 * 48 * Ec * Icr)     [Ec. 11.8.3.1b]
```

#### Metodo (b) - Directo
```
Mu = Mua / (1 - (5 * Pu * lc^2) / (0.75 * 48 * Ec * Icr))     [Ec. 11.8.3.1d]
```

#### Inercia Agrietada
```
Icr = (Es/Ec) * Ase,w * (d - c)^2 + (lw * c^3) / 3     [Ec. 11.8.3.1c]
```
- Es/Ec debe ser al menos **6**
- Ase,w = As + (Pu/fy) * (h/2) / d

### 11.8.4 Deflexion de Servicio

#### Tabla 11.8.4.1 - Calculo de Delta_s

| Condicion | Formula |
|-----------|---------|
| Ma <= (2/3)*Mcr | Delta_s = (Ma/Mcr) * Delta_cr |
| Ma > (2/3)*Mcr | Interpolacion entre Delta_cr y Delta_n |

#### Deflexiones de Referencia
```
Delta_cr = (5 * Mcr * lc^2) / (48 * Ec * Ig)     [Ec. 11.8.4.3a]
Delta_n = (5 * Mn * lc^2) / (48 * Ec * Icr)      [Ec. 11.8.4.3b]
```

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Propiedades del concreto | Capitulo 19 |
| Propiedades del acero | Capitulo 20 |
| Factores phi | 21.2 |
| Resistencia Pn,max | 22.4.2.1 |
| Flexion Mn | 22.3, 22.4 |
| Cortante Vn (fuera del plano) | 22.5 |
| Metodo puntal-tensor | Capitulo 23 |
| Longitudes de desarrollo | 25.4 |
| Longitudes de empalme | 25.5 |
| Muros estructurales especiales | Capitulo 18 |

---

*Resumen del ACI 318-25 Capitulo 11 para diseno de muros.*
*Fecha: 2025*
