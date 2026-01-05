# 26.4 PROPIEDADES DE LOS MATERIALES

## 26.4.1 Propiedades del Concreto para Diseno

**Tabla 26.4.1.1 - Valores para Diseno**

| Propiedad | Ecuacion o Valor |
|-----------|------------------|
| Ec (peso normal) | 57,000*sqrt(f'c) psi |
| Ec (liviano) | wc^1.5 * 33 * sqrt(f'c) psi |
| fr (modulo de ruptura) | 7.5*lambda*sqrt(f'c) psi |
| beta_1 | 0.85 - 0.05*(f'c - 4000)/1000 >= 0.65 |

## 26.4.2 Requisitos de Durabilidad

**Tabla 26.4.2.1 - Requisitos por Clase de Exposicion**

| Clase | w/cm max | f'c min (psi) | Aire (%) | Cemento |
|-------|----------|---------------|----------|---------|
| F0 | - | 2500 | - | - |
| F1 | 0.55 | 3500 | Tabla 19.3.3.1 | - |
| F2 | 0.45 | 4500 | Tabla 19.3.3.1 | - |
| S0 | - | 2500 | - | - |
| S1 | 0.50 | 4000 | - | Tipo II |
| S2 | 0.45 | 4500 | - | Tipo V |
| S3 | 0.40 | 5000 | - | Tipo V + puzolana |
| W0 | - | 2500 | - | - |
| W1 | - | 2500 | - | - |
| W2 | 0.50 | 4000 | - | - |
| C0 | - | 2500 | - | - |
| C1 | - | 2500 | - | - |
| C2 | 0.40 | 5000 | - | - |

## 26.4.3 Proporcionamiento de Mezclas de Concreto

**26.4.3.1** Proporcionar mezcla para:
- Alcanzar f'c especificado
- Cumplir requisitos de durabilidad
- Cumplir requisitos de trabajabilidad

**26.4.3.2** Resistencia promedio requerida (f'cr):

**Tabla 26.4.3.2.1 - Resistencia Promedio Requerida**

| f'c (psi) | f'cr (psi) |
|-----------|------------|
| < 3000 | f'c + 1000 |
| 3000 - 5000 | f'c + 1200 |
| > 5000 | 1.10*f'c + 700 |

*Valores cuando no hay datos historicos de desviacion estandar*

**26.4.3.3** Con datos historicos (30+ ensayos):
```
f'cr = f'c + 1.34*s     (probabilidad 1 en 100 por debajo)
f'cr = f'c + 2.33*s - 500     (promedio de 3 consecutivos)
```
Usar el **mayor** de ambos valores.

## 26.4.4 Propiedades del Acero de Refuerzo

**Tabla 26.4.4.1 - Propiedades de Diseno del Acero**

| Grado | fy (psi) | fyt (psi) | Es (psi) |
|-------|----------|-----------|----------|
| 40 | 40,000 | 40,000 | 29,000,000 |
| 60 | 60,000 | 60,000 | 29,000,000 |
| 80 | 80,000 | 80,000 | 29,000,000 |
| 100 | 100,000 | 100,000 | 29,000,000 |

---

*ACI 318-25 Seccion 26.4*
