# ACI 318-25 - APENDICE A: VERIFICACION POR ANALISIS NO LINEAL
## Metodos Avanzados de Analisis Estructural

---

## INDICE

- [A.1 Alcance](#a1-alcance)
- [A.2 Tipos de Analisis No Lineal](#a2-tipos-de-analisis-no-lineal)
- [A.3 Modelos Constitutivos del Concreto](#a3-modelos-constitutivos-del-concreto)
- [A.4 Modelos de Acero](#a4-modelos-de-acero)
- [A.5 Analisis Pushover](#a5-analisis-pushover)
- [A.6 Analisis Tiempo-Historia](#a6-analisis-tiempo-historia)
- [A.7 Criterios de Desempeno](#a7-criterios-de-desempeno)
- [A.8 Modelado de Elementos](#a8-modelado-de-elementos)
- [A.9 Verificacion del Modelo](#a9-verificacion-del-modelo)
- [A.10 Factores de Reduccion](#a10-factores-de-reduccion)
- [Referencias](#referencias)

---

## A.1 ALCANCE

### A.1.1 Aplicabilidad
Este apendice aplica al uso de analisis no lineal para verificar:
- (a) Resistencia de elementos y estructuras
- (b) Comportamiento bajo cargas extremas
- (c) Capacidad de redistribucion

### A.1.2 Cuando Usar
- Estructuras complejas
- Verificacion de diseno por capacidad
- Analisis pushover
- Analisis tiempo-historia

---

## A.2 TIPOS DE ANALISIS NO LINEAL

### A.2.1 No Linealidad de Material

**Tabla A.2.1.1 - Modelos de Material**

| Material | Modelo | Descripcion |
|----------|--------|-------------|
| Concreto (compresion) | Hognestad, Mander | Curva esfuerzo-deformacion con ablandamiento |
| Concreto (tension) | Tension stiffening | Contribucion post-agrietamiento |
| Acero | Bilineal, Ramberg-Osgood | Fluencia y endurecimiento |

### A.2.2 No Linealidad Geometrica

- Efectos P-Delta
- Grandes desplazamientos
- Cambio de geometria bajo carga

---

## A.3 MODELOS CONSTITUTIVOS DEL CONCRETO

### A.3.1 Compresion

**Modelo Hognestad:**
```
fc = f'c * [2*(epsilon/epsilon_o) - (epsilon/epsilon_o)²]     para epsilon <= epsilon_o
fc = f'c * [1 - 0.15*(epsilon - epsilon_o)/(epsilon_u - epsilon_o)]     para epsilon > epsilon_o
```

Donde:
- epsilon_o = 2*f'c / Ec (tipico 0.002)
- epsilon_u = 0.003 a 0.004

**Modelo Mander (Confinado):**
```
f'cc = f'c * (1 + k1 * fl/f'c)
epsilon_cc = epsilon_o * (1 + k2 * fl/f'c)
```

### A.3.2 Tension

**Comportamiento:**
- Lineal hasta fr = 7.5*sqrt(f'c)
- Reduccion gradual post-agrietamiento
- Tension stiffening en elementos reforzados

---

## A.4 MODELOS DE ACERO

### A.4.1 Modelo Bilineal

```
fs = Es * epsilon_s                    para epsilon_s <= epsilon_y
fs = fy + Esh * (epsilon_s - epsilon_y)     para epsilon_s > epsilon_y
```

Donde:
- Esh = modulo de endurecimiento (tipico 0.01 a 0.03 * Es)

### A.4.2 Modelo con Meseta

- Fluencia perfectamente plastica hasta epsilon_sh
- Endurecimiento hasta fu

---

## A.5 ANALISIS PUSHOVER

### A.5.1 Procedimiento

1. Aplicar cargas gravitacionales
2. Aplicar patron de cargas laterales incremental
3. Registrar curva capacidad (V vs delta)
4. Identificar mecanismos de falla

### A.5.2 Patrones de Carga

**Tabla A.5.2.1 - Patrones de Carga Lateral**

| Patron | Distribucion |
|--------|--------------|
| Uniforme | Fi = Wi |
| Triangular | Fi = Wi * hi |
| Primer modo | Fi = Wi * phi_i |
| Adaptativo | Basado en forma modal actual |

### A.5.3 Criterios de Aceptacion

- Identificar punto de desempeno
- Comparar con demanda sismica
- Verificar rotaciones plasticas

---

## A.6 ANALISIS TIEMPO-HISTORIA

### A.6.1 Registros de Entrada

**A.6.1.1** Seleccion de sismos:
- Minimo 3 registros (usar maximo)
- Minimo 7 registros (usar promedio)
- Escalar al espectro de diseno

### A.6.2 Modelos de Amortiguamiento

**Amortiguamiento de Rayleigh:**
```
C = alpha*M + beta*K
```

Tipico: xi = 2% a 5% del critico

### A.6.3 Integracion Numerica

- Metodo de Newmark
- HHT-alpha
- Paso de tiempo <= T1/20

---

## A.7 CRITERIOS DE DESEMPENO

### A.7.1 Estados Limite

**Tabla A.7.1.1 - Estados Limite de Desempeno**

| Estado | Descripcion | Drift Tipico |
|--------|-------------|--------------|
| Ocupacion Inmediata | Dano menor, funcional | 0.5% - 1.0% |
| Seguridad de Vida | Dano significativo, estable | 1.5% - 2.0% |
| Prevencion de Colapso | Dano severo, sin colapso | 2.5% - 4.0% |

### A.7.2 Limites de Rotacion Plastica

**Tabla A.7.2.1 - Rotaciones Plasticas Permitidas**

| Elemento | IO | LS | CP |
|----------|-----|-----|-----|
| Vigas ductiles | 0.010 | 0.025 | 0.050 |
| Columnas (P/Agf'c < 0.1) | 0.010 | 0.020 | 0.035 |
| Columnas (P/Agf'c = 0.4) | 0.005 | 0.010 | 0.015 |
| Muros (controlados por flexion) | 0.005 | 0.010 | 0.015 |

*Valores de referencia - verificar ASCE 41 para valores especificos*

---

## A.8 MODELADO DE ELEMENTOS

### A.8.1 Vigas y Columnas

**A.8.1.1** Modelos de plasticidad:
- Rotulas plasticas concentradas
- Plasticidad distribuida (fibras)
- Longitud de rotula: lp = 0.08*L + 0.15*db*fy/sqrt(f'c)

### A.8.2 Muros

**A.8.2.1** Opciones de modelado:
- Elementos tipo "Wide Column"
- Elementos fibra
- Elementos shell no lineales

### A.8.3 Conexiones

- Modelar rigidez de nudo
- Considerar deslizamiento de barras
- Incluir degradacion si aplica

---

## A.9 VERIFICACION DEL MODELO

### A.9.1 Validacion

**Tabla A.9.1.1 - Verificaciones Requeridas**

| Item | Verificar |
|------|-----------|
| Periodo fundamental | Comparar con formulas empiricas |
| Modos de vibracion | Masa participativa >= 90% |
| Equilibrio estatico | Suma de reacciones = cargas aplicadas |
| Convergencia | Tolerancia <= 0.001 |

### A.9.2 Analisis de Sensibilidad

- Variar propiedades de materiales ± 20%
- Evaluar efecto en respuesta global
- Identificar parametros criticos

---

## A.10 FACTORES DE REDUCCION

### A.10.1 Para Analisis No Lineal

**A.10.1.1** Usar phi = 1.0 si:
- Modelo captura todos los modos de falla
- Materiales modelados con valores esperados
- Se usa factor de carga adecuado

**A.10.1.2** Valores esperados de materiales:
```
f'c,esperado = 1.3 * f'c
fy,esperado = 1.17 * fy (Grado 60)
fy,esperado = 1.10 * fy (Grado 80)
```

---

## REFERENCIAS

| Tema | Referencia |
|------|------------|
| Criterios de desempeno | ASCE 41 |
| Modelado de concreto | ACI 369R |
| Pushover | FEMA 440 |
| Tiempo-historia | ASCE 7 |

---

*Resumen del ACI 318-25 Apendice A para analisis no lineal.*
*Fecha: 2025*
