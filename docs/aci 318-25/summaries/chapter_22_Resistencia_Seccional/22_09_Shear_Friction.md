# 22.9 FRICCION POR CORTANTE (SHEAR FRICTION)

## 22.9.1 General

### 22.9.1.1 Aplicabilidad
Aplica donde es apropiado considerar transferencia de cortante a traves de un plano dado:
- Grieta existente o potencial
- Interfaz entre materiales diferentes
- Interfaz entre concretos colocados en diferentes tiempos

### Concepto de Friccion por Cortante (R22.9.1.1)

1. Se asume que una grieta se formara en el plano de cortante
2. Se proporciona refuerzo a traves de la grieta para resistir deslizamiento
3. Al deslizarse, las caras rugosas se separan, tensionando el refuerzo
4. El refuerzo en tension proporciona fuerza de sujecion **Avf*fy**
5. El cortante se resiste por friccion entre caras, resistencia al corte de protuberancias, y accion de pasador

**Advertencia:** Requisitos de 22.9 basados en ensayos monotonicos. Pueden ser no conservadores para interfaces sismicas con degradacion por reversiones.

## 22.9.3 Resistencia de Diseno

```
phi*Vn >= Vu                            (Ec. 22.9.3.1)
```

## 22.9.4 Resistencia Nominal

### 22.9.4.2 Refuerzo Perpendicular al Plano de Cortante

```
Vn = mu * (Avf*fy + Nu)                 (Ec. 22.9.4.2)
```

### Tabla 22.9.4.2 - Coeficientes de Friccion

| Condicion de Superficie de Contacto | mu |
|-------------------------------------|-----|
| **(a)** Concreto colocado monoliticamente | **1.4*lambda** |
| **(b)** Concreto contra concreto endurecido, limpio, rugosidad intencional ~1/4 in. | **1.0*lambda** |
| **(c)** Concreto contra concreto endurecido, limpio, **sin** rugosidad intencional | **0.6** |
| **(d)** Concreto contra acero estructural laminado, limpio, cortante por studs o barras soldadas | **0.7*lambda** |

**Notas:**
- lambda = 1.0 para concreto de peso normal
- Para concreto liviano: lambda segun 19.2.4, pero <= 0.85
- **Cambio ACI 318-25:** Se elimino lambda de caso (c)

### 22.9.4.3 Refuerzo Inclinado al Plano de Cortante

Si el cortante induce **tension** en el refuerzo:
```
Vn = Avf*fy*(mu*sin(alpha) + cos(alpha)) + mu*Nu    (Ec. 22.9.4.3)
```

**Nota:** Si el cortante induce **compresion** en el refuerzo, friccion por cortante **no aplica** (Vn = 0).

### Tabla 22.9.4.4 - Vn Maximo

| Condicion | Vn Maximo |
|-----------|-----------|
| **Concreto de peso normal, monolitico o rugoso ~1/4 in.** | Menor de: 0.2*f'c*Ac, (480 + 0.08*f'c)*Ac, 1600*Ac |
| **Otros casos** | Menor de: 0.2*f'c*Ac, 800*Ac |

### 22.9.4.5 Tension a Traves del Plano
El area de refuerzo para resistir tension factorizada neta debe **sumarse** al area requerida para friccion por cortante.

## 22.9.5 Detallado del Refuerzo de Friccion

### 22.9.5.1 Desarrollo del Refuerzo
El refuerzo que cruza el plano de cortante debe desarrollar **fy en tension** a ambos lados del plano.

### 22.9.5.2 Barras U Invertidas en Losas Compuestas

| Requisito | Especificacion |
|-----------|----------------|
| (a) Tamano de barra U | <= **No. 7** |
| (b) Extension de rama transversal | >= **5*db** sobre la interfaz |
| (c) Esquinas superiores | Encierran una barra o toron |
| (d) Espaciamiento entre ramas | >= **8*db** en ambas direcciones |
| (e) Ramas verticales debajo de interfaz | Desarrollan fy segun 25.4.2 |

---

*ACI 318-25 Seccion 22.9*
