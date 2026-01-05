# 26.12 CRITERIOS DE ACEPTACION

## 26.12.1 Aceptacion de Resistencia

**26.12.1.1** El concreto se considera aceptable si:

**(a)** Promedio de cualquier 3 ensayos consecutivos:
```
Promedio >= f'c
```

**(b)** Ningun resultado individual:
```
Resultado individual >= f'c - 500 psi     (f'c <= 5000 psi)
Resultado individual >= 0.90*f'c          (f'c > 5000 psi)
```

## 26.12.2 Concreto de Baja Resistencia

**26.12.2.1** Si criterios de 26.12.1 no se cumplen:
- (a) Investigar causas
- (b) Considerar ensayos adicionales
- (c) Evaluar adecuacion estructural

## 26.12.3 Investigacion de Concreto de Baja Resistencia

**Tabla 26.12.3 - Opciones de Investigacion**

| Opcion | Procedimiento | Norma |
|--------|---------------|-------|
| Nucleos | Extraer y ensayar nucleos | ASTM C42 |
| Ensayos no destructivos | Martillo de rebote, ultrasonido | ASTM C805, C597 |
| Prueba de carga | Cargar elemento en campo | 26.12.4 |

### 26.12.3.2 Criterio de Aceptacion para Nucleos

**Satisfactorio si:**
```
Promedio de 3 nucleos >= 0.85*f'c
Ningun nucleo individual < 0.75*f'c
```

## 26.12.4 Prueba de Carga

**26.12.4.1** Se permite cuando:
- Nucleos no satisfacen criterios
- Existe duda sobre capacidad estructural

**26.12.4.2** Procedimiento:
- Cargar incrementalmente hasta carga de prueba
- Medir deflexiones
- Evaluar recuperacion

**26.12.4.3** Carga de prueba:
```
W_test = 0.85*(1.4*D + 1.7*L)
```

**26.12.4.4** Criterio de aceptacion:
```
Deflexion maxima <= l^2/(20,000*h)
Recuperacion >= 75% de deflexion maxima (24 hrs)
```

---

*ACI 318-25 Seccion 26.12*
