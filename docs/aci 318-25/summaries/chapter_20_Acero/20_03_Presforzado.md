# 20.3 ACERO DE PRESFUERZO

## 20.3.1 Propiedades de Material

### 20.3.1.1 Especificaciones ASTM

| ASTM | Tipo |
|------|------|
| **A416** | Toron (strand) |
| **A421** | Alambre |
| **A421 + S1** | Alambre de baja relajacion |
| **A722** | Barra de alta resistencia |

### 20.3.1.3 Sistemas Sismicos Especiales (Prefabricados)
- Presfuerzo resistiendo M, P, o ambos en **SMF, muros especiales**
- Debe cumplir **ASTM A416** o **ASTM A722**

---

## 20.3.2 Propiedades de Diseno

### 20.3.2.1 Modulo de Elasticidad (Ep)
- Determinar por ensayos o reporte del fabricante
- Valores tipicos: **28,500,000 - 29,000,000 psi**

### 20.3.2.2 Resistencia a Tension (fpu)

#### Tabla 20.3.2.2 - Valores Maximos de fpu

| Tipo | fpu Max (psi) | ASTM |
|------|---------------|------|
| Toron (stress-relieved y low-relaxation) | **270,000** | A416 |
| Alambre (stress-relieved y low-relaxation) | **250,000** | A421, A421+S1 |
| Barra de alta resistencia | **150,000** | A722 |

---

## 20.3.2.3 Esfuerzo fps en Presfuerzo Adherido (Resistencia Nominal)

### 20.3.2.3.1 Formula Aproximada

**Aplicable si:**
- Todo el presfuerzo esta en zona de tension
- fse ≥ 0.5 fpu

```
fps = fpu * {1 - (γp/β1) * [ρp*(fpu/f'c) + (d/dp)*(fy/f'c)*(ρ - ρ')]}
```

#### Tabla 20.3.2.3.1 - Valores de γp

| fpy/fpu | γp |
|---------|-----|
| ≥ 0.80 | **0.55** |
| ≥ 0.85 | **0.40** |
| ≥ 0.90 | **0.28** |

#### Tabla R20.3.2.3.1 - Relacion fpy/fpu por Tipo

| Tipo de Presfuerzo | fpy/fpu |
|--------------------|---------|
| Barras A722 Tipo I (Liso) | ≥ 0.85 |
| Barras A722 Tipo II (Deformado) | ≥ 0.80 |
| Toron/alambre stress-relieved | ≥ 0.85 |
| Toron/alambre low-relaxation | ≥ 0.90 |

**Condiciones para incluir refuerzo de compresion:**
- **(a)** Si d' > 0.15dp: **ignorar refuerzo de compresion**
- **(b)** [ρp*(fpu/f'c) + (d/dp)*(fy/f'c)*(ρ - ρ')] ≥ **0.17**

### 20.3.2.3.2 Torones Pretensados
- Esfuerzo dentro de ℓd desde extremo libre: segun **25.4.8.3**

---

## 20.3.2.4 Esfuerzo fps en Presfuerzo No Adherido (Resistencia Nominal)

### Tabla 20.3.2.4.1 - Valores Aproximados de fps

**Aplicable si:** fse ≥ 0.5 fpu

| ℓn/h | fps |
|------|-----|
| **≤ 35** | Menor de: fse + 10,000 + f'c/(100ρp), fse + 60,000, fpy |
| **> 35** | Menor de: fse + 10,000 + f'c/(300ρp), fse + 30,000, fpy |

---

## 20.3.2.5 Esfuerzos Permisibles en Presfuerzo

### Tabla 20.3.2.5.1 - Esfuerzos Maximos de Tension

| Etapa | Ubicacion | Esfuerzo Maximo |
|-------|-----------|-----------------|
| **Durante tensado** | Extremo de gato | Menor de: **0.94fpy**, **0.80fpu**, Max. del fabricante |
| **Inmediatamente antes de transferencia** | Extremo de gato (pretensado) | **0.75fpu** |
| **Inmediatamente despues de transferencia** | Anclajes y acopladores | **0.70fpu** |

---

## 20.3.2.6 Perdidas de Presfuerzo

### 20.3.2.6.1 Factores a Considerar

| Factor | Descripcion |
|--------|-------------|
| (a) | Asentamiento del presfuerzo en transferencia |
| (b) | Acortamiento elastico del concreto |
| (c) | Flujo plastico del concreto |
| (d) | Contraccion del concreto |
| (e) | Relajacion del acero de presfuerzo |
| (f) | Perdida por friccion (curvatura intencional o no) |

### 20.3.2.6.2 Perdida por Friccion (Post-tensado)
- Basada en coeficientes de friccion por wobble y curvatura
- Determinados **experimentalmente**

### 20.3.2.6.3 Perdida por Conexion
- Incluir perdida anticipada por conexion a construccion adyacente

---

## Referencia de Calculo

### Relaciones fpy/fpu Tipicas

| Tipo | fpy/fpu | γp |
|------|---------|-----|
| Barra alta resistencia (liso) | 0.85 | 0.40 |
| Barra alta resistencia (deformado) | 0.80 | 0.55 |
| Toron stress-relieved | 0.85 | 0.40 |
| Toron low-relaxation | 0.90 | 0.28 |

---

*ACI 318-25 Seccion 20.3*
