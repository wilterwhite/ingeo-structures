# ACI 318-25 - CAPITULO 6: TABLAS RESUMEN

---

## Rigideces Efectivas para Analisis

| Elemento | I para Cargas Factoradas | I para Servicio |
|----------|--------------------------|-----------------|
| Columnas | 0.70*Ig | min(0.98*Ig, Ig) |
| Muros (no fisurados) | 0.70*Ig | min(0.98*Ig, Ig) |
| Muros (fisurados) | 0.35*Ig | min(0.49*Ig, Ig) |
| Vigas | 0.35*Ig | min(0.49*Ig, Ig) |
| Losas planas | 0.25*Ig | min(0.35*Ig, Ig) |

**Alternativa para deflexiones laterales (6.6.3.1.2):** I = 0.5*Ig para todos los miembros

**Propiedades adicionales:**
- Area de corte (rectangular): Ashear <= 5/6*Ag
- Modulo de corte: G = 0.4*Ec

---

## Limites de Esbeltez

| Tipo de Marco | Limite k*lu/r | Referencia |
|---------------|---------------|------------|
| Sway (no arriostrado) | 22 | 6.2.5.1(a) |
| Nonsway (arriostrado) | 34 + 12*(M1/M2) y 40 | 6.2.5.1(b)(c) |

---

## Factores de Magnificacion

| Tipo | Formula | Seccion |
|------|---------|---------|
| Nonsway | delta = Cm/(1 - Pu/0.75Pc) | 6.6.4.5.2 |
| Sway (Q) | delta_s = 1/(1-Q) | 6.6.4.6.2(a) |
| Sway (Sum P) | delta_s = 1/(1 - Sum Pu/0.75 Sum Pc) | 6.6.4.6.2(b) |

---

## Coeficientes de Momentos Simplificados

| Ubicacion | Coeficiente |
|-----------|-------------|
| M+ tramo extremo (extremo integral) | 1/14 |
| M+ tramo extremo (extremo libre) | 1/11 |
| M+ tramos interiores | 1/16 |
| M- primer apoyo interior (2 tramos) | 1/9 |
| M- primer apoyo interior (>2 tramos) | 1/10 |
| M- apoyos interiores | 1/11 |
| M- todos los apoyos (losas cortas) | 1/12 |

---

## Referencias Cruzadas

| Tema | Seccion |
|------|---------|
| Combinaciones de carga | Capitulo 5 |
| Muros esbeltos (fuera del plano) | 11.8 |
| Diafragmas | 12.4.2 |
| Strut-and-Tie | Capitulo 23 |
| Deflexiones | 24.2 |
| Modulo de elasticidad Ec | 19.2.2 |
| Factor k (nomogramas Jackson-Moreland) | Fig. R6.2.5.1 |

---

*ACI 318-25 Capitulo 6 - Tablas Resumen*
