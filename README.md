# INGEO Structures - Verificación Estructural ACI 318-25

Aplicación web para verificación estructural de elementos de hormigón armado según ACI 318-25.

## Elementos Soportados

| Elemento | Verificaciones | Tablas ETABS |
|----------|----------------|--------------|
| **Piers (Muros)** | Flexocompresión P-M + Cortante V2-V3 | Pier Section Properties, Pier Forces |
| **Columnas** | Flexocompresión P-M + Cortante V2-V3 | Frame Sec Def - Conc Rect, Element Forces - Columns |
| **Vigas** | Cortante (solo por ahora) | Frame Sec Def - Conc Rect, Element Forces - Beams |
| **Spandrels** | Cortante (vigas de acople) | Spandrel Section Properties, Spandrel Forces |

## Características

- Importación directa de archivos Excel exportados de ETABS
- Detección automática de tablas disponibles (piers, columnas, vigas)
- Verificación de flexocompresión con diagrama de interacción P-M
- Verificación de corte bidireccional (V2-V3) con DCR combinado
- Análisis de esbeltez y magnificación de momentos
- Clasificación automática de elementos (muro, columna, wall-pier)
- **Propuestas automáticas de diseño** cuando un elemento falla
- Interfaz web interactiva con edición inline de armadura

## Arquitectura

```
app/
├── domain/                     # Lógica de negocio (cálculos ACI 318-25)
│   ├── chapter11/              # Capítulo 11: Muros - Límites y métodos
│   ├── chapter18/              # Capítulo 18: Muros sísmicos - Requisitos especiales
│   ├── flexure/                # Flexocompresión: Diagramas P-M, esbeltez
│   ├── shear/                  # Corte: Verificación, fricción, clasificación
│   ├── entities/               # Estructuras de datos
│   ├── constants/              # Constantes y conversión de unidades
│   └── calculations/           # Calculadores puros
│
├── services/                   # Orquestación y servicios de aplicación
│   ├── analysis/               # Servicios de análisis (SF, DCR)
│   ├── parsing/                # Parsing de Excel ETABS
│   └── presentation/           # Generación de gráficos
│
├── routes/                     # API REST (Flask)
├── templates/                  # HTML (Jinja2)
└── static/                     # CSS, JavaScript
```

## Organización del Dominio

### `domain/chapter11/` - Muros Estructurales (ACI 318-25 Cap. 11)

Contiene **límites y métodos de diseño** para muros no sísmicos:

| Archivo | Contenido |
|---------|-----------|
| `limits.py` | Espesores mínimos, cuantías de refuerzo, espaciamientos máximos |
| `design_methods.py` | Método simplificado vs método detallado de diseño |
| `reinforcement.py` | Distribución de armadura, capas, recubrimientos |

### `domain/chapter18/` - Muros Sísmicos (ACI 318-25 Cap. 18)

Contiene **requisitos sísmicos especiales** para SDC D, E, F:

| Archivo | Contenido |
|---------|-----------|
| `piers.py` | Clasificación de wall piers (§18.10.8) |
| `boundary_elements.py` | Elementos de borde: cuándo se requieren, dimensiones (§18.10.6) |
| `amplification.py` | Amplificación de cortante Ωv×ωv (§18.10.3) |
| `coupling_beams.py` | Vigas de acople: requisitos de armadura diagonal |

### `domain/flexure/` - Flexocompresión

**Cálculo de capacidad** y verificación de flexión:

| Archivo | Contenido |
|---------|-----------|
| `interaction_diagram.py` | Genera curva P-M de capacidad (φPn, φMn) |
| `slenderness.py` | Esbeltez: λ, Pc, δns, momento mínimo M2,min, factor Cm |
| `checker.py` | Compara demanda vs capacidad, calcula SF |

### `domain/shear/` - Corte

**Cálculo de resistencia** y verificación de corte:

| Archivo | Contenido |
|---------|-----------|
| `verification.py` | Vc (concreto) + Vs (acero), fórmulas muro vs columna |
| `classification.py` | Determina si usar fórmula de muro o columna |
| `shear_friction.py` | Fricción cortante en juntas de construcción |
| `results.py` | Estructuras de resultado de corte |

### `domain/entities/` - Estructuras de Datos

| Entidad | Descripción |
|---------|-------------|
| `Pier` | Muro con geometría, materiales y armadura |
| `PierForces` | Colección de combinaciones de carga para piers |
| `Column` | Columna con geometría, materiales y armadura |
| `ColumnForces` | Colección de combinaciones de carga para columnas |
| `Beam` | Viga (frame o spandrel) con geometría y armadura |
| `BeamForces` | Colección de combinaciones de carga para vigas |
| `LoadCombination` | P, M2, M3, V2, V3 de una combinación |
| `VerificationResult` | Resultado completo de verificación |
| `DesignProposal` | Propuesta de diseño cuando falla |

### `domain/constants/` - Constantes

| Archivo | Contenido |
|---------|-----------|
| `units.py` | Conversiones: N↔tonf, mm↔m, MPa↔psi |
| `materials.py` | Propiedades de hormigón y acero |
| `seismic.py` | Categorías de diseño sísmico (SDC) |

## Servicios de Análisis

Los servicios en `services/analysis/` **orquestan los cálculos** y producen factores de seguridad:

### `FlexureService`
```
Pier + Fuerzas → InteractionDiagram → SlendernessService → SF de flexión
```
- Genera diagrama P-M de capacidad
- Aplica magnificación de momentos si es esbelto
- Calcula SF = φMn / Mu para cada combinación

### `ShearService`
```
Pier + Fuerzas → Classification → Vc + Vs → DCR de corte
```
- Clasifica el elemento (muro vs columna)
- Calcula Vc según tipo (αc√f'c para muros, 0.17√f'c para columnas)
- Calcula Vs del refuerzo horizontal
- DCR = √(DCR₂² + DCR₃²) combinando ambas direcciones

### `ProposalService`
```
SF < 1.0 o DCR > 1.0 → Analiza modo de falla → Propuesta automática
```
- **Flexión falla** → Aumenta barras de borde progresivamente
- **Corte falla** → Reduce espaciamiento o aumenta diámetro de malla
- **Combinado** → Mejora ambos iterativamente
- **Esbeltez** → Propone aumento de espesor

### `BeamService`
```
Beam + Fuerzas → Vc + Vs → DCR de corte
```
- Calcula Vc = 0.17λ√f'c × bw × d
- Calcula Vs = Av × fy × d / s
- Verifica φVn ≥ Vu para cada combinación

### `ColumnService`
```
Column + Fuerzas → P-M Diagram + Corte V2-V3 → SF y DCR
```
- Genera diagrama P-M de capacidad para ambas direcciones
- Verifica cortante en V2 y V3 con interacción SRSS
- Calcula esbeltez y factor de reducción por pandeo

### `ACI318_25_Service`
Integra verificaciones adicionales del Capítulo 18:
- Clasificación de elementos (§18.10.8)
- Amplificación de cortante (§18.10.3.3)
- Elementos de borde (§18.10.6)

## Flujo de Verificación

```
                    ┌─────────────────────────────────────┐
                    │         Excel ETABS                 │
                    │  (Pier Forces, Pier Sections)       │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │         EtabsExcelParser            │
                    │  Extrae piers, fuerzas, materiales  │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │         PierAnalysisService         │
                    │       (Orquestador principal)       │
                    └───┬─────────────┬─────────────┬─────┘
                        │             │             │
           ┌────────────▼──┐   ┌──────▼──────┐   ┌──▼────────────┐
           │FlexureService │   │ShearService │   │ACI318_25_Svc  │
           │               │   │             │   │               │
           │ • P-M Diagram │   │ • Vc + Vs   │   │ • Clasific.   │
           │ • Slenderness │   │ • DCR₂, DCR₃│   │ • Amplific.   │
           │ • SF flexión  │   │ • DCR comb. │   │ • Borde       │
           └───────┬───────┘   └──────┬──────┘   └───────┬───────┘
                   │                  │                  │
                   └────────────┬─────┴──────────────────┘
                                │
                                ▼
                   ┌────────────────────────┐
                   │   ¿SF ≥ 1 y DCR ≤ 1?   │
                   └─────────┬──────────────┘
                             │
              ┌──────────────┴──────────────┐
              │ NO                          │ SÍ
              ▼                             ▼
    ┌─────────────────────┐       ┌─────────────────┐
    │  ProposalService    │       │  ✓ PASA         │
    │  Genera propuesta   │       │                 │
    │  automática         │       │                 │
    └─────────────────────┘       └─────────────────┘
```

## Ejecución

```bash
# Desde la raíz del proyecto
python run.py

# El servidor inicia en http://localhost:5001
```

## Uso de la API

### Parsear Excel
```python
POST /structural/parse
Content-Type: multipart/form-data
file: <archivo.xlsx>

Response: { session_id, piers: [...], statistics: {...} }
```

### Analizar
```python
POST /structural/analyze
{
    "session_id": "...",
    "pier_updates": [...],  # Opcional: modificar armadura
    "generate_plots": true,
    "moment_axis": "M3"
}

Response: { results: [...], statistics: {...}, summary_plot: "base64..." }
```

## Sistema de Unidades

| Magnitud | Unidad Interna | Unidad Salida |
|----------|----------------|---------------|
| Longitud | mm | m (geometría) |
| Fuerza | N | tonf |
| Momento | N-mm | tonf-m |
| Esfuerzo | MPa | MPa |

Conversiones en `domain/constants/units.py` según ACI 318-25 Apéndice E.

## Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_proposal_service.py -v
pytest tests/domain/flexure/test_slenderness.py -v
```

## Limitaciones Conocidas

### Secciones Soportadas
- **Piers y Spandrels**: Solo secciones lineales (rectangulares)
- **Columnas**: Solo secciones rectangulares de concreto
- **Vigas**: Solo secciones rectangulares de concreto
- **NO soportado**: Secciones en T, L, C, o formas compuestas

### Alcance de Verificación por Elemento

| Elemento | Verificación Implementada | Pendiente |
|----------|---------------------------|-----------|
| **Piers** | Flexocompresión + Cortante + Esbeltez + Requisitos sísmicos (§18.10) | - |
| **Columnas** | Flexocompresión básica + Cortante | Requisitos sísmicos (§18.7) |
| **Vigas** | Cortante | Flexión, Deflexiones |

### Tablas ETABS Requeridas

Para que el sistema procese cada tipo de elemento, se requieren las siguientes tablas:

**Piers:**
- `Wall Property Definitions` - Materiales de muros
- `Pier Section Properties` - Geometría de piers
- `Pier Forces` - Fuerzas por combinación

**Columnas:**
- `Frame Section Property Definitions - Concrete Rectangular` - Secciones (con Design Type = "Column")
- `Element Forces - Columns` - Fuerzas por combinación

**Vigas:**
- `Frame Section Property Definitions - Concrete Rectangular` - Secciones (con Design Type = "Beam")
- `Element Forces - Beams` - Fuerzas por combinación

**Spandrels (Vigas de Acople):**
- `Spandrel Section Properties` - Geometría
- `Spandrel Forces` - Fuerzas por combinación

## Referencias

- ACI 318-25: Building Code Requirements for Structural Concrete
- Capítulo 6: Análisis estructural (esbeltez, momentos de diseño)
- Capítulo 11: Muros (límites, refuerzo distribuido)
- Capítulo 18: Estructuras resistentes a sismo (muros especiales)
- Capítulo 22: Resistencia de secciones (flexión, corte)
- Apéndice E: Equivalencias de unidades SI/US
