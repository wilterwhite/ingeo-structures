# ACI 318-25 - Seccion 9.5: RESISTENCIA DE DISENO

---

## 9.5.1 General

### 9.5.1.1 Requisito Fundamental

Para cada combinacion de carga factorizada aplicable:

**phi Sn >= U**

Incluyendo:
- **(a)** phi Mn >= Mu
- **(b)** phi Vn >= Vu
- **(c)** phi Tn >= Tu
- **(d)** phi Pn >= Pu

### 9.5.1.2 Factor de Reduccion

phi segun Seccion 21.2

---

## 9.5.2 Momento

### Calculo de Mn

| Condicion | Calculo de Mn |
|-----------|---------------|
| Pu < 0.10 f'c Ag | Segun 22.3 |
| Pu >= 0.10 f'c Ag | Segun 22.4 |

### 9.5.2.3 Tendones Externos

Para vigas presforzadas, tendones externos se consideran como **no adheridos**.

---

## 9.5.3 Cortante

| Seccion | Requisito |
|---------|-----------|
| 9.5.3.1 | Vn segun 22.5 |
| 9.5.3.2 | Para vigas compuestas, Vnh segun 16.4 |

### Resistencia Nominal a Cortante

```
Vn = Vc + Vs
```

Donde:
- Vc = Contribucion del concreto
- Vs = Contribucion del refuerzo transversal

---

## 9.5.4 Torsion

### 9.5.4.1 Torsion Despreciable

Si Tu < phi Tth (segun 22.7), se permite despreciar efectos torsionales:
- No se requieren los minimos de 9.6.4
- No se requiere detallado de 9.7.5 y 9.7.6.3

### 9.5.4.2 Resistencia Nominal

Tn segun 22.7

### 9.5.4.3 Adicion de Refuerzo

Refuerzo longitudinal y transversal para torsion se **suma** al requerido para Vu, Mu y Pu.

### 9.5.4.4 Adicion de Refuerzo Transversal

```
Total(Av+t/s) = Av/s + 2At/s
```

### 9.5.4.5 Reduccion de Refuerzo Longitudinal

Se permite reducir refuerzo longitudinal torsional en zona de compresion por flexion:

```
Reduccion = Mu / (0.9 d fy)
```

---

## Procedimientos Alternativos de Diseno por Torsion

| Seccion | Condicion | Requisito |
|---------|-----------|-----------|
| 9.5.4.6 | h/bt >= 3, secciones solidas | Procedimiento alternativo verificado por ensayos |
| 9.5.4.7 | h/bt >= 4.5, secciones precoladas solidas | Procedimiento alternativo con refuerzo de alma abierta |

---

## Factores de Reduccion de Resistencia (phi)

| Tipo de Solicitacion | phi |
|---------------------|-----|
| Flexion (controlado por tension) | 0.90 |
| Cortante | 0.75 |
| Torsion | 0.75 |

---

## Referencias

| Tema | Seccion |
|------|---------|
| Factores phi | 21.2 |
| Resistencia a flexion | 22.3, 22.4 |
| Resistencia a cortante | 22.5 |
| Resistencia a torsion | 22.7 |
| Vigas compuestas | 16.4 |

---

*ACI 318-25 Seccion 9.5 - Resistencia de Diseno*
