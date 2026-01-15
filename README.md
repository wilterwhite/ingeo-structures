# INGEO Structures - Verificación Estructural ACI 318-25

Aplicación web para verificación estructural de elementos de hormigón armado según ACI 318-25.

## Elementos Soportados

| Elemento | Verificaciones | Tablas ETABS |
|----------|----------------|--------------|
| **Piers (Muros)** | Flexocompresión P-M + Cortante V2-V3 | Pier Section Properties, Pier Forces |
| **Columnas** | Flexocompresión P-M + Cortante V2-V3 | Frame Sec Def - Conc Rect, Element Forces - Columns |
| **Vigas** | Cortante (solo por ahora) | Frame Sec Def - Conc Rect, Element Forces - Beams |
| **Spandrels** | Cortante (vigas de acople) | Spandrel Section Properties, Spandrel Forces |
| **Struts** | Compresión + Flexión (hormigón no confinado) | Elementos pequeños (<15cm) |

## Características

- Importación directa de archivos Excel exportados de ETABS
- Detección automática de tablas disponibles (piers, columnas, vigas)
- Verificación de flexocompresión con diagrama de interacción P-M
- Verificación de corte bidireccional (V2-V3) con DCR combinado
- Análisis de esbeltez y magnificación de momentos
- Clasificación automática de elementos (muro, columna, wall-pier, strut)
- **Propuestas automáticas de diseño** cuando un elemento falla
- Interfaz web interactiva con edición inline de armadura
- Persistencia de proyectos (localStorage + backend)

## Arquitectura

```
app/
├── domain/                                  # Lógica de negocio ACI 318-25
│   ├── calculations/
│   │   ├── confinement.py                   # Refuerzo de confinamiento
│   │   ├── steel_layer_calculator.py        # Capas de acero
│   │   └── wall_continuity.py               # Continuidad vertical muros
│   ├── chapter18/                           # Requisitos sísmicos (Cap. 18)
│   │   ├── common/categories.py             # SeismicCategory enum
│   │   ├── beams/service.py                 # Vigas sísmicas §18.6
│   │   ├── columns/                         # Columnas sísmicas §18.7
│   │   │   ├── dimensional.py               # Límites dimensionales
│   │   │   ├── flexural_strength.py         # Columna fuerte-viga débil
│   │   │   ├── shear.py                     # Cortante sísmico
│   │   │   └── service.py                   # SeismicColumnService
│   │   ├── coupling_beams/service.py        # Vigas acople §18.10.7
│   │   ├── boundary_elements/               # Elementos de borde §18.10.6
│   │   ├── wall_piers/                      # Wall piers §18.10.8
│   │   └── walls/service.py                 # Muros sísmicos §18.10
│   ├── chapter23/                           # Strut-and-Tie (Cap. 23)
│   │   └── strut_capacity.py                # Struts no confinados
│   ├── constants/
│   │   ├── materials.py                     # Propiedades materiales
│   │   ├── phi_chapter21.py                 # Factores φ Cap. 21
│   │   ├── chapter23.py                     # Constantes struts
│   │   └── reinforcement.py                 # Diámetros y áreas barras
│   ├── entities/
│   │   ├── vertical_element.py              # VerticalElement (Column/Pier unificado)
│   │   ├── horizontal_element.py            # HorizontalElement (Beam/DropBeam unificado)
│   │   ├── element_forces.py                # ElementForces (fuerzas unificadas)
│   │   ├── reinforcement.py                 # DiscreteReinforcement, MeshReinforcement
│   │   ├── design_proposal.py               # Propuesta de diseño
│   │   ├── load_combination.py              # Combinación de carga
│   │   └── parsed_data.py                   # Datos parseados ETABS
│   ├── proposals/                           # Generación de propuestas de diseño
│   │   ├── design_generator.py              # Orquestador de búsqueda iterativa
│   │   └── strategies/                      # Estrategias por modo de falla
│   │       ├── flexure.py                   # Propuesta para falla por flexión
│   │       ├── shear.py                     # Propuesta para falla por corte
│   │       ├── combined.py                  # Propuesta para falla combinada
│   │       └── column_min.py                # Espesor mínimo columnas §18.7.2.1
│   ├── flexure/
│   │   ├── interaction_diagram.py           # Diagrama P-M
│   │   └── slenderness.py                   # Esbeltez y magnificación
│   └── shear/
│       ├── concrete_shear.py                # Vc centralizado
│       ├── steel_shear.py                   # Vs centralizado
│       └── combined.py                      # DCR biaxial combinado
├── routes/
│   ├── piers.py                             # Endpoints análisis elementos
│   ├── projects.py                          # Endpoints gestión proyectos
│   └── common.py                            # Utilidades compartidas + /api/constants
├── services/
│   ├── structural_analysis.py               # Orquestador principal
│   ├── analysis/
│   │   ├── element_orchestrator.py          # Orquestador unificado de verificación
│   │   ├── element_classifier.py            # Clasificador elementos
│   │   ├── design_behavior.py               # DesignBehavior enum
│   │   ├── design_behavior_resolver.py      # Resuelve transiciones
│   │   ├── geometry_normalizer.py           # Normaliza geometría entre tipos
│   │   ├── force_extractor.py               # Extrae fuerzas normalizadas
│   │   ├── flexocompression_service.py      # Servicio flexocompresión
│   │   ├── shear_service.py                 # Cortante Vc + Vs + DCR
│   │   └── proposal_service.py              # Orquestador propuestas
│   ├── parsing/
│   │   ├── excel_parser.py                  # Parser Excel principal
│   │   ├── beam_parser.py                   # Parser vigas ETABS
│   │   ├── column_parser.py                 # Parser columnas ETABS
│   │   ├── drop_beam_parser.py              # Parser drop beams ETABS
│   │   └── session_manager.py               # Gestor sesiones
│   ├── presentation/
│   │   ├── modal_data_service.py            # Datos para modal de detalles
│   │   ├── plot_generator.py                # Generador gráficos P-M
│   │   └── result_formatter.py              # Formateador resultados UI
│   └── persistence/
│       ├── project_manager.py               # Gestión proyectos
│       └── parsed_data_serializer.py        # Serialización datos
├── static/                                  # CSS, JavaScript
│   └── js/
│       ├── core/                            # StructuralAPI, Constants, Utils
│       ├── managers/                        # ProjectManager, UploadManager
│       ├── modules/                         # WallsModule
│       └── tables/                          # RowFactory, células
└── templates/                               # HTML Jinja2
```

## Modelo de Entidades Unificado

El sistema usa entidades unificadas que representan elementos estructurales independientemente de su origen en ETABS:

### VerticalElement
Unifica Column y Pier. Se distinguen por `source`:
- `FRAME` → Columna (originalmente de Frame Section)
- `PIER` → Pier/Muro (originalmente de Pier Section)

Propiedades clave:
- `is_small_strut` → True si ambas dimensiones < 150mm (se verifica como strut Cap. 23)
- `seismic_category` → SPECIAL, INTERMEDIATE, ORDINARY, NON_SFRS

### HorizontalElement
Unifica Beam y DropBeam. Se distinguen por `source`:
- `FRAME` → Viga normal
- `DROP_BEAM` → Viga capitel (se diseña como muro §18.10)

### ElementForces
Fuerzas unificadas para cualquier tipo de elemento:
- `P`, `V2`, `V3`, `M2`, `M3` por combinación
- Envolvente calculada automáticamente

## Flujo Unificado de Diseño (ElementOrchestrator)

```
ElementOrchestrator.verify(element, forces)
│
├─ ElementClassifier.classify(element)
│   │  Detecta tipo geométrico:
│   ├─ WALL_PIER_COLUMN: lw/tw ≤ 2.5 Y hw/lw < 2.0 → Pier tipo columna
│   ├─ STRUT: dimensiones < 150mm → Strut no confinado (Cap. 23)
│   ├─ WALL / WALL_SQUAT: Muros normales
│   └─ BEAM, COLUMN_SEISMIC, DROP_BEAM
│
├─ DesignBehaviorResolver.resolve(element_type, forces)
│   │  Determina comportamiento de diseño:
│   ├─ WALL_PIER_COLUMN → SEISMIC_COLUMN (usa §18.7)
│   ├─ Beam con Pu > Ag×f'c/10 → SEISMIC_BEAM_COLUMN (usa §18.7.5)
│   └─ DROP_BEAM → SEISMIC_WALL (usa §18.10)
│
└─ Rutea a servicio apropiado:
    ├─ STRUT → StrutCapacityService (§23.4)
    ├─ SEISMIC_COLUMN → SeismicColumnService (§18.7)
    ├─ SEISMIC_BEAM → SeismicBeamService (§18.6)
    └─ SEISMIC_WALL → SeismicWallService (§18.10)
```

## Verificación de Struts (Cap. 23)

Elementos pequeños (ambas dimensiones < 150mm) se verifican como struts no confinados:

- **Capacidad axial**: Fns = 0.34 × f'c × Acs (ACI 23.4)
- **Capacidad flexión**: Mcr = fr × S = 0.62√f'c × bh²/6 (ACI 19.2.3)
- **Factor φ**: 0.60 para diseño sísmico (Tabla 21.2.1)
- **Diagrama P-M**: Triangular simplificado (sin tracción)

Si hay combinaciones con tracción, el elemento falla pero se muestra el DCR real de compresión.

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

| Elemento | Verificación Implementada |
|----------|---------------------------|
| **Piers** | Flexocompresión + Cortante bidireccional + Esbeltez + §18.10 |
| **Columnas** | Flexocompresión + Cortante + Esbeltez + §18.7 |
| **Vigas** | Flexocompresión + Cortante + §18.6 |
| **Struts** | Compresión + Flexión (Cap. 23) |

### Tablas ETABS Requeridas

**Piers:**
- `Wall Property Definitions` - Materiales de muros
- `Pier Section Properties` - Geometría de piers
- `Pier Forces` - Fuerzas por combinación

**Columnas:**
- `Frame Section Property Definitions - Concrete Rectangular`
- `Element Forces - Columns`

**Vigas:**
- `Frame Section Property Definitions - Concrete Rectangular`
- `Element Forces - Beams`

**Spandrels:**
- `Spandrel Section Properties`
- `Spandrel Forces`
