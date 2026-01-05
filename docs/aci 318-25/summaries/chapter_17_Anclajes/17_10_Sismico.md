# 17.10 REQUISITOS SISMICOS PARA ANCLAJES

## 17.10.1 Alcance

**17.10.1.1** Aplica a anclajes en estructuras asignadas a SDC C, D, E o F que:
- (a) Resisten cargas sismicas, o
- (b) Soporten componentes que requieren proteccion sismica

**17.10.1.2** Excepciones - No aplica a:
- Anclajes en miembros de concreto simple (Cap. 14)
- Anclajes disenados para E multiplicado por omega_o

## 17.10.2 Categorias de Diseno Sismico C, D, E, F

### Tabla 17.10.2 - Requisitos por SDC

| SDC | Requisitos |
|-----|------------|
| C | 17.10.3, 17.10.4, 17.10.6, 17.10.7 |
| D, E, F | Todos los requisitos de 17.10 |

## 17.10.3 Anclajes en Zonas de Rotulas Plasticas

**17.10.3.1** Anclajes NO deben ubicarse en:
- Zonas de rotulas plasticas de elementos del sistema sismo-resistente

**17.10.3.2** Excepcion:
- Anclajes usados para conectar elementos de concreto prefabricado
- Anclajes usados para conexiones que desarrollan la resistencia probable del miembro

## 17.10.4 Requisitos de Ductilidad

**17.10.4.1** Anclajes deben disenarse para comportamiento ductil:

**(a)** El elemento de acero debe ser ductil (17.2.4) Y gobernar la falla:
```
phi*Nn,acero <= phi*Nn,concreto * 1.0
phi*Vn,acero <= phi*Vn,concreto * 1.0
```

**(b)** O disenar para resistencia del mecanismo de fluencia del accesorio:
```
Nua = 1.4 * Sy     [tension]
Vua = 1.4 * Sy     [cortante]
```
donde Sy = fuerza de fluencia del accesorio conectado

## 17.10.5 Requisitos Adicionales para SDC D, E, F

**17.10.5.1** Anclajes de un solo anclaje:
- Disenar para comportamiento ductil (17.10.4), o
- Proveer refuerzo de anclaje (17.10.5.3)

**17.10.5.2** Grupos de anclajes:
- Minimo 4 anclajes
- Minimo 2 anclajes en cada direccion
- Disenar para redistribucion de carga

**17.10.5.3** Refuerzo de anclaje:
- Desarrollado a ambos lados del plano de falla
- Encerrado por estribos o amarres
- phi = 0.75

## 17.10.6 Factores de Reduccion Sismicos

**Tabla 17.10.6.1 - Factores phi para Cargas Sismicas**

| Modo de Falla | Sin Refuerzo Suplementario | Con Refuerzo Suplementario |
|---------------|---------------------------|---------------------------|
| Acero - tension (ductil) | 0.75 | 0.75 |
| Acero - tension (no ductil) | 0.65 | 0.65 |
| Concreto - tension | 0.70 | 0.75 |
| Acero - cortante (ductil) | 0.65 | 0.65 |
| Acero - cortante (no ductil) | 0.60 | 0.60 |
| Concreto - cortante | 0.70 | 0.75 |

## 17.10.7 Anclajes Post-Instalados en Aplicaciones Sismicas

**17.10.7.1** Anclajes de expansion:
- Solo tipo torque-controlled calificados para sismo
- Informe de calificacion debe indicar uso sismico

**17.10.7.2** Anclajes undercut:
- Permitidos si calificados para sismo segun ACI 355.2

**17.10.7.3** Anclajes adhesivos:
- Calificados segun ACI 355.4 para uso sismico
- Categoria 1 o 2 segun carga sostenida

---

*ACI 318-25 Seccion 17.10*
