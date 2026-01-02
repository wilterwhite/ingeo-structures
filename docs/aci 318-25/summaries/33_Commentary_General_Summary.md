# ACI 318-25 - COMENTARIO GENERAL
## Notas de Interpretacion y Cambios Respecto a ACI 318-19

---

## INDICE

- [Proposito del Comentario](#proposito-del-comentario)
- [Cambios Principales en ACI 318-25](#cambios-principales-en-aci-318-25)
- [Notas de Interpretacion por Capitulo](#notas-de-interpretacion-por-capitulo)
- [Erratas y Clarificaciones Comunes](#erratas-y-clarificaciones-comunes)
- [Filosofia de Diseno](#filosofia-de-diseno)
- [Referencias Clave](#referencias-clave)
- [Unidades y Notacion](#unidades-y-notacion)
- [Recomendaciones para Diseno](#recomendaciones-para-diseno)

---

## PROPOSITO DEL COMENTARIO

El Comentario del ACI 318 provee:
- Explicacion de la intencion del codigo
- Antecedentes de los requisitos
- Ejemplos de aplicacion
- Referencias a investigaciones
- Guia de interpretacion

---

## CAMBIOS PRINCIPALES EN ACI 318-25

### 1. MATERIALES

**Concreto de Alta Resistencia:**
- Limites actualizados para f'c > 10,000 psi
- Factores de modificacion para alta resistencia

**Acero de Refuerzo:**
- Expansion de uso de Grado 80 y 100
- Nuevos requisitos para ductilidad
- Actualizacion de tablas de desarrollo

**Sustentabilidad:**
- Nuevo Apendice C
- Guia para cementos alternativos
- Agregados reciclados

### 2. ANALISIS Y DISENO

**Analisis Estructural (Cap. 6):**
- Clarificaciones en efectos P-Delta
- Propiedades de seccion para analisis
- Metodo simplificado actualizado

**Diseno Sismico (Cap. 18):**
- Requisitos para Grado 80 y 100
- Actualizacion de factor alpha_sh
- Clarificaciones en elementos de borde

**Anclajes (Cap. 17):**
- Ecuaciones simplificadas
- Factores actualizados
- Nuevos requisitos sismicos

### 3. NUEVOS APENDICES

**Apendice B - Viento Basado en Desempeno:**
- Marco para edificios altos
- Criterios de confort
- Amortiguamiento suplementario

**Apendice C - Sustentabilidad:**
- Reduccion de huella de carbono
- Materiales alternativos
- Diseno para resiliencia

---

## NOTAS DE INTERPRETACION POR CAPITULO

### CAPITULO 5 - CARGAS

**R5.3.1** Combinaciones de carga:
- Las combinaciones del ACI 318 son consistentes con ASCE 7
- Para casos no cubiertos, usar criterio profesional
- Considerar cargas especiales segun uso

**R5.3.8** Carga viva reducida:
- Reducciones segun ASCE 7 estan permitidas
- No reducir para cargas de impacto o dinamicas

### CAPITULO 6 - ANALISIS

**R6.6.3** Inercia efectiva para analisis:
- Los valores de Tabla 6.6.3.1 son aproximados
- Para analisis mas preciso, usar Ie
- En estructuras esbeltas, considerar agrietamiento

**R6.6.4** Magnificacion de momentos:
- El metodo de magnificacion es conservador
- Para estructuras complejas, usar analisis de 2do orden
- Considerar interaccion marco-muro

### CAPITULO 9 - VIGAS

**R9.5.1** Resistencia a cortante:
- El modelo de 45 grados es simplificado
- Para vigas profundas, usar puntal-tensor
- Considerar efectos de carga axial

**R9.5.4** Refuerzo minimo de cortante:
- Previene falla fragil
- Asegura redistribucion de esfuerzos
- Controla ancho de fisuras

### CAPITULO 10 - COLUMNAS

**R10.3.1** Interaccion P-M:
- El diagrama de interaccion es base del diseno
- Considerar biaxialidad cuando aplique
- Efectos de esbeltez en columnas largas

**R10.6.1** Cuantia de refuerzo:
- 1% minimo asegura comportamiento ductil
- 8% maximo por congestion y vaciado
- En sismo, preferir cuantias moderadas

### CAPITULO 11 - MUROS

**R11.5.4** Cortante en plano:
- Acv incluye toda la longitud del muro
- Considerar aberturas en calculo de Acv
- Refuerzo horizontal resiste cortante

**R11.8** Muros esbeltos:
- Metodo aplicable cuando h/lw > 2.0
- Verificar pandeo fuera del plano
- Considerar excentricidad de cargas

### CAPITULO 18 - SISMICO

**R18.2.5** Materiales:
- Grado 60 preferido por experiencia
- Grado 80 requiere mas atencion al detallado
- Grado 100 solo en muros especiales

**R18.10.4.4** Factor alpha_sh:
- Nuevo en ACI 318-25
- Considera efecto del refuerzo transversal
- Reduce demanda de cortante efectiva

**R18.10.6** Elementos de borde:
- Criticos para ductilidad del muro
- Confinamiento previene pandeo de barras
- Extension segun perfil de deformaciones

### CAPITULO 21 - FACTORES PHI

**R21.2.1** Justificacion de factores:
- phi refleja incertidumbre en resistencia
- Menores para modos fragiles
- Transicion para flexion

**R21.2.2** Transicion controlado por tension/compresion:
- Asegura comportamiento ductil
- Incentiva diseno con mas acero de tension
- Penaliza columnas con alta carga axial

### CAPITULO 22 - RESISTENCIA SECCIONAL

**R22.5.1** Resistencia a cortante del concreto:
- Vc incluye efecto de agregados
- Reducido para alta resistencia
- Afectado por carga axial

**R22.6** Cortante bidireccional:
- Critico en losas planas
- Considerar transferencia de momento
- Capitel o drop panel mejoran capacidad

### CAPITULO 25 - DETALLES

**R25.4.2** Longitud de desarrollo:
- Ecuaciones basadas en investigacion
- Factores consideran condiciones de adherencia
- Mas restrictivo para barras superiores

**R25.5.2** Empalmes por traslape:
- Clase A y B por congestion
- Escalonar empalmes cuando sea posible
- Evitar en zonas de alta demanda sismica

---

## ERRATAS Y CLARIFICACIONES COMUNES

### Tabla de Erratas Frecuentes

| Seccion | Problema | Clarificacion |
|---------|----------|---------------|
| 6.6.4.4 | Calculo de Cm | Usar valor absoluto de M1/M2 |
| 18.7.4.1 | Longitud de confinamiento | Medida desde cara de nudo |
| 22.5.5.1 | Limite de Vs | Verificar tambien limite de espaciamiento |
| 25.4.3.1 | ldh minimo | Aplicar DESPUES de factores |

---

## FILOSOFIA DE DISENO

### Diseno por Resistencia

El ACI 318 usa el metodo de diseno por resistencia (LRFD):
```
phi * Rn >= Ru
```

Donde:
- phi = factor de reduccion de resistencia
- Rn = resistencia nominal
- Ru = resistencia requerida (factorada)

### Ductilidad

El codigo promueve comportamiento ductil mediante:
- Limites de cuantia de refuerzo
- Requisitos de confinamiento
- Detallado adecuado en zonas criticas
- Factores phi menores para modos fragiles

### Jerarquia de Falla

En diseno sismico, la jerarquia preferida es:
1. Fluencia de vigas (deseable)
2. Fluencia de columnas (evitar)
3. Falla de conexiones (evitar)
4. Falla por cortante (evitar)

---

## REFERENCIAS CLAVE

### Documentos ACI Complementarios

| Documento | Tema |
|-----------|------|
| ACI 318.2 | Comentario completo |
| ACI 315 | Detalles de refuerzo |
| ACI 347 | Encofrado |
| ACI 301 | Especificaciones |
| ACI 562 | Reparacion de concreto |

### Investigacion de Respaldo

| Tema | Investigadores Clave |
|------|---------------------|
| Cortante | Kani, ASCE-ACI 426 |
| Columnas | MacGregor, Siess |
| Muros | Paulay, Wallace |
| Anclajes | Eligehausen, Cook |
| Sismico | Park, Priestley |

---

## UNIDADES Y NOTACION

### Sistema de Unidades

El ACI 318-25 usa unidades US:
- Longitud: pulgadas (in), pies (ft)
- Fuerza: libras (lb), kips
- Esfuerzo: psi, ksi
- Momento: lb-in, kip-ft

### Notacion Importante

| Simbolo | Significado |
|---------|-------------|
| f'c | Resistencia especificada del concreto |
| fy | Resistencia a fluencia del acero |
| phi | Factor de reduccion de resistencia |
| lambda | Factor de concreto liviano |
| psi | Factores de modificacion |

---

## RECOMENDACIONES PARA DISENO

### Buenas Practicas

1. **Simplicidad:** Preferir configuraciones simples y regulares
2. **Redundancia:** Proveer multiples trayectorias de carga
3. **Ductilidad:** Detallar para comportamiento ductil
4. **Constructibilidad:** Considerar fabricacion y montaje
5. **Inspeccion:** Facilitar acceso para verificacion

### Errores Comunes a Evitar

1. Olvidar verificar cortante en nudos
2. Empalmes en zonas de alta demanda
3. Espaciamiento excesivo de estribos
4. Recubrimiento insuficiente
5. Anclaje inadecuado en apoyos

---

*Comentario general del ACI 318-25.*
*Fecha: 2025*
