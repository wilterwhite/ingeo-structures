# ACI 318-25 - 6.3-6.4 MODELADO Y DISPOSICION DE CARGA

---

## 6.3 SUPUESTOS DE MODELADO

### 6.3.1 General

#### 6.3.1.1 Rigideces
Las rigideces de miembros deben basarse en un conjunto razonable de supuestos, **consistentes** en todo el analisis.

#### 6.3.1.2 Modelo Simplificado para Gravedad
Para momentos y cortantes por cargas gravitacionales:
- Usar modelo limitado al nivel considerado
- Incluir columnas arriba y abajo
- Extremos lejanos de columnas: **empotrados**

### 6.3.2 Geometria de Vigas T

#### Tabla 6.3.2.1 - Ancho Efectivo de Ala

| Ubicacion del Ala | Ancho Efectivo (mas alla de cara del alma) |
|-------------------|-------------------------------------------|
| **Ambos lados** | Menor de: 8h, sw/2, ln/8 |
| **Un lado** | Menor de: 6h, sw/2, ln/12 |

Donde:
- h = espesor de losa
- sw = distancia libre al alma adyacente
- ln = luz libre

#### 6.3.2.2 Vigas T Aisladas
- Espesor de ala >= **0.5*bw**
- Ancho efectivo de ala <= **4*bw**

---

## 6.4 DISPOSICION DE CARGA VIVA

### 6.4.1 General
Para diseno de pisos/techos: carga viva solo en el nivel considerado.

### 6.4.2 Losas Unidireccionales y Vigas

| Condicion | Ubicacion de L factorada |
|-----------|--------------------------|
| **(a)** Mu+ maximo cerca de centro de luz | En el tramo y tramos alternos |
| **(b)** Mu- maximo en apoyo | Solo en tramos adyacentes |

### 6.4.3 Losas Bidireccionales

| Condicion | Requisito |
|-----------|-----------|
| L conocida (6.4.3.1) | Analizar para esa disposicion |
| L <= 0.75D o carga simultanea (6.4.3.2) | L en todos los paneles |
| Otros casos (6.4.3.3) | 75% de L en patrones criticos |

### 6.4.4 Vacios en Losas

Para embedments que crean vacios paralelos al plano de la losa:
- Dimension de seccion transversal > **1/3 del espesor de losa**, O
- Espaciados a menos de **3 diametros o anchos** c-c

**Requisito:** Considerar la disposicion de carga viva solo en una porcion de la losa.

---

*ACI 318-25 Secciones 6.3-6.4*
