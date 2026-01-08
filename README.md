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
├── __init__.py                              # Flask app factory
├── domain/                                  # Lógica de negocio ACI 318-25
│   ├── __init__.py                          # Re-exports de dominio
│   ├── calculations/
│   │   ├── __init__.py
│   │   ├── confinement.py                   # Refuerzo de confinamiento
│   │   ├── steel_layer_calculator.py        # Capas de acero
│   │   └── wall_continuity.py               # Continuidad vertical muros
│   ├── chapter7/                            # Losas (Cap. 7)
│   │   ├── __init__.py
│   │   ├── limits.py                        # Espesores mínimos losas
│   │   └── reinforcement.py                 # Refuerzo mínimo losas
│   ├── chapter8/                            # Losas 2-Way (Cap. 8)
│   │   ├── __init__.py
│   │   ├── limits.py                        # Límites losas bidireccionales
│   │   └── punching/
│   │       ├── __init__.py
│   │       ├── critical_section.py          # Sección crítica punzonamiento
│   │       └── vc_calculation.py            # Vc punzonamiento
│   ├── chapter11/                           # Muros (Cap. 11)
│   │   ├── __init__.py
│   │   ├── design_methods.py                # Método simplificado/detallado
│   │   ├── limits.py                        # Espesores y cuantías mínimas
│   │   └── reinforcement.py                 # Distribución de armadura
│   ├── chapter18/                           # Requisitos sísmicos (Cap. 18)
│   │   ├── __init__.py
│   │   ├── results.py                       # Dataclasses de resultados
│   │   ├── boundary_elements/               # Elementos de borde §18.10.6
│   │   │   ├── __init__.py
│   │   │   ├── confinement.py               # Confinamiento elementos borde
│   │   │   ├── dimensions.py                # Dimensiones elementos borde
│   │   │   ├── displacement.py              # Método desplazamientos
│   │   │   ├── service.py                   # Orquestador borde
│   │   │   └── stress.py                    # Método tensiones
│   │   ├── coupling_beams/                  # Vigas acople §18.10.7
│   │   │   ├── __init__.py
│   │   │   ├── classification.py            # Clasificación ln/h
│   │   │   ├── confinement.py               # Confinamiento vigas
│   │   │   ├── diagonal.py                  # Armadura diagonal
│   │   │   └── service.py                   # Orquestador vigas acople
│   │   ├── design_forces/                   # Fuerzas de diseño §18.10.3
│   │   │   ├── __init__.py
│   │   │   ├── factors.py                   # Factores Ωv, ωv
│   │   │   └── service.py                   # Amplificación cortante
│   │   ├── reinforcement/                   # Refuerzo sísmico
│   │   │   ├── __init__.py
│   │   │   ├── results.py                   # Resultados refuerzo
│   │   │   └── service.py                   # Verificación refuerzo §18.10.2
│   │   └── wall_piers/                      # Wall piers §18.10.8
│   │       ├── __init__.py
│   │       ├── boundary_zones.py            # Zonas de borde piers
│   │       ├── classification.py            # Clasificación lw/bw
│   │       ├── service.py                   # Orquestador wall piers
│   │       ├── shear_design.py              # Diseño cortante piers
│   │       └── transverse.py                # Refuerzo transversal
│   ├── constants/
│   │   ├── __init__.py
│   │   ├── materials.py                     # Propiedades materiales
│   │   ├── phi_chapter21.py                 # Factores φ Cap. 21
│   │   ├── reinforcement.py                 # Diámetros y áreas barras
│   │   ├── seismic.py                       # SDC y categorías muros
│   │   ├── shear.py                         # Constantes de corte
│   │   ├── stiffness.py                     # Factores rigidez fisurada
│   │   └── units.py                         # Conversión unidades
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── beam.py                          # Entidad Beam
│   │   ├── beam_forces.py                   # Fuerzas en vigas
│   │   ├── column.py                        # Entidad Column
│   │   ├── column_forces.py                 # Fuerzas en columnas
│   │   ├── coupling_beam.py                 # Entidad CouplingBeam
│   │   ├── design_proposal.py               # Propuesta de diseño
│   │   ├── load_combination.py              # Combinación de carga
│   │   ├── parsed_data.py                   # Datos parseados ETABS
│   │   ├── pier.py                          # Entidad Pier
│   │   ├── pier_forces.py                   # Fuerzas en piers
│   │   ├── protocols.py                     # Protocolos/interfaces
│   │   ├── slab.py                          # Entidad Slab
│   │   └── slab_forces.py                   # Fuerzas en losas
│   ├── flexure/
│   │   ├── __init__.py
│   │   ├── checker.py                       # Verificador flexión SF
│   │   ├── interaction_diagram.py           # Diagrama P-M
│   │   └── slenderness.py                   # Esbeltez y magnificación
│   └── shear/
│       ├── __init__.py
│       ├── classification.py                # Clasificación muro/columna
│       ├── results.py                       # Resultados de corte
│       ├── shear_friction.py                # Fricción cortante
│       └── verification.py                  # Vc + Vs verificación
├── routes/
│   ├── __init__.py
│   └── analysis.py                          # Endpoints API REST
├── services/
│   ├── __init__.py
│   ├── factory.py                           # Factory de servicios
│   ├── pier_analysis.py                     # Orquestador principal
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── element_classifier.py            # Clasificador elementos
│   │   ├── element_verification_service.py  # Verificación unificada
│   │   ├── flexocompression_service.py      # Servicio flexocompresión
│   │   ├── pier_capacity_service.py         # Capacidades de piers
│   │   ├── pier_verification_service.py     # Verificación ACI piers
│   │   ├── proposal_service.py              # Propuestas automáticas
│   │   ├── punching_service.py              # Verificación punzonamiento
│   │   ├── shear_service.py                 # Servicio de corte
│   │   ├── slab_service.py                  # Verificación losas
│   │   ├── statistics_service.py            # Estadísticas y resumen
│   │   ├── verification_config.py           # Configuración verificación
│   │   └── verification_result.py           # Dataclasses resultados
│   ├── parsing/
│   │   ├── __init__.py
│   │   ├── beam_parser.py                   # Parser vigas ETABS
│   │   ├── column_parser.py                 # Parser columnas ETABS
│   │   ├── excel_parser.py                  # Parser Excel principal
│   │   ├── material_mapper.py               # Mapeo materiales
│   │   ├── reinforcement_config.py          # Config armadura defecto
│   │   ├── session_manager.py               # Gestor sesiones
│   │   ├── slab_parser.py                   # Parser losas ETABS
│   │   └── table_extractor.py               # Extractor tablas Excel
│   ├── presentation/
│   │   ├── __init__.py
│   │   ├── plot_generator.py                # Generador gráficos P-M
│   │   └── result_formatter.py              # Formateador resultados UI
│   └── report/
│       ├── __init__.py
│       ├── pdf_generator.py                 # Generador PDF reportes
│       └── report_config.py                 # Configuración reportes
├── static/                                  # CSS, JavaScript
└── templates/                               # HTML Jinja2
```

## Capas de la Arquitectura

### 1. `routes/` - Capa de Presentación (API REST)
Expone endpoints HTTP para el frontend. No contiene lógica de negocio.

### 2. `services/` - Capa de Aplicación (Orquestación)
Coordina el flujo de trabajo, gestiona sesiones y formatea resultados para la UI.
**No implementa cálculos ACI** - delega todo al dominio.

### 3. `domain/` - Capa de Dominio (Lógica de Negocio)
Implementa todos los cálculos según ACI 318-25. Es independiente de Flask, Excel o UI.
Los servicios de dominio son **la única fuente de verdad** para fórmulas y requisitos del código.

```
┌─────────────────────────────────────────────────────────────────┐
│  routes/analysis.py                          API REST (Flask)   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  services/pier_analysis.py              Orquestador principal   │
│  ├── ElementService          → Verificación unificada          │
│  ├── PierVerificationService → Conformidad ACI Cap 11/18       │
│  └── PierCapacityService     → Diagramas y capacidades         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  domain/                                Lógica ACI 318-25       │
│  ├── chapter11/    → Muros: límites, cuantías, métodos         │
│  ├── chapter18/    → Sísmico: borde, amplificación, piers      │
│  ├── flexure/      → P-M, esbeltez, magnificación              │
│  └── shear/        → Vc, Vs, clasificación                     │
└─────────────────────────────────────────────────────────────────┘
```

## Servicios de Aplicación (`services/`)

| Servicio | Responsabilidad |
|----------|-----------------|
| `PierAnalysisService` | Orquestador principal, gestiona sesiones y flujo |
| `ElementService` | Verificación unificada de Beam/Column/Pier (SF, DCR) |
| `PierVerificationService` | Conformidad ACI 318-25 Caps 11 y 18 |
| `PierCapacityService` | Genera diagramas de sección y capacidades |
| `FlexocompressionService` | Genera curvas P-M de interacción |
| `ShearService` | Calcula Vc + Vs y DCR de corte |
| `ProposalService` | Genera propuestas de diseño cuando falla |
| `StatisticsService` | Estadísticas y gráfico resumen |

## Servicios de Dominio (`domain/`)

### `domain/chapter11/` - Muros (Cap. 11)

| Servicio | Responsabilidad |
|----------|-----------------|
| `WallLimitsService` | Espesores mínimos, espaciamientos máximos |
| `ReinforcementLimitsService` | Cuantías mínimas ρ_min |
| `WallDesignMethodsService` | Método simplificado vs detallado |

### `domain/chapter18/` - Requisitos Sísmicos (Cap. 18)

| Servicio | Responsabilidad |
|----------|-----------------|
| `ShearAmplificationService` | Amplificación Ωv×ωv (§18.10.3) |
| `BoundaryElementService` | Elementos de borde (§18.10.6) |
| `WallPierService` | Wall piers (§18.10.8) |
| `CouplingBeamService` | Vigas de acople (§18.10.7) |

### `domain/flexure/` - Flexocompresión

| Servicio | Responsabilidad |
|----------|-----------------|
| `InteractionDiagramService` | Genera curva P-M (φPn, φMn) |
| `SlendernessService` | Esbeltez, Pc, δns, M2,min |
| `FlexureChecker` | Compara demanda vs capacidad |

### `domain/shear/` - Corte

| Servicio | Responsabilidad |
|----------|-----------------|
| `ShearVerificationService` | Calcula Vc + Vs |
| `WallClassificationService` | Clasifica muro vs columna |

## Flujo de Verificación

```
┌─────────────────────────────────────────┐
│            Excel ETABS                  │
│   (Pier Forces, Pier Sections)          │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│         ExcelParser (parsing/)          │
│   Extrae piers, fuerzas, materiales     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│      PierAnalysisService (services/)    │
│         Orquestador principal           │
└──────┬───────────┬───────────┬──────────┘
       │           │           │
       ▼           ▼           ▼
┌────────────┐ ┌─────────┐ ┌──────────────┐
│ ElementSvc │ │ShearSvc │ │PierVerifySvc │
│            │ │         │ │              │
│ • P-M      │ │ • Vc+Vs │ │ • Cap 11     │
│ • Esbeltez │ │ • DCR   │ │ • Cap 18     │
│ • SF       │ │         │ │ • Borde      │
└─────┬──────┘ └────┬────┘ └──────┬───────┘
      │             │             │
      └──────┬──────┴─────────────┘
             │
             ▼
   ┌─────────────────────┐
   │  ¿SF ≥ 1 y DCR ≤ 1? │
   └─────────┬───────────┘
             │
    ┌────────┴────────┐
    │ NO              │ SÍ
    ▼                 ▼
┌──────────────┐  ┌────────┐
│ProposalSvc   │  │ ✓ PASA │
│Genera        │  │        │
│propuesta     │  │        │
└──────────────┘  └────────┘
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
