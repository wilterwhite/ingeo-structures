# 18.8 NUDOS DE PORTICOS ESPECIALES

## 18.8.1 Alcance

### 18.8.1.1 Aplicabilidad
Aplica a nudos viga-columna de porticos momento especiales del SFRS.

---

## 18.8.2 General

### 18.8.2.1 Fuerzas en Refuerzo de Viga
Calcular fuerzas asumiendo esfuerzo de tension **= 1.25fy** (no 1.0fy como en nudos intermedios).

### 18.8.2.2 Desarrollo de Refuerzo Terminado
Refuerzo longitudinal terminado en nudo debe:
- Extenderse a la **cara lejana del nucleo del nudo**
- Desarrollarse en tension segun **18.8.5**

### 18.8.2.3 Profundidad del Nudo
Si refuerzo longitudinal de viga **pasa a traves** del nudo, la profundidad **h** del nudo (paralela al refuerzo) debe ser al menos el **mayor de (a)-(c)**:

| Parametro | Requisito |
|-----------|-----------|
| (a) Grade 60 | **(20/λ) db** de la barra mas grande (λ=0.75 liviano, 1.0 otros) |
| (b) Grade 80 | **26 db** de la barra mas grande |
| (c) Relacion de aspecto | **h/2** de cualquier viga que genera cortante en el nudo |

**18.8.2.3.1** Concreto con refuerzo Grade 80 en nudos debe ser **normalweight**.

---

## 18.8.3 Refuerzo Transversal

### 18.8.3.1 Requisitos Generales
Satisfacer **18.7.5.2, 18.7.5.3, 18.7.5.4 y 18.7.5.7**, excepto segun 18.8.3.2.

### 18.8.3.2 Reduccion con Vigas en 4 Lados
Si vigas enmarcan en los **4 lados** del nudo y cada **bw ≥ 0.75c**:
- Cantidad de refuerzo (18.7.5.4) puede **reducirse 50%**
- Espaciamiento (18.7.5.3) puede **aumentarse a 6"** dentro de h de la viga mas baja

### 18.8.3.3 Refuerzo de Viga Fuera del Nucleo
Si refuerzo longitudinal de viga pasa **fuera del nucleo de columna**:
- Debe confinarse con refuerzo transversal que pase a traves de la columna
- Espaciamiento segun **18.6.4.4**
- Requisitos de **18.6.4.2 y 18.6.4.3**
- No requerido si una viga transversal proporciona el confinamiento

---

## 18.8.4 Resistencia al Cortante

### 18.8.4.1 Fuerza de Cortante del Nudo
Vu calculado en un plano a **media altura del nudo** usando:
- Fuerzas de viga (T y C) segun **18.8.2.1** (1.25fy)
- Cortante de columna consistente con **Mpr** de vigas

### 18.8.4.2 Factor φ
Segun **21.2.4.4**.

### 18.8.4.3 Resistencia Nominal Vn

**Tabla 18.8.4.3 - Resistencia Nominal al Cortante del Nudo Vn**

| Columna | Viga en direccion de Vu | Confinamiento (15.5.2.5) | Vn (lb) |
|---------|------------------------|--------------------------|---------|
| Continua o cumple 15.5.2.3 | Continua o cumple 15.5.2.4 | Confinado | **20λ√f'c Aj** |
| | | No confinado | **15λ√f'c Aj** |
| | Otra | Confinado | **15λ√f'c Aj** |
| | | No confinado | **12λ√f'c Aj** |
| Otra | Continua o cumple 15.5.2.4 | Confinado | **15λ√f'c Aj** |
| | | No confinado | **12λ√f'c Aj** |
| | Otra | Confinado | **12λ√f'c Aj** |
| | | No confinado | **8λ√f'c Aj** |

- λ = 0.75 (liviano), 1.0 (normalweight)
- Aj segun **15.5.2.2**

---

## 18.8.5 Longitud de Desarrollo en Tension

### 18.8.5.1 Barras con Gancho Estandar (No. 3 - No. 11)

```
ℓdh = fy*db / (65λ√f'c)              [Eq. 18.8.5.1]
```

**Minimos:**

| Concreto | Minimo |
|----------|--------|
| Normalweight | ≥ **max(8db, 6")** |
| Lightweight | ≥ **max(10db, 7.5")** |

- λ = 0.75 (liviano), 1.0 (otros)
- Gancho debe ubicarse dentro del **nucleo confinado** de columna o elemento de borde
- Gancho doblado **hacia el nudo**

### 18.8.5.2 Barras con Cabeza
Barras con cabeza (segun 20.2.1.6) deben desarrollar **1.25fy** en tension segun **25.4.4** (sustituyendo 1.25fy por fy).

### 18.8.5.3 Barras Rectas (No. 3 - No. 11)
ℓd debe ser al menos el **mayor de (a) y (b)**:

| Condicion | ℓd |
|-----------|-----|
| (a) Concreto bajo la barra ≤ 12" | **2.5 * ℓdh** (de 18.8.5.1) |
| (b) Concreto bajo la barra > 12" | **3.25 * ℓdh** (de 18.8.5.1) |

### 18.8.5.4 Barras Rectas Terminadas en Nudo
Deben pasar a traves del **nucleo confinado**. Cualquier porcion de ℓd fuera del nucleo confinado debe **multiplicarse por 1.6**.

```
ℓdm = 1.6*ℓd - 0.6*ℓdc
```
Donde ℓdc = longitud dentro del concreto confinado.

### 18.8.5.5 Refuerzo con Epoxico
Multiplicar longitudes de 18.8.5.1, 18.8.5.3 y 18.8.5.4 por factores de **25.4.2.5 o 25.4.3.2**.

---

*ACI 318-25 Seccion 18.8*
