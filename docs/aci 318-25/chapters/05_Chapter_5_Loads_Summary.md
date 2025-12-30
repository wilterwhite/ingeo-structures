# ACI 318-25 - CAPITULO 5: CARGAS
## Loads

---

## 5.1 ALCANCE

### 5.1.1 Aplicacion
Este capitulo aplica a la seleccion de factores de carga y combinaciones usadas en diseno, excepto lo permitido en el **Capitulo 27** (Evaluacion de estructuras existentes).

> **NOTA**: Las provisiones de carga estan destinadas para diseno de estructuras nuevas y evaluacion analitica de resistencia de estructuras existentes. Para cargas durante construccion, ver ASCE/SEI 37.

---

## 5.2 GENERALIDADES

### 5.2.1 Tipos de Cargas
Las cargas deben incluir:
- Peso propio
- Cargas aplicadas
- Efectos de presfuerzo
- Efectos de sismos
- Restriccion de cambio de volumen
- Asentamiento diferencial

### 5.2.2 Fuente de Cargas
Las cargas y Categorias de Diseno Sismico (SDC) deben estar de acuerdo con:
- El codigo general de edificacion, o
- Lo determinado por el funcionario de edificacion

> **NOTA**: Los SDC se adoptan directamente de ASCE/SEI 7.

### 5.2.3 Reduccion de Carga Viva
Se permite reduccion de carga viva de acuerdo con:
- El codigo general de edificacion, o
- ASCE/SEI 7 (en ausencia de codigo general)

---

## 5.3 FACTORES DE CARGA Y COMBINACIONES

### 5.3.1 Combinaciones de Carga

| Combinacion de Carga | Ecuacion | Carga Principal |
|---------------------|----------|-----------------|
| U = 1.4D | (5.3.1a) | D |
| U = 1.2D + 1.6L + (0.5Lr o 0.3S o 0.5R) | (5.3.1b) | L |
| U = 1.2D + (1.6Lr o 1.0S o 1.6R) + (1.0L o 0.5W) | (5.3.1c) | Lr o S o R |
| U = 1.2D + 1.0W + 1.0L + (0.5Lr o 0.3S o 0.5R) | (5.3.1d) | W |
| U = 1.2D + 1.0E + 1.0L + 0.15S | (5.3.1e) | E |
| U = 0.9D + 1.0W | (5.3.1f) | W |
| U = 0.9D + 1.0E | (5.3.1g) | E |

### Notacion de Cargas

| Simbolo | Descripcion |
|---------|-------------|
| D | Carga muerta |
| L | Carga viva |
| Lr | Carga viva de techo |
| S | Carga de nieve |
| R | Carga de lluvia |
| W | Carga de viento |
| E | Efecto sismico (horizontal y vertical) |

---

### 5.3.2 Cargas No Simultaneas
Se debe investigar el efecto de una o mas cargas que no actuan simultaneamente.

---

### 5.3.3 Reduccion del Factor de Carga Viva

El factor de carga viva L en Ec. (5.3.1c), (5.3.1d) y (5.3.1e) se permite reducir a **0.5**, **EXCEPTO** para:

| Excepcion | Descripcion |
|-----------|-------------|
| (a) | Garajes |
| (b) | Areas de asamblea publica |
| (c) | Areas donde L > 100 lb/ft² |

---

### 5.3.4 Cargas Vivas Incluidas
Si aplica, L debe incluir:

| Item | Tipo de Carga |
|------|---------------|
| (a) | Cargas vivas concentradas |
| (b) | Cargas vehiculares |
| (c) | Cargas de grua |
| (d) | Cargas en pasamanos, barandas y barreras vehiculares |
| (e) | Efectos de impacto |
| (f) | Efectos de vibracion |

---

### 5.3.5 Cargas de Viento a Nivel de Servicio
Si la carga de viento W se proporciona a nivel de servicio:
- Usar **1.6W** en lugar de 1.0W en Ec. (5.3.1d) y (5.3.1f)
- Usar **0.8W** en lugar de 0.5W en Ec. (5.3.1c)

> **NOTA**: ASCE/SEI 7-22 prescribe cargas de viento a nivel de resistencia (factor 1.0). Las velocidades de diseno se basan en periodos de recurrencia de 300, 700, 1700 y 3000 anos segun la categoria de riesgo.

---

### 5.3.6 Efectos de Cambio de Volumen (T)
Los efectos estructurales de fuerzas por restriccion de cambio de volumen y asentamiento diferencial **T** deben considerarse si pueden afectar adversamente la seguridad o desempeno estructural.

**Consideraciones para el factor de carga T:**
- Incertidumbre en la magnitud probable de T
- Probabilidad de ocurrencia simultanea con otras cargas
- Consecuencias adversas potenciales

**Factor de carga minimo: 1.0**

---

### 5.3.7 Carga de Fluidos (F)

| Condicion | Factor de Carga | Ecuacion |
|-----------|-----------------|----------|
| F actua sola o suma a D | 1.4 | (5.3.1a) |
| F suma a la carga principal | 1.2 | (5.3.1b) a (5.3.1e) |
| F es permanente y contrarresta la carga principal | 0.9 | (5.3.1g) |
| F no es permanente y contrarresta la carga principal | No incluir | - |

---

### 5.3.8 Presion Lateral de Tierra (H)

| Condicion | Factor de Carga |
|-----------|-----------------|
| H actua sola o suma al efecto de carga principal | 1.6 |
| H es permanente y contrarresta el efecto de carga principal | 0.9 |
| H no es permanente y contrarresta el efecto de carga principal | No incluir |

---

### 5.3.9 Cargas de Inundacion
Si la estructura esta en zona de inundacion, usar cargas de inundacion y factores de **ASCE/SEI 7**.

---

### 5.3.10 Cargas de Hielo Atmosferico
Si la estructura esta sujeta a cargas de hielo atmosferico, usar cargas y factores de **ASCE/SEI 7**.

---

### 5.3.11 Cargas de Tornado
Para estructuras que requieren resistir cargas de tornado, usar cargas y factores de **ASCE/SEI 7**.

---

### 5.3.12 Cargas de Tsunami
Para estructuras que requieren resistir cargas de tsunami, usar cargas y factores de **ASCE/SEI 7**.

---

### 5.3.13 Agua en Suelo
Se permite el metodo alternativo de ASCE/SEI 7 para cargas de agua en suelo.

> **NOTA**: El metodo alternativo permite desacoplar el efecto de presion de agua subterranea de la presion de suelo.

---

### 5.3.14 Efectos de Presfuerzo
La resistencia requerida U debe incluir efectos de carga internos debido a reacciones inducidas por presfuerzo con factor de carga **1.0**.

> **NOTA**: Para estructuras estaticamente indeterminadas, los efectos internos de carga (momentos secundarios) pueden ser significativos.

---

### 5.3.15 Zonas de Anclaje Post-tensado
Para diseno de zona de anclaje post-tensado, aplicar factor de carga **1.2** a la fuerza maxima de tensado del refuerzo de presfuerzo.

> **NOTA**: El factor 1.2 resulta en una carga de diseno de ~113% de fy pero no mas del 96% de fpu.

---

### 5.3.16 Presfuerzo con Metodo Puntal-Tensor

| Condicion | Factor de Carga |
|-----------|-----------------|
| Efectos de presfuerzo **aumentan** la fuerza neta en puntales o tensores | 1.2 |
| Efectos de presfuerzo **reducen** la fuerza neta en puntales o tensores | 0.9 |

---

## RESUMEN DE FACTORES DE CARGA

### Factores por Tipo de Carga

| Carga | Factor Tipico | Notas |
|-------|---------------|-------|
| D (Muerta) | 1.2 o 1.4 | 0.9 cuando contrarresta |
| L (Viva) | 1.6 | 0.5 o 1.0 en algunas combinaciones |
| Lr (Viva techo) | 1.6 | 0.5 en algunas combinaciones |
| S (Nieve) | 1.0 | 0.3 o 0.15 en algunas combinaciones |
| R (Lluvia) | 1.6 | 0.5 en algunas combinaciones |
| W (Viento) | 1.0 | 1.6 si es a nivel de servicio |
| E (Sismo) | 1.0 | Incluye Eh y Ev |
| F (Fluido) | 1.2 o 1.4 | 0.9 cuando contrarresta |
| H (Tierra) | 1.6 | 0.9 cuando contrarresta |
| T (Cambio volumen) | ≥ 1.0 | Segun analisis |

---

## REFERENCIAS A OTROS DOCUMENTOS

| Documento | Tema |
|-----------|------|
| ASCE/SEI 7-22 | Cargas de diseno, mapas, combinaciones |
| ASCE/SEI 37 | Cargas durante construccion |
| IBC | Codigo internacional de edificacion |
| NFPA 5000 | Codigo de edificacion |
| Capitulo 27 | Evaluacion de estructuras existentes |

---

## NOTAS IMPORTANTES

1. **Cargas a Nivel de Resistencia**: ASCE/SEI 7-22 proporciona cargas de viento, nieve, sismo y tornado a nivel de resistencia (factor 1.0)

2. **Efectos Sismicos**: E incluye efectos horizontales (Eh) y verticales (Ev). Ev se aplica como adicion o sustraccion del efecto de carga muerta

3. **Combinaciones 0.9D**: Incluidas para casos donde mayor carga muerta reduce los efectos de otras cargas, o para secciones de columnas controladas por tension

4. **Carga de Lluvia**: Debe considerar todas las acumulaciones probables de agua. Disenar con pendiente o contraflecha adecuada para drenaje

5. **Efectos P-Delta**: Si los efectos de carga no son linealmente relacionados a las cargas, las cargas se factorizan antes de determinar los efectos

---

*Resumen del ACI 318-25 Capitulo 5 - Cargas.*
*Fecha: 2025*
