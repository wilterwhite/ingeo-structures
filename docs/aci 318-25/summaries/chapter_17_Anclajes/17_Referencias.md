# VARIABLES, FACTORES Y REFERENCIAS - CAPITULO 17

## Variables Clave

### Tension

| Variable | Descripcion |
|----------|-------------|
| Ase,N | Area efectiva del anclaje en tension |
| futa | Resistencia a tension especificada del acero |
| fya | Resistencia a fluencia especificada del acero |
| hef | Profundidad efectiva de empotramiento |
| ANc, ANco | Areas proyectadas de falla por breakout |
| ca1, ca2 | Distancias al borde |
| Abrg | Area de apoyo de la cabeza |
| da | Diametro del anclaje |
| eh | Distancia del borde interior del vastago a la punta del gancho |
| tau_cr | Esfuerzo de adherencia caracteristico |
| cNa | Radio de influencia critico para adherencia |
| lambda_a | Factor de concreto liviano |

### Cortante

| Variable | Descripcion |
|----------|-------------|
| Ase,V | Area efectiva del anclaje en cortante |
| ca1 | Distancia al borde en direccion de la carga |
| ca2 | Distancia al borde perpendicular a ca1 |
| AVc, AVco | Areas proyectadas de falla por breakout en cortante |
| le | Longitud efectiva de carga del anclaje |
| da | Diametro del anclaje |
| ha | Espesor del miembro donde esta el anclaje |
| e'V | Excentricidad de cortante en grupo |
| kcp | Factor de pryout |
| lambda_a | Factor de concreto liviano |

---

## Resumen de Factores

### Factores de Reduccion phi

| Modo | Estatico | Sismico |
|------|----------|---------|
| Tension - acero ductil | 0.75 | 0.75 |
| Tension - acero no ductil | 0.65 | 0.65 |
| Tension - concreto | 0.70/0.75 | 0.70/0.75 |
| Cortante - acero ductil | 0.65 | 0.65 |
| Cortante - acero no ductil | 0.60 | 0.60 |
| Cortante - concreto | 0.70/0.75 | 0.70/0.75 |

### Ecuaciones Principales

**Tension:**
```
Nn = min(Nsa, Ncb o Ncbg, Npn, Nsb o Nsbg, Na o Nag)
```

**Cortante:**
```
Vn = min(Vsa, Vcb o Vcbg, Vcp o Vcpg)
```

**Interaccion:**
```
Nua/(phi*Nn) + Vua/(phi*Vn) <= 1.2
```

---

## Lista de Verificacion - Diseno de Anclajes

### Paso 1: Determinar Cargas
- [ ] Nua (tension factorada)
- [ ] Vua (cortante factorado)
- [ ] Excentricidades
- [ ] Combinaciones de carga (incluyendo sismo si aplica)

### Paso 2: Seleccionar Anclaje
- [ ] Tipo (colado, post-instalado, adhesivo)
- [ ] Material y grado
- [ ] Diametro da
- [ ] Profundidad efectiva hef

### Paso 3: Verificar Geometria
- [ ] Distancias al borde (ca1, ca2)
- [ ] Espaciamiento (s)
- [ ] Espesor del miembro (ha)
- [ ] Requisitos de splitting

### Paso 4: Calcular Resistencias
- [ ] Tension: Nsa, Ncb, Npn, Nsb (Na si adhesivo)
- [ ] Cortante: Vsa, Vcb, Vcp
- [ ] Aplicar factores phi

### Paso 5: Verificar
- [ ] phi*Nn >= Nua
- [ ] phi*Vn >= Vua
- [ ] Interaccion si aplica

### Paso 6: Requisitos Sismicos (si SDC C-F)
- [ ] Verificar ductilidad o refuerzo de anclaje
- [ ] Verificar ubicacion respecto a rotulas plasticas

---

## Referencias Normativas

| Norma | Descripcion |
|-------|-------------|
| ACI 355.2 | Calificacion de anclajes mecanicos post-instalados |
| ACI 355.4 | Calificacion de anclajes adhesivos |
| ASTM F1554 | Pernos de anclaje (Grado 36, 55, 105) |
| ASTM A354 | Pernos de alta resistencia |
| ASTM A449 | Pernos de acero templado |
| AWS D1.1 | Conectores de cabeza |

## Referencias Cruzadas Internas

| Tema | Seccion |
|------|---------|
| Factores phi | 21.2 |
| Requisitos sismicos generales | Capitulo 18 |
| Propiedades del concreto | Capitulo 19 |
| Recubrimiento | 20.5 |

---

*ACI 318-25 Capitulo 17 - Variables, Factores y Referencias*
