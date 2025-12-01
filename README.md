# Knitting Pattern Visualization Project

A layered architecture application that generates visual representations of knitting patterns by parsing pattern instructions and creating interactive charts.

## Contributors
Diana Whealan

## Architecture

This project follows a **3-layer architecture**:

- **Presentation Layer**: ViewModels, Mappers, and JavaScript visualization components
- **Domain Layer**: Business logic, pattern processing, chart generation, and validation
- **Data Layer**: Data models, persistence, and serialization

See `docs/refactored_design.uml` for the complete architecture diagram.

## Dependencies

- **Python 3.x**
- **External Libraries**: None (pure Python implementation)
- **JavaScript**: D3.js (for visualization in HTML)

## Project Structure
project-20252601-diana_final_project/
├── engine/ # Main application code
│ ├── main.py # Application entry point
│ ├── chart_section.py # Core chart orchestration class
│ ├── domain/ # Domain layer (business logic)
│ │ ├── factories/ # Factory pattern implementations
│ │ ├── interfaces/ # Interface definitions
│ │ ├── models/ # Domain models and managers
│ │ │ ├── operations/ # Command pattern operations
│ │ │ ├── validation/ # Chain of Responsibility validators
│ │ │ └── validators/ # Validation logic
│ │ └── services/ # Service layer
│ ├── data/ # Data layer
│ │ ├── models/ # Data transfer objects
│ │ └── repositories/ # Data persistence
│ ├── presentation/ # Presentation layer
│ │ ├── viewmodels/ # View models
│ │ ├── mappers/ # ViewModel mappers
│ │ ├── observers/ # Observer pattern implementations
│ │ └── services/ # Presentation services
│ └── test_.py # Test files
├── presentation/ # Frontend visualization
│ └── visualizaion.html # Interactive D3.js visualizer
└── docs/ # Documentation
└── refactored_design.uml # Architecture diagram


## Design Patterns

The project implements several design patterns:

- **Factory Pattern**: `ChartSectionFactory` creates and wires all dependencies
- **Command Pattern**: Operations (`CastOnOperation`, `AddRowOperation`, etc.) encapsulate chart operations
- **Chain of Responsibility**: Validation handlers process validation requests in sequence
- **Observer Pattern**: `ChartVisualizationObserver` updates visualization on chart state changes
- **Builder Pattern**: `ValidationChainBuilder` constructs validation chains
- **Dependency Injection**: All dependencies are injected into `ChartSection`

## Build Instructions

1. **Clone the repository**
2. **Navigate to the project directory**
3. **Run the application**:
   python engine/main.py
   This will:
- Create chart sections using `ChartService`
- Process knitting patterns
- Export JSON data to `engine/charts.json` and individual chart files

## Code Entry Points

### Main Application
- **`engine/main.py`** - Main script that uses `ChartService` to create charts, process patterns, and export JSON data

### Example Usage

The refactored code uses the service layer and factory pattern:

from engine.domain.services.chart_service import ChartService
from engine.data.repositories.chart_repository import ChartRepository

# Initialize service layer
repository = ChartRepository(data_path="engine")
chart_service = ChartService(chart_repository=repository)

# Create a chart using the service (factory creates ChartSection internally)
raglan = chart_service.create_chart(name="raglan", start_side="RS", sts=23, rows=21)

# Build the chart
raglan.cast_on_start(122)
raglan.repeat_rounds(["repeat(k1, p1)"], 15)
raglan.add_round("bo4, repeat(k1), rm").place_on_hold()
# ... additional pattern instructions ...

# Save charts
chart_service.save_charts([raglan])**Note**: `ChartSection` should be created through `ChartService` (which uses `ChartSectionFactory`). Direct instantiation is not supported in the refactored architecture.

## Running Tests

Run all tests:
python engine/run_all_tests.pyIndividual test files:
- `test_factory.py` - Tests factory pattern
- `test_refactored_chart_section.py` - Tests refactored ChartSection
- `test_service_integration.py` - Tests service layer
- `test_validation_infrastructure.py` - Tests validation system
- `test_pattern_processor.py` - Tests pattern processing
- `test_view_models.py` - Tests presentation layer

## JSON Export Location

The application exports JSON data in two formats:

1. **Master file**: `engine/charts.json`
   - Contains all chart sections in a single file
   - Uses ViewModels for presentation layer compatibility
   - Structure: `{"charts": [{"name": "...", "nodes": [...], "links": [...]}, ...]}`

2. **Individual chart files**: `engine/{chart_name}.json`
   - One file per chart section (e.g., `raglan.json`, `raglan_back.json`)
   - Structure: `{"name": "...", "nodes": [...], "links": [...]}`

Both formats are written to the `engine/` directory when you run `main.py`.

## Visualizer HTML Location

The interactive visualizer is located at:

- **`presentation/visualizaion.html`**

To use the visualizer:

1. Generate the JSON files by running `engine/main.py`
2. Open `presentation/visualizaion.html` in a web browser
3. The visualizer will automatically load `engine/charts.json`

The visualizer provides:
- Interactive tabbed interface for multiple charts
- SVG rendering of knitting patterns with color-coded stitch types:
  - Blue (`k`) - Knit stitches
  - Purple (`p`) - Purl stitches
  - Green (`inc`) - Increases
  - Red (`dec`) - Decreases
- Download functionality for individual chart SVGs
- Presentation layer architecture with ViewModels, Mappers, and Renderers

## Key Components

### Service Layer
- **`ChartService`**: Main service for chart operations
- **`ChartVisualizationService`**: Service for visualization concerns

### Domain Layer
- **`ChartSection`**: Core chart orchestration (uses dependency injection)
- **`PatternProcessor`**: Processes and validates patterns
- **`ChartGenerator`**: Generates nodes and links
- **`ChartQueries`**: Query interface for chart data
- **`OperationRegistry`**: Manages chart operations (Command pattern)
- **`ValidationHandler`**: Chain of Responsibility for validation

### Data Layer
- **`ChartRepository`**: Persists and loads chart data
- **`ChartDataSerializer`**: Serializes charts with deterministic ordering
- **`ChartDataValidator`**: Validates chart data structure

### Presentation Layer
- **`ChartViewModel`**, **`NodeViewModel`**, **`LinkViewModel`**: Presentation models
- **`ViewModelMapper`**: Maps domain/data models to view models
- **`ChartVisualizationObserver`**: Observer for real-time visualization updates

## Future Work

The following components are planned for future implementation:
- `ShortRowOperation` - Operation for short row patterns
- `IBodyFormTemplate` & `BodyFormTemplateRenderer` - Body form template system