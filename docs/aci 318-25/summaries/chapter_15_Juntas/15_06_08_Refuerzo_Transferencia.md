# ACI 318-25 - 15.6-15.8 REFUERZO Y TRANSFERENCIA

---

## 15.6 LIMITES DE REFUERZO

### 15.6.1 Refuerzo Transversal en Juntas

**15.6.1.1** Proporcionar refuerzo transversal cerrado a traves de la junta.

**15.6.1.2** Cantidad minima:
El refuerzo transversal en la junta debe ser al menos igual al requerido en las columnas adyacentes.

### 15.6.2 Desarrollo del Refuerzo

**15.6.2.1** El refuerzo longitudinal de vigas que termina en una junta debe:
- Extenderse hasta la cara lejana del nucleo confinado
- Desarrollarse por ld o ldh segun aplique

**15.6.2.2** Ganchos estandar:
- Doblar hacia el nucleo confinado de la junta

---

## 15.7 DETALLADO DEL REFUERZO

### 15.7.1 General

| Requisito | Referencia |
|-----------|------------|
| Recubrimiento | 20.5.1 |
| Longitudes de desarrollo | 25.4 |
| Empalmes | 25.5 |

### 15.7.2 Refuerzo Longitudinal de Columna

**15.7.2.1** Continuidad:
- El refuerzo longitudinal de columna debe ser continuo a traves de la junta
- O empalmado segun requisitos de empalme

### 15.7.3 Refuerzo de Viga en Juntas

**15.7.3.1** Barras superiores:
- Desarrollar hacia el nucleo de la junta
- Ganchos doblados hacia abajo en columnas exteriores

**15.7.3.2** Barras inferiores:
- Desarrollar hacia el nucleo de la junta
- Ganchos doblados hacia arriba en columnas exteriores

### 15.7.4 Espaciamiento en la Junta

El espaciamiento del refuerzo transversal en la junta no debe exceder:
- **s <= d/4** de la viga mas pequena
- **s <= 6 in.**

---

## 15.8 TRANSFERENCIA DE FUERZA AXIAL EN COLUMNAS

### 15.8.1 Transferencia de Compresion

**15.8.1.1** La fuerza axial de compresion se transfiere por:
- Aplastamiento directo del concreto
- Refuerzo de interface (dowels)

**15.8.1.2** Resistencia al aplastamiento:
```
Bn = 0.85 * fc' * A1 * √(A2/A1) <= 1.7 * fc' * A1
```

### 15.8.2 Transferencia de Tension

**15.8.2.1** La fuerza axial de tension se transfiere por:
- Refuerzo continuo, o
- Empalmes mecanicos, o
- Empalmes soldados, o
- Empalmes por traslape

### 15.8.3 Dowels de Columna

**15.8.3.1** Area minima de dowels:
```
As,dowel >= 0.005 * Ag (columna)
```

**15.8.3.2** Numero minimo: **4 barras**

**15.8.3.3** Desarrollo:
- Desarrollar completamente en compresion arriba y abajo de la junta
- Si hay tension, desarrollar para fy en tension

---

## 15.8.4 Transferencia Horizontal de Fuerzas

### 15.8.4.1 Cortante por Friccion

Para transferir cortante horizontal entre columna y fundacion:
```
Vn = μ * Avf * fy
```

Donde:
- **μ** = 1.4λ (concreto monolitico)
- **μ** = 1.0λ (concreto colocado contra concreto endurecido rugoso)

### 15.8.4.2 Otros Metodos
- Llaves de cortante
- Conectores mecanicos

---

## Resumen de Requisitos

| Parametro | Requisito |
|-----------|-----------|
| fc' junta / fc' columna | >= **0.7** |
| As,dowel minimo | >= **0.005*Ag** |
| Dowels minimos | **4 barras** |
| Espaciamiento transversal | <= menor de (d/4, 6 in.) |

### Transferencia de Fuerzas

| Fuerza | Metodo |
|--------|--------|
| Compresion | Aplastamiento + dowels |
| Tension | Refuerzo continuo o empalmes |
| Cortante | Friccion, llaves, conectores |

---

*ACI 318-25 Secciones 15.6-15.8*
