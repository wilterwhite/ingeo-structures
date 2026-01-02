# ACI 318-25 - APENDICE B: DISENO POR VIENTO BASADO EN DESEMPENO (NUEVO)
## Performance-Based Wind Design

---

## INDICE

- [B.1 Alcance](#b1-alcance)
- [B.2 Niveles de Desempeno](#b2-niveles-de-desempeno)
- [B.3 Criterios de Aceptacion](#b3-criterios-de-aceptacion)
- [B.4 Analisis Requerido](#b4-analisis-requerido)
- [B.5 Efectos Aerodinamicos](#b5-efectos-aerodinamicos)
- [B.6 Amortiguamiento](#b6-amortiguamiento)
- [B.7 Consideraciones Especiales](#b7-consideraciones-especiales)
- [B.8 Documentacion](#b8-documentacion)
- [Referencias](#referencias)

---

## B.1 ALCANCE

### B.1.1 Aplicabilidad
Este apendice provee requisitos para diseno por viento basado en desempeno para:
- (a) Edificios altos (> 60 m)
- (b) Edificios con geometria irregular
- (c) Estructuras donde se requiere desempeno especifico

### B.1.2 Objetivos
- Definir niveles de desempeno bajo viento
- Establecer criterios de aceptacion
- Proveer marco para analisis avanzado

---

## B.2 NIVELES DE DESEMPENO

### B.2.1 Definicion de Niveles

**Tabla B.2.1.1 - Niveles de Desempeno por Viento**

| Nivel | MRI (anos) | Descripcion |
|-------|------------|-------------|
| Viento frecuente | 10 | Confort de ocupantes |
| Viento de diseno | 25-50 | Funcionalidad, dano menor |
| Viento extremo | 700-1700 | Seguridad estructural |

*MRI = Mean Recurrence Interval*

### B.2.2 Objetivos por Nivel

**Tabla B.2.2.1 - Objetivos de Desempeno**

| Nivel | Estructural | No Estructural | Ocupantes |
|-------|-------------|----------------|-----------|
| Frecuente | Elastico | Sin dano | Confort |
| Diseno | Fluencia limitada | Dano menor | Seguridad |
| Extremo | Ductilidad controlada | Dano significativo | Evacuacion |

---

## B.3 CRITERIOS DE ACEPTACION

### B.3.1 Derivas (Drift)

**Tabla B.3.1.1 - Limites de Deriva por Viento**

| Nivel | Limite Drift Entrepiso |
|-------|----------------------|
| Viento frecuente | H/500 a H/400 |
| Viento de diseno | H/400 a H/300 |
| Viento extremo | H/200 a H/100 |

### B.3.2 Aceleraciones

**Tabla B.3.2.1 - Limites de Aceleracion (Confort)**

| Uso | Frecuencia < 1 Hz | Frecuencia > 1 Hz |
|-----|-------------------|-------------------|
| Residencial | 10-15 milli-g | 15-25 milli-g |
| Oficinas | 15-25 milli-g | 25-40 milli-g |
| MRI = 1 ano | | |

### B.3.3 Esfuerzos

**Tabla B.3.3.1 - Limites de Esfuerzo**

| Nivel | Concreto | Acero |
|-------|----------|-------|
| Frecuente | fc <= 0.45*f'c | fs <= 0.60*fy |
| Diseno | fc <= 0.60*f'c | fs <= 0.90*fy |
| Extremo | fc <= 0.85*f'c | fs <= 1.00*fy |

---

## B.4 ANALISIS REQUERIDO

### B.4.1 Pruebas de Tunel de Viento

**B.4.1.1** Requeridas para:
- Edificios > 120 m
- Edificios con irregularidades significativas
- Cuando se requiere optimizacion

**B.4.1.2** Tipos de pruebas:
- HFFB (High Frequency Force Balance)
- HFPB (High Frequency Pressure Balance)
- Aeroelastico

### B.4.2 Modelado Dinamico

**B.4.2.1** Propiedades requeridas:
- Masa y rigidez del edificio
- Amortiguamiento (tipico 1.5% - 2.5%)
- Formas modales

**B.4.2.2** Respuesta dinamica:
```
Response = Background + Resonant
sigma_total = sqrt(sigma_B² + sigma_R²)
```

### B.4.3 Factor de Pico

```
g = sqrt(2*ln(nu*T)) + 0.5772/sqrt(2*ln(nu*T))
```

Tipico g = 3.5 a 4.0

---

## B.5 EFECTOS AERODINAMICOS

### B.5.1 Vortex Shedding

**B.5.1.1** Frecuencia de desprendimiento:
```
fs = St * V / D
```

Donde:
- St = numero de Strouhal (tipico 0.12 a 0.20)
- V = velocidad del viento
- D = dimension caracteristica

**B.5.1.2** Lock-in ocurre cuando fs ≈ fn

### B.5.2 Galloping

Verificar para secciones no circulares con:
- Gradiente de fuerza negativo
- Baja frecuencia natural

### B.5.3 Flutter

- Tipicamente no critico para edificios de concreto
- Verificar para estructuras muy esbeltas

---

## B.6 AMORTIGUAMIENTO

### B.6.1 Valores de Amortiguamiento

**Tabla B.6.1.1 - Amortiguamiento Inherente**

| Tipo de Estructura | Amplitud Baja | Amplitud Alta |
|--------------------|---------------|---------------|
| Concreto reforzado | 1.0% - 1.5% | 2.0% - 3.0% |
| Concreto pretensado | 0.7% - 1.0% | 1.5% - 2.0% |
| Acero con particiones | 1.5% - 2.0% | 2.5% - 3.5% |

### B.6.2 Sistemas de Amortiguamiento Suplementario

**Tabla B.6.2.1 - Tipos de Sistemas**

| Sistema | Aplicacion |
|---------|------------|
| TMD (Tuned Mass Damper) | Edificios altos |
| TLD (Tuned Liquid Damper) | Alternativa economica |
| Amortiguadores viscosos | Control distribuido |
| Amortiguadores de friccion | Alta capacidad |

---

## B.7 CONSIDERACIONES ESPECIALES

### B.7.1 Efectos de Interferencia

- Edificios cercanos pueden amplificar respuesta
- Considerar en pruebas de tunel de viento
- Buffeting de estela

### B.7.2 Efectos Direccionales

- Viento de diferentes direcciones
- Combinar con probabilidad direccional
- No reducir mas del 15% respecto a omni-direccional

### B.7.3 Cambio Climatico

- Considerar tendencias a largo plazo
- Incrementos proyectados de velocidad
- Incertidumbre en predicciones

---

## B.8 DOCUMENTACION

### B.8.1 Informe de Diseno

**Tabla B.8.1.1 - Contenido del Informe**

| Seccion | Contenido |
|---------|-----------|
| Objetivos | Niveles de desempeno seleccionados |
| Analisis | Metodos usados, resultados de tunel |
| Demandas | Cargas, derivas, aceleraciones |
| Capacidades | Verificacion de elementos |
| Aceptacion | Comparacion demanda vs capacidad |
| Sistemas | Amortiguamiento suplementario si aplica |

### B.8.2 Revision por Pares

**B.8.2.1** Requerida para:
- Edificios > 150 m
- Sistemas de amortiguamiento suplementario
- Desviaciones del codigo prescriptivo

---

## REFERENCIAS

| Tema | Referencia |
|------|------------|
| Cargas de viento | ASCE 7 |
| Tunel de viento | ASCE 49 |
| TMD y TLD | CTBUH Guidelines |
| Confort de ocupantes | ISO 10137, ISO 6897 |

---

*Resumen del ACI 318-25 Apendice B para diseno por viento basado en desempeno.*
*Fecha: 2025*
