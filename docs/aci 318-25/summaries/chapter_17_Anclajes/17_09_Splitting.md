# 17.9 SPLITTING (HENDIMIENTO)

## 17.9.1 General
Verificar que las fuerzas de splitting inducidas por la instalacion y carga no causen falla prematura.

## 17.9.2 Requisitos de Distancia Minima

### Tabla 17.9.2.1 - Distancias Minimas al Borde y Espaciamiento

| Tipo de Anclaje | ca,min | s,min |
|-----------------|--------|-------|
| Colados en sitio | Segun recubrimiento (Cap. 20) | Segun 17.9.3 |
| Post-instalados (sin torque) | 6*da | 6*da |
| Post-instalados (torque-controlled) | Segun informe ACI 355.2 | Segun informe |
| Adhesivos | Segun informe ACI 355.4 | Segun informe |

## 17.9.3 Espaciamiento Minimo

**Anclajes colados en sitio:**
```
s,min >= 4*da     [para tension]
s,min >= 4*da     [para cortante]
```

**Anclajes post-instalados:**
- Segun informe de calificacion
- Minimo 6*da si no se especifica

## 17.9.4 Distancia Critica al Borde (cac)

Para anclajes post-instalados, verificar splitting usando:
```
cac = valor del informe de calificacion
```

**Si ca,min < cac:**
- Aplicar factor psi_cp,N (ver 17.6.2.4)
- Verificar resistencia reducida al desprendimiento

## 17.9.5 Control de Splitting en Bordes Delgados

**17.9.5.1** Si ha < 1.5*hef:
- Limitar carga o
- Proveer refuerzo de confinamiento

**17.9.5.2** Refuerzo de confinamiento:
- Estribos o amarres que encierren los anclajes
- Espaciamiento <= 3 in desde la superficie de carga

---

*ACI 318-25 Seccion 17.9*
