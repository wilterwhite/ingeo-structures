# ACI 318-25 - Seccion 9.4: RESISTENCIA REQUERIDA

---

## 9.4.1 General

| Seccion | Requisito |
|---------|-----------|
| 9.4.1.1 | Calcular segun combinaciones de carga factorizadas del Capitulo 5 |
| 9.4.1.2 | Calcular segun procedimientos de analisis del Capitulo 6 |
| 9.4.1.3 | Para vigas presforzadas, considerar efectos de presfuerzo segun 5.3.14 |

---

## 9.4.2 Momento Factorizado

### 9.4.2.1 Seccion Critica

Para vigas construidas integralmente con apoyos, Mu puede calcularse en la **cara del apoyo**.

---

## 9.4.3 Cortante Factorizado

### 9.4.3.1 General

Para vigas construidas integralmente con apoyos, Vu puede calcularse en la **cara del apoyo**.

### 9.4.3.2 Seccion Critica Reducida

Se permite usar seccion critica reducida si se cumplen **(a)**, **(b)** y **(c)**:

- **(a)** Reaccion del apoyo introduce compresion en la region del extremo
- **(b)** Cargas aplicadas en o cerca de la superficie superior
- **(c)** No hay carga concentrada entre cara del apoyo y seccion critica

| Tipo de Viga | Seccion Critica |
|--------------|-----------------|
| No presforzada | **d** desde la cara del apoyo |
| Presforzada | **h/2** desde la cara del apoyo |

---

## 9.4.4 Torsion Factorizada

| Seccion | Requisito |
|---------|-----------|
| 9.4.4.1 | Se permite tomar carga torsional de losa como uniforme |
| 9.4.4.2 | Tu puede calcularse en la cara del apoyo |
| 9.4.4.3 | Seccion critica a d (no presforzada) o h/2 (presforzada), excepto si hay momento torsional concentrado |
| 9.4.4.4 | Se permite reducir Tu segun 22.7.3 |

---

## Diagrama - Secciones Criticas

```
                     Carga uniforme
                     ||||||||||||||||
                     vvvvvvvvvvvvvvvv
    |=======================================|
    |                                       |
    |<--d-->|                       |<--d-->|
         ^                               ^
    Seccion                         Seccion
    critica                         critica
    cortante                        cortante
```

### Notas:
- **d** = peralte efectivo (no presforzada)
- **h/2** = mitad del peralte total (presforzada)

---

## Resumen de Secciones Criticas

| Solicitacion | Ubicacion | Condiciones |
|--------------|-----------|-------------|
| Momento (Mu) | Cara del apoyo | Construccion integral |
| Cortante (Vu) | Cara del apoyo | General |
| Cortante (Vu) | d o h/2 de la cara | Con condiciones 9.4.3.2 |
| Torsion (Tu) | Cara del apoyo | General |
| Torsion (Tu) | d o h/2 de la cara | Sin momento torsional concentrado |

---

## Referencias

| Tema | Seccion |
|------|---------|
| Combinaciones de carga | Capitulo 5 |
| Efectos de presfuerzo | 5.3.14 |
| Procedimientos de analisis | Capitulo 6 |
| Reduccion de torsion | 22.7.3 |

---

*ACI 318-25 Seccion 9.4 - Resistencia Requerida*
