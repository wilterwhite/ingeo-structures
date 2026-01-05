# ACI 318-25 - 10.4-10.5 RESISTENCIA

---

## 10.4 RESISTENCIA REQUERIDA

### 10.4.1 General

| Requisito | Referencia |
|-----------|------------|
| Combinaciones de carga | Capitulo 5 |
| Analisis estructural | Capitulo 6 |
| Efectos de esbeltez | 6.6 |

### 10.4.2 Fuerza Axial y Momento
**10.4.2.1** Considerar Pu y Mu simultaneos para cada combinacion de carga aplicable.

> **NOTA**: La combinacion critica puede no ser evidente. Verificar todas las combinaciones, no solo las de Pu,max y Mu,max.

---

## 10.5 RESISTENCIA DE DISENO

### 10.5.1 General
Para cada combinacion de carga:
```
phi*Pn >= Pu
phi*Mn >= Mu
phi*Vn >= Vu
phi*Tn >= Tu
```

Considerar interaccion entre efectos de carga.

### 10.5.1.2 Factor de Reduccion (φ)

| Tipo de Seccion | φ |
|-----------------|---|
| Controlada por compresion (estribos) | **0.65** |
| Controlada por compresion (espirales) | **0.75** |
| Zona de transicion | 0.65 a 0.90 (interpolar) |
| Controlada por tension | 0.90 |

Ver **21.2** para definicion de zonas.

### 10.5.2 Resistencia Axial Maxima (Pn,max)

#### Columnas con Estribos
```
Pn,max = 0.80 * [0.85*fc'*(Ag - Ast) + fy*Ast]
```

#### Columnas con Espirales
```
Pn,max = 0.85 * [0.85*fc'*(Ag - Ast) + fy*Ast]
```

**Nota:** Factor adicional de 0.80/0.85 para excentricidad accidental minima.

### 10.5.3 Fuerza Axial y Momento
Pn y Mn segun **22.4** (Diagrama de interaccion).

### 10.5.4 Cortante
Vn segun **22.5**.

#### Vc en Columnas (con carga axial de compresion)
```
Vc = 2*(1 + Nu/(2000*Ag)) * λ*√fc' * bw*d
```

### 10.5.5 Torsion
Si Tu >= phi*Tth (umbral de 22.7), considerar torsion segun **Capitulo 9**.

> **NOTA**: La torsion en columnas de edificios es tipicamente despreciable.

---

## Resumen de Factores φ para Columnas

| εt | Tipo de Control | φ (estribos) | φ (espirales) |
|----|-----------------|--------------|---------------|
| εt <= εty | Compresion | 0.65 | 0.75 |
| εty < εt < εty+0.003 | Transicion | 0.65-0.90 | 0.75-0.90 |
| εt >= εty + 0.003 | Tension | 0.90 | 0.90 |

Donde εty = fy/Es (0.002 para Grado 60).

---

*ACI 318-25 Secciones 10.4-10.5*
