# ACI 318-25 - 25.4 LONGITUD DE DESARROLLO

---

## 25.4.1 General
La longitud de desarrollo debe proveerse donde sea requerido por analisis.

---

## 25.4.2 Desarrollo de Barras Corrugadas en Tension

**Ecuacion General:**
```
ld = (fy*psi_t*psi_e*psi_s*psi_g / (25*lambda*sqrt(f'c))) * db
```

**Ecuacion Simplificada (Si cumple condiciones de espaciamiento y recubrimiento):**
```
ld = (fy*psi_t*psi_e / (20*lambda*sqrt(f'c))) * db
```

### Tabla 25.4.2.5 - Factores de Modificacion

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_t** (ubicacion) | Mas de 12 in de concreto debajo | 1.3 |
| | Otros casos | 1.0 |
| **psi_e** (epoxico) | Recubrimiento < 3*db o espaciamiento < 6*db | 1.5 |
| | Otros casos epoxico | 1.2 |
| | Sin recubrimiento epoxico | 1.0 |
| **psi_s** (tamano) | No. 6 o menor | 0.8 |
| | No. 7 o mayor | 1.0 |
| **psi_g** (grado) | Grado 60 | 1.0 |
| | Grado 80 | 1.15 |
| | Grado 100 | 1.3 |
| **lambda** | Concreto peso normal | 1.0 |
| | Concreto liviano | Ver 19.2.4 |

**Limites:**
- psi_t * psi_e <= 1.7
- ld,min >= 12 in

---

## 25.4.3 Desarrollo de Ganchos Estandar en Tension

**Ecuacion:**
```
ldh = (fy*psi_e*psi_r*psi_o*psi_c*psi_g / (55*lambda*sqrt(f'c))) * db
```

### Tabla 25.4.3.2 - Factores para Ganchos

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_r** (confinamiento) | Gancho en esquina interior de columna | 0.8 |
| | Otros casos | 1.0 |
| **psi_o** (confinamiento) | Refuerzo perpendicular dentro del gancho | 0.8 |
| | Otros casos | 1.0 |
| **psi_c** (recubrimiento) | Recubrimiento lateral >= 2.5 in (cola gancho) | 0.8 |
| | Recubrimiento >= 2 in (cola de gancho 180 grados) | 0.8 |
| | Otros casos | 1.0 |

**Limites:**
- ldh,min >= mayor de 8*db, 6 in

---

## 25.4.4 Desarrollo de Barras con Cabeza en Tension

**Ecuacion:**
```
ldt = (fy*psi_e*psi_p*psi_o*psi_g / (22*lambda*sqrt(f'c))) * db
```

**Requisitos:**
- Area neta de apoyo de cabeza Abrg >= 4*Ab
- Recubrimiento libre >= db
- Espaciamiento libre >= 2*db

**Limites:**
- ldt,min >= mayor de 8*db, 6 in

---

## 25.4.9 Desarrollo de Barras Corrugadas en Compresion

**Ecuacion:**
```
ldc = (fy*psi_r*psi_g / (50*lambda*sqrt(f'c))) * db >= 0.0003*fy*db
```

| Factor | Condicion | Valor |
|--------|-----------|-------|
| **psi_r** | Confinado con espirales o estribos | 0.75 |
| | Otros casos | 1.0 |

**Limite:** ldc,min >= 8 in

---

*ACI 318-25 Seccion 25.4*
