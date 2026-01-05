# 22.4 RESISTENCIA AXIAL O COMBINADA FLEXION-AXIAL

## 22.4.1 General
```
Pn, Mn = calculados segun supuestos de 22.2
```

## 22.4.2 Resistencia Axial Maxima a Compresion

### Tabla 22.4.2.1 - Resistencia Axial Maxima

| Miembro | Refuerzo Transversal | Pn,max |
|---------|----------------------|--------|
| No pretensado | Estribos (22.4.2.4) | **0.80 Po** |
| No pretensado | Espirales (22.4.2.5) | **0.85 Po** |
| Pretensado | Estribos | **0.80 Po** |
| Pretensado | Espirales | **0.85 Po** |
| Cimentacion profunda | Estribos (Cap. 13) | **0.80 Po** |

**Nota:** fy limitado a maximo **80,000 psi**.

### 22.4.2.2 Po para Miembros No Pretensados
```
Po = 0.85*f'c*(Ag - Ast) + fy*Ast       (Ec. 22.4.2.2)
```

### 22.4.2.3 Po para Miembros Pretensados
```
Po = 0.85*f'c*(Ag - Ast - Apd) + fy*Ast - (fse - 0.003*Ep)*Apt    (Ec. 22.4.2.3)
```
Donde:
- Apt = area total de refuerzo pretensado
- Apd = area ocupada por ducto, vaina y refuerzo pretensado
- fse >= 0.003*Ep

## 22.4.3 Resistencia Axial Maxima a Tension

### 22.4.3.1 Resistencia Maxima
```
Pnt,max = fy*Ast + (fse + delta_fp)*Apt     (Ec. 22.4.3.1)
```
Donde (fse + delta_fp) no debe exceder fpy, y Apt = 0 para no pretensados.

---

*ACI 318-25 Seccion 22.4*
