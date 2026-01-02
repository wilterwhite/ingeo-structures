# ACI 318-25 - CAPITULO 27: EVALUACION DE ESTRUCTURAS EXISTENTES
## Evaluacion de Resistencia y Pruebas de Carga

---

## INDICE

- [27.1 Alcance](#271-alcance)
- [27.2 Evaluacion Analitica](#272-evaluacion-analitica)
- [27.3 Resistencia Basada en Nucleos](#273-resistencia-basada-en-nucleos)
- [27.4 Prueba de Carga](#274-prueba-de-carga)
- [27.5 Evaluacion Sismica](#275-evaluacion-sismica)
- [27.6 Evaluacion de Danos](#276-evaluacion-de-danos)
- [27.7 Ensayos No Destructivos](#277-ensayos-no-destructivos)
- [27.8 Documentacion e Informe](#278-documentacion-e-informe)
- [Formulas de Referencia Rapida](#formulas-de-referencia-rapida)
- [Referencias Cruzadas](#referencias-cruzadas)

---

## 27.1 ALCANCE

### 27.1.1 Aplicabilidad
Este capitulo aplica a la evaluacion de resistencia de estructuras existentes mediante:
- (a) Analisis analitico
- (b) Prueba de carga
- (c) Combinacion de ambos metodos

### 27.1.2 Cuando Aplica
- Dudas sobre capacidad estructural
- Danos por eventos (incendio, sismo, impacto)
- Cambio de uso o incremento de cargas
- Investigacion de concreto de baja resistencia
- Verificacion de construccion

---

## 27.2 EVALUACION ANALITICA

### 27.2.1 General

**27.2.1.1** La evaluacion analitica requiere:
- Documentacion de la estructura existente
- Determinacion de propiedades de materiales
- Analisis estructural

### 27.2.2 Investigacion de Campo

**Tabla 27.2.2.1 - Elementos de Investigacion**

| Item | Metodo |
|------|--------|
| Dimensiones | Medicion directa |
| Refuerzo (ubicacion) | Detector de refuerzo, excavacion |
| Refuerzo (tamano) | Exposicion y medicion |
| Resistencia del concreto | Nucleos (ASTM C42) |
| Resistencia del acero | Muestras (ASTM A370) |
| Condicion | Inspeccion visual, NDT |

### 27.2.3 Propiedades de Materiales In-Situ

**27.2.3.1** Resistencia del concreto:
- Minimo 3 nucleos por elemento o zona
- f'c in-situ = promedio de nucleos

**27.2.3.2** Resistencia del acero:
- Minimo 2 muestras por grado
- fy in-situ = promedio de muestras (no menor que especificado)

### 27.2.4 Factores de Reduccion Modificados

**Tabla 27.2.4.1 - Factores phi para Evaluacion**

| Condicion | Factor |
|-----------|--------|
| Materiales in-situ bien documentados | phi del Capitulo 21 |
| Incertidumbre moderada | 0.9 * phi |
| Alta incertidumbre | 0.8 * phi |

---

## 27.3 RESISTENCIA BASADA EN NUCLEOS

### 27.3.1 Extraccion de Nucleos

**27.3.1.1** Requisitos:
- Diametro >= 3.75 in (preferible 4 in)
- Relacion L/D entre 1.0 y 2.0
- Ubicacion representativa

**27.3.1.2** Procedimiento segun ASTM C42

### 27.3.2 Criterios de Aceptacion

**27.3.2.1** El concreto es estructuralmente adecuado si:

**(a)** Promedio de 3 nucleos:
```
f_nucleo,promedio >= 0.85 * f'c
```

**(b)** Ningun nucleo individual:
```
f_nucleo,individual >= 0.75 * f'c
```

### 27.3.3 Si No Cumple Criterios

**27.3.3.1** Opciones:
- Extraer nucleos adicionales
- Realizar prueba de carga
- Reforzar la estructura
- Reducir cargas

---

## 27.4 PRUEBA DE CARGA

### 27.4.1 General

**27.4.1.1** Se permite prueba de carga cuando:
- Nucleos no satisfacen criterios
- Analisis no es concluyente
- Se requiere verificacion directa

**27.4.1.2** Limitaciones:
- No usar en estructuras con dano severo
- No usar si representa riesgo de colapso

### 27.4.2 Requisitos Previos

**27.4.2.1** Antes de la prueba:
- Edad del concreto >= 56 dias
- Documentar condicion existente
- Establecer puntos de medicion
- Preparar plan de seguridad

### 27.4.3 Carga de Prueba

**27.4.3.1** Magnitud de carga de prueba:
```
Wt = 0.85 * (1.4*D + 1.7*L + 0.5*(Lr o S o R))     [Ec. 27.4.3.1a]
```

**27.4.3.2** Carga de prueba simplificada (solo D + L):
```
Wt = 0.85 * (1.4*D + 1.7*L)     [Ec. 27.4.3.1b]
```

### 27.4.4 Procedimiento de Carga

**Tabla 27.4.4.1 - Secuencia de Carga**

| Etapa | Carga | Duracion |
|-------|-------|----------|
| 1 | 0.25 * Wt | Hasta estabilizar |
| 2 | 0.50 * Wt | Hasta estabilizar |
| 3 | 0.75 * Wt | Hasta estabilizar |
| 4 | 1.00 * Wt | 24 horas |
| 5 | Remocion | Gradual |
| 6 | Recuperacion | 24 horas |

**27.4.4.2** Mediciones:
- Deflexiones en cada etapa
- Anchos de fisura
- Desplazamientos laterales (si aplica)

### 27.4.5 Criterios de Aceptacion

**27.4.5.1** La estructura pasa la prueba si cumple TODOS:

**(a)** No hay evidencia de falla:
- Sin fisuras de cortante
- Sin aplastamiento de concreto
- Sin rotura de refuerzo

**(b)** Deflexion maxima:
```
delta_max <= lt² / (20,000 * h)     [Ec. 27.4.5.1b]
```
Donde:
- lt = luz del claro (in)
- h = peralte total (in)

**(c)** Recuperacion de deflexion:
```
delta_recuperacion >= 0.75 * delta_max     [Ec. 27.4.5.1c]
```
*(medida 24 horas despues de remover carga)*

### 27.4.6 Si No Cumple Criterio de Recuperacion

**27.4.6.1** Se permite repetir la prueba:
- Esperar 72 horas minimo
- Segunda prueba con misma carga
- Recuperacion >= 0.80 * delta_max (segunda prueba)

### 27.4.7 Falla de la Prueba

**27.4.7.1** Si falla la prueba:
- Reforzar la estructura
- Cambiar uso a cargas menores
- Demoler y reconstruir

---

## 27.5 EVALUACION SISMICA

### 27.5.1 General

**27.5.1.1** Para estructuras existentes en zonas sismicas:
- Evaluar segun ASCE 41 o codigo local
- Considerar deficiencias tipicas

### 27.5.2 Deficiencias Comunes

**Tabla 27.5.2.1 - Deficiencias Sismicas Tipicas**

| Deficiencia | Efecto |
|-------------|--------|
| Refuerzo transversal insuficiente | Falla fragil en cortante |
| Traslapes en zonas de rotulas | Perdida de anclaje |
| Columnas cortas | Falla por cortante |
| Conexiones debiles | Perdida de continuidad |
| Muros no ductiles | Falla por cortante en plano |

### 27.5.3 Estrategias de Reforzamiento

**Tabla 27.5.3.1 - Metodos de Reforzamiento**

| Metodo | Aplicacion |
|--------|------------|
| Encamisado de concreto | Columnas, vigas, muros |
| Encamisado de acero | Columnas |
| FRP (fibra) | Columnas, vigas, losas |
| Adicion de muros | Rigidez y resistencia |
| Contravientos | Rigidez lateral |
| Aislamiento sismico | Reduccion de demanda |

---

## 27.6 EVALUACION DE DANOS

### 27.6.1 Por Fuego

**Tabla 27.6.1.1 - Evaluacion Post-Incendio**

| Indicador | Accion |
|-----------|--------|
| Cambio de color (< 300°C) | Generalmente aceptable |
| Delaminacion superficial | Reparar recubrimiento |
| Exposicion de refuerzo | Evaluar propiedades residuales |
| Deflexiones permanentes | Analisis detallado |

### 27.6.2 Por Sismo

**27.6.2.1** Clasificacion de danos:
- Insignificante: fisuras < 0.2 mm
- Leve: fisuras 0.2 - 1.0 mm
- Moderado: fisuras 1.0 - 2.0 mm, desprendimiento menor
- Severo: fisuras > 2.0 mm, exposicion de refuerzo
- Colapso parcial: perdida de seccion

### 27.6.3 Por Corrosion

**27.6.3.1** Evaluar:
- Potencial de media celda
- Resistividad del concreto
- Contenido de cloruros
- Profundidad de carbonatacion
- Perdida de seccion de refuerzo

---

## 27.7 ENSAYOS NO DESTRUCTIVOS

### 27.7.1 Tipos de Ensayos

**Tabla 27.7.1.1 - Metodos NDT**

| Metodo | Norma | Aplicacion |
|--------|-------|------------|
| Martillo de rebote | ASTM C805 | Uniformidad, estimacion f'c |
| Ultrasonido | ASTM C597 | Integridad, vacios |
| Radiografia | ASTM E94 | Ubicacion de refuerzo |
| Termografia | ASTM C1153 | Delaminaciones |
| GPR (radar) | ASTM D6432 | Refuerzo, vacios |
| Potencial media celda | ASTM C876 | Corrosion |

### 27.7.2 Correlacion con Resistencia

**27.7.2.1** Martillo de rebote:
- Requiere curva de correlacion con nucleos
- Precision tipica: ± 25%

**27.7.2.2** Ultrasonido:
- Velocidad de pulso indica calidad
- V > 4500 m/s: buena calidad
- V < 3000 m/s: posible dano

---

## 27.8 DOCUMENTACION E INFORME

### 27.8.1 Contenido del Informe

**Tabla 27.8.1.1 - Elementos del Informe**

| Seccion | Contenido |
|---------|-----------|
| Antecedentes | Proposito, alcance, documentos revisados |
| Investigacion | Metodos usados, ubicacion de ensayos |
| Resultados | Datos de campo, ensayos de laboratorio |
| Analisis | Evaluacion de capacidad |
| Conclusiones | Adecuacion estructural |
| Recomendaciones | Reparaciones, monitoreo, limitaciones |

### 27.8.2 Retencion de Registros

**27.8.2.1** Conservar por minimo 10 anos:
- Planos de investigacion
- Resultados de ensayos
- Fotografias
- Calculos

---

## FORMULAS DE REFERENCIA RAPIDA

### Carga de Prueba
```
Wt = 0.85 * (1.4*D + 1.7*L)
```

### Deflexion Maxima Permitida
```
delta_max <= lt² / (20,000*h)
```

### Recuperacion Requerida
```
delta_rec >= 0.75 * delta_max     (primera prueba)
delta_rec >= 0.80 * delta_max     (segunda prueba)
```

### Resistencia de Nucleos
```
Promedio >= 0.85*f'c
Individual >= 0.75*f'c
```

---

## REFERENCIAS CRUZADAS

| Tema | Seccion |
|------|---------|
| Resistencia del concreto | Capitulo 19 |
| Nucleos y ensayos | 26.12.4 |
| Requisitos sismicos | Capitulo 18 |
| Factores phi | 21.2 |
| Reforzamiento sismico | ASCE 41 |
| Evaluacion de estructuras | ACI 562 |

---

*Resumen del ACI 318-25 Capitulo 27 para evaluacion de estructuras existentes.*
*Fecha: 2025*
