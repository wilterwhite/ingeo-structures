# ACI 318-25 - CAPITULO 21: FACTORES DE REDUCCION DE RESISTENCIA

## Contenido del Capitulo

| Archivo | Secciones | Contenido |
|---------|-----------|-----------|
| [21_Factores_Reduccion.md](21_Factores_Reduccion.md) | 21.1-21.2 | Tabla 21.2.1, 21.2.2, modificaciones sismicas |

---

## Factores φ Principales

| Accion | φ |
|--------|---|
| Flexion (tension controlada) | **0.90** |
| Flexion (compresion, espirales) | **0.75** |
| Flexion (compresion, estribos) | **0.65** |
| Cortante | **0.75** |
| Torsion | **0.75** |
| Aplastamiento | **0.65** |
| Puntal-tensor | **0.75** |
| Concreto simple | **0.60** |

---

## Clasificacion por Deformacion εt

| Clasificacion | εt | φ (Espirales) | φ (Otros) |
|---------------|-----|---------------|-----------|
| Compresion controlada | ≤ εty | 0.75 | 0.65 |
| Transicion | εty a εty+0.003 | Interpolar | Interpolar |
| Tension controlada | ≥ εty+0.003 | 0.90 | 0.90 |

### εty por Grado
```
εty = fy / Es = fy / 29,000,000

Grado 60:  εty = 0.00207 (permitido usar 0.002)
Grado 80:  εty = 0.00276
Grado 100: εty = 0.00345
```

---

## Formulas de Transicion

**Espirales:**
```
φ = 0.75 + 0.15 * (εt - εty) / 0.003
```

**Otros (estribos):**
```
φ = 0.65 + 0.25 * (εt - εty) / 0.003
```

---

## Modificaciones Sismicas (21.2.4)

| Condicion | φ Cortante |
|-----------|------------|
| Miembro controlado por cortante | **0.60** |
| Nudos SMF, vigas acople diagonales | **0.85** |
| Diafragmas/cimentaciones | ≤ menor del SFRS |

---

## Anclajes

| Tipo | Ductil | No Ductil |
|------|--------|-----------|
| Acero - Tension | 0.75 | 0.65 |
| Acero - Cortante | 0.65 | 0.60 |
| Concreto - Tension (redundante) | 0.75 | — |
| Concreto - Tension (no redundante) | 0.65 | — |
| Concreto - Cortante | 0.75 | — |

---

*ACI 318-25 Capitulo 21 - Indice*
