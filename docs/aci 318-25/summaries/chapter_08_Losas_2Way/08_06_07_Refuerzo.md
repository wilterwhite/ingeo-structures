# ACI 318-25 - 8.6-8.7 LIMITES Y DETALLADO DEL REFUERZO

---

## 8.6 LIMITES DE REFUERZO

### 8.6.1 Refuerzo Minimo a Flexion (No Presforzadas)

**8.6.1.1:**
```
As,min = 0.0018 * Ag
```

En cada direccion, para losas no presforzadas.

### 8.6.2 Refuerzo Minimo a Flexion (Presforzadas)

#### 8.6.2.1 Tendones Adheridos
Cantidad total de As + Aps debe desarrollar:
```
Carga factorada >= 1.2 * Carga de agrietamiento
```

#### 8.6.2.2 Excepcion
Si φMn y φVn >= **2 veces** los requeridos, no aplica 8.6.2.1.

#### 8.6.2.3 Tendones No Adheridos
```
As,min >= 0.004 * Act
```

### 8.6.3 Refuerzo en Aberturas

En secciones criticas de cortante bidireccional, si apertura esta dentro de 10h de columna:

| Area de abertura | Accion |
|------------------|--------|
| <= 0.25 * bo * d | Reducir bo proporcionalmente |
| > 0.25 * bo * d | Requiere analisis especial |

---

## 8.7 DETALLADO DEL REFUERZO

### 8.7.1 General

| Requisito | Referencia |
|-----------|------------|
| Recubrimiento | 20.5.1 |
| Longitud de desarrollo | 25.4 |
| Empalmes | 25.5 |

### 8.7.2 Espaciamiento

#### 8.7.2.1 Espaciamiento Minimo
Segun **25.2**.

#### 8.7.2.2 Espaciamiento Maximo

| Tipo | s_max |
|------|-------|
| Refuerzo principal | **menor de (2h, 18 in.)** |
| En secciones criticas | Ver 8.7.6 |

### 8.7.3 Extension del Refuerzo

**8.7.3.1:** Extender mas alla del punto donde ya no se requiere:
```
Extension >= mayor de (d, 12*db)
```

### 8.7.4 Terminacion del Refuerzo

#### 8.7.4.1 Refuerzo Positivo
| Ubicacion | Requisito |
|-----------|-----------|
| Apoyo discontinuo | Extender hasta borde de apoyo |
| Apoyo continuo | Al menos **1/4** del As maximo debe extenderse al apoyo |

#### 8.7.4.2 Refuerzo Negativo
- Al menos **1/3** debe extenderse mas alla del punto de inflexion:
```
>= mayor de (d, 12*db, ln/16)
```

### 8.7.5 Colocacion del Refuerzo en Bandas

| Banda | % del momento |
|-------|---------------|
| Banda de columna | 100% del momento negativo + porcion del positivo |
| Banda central | Porcion del momento positivo |

### 8.7.6 Refuerzo en Conexiones Losa-Columna

#### 8.7.6.1 Requisito General
Concentrar refuerzo en el ancho efectivo (c2 + 3h o similar).

#### 8.7.6.2 Conexiones Interiores

| Parametro | Requisito |
|-----------|-----------|
| As minimo en banda c2+3h | As para γf*Msc |
| Espaciamiento | <= 2h |

#### 8.7.6.3 Conexiones de Borde y Esquina
Colocar refuerzo perpendicular al borde libre dentro del ancho efectivo.

### 8.7.7 Integridad Estructural

**8.7.7.1:** Al menos **2 barras** en cada direccion deben:
- Pasar continuas a traves de la columna
- O desarrollarse para **1.25*fy** a cada lado de la columna

**8.7.7.2:** Empalmes cerca de apoyos:
- Empalmes mecanicos, soldados, o de traslape Clase B

---

## Resumen de Espaciamientos

| Refuerzo | s_max |
|----------|-------|
| Principal (general) | menor de (2h, 18 in.) |
| En banda de columna | <= 2h |
| Zona de transferencia | Variable segun 8.7.6 |

---

*ACI 318-25 Secciones 8.6-8.7*
