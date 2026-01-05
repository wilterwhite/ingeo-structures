# ACI 318-25 - Seccion 9.7: DETALLADO DEL REFUERZO

---

## 9.7.1 General

| Seccion | Requisito | Referencia |
|---------|-----------|------------|
| 9.7.1.1 | Recubrimiento de concreto | 20.5.1 |
| 9.7.1.2 | Longitudes de desarrollo | 25.4 |
| 9.7.1.3 | Empalmes de refuerzo deformado | 25.5 |
| 9.7.1.4 | Para fy >= 80,000 psi: Ktr >= 0.5 db a lo largo de desarrollo y empalmes | - |
| 9.7.1.5 | Barras en paquete | 25.6 |

---

## 9.7.2 Espaciamiento del Refuerzo

| Seccion | Requisito |
|---------|-----------|
| 9.7.2.1 | Espaciamientos minimos segun 25.2 |
| 9.7.2.2 | Para vigas no presforzadas y Clase C presforzadas: s segun 24.3 |
| 9.7.2.3 | Para vigas con h > 36 in.: refuerzo de piel distribuido en h/2 desde cara en tension, s segun 24.3.2 |

---

## 9.7.3 Refuerzo a Flexion en Vigas No Presforzadas

### 9.7.3.1-9.7.3.4 Desarrollo del Refuerzo

| Seccion | Requisito |
|---------|-----------|
| 9.7.3.1 | Desarrollar fuerza calculada a cada lado de la seccion |
| 9.7.3.2 | Ubicaciones criticas: puntos de maximo esfuerzo y donde el refuerzo ya no es necesario |
| 9.7.3.3 | Extender mas alla del punto donde no es necesario: >= mayor de d y 12 db |
| 9.7.3.4 | Refuerzo continuo: embedment >= ld mas alla del punto de corte |

### 9.7.3.5 Terminacion en Zona de Tension

No terminar refuerzo en zona de tension a menos que:

- **(a)** Vu <= (2/3) phi Vn en el punto de corte
- **(b)** Para barras No. 11 y menores: refuerzo continuo = 2x requerido y Vu <= (3/4) phi Vn
- **(c)** Estribos adicionales: area >= 60 bw s / fyt, s <= d/(8 beta_b), sobre distancia 3d/4

### 9.7.3.8 Terminacion del Refuerzo

| Ubicacion | Requisito |
|-----------|-----------|
| Apoyos simples | >= 1/3 del refuerzo de momento positivo maximo se extiende >= 6 in. al apoyo |
| Otros apoyos | >= 1/4 del refuerzo de momento positivo maximo se extiende >= 6 in. al apoyo |
| Sistema resistente lateral | Desarrollar fy en tension en cara del apoyo |
| Apoyos simples y P.I. | ld <= 1.3 Mn/Vu + la (confinado) o ld <= Mn/Vu + la (no confinado) |
| Momento negativo | >= 1/3 con embedment >= mayor de d, 12 db y ln/16 mas alla de P.I. |

---

## 9.7.4 Refuerzo a Flexion en Vigas Presforzadas

| Seccion | Requisito |
|---------|-----------|
| 9.7.4.1 | Tendones externos: mantener excentricidad especificada |
| 9.7.4.3.1 | Zonas de anclaje post-tensado segun 25.9 |
| 9.7.4.3.2 | Anclajes y acopladores segun 25.8 |

### 9.7.4.4 Terminacion de Refuerzo con Tendones No Adheridos

- **(a)** >= ln/3 en areas de momento positivo, centrado
- **(b)** >= ln/6 a cada lado de la cara del apoyo

---

## 9.7.5 Refuerzo Longitudinal por Torsion

| Seccion | Requisito |
|---------|-----------|
| 9.7.5.1 | Distribuir alrededor del perimetro de estribos cerrados, s <= 12 in., al menos una barra en cada esquina |
| 9.7.5.2 | Diametro >= 0.042 x espaciamiento transversal, pero no menor que 3/8 in. |
| 9.7.5.3 | Extender >= (bt + d) mas alla del punto requerido por analisis |
| 9.7.5.4 | Desarrollar en la cara del apoyo en ambos extremos |

---

## 9.7.6 Refuerzo Transversal

### 9.7.6.2 Cortante

#### Tabla 9.7.6.2.2 - Espaciamiento Maximo de Piernas de Refuerzo de Cortante

| Vs Requerido | Viga No Presforzada | | Viga Presforzada | |
|--------------|---------------------|---|------------------|---|
| | A lo largo | A traves | A lo largo | A traves |
| <= 4 sqrt(f'c) bw d | Menor de d/2 y 24 in. | d | Menor de 3h/4 y 24 in. | 3h/2 |
| > 4 sqrt(f'c) bw d | Menor de d/4 y 12 in. | d/2 | Menor de 3h/8 y 12 in. | 3h/4 |

### 9.7.6.3 Torsion

| Seccion | Requisito |
|---------|-----------|
| 9.7.6.3.1 | Estribos cerrados segun 25.7.1.6 o aros |
| 9.7.6.3.2 | Extender >= (bt + d) mas alla del punto requerido |
| 9.7.6.3.3 | s <= menor de ph/8 y 12 in. |
| 9.7.6.3.4 | Secciones huecas: distancia al centro del refuerzo desde cara interior >= 0.5 Aoh/ph |

### 9.7.6.4 Soporte Lateral del Refuerzo de Compresion

| Seccion | Requisito |
|---------|-----------|
| 9.7.6.4.2 | Tamano minimo: No. 3 para barras <= No. 10; No. 4 para barras >= No. 11 y paquetes |
| 9.7.6.4.3 | Espaciamiento <= menor de 16 db (long.), 48 db (transv.) y dimension menor de la viga |
| 9.7.6.4.4 | Toda barra de compresion a <= 6 in. de una esquina de estribo con angulo <= 135 grados |

---

## 9.7.7 Refuerzo de Integridad Estructural (Vigas Coladas en Sitio)

### 9.7.7.1 Vigas Perimetrales

- **(a)** >= 1/4 del refuerzo de momento positivo maximo continuo (min. 2 barras)
- **(b)** >= 1/6 del refuerzo de momento negativo continuo (min. 2 barras)
- **(c)** Estribos cerrados con s <= d/2 (no presforzada) o 3h/4 (presforzada)
- En extremos apoyados sobre longitud >= 2h: s <= menor de d/4 (o 3h/8), 8 db, 24 db de estribo, 12 in.

### 9.7.7.2 Otras Vigas

- **(a)** >= 1/4 del refuerzo de momento positivo maximo continuo (min. 2 barras), o
- **(b)** Refuerzo longitudinal encerrado por estribos cerrados

| Seccion | Requisito |
|---------|-----------|
| 9.7.7.3 | Refuerzo de integridad pasa a traves de la region de la columna |
| 9.7.7.4 | Desarrollar en tension con 1.25 fy en apoyos no continuos |
| 9.7.7.5 | Empalmes: momento positivo cerca del apoyo, momento negativo cerca de midspan |
| 9.7.7.6 | Empalmes mecanicos, soldados o Clase B |

---

## Referencias

| Tema | Seccion |
|------|---------|
| Recubrimiento | 20.5.1 |
| Longitud de desarrollo | 25.4 |
| Empalmes | 25.5 |
| Barras en paquete | 25.6 |
| Estribos cerrados | 25.7.1.6 |
| Anclajes y acopladores | 25.8 |
| Zonas de anclaje | 25.9 |
| Control de fisuración | 24.3 |

---

*ACI 318-25 Seccion 9.7 - Detallado del Refuerzo*
