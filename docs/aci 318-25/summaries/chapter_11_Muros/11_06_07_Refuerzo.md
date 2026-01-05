# ACI 318-25 - 11.6-11.7 REFUERZO

---

## 11.6 LIMITES DE REFUERZO

### 11.6.1 Refuerzo Minimo (Cortante Bajo)
**Condicion**: Vu <= 0.5 * phi * alpha_c * lambda * sqrt(f'c) * Acv

### Tabla 11.6.1 - Cuantias Minimas

| Tipo | Barra | fy (psi) | rho_l min | rho_t min |
|------|-------|----------|-----------|-----------|
| Colado en sitio | <= No. 5 | >= 60,000 | 0.0012 | 0.0020 |
| Colado en sitio | <= No. 5 | < 60,000 | 0.0015 | 0.0025 |
| Colado en sitio | > No. 5 | Cualquiera | 0.0015 | 0.0025 |
| Prefabricado | Cualquiera | Cualquiera | 0.0010 | 0.0010 |

### 11.6.2 Refuerzo Minimo (Cortante Alto)
**Condicion**: Vu > 0.5 * phi * alpha_c * lambda * sqrt(f'c) * Acv

**(a) Refuerzo Longitudinal:**
```
rho_l >= 0.0025 + 0.5 * (2.5 - hw/lw) * (rho_t - 0.0025)
```
- Minimo: **0.0025**

**(b) Refuerzo Transversal:**
- Minimo: **0.0025**

---

## 11.7 DETALLADO DE REFUERZO

### 11.7.2 Espaciamiento de Refuerzo Longitudinal

| Tipo | Espaciamiento Maximo |
|------|---------------------|
| Colado en sitio (general) | Menor de: 3h, 18 in |
| Colado en sitio (cortante) | No exceder lw/3 |
| Prefabricado (general) | Menor de: 5h, 18 in (ext) o 30 in (int) |

### 11.7.2.3 Doble Cortina de Refuerzo
Muros con espesor > 10 in: refuerzo en **dos cortinas**.

### 11.7.3 Espaciamiento de Refuerzo Transversal

| Tipo | Espaciamiento Maximo |
|------|---------------------|
| Colado en sitio (general) | Menor de: 3h, 18 in |
| Colado en sitio (cortante) | No exceder lw/5 |
| Prefabricado (general) | Menor de: 5h, 18 in (ext) o 30 in (int) |

### 11.7.5 Soporte Lateral del Refuerzo Longitudinal
Si Ast > 0.01*Ag: refuerzo longitudinal debe tener soporte lateral con estribos.

### 11.7.6 Refuerzo Alrededor de Aberturas

| Cortinas | Refuerzo Adicional |
|----------|-------------------|
| Dos cortinas | Al menos 2 barras No. 5 |
| Una cortina | Al menos 1 barra No. 5 |

Desarrollar fy en tension en esquinas de aberturas.

---

*ACI 318-25 Secciones 11.6-11.7*
