# ACI 318-25 - 7.6 LIMITES DE REFUERZO

---

## 7.6.1 Refuerzo Minimo a Flexion (No Presforzadas)

### 7.6.1.1 Area Minima
```
As,min = 0.0018 * Ag
```

**Nota:** Igual al requisito de temperatura y contracción (24.4.3.2), pero debe colocarse cerca de la cara en tensión.

---

## 7.6.2 Refuerzo Minimo a Flexion (Presforzadas)

### 7.6.2.1 Losas con Tendones Adheridos
La cantidad total de As + Aps debe ser adecuada para desarrollar:
```
Carga factorada >= 1.2 * Carga de agrietamiento
```
Calculada con fr según 19.2.3.

### 7.6.2.2 Excepcion
Si resistencia de diseño a flexión y cortante >= **2 veces** la requerida, no aplica 7.6.2.1.

### 7.6.2.3 Losas con Tendones No Adheridos
```
As,min >= 0.004 * Act
```

Donde:
- **Act** = área entre la cara en tensión y el centroide de la sección bruta

---

## 7.6.3 Refuerzo Minimo a Cortante

### 7.6.3.1 Requisito General
Proporcionar **Av,min** en todas las regiones donde:
```
Vu > φVc
```

### 7.6.3.1 Losas Hollow-Core (h > 12.5 in.)
Para losas hollow-core presforzadas prefabricadas sin topping y h > 12.5 in.:
```
Av,min requerido cuando: Vu > 0.5*φ*Vcw
```

### 7.6.3.2 Excepcion por Ensayo
Si se demuestra por ensayo que se pueden desarrollar Mn y Vn requeridos, no aplica 7.6.3.1.

### 7.6.3.3 Cantidad de Av,min
Si se requiere refuerzo de cortante:
```
Av,min según 9.6.3.4
```

---

## 7.6.4 Refuerzo Minimo de Temperatura y Contraccion

### 7.6.4.1 Requisito General
Proporcionar refuerzo según **24.4**.

### 7.6.4.2 Presforzado para T&S

#### 7.6.4.2.1 Construccion Monolitica Viga-Losa
Area bruta de concreto = área de viga + área de losa tributaria (hasta mitad de distancia a vigas adyacentes).

#### 7.6.4.2.2 Losas sobre Muros o No Monoliticas
Area bruta = sección de losa tributaria al tendón.

#### 7.6.4.2.3 Minimo un Tendon
Al menos **un tendón** requerido entre caras de vigas o muros adyacentes.

---

## Resumen de As,min por Tipo de Losa

| Tipo de Losa | As,min | Referencia |
|--------------|--------|------------|
| No presforzada | 0.0018*Ag | 7.6.1.1 |
| Presforzada (adherida) | Para φMn >= 1.2*Mcr | 7.6.2.1 |
| Presforzada (no adherida) | 0.004*Act | 7.6.2.3 |

---

*ACI 318-25 Seccion 7.6*
