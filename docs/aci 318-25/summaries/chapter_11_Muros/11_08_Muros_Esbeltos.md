# ACI 318-25 - 11.8 METODO ALTERNATIVO PARA MUROS ESBELTOS

---

## 11.8.1 Condiciones de Aplicabilidad

| Condicion | Requisito |
|-----------|-----------|
| (a) Seccion | Constante en toda la altura |
| (b) Comportamiento | Controlado por tension |
| (c) Resistencia | phi*Mn >= Mcr |
| (d) Carga axial | Pu <= 0.06*f'c*Ag (a media altura) |
| (e) Deflexion | <= lc/150 (cargas de servicio) |

---

## 11.8.3 Momento Factorado

### Metodo (a) - Iterativo
```
Mu = Mua + Pu * Delta_u

Delta_u = (5 * Mu * lc^2) / (0.75 * 48 * Ec * Icr)
```

### Metodo (b) - Directo
```
Mu = Mua / (1 - (5 * Pu * lc^2) / (0.75 * 48 * Ec * Icr))
```

### Inercia Agrietada
```
Icr = (Es/Ec) * Ase,w * (d - c)^2 + (lw * c^3) / 3
```

- Es/Ec debe ser al menos **6**
- Ase,w = As + (Pu/fy) * (h/2) / d

---

## 11.8.4 Deflexion de Servicio

### Tabla 11.8.4.1 - Calculo de Delta_s

| Condicion | Formula |
|-----------|---------|
| Ma <= (2/3)*Mcr | Delta_s = (Ma/Mcr) * Delta_cr |
| Ma > (2/3)*Mcr | Interpolacion entre Delta_cr y Delta_n |

### Deflexiones de Referencia
```
Delta_cr = (5 * Mcr * lc^2) / (48 * Ec * Ig)
Delta_n = (5 * Mn * lc^2) / (48 * Ec * Icr)
```

---

*ACI 318-25 Seccion 11.8*
