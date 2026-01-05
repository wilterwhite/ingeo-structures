# 18.12 DIAFRAGMAS Y CERCHAS

## 18.12.1 Alcance

| Seccion | Aplicabilidad |
|---------|---------------|
| 18.12.1.1 | Diafragmas y colectores en SDC D, E, F |
| 18.12.1.2 | Diafragmas prefabricados en SDC C, D, E, F |
| 18.12.1.3 | Cerchas estructurales en SDC D, E, F |

---

## 18.12.6 Espesor Minimo

| Tipo | Espesor Minimo |
|------|----------------|
| Losas de concreto | **2"** |
| Compuestas sobre prefabricado | **2"** |
| No compuestas sobre prefabricado | **2-1/2"** |

---

## 18.12.7 Refuerzo

### 18.12.7.1 Requisitos Generales
- Espaciamiento maximo: **18"** cada direccion
- Malla soldada sobre prefabricado: espaciamiento ≥ **10"**
- Refuerzo distribuido uniformemente en plano de cortante

### 18.12.7.2 Tendones Adheridos
- Esfuerzo por sismo ≤ **60,000 psi**

### 18.12.7.3 Desarrollo
- Todo refuerzo desarrollado para **fy en tension**

### 18.12.7.4 Empalmes Mecanicos
- Clase **G o S** requerida en conexion diafragma-elementos verticales

### 18.12.7.5 Colectores - Esfuerzo Promedio
- Esfuerzo de tension promedio ≤ **φfy** con **fy ≤ 60,000 psi**

### 18.12.7.6 Colectores - Confinamiento

**Requiere refuerzo transversal cuando σc > 0.2f'c** (o 0.5f'c si amplificado por Ωo)

### Tabla 18.12.7.6 - Refuerzo Transversal para Colectores

| Tipo | Formula |
|------|---------|
| Ash/sbc (rectangular) | **0.09 * f'c/fyt** |
| ρs (espiral) | Mayor de: **0.45(Ag/Ach - 1)(f'c/fyt)** y **0.12(f'c/fyt)** |

Discontinuar cuando σc < **0.15f'c** (o 0.4f'c si amplificado)

---

## 18.12.9 Resistencia al Cortante

### 18.12.9.1 Ecuacion General
```
Vn = Acv * (2λ√f'c + ρt*fy)     [Ec. 18.12.9.1]
```

### 18.12.9.2 Limite Maximo
```
Vn ≤ 8√f'c * Acv
```

### 18.12.9.3 Friccion por Cortante (Juntas Prefabricadas)
```
Vn = Avf * fy * μ     [Ec. 18.12.9.3]
```
- **μ = 1.0λ** para concreto normalweight
- ≥ **50%** de Avf debe ser distribuido uniformemente

### 18.12.9.4 Limite en Juntas
- Vn ≤ limites de **22.9.4.4** usando solo espesor de topping

---

## 18.12.11 Diafragmas de Concreto Prefabricado

- Deben satisfacer **ACI CODE-550.5**
- Conexiones ensayadas segun **ACI CODE-550.4**
- Tolerancias de construccion: max **1/2"**

---

## 18.12.12 Cerchas Estructurales

### 18.12.12.1 Confinamiento
Requiere refuerzo transversal cuando σc > **0.2f'c**

### Tabla 18.12.12.1 - Refuerzo Transversal para Cerchas

| Tipo | Expresiones |
|------|-------------|
| Ash/sbc (rectangular) | Mayor de: **0.3(Ag/Ach - 1)(f'c/fyt)** y **0.09(f'c/fyt)** |
| ρs (espiral) | Mayor de: **0.45(Ag/Ach - 1)(f'c/fyt)** y **0.12(f'c/fyt)** |

### 18.12.12.2 Desarrollo
- Todo refuerzo continuo desarrollado para **fy en tension**

---

*ACI 318-25 Seccion 18.12*
