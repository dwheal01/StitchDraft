## Goal

Build a blocks-based web editor that lets a user assemble knitting “pattern programs” as blocks, preview the resulting chart live, and export either:

- Engine-compatible JSON (for persistence / backend execution)
- A `flirt.py`-style Python script that imports and calls your engine API

The MVP should support the operations you already demonstrate in `engine/flirt.py` and `engine/main.py`.

---

## Non-goals (MVP)

- Full stitch-level visual row building (dragging each knit/purl stitch as blocks)
- Multi-user collaboration
- Full design templating library
- Perfect reverse-import from existing `charts.json` into blocks (optional later)

---

## Recommended Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Blocks**: Google Blockly (with a React wrapper)
- **Backend**: FastAPI (Python) + your existing engine package
- **Transport**: JSON over HTTP
- **Optional**: WebSocket for “live preview” streaming (not required for MVP)

---

## Core Idea: One Source of Truth (IR)

Blockly workspace compiles to a JSON Intermediate Representation (IR). The backend executes IR using your engine and returns preview artifacts.

### IR v0 (draft)

Top-level:

- `version`: string
- `charts`: list of chart programs

Chart program:

- `name`, `start_side`, `sts`, `rows`
- `commands`: ordered list of operations

Commands (MVP set):

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

Example:
json
{
   "version": "0.1",
   "charts": [
      {
      "name": "lobster_back",
      "start_side": "RS",
      "sts": 22,
      "rows": 44,
      "commands": [
         { "op": "cast_on_start", "count": 41 },
         {
            "op": "repeat_rows",
            "times": 17,
            "patterns": ["k2, inc, repeat(k1), inc, k2", "repeat(k1)"]
         },
         { "op": "add_row", "pattern": "repeat(k1,p1)" },
         { "op": "repeat_rows", "times": 3, "patterns": ["work est"] }
      ]
      }
   ]
}


Notes:
- Keep patterns as strings in MVP (your existing `PatternParser` language).
- Later you can add structured row tokens, but MVP stays string-based.

---

## MVP Features (User-facing)

### 1) Block Editor (Blockly)

User can:
- Create one or more charts (pieces)
- Add operations to each chart in order
- Edit pattern strings in blocks (rows/rounds)
- Repeat rows/rounds
- Place markers (absolute position)
- Hold/needle operations (basic)
- Join charts (demo use case)

### 2) Live Preview Pane

User sees:
- Current stitch count and row/round count
- Markers list
- Rendered chart grid (basic): rows x stitches, with stitch types

Preview should update:
- On block change (debounced)
- With clear error display when validation fails

### 3) Export

User can export:
- JSON IR (the workspace program)
- Generated Python script (a `flirt.py`-style runner)

---

## Backend API (FastAPI)

### Endpoints (MVP)

1) `POST /preview`
- Input: IR JSON
- Output: preview payload per chart:
  - rows (expanded stitches per row)
  - markers by side
  - stitch counts after each row
  - any warnings/errors

2) `POST /validate`
- Input: IR JSON
- Output: structured validation errors (by chart, command index, message)

3) `POST /export/python`
- Input: IR JSON
- Output: downloadable `.py` script text that:
  - imports `ChartService`, `ChartRepository`
  - recreates charts
  - executes commands in order
  - saves charts

Optional later:
- `POST /export/engine-json` if you want server-side generation of the engine JSON artifacts.

### Execution Strategy (Incremental-friendly)

Even in MVP, design with incremental rebuild in mind:
- Backend can accept full IR each time.
- It can still implement checkpoints internally later without changing the contract.

---

## Frontend Architecture

### Main screens/components

- `WorkspacePage`
  - `BlocklyWorkspace`
  - `PreviewPane`
  - `ErrorsPane`
  - `ExportPanel`

### Data flow

1. Blockly workspace changes
2. Compile workspace -> IR
3. Debounce (e.g., 300–500ms)
4. Send IR to `/preview`
5. Render preview and errors

### State

- `workspaceXml` (or Blockly JSON) for saving/loading the block layout
- `ir` (compiled)
- `preview` (from backend)
- `errors` (from backend)

---

## Blocks Spec (MVP Set)

### Chart blocks

- **Create Chart**
  - fields: `name`, `start_side`, `sts`, `rows`

### Command blocks (chart attached)

- **Cast On Start**
  - field: `count`
  - maps: `chart.cast_on_start(count)`

- **Cast On Additional**
  - field: `count`
  - maps: `chart.cast_on(count)`

- **Add Row**
  - field: `pattern` (string DSL)
  - maps: `chart.add_row(pattern)`

- **Add Round**
  - field: `pattern` (string DSL)
  - maps: `chart.add_round(pattern)`

- **Repeat Rows**
  - fields: `times`, `patterns` (list, or nested “Row Pattern” blocks)
  - maps: `chart.repeat_rows(patterns, times)`

- **Repeat Rounds**
  - fields: `times`, `patterns`
  - maps: `chart.repeat_rounds(patterns, times)`

- **Place Marker**
  - fields: `side` (`RS`/`WS`), `position` (int)
  - maps: `chart.place_marker(side, position)`

- **Place On Hold**
  - maps: `chart.place_on_hold()`

- **Place On Needle**
  - fields: `join_side` (`RS`/`WS`), `source` (held reference)
  - maps: `chart.place_on_needle(stitches_on_hold, join_side)`
  - MVP simplification: “use last hold result” (single slot), or store a hold-id in IR.

- **Join Charts**
  - fields: `left_chart_name`, `right_chart_name`
  - maps: `left.join(right)` or `chart_service.join_charts(left, right)`

---

## Preview Payload (Frontend Rendering Contract)

For each chart, backend returns:

- `chartName`
- `rows`: array of expanded rows (each row is an array of stitch tokens like `"k"`, `"p"`, `"inc"`, `"dec"`, `"bo"`, etc.)
- `rowMeta`: for each row:
  - `side`, `isRound`, `stitchCountBefore`, `stitchCountAfter`
- `markers`: by side
- `errors`: list of `{ commandIndex, message }`

MVP rendering can be simple:
- A grid where each stitch token maps to a small colored cell with a letter.

---

## Error Handling UX

- Show errors with:
  - Chart name
  - Block label (command type + index)
  - Message from backend (e.g. pattern validation failures)
- Highlight the corresponding block in Blockly (select/focus) when the user clicks an error.

---

## Milestones (MVP Build Order)

### Milestone A — Skeleton & plumbing (1–2 days)
- React+TS+Vite app boots
- Blockly workspace renders
- “Export IR” button prints IR JSON from workspace (even if minimal)

### Milestone B — Minimal blocks to run `flirt.py`-like flow (2–4 days)
- Implement custom blocks: Create Chart, Cast On Start, Add Row, Repeat Rows
- IR compiler stable
- Backend `/preview` executes IR and returns expanded rows
- Frontend shows basic preview + errors

### Milestone C — Rounds + markers (2–4 days)
- Add blocks: Add Round, Repeat Rounds, Place Marker
- Preview shows markers and side/round metadata

### Milestone D — Holds + join (2–4 days)
- Add blocks: Place On Hold, Place On Needle, Join Charts
- Provide a simple “hold slot” model (one hold buffer) or hold-id references

### Milestone E — Export (1–2 days)
- JSON IR export and load
- Python script export (`/export/python`) producing a runnable `flirt_like.py`

### Milestone F — Stitch semantics parity (cast-on+, rm, bo)
- Engine and PatternParser fully support:
  - Additional cast-on stitches after start (API + DSL).
  - Marker removal semantics (`rm` in pattern string) consistent with marker placement and tracking.
  - Bind-off operations (`bo`, `boN`) that correctly consume stitches and update counts.
- IR and block editor expose `cast_on_additional` (Cast On Additional block) so programs in blocks can reproduce flows in `engine/main.py` and `engine/flirt.py`.
- Preview payload correctly reflects these operations in `rows` and `rowMeta` (stitch counts, markers); no crashes when used.
- Regression tests for raglan, raglan_back, sleeve, and lobster_back flows pass.

### Named holds (reconnect workflow)
- **Place on hold** accepts a **name** (e.g. `"left"`, `"right"`); unconsumed stitches go into that slot.
- **Place on needle** accepts **from_hold** (name) and **join_side**; stitches from that slot are placed back and the slot is cleared.
- Workflow: place on hold name "left", place on hold name "right", place on needle from hold "left" and work the left, then place on needle from hold "right" and work a final row (e.g. k across, co4, k across) to reconnect after bind-off. Default name is `"last"` for backward compatibility.

---

## Definition of Done (MVP)

- User can reproduce the structure of `engine/flirt.py` (and a subset of `engine/main.py`) using blocks.
- Preview updates after changes and shows either:
  - Updated chart grid, stitch counts, markers
  - Or clear validation errors without crashing
- User can export:
  - IR JSON
  - A Python script that imports your engine and runs the program

---

## Next Steps After MVP

- Incremental execution + checkpoints to speed up mid-program edits
- Visual stitch-level row builder (blocks that compile to your DSL)
- Better chart rendering (symbol set, zoom, legend)
- Template gallery (raglan, sleeve, ribbing, etc.)
- Import engine `charts.json` -> blocks (reverse mapping)