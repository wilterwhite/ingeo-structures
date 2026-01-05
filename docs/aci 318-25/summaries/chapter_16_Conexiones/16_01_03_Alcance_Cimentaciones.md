# ACI 318-25 - 16.1-16.3 ALCANCE Y CONEXIONES A CIMENTACIONES

---

## 16.1 ALCANCE

### 16.1.1 Aplicabilidad
Aplica al diseno de conexiones entre miembros incluyendo:
- (a) Conexiones de miembros prefabricados
- (b) Conexiones a cimentaciones
- (c) Cortante horizontal en miembros compuestos
- (d) Mensulas y corbeles

---

## 16.2 CONEXIONES DE MIEMBROS PREFABRICADOS

### 16.2.1 General

| Requisito | Descripcion |
|-----------|-------------|
| 16.2.1.1 | Fuerzas transferidas entre miembros mediante aplastamiento, cortante, friccion, anclaje, soldadura, o combinacion |
| 16.2.1.2 | Seleccionar localizacion, configuracion y detallado para minimizar restriccion al volumen de cambios |

### 16.2.2 Transferencia de Fuerzas

**16.2.2.1** Apoyos de miembros de entrepiso:
- Longitud de apoyo >= **3 in.** (con superficie nivelada)
- Longitud de apoyo >= **espesor del miembro/2** (sin superficie nivelada)

### 16.2.3 Conexiones Resistentes al Momento

**16.2.3.1** Transferencia de momento por:
- Soldadura de conexion
- Dowels inyectados
- Refuerzo postensado
- Otros medios aprobados

### 16.2.4 Integridad Estructural

**16.2.4.1** Proporcionar tirantes de conexion para asegurar continuidad estructural y resistir colapso progresivo.

**16.2.4.2** Fuerza de tirante minima:
```
Tie force >= 1,500 lbs per foot of member
```

---

## 16.3 CONEXIONES A CIMENTACIONES

### 16.3.1 General

**16.3.1.1** Fuerzas y momentos en la base de columnas, muros y pedestales transferidos a la cimentacion.

### 16.3.2 Transferencia de Compresion

**16.3.2.1** Resistencia al aplastamiento:
```
φBn = φ * 0.85 * fc' * A1
```

**16.3.2.2** Si area de apoyo A1 < area de cimentacion A2:
```
φBn = φ * 0.85 * fc' * A1 * √(A2/A1) <= φ * 1.7 * fc' * A1
```

Donde **φ = 0.65**

### 16.3.3 Transferencia de Tension

**16.3.3.1** Tension transferida por:
- Dowels
- Anclas
- Conectores mecanicos

**16.3.3.2** Desarrollo completo requerido.

### 16.3.4 Transferencia de Cortante Lateral

**16.3.4.1** Cortante lateral transferido por:
- Friccion de cortante (16.5)
- Llaves de cortante
- Dowels
- Otros medios

### 16.3.5 Dowels Minimos

**16.3.5.1** Area minima de dowels:
```
As,dowel >= 0.005 * Ag (columna o pedestal)
```

**16.3.5.2** Minimo **4 barras**.

**16.3.5.3** Diametro de dowel no mayor que el diametro de barra longitudinal + **0.15 in.**

---

## Resumen de Transferencia a Cimentacion

| Fuerza | Metodo | Formula/Requisito |
|--------|--------|-------------------|
| Compresion | Aplastamiento | Bn = 0.85*fc'*A1*√(A2/A1) |
| Tension | Dowels/anclas | Desarrollar fy |
| Cortante | Friccion | Vn = μ*Avf*fy |
| - | Dowels minimos | 0.005*Ag, 4 barras |

---

*ACI 318-25 Secciones 16.1-16.3*
