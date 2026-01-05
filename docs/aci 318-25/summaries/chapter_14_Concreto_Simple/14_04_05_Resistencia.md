# ACI 318-25 - 14.4-14.5 RESISTENCIA

---

## 14.4 RESISTENCIA REQUERIDA

### 14.4.1 General

| Requisito | Referencia |
|-----------|------------|
| Combinaciones de carga | Capitulo 5 |
| Procedimientos de analisis | Capitulo 6 |

### 14.4.2 Momentos y Cortantes Factorados

**14.4.2.1** Para muros de concreto simple continuamente soportados:
- Mu y Vu se permiten calcular asumiendo que el miembro actua como **miembro simplemente apoyado**

**14.4.2.2** Longitud del claro efectivo:
```
leff = ln + h   (no exceder la distancia centro a centro de apoyos)
```

Donde:
- **ln** = luz libre
- **h** = espesor del muro

---

## 14.5 RESISTENCIA DE DISENO

### 14.5.1 General

**14.5.1.1** Para cada combinacion de carga:
```
φSn >= U
```

**14.5.1.2** Factor de reduccion:
```
φ = 0.60   (para todo concreto simple)
```

### 14.5.2 Resistencia a Compresion Axial

#### 14.5.2.1 Pedestales y Muros de Carga

```
Pn = 0.60 * fc' * A1 * [1 - (lc/32h)²]
```

Donde:
- **A1** = area cargada
- **lc** = altura efectiva (k*lu)
- **h** = espesor del muro o dimension menor del pedestal

#### 14.5.2.2 Factor de Longitud Efectiva k

| Condicion de Borde | k |
|-------------------|---|
| Arriostrado ambos extremos | **0.8** |
| Arriostrado un extremo | **1.0** |
| No arriostrado | **2.0** |

### 14.5.3 Resistencia al Aplastamiento (Bearing)

```
Bn = 0.85 * fc' * A1 * √(A2/A1)
```

Donde:
- **A1** = area cargada
- **A2** = area de la base del tronco de piramide con pendientes 1:2
- **√(A2/A1) <= 2**

### 14.5.4 Resistencia a Flexion

#### 14.5.4.1 Momento Nominal

```
Mn = 5 * λ * √fc' * Sm
```

Donde:
- **Sm** = modulo de seccion elastico = bh²/6
- **λ** = factor para concreto liviano

### 14.5.5 Resistencia a Cortante

#### 14.5.5.1 Cortante en Una Direccion

```
Vn = (4/3) * λ * √fc' * bw * h
```

#### 14.5.5.2 Cortante en Dos Direcciones (Punzonamiento)

```
Vn = (4/3) * λ * √fc' * bo * h
```

Donde:
- **bo** = perimetro de seccion critica
- Seccion critica a **h/2** de la cara de columna

#### 14.5.5.3 Limite de √fc'
```
√fc' <= 100 psi
```

---

## Resumen de Formulas

| Solicitacion | Formula | φ |
|--------------|---------|---|
| Compresion axial | Pn = 0.60*fc'*A1*[1-(lc/32h)²] | 0.60 |
| Aplastamiento | Bn = 0.85*fc'*A1*√(A2/A1) | 0.60 |
| Flexion | Mn = 5*λ*√fc'*Sm | 0.60 |
| Cortante 1-dir | Vn = (4/3)*λ*√fc'*bw*h | 0.60 |
| Cortante 2-dir | Vn = (4/3)*λ*√fc'*bo*h | 0.60 |

---

## Factor φ Unico

```
φ = 0.60   (para todas las solicitaciones en concreto simple)
```

---

*ACI 318-25 Secciones 14.4-14.5*
