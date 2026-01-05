# 22.5 RESISTENCIA A CORTANTE UNIDIRECCIONAL

## 22.5.1 General

### 22.5.1.1 Resistencia Nominal
```
Vn = Vc + Vs                              (Ec. 22.5.1.1)
```

### 22.5.1.2 Limite de Dimensiones
```
Vu <= phi*(Vc + 8*sqrt(f'c)*bw*d)         (Ec. 22.5.1.2)
```
**Proposito:** Controlar agrietamiento en servicio y minimizar falla por compresion diagonal.

### Referencias para Calculo de Vc

| Miembro | Seccion |
|---------|---------|
| No pretensado | 22.5.5 |
| Pretensado | 22.5.6 o 22.5.7 |

### 22.5.1.5 Factor Lambda
Para Vc, Vci, Vcw: lambda segun **19.2.4** (concreto liviano).

### 22.5.1.7-8 Consideraciones Adicionales
- Debe considerarse el efecto de **aberturas** en Vn
- Debe considerarse el efecto de **tension axial** por flujo plastico y retraccion en Vc

## 22.5.1.10-11 Interaccion de Cortante Biaxial

Se puede ignorar la interaccion si:
```
(a) Vu,x / (phi*Vn,x) <= 0.5
(b) Vu,y / (phi*Vn,y) <= 0.5
```

Si ambas relaciones > 0.5:
```
Vu,x/(phi*Vn,x) + Vu,y/(phi*Vn,y) <= 1.5    (Ec. 22.5.1.11)
```

## 22.5.2 Supuestos Geometricos

| Condicion | d | bw |
|-----------|---|----|
| Columnas rectangulares | 0.8h | - |
| Secciones circulares | 0.8*diametro | diametro (solidas) |
| Secciones circulares huecas | 0.8*diametro | 2*espesor |
| Pretensados | >= 0.8h | - |

## 22.5.3 Limites de Materiales

| Parametro | Limite | Excepcion |
|-----------|--------|-----------|
| sqrt(f'c) para Vc | **100 psi** | 22.5.3.2 |
| sqrt(f'c) > 100 psi | Permitido | Si Av,min cumple 9.6.3.4 o 9.6.4.2 |
| fy, fyt para Vs | Limites de 20.2.2.4 | fy <= 60,000 psi |

## 22.5.5 Vc para Miembros No Pretensados

### Tabla 22.5.5.1 - Vc para Miembros No Pretensados

| Criterio | Vc |
|----------|-----|
| **Av >= Av,min** | Cualquiera de: |
| | (a) [2*lambda*sqrt(f'c) + Nu/(6Ag)] * bw*d |
| | (b) [8*lambda*(rho_w)^(1/3)*sqrt(f'c) + Nu/(6Ag)] * bw*d |
| **Av < Av,min** | (c) [8*lambda_s*lambda*(rho_w)^(1/3)*sqrt(f'c) + Nu/(6Ag)] * bw*d |

**Notas:**
- Nu positivo para compresion, negativo para tension
- Vc no debe ser menor que cero
- Nu/(6Ag) no debe exceder 0.05*f'c

### 22.5.5.1.1 Limites de Vc
```
Vc,max = 5*lambda*sqrt(f'c)*bw*d
Vc,min = lambda*sqrt(f'c)*bw*d     (excepto tension axial neta o 18.6.5.2/18.7.6.2.1)
```

### 22.5.5.1.3 Factor de Efecto de Tamano (Size Effect)
```
lambda_s = 2 / (1 + d/10) <= 1.0     (Ec. 22.5.5.1.3)
```
**Nota:** d en pulgadas.

## 22.5.6 Vc para Miembros Pretensados

### 22.5.6.2 Vc como menor de Vci y Vcw

#### Vci - Resistencia a Agrietamiento Flexion-Cortante
```
Vci = 0.6*lambda*sqrt(f'c)*bw*dp + Vd + (Vi*Mcre)/Mmax    (Ec. 22.5.6.2.1a)
```

Minimo de Vci:
- Si Aps*fse < 0.4*(Aps*fpu + As*fy): Vci >= 1.7*lambda*sqrt(f'c)*bw*d
- Si Aps*fse >= 0.4*(Aps*fpu + As*fy): Vci >= 2*lambda*sqrt(f'c)*bw*d

Momento de agrietamiento:
```
Mcre = (I/yt)*(6*lambda*sqrt(f'c) + fpe - fd)    (Ec. 22.5.6.2.1d)
```

#### Vcw - Resistencia a Agrietamiento Web-Cortante
```
Vcw = (3.5*lambda*sqrt(f'c) + 0.3*fpc)*bw*dp + Vp    (Ec. 22.5.6.2.2)
```
Donde dp >= 0.8h y Vp = componente vertical del preesfuerzo efectivo.

## 22.5.8 Refuerzo a Cortante Unidireccional

### 22.5.8.1 Requisito
```
Vs >= Vu/phi - Vc                        (Ec. 22.5.8.1)
```

### 22.5.8.5.3 Vs para Estribos Perpendiculares
```
Vs = Av*fyt*d / s                        (Ec. 22.5.8.5.3)
```

### 22.5.8.5.4 Vs para Estribos Inclinados
```
Vs = Av*fyt*(sin(alpha) + cos(alpha))*d / s    (Ec. 22.5.8.5.4)
```
Donde alpha >= 45 grados.

---

*ACI 318-25 Seccion 22.5*
