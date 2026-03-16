# StitchDraft – Knitting Pattern Visualization

StitchDraft is a block-based system for authoring and visualizing knitting patterns.  
Users build patterns with Blockly, the frontend compiles them to a knitting-specific IR, and the backend engine executes that IR to generate stitch-level charts that can be overlaid on a proportional torso silhouette.

This README explains how to clone the repo, run the backend and frontend, and where the main pieces live.

## Prerequisites

- **Python**: 3.10+ recommended
- **Node.js**: 18+ (for the React/Vite frontend)
- **npm** (or `pnpm`/`yarn` if you prefer and adjust commands accordingly)

All Python dependencies are installed via `pip`, and frontend dependencies via `npm`.

## Quick start – run backend and frontend

From the project root (`project-20252601-diana_final_project/`):

### 1. Create and activate a Python virtualenv (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
```

### 2. Install backend + engine dependencies

```bash
pip install -r backend/requirements.txt
```

> If `requirements.txt` is missing or you changed dependencies, inspect `backend/app` and `engine/` and install the needed packages manually (e.g. `fastapi`, `uvicorn`, `pydantic`, etc.).

### 3. Run the backend API (FastAPI)

From the project root:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

This starts the API at `http://localhost:8000` with the following main endpoints:

- `GET /healthz` – simple health check
- `POST /preview` – accepts a `KnittingIR` JSON payload and returns chart previews (nodes, links, rows, markers, errors/warnings)
- `GET /torso/sizes` – returns Craft Yarn Council body measurements by size
- `POST /torso/svg` – generates a torso SVG (either by size or by custom measurements)

The backend uses the **engine** package (`engine/`) as a library for chart execution and geometry. It does not persist anything; all charts are built in memory per request.

### 4. Install frontend dependencies

From the `frontend/` directory:

```bash
cd frontend
npm install
```

### 5. Run the frontend (Vite dev server)

Still inside `frontend/`:

```bash
npm run dev
```

By default Vite serves the app at `http://localhost:5173`.

The frontend is configured to talk to the backend via a relative URL (`/preview`, `/torso/svg`, etc.), and the Vite dev server proxies to `http://localhost:8000`. If you run the backend on a different host/port, set:

```bash
export VITE_API_BASE_URL="http://localhost:8000"
```

before running `npm run dev`, so the frontend sends requests to the correct base URL.

Once both servers are running:

- Open `http://localhost:5173` in your browser.
- Use the **Blockly** workspace to add a `Chart` block and commands.
- The **Preview** panel will automatically compile the workspace to IR, call `/preview`, and show:
  - a node-link chart (`NodeLinkView`)
  - per-row metadata and markers
  - optional torso overlay (`TorsoOverlayView`) once you generate a torso in the panel.

## Project structure (high-level)

At the top level:

- `backend/` – FastAPI app and IR/preview/torso models
  - `app/main.py` – API entrypoint (`/preview`, `/torso/svg`, `/torso/sizes`, `/healthz`)
  - `app/engine_adapter.py` – glue between IR (`KnittingIR`) and the engine (`ChartService`, `ChartSection`)
  - `app/ir_models.py` – Pydantic models for the knitting IR (commands like `add_row`, `join`, `place_on_hold`, etc.)
  - `app/preview_models.py` – Pydantic models for the preview response (`ChartPreview`, `NodeView`, `LinkView`, `RowMeta`, markers, errors/warnings)
  - `app/torso_generator.py` – SVG torso generator (uses Craft Yarn Council measurements or custom inputs)
  - `app/torso_models.py` – Pydantic models for torso requests/responses

- `engine/` – reusable chart engine library (no HTTP)
  - `chart_section.py` – core orchestration class for one chart; coordinates row manager, node manager, marker manager, pattern parser, position calculator, chart generator, etc.
  - `domain/` – domain logic
    - `factories/chart_section_factory.py` – builds fully-wired `ChartSection` instances
    - `models/pattern_parser.py` – stitch-level DSL parser (`k`, `p`, `inc`, `dec`, `repeat(...)`, `work est`, segmenting by markers)
    - `models/validators/pattern_validator.py` – fast token/parenthesis validation for pattern strings
    - `models/chart_generator.py` – converts expanded rows into nodes/links using `PositionCalculator`
    - `models/position_calculator.py` – computes node positions from gauge and previous-row geometry (96 units per inch)
    - `models/operations/` – command pattern operations (`AddRowOperation`, `CastOnOperation`, `JoinOperation`, `PlaceOnHoldOperation`, etc.)
    - managers: `RowManager`, `NodeManager`, `LinkManager`, `MarkerManager`, `StitchCounter`
  - `data/` – simple DTOs and serializers
    - `models/chart_data.py` – `ChartData` (name, nodes, links)
    - `repositories/chart_data_serializer.py` – converts `ChartSection` → `ChartData`
  - `presentation/` – internal view models and mappers used by the backend to produce API-friendly node/link shapes

- `frontend/` – React + TypeScript + Vite app (primary UI)
  - `src/ir/types.ts` – TypeScript definitions for the IR (`KnittingIR`, `ChartProgram`, `KnittingCommand`)
  - `src/blockly/` – Blockly integration
    - `registerBlocks.ts` – knitting-specific blocks (chart, add row/round, repeat rows/rounds, markers, holds, joins)
    - `toolbox.ts` – toolbox configuration
    - `compileToIr.ts` – compiler from Blockly workspace → `KnittingIR` (JSON)
  - `src/api/client.ts` – small API client:
    - `fetchPreview(ir)` – calls `POST /preview`
    - `fetchTorsoSizes()` – calls `GET /torso/sizes`
    - `fetchTorsoSvg(req)` – calls `POST /torso/svg`
  - `src/components/BlocklyWorkspace.tsx` – mounts Blockly and emits compiled IR on changes
  - `src/components/NodeLinkView.tsx` – SVG node-link chart view with selection-based measurement
  - `src/components/TorsoControls.tsx` – controls for generating torsos (size/custom + ease)
  - `src/components/TorsoOverlayView.tsx` – overlay chart (converted to inches) on torso SVG with drag + rotation
  - `src/utils/chartSnapshot.ts` – builds snapshot SVG/PNG of a chart from node positions and types
  - `src/App.tsx` – top-level app wiring workspace → IR → preview → chart + torso views

- `docs/` – technical report and diagrams
  - `technical_report.md` – main writeup
  - `refactored_design.uml` – internal architecture diagram

## Running tests

The engine and backend ship with Python tests under `engine/`. To run all tests:

```bash
cd engine
python -m pytest
```

If you prefer the legacy test runner:

```bash
python run_all_tests.py
```

This exercises the pattern parser, stitch counting, operations, and integration flow from `ChartService` down through `ChartSection`.

## Notes for contributors

- The **IR** (`KnittingIR`) is the stable contract between the Blockly frontend and the backend engine. If you add new commands or fields, update:
  - `frontend/src/ir/types.ts`
  - `frontend/src/blockly/compileToIr.ts`
  - `backend/app/ir_models.py`
  - `backend/app/engine_adapter.py`
- The engine is deliberately **framework-agnostic**: it has no FastAPI or React imports. All web integration lives in `backend/app`.
- The legacy D3-based HTML visualizations under `presentation/` are no longer the primary UI; use the React frontend in `frontend/` instead.

For deeper design details, see `docs/technical_report.md` and `docs/refactored_design.uml`.
