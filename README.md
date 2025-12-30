# Módulo Structural - Análisis de Muros de Hormigón Armado

App standalone para análisis estructural de muros (piers) de hormigón armado según ACI 318.

## Estructura

```
app/structural/
├── domain/                    # Lógica de negocio pura
│   ├── entities/              # Entidades de dominio
│   │   ├── pier.py            # Muro de hormigón
│   │   ├── load_combination.py # Combinación de carga
│   │   ├── pier_forces.py     # Colección de combinaciones
│   │   ├── verification_result.py # Resultado de verificación
│   │   └── parsed_data.py     # Datos parseados de Excel
│   │
│   ├── calculations/          # Calculadores puros
│   │   ├── steel_layer_calculator.py    # Capas de acero
│   │   ├── reinforcement_calculator.py  # Propiedades de armadura
│   │   └── flexure_checker.py           # Verificación flexión
│   │
│   ├── interaction_diagram.py # Diagrama de interacción P-M
│   ├── shear_verification.py  # Verificación de corte
│   ├── slenderness.py         # Análisis de esbeltez
│   └── result.py              # Tipo Result genérico
│
├── services/                  # Lógica de aplicación
│   ├── pier_analysis.py       # Orquestador principal
│   ├── factory.py             # Factory para servicios
│   │
│   ├── analysis/              # Servicios de análisis
│   │   ├── flexure_service.py
│   │   ├── shear_service.py
│   │   └── statistics_service.py
│   │
│   ├── parsing/               # Servicios de parsing
│   │   ├── excel_parser.py    # Parser de Excel ETABS
│   │   ├── session_manager.py # Gestión de sesiones
│   │   ├── material_mapper.py # Mapeo de materiales
│   │   └── table_extractor.py # Extracción de tablas
│   │
│   └── presentation/          # Servicios de presentación
│       └── plot_generator.py  # Generación de gráficos
│
├── routes/                    # API REST
│   └── analysis.py            # Endpoints
│
├── templates/                 # HTML
├── static/                    # CSS/JS
└── standalone_app.py          # Punto de entrada Flask
```

## Ejecución

### Servidor standalone

Ejecutar desde la raíz del proyecto:

```bash
python app/structural/standalone_app.py
```

O como módulo:

```bash
python -m app.structural.standalone_app
```

El servidor inicia en **http://localhost:5001**

### Configuración

| Variable | Valor |
|----------|-------|
| Puerto | 5001 |
| Max upload | 50 MB |
| Debug | Habilitado |

## Patrones Arquitectónicos

### Capas
1. **Domain**: Lógica de negocio pura, sin dependencias externas
2. **Services**: Orquestación y coordinación
3. **Routes**: API REST (presentación)

### Calculadores (domain/calculations/)
Clases estáticas con métodos puros para cálculos:
- `SteelLayerCalculator`: Genera capas de acero para análisis P-M
- `ReinforcementCalculator`: Calcula propiedades de armadura
- `FlexureChecker`: Verifica flexocompresión contra demandas

### Inyección de Dependencias
`PierAnalysisService` acepta dependencias opcionales:

```python
# Default
service = PierAnalysisService()

# Con dependencias personalizadas (testing)
service = PierAnalysisService(
    session_manager=mock_session,
    flexure_service=mock_flexure
)

# Usando factory
from app.structural.services.factory import ServiceFactory
service = ServiceFactory.create_analysis_service()
```

## Flujo de Datos

```
Excel ETABS → EtabsExcelParser → ParsedData → SessionManager (cache)
                                                    ↓
                                            PierAnalysisService
                                                    ↓
                                    ┌───────────────┼───────────────┐
                                    ↓               ↓               ↓
                            FlexureService   ShearService   StatisticsService
                                    ↓               ↓               ↓
                            VerificationResult (por pier)
                                                    ↓
                                            JSON Response
```

## Uso

### Análisis básico
```python
from app.structural.services import PierAnalysisService

service = PierAnalysisService()

# Parsear Excel
result = service.parse_excel(file_content, session_id)

# Analizar
result = service.analyze(session_id, generate_plots=True)
```

### Análisis de combinación específica
```python
result = service.analyze_single_combination(
    session_id=session_id,
    pier_key="Cielo P1_PMar-C4-1",
    combination_index=5
)
```

## Cálculos Implementados

- **Flexocompresión**: Diagrama de interacción P-M según ACI 318
- **Corte bidireccional**: Interacción V2-V3 con verificación combinada
- **Esbeltez**: Factor de reducción por pandeo (k*lu/r)
- **Materiales**: Conversión automática de nombres ETABS a f'c
