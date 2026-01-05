# 13.2 GENERALIDADES

## 13.2.1 Materiales

| Seccion | Requisito | Referencia |
|---------|-----------|------------|
| 13.2.1.1 | Propiedades de diseno del concreto | Capitulo 19 |
| 13.2.1.2 | Propiedades de diseno del refuerzo | Capitulo 20 |
| 13.2.1.3 | Empotramientos en concreto | 20.6 |

## 13.2.2 Conexion a Otros Miembros
**13.2.2.1** Diseno y detallado de conexiones de columnas, pedestales y muros colados en sitio y precolados a fundaciones segun **16.3**.

## 13.2.3 Efectos Sismicos

| Seccion | Requisito |
|---------|-----------|
| 13.2.3.1 | Miembros estructurales que se extienden debajo de la base de la estructura y transmiten fuerzas sismicas a la fundacion deben disenarse segun 18.2.2.3 |
| 13.2.3.2 | Para estructuras asignadas a **SDC C, D, E o F**: fundaciones que resisten o transfieren fuerzas sismicas deben disenarse segun 18.13 |

> **NOTA**: La base de una estructura, segun se define en el analisis, no necesariamente corresponde a la fundacion o nivel del suelo.

## 13.2.4 Losas sobre Terreno (Slabs-on-Ground)

| Seccion | Requisito |
|---------|-----------|
| 13.2.4.1 | Losas sobre terreno que transmiten cargas verticales o fuerzas laterales deben disenarse y detallarse segun este Codigo |
| 13.2.4.2 | Losas sobre terreno que transmiten fuerzas laterales como parte del sistema sismo-resistente deben disenarse segun 18.13 |

> **NOTA**: Las losas sobre terreno frecuentemente actuan como diafragma para mantener el edificio unido a nivel del suelo.

## 13.2.5 Concreto Simple
**13.2.5.1** Fundaciones de concreto simple deben disenarse segun **Capitulo 14**.

## 13.2.6 Criterios de Diseno

### 13.2.6.1 Proporciones de Fundacion
Las fundaciones deben proporcionarse para:
- Efectos de apoyo (bearing)
- Estabilidad contra volteo
- Estabilidad contra deslizamiento en la interfaz suelo-fundacion

Segun el codigo general de edificacion.

### 13.2.6.2 Resistencia a Cortante para Fundaciones Superficiales Rigidas
Para fundaciones superficiales continuamente apoyadas en suelo y disenadas asumiendo comportamiento rigido:

**(a) Cortante en una direccion:**
```
Vc = 2*lambda*sqrt(fc') * bw * d
```

**(b) Cortante en dos direcciones:**
El factor de efecto de tamano lambda_s (segun 22.6) puede tomarse igual a **1.0**

> **NOTA**: Esta provision se basa en el comportamiento satisfactorio historico de fundaciones superficiales sin considerar efectos de tamano.

### 13.2.6.3 Cargas Factorizadas
Los miembros de fundacion deben disenarse para resistir cargas factorizadas y reacciones inducidas correspondientes, excepto lo permitido en 13.4.2.

### 13.2.6.4 Metodos de Diseno Alternativos
Se permite disenar sistemas de fundacion por cualquier procedimiento que satisfaga equilibrio y compatibilidad geometrica.

### 13.2.6.5 Metodo Puntal-Tensor
Se permite el diseno de fundaciones segun el metodo puntal-tensor del **Capitulo 23**.

### 13.2.6.6 Momento Externo
El momento externo en cualquier seccion de zapata corrida, zapata aislada o cabezal de pilotes debe calcularse pasando un plano vertical a traves del miembro y calculando el momento de las fuerzas actuando sobre toda el area del miembro a un lado de ese plano.

---

## 13.2.7 Secciones Criticas para Fundaciones Superficiales y Cabezales

### Tabla 13.2.7.1 - Ubicacion de Seccion Critica para Mu

| Miembro Soportado | Ubicacion de Seccion Critica |
|-------------------|------------------------------|
| Columna o pedestal | Cara de columna o pedestal |
| Columna con placa base de acero | A mitad de camino entre cara de columna y borde de placa |
| Muro de concreto | Cara del muro |
| Muro de mamposteria | A mitad de camino entre centro y cara del muro |

### 13.2.7.2 Seccion Critica para Cortante
La ubicacion de la seccion critica para cortante factorizado:
- **Cortante en una direccion**: segun 7.4.3 y 8.4.3
- **Cortante en dos direcciones**: segun 8.4.4.1

Medida desde la ubicacion de la seccion critica para Mu en 13.2.7.1.

### 13.2.7.3 Columnas Circulares o Poligonales
Se permite tratar como miembros cuadrados de area equivalente al ubicar secciones criticas para momento, cortante y desarrollo de refuerzo.

---

## 13.2.8 Desarrollo de Refuerzo en Fundaciones Superficiales y Cabezales

| Seccion | Requisito |
|---------|-----------|
| 13.2.8.1 | Desarrollo de refuerzo segun Capitulo 25 |
| 13.2.8.2 | Fuerza calculada en tension o compresion debe desarrollarse a cada lado de la seccion |
| 13.2.8.3 | Secciones criticas en mismas ubicaciones que 13.2.7.1 para momento maximo y donde ocurren cambios de seccion o refuerzo |
| 13.2.8.4 | Embedment adecuado para refuerzo en tension donde el esfuerzo no es directamente proporcional al momento (zapatas inclinadas, escalonadas o ahusadas) |

## 13.2.9 Recubrimiento de Concreto
**13.2.9.1** Recubrimiento para refuerzo en miembros de fundacion segun **20.5.1.3**.

---

*ACI 318-25 Seccion 13.2*
