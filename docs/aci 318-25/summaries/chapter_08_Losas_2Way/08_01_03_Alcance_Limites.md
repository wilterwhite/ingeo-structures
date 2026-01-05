# ACI 318-25 - 8.1-8.3 ALCANCE Y LIMITES DE DISENO

---

## 8.1 ALCANCE

Aplica al diseno de losas no presforzadas y presforzadas reforzadas para flexion en dos direcciones:
- Con o sin vigas entre apoyos
- Con o sin capiteles
- Con o sin abaco (drop panel)

**Nota:** Incluye losas planas, losas con vigas, placas planas y sistemas de viguetas en dos direcciones.

---

## 8.2 GENERAL

### 8.2.1 Consideraciones de Diseño
Considerar efectos de:
- Cargas concentradas
- Aberturas en la losa

### 8.2.2 Vigas de Borde
Los miembros de borde deben diseñarse para resistir el momento total de la franja de losa de borde.

### 8.2.3 Vacios y Aberturas

| Ubicacion | Requisitos |
|-----------|------------|
| Interseccion de bandas de columna | No permitido sin analisis especial |
| Banda central | Permitido si se mantiene resistencia |
| Area comun | No interrumpir refuerzo requerido |

---

## 8.3 LIMITES DE DISENO

### 8.3.1 Espesor Minimo de Losa

#### Tabla 8.3.1.1 - Sin Vigas Interiores (αfm < 0.2)

| Condicion | Sin drop panel | Con drop panel |
|-----------|----------------|----------------|
| **Sin vigas de borde** (αf = 0) | ln/33 | ln/36 |
| **Con vigas de borde** (αf >= 0.8) | ln/33 | ln/36 |
| **Minimo absoluto** | **5 in.** | **4 in.** |

#### Tabla 8.3.1.2 - Con Vigas Interiores (αfm >= 0.2)

| αfm | h minimo |
|-----|----------|
| 0.2 <= αfm < 2.0 | ln*(0.8 + fy/200,000) / (36 + 5β*(αfm - 0.2)) |
| αfm >= 2.0 | ln*(0.8 + fy/200,000) / (36 + 9β) |
| **Minimo absoluto** | **3.5 in.** |

Donde:
- **ln** = luz libre en direccion larga (in.)
- **β** = relacion de luz libre larga a corta
- **αfm** = promedio de αf para vigas en bordes del panel
- **αf** = EcbIb / (EcsIs)

#### 8.3.1.1 Modificacion por fy
Para fy diferente de 60,000 psi, usar factor:
```
Factor = (0.8 + fy/200,000)
```

#### 8.3.1.2 Modificacion por Concreto Liviano
Para wc = 90 a 115 lb/ft³, multiplicar por el **mayor** de:
- (a) **1.65 - 0.005*wc**
- (b) **1.09**

### 8.3.1.3 Requisitos para Drop Panel

Para usar espesores reducidos, el drop panel debe:

| Parametro | Requisito |
|-----------|-----------|
| Extension cada lado | >= **l/6** desde eje de apoyo |
| Proyeccion bajo losa | >= **h/4** (h = espesor losa fuera del drop panel) |

### 8.3.1.4 Requisitos para Vigas de Borde

Para considerar αf >= 0.8:
- Viga debe tener relacion altura/ancho >= 3

---

### 8.3.2 Deflexion Calculada

| Condicion | Requisito |
|-----------|-----------|
| Losas que no cumplen 8.3.1 | Calcular deflexiones segun 24.2 |
| Losas presforzadas | Siempre calcular deflexiones |

---

### 8.3.3 Deformacion del Refuerzo

**8.3.3.1:** Losas no presforzadas deben ser **controladas por tension** segun Tabla 21.2.2.

---

### 8.3.4 Limites de Esfuerzo (Presforzadas)

| Etapa | Referencia |
|-------|------------|
| Clasificacion (U, T, C) | 24.5.2 |
| Esfuerzos inmediatamente despues de transferencia | 24.5.3 |
| Esfuerzos en cargas de servicio | 24.5.4 |

---

## Resumen de Espesores Minimos

| Sistema | h minimo | Condiciones |
|---------|----------|-------------|
| Placa plana | ln/33 >= 5 in. | Sin drop panel |
| Placa plana | ln/36 >= 4 in. | Con drop panel |
| Losa plana con vigas | Variable | Segun Tabla 8.3.1.2 |
| Minimo con vigas (αfm >= 2) | 3.5 in. | - |

---

*ACI 318-25 Secciones 8.1-8.3*
