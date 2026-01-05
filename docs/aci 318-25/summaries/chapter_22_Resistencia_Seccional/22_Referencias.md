# TABLAS RESUMEN Y REFERENCIAS - CAPITULO 22

## Resistencias Nominales

| Tipo | Formula Principal | Seccion |
|------|-------------------|---------|
| Flexion | Mn segun supuestos de 22.2 | 22.3 |
| Axial compresion | Pn,max = 0.80*Po (estribos) o 0.85*Po (espirales) | 22.4.2 |
| Cortante unidireccional | Vn = Vc + Vs | 22.5.1.1 |
| Cortante bidireccional | vn = vc + vs | 22.6.1.3 |
| Torsion | Tn = 2*Ao*At*fyt/s * cot(theta) | 22.7.6.1 |
| Aplastamiento | Bn = 0.85*f'c*A1 * sqrt(A2/A1) <= 2*(0.85*f'c*A1) | 22.8.3.2 |
| Friccion por cortante | Vn = mu*(Avf*fy + Nu) | 22.9.4.2 |

## Parametros Clave

| Parametro | Formula/Valor | Seccion |
|-----------|---------------|---------|
| epsilon_cu (concreto) | **0.003** | 22.2.2.1 |
| Bloque de esfuerzos | 0.85*f'c | 22.2.2.4.1 |
| a (profundidad bloque) | beta_1 * c | 22.2.2.4.1 |
| beta_1 (f'c <= 4000 psi) | **0.85** | 22.2.2.4.3 |
| beta_1 (f'c >= 8000 psi) | **0.65** | 22.2.2.4.3 |
| lambda_s (size effect) | 2/(1 + d/10) <= 1 | 22.5.5.1.3 |
| Ao (torsion simplificada) | 0.85 * Aoh | 22.7.6.1.1 |
| theta (no pretensado) | **45°** | 22.7.6.1.2 |

## Limites de Materiales

| Parametro | Limite | Aplicacion |
|-----------|--------|------------|
| sqrt(f'c) | 100 psi | Cortante, torsion |
| fy, fyt | 60,000 psi | Cortante, torsion, friccion |
| fy | 80,000 psi | Resistencia axial Po |

## Coeficientes de Friccion

| Condicion | mu |
|-----------|-----|
| Monolitico | 1.4*lambda |
| Rugoso (~1/4 in.) | 1.0*lambda |
| No rugoso | 0.6 |
| Contra acero | 0.7*lambda |

---

## Referencias Cruzadas

| Tema | Seccion |
|------|---------|
| Factores de reduccion phi | Capitulo 21 |
| Strut-and-Tie | Capitulo 23 |
| Propiedades del refuerzo | 20.2 |
| Propiedades del pretensado | 20.3 |
| Concreto liviano (lambda) | 19.2.4 |
| Limites de fy, fyt | 20.2.2.4 |
| Refuerzo minimo a cortante | 9.6.3, 9.6.4 |
| Losas bidireccionales | Capitulo 8 |
| Detallado de estribos bidireccionales | 8.7.6 |
| Detallado de studs con cabeza | 8.7.7 |
| Anclaje de refuerzo | 25.4 |
| Zonas de anclaje post-tensado | 25.9 |
| Combinaciones de carga | Capitulo 5 |
| Procedimientos de analisis | Capitulo 6 |
| Rugosidad intencional | 26.5.6.2(e) |

---

*ACI 318-25 Capitulo 22 - Tablas Resumen y Referencias*
