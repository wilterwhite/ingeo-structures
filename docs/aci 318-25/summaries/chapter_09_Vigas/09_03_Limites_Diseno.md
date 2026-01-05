# ACI 318-25 - Seccion 9.3: LIMITES DE DISENO

---

## 9.3.1 Peralte Minimo de Viga

### Tabla 9.3.1.1 - Peralte Minimo de Vigas No Presforzadas

| Condicion de Apoyo | Peralte Minimo h |
|-------------------|------------------|
| Simplemente apoyada | l/16 |
| Un extremo continuo | l/18.5 |
| Ambos extremos continuos | l/21 |
| Cantilever | l/8 |

> **NOTA**: Expresiones aplicables para concreto de peso normal y fy = 60,000 psi.

### 9.3.1.1.1 Modificacion por fy

Para fy diferente de 60,000 psi, multiplicar por:

```
(0.4 + fy/100,000)
```

### 9.3.1.1.2 Modificacion por Concreto Liviano

Para vigas de concreto liviano con wc entre 90 y 115 lb/ft^3, multiplicar por el mayor de:

- **(a)** 1.65 - 0.005wc
- **(b)** 1.09

### 9.3.1.2 Acabado de Piso

El espesor de acabado de piso puede incluirse en h si:
- Se coloca monoliticamente, o
- Se disena compuesto segun 16.4

---

## 9.3.2 Limites de Deflexion Calculada

| Seccion | Requisito |
|---------|-----------|
| 9.3.2.1 | Para vigas no presforzadas que no satisfacen 9.3.1 y vigas presforzadas: calcular deflexiones segun 24.2 |
| 9.3.2.2 | Para vigas compuestas apuntaladas que satisfacen 9.3.1: no se requiere calcular deflexiones post-composicion |

---

## 9.3.3 Limite de Deformacion del Refuerzo

### 9.3.3.1 Control por Tension

Vigas no presforzadas con Pu < 0.10 f'c Ag deben ser **controladas por tension** segun Tabla 21.2.2.

Esto significa:
- epsilon_t >= epsilon_ty + 0.003 para acero Grado 60
- Garantiza comportamiento ductil

---

## 9.3.4 Limites de Esfuerzo en Vigas Presforzadas

| Seccion | Requisito |
|---------|-----------|
| 9.3.4.1 | Clasificar como Clase U, T o C segun 24.5.2 |
| 9.3.4.2 | Esfuerzos despues de transferencia y en servicio no deben exceder 24.5.3 y 24.5.4 |

### Clasificacion de Vigas Presforzadas

| Clase | Esfuerzo de Tension en Servicio |
|-------|--------------------------------|
| U (Uncracked) | ft <= 7.5 sqrt(f'c) |
| T (Transition) | 7.5 sqrt(f'c) < ft <= 12 sqrt(f'c) |
| C (Cracked) | ft > 12 sqrt(f'c) |

---

## Resumen - Factores de Ajuste de Peralte

| Factor | Condicion | Multiplicar por |
|--------|-----------|-----------------|
| fy | fy != 60,000 psi | (0.4 + fy/100,000) |
| Concreto liviano | wc = 90-115 lb/ft^3 | mayor de (1.65 - 0.005wc) y 1.09 |

---

## Referencias

| Tema | Seccion |
|------|---------|
| Deflexiones | 24.2 |
| Control por tension | 21.2.2 |
| Clasificacion presforzadas | 24.5.2 |
| Esfuerzos transferencia | 24.5.3 |
| Esfuerzos servicio | 24.5.4 |
| Construccion compuesta | 16.4 |

---

*ACI 318-25 Seccion 9.3 - Limites de Diseno*
