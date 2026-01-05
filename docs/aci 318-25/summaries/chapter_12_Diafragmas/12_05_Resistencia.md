# ACI 318-25 - 12.5 RESISTENCIA DE DISENO

---

## 12.5.1 General

**12.5.1.1** Para cada combinacion de carga factorizada aplicable:

**phi*Sn >= U**

Considerar interaccion entre efectos de carga.

**12.5.1.2** phi segun 21.2

### 12.5.1.3 Metodos de Resistencia de Diseno

| Metodo | Requisitos |
|--------|------------|
| (a) Diafragma como viga de profundidad completa | Resistencias segun 12.5.2 a 12.5.4 |
| (b) Modelo puntal-tensor | Resistencias segun 23.3 |
| (c) Modelo de elementos finitos | Resistencias segun Capitulo 22, considerar distribuciones de cortante no uniformes |
| (d) Metodos alternativos | Satisfacer equilibrio y proporcionar resistencias >= requeridas |

---

## 12.5.2 Momento y Fuerza Axial

### 12.5.2.1 Fuerzas en Cuerdas (Chords)

Para un diafragma actuando como viga horizontal:
```
Tu = Cu = Mu / (j*d)
```

Donde:
- **Tu, Cu** = fuerza de tension/compresion en las cuerdas
- **Mu** = momento factorado en el diafragma
- **d** = profundidad del diafragma (perpendicular al cortante)
- **j** ≈ 0.9 (brazo de palanca interno)

### 12.5.2.2 Resistencia de Cuerdas
Calcular Pn y Mn segun **22.4**.

**12.5.2.3** Refuerzo no presforzado y conectores mecanicos resistiendo tension por momento deben ubicarse dentro de **h/4** del borde en tension, donde h es la profundidad del diafragma.

---

## 12.5.3 Cortante

**12.5.3.2** phi = **0.75**, a menos que se requiera un valor menor por 21.2.4.

### 12.5.3.3 Diafragma Completamente Colado en Sitio

**Resistencia nominal al cortante:**
```
Vn = Acv*(2*lambda*sqrt(f'c) + rho_t*fy)
```

Donde:
- Acv = area bruta de concreto limitada por espesor y profundidad del alma
- sqrt(f'c) <= 100 psi
- rho_t = refuerzo distribuido paralelo al cortante

### 12.5.3.4 Limite de Cortante
```
Vu <= phi*8*Acv*sqrt(f'c)
```

### 12.5.3.6 Diafragma de Precolados Interconectados (Sin Recubrimiento)

| Metodo | Requisito |
|--------|-----------|
| (a) Juntas inyectadas | Resistencia nominal <= **80 psi**. Disenar refuerzo por friccion de cortante |
| (b) Conectores mecanicos | Disenar para resistir cortante bajo apertura de junta anticipada |

---

## 12.5.4 Colectores

> **Definicion**: Un colector es una region del diafragma que transfiere fuerzas entre el diafragma y un elemento vertical del sistema resistente a fuerzas laterales.

**12.5.4.1** Los colectores deben extenderse desde los elementos verticales a traves de todo o parte de la profundidad del diafragma segun se requiera para transferir cortante.

**12.5.4.2** Los colectores deben disenarse como miembros a tension, compresion, o ambos, segun 22.4.

**12.5.4.3** El refuerzo del colector debe extenderse a lo largo del elemento vertical al menos el mayor de:
- (a) Longitud requerida para desarrollar el refuerzo en tension
- (b) Longitud requerida para transmitir fuerzas de diseno al elemento vertical por friccion de cortante (22.9)

### Friccion de Cortante para Colectores (22.9)

```
Vn = μ * Avf * fy
```

Donde:
- **μ** = 1.4λ (concreto colado contra concreto endurecido rugoso)
- **μ** = 1.0λ (concreto colado contra concreto endurecido liso)
- **μ** = 0.6λ (concreto contra acero)

---

## Resumen de Formulas

| Parametro | Formula |
|-----------|---------|
| Cortante nominal (colado en sitio) | Vn = Acv*(2λ√fc' + ρt*fy) |
| Cortante maximo | Vn,max = 8√fc'*Acv |
| Fuerza en cuerda | Tu = Cu = Mu/(j*d) |
| Friccion de cortante | Vn = μ*Avf*fy |

| Factor | Valor |
|--------|-------|
| φ (cortante) | **0.75** |
| √fc' limite | 100 psi max |

---

*ACI 318-25 Seccion 12.5*
