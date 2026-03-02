## Backend (MVP)

FastAPI service that accepts Blockly-compiled IR and executes it using the `engine` package.

### Install

From repo root:

```bash
python -m pip install -r backend/requirements.txt
```

### Run (dev)

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### Endpoints

- `POST /preview`: execute IR and return preview payload

