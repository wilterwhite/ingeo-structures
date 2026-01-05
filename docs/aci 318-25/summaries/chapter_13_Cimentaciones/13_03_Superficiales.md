# 13.3 FUNDACIONES SUPERFICIALES

## 13.3.1 General

| Seccion | Requisito |
|---------|-----------|
| 13.3.1.1 | Area minima de base proporcionada para no exceder la presion de apoyo permisible. Presiones permisibles determinadas por mecanica de suelos segun codigo general de edificacion |
| 13.3.1.2 | **Profundidad total** seleccionada tal que la profundidad efectiva del refuerzo inferior sea **al menos 6 in.** |
| 13.3.1.3 | En zapatas inclinadas, escalonadas o ahusadas: profundidad, ubicacion de escalones o angulo de inclinacion tal que los requisitos de diseno se satisfagan en cada seccion |

---

## 13.3.2 Fundaciones Superficiales en Una Direccion

**13.3.2.1** Diseno y detallado de fundaciones superficiales en una direccion (zapatas corridas, combinadas, vigas de fundacion) segun esta seccion y provisiones aplicables de **Capitulo 7** y **Capitulo 9**.

**13.3.2.2** El refuerzo debe distribuirse **uniformemente** a lo largo de todo el ancho de las zapatas en una direccion.

---

## 13.3.3 Zapatas Aisladas en Dos Direcciones

**13.3.3.1** Diseno y detallado segun esta seccion y provisiones aplicables de **Capitulo 7** y **Capitulo 8**.

**13.3.3.2** En zapatas cuadradas en dos direcciones:
- Refuerzo distribuido **uniformemente** a lo largo de todo el ancho de la zapata en ambas direcciones

**13.3.3.3** En zapatas rectangulares, el refuerzo debe distribuirse segun:

**(a) Direccion larga:**
- Refuerzo distribuido uniformemente a lo largo de todo el ancho de la zapata

**(b) Direccion corta:**
- Una porcion del refuerzo total, **gamma_s x As**, distribuida uniformemente sobre una banda de ancho igual a la longitud del lado corto, centrada en el eje de columna o pedestal
- El resto del refuerzo, **(1 - gamma_s) x As**, distribuido uniformemente fuera del ancho de banda central

**Factor de distribucion:**
```
gamma_s = 2 / (beta + 1)
```

Donde **beta** = relacion de lado largo a lado corto de la zapata

> **NOTA**: Para minimizar errores de construccion, una practica comun es aumentar la cantidad de refuerzo en la direccion corta por 2*beta/(beta + 1) y espaciarlo uniformemente.

---

## 13.3.4 Zapatas Combinadas y Losas de Fundacion en Dos Direcciones

| Seccion | Requisito |
|---------|-----------|
| 13.3.4.1 | Diseno y detallado segun esta seccion y provisiones aplicables del Capitulo 8 |
| 13.3.4.2 | El **metodo de diseno directo NO debe usarse** para disenar zapatas combinadas y losas de fundacion |
| 13.3.4.3 | Distribucion de presion de apoyo debe ser consistente con propiedades del suelo/roca y la estructura, y principios de mecanica de suelos |
| 13.3.4.4 | Refuerzo minimo en losas de fundacion no presforzadas segun **8.6.1.1** (As,min = 0.0018Ag) |

> **NOTA**: Recomendaciones detalladas en ACI PRC-336.2.

---

## 13.3.5 Muros como Vigas de Fundacion

| Seccion | Requisito |
|---------|-----------|
| 13.3.5.1 | Diseno segun provisiones aplicables del Capitulo 9 |
| 13.3.5.2 | Si el muro de viga de fundacion se considera viga profunda segun 9.9.1.1, el diseno debe satisfacer los requisitos de 9.9 |
| 13.3.5.3 | Muros de viga de fundacion deben satisfacer requisitos minimos de refuerzo de 11.6 |

---

## 13.3.6 Componentes de Muro de Muros de Contencion en Voladizo

### 13.3.6.1 Vastago de Muro en Voladizo Simple
- Disenar como losa en una direccion segun provisiones aplicables del **Capitulo 7**

**Resistencia a cortante del concreto:**
```
Vc = 2*lambda*sqrt(fc') * bw * d
```

> **NOTA**: Esta provision se basa en el desempeno historico satisfactorio de muros de contencion en voladizo disenados bajo ediciones anteriores del Codigo.

### 13.3.6.2 Muros con Contrafuertes o Estribos
- Disenar el vastago como losa en dos direcciones segun provisiones aplicables del **Capitulo 8**

> **NOTA**: Muros con contrafuertes tienden a comportarse mas en accion bidireccional que unidireccional.

### 13.3.6.3 Seccion Critica
| Tipo de Muro | Seccion Critica |
|--------------|-----------------|
| Espesor uniforme | Interfaz entre vastago y zapata |
| Espesor variable o ahusado | Investigar cortante y momento a lo largo de toda la altura |

---

## 13.3.7 Muros de Sotano

**13.3.7.1** Diseno de muros de sotano para resistir presion lateral de tierra fuera del plano:

| Requisito | Descripcion |
|-----------|-------------|
| (a) | Disenar como losas en una direccion (Capitulo 7) o en dos direcciones (Capitulo 8) |
| (b) | Disenar para resistir presion hidrostatica, si aplica |
| (c) | Resistencia a cortante en una direccion: Vc = 2*lambda*sqrt(fc') * bw * d |
| (d) | Para cortante en dos direcciones: factor de efecto de tamano lambda_s = 1.0 |
| (e) | Satisfacer provisiones aplicables del Capitulo 18 |

**13.3.7.2** Para cargas distintas a presion lateral de tierra fuera del plano, satisfacer provisiones aplicables del **Capitulo 11**.

---

*ACI 318-25 Seccion 13.3*
