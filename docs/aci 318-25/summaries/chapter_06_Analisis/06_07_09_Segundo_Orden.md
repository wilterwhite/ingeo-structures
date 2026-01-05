# ACI 318-25 - 6.7-6.9 ANALISIS 2DO ORDEN, INELASTICO Y FEM

---

## 6.7 ANALISIS ELASTICO LINEAL DE SEGUNDO ORDEN

### 6.7.1 General

#### 6.7.1.1 Requisitos
Debe considerar:
- Influencia de cargas axiales
- Presencia de regiones fisuradas
- Efectos de duracion de carga

#### 6.7.1.2 Efectos de Esbeltez
Se deben considerar a lo largo de la longitud de la columna. Se permite usar 6.6.4.5.

### 6.7.2 Propiedades de Seccion
- **Cargas factoradas:** Usar propiedades de 6.6.3.1
- **Cargas de servicio:** I = 1.4 * I_factorado (pero <= Ig)

---

## 6.8 ANALISIS INELASTICO

### 6.8.1 General

#### 6.8.1.1 Requisitos
- Debe considerar **no linealidad del material**
- 1er orden: equilibrio en configuracion no deformada
- 2do orden: equilibrio en configuracion deformada

#### 6.8.1.2 Validacion
El procedimiento debe demostrar concordancia sustancial con resultados de ensayos fisicos.

#### 6.8.1.5 Redistribucion
**NO se permite** redistribuir momentos calculados por analisis inelastico.

---

## 6.9 ANALISIS DE ELEMENTOS FINITOS

### 6.9.1 Permiso
Se permite usar analisis de elementos finitos para determinar efectos de carga.

### 6.9.2 Modelo Apropiado
El modelo debe ser apropiado para el proposito previsto:
- Tipos de elementos capaces de representar la respuesta requerida
- Malla de tamano suficiente para capturar detalle estructural

### 6.9.3 Analisis Inelastico
Se requiere un analisis **separado** para cada combinacion de carga factorada (superposicion no aplica).

### 6.9.5 Tolerancia Dimensional
Dimensiones usadas en analisis deben estar dentro del **10%** de las especificadas, o repetir el analisis.

### 6.9.6 Redistribucion
**NO se permite** redistribuir momentos de analisis inelastico.

---

## FIGURAS CLAVE

### Fig. R6.2.5.1 - Factor de Longitud Efectiva k
- **(a) Marcos Nonsway:** k = 0.5 a 1.0
- **(b) Marcos Sway:** k >= 1.0

### Fig. R6.2.5.3 - Diagrama de Flujo para Esbeltez
1. Ignorar esbeltez? (6.2.5.1) → Si: Solo analisis 1er orden
2. Columnas como nonsway? (6.6.4.3) → Si: Magnificacion nonsway (6.6.4.5)
3. Marcos sway → Magnificacion sway (6.6.4.6) o analisis 2do orden
4. Verificar Mu(2do orden) <= 1.4*Mu(1er orden)

---

*ACI 318-25 Secciones 6.7-6.9*
