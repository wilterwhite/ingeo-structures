# 22.8 APLASTAMIENTO (BEARING)

## 22.8.1 General

### 22.8.1.1 Aplicabilidad
Aplica al calculo de resistencia al aplastamiento de miembros de concreto.

### 22.8.1.2 Excepcion
**No aplica** a zonas de anclaje post-tensado (usar 25.9).

## 22.8.3 Resistencia de Diseno

### 22.8.3.1 Verificacion
```
phi*Bn >= Bu                            (Ec. 22.8.3.1)
```

### Tabla 22.8.3.2 - Resistencia Nominal al Aplastamiento

| Geometria | Bn |
|-----------|-----|
| **Superficie de apoyo mas ancha que area cargada en todos los lados** | Menor de (a) y (b): |
| | (a) sqrt(A2/A1) * (0.85*f'c*A1) |
| | (b) 2 * (0.85*f'c*A1) |
| **Otros casos** | (c) 0.85*f'c*A1 |

### Definiciones

| Parametro | Definicion |
|-----------|------------|
| **A1** | Area cargada (no mayor que area de placa de apoyo) |
| **A2** | Area de la base inferior del mayor tronco de piramide, cono o cuna contenido dentro del soporte |

### Geometria del Tronco (Frustum)
- Base superior = area cargada A1
- Lados inclinados: **1 vertical : 2 horizontal** (45°)
- A2 se mide en el plano inferior del soporte

---

*ACI 318-25 Seccion 22.8*
