# StitchDraft — Technical Report (Markdown Template)

> **How to use this file**: Replace the bracketed placeholders (e.g., `[TODO: ...]`) with your final text and screenshots. Sections marked **(Core contribution)** are the ones to emphasize in your paper.  
> **Project name in UI**: “StitchDraft” (see `frontend/src/App.tsx`).

---

## Title page

**Title**: StitchDraft: A Block-Based System for Visualizing Fit in Hand‑Knit Garments  
**Author**: Diana Whealan  
**Course/Instructor**: [TODO]  
**Date**: [TODO]  

---

## Abstract

[TODO: 150–250 words]

Suggested abstract content (edit as needed):
- StitchDraft is a block-based authoring system for knitting patterns that compiles to an intermediate representation (IR) and executes that IR to generate a geometry-aware node/link model of stitches.
- Unlike standard knitting charts (which assume uniform grid placement), StitchDraft computes stitch positions from stitch-to-stitch relationships across rows, handling increases/decreases/bind-offs in a way that produces more realistic garment shaping.
- The generated chart can be previewed interactively and overlaid on a proportional torso silhouette to support reasoning about garment fit.

---

## Table of contents

[TODO: generate automatically if your Markdown renderer supports it]

---

## 1. Introduction

### 1.1 Problem statement

[TODO: describe the pain point: textual patterns are hard to visualize as shaped garments; standard charts can be misleading for fit/shaping]

### 1.2 Contributions (high-level)

This project’s main contributions are:
- **(Core contribution) Block-based authoring workflow** that lowers the barrier to composing complex pattern programs by assembling commands visually and compiling them deterministically into an IR.
- **(Core contribution) Intermediate representation (IR)** that separates user authoring from execution, enabling validation, repeatability, and a clear backend execution contract.
- **(Core contribution) Geometry-aware stitch positioning** that anchors stitch positions to the previous row and handles shaping operations (increase/decrease/bind-off/cast-on) to produce a garment-like silhouette rather than a uniform grid.
- **(Core contribution) Proportional torso overlay** that renders a torso silhouette in real-world units and overlays the generated chart in a consistent coordinate space.

### 1.3 Document roadmap

[TODO: 4–6 sentences]

---

## 2. Background

### 2.1 Knitting patterns vs knitting charts

[TODO: explain row-by-row instructions, right-side (RS)/wrong-side (WS), markers, shaping operations]

### 2.2 Why “standard chart grids” are insufficient for garment fit

[TODO: explain that uniform x‑spacing hides shaping; inc/dec reposition fabric mass; bind-offs create edges/holes; a garment’s outline changes]

### 2.3 Visual programming and intermediate languages

[TODO: brief background on why blocks + IR is a useful separation]

---

## 3. Requirements

### 3.1 Functional requirements

Examples (edit to match your final list):
- **FR1**: Create one or more chart “pieces” (e.g., body, sleeve) with a start side and nominal gauge.
- **FR2**: Author a sequence of knitting commands (cast on, add row/round, repeats, markers, holds, joins).
- **FR3**: Preview charts as nodes/links (stitches + connections) with row metadata.
- **FR4**: Support shaping operations (increase/decrease) and edge operations (bind-off/cast-on).
- **FR5**: Overlay generated charts on a proportional torso silhouette.

### 3.2 Non-functional requirements

Examples:
- **NFR1**: Deterministic output for the same IR input.
- **NFR2**: Clear error messages for invalid patterns or invalid command sequences.
- **NFR3**: Maintainable architecture (layering, separation of concerns, testability).

---

## 4. System overview

### 4.1 Architecture (current high‑level layout)

The project is organized as a **client–server system with a reusable engine library**:
- **Frontend (React/TypeScript, Blockly UI + visualization)** in `frontend/`  
  - Hosts the Blockly workspace, IR preview status, node/link chart view, and torso overlay UI.
- **Backend API (FastAPI)** in `backend/app/`  
  - Exposes `/preview` for executing IR against the engine and `/torso/*` endpoints for proportional torso SVGs.
- **Engine library (Python)** in `engine/`  
  - Implements chart construction, pattern parsing/validation, stitch positioning, and JSON export.

Within the engine library itself, the refactored code still follows an internal **Presentation / Domain / Data** layering as documented in `README.md` and `docs/refactored_design.uml`, but the overall architecture should be understood as “frontend + FastAPI backend over the engine library” rather than a single monolithic 3‑layer app.

**Figure 1 (architecture UML)**  
_Suggested file_: `docs/figures/figure-01-architecture.png`  
[TODO: Export a readable crop of `docs/refactored_design.uml` or paste the diagram image here.]

![Figure 1: System architecture overview](figures/figure-01-architecture.png)

### 4.2 Primary runtime flow (end-to-end)

At a high level, StitchDraft executes this flow:

1. **Blockly workspace** emits an IR JSON structure in the browser.
2. The **backend** accepts IR (`POST /preview`) and executes each chart program (plus join dependencies).
3. The **engine** builds a node/link model with stitch positioning.
4. The backend returns a preview payload (nodes/links + row metadata) to the frontend for interactive rendering.
5. Optionally, the frontend requests a torso SVG (`POST /torso/svg`) and overlays the chart onto it.

**Figure 2 (end-to-end flow)**  
_Suggested file_: `docs/figures/figure-02-end-to-end-flow.png`  
[TODO: add a flow diagram screenshot/graphic.]

![Figure 2: End-to-end flow (Blocks → IR → Preview → Torso overlay)](figures/figure-02-end-to-end-flow.png)

---

## 5. Block-based authoring (Core contribution)

### 5.1 Blockly workspace integration

The frontend mounts a Blockly workspace and recompiles it on relevant workspace events (block create/move/change/delete).

Reference: `frontend/src/components/BlocklyWorkspace.tsx` (wires `compileWorkspaceToIr`).

**Figure 3 (Blockly workspace)**  
_Suggested file_: `docs/figures/figure-03-blockly-workspace.png`  
[TODO: screenshot the Blockly workspace showing a `Chart` block and a command chain.]

![Figure 3: Block-based authoring in Blockly](figures/figure-03-blockly-workspace.png)

### 5.2 Block categories and supported commands

The toolbox is organized into categories such as chart setup, stitch rows, and structure/markers.

Reference: `frontend/src/blockly/toolbox.ts`.

#### Supported command blocks (authoring-time)

Blocks compile into command objects:
- `cast_on_start`
- `cast_on_additional`
- `add_row`
- `add_round`
- `repeat_rows`
- `repeat_rounds`
- `place_marker`
- `place_on_hold`
- `place_on_needle`
- `join`

Reference: `frontend/src/blockly/registerBlocks.ts`.

### 5.3 Compilation: blocks → IR

The compiler walks top-level `Chart` blocks and serializes their fields + attached command chain into IR. It also produces compile-time errors (e.g., missing chart blocks, invalid counts, missing join chart name).

At a high level, the **intermediate representation (IR)** is a **pure data structure** that captures:
- The **set of charts** (`ChartProgram`) the user wants to build (name, starting side, nominal stitch/row counts).
- A **linear program of commands** per chart (`KnittingCommand[]`), each identified by an `op` tag and a small set of JSON‑serializable arguments.

Design choices for the IR:
- **Minimal surface area**: only operations that the engine actually supports (`cast_on_start`, `add_row`, `repeat_rows`, `place_marker`, `place_on_hold`, `place_on_needle`, `join`, etc.) are representable. This prevents the UI from expressing impossible states and makes IR validation straightforward.
- **Stable, versioned contract**: the top‑level object carries an `IR_VERSION` (see `frontend/src/ir/types.ts`), allowing future evolution without breaking older clients.
- **Backend‑driven semantics**: the IR does not duplicate low‑level knitting semantics (e.g., consumed/produced stitch counts, `work est` behavior). Instead, it delegates these to the engine library, so the same engine logic can be reused by different frontends.
- **Discriminated union by `op`**: on the backend, `backend/app/ir_models.py` defines a Pydantic union keyed by the `op` field, which ensures each command is shape‑checked at the API boundary before it ever touches the engine.

Concretely, compiling a single `Chart` block yields one `ChartProgram` in the IR. Each attached command block becomes a single JSON command object. For example, an “add row pattern `repeat(k1, p1)`” block compiles to `{ "op": "add_row", "pattern": "repeat(k1, p1)" }`, which the backend later interprets via the pattern parser and position calculator described in Sections 7–9.

Reference: `frontend/src/blockly/compileToIr.ts`.

**Figure 4 (IR JSON excerpt)**  
_Suggested file_: `docs/figures/figure-04-ir-json.png`  
[TODO: copy an IR JSON snippet from the UI (or DevTools) and render it as an image or code block.]

![Figure 4: IR JSON emitted by the compiler](figures/figure-04-ir-json.png)

#### Compile-time error strategy

The compiler returns `{ ir, errors }` rather than throwing, which supports “live preview” UX: the UI can show errors while still displaying the IR structure.

[TODO: add your specific rationale: user feedback loop, iterative building, avoids hard stops]

---

## 6. Intermediate representation (IR) (Core contribution)

### 6.1 Purpose of the IR

The IR is the contract between:
- **Authoring** (Blockly UI) and
- **Execution** (backend + engine)

This separation enables:
- Deterministic replay (same IR → same chart)
- A stable interface for validation and testing
- Potential future frontends (text-based authoring, templates) that also compile to IR

### 6.2 IR schema (frontend TypeScript)

The IR contains:
- a `version` string
- a list of `charts`, each with `name`, `start_side`, nominal `sts/rows` (used as gauge inputs), and a list of `commands`

Reference: `frontend/src/ir/types.ts`.

### 6.3 IR schema (backend Pydantic)

The backend defines a discriminated union by `op` to validate incoming IR payloads at the API boundary.

Reference: `backend/app/ir_models.py`.

### 6.4 IR execution order and join dependencies

The backend validates and orders join dependencies so that referenced charts are built before the chart that joins them, preventing cycles.

Reference: `backend/app/main.py` (join graph validation) and `backend/app/engine_adapter.py` (`ensure_chart_built`).

---

## 7. Engine pattern language (token-level intermediate language)

This section documents the **pattern string language** used inside IR commands like `add_row`, `add_round`, and repeat patterns. While the IR is a structural command list, the **pattern strings** are a second intermediate language that expands into per-stitch operations.

### 7.1 Token set and stitch semantics

The engine supports tokens including:
- **Regular stitches**: `k`, `p`
- **Shaping**: `inc`, `dec`
- **Markers**: `pm` (place marker), `sm` (slip marker), `rm` (remove marker)
- **Edges**: `bo` (bind off), `co` (cast on)
- **Repetition**: `repeat(...)`
- **Work-as-established** aliases: `"work est"`, `"est"`, `"cont as est"` etc.

Reference: `engine/domain/models/pattern_parser.py` and `engine/domain/models/validators/pattern_validator.py`.

#### Stitch-count semantics: consumed vs produced

Each token has a \((consumed, produced)\) behavior used during expansion:
- `k` / `p`: consumes 1, produces 1
- `inc`: consumes 0, produces 1 (requires a stitch before it in a row)
- `dec`: consumes 2, produces 1
- `bo`: consumes 1, produces 0
- `co`: consumes 0, produces 1
- marker operations produce/consume 0

Reference: `PatternParser.CONSUME_PRODUCE` in `engine/domain/models/pattern_parser.py`.

### 7.2 Validation: pattern token validation vs stitch-count validation

There are two distinct validation layers:

- **Pattern token validation (syntax/ops)** occurs before expansion in `AddRowOperation` using `PatternValidator.validate_pattern()`.
  - This ensures unknown operations are rejected early and can provide a clear “Allowed ops” hint.
  - Reference: `engine/domain/models/operations/add_row_operation.py` and `engine/domain/models/validators/pattern_validator.py`.

- **Stitch-count consistency validation** is done after expansion and after execution using a validation chain and stitch counter consistency checks.
  - Reference: `engine/chart_section.py` (post-execution `_verify_stitch_count_consistency`), and the validators/validation chain described in `docs/refactored_design.uml`.

### 7.3 Expansion algorithm (how a pattern becomes stitches)

`PatternParser.expand_pattern()` performs the core expansion:

- Splits patterns into **segments** at `sm` (and tracks marker indices) so repeats can “fill” a segment instead of the entire row.
- Supports `repeat(inner_tokens)` tokens that fill remaining stitches in a segment (with safeguards against over-consuming).
- Interprets **work-as-established** (aliases normalized to `work_est`) by looking at the previous row and selecting the stitch that preserves RS appearance.

Reference: `engine/domain/models/pattern_parser.py`.

#### Markers as segment boundaries

The parser queries and updates marker positions through an injected `IMarkerProvider` (implemented by `MarkerManager`). Markers allow patterns like ribbing to continue “in pattern” across shaping events by keeping segment boundaries consistent.

References:
- `engine/domain/interfaces/imarker_provider.py` (interface)
- `engine/domain/models/marker_manager.py` (implementation)
- `engine/domain/models/pattern_parser.py` (uses marker provider to split segments and move/remove markers)

---

## 8. Chart construction pipeline (Core “how it works”)

### 8.1 Row addition: call graph

For a typical `add_row`/`add_round` command, the engine pipeline is:

1. `ChartSection.add_row(pattern, isRound)` delegates to the `add_row` operation
2. `AddRowOperation.execute(...)`:
   - validates token syntax (PatternValidator)
   - expands the pattern into a list of stitch tokens (PatternParser)
   - updates markers based on increases/decreases
   - reverses WS rows when needed
   - adds nodes and links (ChartGenerator + PositionCalculator)
   - updates stitch counters / validation chain

References:
- `engine/chart_section.py`
- `engine/domain/models/operations/add_row_operation.py`
- `engine/domain/models/pattern_parser.py`
- `engine/domain/models/chart_generator.py`
- `engine/domain/models/position_calculator.py`

### 8.2 Node/link model

The generated visualization is a graph:
- **Nodes** represent stitches (and also “strand” nodes between stitches for horizontal structure).
- **Links** represent:
  - Horizontal adjacency (stitch → strand → next stitch)
  - Vertical relationships (previous row stitch(es) → current stitch), including special handling for `inc/dec`.

Reference: `engine/domain/models/chart_generator.py` (strand nodes + horizontal links) and `engine/domain/models/position_calculator.py` (vertical links).

**Figure 5 (node/link preview)**  
_Suggested file_: `docs/figures/figure-05-node-link-preview.png`  
[TODO: screenshot the preview panel showing nodes + links for a shaped chart.]

![Figure 5: Node/link visualization of a chart](figures/figure-05-node-link-preview.png)

---

## 9. Stitch position calculation (Core contribution)

### 9.1 Motivation

Standard knitting charts draw stitches on a uniform grid, which can make shaped garments look like rectangles. StitchDraft instead computes stitch x-positions (“anchors”) based on the previous row so shaping operations visibly alter the silhouette.

### 9.2 Gauge mapping and coordinate system

The engine uses a 96-units-per-inch convention when mapping gauge to spacing:

- Default spacing: \(96 / (sts/4)\)
- Row height: \(96 / (rows/4)\)

Reference: `PositionCalculator.set_guage()` in `engine/domain/models/position_calculator.py`.

### 9.3 Anchors for regular stitches

For regular stitches (`k`, `p`, `bo`), anchors are taken directly from the previous row’s stitch `fx` positions (skipping bound-off nodes), and vertical links are created from the previous stitch node to the current stitch node.

Reference: `PositionCalculator._calculate_from_previous_row()` in `engine/domain/models/position_calculator.py`.

### 9.4 Anchors for shaping stitches: increase and decrease

The engine computes anchors for `inc` and `dec` using local geometry:

- **Increase (`inc`)**: positioned between the last-used and next-unused stitches, or extended beyond the working edge when it occurs at the beginning/end.
  - Vertical link comes from the **strand node after the previous stitch**, reflecting that an increase conceptually happens “between stitches”.
  - Reference: `_add_increase_decrease_links()` for inc behavior.

- **Decrease (`dec`)**: positioned at the midpoint of the two consumed stitches.
  - Vertical links connect **both** consumed stitches to the single resulting decrease node.
  - Reference: `_add_increase_decrease_links()` for dec behavior.

Reference: `PositionCalculator._calculate_increase_decrease_anchor()` and `PositionCalculator._add_increase_decrease_links()` in `engine/domain/models/position_calculator.py`.

**Figure 6 (inc vs dec geometry)**  
_Suggested file_: `docs/figures/figure-06-inc-dec-geometry.png`  
[TODO: zoomed screenshot showing an increase and a decrease and their vertical links.]

![Figure 6: Increase vs decrease linking/anchors](figures/figure-06-inc-dec-geometry.png)

### 9.5 RS/WS handling and row reversal

WS rows are reversed earlier in the pipeline (so position calculation can treat them symmetrically), and stitch types are flipped for display (knit ↔ purl) at node creation time.

References:
- `RowManager.reverse_row_if_needed(...)` (see `engine/domain/models/row_manager.py`)
- `ChartGenerator.create_nodes_for_row(...)` (flips stitch type when `side == "WS"`) in `engine/domain/models/chart_generator.py`

### 9.6 Centering anchors

After deriving anchors from the previous row, the engine recenters and regularizes spacing by centering around the average anchor position and placing the row on an evenly spaced centered array. This keeps charts visually tidy while preserving overall alignment to the previous row.

Reference: `PositionCalculator._center_anchors()` in `engine/domain/models/position_calculator.py`.

---

## 10. Proportional torso overlay (Core contribution)

### 10.1 Overview

The torso overlay feature renders a torso silhouette as SVG using human body measurements (Craft Yarn Council sizes or custom input), then overlays the generated stitch chart in the same coordinate system.

### 10.2 Backend: torso SVG generation

The backend exposes:
- `GET /torso/sizes` returning the size table
- `POST /torso/svg` returning `{ svg, viewBox, width, height }`

Reference: `backend/app/main.py`.

The SVG builder:
- Computes half-widths at shoulder/underarm/bust/waist/hip levels
- Creates a symmetric torso shape by drawing a half-outline and mirroring it
- Adds guideline lines (underarm, apex/nipple line) useful for aligning garment pieces

Reference: `backend/app/torso_generator.py`.

### 10.3 Frontend: overlay rendering and unit conversion

The torso SVG coordinates are in **inches**. The chart comes back from the engine in “engine units” (96 per inch), so the frontend converts by:

> `engineUnitsToInches(v) = v / 96`

Then it overlays either:
- a rasterized snapshot of the chart, or
- per-node circles when a snapshot isn’t available

The overlay is draggable so the user can align chart features (e.g., underarm line, shoulder width) with the torso guides.

Reference: `frontend/src/components/TorsoOverlayView.tsx`.

**Figure 7 (torso overlay)**  
_Suggested file_: `docs/figures/figure-07-torso-overlay.png`  
[TODO: screenshot the torso overlay after aligning the chart to the underarm guideline.]

![Figure 7: Chart overlay on proportional torso](figures/figure-07-torso-overlay.png)

### 10.4 Torso controls (size vs custom)

Users can generate a torso from a size label or from custom measurement inputs (inches), including optional ease.

Reference: `frontend/src/components/TorsoControls.tsx`, plus Pydantic models in `backend/app/torso_models.py`.

---

## 11. Validation and error handling

### 11.1 Compile-time (frontend) errors

The compiler returns a list of errors (e.g., missing chart block, invalid cast-on additional count, missing join chart name) without throwing.

Reference: `frontend/src/blockly/compileToIr.ts`.

### 11.2 Runtime (backend/engine) errors

The backend executes commands sequentially and stops on the first failure for a given chart, returning `errors: [{commandIndex, message}]` to the UI.

Reference: `backend/app/engine_adapter.py` and `backend/app/preview_models.py`.

### 11.3 Non-fatal warnings

The engine can generate non-fatal warnings (e.g., repeat alignment warnings), which the backend surfaces as `warnings` associated with the command index.

References:
- `engine/domain/models/pattern_parser.py` (warnings list)
- `engine/chart_section.py` (`get_last_warnings` / `pop_last_warnings`)
- `backend/app/engine_adapter.py` (collects `pop_last_warnings()` during row recording)

---

## 12. Implementation notes and design patterns

[TODO: tie to your refactor/design goals]

The refactored architecture employs multiple patterns:
- **Factory**: creates/wires `ChartSection` dependencies (`ChartSectionFactory`)
- **Command**: operations like `AddRowOperation` encapsulate changes
- **Observer**: visualization observer reacts to chart events
- **Chain of Responsibility**: validation handlers
- **Dependency injection**: explicit injection of managers/calculators into `ChartSection`

Reference: `README.md` and `docs/refactored_design.uml`.

---

## 13. Testing strategy and results

### 13.1 Test organization

The repo includes a set of Python tests under `engine/test_*.py` (see `README.md` for filenames) and a frontend test for the IR compiler.

References:
- `engine/run_all_tests.py`
- `frontend/src/blockly/compileToIr.test.ts`

### 13.2 What was tested (examples)

[TODO: list concrete cases you covered]
- Pattern parsing correctness for repeats and marker-based segmentation
- Stitch count consistency under increases/decreases/bind-offs/cast-ons
- Join graph validation (cycle detection)
- Frontend compiler correctness (blocks → IR)

### 13.3 Known gaps

[TODO: e.g., complex stitch types beyond k/p, short rows, fully realistic drape simulation]

---

## 14. Limitations and future work

Examples (edit to match your intent):
- Expand the stitch vocabulary beyond the MVP tokens (e.g., k2tog/ssk/yo) while preserving deterministic consumed/produced semantics.
- Add explicit **short row** support (noted as future work in `README.md`).
- Improve the position model to incorporate yarn tension/drape (currently geometric/structural rather than physics-based).
- Improve automatic alignment between chart and torso guides (currently user-draggable).

---

## References

[TODO: include Craft Yarn Council reference, Blockly, D3/React/Vite, any knitting visualization references]

---

## Appendix A — IR reference (copy/paste friendly)

### A.1 IR (TypeScript) summary

Reference: `frontend/src/ir/types.ts`.

- `KnittingIR = { version: string, charts: ChartProgram[] }`
- `ChartProgram = { name, start_side, sts, rows, commands: KnittingCommand[] }`
- `KnittingCommand` discriminated by `op`:
  - `cast_on_start {count}`
  - `cast_on_additional {count}`
  - `add_row {pattern}`
  - `add_round {pattern}`
  - `repeat_rows {times, patterns[]}`
  - `repeat_rounds {times, patterns[]}`
  - `place_marker {side, position}`
  - `place_on_hold {name?}`
  - `place_on_needle {join_side, from_hold?, source?, cast_on_between?}`
  - `join {left_chart_name, right_chart_name, right_pattern?}`

### A.2 IR example

[TODO: paste an example IR JSON captured from the UI]

---

## Appendix B — Pattern token reference

Reference: `engine/domain/models/pattern_parser.py` and `engine/domain/models/validators/pattern_validator.py`.

| Token | Meaning | Consumed | Produced | Notes |
|------:|---------|---------:|---------:|------|
| `k` | knit | 1 | 1 | |
| `p` | purl | 1 | 1 | |
| `inc` | increase | 0 | 1 | cannot be first stitch of row (`AddRowOperation`) |
| `dec` | decrease | 2 | 1 | |
| `bo` | bind off | 1 | 0 | |
| `co` | cast on | 0 | 1 | |
| `pm` | place marker | 0 | 0 | produces marker positions list during expansion |
| `sm` | slip marker (segment boundary) | 0 | 0 | used to split pattern into segments |
| `rm` | remove marker (segment boundary + removal) | 0 | 0 | |
| `repeat(...)` | repeat inner tokens | varies | varies | fill logic is segment-aware |
| `work est` / `est` / `cont as est` | work as established | 1 | 1 | expanded using previous row + RS appearance rules |

---

## Appendix C — Figures checklist (placeholders)

- **Figure 1**: Architecture overview (UML / component diagram).  
  Caption: “Three-layer architecture and core domain components.”

- **Figure 2**: End-to-end flow diagram.  
  Caption: “Blocks → IR → backend execution → chart preview → torso overlay.”

- **Figure 3**: Blockly workspace screenshot.  
  Caption: “Block-based authoring of a chart program; live compilation to IR.”

- **Figure 4**: IR JSON excerpt for one chart.  
  Caption: “Intermediate representation (IR) emitted by the compiler and consumed by the backend.”

- **Figure 5**: Node/link preview of a chart with shaping.  
  Caption: “Graph representation of stitches: stitch nodes, strand nodes, horizontal links, and vertical links across rows.”

- **Figure 6**: Increase vs decrease geometry (zoomed).  
  Caption: “Anchor and linking semantics: `inc` links from a strand node; `dec` links from two consumed stitches.”

- **Figure 7**: Torso overlay view with a chart aligned to guidelines.  
  Caption: “Proportional torso overlay in inches with chart geometry converted from engine units (96 per inch).”

