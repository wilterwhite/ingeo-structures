# 22.6 RESISTENCIA A CORTANTE BIDIRECCIONAL

## 22.6.1 General

### 22.6.1.2 Sin Refuerzo de Cortante
```
vn = vc                                  (Ec. 22.6.1.2)
```

### 22.6.1.3 Con Refuerzo de Cortante
```
vn = vc + vs                             (Ec. 22.6.1.3)
```

## 22.6.2 Peralte Efectivo

| Condicion | d |
|-----------|---|
| General | Promedio de d en dos direcciones ortogonales |
| Pretensados | >= 0.8h |

## 22.6.3 Limites de Materiales

| Parametro | Limite |
|-----------|--------|
| sqrt(f'c) para vc | **100 psi** |
| fyt para vs | Limites de 20.2.2.4 |

## 22.6.4 Secciones Criticas

### 22.6.4.1 Ubicacion
Perimetro bo minimo, no mas cerca que **d/2** de:
- (a) Bordes o esquinas de columnas, cargas concentradas o areas de reaccion
- (b) Cambios de espesor (capiteles, drop panels, shear caps)

### 22.6.4.1.1-2 Simplificaciones
- Columnas cuadradas/rectangulares: permitido asumir lados rectos
- Columnas circulares/poligonales: permitido asumir columna cuadrada de area equivalente

### 22.6.4.3 Aberturas
Si abertura esta a menos de **4h** de la columna:
- Porcion de bo entre lineas tangentes desde centroide de columna a limites de abertura es **inefectiva**

## 22.6.5 vc para Miembros sin Refuerzo de Cortante

### Tabla 22.6.5.2 - Cortante Bidireccional vc

| vc | Formula |
|----|---------|
| **(a)** | 4*lambda_s*lambda*sqrt(f'c) |
| **(b)** | (2 + 4/beta)*lambda_s*lambda*sqrt(f'c) |
| **(c)** | (2 + alpha_s*d/bo)*lambda_s*lambda*sqrt(f'c) |

**vc = menor de (a), (b) y (c)**

Donde:
- lambda_s = factor de tamano (22.5.5.1.3)
- beta = relacion lado largo / lado corto de columna
- alpha_s = 40 (interior), 30 (borde), 20 (esquina)

## 22.6.5.5 vc para Miembros Pretensados (si cumple 22.6.5.4)

Condiciones:
- (a) Refuerzo adherido segun 8.6.2.3 y 8.7.5.3
- (b) Columna a >= 4h de borde discontinuo
- (c) fpc >= 125 psi en cada direccion

```
vc = menor de:
(a) 3.5*lambda*sqrt(f'c) + 0.3*fpc + Vp/(bo*d)    (Ec. 22.6.5.5a)
(b) (1.5 + alpha_s*d/bo)*lambda*sqrt(f'c) + 0.3*fpc + Vp/(bo*d)    (Ec. 22.6.5.5b)
```

Limites: fpc <= 500 psi; sqrt(f'c) <= 70 psi

## 22.6.6 vc para Miembros con Refuerzo de Cortante

### Tabla 22.6.6.1 - vc para Miembros con Refuerzo de Cortante

| Tipo de Refuerzo | Seccion Critica | vc |
|------------------|-----------------|-----|
| **Estribos** | Todas | 2*lambda_s*lambda*sqrt(f'c) |
| **Studs** | Segun 22.6.4.1 | Menor de: 3*lambda_s*lambda*sqrt(f'c), (2+4/beta)*lambda_s*lambda*sqrt(f'c), (2+alpha_s*d/bo)*lambda_s*lambda*sqrt(f'c) |
| **Studs** | Segun 22.6.4.2 | 2*lambda_s*lambda*sqrt(f'c) |

### 22.6.6.2 Factor de Tamano lambda_s = 1.0

Se permite tomar lambda_s = 1.0 si:
- **(a) Estribos:** Disenados segun 8.7.6 y Av/s >= 2*sqrt(f'c)*bo/fyt
- **(b) Studs lisos:** Longitud de vastago <= 10 in., segun 8.7.7 y Av/s >= 2*sqrt(f'c)*bo/fyt

### Tabla 22.6.6.3 - Esfuerzo Maximo vu

| Tipo de Refuerzo | vu Maximo (seccion 22.6.4.1) |
|------------------|------------------------------|
| Estribos | **phi*6*sqrt(f'c)** |
| Studs con cabeza | **phi*8*sqrt(f'c)** |

## 22.6.7 vs por Estribos

### 22.6.7.1 Requisitos
Estribos permitidos en losas y zapatas si: d >= **6 in.** y d >= **16*db**

### 22.6.7.2 Calculo de vs
```
vs = Av * fyt / (bo * s)                (Ec. 22.6.7.2)
```

## 22.6.8 vs por Studs con Cabeza

### 22.6.8.2 Calculo de vs
```
vs = Av * fyt / (bo * s)                (Ec. 22.6.8.2)
```

### 22.6.8.3 Refuerzo Minimo
```
Av/s >= 2*sqrt(f'c) * bo / fyt          (Ec. 22.6.8.3)
```

---

*ACI 318-25 Seccion 22.6*
