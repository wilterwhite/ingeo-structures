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
│   │   ├── common/                          # Infraestructura común
│   │   │   └── seismic_category.py          # SeismicCategory enum
│   │   ├── results.py                       # Dataclasses de resultados
│   │   ├── beams/                           # Vigas sísmicas §18.6
│   │   │   ├── __init__.py
│   │   │   ├── results.py                   # SeismicBeamResult
│   │   │   └── service.py                   # SeismicBeamService
│   │   ├── columns/                         # Columnas sísmicas §18.7
│   │   │   ├── __init__.py
│   │   │   ├── dimensional.py               # Límites dimensionales
│   │   │   ├── flexural_strength.py         # Columna fuerte-viga débil
│   │   │   ├── longitudinal.py              # Refuerzo longitudinal
│   │   │   ├── results.py                   # SeismicColumnResult
│   │   │   ├── service.py                   # SeismicColumnService
│   │   │   ├── shear.py                     # Cortante sísmico
│   │   │   └── transverse.py                # Refuerzo transversal
│   │   ├── non_sfrs/                        # No-SFRS §18.14
│   │   │   ├── __init__.py
│   │   │   ├── results.py                   # NonSfrsResult
│   │   │   └── service.py                   # NonSfrsService
│   │   ├── coupled_walls/                   # Muros acoplados §18.10.9
│   │   │   ├── __init__.py
│   │   │   ├── results.py                   # DuctileCoupledWallResult
│   │   │   └── service.py                   # DuctileCoupledWallService
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
│   │   ├── design_proposal.py               # Propuesta de diseño (dataclasses)
│   │   ├── load_combination.py              # Combinación de carga
│   │   ├── parsed_data.py                   # Datos parseados ETABS
│   │   ├── pier.py                          # Entidad Pier
│   │   ├── pier_forces.py                   # Fuerzas en piers
│   │   ├── protocols.py                     # Protocolos/interfaces
│   │   ├── slab.py                          # Entidad Slab
│   │   └── slab_forces.py                   # Fuerzas en losas
│   ├── proposals/                           # Generación de propuestas de diseño
│   │   ├── __init__.py
│   │   ├── design_generator.py              # Orquestador de búsqueda iterativa
│   │   ├── failure_analysis.py              # Detección de modo de falla
│   │   └── strategies/                      # Estrategias por modo de falla
│   │       ├── __init__.py
│   │       ├── base.py                      # Utilidades comunes
│   │       ├── flexure.py                   # Propuesta para falla por flexión
│   │       ├── shear.py                     # Propuesta para falla por corte
│   │       ├── combined.py                  # Propuesta para falla combinada
│   │       ├── reduction.py                 # Optimización de sobrediseño
│   │       ├── thickness.py                 # Aumento de espesor
│   │       └── column_min.py                # Espesor mínimo columnas §18.7.2.1
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
│   ├── structural_analysis.py               # Orquestador principal
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── element_classifier.py            # Clasificador elementos
│   │   ├── element_orchestrator.py          # Orquestador unificado de verificación
│   │   ├── flexocompression_service.py      # Servicio flexocompresión
│   │   ├── shear/                           # Servicio de corte
│   │   │   ├── __init__.py
│   │   │   ├── facade.py                    # ShearService (fachada principal)
│   │   │   ├── column_shear.py              # Cortante columnas §22.5, §18.7.6
│   │   │   ├── wall_shear.py                # Cortante muros §11.5, §18.10.4
│   │   │   └── wall_special_elements.py     # Clasificación, amplificación, borde
│   │   ├── proposal_service.py              # Orquestador (delega a domain/proposals/)
│   │   ├── punching_service.py              # Verificación punzonamiento
│   │   ├── slab_service.py                  # Verificación losas
│   │   ├── statistics_service.py            # Estadísticas y resumen
│   │   ├── formatting.py                    # Formateo SF y valores para JSON
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
│   │   ├── pier_details_formatter.py        # Formateador detalles piers
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
│  services/structural_analysis.py        Orquestador principal   │
│  ├── ElementService          → Verificación unificada          │
│  ├── FlexocompressionService → Curvas P-M de interacción       │
│  └── ShearService            → Cortante Vc + Vs                │
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
| `StructuralAnalysisService` | Orquestador principal, gestiona sesiones y flujo |
| `ElementService` | Verificación unificada de Beam/Column/Pier (SF, DCR, sísmico) |
| `FlexocompressionService` | Genera curvas P-M de interacción, calcula Mpr |
| `ShearService` | Calcula Vc + Vs y DCR de corte |
| `ProposalService` | Orquesta generación de propuestas (delega a domain/proposals/) |
| `StatisticsService` | Estadísticas y gráfico resumen |
| `PierDetailsFormatter` | Formatea detalles de piers para UI |

## Servicios de Dominio (`domain/`)

### `domain/chapter11/` - Muros (Cap. 11)

| Servicio | Responsabilidad |
|----------|-----------------|
| `WallLimitsService` | Espesores mínimos, espaciamientos máximos |
| `ReinforcementLimitsService` | Cuantías mínimas ρ_min |
| `SlenderWallService` | Método alternativo muros esbeltos (§11.8) |

### `domain/chapter18/` - Requisitos Sísmicos (Cap. 18)

| Servicio | Responsabilidad |
|----------|-----------------|
| `ShearAmplificationService` | Amplificación Ωv×ωv (§18.10.3) |
| `BoundaryElementService` | Elementos de borde (§18.10.6) |
| `WallPierService` | Wall piers (§18.10.8) |
| `CouplingBeamService` | Vigas de acople (§18.10.7) |
| `SeismicBeamService` | Vigas sísmicas §18.6 (dimensional, longitudinal, transversal, cortante) |
| `SeismicColumnService` | Columnas sísmicas §18.7 (dimensional, columna fuerte, refuerzo, cortante) |
| `NonSfrsService` | Elementos no-SFRS §18.14 (compatibilidad de deriva) |
| `DuctileCoupledWallService` | Muros acoplados dúctiles §18.10.9 |

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
| `WallClassificationService` | Clasifica muro vs columna (Tabla R18.10.1) |

### `domain/proposals/` - Generación de Propuestas

Sistema de búsqueda iterativa que propone soluciones cuando un elemento falla verificación.

| Componente | Responsabilidad |
|------------|-----------------|
| `DesignGenerator` | Orquesta estrategias según modo de falla |
| `determine_failure_mode()` | Detecta tipo de falla (flexión, corte, combinada, sobrediseño) |
| `strategies/flexure.py` | Aumenta barras de borde progresivamente |
| `strategies/shear.py` | Reduce espaciamiento → aumenta diámetro → agrega malla |
| `strategies/combined.py` | Búsqueda exhaustiva borde + malla + espesor |
| `strategies/reduction.py` | Optimiza elementos sobrediseñados (SF >> 1.0) |
| `strategies/column_min.py` | Aplica espesor mínimo 300mm para columnas sísmicas §18.7.2.1 |

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
┌─────────────────────────────────────────────────────────────┐
│  StructuralAnalysisService (services/structural_analysis)   │
│  Orquestador de SESIÓN - gestiona estado y batch            │
│                                                             │
│  • Guarda datos en cache (SessionManager)                   │
│  • Itera sobre TODOS los elementos                          │
│  • Genera estadísticas y reportes                           │
│                                                             │
│    for element in [piers + columns + beams]:                │
│        ┌─────────────────────────────────────────────────┐  │
│        │                                                 │  │
│        ▼                                                 │  │
│  ┌───────────────────────────────────────────────────┐   │  │
│  │  ElementService (analysis/element_verification)   │   │  │
│  │  Verificador de UN elemento - sin estado          │   │  │
│  │                                                   │   │  │
│  │  ┌─────────────────┐ ┌────────────────┐           │   │  │
│  │  │ FlexocompreSvc  │ │   ShearSvc     │           │   │  │
│  │  │ • Curva P-M     │ │ • Vc + Vs      │           │   │  │
│  │  │ • Esbeltez      │ │ • DCR          │           │   │  │
│  │  └────────┬────────┘ └───────┬────────┘           │   │  │
│  │           └──────┬───────────┘                    │   │  │
│  │                  ▼                                │   │  │
│  │     Combina SF + DCR + Checks muro                │   │  │
│  │                  │                                │   │  │
│  │                  ▼                                │   │  │
│  │     ElementVerificationResult                     │   │  │
│  └───────────────────────────────────────────────────┘   │  │
│        │                                                 │  │
│        └─────────────────────────────────────────────────┘  │
│                                                             │
│  Acumula resultados → Estadísticas                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  ¿SF ≥ 1 y DCR ≤ 1? │
         └─────────┬───────────┘
                   │
          ┌────────┴────────┐
          │ NO              │ SÍ
          ▼                 ▼
    ┌──────────────┐    ┌────────┐
    │ ProposalSvc  │    │ ✓ PASA │
    │ Genera       │    │        │
    │ propuesta    │    │        │
    └──────────────┘    └────────┘
```

**Responsabilidades:**

| Servicio | Nivel | Responsabilidad |
|----------|-------|-----------------|
| `StructuralAnalysisService` | Sesión | Gestiona cache, itera elementos, genera estadísticas |
| `ElementService` | Elemento | Verifica UN elemento (Pier/Column/Beam), sin estado |
| `FlexocompressionService` | Cálculo | Genera curva P-M, calcula SF de flexión |
| `ShearService` | Cálculo | Calcula Vc+Vs, DCR de cortante |

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
| **Piers** | Flexocompresión + Cortante bidireccional + Esbeltez + Requisitos sísmicos (§18.10) | - |
| **Columnas** | Flexocompresión + Cortante + Esbeltez + Requisitos sísmicos (§18.7) | - |
| **Vigas** | Flexocompresión + Cortante + Requisitos sísmicos (§18.6) | Deflexiones |
| **Non-SFRS** | Compatibilidad de deriva (§18.14) | - |
| **Muros Acoplados** | Verificación sistema dúctil (§18.10.9) | - |

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
