# ACI 318-25 - 6.1-6.2 ALCANCE Y GENERAL

---

## 6.1 ALCANCE

### 6.1.1 Aplicabilidad
Aplica a metodos de analisis, modelado de miembros y sistemas estructurales, y calculo de efectos de carga.

---

## 6.2 GENERAL

### 6.2.3 Metodos de Analisis Permitidos

| Metodo | Seccion | Descripcion |
|--------|---------|-------------|
| **(a)** Simplificado | 6.5 | Vigas continuas y losas unidireccionales (cargas gravitacionales) |
| **(b)** Elastico lineal 1er orden | 6.6 | Con magnificacion de momentos para esbeltez |
| **(c)** Elastico lineal 2do orden | 6.7 | Considera geometria deformada |
| **(d)** Inelastico | 6.8 | No linealidad del material |
| **(e)** Elementos finitos | 6.9 | Metodo general |

### 6.2.4 Metodos Adicionales Permitidos

| Aplicacion | Metodo | Referencia |
|------------|--------|------------|
| Losas bidireccionales (gravedad) | Diseno directo o marco equivalente | 6.2.4.1 |
| Muros esbeltos | Efectos fuera del plano | 11.8 |
| Diafragmas | Analisis especifico | 12.4.2 |
| Regiones D | Strut-and-Tie | Capitulo 23 |

---

## 6.2.5 EFECTOS DE ESBELTEZ

### 6.2.5.1 Cuando se Pueden Ignorar

#### (a) Columnas NO arriostradas (sway)
```
k*lu/r <= 22
```

#### (b) Columnas arriostradas (nonsway)
```
k*lu/r <= 34 + 12*(M1/M2)
k*lu/r <= 40
```

**Convencion de signos:**
- M1/M2 **negativo** = curvatura simple
- M1/M2 **positivo** = curvatura doble

**Criterio de arriostramiento:**
Si rigidez lateral de elementos de arriostre >= 12 x rigidez lateral bruta de columnas → columnas se consideran arriostradas.

### 6.2.5.2 Radio de Giro

| Metodo | Formula |
|--------|---------|
| General | r = sqrt(Ig/Ag) |
| Columnas rectangulares | r = 0.30 x dimension en direccion de estabilidad |
| Columnas circulares | r = 0.25 x diametro |

### 6.2.5.3 Limite de Efectos de Segundo Orden
```
Mu (con efectos 2do orden) <= 1.4 * Mu (1er orden)
```
Si se excede, revisar sistema estructural.

---

*ACI 318-25 Secciones 6.1-6.2*
