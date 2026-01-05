# ACI 318-25 - Seccion 9.9: VIGAS PROFUNDAS (DEEP BEAMS)

---

## 9.9.1 General

### 9.9.1.1 Definicion de Viga Profunda

Una viga se considera profunda si cumple una de las siguientes condiciones:

- **(a)** Claro libre <= **4h**
- **(b)** Cargas concentradas dentro de **2h** de la cara del apoyo

### 9.9.1.2 Distribucion No Lineal

Disenar considerando distribucion no lineal de deformacion longitudinal.

### 9.9.1.3 Metodo Puntal-Tensor

El metodo puntal-tensor (Capitulo 23) satisface 9.9.1.2.

---

## 9.9.2 Limites Dimensionales

### 9.9.2.1 Cortante Maximo

Excepto segun 23.4.4:

```
Vu <= phi 10 sqrt(f'c) bw d
```

---

## 9.9.3 Limites de Refuerzo

### 9.9.3.1 Refuerzo Distribuido Minimo

- **(a)** Transversal: **Atd >= 0.0025 bw std**
- **(b)** Longitudinal: **Ald >= 0.0025 bw sld**

### 9.9.3.2 Refuerzo Minimo a Flexion

Segun 9.6.1.

---

## 9.9.4 Detallado del Refuerzo

| Seccion | Requisito |
|---------|-----------|
| 9.9.4.1 | Recubrimiento segun 20.5.1 |
| 9.9.4.2 | Espaciamiento minimo segun 25.2 |
| 9.9.4.3 | Espaciamiento de refuerzo distribuido <= menor de d/5 y 12 in. |
| 9.9.4.4 | Para bw > 8 in.: al menos 2 cortinas, swd <= 24 in. |
| 9.9.4.5 | Desarrollo considerando distribucion de esfuerzo no proporcional al momento |
| 9.9.4.6 | Apoyos simples: desarrollar fy en la cara del apoyo |
| 9.9.4.7 | Apoyos interiores: refuerzo negativo continuo; refuerzo positivo continuo o empalmado |

---

## Diagrama de Viga Profunda

```
            P (carga concentrada)
            |
            v
    |===================|
    |                   |
    |    Zona donde     |    ln <= 4h
    |    aplica STM     |    o carga dentro de 2h
    |                   |
    |___________________|
    ^                   ^
    R1                  R2

    |<------- ln ------>|

    Condiciones:
    - ln/h <= 4, o
    - a/h <= 2 (donde a = distancia de carga al apoyo)
```

---

## Refuerzo Distribuido

```
    |---------------------------|
    |   |   |   |   |   |   |   |  <- Refuerzo horizontal
    |---|---|---|---|---|---|---|     rho_h >= 0.0025
    |   |   |   |   |   |   |   |
    |---|---|---|---|---|---|---|
    |   |   |   |   |   |   |   |
    |---|---|---|---|---|---|---|
    |   |   |   |   |   |   |   |
    |---------------------------|
        ^   ^   ^   ^   ^   ^
        Refuerzo vertical
        rho_v >= 0.0025

    Espaciamiento: s <= min(d/5, 12 in.)
```

---

## Resumen de Requisitos

| Parametro | Requisito |
|-----------|-----------|
| Definicion | ln <= 4h o carga dentro de 2h |
| Cortante maximo | Vu <= phi 10 sqrt(f'c) bw d |
| Refuerzo distribuido minimo | 0.0025 en ambas direcciones |
| Espaciamiento maximo | Menor de d/5 y 12 in. |
| Cortinas (bw > 8 in.) | Minimo 2, separacion <= 24 in. |
| Metodo de diseno | Puntal-tensor (Capitulo 23) |

---

## Referencias

| Tema | Seccion |
|------|---------|
| Metodo puntal-tensor | Capitulo 23 |
| Recubrimiento | 20.5.1 |
| Espaciamiento minimo | 25.2 |
| Refuerzo minimo a flexion | 9.6.1 |

---

*ACI 318-25 Seccion 9.9 - Vigas Profundas (Deep Beams)*
